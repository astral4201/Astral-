"""Major planetary cycles relevant to financial markets.

Key cycles:
- Jupiter-Saturn (~20 years): economic expansion/contraction
- Saturn-Pluto (~33-38 years): major structural crises
- Jupiter-Pluto (~12-13 years): wealth/power cycles
"""

from __future__ import annotations

from datetime import date

from astral.core.models import Planet, Signal, SignalSource, Direction
from astral.planetary.ephemeris import Ephemeris
from astral.planetary.aspects import angular_distance


# Known conjunction dates for major cycles
JUPITER_SATURN_CONJUNCTIONS = [
    date(1901, 11, 28), date(1921, 9, 10), date(1940, 8, 8),
    date(1940, 10, 20), date(1941, 2, 15), date(1961, 2, 19),
    date(1980, 12, 31), date(2000, 5, 28), date(2020, 12, 21),
]

SATURN_PLUTO_CONJUNCTIONS = [
    date(1914, 10, 4), date(1947, 8, 11), date(1982, 11, 8), date(2020, 1, 12),
]


class PlanetaryCycles:
    """Analyzes major planetary cycles and their market implications."""

    def __init__(self, ephemeris: Ephemeris):
        self.eph = ephemeris

    def get_cycle_phase(
        self,
        planet1: Planet,
        planet2: Planet,
        d: date,
    ) -> tuple[str, float]:
        """Determine the current phase of a planetary cycle.

        Returns (phase_name, degrees_into_cycle).
        Phases: Congiunzione (0°), Crescente (90°), Opposizione (180°), Calante (270°).
        """
        pos1 = self.eph.get_planet_position(planet1, d)
        pos2 = self.eph.get_planet_position(planet2, d)

        # Angular separation (faster planet from slower)
        diff = (pos1.longitude - pos2.longitude) % 360

        if diff < 90:
            phase = "Congiunzione → Quadratura crescente"
        elif diff < 180:
            phase = "Quadratura crescente → Opposizione"
        elif diff < 270:
            phase = "Opposizione → Quadratura calante"
        else:
            phase = "Quadratura calante → Congiunzione"

        return phase, round(diff, 2)

    def analyze_jupiter_saturn(self, d: date) -> Signal:
        """Analyze the Jupiter-Saturn cycle (~20 years).

        This cycle governs major economic expansions and contractions.
        Conjunction = new economic era. Opposition = peak/crisis.
        """
        phase, degrees = self.get_cycle_phase(Planet.JUPITER, Planet.SATURN, d)

        # Find nearest past conjunction
        past = [c for c in JUPITER_SATURN_CONJUNCTIONS if c <= d]
        last_conj = past[-1] if past else date(2020, 12, 21)
        years_since = (d - last_conj).days / 365.25

        if degrees < 90:
            direction = Direction.BULLISH
            desc = f"Fase espansiva post-congiunzione ({years_since:.1f} anni). Crescita economica."
        elif degrees < 180:
            direction = Direction.BULLISH
            desc = f"Fase di maturazione ({years_since:.1f} anni). Espansione rallenta."
        elif degrees < 270:
            direction = Direction.BEARISH
            desc = f"Fase di contrazione/opposizione ({years_since:.1f} anni). Tensioni economiche."
        else:
            direction = Direction.BEARISH
            desc = f"Fase terminale del ciclo ({years_since:.1f} anni). Preparazione al reset."

        return Signal(
            source=SignalSource.PLANETARY_CYCLE,
            direction=direction,
            strength=0.8,
            description=(
                f"Ciclo ♃ Giove - ♄ Saturno (20 anni): {phase} ({degrees}°). "
                f"Ultima congiunzione: {last_conj.isoformat()}. {desc}"
            ),
            date=d,
            metadata={"cycle": "Jupiter-Saturn", "degrees": degrees, "phase": phase},
        )

    def analyze_saturn_pluto(self, d: date) -> Signal:
        """Analyze the Saturn-Pluto cycle (~33-38 years).

        This cycle governs major structural transformations and crises.
        1914 (WWI), 1947 (Cold War), 1982 (Volcker), 2020 (COVID).
        """
        phase, degrees = self.get_cycle_phase(Planet.SATURN, Planet.PLUTO, d)

        past = [c for c in SATURN_PLUTO_CONJUNCTIONS if c <= d]
        last_conj = past[-1] if past else date(2020, 1, 12)
        years_since = (d - last_conj).days / 365.25

        if degrees < 90:
            direction = Direction.LATERAL
            desc = f"Nuova struttura in formazione ({years_since:.1f} anni dalla congiunzione)."
        elif degrees < 180:
            direction = Direction.BEARISH
            desc = f"Tensione strutturale crescente ({years_since:.1f} anni). Attenzione a crisi."
        elif degrees < 270:
            direction = Direction.BEARISH
            desc = f"Crisi e trasformazione attiva ({years_since:.1f} anni)."
        else:
            direction = Direction.LATERAL
            desc = f"Dissoluzione del vecchio ordine ({years_since:.1f} anni). Transizione."

        return Signal(
            source=SignalSource.PLANETARY_CYCLE,
            direction=direction,
            strength=0.75,
            description=(
                f"Ciclo ♄ Saturno - ♇ Plutone (33-38 anni): {phase} ({degrees}°). "
                f"Ultima congiunzione: {last_conj.isoformat()}. {desc}"
            ),
            date=d,
            metadata={"cycle": "Saturn-Pluto", "degrees": degrees, "phase": phase},
        )

    def get_all_cycle_signals(self, d: date) -> list[Signal]:
        """Get signals from all major planetary cycles."""
        return [
            self.analyze_jupiter_saturn(d),
            self.analyze_saturn_pluto(d),
        ]
