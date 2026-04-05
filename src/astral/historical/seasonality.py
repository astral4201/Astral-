"""Market seasonality patterns.

Well-documented calendar effects:
- January Effect: small-caps outperform in January
- Sell in May (May-October underperformance)
- Santa Claus Rally (last 5 Dec + first 2 Jan trading days)
- Halloween Indicator (Nov-Apr outperformance)
- September Effect (historically worst month)
- Triple/Quadruple Witching (3rd Friday of Mar/Jun/Sep/Dec)
"""

from __future__ import annotations

from datetime import date

from astral.core.models import Direction, Signal, SignalSource


class Seasonality:
    """Detects active seasonal patterns."""

    def active_patterns(self, d: date) -> list[Signal]:
        """Get all active seasonal signals for a given date."""
        signals = []
        month = d.month
        day = d.day

        # January Effect (January)
        if month == 1:
            signals.append(Signal(
                source=SignalSource.HISTORICAL_SEASONALITY,
                direction=Direction.BULLISH,
                strength=0.5,
                description=(
                    "January Effect: storicamente le small-cap sovraperformano a gennaio. "
                    "Flussi di fine/inizio anno e tax-loss harvesting recovery."
                ),
                date=d,
                metadata={"pattern": "january_effect"},
            ))

        # Santa Claus Rally (Dec 26 - Jan 3 approximately)
        if (month == 12 and day >= 24) or (month == 1 and day <= 3):
            signals.append(Signal(
                source=SignalSource.HISTORICAL_SEASONALITY,
                direction=Direction.BULLISH,
                strength=0.6,
                description=(
                    "Santa Claus Rally: le ultime 5 sedute di dicembre e le prime 2 di gennaio "
                    "sono storicamente rialziste. 'Se Babbo Natale non arriva, gli orsi domineranno.'"
                ),
                date=d,
                metadata={"pattern": "santa_claus_rally"},
            ))

        # Sell in May (May-October)
        if 5 <= month <= 10:
            signals.append(Signal(
                source=SignalSource.HISTORICAL_SEASONALITY,
                direction=Direction.BEARISH,
                strength=0.4,
                description=(
                    "'Sell in May and go away': il periodo maggio-ottobre è storicamente "
                    "più debole di novembre-aprile. Rendimenti medi inferiori."
                ),
                date=d,
                metadata={"pattern": "sell_in_may"},
            ))

        # Halloween Indicator (November-April = strong period)
        if month >= 11 or month <= 4:
            signals.append(Signal(
                source=SignalSource.HISTORICAL_SEASONALITY,
                direction=Direction.BULLISH,
                strength=0.5,
                description=(
                    "Indicatore di Halloween: il semestre novembre-aprile è il più forte "
                    "dell'anno. La maggior parte dei rendimenti annuali avviene qui."
                ),
                date=d,
                metadata={"pattern": "halloween_indicator"},
            ))

        # September Effect (worst month historically)
        if month == 9:
            signals.append(Signal(
                source=SignalSource.HISTORICAL_SEASONALITY,
                direction=Direction.BEARISH,
                strength=0.5,
                description=(
                    "Effetto Settembre: storicamente il PEGGIOR mese dell'anno per i mercati. "
                    "1929, 2001, 2008 — settembre porta le tempeste."
                ),
                date=d,
                metadata={"pattern": "september_effect"},
            ))

        # Options Expiration / Triple Witching (3rd Friday of Mar, Jun, Sep, Dec)
        if month in (3, 6, 9, 12):
            # Calculate 3rd Friday
            first_day = date(d.year, month, 1)
            first_friday = first_day.weekday()
            if first_friday <= 4:  # Mon-Fri
                third_friday = 1 + (4 - first_friday) + 14
            else:
                third_friday = 1 + (11 - first_friday) + 14

            if abs(day - third_friday) <= 1:
                signals.append(Signal(
                    source=SignalSource.HISTORICAL_SEASONALITY,
                    direction=Direction.LATERAL,
                    strength=0.5,
                    description=(
                        "Triple Witching: scadenza simultanea di opzioni su indici, "
                        "opzioni su azioni e futures. Volume e volatilità elevati."
                    ),
                    date=d,
                    metadata={"pattern": "triple_witching"},
                ))

        return signals
