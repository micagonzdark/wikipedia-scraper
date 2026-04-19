"""
scraper.py
Pipeline completo:
  1. scrape_headlines()  — extrae titulares de la portada de Wikipedia
  2. save_to_csv()       — guarda los titulares en output/titulares.csv
  3. analyze_words()     — cuenta frecuencia de palabras y exporta el Top N
"""

import sys
import csv
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Forzar UTF-8 en stdout (evita errores cp1252 en consolas Windows)
sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------
WIKIPEDIA_URL = "https://es.wikipedia.org/wiki/Wikipedia:Portada"
OUTPUT_DIR    = Path(__file__).parent / "output"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Stopwords en espagnol: articulos, preposiciones, conjunciones y palabras
# muy frecuentes que no aportan significado semantico al analisis.
STOPWORDS = {
    # articulos
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
    # numeros y fechas (se filtran por regex, pero por si acaso)
    "hace", "anos",
}


# ---------------------------------------------------------------------------
# 1. scrape_headlines
# ---------------------------------------------------------------------------
def scrape_headlines(url: str = WIKIPEDIA_URL) -> list[dict]:
    """
    Descarga la portada de Wikipedia en espagnol y extrae titulares de:
      - Noticias de actualidad  (id='main-cur')
      - Articulo destacado      (id='main-tfa')
      - Efemerides              (id='main-itd')

    Returns:
        Lista de dicts con claves: 'titular', 'seccion', 'fecha'
    """
    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    titulares = []
    fecha = datetime.now().isoformat(timespec="seconds")

    secciones = [
        ("main-cur", "Noticias de actualidad", "li"),
        ("main-itd", "Efemerides",             "li"),
    ]

    for div_id, nombre_seccion, tag in secciones:
        div = soup.find("div", id=div_id)
        if div:
            for elem in div.find_all(tag):
                texto = elem.get_text(separator=" ", strip=True)
                if texto:
                    titulares.append({"titular": texto, "seccion": nombre_seccion, "fecha": fecha})

    # Articulo destacado: extraer el primer <b>
    tfa_div = soup.find("div", id="main-tfa")
    if tfa_div:
        primer_b = tfa_div.find("b")
        if primer_b:
            texto = primer_b.get_text(strip=True)
            if texto:
                titulares.append({"titular": texto, "seccion": "Articulo destacado", "fecha": fecha})

    return titulares


# ---------------------------------------------------------------------------
# 2. save_to_csv
# ---------------------------------------------------------------------------
def save_to_csv(titulares: list[dict], filename: str = "titulares.csv") -> Path:
    """
    Guarda la lista de titulares en un archivo CSV dentro de output/.

    Args:
        titulares: lista de dicts con claves 'titular', 'seccion', 'fecha'
        filename:  nombre del archivo de salida

    Returns:
        Path al archivo generado
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = OUTPUT_DIR / filename

    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titular", "seccion", "fecha"])
        writer.writeheader()
        writer.writerows(titulares)

    return ruta


# ---------------------------------------------------------------------------
# 3. analyze_words
# ---------------------------------------------------------------------------
def analyze_words(
    titulares: list[dict],
    top_n: int = 5,
    stopwords: set = STOPWORDS,
    output_filename: str = "top_palabras.csv",
) -> list[tuple[str, int]]:
    """
    Analiza la frecuencia de palabras en los titulares, filtrando stopwords,
    numeros y tokens de menos de 3 caracteres.

    Args:
        titulares:       lista de dicts con clave 'titular'
        top_n:           cuantas palabras retornar
        stopwords:       conjunto de palabras a ignorar
        output_filename: nombre del CSV de resultados

    Returns:
        Lista de tuplas (palabra, frecuencia) ordenada de mayor a menor
    """
    contador = Counter()

    for item in titulares:
        texto = item["titular"].lower()
        # Eliminar puntuacion y caracteres especiales, conservar letras y espacios
        texto = re.sub(r"[^a-záéíóúüñ\s]", " ", texto)
        palabras = texto.split()

        for palabra in palabras:
            # Ignorar tokens de menos de 3 caracteres y stopwords
            if len(palabra) >= 3 and palabra not in stopwords:
                contador[palabra] += 1

    top = contador.most_common(top_n)

    # Guardar resultados en CSV
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ruta = OUTPUT_DIR / output_filename
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ranking", "palabra", "frecuencia"])
        for i, (palabra, freq) in enumerate(top, start=1):
            writer.writerow([i, palabra, freq])

    return top


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sep = "-" * 60

    # --- PASO 1: Scraping ---
    print(sep)
    print("PASO 1: Extrayendo titulares de Wikipedia...")
    print(sep)
    titulares = scrape_headlines()
    print(f"  Titulares extraidos: {len(titulares)}")
    for seccion in ["Noticias de actualidad", "Articulo destacado", "Efemerides"]:
        n = sum(1 for t in titulares if t["seccion"] == seccion)
        print(f"    [{seccion}]: {n} items")

    # --- PASO 2: Guardar CSV ---
    print()
    print(sep)
    print("PASO 2: Guardando titulares en CSV...")
    print(sep)
    ruta_csv = save_to_csv(titulares)
    print(f"  Archivo generado: {ruta_csv}")
    print(f"  Tamano: {ruta_csv.stat().st_size:,} bytes")

    # Mostrar primeras 3 filas a modo de preview
    print("\n  Preview (primeras 3 filas):")
    print(f"  {'SECCION':<25} {'TITULAR'}")
    print(f"  {'-'*22} {'-'*45}")
    for item in titulares[:3]:
        titular_corto = item["titular"][:50] + "..." if len(item["titular"]) > 50 else item["titular"]
        print(f"  {item['seccion']:<25} {titular_corto}")

    # --- PASO 3: Analisis de palabras ---
    print()
    print(sep)
    print("PASO 3: Analizando frecuencia de palabras (Top 5)...")
    print(sep)
    top5 = analyze_words(titulares, top_n=5)
    ruta_top = OUTPUT_DIR / "top_palabras.csv"
    print(f"  Resultados guardados en: {ruta_top}")
    print()
    print(f"  {'RANK':<6} {'PALABRA':<20} {'FRECUENCIA'}")
    print(f"  {'----':<6} {'-------':<20} {'----------'}")
    for i, (palabra, freq) in enumerate(top5, start=1):
        barra = "#" * freq
        print(f"  {i:<6} {palabra:<20} {freq:>4}  {barra}")

    print()
    print(sep)
    print("Pipeline completado exitosamente.")
    print(sep)
