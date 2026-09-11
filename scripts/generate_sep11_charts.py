#!/usr/bin/env python3
"""9월 11일 한 장용 차트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager

import sep11_data as D

OUT = Path("/workspace/reports/charts_sep11")
OUT.mkdir(parents=True, exist_ok=True)
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
font_manager.fontManager.addfont(FONT)
plt.rcParams.update({
    "font.family": "WenQuanYi Micro Hei",
    "axes.unicode_minus": False,
    "figure.facecolor": "#f4f6fb",
    "axes.facecolor": "#ffffff",
    "axes.edgecolor": "#d5dce6",
    "axes.titleweight": "bold",
})
NAVY, NAVY2, GOLD, GREEN, RED, GRAY = "#0f2043", "#1e407c", "#b8943a", "#166534", "#991b1b", "#6b7280"


def _save(fig, name):
    fig.tight_layout()
    p = OUT / name
    fig.savefig(p, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("wrote", p)


def chart_oracle():
    fig, ax = plt.subplots(figsize=(7.6, 3.6))
    labs = ["RPO\n$B", "신규 AI계약\n$B", "FY27 Capex\n$B", "순현금 Capex\n상한 $B", "고객 선급/BYOH\n$B"]
    vals = [664, 30, 92.5, 70, 22.5]
    colors = [NAVY, NAVY2, GOLD, GREEN, GRAY]
    bars = ax.bar(labs, vals, color=colors, width=0.62)
    texts = ["664", "30", "90~95", "≤70", "20~25"]
    for b, t in zip(bars, texts):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 8, t,
                ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax.set_ylim(0, 780)
    ax.set_title("Oracle — RPO는 쌓이고, 신규 계약은 자기 돈으로 안 짓는다")
    _save(fig, "01_oracle.png")


def chart_export():
    fig, ax = plt.subplots(figsize=(7.8, 3.7))
    names = ["메모리", "DRAM", "Flash", "MCP", "DRAM모듈"]
    yoy = [D.MEM_YOY, D.DRAM_YOY, D.FLASH_YOY, D.MCP_YOY, D.MOD_YOY]
    asp = [D.MEM_ASP_MOM, D.DRAM_ASP_MOM, D.FLASH_ASP_MOM, D.MCP_ASP_MOM, D.MOD_ASP_MOM]
    x = range(len(names))
    w = 0.38
    ax.bar([i - w / 2 for i in x], yoy, w, color=NAVY, label="수출액 YoY %")
    ax.bar([i + w / 2 for i in x], asp, w, color=GOLD, label="단가 MoM %")
    ax.axhline(0, color=NAVY, lw=0.8)
    ax.set_xticks(list(x))
    ax.set_xticklabels(names)
    ax.set_title("9월 1~10일 메모리 — 금액은 폭발, DRAM 단가 MoM은 첫 균열")
    ax.legend(frameon=False, fontsize=9)
    _save(fig, "02_export.png")


def chart_ust():
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.bar(["30Y 입찰\n수요", "바이백\n집행"], [100, 51.87 / 60 * 100], color=[GREEN, GOLD], width=0.5)
    ax.text(0, 104, "Indirect 79.5%\n고점 5.308%", ha="center", fontsize=10, color=NAVY)
    ax.text(1, 90, "51.9 / 60억$\n가격이 비싸다", ha="center", fontsize=10, color=NAVY)
    ax.set_ylim(0, 130)
    ax.set_ylabel("%")
    ax.set_title("국채 — 수요 붕괴가 아니라 5.3%에서의 가격 싸움. 다음 시험대 9/24")
    _save(fig, "03_ust.png")


def chart_mlcc():
    fig, ax = plt.subplots(figsize=(7.6, 3.3))
    ax.axis("off")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4)
    ax.set_title("같은 MLCC라도 자리가 다르다", loc="left")
    ax.text(2.4, 2.7, "삼성전기", ha="center", fontsize=13, fontweight="bold", color=NAVY)
    ax.text(2.4, 1.5, "GPU↑ → 전력↑\n고용량·고압 MLCC\n서버 전기 안정화", ha="center", fontsize=11, color=NAVY)
    ax.add_patch(plt.Rectangle((0.4, 0.6), 4.0, 2.7, fill=False, edgecolor=NAVY, lw=2, zorder=0))
    ax.text(7.5, 2.7, "아모텍", ha="center", fontsize=13, fontweight="bold", color="#7a5c12")
    ax.text(7.5, 1.5, "800G/1.6T → BBC\n신호 무결성\n고객 진입 후 고압 교차판매", ha="center", fontsize=11)
    ax.add_patch(plt.Rectangle((5.5, 0.6), 4.0, 2.7, fill=False, edgecolor=GOLD, lw=2, zorder=0))
    _save(fig, "04_mlcc.png")


def main():
    chart_oracle()
    chart_export()
    chart_ust()
    chart_mlcc()
    print("charts ok")


if __name__ == "__main__":
    main()
