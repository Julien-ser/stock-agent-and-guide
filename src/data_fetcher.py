"""Stock data fetcher using Yahoo Finance API"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional


class DataFetcher:
    """Fetches financial data for stocks"""

    def __init__(self, cache_dir: str = "data"):
        self.cache_dir = cache_dir

    def get_sp500_tickers(self) -> List[str]:
        """Fetch current S&P 500 constituent tickers"""
        # Use Wikipedia table of S&P 500 components
        tables = pd.read_html(
            "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        )
        sp500_df = tables[0]
        return sp500_df["Symbol"].str.replace(".", "-").tolist()

    def get_financial_metrics(self, ticker: str) -> Optional[Dict]:
        """Retrieve key financial metrics for a single stock"""
        try:
            stock = yf.Ticker(ticker)

            # Get financial statements
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            cashflow = stock.cashflow

            # Get info
            info = stock.info

            # Calculate or extract the 5 key metrics
            metrics = {
                "ticker": ticker,
                "name": info.get("longName", ticker),
                "sector": info.get("sector", "Unknown"),
            }

            # Profit Margin = Net Income / Revenue
            if (
                "Net Income" in income_stmt.index
                and "Total Revenue" in income_stmt.index
            ):
                net_income = income_stmt.loc["Net Income"].iloc[0]
                revenue = income_stmt.loc["Total Revenue"].iloc[0]
                metrics["profit_margin"] = (
                    net_income / revenue if revenue != 0 else None
                )

            # Operating Margin = Operating Income / Revenue
            if (
                "Operating Income" in income_stmt.index
                and "Total Revenue" in income_stmt.index
            ):
                operating_income = income_stmt.loc["Operating Income"].iloc[0]
                revenue = income_stmt.loc["Total Revenue"].iloc[0]
                metrics["operating_margin"] = (
                    operating_income / revenue if revenue != 0 else None
                )

            # Free Cash Flow (from cashflow statement)
            if "Free Cash Flow" in cashflow.index:
                metrics["free_cash_flow"] = cashflow.loc["Free Cash Flow"].iloc[0]

            # Return on Invested Capital (ROIC)
            # ROIC = NOPAT / Invested Capital
            # NOPAT = Operating Income * (1 - tax rate)
            if "Operating Income" in income_stmt.index:
                operating_income = income_stmt.loc["Operating Income"].iloc[0]
                tax_rate = info.get("effectiveTaxRate", 0.21)
                nopat = operating_income * (1 - tax_rate)

                # Invested Capital = Total Assets - Cash + Debt
                # Simplified: Total Assets - Cash
                if "Total Assets" in balance_sheet.index:
                    total_assets = balance_sheet.loc["Total Assets"].iloc[0]
                    cash = info.get("totalCash", 0)
                    invested_capital = total_assets - cash
                    metrics["roic"] = (
                        nopat / invested_capital if invested_capital != 0 else None
                    )

            # Interest Coverage Ratio = EBIT / Interest Expense
            if "EBIT" in income_stmt.index and "Interest Expense" in income_stmt.index:
                ebit = income_stmt.loc["EBIT"].iloc[0]
                interest_expense = income_stmt.loc["Interest Expense"].iloc[0]
                metrics["interest_coverage"] = (
                    ebit / abs(interest_expense) if interest_expense != 0 else None
                )

            return metrics

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
            return None

    def fetch_multiple(self, tickers: List[str]) -> List[Dict]:
        """Fetch metrics for multiple tickers"""
        results = []
        for ticker in tickers:
            metrics = self.get_financial_metrics(ticker)
            if metrics:
                results.append(metrics)
        return results
