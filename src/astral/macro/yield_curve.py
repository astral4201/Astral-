"""Yield curve analysis.

The yield curve (10Y-2Y spread) has preceded every US recession since 1960.
When inverted (spread < 0), recession typically follows within 6-24 months.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from astral.core.models import Direction, Signal, SignalSource
from astral.macro.fred_client import FredClient


class YieldCurveAnalyzer:
    """Analyzes yield curve inversions and their recession signals."""

    def __init__(self, fred_client: FredClient):
        self.fred = fred_client

    def get_current_spread(self) -> Optional[float]:
        """Get the current 10Y-2Y Treasury spread."""
        return self.fred.get_latest("t10y2y")

    def is_inverted(self) -> Optional[bool]:
        """Check if the yield curve is currently inverted."""
        spread = self.get_current_spread()
        if spread is None:
            return None
        return spread < 0

    def inversion_duration_days(self) -> Optional[int]:
        """Calculate how many days the curve has been continuously inverted."""
        series = self.fred.get_series("t10y2y")
        if series is None or series.empty:
            return None

        clean = series.dropna()
        if clean.empty or clean.iloc[-1] >= 0:
            return 0

        # Walk backwards to find start of inversion
        count = 0
        for val in clean.iloc[::-1]:
            if val < 0:
                count += 1
            else:
                break
        # Convert periods (monthly) to approximate days
        return count * 30

    def get_signal(self, d: date) -> Optional[Signal]:
        """Generate a yield curve signal."""
        spread = self.get_current_spread()
        if spread is None:
            return None

        inverted = spread < 0
        duration = self.inversion_duration_days() if inverted else 0

        if inverted:
            strength = min(0.9, 0.5 + (duration or 0) / 365)
            return Signal(
                source=SignalSource.MACRO_YIELD_CURVE,
                direction=Direction.BEARISH,
                strength=strength,
                description=(
                    f"⚠️ CURVA DEI RENDIMENTI INVERTITA: spread 10Y-2Y = {spread:.2f}%. "
                    f"Durata inversione: ~{duration} giorni. "
                    f"Ogni recessione USA dal 1960 è stata preceduta da questa inversione. "
                    f"Finestra tipica: 6-24 mesi."
                ),
                date=d,
                metadata={"spread": spread, "inverted": True, "duration_days": duration},
            )
        else:
            return Signal(
                source=SignalSource.MACRO_YIELD_CURVE,
                direction=Direction.BULLISH,
                strength=0.4,
                description=(
                    f"Curva dei rendimenti normale: spread 10Y-2Y = {spread:.2f}%. "
                    f"Nessun segnale recessivo immediato."
                ),
                date=d,
                metadata={"spread": spread, "inverted": False},
            )
