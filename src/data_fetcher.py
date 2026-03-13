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
            info = stock.info

            # Helper functions
            def to_float(val):
                try:
                    return float(val) if val is not None else None
                except:
                    return None

            def find_value(df, possible_names):
                """Find a value in a DataFrame by possible row labels (case-insensitive)"""
                if df is None or df.empty:
                    return None
                idx_map = {str(idx).lower(): idx for idx in df.index}
                for name in possible_names:
                    if name.lower() in idx_map:
                        val = df.loc[idx_map[name.lower()]].iloc[0]
                        return to_float(val)
                return None

            # Initialize metrics
            metrics = {
                "ticker": ticker,
                "name": info.get("longName", ticker),
                "sector": info.get("sector", "Unknown"),
            }

            # Lazy fetch statements
            income_stmt = None
            balance_sheet = None
            cashflow = None

            # 1. Profit Margin = Net Income / Total Revenue
            profit_margin = to_float(info.get("profitMargins"))
            if profit_margin is not None:
                metrics["profit_margin"] = profit_margin
            else:
                income_stmt = stock.financials if income_stmt is None else income_stmt
                net_income = find_value(
                    income_stmt, ["Net Income", "NetIncome", "Net Income Total"]
                )
                revenue = find_value(
                    income_stmt, ["Total Revenue", "Revenue", "TotalRevenue", "Sales"]
                )
                if net_income is not None and revenue is not None and revenue != 0:
                    metrics["profit_margin"] = net_income / revenue

            # 2. Operating Margin = Operating Income / Revenue
            operating_margin = to_float(info.get("operatingMargins"))
            if operating_margin is not None:
                metrics["operating_margin"] = operating_margin
            else:
                income_stmt = stock.financials if income_stmt is None else income_stmt
                op_income = find_value(
                    income_stmt,
                    [
                        "Operating Income",
                        "OperatingIncome",
                        "Operating Income Total",
                        "EBIT",
                    ],
                )
                revenue = find_value(
                    income_stmt, ["Total Revenue", "Revenue", "TotalRevenue", "Sales"]
                )
                if op_income is not None and revenue is not None and revenue != 0:
                    metrics["operating_margin"] = op_income / revenue

            # 3. Free Cash Flow
            fcf = to_float(info.get("freeCashflow"))
            if fcf is not None:
                metrics["free_cash_flow"] = fcf
            else:
                cashflow = stock.cashflow if cashflow is None else cashflow
                fcf_val = find_value(
                    cashflow,
                    [
                        "Free Cash Flow",
                        "FreeCashFlow",
                        "Cash Flow From Operations Total",
                    ],
                )
                if fcf_val is not None:
                    metrics["free_cash_flow"] = fcf_val

            # 4. ROIC = NOPAT / Invested Capital
            op_income = to_float(info.get("operatingIncome"))
            total_assets = to_float(info.get("totalAssets"))
            total_cash = to_float(info.get("totalCash"))
            tax_rate = to_float(info.get("effectiveTaxRate"))
            if (
                op_income is not None
                and total_assets is not None
                and total_cash is not None
            ):
                nopat = op_income * (1 - (tax_rate or 0.21))
                invested_capital = total_assets - total_cash
                if invested_capital != 0:
                    metrics["roic"] = nopat / invested_capital
            else:
                # Fallback to statements
                if income_stmt is None:
                    income_stmt = stock.financials
                if balance_sheet is None:
                    balance_sheet = stock.balance_sheet
                op_income = (
                    op_income
                    if op_income is not None
                    else find_value(
                        income_stmt,
                        [
                            "Operating Income",
                            "OperatingIncome",
                            "Operating Income Total",
                            "EBIT",
                        ],
                    )
                )
                total_assets = (
                    total_assets
                    if total_assets is not None
                    else find_value(balance_sheet, ["Total Assets", "TotalAssets"])
                )
                total_cash = (
                    total_cash
                    if total_cash is not None
                    else find_value(
                        balance_sheet,
                        [
                            "Cash",
                            "Cash And Cash Equivalents",
                            "Cash and Short Term Investments",
                        ],
                    )
                )
                tax_rate = tax_rate if tax_rate is not None else 0.21
                if (
                    op_income is not None
                    and total_assets is not None
                    and total_cash is not None
                ):
                    nopat = op_income * (1 - tax_rate)
                    invested_capital = total_assets - total_cash
                    if invested_capital != 0:
                        metrics["roic"] = nopat / invested_capital

            # 5. Interest Coverage = EBIT / Interest Expense
            ebit = to_float(info.get("ebit"))
            interest = to_float(info.get("interestExpense"))
            if ebit is not None and interest is not None and interest != 0:
                metrics["interest_coverage"] = ebit / abs(interest)
            else:
                if income_stmt is None:
                    income_stmt = stock.financials
                ebit = (
                    ebit
                    if ebit is not None
                    else find_value(
                        income_stmt,
                        [
                            "EBIT",
                            "Earnings Before Interest and Taxes",
                            "Operating Income",
                        ],
                    )
                )
                interest = (
                    interest
                    if interest is not None
                    else find_value(
                        income_stmt,
                        [
                            "Interest Expense",
                            "InterestExpense",
                            "Interest Expense Total",
                        ],
                    )
                )
                if ebit is not None and interest is not None and interest != 0:
                    metrics["interest_coverage"] = ebit / abs(interest)

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
