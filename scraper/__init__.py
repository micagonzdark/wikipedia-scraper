"""
scraper package
Módulos:
  fetcher    — descarga y extrae titulares de Wikipedia
  storage    — persiste los datos en CSV (append mode)
  analyzer   — análisis de frecuencia de palabras
  visualizer — genera gráficos de series temporales
"""

from .fetcher    import scrape_headlines, WIKIPEDIA_URL
from .storage    import save_to_csv
from .analyzer   import analyze_words, STOPWORDS
from .visualizer import generate_timeseries

__all__ = [
    "scrape_headlines",
    "WIKIPEDIA_URL",
    "save_to_csv",
    "analyze_words",
    "STOPWORDS",
    "generate_timeseries",
]

