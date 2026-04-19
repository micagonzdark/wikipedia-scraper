# Wikipedia Headline Scraper & Analyzer CLI

> A modular Python CLI tool that scrapes Wikipedia's front page, exports headlines to CSV, and performs automated word-frequency analysis — built with real-world engineering practices.

---

## Description

**Wikipedia Headline Scraper & Analyzer** is a command-line data pipeline that:

1. **Scrapes** Wikipedia's Spanish front page using `requests` + `BeautifulSoup`
2. **Exports** all extracted headlines to a structured CSV file
3. **Analyzes** word frequency across headlines, filtering Spanish stopwords, and surfaces the most relevant terms of the day

The tool was built with a focus on **modularity**, **reproducibility**, and **clean CLI ergonomics** using [Typer](https://typer.tiangolo.com/) with [Rich](https://github.com/Textualize/rich) for beautiful terminal output.

---

## Key Features

| Feature | Details |
|---|---|
| 🏗️ **Modular Architecture** | Logic split into `fetcher`, `storage`, and `analyzer` modules under a clean `scraper/` package |
| ⚙️ **Typer CLI** | Full argument parsing with `--url`, `--top`, `--output`; built-in `--help`; range validation on `--top` |
| 🧹 **Automated Data Cleaning** | Regex-based tokenization, Spanish stopword filtering, and minimum token-length threshold |
| 📄 **Dual CSV Export** | Generates `titulares.csv` (raw headlines) and `top_N_palabras.csv` (frequency ranking) |
| 📊 **Rich Terminal Output** | Colored tables, progress spinners, Unicode bar charts — all rendered via the `rich` library |
| 🔁 **Configurable Pipeline** | Every parameter (URL, output file, top-N count) is overridable from the command line |

---

## Engineering Highlights

### 🔍 Dynamic Selector Discovery

Wikipedia's HTML structure does not match commonly documented CSS selectors (e.g., the frequently cited `#mp-itn` does not exist on the Spanish portal). Rather than hardcoding selectors based on assumptions, a **diagnostic introspection script** was run against the live page to enumerate all `<div id="...">` elements and map them to their actual content:

```
main-cur  →  Noticias de actualidad (news)
main-tfa  →  Artículo destacado (featured article)
main-itd  →  Efemérides (historical events)
```

This approach makes the scraper resilient and easy to adapt to other Wikipedia portals or news sites.

---

### 🪟 Windows UTF-8 Encoding Fix

Python's default console encoding on Windows is `cp1252`, which cannot represent Unicode characters used by `rich` (e.g., `█`, `─`, `→`). Two complementary fixes were applied:

1. **Pre-import stdout reconfiguration** — `sys.stdout.reconfigure(encoding="utf-8")` is called before any library import that touches the console.
2. **Modern Rich console renderer** — `Console(legacy_windows=False)` disables the `LegacyWindowsConsole` wrapper (which routes through `cp1252`) and uses the modern Win32 Unicode-native renderer instead.
3. **Python UTF-8 mode** — The tool is invoked with the `-X utf8` flag, which activates [PEP 540](https://peps.python.org/pep-0540/) UTF-8 mode globally at interpreter startup.

---

## Project Structure

```
wikipedia_scraper/
├── scraper/
│   ├── __init__.py        # Public API re-exports
│   ├── fetcher.py         # scrape_headlines() — HTTP + HTML parsing
│   ├── storage.py         # save_to_csv() — CSV persistence
│   └── analyzer.py        # analyze_words() — NLP frequency analysis
├── output/
│   └── .gitkeep           # Folder tracked; generated files are gitignored
├── main.py                # CLI entry point (Typer)
├── requirements.txt
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.10+
- Git

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/wikipedia-scraper.git
cd wikipedia-scraper

# 2. Create and activate a virtual environment
python -m venv venv

# Windows
.\venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Usage

> **Windows note:** Use the `-X utf8` flag to enable full Unicode support in the terminal.

### Show help

```bash
python -X utf8 main.py --help
```

```
 Usage: main.py [OPTIONS]

 Pipeline completo: scraping -> CSV -> analisis de frecuencia de palabras.

┌─ Options ───────────────────────────────────────────────────────────────────┐
│ --url    TEXT               URL of the page to scrape.                      │
│                             [default: https://es.wikipedia.org/wiki/...]    │
│ --top    INTEGER [1<=x<=50] Number of top words to display. [default: 5]    │
│ --output TEXT               Name of the output CSV file.                    │
│                             [default: titulares.csv]                        │
│ --help                      Show this message and exit.                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Run with defaults

```bash
python -X utf8 main.py
```

### Custom run — Top 3 words, custom filename

```bash
python -X utf8 main.py --top 3 --output noticias_hoy.csv
```

### Scrape an English Wikipedia page

```bash
python -X utf8 main.py --url https://en.wikipedia.org/wiki/Main_Page --top 10
```

---

## Visual Report: Real-World Results

Sample run on **April 19, 2026** — 48 headlines extracted from the Spanish Wikipedia front page.

### Terminal Output (Top 5 Words)

```
────────────────────────── Paso 3 — Top 5 palabras ──────────────────────────

                    Top 5 palabras más frecuentes
╭────────┬────────────────┬────────────┬────────────────────────────────╮
│  Rank  │ Palabra        │ Frecuencia │ Barra                          │
├────────┼────────────────┼────────────┼────────────────────────────────┤
│   1    │ abril          │         35 │ ██████████████████████████████ │
│   2    │ años           │          5 │ ████                           │
│   3    │ futbolista     │          4 │ ███                            │
│   4    │ día            │          4 │ ███                            │
│   5    │ israel         │          3 │ ███                            │
╰────────┴────────────────┴────────────┴────────────────────────────────╯

─────────────────────────── Pipeline completado ────────────────────────────
```

> **Insight:** `abril` dominates because Wikipedia timestamps every event with the current month. The semantically meaningful signal lies in words like **futbolista** and **israel**, which accurately reflect the news cycle of the day (NBA playoffs start, WrestleMania 42, and ongoing geopolitical events).

### Generated CSV: `titulares.csv`

| titular | seccion | fecha |
|---|---|---|
| 19 de abril: Elecciones legislativas de Bulgaria | Noticias de actualidad | 2026-04-19T20:26:40 |
| 19 de abril: Amstel Gold Race masculina y femenina | Noticias de actualidad | 2026-04-19T20:26:40 |
| 1926 (hace 100 años): Nace William Klein, fotógrafo... | Efemerides | 2026-04-19T20:26:40 |
| Pericles | Articulo destacado | 2026-04-19T20:26:40 |

- **48 rows**, UTF-8 encoded
- **3 columns:** `titular`, `seccion`, `fecha`
- Timestamp in ISO 8601 format for easy parsing with `pandas` or any data tool

---

## Dependencies

| Package | Version | Role |
|---|---|---|
| `requests` | 2.32.3 | HTTP client for page download |
| `beautifulsoup4` | 4.12.3 | HTML parsing and content extraction |
| `lxml` | 5.3.0 | High-performance HTML parser backend |
| `typer[all]` | 0.24.1 | CLI framework (includes `click` + `rich`) |

---

## License

MIT License — free to use, fork, and extend.
