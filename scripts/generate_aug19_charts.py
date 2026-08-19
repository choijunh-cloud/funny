#!/usr/bin/env python3
"""8월 19일 Quick 코멘트 종합 리포트용 차트 생성 (matplotlib)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

CHART_DIR = Path("/workspace/reports/charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update(
    {
        "font.family": "NanumGothic",
        "axes.unicode_minus": False,
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "axes.edgecolor": "#C9D2E0",
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.color": "#E5EAF2",
        "grid.linewidth": 0.7,
        "axes.axisbelow": True,
        "font.size": 10.5,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.titlecolor": "#0F2043",
        "axes.labelcolor": "#374151",
        "xtick.color": "#374151",
        "ytick.color": "#374151",
    }
)

NAVY = "#0F2043"
BLUE = "#1E407C"
SKY = "#5B85C9"
GOLD = "#B8943A"
RED = "#C0392B"
GREEN = "#1E8449"
GRAY = "#6B7280"
LIGHT = "#EEF2F8"

SRC = "자료: 8/19 Quick 코멘트 정리"


def _src(fig, text=SRC):
    fig.text(0.99, 0.01, text, ha="right", va="bottom", fontsize=8, color=GRAY)


def _save(fig, name):
    fig.savefig(CHART_DIR / name, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


def _bar_labels(ax, bars, fmt="{:,.1f}", dy=0.0, fontsize=10, color="#1A1A1A", suffix=""):
    for b in bars:
        h = b.get_height()
        va = "bottom" if h >= 0 else "top"
        off = dy if h >= 0 else -dy
        ax.text(
            b.get_x() + b.get_width() / 2,
            h + off,
            fmt.format(h) + suffix,
            ha="center",
            va=va,
            fontsize=fontsize,
            fontweight="bold",
            color=color,
        )


# ── 1. SK하이닉스 주주환원 워터폴 ──────────────────────────────────────────
def chart_skh_waterfall():
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    labels = [
        "25~27 누적 FCF\n(보수 가정)",
        "최소 환원 재원\n(FCF의 50%)",
        "기확정: 40조\n자사주 매입·소각",
        "추가 환원 여지\n(50% 기준 하한)",
    ]
    vals = [385, 192.5, 40, 152.5]
    colors = [BLUE, GOLD, NAVY, GREEN]
    bars = ax.bar(labels, vals, color=colors, width=0.62)
    _bar_labels(ax, bars, fmt="{:,.1f}조", dy=5)
    ax.set_ylabel("조원")
    ax.set_ylim(0, 440)
    ax.set_title("SK하이닉스 주주환원 재원 추산 — 누적 FCF 385조원 가정 시")
    ax.annotate(
        "회사 목표는 '50% 이상' + 특별배당 검토\n→ 실제 환원은 192.5조를 상회할 가능성",
        xy=(1, 192.5),
        xytext=(1.7, 320),
        fontsize=9.5,
        color=NAVY,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=GRAY),
    )
    ax.text(
        0.01,
        -0.24,
        "* 별도 FCF 모델(보수적 150/210/205조원)로는 3년 누적 약 565조원 → 50% 기준 약 282.5조원 재원도 거론.\n"
        "* 추가 환원의 구체 규모·방식은 3Q26 실적발표 시 이사회 결의를 거쳐 안내 예정.",
        transform=ax.transAxes,
        fontsize=8.5,
        color=GRAY,
        va="top",
    )
    _src(fig)
    _save(fig, "01_skh_waterfall.png")


# ── 2. 자사주 매입·소각 구조 ─────────────────────────────────────────────
def chart_skh_buyback():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.1), gridspec_kw={"width_ratios": [1, 1.25]})
    # 좌: 소각 비중 도넛
    ax1.grid(False)
    wedges, _ = ax1.pie(
        [3.3, 96.7],
        colors=[RED, "#D7DFEC"],
        startangle=90,
        counterclock=False,
        wedgeprops=dict(width=0.42, edgecolor="white"),
    )
    ax1.text(0, 0.12, "소각 3.3%", ha="center", fontsize=13, fontweight="bold", color=RED)
    ax1.text(0, -0.18, "약 2,407만주\n(발행 7억3,049만주)", ha="center", fontsize=9, color=GRAY)
    ax1.set_title("발행주식 대비 소각 규모")
    # 우: 집행 스케줄 (누적 매입액 경로)
    days = list(range(0, 63))
    cum = [d * 0.6452 for d in days]
    ax2.plot(days, cum, color=NAVY, lw=2.5)
    ax2.fill_between(days, cum, color=NAVY, alpha=0.12)
    ax2.scatter([62], [40], color=RED, zorder=5)
    ax2.annotate("40조원 완료\n(11/19, 62영업일)", xy=(62, 40), xytext=(36, 34), fontsize=9.5, fontweight="bold", color=RED, arrowprops=dict(arrowstyle="->", color=GRAY))
    ax2.text(28, 12, "일평균 약 6,452억원 매입\n(현 주가 기준)", fontsize=10, color=NAVY, fontweight="bold", ha="center")
    ax2.set_xlim(0, 68)
    ax2.set_ylim(0, 46)
    ax2.set_xlabel("영업일 (8/20 시작)")
    ax2.set_ylabel("누적 매입액 (조원)")
    ax2.set_title("40조원, 8/20~11/19 3개월 내 집행")
    ax2.text(
        0.02,
        -0.38,
        "· 취득 후 전량 소각 → 동일 순이익 가정 시 EPS 약 +3.4% 효과\n"
        "· ADR 발행으로 희석된 SK스퀘어 지분율을 이전 수준으로 되돌리는 구조",
        transform=ax2.transAxes,
        fontsize=9,
        color=GRAY,
        va="top",
    )
    _src(fig)
    _save(fig, "02_skh_buyback.png")


# ── 3. 미 국채금리 임계선 ────────────────────────────────────────────────
def chart_rates():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.2))
    x = ["장중 고점\n(급등)", "8/19 장 마감", "재무부 바이백\n발표 이후"]
    y10 = [4.75, 4.708, 4.64]
    y30 = [5.34, 5.285, 5.19]

    bars1 = ax1.bar(x, y10, color=[RED, GOLD, GREEN], width=0.55)
    _bar_labels(ax1, bars1, fmt="{:.3f}%", dy=0.006)
    ax1.axhline(4.7, color=GREEN, ls="--", lw=1.4)
    ax1.axhline(5.0, color=RED, ls="--", lw=1.4)
    ax1.text(-0.42, 4.695, "4.7% 이하 = 성장주 부담 완화", fontsize=8.5, color=GREEN, ha="left", va="top")
    ax1.text(-0.42, 5.005, "5.0% 돌파·고착 = 밸류 조정 위험", fontsize=8.5, color=RED, ha="left", va="bottom")
    ax1.set_ylim(4.4, 5.1)
    ax1.set_title("미 10년물 금리")

    bars2 = ax2.bar(x, y30, color=[RED, GOLD, GREEN], width=0.55)
    _bar_labels(ax2, bars2, fmt="{:.3f}%", dy=0.006)
    ax2.axhline(5.19, color=GRAY, ls=":", lw=1.2)
    ax2.set_ylim(5.0, 5.5)
    ax2.set_title("미 30년물 금리 (19년래 고점권)")

    fig.suptitle("유가발 금리 쇼크 → 재무부 장기채 바이백(20억→40억달러)으로 진정", fontsize=12.5, fontweight="bold", color=NAVY, y=1.04)
    _src(fig)
    _save(fig, "03_rates.png")


# ── 4. 2024년 8월 엔캐리 청산 사례 ──────────────────────────────────────
def chart_yen_carry():
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    labels = ["Nikkei", "KOSPI"]
    crash = [-19.5, -11.9]
    rebound = [10.23, 3.30]
    x = range(len(labels))
    w = 0.34
    b1 = ax.bar([i - w / 2 for i in x], crash, width=w, color=RED, label="7/31→8/5 낙폭")
    b2 = ax.bar([i + w / 2 for i in x], rebound, width=w, color=GREEN, label="8/6 하루 반등")
    _bar_labels(ax, b1, fmt="{:+.1f}%", dy=0.6)
    _bar_labels(ax, b2, fmt="{:+.2f}%", dy=0.6)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.axhline(0, color=GRAY, lw=0.9)
    ax.set_ylim(-25, 16)
    ax.set_ylabel("%")
    ax.legend(loc="lower right", frameon=False)
    ax.set_title("2024년 8월 엔캐리 청산 사례 — 유동성 쇼크였다는 증거")
    ax.text(
        0.98,
        0.97,
        "당시 USD/JPY 152~153 → 142~145 (6%대 엔 강세)\n"
        "지금은 157~159에서 반등 → 엔캐리 청산보다\n'금리 상승발 밸류 압박' 성격",
        transform=ax.transAxes,
        fontsize=9.5,
        color=NAVY,
        va="top",
        ha="right",
    )
    _src(fig)
    _save(fig, "04_yen_carry_2024.png")


# ── 5. 달러-원 하단 시나리오 ─────────────────────────────────────────────
def chart_fx_scenarios():
    fig, ax = plt.subplots(figsize=(8.6, 4.3))
    levels = [
        ("현재", 1412, NAVY, "1,400원 하회 — 국내 달러 공급이 주도"),
        ("시나리오 ①", 1360, GOLD, "달러인덱스 99 → 96~97 (금리 인상 기대 되돌림)"),
        ("시나리오 ②", 1340, RED, "① + 한국의 강한 달러 공급 지속"),
    ]
    names = [l[0] for l in levels]
    vals = [l[1] for l in levels]
    colors = [l[2] for l in levels]
    bars = ax.barh(names, vals, color=colors, height=0.5)
    ax.set_xlim(1280, 1460)
    ax.invert_yaxis()
    for b, (_, v, _, note) in zip(bars, levels):
        ax.text(v + 4, b.get_y() + b.get_height() / 2, f"{v:,}원대", va="center", fontsize=11, fontweight="bold", color="#1A1A1A")
        ax.text(1284, b.get_y() + b.get_height() / 2, note, va="center", fontsize=8.8, color="white", fontweight="bold")
    ax.axvline(1350, color=GRAY, ls="--", lw=1.2)
    ax.text(1350, 2.62, "▲ 1,350원 부근: 달러 실수요 유입 가능성(지지)", fontsize=8.8, color=GRAY, ha="center", va="top")
    ax.set_xlabel("원/달러")
    ax.set_title("달러-원 하단 시나리오 — '1,300원대 중반'은 조건부")
    ax.text(
        0.01,
        -0.26,
        "원화 추가 강세의 리스크: ① 외국인 국내주식 매도 확대  ② 미국-이란 / 유가  ③ 1,350원 부근 달러 수요 증가",
        transform=ax.transAxes,
        fontsize=8.8,
        color=GRAY,
        va="top",
    )
    _src(fig)
    _save(fig, "05_fx_scenarios.png")


# ── 6. 환율 민감도 ──────────────────────────────────────────────────────
def chart_fx_sensitivity():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.1))
    b = ax1.bar(["삼성전자", "SK하이닉스"], [0.4, 0.9], color=[SKY, NAVY], width=0.5)
    _bar_labels(ax1, b, fmt="+{:.1f}%", dy=0.02)
    ax1.set_ylim(0, 1.15)
    ax1.set_title("원/달러 +1% 당 EPS 민감도")
    ax1.set_ylabel("EPS 변화율 (%)")

    b2 = ax2.bar(
        ["EPS 영향", "이익 조정\n(순익 300조)", "이익 조정\n(순익 400조)", "26년 하반기\n환율 기준"],
        [-5.9, -18, -24, -16.3],
        color=[RED, GOLD, GOLD, GRAY],
        width=0.55,
    )
    for bar, txt in zip(b2, ["-5.9%", "-18조원", "-24조원", "-16.3조원"]):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() - 0.9, txt, ha="center", va="top", fontsize=10, fontweight="bold", color="#1A1A1A")
    ax2.axhline(0, color=GRAY, lw=0.9)
    ax2.set_ylim(-32, 3)
    ax2.tick_params(axis="x", labelsize=8.6)
    ax2.set_title("환율 1,520 → 1,420원 가정 시 SK하이닉스(2027년)")
    fig.suptitle("환율 하락(원화 강세)은 수출주 이익의 역풍 — 민감도는 SK하이닉스가 더 큼", fontsize=12.5, fontweight="bold", color=NAVY, y=1.04)
    fig.text(0.01, -0.05, "* 원문 코멘트의 '+0.4%'는 'SK하이닉스'로 표기되어 있으나 문맥상 삼성전자 민감도로 해석.", fontsize=8.3, color=GRAY)
    _src(fig)
    _save(fig, "06_fx_sensitivity.png")


# ── 7. HBM 논쟁 핵심 변수 ───────────────────────────────────────────────
def chart_hbm_variable():
    fig, ax = plt.subplots(figsize=(8.6, 4.3))
    labels = ["케이스 A", "케이스 B"]
    ai = [50, 20]
    eff = [20, 30]
    net = [30, -10]
    x = range(len(labels))
    w = 0.26
    b1 = ax.bar([i - w for i in x], ai, width=w, color=BLUE, label="AI 연산(추론량) 증가율")
    b2 = ax.bar(list(x), eff, width=w, color=GOLD, label="메모리 효율 개선률")
    b3 = ax.bar([i + w for i in x], net, width=w, color=[GREEN, RED], label="순효과(수요 방향)")
    for bars in (b1, b2, b3):
        _bar_labels(ax, bars, fmt="{:+.0f}%p" if bars is b3 else "+{:.0f}%", dy=1)
    ax.axhline(0, color=GRAY, lw=0.9)
    ax.set_xticks(list(x))
    ax.set_xticklabels(["케이스 A\n→ 메모리 수요 여전히 크게 증가", "케이스 B\n→ 메모리 수요 증가세 둔화"])
    ax.set_ylim(-20, 62)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.set_title("HBM 논쟁의 핵심 변수 = AI 연산 증가율 - 메모리 효율 개선률")
    _src(fig)
    _save(fig, "07_hbm_variable.png")


# ── 8. PER 비교 ─────────────────────────────────────────────────────────
def chart_per():
    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    groups = [
        ("SK하이닉스\n(본주 150만원)", [4.3, 3.4, 5.1]),
        ("삼성전자\n(24.75만원)", [5.2, 3.7, 5.6]),
        ("SK하이닉스 ADR\n(163.8달러)", [6.6, 5.2, 7.7]),
        ("마이크론\n(937.11달러)", [7.5, 6.25, None]),
        ("샌디스크\n(1,568.37달러)", [None, 7.8, None]),
    ]
    w = 0.26
    colors = [BLUE, GREEN, RED]
    legend = ["2026년 PER", "2027년 PER", "보수적 시나리오 27년 PER"]
    for gi, (name, vals) in enumerate(groups):
        for si, v in enumerate(vals):
            if v is None:
                continue
            b = ax.bar(gi + (si - 1) * w, v, width=w, color=colors[si])
            ax.text(gi + (si - 1) * w, v + 0.1, f"{v:g}", ha="center", fontsize=9.5, fontweight="bold")
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([g[0] for g in groups], fontsize=9.5)
    handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in colors]
    ax.legend(handles, legend, loc="upper left", frameon=False, fontsize=9)
    ax.set_ylim(0, 9.5)
    ax.set_ylabel("PER (배)")
    ax.set_title("메모리 밸류에이션 비교 — 컨센서스 기준")
    ax.text(
        0.01,
        -0.22,
        "* 마이크론: Forward 12개월 7.5배 / CY27 EPS 150달러 기준 6.25배.  샌디스크: FY27 EPS 201달러 가정 7.8배.\n"
        "* SK하이닉스 ADR은 마이크론 대비 -17% (과거 -20~-50% 할인 대비 축소).",
        transform=ax.transAxes,
        fontsize=8.5,
        color=GRAY,
        va="top",
    )
    _src(fig)
    _save(fig, "08_per_comparison.png")


# ── 9. 시나리오 목표 밴드 ────────────────────────────────────────────────
def chart_target_bands():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.3))
    # SK하이닉스
    ax1.bar(["산출 밴드"], [242 - 208], bottom=[208], color=SKY, width=0.35, alpha=0.85)
    ax1.axhline(150, color=NAVY, lw=1.6)
    ax1.text(0.03, 152, "현재 150만원", fontsize=9.5, color=NAVY, fontweight="bold", va="bottom", transform=ax1.get_yaxis_transform())
    ax1.axhline(169, color=GOLD, ls="--", lw=1.3)
    ax1.axhline(175, color=GOLD, ls="--", lw=1.3)
    ax1.text(0.03, 177, "ADR 30~35% 프리미엄 역산: 169~175만원", fontsize=8.5, color=GOLD, va="bottom", fontweight="bold", transform=ax1.get_yaxis_transform())
    ax1.text(0, 225, "208~242만원", ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax1.set_ylim(120, 270)
    ax1.set_ylabel("만원")
    ax1.set_title("SK하이닉스 — 26년 PER 6~7배 적용")
    # 삼성전자
    ax2.bar(["산출 밴드"], [33.5 - 28.7], bottom=[28.7], color=SKY, width=0.35, alpha=0.85)
    ax2.axhline(24.75, color=NAVY, lw=1.6)
    ax2.text(0.03, 25.0, "현재 24.75만원", fontsize=9.5, color=NAVY, fontweight="bold", va="bottom", transform=ax2.get_yaxis_transform())
    ax2.text(0, 31.1, "28.7~33.5만원", ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax2.set_ylim(20, 38)
    ax2.set_ylabel("만원")
    ax2.set_title("삼성전자 — 26년 PER 6~7배 적용")
    fig.suptitle("'27년 성장 제로' 보수 가정 + 과거 사이클 PER(4~8배) 중간값 적용 시나리오", fontsize=12, fontweight="bold", color=NAVY, y=1.04)
    _src(fig)
    _save(fig, "09_target_bands.png")


# ── 10. 삼성 파운드리 가격 인상 ─────────────────────────────────────────
def chart_foundry():
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    labels = ["4나노(SF4)\n중국·미국 고객", "4나노(SF4)\n대만 고객", "5나노(SF5)\n웨이퍼 기준", "8나노\n레거시"]
    lo = [10, 5, 10, 10]
    hi = [15, 10, 15, 10]
    for i, (l, h) in enumerate(zip(lo, hi)):
        if l == h:
            ax.bar(i, 1.2, bottom=l - 0.6, color=NAVY, width=0.5)
            ax.text(i, h + 0.8, f"약 {h}%", ha="center", fontsize=10.5, fontweight="bold", color=NAVY)
        else:
            ax.bar(i, h - l, bottom=l, color=NAVY, width=0.5)
            ax.text(i, h + 0.8, f"{l}~{h}%", ha="center", fontsize=10.5, fontweight="bold", color=NAVY)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylim(0, 20)
    ax.set_ylabel("신규 주문 가격 인상률 (%)")
    ax.set_title("삼성전자 첨단 파운드리 가격 최대 15% 인상 (로이터, 8/19)")
    ax.text(
        0.01,
        -0.25,
        "배경: TSMC 첨단공정 포화 → 고객 분산, 中 팹리스의 해외 파운드리 의존 심화, 평택 SF4 라인 풀가동(퀄컴 + 차세대 HBM 베이스 다이).",
        transform=ax.transAxes,
        fontsize=8.5,
        color=GRAY,
        va="top",
    )
    _src(fig, "자료: Reuters (2026.8.19), Quick 코멘트 정리")
    _save(fig, "10_foundry_price.png")


# ── 11. 이수페타시스 ────────────────────────────────────────────────────
def chart_isu():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.2, 4.2))
    b1 = ax1.bar(["1Q26", "2Q26", "현재\n수주잔고"], [7, 11, 20], color=[SKY, BLUE, NAVY], width=0.5)
    for bar, t in zip(b1, ["7%", "11%", "20%+"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, t, ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax1.set_ylim(0, 26)
    ax1.set_ylabel("Multi-Lam 매출 비중 (%)")
    ax1.set_title("고부가 Multi-Lam 비중 급상승")

    b2 = ax2.bar(["현재", "2027년 2Q", "2028년 하반기"], [1200, 1500, 1800], color=[SKY, BLUE, NAVY], width=0.5)
    _bar_labels(ax2, b2, fmt="{:,.0f}억", dy=25)
    ax2.set_ylim(0, 2100)
    ax2.set_ylabel("월 매출 Capa (억원)")
    ax2.set_title("Capa 증설 로드맵")
    fig.suptitle("이수페타시스 2Q26 Review — 'Capa 증설'에서 '이익 레버리지' 스토리로", fontsize=12.5, fontweight="bold", color=NAVY)
    fig.text(
        0.01,
        -0.04,
        "2Q26: 매출 3,799억(+57.4% YoY, 컨센 +4.9% 상회) / 영업이익 771억(+83.3% YoY, +2.7% 상회) / OPM 20.3%\n"
        "+ 하반기 평균 약 +15% 판가 인상 효과, 2027년 영업이익 컨센 대비 +10% 전후 상향 여지",
        fontsize=8.8,
        color=GRAY,
    )
    _src(fig)
    _save(fig, "11_isu_petasys.png")


# ── 12. 기가비스 ────────────────────────────────────────────────────────
def chart_gigavis():
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    x = range(2)
    w = 0.32
    rev = [847, 1785]
    op = [121, 721]
    b1 = ax.bar([i - w / 2 for i in x], rev, width=w, color=BLUE, label="매출액")
    b2 = ax.bar([i + w / 2 for i in x], op, width=w, color=GOLD, label="영업이익")
    _bar_labels(ax, b1, fmt="{:,.0f}억", dy=25)
    _bar_labels(ax, b2, fmt="{:,.0f}억", dy=25)
    ax.set_xticks(list(x))
    ax.set_xticklabels(["2025년 (집계)", "2026년E (메리츠증권)"])
    ax.set_ylim(0, 2100)
    ax.legend(frameon=False)
    ax.set_title("기가비스 — FC-BGA 검사(AOI)·수리(AOR) 장비, 실적 레버리지 구조")
    for i, (r, o) in enumerate(zip(rev, op)):
        ax.text(i, max(r, o) + 170, f"OPM {o / r * 100:.0f}%", ha="center", fontsize=10, color=GREEN, fontweight="bold")
    ax.text(
        0.01,
        -0.22,
        "8/18 일본 기판업체향 89.5억원(매출 대비 17.1%) 공급계약 공시. 증권사 컨센 TP 19만원선 — 26년 기준 비싸고 27년 성장이 초점, 분할접근 후보.",
        transform=ax.transAxes,
        fontsize=8.5,
        color=GRAY,
        va="top",
    )
    _src(fig)
    _save(fig, "12_gigavis.png")


# ── 13. LS 자회사 영업이익 ──────────────────────────────────────────────
def chart_ls():
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    names = ["LS일렉트릭", "LS MnM", "LS전선", "LS아이앤디"]
    vals = [1785, 1757, 1413, 741]
    yoy = ["+64%", "흑자전환", "+71%", "+166%"]
    bars = ax.bar(names, vals, color=[NAVY, BLUE, SKY, GOLD], width=0.55)
    for bar, v, y in zip(bars, vals, yoy):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 30, f"{v:,}억", ha="center", fontsize=10.5, fontweight="bold")
        ax.text(bar.get_x() + bar.get_width() / 2, v / 2, f"YoY {y}", ha="center", fontsize=9, color="white", fontweight="bold")
    ax.set_ylim(0, 2200)
    ax.set_ylabel("2Q26 영업이익 (억원)")
    ax.set_title("LS — 2개 분기 연속 사상 최대 (2Q 영업이익 5,956억원, +153% YoY)")
    ax.text(
        0.01,
        -0.22,
        "키움증권: 26·27년 영업이익 전망 각각 +20%, +17% 상향. 자사주 11.1% 보유 → 소각 의무화로 하반기 이후 소각 논의 본격화 전망.",
        transform=ax.transAxes,
        fontsize=8.5,
        color=GRAY,
        va="top",
    )
    _src(fig)
    _save(fig, "13_ls_subsidiaries.png")


# ── 14. NVIDIA 매출 전망 ────────────────────────────────────────────────
def chart_nvda():
    fig, ax = plt.subplots(figsize=(8.6, 4.3))
    x = ["Q3 FY27E", "Q4 FY27E"]
    rev = [108, 120]
    yoy = [90, 77]
    bars = ax.bar(x, rev, color=[BLUE, NAVY], width=0.42)
    _bar_labels(ax, bars, fmt="${:,.0f}B", dy=2)
    ax.set_ylim(0, 145)
    ax.set_ylabel("분기 매출 (십억달러)")
    ax2 = ax.twinx()
    ax2.plot(x, yoy, color=RED, marker="o", lw=2, label="YoY 성장률")
    for xi, yv in zip(x, yoy):
        ax2.annotate(f"+{yv}%", (xi, yv), textcoords="offset points", xytext=(18, 4), color=RED, fontweight="bold", fontsize=10.5)
    ax2.set_ylim(0, 130)
    ax2.set_ylabel("YoY (%)", color=RED)
    ax2.grid(False)
    ax.set_title("NVIDIA Q2 FY27 실적 프리뷰(8/26) — 성장률 둔화에도 절대 매출은 폭발적 증가")
    ax.text(
        0.01,
        -0.22,
        "관전 포인트: ① AI 인프라 수요 지속 ② Hyperscaler CAPEX(2027년 Top5 ≥ $1T, +33%) ③ AI 기업 자금조달(순환금융 논쟁)\n"
        "④ GM 75% 유지 ⑤ Blackwell→Rubin 전환(3Q26 출하, 추론 처리량 최대 35배, 랙 $7~8.5M로 약 2배 ASP)",
        transform=ax.transAxes,
        fontsize=8.5,
        color=GRAY,
        va="top",
    )
    _src(fig)
    _save(fig, "14_nvidia_preview.png")


# ── 15. 8/19 미국장 주요 종목 등락 ──────────────────────────────────────
def chart_us_moves():
    fig, ax = plt.subplots(figsize=(9.2, 4.8))
    names = [
        "모더나",
        "BioNTech",
        "MSD",
        "마벨",
        "일라이릴리",
        "SK하이닉스 ADR",
        "마이크론",
        "샌디스크",
        "브로드컴",
    ]
    vals = [77, 22, 12.9, 9.9, 4.5, 0.3, -0.39, -3.5, -4.6]
    colors = [GREEN if v >= 0 else RED for v in vals]
    bars = ax.barh(names, vals, color=colors, height=0.55)
    for b, v in zip(bars, vals):
        ax.text(v + (1.2 if v >= 0 else -1.2), b.get_y() + b.get_height() / 2, f"{v:+.1f}%", va="center", ha="left" if v >= 0 else "right", fontsize=10, fontweight="bold")
    ax.axvline(0, color=GRAY, lw=0.9)
    ax.invert_yaxis()
    ax.set_xlim(-15, 92)
    ax.set_xlabel("전일 대비 등락률 (%)")
    ax.set_title("8/19 미국장 — 자금의 피벗: AI·반도체 → 헬스케어 로테이션")
    ax.text(
        0.99,
        0.05,
        "모더나: 키트루다 병용 mRNA 항암백신 3상 성공\n마벨: 구글 TPU 생태계 협력 확대(워런트 5,897만주)\n브로드컴: 구글 TPU 독점 지위 견제 신호로 해석",
        transform=ax.transAxes,
        fontsize=9,
        color=NAVY,
        ha="right",
        va="bottom",
    )
    _src(fig)
    _save(fig, "15_us_moves.png")


# ── 16. 매크로 전달 경로 도식 ───────────────────────────────────────────
def chart_macro_flow():
    fig, ax = plt.subplots(figsize=(9.2, 2.9))
    ax.axis("off")
    ax.grid(False)
    steps = [
        ("미·이란\n협상 불확실성", RED),
        ("호르무즈 리스크\n→ 유가 상승\n(WTI 84달러대)", GOLD),
        ("인플레이션\n우려", GOLD),
        ("미 국채금리\n급등", RED),
        ("기술주·반도체\n밸류에이션 압박", NAVY),
    ]
    n = len(steps)
    for i, (txt, c) in enumerate(steps):
        x = i / (n - 0.35)
        ax.text(
            x + 0.07,
            0.55,
            txt,
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="white",
            bbox=dict(boxstyle="round,pad=0.55", facecolor=c, edgecolor="none"),
            transform=ax.transAxes,
        )
        if i < n - 1:
            ax.annotate(
                "",
                xy=(x + 0.155, 0.55),
                xytext=(x + 0.125, 0.55),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.8),
            )
    ax.text(0.5, 0.02, "↳ 대응: 미 재무부 장기국채 바이백 2배 확대(20억→40억달러) → 30년물 5.19% 아래로, 10년물 4.64%로 진정", ha="center", fontsize=10, color=GREEN, fontweight="bold", transform=ax.transAxes)
    ax.set_title("『매크로의 역습』 — 8/19 하락의 전달 경로", pad=14)
    _src(fig)
    _save(fig, "16_macro_flow.png")


# ── 17. 환율 하락 메커니즘 도식 ─────────────────────────────────────────
def chart_fx_flow():
    fig, ax = plt.subplots(figsize=(9.2, 2.9))
    ax.axis("off")
    ax.grid(False)
    steps = [
        ("법인세 납부·\n국내 설비투자\n원화 수요", BLUE),
        ("수출기업\n달러 매도 ↑", BLUE),
        ("환헤지 비중\n상승", GOLD),
        ("달러-원 하락", NAVY),
        ("높은 환율에서\n추가 달러 매도", GOLD),
        ("환율 하락\n가속", RED),
    ]
    n = len(steps)
    for i, (txt, c) in enumerate(steps):
        x = i / (n - 0.28)
        ax.text(
            x + 0.06,
            0.55,
            txt,
            ha="center",
            va="center",
            fontsize=9.3,
            fontweight="bold",
            color="white",
            bbox=dict(boxstyle="round,pad=0.5", facecolor=c, edgecolor="none"),
            transform=ax.transAxes,
        )
        if i < n - 1:
            ax.annotate(
                "",
                xy=(x + 0.135, 0.55),
                xytext=(x + 0.108, 0.55),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color=GRAY, lw=1.6),
            )
    ax.text(0.5, 0.02, "핵심: '달러 약세 때문'이 아니라 '한국의 달러 공급이 강해 달러-원이 먼저 떨어졌다' — 국내 수급 주도", ha="center", fontsize=10, color=NAVY, fontweight="bold", transform=ax.transAxes)
    ax.set_title("왜 1,400원 아래로 내려왔나 — 국내 수급 메커니즘", pad=14)
    _src(fig)
    _save(fig, "17_fx_flow.png")


if __name__ == "__main__":
    chart_skh_waterfall()
    chart_skh_buyback()
    chart_rates()
    chart_yen_carry()
    chart_fx_scenarios()
    chart_fx_sensitivity()
    chart_hbm_variable()
    chart_per()
    chart_target_bands()
    chart_foundry()
    chart_isu()
    chart_gigavis()
    chart_ls()
    chart_nvda()
    chart_us_moves()
    chart_macro_flow()
    chart_fx_flow()
    print("done:", len(list(CHART_DIR.glob("*.png"))), "charts")
