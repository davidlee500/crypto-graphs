import requests
import time
from typing import Dict, List, Optional, Union
import logging

class CoinGeckoAPI:
    """A wrapper for the CoinGecko API with rate limiting."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = api_key
        self.last_request_time = 0
        self.min_request_interval = 6.0  # seconds between requests for free tier
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'  # Some APIs require a user agent
        }
        if self.api_key:
            headers['x-cg-pro-api-key'] = self.api_key
        return headers
    
    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            logging.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        self.last_request_time = time.time()
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make a rate-limited request to the API."""
        self._rate_limit()
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self._get_headers(), params=params)
            
            # Handle common API errors
            if response.status_code == 429:
                logging.warning("Rate limit exceeded. Waiting before retrying...")
                time.sleep(30)  # Wait 30 seconds before retrying
                return self._make_request(endpoint, params)
            
            if response.status_code == 403:
                raise Exception("API key invalid or expired")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {str(e)}")
            raise
    
    def get_coins_markets(self, vs_currency: str = 'usd', order: str = 'market_cap_desc',
                         per_page: int = 100, page: int = 1, sparkline: bool = False) -> List[Dict]:
        """Get cryptocurrency prices, market cap, volume, and market related data."""
        params = {
            'vs_currency': vs_currency,
            'order': order,
            'per_page': per_page,
            'page': page,
            'sparkline': sparkline,
            'x_cg_pro_api_key': self.api_key  # Some endpoints require the key in params
        }
        return self._make_request('coins/markets', params)
    
    def get_coin_market_chart_by_id(self, id: str, vs_currency: str = 'usd',
                                   days: Union[int, str] = 1) -> Dict:
        """Get historical market data including price, market cap, and 24h volume."""
        params = {
            "vs_currency": vs_currency,
            "days": str(days),
            "interval": "daily",
            "x_cg_demo_api_key": self.api_key  # <-- add this line
        }
        headers = {}  # <-- remove the header for the key
        return self._make_request(f'coins/{id}/market_chart', params)
    
    def get_coin_by_id(self, id: str) -> Dict:
        """Get current data for a coin by its ID."""
        params = {
            'x_cg_pro_api_key': self.api_key  # Some endpoints require the key in params
        }
        return self._make_request(f'coins/{id}', params)

print(f"Using CoinGecko API key: {COINGECKO_API_KEY}") 