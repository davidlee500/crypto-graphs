import unittest
from datetime import datetime
from src.utils.api import fetch_top_coins, fetch_historical_price
from src.utils.data_processing import format_price, format_market_cap

class TestAPI(unittest.TestCase):
    def test_fetch_top_coins(self):
        coins = fetch_top_coins(limit=10)
        self.assertIsInstance(coins, list)
        self.assertLessEqual(len(coins), 10)
        if coins:
            self.assertIn('id', coins[0])
            self.assertIn('symbol', coins[0])
            self.assertIn('name', coins[0])

    def test_fetch_historical_price(self):
        # Test with Bitcoin
        price = fetch_historical_price('bitcoin', '2024-01-01')
        self.assertIsInstance(price, (float, type(None)))
        if price is not None:
            self.assertGreater(price, 0)

class TestDataProcessing(unittest.TestCase):
    def test_format_price(self):
        self.assertEqual(format_price(1234.5678), '$1,234.57')
        self.assertEqual(format_price(0.00012345), '$0.000123')
        self.assertEqual(format_price(1000000), '$1,000,000.00')

    def test_format_market_cap(self):
        self.assertEqual(format_market_cap(1000000000), '$1.00B')
        self.assertEqual(format_market_cap(1000000), '$1.00M')
        self.assertEqual(format_market_cap(1000), '$1.00K')
        self.assertEqual(format_market_cap(1000000000000), '$1.00T')

if __name__ == '__main__':
    unittest.main() 