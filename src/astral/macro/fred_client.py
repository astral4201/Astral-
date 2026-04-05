"""FRED (Federal Reserve Economic Data) API client.

Fetches macroeconomic data with graceful degradation if no API key.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

import pandas as pd


# Key FRED series for financial market analysis
FRED_SERIES = {
    "fed_funds": "FEDFUNDS",        # Federal Funds Rate
    "cpi": "CPIAUCSL",              # Consumer Price Index
    "ppi": "PPIACO",                # Producer Price Index
    "pce": "PCEPI",                 # Personal Consumption Expenditures
    "m2": "M2SL",                   # M2 Money Supply
    "t10y2y": "T10Y2Y",             # 10Y - 2Y spread (yield curve)
    "t10y3m": "T10Y3M",             # 10Y - 3M spread
    "vix": "VIXCLS",                # CBOE VIX
    "dxy": "DTWEXBGS",              # Trade-weighted Dollar Index
    "unemployment": "UNRATE",        # Unemployment Rate
    "gdp": "GDP",                   # Gross Domestic Product
}


class FredClient:
    """FRED API wrapper with graceful fallback."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._fred = None
        if api_key:
            try:
                from fredapi import Fred
                self._fred = Fred(api_key=api_key)
            except Exception:
                self._fred = None

    @property
    def available(self) -> bool:
        """Check if FRED API is available (valid key + library installed)."""
        return self._fred is not None

    def get_series(
        self,
        series_key: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Optional[pd.Series]:
        """Fetch a FRED series. Returns None if not available."""
        if not self.available:
            return None

        series_id = FRED_SERIES.get(series_key, series_key)
        try:
            data = self._fred.get_series(
                series_id,
                observation_start=start_date.isoformat() if start_date else None,
                observation_end=end_date.isoformat() if end_date else None,
            )
            return data
        except Exception:
            return None

    def get_latest(self, series_key: str) -> Optional[float]:
        """Get the latest value of a FRED series."""
        data = self.get_series(series_key, start_date=date.today() - timedelta(days=365))
        if data is None or data.empty:
            return None
        # Drop NaN and get last valid value
        clean = data.dropna()
        if clean.empty:
            return None
        return float(clean.iloc[-1])

    def yoy_change(self, series_key: str) -> Optional[float]:
        """Calculate year-over-year percentage change."""
        data = self.get_series(series_key, start_date=date.today() - timedelta(days=400))
        if data is None or len(data) < 13:
            return None
        clean = data.dropna()
        if len(clean) < 13:
            return None
        current = clean.iloc[-1]
        year_ago = clean.iloc[-13]
        if year_ago == 0:
            return None
        return float((current - year_ago) / year_ago * 100)
