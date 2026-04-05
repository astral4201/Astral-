"""Gann Time-Price Squaring.

"When time and price are squared, a change in trend is inevitable."
— W.D. Gann

Time-Price squaring occurs when the elapsed time (in trading days × scale)
equals the price range from a pivot. This is one of Gann's most powerful signals.
"""

from __future__ import annotations

import math
from datetime import date

from astral.core.models import Signal, SignalSource, Direction


class TimePriceSquaring:
    """Detects when time and price are 'squared' (equal)."""

    def __init__(self, scale_factor: float = 1.0):
        self.scale_factor = scale_factor

    def check_squaring(
        self,
        pivot_price: float,
        pivot_date: date,
        current_price: float,
        current_date: date,
        tolerance_pct: float = 0.02,
    ) -> list[Signal]:
        """Check if time and price are squared from a pivot point.

        Squaring conditions:
        1. Time (days × scale) ≈ Price range (|current - pivot|)
        2. Time (days × scale) ≈ Current price level (absolute)
        3. √time ≈ √price (harmonic squaring)
        """
        signals = []
        days = (current_date - pivot_date).days
        if days <= 0:
            return signals

        time_value = days * self.scale_factor
        price_range = abs(current_price - pivot_price)

        # Method 1: Time = Price Range
        if price_range > 0:
            ratio = time_value / price_range
            if abs(ratio - 1.0) < tolerance_pct:
                signals.append(Signal(
                    source=SignalSource.GANN_TIME_PRICE,
                    direction=Direction.LATERAL,
                    strength=0.9,
                    description=(
                        f"QUADRATURA TEMPO-PREZZO: Tempo ({time_value:.1f}) = "
                        f"Range Prezzo ({price_range:.1f}). "
                        f"Rapporto = {ratio:.4f}. INVERSIONE IMMINENTE."
                    ),
                    date=current_date,
                    metadata={"time_value": time_value, "price_range": price_range, "ratio": ratio},
                ))

        # Method 2: Time = Absolute Price
        if current_price > 0:
            ratio_abs = time_value / current_price
            if abs(ratio_abs - 1.0) < tolerance_pct:
                signals.append(Signal(
                    source=SignalSource.GANN_TIME_PRICE,
                    direction=Direction.LATERAL,
                    strength=0.85,
                    description=(
                        f"QUADRATURA TEMPO-PREZZO (assoluta): Tempo ({time_value:.1f}) = "
                        f"Prezzo ({current_price:.1f}). "
                        f"Il prezzo ha incontrato il suo riflesso nel tempo."
                    ),
                    date=current_date,
                    metadata={"time_value": time_value, "price": current_price},
                ))

        # Method 3: √Time = √Price (harmonic)
        sqrt_time = math.sqrt(time_value) if time_value > 0 else 0
        sqrt_price = math.sqrt(current_price) if current_price > 0 else 0
        if sqrt_time > 0 and sqrt_price > 0:
            harmonic_ratio = sqrt_time / sqrt_price
            if abs(harmonic_ratio - 1.0) < tolerance_pct:
                signals.append(Signal(
                    source=SignalSource.GANN_TIME_PRICE,
                    direction=Direction.LATERAL,
                    strength=0.85,
                    description=(
                        f"QUADRATURA ARMONICA: √Tempo ({sqrt_time:.2f}) = "
                        f"√Prezzo ({sqrt_price:.2f}). "
                        f"Risonanza armonica divina."
                    ),
                    date=current_date,
                    metadata={"sqrt_time": sqrt_time, "sqrt_price": sqrt_price},
                ))

        return signals
