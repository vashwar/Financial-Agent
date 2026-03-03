import re
import urllib.parse
import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import earningscall

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


class YFinanceService:
    """Yahoo Finance API integration service using yfinance library."""

    def __init__(self):
        pass

    def get_historical_prices(self, ticker: str, years: int = 5) -> pd.DataFrame:
        """
        Get historical daily prices for a stock.

        Returns DataFrame with columns: date, close
        """
        try:
            import time
            # Calculate date range
            end_date = datetime.now() - timedelta(days=1)
            start_date = end_date - timedelta(days=365 * years)

            # Fetch historical data
            data = yf.download(
                ticker.upper(),
                start=start_date,
                end=end_date,
                progress=False,
                threads=False
            )

            if data.empty:
                raise ValueError(f"No data found for ticker: {ticker}")

            # Reset index to make date a column
            data = data.reset_index()
            data = data[['Date', 'Close']].copy()
            data.columns = ['date', 'close']
            data['date'] = pd.to_datetime(data['date'])

            return data.sort_values('date').reset_index(drop=True)

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                raise ValueError(f"Yahoo Finance rate limit exceeded. Please try again in a few moments.")
            elif "No data found" in error_msg or "No timezone found" in error_msg:
                raise ValueError(f"Ticker '{ticker}' not found or delisted. Please check the ticker symbol.")
            else:
                raise ValueError(f"Failed to get historical prices for {ticker}: {error_msg}")

    def get_fundamentals(self, ticker: str) -> pd.DataFrame:
        """
        Get quarterly fundamental data from yfinance.

        Returns DataFrame with financial metrics
        """
        try:
            ticker_obj = yf.Ticker(ticker.upper())

            # Get annual financials (yfinance doesn't have direct quarterly, use annual)
            income = ticker_obj.financials
            balance = ticker_obj.balance_sheet
            cashflow = ticker_obj.cashflow

            if income is None or income.empty:
                raise ValueError(f"No fundamental data found for ticker: {ticker}")

            # Transpose to have dates as rows
            income_t = income.T
            income_t['date'] = income_t.index
            income_t['date'] = pd.to_datetime(income_t['date'])

            # Extract relevant columns
            fundamentals = pd.DataFrame()
            fundamentals['date'] = income_t['date']

            # Income statement metrics
            if 'Total Revenue' in income_t.columns:
                fundamentals['revenue'] = income_t['Total Revenue']
            if 'Operating Income' in income_t.columns:
                fundamentals['ebit'] = income_t['Operating Income']
            if 'EBITDA' in income_t.columns:
                fundamentals['ebitda'] = income_t['EBITDA']
            if 'Net Income' in income_t.columns:
                fundamentals['netIncome'] = income_t['Net Income']
            if 'Reconciled Cost Of Revenue' in income_t.columns:
                fundamentals['cogs'] = income_t['Reconciled Cost Of Revenue']

            # Balance sheet metrics
            if not balance.empty:
                balance_t = balance.T
                balance_t['date'] = balance_t.index
                balance_t['date'] = pd.to_datetime(balance_t['date'])

                # Merge balance sheet data
                fundamentals = fundamentals.merge(
                    balance_t[['date', 'Total Debt', 'Stockholders Equity']],
                    on='date',
                    how='left'
                )
                fundamentals.rename(columns={
                    'Total Debt': 'totalDebt',
                    'Stockholders Equity': 'totalEquity'
                }, inplace=True)

            # Cash flow metrics
            if not cashflow.empty:
                cf_t = cashflow.T
                cf_t['date'] = cf_t.index
                cf_t['date'] = pd.to_datetime(cf_t['date'])

                # Free Cash Flow
                if 'Free Cash Flow' in cf_t.columns:
                    fundamentals = fundamentals.merge(
                        cf_t[['date', 'Free Cash Flow']],
                        on='date',
                        how='left'
                    )
                    fundamentals.rename(columns={'Free Cash Flow': 'fcf'}, inplace=True)

                # Interest Paid (for Interest Coverage calculation)
                # Try multiple sources: Interest Paid Supplemental Data (cashflow) or use income statement
                if 'Interest Paid Supplemental Data' in cf_t.columns:
                    fundamentals = fundamentals.merge(
                        cf_t[['date', 'Interest Paid Supplemental Data']],
                        on='date',
                        how='left'
                    )
                    fundamentals.rename(columns={'Interest Paid Supplemental Data': 'interestExpense'}, inplace=True)

            # Interest Expense from Income Statement (if not already from cashflow)
            if 'interestExpense' not in fundamentals.columns or fundamentals['interestExpense'].isna().all():
                if not income.empty:
                    income_t = income.T
                    income_t['date'] = income_t.index
                    income_t['date'] = pd.to_datetime(income_t['date'])

                    # Try different field names for interest expense
                    interest_field = None
                    if 'Interest Expense Non Operating' in income_t.columns:
                        interest_field = 'Interest Expense Non Operating'
                    elif 'Interest Expense' in income_t.columns:
                        interest_field = 'Interest Expense'

                    if interest_field:
                        # Merge with fundamentals
                        interest_df = income_t[['date', interest_field]].copy()
                        interest_df.rename(columns={interest_field: 'interestExpense'}, inplace=True)

                        if 'interestExpense' in fundamentals.columns:
                            # Fill NaN values from income statement
                            fundamentals['interestExpense'].fillna(interest_df.set_index('date')['interestExpense'], inplace=True)
                        else:
                            fundamentals = fundamentals.merge(interest_df, on='date', how='left')

            # Sort and get last 20 periods
            fundamentals = fundamentals.sort_values('date').tail(20).reset_index(drop=True)

            return fundamentals

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                raise ValueError(f"Yahoo Finance rate limit exceeded. Please try again in a few moments.")
            elif "No data found" in error_msg or "No timezone found" in error_msg:
                raise ValueError(f"Ticker '{ticker}' not found or delisted. Please check the ticker symbol.")
            else:
                raise ValueError(f"Failed to get fundamentals for {ticker}: {error_msg}")

    def get_sp500_prices(self, years: int = 5) -> pd.DataFrame:
        """
        Get S&P 500 historical prices for comparison.
        """
        return self.get_historical_prices("SPY", years)

    def get_current_price(self, ticker: str) -> float:
        """Get current share price."""
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            price = ticker_obj.info.get('currentPrice') or ticker_obj.info.get('regularMarketPrice')

            if price is None:
                return 0.0

            return float(price)

        except Exception as e:
            print(f"Error getting current price: {str(e)}")
            return 0.0

    def get_earnings_transcript(self, ticker: str) -> Optional[str]:
        """
        Get latest earnings call transcript using earningscall library.
        """
        try:
            ticker_upper = ticker.upper()

            # Get company from earningscall
            company = earningscall.get_company(ticker_upper)

            # Get earnings events
            events = company.events()

            if not events:
                return None

            # Get latest event
            latest_event = events[0]

            # Get transcript
            transcript_obj = company.get_transcript(year=latest_event.year, quarter=latest_event.quarter)

            if transcript_obj and hasattr(transcript_obj, 'text'):
                transcript_text = transcript_obj.text

                # Clean up excessive blank lines
                if isinstance(transcript_text, str):
                    text = re.sub(r"\n{3,}", "\n\n", transcript_text).strip()
                    # Only return if we got substantial content
                    if text and len(text) > 500:
                        return text

            return None

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg or "Too Many Requests" in error_msg:
                print(f"Rate limit exceeded while fetching transcript for {ticker}")
            else:
                print(f"Error fetching transcript for {ticker}: {error_msg}")
            return None

    def get_eps_and_shares(self, ticker: str) -> Dict:
        """
        Get EPS and shares outstanding for P/E ratio calculation.

        Returns:
            Dictionary with 'eps', 'shares_outstanding', and 'price'
        """
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            info = ticker_obj.info

            return {
                'eps': info.get('trailingEps'),
                'shares_outstanding': info.get('sharesOutstanding'),
                'price': info.get('currentPrice') or info.get('regularMarketPrice'),
            }

        except Exception as e:
            print(f"Error getting EPS and shares: {str(e)}")
            return {}

    def search_tickers(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search for tickers by company name or symbol using Yahoo Finance autocomplete API.

        Returns list of {symbol, name, exchange, quote_type}.
        """
        try:
            url = "https://query2.finance.yahoo.com/v1/finance/search"
            params = {
                "q": query,
                "quotesCount": max_results,
                "newsCount": 0,
                "listsCount": 0,
            }
            resp = requests.get(url, params=params, headers=HEADERS, timeout=5)
            resp.raise_for_status()
            data = resp.json()

            results = []
            for quote in data.get("quotes", []):
                results.append({
                    "symbol": quote.get("symbol", ""),
                    "name": quote.get("longname") or quote.get("shortname", ""),
                    "exchange": quote.get("exchDisp", quote.get("exchange", "")),
                    "quote_type": quote.get("quoteType", ""),
                })
            return results

        except Exception as e:
            print(f"Error searching tickers: {str(e)}")
            return []

    def get_etf_holdings(self, ticker: str) -> List[Dict]:
        """
        Get top holdings for an ETF using yfinance funds_data.

        Returns list of {symbol, name, weight}.
        """
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            funds_data = ticker_obj.funds_data
            top_holdings = funds_data.top_holdings

            results = []
            if top_holdings is not None and not top_holdings.empty:
                for symbol, row in top_holdings.iterrows():
                    results.append({
                        "symbol": str(symbol),
                        "name": row.get("Name", str(symbol)),
                        "weight": round(float(row.get("Holding Percent", 0)) * 100, 2),
                    })
            return results[:10]

        except Exception as e:
            print(f"Error getting ETF holdings for {ticker}: {str(e)}")
            return []

    def get_etf_info(self, ticker: str) -> Dict:
        """Get ETF-specific information: name, category, expense ratio, total assets."""
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            info = ticker_obj.info

            return {
                "name": info.get("longName") or info.get("shortName", ticker.upper()),
                "category": info.get("category", "N/A"),
                "expense_ratio": info.get("annualReportExpenseRatio"),
                "total_assets": info.get("totalAssets"),
            }

        except Exception as e:
            print(f"Error getting ETF info for {ticker}: {str(e)}")
            return {"name": ticker.upper(), "category": "N/A", "expense_ratio": None, "total_assets": None}

    def get_stock_info(self, ticker: str) -> Dict:
        """Get comprehensive stock information."""
        try:
            ticker_obj = yf.Ticker(ticker.upper())
            info = ticker_obj.info

            return {
                'symbol': info.get('symbol'),
                'name': info.get('longName'),
                'price': info.get('currentPrice') or info.get('regularMarketPrice'),
                'change': (info.get('currentPrice') or info.get('regularMarketPrice', 0)) - (info.get('previousClose') or 0),
                'exchange': info.get('exchange'),
                'marketCap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'eps': info.get('trailingEps'),
                'beta': info.get('beta'),
            }

        except Exception as e:
            print(f"Error getting stock info: {str(e)}")
            return {}
