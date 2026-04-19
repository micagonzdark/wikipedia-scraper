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
    Guarda una lista de titulares en un archivo CSV con encoding UTF-8.

    Args:
        titulares:  lista de dicts con claves 'titular', 'seccion', 'fecha'.
        filename:   nombre del archivo CSV de salida.
        output_dir: directorio donde guardar el archivo (se crea si no existe).

    Returns:
        Path absoluto al archivo CSV generado.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    ruta = output_dir / filename

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=_FIELDNAMES)
        writer.writeheader()
        writer.writerows(titulares)

    return ruta
