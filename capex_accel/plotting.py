"""Charts for the capex-acceleration verification."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np

from capex_accel.metrics import CapexFrame

DISPLAY = {"SK하이닉스": "SK hynix", "삼성전자": "Samsung"}


def _label(name: str) -> str:
    return DISPLAY.get(name, name)


NAVY = "#0F2043"
GOLD = "#B8943A"
TEAL = "#0F766E"
RED = "#991B1B"
BLUE = "#1D4E89"
GRAY = "#6B7280"
LIGHT = "#E5E7EB"


def _style():
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.edgecolor": "#D1D5DB",
            "axes.labelcolor": NAVY,
            "xtick.color": GRAY,
            "ytick.color": GRAY,
            "text.color": NAVY,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.titleweight": "bold",
            "axes.titlesize": 13,
            "axes.labelsize": 10,
        }
    )


def save(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140, bbox_inches="tight")
    plt.close(fig)


def plot_history(frame: CapexFrame, path: Path):
    _style()
    fig, axes = plt.subplots(2, 1, figsize=(11.2, 7.4), sharex=True, gridspec_kw={"height_ratios": [1.15, 1]})
    x = frame.quarters
    ax = axes[0]
    ax.bar(x, frame.c, width=80, color="#C5D0DE", label="Quarterly cash capex")
    ttm = [v if v is not None else np.nan for v in frame.ttm]
    ax.plot(x, ttm, color=NAVY, lw=2.2, label="Trailing four-quarter sum")
    ax.set_ylabel("USD billions")
    ax.set_title("Microsoft, Alphabet, Amazon, Meta — cash purchases of PP&E")
    ax.legend(frameon=False, loc="upper left")
    ax.set_xlim(date(2016, 1, 1), date(2026, 9, 1))

    ax = axes[1]
    colors = [TEAL if (v or 0) >= 0 else RED for v in frame.acceleration]
    acc = [0 if v is None else v for v in frame.acceleration]
    ax.bar(x, acc, width=80, color=colors)
    ax.axhline(0, color=GRAY, lw=0.8)
    q2 = date(2026, 6, 30)
    if q2 in frame.quarters:
        a = frame.value(q2, "acceleration")
        ax.scatter([q2], [a], color=GOLD, s=46, zorder=3, label=f"2026 Q2  {a:.1f}")
        ax.legend(frameon=False, loc="upper left")
    ax.set_ylabel("Acceleration  $B / quarter²")
    ax.set_title("Second difference of the trailing four-quarter sum  A_q")
    ax.xaxis.set_major_locator(mdates.YearLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    fig.tight_layout()
    save(fig, path)


def plot_scenarios(frame: CapexFrame, paths: dict[str, list[tuple[date, float]]], path: Path):
    _style()
    fig, ax = plt.subplots(figsize=(11.2, 5.2))
    hist_x = [q for q, a in zip(frame.quarters, frame.acceleration) if a is not None and q >= date(2024, 1, 1)]
    hist_y = [frame.value(q, "acceleration") for q in hist_x]
    ax.plot(hist_x, hist_y, color=NAVY, lw=2.4, marker="o", ms=4.5, label="Reported")
    styles = {
        "base": (GOLD, "Base path: 2026 $680B, 2027 $1.02T"),
        "reaccel": (RED, "Reacceleration: 2027 $1.12T, fast Q1"),
    }
    for key, (color, label) in styles.items():
        xs, ys = zip(*paths[key])
        ax.plot(xs, ys, color=color, lw=2.0, marker="o", ms=4, label=label)
    a2 = frame.value(date(2026, 6, 30), "acceleration")
    ax.axhline(a2, color=BLUE, lw=1, ls="--", label=f"2026 Q2 acceleration {a2:.1f}")
    ax.axhline(0, color=GRAY, lw=0.7)
    ax.set_title("Acceleration is still rising in the filings. Later points are a spending assumption.")
    ax.set_ylabel("A_q   $B / quarter²")
    ax.legend(frameon=False, loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    fig.tight_layout()
    save(fig, path)


def plot_prices(prices: dict[str, list[tuple[date, float]]], peaks: dict[str, date], path: Path):
    _style()
    fig, ax = plt.subplots(figsize=(11.2, 6.0))
    colors = {
        "NVDA": NAVY,
        "TSM": BLUE,
        "AVGO": "#7C3AED",
        "MU": RED,
        "SOX": GOLD,
        "SK하이닉스": TEAL,
        "삼성전자": "#B45309",
    }
    start = date(2023, 1, 3)
    for name, rows in prices.items():
        series = [(d, px) for d, px in rows if d >= start]
        base = series[0][1]
        ax.plot(
            [d for d, _ in series],
            [px / base * 100 for _, px in series],
            color=colors.get(name, GRAY),
            lw=1.6,
            label=_label(name),
        )
        peak = peaks.get(name)
        if peak:
            match = min(series, key=lambda item: abs((item[0] - peak).days))
            ax.scatter([match[0]], [match[1] / base * 100], color=colors.get(name, GRAY), s=22, zorder=3)
    ax.axvline(date(2026, 6, 30), color=GRAY, lw=1, ls="--")
    ax.set_yscale("log")
    ax.set_ylabel("Index, 2023-01-03 = 100, log scale")
    ax.set_title("Beneficiary prices. Dots mark each series high from 2024 through 9 Oct 2026.")
    ax.legend(frameon=False, ncol=4, loc="upper left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    fig.tight_layout()
    save(fig, path)


def plot_gain_share(shares: dict[str, list[dict]], path: Path):
    _style()
    fig, ax = plt.subplots(figsize=(11.2, 5.4))
    names = list(shares)
    checkpoints = [date(2024, 12, 31), date(2025, 6, 30), date(2025, 12, 31), date(2026, 3, 31)]
    labels = ["End-2024", "Mid-2025", "End-2025", "End-Q1 2026"]
    x = np.arange(len(names))
    width = 0.18
    palette = ["#C5D0DE", "#7DD3C7", GOLD, RED]
    for i, (day, label, color) in enumerate(zip(checkpoints, labels, palette)):
        vals = []
        for name in names:
            match = next((row for row in shares[name] if str(row["checkpoint"])[:10] == day.isoformat()), None)
            vals.append(0 if match is None or match["share_of_gain"] is None else match["share_of_gain"] * 100)
        ax.bar(x + (i - 1.5) * width, vals, width=width, color=color, label=label)
    ax.axhline(100, color=LIGHT, lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([_label(name) for name in names])
    ax.set_ylabel("Share of the gain from Jan 2023 to the 2024–2026 high")
    ax.set_title("Share of the Jan 2023-to-high gain already in the price")
    ax.set_ylim(0, 110)
    ax.legend(frameon=False, ncol=4, loc="upper right")
    fig.tight_layout()
    save(fig, path)


def plot_lead_times(rows: list[dict], path: Path):
    _style()
    fig, ax = plt.subplots(figsize=(11.2, 5.6))
    # rows: cycle, name, lag
    rows = [
        row
        for row in rows
        if row.get("lag_months") is not None
        and (str(row.get("cycle", "")).startswith("2026") or row.get("status") == "drawdown_top")
    ]
    cycles = []
    for row in rows:
        if row["cycle"] not in cycles:
            cycles.append(row["cycle"])
    names = []
    for row in rows:
        if row["name"] not in names:
            names.append(row["name"])
    y = np.arange(len(names))
    offsets = np.linspace(-0.22, 0.22, len(cycles)) if len(cycles) > 1 else [0]
    colors = [NAVY, GOLD, RED, TEAL]
    for i, cycle in enumerate(cycles):
        lags = []
        for name in names:
            match = next((r for r in rows if r["cycle"] == cycle and r["name"] == name), None)
            lags.append(np.nan if match is None or match["lag_months"] is None else match["lag_months"])
        legend = cycle.replace("성장률", "growth peak").replace("가속도 후보", "accel. candidate")
        ax.scatter(lags, y + offsets[i], s=48, color=colors[i % len(colors)], label=legend, zorder=3)
    ax.axvline(0, color=GRAY, lw=0.9)
    ax.set_yticks(y)
    ax.set_yticklabels([_label(name) for name in names])
    ax.set_xlabel("Months from capex-signal quarter-end to the price high. Negative = price topped first.")
    ax.set_title("Price-high lag versus the capex growth-rate peak, and versus 2026 Q2")
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    save(fig, path)
