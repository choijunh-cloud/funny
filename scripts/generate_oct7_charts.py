#!/usr/bin/env python3
"""10월 7일 브리프용 차트 생성."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np

OUT = Path("/workspace/reports/charts")
OUT.mkdir(parents=True, exist_ok=True)

NAVY = "#0f2043"
NAVY2 = "#1e407c"
GOLD = "#b8943a"
GREEN = "#166534"
RED = "#991b1b"
GRAY = "#4b5563"
LINE = "#d5dce6"
BG = "#f4f6fb"

_KR_FONT = "DejaVu Sans"
for _path in (
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
):
    if Path(_path).exists():
        font_manager.fontManager.addfont(_path)
        _KR_FONT = font_manager.FontProperties(fname=_path).get_name()
        break
print(f"[charts] font={_KR_FONT}")


def _style():
    plt.rcParams.update(
        {
            "font.family": _KR_FONT,
            "axes.unicode_minus": False,
            "axes.facecolor": "white",
            "figure.facecolor": BG,
            "axes.edgecolor": LINE,
            "axes.labelcolor": NAVY,
            "xtick.color": GRAY,
            "ytick.color": GRAY,
            "text.color": NAVY,
            "axes.titleweight": "bold",
        }
    )


def chart_cpu_tam():
    _style()
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    years = [2025, 2026, 2030]
    citi_may = [29.3, None, 131.5]
    citi_oct = [29.0, 46.4, 300.0]  # 46.4 = 60% CAGR reverse (labeled)
    mizuho = [25.9, None, 209.0]

    ax.plot([2025, 2030], [29.3, 131.5], "o--", color="#94a3b8", lw=2, label="Citi May → $131.5B")
    ax.plot([2025, 2026, 2030], [29.0, 46.4, 300.0], "o-", color=NAVY2, lw=2.5, label="Citi Oct → $300B")
    ax.plot([2025, 2030], [25.9, 209.0], "s-", color=GOLD, lw=2.5, label="Mizuho → $209B")
    ax.annotate(
        "2026E ~$46B\n(60% CAGR 역산, 비공시)",
        xy=(2026, 46.4),
        xytext=(2026.35, 95),
        fontsize=9,
        color=GRAY,
        arrowprops=dict(arrowstyle="->", color=GRAY),
    )
    ax.set_ylabel("Server CPU TAM ($B)")
    ax.set_title("Agentic AI 이후 서버 CPU TAM 상향")
    ax.set_xticks(years)
    ax.set_ylim(0, 340)
    ax.legend(loc="upper left", frameon=False)
    ax.grid(axis="y", color=LINE, lw=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "01_cpu_tam.png", dpi=160)
    plt.close(fig)


def chart_memory_per():
    _style()
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    names = ["Sandisk\nFY27", "Micron\nFY27", "Micron\nCY27", "SKH ADR\n27Y", "SKH 본주\n27Y", "삼성\n27Y"]
    pers = [7.2, 6.3, 5.8, 5.5, 4.0, 4.0]
    colors = [NAVY2, NAVY2, NAVY2, GOLD, GREEN, GREEN]
    bars = ax.bar(names, pers, color=colors, width=0.62)
    ax.axhline(7.0, color=RED, ls="--", lw=1.2, label="보수 시나리오 PER ~7x")
    ax.set_ylabel("PER (x)")
    ax.set_title("메모리 밸류에이션 (10/6 종가)")
    ax.set_ylim(0, 9)
    for b, v in zip(bars, pers):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.15, f"{v:.1f}x", ha="center", fontsize=10, fontweight="bold")
    ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", color=LINE, lw=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "02_memory_per.png", dpi=160)
    plt.close(fig)


def chart_muse_ram():
    _style()
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    stages = ["현재", "고도화", "복잡 Agent"]
    allocated = [8, 16, 32]
    used_lo = [3, 6, 10]
    used_hi = [3, 10, 20]
    x = np.arange(len(stages))
    ax.bar(x - 0.18, allocated, width=0.34, color="#94a3b8", label="할당 (GB)")
    ax.bar(x + 0.18, used_lo, width=0.34, color=NAVY2, label="실제 사용 하단 (GB)")
    ax.errorbar(
        x + 0.18,
        [(a + b) / 2 for a, b in zip(used_lo, used_hi)],
        yerr=[(b - a) / 2 for a, b in zip(used_lo, used_hi)],
        fmt="none",
        ecolor=GOLD,
        elinewidth=2,
        capsize=5,
        label="사용 범위",
    )
    ax.set_xticks(x)
    ax.set_xticklabels(stages)
    ax.set_ylabel("GB / Agent VM")
    ax.set_title("Muse VM DRAM: 할당 vs 실제 사용 경로")
    ax.legend(frameon=False, loc="upper left")
    ax.grid(axis="y", color=LINE, lw=0.8)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "03_muse_ram.png", dpi=160)
    plt.close(fig)


def chart_verdicts():
    _style()
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    labels = [
        "경제성 분석",
        "중국≠가격만큼 쌈",
        "미국이 전반 쌈",
        "기업지출 비폭증",
        "→CapEx 과도",
    ]
    scores = [3, 3, 2, 2, 1]  # 3 ok, 2 partial, 1 bad
    colors = [GREEN, GREEN, GOLD, GOLD, RED]
    ax.barh(labels[::-1], scores[::-1], color=colors[::-1], height=0.55)
    ax.set_xlim(0, 3.5)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["비약", "부분타당", "타당"])
    ax.set_title("중국 AI 저가 논쟁 — 주장별 판정")
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUT / "04_china_ai_verdicts.png", dpi=160)
    plt.close(fig)


def chart_flow():
    _style()
    fig, ax = plt.subplots(figsize=(8.4, 2.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 2)
    ax.axis("off")
    boxes = [
        (0.3, "Agentic AI"),
        (2.3, "Inference↑"),
        (4.3, "GPU+CPU"),
        (6.3, "DRAM/HBM\nNAND"),
        (8.3, "후공정\nCoWoS·EMIB"),
    ]
    for x, t in boxes:
        fancy = mpatches.FancyBboxPatch(
            (x, 0.55),
            1.6,
            1.0,
            boxstyle="round,pad=0.04,rounding_size=0.15",
            facecolor=NAVY,
            edgecolor=NAVY,
        )
        ax.add_patch(fancy)
        ax.text(x + 0.8, 1.05, t, ha="center", va="center", color="white", fontsize=10, fontweight="bold")
    for x in (1.95, 3.95, 5.95, 7.95):
        ax.annotate("", xy=(x + 0.3, 1.05), xytext=(x, 1.05), arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
    ax.set_title("투자 연결고리", loc="left", fontsize=12, color=NAVY, pad=8)
    fig.tight_layout()
    fig.savefig(OUT / "05_investment_flow.png", dpi=160)
    plt.close(fig)


def main():
    chart_cpu_tam()
    chart_memory_per()
    chart_muse_ram()
    chart_verdicts()
    chart_flow()
    print("wrote", sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
