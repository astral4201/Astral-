"""Planetary aspect detection.

Aspects are angular relationships between planets that are considered
significant in astrological analysis. Each aspect has an orb (tolerance).
"""

from __future__ import annotations

from datetime import date, timedelta
from itertools import combinations

from astral.core.models import (
    AspectType, Planet, PlanetaryAspect, PlanetPosition,
    Signal, SignalSource, Direction,
)
from astral.planetary.ephemeris import Ephemeris

# Default orbs per aspect
DEFAULT_ORBS = {
    AspectType.CONJUNCTION: 8.0,
    AspectType.SEXTILE: 6.0,
    AspectType.SQUARE: 8.0,
    AspectType.TRINE: 8.0,
    AspectType.OPPOSITION: 8.0,
}

# Financial significance of aspects
ASPECT_MARKET_MEANING = {
    AspectType.CONJUNCTION: "Inizio di un nuovo ciclo — energia concentrata",
    AspectType.SEXTILE: "Opportunità — flusso armonico di energia",
    AspectType.SQUARE: "Tensione e conflitto — volatilità elevata",
    AspectType.TRINE: "Armonia e flusso — trend forte e sostenuto",
    AspectType.OPPOSITION: "Polarizzazione — punto di svolta critico",
}

# Planets with highest financial relevance (outer planets = bigger cycles)
FINANCIAL_WEIGHT = {
    Planet.JUPITER: 0.9,   # Espansione
    Planet.SATURN: 0.9,    # Contrazione
    Planet.MARS: 0.7,      # Volatilità
    Planet.VENUS: 0.6,     # Inversioni
    Planet.MERCURY: 0.5,   # Liquidità / comunicazione
    Planet.URANUS: 0.8,    # Shock improvvisi
    Planet.NEPTUNE: 0.6,   # Illusione / bolle
    Planet.PLUTO: 0.85,    # Trasformazione strutturale
    Planet.SUN: 0.4,
    Planet.MOON: 0.3,
}


def angular_distance(lon1: float, lon2: float) -> float:
    """Calculate the shortest angular distance between two longitudes."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


class AspectDetector:
    """Detects planetary aspects and their financial significance."""

    def __init__(self, ephemeris: Ephemeris, orbs: dict[AspectType, float] | None = None):
        self.eph = ephemeris
        self.orbs = orbs or DEFAULT_ORBS

    def detect_aspects(
        self,
        d: date,
        positions: dict[Planet, PlanetPosition] | None = None,
    ) -> list[PlanetaryAspect]:
        """Detect all active aspects on a given date."""
        if positions is None:
            positions = self.eph.get_all_positions(d)

        aspects = []
        # Exclude Moon for major aspects (too fast) — but include for conjunctions
        planets = [p for p in positions if p != Planet.MOON]

        for p1, p2 in combinations(planets, 2):
            lon1 = positions[p1].longitude
            lon2 = positions[p2].longitude
            dist = angular_distance(lon1, lon2)

            for aspect_type in AspectType:
                orb = self.orbs[aspect_type]
                if abs(dist - aspect_type.angle) <= orb:
                    actual_orb = abs(dist - aspect_type.angle)
                    # Determine if applying or separating
                    # (simplified: check if distance is decreasing)
                    speed_diff = positions[p1].speed - positions[p2].speed
                    applying = speed_diff < 0 if lon1 > lon2 else speed_diff > 0

                    aspects.append(PlanetaryAspect(
                        planet1=p1,
                        planet2=p2,
                        aspect=aspect_type,
                        exact_date=d,
                        orb=round(actual_orb, 2),
                        applying=applying,
                    ))
        return aspects

    def aspects_to_signals(self, aspects: list[PlanetaryAspect], d: date) -> list[Signal]:
        """Convert detected aspects to trading signals."""
        signals = []
        for asp in aspects:
            # Weight based on planet significance
            w1 = FINANCIAL_WEIGHT.get(asp.planet1, 0.5)
            w2 = FINANCIAL_WEIGHT.get(asp.planet2, 0.5)
            strength = (w1 + w2) / 2 * (1 - asp.orb / self.orbs[asp.aspect])

            # Direction based on aspect type
            if asp.aspect in (AspectType.TRINE, AspectType.SEXTILE):
                direction = Direction.BULLISH
            elif asp.aspect in (AspectType.SQUARE, AspectType.OPPOSITION):
                direction = Direction.BEARISH
            else:  # Conjunction depends on planets
                direction = Direction.LATERAL

            meaning = ASPECT_MARKET_MEANING[asp.aspect]
            applying_str = "applicante (si avvicina)" if asp.applying else "separante (si allontana)"

            signals.append(Signal(
                source=SignalSource.PLANETARY_ASPECT,
                direction=direction,
                strength=round(max(0.1, min(1.0, strength)), 2),
                description=(
                    f"{asp.planet1.symbol} {asp.planet1.label_it} "
                    f"{asp.aspect.label} "
                    f"{asp.planet2.symbol} {asp.planet2.label_it} "
                    f"(orbe {asp.orb}°, {applying_str}). "
                    f"{meaning}."
                ),
                date=d,
                metadata={
                    "planet1": asp.planet1.name,
                    "planet2": asp.planet2.name,
                    "aspect": asp.aspect.name,
                    "orb": asp.orb,
                },
            ))
        return signals
