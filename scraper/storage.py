"""
scraper/storage.py
Responsabilidad: persistir los titulares en archivos CSV.
"""

import csv
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "output"

_FIELDNAMES = ["titular", "seccion", "fecha"]


def save_to_csv(
    titulares: list[dict],
    filename: str = "titulares.csv",
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> Path:
    """
    Appends a list of headlines to a UTF-8 encoded CSV file.
    The header row is written only when the file does not yet exist,
    allowing daily runs to accumulate a growing historical dataset.

    Args:
        titulares:  list of dicts with keys 'titular', 'seccion', 'fecha'.
        filename:   name of the output CSV file.
        output_dir: directory to write the file into (created if absent).

    Returns:
        Absolute Path to the CSV file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    ruta = output_dir / filename

    # Append mode ('a'): preserves existing rows across daily runs.
    # Header is written only for new files to avoid duplicates.
    file_is_new = not ruta.exists() or ruta.stat().st_size == 0

    with open(ruta, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        if file_is_new:
            writer.writeheader()
        writer.writerows(titulares)

    return ruta
