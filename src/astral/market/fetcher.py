"""Market data fetcher using yfinance."""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import yfinance as yf


# Ticker symbol mappings for common instruments
SYMBOL_MAP = {
    "SPX": "^GSPC",
    "SP500": "^GSPC",
    "DJIA": "^DJI",
    "DOW": "^DJI",
    "NDX": "^IXIC",
    "NASDAQ": "^IXIC",
    "GOLD": "GC=F",
    "OIL": "CL=F",
    "BTC": "BTC-USD",
    "BITCOIN": "BTC-USD",
    "ETH": "ETH-USD",
    "EUR": "EURUSD=X",
    "DXY": "DX-Y.NYB",
    "VIX": "^VIX",
    "SILVER": "SI=F",
}


class MarketFetcher:
    """Fetches OHLCV data from Yahoo Finance."""

    def __init__(self, custom_symbols: dict[str, str] | None = None):
        self._symbols = {**SYMBOL_MAP, **(custom_symbols or {})}

    def resolve_ticker(self, ticker: str) -> str:
        """Resolve user-friendly ticker to Yahoo Finance symbol."""
        return self._symbols.get(ticker.upper(), ticker)

    def get_ohlcv(
        self,
        ticker: str,
        start: date | None = None,
        end: date | None = None,
        interval: str = "1d",
        lookback_days: int = 365,
    ) -> pd.DataFrame:
        """Fetch OHLCV data for a ticker.

        Returns DataFrame with columns: Open, High, Low, Close, Volume.
        """
        symbol = self.resolve_ticker(ticker)
        if end is None:
            end = date.today()
        if start is None:
            start = end - timedelta(days=lookback_days)

        data = yf.download(
            symbol,
            start=start.isoformat(),
            end=end.isoformat(),
            interval=interval,
            progress=False,
        )
        # Flatten MultiIndex columns if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data

    def current_price(self, ticker: str) -> float:
        """Get the latest closing price for a ticker."""
        symbol = self.resolve_ticker(ticker)
        t = yf.Ticker(symbol)
        hist = t.history(period="1d")
        if hist.empty:
            # Fallback: get last 5 days
            hist = t.history(period="5d")
        if hist.empty:
            raise ValueError(f"Impossibile ottenere il prezzo per {ticker} ({symbol})")
        return float(hist["Close"].iloc[-1])
