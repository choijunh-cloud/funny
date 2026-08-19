#!/usr/bin/env python3
"""8월 19일 Quick 코멘트 시각화 보고서(.docx + 차트 PNG) 생성."""

from __future__ import annotations

import os
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
import numpy as np
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Mm, Pt, RGBColor, Inches

# ── paths ──────────────────────────────────────────────────────
ROOT = Path("/workspace")
CHART_DIR = ROOT / "lectures" / "charts" / "aug19"
OUT_PATH = ROOT / "lectures" / "8월 19일 Quick코멘트 시각화보고서.docx"

KR_FONT = "NanumGothic"
FALLBACK = "DejaVu Sans"

NAVY = RGBColor(0x0F, 0x20, 0x43)
NAVY2 = RGBColor(0x1E, 0x40, 0x7C)
GOLD = RGBColor(0xB8, 0x94, 0x3A)
GRAY = RGBColor(0x4B, 0x55, 0x63)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x16, 0x65, 0x34)
RED = RGBColor(0x99, 0x1B, 0x1B)
AMBER = RGBColor(0x7A, 0x5C, 0x12)

NAVY_HEX = "0F2043"
NAVY2_HEX = "1E407C"
GOLD_HEX = "B8943A"
LIGHT_HEX = "EEF2F8"
GREEN_HEX = "E8F5E9"
RED_HEX = "FDECEA"
AMBER_HEX = "FFF8E7"
BLUE_HEX = "E8F1FB"
ROW_HEX = "F7F9FC"
WHITE_HEX = "FFFFFF"

# matplotlib palette
C_NAVY = "#0F2043"
C_NAVY2 = "#1E407C"
C_GOLD = "#B8943A"
C_GREEN = "#166534"
C_RED = "#991B1B"
C_BLUE = "#2563EB"
C_GRAY = "#6B7280"
C_LIGHT = "#EEF2F8"


def setup_matplotlib():
    font_dir = ROOT / "fonts"
    for name in ("NanumGothic.ttf", "NanumGothicBold.ttf"):
        fp = font_dir / name
        if fp.exists():
            font_manager.fontManager.addfont(str(fp))
    plt.rcParams["font.family"] = "NanumGothic"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 150
    plt.rcParams["savefig.dpi"] = 150
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["savefig.facecolor"] = "white"


# ── chart generators ───────────────────────────────────────────
def chart_macro_chain(path: Path):
    """유가 → 금리 → 반도체 전달 경로."""
    fig, ax = plt.subplots(figsize=(10, 3.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 3)
    ax.axis("off")

    boxes = [
        (0.3, "미·이란\n협상 불확실", C_RED),
        (2.0, "호르무즈\n리스크", C_RED),
        (3.7, "유가 상승\n(WTI $84~90+)", C_GOLD),
        (5.4, "인플레\n우려", C_GOLD),
        (7.1, "美 10Y·30Y\n국채 급등", C_NAVY2),
        (8.8, "고PER\n성장주 압박", C_NAVY),
    ]
    for x, label, color in boxes:
        rect = mpatches.FancyBboxPatch(
            (x, 0.9), 1.4, 1.2, boxstyle="round,pad=0.08",
            facecolor=color, edgecolor="white", linewidth=1.5, alpha=0.92,
        )
        ax.add_patch(rect)
        ax.text(x + 0.7, 1.5, label, ha="center", va="center", color="white",
                fontsize=9, fontweight="bold", linespacing=1.3)
    for x in range(5):
        ax.annotate("", xy=(boxes[x + 1][0], 1.5), xytext=(boxes[x][0] + 1.4, 1.5),
                    arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=2))

    ax.text(5, 0.25, "※ 8/19 장 막판: 10Y 4.708% (-0.34%p), 30Y 5.285% (-0.48%p) 반전",
            ha="center", fontsize=8.5, color=C_GRAY, style="italic")
    ax.set_title("매크로 전달 경로 — 유가 → 금리 → AI·반도체", fontsize=13,
                 fontweight="bold", color=C_NAVY, pad=12)
    fig.savefig(path)
    plt.close(fig)


def chart_bond_thresholds(path: Path):
    """10년물 금리 임계 구간."""
    fig, ax = plt.subplots(figsize=(9, 4))
    zones = [
        (4.0, 4.7, C_GREEN, "성장주\n부담 완화"),
        (4.7, 5.0, C_GOLD, "주의\n구간"),
        (5.0, 5.5, C_RED, "위험자산\n회피 구간"),
    ]
    for lo, hi, color, label in zones:
        ax.axvspan(lo, hi, alpha=0.35, color=color)
        ax.text((lo + hi) / 2, 0.55, label, ha="center", va="center",
                fontsize=10, fontweight="bold", color=C_NAVY)
    current = 4.708
    ax.axvline(current, color=C_NAVY, lw=2.5, linestyle="--", label=f"8/19 10Y = {current}%")
    ax.scatter([current], [0.55], s=120, color=C_NAVY, zorder=5)
    ax.set_xlim(3.9, 5.6)
    ax.set_ylim(0, 1)
    ax.set_xlabel("미국 10년물 국채 수익률 (%)", fontsize=11)
    ax.set_yticks([])
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title("단기 핵심 변수: 10년물 금리 임계 구간", fontsize=13,
                 fontweight="bold", color=C_NAVY)
    fig.savefig(path)
    plt.close(fig)


def chart_sector_rotation(path: Path):
    """섹터 로테이션 — 금리↓에도 기술주 약세."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    sectors = ["S&P500\n기술", "반도체\n(SOX)", "헬스케어\n(XBI)", "Moderna", "Merck"]
    changes = [-0.73, -2.12, 4.41, 77, 12.9]
    colors = [C_RED if c < 0 else C_GREEN for c in changes]
    bars = ax.bar(sectors, changes, color=colors, edgecolor="white", linewidth=1.2, width=0.6)
    for bar, val in zip(bars, changes):
        y = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, y + (1.5 if y > 0 else -3),
                f"{val:+.1f}%", ha="center", va="bottom" if y > 0 else "top",
                fontsize=10, fontweight="bold", color=C_NAVY)
    ax.axhline(0, color=C_GRAY, lw=0.8)
    ax.set_ylabel("등락률 (%)", fontsize=11)
    ax.set_title("8/19 美장: 금리 하락에도 AI→헬스케어 자금 이동", fontsize=13,
                 fontweight="bold", color=C_NAVY)
    ax.text(0.5, -0.12, "국채 바이백(20→40억$) → 10Y 4.64%, 30Y 5.19% 하락  |  그러나 기술주는 약세 지속",
            transform=ax.transAxes, ha="center", fontsize=8.5, color=C_GRAY)
    fig.savefig(path)
    plt.close(fig)


def chart_sk_buyback(path: Path):
    """SK하이닉스 주주환원 규모."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    # left: buyback vs market cap
    ax = axes[0]
    labels = ["40조\n자사주\n매입·소각", "잔여\n시가총액"]
    sizes = [40, 1160]
    colors_pie = [C_GOLD, C_LIGHT]
    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.1f%%", startangle=90,
        colors=colors_pie, explode=(0.06, 0), textprops={"fontsize": 9},
        wedgeprops=dict(edgecolor="white", linewidth=2),
    )
    for t in autotexts:
        t.set_fontweight("bold")
        t.set_color(C_NAVY)
    ax.set_title("40조원 = 발행주식 3.3%\n(EPS +3.4% 효과)", fontsize=11,
                 fontweight="bold", color=C_NAVY)

    # right: FCF return waterfall
    ax = axes[1]
    items = ["누적 FCF\n(25~27)", "50% 환원\n목표", "이미 확정\n40조", "추가 환원\n여지"]
    vals = [385, 192.5, 40, 152.5]
    x = np.arange(len(items))
    bar_colors = [C_NAVY2, C_NAVY, C_GOLD, C_GREEN]
    bars = ax.bar(x, vals, color=bar_colors, edgecolor="white", width=0.55)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                f"{val:.0f}조", ha="center", fontsize=9, fontweight="bold", color=C_NAVY)
    ax.set_xticks(x)
    ax.set_xticklabels(items, fontsize=8.5)
    ax.set_ylabel("조원", fontsize=10)
    ax.set_title("2025~27 FCF 50% 이상 환원", fontsize=11, fontweight="bold", color=C_NAVY)
    ax.set_ylim(0, 420)

    fig.suptitle("SK하이닉스 주주환원 — 역대 최대 40조 자사주 소각", fontsize=13,
                 fontweight="bold", color=C_NAVY, y=1.02)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def chart_fx_sensitivity(path: Path):
    """환율 민감도 비교."""
    fig, ax = plt.subplots(figsize=(8, 4.5))
    companies = ["SK하이닉스", "삼성전자"]
    eps_impact = [0.9, 0.4]
    bars = ax.barh(companies, eps_impact, color=[C_NAVY, C_NAVY2], height=0.45, edgecolor="white")
    for bar, val in zip(bars, eps_impact):
        ax.text(val + 0.03, bar.get_y() + bar.get_height() / 2,
                f"+{val}% EPS / 환율 +1%", va="center", fontsize=10, fontweight="bold", color=C_NAVY)
    ax.set_xlim(0, 1.2)
    ax.set_xlabel("원/달러 +1% 시 EPS 변화 (%)", fontsize=11)
    ax.set_title("환율 민감도 — SK하이닉스 > 삼성전자", fontsize=13,
                 fontweight="bold", color=C_NAVY)
    ax.axvline(0, color=C_GRAY, lw=0.5)
    fig.savefig(path)
    plt.close(fig)


def chart_fx_scenario(path: Path):
    """환율 시나리오별 EPS·이익 영향."""
    fig, ax1 = plt.subplots(figsize=(9, 4.5))
    rates = ["1,520\n(기준)", "1,420\n(-100원)", "1,360\n(하단)", "1,340\n(추가강세)"]
    sk_eps_chg = [0, -5.9, -9.5, -11.2]
    profit_adj = [0, 21, 16.3, 24]

    x = np.arange(len(rates))
    w = 0.35
    b1 = ax1.bar(x - w / 2, sk_eps_chg, w, label="SK하이닉스 EPS 변화 (%)", color=C_NAVY, alpha=0.85)
    ax2 = ax1.twinx()
    b2 = ax2.bar(x + w / 2, profit_adj, w, label="순이익 조정 가능 (조원)", color=C_GOLD, alpha=0.85)

    ax1.set_ylabel("EPS 변화 (%)", fontsize=10, color=C_NAVY)
    ax2.set_ylabel("이익 조정 (조원, 27년 기준)", fontsize=10, color=C_GOLD)
    ax1.set_xticks(x)
    ax1.set_xticklabels(rates, fontsize=9)
    ax1.axhline(0, color=C_GRAY, lw=0.8)
    ax1.set_title("환율 하락 시나리오 — SK하이닉스 EPS·이익 영향", fontsize=13,
                  fontweight="bold", color=C_NAVY)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left", fontsize=8)

    for bar in b1:
        h = bar.get_height()
        if h != 0:
            ax1.text(bar.get_x() + bar.get_width() / 2, h - 0.8, f"{h:.1f}%",
                     ha="center", fontsize=8, color="white", fontweight="bold")
    fig.savefig(path)
    plt.close(fig)


def chart_fx_drivers(path: Path):
    """원화 강세 핵심 요인."""
    fig, ax = plt.subplots(figsize=(9, 4))
    factors = ["국내\n달러공급↑", "수출기업\n달러매도", "환헤지\n비중↑", "고환율\n추가매도", "달러인덱스\n하락(96~97)"]
    impact = [95, 85, 70, 65, 55]
    colors = plt.cm.Blues(np.linspace(0.45, 0.9, len(factors)))[::-1]
    bars = ax.barh(factors[::-1], impact[::-1], color=colors[::-1], height=0.55, edgecolor="white")
    ax.set_xlim(0, 110)
    ax.set_xlabel("상대적 영향력 (정성)", fontsize=10)
    ax.set_title("달러-원 1,400원 하회 — 국내 수급이 핵심 변수", fontsize=13,
                 fontweight="bold", color=C_NAVY)
    ax.text(0.98, 0.02, "리스크: ①외국인 매도  ②미·이란/유가  ③1,350원 부근 달러 수요↑",
            transform=ax.transAxes, ha="right", fontsize=8, color=C_RED, style="italic")
    fig.savefig(path)
    plt.close(fig)


def chart_per_comparison(path: Path):
    """메모리·반도체 PER 비교."""
    fig, ax = plt.subplots(figsize=(10, 5))
    names = ["SK하이닉스\n(26년)", "SK하이닉스\n(27년)", "삼성전자\n(26년)", "삼성전자\n(27년)",
             "마이크론\n(CY27)", "Sandisk\n(FY27)", "SKHY ADR\n(27년)"]
    per26 = [4.3, 3.4, 5.2, 3.7, 6.25, 7.8, 5.2]
    per_cons = [5.1, None, 5.6, None, None, None, 7.7]

    x = np.arange(len(names))
    w = 0.35
    b1 = ax.bar(x - w / 2, per26, w, label="컨센 PER", color=C_NAVY, edgecolor="white")
    cons_x = [i for i, v in enumerate(per_cons) if v is not None]
    cons_v = [v for v in per_cons if v is not None]
    ax.bar([x[i] + w / 2 for i in cons_x], cons_v, w, label="보수 시나리오 PER",
           color=C_GOLD, edgecolor="white", hatch="//")

    for bar in b1:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.15, f"{h:.1f}x",
                ha="center", fontsize=8, fontweight="bold", color=C_NAVY)

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=8)
    ax.set_ylabel("PER (배)", fontsize=11)
    ax.set_title("8/19 밸류에이션 비교 — 국내 vs 해외 메모리 피어", fontsize=13,
                 fontweight="bold", color=C_NAVY)
    ax.legend(fontsize=9)
    ax.set_ylim(0, 9.5)
    fig.savefig(path)
    plt.close(fig)


def chart_marvell_broadcom(path: Path):
    """Marvell vs Broadcom."""
    fig, ax = plt.subplots(figsize=(7, 4))
    names = ["Marvell\n(MRVL)", "Broadcom\n(AVGO)"]
    changes = [9.9, -4.6]
    colors = [C_GREEN, C_RED]
    bars = ax.bar(names, changes, color=colors, width=0.45, edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars, changes):
        y = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, y + (0.3 if y > 0 else -1.2),
                f"{val:+.1f}%", ha="center", fontsize=12, fontweight="bold", color=C_NAVY)
    ax.axhline(0, color=C_GRAY, lw=0.8)
    ax.set_ylabel("등락률 (%)", fontsize=11)
    ax.set_title("Google TPU 생태계 — Marvell 협력 vs Broadcom 견제", fontsize=13,
                 fontweight="bold", color=C_NAVY)
    ax.text(0.5, -0.15, "Warrant 최대 5,897만주 · 행사가 $206.58 · 매출 $5억/tranche",
            transform=ax.transAxes, ha="center", fontsize=8.5, color=C_GRAY)
    fig.savefig(path)
    plt.close(fig)


def chart_hbm_debate(path: Path):
    """HBM 대체 기술 진행도."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    techs = ["Cerebras\n(온칩 SRAM)", "Groq\n(SRAM inference)", "NVIDIA+Groq\n(inference)", "KV Cache\n압축", "HBF/SSD\n계층화"]
    progress = [90, 88, 85, 82, 55]
    status = ["높음", "높음", "높음", "높음", "진행중"]
    colors = [C_GREEN if p >= 80 else C_GOLD for p in progress]
    bars = ax.barh(techs[::-1], progress[::-1], color=colors[::-1], height=0.55, edgecolor="white")
    for i, (bar, st) in enumerate(zip(bars, status[::-1])):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                st, va="center", fontsize=9, color=C_NAVY)
    ax.set_xlim(0, 105)
    ax.set_xlabel("대체·효율화 진행도 (정성)", fontsize=10)
    ax.set_title("HBM 가격 급등 → AI 업체의 HBM 의존도 축소 유인", fontsize=13,
                 fontweight="bold", color=C_NAVY)
    ax.text(0.5, -0.12, "핵심: SRAM ≠ HBM 완전 대체 → workload별 SRAM+HBM+DRAM+SSD 최적 조합",
            transform=ax.transAxes, ha="center", fontsize=8.5, color=C_GRAY, style="italic")
    fig.savefig(path)
    plt.close(fig)


def chart_kospi_flow(path: Path):
    """8/19 국내 시장 흐름."""
    fig, ax = plt.subplots(figsize=(9, 4))
    events = ["갭\n하락", "장중\n외국인\n매도", "선물\n막판\n매도축소", "SKHY\n40조\n발표", "NXT\n반등"]
    sentiment = [-80, -60, 20, 70, 50]
    colors = [C_RED if s < 0 else C_GREEN for s in sentiment]
    ax.plot(range(len(events)), sentiment, color=C_NAVY, lw=2, marker="o", markersize=8, zorder=3)
    for i, (ev, s, c) in enumerate(zip(events, sentiment, colors)):
        ax.scatter(i, s, s=150, color=c, zorder=4, edgecolors="white", linewidth=1.5)
        ax.text(i, s + (12 if s >= 0 else -18), ev, ha="center", fontsize=8.5, fontweight="bold", color=C_NAVY)
    ax.axhline(0, color=C_GRAY, lw=0.8, linestyle="--")
    ax.set_xticks([])
    ax.set_ylabel("시장 심리 (정성)", fontsize=10)
    ax.set_title("8/19 코스피 — 금리 쇼크 vs SK하이닉스 주주환원", fontsize=13,
                 fontweight="bold", color=C_NAVY)
    ax.set_ylim(-100, 90)
    fig.savefig(path)
    plt.close(fig)


def generate_all_charts() -> dict[str, Path]:
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    charts = {
        "macro_chain": CHART_DIR / "01_macro_chain.png",
        "bond_thresholds": CHART_DIR / "02_bond_thresholds.png",
        "sector_rotation": CHART_DIR / "03_sector_rotation.png",
        "sk_buyback": CHART_DIR / "04_sk_buyback.png",
        "fx_sensitivity": CHART_DIR / "05_fx_sensitivity.png",
        "fx_scenario": CHART_DIR / "06_fx_scenario.png",
        "fx_drivers": CHART_DIR / "07_fx_drivers.png",
        "per_comparison": CHART_DIR / "08_per_comparison.png",
        "marvell_broadcom": CHART_DIR / "09_marvell_broadcom.png",
        "hbm_debate": CHART_DIR / "10_hbm_debate.png",
        "kospi_flow": CHART_DIR / "11_kospi_flow.png",
    }
    chart_macro_chain(charts["macro_chain"])
    chart_bond_thresholds(charts["bond_thresholds"])
    chart_sector_rotation(charts["sector_rotation"])
    chart_sk_buyback(charts["sk_buyback"])
    chart_fx_sensitivity(charts["fx_sensitivity"])
    chart_fx_scenario(charts["fx_scenario"])
    chart_fx_drivers(charts["fx_drivers"])
    chart_per_comparison(charts["per_comparison"])
    chart_marvell_broadcom(charts["marvell_broadcom"])
    chart_hbm_debate(charts["hbm_debate"])
    chart_kospi_flow(charts["kospi_flow"])
    return charts


# ── docx helpers (from aug18 pattern) ──────────────────────────
def set_run_font(run, size=11, bold=False, color=DARK, italic=False, font=KR_FONT):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), KR_FONT)
    run._element.rPr.rFonts.set(qn("w:ascii"), font)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_pr.append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill}"/>'))


def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_pr.append(parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/>'
        f"</w:tcMar>"))


def set_table_borders(table, color="D0D7E2", sz="4"):
    tbl = table._tbl
    tbl_pr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>')
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f"</w:tblBorders>")
    tbl_pr.append(borders)


def cell_text(cell, text, size=10, bold=False, color=DARK, align="left"):
    cell.text = ""
    align_enum = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER,
                  "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
    for i, line in enumerate(str(text).split("\n")):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.alignment = align_enum
        run = p.add_run(line)
        set_run_font(run, size=size, bold=bold, color=color)
    set_cell_margins(cell)


def set_left_accent(cell, color=NAVY_HEX, sz="24"):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_pr.append(parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="nil"/><w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="nil"/><w:right w:val="nil"/></w:tcBorders>'))


class Report:
    def __init__(self):
        self.doc = Document()
        self._setup()

    def _setup(self):
        sec = self.doc.sections[0]
        sec.page_width = Mm(210)
        sec.page_height = Mm(297)
        sec.left_margin = Mm(16)
        sec.right_margin = Mm(16)
        sec.top_margin = Mm(16)
        sec.bottom_margin = Mm(16)
        normal = self.doc.styles["Normal"]
        normal.font.name = KR_FONT
        normal.font.size = Pt(11)
        normal._element.rPr.rFonts.set(qn("w:eastAsia"), KR_FONT)
        header = sec.header.paragraphs[0]
        header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = header.add_run("8/19 Quick 코멘트  ·  시각화 보고서")
        set_run_font(r, size=8.5, color=GRAY)
        footer = sec.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = footer.add_run("참고 자료  ·  투자 추천 아님  ·  ")
        set_run_font(r, size=8, color=GRAY)
        core = self.doc.core_properties
        core.title = "8월 19일 Quick 코멘트 시각화 보고서"
        core.author = "준혁"
        core.subject = "매크로·SK하이닉스·환율·메모리·섹터로테이션"

    def p(self, text, size=11, bold=False, color=DARK, space_after=6, align="left"):
        para = self.doc.add_paragraph()
        para.alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER,
                          "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
        para.paragraph_format.space_after = Pt(space_after)
        run = para.add_run(text)
        set_run_font(run, size=size, bold=bold, color=color)
        return para

    def h1(self, text, num=None):
        para = self.doc.add_paragraph()
        para.paragraph_format.space_before = Pt(14)
        para.paragraph_format.space_after = Pt(8)
        if num:
            run = para.add_run(f"{num}  ")
            set_run_font(run, size=16, bold=True, color=GOLD)
        run = para.add_run(text)
        set_run_font(run, size=16, bold=True, color=NAVY)
        pPr = para._p.get_or_add_pPr()
        pPr.append(parse_xml(
            f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="{NAVY_HEX}"/></w:pBdr>'))

    def h2(self, text):
        para = self.doc.add_paragraph()
        para.paragraph_format.space_before = Pt(10)
        para.paragraph_format.space_after = Pt(4)
        run = para.add_run(text)
        set_run_font(run, size=13, bold=True, color=NAVY2)

    def bullet(self, text, bold_lead=None):
        para = self.doc.add_paragraph()
        para.paragraph_format.left_indent = Cm(0.55)
        para.paragraph_format.first_line_indent = Cm(-0.35)
        para.paragraph_format.space_after = Pt(2.5)
        run = para.add_run("• ")
        set_run_font(run, color=NAVY2)
        if bold_lead:
            run = para.add_run(bold_lead)
            set_run_font(run, bold=True)
            run = para.add_run(text)
            set_run_font(run)
        else:
            run = para.add_run(text)
            set_run_font(run)

    def callout(self, title, body, kind="key"):
        palette = {"key": (NAVY_HEX, LIGHT_HEX, NAVY), "bull": ("166534", GREEN_HEX, GREEN),
                   "bear": ("991B1B", RED_HEX, RED), "note": (GOLD_HEX, AMBER_HEX, AMBER)}
        accent, fill, title_color = palette[kind]
        table = self.doc.add_table(rows=1, cols=1)
        cell = table.cell(0, 0)
        shade_cell(cell, fill)
        set_left_accent(cell, accent)
        set_cell_margins(cell, 80, 80, 120, 120)
        cell.text = ""
        p1 = cell.paragraphs[0]
        r = p1.add_run(title)
        set_run_font(r, size=10, bold=True, color=title_color)
        for line in (body if isinstance(body, list) else [body]):
            p = cell.add_paragraph()
            r = p.add_run(line)
            set_run_font(r, size=10.5)
        self.doc.add_paragraph()

    def table(self, headers, rows, col_widths=None):
        table = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_borders(table)
        for i, h in enumerate(headers):
            cell = table.rows[0].cells[i]
            shade_cell(cell, NAVY_HEX)
            cell_text(cell, h, size=9.5, bold=True, color=WHITE, align="center")
        for r_i, row in enumerate(rows):
            for c_i, val in enumerate(row):
                cell = table.rows[r_i + 1].cells[c_i]
                shade_cell(cell, ROW_HEX if r_i % 2 else WHITE_HEX)
                cell_text(cell, str(val), size=9.5, bold=(c_i == 0), align="left" if c_i == 0 else "center")
        if col_widths:
            for row in table.rows:
                for i, w in enumerate(col_widths):
                    row.cells[i].width = Cm(w)
        self.doc.add_paragraph()

    def image(self, path: Path, width_cm=16):
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run()
        run.add_picture(str(path), width=Cm(width_cm))
        para.paragraph_format.space_after = Pt(10)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(path))


def build_report(charts: dict[str, Path]):
    r = Report()

    # cover
    r.p("2026. 8. 19.  Quick 코멘트 정리", size=10.5, color=GRAY, align="center", space_after=4)
    r.p("시각화 보고서", size=22, bold=True, color=NAVY, align="center", space_after=2)
    r.p("매크로 · SK하이닉스 · 환율 · 메모리 · 섹터로테이션", size=12, color=NAVY2, align="center", space_after=10)

    r.callout("Executive Summary — 오늘 한 장", [
        "① 악재의 본질: AI 수요 훼손보다 '유가→금리→고PER 압박' + 차익실현.",
        "② 호재: SK하이닉스 40조 자사주 소각 + FCF 50% 이상 환원 → 삼성전자 기대감.",
        "③ 美장: 국채 바이백으로 금리 하락했으나 AI→헬스케어 섹터 로테이션.",
        "④ 환율: 국내 달러 공급이 핵심. 1,400원 하회, 추가 1,340~1,360 가능.",
        "⑤ 메모리: 캐시 우드·벤 톰슨의 HBM 가격 경고 — 단기 호재, 장기 대체 기술 촉진.",
    ])

    r.h2("오늘 핵심 숫자")
    r.table(
        ["항목", "숫자", "함의"],
        [
            ["SKHY 자사주", "40조원 / 3.3% / 3개월", "EPS +3.4%, 역대 최대 환원"],
            ["FCF 환원", "25~27 누적 385조 × 50%+", "추가 152.5조+ 환원 여지"],
            ["美 10Y", "4.708% (막판 -0.34%p)", "4.7% 이하 안정 = 성장주 완화"],
            ["달러-원", "1,412원대", "국내 수급 주도, 추가 하락 가능"],
            ["Marvell", "+9.9% vs AVGO -4.6%", "Google TPU 생태계 재편"],
            ["Moderna", "+77%", "AI→헬스케어 자금 이동"],
        ],
        col_widths=[3.5, 5.5, 8.6],
    )

    # 1 macro
    r.h1("매크로 — 유가·금리·반도체", "1.")
    r.image(charts["macro_chain"])
    r.image(charts["bond_thresholds"])
    r.callout("핵심 논리", [
        "미·이란 협상 불확실 → 호르무즈 → 유가 → 인플레 → 국채 금리 → 고PER 성장주 압박.",
        "8/19 장 막판 10Y·30Y 반전은 긍정적. 10Y 4.7% 이하 안정이 단기 최대 변수.",
        "5% 돌파·고착 시 AI/반도체 밸류에이션 조정 위험 확대.",
        "재무부 국채 바이백(20→40억$) = 단기 호재, 재정적자·AI CAPEX 구조적 요인은 잔존.",
    ])
    r.bullet("금리 상승 = AI 수요 약화(X). 높은 밸류에이션 + 차익실현(O).", bold_lead="해석: ")
    r.bullet("유진투자 허재환: '금리는 무죄' — 명목성장률(5~6%) 대비 금리는 아직 위기 수준 아님.")
    r.bullet("다만 6~7월 급락 상처 + 2주 +25% 급등 후 되돌림 심리가 강함.")

    # 2 market flow
    r.h1("국내 시장 — 8/19 장세", "2.")
    r.image(charts["kospi_flow"])
    r.bullet("전일 美 반도체 급락 → 코스피·코스닥 갭 하락, 외국인 매도 지속.")
    r.bullet("선물 막판 매도 급감(800억대) → 추가 하락 제한 시그널.")
    r.bullet("SK하이닉스 40조 발표 → NXT 반등, 삼성전자 주주환원 기대감.")

    # 3 SK Hynix
    r.h1("SK하이닉스 — 역대 최대 주주환원", "3.")
    r.image(charts["sk_buyback"])
    r.table(
        ["항목", "내용"],
        [
            ["자사주 매입", "40조원, 8/20~11/19, 전량 소각"],
            ["규모", "전체 주식 3.3% (약 2,407만주)"],
            ["일일 매입", "62영업일 × 6,452억원/일"],
            ["정책 변경", "FCF 50% 범위 → 50% 이상 환원"],
            ["추가 환원", "3Q26 실적발표 시 구체 공개"],
            ["주가 영향", "직관적 +5~9% (키옥시아·샌디스크 사례 참고)"],
        ],
        col_widths=[4.0, 13.6],
    )
    r.callout("주의", [
        "192.5조 = 2027년 일시 지급 아님. 2025~27 프로그램 기간 누적 환원.",
        "2028년 102.5조는 FCF 50% 참고치이며, 회사 정책 확정 아님.",
        "보수적 FCF(운전자본 차감) 기준 3년 누적 ~565조 → 50% 초과 환원.",
    ], kind="note")

    # 4 FX
    r.h1("환율 — 달러-원 하락과 민감도", "4.")
    r.image(charts["fx_drivers"])
    r.image(charts["fx_sensitivity"])
    r.image(charts["fx_scenario"])
    r.callout("핵심", [
        "달러 약세가 아니라 한국 달러 공급↑ → 원화 강세.",
        "법인세 납부·설비투자 원화 수요 + 수출기업 달러 매도 + 환헤지 → 하락 가속.",
        "추가 하락: 연준 금리인상 기대 후퇴 → DXY 99→96~97 → 달러-원 추가 하락.",
        "1,300원대 중반은 조건부. DXY 3~4% 하락 시 1,360, 달러 공급 지속 시 1,340대.",
    ])
    r.bullet("원화 추가 강세 리스크: ①외국인 매도  ②미·이란/유가  ③1,350원 부근 달러 수요↑")

    # 5 valuation
    r.h1("밸류에이션 — 삼전·하이닉스·해외 피어", "5.")
    r.image(charts["per_comparison"])
    r.table(
        ["종목", "가격", "26Y PER", "27Y PER", "27Y OP/EPS"],
        [
            ["SK하이닉스", "150만원", "4.3x", "3.4x", "392조 / 437K"],
            ["삼성전자", "24.75만원", "5.2x", "3.7x", "549조 / 67.2K"],
            ["마이크론", "$937", "7.5x Fwd", "6.25x", "CY27 EPS $150"],
            ["Sandisk", "$1,568", "—", "7.8x", "FY27 EPS $201"],
            ["SKHY ADR", "$163.8", "6.6x", "5.2x", "본주 대비 52% 프리미엄"],
        ],
        col_widths=[3.2, 2.8, 2.6, 2.6, 6.4],
    )
    r.bullet("보수 시나리오(27년 성장 0 가정) PER 6~7x → SKHY 208~242만, 삼전 28.7~33.5만.")

    # 6 sector rotation
    r.h1("美장 — 섹터 로테이션 & Marvell", "6.")
    r.image(charts["sector_rotation"])
    r.image(charts["marvell_broadcom"])
    r.bullet("Moderna mRNA 암백신 3상 성공 → MSD +12.9%, 헬스케어 섹터 급등.")
    r.bullet("금리↓ ≠ 기술주↑. AI/반도체 차익실현 → 헬스케어 자금 이동.")
    r.bullet("Google-Marvell TPU 협력: AI ASIC + Storage + NIC + Memory Interface.")
    r.bullet("OpenAI Q2 매출 $6.7B(+18% QoQ) but 영업손실 $12.3B — 성장 둔화 우려.")

    # 7 HBM debate
    r.h1("메모리 — HBM 논쟁 & 대체 기술", "7.")
    r.image(charts["hbm_debate"])
    r.callout("캐시 우드 + 벤 톰슨 논리", [
        "HBM 가격 급등 → AI 원가↑ → 고객사 HBM 의존도 축소 유인↑.",
        "벤 톰슨 비유: HBM 공급자 = 호르무즈 해협 — 과도한 가격은 장기적 대체 촉진.",
        "결론: '메모리주가 틀렸다'가 아니라 '현재 HBM 가격결정력이 영구적이라 가정하면 안 된다'.",
        "2026~28 초과이익 vs 2028+ 효율화·대체 기술 = 양날의 검.",
    ], kind="note")
    r.bullet("핵심 변수: AI 연산 증가율 − 메모리 효율 개선률.")

    # 8 other news
    r.h1("기타 종목·이슈", "8.")
    r.table(
        ["종목/이슈", "핵심", "투자 포인트"],
        [
            ["삼성 파운드리", "SF4/SF5/SF8 가격 10~15% 인상", "TSMC 포화·중국 수요·흑자전환 기대"],
            ["기가비스(420770)", "일본 기판사 89.5억 수주", "FC-BGA AOI/AOR, AI→기판 CAPEX"],
            ["이수페타시스", "2Q OP 771억(+83% YoY)", "Multi-Lam 7→11→20%+, 이익 레버리지"],
            ["LS", "2Q OP 5,956억(사상 최대)", "일렉트릭·전선·MnM·아이앤디 호조"],
            ["LG엔솔", "북미 EV→ESS 전환", "테슬라 메가팩 43억$ LFP 공급"],
            ["한화에어로", "美 MTC 자주포 단독 수주", "시제 1억$, 옵션 2.6억$, 양산 10조$"],
            ["유니트리 IPO", "커촹반 5배 급등", "PSR 155배, 상업화 검증 필요"],
        ],
        col_widths=[3.6, 6.4, 7.6],
    )

    # 9 checklist
    r.h1("앞으로 볼 변수 — 체크리스트", "9.")
    r.table(
        ["#", "변수", "관찰 포인트", "시장 영향"],
        [
            ["①", "美 10Y 금리", "4.7% 이하 안정 vs 5% 돌파", "성장주 밸류에이션"],
            ["②", "유가(WTI)", "$90 안정 vs $100+", "인플레→금리 악순환"],
            ["③", "미·이란", "협상/확전", "호르무즈·유가·금리"],
            ["④", "달러-원", "1,350~1,400 구간", "수출주 EPS·외국인 수급"],
            ["⑤", "SKHY 매입", "일 6,452억 집행", "지수·반도체 지지"],
            ["⑥", "NVIDIA 실적", "8/26, Rubin·마진·CAPEX", "AI 투자 심리"],
            ["⑦", "섹터 로테", "헬스케어 vs AI", "반도체 자금 유출 여부"],
        ],
        col_widths=[1.0, 3.0, 6.8, 6.8],
    )

    r.callout("종합", [
        "단기: 금리·유가·환율이 펀더멘탈을 압도하는 구간. SKHY 40조는 하방 지지.",
        "중기: AI CAPEX 지속 + 메모리/파운드리 가격결정력 + 주주환원 = 재평가 모멘텀.",
        "장기: HBM 가격이 대체 기술 촉진 → 메모리 업체 가격결정력 한계 경계.",
        "투자 접근: 보수적 분할, 27년 성장·환율·금리 3변수 동시 모니터링.",
    ])

    r.p("— 8월 19일 Quick 코멘트(00:02~23:50) 기준 시각화 정리. 투자 추천이 아닌 참고 자료입니다.",
        size=9.5, color=GRAY, align="right")
    r.save(OUT_PATH)


def main():
    setup_matplotlib()
    charts = generate_all_charts()
    build_report(charts)
    print(f"Charts: {CHART_DIR}")
    print(f"Report: {OUT_PATH} ({OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
