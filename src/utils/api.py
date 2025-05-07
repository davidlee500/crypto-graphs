import requests
import time
import logging
import os
from typing import List, Dict, Any, Optional

# Constants
BASE_URL = "https://api.coingecko.com/api/v3"
API_KEY = os.getenv("COINGECKO_API_KEY", "CG-1KR3Wbo6yQfvUD9EHQoeECet")
REQUEST_DELAY = 5  # Fixed 5 second delay between requests

# List of coins to exclude (stablecoins and wrapped tokens)
EXCLUDED_COINS = {
    'tether', 'usd-coin', 'wrapped-bitcoin', 'dai', 'true-usd', 'usdd',
    'paxos-standard', 'gemini-dollar', 'wrapped-ether', 'staked-ether',
    'wrapped-staked-ether'
}

def make_request(url: str) -> Optional[Dict]:
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

def fetch_top_coins(limit: int = 200) -> List[Dict[str, Any]]:
    """Fetch top coins by market cap, excluding stablecoins and wrapped tokens."""
    url = f"{BASE_URL}/coins/markets"
    headers = {"x-cg-demo-api-key": API_KEY}
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": False
    }
    
    all_coins = []
    page = 1
    
    while len(all_coins) < limit and page <= 2:
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
        logging.error("No coins were fetched.")
        return []
        
    logging.info(f"Total coins fetched: {len(all_coins)}")
    return all_coins[:limit]

def fetch_historical_price(coin_id: str, date: str) -> Optional[float]:
    """
    Fetch historical price for a specific coin and date.
    
    Args:
        coin_id (str): The CoinGecko ID of the coin
        date (str): Date in dd-mm-yyyy format
        
    Returns:
        Optional[float]: The historical price in USD, or None if not available
    """
    url = f"{BASE_URL}/coins/{coin_id}/history"
    headers = {"x-cg-demo-api-key": API_KEY}
    params = {"date": date}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise exception for non-200 status codes
        data = response.json()
        
        # Check if market_data exists and has price information
        if "market_data" not in data:
            logging.info(f"No market data available for {coin_id} on {date}")
            return None
            
        if "current_price" not in data["market_data"]:
            logging.info(f"No price data available for {coin_id} on {date}")
            return None
            
        if "usd" not in data["market_data"]["current_price"]:
            logging.info(f"No USD price available for {coin_id} on {date}")
            return None
            
        price = data["market_data"]["current_price"]["usd"]
        if not isinstance(price, (int, float)) or price < 0:
            logging.warning(f"Invalid price value for {coin_id} on {date}: {price}")
            return None
            
        time.sleep(REQUEST_DELAY)  # Fixed delay after each request
        return price
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            logging.error(f"Rate limit exceeded for {coin_id}: {e}")
        else:
            logging.error(f"HTTP error for {coin_id}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Network error for {coin_id}: {e}")
        return None
    except (KeyError, ValueError, TypeError) as e:
        logging.error(f"Data parsing error for {coin_id}: {e}")
        return None 