"""Main stock agent logic"""

import json
from pathlib import Path
from src.data_fetcher import DataFetcher
from src.analyzer import Analyzer


class StockAgent:
    """Coordinates stock analysis workflow"""

    def __init__(self, data_fetcher: DataFetcher):
        self.data_fetcher = data_fetcher

    def run_analysis(self, universe: str = "sp500") -> dict:
        """Run full analysis on stock universe

        Args:
            universe: Stock universe to analyze (currently only 'sp500' supported)

        Returns:
            Dictionary of rankings by metric
        """
        # Get tickers for the universe
        if universe.lower() == "sp500":
            tickers = self.data_fetcher.get_sp500_tickers()
        else:
            raise ValueError(f"Unsupported universe: {universe}")

        # Fetch metrics for all tickers
        metrics_list = self.data_fetcher.fetch_multiple(tickers)

        # Analyze and rank
        analyzer = Analyzer()
        rankings = analyzer.analyze(metrics_list)

        # Save results to output directory
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"rankings_{universe}.json"
        with open(output_file, "w") as f:
            json.dump(rankings, f, indent=2)

        return rankings
