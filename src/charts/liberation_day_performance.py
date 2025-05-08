import os
import sys
from datetime import datetime, timedelta
import requests
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
import time

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config import COINGECKO_API_KEY

# Constants
BASE_URL = "https://api.coingecko.com/api/v3"

def get_traditional_assets_data(start_date):
    """Fetch data for traditional assets using spot prices and forward-fill for weekends."""
    # Define the symbols
    symbols = {
        '^GSPC': 'S&P 500',
        '^NDX': 'Nasdaq 100',
        'GLD': 'Gold'  # Using GLD (Gold ETF) instead of futures
    }
    
    # Create a complete date range - ensure we start exactly on start_date
    date_range = pd.date_range(start=start_date, end=datetime.now(), freq='D')
    
    # Initialize the result DataFrame with the date range as index
    result_df = pd.DataFrame(index=date_range)
    
    # Fetch data for each symbol
    for symbol, name in symbols.items():
        print(f"Fetching data for {name} ({symbol})...")
        
        # Try to get data from a few days before to ensure we have the start date
        buffer_start = start_date - timedelta(days=5)
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=buffer_start, interval='1d')
        
        if not hist.empty:
            # Convert index to UTC for consistency with crypto data
            hist.index = hist.index.tz_localize(None)
            
            # Filter to only include dates >= start_date
            hist = hist[hist.index >= pd.Timestamp(start_date)]
            
            # If we don't have data exactly on start_date, we need to backfill
            if hist.empty or hist.index[0] > pd.Timestamp(start_date):
                print(f"  Warning: No data for {name} on Liberation Day. Using first available data point.")
                # If we have any data after start_date, use that first point
                if not hist.empty:
                    first_available_date = hist.index[0]
                    first_price = hist['Close'].iloc[0]
                    
                    # Create a new entry at start_date with the first available price
                    new_row = pd.DataFrame({'Close': [first_price]}, index=[pd.Timestamp(start_date)])
                    hist = pd.concat([new_row, hist])
            
            # Calculate percentage change from start date
            initial_price = hist['Close'].iloc[0]
            pct_change = (hist['Close'] / initial_price - 1) * 100
            
            # Reindex to our date range and forward fill
            pct_change = pct_change.reindex(date_range).ffill()
            
            # Add to result DataFrame
            result_df[name] = pct_change
        else:
            print(f"  Warning: No data available for {name}")
    
    return result_df

def fetch_top_coins(limit=20):
    """Fetch top coins from CoinGecko."""
    url = f"{BASE_URL}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False,
        "x_cg_demo_api_key": COINGECKO_API_KEY  # Pass API key as query param
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch top coins: {str(e)}")
        return []

def fetch_historical_data(coin_id, days):
    """Fetch historical price data for a coin."""
    url = f"{BASE_URL}/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": str(days),
        "interval": "daily",
        "x_cg_demo_api_key": COINGECKO_API_KEY  # Pass API key as query param
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        prices = response.json().get("prices", [])
        print(f"Coin: {coin_id}, Days requested: {days}, Data points returned: {len(prices)}")
        if prices:
            print(f"  First 2 data points: {prices[:2]}")
        else:
            print(f"  No data returned for {coin_id}")
        return prices
    except Exception as e:
        print(f"Failed to fetch data for {coin_id}: {str(e)}")
        return []

def get_crypto_data(start_date):
    """Fetch data for cryptocurrencies with improved date handling."""
    # Get top coins
    coins = fetch_top_coins(limit=20)  # Fetches more to account for filtering
    
    # Define allowed crypto symbols
    allowed_symbols = ['btc', 'eth', 'xrp', 'bnb', 'sol', 'doge', 'sui']

    # Only include coins whose symbol is in the allowed list
    filtered_coins = []
    print('Fetched coins from CoinGecko:')
    for coin in coins:
        print(f"  Symbol: {coin['symbol']}, ID: {coin['id']}")
        if coin['symbol'].lower() in allowed_symbols:
            filtered_coins.append(coin)
    print(f"Filtered coins: {[coin['symbol'] for coin in filtered_coins]}")
    
    # Create a complete date range - ensure we start exactly on start_date
    date_range = pd.date_range(start=start_date, end=datetime.now(), freq='D')
    
    # Get historical data for each coin
    data = {}
    
    # Try to get data from a few days before to ensure we have the start date
    # buffer_start = start_date - timedelta(days=5) # This line will be removed/replaced by new logic
    
    for coin in filtered_coins:
        print(f"Fetching data for {coin['symbol']}...")

        # Calculate days for Coingecko API
        # 'start_date' is the liberation_day datetime object
        # 'days' param for Coingecko is "Data up to 'days' ago from today"
        today = datetime.now()
        # Ensure we are comparing dates only, without time component, for day calculation
        # .date() converts datetime to date, so time components are ignored in subtraction
        delta_days = (today.date() - start_date.date()).days

        if delta_days < 0:
            # start_date is in the future. Fetch 1 day of data (most recent).
            # This data will be filtered out by subsequent logic if it's before start_date.
            api_days_param = 1
        else:
            # start_date is today or in the past.
            # We need data from start_date up to today.
            # Request delta_days + 2 to potentially capture the true start_date if N+1 day windowing is tricky.
            # Example: If start_date is Apr 2, today is Apr 3. delta_days=1. We want Apr2, Apr3 (2 days data).
            # api_days_param = 1 + 1 = 2. If CG gives N+1 points, then for N=2, we get 3 points. If first is Today-N, then Apr3-2=Apr1. [Apr1,Apr2,Apr3]
            # Our previous logic: api_days_param = delta_days + 1
            api_days_param = delta_days + 2 # Fetch one more day to increase chance of getting start_date
            
        prices = fetch_historical_data(coin['id'], api_days_param) # Pass integer days
        
        if prices:
            df = pd.DataFrame(prices, columns=['timestamp', 'price'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True) # Ensure DF is sorted by timestamp index
            
            # Ensure we have a value at or first value after start_date
            if df[df.index >= start_date].empty:
                print(f"  Warning: No data for {coin['symbol']} on or after Liberation Day.")
                continue
            
            # Find the first date at or after start_date
            first_date_idx = df[df.index >= start_date].index[0]
            first_price = df.loc[first_date_idx, 'price']
            
            # If first date is after start_date, insert a point at start_date with the same price
            if first_date_idx.date() > start_date.date():
                print(f"  Adding artificial start point for {coin['symbol']} at Liberation Day")
                new_row = pd.DataFrame({'price': [first_price]}, index=[pd.Timestamp(start_date)])
                df = pd.concat([new_row, df])
            
            # Calculate percentage change from the start date
            df = df[df.index >= start_date]  # Keep only dates from start_date
            initial_price = df['price'].iloc[0]
            pct_changes = (df['price'] / initial_price - 1) * 100
            
            # Reindex to our date range and forward fill for any missing dates
            pct_changes = pct_changes.reindex(date_range).ffill()
            
            data[coin['symbol'].upper()] = pct_changes
        
        time.sleep(2)  # Slight delay between requests to avoid rate limits
    
    crypto_df = pd.DataFrame(data)
    print(f"crypto_data DataFrame shape: {crypto_df.shape}")
    return crypto_df

def _add_asset_trace(fig, series_data, asset_name, asset_color, x_axis_data):
    """Helper function to add a trace and annotation for an asset."""
    if series_data.empty:
        return

    fig.add_trace(go.Scatter(
        x=x_axis_data,
        y=series_data,
        name=asset_name,
        line=dict(color=asset_color, width=2),
        hovertemplate=f'%{{x|%Y-%m-%d}}<br>{asset_name}: %{{y:.2f}}%<extra></extra>',
        mode='lines+markers',
        marker=dict(size=4, opacity=0.6, color=asset_color)
    ))

    last_valid_idx = series_data.last_valid_index()
    if last_valid_idx is not None:
        last_valid_value = series_data[last_valid_idx]

        fig.add_trace(go.Scatter(
            x=[last_valid_idx],
            y=[last_valid_value],
            mode='markers',
            marker=dict(size=8, color=asset_color),
            showlegend=False,
            hoverinfo='skip'
        ))

        fig.add_annotation(
            x=last_valid_idx,
            y=last_valid_value,
            text=f"{asset_name}: {last_valid_value:.1f}%",
            showarrow=False,
            xshift=10,
            yshift=0,
            xanchor='left',
            yanchor='middle',
            font=dict(size=10, color=asset_color),
            align='left',
            bordercolor=asset_color,
            borderwidth=1,
            borderpad=4,
            bgcolor='rgba(255, 255, 255, 0.8)'
        )

def generate_liberation_day_chart():
    """Generate the liberation day performance chart with improved label positioning."""
    # Set the liberation day date
    liberation_day = datetime(2025, 4, 2)
    
    # Get data for both traditional and crypto assets
    print("Fetching traditional asset data...")
    traditional_data = get_traditional_assets_data(liberation_day)
    
    print("Fetching crypto data...")
    crypto_data = get_crypto_data(liberation_day)
    
    # Combine the data
    combined_data = pd.concat([traditional_data, crypto_data], axis=1)
    
    # Create the figure
    fig = go.Figure()
    
    # Define colors for traditional assets
    traditional_asset_colors = {
        'S&P 500': '#2E86C1',
        'Nasdaq 100': '#2874A6',
        'Gold': '#F1C40F',
    }
    
    # Add traditional assets
    for asset_name in traditional_data.columns:
        asset_color = traditional_asset_colors.get(asset_name, '#000000') # Default to black if not found
        _add_asset_trace(fig, combined_data[asset_name], asset_name, asset_color, combined_data.index)
    
    # Define colors for crypto assets
    crypto_asset_colors = ['#E74C3C', '#27AE60', '#8E44AD', '#F39C12', '#16A085',
                           '#D35400', '#2980B9', '#C0392B', '#1ABC9C', '#7D3C98']
    
    # Add crypto assets
    for i, asset_name in enumerate(crypto_data.columns):
        asset_color = crypto_asset_colors[i % len(crypto_asset_colors)]
        _add_asset_trace(fig, combined_data[asset_name], asset_name, asset_color, combined_data.index)
    
    # Update layout
    fig.update_layout(
        title='Asset Performance Since Liberation Day (April 2, 2025)',
        xaxis_title='Date',
        yaxis_title='Percentage Change (%)',
        hovermode='closest',
        showlegend=True,
        template='plotly_white',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02
        ),
        margin=dict(r=160),  # Extra right margin for end labels
        xaxis=dict(
            rangeslider=dict(visible=False),
            type='date'
        )
    )
    
    # Add a horizontal line at y=0
    fig.add_shape(
        type="line",
        x0=combined_data.index[0],
        y0=0,
        x1=combined_data.index[-1],
        y1=0,
        line=dict(color="gray", width=1, dash="dash")
    )
    
    # Save the chart
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                             'public', 'charts', 'liberation_day_performance.html')
    fig.write_html(
        output_path,
        include_plotlyjs='cdn',  # Use CDN version of plotly.js
        full_html=True,
        include_mathjax=False,
        validate=False,
        config={'displayModeBar': False}  # Hide the mode bar
    )
    
    print(f"Chart generated successfully: {output_path}")
    return output_path

if __name__ == "__main__":
    output_file = generate_liberation_day_chart()