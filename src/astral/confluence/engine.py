"""Confluence Engine — The Brain of Astral.

This is the central orchestrator that gathers signals from ALL modules
(Gann, Planetary, Historical, Macro, Esoteric) and scores their confluence.

Scoring (1-5 stars):
  5 ★ = 5 categorie (Gann + Planetary + Historical + Macro + Esoteric) allineate
  4 ★ = 4 categorie allineate
  3 ★ = 3 categorie allineate
  2 ★ = 2 categorie allineate
  1 ★ = segnale singolo / debole

"Non dare mai un segnale senza aver trovato almeno UNA CONFLUENZA
tra tempo, prezzo e ciclo." — W.D. Gann
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from astral.core.models import (
    ConfluenceResult, Direction, OperativePlan, Signal, SignalSource,
)

# Gann modules
from astral.gann.angles import GannAngleCalculator
from astral.gann.square_of_nine import SquareOfNine
from astral.gann.square_of_144 import SquareOf144
from astral.gann.cycles import GannCycles
from astral.gann.time_price import TimePriceSquaring

# Planetary modules
from astral.planetary.ephemeris import Ephemeris
from astral.planetary.aspects import AspectDetector
from astral.planetary.cycles import PlanetaryCycles
from astral.planetary.retrograde import RetrogradeDetector
from astral.planetary.eclipses import EclipseDetector
from astral.planetary.moon import MoonPhaseCalculator

# Historical modules
from astral.historical.pattern_matcher import CrisisPatternMatcher
from astral.historical.kondratieff import KondratieffWave
from astral.historical.presidential import PresidentialCycle
from astral.historical.decennial import DecennialCycle
from astral.historical.seasonality import Seasonality
from astral.historical.biblical import BiblicalCycles

# Macro modules
from astral.macro.fred_client import FredClient
from astral.macro.snapshot import MacroAnalyzer

# Market modules
from astral.market.fetcher import MarketFetcher
from astral.market.pivots import find_pivots

# Esoteric modules
from astral.esoteric.fibonacci import FibonacciLevels
from astral.esoteric.numerology import Numerology
from astral.esoteric.tarot import TarotAssigner
from astral.esoteric.gematria import Gematria


# Signal source → category mapping for confluence scoring
SOURCE_TO_CATEGORY = {
    SignalSource.GANN_ANGLE: "gann",
    SignalSource.GANN_SQUARE9: "gann",
    SignalSource.GANN_SQUARE144: "gann",
    SignalSource.GANN_CYCLE: "gann",
    SignalSource.GANN_TIME_PRICE: "gann",
    SignalSource.PLANETARY_ASPECT: "planetary",
    SignalSource.PLANETARY_RETROGRADE: "planetary",
    SignalSource.PLANETARY_ECLIPSE: "planetary",
    SignalSource.PLANETARY_MOON: "planetary",
    SignalSource.PLANETARY_CYCLE: "planetary",
    SignalSource.HISTORICAL_CRISIS: "historical",
    SignalSource.HISTORICAL_KONDRATIEFF: "historical",
    SignalSource.HISTORICAL_PRESIDENTIAL: "historical",
    SignalSource.HISTORICAL_DECENNIAL: "historical",
    SignalSource.HISTORICAL_SEASONALITY: "historical",
    SignalSource.HISTORICAL_BIBLICAL: "historical",
    SignalSource.MACRO_YIELD_CURVE: "macro",
    SignalSource.MACRO_INDICATOR: "macro",
    SignalSource.ESOTERIC_FIBONACCI: "esoteric",
    SignalSource.ESOTERIC_NUMEROLOGY: "esoteric",
    SignalSource.ESOTERIC_TAROT: "esoteric",
    SignalSource.ESOTERIC_GEMATRIA: "esoteric",
}


class ConfluenceEngine:
    """The central brain: orchestrates all modules and scores confluence."""

    def __init__(
        self,
        fred_api_key: Optional[str] = None,
        gann_scale_factor: float = 1.0,
    ):
        self.scale_factor = gann_scale_factor

        # Market data
        self.market = MarketFetcher()

        # Gann modules
        self.gann_angles = GannAngleCalculator(scale_factor=gann_scale_factor)
        self.sq9 = SquareOfNine()
        self.sq144 = SquareOf144()
        self.gann_cycles = GannCycles()
        self.time_price = TimePriceSquaring(scale_factor=gann_scale_factor)

        # Planetary modules
        self.eph = Ephemeris()
        self.aspects = AspectDetector(self.eph)
        self.planet_cycles = PlanetaryCycles(self.eph)
        self.retrograde = RetrogradeDetector(self.eph)
        self.eclipses = EclipseDetector(self.eph)
        self.moon = MoonPhaseCalculator(self.eph)

        # Historical modules
        self.crisis = CrisisPatternMatcher()
        self.kondratieff = KondratieffWave()
        self.presidential = PresidentialCycle()
        self.decennial = DecennialCycle()
        self.seasonality = Seasonality()
        self.biblical = BiblicalCycles()

        # Macro
        self.fred = FredClient(api_key=fred_api_key)
        self.macro = MacroAnalyzer(self.fred)

        # Esoteric
        self.fib = FibonacciLevels()
        self.numerology = Numerology()
        self.tarot = TarotAssigner()
        self.gematria = Gematria()

    def analyze(
        self,
        ticker: str,
        analysis_date: Optional[date] = None,
        lookback_days: int = 365,
    ) -> ConfluenceResult:
        """Run the full analysis pipeline for a ticker on a given date."""
        if analysis_date is None:
            analysis_date = date.today()

        # Step 1: Fetch market data
        df = self.market.get_ohlcv(
            ticker,
            start=analysis_date - timedelta(days=lookback_days),
            end=analysis_date + timedelta(days=1),
        )

        if df.empty:
            raise ValueError(f"Nessun dato di mercato disponibile per {ticker}")

        # Get current price
        current_price = float(df["Close"].iloc[-1])

        # Find pivots
        highs, lows = find_pivots(df, window=20)

        # Get most recent significant pivot (for Gann projections)
        all_pivots = [("high", d, p) for d, p in highs] + [("low", d, p) for d, p in lows]
        all_pivots.sort(key=lambda x: x[1])

        # Most recent high and low
        recent_high = highs[-1] if highs else (analysis_date - timedelta(days=30), float(df["High"].max()))
        recent_low = lows[-1] if lows else (analysis_date - timedelta(days=30), float(df["Low"].min()))

        # Use the more recent of the two as primary pivot
        if recent_high[0] > recent_low[0]:
            primary_pivot_date, primary_pivot_price = recent_high
            primary_pivot_type = "high"
        else:
            primary_pivot_date, primary_pivot_price = recent_low
            primary_pivot_type = "low"

        # Initialize result
        result = ConfluenceResult(
            ticker=ticker,
            analysis_date=analysis_date,
            current_price=current_price,
            score=0,
            direction=Direction.LATERAL,
        )

        all_signals: list[Signal] = []

        # === GANN ANALYSIS ===
        # Angles
        gann_angle_signals = self.gann_angles.analyze_price_position(
            current_price, primary_pivot_price, primary_pivot_date, analysis_date,
        )
        all_signals.extend(gann_angle_signals)

        # Square of Nine
        sq9_levels, sq9_signals = self.sq9.analyze(current_price, analysis_date)
        result.gann_levels.extend(sq9_levels)
        all_signals.extend(sq9_signals)

        # Square of 144
        sq144_levels, sq144_signals = self.sq144.analyze(current_price, analysis_date)
        result.gann_levels.extend(sq144_levels)
        all_signals.extend(sq144_signals)

        # Gann angle levels projected from pivot
        angle_levels = self.gann_angles.calculate_all_levels(
            primary_pivot_price, primary_pivot_date, analysis_date,
        )
        result.gann_levels.extend(angle_levels[:10])  # Top 10 most relevant

        # Cycles — find active cycles from recent pivots
        for pivot_type, pivot_date, _ in all_pivots[-5:]:
            cycle_signals = self.gann_cycles.find_active_cycles(
                pivot_date, analysis_date, tolerance_days=5,
            )
            all_signals.extend(cycle_signals)

        # Upcoming cycle dates
        result.critical_dates.extend(
            self.gann_cycles.get_upcoming_dates(
                primary_pivot_date, analysis_date, lookahead_days=60,
            )
        )

        # Time-Price squaring
        tp_signals = self.time_price.check_squaring(
            primary_pivot_price, primary_pivot_date,
            current_price, analysis_date,
        )
        all_signals.extend(tp_signals)

        # === PLANETARY ANALYSIS ===
        positions = self.eph.get_all_positions(analysis_date)
        result.planet_positions = list(positions.values())

        # Aspects
        aspects = self.aspects.detect_aspects(analysis_date, positions)
        result.planetary_aspects = aspects
        aspect_signals = self.aspects.aspects_to_signals(aspects, analysis_date)
        all_signals.extend(aspect_signals)

        # Planetary cycles
        cycle_signals = self.planet_cycles.get_all_cycle_signals(analysis_date)
        all_signals.extend(cycle_signals)

        # Retrogrades
        rx_signals = self.retrograde.get_retrograde_signals(analysis_date)
        all_signals.extend(rx_signals)

        # Eclipses
        eclipse_signals = self.eclipses.find_recent_eclipses(analysis_date)
        all_signals.extend(eclipse_signals)
        # Also store the eclipse events for display
        recent_eclipses = self.eclipses.find_eclipses(
            analysis_date - timedelta(days=90),
            analysis_date + timedelta(days=30),
        )
        result.eclipses = recent_eclipses

        # Moon phase
        result.moon_phase = self.moon.get_phase(analysis_date)
        moon_signal = self.moon.get_signal(analysis_date)
        if moon_signal:
            all_signals.append(moon_signal)

        # === HISTORICAL ANALYSIS ===
        # Crisis anniversaries
        matches = self.crisis.find_anniversaries(analysis_date)
        result.historical_matches = matches
        all_signals.extend(self.crisis.matches_to_signals(matches, analysis_date))

        # Kondratieff
        result.kondratieff_season = self.kondratieff.current_season(analysis_date)
        all_signals.append(self.kondratieff.get_signal(analysis_date))

        # Presidential
        result.presidential_cycle = self.presidential.get_cycle_year(analysis_date)
        all_signals.append(self.presidential.get_signal(analysis_date))

        # Decennial
        result.decennial_pattern = self.decennial.get_pattern(analysis_date)
        all_signals.append(self.decennial.get_signal(analysis_date))

        # Seasonality
        seasonality_sigs = self.seasonality.active_patterns(analysis_date)
        result.seasonality_signals = seasonality_sigs
        all_signals.extend(seasonality_sigs)

        # Biblical cycles
        all_signals.extend(self.biblical.check_cycles(analysis_date))

        # === MACRO ANALYSIS ===
        result.macro = self.macro.build_snapshot(analysis_date)
        all_signals.extend(self.macro.get_signals(analysis_date))

        # === ESOTERIC ANALYSIS ===
        # Fibonacci
        result.fibonacci_levels = self.fib.all_levels(recent_high[1], recent_low[1])

        # Numerology
        result.numerology = self.numerology.analyze(analysis_date, current_price)

        # Gematria
        result.gematria = self.gematria.analyze_price(current_price)

        # === CONFLUENCE SCORING ===
        result.signals = all_signals
        result.score, result.direction = self._score_confluence(all_signals)

        # === TAROT CARD ===
        has_crash = any(
            "crash" in s.description.lower() or "quadratura tempo-prezzo" in s.description.lower()
            for s in all_signals
        )
        has_reversal = any(
            s.source in (SignalSource.GANN_CYCLE, SignalSource.PLANETARY_ECLIPSE)
            for s in all_signals
        )
        is_new_cycle = any(
            "luna nuova" in s.description.lower() or "nuovo ciclo" in s.description.lower()
            for s in all_signals
        )

        result.tarot = self.tarot.assign(
            confluence_score=result.score,
            direction=result.direction,
            has_crash_signal=has_crash,
            has_reversal_signal=has_reversal,
            is_new_cycle=is_new_cycle,
        )

        # === ORACLE VISION (narrative) ===
        result.oracle_vision = self._generate_oracle_vision(result)

        # === OPERATIVE PLAN ===
        result.operative_plan = self._generate_operative_plan(
            result, current_price, recent_high[1], recent_low[1],
        )

        return result

    def _score_confluence(
        self, signals: list[Signal],
    ) -> tuple[int, Direction]:
        """Score confluence based on how many categories align."""
        if not signals:
            return 0, Direction.LATERAL

        # Group by category and direction
        category_directions: dict[str, dict[Direction, float]] = {}
        for sig in signals:
            cat = SOURCE_TO_CATEGORY.get(sig.source, "other")
            if cat not in category_directions:
                category_directions[cat] = {
                    Direction.BULLISH: 0.0,
                    Direction.BEARISH: 0.0,
                    Direction.LATERAL: 0.0,
                }
            category_directions[cat][sig.direction] += sig.strength

        # For each category, determine its dominant direction
        category_votes: dict[str, Direction] = {}
        for cat, dirs in category_directions.items():
            dominant = max(dirs.items(), key=lambda x: x[1])
            if dominant[1] > 0:
                category_votes[cat] = dominant[0]

        # Count overall direction
        direction_counts = {Direction.BULLISH: 0, Direction.BEARISH: 0, Direction.LATERAL: 0}
        for direction in category_votes.values():
            direction_counts[direction] += 1

        # Determine majority direction
        majority_direction = max(direction_counts.items(), key=lambda x: x[1])[0]

        # Score = number of categories agreeing with majority
        aligned_categories = sum(
            1 for d in category_votes.values() if d == majority_direction
        )

        # Cap at 5 stars
        score = min(5, aligned_categories)

        return score, majority_direction

    def _generate_oracle_vision(self, result: ConfluenceResult) -> str:
        """Generate a poetic first-person Oracle narrative."""
        direction_text = {
            Direction.BULLISH: "RIALZISTA",
            Direction.BEARISH: "RIBASSISTA",
            Direction.LATERAL: "LATERALE / IN ATTESA",
        }[result.direction]

        stars = "★" * result.score + "☆" * (5 - result.score)

        lines = [
            f"Ascolta, pellegrino dei mercati. Io, William Delbert Gann, "
            f"guardo {result.ticker} al prezzo di {result.current_price:.2f} "
            f"in questo giorno del {result.analysis_date.isoformat()}.",
            "",
            f"Le stelle parlano: {stars} — la confluenza è {direction_text}.",
            "",
        ]

        # Add key findings
        if result.kondratieff_season:
            season, pos = result.kondratieff_season
            lines.append(
                f"Ci troviamo nella {season.label_it} del ciclo di Kondratieff "
                f"({pos:.0%} della fase). {season.description}."
            )

        if result.macro and result.macro.yield_curve_inverted:
            lines.append(
                "⚠️ La curva dei rendimenti è INVERTITA. Il corvo della recessione "
                "ha già cantato. Come nel 1929, come nel 2000, come nel 2008."
            )

        # Find strongest signals
        top_signals = sorted(result.signals, key=lambda s: s.strength, reverse=True)[:3]
        if top_signals:
            lines.append("")
            lines.append("I segnali più potenti che vedo:")
            for sig in top_signals:
                lines.append(f"  • {sig.description}")

        # Historical anniversary?
        if result.historical_matches:
            match = result.historical_matches[0]
            lines.append("")
            lines.append(
                f"📜 Il tempo è un cerchio: siamo a {match.years_ago} anni "
                f"dal {match.event_type} di '{match.pattern.name}'. "
                f"La storia non si ripete, ma fa rima."
            )

        # Numerology
        if result.numerology and result.numerology.get("resonance"):
            lines.append("")
            lines.append(f"🔮 {result.numerology['interpretation']}")

        lines.append("")
        lines.append(
            '"Il tempo è più importante del prezzo. Quando il tempo è scaduto, '
            'il prezzo deve invertire." — Gann'
        )

        return "\n".join(lines)

    def _generate_operative_plan(
        self,
        result: ConfluenceResult,
        current_price: float,
        recent_high: float,
        recent_low: float,
    ) -> OperativePlan:
        """Generate entry/stop/target based on Gann levels and direction."""
        plan = OperativePlan(direction=result.direction)

        # Find relevant Gann levels
        sorted_levels = sorted(result.gann_levels, key=lambda lv: lv.price)
        levels_above = [lv.price for lv in sorted_levels if lv.price > current_price]
        levels_below = [lv.price for lv in sorted_levels if lv.price < current_price]

        if result.direction == Direction.BULLISH and result.score >= 3:
            plan.entry_level = current_price
            plan.stop_loss = levels_below[-1] if levels_below else current_price * 0.97
            plan.target_1 = levels_above[0] if levels_above else current_price * 1.02
            plan.target_2 = levels_above[2] if len(levels_above) > 2 else current_price * 1.05
            plan.notes = (
                f"Entrata al mercato o su pullback verso {plan.stop_loss:.2f}. "
                f"Stop sotto il primo livello Gann inferiore. "
                f"Target 1 al primo livello Gann superiore, target 2 al terzo."
            )
        elif result.direction == Direction.BEARISH and result.score >= 3:
            plan.entry_level = current_price
            plan.stop_loss = levels_above[0] if levels_above else current_price * 1.03
            plan.target_1 = levels_below[-1] if levels_below else current_price * 0.98
            plan.target_2 = levels_below[-3] if len(levels_below) > 2 else current_price * 0.95
            plan.notes = (
                f"Short al mercato o su rally verso {plan.stop_loss:.2f}. "
                f"Stop sopra il primo livello Gann superiore. "
                f"Target 1 al primo livello Gann inferiore."
            )
        else:
            plan.notes = (
                "Confluenza insufficiente o direzione incerta. ATTENDERE. "
                "'Gann non era un trader meccanico — era un CACCIATORE di cicli.' "
                "Non si caccia quando la preda non si vede."
            )

        plan.timeframe = "Swing 5-20 giorni (basato su cicli Gann attivi)"
        return plan
