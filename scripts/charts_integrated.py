"""8/18~20 통합 보고서 matplotlib 차트."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib.pyplot as plt
import numpy as np

import aug19_data as a
import charts_aug19 as c19
import integrated_data as d

PROP = c19.PROP
NAVY, NAVY2, GOLD = c19.NAVY, c19.NAVY2, c19.GOLD
GREEN, RED, AMBER, TEAL, GRAY = c19.GREEN, c19.RED, c19.AMBER, c19.TEAL, c19.GRAY
_style, _save = c19._style, c19._save


def chart_kospi_turnover(path: Path):
    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    xs, ys = list(d.KOSPI_TURNOVER.keys()), list(d.KOSPI_TURNOVER.values())
    colors = [GOLD if v >= 50 else (AMBER if v >= 35 else NAVY2) for v in ys]
    bars = ax.bar(xs, ys, color=colors, width=0.62, zorder=3)
    for b, v in zip(bars, ys):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.7, f"{v:.1f}", ha="center", fontsize=8)
    ax.axhline(50, color=GOLD, ls="--", lw=0.8, alpha=0.7)
    ax.set_ylabel("일평균 거래대금 (조원)", fontproperties=PROP)
    _style(ax, "코스피 일평균 거래대금 — 5~6월 50조 → 8월 25.7조")
    _save(fig, path)


def chart_jgb(path: Path):
    fig, ax = plt.subplots(figsize=(6.8, 3.4))
    labels = ["2년\n31년래", "5년\n사상최고", "10년\n30년래"]
    vals = [d.JGB["2y"], d.JGB["5y"], d.JGB["10y"]]
    bars = ax.bar(labels, vals, color=[NAVY2, AMBER, RED], width=0.5, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.05, f"{v:.3f}%", ha="center", fontsize=9, fontproperties=PROP)
    ax.axhline(3.0, color=RED, ls="--", lw=1, label="10년 3% 경계")
    ax.legend(prop=PROP)
    ax.set_ylabel("%", fontproperties=PROP)
    _style(ax, "일본 금리 — 상승 자체보다 엔화 급등 조합이 위험")
    _save(fig, path)


def chart_crash_2024(path: Path):
    fig, ax1 = plt.subplots(figsize=(7.6, 3.7))
    dates = [x[0] for x in d.CRASH_2024]
    jpy = [x[1] for x in d.CRASH_2024]
    nk = [x[2] for x in d.CRASH_2024]
    kp = [x[3] for x in d.CRASH_2024]
    ax1.plot(dates, jpy, color=NAVY2, marker="o", lw=2, label="USD/JPY")
    ax1.set_ylabel("USD/JPY", fontproperties=PROP, color=NAVY2)
    ax1.invert_yaxis()
    ax2 = ax1.twinx()
    ax2.bar([i - 0.18 for i in range(len(dates))], nk, 0.36, color=RED, alpha=0.7, label="Nikkei %")
    ax2.bar([i + 0.18 for i in range(len(dates))], kp, 0.36, color=GOLD, alpha=0.85, label="KOSPI %")
    ax2.axhline(0, color="#9CA3AF", lw=0.6)
    ax2.set_ylabel("일간 %", fontproperties=PROP)
    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax1.legend(h1 + h2, l1 + l2, prop=PROP, loc="lower left", fontsize=8)
    _style(ax1, "2024.8 엔화 급등 + 지수 동반폭락 — 8/6 반등 = 청산 쇼크")
    _save(fig, path)


def chart_sess819(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    labels = ["30Y bp", "10Y bp", "S&P500", "Nasdaq", "SOX", "Dow", "달러"]
    vals = [
        (d.SESS_819["us30"][1] - d.SESS_819["us30"][0]) * 100,
        (d.SESS_819["us10"][1] - d.SESS_819["us10"][0]) * 100,
        d.SESS_819["spx"],
        d.SESS_819["ndx"],
        d.SESS_819["sox"],
        d.SESS_819["dow"],
        d.SESS_819["dxy"],
    ]
    colors = [GREEN if v >= 0 else RED for v in vals]
    # rates down is green for stocks; SOX is red
    colors[0] = GREEN
    colors[1] = GREEN
    bars = ax.bar(labels, vals, color=colors, width=0.58, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.12 if v >= 0 else -0.28), f"{v:+.2f}", ha="center", fontsize=8)
    ax.axhline(0, color="#9CA3AF", lw=0.7)
    _style(ax, "8/19 미국장 — 금리↓·지수+ 인데 SOX −2.12% (OpenAI 우려)")
    _save(fig, path)


def chart_skh_hit60(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    labels = ["2H26 환율\n16.3조", "27년 환율\n18~24조", "키옥시아+가격\n+환율 합산"]
    vals = [d.SKH_2H26_FX, a.SKH_NI_ADJ_HIGH, d.SKH_TOTAL_HIT]
    bars = ax.bar(labels, vals, color=[NAVY2, AMBER, RED], width=0.5, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 1.2, f"{v:.1f}조", ha="center", fontsize=9, fontproperties=PROP)
    ax.set_ylabel("조원", fontproperties=PROP)
    _style(ax, "SK하이닉스 이익 하향 바구니 — 환율만으로 끝나지 않음")
    _save(fig, path)


def chart_fcf_years(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    years = list(d.SKH_FCF_YEARS.keys())
    fcf = list(d.SKH_FCF_YEARS.values())
    cum = list(d.SKH_FCF_CUM.values())
    x = np.arange(len(years))
    ax.bar(x, fcf, 0.45, color=NAVY2, label="연간 FCF", zorder=3)
    ax.plot(x, cum, color=GOLD, marker="D", lw=2, label="누적 FCF")
    for i, (f, c) in enumerate(zip(fcf, cum)):
        ax.text(i, f + 6, f"{f}", ha="center", fontsize=8, fontproperties=PROP)
        ax.text(i, c + 12, f"누적 {c}", ha="center", fontsize=7.5, color=AMBER, fontproperties=PROP)
    ax.set_xticks(x)
    ax.set_xticklabels(years, fontproperties=PROP)
    ax.legend(prop=PROP)
    ax.set_ylabel("조원", fontproperties=PROP)
    _style(ax, "보수 FCF — 25+150+210=385조  ·  2028 205조는 정책 아님")
    _save(fig, path)


def chart_per_hdd(path: Path):
    fig, ax = plt.subplots(figsize=(7.6, 3.7))
    labels = ["SKH본주26", "SKH본주27", "SKH ADR27", "MU CY27", "SNDK FY27", "삼성26", "WDC FY27", "STX FY27"]
    vals = [a.SKH_PER_26, a.SKH_PER_27, a.SKH_ADR_PER27, a.MU_CY27_PER, a.SNDK_FY27_PER, a.SEC_PER_26, d.WDC_PER, d.STX_PER]
    colors = [NAVY, NAVY2, TEAL, GRAY, GRAY, GOLD, RED, RED]
    bars = ax.bar(labels, vals, color=colors, width=0.7, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.25, f"{v:g}", ha="center", fontsize=7.5)
    ax.set_ylabel("PER (배)", fontproperties=PROP)
    _style(ax, "메모리 6~8배 vs HDD 26배 — 같은 '스토리지'가 아님")
    _save(fig, path)


def chart_sca_asp(path: Path):
    fig, ax = plt.subplots(figsize=(7.4, 3.5))
    labels = [s[0] for s in d.SCA_ASP]
    vals = [s[1] for s in d.SCA_ASP]
    bars = ax.barh(labels, vals, color=NAVY2, height=0.5, zorder=3)
    ax.axvline(100, color=GRAY, ls="--", lw=1, label="현재 ASP 100")
    for b, v in zip(bars, vals):
        ax.text(v + 0.8, b.get_y() + b.get_height() / 2, f"{v}", va="center", fontsize=8)
    ax.set_xlim(60, 110)
    ax.legend(prop=PROP)
    _style(ax, "SCA 50% 가중 ASP — 바닥(Floor)이 하락을 얼마나 받치나")
    _save(fig, path)


def chart_gp_bit(path: Path):
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    growth = [10, 20, 30]
    # GP/bit -16.6%, cost already in. Total GP ≈ (1-0.166)*(1+g)
    totals = [(1 + d.GP_BIT_DROP / 100) * (1 + g / 100) * 100 - 100 for g in growth]
    colors = [AMBER, GREEN, GREEN]
    bars = ax.bar([f"Bit +{g}%" for g in growth], totals, color=colors, width=0.5, zorder=3)
    for b, v in zip(bars, totals):
        ax.text(b.get_x() + b.get_width() / 2, v + (0.4 if v >= 0 else -1.2), f"{v:+.1f}%", ha="center", fontsize=9)
    ax.axhline(0, color="#9CA3AF", lw=0.8)
    ax.set_ylabel("Total GP 변화 %", fontproperties=PROP)
    _style(ax, f"시장가 −20%·Floor90% → GP/bit {d.GP_BIT_DROP}%  ·  Bit +{d.BIT_GROWTH_NEUTRAL}%면 총GP 유지")
    _save(fig, path)


def chart_nvda_q2(path: Path):
    fig, ax = plt.subplots(figsize=(6.8, 3.5))
    labels = ["가이던스\n하단", "컨센", "가이던스\n상단", "저자 예상"]
    vals = [d.NVDA_Q2["guide_lo"], d.NVDA_Q2["cons_rev"], d.NVDA_Q2["guide_hi"], d.NVDA_Q2["author"]]
    colors = [GRAY, NAVY2, GRAY, GOLD]
    bars = ax.bar(labels, vals, color=colors, width=0.55, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.15, f"${v}B", ha="center", fontsize=8.5)
    ax.set_ylim(88, 95)
    _style(ax, f"NVIDIA Q2 — 컨센 ${d.NVDA_Q2['cons_rev']}B(+{d.NVDA_Q2['cons_yoy']}%)  ·  Beat보다 CAPEX·Rubin")
    _save(fig, path)


def chart_baba(path: Path):
    fig, ax = plt.subplots(figsize=(6.8, 3.5))
    labels = ["전사 매출\nYoY", "Cloud\nYoY", "직전 분기\n조정EBITA"]
    vals = [d.BABA_REV_YOY, d.BABA_CLOUD_YOY, d.BABA_EBITA_DROP]
    colors = [NAVY2, GREEN, RED]
    bars = ax.bar(labels, vals, color=colors, width=0.5, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + (2 if v >= 0 else -8), f"{v:+.0f}%", ha="center", fontsize=9)
    ax.axhline(0, color="#9CA3AF", lw=0.7)
    _style(ax, f"알리바바 FY1Q27 — 매출 {d.BABA_REV:,}억위안, Cloud {d.BABA_CLOUD}억(+{d.BABA_CLOUD_YOY}%)")
    _save(fig, path)


def chart_baba_mult(path: Path):
    fig, ax = plt.subplots(figsize=(6.8, 3.4))
    labels = ["Trail PER", "Fwd PER", "PEG×10", "52주고점"]
    vals = [20.5, 19.5, d.BABA_PEG * 10, 33]
    colors = [NAVY2, TEAL, GREEN, AMBER]
    bars = ax.bar(labels, vals, color=colors, width=0.5, zorder=3)
    notes = ["20~21배", "19~20배", "PEG 0.5", "−33%"]
    for b, n in zip(bars, notes):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.6, n, ha="center", fontsize=8, fontproperties=PROP)
    _style(ax, "알리바바 배수 — 싸지는 않음, PEG는 낮고 고점 대비 할인")
    _save(fig, path)


def chart_wolf(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    labels = ["매출 $M", "컨센 매출", "EPS×−10", "컨센 EPS×−10", "GM %", "AI DC QoQ"]
    vals = [d.WOLF["rev"], d.WOLF["cons_rev"], -d.WOLF["eps"] * 10, -d.WOLF["cons_eps"] * 10, d.WOLF["gm"], d.WOLF["ai_dc_qoq"]]
    colors = [NAVY2, GRAY, RED, AMBER, RED, GREEN]
    bars = ax.bar(labels, vals, color=colors, width=0.6, zorder=3)
    notes = ["149.6", "150", "−2.26", "−1.47", "−20%", "+20%"]
    for b, n, v in zip(bars, notes, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + (4 if v >= 0 else -8), n, ha="center", fontsize=7.5, fontproperties=PROP)
    ax.axhline(0, color="#9CA3AF", lw=0.6)
    _style(ax, "Wolfspeed FY4Q26 — 매출 부합, EPS·마진 크게 하회")
    _save(fig, path)


def chart_unitree(path: Path):
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    labels = ["정당화선\nPSR 60", "종가 PSR\n155", "PER\n850÷10"]
    vals = [60, 155, 85]
    bars = ax.bar(labels, vals, color=[GREEN, RED, AMBER], width=0.5, zorder=3)
    notes = ["CAGR 31%×2", "3418÷22억", "실제 850배"]
    for b, v, n in zip(bars, vals, notes):
        ax.text(b.get_x() + b.get_width() / 2, v + 3, n, ha="center", fontsize=8, fontproperties=PROP)
    _style(ax, f"유니트리 — 종가 ¥{d.UNITREE_PX} / IPO 대비 +{d.UNITREE_IPO_CHG}%  ·  PSR은 60배의 2.6배")
    _save(fig, path)


def chart_silicon2(path: Path):
    fig, ax = plt.subplots(figsize=(7.0, 3.5))
    labels = list(d.SIL_REG.keys())
    revs = [d.SIL_REG[k][0] / 100 for k in labels]
    yoy = [d.SIL_REG[k][1] for k in labels]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, revs, 0.36, color=NAVY2, label="매출 100억", zorder=3)
    ax.bar(x + 0.18, yoy, 0.36, color=GOLD, label="YoY %", zorder=3)
    ax.set_xticks(x)
    ax.set_xticklabels(["EU", "미국", "영국", "러시아"], fontproperties=PROP)
    ax.legend(prop=PROP)
    _style(ax, "실리콘투 상반기 지역 — 미국 모델을 유럽·영국으로 복제")
    _save(fig, path)


def chart_sndk_bb(path: Path):
    fig, ax = plt.subplots(figsize=(7.2, 3.5))
    keys = ["이미 매입", "기존 잔여", "신규 승인", "향후 여력"]
    vals = [d.SNDK_BB[k][0] for k in keys]
    pcts = [d.SNDK_BB[k][1] for k in keys]
    bars = ax.bar(keys, vals, color=[GRAY, NAVY2, GOLD, GREEN], width=0.55, zorder=3)
    for b, v, p in zip(bars, vals, pcts):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.25, f"${v:g}B\n{p}%", ha="center", fontsize=8)
    _style(ax, f"샌디스크 바이백 — 시총 ${d.SNDK_MCAP}B 대비 향후 여력 6.5% (8/13 ID가 본반등)")
    _save(fig, path)


def chart_foreign(path: Path):
    fig, ax = plt.subplots(figsize=(6.6, 3.4))
    labels = ["5/7~8/10\n누적 순매도", "8/11~최근\n5일 순매수"]
    vals = [-d.FOREIGN_SELL_TO_810, d.FOREIGN_5D_BUY]
    bars = ax.bar(labels, vals, color=[RED, GREEN], width=0.45, zorder=3)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + (-8 if v < 0 else 2), f"{v:+.1f}조", ha="center", fontsize=9, fontproperties=PROP)
    ax.axhline(0, color="#9CA3AF", lw=0.7)
    _style(ax, "코스피 외국인 — 116조 매도 뒤 5일 9.5조 매수. 거래량은 안 따라옴")
    _save(fig, path)


NEW_CHARTS = {
    "kospi_turnover": chart_kospi_turnover,
    "jgb": chart_jgb,
    "crash_2024": chart_crash_2024,
    "sess819": chart_sess819,
    "skh_hit60": chart_skh_hit60,
    "fcf_years": chart_fcf_years,
    "per_hdd": chart_per_hdd,
    "sca_asp": chart_sca_asp,
    "gp_bit": chart_gp_bit,
    "nvda_q2": chart_nvda_q2,
    "baba": chart_baba,
    "baba_mult": chart_baba_mult,
    "wolf": chart_wolf,
    "unitree": chart_unitree,
    "silicon2": chart_silicon2,
    "sndk_bb": chart_sndk_bb,
    "foreign": chart_foreign,
}


def render_all(out_dir: Path) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = c19.render_all(out_dir)
    for name, fn in NEW_CHARTS.items():
        dest = out_dir / f"{name}.png"
        fn(dest)
        written[name] = dest
    return written
