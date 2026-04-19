"""
scraper/visualizer.py
Responsabilidad: leer el CSV histórico y generar un gráfico de series
temporales con la frecuencia diaria de las N palabras más frecuentes.
"""

import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

from .analyzer import STOPWORDS
from .storage import DEFAULT_OUTPUT_DIR

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_LIMPIEZA = re.compile(r"[^a-záéíóúüñ\s]")

# Curated color palette — vibrant, dark-mode friendly
_PALETTE = [
    "#7C3AED",  # violet
    "#06B6D4",  # cyan
    "#10B981",  # emerald
    "#F59E0B",  # amber
    "#EF4444",  # red
    "#EC4899",  # pink
    "#3B82F6",  # blue
    "#84CC16",  # lime
    "#F97316",  # orange
    "#A78BFA",  # light violet
]

_DARK_BG     = "#0D1117"
_PANEL_BG    = "#161B22"
_GRID_COLOR  = "#30363D"
_AXIS_COLOR  = "#94A3B8"
_TICK_COLOR  = "#CBD5E1"
_FOOTER_COLOR = "#484F58"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _tokenize(text: str, stopwords: set[str]) -> list[str]:
    """Lowercase, strip non-letter chars, filter stopwords and short tokens."""
    cleaned = _LIMPIEZA.sub(" ", text.lower())
    return [w for w in cleaned.split() if len(w) >= 3 and w not in stopwords]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_timeseries(
    csv_path: Path,
    top_n: int = 5,
    stopwords: set[str] = STOPWORDS,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    output_filename: str = "timeseries_plot.png",
) -> Path:
    """
    Reads the accumulated headlines CSV and produces a time-series line chart
    showing the daily frequency of the top N words over time.

    Args:
        csv_path:        Path to the historical 'titulares.csv'.
        top_n:           Number of top words to track.
        stopwords:       Words to exclude from the analysis.
        output_dir:      Directory to save the PNG chart.
        output_filename: File name for the saved chart.

    Returns:
        Path to the generated PNG image.

    Raises:
        FileNotFoundError: if csv_path does not exist.
        ValueError:        if the CSV is empty or yields no valid tokens.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Headlines CSV not found: {csv_path}\n"
            "Run the scraper first with: python -X utf8 main.py"
        )

    df = pd.read_csv(csv_path, encoding="utf-8")

    if df.empty:
        raise ValueError("The headlines CSV is empty — run the scraper first.")

    # Extract just the date part from the ISO-8601 timestamp
    df["date"] = pd.to_datetime(df["fecha"]).dt.date

    # Explode each headline into (date, word) pairs
    records: list[dict] = []
    for _, row in df.iterrows():
        tokens = _tokenize(str(row["titular"]), stopwords)
        for word in tokens:
            records.append({"date": row["date"], "word": word})

    if not records:
        raise ValueError("No valid words found after filtering stopwords.")

    long_df = pd.DataFrame(records)

    # Identify the top N words globally (by total count)
    top_words = [w for w, _ in Counter(long_df["word"]).most_common(top_n)]

    # Keep only top words, count per (date, word)
    daily = (
        long_df[long_df["word"].isin(top_words)]
        .groupby(["date", "word"])
        .size()
        .reset_index(name="frequency")
    )

    # Pivot to matrix: rows = date, columns = word
    pivot = (
        daily.pivot(index="date", columns="word", values="frequency")
        .fillna(0)
        .sort_index()
    )
    pivot.index = pd.to_datetime(pivot.index)

    unique_dates = pivot.index.nunique()

    # -----------------------------------------------------------------------
    # Plot
    # -----------------------------------------------------------------------
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(14, 7))
    fig.patch.set_facecolor(_DARK_BG)
    ax.set_facecolor(_PANEL_BG)

    for i, word in enumerate(top_words):
        if word not in pivot.columns:
            continue
        color = _PALETTE[i % len(_PALETTE)]
        ax.plot(
            pivot.index,
            pivot[word],
            label=word,
            color=color,
            linewidth=2.5,
            marker="o",
            markersize=7,
            markerfacecolor=color,
            markeredgecolor=_DARK_BG,
            markeredgewidth=1.2,
            alpha=0.92,
        )

    # --- Title & labels ---
    num_days = unique_dates
    date_range = (
        f"{pivot.index.min().strftime('%b %d')} – {pivot.index.max().strftime('%b %d, %Y')}"
        if num_days > 1
        else pivot.index.min().strftime("%B %d, %Y")
    )
    ax.set_title(
        f"Wikipedia Headline Word Frequency — Top {top_n} Words\n"
        f"{date_range}  ·  {len(df):,} headlines tracked",
        fontsize=15,
        fontweight="bold",
        color="white",
        pad=18,
        linespacing=1.6,
    )
    ax.set_xlabel("Date", fontsize=12, color=_AXIS_COLOR, labelpad=10)
    ax.set_ylabel("Daily Occurrences", fontsize=12, color=_AXIS_COLOR, labelpad=10)

    # --- X-axis date formatting ---
    if unique_dates == 1:
        # Single-day: show a clear label so the chart isn't blank on x-axis
        ax.set_xticks(pivot.index)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    else:
        ax.xaxis.set_major_locator(mdates.DayLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    plt.xticks(rotation=45, ha="right", color=_TICK_COLOR, fontsize=10)
    plt.yticks(color=_TICK_COLOR, fontsize=10)

    # --- Grid & spines ---
    ax.grid(color=_GRID_COLOR, linestyle="--", linewidth=0.8, alpha=0.7)
    ax.spines["bottom"].set_color(_GRID_COLOR)
    ax.spines["left"].set_color(_GRID_COLOR)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # --- Legend ---
    legend = ax.legend(
        title=f"Top {top_n} Words",
        title_fontsize=10,
        fontsize=10,
        framealpha=0.25,
        facecolor="#21262D",
        edgecolor=_GRID_COLOR,
        labelcolor="white",
        loc="upper right",
    )
    legend.get_title().set_color(_AXIS_COLOR)

    # --- Annotation for single-day chart ---
    if unique_dates == 1:
        ax.annotate(
            "Tip: run daily to build a multi-day time series",
            xy=(0.5, 0.05),
            xycoords="axes fraction",
            ha="center",
            fontsize=9,
            color=_AXIS_COLOR,
            style="italic",
        )

    # --- Footer ---
    fig.text(
        0.99, 0.01,
        "Source: Wikipedia Portada  ·  github.com/YOUR_USERNAME/wikipedia-scraper",
        ha="right",
        fontsize=8,
        color=_FOOTER_COLOR,
    )

    plt.tight_layout(pad=2.0)

    # --- Save ---
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename
    plt.savefig(
        output_path,
        dpi=150,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)

    return output_path
