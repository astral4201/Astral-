"""Decennial (10-year) cycle analysis.

Years ending in specific digits show historical tendencies:
- Years ending in 5: historically strong
- Years ending in 7: often crashes (1907, 1937, 1987, 2007)
- Years ending in 0: mixed/transition
"""

from __future__ import annotations

from datetime import date

from astral.core.models import Direction, Signal, SignalSource


DECENNIAL_PATTERNS = {
    0: ("Transizione", Direction.LATERAL, 0.4,
        "Anni '0': transizione. 1900-laterale, 1930-crisi, 1960-top, 1990-forte, 2000-crash, 2010-ripresa, 2020-crash/ripresa."),
    1: ("Rialzo post-crisi", Direction.BULLISH, 0.5,
        "Anni '1': spesso recupero post-crisi. 1921-bull, 1991-bull, 2011-QE rally."),
    2: ("Incertezza", Direction.BEARISH, 0.5,
        "Anni '2': incerti. 1932-bottom, 1962-Cuban crisis, 2002-bottom, 2022-bear."),
    3: ("Ripresa", Direction.BULLISH, 0.5,
        "Anni '3': recupero. 1933-New Deal rally, 2003-bull start, 2013-QE rally."),
    4: ("Laterale/debole", Direction.LATERAL, 0.4,
        "Anni '4': deboli/laterali. 1934-laterale, 1974-bottom, 2014-laterale."),
    5: ("FORTE", Direction.BULLISH, 0.7,
        "Anni '5': storicamente i PIÙ FORTI del decennio. 1925, 1955, 1985, 1995, 2005 tutti rialzisti."),
    6: ("Rialzo maturo", Direction.BULLISH, 0.5,
        "Anni '6': continuazione rialzista. 1926, 1986, 1996, 2006 tutti positivi. Ma il top si avvicina."),
    7: ("⚠️ PERICOLO", Direction.BEARISH, 0.8,
        "Anni '7': MASSIMO PERICOLO. 1907-panico, 1937-crash, 1987-Black Monday, 2007-top pre-GFC. Pattern mortale."),
    8: ("Crash/bottom", Direction.BEARISH, 0.6,
        "Anni '8': spesso crash o bottom. 1908-bottom, 1938-bottom, 1998-LTCM, 2008-Lehman."),
    9: ("Recupero forte", Direction.BULLISH, 0.6,
        "Anni '9': recupero dopo crisi. 1909-bull, 1949-bottom/bull, 1999-tech bubble, 2009-bottom epico."),
}


class DecennialCycle:
    """Analyzes the decennial (10-year) cycle pattern."""

    def get_pattern(self, d: date) -> tuple[int, str]:
        """Get the decennial digit and its label."""
        digit = d.year % 10
        label = DECENNIAL_PATTERNS[digit][0]
        return digit, label

    def get_signal(self, d: date) -> Signal:
        """Generate a decennial cycle signal."""
        digit = d.year % 10
        label, direction, strength, description = DECENNIAL_PATTERNS[digit]

        return Signal(
            source=SignalSource.HISTORICAL_DECENNIAL,
            direction=direction,
            strength=strength,
            description=f"Ciclo Decennale — Anno che finisce in {digit} ({label}): {description}",
            date=d,
            metadata={"digit": digit, "label": label},
        )
