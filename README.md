# Crypto Graphs

**Project Owner:** David Lee (davidlee500@gmail.com)  
**Live Site:** [crypto-graphs on GitHub Pages](https://davidlee500.github.io/crypto-graphs/crypto_performance.html)  
**Repository:** [davidlee500/crypto-graphs](https://github.com/davidlee500/crypto-graphs)

---

## Project Overview

Crypto Graphs is a free, automated website that hosts multiple crypto market charts, starting with a chart that visualizes the average performance of major cryptocurrencies (BTC, ETH, and TOTAL3) following significant market cap drops. The site is designed for easy expansion to additional charts and is updated daily using GitHub Actions.

- **Data Source:** CoinGecko API (free tier, API key required).
- **Automation:** Daily updates via GitHub Actions workflow.
- **Hosting:** GitHub Pages (serves generated HTML charts).

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
  - **Hosting:** [crypto_performance.html](https://davidlee500.github.io/crypto-graphs/crypto_performance.html)

---

<!-- Template for future charts: Copy and fill in for each new chart -->
### Chart 2: [Chart Title Here]

- **Filename:** `[your_chart_file.html]`
- **Description:**  
  [Brief description of what this chart shows.]
- **Requirements:**  
  - [List requirements for this chart, e.g., data sources, event definitions, axes, update frequency, etc.]
  - **Hosting:** [link to chart file]

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
- **GitHub Pages** (serves HTML files from the root directory or a `charts/` directory).

---

## Current State

- **Codebase:**  
  - `update_chart.py`: Fetches top 200 coins, processes 1 year of data, generates `crypto_performance.html`.
  - `historical_data.json`: Cached raw data for reproducibility and debugging.
  - `.github/workflows/update_chart.yml`: GitHub Actions workflow for daily automation.
  - `requirements.txt`: Python dependencies.
- **Charts:**  
  - [crypto_performance.html](https://davidlee500.github.io/crypto-graphs/crypto_performance.html) (auto-updated daily)
- **Automation:**  
  - Workflow runs daily at midnight UTC, commits new chart/data if changed.
  - Uses repository secret `GH_TOKEN` for push authentication.
  - CoinGecko API key is set as `COINGECKO_API_KEY` secret.
- **Hosting:**  
  - GitHub Pages serves HTML files from the root directory.
  - Main chart is accessible at `/crypto_performance.html`.
- **Scalability:**  
  - Site structure supports adding more charts (e.g., place new charts in a `charts/` directory and link from a main `index.html` dashboard).

---

## How to Continue or Expand

1. **Add New Charts:**  
   - Create new Python scripts to generate additional HTML charts.
   - Place new charts in a `charts/` directory.
   - Update or create `index.html` to link to all available charts.

2. **Improve Data Processing:**  
   - Optimize data fetching (e.g., reduce API calls, handle rate limits).
   - Add error handling and logging for robustness.

3. **Enhance Visualization:**  
   - Add tooltips, annotations, or additional metrics as needed.
   - Consider user feedback for new features.

4. **Maintain Automation:**  
   - Ensure GitHub Actions workflow remains functional (update secrets if needed).
   - Monitor for API changes or quota issues.

---

## Setup & Development

- **Clone the repo:**  
  `git clone https://github.com/davidlee500/crypto-graphs.git`
- **Install dependencies:**  
  `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
- **Run locally:**  
  `python update_chart.py` (requires `COINGECKO_API_KEY` in environment)
- **Manual workflow run:**  
  Trigger via GitHub Actions tab if needed.

---

## Credentials & Secrets

- **CoinGecko API Key:**  
  - Set as `COINGECKO_API_KEY` in GitHub repository secrets for automation.
- **GitHub PAT:**  
  - Set as `GH_TOKEN` in repository secrets for workflow push access.

---

## Contact

For questions or contributions, contact David Lee (davidlee500@gmail.com) or open an issue on GitHub.

---

*This README is structured for both human and AI agent consumption. It summarizes the project, its goals, requirements, current state, and next steps to enable seamless continuation or expansion.*