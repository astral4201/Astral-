"""Pythagorean numerology for dates and prices.

Numbers are reduced to their root (1-9) by iterative digit summing.
Power numbers in Gann's system: 3 (creativity), 7 (cycles), 9 (completion).
"""

from __future__ import annotations

from datetime import date


# Numerological meanings
NUMBER_MEANINGS = {
    1: "Unità, inizio, leadership — nuovi cicli",
    2: "Dualità, equilibrio, partnership — indecisione",
    3: "Creatività, espressione, crescita — POTENTE per i mercati",
    4: "Stabilità, struttura, fondamenta — consolidamento",
    5: "Cambiamento, libertà, movimento — volatilità",
    6: "Armonia, responsabilità, cura — equilibrio",
    7: "Mistica, analisi, cicli — SACRO NUMERO DI GANN",
    8: "Potere, materialismo, karma — forza e ricchezza",
    9: "Completamento, saggezza, fine ciclo — CHIUSURA",
    11: "Master number — intuizione, visione",
    22: "Master number — costruttore, realizzazione",
    33: "Master number — maestro guaritore",
}

MASTER_NUMBERS = {11, 22, 33}


class Numerology:
    """Pythagorean number reduction and date/price analysis."""

    def reduce(self, n: int) -> int:
        """Reduce a number to its root digit (preserving master numbers)."""
        if n < 0:
            n = abs(n)
        while n >= 10 and n not in MASTER_NUMBERS:
            n = sum(int(d) for d in str(n))
        return n

    def date_vibration(self, d: date) -> int:
        """Calculate the vibrational root of a date."""
        total = d.day + d.month + d.year
        return self.reduce(total)

    def price_vibration(self, price: float) -> int:
        """Calculate the vibrational root of a price."""
        # Use integer part, digit sum
        int_part = int(abs(price))
        return self.reduce(int_part)

    def analyze(self, d: date, price: float) -> dict:
        """Full numerological analysis of a date and price."""
        date_vib = self.date_vibration(d)
        price_vib = self.price_vibration(price)
        combined = self.reduce(date_vib + price_vib)

        resonance = date_vib == price_vib
        is_power = combined in (3, 7, 9) or combined in MASTER_NUMBERS

        return {
            "date_vibration": date_vib,
            "date_meaning": NUMBER_MEANINGS.get(date_vib, ""),
            "price_vibration": price_vib,
            "price_meaning": NUMBER_MEANINGS.get(price_vib, ""),
            "combined": combined,
            "combined_meaning": NUMBER_MEANINGS.get(combined, ""),
            "resonance": resonance,
            "is_power_number": is_power,
            "interpretation": self._interpret(date_vib, price_vib, combined, resonance),
        }

    def _interpret(self, d_vib: int, p_vib: int, combined: int, resonance: bool) -> str:
        """Generate an interpretive statement."""
        if resonance:
            return (
                f"⚡ RISONANZA NUMEROLOGICA: data e prezzo vibrano entrambi al {d_vib}. "
                f"Allineamento vibrazionale raro — il cosmo parla attraverso i numeri."
            )
        if combined in (3, 7, 9):
            return (
                f"Numero di potere combinato: {combined}. "
                f"Vibrazione favorevole ai grandi movimenti di mercato."
            )
        if combined in MASTER_NUMBERS:
            return (
                f"MASTER NUMBER {combined}: portale di destino aperto. "
                f"Eventi di portata storica possibili."
            )
        return f"Vibrazione combinata {combined}: {NUMBER_MEANINGS.get(combined, 'energia neutra')}"
