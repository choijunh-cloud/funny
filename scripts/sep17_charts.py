#!/usr/bin/env python3
"""9월 17일 브리핑용 차트. 한글은 WenQuanYi Micro Hei."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

OUT = Path("/workspace/lectures/assets/sep17")
NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GREEN = "#166534"
RED = "#991B1B"
GRAY = "#4B5563"
BLUE = "#3B6F9E"


def _font():
    for p in (
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJKkr-Regular.otf",
    ):
        if Path(p).exists():
            font_manager.fontManager.addfont(p)
            name = font_manager.FontProperties(fname=p).get_name()
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["axes.edgecolor"] = "#D5DCE6"
    plt.rcParams["axes.labelcolor"] = NAVY
    plt.rcParams["xtick.color"] = GRAY
    plt.rcParams["ytick.color"] = GRAY


def _save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return path


def chart_fomc_dots() -> Path:
    years = ["2026", "2027", "2028", "2029", "장기"]
    june = [3.8, 3.6, 3.4, None, 3.1]
    sep = [4.1, 4.1, 3.9, 3.6, 3.2]
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    x = range(len(years))
    ax.plot(x, june, "o--", color="#9AA6B2", lw=1.8, ms=7, label="6월 중앙값")
    ax.plot(x, sep, "o-", color=NAVY, lw=2.4, ms=8, label="9월 중앙값")
    for i, v in enumerate(sep):
        ax.annotate(f"{v:.1f}%", (i, v), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=NAVY, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(years)
    ax.set_ylim(2.6, 4.6)
    ax.set_ylabel("연방기금금리 중앙값 (%)")
    ax.set_title("FOMC 점도표 중앙값  —  올해 한 번 더, 내년은 제자리", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.legend(frameon=False, loc="lower left")
    ax.axhline(4.1, color=GOLD, lw=0.8, ls=":", alpha=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return _save(fig, "01_fomc_dots.png")


def chart_dc_gap() -> Path:
    labels = ["2025\n수요", "2026\n수요", "2030\n수요", "2030\n그리드"]
    vals = [122.9, 161.0, 490.7, 222.6]
    colors = [NAVY2, NAVY, RED, GOLD]
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    bars = ax.bar(labels, vals, color=colors, width=0.62)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 8, f"{v:g}GW", ha="center", va="bottom", fontsize=9, color=NAVY, fontweight="bold")
    ax.annotate(
        "종이 갭 268GW\n(현장발전 미포함)",
        xy=(2, 490.7),
        xytext=(3.15, 390),
        fontsize=8.5,
        color=RED,
        arrowprops=dict(arrowstyle="->", color=RED, lw=1.1),
    )
    ax.set_ylim(0, 560)
    ax.set_ylabel("GW")
    ax.set_title("데이터센터 전력 수요 vs 그리드 공급  —  TrendForce", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return _save(fig, "02_dc_power_gap.png")


def chart_ai_share() -> Path:
    years = ["2025", "2026", "2027"]
    ai = [25.0, 33.4, 40.0]
    gen = [40.0, 33.0, 25.6]
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    ax.plot(years, ai, "o-", color=NAVY, lw=2.4, ms=8, label="AI 서버 비중")
    ax.plot(years, gen, "s--", color=GOLD, lw=2.0, ms=7, label="일반 서버 비중")
    for x, y in zip(years, ai):
        ax.annotate(f"{y:g}%", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=NAVY, fontweight="bold")
    for x, y in zip(years, gen):
        ax.annotate(f"{y:g}%", (x, y), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=8.5, color=GOLD)
    ax.set_ylim(15, 50)
    ax.set_ylabel("전력 수요 용량 비중 (%)")
    ax.set_title("데이터센터 안에서 AI 서버가 일반 서버를 밀어낸다", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.legend(frameon=False, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    note = ax.text(0.99, 0.04, "2027 AI 40%는 TrendForce ‘넘을 가능성’. 일반 서버 2026 33%는 보간.", transform=ax.transAxes, ha="right", fontsize=7.5, color=GRAY)
    return _save(fig, "03_ai_server_share.png")


def chart_macro_vs_chips() -> Path:
    labels = ["WTI", "美 10년", "S&P500", "Nasdaq", "SOX", "KOSPI"]
    # signed moves from the 9/16 session comments / official closes
    vals = [4.38, None, -0.45, -0.78, 0.40, 1.37]
    # 10Y is a level event, show as n/a bar? Use a separate annotation.
    # Represent 10Y as 0 with note, or skip. I'll plot the five percent moves and annotate 10Y.
    plot_labels = ["WTI\n+4.4%", "S&P\n-0.45%", "Nasdaq\n-0.78%", "SOX\n+0.4%", "KOSPI\n+1.37%"]
    plot_vals = [4.38, -0.45, -0.78, 0.40, 1.37]
    colors = [RED if v < 0 else GREEN for v in plot_vals]
    colors[0] = RED  # oil up is headwind
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    bars = ax.bar(plot_labels, plot_vals, color=colors, width=0.58)
    ax.axhline(0, color="#D0D7E2", lw=1)
    for b, v in zip(bars, plot_vals):
        y = v + (0.18 if v >= 0 else -0.28)
        ax.text(b.get_x() + b.get_width() / 2, y, f"{v:+.2f}%", ha="center", va="bottom" if v >= 0 else "top", fontsize=9, fontweight="bold", color=NAVY)
    ax.set_ylabel("전일 대비 (%)")
    ax.set_title("9/16  —  유가·지수는 부담, 반도체·코스피는 차별화", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.set_ylim(-1.6, 5.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(0.01, 0.96, "美 10년물 장중 5.041% (2007 이후 최고)는 레벨 이벤트. SOX는 필라델피아 반도체 +0.40%.", transform=ax.transAxes, fontsize=7.8, color=GRAY, va="top")
    return _save(fig, "04_macro_vs_chips.png")


def main():
    _font()
    paths = [chart_fomc_dots(), chart_dc_gap(), chart_ai_share(), chart_macro_vs_chips()]
    for p in paths:
        print(p, p.stat().st_size)


if __name__ == "__main__":
    main()
