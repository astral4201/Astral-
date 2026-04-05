"""US Presidential Cycle analysis.

The 4-year presidential cycle shows consistent market patterns:
- Year 1 (post-inauguration): reforms, bearish tendency
- Year 2 (midterm): worst year, bottoming
- Year 3 (pre-election): best year, stimulus
- Year 4 (election): bullish early, uncertain late
"""

from __future__ import annotations

from datetime import date

from astral.core.models import Direction, Signal, SignalSource


# Election years (November) - used to calculate cycle position
# The cycle year starts from inauguration (January 20th)
def _get_cycle_year(d: date) -> int:
    """Get the year in the presidential cycle (1-4)."""
    # Last election was 2024, next is 2028
    # Year 1 starts Jan 20 of year after election
    year = d.year
    # Find most recent election year
    election_year = year - ((year - 2024) % 4)
    if election_year > year:
        election_year -= 4

    # Inauguration is Jan 20 of the year after election
    inauguration_year = election_year + 1

    cycle_year = year - inauguration_year + 1

    # Handle edge case: before inauguration in inauguration year
    if year == inauguration_year and d.month == 1 and d.day < 20:
        cycle_year = 4  # Still in previous cycle

    # Clamp to 1-4
    cycle_year = ((cycle_year - 1) % 4) + 1
    return cycle_year


CYCLE_PROFILES = {
    1: ("Post-inaugurazione", Direction.BEARISH, 0.5,
        "Anno 1: il nuovo presidente implementa riforme. Mercati incerti. Storicamente debole."),
    2: ("Midterm", Direction.BEARISH, 0.6,
        "Anno 2: midterm elections. Anno peggiore del ciclo. Bottom tipico in Q3-Q4."),
    3: ("Pre-elezione", Direction.BULLISH, 0.7,
        "Anno 3: pre-elettorale. ANNO MIGLIORE del ciclo. Stimoli e ottimismo."),
    4: ("Elezione", Direction.BULLISH, 0.5,
        "Anno 4: anno elettorale. Rialzista nella prima metà, incertezza nella seconda."),
}


class PresidentialCycle:
    """Analyzes the US presidential cycle position."""

    def get_cycle_year(self, d: date) -> tuple[int, str]:
        """Get the current cycle year and its label."""
        year = _get_cycle_year(d)
        label = CYCLE_PROFILES[year][0]
        return year, label

    def get_signal(self, d: date) -> Signal:
        """Generate a presidential cycle signal."""
        year = _get_cycle_year(d)
        label, direction, strength, description = CYCLE_PROFILES[year]

        return Signal(
            source=SignalSource.HISTORICAL_PRESIDENTIAL,
            direction=direction,
            strength=strength,
            description=f"Ciclo Presidenziale USA — Anno {year}/4 ({label}): {description}",
            date=d,
            metadata={"cycle_year": year, "label": label},
        )
