"""Kondratieff Wave (Long Wave) cycle analysis.

The Kondratieff cycle is a ~50-60 year economic cycle with four seasons:
- Spring (recovery/expansion)
- Summer (inflation/overheating)
- Autumn (speculation/plateau)
- Winter (deflation/crisis)
"""

from __future__ import annotations

from datetime import date

from astral.core.models import Direction, KondSeason, Signal, SignalSource


# Approximate US Kondratieff wave dating
WAVE_PERIODS = [
    # Wave 3
    (KondSeason.SPRING, 1896, 1907),
    (KondSeason.SUMMER, 1907, 1920),
    (KondSeason.AUTUMN, 1920, 1929),
    (KondSeason.WINTER, 1929, 1949),
    # Wave 4
    (KondSeason.SPRING, 1949, 1966),
    (KondSeason.SUMMER, 1966, 1982),
    (KondSeason.AUTUMN, 1982, 2000),
    (KondSeason.WINTER, 2000, 2009),
    # Wave 5 (current, projected)
    (KondSeason.SPRING, 2009, 2025),
    (KondSeason.SUMMER, 2025, 2040),
    (KondSeason.AUTUMN, 2040, 2055),
    (KondSeason.WINTER, 2055, 2070),
]

SEASON_DIRECTION = {
    KondSeason.SPRING: Direction.BULLISH,
    KondSeason.SUMMER: Direction.LATERAL,
    KondSeason.AUTUMN: Direction.BULLISH,
    KondSeason.WINTER: Direction.BEARISH,
}

SEASON_CHARACTERISTICS = {
    KondSeason.SPRING: {
        "inflazione": "Bassa → in crescita",
        "tassi": "Bassi → in crescita",
        "mercati": "Bull market strutturale",
        "asset_migliori": "Azioni, immobili",
    },
    KondSeason.SUMMER: {
        "inflazione": "Alta e crescente",
        "tassi": "In forte crescita",
        "mercati": "Volatili, laterali in termini reali",
        "asset_migliori": "Commodities, oro, TIPS",
    },
    KondSeason.AUTUMN: {
        "inflazione": "In calo",
        "tassi": "In calo",
        "mercati": "Speculazione sfrenata, bolle",
        "asset_migliori": "Azioni growth, tech, credito",
    },
    KondSeason.WINTER: {
        "inflazione": "Deflazione / molto bassa",
        "tassi": "Zero / negativi",
        "mercati": "Bear market, crisi del debito",
        "asset_migliori": "Cash, treasuries, oro",
    },
}


class KondratieffWave:
    """Analyzes the current position in the Kondratieff long-wave cycle."""

    def current_season(self, d: date) -> tuple[KondSeason, float]:
        """Determine the current Kondratieff season and position within it.

        Returns (season, position_pct) where position_pct is 0.0 to 1.0.
        """
        year = d.year
        for season, start_year, end_year in WAVE_PERIODS:
            if start_year <= year < end_year:
                duration = end_year - start_year
                position = (year - start_year) / duration
                return season, round(position, 2)

        # Default to projected values
        return KondSeason.SUMMER, 0.0

    def get_signal(self, d: date) -> Signal:
        """Generate a Kondratieff wave signal for the given date."""
        season, position = self.current_season(d)
        chars = SEASON_CHARACTERISTICS[season]
        direction = SEASON_DIRECTION[season]

        char_text = " | ".join(f"{k}: {v}" for k, v in chars.items())

        return Signal(
            source=SignalSource.HISTORICAL_KONDRATIEFF,
            direction=direction,
            strength=0.7,
            description=(
                f"Ciclo di Kondratieff (50-60 anni): {season.label_it} — "
                f"{season.description}. Posizione: {position:.0%} nella fase. "
                f"[{char_text}]"
            ),
            date=d,
            metadata={
                "season": season.name,
                "position": position,
                "characteristics": chars,
            },
        )
