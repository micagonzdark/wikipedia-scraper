"""
scraper/fetcher.py
Responsabilidad: descargar la portada de Wikipedia y extraer titulares.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime

WIKIPEDIA_URL = "https://es.wikipedia.org/wiki/Wikipedia:Portada"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Mapa: id del div en el HTML → nombre legible de la sección
_SECCIONES_LISTA = {
    "main-cur": "Noticias de actualidad",
    "main-itd": "Efemerides",
}

_SECCIONES_BOLD = {
    "main-tfa": "Articulo destacado",
}


def scrape_headlines(url: str = WIKIPEDIA_URL) -> list[dict]:
    """
    Descarga la portada de Wikipedia en español y extrae titulares de:
      - Noticias de actualidad  (id='main-cur')
      - Efemérides              (id='main-itd')
      - Artículo destacado      (id='main-tfa', primer <b>)

    Args:
        url: URL de la portada a scrapear. Por defecto Wikipedia en español.

    Returns:
        Lista de dicts con claves:
          'titular' (str), 'seccion' (str), 'fecha' (str ISO-8601)

    Raises:
        requests.HTTPError: si el servidor responde con un código de error HTTP.
        requests.Timeout:   si la conexión supera los 10 segundos.
    """
    response = requests.get(url, headers=_HEADERS, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    titulares: list[dict] = []
    fecha = datetime.now().isoformat(timespec="seconds")

    # Secciones que usan listas (<li>)
    for div_id, nombre in _SECCIONES_LISTA.items():
        div = soup.find("div", id=div_id)
        if div:
            for li in div.find_all("li"):
                texto = li.get_text(separator=" ", strip=True)
                if texto:
                    titulares.append({"titular": texto, "seccion": nombre, "fecha": fecha})

    # Secciones que usan el primer <b> como titular
    for div_id, nombre in _SECCIONES_BOLD.items():
        div = soup.find("div", id=div_id)
        if div:
            primer_b = div.find("b")
            if primer_b:
                texto = primer_b.get_text(strip=True)
                if texto:
                    titulares.append({"titular": texto, "seccion": nombre, "fecha": fecha})

    return titulares
