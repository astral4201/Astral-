"""Gematria and Kabbalistic Tree of Life correlations.

The Tree of Life has 10 Sephirot representing fundamental forces.
Price levels and dates can be mapped to Sephirot via numerological reduction.
"""

from __future__ import annotations

from astral.core.models import GematriaResult


# The 10 Sephirot of the Tree of Life
SEPHIROT = {
    1: ("Keter", "Corona", "Volontà divina, sorgente suprema, punti di svolta assoluti"),
    2: ("Chokmah", "Saggezza", "Espansione, forza maschile, impulso creativo rialzista"),
    3: ("Binah", "Comprensione", "Contrazione, forza femminile, strutturazione ribassista"),
    4: ("Chesed", "Misericordia", "Abbondanza, crescita, espansione benevola"),
    5: ("Geburah", "Giustizia", "Severità, correzione, forza distruttiva necessaria"),
    6: ("Tiphareth", "Bellezza", "Equilibrio, armonia, centro del sistema — bull market sano"),
    7: ("Netzach", "Vittoria", "Desiderio, arte, emozioni — euforia dei mercati"),
    8: ("Hod", "Gloria", "Intelletto, comunicazione — analisi e dati"),
    9: ("Yesod", "Fondamento", "Immaginazione, subconscio collettivo — sentiment"),
    10: ("Malkuth", "Regno", "Manifestazione materiale, realtà fisica — prezzi reali"),
}


class Gematria:
    """Kabbalistic analysis of prices and dates."""

    def reduce_to_sephira(self, value: int) -> int:
        """Reduce a number to a Sephira index (1-10)."""
        if value < 1:
            return 1
        # Modulo 10, but use 10 instead of 0
        result = value % 10
        return result if result != 0 else 10

    def analyze_price(self, price: float) -> GematriaResult:
        """Map a price to its corresponding Sephira."""
        int_price = int(abs(price))
        # Digit sum first
        digit_sum = sum(int(d) for d in str(int_price))
        # Map to sephira
        sephira_idx = self.reduce_to_sephira(digit_sum)
        name, title, meaning = SEPHIROT[sephira_idx]

        return GematriaResult(
            value=int_price,
            root_number=digit_sum,
            sephira=f"{name} ({title})",
            meaning=meaning,
        )
