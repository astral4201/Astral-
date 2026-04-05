"""Gann Angles Calculator.

Gann angles represent the relationship between time and price.
The 1x1 angle (45°) is the master angle: 1 unit of price per 1 unit of time.
Price above the 1x1 = bullish; below = bearish.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

from astral.core.models import Direction, GannAngleType, GannLevel, Signal, SignalSource


class GannAngleCalculator:
    """Calculates Gann angle price levels from a pivot point."""

    # All standard Gann angles
    ANGLES = list(GannAngleType)

    def __init__(self, scale_factor: float = 1.0):
        self.scale_factor = scale_factor

    def calculate_level(
        self,
        pivot_price: float,
        days_elapsed: int,
        angle: GannAngleType,
        ascending: bool = True,
    ) -> float:
        """Calculate the price level for a given Gann angle.

        Formula: level = pivot ± (days × ratio × scale)
        """
        delta = days_elapsed * angle.ratio * self.scale_factor
        return pivot_price + delta if ascending else pivot_price - delta

    def calculate_all_levels(
        self,
        pivot_price: float,
        pivot_date: date,
        current_date: date,
    ) -> list[GannLevel]:
        """Calculate all Gann angle levels from a pivot to current date."""
        days = (current_date - pivot_date).days
        if days <= 0:
            return []

        levels = []
        for angle in self.ANGLES:
            # Ascending (from low pivot)
            price_up = self.calculate_level(pivot_price, days, angle, ascending=True)
            levels.append(GannLevel(
                price=round(price_up, 2),
                level_type=f"angle_{angle.label}_up",
                direction=Direction.BULLISH,
                description=f"Angolo {angle.label} ({angle.degrees}°) ascendente da {pivot_price:.2f}",
            ))
            # Descending (from high pivot)
            price_down = self.calculate_level(pivot_price, days, angle, ascending=False)
            levels.append(GannLevel(
                price=round(price_down, 2),
                level_type=f"angle_{angle.label}_down",
                direction=Direction.BEARISH,
                description=f"Angolo {angle.label} ({angle.degrees}°) discendente da {pivot_price:.2f}",
            ))
        return levels

    def analyze_price_position(
        self,
        current_price: float,
        pivot_price: float,
        pivot_date: date,
        current_date: date,
    ) -> list[Signal]:
        """Determine where current price sits relative to Gann angles."""
        days = (current_date - pivot_date).days
        if days <= 0:
            return []

        signals = []
        # Key angle: 1x1 (the master angle)
        master = GannAngleType.A1x1
        master_level = self.calculate_level(pivot_price, days, master, ascending=True)

        if current_price > master_level:
            signals.append(Signal(
                source=SignalSource.GANN_ANGLE,
                direction=Direction.BULLISH,
                strength=0.7,
                description=f"Prezzo ({current_price:.2f}) SOPRA l'angolo maestro 1x1 ({master_level:.2f}) — forza rialzista",
                date=current_date,
                metadata={"angle": "1x1", "level": master_level},
            ))
        else:
            signals.append(Signal(
                source=SignalSource.GANN_ANGLE,
                direction=Direction.BEARISH,
                strength=0.7,
                description=f"Prezzo ({current_price:.2f}) SOTTO l'angolo maestro 1x1 ({master_level:.2f}) — debolezza ribassista",
                date=current_date,
                metadata={"angle": "1x1", "level": master_level},
            ))

        # Check proximity to any angle (within 1% = potential support/resistance)
        for angle in self.ANGLES:
            for ascending in (True, False):
                level = self.calculate_level(pivot_price, days, angle, ascending)
                if level > 0:
                    proximity = abs(current_price - level) / level
                    if proximity < 0.01:  # Within 1%
                        direction = Direction.BULLISH if current_price > level else Direction.BEARISH
                        signals.append(Signal(
                            source=SignalSource.GANN_ANGLE,
                            direction=direction,
                            strength=0.8,
                            description=(
                                f"Prezzo a contatto con angolo {angle.label} "
                                f"({'asc' if ascending else 'disc'}) = {level:.2f} — "
                                f"supporto/resistenza critico"
                            ),
                            date=current_date,
                            metadata={"angle": angle.label, "level": level, "proximity": proximity},
                        ))
        return signals
