"""
main.py — CLI entry point for wikipedia-scraper.

Usage (Windows):
    python -X utf8 main.py [OPTIONS]
    python -X utf8 main.py visualize [OPTIONS]

Examples:
    python -X utf8 main.py                                 # default pipeline
    python -X utf8 main.py --top 10 --plot                 # scrape + chart
    python -X utf8 main.py --top 3 --output noticias.csv   # custom output
    python -X utf8 main.py visualize --csv output/titulares.csv --top 7
"""

import sys

# Force UTF-8 before any import that touches stdout (Rich, Typer, etc.)
# Required on Windows where the console defaults to cp1252.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table
from rich import box

from scraper import (
    scrape_headlines,
    save_to_csv,
    analyze_words,
    generate_timeseries,
    WIKIPEDIA_URL,
)
from scraper.storage import DEFAULT_OUTPUT_DIR

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = typer.Typer(
    name="wikipedia-scraper",
    help=(
        "Scrape Wikipedia headlines, export to CSV, analyze word frequency, "
        "and visualize trends over time."
    ),
    add_completion=False,
    rich_markup_mode="rich",
)

# legacy_windows=False: use the modern Win32 Unicode renderer, not the
# LegacyWindowsConsole wrapper that fails with cp1252 on special characters.
console = Console(legacy_windows=False)


# ---------------------------------------------------------------------------
# Command 1: run  (scrape + save + analyze, optionally plot)
# ---------------------------------------------------------------------------
@app.command()
def run(
    url: Annotated[
        str,
        typer.Option("--url", help="URL of the Wikipedia front page to scrape.", show_default=True),
    ] = WIKIPEDIA_URL,
    top: Annotated[
        int,
        typer.Option("--top", help="Number of top words to display.", min=1, max=50, show_default=True),
    ] = 5,
    output: Annotated[
        str,
        typer.Option("--output", help="CSV filename for storing headlines (appends to existing).", show_default=True),
    ] = "titulares.csv",
    plot: Annotated[
        bool,
        typer.Option("--plot/--no-plot", help="Generate a time-series chart from the full CSV history."),
    ] = False,
) -> None:
    """
    [bold cyan]Full pipeline:[/bold cyan] scraping → CSV (append) → word-frequency analysis.

    Use [bold]--plot[/bold] to also generate a time-series chart from the accumulated history.
    """
    # --- Step 1: Scraping ----------------------------------------------------
    console.rule("[bold cyan]Step 1 — Scraping")
    console.print(f"  URL: [link={url}]{url}[/link]")

    try:
        with console.status("Downloading front page...", spinner="dots"):
            titulares = scrape_headlines(url)
    except Exception as e:
        console.print(f"[bold red]Connection error:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(f"  [green]OK[/green] {len(titulares)} headlines extracted\n")

    section_counts: dict[str, int] = {}
    for t in titulares:
        section_counts[t["seccion"]] = section_counts.get(t["seccion"], 0) + 1
    for seccion, n in section_counts.items():
        console.print(f"    [dim]·[/dim] {seccion}: [bold]{n}[/bold]")

    # --- Step 2: Append to CSV -----------------------------------------------
    console.rule("[bold cyan]Step 2 — Saving CSV")
    ruta_csv = save_to_csv(titulares, filename=output)

    # Count total rows in accumulated file
    with open(ruta_csv, encoding="utf-8") as f:
        total_rows = sum(1 for _ in f) - 1  # subtract header

    console.print(f"  [green]OK[/green] {ruta_csv}")
    console.print(f"       {ruta_csv.stat().st_size:,} bytes  ·  "
                  f"[bold]{len(titulares)}[/bold] new rows  ·  "
                  f"[bold]{total_rows}[/bold] total\n")

    # --- Step 3: Word-frequency analysis -------------------------------------
    top_filename = f"top_{top}_palabras.csv"
    console.rule(f"[bold cyan]Step 3 — Top {top} Words")

    top_palabras = analyze_words(titulares, top_n=top, output_filename=top_filename)
    ruta_top = ruta_csv.parent / top_filename
    console.print(f"  [green]OK[/green] {ruta_top}\n")

    tabla = Table(
        title=f"Top {top} most frequent words  [dim](today's run)[/dim]",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    tabla.add_column("Rank",      justify="center", style="dim", width=6)
    tabla.add_column("Word",      style="bold")
    tabla.add_column("Frequency", justify="right")
    tabla.add_column("Bar",       no_wrap=True)

    max_freq = top_palabras[0][1] if top_palabras else 1
    for i, (palabra, freq) in enumerate(top_palabras, start=1):
        barra_len = int((freq / max_freq) * 30)
        tabla.add_row(str(i), palabra, str(freq), "[green]" + "█" * barra_len + "[/green]")

    console.print(tabla)

    # --- Step 4 (optional): Time-series plot ---------------------------------
    if plot:
        _run_visualizer(ruta_csv, top)

    console.rule("[bold green]Pipeline complete")


# ---------------------------------------------------------------------------
# Command 2: visualize  (standalone chart from existing CSV)
# ---------------------------------------------------------------------------
@app.command()
def visualize(
    csv: Annotated[
        Path,
        typer.Option(
            "--csv",
            help="Path to the accumulated headlines CSV.",
            show_default=True,
        ),
    ] = DEFAULT_OUTPUT_DIR / "titulares.csv",
    top: Annotated[
        int,
        typer.Option("--top", help="Number of top words to chart.", min=1, max=50, show_default=True),
    ] = 5,
) -> None:
    """
    [bold cyan]Standalone visualizer:[/bold cyan] generate a time-series chart from an existing CSV.

    Reads the accumulated [bold]titulares.csv[/bold] and saves [bold]timeseries_plot.png[/bold].
    """
    _run_visualizer(csv, top)
    console.rule("[bold green]Visualization complete")


# ---------------------------------------------------------------------------
# Shared visualization helper
# ---------------------------------------------------------------------------
def _run_visualizer(csv_path: Path, top_n: int) -> None:
    console.rule("[bold cyan]Step 4 — Time-Series Visualization")
    console.print(f"  Reading: {csv_path}")

    try:
        with console.status("Generating chart...", spinner="dots"):
            ruta_plot = generate_timeseries(csv_path, top_n=top_n)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"[bold red]Visualization error:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(f"  [green]OK[/green] Chart saved → {ruta_plot}\n")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app()
