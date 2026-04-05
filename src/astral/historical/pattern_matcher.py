"""Historical crisis pattern matching.

Identifies anniversaries and structural similarities between
current market conditions and past crises spanning 100+ years.
"""

from __future__ import annotations

from datetime import date

from astral.core.models import CrisisPattern, HistoricalMatch, Signal, SignalSource, Direction


# Major market crises database
CRISIS_DATABASE = [
    CrisisPattern("Panico del 1907", date(1907, 10, 1), date(1907, 11, 15), -48.0,
                   "Panico bancario, crollo del trust. JP Morgan salva il sistema."),
    CrisisPattern("Crash del 1929", date(1929, 9, 3), date(1932, 7, 8), -89.2,
                   "Il Grande Crollo. Gann lo predisse. Inizio della Grande Depressione."),
    CrisisPattern("Recessione 1937-38", date(1937, 3, 10), date(1938, 3, 31), -49.1,
                   "Doppia recessione nella Depressione. Fed restringe troppo presto."),
    CrisisPattern("Bear Market 1973-74", date(1973, 1, 11), date(1974, 10, 3), -48.2,
                   "Shock petrolifero, Watergate, fine Bretton Woods. Stagflazione."),
    CrisisPattern("Black Monday 1987", date(1987, 8, 25), date(1987, 10, 19), -33.5,
                   "Crash del 22.6% in un giorno. Program trading. Gann cycle da 1929 (58 anni)."),
    CrisisPattern("Crisi LTCM 1998", date(1998, 7, 17), date(1998, 10, 8), -19.3,
                   "Russia default, LTCM collassa. Contagio globale."),
    CrisisPattern("Bolla Dot-Com 2000", date(2000, 3, 24), date(2002, 10, 9), -49.1,
                   "Esplosione bolla internet. NASDAQ -78%. 7 anni dal top 1993."),
    CrisisPattern("Grande Crisi Finanziaria 2008", date(2007, 10, 9), date(2009, 3, 9), -56.8,
                   "Subprime, Lehman Brothers. Crisi sistemica globale. 7 anni da 2000."),
    CrisisPattern("Flash Crash 2010", date(2010, 4, 26), date(2010, 5, 6), -9.2,
                   "Crollo lampo del 9% in minuti. Algoritmi impazziti."),
    CrisisPattern("COVID Crash 2020", date(2020, 2, 19), date(2020, 3, 23), -33.9,
                   "Pandemia globale. Crollo più rapido della storia. V-recovery."),
]

# Sacred year intervals to check (Gann/Biblical)
SACRED_INTERVALS = [7, 10, 12, 14, 20, 21, 25, 28, 30, 33, 36, 49, 50, 60, 72, 84, 90, 100]


class CrisisPatternMatcher:
    """Matches current date against historical crisis patterns."""

    def __init__(self, patterns: list[CrisisPattern] | None = None):
        self.patterns = patterns or CRISIS_DATABASE

    def find_anniversaries(
        self,
        current_date: date,
        tolerance_days: int = 7,
    ) -> list[HistoricalMatch]:
        """Find crisis anniversaries near the current date."""
        matches = []

        for pattern in self.patterns:
            for event_type, event_date in [("peak", pattern.peak_date), ("trough", pattern.trough_date)]:
                for interval in SACRED_INTERVALS:
                    anniversary = date(
                        event_date.year + interval,
                        event_date.month,
                        min(event_date.day, 28),  # Avoid Feb 29 issues
                    )
                    days_diff = abs((current_date - anniversary).days)
                    if days_diff <= tolerance_days:
                        matches.append(HistoricalMatch(
                            pattern=pattern,
                            event_type=event_type,
                            years_ago=interval,
                            anniversary_date=anniversary,
                        ))

        return matches

    def matches_to_signals(self, matches: list[HistoricalMatch], d: date) -> list[Signal]:
        """Convert historical matches to trading signals."""
        signals = []
        for match in matches:
            # Sacred numbers get higher strength
            strength = 0.6
            sacred_note = ""
            if match.years_ago in (7, 49, 50):
                strength = 0.9
                sacred_note = f" NUMERO SACRO: {match.years_ago} (Shemitah/Giubileo)!"
            elif match.years_ago in (12, 60, 84):
                strength = 0.8
                sacred_note = f" Ciclo di {match.years_ago} anni (Giove/Saturno)."
            elif match.years_ago % 10 == 0:
                strength = 0.7
                sacred_note = f" Ciclo decennale ({match.years_ago} anni)."

            direction = Direction.BEARISH if match.event_type == "peak" else Direction.BULLISH

            signals.append(Signal(
                source=SignalSource.HISTORICAL_CRISIS,
                direction=direction,
                strength=strength,
                description=(
                    f"Anniversario {match.years_ago} anni dal {match.event_type} "
                    f"di '{match.pattern.name}' ({match.pattern.peak_date.year}). "
                    f"Declino: {match.pattern.decline_pct}%. "
                    f"{match.pattern.description}{sacred_note}"
                ),
                date=d,
                metadata={
                    "pattern": match.pattern.name,
                    "event_type": match.event_type,
                    "years_ago": match.years_ago,
                    "decline_pct": match.pattern.decline_pct,
                },
            ))
        return signals
