"""Tarot card assignment for market phases.

Each Major Arcana represents a market archetype.
The Oracle assigns a card based on confluence + direction + volatility.
"""

from __future__ import annotations

from astral.core.models import Direction, TarotCard


# Major Arcana with market meanings
MAJOR_ARCANA = {
    0: TarotCard(
        number=0, name="The Fool", name_it="Il Matto",
        meaning="Nuovi inizi, innocenza, salto nel vuoto",
        market_interpretation="Nuovo ciclo / early bull market. Entusiasmo dei retail, FOMO iniziale.",
    ),
    1: TarotCard(
        number=1, name="The Magician", name_it="Il Mago",
        meaning="Manifestazione, potere, abilità",
        market_interpretation="Trend forte in formazione. Smart money in azione, manipolazione del prezzo.",
    ),
    2: TarotCard(
        number=2, name="The High Priestess", name_it="La Papessa",
        meaning="Intuizione, mistero, saggezza nascosta",
        market_interpretation="Forze nascoste al lavoro. Divergenze, pattern invisibili ai più.",
    ),
    3: TarotCard(
        number=3, name="The Empress", name_it="L'Imperatrice",
        meaning="Fertilità, abbondanza, crescita",
        market_interpretation="Bull market maturo con earnings in crescita. Settori value brillano.",
    ),
    4: TarotCard(
        number=4, name="The Emperor", name_it="L'Imperatore",
        meaning="Autorità, struttura, controllo",
        market_interpretation="Fed in controllo, politica monetaria dominante. Mercati regolati.",
    ),
    10: TarotCard(
        number=10, name="Wheel of Fortune", name_it="La Ruota della Fortuna",
        meaning="Cicli, destino, cambiamento",
        market_interpretation="PUNTO DI SVOLTA CICLICO. Inversione di trend imminente.",
    ),
    13: TarotCard(
        number=13, name="Death", name_it="La Morte",
        meaning="Trasformazione, fine, rinnovamento",
        market_interpretation="Fine di un'era di mercato. Vecchi leader muoiono, nuovi nascono.",
    ),
    15: TarotCard(
        number=15, name="The Devil", name_it="Il Diavolo",
        meaning="Illusione, attaccamento materiale, tentazione",
        market_interpretation="Bolla speculativa. Avidità estrema, illusione di ricchezza facile.",
    ),
    16: TarotCard(
        number=16, name="The Tower", name_it="La Torre",
        meaning="Distruzione improvvisa, rivelazione, caos",
        market_interpretation="⚡ CRASH IMPROVVISO. Black swan, capitulation, strutture crollano.",
    ),
    17: TarotCard(
        number=17, name="The Star", name_it="La Stella",
        meaning="Speranza, ispirazione, rinnovamento",
        market_interpretation="Post-crash recovery. Speranza torna, primi segnali di bottom.",
    ),
    18: TarotCard(
        number=18, name="The Moon", name_it="La Luna",
        meaning="Illusione, incertezza, subconscio",
        market_interpretation="Mercato laterale confuso. Whipsaw, false rotture, incertezza dominante.",
    ),
    19: TarotCard(
        number=19, name="The Sun", name_it="Il Sole",
        meaning="Gioia, successo, vitalità",
        market_interpretation="Bull market maturo e glorioso. Tutti guadagnano, top che si avvicina.",
    ),
    20: TarotCard(
        number=20, name="Judgement", name_it="Il Giudizio",
        meaning="Resurrezione, risveglio, reckoning",
        market_interpretation="Grande reset. Giudizio storico dei mercati. Cambio di paradigma.",
    ),
    21: TarotCard(
        number=21, name="The World", name_it="Il Mondo",
        meaning="Completamento, realizzazione, chiusura del ciclo",
        market_interpretation="Fine di un super-ciclo. Culminazione maxima prima del reset.",
    ),
}


class TarotAssigner:
    """Assigns the appropriate Tarot card based on market state."""

    def assign(
        self,
        confluence_score: int,
        direction: Direction,
        has_crash_signal: bool = False,
        has_reversal_signal: bool = False,
        is_bubble: bool = False,
        is_new_cycle: bool = False,
    ) -> TarotCard:
        """Assign the most fitting Tarot card."""

        # Priority 1: Crash signal
        if has_crash_signal and direction == Direction.BEARISH:
            return MAJOR_ARCANA[16]  # The Tower

        # Priority 2: Bubble (high confluence + bullish + warning signs)
        if is_bubble:
            return MAJOR_ARCANA[15]  # The Devil

        # Priority 3: Major reversal (high confluence + lateral)
        if has_reversal_signal and confluence_score >= 4:
            return MAJOR_ARCANA[10]  # Wheel of Fortune

        # Priority 4: New cycle / early bull
        if is_new_cycle and direction == Direction.BULLISH:
            return MAJOR_ARCANA[0]  # The Fool

        # Priority 5: Direction-based
        if direction == Direction.BULLISH:
            if confluence_score >= 4:
                return MAJOR_ARCANA[19]  # The Sun (mature bull)
            elif confluence_score >= 2:
                return MAJOR_ARCANA[3]  # The Empress (fertile bull)
            else:
                return MAJOR_ARCANA[1]  # The Magician (forming trend)

        if direction == Direction.BEARISH:
            if confluence_score >= 4:
                return MAJOR_ARCANA[13]  # Death (transformation)
            elif confluence_score >= 2:
                return MAJOR_ARCANA[17]  # The Star (post-crash hope)
            else:
                return MAJOR_ARCANA[4]  # The Emperor (controlled decline)

        # Lateral / uncertain
        return MAJOR_ARCANA[18]  # The Moon (confusion)
