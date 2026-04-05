"""Biblical number cycles.

Key cycles from Gann's biblical analysis:
- Shemitah (7 years): sabbatical year cycle
- Jubilee (49-50 years): freedom/reset cycle
- 144: sacred Gann number (12² = completion × completion)
- 360: prophetic year (12 months × 30 days)
"""

from __future__ import annotations

from datetime import date

from astral.core.models import Direction, Signal, SignalSource


# Reference years for Shemitah cycle (every 7 years)
# Historically aligned with market disruptions
SHEMITAH_YEARS = [
    1901, 1908, 1915, 1922, 1929, 1936, 1943, 1950,
    1957, 1964, 1971, 1978, 1985, 1992, 1999, 2006,
    2013, 2020, 2027, 2034,
]

# Reference years for Jubilee cycle (every 49/50 years)
JUBILEE_YEARS = [1917, 1966, 2015, 2064]

# Key biblical/Gann numbers
SACRED_NUMBERS = {
    7: "Shemitah — ciclo di riposo e rilascio",
    12: "Completamento (12 tribù, 12 mesi, 12 segni zodiacali)",
    40: "Prova e purificazione (40 giorni nel deserto)",
    49: "Giubileo - 1: culminazione del 7° ciclo Shemitah",
    50: "Giubileo: anno di libertà e reset totale",
    70: "Completamento profetico (70 settimane di Daniele)",
    144: "Quadrato sacro di Gann (12×12). Base dello Square of 144",
    360: "Anno cosmico (360 gradi, cerchio completo)",
}


class BiblicalCycles:
    """Analyzes biblical number cycles relevant to markets."""

    def is_shemitah_year(self, d: date) -> bool:
        """Check if the given year is a Shemitah year."""
        return d.year in SHEMITAH_YEARS or (d.year - 2020) % 7 == 0

    def is_jubilee_year(self, d: date) -> bool:
        """Check if the given year is near a Jubilee year."""
        return d.year in JUBILEE_YEARS or (d.year - 2015) % 49 == 0 or (d.year - 2015) % 50 == 0

    def check_cycles(self, d: date) -> list[Signal]:
        """Check all biblical cycles for the given date."""
        signals = []
        year = d.year

        # Shemitah year check
        if self.is_shemitah_year(d):
            # Shemitah ends around September (Elul 29)
            if d.month >= 8 and d.month <= 10:
                strength = 0.8  # Strongest near end of Shemitah
            else:
                strength = 0.6

            signals.append(Signal(
                source=SignalSource.HISTORICAL_BIBLICAL,
                direction=Direction.BEARISH,
                strength=strength,
                description=(
                    f"Anno Shemitah ({year}): il 7° anno del ciclo biblico è un anno di riposo "
                    f"e rilascio dei debiti. Storicamente associato a crolli: "
                    f"1929, 2001, 2008, 2015. Massimo rischio a settembre (Elul 29)."
                ),
                date=d,
                metadata={"cycle": "shemitah", "year": year},
            ))

        # Jubilee check
        if self.is_jubilee_year(d):
            signals.append(Signal(
                source=SignalSource.HISTORICAL_BIBLICAL,
                direction=Direction.LATERAL,
                strength=0.9,
                description=(
                    f"Anno del Giubileo ({year}): il 50° anno — RESET TOTALE. "
                    f"Liberazione dei debiti, redistribuzione della terra. "
                    f"In finanza: cambio di paradigma strutturale."
                ),
                date=d,
                metadata={"cycle": "jubilee", "year": year},
            ))

        # Check if current year distance from major events is a sacred number
        major_events = {
            1929: "Crash del '29",
            1987: "Black Monday",
            2000: "Dot-Com",
            2008: "GFC",
            2020: "COVID",
        }
        for event_year, event_name in major_events.items():
            years_since = year - event_year
            if years_since > 0 and years_since in SACRED_NUMBERS:
                signals.append(Signal(
                    source=SignalSource.HISTORICAL_BIBLICAL,
                    direction=Direction.LATERAL,
                    strength=0.7,
                    description=(
                        f"Numero sacro: {years_since} anni dal {event_name} ({event_year}). "
                        f"{SACRED_NUMBERS[years_since]}."
                    ),
                    date=d,
                    metadata={
                        "sacred_number": years_since,
                        "event": event_name,
                        "event_year": event_year,
                    },
                ))

        return signals
