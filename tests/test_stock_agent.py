"""Tests for StockAgent class"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.stock_agent import StockAgent


def test_stock_agent_run_analysis_sp500():
    """Test that run_analysis executes the full workflow for S&P 500"""
    # Create mocks
    mock_fetcher = Mock()
    mock_analyzer = Mock()

    # Mock data
    mock_tickers = ["AAPL", "MSFT", "GOOGL"]
    mock_metrics = [
        {"ticker": "AAPL", "profit_margin": 0.25},
        {"ticker": "MSFT", "profit_margin": 0.40},
    ]
    mock_rankings = {
        "profit_margin": [
            {"ticker": "MSFT", "profit_margin": 0.40},
            {"ticker": "AAPL", "profit_margin": 0.25},
        ]
    }

    # Configure mocks
    mock_fetcher.get_sp500_tickers.return_value = mock_tickers
    mock_fetcher.fetch_multiple.return_value = mock_metrics
    mock_analyzer.analyze.return_value = mock_rankings

    # Patch Analyzer creation
    with patch("src.stock_agent.Analyzer", return_value=mock_analyzer):
        agent = StockAgent(mock_fetcher)
        rankings = agent.run_analysis("sp500")

        # Verify the workflow
        mock_fetcher.get_sp500_tickers.assert_called_once()
        mock_fetcher.fetch_multiple.assert_called_once_with(mock_tickers)
        mock_analyzer.analyze.assert_called_once_with(mock_metrics)

        # Verify return value
        assert rankings == mock_rankings

        # Verify file output
        output_file = Path("output/rankings_sp500.json")
        assert output_file.exists()
        with open(output_file) as f:
            saved_rankings = json.load(f)
            assert saved_rankings == mock_rankings

        # Cleanup
        output_file.unlink()


def test_stock_agent_run_analysis_custom_universe():
    """Test that run_analysis raises error for unsupported universe"""
    mock_fetcher = Mock()
    mock_fetcher.get_sp500_tickers.return_value = []

    with patch("src.stock_agent.Analyzer") as mock_analyzer:
        agent = StockAgent(mock_fetcher)

        # Should raise ValueError for unsupported universe
        with pytest.raises(ValueError, match="Unsupported universe"):
            agent.run_analysis("custom_universe")


def test_stock_agent_run_analysis_unsupported_universe():
    """Test that run_analysis raises error for unsupported universe"""
    mock_fetcher = Mock()
    agent = StockAgent(mock_fetcher)

    with pytest.raises(ValueError, match="Unsupported universe"):
        agent.run_analysis("nasdaq100")


def test_stock_agent_creates_output_directory():
    """Test that output directory is created if it doesn't exist"""
    mock_fetcher = Mock()
    mock_fetcher.get_sp500_tickers.return_value = []

    # Ensure output directory doesn't exist
    output_dir = Path("output")
    if output_dir.exists():
        # Clean up any test files
        for f in output_dir.glob("rankings_*.json"):
            f.unlink()
        # Try to remove if empty
        try:
            output_dir.rmdir()
        except OSError:
            pass

    with patch("src.stock_agent.Analyzer") as mock_analyzer:
        mock_analyzer.return_value.analyze.return_value = {}
        agent = StockAgent(mock_fetcher)
        agent.run_analysis()  # Uses default 'sp500'

        assert output_dir.exists()
        # Cleanup
        if output_dir.exists():
            for f in output_dir.glob("rankings_*.json"):
                f.unlink()
            try:
                output_dir.rmdir()
            except OSError:
                pass
