"""
scraper/visualizer.py
Reads the accumulated headlines CSV and generates an interactive
Plotly time-series chart saved as an HTML file.
"""

import re
from collections import Counter
from pathlib import Path

import pandas as pd
import plotly.express as px

from .analyzer import STOPWORDS
from .storage import DEFAULT_OUTPUT_DIR

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_LIMPIEZA = re.compile(r"[^a-záéíóúüñ\s]")

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
    output_filename: str = "timeseries_plot.html",
) -> Path:
    """
    Reads the accumulated headlines CSV and produces an interactive
    Plotly time-series HTML chart showing the daily frequency of
    the top N words over time.

    Args:
        csv_path:        Path to the historical 'titulares.csv'.
        top_n:           Number of top words to track.
        stopwords:       Words to exclude from the analysis.
        output_dir:      Directory to save the HTML chart.
        output_filename: File name for the saved chart.

    Returns:
        Path to the generated HTML file.

    Raises:
        FileNotFoundError: if csv_path does not exist.
        ValueError:        if the CSV is empty or yields no valid tokens.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Headlines CSV not found: {csv_path}\n"
            "Run the scraper first:  python -X utf8 main.py run"
        )

    df = pd.read_csv(csv_path, encoding="utf-8")

    if df.empty:
        raise ValueError("The headlines CSV is empty — run the scraper first.")

    # Extract date portion from ISO-8601 timestamp
    df["date"] = pd.to_datetime(df["fecha"]).dt.date

    # Explode each headline into (date, word) pairs
    records: list[dict] = []
    for _, row in df.iterrows():
        for word in _tokenize(str(row["titular"]), stopwords):
            records.append({"date": row["date"], "word": word})

    if not records:
        raise ValueError("No valid words found after filtering stopwords.")

    long_df = pd.DataFrame(records)

    # Identify the top N words globally
    top_words = [w for w, _ in Counter(long_df["word"]).most_common(top_n)]

    # Aggregate daily frequency for top words (long format — perfect for px.line)
    daily = (
        long_df[long_df["word"].isin(top_words)]
        .groupby(["date", "word"])
        .size()
        .reset_index(name="frequency")
    )
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.sort_values(["date", "word"])

    # Build readable date range for the subtitle
    unique_dates = daily["date"].nunique()
    min_d = daily["date"].min().strftime("%b %d")
    max_d = daily["date"].max().strftime("%b %d, %Y")
    date_range = f"{min_d} – {max_d}" if unique_dates > 1 else min_d

    # -----------------------------------------------------------------------
    # Build Plotly chart
    # -----------------------------------------------------------------------
    fig = px.line(
        daily,
        x="date",
        y="frequency",
        color="word",
        markers=True,
        template="plotly_dark",
        title=(
            f"Wikipedia Headline Word Frequency — Top {top_n} Words"
            f"<br><sup>{date_range}  ·  {len(df):,} headlines tracked</sup>"
        ),
        labels={
            "date":      "Date",
            "frequency": "Daily Occurrences",
            "word":      "Word",
        },
        color_discrete_sequence=_PALETTE,
        line_shape="spline",
    )

    # Polish the traces
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=9, line=dict(width=1.5, color="#0D1117")),
    )

    # Custom layout on top of plotly_dark
    fig.update_layout(
        plot_bgcolor="#161B22",
        paper_bgcolor="#0D1117",
        font=dict(family="Inter, system-ui, sans-serif", color="#E2E8F0", size=13),
        title=dict(font=dict(size=18, color="white"), x=0.5, xanchor="center", pad=dict(b=20)),
        legend=dict(
            title=dict(text=f"Top {top_n} Words", font=dict(color="#94A3B8")),
            bgcolor="#21262D",
            bordercolor="#30363D",
            borderwidth=1,
        ),
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#21262D", bordercolor="#30363D", font_color="white"),
        xaxis=dict(
            showgrid=True,
            gridcolor="#30363D",
            tickformat="%b %d",
            dtick="D1",
            title=dict(font=dict(color="#94A3B8")),
            tickfont=dict(color="#CBD5E1"),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#30363D",
            title=dict(font=dict(color="#94A3B8")),
            tickfont=dict(color="#CBD5E1"),
            rangemode="tozero",
        ),
        margin=dict(t=100, b=60, l=60, r=40),
    )

    # Single-day hint annotation
    if unique_dates == 1:
        fig.add_annotation(
            text="Tip: run daily to build a multi-day time series",
            xref="paper", yref="paper",
            x=0.5, y=-0.12,
            showarrow=False,
            font=dict(color="#94A3B8", size=11),
            align="center",
        )

    # Footer watermark
    fig.add_annotation(
        text="Source: Wikipedia Portada  ·  github.com/YOUR_USERNAME/wikipedia-scraper",
        xref="paper", yref="paper",
        x=1.0, y=-0.09,
        showarrow=False,
        font=dict(color="#484F58", size=9),
        align="right",
    )

    # -----------------------------------------------------------------------
    # Save as interactive HTML
    # -----------------------------------------------------------------------
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / output_filename

    fig.write_html(
        output_path,
        include_plotlyjs="cdn",   # loads Plotly from CDN — keeps file small
        full_html=True,
    )

    return output_path
