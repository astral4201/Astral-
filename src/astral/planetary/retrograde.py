"""Planetary retrograde detection.

A planet is retrograde when its apparent motion reverses direction
(speed < 0 in the ephemeris). Key retrogrades for markets:
- Mercury (3x/year, ~3 weeks): communication/transport disruptions, contract issues
- Venus (~every 18 months): value reassessment, relationship with money
- Mars (~every 2 years): energy/conflict reversals
"""

from __future__ import annotations

from datetime import date, timedelta

from astral.core.models import Planet, Signal, SignalSource, Direction
from astral.planetary.ephemeris import Ephemeris


# Financial impact of retrogrades by planet
RETROGRADE_MEANING = {
    Planet.MERCURY: (
        "Mercurio Retrogrado: comunicazioni errate, contratti problematici, "
        "errori tecnici. Evitare nuove posizioni. Mercati confusi e volatili."
    ),
    Planet.VENUS: (
        "Venere Retrograda: rivalutazione del valore, inversioni di prezzo. "
        "Settori lusso/finanza sotto pressione. Possibili bottom."
    ),
    Planet.MARS: (
        "Marte Retrogrado: energia bloccata, conflitti latenti. "
        "Volatilità compressa che esplode alla stazione diretta."
    ),
    Planet.JUPITER: (
        "Giove Retrogrado: espansione rallenta, ottimismo si ridimensiona. "
        "Riesame delle strategie di crescita."
    ),
    Planet.SATURN: (
        "Saturno Retrogrado: strutture vengono riesaminate. "
        "Regolamentazione e restrizioni sotto revisione."
    ),
}


class RetrogradeDetector:
    """Detects planetary retrogrades and their market implications."""

    def __init__(self, ephemeris: Ephemeris):
        self.eph = ephemeris

    def is_retrograde(self, planet: Planet, d: date) -> bool:
        """Check if a planet is retrograde on a given date."""
        pos = self.eph.get_planet_position(planet, d)
        return pos.is_retrograde

    def check_station(self, planet: Planet, d: date, window_days: int = 3) -> str | None:
        """Check if a planet is near a station (turning point).

        Stations are the most powerful retrograde points:
        - Station Retrograde: planet about to go Rx
        - Station Direct: planet about to go direct
        """
        pos_before = self.eph.get_planet_position(planet, d - timedelta(days=window_days))
        pos_now = self.eph.get_planet_position(planet, d)
        pos_after = self.eph.get_planet_position(planet, d + timedelta(days=window_days))

        if not pos_before.is_retrograde and pos_after.is_retrograde:
            return "stazione_retrograda"
        elif pos_before.is_retrograde and not pos_after.is_retrograde:
            return "stazione_diretta"
        return None

    def get_retrograde_signals(self, d: date) -> list[Signal]:
        """Get retrograde signals for all financially relevant planets."""
        signals = []
        key_planets = [Planet.MERCURY, Planet.VENUS, Planet.MARS, Planet.JUPITER, Planet.SATURN]

        for planet in key_planets:
            if self.is_retrograde(planet, d):
                station = self.check_station(planet, d)
                meaning = RETROGRADE_MEANING.get(planet, f"{planet.label_it} retrogrado.")

                strength = 0.6
                extra = ""
                if station == "stazione_retrograda":
                    strength = 0.85
                    extra = " ⚠️ STAZIONE RETROGRADA — massima turbolenza!"
                elif station == "stazione_diretta":
                    strength = 0.8
                    extra = " ✦ STAZIONE DIRETTA — energia si sblocca!"

                signals.append(Signal(
                    source=SignalSource.PLANETARY_RETROGRADE,
                    direction=Direction.BEARISH if planet in (Planet.MERCURY, Planet.VENUS) else Direction.LATERAL,
                    strength=strength,
                    description=f"{planet.symbol} {meaning}{extra}",
                    date=d,
                    metadata={"planet": planet.name, "station": station},
                ))

        return signals
