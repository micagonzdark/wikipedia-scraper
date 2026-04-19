"""
main.py — Punto de entrada CLI de wikipedia-scraper.

Uso (Windows):
    python -X utf8 main.py [OPTIONS]

Ejemplos:
    python -X utf8 main.py
    python -X utf8 main.py --top 10
    python -X utf8 main.py --url https://en.wikipedia.org/wiki/Main_Page --top 3
    python -X utf8 main.py --top 5 --output noticias_hoy.csv
"""

import sys

# Forzar UTF-8 antes de cualquier import que toque stdout (Rich, Typer, etc.)
# Necesario en Windows donde la consola usa cp1252 por defecto.
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

from scraper import scrape_headlines, save_to_csv, analyze_words, WIKIPEDIA_URL

# ---------------------------------------------------------------------------
# App Typer
# ---------------------------------------------------------------------------
app = typer.Typer(
    name="wikipedia-scraper",
    help=(
        "Extrae titulares de la portada de Wikipedia, los guarda en un CSV "
        "y analiza las palabras más frecuentes del día."
    ),
    add_completion=False,
)

# legacy_windows=False: usa el renderer moderno de Windows (Unicode nativo)
# en lugar del wrapper LegacyWindowsConsole que falla con cp1252.
console = Console(legacy_windows=False)


# ---------------------------------------------------------------------------
# Comando principal
# ---------------------------------------------------------------------------
@app.command()
def run(
    url: Annotated[
        str,
        typer.Option(
            "--url",
            help="URL de la portada a scrapear.",
            show_default=True,
        ),
    ] = WIKIPEDIA_URL,
    top: Annotated[
        int,
        typer.Option(
            "--top",
            help="Cantidad de palabras más frecuentes a mostrar.",
            min=1,
            max=50,
            show_default=True,
        ),
    ] = 5,
    output: Annotated[
        str,
        typer.Option(
            "--output",
            help="Nombre del archivo CSV donde se guardan los titulares.",
            show_default=True,
        ),
    ] = "titulares.csv",
) -> None:
    """
    Pipeline completo: scraping -> CSV -> analisis de frecuencia de palabras.
    """

    # --- Paso 1: Scraping ----------------------------------------------------
    console.rule("[bold cyan]Paso 1 — Scraping")
    console.print(f"  URL: [link={url}]{url}[/link]")

    try:
        with console.status("Descargando portada...", spinner="dots"):
            titulares = scrape_headlines(url)
    except Exception as e:
        console.print(f"[bold red]Error al conectar:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(f"  [green]OK[/green] {len(titulares)} titulares extraídos\n")

    # Breakdown por sección
    secciones: dict[str, int] = {}
    for t in titulares:
        secciones[t["seccion"]] = secciones.get(t["seccion"], 0) + 1
    for seccion, n in secciones.items():
        console.print(f"    [dim]·[/dim] {seccion}: [bold]{n}[/bold]")

    # --- Paso 2: Guardar CSV -------------------------------------------------
    console.rule("[bold cyan]Paso 2 — Guardando CSV")
    ruta_csv = save_to_csv(titulares, filename=output)
    console.print(f"  [green]OK[/green] {ruta_csv}")
    console.print(f"       {ruta_csv.stat().st_size:,} bytes · {len(titulares)} filas\n")

    # --- Paso 3: Análisis de palabras ----------------------------------------
    top_filename = f"top_{top}_palabras.csv"
    console.rule(f"[bold cyan]Paso 3 — Top {top} palabras")

    top_palabras = analyze_words(titulares, top_n=top, output_filename=top_filename)
    ruta_top = Path(ruta_csv).parent / top_filename
    console.print(f"  [green]OK[/green] {ruta_top}\n")

    # Tabla de resultados con rich
    tabla = Table(
        title=f"Top {top} palabras más frecuentes",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta",
    )
    tabla.add_column("Rank", justify="center", style="dim", width=6)
    tabla.add_column("Palabra", style="bold")
    tabla.add_column("Frecuencia", justify="right")
    tabla.add_column("Barra", no_wrap=True)

    max_freq = top_palabras[0][1] if top_palabras else 1
    for i, (palabra, freq) in enumerate(top_palabras, start=1):
        barra_len = int((freq / max_freq) * 30)
        barra = "[green]" + "█" * barra_len + "[/green]"
        tabla.add_row(str(i), palabra, str(freq), barra)

    console.print(tabla)
    console.rule("[bold green]Pipeline completado")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app()
