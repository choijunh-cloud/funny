"""8/19 보고서용 matplotlib 차트. 한글은 WenQuanYi Micro Hei."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

from aug19_data import (
    AVGO_CHG,
    GIGA_25,
    GIGA_26E,
    HBM_SCENARIOS,
    ISU_CAPA,
    ISU_ML,
    KRW_FLOOR_DXY,
    KRW_FLOOR_SUPPLY,
    KOSPI_2024,
    MRVL_CHG,
    MU_CY27_PER,
    MU_F12_PER,
    NIKKEI_2024,
    NVDA_Q3,
    NVDA_Q4,
    OPENAI_LOSS,
    OPENAI_Q2_REV,
    SEC_FX_BETA,
    SEC_PER6,
    SEC_PER7,
    SEC_PER_26,
    SEC_PER_27,
    SEC_PER_27_BEAR,
    SKH_2H26_FX_ADJ,
    SKH_ADR_PER26,
    SKH_ADR_PER27,
    SKH_BUYBACK_KRW_T,
    SKH_EPS_FX_HIT,
    SKH_FCF_2527,
    SKH_FCF_CONSERVATIVE,
    SKH_FCF_LADDER,
    SKH_FX_BETA,
    SKH_LOCAL_IF_PREM20,
    SKH_LOCAL_IF_PREM30,
    SKH_LOCAL_IF_PREM35,
    SKH_LOCAL_PX,
    SKH_NI_ADJ_HIGH,
    SKH_NI_ADJ_LOW,
    SKH_PER6,
    SKH_PER7,
    SKH_PER_26,
    SKH_PER_27,
    SKH_PER_27_BEAR,
    SKH_RETURN_ADD,
    SKH_RETURN_MIN,
    SNDK_FY27_PER,
    USD_KRW_FROM,
    USD_KRW_MORNING,
    USD_KRW_TO,
    USDJPY_2024_FROM,
    USDJPY_2024_TO,
)

NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GREEN = "#166534"
RED = "#B91C1C"
AMBER = "#B45309"
TEAL = "#0F766E"
GRAY = "#6B7280"
BLUE = "#2563EB"
LIGHT = "#EEF2F8"

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
]


def _setup_font() -> fm.FontProperties:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            fm.fontManager.addfont(path)
            prop = fm.FontProperties(fname=path)
            plt.rcParams["font.family"] = prop.get_name()
            plt.rcParams["axes.unicode_minus"] = False
            return prop
    plt.rcParams["axes.unicode_minus"] = False
    return fm.FontProperties()


PROP = _setup_font()
plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#D0D7E2",
        "axes.grid": True,
        "grid.color": "#E5EAF1",
        "grid.linewidth": 0.7,
        "axes.titleweight": "bold",
        "axes.titlesize": 12,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8,
        "figure.dpi": 140,
    }
)


def _style(ax, title: str):
    ax.set_title(title, fontproperties=PROP, fontsize=12, color=NAVY, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for lab in ax.get_xticklabels() + ax.get_yticklabels():
        lab.set_fontproperties(PROP)


def _save(fig, path: Path):
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def chart_macro_levels(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    labels = ["장중 부담", "장 마감 진정", "바이백 후"]
    values = [4.75, 4.708, 4.64]
    ax.plot(labels, values, color=NAVY2, marker="o", lw=2.4, ms=9, zorder=3)
    ax.axhline(4.70, color=GREEN, ls="--", lw=1.2, label="소프트 4.7%")
    ax.axhline(5.00, color=RED, ls="--", lw=1.2, label="하드 5.0%")
    for i, v in enumerate(values):
        ax.text(i, v + 0.03, f"{v:.3f}%", ha="center", fontsize=8.5, fontproperties=PROP, color=NAVY)
    ax.set_ylim(4.50, 5.15)
    ax.set_ylabel("미 10년물 (%)", fontproperties=PROP)
    ax.legend(prop=PROP, loc="upper right")
    _style(ax, "10년물 경로 — 4.7% 안착 vs 5% 고착이 분기점")
    _save(fig, path)


def chart_carry_compare(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    x = np.arange(3)
    w = 0.36
    y2024 = [
        (USDJPY_2024_TO / USDJPY_2024_FROM - 1) * 100,
        (NIKKEI_2024[1] / NIKKEI_2024[0] - 1) * 100,
        (KOSPI_2024[1] / KOSPI_2024[0] - 1) * 100,
    ]
    y2026 = [1.0, 0.0, 0.0]  # 엔화 반등·지수 동반급락 없음 (코멘트: 157~159 반등)
    ax.bar(x - w / 2, y2024, w, color=RED, label="2024.8/5 엔캐리 청산", zorder=3)
    ax.bar(x + w / 2, y2026, w, color=NAVY2, label="2026.8 현재(엔화 반등)", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["USD/JPY 변화", "Nikkei", "KOSPI"], fontproperties=PROP)
    ax.axhline(0, color="#9CA3AF", lw=0.8)
    ax.set_ylabel("%", fontproperties=PROP)
    ax.legend(prop=PROP, loc="lower right")
    _style(ax, "2024.8형 엔캐리 청산 vs 현재 — 패턴이 다름")
    _save(fig, path)


def chart_fx_ladder(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    xs = ["가정\n1,520", "현재 가정\n1,420", "장초\n1,412", "DXY -3~4%\n1,360", "공급 가세\n1,340"]
    ys = [USD_KRW_FROM, USD_KRW_TO, USD_KRW_MORNING, KRW_FLOOR_DXY, KRW_FLOOR_SUPPLY]
    ax.plot(xs, ys, color=NAVY2, marker="o", lw=2.4, ms=8, zorder=3)
    ax.fill_between(range(len(ys)), ys, USD_KRW_FROM, color=NAVY2, alpha=0.08)
    for i, v in enumerate(ys):
        ax.text(i, v + 12, f"{v:,}", ha="center", fontsize=8.5, color=NAVY, fontproperties=PROP)
    ax.axhline(1350, color=AMBER, ls="--", lw=1, label="1,350 달러수요 증가 가능")
    ax.set_ylabel("원/달러", fontproperties=PROP)
    ax.legend(prop=PROP)
    ax.invert_yaxis()
    _style(ax, "달러-원 시나리오 래더 (강세일수록 아래)")
    _save(fig, path)


def chart_fx_sensitivity(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    names = ["삼성전자\nβ 0.4", "SK하이닉스\nβ 0.9"]
    move = (USD_KRW_TO / USD_KRW_FROM - 1) * 100  # 음수 = 원화 강세
    hit = [move * b for b in (SEC_FX_BETA, SKH_FX_BETA)]
    colors = [NAVY2, RED]
    bars = ax.barh(names, [abs(v) for v in hit], color=colors, height=0.45, zorder=3)
    for b, v, beta in zip(bars, hit, (SEC_FX_BETA, SKH_FX_BETA)):
        ax.text(
            abs(v) + 0.12,
            b.get_y() + b.get_height() / 2,
            f"1,520→1,420  EPS {v:.1f}%  (β={beta})",
            va="center",
            fontsize=8.5,
            fontproperties=PROP,
            color=NAVY,
        )
    ax.set_xlabel("EPS 하락 폭 (절댓값 막대)  ·  원/달러 하락=수출주 역풍", fontproperties=PROP)
    _style(ax, "환율 민감도 — 1,520 → 1,420 가정")
    _save(fig, path)


def chart_fx_ni_adj(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    labels = ["27년 순익\n300조 가정", "27년 순익\n400조 가정", "26년 하반기\n환율 조정"]
    vals = [SKH_NI_ADJ_LOW, SKH_NI_ADJ_HIGH, SKH_2H26_FX_ADJ]
    bars = ax.bar(labels, vals, color=[AMBER, RED, NAVY2], width=0.55, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.35, f"{v:.1f}조", ha="center", fontsize=9, fontproperties=PROP, color=NAVY)
    ax.set_ylabel("이익 조정 (조원)", fontproperties=PROP)
    _style(ax, f"SK하이닉스 이익 조정 가능성  ·  EPS {SKH_EPS_FX_HIT:.1f}%")
    _save(fig, path)


def chart_skh_return(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    labels = ["25~27 FCF", "50% 환원\n하한", "40조 소각\n(이미 확정)", "추가 환원\n필요"]
    vals = [SKH_FCF_2527, SKH_RETURN_MIN, SKH_BUYBACK_KRW_T, SKH_RETURN_ADD]
    colors = [NAVY, NAVY2, GOLD, GREEN]
    bars = ax.bar(labels, vals, color=colors, width=0.58, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 4, f"{v:g}조", ha="center", fontsize=9, fontproperties=PROP, color=NAVY)
    ax.set_ylabel("조원", fontproperties=PROP)
    _style(ax, "SK하이닉스 주주환원 — 192.5조는 3년 프로그램 합")
    _save(fig, path)


def chart_skh_fcf_ladder(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    x = np.arange(3)
    w = 0.36
    ax.bar(x - w / 2, SKH_FCF_LADDER, w, color=NAVY2, label="기존 계산", zorder=3)
    ax.bar(x + w / 2, SKH_FCF_CONSERVATIVE, w, color=GOLD, label="WC·기타 20~30조 차감", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["연도 A", "연도 B", "연도 C"], fontproperties=PROP)
    ax.legend(prop=PROP)
    ax.set_ylabel("조원", fontproperties=PROP)
    _style(ax, f"내부 FCF 래더  ·  보수 3년 합 {sum(SKH_FCF_CONSERVATIVE)}조 (25~27 385조와 별 프레임)")
    _save(fig, path)


def chart_per_map(path: Path):
    fig, ax = plt.subplots(figsize=(7.4, 3.8))
    labels = ["SKH 본주\n26Y", "SKH 본주\n27Y", "SKH 보수\n27Y", "SKH ADR\n26Y", "SKH ADR\n27Y", "MU\nF12M", "MU\nCY27", "SNDK\nFY27", "삼성\n26Y", "삼성\n27Y"]
    vals = [SKH_PER_26, SKH_PER_27, SKH_PER_27_BEAR, SKH_ADR_PER26, SKH_ADR_PER27, MU_F12_PER, MU_CY27_PER, SNDK_FY27_PER, SEC_PER_26, SEC_PER_27]
    colors = [NAVY, NAVY2, AMBER, TEAL, TEAL, GRAY, GRAY, GRAY, GOLD, GOLD]
    bars = ax.bar(labels, vals, color=colors, width=0.72, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.12, f"{v:.1f}", ha="center", fontsize=7.5, color=NAVY)
    ax.set_ylabel("PER (배)", fontproperties=PROP)
    _style(ax, "메모리 밸류에이션 맵 — 본주 vs ADR vs 피어")
    _save(fig, path)


def chart_adr_premium(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    labels = ["본주\n현재", "프리미엄\n30%", "프리미엄\n35%", "정상\n+20%", "PER 6배\n26Y EPS", "PER 7배\n26Y EPS"]
    vals = [
        SKH_LOCAL_PX / 10_000,
        SKH_LOCAL_IF_PREM30 / 10_000,
        SKH_LOCAL_IF_PREM35 / 10_000,
        SKH_LOCAL_IF_PREM20 / 10_000,
        SKH_PER6 / 10_000,
        SKH_PER7 / 10_000,
    ]
    colors = [GRAY, NAVY2, NAVY2, GREEN, GOLD, GOLD]
    bars = ax.bar(labels, vals, color=colors, width=0.6, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.0f}만", ha="center", fontsize=8, fontproperties=PROP, color=NAVY)
    ax.set_ylabel("본주 환산 (만원)", fontproperties=PROP)
    _style(ax, "SK하이닉스 본주 시나리오 — ADR 프리미엄 vs PER 밴드")
    _save(fig, path)


def chart_hbm_net(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    names = [s["name"] for s in HBM_SCENARIOS]
    ai = [s["ai"] for s in HBM_SCENARIOS]
    eff = [s["eff"] for s in HBM_SCENARIOS]
    net = [s["net"] for s in HBM_SCENARIOS]
    x = np.arange(len(names))
    w = 0.25
    ax.bar(x - w, ai, w, color=NAVY2, label="AI 추론량 +", zorder=3)
    ax.bar(x, eff, w, color=AMBER, label="메모리 효율 +", zorder=3)
    ax.bar(x + w, net, w, color=[GREEN, RED], label="순 메모리 수요", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontproperties=PROP)
    ax.axhline(0, color="#9CA3AF", lw=0.8)
    ax.legend(prop=PROP)
    ax.set_ylabel("%", fontproperties=PROP)
    _style(ax, "핵심 변수 = AI 연산 증가율 − 메모리 효율 개선률")
    _save(fig, path)


def chart_mrvl_avgo(path: Path):
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    labels = ["Marvell", "Broadcom"]
    vals = [MRVL_CHG, AVGO_CHG]
    bars = ax.barh(labels, vals, color=[GREEN, RED], height=0.42, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(v + (0.25 if v > 0 else -0.25), b.get_y() + b.get_height() / 2, f"{v:+.1f}%", va="center", ha="left" if v > 0 else "right", fontsize=10, fontproperties=PROP, color=NAVY)
    ax.axvline(0, color="#9CA3AF", lw=0.8)
    _style(ax, "Google TPU 생태계 확장 — 마벨 vs 브로드컴")
    _save(fig, path)


def chart_isu_mix(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    labels = list(ISU_ML.keys()) + list(ISU_CAPA.keys())
    # two panels
    fig.clear()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 3.4))
    ax1.bar(list(ISU_ML.keys()), list(ISU_ML.values()), color=[LIGHT, NAVY2, GOLD], zorder=3, width=0.55)
    for i, v in enumerate(ISU_ML.values()):
        ax1.text(i, v + 0.4, f"{v}%", ha="center", fontsize=8.5, fontproperties=PROP)
    ax1.set_ylabel("매출/잔고 비중 %", fontproperties=PROP)
    _style(ax1, "이수페타시스 Multi-Lam 비중")
    ax2.plot(list(ISU_CAPA.keys()), list(ISU_CAPA.values()), color=NAVY2, marker="o", lw=2.2, ms=8)
    for i, v in enumerate(ISU_CAPA.values()):
        ax2.text(i, v + 40, f"{v:,}억", ha="center", fontsize=8, fontproperties=PROP)
    ax2.set_ylabel("월 매출 Capa (억원)", fontproperties=PROP)
    _style(ax2, "Capa 로드맵 1,200 → 1,800억")
    _save(fig, path)


def chart_giga_leverage(path: Path):
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    x = np.arange(2)
    w = 0.35
    ax.bar(x - w / 2, [GIGA_25["rev"], GIGA_26E["rev"]], w, color=NAVY2, label="매출", zorder=3)
    ax.bar(x + w / 2, [GIGA_25["op"], GIGA_26E["op"]], w, color=GOLD, label="영업이익", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["2025", "2026E 메리츠"], fontproperties=PROP)
    ax.legend(prop=PROP)
    ax.set_ylabel("억원", fontproperties=PROP)
    _style(ax, "기가비스 — 매출보다 이익 레버리지")
    _save(fig, path)


def chart_nvda_openai(path: Path):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(7.4, 3.4))
    ax1.bar(["Q3 YoY+90%", "Q4 YoY+77%"], [NVDA_Q3["rev"], NVDA_Q4["rev"]], color=[NAVY2, TEAL], width=0.5, zorder=3)
    ax1.set_ylabel("$B", fontproperties=PROP)
    _style(ax1, "NVIDIA 매출 절대액은 계속 증가")
    ax2.bar(["OpenAI 매출", "영업손실 Q1", "영업손실 Q2"], [OPENAI_Q2_REV, OPENAI_LOSS[0], OPENAI_LOSS[1]], color=[GREEN, AMBER, RED], width=0.55, zorder=3)
    ax2.set_ylabel("$B", fontproperties=PROP)
    _style(ax2, "OpenAI — 매출 +18% vs 손실 확대")
    _save(fig, path)


def chart_samsung_sec_band(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    labels = ["현재\n24.75만", "PER 6배\n26Y", "PER 7배\n26Y"]
    vals = [24.75, SEC_PER6 / 10_000, SEC_PER7 / 10_000]
    colors = [GRAY, GOLD, GOLD]
    bars = ax.bar(labels, vals, color=colors, width=0.5, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.4, f"{v:.1f}만", ha="center", fontsize=9, fontproperties=PROP)
    ax.set_ylabel("만원", fontproperties=PROP)
    _style(ax, f"삼성전자 밴드  ·  26Y {SEC_PER_26}배 / 27Y {SEC_PER_27}배 (보수 {SEC_PER_27_BEAR}배)")
    _save(fig, path)


CHARTS = {
    "macro_levels": chart_macro_levels,
    "carry_compare": chart_carry_compare,
    "fx_ladder": chart_fx_ladder,
    "fx_sensitivity": chart_fx_sensitivity,
    "fx_ni_adj": chart_fx_ni_adj,
    "skh_return": chart_skh_return,
    "skh_fcf_ladder": chart_skh_fcf_ladder,
    "per_map": chart_per_map,
    "adr_premium": chart_adr_premium,
    "hbm_net": chart_hbm_net,
    "mrvl_avgo": chart_mrvl_avgo,
    "isu_mix": chart_isu_mix,
    "giga_leverage": chart_giga_leverage,
    "nvda_openai": chart_nvda_openai,
    "samsung_band": chart_samsung_sec_band,
}


def render_all(out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = {}
    for name, fn in CHARTS.items():
        dest = out_dir / f"{name}.png"
        fn(dest)
        written[name] = dest
    return written
