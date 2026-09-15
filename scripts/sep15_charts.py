#!/usr/bin/env python3
"""9월 중순 통합브리핑용 차트 PNG 생성."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUT = Path("/workspace/lectures/assets/sep15")
FONT = "WenQuanYi Micro Hei"

NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
TEAL = "#0F766E"
RED = "#B91C1C"
GREEN = "#15803D"
AMBER = "#B45309"
GRAY = "#64748B"
BLUE = "#2563EB"
PURPLE = "#6D28D9"
LIGHT = "#EEF2F8"


def setup():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": FONT,
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.edgecolor": "#D0D7E2",
            "axes.labelcolor": NAVY,
            "xtick.color": "#334155",
            "ytick.color": "#334155",
            "text.color": NAVY,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "figure.dpi": 140,
        }
    )


def save(fig, name: str):
    path = OUT / name
    fig.savefig(path, bbox_inches="tight", pad_inches=0.28)
    plt.close(fig)
    return path


def chart_july_sep_returns():
    labels = [
        "샌디스크",
        "SK하이닉스 ADR",
        "삼성전기",
        "마벨",
        "마이크론",
        "오라클",
        "KOSDAQ",
        "엔비디아",
        "애플",
        "SOX",
        "KOSPI",
        "SK하이닉스 본주",
        "삼성전자",
        "현대차",
        "알파벳",
        "브로드컴",
    ]
    vals = [34.5, 32.2, 22.6, 19.5, 18.5, 15.6, 14.0, 8.7, 7.6, 4.5, 4.8, 5.5, -1.1, -1.4, -5.0, -7.0]
    colors = [GREEN if v >= 0 else RED for v in vals]
    fig, ax = plt.subplots(figsize=(10.4, 6.2))
    y = np.arange(len(labels))
    ax.barh(y, vals, color=colors, height=0.72, zorder=3)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.axvline(0, color=NAVY, lw=0.8)
    ax.set_xlabel("7/31 → 9/1 변동률 (%)")
    ax.set_title("7월 말 대비 9월 1일 — 금리·유가 악재에도 메모리/AI가 이김")
    ax.grid(axis="x", color=LIGHT, zorder=0)
    for i, v in enumerate(vals):
        ax.text(v + (0.4 if v >= 0 else -0.4), i, f"{v:+.1f}%", va="center",
                ha="left" if v >= 0 else "right", fontsize=8, color=NAVY)
    ax.set_xlim(-12, 42)
    fig.text(0.01, -0.02, "자료: 강의노트 「7월 말 대비 달라진 것」「Where is market headed」(9/1 vs 7/31)", fontsize=8, color=GRAY)
    return save(fig, "01_july_sep_returns.png")


def chart_macro_shock():
    labels = ["WTI", "美 2년물", "美 10년물", "美 30년물"]
    vals = [18.8, 7.9, 4.8, 1.5]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    bars = ax.bar(labels, vals, color=[RED, AMBER, GOLD, NAVY2], width=0.62, zorder=3)
    ax.set_title("같은 기간 매크로 악재 (7/31 → 9/1)")
    ax.set_ylabel("변동률 (%)")
    ax.grid(axis="y", color=LIGHT, zorder=0)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.25, f"+{v}%", ha="center", fontsize=10, color=NAVY, fontweight="bold")
    fig.text(0.01, -0.04, "유가 +18.8%, 2년물 +7.9%, 10년물 +4.8%에도 메모리 상승", fontsize=8, color=GRAY)
    return save(fig, "02_macro_shock.png")


def chart_memory_per():
    names = ["Sandisk\nFY27", "Micron\nCY27", "SK Hynix ADR\n27E", "SK Hynix 본주\n27E*", "삼성전자\n27E*"]
    sep11 = [8.1, 6.5, 5.8, 4.6, 4.2]
    sep14 = [7.7, 6.2, 5.4, 4.3, 4.2]
    x = np.arange(len(names))
    w = 0.36
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    b1 = ax.bar(x - w / 2, sep11, w, label="9/11", color=NAVY2, zorder=3)
    b2 = ax.bar(x + w / 2, sep14, w, label="9/14 (속도조절 이후)", color=GOLD, zorder=3)
    ax.set_xticks(x, names)
    ax.set_ylabel("Forward PER (배)")
    ax.set_title("메모리 밸류에이션 — 9/11 vs 9/14")
    ax.legend(frameon=False)
    ax.grid(axis="y", color=LIGHT, zorder=0)
    ax.set_ylim(0, 10)
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.15,
                    f"{b.get_height():.1f}", ha="center", fontsize=8, color=NAVY)
    fig.text(0.01, -0.05, "*본주 27E는 환율 하향 반영 PER. 과거 마이크론 대비 할인은 -20~-50%.", fontsize=8, color=GRAY)
    return save(fig, "03_memory_per.png")


def chart_lead_times():
    items = ["ABF 기판", "HDD", "MLCC", "DRAM", "NAND eSSD", "GPU"]
    now = [52, 50, 30, 20, 16, 25]
    bal = [12, 16, 12, 8, 8, 25]
    fig, ax = plt.subplots(figsize=(9.0, 5.0))
    y = np.arange(len(items))
    ax.barh(y, now, color=RED, height=0.55, label="현재 리드타임", zorder=3)
    ax.barh(y, bal, color=NAVY2, height=0.28, label="균형 기준", zorder=4)
    ax.set_yticks(y, items)
    ax.invert_yaxis()
    ax.set_xlabel("주(weeks)")
    ax.set_title("TrendForce — AI 인프라 부품 리드타임 (9월)")
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", color=LIGHT, zorder=0)
    notes = ["Very Tight (4배)", "Very Tight", "Tight (2.5배)", "Very Tight (2.5배)", "Tight (2배)", "Balanced"]
    for i, (n, note) in enumerate(zip(now, notes)):
        ax.text(n + 0.8, i, f"{n}주 · {note}", va="center", fontsize=8, color=NAVY)
    ax.set_xlim(0, 72)
    fig.text(0.01, -0.04, "GPU만 균형. 메모리·기판·HDD·MLCC는 병목 — Token 확장을 공급이 따라가지 못함", fontsize=8, color=GRAY)
    return save(fig, "04_lead_times.png")


def chart_per_vs_yield():
    pers = [18, 19, 20, 21, 22, 23]
    ey = [5.56, 5.26, 5.00, 4.76, 4.55, 4.35]
    gap = [0.56, 0.26, 0.00, -0.24, -0.45, -0.65]
    fig, ax = plt.subplots(figsize=(8.4, 4.8))
    ax.plot(pers, ey, "o-", color=NAVY2, lw=2.2, ms=8, label="Earnings Yield")
    ax.axhline(5.0, color=RED, ls="--", lw=1.2, label="10년물 5% 가정")
    ax.set_xlabel("S&P500 Forward PER (배)")
    ax.set_ylabel("Earnings Yield (%)")
    ax.set_title("높은 금리에서 PER이 의미하는 것 — EY vs 10년물 5%")
    ax.grid(color=LIGHT)
    ax.legend(frameon=False)
    for p, e, g in zip(pers, ey, gap):
        ax.annotate(f"{g:+.2f}%p", (p, e), textcoords="offset points", xytext=(0, 8),
                    ha="center", fontsize=8, color=GREEN if g >= 0 else RED)
    fig.text(0.01, -0.05, "현재 26E PER 21배 / 27E 18.5배 (9/12). 21배면 EY 4.76%로 10년물 대비 -0.24%p", fontsize=8, color=GRAY)
    return save(fig, "05_per_vs_yield.png")


def chart_per_history():
    years = ["90초", "95", "00 IT", "07", "12", "20.2", "21", "22", "24.11", "25.10", "26.6", "현재"]
    per = [14, 15, 24.5, 15.5, 13, 19, 21.5, 17.5, 22.2, 23.1, 20.4, 20.5]
    yld = [8.0, 6.0, 6.0, 4.7, 1.85, 1.6, 1.6, 3.5, 4.3, 4.0, 4.4, 4.9]
    fig, ax1 = plt.subplots(figsize=(10.2, 5.0))
    ax2 = ax1.twinx()
    ax1.bar(years, per, color=NAVY2, alpha=0.85, label="Fwd PER")
    ax2.plot(years, yld, "o-", color=GOLD, lw=2.2, ms=6, label="10Y 금리")
    ax1.set_ylabel("S&P Forward PER (배)")
    ax2.set_ylabel("10년물 (%)")
    ax1.set_title("역사적으로 고금리 + 고PER은 공존하기 어렵다")
    ax1.set_ylim(0, 30)
    ax2.set_ylim(0, 10)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, frameon=False, loc="upper right")
    fig.text(0.01, -0.04, "현재: PER 20배대 + 10년물 4.8~5.0% = 역사적으로 상당히 이례적", fontsize=8, color=GRAY)
    return save(fig, "06_per_history.png")


def chart_apple_memory():
    labels = ["DRAM $/Gb", "NAND $/Gb"]
    q3 = [1.45, 0.26]
    q1 = [2.00, 0.33]
    x = np.arange(2)
    w = 0.34
    fig, ax = plt.subplots(figsize=(6.8, 4.6))
    ax.bar(x - w / 2, q3, w, label="3Q26 제시가", color=NAVY2)
    ax.bar(x + w / 2, q1, w, label="1Q27 제시가 (+30~40%)", color=GOLD)
    ax.set_xticks(x, labels)
    ax.set_title("삼성전자 → Apple 메모리 가격 (IThome 9/15)")
    ax.legend(frameon=False)
    ax.grid(axis="y", color=LIGHT)
    for i, (a, b) in enumerate(zip(q3, q1)):
        ax.text(i - w / 2, a + 0.04, f"${a}", ha="center", fontsize=8)
        ax.text(i + w / 2, b + 0.04, f"${b}", ha="center", fontsize=8)
    fig.text(0.01, -0.06, "iPhone 18 Pro 256GB 메모리 원가 YoY +400%, BOM 내 메모리 10%→34% (TrendForce)", fontsize=8, color=GRAY)
    return save(fig, "07_apple_memory.png")


def chart_psk_growth():
    years = ["2026E", "2027E"]
    sales = [2792, 4014]
    op = [1088, 1648]
    fig, ax = plt.subplots(figsize=(6.6, 4.6))
    x = np.arange(2)
    w = 0.34
    ax.bar(x - w / 2, sales, w, label="매출(억원)", color=NAVY2)
    ax.bar(x + w / 2, op, w, label="영업이익(억원)", color=GOLD)
    ax.set_xticks(x, years)
    ax.set_title("PSK홀딩스 — 매출 +34%/+44%, 이익이 더 빠름")
    ax.legend(frameon=False)
    ax.grid(axis="y", color=LIGHT)
    for i, (s, o) in enumerate(zip(sales, op)):
        ax.text(i - w / 2, s + 40, f"{s:,}", ha="center", fontsize=8)
        ax.text(i + w / 2, o + 40, f"{o:,}", ha="center", fontsize=8)
    fig.text(0.01, -0.05, "OPM 39%→41%. 목표주가 컨센 19.5만원 ≈ 27년 PER 15배 전후", fontsize=8, color=GRAY)
    return save(fig, "08_psk_growth.png")


def chart_doosan_tp():
    brokers = ["DS", "현재가\n(9/11)", "컨센", "NH", "SK", "메리츠", "유진"]
    tps = [4.7, 4.88, 6.3, 5.8, 7.4, 7.6, 8.0]
    colors = [GRAY, NAVY, GOLD, NAVY2, TEAL, TEAL, GREEN]
    fig, ax = plt.subplots(figsize=(8.6, 4.6))
    bars = ax.bar(brokers, tps, color=colors, zorder=3)
    ax.set_ylabel("만원")
    ax.set_title("두산퓨얼셀 목표가 분포 — 미국 DC 수주 반영 폭이 핵심")
    ax.grid(axis="y", color=LIGHT, zorder=0)
    ax.axhline(4.88, color=RED, ls=":", lw=1)
    for b, v in zip(bars, tps):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.12, f"{v}", ha="center", fontsize=9, color=NAVY)
    fig.text(0.01, -0.05, "보수 4.7만 vs 미국 AI DC 적극 반영 7~8만. 추가 수주가 7~8만을 정당화하는 조건", fontsize=8, color=GRAY)
    return save(fig, "09_doosan_tp.png")


def chart_oracle():
    labels = ["매출", "Cloud", "OCI(IaaS)", "SaaS", "RPO"]
    yoy = [30, 62, 121, 10, 46]
    fig, ax = plt.subplots(figsize=(7.6, 4.6))
    colors = [NAVY2, TEAL, GREEN, GRAY, GOLD]
    bars = ax.bar(labels, yoy, color=colors, zorder=3)
    ax.set_ylabel("YoY %")
    ax.set_title("Oracle FY27 1Q — 성장엔진이 SaaS에서 AI Cloud로 이동")
    ax.grid(axis="y", color=LIGHT, zorder=0)
    for b, v in zip(bars, yoy):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"+{v}%", ha="center", fontsize=9, fontweight="bold")
    fig.text(0.01, -0.05, "RPO $664B · Capex $28.5B · FY27 순현금 Capex $70B 이하 (선급금·BYOH $20~25B)", fontsize=8, color=GRAY)
    return save(fig, "10_oracle.png")


def chart_perp_meaning():
    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    cats = ["심리 악화\n신호", "월요일\n약세 참고", "현물 -4.35%\n예고", "HBM 펀더\n멘털 훼손", "CapEx\n축소 신호"]
    score = [4, 3, 0.4, 0.4, 0.4]
    colors = [AMBER, GOLD, GRAY, GRAY, GRAY]
    ax.bar(cats, score, color=colors, zorder=3)
    ax.set_ylim(0, 5)
    ax.set_ylabel("의미 강도 (0=없음, 5=강함)")
    ax.set_title("SK하이닉스 Perp -4.35%를 어떻게 볼 것인가")
    ax.grid(axis="y", color=LIGHT, zorder=0)
    fig.text(0.01, -0.06, "Hyperliquid = 야간 심리 온도계. 7/28 Oracle 왜곡으로 18~20% 순간 폭락·$57M 청산 사례", fontsize=8, color=GRAY)
    return save(fig, "11_perp_meaning.png")


def chart_capex_formula():
    fig, ax = plt.subplots(figsize=(10.2, 3.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    ax.set_title("AI Capex ≈ Workload × Tokens/Workload × Compute/Token × $/Compute", pad=8)
    boxes = [
        (0.3, "Workload\n↑↑", TEAL),
        (2.8, "Tokens/\nWorkload ↑↑", GREEN),
        (5.3, "Cost/\nToken ↓", GOLD),
        (7.8, "총수요는\n증가 가능", NAVY2),
    ]
    for x, text, c in boxes:
        ax.add_patch(plt.Rectangle((x, 0.7), 1.9, 1.6, fc=c, ec="none", alpha=0.92, zorder=2))
        ax.text(x + 0.95, 1.5, text, ha="center", va="center", color="white", fontsize=11, fontweight="bold", zorder=3)
    for x in (2.25, 4.75, 7.25):
        ax.annotate("", xy=(x + 0.5, 1.5), xytext=(x, 1.5),
                    arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
    return save(fig, "12_capex_formula.png")


def main():
    setup()
    paths = [
        chart_july_sep_returns(),
        chart_macro_shock(),
        chart_memory_per(),
        chart_lead_times(),
        chart_per_vs_yield(),
        chart_per_history(),
        chart_apple_memory(),
        chart_psk_growth(),
        chart_doosan_tp(),
        chart_oracle(),
        chart_perp_meaning(),
        chart_capex_formula(),
    ]
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
