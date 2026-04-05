"""FastAPI application exposing the Astral Gann Oracle as a web service."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from pydantic import BaseModel, Field

from astral import __version__
from astral.confluence.engine import ConfluenceEngine
from astral.core.config import load_config
from astral.output.export import result_to_dict


BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Astral — The Gann Oracle",
    description="Sacred geometry, planetary cycles and confluence engine as a web API.",
    version=__version__,
)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# Lazy singleton — the engine is heavy to instantiate (Swiss Ephemeris etc.)
_engine: Optional[ConfluenceEngine] = None


def get_engine(scale_factor: float = 1.0) -> ConfluenceEngine:
    """Return a shared ConfluenceEngine instance, rebuilding if scale changes."""
    global _engine
    if _engine is None or _engine.scale_factor != scale_factor:
        config = load_config()
        fred_key = config.get("macro", {}).get("fred_api_key", "") if config else ""
        _engine = ConfluenceEngine(
            fred_api_key=fred_key,
            gann_scale_factor=scale_factor,
        )
    return _engine


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------


class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=20, description="Simbolo (es. SPX, BTC, GOLD)")
    analysis_date: Optional[str] = Field(None, description="Data YYYY-MM-DD (default: oggi)")
    lookback: int = Field(365, ge=30, le=3650, description="Giorni di lookback storici")
    scale: float = Field(1.0, gt=0, description="Scale factor per angoli Gann")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def landing(request: Request) -> HTMLResponse:
    """Public landing page."""
    return templates.TemplateResponse(
        request, "landing.html", {"version": __version__}
    )


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request) -> HTMLResponse:
    """The interactive oracle dashboard."""
    return templates.TemplateResponse(
        request, "dashboard.html", {"version": __version__}
    )


@app.get("/methodology", response_class=HTMLResponse)
async def methodology(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "methodology.html", {"version": __version__}
    )


@app.get("/pricing", response_class=HTMLResponse)
async def pricing(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "pricing.html", {"version": __version__}
    )


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "version": __version__}


@app.get("/api/ohlcv")
async def ohlcv(
    ticker: str = Query(..., min_length=1),
    lookback: int = Query(365, ge=30, le=3650),
) -> dict:
    """Return OHLCV candle data for TradingView Lightweight Charts."""
    from datetime import timedelta
    from astral.market.fetcher import MarketFetcher

    fetcher = MarketFetcher()
    end = date.today()
    start = end - timedelta(days=lookback)
    try:
        df = fetcher.get_ohlcv(ticker.upper().strip(), start=start, end=end + timedelta(days=1))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore fetch: {e}")

    if df is None or df.empty:
        raise HTTPException(status_code=404, detail=f"Nessun dato per {ticker}")

    candles = []
    for idx, row in df.iterrows():
        ts = idx.date().isoformat() if hasattr(idx, "date") else str(idx)[:10]
        try:
            candles.append({
                "time": ts,
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
            })
        except (KeyError, ValueError, TypeError):
            continue

    return {"ticker": ticker.upper().strip(), "candles": candles}


@app.post("/api/analyze")
async def analyze(payload: AnalyzeRequest) -> JSONResponse:
    """Run the full confluence analysis and return the result as JSON."""
    # Parse date
    if payload.analysis_date:
        try:
            target_date = datetime.strptime(payload.analysis_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Data non valida: {payload.analysis_date}")
    else:
        target_date = date.today()

    engine = get_engine(scale_factor=payload.scale)

    try:
        result = engine.analyze(
            payload.ticker.upper().strip(),
            target_date,
            lookback_days=payload.lookback,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'analisi: {e}")

    return JSONResponse(content=result_to_dict(result))


@app.get("/api/sq9")
async def square_of_nine(price: float = Query(..., gt=0)) -> dict:
    """Return Square of Nine cardinal levels for a given price."""
    from astral.gann.square_of_nine import SquareOfNine

    sq = SquareOfNine()
    levels = sq.get_cardinal_levels(price)
    return {
        "price": price,
        "levels": [
            {
                "level_type": lv.level_type,
                "price": lv.price,
                "delta_pct": ((lv.price - price) / price) * 100,
                "description": lv.description,
            }
            for lv in sorted(levels, key=lambda x: x.price)
        ],
    }


@app.get("/api/planets")
async def planets(target_date: Optional[str] = Query(None, alias="date")) -> dict:
    """Return planetary positions and active aspects for a given date."""
    from astral.planetary.ephemeris import Ephemeris
    from astral.planetary.aspects import AspectDetector

    if target_date:
        try:
            d = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Data non valida: {target_date}")
    else:
        d = date.today()

    eph = Ephemeris()
    positions = eph.get_all_positions(d)

    detector = AspectDetector(eph)
    aspects = detector.detect_aspects(d, positions)

    return {
        "date": d.isoformat(),
        "positions": [
            {
                "planet": p.label_it,
                "symbol": p.symbol,
                "longitude": round(pos.longitude, 2),
                "sign": pos.sign,
                "degree_in_sign": round(pos.degree_in_sign, 2),
                "retrograde": pos.is_retrograde,
            }
            for p, pos in positions.items()
        ],
        "aspects": [
            {
                "planet1": a.planet1.label_it,
                "symbol1": a.planet1.symbol,
                "aspect": a.aspect.label,
                "planet2": a.planet2.label_it,
                "symbol2": a.planet2.symbol,
                "orb": round(a.orb, 2),
                "applying": a.applying,
            }
            for a in aspects
        ],
    }


def run(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Entry point to launch the server with uvicorn."""
    import uvicorn

    uvicorn.run(
        "astral.web.app:app",
        host=host,
        port=port,
        reload=reload,
    )
