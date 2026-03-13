"""Command-line interface for stock agent"""

import json
import click
from src.data_fetcher import DataFetcher
from src.stock_agent import StockAgent
from src.guide_generator import GuideGenerator


@click.group()
def cli():
    """Stock analysis CLI"""
    pass


@cli.command()
@click.option("--universe", default="sp500", help="Stock universe to analyze")
def analyze(universe):
    """Analyze top stocks in all categories"""
    click.echo(f"Fetching and analyzing {universe} stocks...")

    fetcher = DataFetcher()
    agent = StockAgent(fetcher)
    rankings = agent.run_analysis(universe)

    click.echo("\nTop 10 stocks by metric:\n")
    for metric, stocks in rankings.items():
        click.echo(f"\n{metric.replace('_', ' ').title()}:")
        for i, stock in enumerate(stocks, 1):
            name = stock.get("name", stock["ticker"])
            value = stock.get(metric)
            click.echo(
                f"  {i}. {stock['ticker']} ({name}): {value:.2%}"
                if isinstance(value, float)
                else f"  {i}. {stock['ticker']} ({name}): {value}"
            )

    click.echo(f"\nResults saved to output/rankings_{universe}.json")


@cli.command()
def generate_guide():
    """Generate user guide"""
    click.echo("Generating user guide...")
    generator = GuideGenerator()
    generator.generate()
    click.echo("Guide saved to output/guide.md")


@cli.command()
def full_run():
    """Run both analysis and guide generation"""
    click.echo("Running full pipeline...")
    fetcher = DataFetcher()
    agent = StockAgent(fetcher)
    rankings = agent.run_analysis()

    click.echo("\nAnalysis complete. Generating guide...")
    generator = GuideGenerator()
    generator.generate()
    click.echo("\nFull run complete!")


if __name__ == "__main__":
    cli()
