#!/usr/bin/env python3
"""8월 24일 투자판단 검증 차트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUT_DIR = Path("/workspace/lectures/charts")

NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GRAY = "#4B5563"
GREEN = "#166534"
RED = "#991B1B"
AMBER = "#B45309"
BLUE = "#2563EB"
TEAL = "#0F766E"
LIGHT = "#EEF2F8"


def _font():
    path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    fm.fontManager.addfont(path)
    name = fm.FontProperties(fname=path).get_name()
    plt.rcParams.update(
        {
            "font.family": name,
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#D0D7E2",
            "axes.labelcolor": NAVY,
            "xtick.color": GRAY,
            "ytick.color": GRAY,
            "text.color": NAVY,
            "axes.titleweight": "bold",
        }
    )
    return name


def memory_export_decomposition():
    _font()
    categories = ["수출액 MoM", "kg당 통관단가 MoM", "역산 수출중량 MoM"]
    dram = [-51.4, -36.1, -23.9]
    mcp = [4.6, 10.8, -5.6]

    x = np.arange(len(categories))
    width = 0.36

    fig, ax = plt.subplots(figsize=(11.2, 5.6), dpi=180)
    b1 = ax.bar(x - width / 2, dram, width, color=NAVY, label="DRAM 모듈", zorder=3)
    b2 = ax.bar(x + width / 2, mcp, width, color=GOLD, label="MCP (HBM 포함)", zorder=3)

    ax.axhline(0, color="#94A3B8", linewidth=0.8, zorder=2)
    ax.set_xticks(x)
    ax.set_xticklabels(categories, fontsize=11)
    ax.set_ylabel("전월 대비 증감률 (%)", fontsize=10)
    ax.set_title(
        "8월 1~20일 월간 환산치 분해  ·  수출액 = 통관단가 × 중량",
        fontsize=14,
        pad=12,
        color=NAVY,
    )
    ax.legend(frameon=False, loc="upper right", fontsize=10)
    ax.set_ylim(-62, 22)
    ax.yaxis.grid(True, linestyle="--", linewidth=0.6, color="#E2E8F0", zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    def label(bars):
        for bar in bars:
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                h + (1.4 if h >= 0 else -3.2),
                f"{h:+.1f}%",
                ha="center",
                va="bottom" if h >= 0 else "top",
                fontsize=9.5,
                fontweight="bold",
                color=NAVY if h >= 0 else RED,
            )

    label(b1)
    label(b2)

    ax.text(
        0.0,
        -0.18,
        "역산 중량 = (1+수출액증감)÷(1+kg당단가증감) − 1   ·   "
        "DRAM 0.486/0.639−1 = −23.9%   ·   MCP 1.046/1.108−1 = −5.6%\n"
        "ASP는 DIMM·HBM 개별 가격이 아니라 USD/kg 통관단가. 8/20 기준 13/20 조업일 환산 중간 추정치.",
        transform=ax.transAxes,
        fontsize=8.2,
        color=GRAY,
        ha="left",
        va="top",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    out = OUT_DIR / "20260824_memory_export_decomposition.png"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def ai_ads_comparison():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.5), dpi=180)

    # left: rates
    ax = axes[0]
    labels = ["광고 노출률", "광고주 도메인\n출처 중복", "동일 URL\n출처 중복"]
    google = [29.45, 11.53, 1.95]
    chatgpt = [25.94, 3.63, 0.09]
    x = np.arange(len(labels))
    w = 0.36
    ax.bar(x - w / 2, google, w, color=NAVY2, label="Google AI Mode", zorder=3)
    ax.bar(x + w / 2, chatgpt, w, color=TEAL, label="ChatGPT (Free·Go)", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("%", fontsize=10)
    ax.set_title("상업성 표본에서의 광고 지표", fontsize=13, color=NAVY, pad=10)
    ax.set_ylim(0, 36)
    ax.legend(frameon=False, fontsize=9)
    ax.yaxis.grid(True, linestyle="--", linewidth=0.6, color="#E2E8F0")
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for i, (g, c) in enumerate(zip(google, chatgpt)):
        ax.text(i - w / 2, g + 0.6, f"{g:.2f}", ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
        ax.text(i + w / 2, c + 0.6, f"{c:.2f}", ha="center", fontsize=8.5, color=TEAL, fontweight="bold")

    # right: CPC buckets (Google only) + caveats
    ax = axes[1]
    buckets = ["2달러 미만", "2~10달러", "10달러 이상"]
    rates = [24.33, 32.45, 53.56]
    colors = ["#93C5FD", "#3B82F6", NAVY]
    bars = ax.bar(buckets, rates, color=colors, zorder=3)
    ax.set_title("AI Mode 광고 노출률 × CPC 구간", fontsize=13, color=NAVY, pad=10)
    ax.set_ylabel("%", fontsize=10)
    ax.set_ylim(0, 66)
    ax.yaxis.grid(True, linestyle="--", linewidth=0.6, color="#E2E8F0")
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for bar, v in zip(bars, rates):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            v + 1.4,
            f"{v:.2f}%",
            ha="center",
            fontsize=9.5,
            fontweight="bold",
            color=NAVY,
        )
    ax.text(
        0.5,
        -0.22,
        "상관관계이지 인과가 아님.\n상업성·경쟁이 강한 키워드일수록\nCPC와 노출률이 함께 높다.",
        transform=ax.transAxes,
        ha="center",
        fontsize=8.5,
        color=GRAY,
    )

    fig.suptitle(
        "Google 29.45% · ChatGPT 25.94%는 전체 검색·대화가 아니라 미국 상업성 표본",
        fontsize=13.5,
        color=NAVY,
        y=1.02,
    )
    fig.text(
        0.5,
        -0.02,
        "Google: 미국 상업성 키워드 50,032개 (2026-06-30)  ·  ChatGPT: 동일 계열 프롬프트 50,006개, Free·Go, 2026-07-23  ·  SE Ranking",
        ha="center",
        fontsize=8,
        color=GRAY,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.96))
    out = OUT_DIR / "20260824_ai_ads_comparison.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def six_fixes_card():
    _font()
    fig, ax = plt.subplots(figsize=(11.2, 6.4), dpi=180)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("배포 전 반드시 고칠 여섯 가지", fontsize=16, color=NAVY, pad=8, loc="left")

    items = [
        ("1  마이크론 150%", "산업 전체 수요가 공급보다 50% 많음이 아님.\n확약 가능 물량 대비 데이터센터 요구량이 약 1.5배."),
        ("2  MCP ≠ HBM ≠ DDR5", "MCP는 패키지·통관 분류. HBM은 그 안의 한 제품.\nDDR5는 세대 규격. 같은 층위가 아님."),
        ("3  NVIDIA 15%", "GPU ASP가 아니라 AI 칩 탑재 서버 시스템 가격.\nBloomberg 인용, NVIDIA 공식 확인 없음."),
        ("4  광고 노출률 분모", "29.45%·25.94%는 미국 상업성 표본.\n전체 검색·전체 ChatGPT 이용량이 아님."),
        ("5  OpenAI 3~5달러", "실제 지불 CPC가 아니라 권장 최대 CPC 입찰가.\n2순위 경매라 실효 CPC는 더 낮을 수 있음."),
        ("6  SDD 90% 경량화", "중국산 대비 90% 가벼움이 아님.\n중국 제품 무게의 약 90% = 약 10% 경량화."),
    ]
    positions = [(0.2, 6.55), (5.15, 6.55), (0.2, 3.55), (5.15, 3.55), (0.2, 0.55), (5.15, 0.55)]
    for (x, y), (title, body) in zip(positions, items):
        box = FancyBboxPatch(
            (x, y),
            4.65,
            2.7,
            boxstyle="round,pad=0.04,rounding_size=0.12",
            linewidth=1.0,
            edgecolor="#D0D7E2",
            facecolor=LIGHT,
        )
        ax.add_patch(box)
        ax.text(x + 0.2, y + 2.15, title, fontsize=11.5, fontweight="bold", color=NAVY, va="top")
        ax.text(x + 0.2, y + 1.55, body, fontsize=9.4, color=GRAY, va="top", linespacing=1.35)

    out = OUT_DIR / "20260824_six_must_fix.png"
    fig.savefig(out, bbox_inches="tight")
    plt.close(fig)
    return out


def main():
    paths = [memory_export_decomposition(), ai_ads_comparison(), six_fixes_card()]
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
