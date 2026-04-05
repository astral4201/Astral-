"""Swiss Ephemeris wrapper for planetary position calculations.

Uses pyswisseph to calculate precise planetary longitudes, latitudes,
distances and speeds for any date. This is the foundation for all
astrological analysis.
"""

from __future__ import annotations

from datetime import date, datetime

import swisseph as swe

from astral.core.models import Planet, PlanetPosition

# Zodiac signs in order (0° Aries = 0)
ZODIAC_SIGNS = [
    "Ariete", "Toro", "Gemelli", "Cancro",
    "Leone", "Vergine", "Bilancia", "Scorpione",
    "Sagittario", "Capricorno", "Acquario", "Pesci",
]


def _longitude_to_sign(longitude: float) -> tuple[str, float]:
    """Convert ecliptic longitude to zodiac sign and degree within sign."""
    sign_index = int(longitude / 30) % 12
    degree = longitude % 30
    return ZODIAC_SIGNS[sign_index], degree


def date_to_jd(d: date) -> float:
    """Convert a Python date to Julian Day (UT)."""
    return swe.julday(d.year, d.month, d.day, 0.0)


class Ephemeris:
    """Swiss Ephemeris wrapper for planetary calculations."""

    # Planets we track
    PLANETS = list(Planet)

    def __init__(self):
        # Use bundled ephemeris data
        swe.set_ephe_path(None)

    def get_planet_position(self, planet: Planet, d: date) -> PlanetPosition:
        """Get the position of a planet on a given date."""
        jd = date_to_jd(d)
        # swe.calc_ut returns (longitude, latitude, distance, speed_lon, speed_lat, speed_dist)
        result, _flags = swe.calc_ut(jd, planet.swe_id)
        longitude = result[0]
        latitude = result[1]
        distance = result[2]
        speed = result[3]

        sign, deg_in_sign = _longitude_to_sign(longitude)

        return PlanetPosition(
            planet=planet,
            longitude=longitude,
            latitude=latitude,
            distance=distance,
            speed=speed,
            sign=sign,
            degree_in_sign=deg_in_sign,
        )

    def get_all_positions(self, d: date) -> dict[Planet, PlanetPosition]:
        """Get positions of all tracked planets."""
        return {p: self.get_planet_position(p, d) for p in self.PLANETS}

    def get_node_position(self, d: date) -> float:
        """Get the True Node (Rahu) longitude — needed for eclipse detection."""
        jd = date_to_jd(d)
        result, _flags = swe.calc_ut(jd, swe.TRUE_NODE)
        return result[0]
