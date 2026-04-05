"""Core data models for the Astral Gann Trading Analyzer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Direction(Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    LATERAL = "laterale"


class SignalSource(Enum):
    GANN_ANGLE = "gann_angle"
    GANN_SQUARE9 = "gann_sq9"
    GANN_SQUARE144 = "gann_sq144"
    GANN_CYCLE = "gann_cycle"
    GANN_TIME_PRICE = "gann_time_price"
    PLANETARY_ASPECT = "planetary_aspect"
    PLANETARY_RETROGRADE = "planetary_retrograde"
    PLANETARY_ECLIPSE = "planetary_eclipse"
    PLANETARY_MOON = "planetary_moon"
    PLANETARY_CYCLE = "planetary_cycle"
    HISTORICAL_CRISIS = "historical_crisis"
    HISTORICAL_KONDRATIEFF = "historical_kondratieff"
    HISTORICAL_PRESIDENTIAL = "historical_presidential"
    HISTORICAL_DECENNIAL = "historical_decennial"
    HISTORICAL_SEASONALITY = "historical_seasonality"
    HISTORICAL_BIBLICAL = "historical_biblical"
    MACRO_YIELD_CURVE = "macro_yield_curve"
    MACRO_INDICATOR = "macro_indicator"
    ESOTERIC_FIBONACCI = "esoteric_fibonacci"
    ESOTERIC_NUMEROLOGY = "esoteric_numerology"
    ESOTERIC_TAROT = "esoteric_tarot"
    ESOTERIC_GEMATRIA = "esoteric_gematria"


class AspectType(Enum):
    CONJUNCTION = ("Congiunzione", 0.0)
    SEXTILE = ("Sestile", 60.0)
    SQUARE = ("Quadratura", 90.0)
    TRINE = ("Trigono", 120.0)
    OPPOSITION = ("Opposizione", 180.0)

    def __init__(self, label: str, angle: float):
        self.label = label
        self.angle = angle


class Planet(Enum):
    SUN = (0, "Sole", "☉")
    MOON = (1, "Luna", "☽")
    MERCURY = (2, "Mercurio", "☿")
    VENUS = (3, "Venere", "♀")
    MARS = (4, "Marte", "♂")
    JUPITER = (5, "Giove", "♃")
    SATURN = (6, "Saturno", "♄")
    URANUS = (7, "Urano", "♅")
    NEPTUNE = (8, "Nettuno", "♆")
    PLUTO = (9, "Plutone", "♇")

    def __init__(self, swe_id: int, label_it: str, symbol: str):
        self.swe_id = swe_id
        self.label_it = label_it
        self.symbol = symbol


class GannAngleType(Enum):
    A8x1 = ("8x1", 8.0, 7.5)
    A4x1 = ("4x1", 4.0, 15.0)
    A3x1 = ("3x1", 3.0, 18.75)
    A2x1 = ("2x1", 2.0, 26.25)
    A1x1 = ("1x1", 1.0, 45.0)
    A1x2 = ("1x2", 0.5, 63.75)
    A1x3 = ("1x3", 1 / 3, 71.25)
    A1x4 = ("1x4", 0.25, 75.0)
    A1x8 = ("1x8", 0.125, 82.5)

    def __init__(self, label: str, ratio: float, degrees: float):
        self.label = label
        self.ratio = ratio
        self.degrees = degrees


class KondSeason(Enum):
    SPRING = ("Primavera", "Ripresa / espansione")
    SUMMER = ("Estate", "Inflazione / surriscaldamento")
    AUTUMN = ("Autunno", "Speculazione / plateau")
    WINTER = ("Inverno", "Deflazione / crisi")

    def __init__(self, label_it: str, description: str):
        self.label_it = label_it
        self.description = description


class MoonPhaseName(Enum):
    NEW_MOON = "Luna Nuova"
    WAXING_CRESCENT = "Crescente"
    FIRST_QUARTER = "Primo Quarto"
    WAXING_GIBBOUS = "Gibbosa Crescente"
    FULL_MOON = "Luna Piena"
    WANING_GIBBOUS = "Gibbosa Calante"
    LAST_QUARTER = "Ultimo Quarto"
    WANING_CRESCENT = "Calante"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Signal:
    source: SignalSource
    direction: Direction
    strength: float  # 0.0 to 1.0
    description: str
    date: date
    metadata: dict = field(default_factory=dict)


@dataclass
class GannLevel:
    price: float
    level_type: str  # "sq9_90", "sq9_180", "angle_1x1", "sq144", etc.
    direction: Direction
    description: str


@dataclass
class PlanetaryAspect:
    planet1: Planet
    planet2: Planet
    aspect: AspectType
    exact_date: date
    orb: float  # degrees from exact
    applying: bool  # True if approaching exact, False if separating


@dataclass
class PlanetPosition:
    planet: Planet
    longitude: float
    latitude: float
    distance: float
    speed: float  # negative = retrograde
    sign: str
    degree_in_sign: float

    @property
    def is_retrograde(self) -> bool:
        return self.speed < 0


@dataclass
class EclipseEvent:
    eclipse_type: str  # "solar" or "lunar"
    date: date
    longitude: float
    description: str
    impact_window_end: date


@dataclass
class MoonPhase:
    phase: MoonPhaseName
    illumination: float
    date: date


@dataclass
class CrisisPattern:
    name: str
    peak_date: date
    trough_date: date
    decline_pct: float
    description: str


@dataclass
class HistoricalMatch:
    pattern: CrisisPattern
    event_type: str  # "peak" or "trough"
    years_ago: int
    anniversary_date: date


@dataclass
class TarotCard:
    number: int
    name: str
    name_it: str
    meaning: str
    market_interpretation: str


@dataclass
class GematriaResult:
    value: int
    root_number: int
    sephira: str
    meaning: str


@dataclass
class CycleDate:
    date: date
    cycle_name: str
    days_from_pivot: int
    description: str


@dataclass
class MacroSnapshot:
    date: date
    fed_funds: Optional[float] = None
    cpi_yoy: Optional[float] = None
    m2_yoy: Optional[float] = None
    yield_curve_10y2y: Optional[float] = None
    yield_curve_inverted: Optional[bool] = None
    vix: Optional[float] = None
    dxy: Optional[float] = None
    bias: Optional[Direction] = None
    notes: list[str] = field(default_factory=list)


@dataclass
class OperativePlan:
    direction: Direction
    entry_level: Optional[float] = None
    stop_loss: Optional[float] = None
    target_1: Optional[float] = None
    target_2: Optional[float] = None
    timeframe: str = ""
    notes: str = ""


@dataclass
class ConfluenceResult:
    ticker: str
    analysis_date: date
    current_price: float
    # Confluence score (1-5 stars)
    score: int
    direction: Direction
    # Module outputs
    signals: list[Signal] = field(default_factory=list)
    gann_levels: list[GannLevel] = field(default_factory=list)
    planetary_aspects: list[PlanetaryAspect] = field(default_factory=list)
    planet_positions: list[PlanetPosition] = field(default_factory=list)
    eclipses: list[EclipseEvent] = field(default_factory=list)
    moon_phase: Optional[MoonPhase] = None
    historical_matches: list[HistoricalMatch] = field(default_factory=list)
    kondratieff_season: Optional[tuple[KondSeason, float]] = None
    presidential_cycle: Optional[tuple[int, str]] = None
    decennial_pattern: Optional[tuple[int, str]] = None
    seasonality_signals: list[Signal] = field(default_factory=list)
    macro: Optional[MacroSnapshot] = None
    tarot: Optional[TarotCard] = None
    numerology: Optional[dict] = None
    gematria: Optional[GematriaResult] = None
    fibonacci_levels: Optional[dict[str, float]] = None
    critical_dates: list[CycleDate] = field(default_factory=list)
    oracle_vision: str = ""
    operative_plan: Optional[OperativePlan] = None
