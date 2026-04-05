"""Macroeconomic snapshot aggregator.

Collects all macro indicators into a unified snapshot with
directional bias for confluence scoring.
"""

from __future__ import annotations

from datetime import date

from astral.core.models import Direction, MacroSnapshot, Signal, SignalSource
from astral.macro.fred_client import FredClient
from astral.macro.yield_curve import YieldCurveAnalyzer


class MacroAnalyzer:
    """Aggregates macro indicators into a snapshot with bias."""

    def __init__(self, fred_client: FredClient):
        self.fred = fred_client
        self.yc = YieldCurveAnalyzer(fred_client)

    def build_snapshot(self, d: date) -> MacroSnapshot:
        """Build a full macro snapshot."""
        snapshot = MacroSnapshot(date=d)

        if not self.fred.available:
            snapshot.notes.append("FRED API non disponibile (FRED_API_KEY mancante). Macro analysis saltata.")
            snapshot.bias = Direction.LATERAL
            return snapshot

        snapshot.fed_funds = self.fred.get_latest("fed_funds")
        snapshot.cpi_yoy = self.fred.yoy_change("cpi")
        snapshot.m2_yoy = self.fred.yoy_change("m2")
        snapshot.yield_curve_10y2y = self.fred.get_latest("t10y2y")
        snapshot.yield_curve_inverted = self.yc.is_inverted()
        snapshot.vix = self.fred.get_latest("vix")
        snapshot.dxy = self.fred.get_latest("dxy")

        # Calculate bias
        bearish_factors = 0
        bullish_factors = 0

        if snapshot.yield_curve_inverted:
            bearish_factors += 2
            snapshot.notes.append("Curva invertita = segnale recessivo forte")

        if snapshot.cpi_yoy is not None and snapshot.cpi_yoy > 4:
            bearish_factors += 1
            snapshot.notes.append(f"Inflazione elevata ({snapshot.cpi_yoy:.1f}%)")

        if snapshot.fed_funds is not None and snapshot.fed_funds > 4:
            bearish_factors += 1
            snapshot.notes.append(f"Tassi Fed alti ({snapshot.fed_funds:.2f}%)")

        if snapshot.m2_yoy is not None and snapshot.m2_yoy > 5:
            bullish_factors += 1
            snapshot.notes.append(f"M2 in espansione ({snapshot.m2_yoy:.1f}%)")

        if snapshot.vix is not None and snapshot.vix > 25:
            bearish_factors += 1
            snapshot.notes.append(f"VIX elevato ({snapshot.vix:.1f}) = paura sui mercati")
        elif snapshot.vix is not None and snapshot.vix < 15:
            bullish_factors += 1
            snapshot.notes.append(f"VIX basso ({snapshot.vix:.1f}) = compiacenza")

        if bearish_factors > bullish_factors + 1:
            snapshot.bias = Direction.BEARISH
        elif bullish_factors > bearish_factors:
            snapshot.bias = Direction.BULLISH
        else:
            snapshot.bias = Direction.LATERAL

        return snapshot

    def get_signals(self, d: date) -> list[Signal]:
        """Get macro signals for confluence engine."""
        signals = []

        # Yield curve signal
        yc_signal = self.yc.get_signal(d)
        if yc_signal:
            signals.append(yc_signal)

        if not self.fred.available:
            return signals

        # VIX signal
        vix = self.fred.get_latest("vix")
        if vix is not None:
            if vix > 30:
                signals.append(Signal(
                    source=SignalSource.MACRO_INDICATOR,
                    direction=Direction.LATERAL,
                    strength=0.7,
                    description=f"VIX elevato ({vix:.1f}): paura estrema. Possibile capitulation bottom.",
                    date=d,
                    metadata={"indicator": "vix", "value": vix},
                ))
            elif vix < 12:
                signals.append(Signal(
                    source=SignalSource.MACRO_INDICATOR,
                    direction=Direction.BEARISH,
                    strength=0.5,
                    description=f"VIX molto basso ({vix:.1f}): compiacenza estrema, risk-off imminente.",
                    date=d,
                    metadata={"indicator": "vix", "value": vix},
                ))

        # CPI signal
        cpi_yoy = self.fred.yoy_change("cpi")
        if cpi_yoy is not None:
            if cpi_yoy > 5:
                signals.append(Signal(
                    source=SignalSource.MACRO_INDICATOR,
                    direction=Direction.BEARISH,
                    strength=0.6,
                    description=f"Inflazione CPI elevata ({cpi_yoy:.1f}% YoY): Fed hawkish, pressione sui mercati.",
                    date=d,
                    metadata={"indicator": "cpi_yoy", "value": cpi_yoy},
                ))

        return signals
