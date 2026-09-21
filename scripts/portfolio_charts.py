#!/usr/bin/env python3
"""9/21 실행 북 차트."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

sys.path.insert(0, str(Path(__file__).resolve().parent))

import insights_charts as IC
import portfolio_book as B

OUT = Path("/workspace/lectures/assets/portfolio")
NAVY, NAVY2, GOLD, GREEN, RED, GRAY, LIGHT, AMBER, TEAL = (
    IC.NAVY, IC.NAVY2, IC.GOLD, IC.GREEN, IC.RED, IC.GRAY, IC.LIGHT, IC.AMBER, IC.TEAL
)


def _save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def chart_01_pie() -> Path:
    IC._font()
    fig, ax = plt.subplots(figsize=(6.8, 4.0))
    labels = ["현금 40", "주식 60"]
    ax.pie(
        [B.CASH_PCT, B.EQUITY_PCT],
        labels=labels,
        colors=[TEAL, NAVY],
        startangle=90,
        wedgeprops=dict(width=0.46, edgecolor="white"),
        textprops=dict(color=NAVY, fontsize=11),
    )
    ax.text(0, 0, "1억 기준\n주식 6,000만", ha="center", va="center", color=NAVY, fontsize=11)
    fig.suptitle("자산배분 — 60/40은 유지, 반도체 추격은 접는다", color=NAVY, fontsize=12, x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "01_alloc.png")


def chart_02_bookc() -> Path:
    IC._font()
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    got = B.book_c_weights()
    names = [n for n, _ in B.BOOK_C]
    target = [t for _, t in B.BOOK_C]
    actual = [got[n] for n in names]
    x = range(len(names))
    ax.bar([i - 0.18 for i in x], target, width=0.36, color=GOLD, label="Book C 목표")
    ax.bar([i + 0.18 for i in x], actual, width=0.36, color=NAVY2, label="이번 북")
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.set_ylabel("% of 주식")
    ax.legend(frameon=False)
    ax.set_ylim(0, 55)
    fig.suptitle("주식 안 Book C — 버킷은 맞추고, 삼성+닉스+스퀘어만 22%로 축소", color=NAVY, fontsize=12, x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "02_bookc.png")


def chart_03_names() -> Path:
    IC._font()
    fig, ax = plt.subplots(figsize=(8.8, 5.0))
    rows = [h for h in B.HOLDINGS if h["sleeve"] != "CASH"]
    names = [f"{h['name']}  {h['action']}" for h in rows][::-1]
    w = [h["weight"] for h in rows][::-1]
    colors = []
    for h in rows[::-1]:
        colors.append(
            GOLD if h["action"].startswith("BUY") else
            TEAL if h["action"] == "HOLD" else
            AMBER if h["action"] == "WATCH" else
            NAVY2
        )
    ax.barh(names, w, color=colors, height=0.62)
    ax.set_xlabel("% of 전체 (1억)")
    fig.suptitle("종목 비중 — 금=신규매수  ·  청록=홀드  ·  남=눌림  ·  황=관망", color=NAVY, fontsize=12, x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "03_names.png")


def chart_04_newmoney() -> Path:
    IC._font()
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    rows = B.buy_order()
    ax.bar([h["name"] for h in rows], [h["weight"] for h in rows], color=[GOLD, NAVY2, TEAL, NAVY], width=0.55)
    ax.set_ylabel("% of 전체")
    for i, h in enumerate(rows):
        ax.text(i, h["weight"] + 0.15, f"{h['action']}\n{B.krw(h['weight'])//10000}만", ha="center", fontsize=9, color=NAVY)
    fig.suptitle("지금 넣는 돈 — 한금융 8% · 네이버 4.5% · 모비스 5% · 한전 3.5%", color=NAVY, fontsize=12, x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "04_newmoney.png")


def chart_05_actions() -> Path:
    IC._font()
    fig, ax = plt.subplots(figsize=(8.8, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.axis("off")
    cards = [
        (0.25, GREEN, "HOLD", "삼성 10 · 닉스 8\n스퀘어 4", "더 넣지 않는다"),
        (2.6, GOLD, "BUY", "한금융 8 · 네이버 4.5\n모비스 5 · 한전 3.5", "빈 돈은 여기만"),
        (4.95, NAVY2, "DIP", "삼전전 · 이수 · KB\n신한 · 항공", "눌림만"),
        (7.3, AMBER, "WATCH/OUT", "두산 1 · 한미 0\n레인보우 0", "추격 금지"),
    ]
    for x, col, t, body, foot in cards:
        ax.add_patch(FancyBboxPatch((x, 0.35), 2.2, 3.2, boxstyle="round,pad=0.03,rounding_size=0.12",
                                    facecolor=LIGHT, edgecolor=col, lw=1.6))
        ax.text(x + 1.1, 3.1, t, ha="center", fontsize=13, color=col)
        ax.text(x + 1.1, 2.05, body, ha="center", fontsize=9, color=NAVY)
        ax.text(x + 1.1, 0.75, foot, ha="center", fontsize=9, color=GRAY)
    fig.suptitle("실행 카드 — 사지 않을 자리가 절반이다", color=NAVY, fontsize=12, x=0.02, ha="left")
    return _save(fig, "05_actions.png")


def chart_06_cashflow() -> Path:
    IC._font()
    fig, ax = plt.subplots(figsize=(8.6, 3.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    nodes = [("1억", NAVY), ("현금 4,000만", TEAL), ("주식 6,000만", NAVY2), ("신규 2,100만", GOLD)]
    for i, (t, c) in enumerate(nodes):
        x = 0.35 + i * 2.4
        ax.add_patch(FancyBboxPatch((x, 1.05), 2.05, 1.15, boxstyle="round,pad=0.03,rounding_size=0.1",
                                    facecolor=LIGHT, edgecolor=c, lw=1.4))
        ax.text(x + 1.02, 1.62, t, ha="center", va="center", fontsize=12, color=NAVY)
        if i:
            ax.annotate("", xy=(x, 1.62), xytext=(x - 0.32, 1.62),
                        arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
    ax.text(5, 0.35, "신규 2,100만 = 한금융 800 + 네이버 450 + 모비스 500 + 한전 350",
            ha="center", fontsize=9, color=GRAY)
    fig.suptitle("1억을 지금 넣는다면", color=NAVY, fontsize=12, x=0.02, ha="left")
    return _save(fig, "06_flow.png")


CHARTS = [chart_01_pie, chart_02_bookc, chart_03_names, chart_04_newmoney, chart_05_actions, chart_06_cashflow]


def render_all() -> list[Path]:
    IC._font()
    return [fn() for fn in CHARTS]


if __name__ == "__main__":
    for p in render_all():
        print(p, p.stat().st_size)
