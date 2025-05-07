from typing import Dict, Any, List
import pandas as pd
import logging

def format_price(price: float) -> str:
    """Format price with appropriate decimal places."""
    if price >= 0.01:
        return f"${price:.2f}"
    else:
        return f"${price:.3g}"

def format_market_cap(market_cap: float) -> str:
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

def process_coin_data(coin: Dict[str, Any], start_price: float) -> Dict[str, Any]:
    """Process a single coin's data for visualization."""
    current_price = coin['current_price']
    market_cap = coin['market_cap']
    
    # Calculate percent change
    percent_change = ((current_price - start_price) / start_price) * 100
    
    return {
        'id': coin['id'],
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

def create_performance_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create a DataFrame from processed coin data."""
    if not data:
        logging.error("No data to create DataFrame")
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    logging.info(f"Created DataFrame with {len(df)} coins")
    return df 