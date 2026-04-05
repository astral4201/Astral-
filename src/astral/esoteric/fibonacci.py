"""Fibonacci / Phi golden ratio calculations.

"Fibonacci non è solo tecnica — è la SPIRALE DIVINA che governa galassie,
nautilus, girasoli e mercati." — W.D. Gann
"""

from __future__ import annotations


PHI = 1.6180339887498948
PHI_INV = 0.6180339887498948

# Standard Fibonacci retracement levels
RETRACEMENTS = {
    "0.0%": 0.0,
    "23.6%": 0.236,
    "38.2%": 0.382,
    "50.0%": 0.5,
    "61.8%": 0.618,  # The sacred level
    "78.6%": 0.786,
    "100.0%": 1.0,
}

# Fibonacci extension levels
EXTENSIONS = {
    "127.2%": 1.272,
    "138.2%": 1.382,
    "161.8%": 1.618,  # Phi
    "200.0%": 2.0,
    "261.8%": 2.618,  # Phi²
    "361.8%": 3.618,
    "423.6%": 4.236,
}


class FibonacciLevels:
    """Calculates Fibonacci retracements and extensions."""

    def retracements(self, high: float, low: float) -> dict[str, float]:
        """Calculate retracement levels between a swing high and low."""
        diff = high - low
        return {
            label: round(high - diff * ratio, 2)
            for label, ratio in RETRACEMENTS.items()
        }

    def extensions(self, high: float, low: float) -> dict[str, float]:
        """Calculate extension levels beyond a swing."""
        diff = high - low
        return {
            label: round(high + diff * (ratio - 1), 2)
            for label, ratio in EXTENSIONS.items()
        }

    def all_levels(self, high: float, low: float) -> dict[str, float]:
        """Get all Fibonacci levels (retracements + extensions)."""
        return {**self.retracements(high, low), **self.extensions(high, low)}
