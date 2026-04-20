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

- **Web scraping** with `requests` and `BeautifulSoup` — including how to actually inspect a live webpage's HTML to find the right elements (they're often different from what you'd expect from tutorials)
- **Building CLI tools** with `Typer` and `Rich` for colored, readable terminal output
- **Python package structure** — organizing code into a proper `scraper/` package with separate files for each responsibility
- **Working with data** using `pandas` — grouping, counting, and reshaping data over time
- **Interactive charts** with `Plotly` — hover effects, dark themes, and publishing as standalone HTML files
- **Debugging a Windows encoding bug** — a tricky issue where the terminal crashes on special characters because Windows uses `cp1252` instead of `UTF-8` by default

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

## Sample output

Running `main.py run` prints a table directly in the terminal:

```
────────────────── Step 3 — Top 5 Words ──────────────────

        Top 5 most frequent words  (today's run)
╭────────┬─────────────┬────────────┬────────────────────────────────╮
│  Rank  │ Word        │ Frequency  │ Bar                            │
├────────┼─────────────┼────────────┼────────────────────────────────┤
│   1    │ futbolista  │     4      │ ██████████████████████████████ │
│   2    │ día         │     4      │ ██████████████████████████████ │
│   3    │ israel      │     3      │ ██████████████████████         │
│   4    │ años        │     5      │ ████████████████████████       │
│   5    │ baloncesto  │     2      │ ███████████████                │
╰────────┴─────────────┴────────────┴────────────────────────────────╯
```

After several daily runs, `visualize` creates an interactive chart at `output/timeseries_plot.html`.
Open it in any browser — you can hover to see exact values, click the legend to toggle words on and off,
and zoom into specific date ranges.

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
