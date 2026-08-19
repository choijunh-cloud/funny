#!/usr/bin/env python3
"""8월 19일 시장 Quick 코멘트 종합 리포트(.docx) 생성.

실행 전 scripts/generate_aug19_charts.py 로 차트를 먼저 생성해야 한다.
"""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Mm, Pt, RGBColor

CHART_DIR = Path("/workspace/reports/charts")
OUT_PATH = Path("/workspace/reports/8월 19일 시장 코멘트 리포트 (SK하이닉스 주주환원·금리·환율·HBM).docx")

KR_FONT = "맑은 고딕"

NAVY = RGBColor(0x0F, 0x20, 0x43)
NAVY2 = RGBColor(0x1E, 0x40, 0x7C)
GOLD = RGBColor(0xB8, 0x94, 0x3A)
GRAY = RGBColor(0x4B, 0x55, 0x63)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x16, 0x65, 0x34)
RED = RGBColor(0x99, 0x1B, 0x1B)

NAVY_HEX = "0F2043"
LIGHT_HEX = "EEF2F8"
GREEN_HEX = "E8F5E9"
RED_HEX = "FDECEA"
AMBER_HEX = "FFF8E7"
ROW_HEX = "F7F9FC"
WHITE_HEX = "FFFFFF"


def set_run_font(run, size=10.5, bold=False, color=DARK, italic=False):
    run.font.name = KR_FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), KR_FONT)
    run._element.rPr.rFonts.set(qn("w:ascii"), KR_FONT)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), KR_FONT)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def shade_cell(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_pr.append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill}"/>'))


def set_table_borders(table, color="D0D7E2", sz="4"):
    tbl_pr = table._tbl.tblPr
    tbl_pr.append(
        parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            + "".join(
                f'<w:{edge} w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
                for edge in ("top", "left", "bottom", "right", "insideH", "insideV")
            )
            + "</w:tblBorders>"
        )
    )


def cell_text(cell, text, size=9.5, bold=False, color=DARK, align="left"):
    cell.text = ""
    align_enum = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    for i, line in enumerate(str(text).split("\n")):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.alignment = align_enum
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        run = p.add_run(line)
        set_run_font(run, size=size, bold=bold, color=color)


def add_para(doc, text="", size=10.5, bold=False, color=DARK, align="left", space_before=2, space_after=4, italic=False):
    p = doc.add_paragraph()
    p.alignment = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    if text:
        run = p.add_run(text)
        set_run_font(run, size=size, bold=bold, color=color, italic=italic)
    return p


def add_rich_para(doc, parts, align="left", space_before=2, space_after=4):
    """parts = [(text, {kwargs})...]"""
    p = doc.add_paragraph()
    p.alignment = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
    }[align]
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    for text, kw in parts:
        run = p.add_run(text)
        set_run_font(run, **kw)
    return p


def add_heading(doc, number, title):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.columns[0].width = Cm(17.2)
    cell = t.cell(0, 0)
    cell.width = Cm(17.2)
    shade_cell(cell, NAVY_HEX)
    cell_text(cell, f"{number}.  {title}" if number else title, size=13, bold=True, color=WHITE)
    add_para(doc, "", size=4, space_before=0, space_after=2)


def add_subheading(doc, text):
    add_rich_para(
        doc,
        [("▎", dict(size=12, bold=True, color=GOLD)), (text, dict(size=11.5, bold=True, color=NAVY2))],
        space_before=8,
        space_after=3,
    )


def add_bullet(doc, text, size=10, color=DARK, bold=False, indent=0.4):
    p = add_rich_para(
        doc,
        [("·  ", dict(size=size, bold=True, color=GOLD)), (text, dict(size=size, bold=bold, color=color))],
        space_before=1,
        space_after=1,
    )
    p.paragraph_format.left_indent = Cm(indent)
    return p


def add_box(doc, title, body, fill=LIGHT_HEX, title_color=NAVY, body_color=DARK):
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.columns[0].width = Cm(17.2)
    cell = t.cell(0, 0)
    cell.width = Cm(17.2)
    shade_cell(cell, fill)
    set_table_borders(t, color="C9D2E0")
    cell.text = ""
    if title:
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(2)
        set_run_font(p.add_run(title), size=10.5, bold=True, color=title_color)
        first = False
    else:
        first = True
    for line in body.split("\n"):
        if first:
            p = cell.paragraphs[0]
            first = False
        else:
            p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2)
        set_run_font(p.add_run(line), size=9.8, color=body_color)
    add_para(doc, "", size=4, space_before=0, space_after=2)


def add_data_table(doc, headers, rows, widths=None, align_map=None, header_fill=NAVY_HEX, zebra=True):
    t = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t)
    total = 17.2
    widths = widths or [total / len(headers)] * len(headers)
    for ci, h in enumerate(headers):
        c = t.cell(0, ci)
        c.width = Cm(widths[ci])
        shade_cell(c, header_fill)
        cell_text(c, h, size=9.5, bold=True, color=WHITE, align="center")
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            c = t.cell(ri + 1, ci)
            c.width = Cm(widths[ci])
            if zebra and ri % 2 == 1:
                shade_cell(c, ROW_HEX)
            al = "left"
            if align_map:
                al = align_map[ci]
            cell_text(c, val, size=9.3, align=al)
    add_para(doc, "", size=4, space_before=0, space_after=2)
    return t


def add_chart(doc, filename, width=16.8, caption=None):
    path = CHART_DIR / filename
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(2)
    p.add_run().add_picture(str(path), width=Cm(width))
    if caption:
        add_para(doc, caption, size=8.5, color=GRAY, align="center", space_before=0, space_after=6)


# ──────────────────────────────────────────────────────────────────────────
def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Mm(210)
    sec.page_height = Mm(297)
    sec.top_margin = Cm(1.6)
    sec.bottom_margin = Cm(1.6)
    sec.left_margin = Cm(1.9)
    sec.right_margin = Cm(1.9)

    # ── 표지 헤더 ──
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = t.cell(0, 0)
    cell.width = Cm(17.2)
    shade_cell(cell, NAVY_HEX)
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    set_run_font(p.add_run("8월 19일 시장 Quick 코멘트 종합 리포트"), size=19, bold=True, color=WHITE)
    p2 = cell.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_run_font(p2.add_run("SK하이닉스 40조원 주주환원  ·  매크로의 역습(유가→금리)  ·  달러-원 1,400원 하회  ·  HBM 대체 논쟁"), size=10.5, color=RGBColor(0xC9, 0xD2, 0xE0))
    p3 = cell.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.space_after = Pt(14)
    set_run_font(p3.add_run("2026. 8. 19 (수)  |  Quick 코멘트 채널 정리  |  시각화 리포트"), size=9.5, color=GOLD)
    add_para(doc, "", size=6, space_before=0, space_after=2)

    # ── Executive Summary ──
    add_heading(doc, "", "오늘의 핵심 요약 (Executive Summary)")
    add_data_table(
        doc,
        ["테마", "핵심 내용", "시장 함의"],
        [
            (
                "SK하이닉스\n주주환원",
                "40조원 자사주 매입·소각(발행주식의 3.3%, 국내 역대 최대). 25~27년 누적 FCF의 '50% 이상' 환원으로 정책 강화, 특별배당 검토. 추가 규모는 3Q26 실적발표 시 공개",
                "EPS +3.4% 효과 + 밸류에이션 재평가 모멘텀.\n직관적 상승 여력 +5~9%. 삼성전자 주주환원 기대 강화",
            ),
            (
                "매크로\n(유가→금리)",
                "미·이란 불확실성 → 유가 상승 → 인플레 우려 → 미 10년물 4.75%, 30년물 5.34%까지 급등. 이후 재무부 장기채 바이백 2배 확대(20억→40억달러)로 진정",
                "10년물 4.7% 이하 안정 여부가 단기 최대 변수.\n5% 돌파·고착 시 AI/반도체 밸류 조정 위험",
            ),
            (
                "환율",
                "달러-원 1,400원 하회 — 달러 약세보다 한국의 강한 달러 공급(법인세·설비투자·수출기업 매도)이 주도. 하단 1,360원, 조건 충족 시 1,340원대",
                "원화 강세는 수출주 EPS 역풍(하이닉스 민감도 +1%당 0.9%). 너무 가파르면 3Q 원화약세 효과 소멸",
            ),
            (
                "HBM 논쟁",
                "캐시 우드·벤 톰슨: 'HBM 가격 급등이 대체 기술(SRAM·압축·경량화·ASIC) 투자를 자극' 경고. 반론: SRAM ≠ HBM, 대체보다 분업",
                "핵심 변수 = AI 연산 증가율 - 메모리 효율 개선률.\n26~28년 초과이익은 유효, '영구적 가격결정력' 가정은 경계",
            ),
            (
                "미국장·종목",
                "자금의 피벗: AI·반도체 → 헬스케어(모더나 +77%). 마벨 +9.9%(구글 협력) vs 브로드컴 -4.6%. 삼성 파운드리 최대 15% 가격 인상",
                "8/26 엔비디아 실적 전까지 AI 심리 재강화 vs 로테이션 지속 여부가 단기 변수",
            ),
        ],
        widths=[2.4, 8.2, 6.6],
    )

    # ── 1. SK하이닉스 ──
    add_heading(doc, "1", "SK하이닉스 — 40조원 자사주 매입·소각, 국내 증시 역대 최대 주주환원")
    add_subheading(doc, "공시 요약 (8/19 장 마감 후, DART)")
    add_data_table(
        doc,
        ["항목", "내용"],
        [
            ("취득·소각 규모", "40조원 (전일 종가 166.2만원 기준 약 2,407만주, 발행주식 7억 3,049만주의 약 3.3%)"),
            ("집행 기간", "8/20 ~ 11/19, 3개월 내 완료 후 전량 소각 — 현 주가 기준 62영업일간 일평균 약 6,452억원 매입"),
            ("정책 변경", "2025~27년 누적 FCF의 '50% 범위 내' → '50% 이상' 환원으로 강화. 고정배당 + 특별배당 확대 검토"),
            ("재무 여력", "2Q 말 순현금 약 69조원. '주가가 내재가치 대비 저평가' — 회사가 직접 명시"),
            ("추가 환원", "구체적 추가 규모·방식은 이사회 결의를 거쳐 3분기 실적발표 시점에 안내 예정"),
            ("구조적 효과", "주식수 3.3% 감소 → 동일 순이익 가정 시 EPS 약 +3.4%. ADR 발행으로 희석된 SK스퀘어 지분율 원상 복귀 구조"),
        ],
        widths=[3.2, 14.0],
    )
    add_chart(doc, "02_skh_buyback.png", caption="[차트 1] 소각 규모와 집행 스케줄")
    add_chart(doc, "01_skh_waterfall.png", caption="[차트 2] 주주환원 재원 추산 — 40조원은 시작일 가능성")
    add_box(
        doc,
        "해석 포인트",
        "① 192.5조원은 '2027년에 반드시 지급'이 아니라 25~27년 프로그램 기간 누적 환원 하한의 개념.\n"
        "② 이미 확정된 40조원을 빼면 50% 기준만으로도 약 152.5조원의 추가 환원이 필요. 회사는 '50% 초과'로 목표를 올렸음.\n"
        "③ 별도 FCF 모델(운전자본 등 보수 차감 후 150/210/205조원)로는 3년 누적 약 565조원 → 재원은 더 커질 수 있음.\n"
        "④ 상승폭은 '규모 확대 가능성'을 얼마나 반영하느냐에 좌우 — 직관적으로 +5~9% 사이. 키옥시아(8월 자사주 매입 후 누적 +7.4%)·"
        "샌디스크(Buyback 자체보다 Investor Day 재평가가 반등 동력) 사례 참고.",
    )
    add_subheading(doc, "ADR로 역산한 본주 적정가")
    add_data_table(
        doc,
        ["구분", "수치", "해석"],
        [
            ("ADR 8/19 종가", "156.16달러 (+0.3%)", "장중 +5.2%(163.8달러)까지 상승 후 반납. 시간외 +1%대 중반"),
            ("ADR 환산 주가", "약 228만원 (환율 1,390원 기준)", "본주(150만원) 대비 52% 프리미엄"),
            ("정상 프리미엄 +20% 가정", "본주 약 190만원", "TSMC ADR 프리미엄 15% 수준 참고"),
            ("최근 실제 30~35% 적용", "본주 약 169~175만원", "현 주가 대비 +13~17% 여력"),
        ],
        widths=[4.2, 5.4, 7.6],
    )

    # ── 2. 매크로 ──
    add_heading(doc, "2", "매크로의 역습 — 전쟁 · 유가 · 금리")
    add_chart(doc, "16_macro_flow.png", caption="[차트 3] 8/19 하락의 전달 경로")
    add_chart(doc, "03_rates.png", caption="[차트 4] 미 국채금리와 임계선 — 4.7% / 5.0%가 기준")
    add_box(
        doc,
        "이번 조정의 성격",
        "· 'AI 수요가 갑자기 약해졌다'(X) → '금리 상승으로 높은 밸류에이션이 압박받았다'로 단순화되기 쉽지만, 그마저도 타당성은 부족.\n"
        "· 메모리는 원래 AI 투자 지속성 우려로 사이클 특성을 반영한 낮은 밸류에이션이었음.\n"
        "· 국내 급락의 실제 배경: 2주 만에 코스피 +25%, 필라델피아 반도체 +21% 급등 후 차익 심리 + 6~7월 급락의 상처 미회복 + 반도체 실적 상향 정체.\n"
        "· 유진투자증권 허재환 '금리는 무죄': 미 명목성장률 5~6% 대비 기준금리 4~5%·장기금리 5~6%가 성장 타격 임계 — 부담은 커졌지만 위기는 아님.\n"
        "· 극복 경로는 두 가지: 기업의 대규모 주주환원(→ SK하이닉스가 실행) 또는 연준의 적극적 물가 대응.",
    )
    add_subheading(doc, "엔캐리 청산 가능성 점검 — 2024년 8월과의 비교")
    add_chart(doc, "04_yen_carry_2024.png", caption="[차트 5] 2024년 8월 사례 — 하루 만의 반등은 유동성 쇼크였다는 증거")
    add_box(
        doc,
        "판단 기준",
        "· USD/JPY가 159 → 155 → 150으로 빠르게 하락하며 Nikkei·KOSPI가 동시에 무너지면 → 2024년 8월형 엔캐리 청산을 본격 의심.\n"
        "· 반대로 현재처럼 157~159에서 반등하는 상태라면 → 1차 충격은 '글로벌 채권금리 상승/밸류에이션 압박' 성격.\n"
        "· 일본 금리가 올라도 엔화·미 금리가 안정되고 일본 국채 입찰이 견조하면 → 일본의 금리 정상화 과정으로 흡수될 가능성.",
        fill=AMBER_HEX,
    )
    add_box(
        doc,
        "핵심 3대 변수 (전쟁 → 유가 → 금리 → AI/반도체)",
        "① 10년물 미 국채금리: 4.7% 이하 안정 = 부담 완화  /  5% 돌파·고착 = 어떤 위험자산도 회피 국면.\n"
        "② 유가: 브렌트 $90 전후 안정 = 충격 완화  /  $100 이상 = 인플레·금리 악순환.\n"
        "③ 엔/달러 현 수준 유지 vs 150 초반 진입, 그리고 미·이란전 장기화 여부.\n"
        "→ 토큰 수요 확대 = AI 투자 GO는 웬만한 금리 상승에도 근본 궤도가 바뀔 가능성 낮음. 다만 이란발 금리 이슈 안정화까지는 채권시장의 목소리에 힘이 실리는 국면.",
        fill=RED_HEX,
        title_color=RED,
    )

    # ── 3. 환율 ──
    add_heading(doc, "3", "달러-원 — 1,400원 하회, 국내 수급이 주도")
    add_chart(doc, "17_fx_flow.png", caption="[차트 6] 환율 하락 메커니즘 — 달러인덱스·엔화만으로는 설명 불가")
    add_chart(doc, "05_fx_scenarios.png", caption="[차트 7] 하단 시나리오 — 1,300원대 중반은 조건부")
    add_chart(doc, "06_fx_sensitivity.png", caption="[차트 8] 환율 민감도 — 원화 강세는 수출주 이익의 역풍")
    add_box(
        doc,
        "이익 추정에 주는 함의",
        "· 환율 하락이 '너무 가파르면' 수출주의 원화약세 효과는 3Q부터 소멸 가능.\n"
        "· 1,520 → 1,420원 가정 시 SK하이닉스 EPS 약 -5.9% → 2027년 순익 300~400조원 가정이면 약 18~24조원의 이익 하향 조정 가능성 (26년 하반기 환율 기준으로는 16.3조원).\n"
        "· 추가 하락의 핵심 변수는 달러: 시장에 반영된 연준 금리 인상 기대(1~2회)가 되돌려지면 달러인덱스 99 → 96~97 → 달러-원 추가 하락 경로.",
    )

    # ── 4. HBM 논쟁 ──
    add_heading(doc, "4", "HBM 대체 논쟁 — '왜 메모리 주식을 사지 않는가' (캐시 우드 · 벤 톰슨)")
    add_data_table(
        doc,
        ["구분", "주장", "평가"],
        [
            (
                "캐시 우드\n(아크 인베스트)",
                "메모리 가격이 단기간 수배 급등하는 것은 긍정이 아닌 부정 신호. 급등이 지속될수록 AI 업계가 비용 절감 위해 대체 기술을 찾는 유인 확대",
                "'HBM이 비싸지면 수요가 곧 꺾인다' → 타당성 낮음\n'대체 기술 개발의 경제적 유인이 커진다' → 타당성 높음",
            ),
            (
                "벤 톰슨",
                "HBM 공급자를 이란·호르무즈 해협에 비유 — 가격을 과도하게 올리면 고객은 장기적으로 공급망·기술 대체를 찾는다",
                "'현재 메모리주가 틀렸다'가 아니라 '높은 가격결정력이 영구적이라 가정하면 안 된다'는 경고로 해석이 타당",
            ),
            (
                "대체 경로 4가지",
                "① SRAM 확대  ② 메모리 압축(KV Cache)  ③ 모델 경량화  ④ ASIC 개발",
                "헤게모니 프레임(메모리 vs 비메모리)으로 확산 시 수급 부담 가능성은 경계",
            ),
        ],
        widths=[3.0, 7.6, 6.6],
    )
    add_chart(doc, "07_hbm_variable.png", caption="[차트 9] 논쟁의 핵심 변수 — 연산 증가율과 효율 개선률의 경주")
    add_subheading(doc, "이미 현실에서 나타나는 현상")
    add_data_table(
        doc,
        ["사례", "내용", "현실성"],
        [
            ("Cerebras", "대규모 온칩 SRAM으로 HBM 의존도 축소 (실제 HBM 없이 구동)", "🟢 높음"),
            ("Groq", "SRAM 기반 inference 구조", "🟢 높음"),
            ("NVIDIA + Groq 기술", "inference 전용 SRAM 구조를 NVIDIA도 채택", "🟢 높음"),
            ("KV Cache 압축", "필요한 HBM 용량 감소 가능", "🟢 높음"),
            ("HBF/SSD 활용", "메모리 계층 다변화 (GPU HBM + CPU 메모리 + SSD 계층 활용)", "🟡 진행 중"),
        ],
        widths=[4.0, 10.0, 3.2],
        align_map=["left", "left", "center"],
    )
    add_box(
        doc,
        "결론",
        "· 가장 중요한 반론: SRAM ≠ HBM. 핵심은 '대체'보다 '분업' — workload에 따라 SRAM + HBM + DRAM + SSD의 최적 조합.\n"
        "· 'HBM 가격 상승은 2026~28년에는 메모리 업체의 초과이익을 만들지만, 지나치면 2028년 이후 효율화·대체 기술을 촉진하는 양날의 검.'\n"
        "· 글로벌 투자자가 AI 비중을 줄일 생각은 임계점 도달 전에는 하기 어려움. 선호 순서: 빅테크 → 파운드리 → 메모리 / 미국 → 일본 → 한국.",
        fill=GREEN_HEX,
        title_color=GREEN,
    )

    # ── 5. 밸류에이션 ──
    add_heading(doc, "5", "밸류에이션 — 컨센서스와 보수 시나리오")
    add_data_table(
        doc,
        ["구분", "영업이익 (컨센)", "EPS (컨센)", "보수적 시나리오"],
        [
            ("SK하이닉스\n(본주 150만원)", "26년 266조 / 27년 392조", "26년 346K / 27년 437K", "영업이익 250~260조\nEPS 290~300K → 27년 PER 5.1배"),
            ("삼성전자\n(24.75만원)", "26년 391조 / 27년 549조", "26년 47.9K / 27년 67.2K", "영업이익 355~370조\nEPS 43~45K → 27년 PER 5.6배"),
        ],
        widths=[3.6, 4.4, 4.4, 4.8],
    )
    add_chart(doc, "08_per_comparison.png", caption="[차트 10] 메모리 PER 비교 — 하이닉스 본주가 가장 낮은 구간")
    add_chart(doc, "09_target_bands.png", caption="[차트 11] '27년 성장 제로' 보수 가정 + 사이클 PER 6~7배 적용 밴드")

    # ── 6. 산업·종목 ──
    add_heading(doc, "6", "산업 · 종목 브리핑")
    add_subheading(doc, "6-1. 8/19 미국장 — 자금의 피벗 (AI·반도체 → 헬스케어)")
    add_chart(doc, "15_us_moves.png", caption="[차트 12] 장기금리 하락에도 기술주 약세 — 금리보다 강한 섹터 로테이션")
    add_box(
        doc,
        "왜 중요한가",
        "· 국채 바이백 → 장기금리 안정은 기술주에 우호적 환경이지만, AI·반도체 → 헬스케어 자금 이동이 이를 상쇄.\n"
        "· 모더나: MSD 키트루다 병용 개인맞춤형 mRNA 항암백신 임상 3상 성공 → NBI +4.86% 역사적 신고가. 국내 관련주: 알테오젠, 에스티팜, 올릭스 등.\n"
        "· 한국 투자자 관점: '장기금리 하락' 안도보다, AI·반도체에서 자금이 계속 빠지는지 + 8/26 엔비디아 실적 전 심리 재강화 여부 확인이 더 중요.",
    )
    add_subheading(doc, "6-2. Marvell × Google — TPU 생태계 공동 확장 (마벨 +9.9% / 브로드컴 -4.6%)")
    add_data_table(
        doc,
        ["항목", "내용"],
        [
            ("협력 확대", "7/29 커스텀 반도체 협력 확대 — AI 추론 가속기 + Storage Controller + NIC + Memory Interface Controller + Near-memory Compute로 TPU 주변 생태계 전체 확장"),
            ("Warrant 발행", "Google에 최대 5,897만주 매입권 부여, 행사가 $206.58 — 주가 상승 시 Google의 잠재적 이해관계 확대"),
            ("Vesting 조건", "Google 관련 Custom Products 매출 $5억마다 1 tranche — 매출 증가와 Marvell 주식 보상 연동. 기간 FY2027 Q3~FY2033 (장기 계약 성격)"),
            ("함의", "마벨의 커스텀 ASIC 사업이 '칩 설계'에서 AI 인프라 전반으로 확대 가능성 + 브로드컴의 Google TPU 독점 지위에 대한 견제 신호"),
        ],
        widths=[3.2, 14.0],
    )
    add_subheading(doc, "6-3. 삼성전자 — 첨단 파운드리 가격 최대 15% 인상 (로이터)")
    add_chart(doc, "10_foundry_price.png", caption="[차트 13] 공정별 신규 주문 가격 인상률")
    add_box(
        doc,
        "전망 — 삼성전자에 긍정적",
        "· 흑자 전환 기대: 2022년 이후 적자였던 파운드리가 단가 인상 + 수율 개선 + 가동률 상승으로 이르면 내년 흑자 전환 전망.\n"
        "· 올해 파운드리 매출 중 첨단공정 비중 절반 초과, AI·HPC 비중 30% 이상으로 확대 (2025년 말 15~20%).\n"
        "· 고객: 테슬라·애플·브로드컴 계약 + 엔비디아 신규 AI 추론 칩 수주 + 구글과 4나노 생산 협의 중.",
        fill=GREEN_HEX,
        title_color=GREEN,
    )
    add_subheading(doc, "6-4. 이수페타시스 — 2Q26 컨센 상회, 'Multi-Lam 이익 레버리지'가 핵심")
    add_chart(doc, "11_isu_petasys.png", caption="[차트 14] Multi-Lam 비중 상승 + Capa 로드맵")
    add_box(
        doc,
        "투자 논리",
        "· ① Capa 확대 + ② Multi-Lam 비중 상승(수주잔고 20%+) + ③ 수율 개선 + ④ 하반기 평균 +15% 판가 인상 = 양적 + 질적 성장 동시 진행.\n"
        "· 4Q부터 G사 제품 Multi-Lam 전환 + M사 ASIC 양산 본격화. 2027년 영업이익 컨센 대비 +10% 전후 상향 여지 — 시장이 레버리지를 과소평가.\n"
        "· Multi-Lam = 여러 겹 회로층을 쌓은 고다층 PCB. AI 서버·가속기·고속 스위치용 → 단가↑ 난이도↑ 진입장벽↑ 수익성↑.\n"
        "· '이제 Capa 증설만 보는 회사가 아니라 이익 레버리지를 봐야 한다' — 주가 조정 = 실적 상향 국면의 매수 기회 논리 가능.",
    )
    add_subheading(doc, "6-5. 기가비스 — FC-BGA 검사·수리 장비 글로벌 Top-tier")
    add_chart(doc, "12_gigavis.png", caption="[차트 15] 2026년 실적 레버리지 전망 (메리츠증권)")
    add_box(
        doc,
        "요약",
        "· AOI(불량을 찾는 장비) + AOR(찾은 불량을 레이저로 고치는 장비) — 고사양 FC-BGA 기판의 '눈'과 '수리공', 독점적 성격.\n"
        "· 연결고리: AI → FC-BGA 고사양화·증설(이비덴·신코·유니마이크론·삼성전기 CAPEX) → 기가비스 수주 → 매출/영업 레버리지.\n"
        "· 8/18 일본 기판업체향 89.5억원(매출 대비 17.1%) 공급계약. 증권사 컨센 TP 19만원선.\n"
        "· 단, 26년 실적 기준으로는 비쌈 — 27년 성장 잠재력이 초점. 적정 안전마진 고려한 분할접근 후보.",
    )
    add_subheading(doc, "6-6. LS — 자회사 이익 체력의 구조적 상승 (키움증권)")
    add_chart(doc, "13_ls_subsidiaries.png", caption="[차트 16] 2Q26 자회사별 영업이익 — 2개 분기 연속 사상 최대")
    add_subheading(doc, "6-7. 기타 주요 뉴스 한 줄 정리")
    add_data_table(
        doc,
        ["종목/테마", "내용"],
        [
            ("한화에어로스페이스", "미 육군 자주포 현대화(MTC) 시제기 단독 수주 — 집행 $1억(옵션 포함 $2.6억), 최대 18문. 평가 후 양산 직결 시 10조원 규모 사업 진입 + 차륜형 레퍼런스 확보"),
            ("LG에너지솔루션", "북미 EV용 8개 공장 중 5곳 ESS 전환, 연말 ESS 흑자 목표. 테슬라 메가팩에 $43억 LFP 셀 공급(내년~). 미 정부·방산업체와 드론용 배터리 협의 — 방산이 새 성장축"),
            ("알테오젠", "키트루다SC 2Q 매출 $4.63억(출시 3개 분기). 엑셀리시스가 외부사 최초로 키트루다SC 병용 3상 착수 → 로열티 산정 기반 확대. 엔허투 폐암 1차 청신호로 ADC SC 가치 부각"),
            ("유니트리 (중국)", "커촹반 상장 첫날 공모가 대비 5배 급등. 종가 시총 3,418억위안 ÷ 26년 매출 약 22억위안 = PSR 155배 — '성장률 2배 초과 아니면 PSR 60배 이하' 프레임의 약 2.6배. 상업화 초기 단계 유의"),
            ("자사주 매입 사례", "키옥시아: 8/3~10 8,000억엔 집행, 발표 후 누적 +7.4%. 샌디스크: $140억 한도 확대 — 8/13 Investor Day 재평가가 반등의 본질, Buyback은 EPS 레버리지 요인"),
        ],
        widths=[3.4, 13.8],
    )

    # ── 7. NVIDIA 프리뷰 ──
    add_heading(doc, "7", "NVIDIA Q2 FY27 실적 프리뷰 (8/26) — Beat보다 'CAPEX 지속 가능성'과 'Rubin'")
    add_chart(doc, "14_nvidia_preview.png", caption="[차트 17] 분기 매출 전망 — 성장률 둔화에도 절대 규모는 폭발적")
    add_data_table(
        doc,
        ["관전 포인트", "내용"],
        [
            ("① AI 인프라 수요", "성장률 둔화(+90% → +77%)가 시작돼도 절대 매출은 $108B → $120B로 증가"),
            ("② Hyperscaler CAPEX", "Top 5의 2027년 CAPEX ≥ $1T (약 +33%) — Rubin 출시와 맞물려 초기 공급 부족 가능성"),
            ("③ 순환 금융 논쟁", "NVIDIA → AI 기업 투자/금융 지원 → GPU 구매 → NVIDIA 매출. 'AI 수요가 실제 최종 수요인가, 금융으로 만들어진 수요인가' — 젠슨 황의 설명이 중요"),
            ("④ 마진", "75% 수준 Gross Margin 유지 여부"),
            ("⑤ Blackwell → Rubin", "3Q26 생산·출하. Full rack-scale, 7개 purpose-built chips, 추론 처리량 최대 35배, AI Factory 매출 기회 최대 10배. 랙 가격 $7~8.5M(Blackwell Ultra 대비 약 2배) → 성능 + ASP 동시 상승"),
        ],
        widths=[4.2, 13.0],
    )
    add_box(
        doc,
        "참고 — OpenAI 2Q",
        "매출 $6.7B(+18% QoQ)로 기대 성장률에 미달, 영업손실 $9.3B → $12.3B 확대 → AI CAPEX 투자 회수기간 장기화 우려가 SOX -2.12%로 연결된 바 있음.",
        fill=AMBER_HEX,
    )

    # ── 8. 체크리스트 ──
    add_heading(doc, "8", "모니터링 체크리스트")
    add_data_table(
        doc,
        ["변수", "긍정 시그널", "경계 시그널"],
        [
            ("미 10년물 금리", "4.7% 이하 안정", "5.0% 돌파·고착 → 위험자산 전반 회피"),
            ("유가 (브렌트)", "$90 전후 안정", "$100 이상 → 인플레·금리 악순환"),
            ("엔/달러", "157~159 수준 유지·반등", "150 초반 급락 + 닛케이·코스피 동반 급락 → 엔캐리 청산 의심"),
            ("달러-원", "완만한 하락", "가파른 하락 → 3Q 수출주 이익 역풍 / 외국인 매도 확대"),
            ("미·이란", "소강·종전 임박", "확전(유럽 내 미군 자산·호르무즈 해저 인프라) → 유가·금리 재점화"),
            ("8/26 엔비디아", "CAPEX 지속성 + Rubin 램프업 확인 → AI 심리 재강화", "순환금융 우려 확산, 헬스케어 로테이션 지속"),
            ("SK하이닉스 3Q 발표", "추가 환원 규모·특별배당 구체화", "FCF 50% 약속 이행 지연 — '지키지 않으면 큰일 나는' 눈높이"),
            ("삼성전자", "하이닉스發 주주환원 기대 현실화", "기대 미달 시 실망 매물"),
        ],
        widths=[3.4, 6.6, 7.2],
    )

    # ── 유의사항 ──
    add_box(
        doc,
        "유의사항",
        "본 자료는 8/19 Quick 코멘트 채널의 내용을 정리·시각화한 참고 자료이며, 매수·매도의 추천이 아닙니다. "
        "수치는 채널 코멘트 기준(컨센서스·추정 포함)으로 실제와 다를 수 있습니다. 투자에 따른 판단과 책임은 각자의 몫이며, 법적 자료로 활용할 수 없습니다.",
        fill=LIGHT_HEX,
        title_color=GRAY,
        body_color=GRAY,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT_PATH)
    print("saved:", OUT_PATH)


if __name__ == "__main__":
    build()
