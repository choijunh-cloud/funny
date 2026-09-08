#!/usr/bin/env python3
"""9월 8일 브리프용 차트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

import sep08_data as D

OUT = Path("/workspace/reports/charts")
OUT.mkdir(parents=True, exist_ok=True)

FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
font_manager.fontManager.addfont(FONT)
plt.rcParams.update(
    {
        "font.family": "WenQuanYi Micro Hei",
        "axes.unicode_minus": False,
        "figure.facecolor": "#f4f6fb",
        "axes.facecolor": "#ffffff",
        "axes.edgecolor": "#d5dce6",
        "axes.labelcolor": "#0f2043",
        "text.color": "#1a1a1a",
        "xtick.color": "#4b5563",
        "ytick.color": "#4b5563",
        "axes.titleweight": "bold",
    }
)

NAVY = "#0f2043"
NAVY2 = "#1e407c"
GOLD = "#b8943a"
GREEN = "#166534"
RED = "#991b1b"
AMBER = "#b45309"
BLUE = "#2563eb"
GRAY = "#6b7280"


def _save(fig, name: str) -> None:
    fig.tight_layout()
    path = OUT / name
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print("wrote", path)


def chart_dram_vendors() -> None:
    names = [v[0] for v in D.DRAM_VENDORS_2Q26]
    revs = [v[1] for v in D.DRAM_VENDORS_2Q26]
    qoq = [v[3] for v in D.DRAM_VENDORS_2Q26]
    colors = [NAVY, NAVY2, GOLD, BLUE, GRAY, "#94a3b8"]
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    bars = ax.barh(names[::-1], revs[::-1], color=colors[::-1], height=0.62)
    for bar, r, q in zip(bars, revs[::-1], qoq[::-1]):
        ax.text(
            bar.get_width() + 0.6,
            bar.get_y() + bar.get_height() / 2,
            f"${r:.1f}B  +{q:.1f}%",
            va="center",
            fontsize=10,
            color=NAVY,
            fontweight="bold",
        )
    ax.set_xlim(0, 78)
    ax.set_xlabel("2Q26 매출 ($B)")
    ax.set_title(f"DRAM 2Q26 매출 ${D.DRAM_2Q26_REVENUE_B}B  ·  QoQ +{D.DRAM_2Q26_QOQ_PCT}%")
    ax.axvline(0, color=NAVY, lw=0.6)
    _save(fig, "01_dram_2q26.png")


def chart_iphone_bom() -> None:
    xs = ["초기 256GB Pro", "2026 3Q 추정", "2027 상반기"]
    ys = [D.IPHONE18_MEM_BOM_START_PCT, D.IPHONE18_MEM_BOM_PCT, D.IPHONE18_MEM_BOM_1H27_PCT]
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    ax.plot(xs, ys, color=NAVY, lw=2.6, marker="o", ms=10, markerfacecolor=GOLD)
    for x, y in zip(xs, ys):
        ax.text(x, y + 2.2, f"{y}%", ha="center", fontsize=13, fontweight="bold", color=NAVY)
    ax.set_ylim(0, 52)
    ax.set_ylabel("아이폰 BOM 중 메모리 비중")
    ax.set_title("아이폰 메모리 BOM 잠식  ·  TrendForce/업계 추정")
    ax.axhline(10, color=GRAY, ls="--", lw=0.8, alpha=0.5)
    _save(fig, "02_iphone_bom.png")


def chart_buyback() -> None:
    labels = ["SK하이닉스", "삼성전자"]
    # 만주 = 10,000 shares. 0.65 million shares = 65만주
    now = [D.HYNIX_BUYBACK_DAILY_NOW_M * 100, D.SAMSUNG_BUYBACK_DAILY_NOW_M * 100]
    mx = [D.HYNIX_BUYBACK_DAILY_MAX_M * 100, D.SAMSUNG_BUYBACK_DAILY_MAX_M * 100]
    fig, ax = plt.subplots(figsize=(8.6, 4.5))
    x = range(len(labels))
    w = 0.36
    ax.bar([i - w / 2 for i in x], now, w, color=NAVY2, label="현재 신청 물량")
    ax.bar([i + w / 2 for i in x], mx, w, color=GOLD, label="1일 법적 주문 한도")
    now_lab = ["65만", "200만"]
    max_lab = ["240.7만", "732.2만"]
    for i, (n, m, nl, ml) in enumerate(zip(now, mx, now_lab, max_lab)):
        ax.text(i - w / 2, n + 12, nl, ha="center", fontsize=10, color=NAVY)
        ax.text(i + w / 2, m + 12, ml, ha="center", fontsize=10, color=NAVY)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("만주 / 일")
    ax.set_title("자사주 일일 주문 — 현재는 한도의 약 27%")
    ax.legend(frameon=False, loc="upper left")
    ax.set_ylim(0, 860)
    _save(fig, "03_buyback_headroom.png")


def chart_etf() -> None:
    names = [
        "SK하이닉스",
        "삼성전자",
        "한미반도체",
        "주성엔지니어링",
        "테스",
    ]
    # 조원
    vals = [-1.345, -0.22, 0.30, 0.18, 0.14]
    colors = [RED if v < 0 else GREEN for v in vals]
    fig, ax = plt.subplots(figsize=(8.8, 4.6))
    bars = ax.barh(names[::-1], vals[::-1], color=colors[::-1], height=0.58)
    labels_v = ["−1.24~1.45조", "−0.20~0.24조", "+3,000억", "+1,800억", "+1,400억"]
    for bar, lab, v in zip(bars, labels_v[::-1], vals[::-1]):
        pad = 0.06 if v > 0 else -0.06
        ax.text(
            bar.get_width() + pad,
            bar.get_y() + bar.get_height() / 2,
            lab,
            va="center",
            ha="left" if v > 0 else "right",
            fontsize=10,
            fontweight="bold",
        )
    ax.axvline(0, color=NAVY, lw=1)
    ax.set_xlabel("추정 대금 (조원)")
    ax.set_title("9/10 KRX 반도체 ETF 리밸런싱  ·  기계적 매도, 펀더멘탈 무관")
    ax.set_xlim(-2.1, 0.85)
    _save(fig, "04_etf_rebal.png")


def chart_astra() -> None:
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    cats = ["업무당 토큰\n(상대)", "1인 업무량\n(상대)", "1인 inference\n(상대)", "사용자 수\n(상대)", "전체 inference\n(상대)"]
    sol = [1.0, 1.0, 1.0, 1.0, 1.0]
    astra = [0.7, 3.0, 2.1, 2.0, 4.2]
    x = range(len(cats))
    w = 0.36
    ax.bar([i - w / 2 for i in x], sol, w, color="#94a3b8", label="Chatbot/Sol 가정")
    ax.bar([i + w / 2 for i in x], astra, w, color=NAVY, label="Agent/Astra 가정")
    ax.set_xticks(list(x))
    ax.set_xticklabels(cats)
    ax.set_title("Astra 역설  ·  토큰 효율↑ 이어도 총 inference는 늘 수 있다")
    ax.legend(frameon=False)
    ax.set_ylabel("배율 (Sol=1)")
    ax.axhline(1, color=GRAY, ls="--", lw=0.8)
    _save(fig, "05_astra_paradox.png")


def chart_memory_per() -> None:
    names = ["마이크론\nCY27", "샌디스크\nFY27", "하이닉스 ADR\n27E", "하이닉스 본주\n27E", "삼성전자\n27E"]
    pers = [D.MU_CY27_PER, D.SNDK_FY27_PER, D.HYNIX_ADR_PER_27, D.HYNIX_27_PER, D.SAMSUNG_27_PER]
    colors = [GOLD, GOLD, NAVY2, NAVY, NAVY]
    fig, ax = plt.subplots(figsize=(8.8, 4.5))
    bars = ax.bar(names, pers, color=colors, width=0.62)
    for b, p in zip(bars, pers):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.15, f"{p}배",
                ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax.axhspan(4, 8, color=GOLD, alpha=0.12)
    ax.text(4.15, 7.55, "과거 사이클 PER 4~8배 밴드", fontsize=9, color=AMBER, ha="right")
    ax.set_ylim(0, 10.5)
    ax.set_ylabel("Forward PER")
    ax.set_title("메모리 밸류 (9/4 종가)  ·  본주가 ADR보다 더 싸 보인다")
    _save(fig, "06_memory_per.png")


def chart_chain() -> None:
    fig, ax = plt.subplots(figsize=(9.4, 3.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    boxes = [
        (0.2, "모델\nAstra"),
        (1.85, "컴퓨팅\nArm/GPU"),
        (3.5, "메모리\nHBM·DRAM\nNAND"),
        (5.2, "인식 SW\n스트라드비전"),
        (6.9, "액추에이터\n로보티즈"),
        (8.5, "현장\nSDS·Unitree"),
    ]
    ax.set_title("Physical AI 밸류체인  ·  로봇 한 종목이 아니다", loc="left", fontsize=13, pad=8)
    for i, (x, t) in enumerate(boxes):
        ax.add_patch(
            FancyBboxPatch((x, 0.85), 1.45, 1.35, boxstyle="round,pad=0.04,rounding_size=0.15",
                           facecolor=NAVY if i % 2 == 0 else NAVY2, edgecolor="none")
        )
        ax.text(x + 0.72, 1.52, t, ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        if i < len(boxes) - 1:
            ax.annotate("", xy=(x + 1.55, 1.52), xytext=(x + 1.45, 1.52),
                        arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
    ax.text(5, 0.28, "Arm RL0→RL5 = 자동차 SAE 레벨의 로봇판 공통언어", ha="center", color=AMBER, fontsize=10)
    _save(fig, "07_physical_ai_chain.png")


def chart_dc_vs_other() -> None:
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    labels = ["미국 DC 건설\n2021→2026", "기타 민간건설\n(주택·몰·오피스)"]
    vals = [717, -1]  # qualitative; comments: DC +717% since 2021, other private -1200억 달러
    # Better: two callout bars for yoy
    cats = ["DC 건설 YoY", "6월 DC YoY", "7월 DC SAAR"]
    ys = [57.2, 46, 75.2]
    colors = [NAVY, NAVY2, GOLD]
    bars = ax.bar(cats, ys, color=colors, width=0.55)
    texts = ["+57.2%", "+46%", "$75.2B"]
    for b, t in zip(bars, texts):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, t,
                ha="center", fontsize=12, fontweight="bold", color=NAVY)
    ax.set_ylim(0, 95)
    ax.set_title("미국 데이터센터 건설  ·  7월 SAAR 사상 최고")
    ax.set_ylabel("% 또는 $B")
    _save(fig, "08_us_dc.png")


def main() -> None:
    chart_dram_vendors()
    chart_iphone_bom()
    chart_buyback()
    chart_etf()
    chart_astra()
    chart_memory_per()
    chart_chain()
    chart_dc_vs_other()
    print("charts ok")


if __name__ == "__main__":
    main()
