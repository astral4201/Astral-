"""Rich console renderer for the Oracle's output.

Produces a beautifully formatted report in the terminal with panels,
tables, colors and star ratings — the complete Gann Oracle experience.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.align import Align

from astral.core.models import ConfluenceResult, Direction


class OracleRenderer:
    """Renders ConfluenceResult to the console in Italian Gann Oracle style."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()

    def render(self, result: ConfluenceResult) -> None:
        """Render the complete analysis to the console."""
        self._render_header(result)
        self._render_oracle_vision(result)
        self._render_confluence_score(result)
        self._render_gann_levels(result)
        self._render_planetary(result)
        self._render_historical(result)
        self._render_macro(result)
        self._render_esoteric(result)
        self._render_critical_dates(result)
        self._render_tarot(result)
        self._render_operative_plan(result)
        self._render_footer()

    def _render_header(self, result: ConfluenceResult) -> None:
        title = Text.assemble(
            ("✦ ASTRAL ORACLE ✦", "bold gold1"),
            "\n",
            (f"{result.ticker}", "bold white"),
            (f"  @  ", "dim"),
            (f"{result.current_price:.2f}", "bold cyan"),
            "\n",
            (f"Data analisi: {result.analysis_date.isoformat()}", "dim"),
        )
        self.console.print(Panel(
            Align.center(title),
            border_style="gold1",
            padding=(1, 2),
        ))

    def _render_oracle_vision(self, result: ConfluenceResult) -> None:
        self.console.print()
        self.console.print(Panel(
            Text(result.oracle_vision, style="italic"),
            title="🔮 [bold gold1]VISIONE DELL'ORACOLO[/bold gold1]",
            border_style="magenta",
            padding=(1, 2),
        ))

    def _render_confluence_score(self, result: ConfluenceResult) -> None:
        stars_filled = "★" * result.score
        stars_empty = "☆" * (5 - result.score)
        stars_text = Text(stars_filled, style="bold gold1") + Text(stars_empty, style="dim")

        direction_color = {
            Direction.BULLISH: "green",
            Direction.BEARISH: "red",
            Direction.LATERAL: "yellow",
        }[result.direction]

        direction_label = {
            Direction.BULLISH: "RIALZISTA ▲",
            Direction.BEARISH: "RIBASSISTA ▼",
            Direction.LATERAL: "LATERALE ◆",
        }[result.direction]

        content = Text.assemble(
            ("Confluenza: ", "dim"),
            stars_text,
            (f"  ({result.score}/5)", "dim"),
            "\n",
            ("Direzione: ", "dim"),
            (direction_label, f"bold {direction_color}"),
        )

        self.console.print()
        self.console.print(Panel(
            Align.center(content),
            title="⭐ [bold]CONFLUENZA[/bold]",
            border_style="gold1",
        ))

        # Signal breakdown
        if result.signals:
            top_signals = sorted(result.signals, key=lambda s: s.strength, reverse=True)[:8]
            table = Table(title="Segnali più forti", show_header=True, header_style="bold cyan")
            table.add_column("Forza", style="gold1", width=6)
            table.add_column("Dir", width=5)
            table.add_column("Fonte", style="cyan", width=22)
            table.add_column("Descrizione", style="white")

            for sig in top_signals:
                strength_bar = "█" * int(sig.strength * 5) + "░" * (5 - int(sig.strength * 5))
                dir_icon = {"bullish": "▲", "bearish": "▼", "laterale": "◆"}[sig.direction.value]
                dir_color = {"bullish": "green", "bearish": "red", "laterale": "yellow"}[sig.direction.value]
                table.add_row(
                    strength_bar,
                    Text(dir_icon, style=dir_color),
                    sig.source.value.replace("_", " "),
                    sig.description[:80] + ("..." if len(sig.description) > 80 else ""),
                )
            self.console.print(table)

    def _render_gann_levels(self, result: ConfluenceResult) -> None:
        if not result.gann_levels:
            return

        current = result.current_price
        sorted_levels = sorted(result.gann_levels, key=lambda lv: lv.price)
        # Show top 3 above and below current price
        above = [lv for lv in sorted_levels if lv.price > current][:3]
        below = [lv for lv in reversed(sorted_levels) if lv.price < current][:3]

        table = Table(title="📐 LIVELLI DI GANN", show_header=True, header_style="bold gold1")
        table.add_column("Prezzo", style="bold")
        table.add_column("Δ %", justify="right")
        table.add_column("Tipo", style="cyan")
        table.add_column("Descrizione", style="dim")

        for lv in reversed(above):
            delta = ((lv.price - current) / current) * 100
            table.add_row(
                Text(f"{lv.price:.2f}", style="green"),
                f"+{delta:.2f}%",
                lv.level_type,
                lv.description[:60],
            )
        table.add_row(
            Text(f"{current:.2f}", style="bold yellow"),
            "[ORA]",
            "current_price",
            "Prezzo attuale",
        )
        for lv in below:
            delta = ((lv.price - current) / current) * 100
            table.add_row(
                Text(f"{lv.price:.2f}", style="red"),
                f"{delta:.2f}%",
                lv.level_type,
                lv.description[:60],
            )
        self.console.print()
        self.console.print(table)

    def _render_planetary(self, result: ConfluenceResult) -> None:
        if not result.planet_positions:
            return

        table = Table(title="🪐 POSIZIONI PLANETARIE", show_header=True, header_style="bold magenta")
        table.add_column("Pianeta", style="bold")
        table.add_column("Longitudine", justify="right")
        table.add_column("Segno", style="cyan")
        table.add_column("Stato")

        for pos in result.planet_positions:
            rx = "℞ RETRO" if pos.is_retrograde else "→ diretto"
            rx_style = "red bold" if pos.is_retrograde else "green"
            table.add_row(
                f"{pos.planet.symbol} {pos.planet.label_it}",
                f"{pos.longitude:.2f}°",
                f"{pos.sign} {pos.degree_in_sign:.1f}°",
                Text(rx, style=rx_style),
            )
        self.console.print()
        self.console.print(table)

        # Aspects
        if result.planetary_aspects:
            asp_table = Table(title="Aspetti attivi", show_header=True, header_style="bold magenta")
            asp_table.add_column("Pianeta 1", style="cyan")
            asp_table.add_column("Aspetto")
            asp_table.add_column("Pianeta 2", style="cyan")
            asp_table.add_column("Orbe", justify="right")
            for asp in result.planetary_aspects[:8]:
                asp_table.add_row(
                    f"{asp.planet1.symbol} {asp.planet1.label_it}",
                    asp.aspect.label,
                    f"{asp.planet2.symbol} {asp.planet2.label_it}",
                    f"{asp.orb}°",
                )
            self.console.print(asp_table)

        if result.moon_phase:
            self.console.print(
                f"[cyan]☽ Fase lunare:[/cyan] {result.moon_phase.phase.value} "
                f"(illuminazione {result.moon_phase.illumination:.0%})"
            )

    def _render_historical(self, result: ConfluenceResult) -> None:
        self.console.print()
        self.console.print("[bold gold1]📜 ANALISI STORICA[/bold gold1]")

        if result.kondratieff_season:
            season, pos = result.kondratieff_season
            self.console.print(
                f"  • Kondratieff: [cyan]{season.label_it}[/cyan] "
                f"({pos:.0%}) — {season.description}"
            )

        if result.presidential_cycle:
            year, label = result.presidential_cycle
            self.console.print(
                f"  • Ciclo Presidenziale: [cyan]Anno {year}/4[/cyan] ({label})"
            )

        if result.decennial_pattern:
            digit, label = result.decennial_pattern
            self.console.print(
                f"  • Ciclo Decennale: [cyan]finisce in {digit}[/cyan] ({label})"
            )

        if result.historical_matches:
            self.console.print("  • Anniversari di crisi:")
            for match in result.historical_matches[:3]:
                self.console.print(
                    f"    - [yellow]{match.years_ago} anni[/yellow] dal "
                    f"{match.event_type} di '{match.pattern.name}'"
                )

    def _render_macro(self, result: ConfluenceResult) -> None:
        if not result.macro:
            return
        m = result.macro
        self.console.print()
        self.console.print("[bold gold1]📊 MACROECONOMIA[/bold gold1]")
        if m.fed_funds is not None:
            self.console.print(f"  • Fed Funds Rate: [cyan]{m.fed_funds:.2f}%[/cyan]")
        if m.cpi_yoy is not None:
            self.console.print(f"  • CPI YoY: [cyan]{m.cpi_yoy:.2f}%[/cyan]")
        if m.yield_curve_10y2y is not None:
            style = "red" if m.yield_curve_inverted else "green"
            self.console.print(
                f"  • Yield Curve 10Y-2Y: [{style}]{m.yield_curve_10y2y:.2f}%[/{style}] "
                f"({'INVERTITA' if m.yield_curve_inverted else 'normale'})"
            )
        if m.vix is not None:
            self.console.print(f"  • VIX: [cyan]{m.vix:.2f}[/cyan]")
        if m.notes:
            for note in m.notes[:3]:
                self.console.print(f"  • {note}")

    def _render_esoteric(self, result: ConfluenceResult) -> None:
        self.console.print()
        self.console.print("[bold gold1]🔮 ESOTERISMO[/bold gold1]")

        if result.numerology:
            n = result.numerology
            self.console.print(
                f"  • Numerologia: data={n['date_vibration']}, prezzo={n['price_vibration']}, "
                f"combinato={n['combined']}"
            )
            self.console.print(f"    [italic]{n['interpretation']}[/italic]")

        if result.gematria:
            g = result.gematria
            self.console.print(f"  • Gematria / Sephira: [cyan]{g.sephira}[/cyan]")
            self.console.print(f"    [italic]{g.meaning}[/italic]")

        if result.fibonacci_levels:
            key_fibs = {k: v for k, v in result.fibonacci_levels.items() if k in ("38.2%", "50.0%", "61.8%")}
            fib_str = " | ".join(f"{k}={v:.2f}" for k, v in key_fibs.items())
            self.console.print(f"  • Fibonacci: {fib_str}")

    def _render_critical_dates(self, result: ConfluenceResult) -> None:
        if not result.critical_dates:
            return
        self.console.print()
        table = Table(title="📅 DATE CRITICHE FUTURE", show_header=True, header_style="bold gold1")
        table.add_column("Data", style="cyan")
        table.add_column("Ciclo")
        table.add_column("Descrizione", style="dim")
        for cd in result.critical_dates[:6]:
            table.add_row(
                cd.date.isoformat(),
                cd.cycle_name,
                cd.description[:70],
            )
        self.console.print(table)

    def _render_tarot(self, result: ConfluenceResult) -> None:
        if not result.tarot:
            return
        card = result.tarot
        content = Text.assemble(
            (f"{card.name_it}  ({card.name})", "bold gold1"),
            "\n\n",
            (f"{card.meaning}", "italic"),
            "\n\n",
            ("▸ ", "dim"),
            (card.market_interpretation, "cyan"),
        )
        self.console.print()
        self.console.print(Panel(
            content,
            title=f"🃏 [bold]CARTA DEL MOMENTO: Arcano {card.number}[/bold]",
            border_style="magenta",
            padding=(1, 2),
        ))

    def _render_operative_plan(self, result: ConfluenceResult) -> None:
        if not result.operative_plan:
            return
        p = result.operative_plan

        lines = []
        direction_color = {
            Direction.BULLISH: "green",
            Direction.BEARISH: "red",
            Direction.LATERAL: "yellow",
        }[p.direction]
        lines.append(f"[bold {direction_color}]Direzione: {p.direction.value.upper()}[/bold {direction_color}]")
        if p.entry_level:
            lines.append(f"[bold]Entrata:[/bold] {p.entry_level:.2f}")
        if p.stop_loss:
            lines.append(f"[red]Stop Loss:[/red] {p.stop_loss:.2f}")
        if p.target_1:
            lines.append(f"[green]Target 1:[/green] {p.target_1:.2f}")
        if p.target_2:
            lines.append(f"[green]Target 2:[/green] {p.target_2:.2f}")
        if p.timeframe:
            lines.append(f"[dim]Timeframe: {p.timeframe}[/dim]")
        if p.notes:
            lines.append("")
            lines.append(f"[italic]{p.notes}[/italic]")

        self.console.print()
        self.console.print(Panel(
            "\n".join(lines),
            title="⚔️ [bold]PIANO OPERATIVO[/bold]",
            border_style="gold1",
            padding=(1, 2),
        ))

    def _render_footer(self) -> None:
        self.console.print()
        self.console.print(
            "[dim italic]« Gann non era un trader meccanico — era un CACCIATORE di cicli. »[/dim italic]",
            justify="center",
        )
        self.console.print()
