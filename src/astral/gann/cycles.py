"""Gann Time Cycles.

Gann identified specific time cycles as critical turning points:
30, 45, 60, 90, 120, 144, 180, 210, 240, 270, 300, 330, 360 calendar days.
Also 90, 180, 270, 360 trading days from significant highs/lows.
"""

from __future__ import annotations

from datetime import date, timedelta

from astral.core.models import CycleDate, Signal, SignalSource, Direction


# Standard Gann cycle lengths in calendar days
GANN_CYCLE_DAYS = [30, 45, 60, 90, 120, 144, 180, 210, 240, 270, 300, 330, 360]

# Extended cycles (multiples of 360)
EXTENDED_CYCLES = [540, 720, 1080]

# Sacred number cycles
SACRED_CYCLES = [49, 52, 72, 144, 360]


class GannCycles:
    """Projects future turning-point dates from pivot points using Gann cycles."""

    def __init__(self, cycle_days: list[int] | None = None):
        self.cycle_days = cycle_days or GANN_CYCLE_DAYS

    def project_dates(self, pivot_date: date, pivot_type: str = "low") -> list[CycleDate]:
        """Project all Gann cycle dates forward from a pivot."""
        dates = []
        all_cycles = self.cycle_days + EXTENDED_CYCLES

        for days in all_cycles:
            target = pivot_date + timedelta(days=days)
            cycle_name = f"{days}d" if days <= 360 else f"{days}d ({days // 360}×360)"
            dates.append(CycleDate(
                date=target,
                cycle_name=cycle_name,
                days_from_pivot=days,
                description=(
                    f"Ciclo Gann {days} giorni da {pivot_type} del {pivot_date.isoformat()} "
                    f"→ finestra di inversione {target.isoformat()}"
                ),
            ))
        return dates

    def find_active_cycles(
        self,
        pivot_date: date,
        current_date: date,
        tolerance_days: int = 3,
    ) -> list[Signal]:
        """Find any Gann cycles that are currently active (within tolerance)."""
        signals = []
        elapsed = (current_date - pivot_date).days
        all_cycles = self.cycle_days + EXTENDED_CYCLES

        for cycle in all_cycles:
            distance = abs(elapsed - cycle)
            if distance <= tolerance_days:
                strength = 1.0 - (distance / (tolerance_days + 1))
                signals.append(Signal(
                    source=SignalSource.GANN_CYCLE,
                    direction=Direction.LATERAL,  # Cycle = potential reversal
                    strength=round(strength, 2),
                    description=(
                        f"CICLO GANN ATTIVO: {cycle} giorni dal pivot. "
                        f"Oggi = giorno {elapsed} (distanza {distance}d). "
                        f"'Quando il tempo è scaduto, il prezzo DEVE invertire.'"
                    ),
                    date=current_date,
                    metadata={"cycle_days": cycle, "elapsed": elapsed, "distance": distance},
                ))
        return signals

    def get_upcoming_dates(
        self,
        pivot_date: date,
        current_date: date,
        lookahead_days: int = 30,
    ) -> list[CycleDate]:
        """Get cycle dates falling within the next N days."""
        all_dates = self.project_dates(pivot_date)
        cutoff = current_date + timedelta(days=lookahead_days)
        return [d for d in all_dates if current_date <= d.date <= cutoff]
