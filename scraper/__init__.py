"""
scraper package
Módulos:
  fetcher   — descarga y extrae titulares de Wikipedia
  storage   — persiste los datos en CSV
  analyzer  — análisis de frecuencia de palabras
"""

from .fetcher  import scrape_headlines, WIKIPEDIA_URL
from .storage  import save_to_csv
from .analyzer import analyze_words, STOPWORDS

__all__ = [
    "scrape_headlines",
    "WIKIPEDIA_URL",
    "save_to_csv",
    "analyze_words",
    "STOPWORDS",
]
