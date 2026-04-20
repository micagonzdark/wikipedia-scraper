# 📰 Wikipedia Headline Tracker

> A Python project I built to practice web scraping, building CLI tools, and data visualization.

---

## About this project

I wanted to build something that actually *does something* — not just a tutorial clone. The idea is simple: visit Wikipedia's front page every day, grab all the headlines, save them, and track which words keep showing up over time.

After a week of daily runs, you have a real dataset that tells you what topics Wikipedia covered most that week. It's small, but it connects several things I've been learning: web scraping, data analysis, and building proper Python tools.

---

## What it does

1. **Scrapes** Wikipedia's Spanish front page for today's headlines
2. **Cleans** the text — removes common filler words (stopwords), months, and punctuation
3. **Saves** the headlines to a CSV file, appending new data each day so it accumulates over time
4. **Analyzes** which words appear most often in that day's headlines
5. **Visualizes** word frequency trends as an interactive chart you can open in your browser

---

## What I learned building this

- Dealing with a real **Windows encoding bug** — the terminal was crashing on special characters because Windows defaults to `cp1252` instead of `UTF-8`. Took some digging to fix properly.
- **Cleaning messy data** — raw headlines are full of noise (months, prepositions, image captions). I built a stopword filter to strip all of that out so only meaningful words remain.
- **Organizing code into modules** instead of dumping everything into one file. Each module (`fetcher`, `storage`, `analyzer`, `visualizer`) has one job.
- **Building a CLI others can actually use** — flags like `--top`, `--url`, and `--plot` make the tool flexible without needing to touch the code.

---

## Project structure

```
wikipedia_scraper/
├── scraper/
│   ├── __init__.py        # Ties the package together
│   ├── fetcher.py         # Downloads and parses the Wikipedia page
│   ├── storage.py         # Saves data to CSV (appends, never overwrites)
│   ├── analyzer.py        # Counts word frequency, filters noise
│   └── visualizer.py      # Generates the interactive Plotly chart
├── output/
│   └── .gitkeep           # Keeps the folder in git; data files are gitignored
├── main.py                # CLI entry point — two commands: run and visualize
└── requirements.txt
```

---

## Installation

```bash
# 1. Clone the repo
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

> **Windows note:** add `-X utf8` when running the script to avoid an encoding issue with special characters.

### Scrape today's headlines and see the word frequency

```bash
python -X utf8 main.py run
```

### Scrape today's data AND generate the chart in one step

```bash
python -X utf8 main.py run --plot
```

### Generate the interactive chart from your accumulated data

```bash
python -X utf8 main.py visualize
```

### Change how many top words to show

```bash
python -X utf8 main.py run --top 10
```

### See all available options

```bash
python -X utf8 main.py run --help
```

---

## Project Showcase

### Top 5 words — April 19, 2026 (360 headlines tracked over 5 days)

After filtering out months, prepositions, and other noise, the words that actually came out on top:

| Rank | Word | Occurrences | What it reflects |
|:---:|---|:---:|---|
| 1 | **futbolista** | 27 | Several footballer obituaries and sports news |
| 2 | **día** | 30 | International Days listed on Wikipedia |
| 3 | **campeonato** | 22 | Multiple active championships (NBA, snooker, judo) |
| 4 | **nace** | 22 | Birthday entries in the Efemérides section |
| 5 | **actriz** | 18 | Several actress entries in current events |

### What the CSV looks like inside

```csv
titular,seccion,fecha
"19 de abril: Elecciones legislativas de Bulgaria",Noticias de actualidad,2026-04-19T20:26:40
"19 de abril: Amstel Gold Race masculina y femenina de ciclismo",Noticias de actualidad,2026-04-19T20:26:40
"Pericles",Articulo destacado,2026-04-19T20:26:40
```

After several daily runs, `main.py visualize` creates an interactive chart at `output/timeseries_plot.html`.
Open it in any browser — hover to see exact values, click the legend to toggle words on and off, and zoom in.

---

## Dependencies

| Package | What I used it for |
|---|---|
| `requests` | Making the HTTP request to download the Wikipedia page |
| `beautifulsoup4` + `lxml` | Parsing the HTML and extracting the headline text |
| `typer[all]` | Building the CLI with flags, help text, and colored output |
| `pandas` | Grouping and counting word frequencies by day |
| `plotly` | Generating the interactive HTML time-series chart |

---

*This is a learning project. I tried to write it cleanly — but I'm still improving and there's always more to learn!*
