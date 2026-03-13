"""Tests for DataFetcher class"""

import pytest
from unittest.mock import Mock, patch
import pandas as pd
from src.data_fetcher import DataFetcher


def test_get_sp500_tickers():
    """Test that S&P 500 tickers are fetched successfully"""
    # Mock the pandas read_html to return a sample S&P 500 list
    mock_df = pd.DataFrame({"Symbol": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]})

    with patch("pandas.read_html", return_value=[mock_df]):
        fetcher = DataFetcher()
        tickers = fetcher.get_sp500_tickers()

        assert len(tickers) == 5
        assert "AAPL" in tickers
        assert "MSFT" in tickers
        assert "GOOGL" in tickers


def test_get_sp500_tickers_dotted_symbols():
    """Test that tickers with dots are converted to hyphens (BRK.B -> BRK-B)"""
    mock_df = pd.DataFrame({"Symbol": ["BRK.B", "BF.B"]})

    with patch("pandas.read_html", return_value=[mock_df]):
        fetcher = DataFetcher()
        tickers = fetcher.get_sp500_tickers()

        assert "BRK-B" in tickers
        assert "BF-B" in tickers
        assert "BRK.B" not in tickers
        assert "BF.B" not in tickers


def create_mock_ticker_info():
    """Create a mock yfinance Ticker object with necessary data"""
    mock_ticker = Mock()

    # Mock info dict
    mock_ticker.info = {
        "longName": "Apple Inc.",
        "sector": "Technology",
        "effectiveTaxRate": 0.21,
        "totalCash": 50000000000,
    }

    # Mock financials (income statement)
    # yfinance returns DataFrame with dates as columns and line items as index
    mock_ticker.financials = pd.DataFrame(
        [[100000000000], [25000000000], [30000000000], [32000000000], [-1000000000]],
        index=[
            "Total Revenue",
            "Net Income",
            "Operating Income",
            "EBIT",
            "Interest Expense",
        ],
        columns=["2024-12-31"],
    )

    # Mock balance sheet
    mock_ticker.balance_sheet = pd.DataFrame(
        [[200000000000]], index=["Total Assets"], columns=["2024-12-31"]
    )

    # Mock cashflow
    mock_ticker.cashflow = pd.DataFrame(
        [[25000000000]], index=["Free Cash Flow"], columns=["2024-12-31"]
    )

    return mock_ticker


def test_get_financial_metrics_all_metrics():
    """Test that all 5 metrics are extracted correctly"""
    mock_ticker = create_mock_ticker_info()

    with patch("yfinance.Ticker", return_value=mock_ticker):
        fetcher = DataFetcher()
        metrics = fetcher.get_financial_metrics("AAPL")

        assert metrics is not None
        assert metrics["ticker"] == "AAPL"
        assert metrics["name"] == "Apple Inc."
        assert metrics["sector"] == "Technology"

        # Check all 5 metrics are present
        assert "profit_margin" in metrics
        assert metrics["profit_margin"] == 0.25  # 25B / 100B

        assert "operating_margin" in metrics
        assert metrics["operating_margin"] == 0.30  # 30B / 100B

        assert "free_cash_flow" in metrics
        assert metrics["free_cash_flow"] == 25000000000

        assert "roic" in metrics
        # NOPAT = 30B * (1-0.21) = 23.7B, Invested Capital = 200B - 50B = 150B
        expected_roic = (30000000000 * 0.79) / (200000000000 - 50000000000)
        assert abs(metrics["roic"] - expected_roic) < 0.0001

        assert "interest_coverage" in metrics
        assert metrics["interest_coverage"] == 32.0  # 32B / 1B


def test_get_financial_metrics_handles_zero_denominator():
    """Test that division by zero returns None"""
    mock_ticker = Mock()

    mock_ticker.info = {
        "longName": "Test Corp",
        "sector": "Test",
        "effectiveTaxRate": 0.21,
        "totalCash": 0,
    }

    # Revenue is 0, should cause profit_margin and operating_margin to be None
    mock_ticker.financials = pd.DataFrame(
        [[0], [0], [0], [0], [0]],
        index=[
            "Total Revenue",
            "Net Income",
            "Operating Income",
            "EBIT",
            "Interest Expense",
        ],
        columns=["2024-12-31"],
    )

    mock_ticker.balance_sheet = pd.DataFrame(
        [[0]], index=["Total Assets"], columns=["2024-12-31"]
    )

    mock_ticker.cashflow = pd.DataFrame(
        [[0]], index=["Free Cash Flow"], columns=["2024-12-31"]
    )

    with patch("yfinance.Ticker", return_value=mock_ticker):
        fetcher = DataFetcher()
        metrics = fetcher.get_financial_metrics("TEST")

        assert metrics is not None
        # When division by zero or invalid data, metric keys are not added
        assert "profit_margin" not in metrics or metrics.get("profit_margin") is None
        assert (
            "operating_margin" not in metrics or metrics.get("operating_margin") is None
        )
        assert (
            "roic" not in metrics or metrics.get("roic") is None
        )  # invested capital would be 0
        assert (
            "interest_coverage" not in metrics
            or metrics.get("interest_coverage") is None
        )  # division by zero


def test_get_financial_metrics_handles_exception():
    """Test that get_financial_metrics returns None on exception"""
    with patch("yfinance.Ticker", side_effect=Exception("API Error")):
        fetcher = DataFetcher()
        metrics = fetcher.get_financial_metrics("INVALID")
        assert metrics is None


def test_fetch_multiple():
    """Test fetch_multiple returns only successful results"""
    mock_ticker1 = create_mock_ticker_info()
    mock_ticker2 = create_mock_ticker_info()
    mock_ticker2.info["longName"] = "Microsoft Corp"

    # Third ticker fails
    with patch(
        "yfinance.Ticker", side_effect=[mock_ticker1, mock_ticker2, Exception("Error")]
    ):
        fetcher = DataFetcher()
        results = fetcher.fetch_multiple(["AAPL", "MSFT", "INVALID"])

        assert len(results) == 2
        tickers = [r["ticker"] for r in results]
        assert "AAPL" in tickers
        assert "MSFT" in tickers
