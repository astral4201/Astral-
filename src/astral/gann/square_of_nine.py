"""Gann Square of Nine Calculator.

The Square of Nine is a spiral of numbers starting from 1 at the center.
Numbers on the same geometric angle (0°, 90°, 180°, 270°, 360°) from the
center form natural support and resistance levels.

Core formula:
  level_up(price, degrees) = (√price + degrees/360)²
  level_down(price, degrees) = (√price - degrees/360)²
"""

from __future__ import annotations

import math
from datetime import date

from astral.core.models import Direction, GannLevel, Signal, SignalSource


class SquareOfNine:
    """Gann's Square of Nine spiral price calculator."""

    # Standard rotation angles
    ROTATIONS = [90, 180, 270, 360]

    @staticmethod
    def level_up(price: float, degrees: float) -> float:
        """Calculate resistance level by rotating UP on the spiral."""
        sqrt_p = math.sqrt(price)
        return (sqrt_p + degrees / 360.0) ** 2

    @staticmethod
    def level_down(price: float, degrees: float) -> float:
        """Calculate support level by rotating DOWN on the spiral."""
        sqrt_p = math.sqrt(price)
        result = sqrt_p - degrees / 360.0
        if result <= 0:
            return 0.0
        return result ** 2

    def get_cardinal_levels(self, price: float) -> list[GannLevel]:
        """Get all cardinal support/resistance levels at 90°, 180°, 270°, 360°."""
        levels = []
        for deg in self.ROTATIONS:
            # Resistance (up)
            up = self.level_up(price, deg)
            levels.append(GannLevel(
                price=round(up, 2),
                level_type=f"sq9_{deg}_up",
                direction=Direction.BULLISH,
                description=f"Square of 9: resistenza a +{deg}° = {up:.2f}",
            ))
            # Support (down)
            down = self.level_down(price, deg)
            if down > 0:
                levels.append(GannLevel(
                    price=round(down, 2),
                    level_type=f"sq9_{deg}_down",
                    direction=Direction.BEARISH,
                    description=f"Square of 9: supporto a -{deg}° = {down:.2f}",
                ))

        # Multi-rotation levels (720°, 1080° for longer-term)
        for mult in [2, 3]:
            deg = 360 * mult
            up = self.level_up(price, deg)
            levels.append(GannLevel(
                price=round(up, 2),
                level_type=f"sq9_{deg}_up",
                direction=Direction.BULLISH,
                description=f"Square of 9: resistenza a +{deg}° ({mult} rotazioni) = {up:.2f}",
            ))
            down = self.level_down(price, deg)
            if down > 0:
                levels.append(GannLevel(
                    price=round(down, 2),
                    level_type=f"sq9_{deg}_down",
                    direction=Direction.BEARISH,
                    description=f"Square of 9: supporto a -{deg}° ({mult} rotazioni) = {down:.2f}",
                ))
        return levels

    def get_angle_of_price(self, price: float, center: float = 1.0) -> float:
        """Get the angular position of a price on the spiral (in degrees)."""
        if price <= 0 or center <= 0:
            return 0.0
        return (math.sqrt(price) - math.sqrt(center)) * 360.0

    def analyze(self, current_price: float, analysis_date: date) -> tuple[list[GannLevel], list[Signal]]:
        """Full Square of Nine analysis: levels + proximity signals."""
        levels = self.get_cardinal_levels(current_price)
        signals = []

        # Check if price is near a cardinal cross (angular position close to 0/90/180/270)
        angle = self.get_angle_of_price(current_price) % 360
        for cardinal in [0, 90, 180, 270]:
            diff = min(abs(angle - cardinal), 360 - abs(angle - cardinal))
            if diff < 5:  # Within 5 degrees of a cardinal point
                signals.append(Signal(
                    source=SignalSource.GANN_SQUARE9,
                    direction=Direction.LATERAL,  # turning point
                    strength=0.8,
                    description=(
                        f"Prezzo {current_price:.2f} si trova a {angle:.1f}° sulla spirale — "
                        f"vicino alla croce cardinale {cardinal}° (differenza {diff:.1f}°). "
                        f"Punto di svolta potenziale."
                    ),
                    date=analysis_date,
                    metadata={"spiral_angle": angle, "nearest_cardinal": cardinal},
                ))
        return levels, signals
