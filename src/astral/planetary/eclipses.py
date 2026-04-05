"""Eclipse detection and market impact analysis.

Solar eclipses mark major trend changes (0-3 month impact window).
Lunar eclipses amplify volatility.
An eclipse near a Gann angle = maximum confluence.
"""

from __future__ import annotations

from datetime import date, timedelta

from astral.core.models import (
    EclipseEvent, Planet, Signal, SignalSource, Direction,
)
from astral.planetary.ephemeris import Ephemeris
from astral.planetary.aspects import angular_distance


class EclipseDetector:
    """Detects solar and lunar eclipses and their market impact windows."""

    # Eclipse conditions: Sun-Moon alignment near the lunar nodes
    # Solar eclipse: New Moon (conjunction) within ~18° of a node
    # Lunar eclipse: Full Moon (opposition) within ~12° of a node
    SOLAR_NODE_ORB = 18.0
    LUNAR_NODE_ORB = 12.0

    def __init__(self, ephemeris: Ephemeris, impact_window_days: int = 90):
        self.eph = ephemeris
        self.impact_window_days = impact_window_days

    def _check_eclipse(self, d: date) -> EclipseEvent | None:
        """Check if a given date has an eclipse (approximate)."""
        sun_pos = self.eph.get_planet_position(Planet.SUN, d)
        moon_pos = self.eph.get_planet_position(Planet.MOON, d)
        node_lon = self.eph.get_node_position(d)

        sun_moon_dist = angular_distance(sun_pos.longitude, moon_pos.longitude)

        # Solar eclipse: Sun-Moon conjunction near node
        if sun_moon_dist < 5.0:  # Near conjunction (New Moon)
            sun_node_dist = angular_distance(sun_pos.longitude, node_lon)
            if sun_node_dist < self.SOLAR_NODE_ORB:
                return EclipseEvent(
                    eclipse_type="solare",
                    date=d,
                    longitude=sun_pos.longitude,
                    description=(
                        f"Eclissi Solare a {sun_pos.longitude:.1f}° ({sun_pos.sign}). "
                        f"Cambio di trend maggiore entro 0-3 mesi. "
                        f"I mercati non saranno più gli stessi."
                    ),
                    impact_window_end=d + timedelta(days=self.impact_window_days),
                )

        # Lunar eclipse: Sun-Moon opposition near node
        if abs(sun_moon_dist - 180) < 5.0:  # Near opposition (Full Moon)
            moon_node_dist = angular_distance(moon_pos.longitude, node_lon)
            if moon_node_dist < self.LUNAR_NODE_ORB:
                return EclipseEvent(
                    eclipse_type="lunare",
                    date=d,
                    longitude=moon_pos.longitude,
                    description=(
                        f"Eclissi Lunare a {moon_pos.longitude:.1f}° ({moon_pos.sign}). "
                        f"Volatilità amplificata. Emozioni estreme sui mercati."
                    ),
                    impact_window_end=d + timedelta(days=self.impact_window_days),
                )

        return None

    def find_eclipses(
        self,
        start_date: date,
        end_date: date,
    ) -> list[EclipseEvent]:
        """Find all eclipses in a date range.

        Scans day-by-day (eclipses are rare enough that this is efficient).
        """
        eclipses = []
        current = start_date
        last_eclipse_date = None

        while current <= end_date:
            eclipse = self._check_eclipse(current)
            if eclipse:
                # Avoid duplicates (eclipses span a few days)
                if last_eclipse_date is None or (current - last_eclipse_date).days > 5:
                    eclipses.append(eclipse)
                    last_eclipse_date = current
            current += timedelta(days=1)

        return eclipses

    def find_recent_eclipses(self, d: date) -> list[Signal]:
        """Find eclipses within the impact window of the given date."""
        signals = []
        # Look back up to impact_window_days
        start = d - timedelta(days=self.impact_window_days)
        eclipses = self.find_eclipses(start, d + timedelta(days=30))

        for ecl in eclipses:
            if ecl.date <= d and ecl.impact_window_end >= d:
                days_since = (d - ecl.date).days
                remaining = (ecl.impact_window_end - d).days
                strength = 0.9 if ecl.eclipse_type == "solare" else 0.7

                signals.append(Signal(
                    source=SignalSource.PLANETARY_ECLIPSE,
                    direction=Direction.LATERAL,
                    strength=strength,
                    description=(
                        f"Eclissi {ecl.eclipse_type} del {ecl.date.isoformat()} ancora attiva. "
                        f"{ecl.description} "
                        f"Giorni trascorsi: {days_since}. Finestra residua: {remaining}d."
                    ),
                    date=d,
                    metadata={
                        "eclipse_type": ecl.eclipse_type,
                        "eclipse_date": ecl.date.isoformat(),
                        "longitude": ecl.longitude,
                    },
                ))
            elif ecl.date > d:
                days_until = (ecl.date - d).days
                signals.append(Signal(
                    source=SignalSource.PLANETARY_ECLIPSE,
                    direction=Direction.LATERAL,
                    strength=0.5,
                    description=(
                        f"Eclissi {ecl.eclipse_type} in arrivo il {ecl.date.isoformat()} "
                        f"(tra {days_until} giorni). Prepararsi a un cambio di regime."
                    ),
                    date=d,
                    metadata={
                        "eclipse_type": ecl.eclipse_type,
                        "eclipse_date": ecl.date.isoformat(),
                    },
                ))

        return signals
