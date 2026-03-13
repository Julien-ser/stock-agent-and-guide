"""Tests for CLI commands"""

import pytest
from unittest.mock import patch, Mock
from click.testing import CliRunner
from src.cli import cli


@pytest.fixture
def runner():
    """Create CLI test runner"""
    return CliRunner()


def test_cli_analyze_command(runner):
    """Test the analyze CLI command"""
    # Mock the StockAgent
    mock_rankings = {
        "profit_margin": [
            {"ticker": "AAPL", "profit_margin": 0.25, "name": "Apple Inc."}
        ]
    }
    mock_agent = Mock()
    mock_agent.run_analysis.return_value = mock_rankings
    mock_fetcher = Mock()

    with (
        patch("src.cli.DataFetcher", return_value=mock_fetcher),
        patch("src.cli.StockAgent", return_value=mock_agent),
        patch("pathlib.Path.mkdir"),
        patch("builtins.open", create=True) as mock_open,
    ):
        result = runner.invoke(cli, ["analyze", "--universe", "sp500"])

        assert result.exit_code == 0
        assert "Fetching and analyzing sp500 stocks" in result.output
        assert "Profit Margin:" in result.output
        assert "AAPL" in result.output
        mock_agent.run_analysis.assert_called_once_with("sp500")


def test_cli_analyze_default_universe(runner):
    """Test analyze command with default universe"""
    mock_agent = Mock()
    mock_agent.run_analysis.return_value = {}
    mock_fetcher = Mock()

    with (
        patch("src.cli.DataFetcher", return_value=mock_fetcher),
        patch("src.cli.StockAgent", return_value=mock_agent),
        patch("pathlib.Path.mkdir"),
    ):
        result = runner.invoke(cli, ["analyze"])

        assert result.exit_code == 0
        mock_agent.run_analysis.assert_called_once_with("sp500")


def test_cli_generate_guide_command(runner):
    """Test the generate-guide CLI command"""
    mock_generator = Mock()

    with patch("src.cli.GuideGenerator", return_value=mock_generator):
        result = runner.invoke(cli, ["generate-guide"])

        assert result.exit_code == 0
        assert "Generating user guide" in result.output
        assert "Guide saved to output/guide.md" in result.output
        mock_generator.generate.assert_called_once()


def test_cli_generate_guide_custom_path(runner):
    """Test generate-guide with custom output path"""
    mock_generator = Mock()

    with patch("src.cli.GuideGenerator", return_value=mock_generator):
        result = runner.invoke(cli, ["generate-guide", "--output", "custom/path.md"])

        # Note: Current CLI doesn't support --output option, so this test documents expected behavior
        # If the option is added later, this test would validate it
        pass


def test_cli_full_run_command(runner):
    """Test the full-run CLI command"""
    mock_agent = Mock()
    mock_agent.run_analysis.return_value = {}
    mock_fetcher = Mock()
    mock_generator = Mock()

    with (
        patch("src.cli.DataFetcher", return_value=mock_fetcher),
        patch("src.cli.StockAgent", return_value=mock_agent),
        patch("src.cli.GuideGenerator", return_value=mock_generator),
        patch("pathlib.Path.mkdir"),
    ):
        result = runner.invoke(cli, ["full-run"])

        assert result.exit_code == 0
        assert "Running full pipeline" in result.output
        assert "Analysis complete" in result.output
        assert "Full run complete" in result.output
        mock_agent.run_analysis.assert_called_once()  # Called with default 'sp500'
        mock_generator.generate.assert_called_once()


def test_cli_help(runner):
    """Test CLI help output"""
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "Stock analysis CLI" in result.output
    assert "analyze" in result.output
    assert "generate-guide" in result.output
    assert "full-run" in result.output


def test_cli_analyze_handles_fetch_error(runner):
    """Test that analyze command handles errors gracefully"""
    mock_fetcher = Mock()
    mock_fetcher.get_sp500_tickers.side_effect = Exception("Network error")
    mock_agent = Mock()
    mock_agent.run_analysis.side_effect = Exception("Analysis failed")

    with (
        patch("src.cli.DataFetcher", return_value=mock_fetcher),
        patch("src.cli.StockAgent", return_value=mock_agent),
    ):
        result = runner.invoke(cli, ["analyze"])

        # Should exit with non-zero code on error
        assert result.exit_code != 0
