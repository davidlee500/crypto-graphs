#!/usr/bin/env python3
"""
Script to run all chart generation scripts.
"""
import sys
import logging
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.append(str(src_dir))

from charts import crypto_performance, trump_election, liberation_day_performance

def main():
    try:
        # Run crypto performance chart
        print("Generating crypto performance chart...")
        crypto_performance.main()
        
        # Run Trump election chart
        print("Generating Trump election chart...")
        trump_election.main()
        
        # Run Liberation Day performance chart
        print("Generating Liberation Day performance chart...")
        liberation_day_performance.generate_liberation_day_chart()
        
        print("All charts generated successfully!")
        
    except Exception as e:
        logging.error(f"Error generating charts: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 