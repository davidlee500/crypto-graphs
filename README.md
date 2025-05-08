# Crypto Graphs

**Project Owner:** David Lee (davidlee500@gmail.com)  
**Live Site:** [crypto-graphs on GitHub Pages](https://davidlee500.github.io/crypto-graphs/)  
**Repository:** [davidlee500/crypto-graphs](https://github.com/davidlee500/crypto-graphs)

---

## Project Overview

Crypto Graphs is a free, automated website that hosts multiple crypto market charts. The site features a modern, single-page interface with sidebar navigation, allowing users to dynamically load and view charts without page reloads. It began with a chart visualizing the average performance of major cryptocurrencies (BTC, ETH, and TOTAL3) following significant market cap drops and is designed for easy expansion. The site is updated daily using GitHub Actions.

- **Data Source:** CoinGecko API (free tier, API key required).
- **Automation:** Daily updates via GitHub Actions workflow.
- **Hosting:** GitHub Pages (serves the main `index.html` single-page application which dynamically loads generated HTML charts).

---

## Project Structure

```
crypto-graphs/
├── src/
│   ├── charts/          # Chart generation scripts
│   ├── utils/           # Utility modules
│   └── config.py        # Configuration settings
├── data/
│   ├── raw/            # Raw data storage
│   └── processed/      # Processed data storage
├── public/
│   ├── charts/         # Generated chart files
│   └── css/           # Stylesheets
├── logs/              # Log files
├── tests/            # Test files
├── requirements.txt  # Python dependencies
├── index.html        # Main single-page application interface (loads charts dynamically)
└── README.md        # This file
```

---

## Chart Summaries

### Chart 1: Average Performance After >10% Market Cap Drop

- **Filename:** `crypto_performance.html`
- **Description:**  
  Visualizes the average percentage change in BTC (orange), ETH (purple), and TOTAL3 (blue) over 90 days following >10% drops in the total crypto market cap.
- **Requirements:**  
  - **Drop Event:** >10% drop in total market cap within 7 days; Day 0 = lowest point.
  - **Timeframe:** Past 1 year (e.g., Feb 2024–Feb 2025).
  - **Data:** Daily BTC price, ETH price, TOTAL3 market cap (top 200 coins minus BTC/ETH).
  - **X-axis:** Days 0–90 after drop.
  - **Y-axis:** % change from Day 0.
  - **Legend:** BTC, ETH, TOTAL3.
  - **Update Frequency:** Daily (automated).
  - **Hosting:** [crypto_performance.html](https://davidlee500.github.io/crypto-graphs/public/charts/crypto_performance.html) (Viewed within the main site interface)

### Chart 2: Top 50 Coins Performance Since Trump Election

- **Filename:** `trump_election_performance.html`
- **Description:**  
  Interactive scatter plot showing price performance of top 50 cryptocurrencies since November 4, 2024, excluding stablecoins and wrapped tokens. Visualizes the relationship between market cap and price change, with color-coding for positive (blue) and negative (red) performance.
- **Requirements:**  
  - **Data Source:** CoinGecko API (historical and current prices).
  - **Timeframe:** November 4, 2024 to current date.
  - **Coins:** Top 50 by market cap (excluding stablecoins and wrapped tokens).
  - **X-axis:** Market cap (USD, log scale, Nov 4, 2024).
  - **Y-axis:** Percentage price change from Nov 4, 2024.
  - **Visualization:** 
    - Scatter plot with fixed-size markers (size 12, opacity 0.8).
    - Color-coded: blue (≥0%), red (<0%).
    - Interactive hover details (name, market cap, prices, % change).
    - Reference line at y=0.
  - **Update Frequency:** Daily (automated).
  - **Hosting:** [trump_election_performance.html](https://davidlee500.github.io/crypto-graphs/public/charts/trump_election_performance.html) (Viewed within the main site interface)

### Chart 3: Top 10 Cryptocurrencies and Traditional Assets Performance Since Liberation Day

- **Filename:** `liberation_day_performance.html`
- **Description:**  
  Interactive line chart tracking the percentage price changes of the top 10 cryptocurrencies (by market cap) alongside traditional assets (Gold, S&P 500, and Nasdaq 100) since Liberation Day (April 2nd, 2025). Each asset is represented by a distinctly colored line showing its performance over time.
- **Requirements:**  
  - **Data Sources:** 
    - CoinGecko API (for cryptocurrency historical and current prices)
    - Financial APIs (for Gold, S&P 500, and Nasdaq 100 data)
  - **Timeframe:** April 2, 2025 (Liberation Day) to current date.
  - **Assets:** 
    - Top 10 cryptocurrencies by market cap as of Liberation Day (excluding stablecoins and wrapped tokens)
    - Gold price
    - S&P 500 index
    - Nasdaq 100 index
  - **X-axis:** Days since Liberation Day.
  - **Y-axis:** Percentage price change from Liberation Day.
  - **Visualization:** 
    - Line chart with each asset having its own distinct color.
    - Interactive hover details showing date, asset name, and percentage change.
    - Complete legend identifying each cryptocurrency and traditional asset.
    - Option to toggle visibility of individual assets.
  - **Update Frequency:** Daily (automated).
  - **Hosting:** [liberation_day_performance.html](https://davidlee500.github.io/crypto-graphs/public/charts/liberation_day_performance.html) (Viewed within the main site interface)
---

## Goals & Requirements

### Core Goals

- **Automate** daily data fetching, processing, and chart generation.
- **Visualize** key crypto market events and trends.
- **Keep the site simple, scalable, and free** (no paid services or complex infrastructure).
- **Enable easy addition of new charts** (e.g., altcoin trends) in the future.

### Technical Requirements

- **Python** (for data processing and chart generation).
- **Plotly** (for interactive charts, using CDN to minimize HTML size).
- **CoinGecko API** (API key via environment variable or GitHub secret).
- **GitHub Actions** (for daily automation, using a Personal Access Token for push).
- **GitHub Pages** (serves the site from the repository root; the main page is `index.html`, a single-page application that dynamically loads individual chart HTML files from `public/charts/` into an iframe).

---

## Setup & Development

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the charts:
```bash
./run_charts.py
```

Or run individual charts:
```bash
python src/charts/crypto_performance.py
python src/charts/trump_election.py
```

---

## Credentials & Secrets

- **CoinGecko API Key:**  
  - Set as `COINGECKO_API_KEY` in GitHub repository secrets for automation.
- **GitHub PAT:**  
  - Set as `GH_TOKEN` in repository secrets for workflow push access.

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

---

## Contact

For questions or contributions, contact David Lee (davidlee500@gmail.com) or open an issue on GitHub.

---

*This README is structured for both human and AI agent consumption. It summarizes the project, its goals, requirements, current state, and next steps to enable seamless continuation or expansion.*