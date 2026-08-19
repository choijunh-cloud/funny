#!/usr/bin/env python3
"""8월 19일 Quick 코멘트 시각화 보고서(.docx) 생성."""

from __future__ import annotations

import io
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib import font_manager
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Mm, Pt, RGBColor, Inches

matplotlib.use("Agg")

OUT_PATH = Path("/workspace/lectures/8월 19일 시장 Quick 코멘트 보고서.docx")
CHART_DIR = Path("/workspace/lectures/.charts_aug19")
CHART_DIR.mkdir(parents=True, exist_ok=True)

KR_FONT = "WenQuanYi Micro Hei"
FALLBACK = "DejaVu Sans"

for fp in [
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
]:
    if Path(fp).exists():
        font_manager.fontManager.addfont(fp)
        KR_FONT = font_manager.FontProperties(fname=fp).get_name()
        break

plt.rcParams.update({
    "font.family": KR_FONT,
    "axes.unicode_minus": False,
    "figure.facecolor": "#FAFBFC",
    "axes.facecolor": "#FAFBFC",
})

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

C_NAVY = "#0F2043"
C_GOLD = "#B8943A"
C_GREEN = "#166534"
C_RED = "#991B1B"
C_BLUE = "#1E407C"
C_GRAY = "#94A3B8"


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
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f"</w:tcMar>"
    ))


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
        f"</w:tblBorders>"
    )
    tbl_pr.append(borders)


def set_left_accent(cell, color=NAVY_HEX, sz="24"):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_pr.append(parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="nil"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="nil"/>'
        f'<w:right w:val="nil"/>'
        f"</w:tcBorders>"
    ))


def cell_text(cell, text, size=10, bold=False, color=DARK, align="left"):
    cell.text = ""
    align_enum = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER, "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
    for i, line in enumerate(str(text).split("\n")):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.alignment = align_enum
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1)
        run = p.add_run(line)
        set_run_font(run, size=size, bold=bold, color=color)
    set_cell_margins(cell)


# ── Chart generators ──────────────────────────────────────────────

def save_chart(name: str) -> Path:
    path = CHART_DIR / f"{name}.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight", facecolor="#FAFBFC")
    plt.close()
    return path


def chart_macro_chain():
    fig, ax = plt.subplots(figsize=(10, 3.2))
    steps = ["미·이란\n긴장", "유가\n상승", "인플레\n우려", "미 국채\n금리↑", "고PER\n성장주\n밸류압박"]
    x = range(len(steps))
    colors = [C_NAVY, C_GOLD, C_RED, C_RED, C_BLUE]
    bars = ax.bar(x, [1]*5, color=colors, edgecolor="white", linewidth=2, width=0.65)
    ax.set_xticks(x)
    ax.set_xticklabels(steps, fontsize=10)
    ax.set_yticks([])
    ax.set_title("매크로 악재 전파 경로 (8/19)", fontsize=13, fontweight="bold", color=C_NAVY, pad=12)
    for i in range(len(steps)-1):
        ax.annotate("", xy=(i+0.45, 0.5), xytext=(i+0.55, 0.5),
                    arrowprops=dict(arrowstyle="->", color=C_GRAY, lw=2))
    ax.set_xlim(-0.5, 4.5)
    ax.spines[:].set_visible(False)
    return save_chart("01_macro_chain")


def chart_bond_yields():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    labels = ["10년물\n(안정 기준)", "10년물\n(8/19)", "30년물\n(8/19)", "위험\n임계치"]
    vals = [4.70, 4.75, 5.34, 5.00]
    colors = [C_GREEN, C_GOLD, C_RED, C_RED]
    bars = ax.barh(labels, vals, color=colors, height=0.55, edgecolor="white")
    ax.axvline(4.70, color=C_GREEN, ls="--", lw=1.5, alpha=0.7, label="안정 기준 4.7%")
    ax.axvline(5.00, color=C_RED, ls="--", lw=1.5, alpha=0.7, label="위험 임계 5.0%")
    for bar, v in zip(bars, vals):
        ax.text(v + 0.03, bar.get_y() + bar.get_height()/2, f"{v:.2f}%", va="center", fontsize=10, fontweight="bold")
    ax.set_xlim(4.4, 5.6)
    ax.set_xlabel("수익률 (%)", fontsize=10)
    ax.set_title("미국 장기국채 금리 — 단기 핵심 변수", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.legend(loc="lower right", fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save_chart("02_bond_yields")


def chart_treasury_buyback_effect():
    fig, ax = plt.subplots(figsize=(9, 4))
    phases = ["금리 급등\n(유가·재정)", "재무부\n바이백 2배", "장기금리\n진정", "성장주\n단기 호재"]
    y_before = [5.19, 4.64]
    y_after = [4.95, 4.55]
    x = [0, 1]
    ax.plot(x, y_before, "o-", color=C_RED, lw=2.5, markersize=10, label="30Y / 10Y (급등 구간)")
    ax.plot([1, 2, 3], [4.95, 4.70, 4.64], "s--", color=C_GREEN, lw=2, markersize=8, label="바이백 후 진정")
    ax.axhline(4.70, color=C_GREEN, ls=":", alpha=0.5)
    ax.axhline(5.00, color=C_RED, ls=":", alpha=0.5)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_xticklabels(phases, fontsize=9)
    ax.set_ylabel("금리 수준 (%)", fontsize=10)
    ax.set_title("재무부 국채 바이백 — 단기 완화 vs 구조적 고금리", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.legend(fontsize=9)
    ax.set_ylim(4.4, 5.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    note = "근본 원인(재정적자·AI CAPEX·인플레)은 미해결"
    ax.text(0.5, 0.02, note, transform=ax.transAxes, fontsize=9, color=C_RED, ha="center")
    return save_chart("03_treasury_buyback")


def chart_sector_rotation():
    fig, ax = plt.subplots(figsize=(9, 5))
    sectors = ["반도체\n(SOX)", "S&P500\n기술", "헬스케어\n(XBI/LABU)", "모더나\n(MRNA)"]
    changes = [-4.98, -0.73, 4.41, 77.0]
    colors = [C_RED if c < 0 else C_GREEN for c in changes]
    bars = ax.bar(sectors, changes, color=colors, edgecolor="white", linewidth=1.5, width=0.6)
    ax.axhline(0, color=C_GRAY, lw=1)
    for bar, v in zip(bars, changes):
        y = v + (3 if v > 0 else -5)
        ax.text(bar.get_x() + bar.get_width()/2, y, f"{v:+.1f}%", ha="center", fontsize=10, fontweight="bold")
    ax.set_ylabel("등락률 (%)", fontsize=10)
    ax.set_title("8/19 미국장 — 금리↓에도 기술주 약세 (섹터 로테이션)", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save_chart("04_sector_rotation")


def chart_sk_buyback():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.5))
    # Left: buyback breakdown
    labels = ["40조\n즉시 소각", "추가 환원\n(~152.5조)", "잔여 FCF\n(보유)"]
    sizes = [40, 152.5, 192.5]
    colors_pie = [C_NAVY, C_GOLD, C_GRAY]
    explode = (0.05, 0.02, 0)
    ax1.pie(sizes, explode=explode, labels=labels, autopct="%1.0f조", colors=colors_pie,
            startangle=90, textprops={"fontsize": 9})
    ax1.set_title("2025~27 누적 FCF 385조\n× 50% = 192.5조 환원", fontsize=11, fontweight="bold", color=C_NAVY)

    # Right: EPS effect
    categories = ["발행주식\n(현재)", "소각 후\n(-3.3%)"]
    shares = [100, 96.7]
    ax2.bar(categories, shares, color=[C_GRAY, C_NAVY], width=0.5, edgecolor="white")
    ax2.set_ylabel("상대 주식수 (%)", fontsize=10)
    ax2.set_ylim(90, 105)
    ax2.set_title("40조 소각 → EPS +3.4% 효과", fontsize=11, fontweight="bold", color=C_NAVY)
    for i, v in enumerate(shares):
        ax2.text(i, v + 0.5, f"{v}%", ha="center", fontweight="bold")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    fig.suptitle("SK하이닉스 주주환원 — 역대 최대 40조 자사주 소각", fontsize=13, fontweight="bold", color=C_NAVY, y=1.02)
    return save_chart("05_sk_buyback")


def chart_memory_per():
    fig, ax = plt.subplots(figsize=(9, 5))
    names = ["SK하이닉스\n(27년)", "삼성전자\n(27년)", "마이크론\n(CY27)", "샌디스크\n(FY27)", "SK하이닉스\nADR(27년)"]
    per = [3.4, 3.7, 6.25, 7.8, 5.2]
    colors = [C_NAVY, C_BLUE, C_GOLD, C_GOLD, C_GREEN]
    bars = ax.bar(names, per, color=colors, edgecolor="white", width=0.6)
    ax.axhline(6.0, color=C_RED, ls="--", lw=1.5, alpha=0.6, label="글로벌 메모리 Peer ~6~8배")
    for bar, v in zip(bars, per):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.15, f"{v:.1f}x", ha="center", fontweight="bold", fontsize=10)
    ax.set_ylabel("PER (배)", fontsize=10)
    ax.set_title("메모리 밸류에이션 비교 — 국내 vs 글로벌 Peer", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.legend(fontsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save_chart("06_memory_per")


def chart_fx_sensitivity():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    companies = ["삼성전자", "SK하이닉스"]
    eps_impact = [0.4, 0.9]
    colors = [C_BLUE, C_NAVY]
    bars = ax.bar(companies, eps_impact, color=colors, width=0.45, edgecolor="white")
    ax.set_ylabel("원/달러 +1% → EPS 변화 (%)", fontsize=10)
    ax.set_title("환율 민감도 — 원화 강세 시 EPS 영향", fontsize=13, fontweight="bold", color=C_NAVY)
    for bar, v in zip(bars, eps_impact):
        ax.text(bar.get_x() + bar.get_width()/2, v + 0.03, f"+{v}%", ha="center", fontweight="bold", fontsize=11)
    scenario = "1,520→1,420원 (-6.6%) 가정 시 SK하이닉스 EPS 약 -5.9%"
    ax.text(0.5, 0.95, scenario, transform=ax.transAxes, ha="center", fontsize=9,
            bbox=dict(boxstyle="round", facecolor="#FFF8E7", edgecolor=C_GOLD))
    ax.set_ylim(0, 1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save_chart("07_fx_sensitivity")


def chart_fx_scenario():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    levels = ["현재\n(~1,400)", "DXY -3~4%\n하단", "한국 달러\n공급 추가", "리스크\n(수요 증가)"]
    rates = [1400, 1360, 1345, 1350]
    colors = [C_NAVY, C_GREEN, C_GREEN, C_GOLD]
    ax.plot(range(4), rates, "o-", color=C_NAVY, lw=2.5, markersize=10)
    ax.fill_between(range(4), rates, 1300, alpha=0.1, color=C_GREEN)
    ax.axhspan(1340, 1360, alpha=0.15, color=C_GOLD, label="1,340~1,360원 시나리오")
    ax.set_xticks(range(4))
    ax.set_xticklabels(levels, fontsize=9)
    ax.set_ylabel("원/달러", fontsize=10)
    ax.set_title("달러-원 환율 시나리오 — 국내 수급이 핵심 변수", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.legend(fontsize=9)
    ax.set_ylim(1320, 1450)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save_chart("08_fx_scenario")


def chart_hbm_framework():
    fig, ax = plt.subplots(figsize=(9, 5))
    years = ["2024", "2025", "2026", "2027", "2028", "2029+"]
    hbm_price = [30, 55, 85, 100, 95, 70]
    alt_invest = [10, 15, 25, 40, 60, 80]
    ax.plot(years, hbm_price, "o-", color=C_NAVY, lw=2.5, markersize=8, label="HBM 가격결정력")
    ax.plot(years, alt_invest, "s--", color=C_GOLD, lw=2, markersize=7, label="대체기술 투자 (SRAM·압축·ASIC)")
    ax.fill_between(years, hbm_price, alpha=0.1, color=C_NAVY)
    ax.axvline("2028", color=C_RED, ls=":", lw=1.5, alpha=0.7)
    ax.text(4.5, 90, "양날의 검\n(초과이익→대체 가속)", fontsize=9, color=C_RED, ha="center")
    ax.set_ylabel("상대 지수 (100=기준)", fontsize=10)
    ax.set_title("HBM 가격 vs 대체기술 — 캐시 우드·벤 톰슨 프레임", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.legend(fontsize=9, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save_chart("09_hbm_framework")


def chart_marvell_broadcom():
    fig, ax = plt.subplots(figsize=(7, 4))
    names = ["Marvell\n(Google TPU)", "Broadcom\n(TPU 독점 견제)"]
    changes = [9.9, -4.6]
    colors = [C_GREEN, C_RED]
    bars = ax.bar(names, changes, color=colors, width=0.5, edgecolor="white")
    ax.axhline(0, color=C_GRAY, lw=1)
    for bar, v in zip(bars, changes):
        y = v + (0.5 if v > 0 else -0.8)
        ax.text(bar.get_x() + bar.get_width()/2, y, f"{v:+.1f}%", ha="center", fontweight="bold", fontsize=12)
    ax.set_ylabel("주가 등락 (%)", fontsize=10)
    ax.set_title("Google–Marvell 협력 vs Broadcom", fontsize=13, fontweight="bold", color=C_NAVY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save_chart("10_marvell_broadcom")


def chart_market_selloff():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    dates = ["7/31", "8/2", "8/5", "8/6"]
    nikkei = [39102, 36830, 31458, 34677]
    kospi = [2771, 2670, 2442, 2523]
    ax2 = ax.twinx()
    l1 = ax.plot(dates, nikkei, "o-", color=C_RED, lw=2, markersize=8, label="Nikkei")
    l2 = ax2.plot(dates, kospi, "s-", color=C_NAVY, lw=2, markersize=8, label="KOSPI")
    ax.set_ylabel("Nikkei", color=C_RED, fontsize=10)
    ax2.set_ylabel("KOSPI", color=C_NAVY, fontsize=10)
    ax.set_title("8월 초 급락·반등 — 레버리지 청산 vs 펀더멘털", fontsize=13, fontweight="bold", color=C_NAVY)
    lines = l1 + l2
    ax.legend(lines, [l.get_label() for l in lines], loc="lower left", fontsize=9)
    ax.annotate("8/5 투매\n(Nikkei -19%)", xy=(2, 31458), xytext=(2.3, 33000),
                arrowprops=dict(arrowstyle="->", color=C_RED), fontsize=9, color=C_RED)
    ax.annotate("8/6 반등\n(+10%)", xy=(3, 34677), xytext=(2.5, 37000),
                arrowprops=dict(arrowstyle="->", color=C_GREEN), fontsize=9, color=C_GREEN)
    ax.spines["top"].set_visible(False)
    return save_chart("11_market_selloff")


def chart_key_variables():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis("off")
    variables = [
        ("유가 (브렌트)", "$90 안정", "$100+ 위험", C_GREEN, C_RED),
        ("10년물 금리", "4.7% 이하", "5% 돌파", C_GREEN, C_RED),
        ("USD/JPY", "157~159 유지", "150↓ 엔캐리", C_GREEN, C_RED),
        ("AI 자금 흐름", "반도체 유지", "헬스케어 이동", C_GREEN, C_GOLD),
        ("환율 (원/달러)", "1,400~1,420", "1,340~1,360", C_GOLD, C_GREEN),
    ]
    y = 0.85
    ax.text(0.5, 0.97, "단기 핵심 변수 체크리스트", ha="center", fontsize=14, fontweight="bold", color=C_NAVY)
    for name, good, bad, cg, cr in variables:
        ax.add_patch(mpatches.FancyBboxPatch((0.05, y-0.08), 0.9, 0.12, boxstyle="round,pad=0.01",
                     facecolor="#EEF2F8", edgecolor=C_NAVY, linewidth=1))
        ax.text(0.08, y, name, fontsize=11, fontweight="bold", va="center", color=C_NAVY)
        ax.text(0.35, y, f"○ {good}", fontsize=10, va="center", color=cg)
        ax.text(0.65, y, f"× {bad}", fontsize=10, va="center", color=cr)
        y -= 0.16
    return save_chart("12_key_variables")


def chart_isu_petasys():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    quarters = ["1Q26", "2Q26", "수주잔고", "4Q26E"]
    multilam = [7, 11, 20, 25]
    ax.bar(quarters, multilam, color=[C_GRAY, C_BLUE, C_NAVY, C_GOLD], width=0.55, edgecolor="white")
    ax.set_ylabel("Multi-Lam 매출 비중 (%)", fontsize=10)
    ax.set_title("이수페타시스 — Multi-Lam 믹스 개선 (이익 레버리지)", fontsize=13, fontweight="bold", color=C_NAVY)
    for i, v in enumerate(multilam):
        ax.text(i, v + 0.5, f"{v}%", ha="center", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    return save_chart("13_isu_multilam")


def generate_all_charts():
    return [
        chart_macro_chain(),
        chart_bond_yields(),
        chart_treasury_buyback_effect(),
        chart_sector_rotation(),
        chart_sk_buyback(),
        chart_memory_per(),
        chart_fx_sensitivity(),
        chart_fx_scenario(),
        chart_hbm_framework(),
        chart_marvell_broadcom(),
        chart_market_selloff(),
        chart_key_variables(),
        chart_isu_petasys(),
    ]


# ── Document builder ────────────────────────────────────────────────

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
        r = footer.add_run("참고 자료  ·  투자 판단은 각자의 몫  ·  ")
        set_run_font(r, size=8, color=GRAY)

    def p(self, text, size=11, bold=False, color=DARK, space_after=6, align="left"):
        para = self.doc.add_paragraph()
        para.alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER, "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
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
        pPr.append(parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="12" w:space="4" w:color="{NAVY_HEX}"/></w:pBdr>'))
        return para

    def h2(self, text):
        para = self.doc.add_paragraph()
        para.paragraph_format.space_before = Pt(10)
        para.paragraph_format.space_after = Pt(4)
        run = para.add_run(text)
        set_run_font(run, size=13, bold=True, color=NAVY2)
        return para

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
        return para

    def flow(self, items):
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_before = Pt(4)
        para.paragraph_format.space_after = Pt(8)
        for i, item in enumerate(items):
            if i:
                run = para.add_run("   →   ")
                set_run_font(run, bold=True, color=GOLD)
            run = para.add_run(item)
            set_run_font(run, bold=True, color=NAVY)

    def callout(self, title, body, kind="key"):
        palette = {
            "key": (NAVY_HEX, LIGHT_HEX, NAVY),
            "bull": ("166534", GREEN_HEX, GREEN),
            "bear": ("991B1B", RED_HEX, RED),
            "note": (GOLD_HEX, AMBER_HEX, AMBER),
            "blue": (NAVY2_HEX, BLUE_HEX, NAVY2),
        }
        accent, fill, title_color = palette[kind]
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        shade_cell(cell, fill)
        set_left_accent(cell, accent, sz="28")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        cell.text = ""
        p1 = cell.paragraphs[0]
        r = p1.add_run(title)
        set_run_font(r, size=10, bold=True, color=title_color)
        for line in (body if isinstance(body, list) else [body]):
            p = cell.add_paragraph()
            r = p.add_run(line)
            set_run_font(r, size=10.5)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(6)

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
                shade_cell(cell, ROW_HEX if r_i % 2 == 1 else WHITE_HEX)
                cell_text(cell, str(val), size=9.5, bold=(c_i == 0), align="left" if c_i == 0 else "center")
        if col_widths:
            for row in table.rows:
                for i, w in enumerate(col_widths):
                    row.cells[i].width = Cm(w)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(8)

    def image(self, path: Path, width_cm=16, caption=None):
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run()
        run.add_picture(str(path), width=Cm(width_cm))
        if caption:
            cp = self.doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_after = Pt(10)
            r = cp.add_run(caption)
            set_run_font(r, size=9, color=GRAY, italic=True)
        else:
            self.doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(path))


def build(charts: list[Path]):
    r = Report()

    # Cover
    r.p("2026. 8. 19.  Quick 코멘트 시각화 보고서", size=10.5, color=GRAY, align="center", space_after=4)
    r.p("8월 19일 시장 종합", size=22, bold=True, color=NAVY, align="center", space_after=2)
    r.p("금리 · 주주환원 · 환율 · HBM 논쟁 · 섹터 로테이션", size=13, color=NAVY2, align="center", space_after=10)

    r.callout("오늘 한 장으로 보면", [
        "매크로: 미·이란 → 유가 → 금리 상승이 AI/반도체 밸류에이션을 압박. 재무부 바이백으로 단기 진정.",
        "이벤트: SK하이닉스 40조 자사주 소각 + FCF 50% 이상 환원 — 국내 증시 역대 최대 주주환원.",
        "섹터: 금리 하락에도 AI→헬스케어 자금 이동. HBM 장기 논쟁(캐시 우드·벤 톰슨) 부각.",
        "환율: 1,400원 돌파 — 국내 달러 공급이 핵심. 원화 추가 강세 시 EPS 조정 리스크.",
    ], kind="key")

    r.image(charts[11], width_cm=15.5, caption="[그림 12] 단기 핵심 변수 체크리스트")

    # Section 0: Summary table
    r.h1("오늘 숫자 한 장", num="0.")
    r.table(
        ["구분", "핵심 숫자", "한 줄 결론"],
        [
            ["SK하이닉스", "40조 소각 · FCF 50%+ 환원\n62영업일 × 6,452억/일", "역대 최대. +5~9% 반등 기대"],
            ["미 국채", "10Y 4.75% · 30Y 5.34%\n바이백 2배 확대", "단기 진정, 구조적 고금리 유지"],
            ["환율", "1,412원대 → 1,400↓\n1,520→1,420 시 EPS -5.9%", "국내 수급 > 달러인덱스"],
            ["메모리 PER", "SKHY 27Y 3.4x · Micron 6.3x", "글로벌 대비 할인 지속"],
            ["섹터", "SOX -4.98% · XBI +4.4% · MRNA +77%", "AI→헬스케어 로테이션"],
            ["Marvell", "+9.9% vs Broadcom -4.6%", "Google TPU 생태계 확장"],
        ],
        col_widths=[3.2, 6.8, 7.6],
    )

    # Section 1: Macro
    r.h1("매크로 — 금리·유가·지정학", num="1.")
    r.callout("한 줄 결론", [
        "핵심 악재는 전쟁 자체보다 '금리'. 미·이란 → 유가 → 인플레 → 국채금리 상승.",
        "10년물 4.7% 이하 안정이 단기 최대 변수. 5% 돌파 시 위험자산 전면 회피.",
        "재무부 바이백은 단기 호재이나, 재정적자·AI CAPEX·인플레 구조는 미해결.",
    ], kind="bear")

    r.image(charts[0], caption="[그림 1] 매크로 악재 전파 경로")
    r.image(charts[1], caption="[그림 2] 미국 장기국채 금리 수준")
    r.image(charts[2], caption="[그림 3] 재무부 바이백 효과 vs 구조적 한계")

    r.h2("유가 → 금리 → AI/반도체 연결고리")
    r.flow(["유가 $90 안정", "10Y 4.7%↓", "성장주 부담 완화"])
    r.flow(["유가 $100+", "10Y 5%+", "AI/반도체 밸류 조정"])
    r.bullet("미국 기준금리 동결이 주식시장에 최선. 추가 인상 기대 ↓ → 달러약세 → 원화강세 가능.")
    r.bullet("엔캐리: USD/JPY 157~159 유지 시 일본 금리 정상화 흡수. 150↓ 급락 시 2024년 8월형 청산 경계.")

    r.image(charts[10], caption="[그림 11] 8월 초 Nikkei/KOSPI 급락·반등 (레버리지 청산)")

    r.h2("금리는 무죄? (유진투자증권 허재환)")
    r.bullet("물가/금리 상승 = 수요가 좋다는 신호. 기업·주식시장에는 오히려 유리할 수 있음.")
    r.bullet("문제는 '이미 한참 올라온 다음'. 최근 급락은 금리보다 2주 +20% 급등 후 차익실현.")
    r.bullet("고금리 상처 극복 = 대규모 주주환원 OR 연준 적극 긴축(물가 안정 의지). → 오늘 SK하이닉스가 후자.")

    # Section 2: Market flow
    r.h1("시장 흐름 — 하락 · 로테이션 · 주주환원", num="2.")
    r.callout("마감 시장 정리", [
        "코스피 갭하락, 외국인 매도 지속. 장 막판 선물 매도 급감 → 추가 하락 제한 시그널.",
        "SK하이닉스 40조 발표 후 NXT 반등. 주주환원으로 금리 쇼크 일부 방어.",
        "미국: 금리↓에도 기술주 약세. AI→헬스케어 섹터 로테이션.",
    ], kind="key")

    r.image(charts[3], caption="[그림 4] 8/19 미국장 섹터 로테이션")

    r.h2("왜 금리↓인데 기술주가 안 올랐나")
    r.table(
        ["과거 공식", "이번 상황"],
        [
            ["장기금리 ↓ → 할인율 ↓ → 기술주 ↑", "금리↓ + 기술주↓ 동시 발생"],
            ["금리가 유일 변수", "섹터별 기대수익률·자금 흐름이 더 중요"],
            ["AI CAPEX 지속 = 반도체 매수", "모더나 mRNA 암백신 3상 → 헬스케어로 자금 이동"],
        ],
        col_widths=[7.0, 10.6],
    )
    r.bullet("모더나 +77~177%, MSD +12.9%, XBI +4.4%, LABU +13.5% — 52주 신고가.")
    r.bullet("OpenAI Q2 매출 $6.7B(+18% QoQ) but 영업손실 $9.3B→$12.3B 확대 → AI CAPEX 지속성 우려.")

    # Section 3: SK Hynix
    r.h1("SK하이닉스 — 40조 자사주 소각", num="3.")
    r.callout("역대 최대 주주환원", [
        "40조원 자사주 취득·소각 (발행주식 3.3%). 8/20~11/19, 62영업일 × 6,452억/일.",
        "2025~27 누적 FCF의 50% 이상 환원 (기존 '50% 범위 내' → '50% 이상').",
        "추가 환원 규모·방식은 3Q26 실적발표 시 공개. 특별배당 검토.",
        "ADR 발행 희석 → 40조 소각으로 SK스퀘어 지분율 복원 구조.",
    ], kind="bull")

    r.image(charts[4], caption="[그림 5] SK하이닉스 주주환원 구조")

    r.h2("FCF 환원 산식")
    r.table(
        ["항목", "금액", "비고"],
        [
            ["2025~27 누적 FCF (보수적)", "~565조", "운전자본·기타 20~30조 차감"],
            ["50% 환원 기준", "192.5조+", "3년 프로그램 기간"],
            ["이미 확정 (40조)", "40조", "8/20~11/19 소각"],
            ["추가 필요 (50% 기준)", "~152.5조+", "50% 초과 목표 → 더 클 수 있음"],
            ["2028년 102.5조", "참고치", "FCF 50% 적용 모델. 정책 아님"],
        ],
        col_widths=[5.0, 4.0, 8.6],
    )
    r.bullet("2/3항 규모 확대 반영 정도에 따라 +5~9% 상승 가능 (키옥시아·샌디스크 사례 참고).")
    r.bullet("순현금 ~69조 + 강력 FCF. '현 주가는 내재가치 대비 저평가' — 회사 공식 입장.")
    r.bullet("삼성전자 주주환원 기대감 동반 상승. 시장 밸류에이션 재평가 모멘텀.")

    # Section 4: Memory valuation
    r.h1("메모리 밸류에이션 · HBM 논쟁", num="4.")
    r.image(charts[5], caption="[그림 6] 메모리 PER 비교")

    r.h2("PER·EPS 비교 (8/19 기준)")
    r.table(
        ["종목", "가격", "26Y PER", "27Y PER", "27Y OP/EPS"],
        [
            ["SK하이닉스", "150만원", "4.3x", "3.4x", "392조 / 437K"],
            ["삼성전자", "24.75만원", "5.2x", "3.7x", "549조 / 67.2K"],
            ["SK하이닉스 ADR", "163.8달러", "6.6x", "5.2x", "본주 대비 52% 프리미엄"],
            ["마이크론", "937달러", "7.5x", "6.3x", "CY27 EPS 150달러"],
            ["샌디스크", "1,568달러", "-", "7.8x", "FY27 EPS 201달러"],
        ],
        col_widths=[3.2, 2.8, 2.4, 2.4, 5.8],
    )

    r.h2("캐시 우드 · 벤 톰슨 — '왜 메모리주를 사지 않는가'")
    r.callout("핵심 논리", [
        "HBM 가격 급등 → AI 원가↑ → 고객사 HBM 의존도↓ → 대체기술 투자 가속.",
        "벤 톰슨 비유: HBM 공급자 = 호르무즈 해협. 과도한 가격 → 장기적 공급망·기술 대체.",
        "반론: SRAM ≠ HBM. '대체'보다 '분업' — workload별 SRAM+HBM+DRAM+SSD 최적 조합.",
    ], kind="note")

    r.image(charts[8], caption="[그림 9] HBM 가격 vs 대체기술 투자 프레임")

    r.h2("이미 나타나는 현상")
    r.table(
        ["기술/기업", "내용", "진행도"],
        [
            ["Cerebras", "온칩 SRAM, HBM 의존↓", "🟢 높음"],
            ["Groq", "SRAM 기반 inference", "🟢 높음"],
            ["NVIDIA+Groq", "inference SRAM 구조 채택", "🟢 높음"],
            ["KV Cache 압축", "HBM 용량 감소", "🟢 높음"],
            ["HBF/SSD", "메모리 계층 다변화", "🟡 진행 중"],
        ],
        col_widths=[3.6, 8.0, 3.0],
    )
    r.callout("결론", [
        "2026~28: HBM 가격↑ = 메모리 업체 초과이익.",
        "2028+: 가격↑ 지속 → HBM 효율화·대체 기술 촉진 (양날의 검).",
        "AI 연산 증가율 − 메모리 효율 개선률 = 실제 수요. 단순 '수요 꺾임' 논리는 타당성 낮음.",
    ], kind="key")

    # Section 5: FX
    r.h1("환율 — 1,400원 돌파", num="5.")
    r.callout("왜 1,400원 아래?", [
        "① 국내 수급: 8월말 법인세·설비투자 원화수요 → 달러 매도 강화.",
        "② 수출기업 달러 매도 → 환헤지↑ → 환율↓ → 추가 매도 (가속).",
        "③ 한국 내부 요인 > 달러약세. 달러 공급↑가 먼저, DXY·엔화만으로 설명 어려움.",
    ], kind="blue")

    r.image(charts[6], caption="[그림 7] 환율 민감도 (EPS 영향)")
    r.image(charts[7], caption="[그림 8] 달러-원 추가 하락 시나리오")

    r.h2("2027년 순익 300~400조 가정 시 환율 영향")
    r.table(
        ["시나리오", "환율", "SK하이닉스 EPS", "이익 조정"],
        [
            ["기준", "1,520원", "기준", "-"],
            ["현재", "~1,420원", "약 -5.9%", "18~24조원"],
            ["26년 하반기 환율", "적용", "-", "16.3조 조정"],
        ],
        col_widths=[4.0, 3.6, 4.0, 5.8],
    )
    r.bullet("1,300원대 중반은 조건부: DXY -3~4% → 1,360원. 한국 달러 공급 추가 → 1,340원대.")
    r.bullet("원화 추가 강세 리스크: ① 외국인 매도 ② 미·이란/유가 ③ 1,350원 부근 달러 수요↑.")

    # Section 6: Individual stocks
    r.h1("개별 종목 · 산업 이슈", num="6.")

    r.h2("삼성전자 — 파운드리 가격 최대 15% 인상")
    r.table(
        ["공정", "인상폭", "배경"],
        [
            ["4nm (SF4)", "10~15% (중·美), 5~10% (대만)", "TSMC 포화, 중국 수요"],
            ["5nm (SF5)", "10~15%", "평택 SF4 풀가동"],
            ["8nm", "약 10%", "레거시"],
        ],
        col_widths=[3.6, 5.4, 8.6],
    )
    r.bullet("파운드리 흑자 전환 기대(내년). AI/HPC 비중 30%+. Google 4nm 협의 중.")

    r.image(charts[9], caption="[그림 10] Google–Marvell vs Broadcom")

    r.h2("Google–Marvell 협력")
    r.bullet("AI ASIC: 추론 가속기 + Storage Controller + NIC + Memory Interface + Near-memory Compute.")
    r.bullet("Warrant: Google에 최대 5,897만주, 행사가 $206.58. $5억 매출마다 1 tranche (FY27 Q3~FY33).")

    r.h2("기가비스 (420770) — FC-BGA 검사·수리")
    r.bullet("일본 기판업체 89.5억 계약 (매출대비 17.1%). AOI(검사)+AOR(레이저 수리). AI→FC-BGA→장비 수요.")

    r.image(charts[12], caption="[그림 13] 이수페타시스 Multi-Lam 비중 추이")

    r.h2("이수페타시스 — 2Q26 Review")
    r.table(
        ["항목", "2Q26", "포인트"],
        [
            ["매출", "3,799억 (+57% YoY)", "컨센 +4.9% 상회"],
            ["영업이익", "771억 (+83% YoY)", "OPM 20.3%"],
            ["Multi-Lam", "1Q 7% → 2Q 11%", "수주잔고 20%+"],
            ["Capa", "1,200→1,500→1,800억/월", "2027~28 로드맵"],
            ["판가", "+15% 협상", "하반기부터"],
        ],
        col_widths=[3.6, 5.4, 8.6],
    )

    r.h2("기타")
    r.bullet("LS: 2Q OP 5,956억(사상 최대). LS일렉트릭·전선·MnM·아이앤디 호조. 자사주 소각 논의.")
    r.bullet("LG에너지솔루션: 북미 EV→ESS 전환. 테슬라 메가팩 43억달러. 방산 배터리 검토.")
    r.bullet("한화에어로: 미 육군 MTC 자주포 시제 단독 수주(최대 18문, 10조원 규모 사업 진입).")
    r.bullet("유니트리: 상하이 커촹반 IPO 5배 급등. PSR 155배 vs 업계 60배. 상업화 검증이 관문.")

    # Section 7: NVIDIA preview
    r.h1("NVIDIA Q2 FY27 실적 프리뷰", num="7.")
    r.callout("관전 포인트", [
        "① AI 인프라 수요 지속? ② Hyperscaler CAPEX? ③ AI 기업 자금조달?",
        "④ 75% Gross Margin 유지? ⑤ Blackwell→Rubin 전환?",
        "Rubin: 3Q26 출하, 추론 35배, AI Factory 10배, 랙 $7~8.5M.",
        "Top 5 Hyperscaler 2027 CAPEX ≥$1T (+33%). Circular Financing 논쟁 지속.",
    ], kind="blue")

    # Section 8: Closing
    r.h1("종합 — 내일부터 볼 것", num="8.")
    r.callout("3가지 축", [
        "① 금리: 10Y 4.7% 이하 안정 + 재무부 바이백 지속 → 성장주 부담 완화.",
        "② 주주환원: SK하이닉스 40조 → 삼성전자 기대 → 국내 대형주 밸류 재평가.",
        "③ 섹터: AI CAPEX 훼손 < 금리 쇼크. 26일 NVIDIA 실적 + AI→헬스케어 로테이션 주시.",
    ], kind="key")

    r.h2("투자 접근 (코멘트 종합)")
    r.bullet("보수적: 증권사 TP 19만원선, 27년 성장 잠재력 중심 분할 접근.")
    r.bullet("26년 실적 기준 비쌈 → 27년 성장에 초점. 단기는 매크로(금리·유가·환율) 우선.")
    r.bullet("국내 기관: 대형주 exposure + 변압기/소부장 믹스 고민. AI 비중 줄이기는 임계점 전까지 어려움.")

    r.p("— 8월 19일 Quick 코멘트(06:20~23:50) 종합 · 시각화 보고서", size=9.5, color=GRAY, align="right")

    r.save(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    charts = generate_all_charts()
    build(charts)
