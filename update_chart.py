import requests
import time
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import json
import os

BASE_URL = "https://api.coingecko.com/api/v3"
CACHE_FILE = "historical_data.json"
HTML_FILE = "crypto_performance.html"
API_KEY = os.getenv("COINGECKO_API_KEY", "CG-1KR3Wbo6yQfvUD9EHQoeECet")  # Fallback for local runs

def fetch_top_coins(limit=200):
    url = f"{BASE_URL}/coins/markets"
    headers = {"x-cg-demo-api-key": API_KEY}
    params = {"vs_currency": "usd", "order": "market_cap_desc", "per_page": limit, "page": 1, "sparkline": False}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return [coin["id"] for coin in response.json()]
    print(f"Failed to fetch top coins: {response.status_code}")
    return []

def fetch_historical_data(coin_id, days=365):
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    headers = {"x-cg-demo-api-key": API_KEY}
    params = {"vs_currency": "usd", "days": days, "interval": "daily"}
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        prices = data.get("prices", [])
        market_caps = data.get("market_caps", [])
        if not prices or not market_caps:
            print(f"No data found for {coin_id}")
        return prices, market_caps
    except requests.exceptions.HTTPError as e:
        print(f"Failed to fetch data for {coin_id}: {e}")
        return [], []

def save_to_cache(data):
    with open(CACHE_FILE, 'w') as f:
        json.dump(data, f)
    print(f"Data saved to {CACHE_FILE}")

def main():
    # Fetch fresh data
    print("Fetching list of top 200 coins...")
    top_coins = fetch_top_coins(limit=200)
    if not top_coins:
        print("No top coins fetched. Exiting.")
        exit()

    historical_data = {}
    for coin in top_coins:
        print(f"Fetching data for {coin}...")
        prices, market_caps = fetch_historical_data(coin, days=365)
        historical_data[coin] = {'prices': prices, 'market_caps': market_caps}
        time.sleep(2)  # 2-second delay
 
    save_to_cache(historical_data)

    # Process market cap data
    market_cap_dfs = []
    for coin in historical_data.keys():
        market_caps = historical_data[coin]['market_caps']
        if market_caps:
            df = pd.DataFrame(market_caps, columns=['timestamp', 'market_cap'])
            df['date'] = pd.to_datetime(df['timestamp'], unit='ms').dt.date
            df = df.groupby('date')['market_cap'].mean().rename(coin)
            market_cap_dfs.append(df)

    market_cap_df = pd.concat(market_cap_dfs, axis=1).fillna(0)
    total_market_cap = market_cap_df.sum(axis=1)

    if 'bitcoin' in market_cap_df.columns and 'ethereum' in market_cap_df.columns:
        total3 = total_market_cap - market_cap_df['bitcoin'] - market_cap_df['ethereum']
    else:
        total3 = total_market_cap

    # Process BTC and ETH prices
    btc_prices = historical_data['bitcoin']['prices']
    df_btc = pd.DataFrame(btc_prices, columns=['timestamp', 'price'])
    df_btc['date'] = pd.to_datetime(df_btc['timestamp'], unit='ms').dt.date
    df_btc = df_btc.groupby('date')['price'].mean().rename('btc_price')

    eth_prices = historical_data['ethereum']['prices']
    df_eth = pd.DataFrame(eth_prices, columns=['timestamp', 'price'])
    df_eth['date'] = pd.to_datetime(df_eth['timestamp'], unit='ms').dt.date
    df_eth = df_eth.groupby('date')['price'].mean().rename('eth_price')

    price_df = pd.concat([df_btc, df_eth], axis=1)

    # Identify drop events
    total_market_cap_pct_change = total_market_cap.pct_change(periods=7)
    drop_dates = total_market_cap_pct_change[total_market_cap_pct_change < -0.10].index

    # Calculate performance
    btc_performances = []
    eth_performances = []
    total3_performances = []

    for drop_date in drop_dates:
        if isinstance(drop_date, pd.Timestamp):
            drop_date = drop_date.date()
        end_date = pd.Timestamp(drop_date) + pd.DateOffset(days=90)
        if end_date.date() <= price_df.index.max() and drop_date in price_df.index:
            btc_perf = (price_df['btc_price'].loc[drop_date:] / price_df['btc_price'].loc[drop_date] - 1) * 100
            eth_perf = (price_df['eth_price'].loc[drop_date:] / price_df['eth_price'].loc[drop_date] - 1) * 100
            total3_perf = (total3.loc[drop_date:] / total3.loc[drop_date] - 1) * 100
            btc_perf = btc_perf.head(90).reset_index(drop=True)
            eth_perf = eth_perf.head(90).reset_index(drop=True)
            total3_perf = total3_perf.head(90).reset_index(drop=True)
            btc_performances.append(btc_perf)
            eth_performances.append(eth_perf)
            total3_performances.append(total3_perf)

    # Plot results
    if btc_performances:
        avg_btc_performance = pd.concat(btc_performances, axis=1).mean(axis=1)
        avg_eth_performance = pd.concat(eth_performances, axis=1).mean(axis=1)
        avg_total3_performance = pd.concat(total3_performances, axis=1).mean(axis=1)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=avg_btc_performance.index, y=avg_btc_performance.round(2), mode='lines', name='BTC', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=avg_eth_performance.index, y=avg_eth_performance.round(2), mode='lines', name='ETH', line=dict(color='purple')))
        fig.add_trace(go.Scatter(x=avg_total3_performance.index, y=avg_total3_performance.round(2), mode='lines', name='TOTAL3', line=dict(color='blue')))
        fig.update_layout(
            title="Average Performance After >10% Market Cap Drop (1 Year)",
            xaxis_title="Days After Drop",
            yaxis_title="Percentage Change (%)",
            legend_title="Assets",
            template="simple_white",
            showlegend=True,
            hovermode='x unified'
        )
        fig.write_html(
            HTML_FILE,
            include_plotlyjs='cdn',  # Use CDN version of plotly.js
            full_html=True,
            include_mathjax=False,
            validate=False,
            config={'displayModeBar': False}  # Hide the mode bar
        )
        print(f"Chart saved to {HTML_FILE}")
    else:
        print("No drop events found with sufficient data.")

if __name__ == "__main__":
    main()
