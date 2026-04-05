"""Astral CLI entry point."""

from __future__ import annotations

import os
from datetime import date, datetime

import click
from rich.console import Console

from astral import __version__
from astral.confluence.engine import ConfluenceEngine
from astral.core.config import load_config
from astral.output.export import export_to_file, result_to_json
from astral.output.renderer import OracleRenderer


console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="Astral")
def cli() -> None:
    """✦ ASTRAL — The Gann Oracle Trading Analyzer ✦

    Sacred geometry, planetary cycles, historical patterns and macro data
    unified into a single confluence engine.
    """


@cli.command()
@click.argument("ticker")
@click.option("--date", "analysis_date", default=None,
              help="Data di analisi (YYYY-MM-DD). Default: oggi.")
@click.option("--lookback", default=365, type=int,
              help="Giorni di lookback per dati storici.")
@click.option("--scale", default=1.0, type=float,
              help="Scale factor per angoli Gann (default 1.0).")
@click.option("--export", "export_path", default=None,
              help="Esporta risultato in file JSON.")
@click.option("--json-only", is_flag=True,
              help="Stampa solo JSON, niente rendering.")
def analyze(
    ticker: str,
    analysis_date: str | None,
    lookback: int,
    scale: float,
    export_path: str | None,
    json_only: bool,
) -> None:
    """Analizza un ticker con il pieno motore Gann Oracle.

    Esempi:

      astral analyze SPX

      astral analyze BTC --date 2026-04-05 --scale 100

      astral analyze GOLD --export report.json
    """
    config = load_config()
    fred_key = config.get("macro", {}).get("fred_api_key", "")

    if analysis_date:
        try:
            target_date = datetime.strptime(analysis_date, "%Y-%m-%d").date()
        except ValueError:
            console.print(f"[red]Data non valida: {analysis_date}. Usa YYYY-MM-DD.[/red]")
            raise SystemExit(1)
    else:
        target_date = date.today()

    if not json_only:
        console.print(f"[dim]Consultando l'Oracolo per [cyan]{ticker}[/cyan] "
                      f"alla data [cyan]{target_date.isoformat()}[/cyan]...[/dim]")

    engine = ConfluenceEngine(fred_api_key=fred_key, gann_scale_factor=scale)

    try:
        result = engine.analyze(ticker, target_date, lookback_days=lookback)
    except Exception as e:
        console.print(f"[red]Errore durante l'analisi: {e}[/red]")
        raise SystemExit(1)

    if json_only:
        print(result_to_json(result))
    else:
        renderer = OracleRenderer(console)
        renderer.render(result)

    if export_path:
        export_to_file(result, export_path)
        console.print(f"[green]✓ Report esportato in: {export_path}[/green]")


@cli.command()
@click.argument("price", type=float)
def sq9(price: float) -> None:
    """Calcola i livelli Square of Nine per un prezzo."""
    from astral.gann.square_of_nine import SquareOfNine
    from rich.table import Table

    sq = SquareOfNine()
    levels = sq.get_cardinal_levels(price)

    table = Table(title=f"Square of Nine — prezzo {price}", header_style="bold gold1")
    table.add_column("Livello", style="cyan")
    table.add_column("Prezzo", justify="right")
    table.add_column("Δ da corrente", justify="right")

    for lv in sorted(levels, key=lambda x: x.price):
        delta = ((lv.price - price) / price) * 100
        style = "green" if lv.price > price else "red"
        table.add_row(
            lv.level_type,
            f"[{style}]{lv.price:.2f}[/{style}]",
            f"{delta:+.2f}%",
        )

    console.print(table)


@cli.command()
@click.option("--date", "target_date", default=None, help="Data (YYYY-MM-DD)")
def planets(target_date: str | None) -> None:
    """Mostra posizioni planetarie attuali e aspetti attivi."""
    from astral.planetary.ephemeris import Ephemeris
    from astral.planetary.aspects import AspectDetector
    from rich.table import Table

    if target_date:
        d = datetime.strptime(target_date, "%Y-%m-%d").date()
    else:
        d = date.today()

    eph = Ephemeris()
    positions = eph.get_all_positions(d)

    table = Table(title=f"Posizioni planetarie — {d.isoformat()}", header_style="bold magenta")
    table.add_column("Pianeta", style="bold")
    table.add_column("Longitudine", justify="right")
    table.add_column("Segno", style="cyan")
    table.add_column("Stato")

    for planet, pos in positions.items():
        rx = "[red]℞[/red]" if pos.is_retrograde else "→"
        table.add_row(
            f"{planet.symbol} {planet.label_it}",
            f"{pos.longitude:.2f}°",
            f"{pos.sign} {pos.degree_in_sign:.1f}°",
            rx,
        )
    console.print(table)

    # Aspects
    detector = AspectDetector(eph)
    aspects = detector.detect_aspects(d, positions)
    if aspects:
        asp_table = Table(title="Aspetti attivi", header_style="bold magenta")
        asp_table.add_column("P1", style="cyan")
        asp_table.add_column("Aspetto")
        asp_table.add_column("P2", style="cyan")
        asp_table.add_column("Orbe")
        for asp in aspects[:15]:
            asp_table.add_row(
                f"{asp.planet1.symbol} {asp.planet1.label_it}",
                asp.aspect.label,
                f"{asp.planet2.symbol} {asp.planet2.label_it}",
                f"{asp.orb}°",
            )
        console.print(asp_table)


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
