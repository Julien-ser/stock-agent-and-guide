"""Tests for Analyzer class"""

import pytest
from src.analyzer import Analyzer


def test_analyzer_ranks_stocks_by_profit_margin():
    """Test that Analyzer correctly ranks stocks by profit margin"""
    analyzer = Analyzer()

    metrics_list = [
        {"ticker": "AAPL", "profit_margin": 0.25},
        {"ticker": "MSFT", "profit_margin": 0.40},
        {"ticker": "GOOGL", "profit_margin": 0.30},
    ]

    rankings = analyzer.analyze(metrics_list)

    assert "profit_margin" in rankings
    assert len(rankings["profit_margin"]) == 3
    # Should be sorted descending
    assert rankings["profit_margin"][0]["ticker"] == "MSFT"
    assert rankings["profit_margin"][1]["ticker"] == "GOOGL"
    assert rankings["profit_margin"][2]["ticker"] == "AAPL"


def test_analyzer_handles_missing_metrics():
    """Test that Analyzer filters out stocks with None or missing metrics"""
    analyzer = Analyzer()

    metrics_list = [
        {"ticker": "AAPL", "profit_margin": 0.25},
        {"ticker": "MSFT", "profit_margin": None},
        {"ticker": "GOOGL"},  # missing profit_margin
        {"ticker": "TSLA", "profit_margin": 0.15},
    ]

    rankings = analyzer.analyze(metrics_list)

    assert len(rankings["profit_margin"]) == 2
    tickers = [s["ticker"] for s in rankings["profit_margin"]]
    assert "AAPL" in tickers
    assert "TSLA" in tickers
    assert "MSFT" not in tickers
    assert "GOOGL" not in tickers


def test_analyzer_multiple_metrics():
    """Test that Analyzer ranks by all 5 metrics"""
    analyzer = Analyzer()

    metrics_list = [
        {
            "ticker": "AAPL",
            "profit_margin": 0.25,
            "operating_margin": 0.30,
            "free_cash_flow": 100000000000,
            "roic": 0.20,
            "interest_coverage": 50.0,
        },
        {
            "ticker": "MSFT",
            "profit_margin": 0.40,
            "operating_margin": 0.45,
            "free_cash_flow": 150000000000,
            "roic": 0.30,
            "interest_coverage": 60.0,
        },
    ]

    rankings = analyzer.analyze(metrics_list)

    # Should have all 5 metrics
    assert set(rankings.keys()) == set(analyzer.METRICS)

    # Each should have both stocks (top 10 limit not hit)
    for metric in analyzer.METRICS:
        assert len(rankings[metric]) == 2

    # MSFT should be first in all rankings (higher values)
    for metric in analyzer.METRICS:
        assert rankings[metric][0]["ticker"] == "MSFT"


def test_analyzer_limits_to_top_10():
    """Test that Analyzer returns at most 10 stocks per metric"""
    analyzer = Analyzer()

    # Create 15 stocks with varying profit margins
    metrics_list = [
        {"ticker": f"STOCK{i}", "profit_margin": i / 100.0} for i in range(15)
    ]

    rankings = analyzer.analyze(metrics_list)

    assert len(rankings["profit_margin"]) == 10
    # Highest should be STOCK14 (0.14)
    assert rankings["profit_margin"][0]["ticker"] == "STOCK14"
    # Lowest in top 10 should be STOCK5 (0.05)
    assert rankings["profit_margin"][-1]["ticker"] == "STOCK5"


def test_analyzer_metric_constants():
    """Test that Analyzer has correct metric constants"""
    analyzer = Analyzer()

    expected_metrics = [
        "profit_margin",
        "operating_margin",
        "free_cash_flow",
        "roic",
        "interest_coverage",
    ]

    assert analyzer.METRICS == expected_metrics
