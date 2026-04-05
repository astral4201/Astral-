"""Gann Square of 144 Calculator.

144 is a sacred number in Gann's system (12² = 144, Fibonacci number).
The Square of 144 divides price into grids of 144 units,
with key sub-levels at fractions: 1/8, 1/4, 1/3, 1/2, 2/3, 3/4, 7/8.
"""

from __future__ import annotations

import math
from datetime import date

from astral.core.models import Direction, GannLevel, Signal, SignalSource

# Key fractional sub-levels of 144
FRACTIONS = {
    "1/8": 18,
    "1/4": 36,
    "1/3": 48,
    "3/8": 54,
    "1/2": 72,
    "5/8": 90,
    "2/3": 96,
    "3/4": 108,
    "7/8": 126,
}


class SquareOf144:
    """Gann's Square of 144 grid calculator."""

    BASE = 144

    def get_grid_levels(self, price: float, num_levels: int = 3) -> list[GannLevel]:
        """Calculate the nearest 144-grid levels above and below price."""
        levels = []
        base_multiple = math.floor(price / self.BASE)

        for i in range(-num_levels, num_levels + 1):
            mult = base_multiple + i
            grid_price = mult * self.BASE
            if grid_price <= 0:
                continue
            direction = Direction.BULLISH if grid_price > price else Direction.BEARISH
            levels.append(GannLevel(
                price=round(grid_price, 2),
                level_type=f"sq144_main_{mult}",
                direction=direction,
                description=f"Square of 144: livello {mult}×144 = {grid_price}",
            ))

            # Sub-levels within this 144 block
            block_start = mult * self.BASE
            for frac_name, frac_val in FRACTIONS.items():
                sub_price = block_start + frac_val
                if abs(sub_price - price) < self.BASE:  # Only nearby
                    direction = Direction.BULLISH if sub_price > price else Direction.BEARISH
                    levels.append(GannLevel(
                        price=round(sub_price, 2),
                        level_type=f"sq144_sub_{frac_name}",
                        direction=direction,
                        description=f"Square of 144: {mult}×144 + {frac_name} ({frac_val}) = {sub_price}",
                    ))

        return levels

    def analyze(self, current_price: float, analysis_date: date) -> tuple[list[GannLevel], list[Signal]]:
        """Full Square of 144 analysis."""
        levels = self.get_grid_levels(current_price)
        signals = []

        # Check proximity to a main grid level
        remainder = current_price % self.BASE
        proximity_to_grid = min(remainder, self.BASE - remainder)
        if proximity_to_grid < self.BASE * 0.03:  # Within 3% of a grid line
            nearest_grid = round(current_price / self.BASE) * self.BASE
            signals.append(Signal(
                source=SignalSource.GANN_SQUARE144,
                direction=Direction.LATERAL,
                strength=0.7,
                description=(
                    f"Prezzo {current_price:.2f} vicino al livello 144-grid = {nearest_grid:.0f}. "
                    f"Il numero 144 è sacro — supporto/resistenza divino."
                ),
                date=analysis_date,
                metadata={"nearest_grid": nearest_grid, "distance": proximity_to_grid},
            ))

        return levels, signals
