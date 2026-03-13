"""Analyzes and ranks stocks by financial metrics"""

from typing import List, Dict, Any


class Analyzer:
    """Processes metrics and generates rankings"""

    METRICS = [
        "profit_margin",
        "operating_margin",
        "free_cash_flow",
        "roic",
        "interest_coverage",
    ]

    def analyze(
        self, metrics_list: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze metrics and return rankings by category

        Args:
            metrics_list: List of dictionaries containing stock metrics

        Returns:
            Dictionary mapping metric names to ranked lists of stocks
        """
        rankings = {}

        for metric in self.METRICS:
            # Filter out entries with None or missing metric
            valid_entries = [
                entry
                for entry in metrics_list
                if metric in entry and entry[metric] is not None
            ]

            # Sort descending (higher is better)
            sorted_entries = sorted(
                valid_entries, key=lambda x: x[metric], reverse=True
            )

            # Take top 10
            rankings[metric] = sorted_entries[:10]

        return rankings
