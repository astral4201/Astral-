"""Moon phase calculator.

New Moons and Full Moons are significant volatility markers.
New Moon = potential new trend. Full Moon = culmination/reversal.
"""

from __future__ import annotations

from datetime import date, timedelta

from astral.core.models import (
    MoonPhase, MoonPhaseName, Planet, Signal, SignalSource, Direction,
)
from astral.planetary.ephemeris import Ephemeris
from astral.planetary.aspects import angular_distance


class MoonPhaseCalculator:
    """Calculates moon phases and their market significance."""

    def __init__(self, ephemeris: Ephemeris):
        self.eph = ephemeris

    def get_phase(self, d: date) -> MoonPhase:
        """Determine the current moon phase."""
        sun = self.eph.get_planet_position(Planet.SUN, d)
        moon = self.eph.get_planet_position(Planet.MOON, d)

        # Phase angle: Moon longitude - Sun longitude (mod 360)
        phase_angle = (moon.longitude - sun.longitude) % 360

        # Approximate illumination
        illumination = (1 - abs(phase_angle - 180) / 180)

        # Determine phase name
        if phase_angle < 22.5 or phase_angle >= 337.5:
            name = MoonPhaseName.NEW_MOON
        elif phase_angle < 67.5:
            name = MoonPhaseName.WAXING_CRESCENT
        elif phase_angle < 112.5:
            name = MoonPhaseName.FIRST_QUARTER
        elif phase_angle < 157.5:
            name = MoonPhaseName.WAXING_GIBBOUS
        elif phase_angle < 202.5:
            name = MoonPhaseName.FULL_MOON
        elif phase_angle < 247.5:
            name = MoonPhaseName.WANING_GIBBOUS
        elif phase_angle < 292.5:
            name = MoonPhaseName.LAST_QUARTER
        else:
            name = MoonPhaseName.WANING_CRESCENT

        return MoonPhase(
            phase=name,
            illumination=round(illumination, 2),
            date=d,
        )

    def get_signal(self, d: date) -> Signal | None:
        """Get a market signal if the moon is in a significant phase."""
        phase = self.get_phase(d)

        if phase.phase == MoonPhaseName.NEW_MOON:
            return Signal(
                source=SignalSource.PLANETARY_MOON,
                direction=Direction.BULLISH,
                strength=0.5,
                description=(
                    f"☽ Luna Nuova — inizio di un nuovo ciclo lunare. "
                    f"Energia di semina: nuovi trend possono nascere."
                ),
                date=d,
                metadata={"phase": phase.phase.value, "illumination": phase.illumination},
            )
        elif phase.phase == MoonPhaseName.FULL_MOON:
            return Signal(
                source=SignalSource.PLANETARY_MOON,
                direction=Direction.LATERAL,
                strength=0.5,
                description=(
                    f"☽ Luna Piena — culminazione del ciclo. "
                    f"Emozioni al massimo, volatilità elevata. Possibile inversione."
                ),
                date=d,
                metadata={"phase": phase.phase.value, "illumination": phase.illumination},
            )
        elif phase.phase in (MoonPhaseName.FIRST_QUARTER, MoonPhaseName.LAST_QUARTER):
            return Signal(
                source=SignalSource.PLANETARY_MOON,
                direction=Direction.LATERAL,
                strength=0.3,
                description=(
                    f"☽ {phase.phase.value} — punto di tensione nel ciclo lunare. "
                    f"Decisioni e volatilità moderata."
                ),
                date=d,
                metadata={"phase": phase.phase.value, "illumination": phase.illumination},
            )
        return None

    def next_new_moon(self, d: date, max_search_days: int = 35) -> date:
        """Find the next New Moon date."""
        for i in range(1, max_search_days):
            check = d + timedelta(days=i)
            phase = self.get_phase(check)
            if phase.phase == MoonPhaseName.NEW_MOON:
                return check
        return d + timedelta(days=29)  # Approximate

    def next_full_moon(self, d: date, max_search_days: int = 35) -> date:
        """Find the next Full Moon date."""
        for i in range(1, max_search_days):
            check = d + timedelta(days=i)
            phase = self.get_phase(check)
            if phase.phase == MoonPhaseName.FULL_MOON:
                return check
        return d + timedelta(days=15)  # Approximate
