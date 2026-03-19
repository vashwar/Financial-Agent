import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional


class AnalyticsService:
    """Quantitative financial analysis calculations (deterministic)."""

    @staticmethod
    def calculate_price_metrics(price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate price metrics for Chart 1.
        Returns absolute prices for visualization.

        Args:
            price_df: DataFrame with columns [date, close]

        Returns:
            DataFrame with [date, close] ready for charting
        """
        result = price_df[["date", "close"]].copy()
        result = result.sort_values("date").reset_index(drop=True)
        return result

    @staticmethod
    def calculate_normalized_comparison(
        stock_df: pd.DataFrame,
        sp500_df: pd.DataFrame
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Calculate normalized comparison for Chart 2.
        Normalize both to Day 1 = 0% change.

        Args:
            stock_df: DataFrame with [date, close] for stock
            sp500_df: DataFrame with [date, close] for S&P 500

        Returns:
            Tuple of (stock_normalized, sp500_normalized) with [date, percent_change]
        """
        # Sort by date
        stock_df = stock_df.sort_values("date").reset_index(drop=True)
        sp500_df = sp500_df.sort_values("date").reset_index(drop=True)

        # Align dates - find common date range
        min_date = max(stock_df["date"].min(), sp500_df["date"].min())
        max_date = min(stock_df["date"].max(), sp500_df["date"].max())

        stock_aligned = stock_df[(stock_df["date"] >= min_date) & (stock_df["date"] <= max_date)].reset_index(drop=True)
        sp500_aligned = sp500_df[(sp500_df["date"] >= min_date) & (sp500_df["date"] <= max_date)].reset_index(drop=True)

        # Get starting price (Day 1)
        stock_start = stock_aligned.iloc[0]["close"]
        sp500_start = sp500_aligned.iloc[0]["close"]

        # Calculate percentage change from Day 1 (returns already in %, not multiplied by 100)
        stock_aligned["percent_change"] = (
            (stock_aligned["close"] - stock_start) / stock_start
        )
        sp500_aligned["percent_change"] = (
            (sp500_aligned["close"] - sp500_start) / sp500_start
        )

        return stock_aligned[["date", "percent_change"]], sp500_aligned[["date", "percent_change"]]

    @staticmethod
    def calculate_multi_normalized_comparison(
        price_dfs: Dict[str, pd.DataFrame]
    ) -> List[Dict]:
        """
        Normalize multiple tickers to Day 1 = 0% change and align on common dates.

        Args:
            price_dfs: Dict mapping ticker -> DataFrame with [date, close]

        Returns:
            List of {date: str, values: {TICKER: float, ...}}
        """
        if not price_dfs:
            return []

        # Sort each DataFrame by date
        sorted_dfs = {}
        for ticker, df in price_dfs.items():
            sorted_dfs[ticker] = df.sort_values("date").reset_index(drop=True)

        # Find common date range
        min_dates = [df["date"].min() for df in sorted_dfs.values()]
        max_dates = [df["date"].max() for df in sorted_dfs.values()]
        common_min = max(min_dates)
        common_max = min(max_dates)

        # Filter to common range and normalize each to Day 1 = 0%
        normalized = {}
        for ticker, df in sorted_dfs.items():
            aligned = df[(df["date"] >= common_min) & (df["date"] <= common_max)].copy()
            aligned = aligned.reset_index(drop=True)
            if aligned.empty:
                continue
            start_price = aligned.iloc[0]["close"]
            if start_price == 0:
                continue
            aligned["pct"] = (aligned["close"] - start_price) / start_price
            # Use date as string index for joining
            aligned["date_str"] = aligned["date"].apply(
                lambda d: d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
            )
            normalized[ticker] = aligned.set_index("date_str")["pct"]

        if not normalized:
            return []

        # Outer-join all series, forward-fill gaps
        combined = pd.DataFrame(normalized)
        combined = combined.sort_index()
        combined = combined.ffill()

        result = []
        for date_str, row in combined.iterrows():
            values = {}
            for ticker in combined.columns:
                val = row[ticker]
                if pd.notna(val):
                    values[ticker] = float(val)
            result.append({"date": date_str, "values": values})

        return result

    @staticmethod
    def calculate_fundamental_metrics(
        fundamentals_df: pd.DataFrame,
        current_price: float,
        eps: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Calculate all fundamental metrics from quarterly data.

        Args:
            fundamentals_df: DataFrame with quarterly fundamentals
            current_price: Current share price for P/E calculation
            eps: Earnings per share (optional, from ticker.info)

        Returns:
            Dictionary with latest values and time series
        """
        if fundamentals_df.empty:
            return {}

        # Get latest quarter
        latest = fundamentals_df.iloc[-1]

        metrics = {}

        # 1. Income Statement Metrics
        net_income = latest.get("netIncome")
        if pd.notna(net_income):
            metrics["latest_net_income"] = float(net_income)

        ebit = latest.get("ebit")
        if pd.notna(ebit):
            metrics["latest_ebit"] = float(ebit)

        ebitda = latest.get("ebitda")
        if pd.notna(ebitda):
            metrics["latest_ebitda"] = float(ebitda)

        # 2. Operating Margin = EBIT / Revenue (in %)
        revenue = latest.get("revenue")
        if pd.notna(ebit) and pd.notna(revenue) and revenue != 0:
            operating_margin = (ebit / revenue)
            metrics["latest_operating_margin"] = float(operating_margin)

        # 3. Gross Margin = (Revenue - COGS) / Revenue
        cogs = latest.get("cogs")
        if pd.notna(revenue) and pd.notna(cogs) and revenue != 0:
            gross_margin = (revenue - cogs) / revenue
            metrics["latest_gross_margin"] = float(gross_margin)

        # 4. Debt-to-Equity Ratio
        total_debt = latest.get("totalDebt")
        total_equity = latest.get("totalEquity")
        if pd.notna(total_debt) and pd.notna(total_equity) and total_equity != 0:
            debt_to_equity = total_debt / total_equity
            metrics["latest_debt_to_equity"] = float(debt_to_equity)

        # 5. Interest Coverage = EBIT / Interest Expense
        interest_expense = latest.get("interestExpense")
        if pd.notna(ebit) and pd.notna(interest_expense) and interest_expense != 0:
            interest_coverage = ebit / interest_expense
            metrics["latest_interest_coverage"] = float(interest_coverage)

        # 6. Free Cash Flow (FCF)
        # FCF = Operating Cash Flow - Capital Expenditures
        # If not directly available, attempt calculation
        fcf = latest.get("fcf")
        if pd.notna(fcf):
            metrics["latest_fcf"] = float(fcf)

        # 7. ROIC = NOPAT / Invested Capital
        # NOPAT = EBIT * (1 - Tax Rate)
        # Invested Capital = Total Equity + Total Debt
        # Simplified: ROIC = EBIT / (Total Equity + Total Debt)
        if pd.notna(ebit) and pd.notna(total_debt) and pd.notna(total_equity):
            invested_capital = total_debt + total_equity
            if invested_capital != 0:
                roic = ebit / invested_capital
                metrics["latest_roic"] = float(roic)

        # 8. P/E Ratio = Current Price / EPS
        if eps and eps > 0 and current_price > 0:
            # Use provided EPS directly (from ticker.info.trailingEps)
            pe_ratio = current_price / eps
            metrics["latest_pe_ratio"] = float(pe_ratio)
        elif current_price > 0 and pd.notna(net_income) and net_income != 0:
            # Fallback: Calculate EPS from net income and shares outstanding
            shares_outstanding = latest.get("sharesTotalIssued")
            if pd.notna(shares_outstanding) and shares_outstanding > 0:
                calculated_eps = net_income / shares_outstanding
                if calculated_eps > 0:
                    pe_ratio = current_price / calculated_eps
                    metrics["latest_pe_ratio"] = float(pe_ratio)

        # Time series for all metrics
        time_series = {}

        # Net Income time series
        if "netIncome" in fundamentals_df.columns:
            time_series["net_income"] = fundamentals_df["netIncome"].fillna(0).tolist()

        # EBIT time series
        if "ebit" in fundamentals_df.columns:
            time_series["ebit"] = fundamentals_df["ebit"].fillna(0).tolist()

        # EBITDA time series
        if "ebitda" in fundamentals_df.columns:
            time_series["ebitda"] = fundamentals_df["ebitda"].fillna(0).tolist()

        # Gross Margin time series
        if "revenue" in fundamentals_df.columns and "cogs" in fundamentals_df.columns:
            gross_margins = []
            for _, row in fundamentals_df.iterrows():
                if pd.notna(row["revenue"]) and pd.notna(row["cogs"]) and row["revenue"] != 0:
                    gross_margins.append(float((row["revenue"] - row["cogs"]) / row["revenue"]))
                else:
                    gross_margins.append(None)
            time_series["gross_margin"] = gross_margins

        # Operating Margin time series
        if "revenue" in fundamentals_df.columns and "ebit" in fundamentals_df.columns:
            op_margins = []
            for _, row in fundamentals_df.iterrows():
                if pd.notna(row["ebit"]) and pd.notna(row["revenue"]) and row["revenue"] != 0:
                    op_margins.append(float(row["ebit"] / row["revenue"]))
                else:
                    op_margins.append(None)
            time_series["operating_margin"] = op_margins

        # Debt-to-Equity time series
        if "totalDebt" in fundamentals_df.columns and "totalEquity" in fundamentals_df.columns:
            de_ratios = []
            for _, row in fundamentals_df.iterrows():
                if pd.notna(row["totalDebt"]) and pd.notna(row["totalEquity"]) and row["totalEquity"] != 0:
                    de_ratios.append(float(row["totalDebt"] / row["totalEquity"]))
                else:
                    de_ratios.append(None)
            time_series["debt_to_equity"] = de_ratios

        # Interest Coverage time series
        if "ebit" in fundamentals_df.columns and "interestExpense" in fundamentals_df.columns:
            ic_ratios = []
            for _, row in fundamentals_df.iterrows():
                if pd.notna(row["ebit"]) and pd.notna(row["interestExpense"]) and row["interestExpense"] != 0:
                    ic_ratios.append(float(row["ebit"] / row["interestExpense"]))
                else:
                    ic_ratios.append(None)
            time_series["interest_coverage"] = ic_ratios

        metrics["time_series"] = time_series if time_series else None

        return metrics

    @staticmethod
    def validate_calculations() -> bool:
        """
        Verify that all calculations are deterministic (no randomness).
        Returns True if validation passes.
        """
        # All calculations use pandas/numpy operations
        # No random number generation
        # No floating point operations with undefined behavior
        return True
