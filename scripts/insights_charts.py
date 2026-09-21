#!/usr/bin/env python3
"""8/18–9/20 스터디 인사이트 차트. 한글은 WenQuanYi / Noto CJK."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch, Circle

sys.path.insert(0, str(Path(__file__).resolve().parent))

import insights_data as D

OUT = Path("/workspace/lectures/assets/insights")
NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GREEN = "#166534"
RED = "#991B1B"
GRAY = "#4B5563"
BLUE = "#3B6F9E"
LIGHT = "#EEF2F8"
AMBER = "#B45309"
TEAL = "#0F766E"


def _kr_font_path() -> Path:
    # WenQuanYi keeps U+0020 between Hangul. Noto CJK collapses those spaces.
    wqy = Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
    if wqy.exists():
        return wqy
    return Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")


def _kr(s):
    if isinstance(s, str):
        return s.replace(" ", "\u3000")
    return s


def _font() -> None:
    p = _kr_font_path()
    if p.exists():
        font_manager.fontManager.addfont(str(p))
        name = font_manager.FontProperties(fname=str(p)).get_name()
        plt.rcParams["font.family"] = name
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["axes.edgecolor"] = "#D5DCE6"
    plt.rcParams["axes.labelcolor"] = NAVY
    plt.rcParams["xtick.color"] = GRAY
    plt.rcParams["ytick.color"] = GRAY
    if getattr(plt.Axes, "_insights_kr_patched", False):
        return

    _text = plt.Axes.text
    _title = plt.Axes.set_title
    _xlabel = plt.Axes.set_xlabel
    _ylabel = plt.Axes.set_ylabel
    _xticklabels = plt.Axes.set_xticklabels
    _yticklabels = plt.Axes.set_yticklabels
    _sup = matplotlib.figure.Figure.suptitle

    def text(self, x, y, s, *a, **k):
        return _text(self, x, y, _kr(s), *a, **k)

    def set_title(self, label, *a, **k):
        return _title(self, _kr(label), *a, **k)

    def set_xlabel(self, xlabel, *a, **k):
        return _xlabel(self, _kr(xlabel), *a, **k)

    def set_ylabel(self, ylabel, *a, **k):
        return _ylabel(self, _kr(ylabel), *a, **k)

    def set_xticklabels(self, labels, *a, **k):
        return _xticklabels(self, [_kr(x) for x in labels], *a, **k)

    def set_yticklabels(self, labels, *a, **k):
        return _yticklabels(self, [_kr(x) for x in labels], *a, **k)

    def suptitle(self, t, *a, **k):
        return _sup(self, _kr(t), *a, **k)

    plt.Axes.text = text
    plt.Axes.set_title = set_title
    plt.Axes.set_xlabel = set_xlabel
    plt.Axes.set_ylabel = set_ylabel
    plt.Axes.set_xticklabels = set_xticklabels
    plt.Axes.set_yticklabels = set_yticklabels
    matplotlib.figure.Figure.suptitle = suptitle
    plt.Axes._insights_kr_patched = True


def _save(fig, name: str) -> Path:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def _title(ax, text: str) -> None:
    ax.set_title(text, color=NAVY, fontsize=12, fontweight="bold", loc="left", pad=8)


def chart_01_corpus() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(11.0, 5.0))
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    items = D.CORPUS
    for i, (dt, title, sub, kind) in enumerate(items):
        r, c = divmod(i, 7)
        x, y = 0.12 + c * 0.98, 3.15 - r * 1.25
        col = GOLD if kind == "MAIN" else BLUE
        ax.add_patch(FancyBboxPatch((x, y), 0.90, 1.05, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    facecolor=LIGHT, edgecolor=col, lw=1.2))
        ax.text(x + 0.45, y + 0.78, dt, ha="center", fontsize=9, color=col, fontweight="bold")
        ax.text(x + 0.45, y + 0.48, title, ha="center", fontsize=8.2, color=NAVY, fontweight="bold")
        ax.text(x + 0.45, y + 0.20, sub, ha="center", fontsize=7.2, color=GRAY)
    _title(ax, "스터디 코퍼스  8/18 → 9/20   ·   금=MAIN  ·  청=위성")
    ax.text(0.99, 0.02, "커넥톰·봉직·클리닉 제외", transform=ax.transAxes, ha="right", fontsize=8, color=GRAY)
    return _save(fig, "01_corpus.png")


def chart_02_themes() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    names = [t["id"] + " " + t["title"] for t in D.THESES]
    # 반복 빈도: 후반으로 갈수록 매크로/토큰이 두꺼워짐 (스터디 등장 횟수 스케일)
    w = [9, 11, 7, 10, 8, 6, 5, 4]
    colors = [NAVY, NAVY2, TEAL, GOLD, BLUE, GREEN, AMBER, GRAY]
    bars = ax.barh(names[::-1], w[::-1], color=colors[::-1], height=0.62)
    ax.set_xlabel("스터디 세션에서 반복된 무게 (상대)")
    ax.set_xlim(0, 13)
    for b, v in zip(bars, w[::-1]):
        ax.text(v + 0.15, b.get_y() + b.get_height() / 2, str(v), va="center", fontsize=9, color=NAVY, fontweight="bold")
    _title(ax, "여덟 테제 — 반복될수록 두껍다")
    fig.tight_layout()
    return _save(fig, "02_themes.png")


def chart_03_frames() -> Path:
    _font()
    fig, axes = plt.subplots(1, 4, figsize=(10.2, 3.2))
    cards = [
        ("10Y", f"{D.TENY_FRAME:.2f}%", f"터치 {D.TENY_FRI_PRINT}", "안착 아님", NAVY),
        ("30Y", f"{D.THIRTY_Y_FRAME:.1f}%", "낙찰 5.308%", "프레임 6.0", NAVY2),
        ("TIPS", f"{D.TIPS_FRAME:.1f}%", "8/21  2.94%", "프레임 유지", TEAL),
        ("OIL", f"{D.OIL_SIREN:.0f}", f"WTI {D.FRI_WTI:.1f}", "사이렌 꺼짐", RED),
    ]
    for ax, (k, n, s, note, col) in zip(axes, cards):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.04, 0.08), 0.92, 0.84, boxstyle="round,pad=0.02,rounding_size=0.06",
                                    facecolor=LIGHT, edgecolor=col, lw=1.6))
        ax.text(0.5, 0.78, k, ha="center", fontsize=11, color=col, fontweight="bold")
        ax.text(0.5, 0.48, n, ha="center", fontsize=16, color=NAVY, fontweight="bold")
        ax.text(0.5, 0.28, s, ha="center", fontsize=8.5, color=GRAY)
        ax.text(0.5, 0.14, note, ha="center", fontsize=8.5, color=AMBER)
    fig.suptitle("준혁 프레임은 덮어쓰지 않는다", color=NAVY, fontsize=12, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "03_frames.png")


def chart_04_siren() -> Path:
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.6))
    # 10Y working band
    ax = axes[0]
    ax.axhspan(D.TENY_WORKING_LO, D.TENY_WORKING_HI, color=GOLD, alpha=0.25, label="워킹 밴드")
    ax.axhline(D.TENY_SIREN, color=RED, ls="--", lw=1.4, label="사이렌 5.00")
    xs = ["9/8", "9/15", "9/16", "9/17", "9/18"]
    ys = [4.80, 5.041, 5.041, 4.94, 4.951]
    ax.plot(xs, ys, color=NAVY, marker="o", lw=2)
    ax.scatter(["9/18"], [D.TENY_FRI_PRINT], color=AMBER, s=70, zorder=4, label="장중 5.002")
    ax.set_ylim(4.7, 5.2)
    ax.set_ylabel("%")
    _title(ax, "10Y 터치 ≠ 안착")
    ax.legend(fontsize=7.5, frameon=False)
    # oil
    ax = axes[1]
    ax.bar(["WTI 9/18", "Brent 9/18", "사이렌"], [D.FRI_WTI, D.FRI_BRENT, D.OIL_SIREN],
           color=[NAVY2, BLUE, RED], width=0.55)
    ax.set_ylabel("$")
    _title(ax, "Oil 사이렌 120 · 미발화")
    for i, v in enumerate([D.FRI_WTI, D.FRI_BRENT, D.OIL_SIREN]):
        ax.text(i, v + 1.5, f"{v:.1f}", ha="center", fontsize=9, color=NAVY, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "04_siren.png")


def chart_05_and_gate() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    boxes = [
        (0.4, 3.6, "A. 10–20Y\n5.0–5.3% 추세 돌파", "#FDECEA"),
        (0.4, 1.2, "B. No Way Back\n되돌릴 수 없음", "#FDECEA"),
        (5.6, 2.4, "붕괴 조건\nAND 충족 시에만", "#EEF2F8"),
    ]
    for x, y, t, c in boxes:
        ax.add_patch(FancyBboxPatch((x, y), 3.6, 1.8, boxstyle="round,pad=0.04,rounding_size=0.15",
                                    facecolor=c, edgecolor=NAVY, lw=1.2))
        ax.text(x + 1.8, y + 0.9, t, ha="center", va="center", fontsize=10, color=NAVY, fontweight="bold")
    ax.annotate("", xy=(5.55, 3.3), xytext=(4.1, 4.5),
                arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
    ax.annotate("", xy=(5.55, 3.3), xytext=(4.1, 2.1),
                arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
    ax.text(5.0, 0.35, "9/18: 5% 터치 후 종가 4.951 · AND 미충족 · 사이렌 미발화",
            ha="center", fontsize=9, color=GRAY)
    _title(ax, "Gravity Rules — 이은택 AND 게이트")
    return _save(fig, "05_and_gate.png")


def chart_06_kospi_box() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.8, 4.0))
    dates = ["6/22 고", "7/30 저", "9/3 포트", "9/18"]
    pxs = [D.KOSPI_PEAK, D.KOSPI_TROUGH, D.H2_ASOF_KOSPI, D.KOSPI_SEP18]
    ax.fill_between([-0.3, 3.3], D.BOX_LO, D.BOX_HI, color=GOLD, alpha=0.18, label="윤지호 박스 6,000–7,150")
    ax.plot(dates, pxs, color=NAVY, marker="o", lw=2.2, ms=8)
    for x, y in zip(dates, pxs):
        ax.text(x, y + 160, f"{y:,.0f}", ha="center", fontsize=8.5, color=NAVY, fontweight="bold")
    ax.axhline(D.BOX_HI, color=RED, ls=":", lw=1)
    ax.axhline(D.BOX_LO, color=GREEN, ls=":", lw=1)
    ax.set_ylabel("KOSPI")
    ax.set_ylim(5200, 9600)
    _title(ax, "W바닥 과정 · 박스 상단 8,000은 아직 안 연다")
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    fig.tight_layout()
    return _save(fig, "06_kospi_box.png")


def chart_07_memory_per() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.6, 4.0))
    labels = ["Sandisk\nFY27", "Micron\nCY27", "하이닉스\n27E", "삼성\n27E", "S&P\nFwd26"]
    aug = [D.AUG18_PER["sndk_fy27"], D.AUG18_PER["mu_cy27"], D.AUG18_PER["hynix_27"], D.AUG18_PER["samsung_27"], np.nan]
    sep = [D.SEP15_PER["sndk_fy27"], D.SEP15_PER["mu_cy27"], D.SEP15_PER["hynix_27"], D.SEP15_PER["samsung_27"], D.SEP15_PER["spx_fwd26"]]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, aug, width=0.36, color=NAVY2, label="8/18 부록")
    ax.bar(x + 0.18, sep, width=0.36, color=GOLD, label="9/15 스냅")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Forward PER (배)")
    ax.axhline(7, color=GRAY, ls=":", lw=1)
    _title(ax, "메모리 PER은 싸다기보다 이익이 눌렀다")
    ax.legend(frameon=False)
    fig.tight_layout()
    return _save(fig, "07_memory_per.png")


def chart_08_fair_band() -> Path:
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.4))
    specs = [
        ("하이닉스 본주 (만원)", D.HYNIX_SEP18 / 10000, 175, 242, 150, 260),
        ("삼성전자 (만원)", D.SAMSUNG_SEP18 / 10000, 28.7, 33.5, 24, 38),
    ]
    for ax, (name, spot, lo, hi, xmin, xmax) in zip(axes, specs):
        ax.hlines(0.5, lo, hi, color=GOLD, lw=14, alpha=0.7)
        ax.scatter([spot], [0.5], s=110, color=NAVY, zorder=3)
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(0, 1)
        ax.set_yticks([])
        ax.set_xlabel(name)
        ax.text(spot, 0.72, f"9/18  {spot:.1f}", ha="center", fontsize=9, color=NAVY, fontweight="bold")
        ax.text((lo + hi) / 2, 0.22, f"산식 밴드  {lo}–{hi}", ha="center", fontsize=8.5, color=GRAY)
    fig.suptitle("밸류 밴드 = 강의 산식  ·  IB/게스트 가격은 잠금 금지",
                 color=NAVY, fontsize=12, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "08_fair_band.png")


def chart_09_hbm() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    x = np.arange(2)
    w = 0.22
    ax.bar(x - w, D.CITI_DRAM_DEMAND, width=w, color=NAVY, label="DRAM 수요 %")
    ax.bar(x, D.CITI_DRAM_SUPPLY, width=w, color=NAVY2, label="DRAM 공급 %")
    ax.bar(x + w, D.CITI_HBM_BIT, width=w, color=GOLD, label="HBM bit %")
    ax.set_xticks(x)
    ax.set_xticklabels(["2027", "2028"])
    ax.set_ylabel("%")
    _title(ax, "Citi 9/18 — 수요가 공급을 앞선다 (인용)")
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    return _save(fig, "09_hbm.png")


def chart_10_token() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    labels = ["볼륨 MoM", "볼륨 YoY(배)", "지출 MoM", "지출 YoY(배)", "단가 MoM", "단가 YoY"]
    vals = [D.TOKEN_VOL_MOM, D.TOKEN_VOL_YOY_X, D.TOKEN_SPEND_MOM, D.TOKEN_SPEND_YOY_X, D.TOKEN_PRICE_MOM, D.TOKEN_PRICE_YOY]
    colors = [GREEN, GREEN, GREEN, GREEN, RED, RED]
    ax.barh(labels[::-1], vals[::-1], color=colors[::-1], height=0.6)
    ax.axvline(0, color=NAVY, lw=0.8)
    _title(ax, "토큰 P↓ Q↑  ·  8월 JPM/OpenRouter (9/18)")
    fig.tight_layout()
    return _save(fig, "10_token.png")


def chart_11_nvidia() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    labels = ["매출", "순이익", "OCF", "매출채권"]
    vals = [D.NVDA_REV, D.NVDA_NI, D.NVDA_OCF, D.NVDA_AR]
    colors = [NAVY, NAVY2, GOLD, AMBER]
    ax.bar(labels, vals, color=colors, width=0.55)
    ax.set_ylabel("$B")
    ax.text(1.5, D.NVDA_OCF + 4, f"OCF/NI {D.NVDA_OCF_NI}%  ·  DSO 45→60",
            ha="center", fontsize=9, color=AMBER, fontweight="bold")
    _title(ax, "엔비디아 Q2 FY27 — 인쇄는 이겼고 질문은 신용")
    fig.tight_layout()
    return _save(fig, "11_nvidia.png")


def chart_12_capex() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    labels = ["Dell 수주", "Dell 백로그", "Oracle RPO", "NVDA 공급약정"]
    vals = [D.DELL_ORDERS, D.DELL_BACKLOG, D.ORCL_RPO, D.NVDA_SUPPLY_COMMIT]
    ax.bar(labels, vals, color=[NAVY2, NAVY, GOLD, AMBER], width=0.55)
    ax.set_ylabel("$B")
    _title(ax, "CAPEX는 가이던스가 아니라 수주·백로그·약정으로 확인")
    fig.tight_layout()
    return _save(fig, "12_capex.png")


def chart_13_equipment() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    names = ["테스 신규수주", "테스 잔고", "한미 매출", "원익 1Q 잔고"]
    vals = [D.TES_NEW_ORDERS, D.TES_BACKLOG, D.HANMI_REV, D.WONIK_BACKLOG_1Q]
    ax.bar(names, vals, color=[NAVY, NAVY2, GOLD, TEAL], width=0.55)
    ax.set_ylabel("억원 (2Q26 강의)")
    ax.text(1.5, 4200, f"한미 OPM {D.HANMI_OPM}%  ·  가정 점유율 {D.HANMI_SHARE[0]}–{D.HANMI_SHARE[1]}%",
            ha="center", fontsize=9, color=NAVY)
    _title(ax, "소부장 — 2Q 숫자보다 수주가 매출로 바뀌는 속도")
    fig.tight_layout()
    return _save(fig, "13_equipment.png")


def chart_14_sk() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    labels = [n for n, _ in D.SK_ECO_SALES_MIX]
    sizes = [v for _, v in D.SK_ECO_SALES_MIX]
    colors = [NAVY, GOLD, NAVY2, TEAL]
    wedges, *_ = ax.pie(sizes, labels=labels, colors=colors, startangle=90,
                        wedgeprops=dict(width=0.48, edgecolor="white"),
                        textprops=dict(color=NAVY, fontsize=9))
    ax.text(0, 0, f"표 가치\n{D.SK_ECO_TABLE}조\n낮음", ha="center", va="center",
            fontsize=10, color=NAVY, fontweight="bold")
    _title(ax, "SK에코플랜트 1H26 매출 믹스 · 반도체 관련 ≈80%+")
    return _save(fig, "14_sk.png")


def chart_15_atlas() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.8, 3.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")
    nodes = ["신뢰성", "가동률", "데이터", "AI 성능", "추가 배치"]
    for i, n in enumerate(nodes):
        x = 0.6 + i * 1.85
        ax.add_patch(FancyBboxPatch((x, 1.05), 1.55, 0.95, boxstyle="round,pad=0.03,rounding_size=0.12",
                                    facecolor=LIGHT, edgecolor=NAVY, lw=1.2))
        ax.text(x + 0.78, 1.52, n, ha="center", va="center", fontsize=10, color=NAVY, fontweight="bold")
        if i:
            ax.annotate("", xy=(x, 1.52), xytext=(x - 0.28, 1.52),
                        arrowprops=dict(arrowstyle="->", color=GOLD, lw=2))
    ax.text(5, 0.35, "성능 논쟁 → Fleet × 가동률 × 데이터   ·   모비스 31 액추에이터 · 2028 HMGMA",
            ha="center", fontsize=9, color=GRAY)
    _title(ax, "Physical AI 데이터 플라이휠")
    return _save(fig, "15_atlas.png")


def chart_16_h2() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.8, 4.4))
    names = [r[0] for r in D.H2_TOP10][::-1]
    pw = [r[1] for r in D.H2_TOP10][::-1]
    colors = [GOLD if i >= 8 else NAVY2 for i in range(10)]
    ax.barh(names, pw, color=colors, height=0.62)
    ax.set_xlabel("확률가중 수익률 PW %  (9/3 as-of, 계산)")
    _title(ax, "하이브리드 H2 Top 10 — 신규자금은 한금융>네이버>모비스")
    fig.tight_layout()
    return _save(fig, "16_h2.png")


def chart_17_bookc() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(6.6, 3.8))
    labels = [n for n, _ in D.BOOK_C]
    vals = [v for _, v in D.BOOK_C]
    colors = [NAVY, NAVY2, GOLD, TEAL]
    ax.pie(vals, labels=[f"{n}\n{v}%" for n, v in D.BOOK_C], colors=colors,
           startangle=90, wedgeprops=dict(width=0.46, edgecolor="white"),
           textprops=dict(color=NAVY, fontsize=9))
    _title(ax, "절단된 사슬 Book C — oil은 비용, 정책경로는 절단")
    return _save(fig, "17_bookc.png")


def chart_18_power() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    ax.bar(["현재", "다음", "2030 수요", "2030 그리드"],
           [D.DC_GW[0], D.DC_GW[1], D.DC_2030_DEMAND, D.DC_2030_GRID],
           color=[NAVY2, NAVY, GOLD, RED], width=0.55)
    ax.set_ylabel("GW")
    ax.text(2.5, D.DC_2030_DEMAND + 12, f"갭 {D.dc_gap()} GW", ha="center", color=RED, fontweight="bold")
    _title(ax, "DC 전력 — TrendForce 인용 · 다음 영수증은 전력")
    fig.tight_layout()
    return _save(fig, "18_power.png")


def chart_19_flows() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    names = ["개인", "기관", "외인", "법인"]
    vals = [D.FLOW_RETAIL, D.FLOW_INST, D.FLOW_FOREIGN, D.FLOW_CORP]
    colors = [RED if v < 0 else GREEN for v in vals]
    ax.bar(names, vals, color=colors, width=0.55)
    ax.axhline(0, color=NAVY, lw=0.8)
    ax.set_ylabel("조원 (9/18)")
    _title(ax, "9/18 수급 — 개인 매도, 기관·외인·법인 받음")
    fig.tight_layout()
    return _save(fig, "19_flows.png")


def chart_20_export() -> Path:
    _font()
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.2))
    cards = [
        ("8월 반도체 YoY", f"+{D.SEMI_EXPORT_AUG_PCT:.0f}%", "18개월 연속", NAVY),
        ("8월 반도체 수출", f"${D.SEMI_EXPORT_AUG_B:.1f}B", f"총수출 ${D.TOTAL_EXPORT_AUG_B:.1f}B", GOLD),
        ("1–8월 비중", f"{D.SEMI_SHARE_YTD:.1f}%", "수출이 증명", NAVY2),
    ]
    for ax, (k, n, note, col) in zip(axes, cards):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.06, 0.12), 0.88, 0.76, boxstyle="round,pad=0.02,rounding_size=0.06",
                                    facecolor=LIGHT, edgecolor=col, lw=1.6))
        ax.text(0.5, 0.70, k, ha="center", fontsize=10, color=col, fontweight="bold")
        ax.text(0.5, 0.44, n, ha="center", fontsize=18, color=NAVY, fontweight="bold")
        ax.text(0.5, 0.24, note, ha="center", fontsize=9, color=GRAY)
    fig.suptitle("수출이 증명을 대신하고 있다", color=NAVY, fontsize=12, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "20_export.png")


def chart_21_leads() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.2, 3.6))
    names = [n for n, _ in D.LEAD_WEEKS]
    weeks = [w for _, w in D.LEAD_WEEKS]
    ax.barh(names[::-1], weeks[::-1], color=[GOLD if w >= 40 else NAVY2 for w in weeks][::-1], height=0.6)
    ax.set_xlabel("주")
    _title(ax, "리드타임 — 병목이 곧 노드, 노드가 곧 돈 (9/15)")
    fig.tight_layout()
    return _save(fig, "21_leads.png")


def chart_22_calendar() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")
    slots = [
        (0.3, 4.6, "9/28–30", "삼성 배당 창"),
        (2.7, 4.6, "9/29", "DevDay"),
        (5.1, 4.6, "10/1", "Micron"),
        (7.5, 4.6, "10월", "닉스 자사주"),
        (0.3, 2.4, "3Q 콜", "HS 현금"),
        (2.7, 2.4, "상시", "10Y AND"),
        (5.1, 2.4, "탐색", "Ohio 계약"),
        (7.5, 2.4, "2028", "HMGMA"),
    ]
    for x, y, a, b in slots:
        ax.add_patch(FancyBboxPatch((x, y), 2.15, 1.45, boxstyle="round,pad=0.03,rounding_size=0.12",
                                    facecolor=LIGHT, edgecolor=NAVY, lw=1.1))
        ax.text(x + 1.08, y + 0.95, a, ha="center", fontsize=11, color=GOLD, fontweight="bold")
        ax.text(x + 1.08, y + 0.45, b, ha="center", fontsize=9.5, color=NAVY)
    _title(ax, "확인 캘린더 — 숫자로 들어오는 날만 본다")
    return _save(fig, "22_calendar.png")


def chart_23_lock() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.3, 0.4), 4.5, 7.1, boxstyle="round,pad=0.04,rounding_size=0.12",
                                facecolor="#E8F5E9", edgecolor=GREEN, lw=1.2))
    ax.add_patch(FancyBboxPatch((5.2, 0.4), 4.5, 7.1, boxstyle="round,pad=0.04,rounding_size=0.12",
                                facecolor="#FDECEA", edgecolor=RED, lw=1.2))
    ax.text(2.55, 7.05, "잠근다", ha="center", fontsize=12, color=GREEN, fontweight="bold")
    ax.text(7.45, 7.05, "잠그지 않는다", ha="center", fontsize=12, color=RED, fontweight="bold")
    locked = [
        "9/18 종가·수급",
        "FOMC 점도표 · BOJ 1.25%",
        "NVDA/Dell/Oracle 공식",
        "사이렌 미발화",
        "준혁 프레임 5/6/3.0",
        "소부장 2Q 강의 숫자",
    ]
    unlocked = [
        "IB 310/400/59",
        "게스트 200만·29–30만",
        "UBS 90% 경로",
        "Ohio 계약 확정",
        "GDP 25% 공식화",
        "GPU = 2008",
    ]
    for i, t in enumerate(locked):
        ax.text(2.55, 6.2 - i * 0.95, "· " + t, ha="center", fontsize=9.2, color=NAVY)
    for i, t in enumerate(unlocked):
        ax.text(7.45, 6.2 - i * 0.95, "· " + t, ha="center", fontsize=9.2, color=NAVY)
    _title(ax, "합의 세탁 금지")
    return _save(fig, "23_lock.png")


def chart_24_evolve() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(9.0, 4.0))
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 8)
    ax.axis("off")
    for i, (when, what, line) in enumerate(D.EVOLUTION):
        y = 7.2 - i * 1.05
        ax.add_patch(Circle((0.7, y), 0.16, color=GOLD if i == len(D.EVOLUTION) - 1 else NAVY))
        if i < len(D.EVOLUTION) - 1:
            ax.plot([0.7, 0.7], [y - 0.18, y - 0.88], color="#D5DCE6", lw=2)
        ax.text(1.15, y + 0.18, f"{when}  ·  {what}", fontsize=10, color=NAVY, fontweight="bold", va="center")
        ax.text(1.15, y - 0.22, line, fontsize=8.6, color=GRAY, va="center")
    _title(ax, "관점 진화 — 수요 부정에서 조달·각도로")
    return _save(fig, "24_evolve.png")


def chart_25_darkgpu() -> Path:
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.5))
    ax = axes[0]
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("순방향", color=GREEN, fontweight="bold")
    seq = ["AI 수요", "투자", "GPU 구매"]
    for i, s in enumerate(seq):
        ax.add_patch(FancyBboxPatch((0.35 + i * 1.85, 1.4), 1.6, 1.1,
                                    boxstyle="round,pad=0.03,rounding_size=0.1",
                                    facecolor="#E8F5E9", edgecolor=GREEN))
        ax.text(1.15 + i * 1.85, 1.95, s, ha="center", va="center", color=NAVY, fontsize=10, fontweight="bold")
    ax = axes[1]
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 4)
    ax.axis("off")
    ax.set_title("역방향 레버리지", color=RED, fontweight="bold")
    seq = ["가동률↓", "임대료↓", "투자 축소"]
    for i, s in enumerate(seq):
        ax.add_patch(FancyBboxPatch((0.35 + i * 1.85, 1.4), 1.6, 1.1,
                                    boxstyle="round,pad=0.03,rounding_size=0.1",
                                    facecolor="#FDECEA", edgecolor=RED))
        ax.text(1.15 + i * 1.85, 1.95, s, ha="center", va="center", color=NAVY, fontsize=10, fontweight="bold")
    fig.suptitle("Dark GPU — 수요 부정이 아니라 과잉투자·금융 경고", color=NAVY, fontsize=12, fontweight="bold", x=0.02, ha="left")
    fig.tight_layout()
    return _save(fig, "25_darkgpu.png")


def chart_26_opm() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.0, 3.6))
    names = ["한미반도체", "리노공업"]
    vals = [D.HANMI_OPM, D.LEENO_OPM]
    ax.bar(names, vals, color=[GOLD, NAVY2], width=0.45)
    ax.set_ylabel("2Q26 OPM %")
    ax.set_ylim(0, 70)
    for i, v in enumerate(vals):
        ax.text(i, v + 1.5, f"{v}%", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(0.5, 62, "리노: 매출보다 마진 훼손이 핵심 (파업)", ha="center", fontsize=9, color=AMBER)
    _title(ax, "초고마진 소부장 — 숫자 자체보다 지속 조건")
    fig.tight_layout()
    return _save(fig, "26_opm.png")


CHARTS = [
    chart_01_corpus,
    chart_02_themes,
    chart_03_frames,
    chart_04_siren,
    chart_05_and_gate,
    chart_06_kospi_box,
    chart_07_memory_per,
    chart_08_fair_band,
    chart_09_hbm,
    chart_10_token,
    chart_11_nvidia,
    chart_12_capex,
    chart_13_equipment,
    chart_14_sk,
    chart_15_atlas,
    chart_16_h2,
    chart_17_bookc,
    chart_18_power,
    chart_19_flows,
    chart_20_export,
    chart_21_leads,
    chart_22_calendar,
    chart_23_lock,
    chart_24_evolve,
    chart_25_darkgpu,
    chart_26_opm,
]


def render_all() -> list[Path]:
    _font()
    return [fn() for fn in CHARTS]


if __name__ == "__main__":
    paths = render_all()
    for p in paths:
        print(p, p.stat().st_size)
