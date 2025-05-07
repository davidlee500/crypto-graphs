import os
from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Public directories
PUBLIC_DIR = PROJECT_ROOT / "public"
CHARTS_DIR = PUBLIC_DIR / "charts"
CSS_DIR = PUBLIC_DIR / "css"

# Log directory
LOG_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, 
                 PUBLIC_DIR, CHARTS_DIR, CSS_DIR, LOG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY", "CG-1KR3Wbo6yQfvUD9EHQoeECet")
REQUEST_DELAY = 5  # seconds between API requests

# Chart Configuration
START_DATE = "04-11-2024"  # November 4, 2024 (Trump Election)
HTML_FILE = CHARTS_DIR / "trump_election_performance.html"
CRYPTO_PERFORMANCE_FILE = CHARTS_DIR / "crypto_performance.html"

# Logging Configuration
LOG_FILE = LOG_DIR / "trump_election_chart.log" 