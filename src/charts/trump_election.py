import requests
import time
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime
import os
import logging
import sys
import concurrent.futures
from typing import List, Dict, Any
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('trump_election_chart.log')
    ]
)

# Constants
BASE_URL = "https://api.coingecko.com/api/v3"
API_KEY = os.getenv("COINGECKO_API_KEY", "CG-1KR3Wbo6yQfvUD9EHQoeECet")
START_DATE = "04-11-2024"  # November 4, 2024 (Trump Election)
HTML_FILE = "public/charts/trump_election_performance.html"
REQUEST_DELAY = 5  # Fixed 5 second delay between requests

# List of coins to exclude (stablecoins and wrapped tokens)
EXCLUDED_COINS = {
    'tether', 'usd-coin', 'wrapped-bitcoin', 'dai', 'true-usd', 'usdd',
    'paxos-standard', 'gemini-dollar', 'wrapped-ether', 'staked-ether',
    'wrapped-staked-ether'
}

def make_request(url):
    """Make API request with fixed delay"""
    try:
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Error {response.status_code} for {url}")
            return None
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error making request to {url}: {str(e)}")
        return None

def fetch_top_coins(limit=50) -> List[Dict[str, Any]]:
    """Fetch top coins by market cap, excluding stablecoins and wrapped tokens."""
    url = f"{BASE_URL}/coins/markets"
    headers = {"x-cg-demo-api-key": API_KEY}
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": False
    }
    
    all_coins = []
    page = 1
    
    while len(all_coins) < limit and page <= 1:
        params["page"] = page
        try:
            start_time = time.time()
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            coins = response.json()
            
            # Filter out excluded coins
            filtered_coins = [coin for coin in coins if coin["id"] not in EXCLUDED_COINS]
            all_coins.extend(filtered_coins)
            
            elapsed_time = time.time() - start_time
            logging.info(f"Fetched {len(filtered_coins)} coins from page {page} in {elapsed_time:.2f} seconds")
            page += 1
            time.sleep(REQUEST_DELAY)
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching page {page}: {e}")
            if hasattr(e.response, 'status_code'):
                logging.error(f"Status code: {e.response.status_code}")
            break
    
    if not all_coins:
        logging.error("No coins were fetched. Exiting.")
        sys.exit(1)
        
    logging.info(f"Total coins fetched: {len(all_coins)}")
    return all_coins[:limit]

def fetch_historical_price(coin_id: str, date: str) -> float:
    """Fetch historical price for a specific coin and date."""
    url = f"{BASE_URL}/coins/{coin_id}/history"
    headers = {"x-cg-demo-api-key": API_KEY}
    params = {"date": date}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            logging.error(f"Error fetching historical price for {coin_id}: {response.status_code}")
            return None
        data = response.json()
        time.sleep(REQUEST_DELAY)  # Fixed delay after each request
        return data["market_data"]["current_price"]["usd"]
    except (requests.exceptions.RequestException, KeyError) as e:
        logging.error(f"Error fetching historical price for {coin_id}: {e}")
        return None

def format_price(price):
    """Format price with appropriate decimal places."""
    if price >= 0.01:
        return f"${price:.2f}"
    else:
        return f"${price:.3g}"

def format_market_cap(market_cap):
    """Format market cap with appropriate suffix."""
    if market_cap >= 1e12:
        return f"${market_cap/1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap/1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap/1e6:.2f}M"
    elif market_cap >= 1e3:
        return f"${market_cap/1e3:.2f}K"
    else:
        return f"${market_cap:.2f}"

def create_scatter_plot(df):
    """Create the interactive scatter plot."""
    if df.empty:
        logging.error("No data to plot. DataFrame is empty.")
        return
        
    # Simplified color scheme - just red for negative, blue for positive
    colors = df['percent_change'].apply(lambda x: 'red' if x < 0 else 'blue')
    
    # Create trace
    trace = go.Scatter(
        x=df['market_cap'],
        y=df['percent_change'],
        mode='markers',
        marker=dict(
            size=12,
            color=colors,
            opacity=0.8,
            line=dict(width=1, color='black')
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" +
            "Market Cap: %{customdata[1]}<br>" +
            "Nov 4 Price: %{customdata[2]}<br>" +
            "Current Price: %{customdata[3]}<br>" +
            "Change: %{customdata[4]}%<extra></extra>"
        ),
        customdata=df[['name', 'market_cap_formatted', 'start_price_formatted', 
                       'current_price_formatted', 'percent_change_rounded']].values
    )
    
    # Create zero line
    zero_line = go.Scatter(
        x=[df['market_cap'].min(), df['market_cap'].max()],
        y=[0, 0],
        mode='lines',
        line=dict(color='black', width=1, dash='dash'),
        showlegend=False
    )
    
    # Calculate y-axis range with some padding
    y_min = df['percent_change'].min() * 1.1  # Add 10% padding
    y_max = df['percent_change'].max() * 1.1  # Add 10% padding
    
    # Create layout
    layout = go.Layout(
        title=f"Top 50 Coins Performance Since Trump Election (Nov 4, 2024 - {datetime.now().strftime('%Y-%m-%d')})",
        xaxis=dict(
            title="Market Cap (USD, Nov 4, 2024)",
            type="log",  # Keep log scale for market cap
            showgrid=True
        ),
        yaxis=dict(
            title="Percent Price Change",
            type="linear",  # Changed to linear scale
            showgrid=True,
            range=[y_min, y_max],  # Set explicit range
            tickformat=".0f",  # Format as whole numbers
            ticksuffix="%"  # Add % suffix to ticks
        ),
        showlegend=False,
        hovermode='closest',
        template="simple_white",
        annotations=[{
            'text': 'Red: Negative Change, Blue: Positive Change',
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper',
            'x': 0,
            'y': 1.05
        }]
    )
    
    # Create figure
    fig = go.Figure(data=[trace, zero_line], layout=layout)
    
    # Save to HTML
    try:
        fig.write_html(
            HTML_FILE,
            include_plotlyjs='cdn',
            full_html=True,
            include_mathjax=False,
            config={'displayModeBar': False}
        )
        logging.info(f"Chart saved to {HTML_FILE}")
    except Exception as e:
        logging.error(f"Error saving chart: {e}")
        sys.exit(1)

def process_coin(coin: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single coin's data."""
    coin_id = coin['id']
    current_price = coin['current_price']
    market_cap = coin['market_cap']
    
    # Fetch historical price
    start_price = fetch_historical_price(coin_id, START_DATE)
    if start_price is None:
        return None
    
    # Calculate percent change
    percent_change = ((current_price - start_price) / start_price) * 100
    
    return {
        'id': coin_id,
        'name': coin['name'],
        'market_cap': market_cap,
        'market_cap_formatted': format_market_cap(market_cap),
        'start_price': start_price,
        'start_price_formatted': format_price(start_price),
        'current_price': current_price,
        'current_price_formatted': format_price(current_price),
        'percent_change': percent_change,
        'percent_change_rounded': round(percent_change)
    }

def main():
    try:
        # Fetch top coins
        logging.info("Starting to fetch top coins...")
        coins = fetch_top_coins(limit=50)
        
        # Process coins sequentially
        data = []
        for coin in coins:
            result = process_coin(coin)
            if result is not None:
                data.append(result)
                logging.info(f"Processed {result['id']}")
            time.sleep(REQUEST_DELAY)  # Fixed delay between processing each coin
        
        if not data:
            logging.error("No valid data collected. Exiting.")
            sys.exit(1)
            
        # Create DataFrame
        df = pd.DataFrame(data)
        logging.info(f"Created DataFrame with {len(df)} coins")
        
        # Create and save the chart
        create_scatter_plot(df)
        
        logging.info("Script completed successfully")
        
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 