"""
scraper/analyzer.py
Responsabilidad: análisis de frecuencia de palabras sobre los titulares.
"""

import csv
import re
from collections import Counter
from pathlib import Path

from .storage import DEFAULT_OUTPUT_DIR

# ---------------------------------------------------------------------------
# Stopwords en español: artículos, preposiciones, conjunciones, pronombres
# y palabras frecuentes que no aportan significado semántico al análisis.
# ---------------------------------------------------------------------------
STOPWORDS: set[str] = {
    # artículos
    "el", "la", "los", "las", "un", "una", "unos", "unas",
    # preposiciones
    "a", "ante", "bajo", "con", "contra", "de", "desde", "en",
    "entre", "hacia", "hasta", "para", "por", "segun", "sin",
    "sobre", "tras", "durante", "mediante",
    # conjunciones y nexos
    "e", "ni", "o", "u", "y", "pero", "sino", "aunque", "porque",
    "que", "si", "como", "cuando", "donde", "cuya", "cuyo",
    # pronombres y determinantes
    "al", "del", "le", "lo", "les", "se", "su", "sus",
    "mi", "mis", "tu", "tus", "nos", "este", "esta", "estos",
    "estas", "ese", "esa", "esos", "esas", "aquel", "aquella",
    # verbos auxiliares y copulativos comunes
    "es", "son", "fue", "ser", "ha", "han", "he", "hay",
    # adverbios y partículas frecuentes
    "ya", "no", "mas", "muy", "tambien", "solo", "bien",
    # ruido temporal genérico
    "hace", "anos", "años",
    # meses del año — dominan Wikipedia porque cada noticia lleva fecha
    # ("19 de abril: ..."), pero no aportan significado temático
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
    # ruido de Wikipedia: referencias a imágenes en pies de foto
    "imagen", "superior", "inferior",
}

# Solo conservar letras del alfabeto español (incluyendo acentos y ñ)
_LIMPIEZA = re.compile(r"[^a-záéíóúüñ\s]")


def analyze_words(
    titulares: list[dict],
    top_n: int = 5,
    stopwords: set[str] = STOPWORDS,
    output_filename: str = "top_palabras.csv",
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> list[tuple[str, int]]:
    """
    Cuenta la frecuencia de palabras en el campo 'titular' de cada entrada,
    descartando stopwords y tokens de menos de 3 caracteres.

    Args:
        titulares:       lista de dicts con al menos la clave 'titular'.
        top_n:           cantidad de palabras más frecuentes a retornar.
        stopwords:       conjunto de palabras a ignorar (case-insensitive).
        output_filename: nombre del CSV con el ranking resultante.
        output_dir:      directorio donde guardar el CSV de resultados.

    Returns:
        Lista de tuplas (palabra, frecuencia) ordenada de mayor a menor,
        con exactamente top_n elementos (o menos si el vocabulario es pequeño).
    """
    contador: Counter = Counter()

    for item in titulares:
        texto = _LIMPIEZA.sub(" ", item["titular"].lower())
        for palabra in texto.split():
            if len(palabra) >= 3 and palabra not in stopwords:
                contador[palabra] += 1

    top = contador.most_common(top_n)

    # Persistir resultados
    output_dir.mkdir(parents=True, exist_ok=True)
    ruta = output_dir / output_filename
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ranking", "palabra", "frecuencia"])
        for i, (palabra, freq) in enumerate(top, start=1):
            writer.writerow([i, palabra, freq])

    return top
