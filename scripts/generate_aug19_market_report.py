#!/usr/bin/env python3
"""Generate a visual briefing from the supplied 2026-08-19 quick comments.

This is a scenario report, not investment advice.  Values labelled "source
assumption" are reproduced from the supplied comments and intentionally are
not represented as independently verified facts.
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path("/workspace")
OUT = ROOT / "lectures/2026-08-19_시장_반도체_환율_통합브리핑.docx"
ASSET_DIR = ROOT / "lectures/.aug19_report_assets"

NAVY = "102A43"
BLUE = "2563EB"
TEAL = "0F766E"
GOLD = "B7791F"
RED = "B91C1C"
GRAY = "475569"
LIGHT = "F1F5F9"
FONT = "맑은 고딕"


def set_font(run, size=10.5, bold=False, color="172033"):
    run.font.name = FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    run._element.rPr.rFonts.set(qn("w:ascii"), FONT)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), FONT)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = RGBColor.from_string(color)


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell(cell, value, *, bold=False, color="172033", align="left", size=9.2):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT,
                   "center": WD_ALIGN_PARAGRAPH.CENTER,
                   "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    run = p.add_run(str(value))
    set_font(run, size=size, bold=bold, color=color)


def add_page_number(paragraph):
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)


class Report:
    def __init__(self):
        self.doc = Document()
        self._setup()

    def _setup(self):
        section = self.doc.sections[0]
        section.top_margin = Cm(1.5)
        section.bottom_margin = Cm(1.4)
        section.left_margin = Cm(1.55)
        section.right_margin = Cm(1.55)

        style = self.doc.styles["Normal"]
        style.font.name = FONT
        style._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
        style.font.size = Pt(10.5)

        header = section.header.paragraphs[0]
        header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = header.add_run("2026.08.19  |  MARKET & SEMICONDUCTOR BRIEFING")
        set_font(r, size=8.5, color=GRAY)
        footer = section.footer.paragraphs[0]
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = footer.add_run("원문 퀵코멘트 기반 시나리오 보고서  ·  ")
        set_font(r, size=8, color=GRAY)
        add_page_number(footer)

        props = self.doc.core_properties
        props.title = "2026년 8월 19일 시장·반도체·환율 통합 브리핑"
        props.author = "준혁"
        props.subject = "원문 퀵코멘트 재구성 보고서"

    def p(self, text="", *, size=10.5, bold=False, color="172033",
          align="left", after=5, before=0):
        p = self.doc.add_paragraph()
        p.alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT,
                       "center": WD_ALIGN_PARAGRAPH.CENTER,
                       "right": WD_ALIGN_PARAGRAPH.RIGHT}[align]
        p.paragraph_format.space_after = Pt(after)
        p.paragraph_format.space_before = Pt(before)
        p.paragraph_format.line_spacing = 1.15
        r = p.add_run(text)
        set_font(r, size=size, bold=bold, color=color)
        return p

    def heading(self, number, title):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(13)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(f"{number}.  ")
        set_font(r, size=15, bold=True, color=GOLD)
        r = p.add_run(title)
        set_font(r, size=15, bold=True, color=NAVY)

    def subheading(self, title):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(3)
        r = p.add_run(title)
        set_font(r, size=11.5, bold=True, color=BLUE)

    def callout(self, title, lines, fill="E8F1FB", accent=NAVY):
        table = self.doc.add_table(rows=1, cols=1)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        shade(cell, fill)
        set_cell(cell, title, bold=True, color=accent, size=10)
        for line in lines:
            p = cell.add_paragraph()
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.1
            r = p.add_run(line)
            set_font(r, size=9.7, color="172033")
        self.p("", after=2)

    def table(self, headers, rows, widths=None):
        table = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.style = "Table Grid"
        for i, h in enumerate(headers):
            shade(table.rows[0].cells[i], NAVY)
            set_cell(table.rows[0].cells[i], h, bold=True, color="FFFFFF",
                     align="center", size=8.8)
        for r_i, row in enumerate(rows):
            for c_i, value in enumerate(row):
                if r_i % 2:
                    shade(table.rows[r_i + 1].cells[c_i], LIGHT)
                set_cell(table.rows[r_i + 1].cells[c_i], value,
                         bold=(c_i == 0), align="left" if c_i == 0 else "center",
                         size=8.6)
        if widths:
            for row in table.rows:
                for i, width in enumerate(widths):
                    row.cells[i].width = Cm(width)
        self.p("", after=2)

    def image(self, path, width=6.85):
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(5)
        p.add_run().add_picture(str(path), width=Inches(width))

    def page_break(self):
        self.doc.add_page_break()

    def save(self):
        OUT.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(OUT)


def chart_style():
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.labelsize": 10,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
    })


def savefig(name):
    path = ASSET_DIR / name
    plt.tight_layout()
    plt.savefig(path, dpi=190, bbox_inches="tight", facecolor="white")
    plt.close()
    return path


def make_charts():
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    chart_style()
    paths = {}

    # FX sensitivity: delta in FX and EPS, based on provided 0.4% / 0.9% elasticities.
    fx = [-100, -60, -20, 0, 20, 60, 100]
    samsung = [x / 1520 * 100 * 0.4 for x in fx]
    hynix = [x / 1520 * 100 * 0.9 for x in fx]
    fig, ax = plt.subplots(figsize=(8.4, 3.7))
    ax.plot(fx, samsung, marker="o", linewidth=2.7, color="#" + BLUE, label="Samsung Electronics (0.4% EPS / 1% FX)")
    ax.plot(fx, hynix, marker="o", linewidth=2.7, color="#" + TEAL, label="SK hynix (0.9% EPS / 1% FX)")
    ax.axvline(-100, linestyle="--", color="#" + RED, alpha=.7)
    ax.annotate("1,520 → 1,420\n(-6.58%)", (-100, -5.9), xytext=(-92, -4.4),
                arrowprops={"arrowstyle": "->", "color": "#" + RED}, color="#" + RED, fontsize=9)
    ax.axhline(0, color="#94A3B8", linewidth=1)
    ax.set_title("FX sensitivity scenario: KRW/USD change vs EPS impact")
    ax.set_xlabel("KRW/USD change (KRW; base 1,520)")
    ax.set_ylabel("EPS change (%)")
    ax.grid(alpha=.2)
    ax.legend(loc="upper left", fontsize=8)
    paths["fx"] = savefig("fx_sensitivity.png")

    # Oil rate tech risk transmission diagram as a chart-like flow
    fig, ax = plt.subplots(figsize=(9, 2.45))
    ax.axis("off")
    labels = ["Iran escalation /\nHormuz risk", "Oil price ↑", "Inflation\nexpectations ↑",
              "US Treasury\n10Y yield ↑", "Long-duration /\nAI valuation ↓"]
    colors = ["FDE68A", "FCD34D", "FDBA74", "FB923C", "FCA5A5"]
    for i, (label, color) in enumerate(zip(labels, colors)):
        x = .02 + i * .198
        ax.text(x + .075, .51, label, ha="center", va="center", fontsize=9.5,
                fontweight="bold", bbox={"boxstyle": "round,pad=.65", "fc": "#" + color, "ec": "#64748B"})
        if i < len(labels) - 1:
            ax.annotate("", xy=(x + .19, .51), xytext=(x + .155, .51),
                        arrowprops={"arrowstyle": "->", "lw": 2, "color": "#64748B"})
    ax.text(.5, .08, "Key monitor: 10Y yield stabilising below 4.7% vs. a sustained move above 5.0%",
            ha="center", fontsize=10, color="#334155")
    paths["macro"] = savefig("macro_transmission.png")

    # HBM demand/efficiency scenarios
    fig, ax = plt.subplots(figsize=(8.4, 3.7))
    names = ["Compute +50%\nEfficiency +20%", "Compute +20%\nEfficiency +30%", "Base case\nDemand > efficiency"]
    values = [30, -10, 15]
    colors = [TEAL, RED, BLUE]
    bars = ax.bar(names, values, color=["#" + c for c in colors], width=.58)
    ax.axhline(0, color="#64748B", linewidth=1)
    ax.set_title("Memory demand impulse = AI compute growth − efficiency improvement")
    ax.set_ylabel("Illustrative net impulse (%p)")
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width()/2, v + (1.5 if v >= 0 else -3.5),
                f"{v:+d}%p", ha="center", va="bottom" if v >= 0 else "top", fontweight="bold")
    ax.grid(axis="y", alpha=.2)
    paths["memory"] = savefig("memory_efficiency.png")

    # Capital return waterfall
    fig, ax = plt.subplots(figsize=(8.4, 3.8))
    labels = ["25–27\ncumulative FCF", "50% minimum\nreturn", "Announced\nbuyback/cancel", "Potential\nadditional return"]
    vals = [385, -192.5, 40, 152.5]
    bottoms = [0, 385, 0, 0]
    # show headline FCF and derived distribution bridge separately to avoid suggesting a payout timing
    ax.bar([0], [385], color="#" + NAVY, width=.55)
    ax.bar([1], [192.5], color="#" + GOLD, width=.55)
    ax.bar([2], [40], color="#" + TEAL, width=.55)
    ax.bar([3], [152.5], color="#" + BLUE, width=.55)
    for i, val in enumerate([385, 192.5, 40, 152.5]):
        ax.text(i, val + 8, f"{val:g}T KRW", ha="center", fontweight="bold", fontsize=10)
    ax.set_xticks(range(4), labels)
    ax.set_ylim(0, 435)
    ax.set_ylabel("KRW trillion")
    ax.set_title("Capital-return arithmetic in supplied assumptions (not a payment schedule)")
    ax.grid(axis="y", alpha=.2)
    paths["return"] = savefig("capital_return.png")

    # dashboard / scenario matrix
    fig, ax = plt.subplots(figsize=(9, 4.1))
    ax.axis("off")
    rows = ["Macro", "FX", "Memory/HBM", "Capital return", "AI capex"]
    bull = ["10Y <4.7%, oil stabilises", "DXY falls + domestic USD supply", "Compute growth > efficiency gains",
            "Return >50% FCF + execution", "NVIDIA/Hyperscaler capex holds"]
    bear = ["10Y >5% persists, oil >$100", "Foreign selling + oil/geopolitics", "Efficiency / substitution wins",
            "Scale or timing not confirmed", "OpenAI monetisation/circular financing concern"]
    table = ax.table(cellText=[[r, b, be] for r, b, be in zip(rows, bull, bear)],
                     colLabels=["Variable", "Supportive scenario", "Risk scenario"],
                     colWidths=[.16, .42, .42], cellLoc="left", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(8.3)
    table.scale(1, 1.65)
    for (row, col), cell in table.get_celld().items():
        cell.set_edgecolor("#CBD5E1")
        if row == 0:
            cell.set_facecolor("#" + NAVY)
            cell.get_text().set_color("white")
            cell.get_text().set_weight("bold")
        elif col == 1:
            cell.set_facecolor("#ECFDF5")
        elif col == 2:
            cell.set_facecolor("#FEF2F2")
        elif col == 0:
            cell.set_facecolor("#F1F5F9")
            cell.get_text().set_weight("bold")
    ax.set_title("Decision dashboard: conditions matter more than a single headline", pad=16)
    paths["dashboard"] = savefig("scenario_dashboard.png")
    return paths


def build():
    charts = make_charts()
    r = Report()

    r.p("2026. 08. 19  |  QUICK COMMENT SYNTHESIS", size=10, color=GRAY, align="center", after=3)
    r.p("시장·반도체·환율", size=23, bold=True, color=NAVY, align="center", after=1)
    r.p("통합 브리핑", size=20, bold=True, color=BLUE, align="center", after=7)
    r.p("매크로 충격 · AI/메모리 논쟁 · 주주환원 · 원/달러 민감도", size=11, color=GRAY, align="center", after=12)
    r.callout("보고서 사용법", [
        "제공된 퀵코멘트를 논리 흐름과 수치 가정 중심으로 재구성했습니다.",
        "개별 뉴스·공시·증권사 추정치는 별도 사실 검증을 거치지 않았습니다. ‘원문 가정’으로 읽어야 합니다.",
        "특히 주주환원·순익·환율 숫자는 지급 확정 또는 투자 권유가 아닌, 원문상 시나리오 계산입니다.",
    ], fill="FFF7ED", accent=GOLD)
    r.subheading("한 페이지 결론")
    r.table(["축", "핵심 판단", "다음 확인"], [
        ["매크로", "전쟁 자체보다 유가 → 장기금리 → 성장주 할인율 경로가 단기 주가를 좌우", "미 10년물 4.7% 안정 vs. 5% 고착"],
        ["반도체", "AI 수요 훼손보다 HBM 가격·효율화·대체 기술의 장기 균형이 쟁점", "AI 연산 증가율 − 메모리 효율 개선률"],
        ["SK하이닉스", "원문 가정상 대규모 매입·소각과 FCF 50% 이상 환원이 재평가 재료", "3Q 추가 환원 방식·규모, 실행 진척"],
        ["환율", "국내 달러 공급과 달러인덱스가 함께 작용; 원화 강세는 수출주 EPS 역풍", "DXY, 외국인 수급, 유가, 1,350원대 달러수요"],
    ], [2.6, 9.0, 6.0])
    r.image(charts["dashboard"])

    r.heading("1", "매크로: ‘전쟁’보다 유가와 장기금리")
    r.p("원문은 최근 위험자산 조정을 AI 펀더멘털 훼손보다 ‘미·이란 불확실성 → 유가 → 인플레이션 우려 → 장기금리’의 할인율 충격으로 해석합니다. 단, 이는 인과관계의 하나의 해석이며 시장 하락을 단일 변수로 설명할 수는 없습니다.")
    r.image(charts["macro"])
    r.table(["관찰 구간", "해석", "반도체/성장주 함의"], [
        ["미 10년물 ≤ 4.7%", "할인율 부담 완화 가능", "밸류에이션 압력 완화; 실적·수급이 주도"],
        ["미 10년물 4.7~5.0%", "경계 구간", "금리·AI CAPEX·실적을 함께 확인"],
        ["미 10년물 > 5.0% 고착", "원문상 위험 경보", "장기 이익 의존 업종의 멀티플 조정 위험"],
        ["브렌트유 $90 부근", "안정 여부 확인", "인플레 기대가 재점화되지 않는지 점검"],
        ["브렌트유 $100 이상", "유가발 악순환 위험", "금리·리스크 프리미엄 동반 상승 가능"],
    ], [3.6, 5.5, 8.5])
    r.callout("실전 프레임", [
        "금리가 내려도 기술주가 반드시 오르지는 않습니다. 원문이 지적하듯 AI/반도체 차익실현과 헬스케어 등으로의 섹터 로테이션이 금리 효과를 상쇄할 수 있습니다.",
        "따라서 ‘금리 방향’만이 아니라, AI 주도주에서의 자금 유출입과 엔비디아 등 핵심 실적 이벤트를 동시 관찰해야 합니다.",
    ], fill="E8F1FB", accent=BLUE)

    r.heading("2", "환율: 국내 달러 공급과 수출주 EPS")
    r.p("원문은 1,400원 하향의 1차 동인으로 달러인덱스보다 국내 수급(법인세 납부·설비투자·수출기업 매도·환헤지)을 제시합니다. 추가 하락은 연준 기대 변화에 따른 DXY 99→96~97 가능성과 결합될 때라는 조건부 전망입니다.")
    r.image(charts["fx"])
    r.table(["원문상 가정", "계산", "해석"], [
        ["원/달러 1,520 → 1,420", "-100원 / -6.58%", "원화 강세 시나리오"],
        ["삼성전자 환율 민감도", "원/달러 +1% → EPS +0.4%", "원화 강세 시 EPS 약 -2.6% (기계적 계산)"],
        ["SK하이닉스 환율 민감도", "원/달러 +1% → EPS +0.9%", "원화 강세 시 EPS 약 -5.9% (기계적 계산)"],
        ["SK하이닉스 이익 조정", "27년 순익 300~400조 × -5.9%", "약 -18~24조원; 원문 시나리오"],
    ], [4.2, 5.4, 8.0])
    r.callout("표기 오류·한계", [
        "제공문에는 ‘삼성전자 환율 민감도’ 문장에 SK하이닉스가 반복 표기된 불일치가 있습니다. 본 보고서는 문맥에 맞춰 삼성전자 0.4%, SK하이닉스 0.9%를 입력값으로 처리했습니다.",
        "민감도는 매출 통화, 헤지, 원가 구조, 기간별 환율 평균에 따라 달라집니다. EPS 변화를 실제 실적 전망치 변경으로 바로 전환하면 안 됩니다.",
    ], fill="FEF2F2", accent=RED)
    r.table(["원화 추가 강세의 촉매", "원화 강세의 제약/리스크"], [
        ["DXY 3~4% 하락, 연준 인상 기대 되돌림", "외국인 국내주식 매도 확대"],
        ["국내 달러 공급·수출기업 매도 지속", "미·이란 갈등 및 유가 상승"],
        ["원문상 하단: 1,360원, 강한 수급이면 1,340원대", "1,350원 부근 달러 수요 증가 가능성"],
    ], [8.8, 8.8])

    r.heading("3", "AI 메모리: ‘수요 붕괴’가 아니라 효율화 유인의 문제")
    r.p("캐시 우드·벤 톰슨으로 요약된 원문의 반론은 ‘HBM 가격 상승이 당장 메모리 수요를 꺾는다’가 아닙니다. 가격이 높을수록 고객이 메모리 의존도를 낮추는 설계·압축·ASIC·계층화에 투자할 경제적 유인이 커진다는 장기 경고입니다.")
    r.image(charts["memory"])
    r.table(["논점", "원문상 판단", "투자 해석"], [
        ["HBM 가격 급등", "2026~28년 초과이익을 만들 수 있음", "단기 실적 호재"],
        ["SRAM vs HBM", "완전 대체보다 workload별 분업", "SRAM + HBM + DRAM + SSD 계층화"],
        ["대체/효율화", "Cerebras·Groq, KV cache 압축, SSD/HBF 활용", "28년 이후 구조적 가격결정력 리스크"],
        ["핵심 식", "AI 연산 증가율 − 메모리 효율 개선률", "양(+)이면 수요 증가, 음(-)이면 증가세 둔화"],
    ], [3.5, 7.2, 6.9])
    r.callout("균형 잡힌 결론", [
        "SRAM이 HBM을 한 번에 대체한다는 해석은 과도합니다. 최신 추론 시스템은 메모리 계층을 최적 조합하는 방향으로 발전합니다.",
        "다만 높은 HBM 가격이 영구적이라는 전제를 밸류에이션에 그대로 넣는 것도 위험합니다. ‘현재 실적’과 ‘장기 가격결정력’을 분리해야 합니다.",
    ], fill="ECFDF5", accent=TEAL)

    r.heading("4", "SK하이닉스 주주환원: 원문 가정의 산술과 확인 항목")
    r.p("원문은 40조원 자사주 취득·소각과 2025~27년 누적 FCF의 ‘50% 이상’ 환원을 핵심 재평가 요인으로 제시합니다. 아래 그래프는 원문에 등장한 385조원 누적 FCF 가정을 그대로 적용한 산술이며, 실제 지급 시기·형태를 나타내지 않습니다.")
    r.image(charts["return"])
    r.table(["항목", "원문 수치/계산", "해석상 주의"], [
        ["기발표 매입·소각", "40조원, 발행주식 대비 약 3.3%라는 원문 서술", "공시 원문과 주식수·취득기간 재확인 필요"],
        ["누적 FCF 가정", "2025~27년 약 385조원", "FCF 정의·운전자본·CAPEX 가정에 민감"],
        ["50% 이상 환원 산술", "385조 × 50% = 192.5조원 이상", "프로그램 기간 누적 기준; 2027년 단일 지급 아님"],
        ["추가 환원 산술", "192.5조 − 40조 = 약 152.5조원", "배당·추가 매입·특별배당의 배분은 미확정"],
    ], [3.4, 7.3, 6.9])
    r.callout("핵심 정정", [
        "‘2028년 FCF의 50%도 환원한다’는 결론은 제공문 스스로 부정합니다. 2028년 주주환원은 별도 정책이 필요합니다.",
        "원문 안에서도 FCF·순익 규모 및 회사명 표기에 혼재가 있으므로, 투자 판단 전 DART 공시와 회사 IR 원문을 기준으로 재검증해야 합니다.",
    ], fill="FEF2F2", accent=RED)

    r.heading("5", "반도체·AI 관련 종목: 촉매와 반증")
    r.table(["대상", "원문상 긍정 촉매", "반증/체크포인트"], [
        ["SK하이닉스", "대규모 소각·FCF 환원 강화·HBM 수요", "환율 역풍, HBM 효율화, 환원 실행 세부안"],
        ["삼성전자", "SF4 등 파운드리 단가 인상·고객 분산", "수율·가동률·실제 수주와 손익 전환"],
        ["Marvell", "Google TPU 생태계 내 커스텀 ASIC 영역 확대", "Broadcom 대체 강도·워런트 조건·매출 전환"],
        ["이수페타시스", "Multi-Lam 믹스, CAPA·판가 인상", "수율 안정화·고객 ASP·CAPEX 지속성"],
        ["기가비스", "FC-BGA 고사양화 및 검사·수리장비 수주", "글로벌 기판업체 CAPEX와 계약 매출화"],
    ], [3.2, 7.3, 7.1])
    r.p("공통적으로 ‘AI CAPEX가 계속된다’는 내러티브만으로 충분하지 않습니다. 각 기업은 주문·믹스·수율·가동률·현금환원처럼 확인 가능한 지표로 다음 단계에 진입했는지 봐야 합니다.", bold=True, color=NAVY)

    r.heading("6", "모니터링 대시보드와 시나리오")
    r.image(charts["dashboard"])
    r.table(["우선순위", "주간 확인 지표", "판단 기준"], [
        ["1", "미 10년물·브렌트유", "4.7% 하회 안정 / 5% 고착 여부, $90·$100 레벨"],
        ["2", "DXY·원/달러·외국인 수급", "국내 달러 공급의 지속성과 1,350원대 수요"],
        ["3", "엔/달러·일본 장기금리", "급격한 엔화 강세가 동반되면 엔캐리 청산 위험 재평가"],
        ["4", "AI CAPEX·엔비디아/하이퍼스케일러 가이던스", "매출 성장·마진·Rubin 램프·자금조달"],
        ["5", "HBM 가격·고객 효율화 신호", "수요 증가율이 효율 개선을 계속 웃도는지"],
        ["6", "SK하이닉스 3Q 환원 세부안", "40조 실행, 배당/추가 매입 규모, FCF 정의"],
    ], [1.8, 7.7, 8.1])
    r.callout("최종 결론", [
        "단기 시장은 ‘유가발 금리 쇼크’가 완화되는지에 좌우될 가능성이 높습니다. AI·메모리의 펀더멘털 논쟁은 실적보다 오래 지속될 구조적 이슈입니다.",
        "환율은 실적 상향의 역풍이 될 수 있고, 주주환원은 할인율을 낮추는 방어 재료가 될 수 있습니다. 둘을 같은 방향의 호재로 단순화하지 않는 것이 중요합니다.",
        "본 문서는 매수·매도 추천이 아닙니다. 원문 수치와 해석을 압축한 의사결정용 체크리스트입니다.",
    ], fill="E8F1FB", accent=NAVY)
    r.p("작성 기준: 사용자가 제공한 2026년 8월 19일 퀵코멘트. 외부 링크·공시·뉴스는 본 문서에서 독립 검증하지 않음.", size=8.3, color=GRAY, align="right", before=10)
    r.save()
    print(f"Wrote {OUT} ({OUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    build()
