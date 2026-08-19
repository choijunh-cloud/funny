#!/usr/bin/env python3
"""8월 19일 퀵 코멘트 종합 분석 및 전략 보고서 (.docx) 생성 스크립트."""

from __future__ import annotations
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Mm, Pt, RGBColor

OUT_PATH = Path("/workspace/lectures/8월 19일 마켓 심층 분석 및 반도체·매크로 전략 보고서.docx")
CHARTS_DIR = Path("/workspace/charts")

# 한국 Windows 기본 서체
KR_FONT = "맑은 고딕"
EN_FONT = "Calibri"

NAVY = RGBColor(0x0F, 0x20, 0x43)
NAVY2 = RGBColor(0x1E, 0x40, 0x7C)
GOLD = RGBColor(0xB8, 0x94, 0x3A)
GRAY = RGBColor(0x4B, 0x55, 0x63)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x16, 0x65, 0x34)
RED = RGBColor(0x99, 0x1B, 0x1B)
AMBER = RGBColor(0x7A, 0x5C, 0x12)
BLUE = RGBColor(0x1D, 0x4E, 0xD8)

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
    tc_pr.append(
        parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill}"/>')
    )


def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_pr.append(
        parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'<w:top w:w="{top}" w:type="dxa"/>'
            f'<w:left w:w="{left}" w:type="dxa"/>'
            f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'<w:right w:w="{right}" w:type="dxa"/>'
            f"</w:tcMar>"
        )
    )


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
    tc_pr.append(
        parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="nil"/>'
            f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="nil"/>'
            f'<w:right w:val="nil"/>'
            f"</w:tcBorders>"
        )
    )


def prevent_row_split(row):
    tr = row._tr
    tr_pr = tr.get_or_add_trPr()
    tr_pr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))


def cell_text(cell, text, size=10, bold=False, color=DARK, align="left", font=KR_FONT):
    cell.text = ""
    align_enum = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    lines = str(text).split("\n")
    for i, line in enumerate(lines):
        p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
        p.alignment = align_enum
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(1 if i < len(lines) - 1 else 0)
        p.paragraph_format.line_spacing = 1.12
        run = p.add_run(line)
        set_run_font(run, size=size, bold=bold, color=color, font=font)
    set_cell_margins(cell)


def add_runs(paragraph, parts, size=11, color=DARK):
    for part in parts:
        if isinstance(part, str):
            run = paragraph.add_run(part)
            set_run_font(run, size=size, color=color)
        else:
            text, bold, *rest = part
            c = rest[0] if rest else color
            run = paragraph.add_run(text)
            set_run_font(run, size=size, bold=bold, color=c)


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
        sec.header_distance = Mm(8)
        sec.footer_distance = Mm(8)

        normal = self.doc.styles["Normal"]
        normal.font.name = KR_FONT
        normal.font.size = Pt(11)
        normal.font.color.rgb = DARK
        normal._element.rPr.rFonts.set(qn("w:eastAsia"), KR_FONT)
        pf = normal.paragraph_format
        pf.space_after = Pt(6)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.18

        header = sec.header
        header.is_linked_to_previous = False
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = hp.add_run("8/19 마켓 인사이트  ·  반도체 · 매크로 · 주주환원 · 신성장  ·  종합전략보고서")
        set_run_font(r, size=8.5, color=GRAY)

        footer = sec.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run("준혁 투자전략 리서치  ·  8/19 퀵 코멘트 종합  ·  ")
        set_run_font(r, size=8, color=GRAY)
        fld = parse_xml(
            f'<w:fldSimple {nsdecls("w")} w:instr=" PAGE ">'
            f'<w:r><w:rPr><w:sz w:val="16"/><w:color w:val="4B5563"/>'
            f'<w:rFonts w:ascii="{KR_FONT}" w:hAnsi="{KR_FONT}" w:eastAsia="{KR_FONT}"/></w:rPr>'
            f"<w:t></w:t></w:r></w:fldSimple>"
        )
        fp._p.append(fld)

        core = self.doc.core_properties
        core.title = "8월 19일 마켓 심층 분석 및 반도체·매크로 전략 보고서"
        core.author = "준혁"
        core.subject = "SK하이닉스 40조 자사주, 미국 금리·바이백, 삼성 파운드리, AI 인프라, 바이오 로테이션"

    def p(self, text, size=11, bold=False, color=DARK, space_after=6, space_before=0, align="left"):
        para = self.doc.add_paragraph()
        para.alignment = {
            "left": WD_ALIGN_PARAGRAPH.LEFT,
            "center": WD_ALIGN_PARAGRAPH.CENTER,
            "right": WD_ALIGN_PARAGRAPH.RIGHT,
        }[align]
        para.paragraph_format.space_after = Pt(space_after)
        para.paragraph_format.space_before = Pt(space_before)
        para.paragraph_format.line_spacing = 1.18
        run = para.add_run(text)
        set_run_font(run, size=size, bold=bold, color=color)
        return para

    def rich(self, parts, size=11, space_after=6, space_before=0):
        para = self.doc.add_paragraph()
        para.paragraph_format.space_after = Pt(space_after)
        para.paragraph_format.space_before = Pt(space_before)
        para.paragraph_format.line_spacing = 1.18
        add_runs(para, parts, size=size)
        return para

    def h1(self, text, num=None):
        para = self.doc.add_paragraph()
        para.paragraph_format.space_before = Pt(14)
        para.paragraph_format.space_after = Pt(8)
        para.paragraph_format.line_spacing = 1.1
        if num:
            run = para.add_run(f"{num}  ")
            set_run_font(run, size=16, bold=True, color=GOLD)
        run = para.add_run(text)
        set_run_font(run, size=16, bold=True, color=NAVY)
        pPr = para._p.get_or_add_pPr()
        pPr.append(
            parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'<w:bottom w:val="single" w:sz="12" w:space="4" w:color="{NAVY_HEX}"/>'
                f"</w:pBdr>"
            )
        )
        return para

    def h2(self, text):
        para = self.doc.add_paragraph()
        para.paragraph_format.space_before = Pt(10)
        para.paragraph_format.space_after = Pt(4)
        run = para.add_run(text)
        set_run_font(run, size=13, bold=True, color=NAVY2)
        return para

    def h3(self, text):
        para = self.doc.add_paragraph()
        para.paragraph_format.space_before = Pt(8)
        para.paragraph_format.space_after = Pt(3)
        run = para.add_run(text)
        set_run_font(run, size=11.5, bold=True, color=NAVY)
        return para

    def bullet(self, text, level=0, bold_lead=None, size=11):
        para = self.doc.add_paragraph()
        para.paragraph_format.left_indent = Cm(0.55 + level * 0.45)
        para.paragraph_format.first_line_indent = Cm(-0.35)
        para.paragraph_format.space_after = Pt(2.5)
        para.paragraph_format.space_before = Pt(0)
        para.paragraph_format.line_spacing = 1.15
        mark = "• " if level == 0 else "– "
        run = para.add_run(mark)
        set_run_font(run, size=size, color=NAVY2 if level == 0 else GRAY)
        if bold_lead:
            run = para.add_run(bold_lead)
            set_run_font(run, size=size, bold=True, color=DARK)
            run = para.add_run(text)
            set_run_font(run, size=size, color=DARK)
        else:
            run = para.add_run(text)
            set_run_font(run, size=size, color=DARK)
        return para

    def flow(self, items, size=11):
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_before = Pt(4)
        para.paragraph_format.space_after = Pt(8)
        para.paragraph_format.line_spacing = 1.2
        for i, item in enumerate(items):
            if i:
                run = para.add_run("   →   ")
                set_run_font(run, size=size, bold=True, color=GOLD)
            run = para.add_run(item)
            set_run_font(run, size=size, bold=True, color=NAVY)
        return para

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
        table.autofit = True
        table.allow_autofit = True
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = table.cell(0, 0)
        shade_cell(cell, fill)
        set_left_accent(cell, accent, sz="28")
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        cell.text = ""
        p1 = cell.paragraphs[0]
        p1.paragraph_format.space_after = Pt(2)
        p1.paragraph_format.space_before = Pt(0)
        r = p1.add_run(title)
        set_run_font(r, size=10, bold=True, color=title_color)
        if isinstance(body, str):
            body = [body]
        for line in body:
            p = cell.add_paragraph()
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing = 1.15
            r = p.add_run(line)
            set_run_font(r, size=10.5, color=DARK)
        self.doc.add_paragraph().paragraph_format.space_after = Pt(6)

    def table(self, headers, rows, col_widths=None, first_col_bold=True):
        table = self.doc.add_table(rows=1 + len(rows), cols=len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True
        set_table_borders(table, color="D5DCE6", sz="4")
        for i, h in enumerate(headers):
            cell = table.rows[0].cells[i]
            shade_cell(cell, NAVY_HEX)
            cell_text(cell, h, size=9.5, bold=True, color=WHITE, align="center")
        prevent_row_split(table.rows[0])
        for r_i, row in enumerate(rows):
            for c_i, val in enumerate(row):
                cell = table.rows[r_i + 1].cells[c_i]
                if r_i % 2 == 1:
                    shade_cell(cell, ROW_HEX)
                else:
                    shade_cell(cell, WHITE_HEX)
                align = "left" if c_i == 0 else "center"
                bold = first_col_bold and c_i == 0
                cell_text(cell, str(val), size=9.5, bold=bold, color=DARK, align=align)
            prevent_row_split(table.rows[r_i + 1])
        if col_widths:
            for row in table.rows:
                for i, w in enumerate(col_widths):
                    row.cells[i].width = Cm(w)
        spacer = self.doc.add_paragraph()
        spacer.paragraph_format.space_after = Pt(8)
        spacer.paragraph_format.space_before = Pt(2)
        return table

    def add_image(self, image_path: Path, width_cm=16.0, caption=None):
        if not image_path.exists():
            print(f"Warning: Image {image_path} does not exist!")
            return
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run()
        run.add_picture(str(image_path), width=Cm(width_cm))
        if caption:
            cp = self.doc.add_paragraph()
            cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.space_before = Pt(0)
            cp.paragraph_format.space_after = Pt(8)
            r = cp.add_run(f"▲ {caption}")
            set_run_font(r, size=9, bold=True, color=GRAY)

    def spacer(self, pt=4):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(pt)
        p.paragraph_format.space_before = Pt(0)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(path))
        print(f"Wrote {path} ({path.stat().st_size} bytes)")


def build():
    r = Report()

    # ── Cover ──────────────────────────────────────────────
    r.p("2026. 8. 19. 심층 전략 보고서  ·  매크로 · 반도체 · 주주환원 · 신성장", size=10.5, color=GRAY, align="center", space_after=4)
    r.p("DAILY MARKET STRATEGY & DEEP DIVE", size=13, bold=True, color=GOLD, align="center", space_after=2)
    r.p("8월 19일 마켓 종합 분석 및 전략 보고서", size=22, bold=True, color=NAVY, align="center", space_after=2)
    r.p("역대급 주주환원, 금리 쇼크와 재무부 바이백, 그리고 AI·바이오 섹터 로테이션", size=14, bold=True, color=NAVY2, align="center", space_after=8)
    r.p("작성: 준혁 (마케팅 & 투자전략)  |  기준일: 2026년 8월 19일 (수)", size=10.5, color=GRAY, align="center", space_after=12)

    # ── Executive Summary Callout ──────────────────────────
    r.callout(
        "8월 19일 핵심 총괄 요약 (Executive Summary)",
        [
            "① [역대급 주주환원]: SK하이닉스가 40조원(발행주식 3.3%) 자사주 매입·소각 및 2025~27년 누적 FCF의 '50% 초과' 주주환원 발표. 누적 565조 FCF 기준 152.5조원 이상의 추가 배당/특별배당 여력 확보로 증시 하방 경직성 및 밸류에이션 재평가 촉발.",
            "② [매크로 공방 & 재무부 방어]: 미·이란 확전 우려와 유가($84~90)가 10년물 금리를 4.75%, 30년물을 5.34%까지 밀어올렸으나, 베선트 미 재무장관의 장기국채 바이백 2배 확대(20억→40억$)로 10년물 4.64%, 30년물 5.19%로 급속 안정.",
            "③ [섹터 로테이션 (Pivot)]: 금리 안정에도 기술주가 반등하지 못한 본질은 AI·반도체 차익실현 자금이 키트루다+mRNA 암백신 3상 성공에 힘입은 바이오·헬스케어(모더나 +77%, MSD +11%)로 이동했기 때문.",
            "④ [반도체 펀더멘털 & 신성장]: 삼성전자 4/5나노 파운드리 최대 15% 단가 인상 및 흑자전환 가시화, Google-Marvell TPU 생태계 제휴(Warrant 연동), 이수페타시스 Multi-Lam 수주 20%+ 및 증설, 유니트리 커촹반 5배 폭등과 휴머노이드 경쟁 가열.",
        ],
        kind="key",
    )

    # ── Macro & Market Overview Table ─────────────────────
    r.h1("오늘의 핵심 지표 및 시장 요약", num="0.")
    r.table(
        ["구분", "주요 지표 / 이벤트", "수치 및 변동", "핵심 투자 함의"],
        [
            ["금리 (Macro)", "미 국채 10년물 / 30년물", "10년물 4.64% (고점 4.75%)\n30년물 5.19% (고점 5.34%)", "재무부 바이백 개입으로 단기 진정. 10년물 4.7% 이하 안착 여부 주목"],
            ["환율 / 유가", "달러-원 환율 / WTI 유가", "1,412원 (하단 1,360~1,340원)\nWTI $84대 / 브렌트 $90", "월말 법인세 납부·수출기업 달러 매도. 환율 1,400원 하회 시 실적 영향 점검"],
            ["주주환원 (Big Event)", "SK하이닉스 주주환원", "40조원 자사주 매입·소각\nFCF 50% 이상 환원", "국내 증시 역대 최대. 주식수 3.3% 감소로 EPS +3.4% 영구 상승 효과"],
            ["파운드리 (반도체)", "삼성전자 첨단공정 판가", "4/5나노 최대 15% 인상\n8나노 10% 인상", "TSMC 가동률 포화 반사이익 + 평택 SF4 풀가동 → 2027 파운드리 흑전 기대"],
            ["AI ASIC 생태계", "Google - Marvell 제휴", "Marvell +9.9% 급등\nBroadcom -4.6% 하락", "Google TPU 전방위 확대. Marvell에 5,897만주 Warrant 부여. 브로드컴 견제"],
            ["바이오 (Rotation)", "모더나 / MSD 암백신 3상", "모더나 +77% (장중 117%)\nMSD +11.2% (역사적 신고가)", "키트루다+mRNA 임상 3상 성공. AI·기술주에서 헬스케어 성장주로 강력한 자금 이동"],
            ["소부장 & PCB", "이수페타시스 / 기가비스", "이수 Multi-Lam 비중 20%+\n기가비스 89.5억 공급계약", "Multi-Lam 판가 +15% 인상 및 이익 레버리지. FC-BGA 검사·수리 독점력 부각"],
            ["피지컬 AI (로봇)", "유니트리(Unitree) 상장", "공모가 대비 5배 급등\n시총 3,418억 RMB (PSR 155배)", "중국 로봇 공급망 및 저가 제조(미국의 35%) 강점 vs 밸류에이션 과열 논쟁"],
        ],
        col_widths=[2.8, 4.4, 4.4, 6.2],
        first_col_bold=True,
    )

    # ── Part 1: Macro & Interest Rate Dynamics ────────────
    r.h1("매크로 심층 분석: 전쟁, 금리 쇼크, 그리고 미 재무부의 바이백 방어선", num="1.")
    r.callout(
        "매크로의 역습과 핵심 연결고리",
        [
            "흐름: 미·이란 협상 시한 종료 및 강경 발언 → 호르무즈 해협 리스크 부각 → 유가 상승 → 인플레이션 우려 → 미 국채금리 급등 → 기술주·반도체 밸류에이션 압박",
            "재무부의 개입: 스콧 베선트 미 재무장관이 장기국채 바이백 규모를 20억$에서 40억$ 이상으로 2배 확대하며 30년물 금리 급등에 강력 제동.",
        ],
        kind="note",
    )

    r.add_image(CHARTS_DIR / "macro_indicators.png", width_cm=16.0, caption="글로벌 매크로 지표 현황 및 위험 임계선 대시보드")

    r.h2("1) 10년물 국채금리와 주식시장 할인율의 관계")
    r.p("최근 시장을 짓누른 가장 큰 악재는 AI 산업 자체의 펀더멘털 훼손이 아니라, '유가발 금리 쇼크'였습니다. 시장에서는 30년물 금리를 많이 거론하지만, 실물 경제와 주식시장 할인율의 실질적인 기준은 '미 국채 10년물 금리'입니다.")
    r.flow(["유가 $90 돌파", "인플레 압력", "10년물 금리 4.75% 돌파", "성장주 할인율 상승", "주가 밸류에이션 압박"])
    
    r.bullet("10년물 4.7% 이하 안착: 성장주 및 반도체 밸류에이션 부담 완화 구간 진입.")
    r.bullet("10년물 5.0% 돌파 및 고착: 글로벌 모든 위험자산에 대한 강력한 회피 심리 발동.")
    r.bullet("유가 $100 이상: 인플레이션과 추가 금리 인상의 악순환 발생 가능성.")

    r.h2("2) 미 재무부(베선트 장관)의 장기국채 바이백 2배 확대 조치")
    r.p("미 재무부는 장기국채 시장에 사실상의 '정책적 방어선'을 구축했습니다. 유동성 지원을 위한 국채 조기 재매입(Buyback) 규모를 기존 회차당 20억 달러에서 40억 달러 이상으로 확대하고, 대상을 10~30년물 장기채로 집중 지목했습니다.")
    r.table(
        ["구분", "기존 정책", "확대 변경 정책", "시장 영향 및 함의"],
        [
            ["바이백 규모", "회차당 20억 달러", "회차당 40억 달러 이상 (2배+)", "장기채 시장 내 강력한 매수 주체 등장"],
            ["매입 대상", "중단기물 중심 분산", "10년~30년 장기국채 집중", "장기금리 급등 차단 및 기간 프리미엄 축소"],
            ["정책적 의지", "통상적 유동성 관리", "금리 상단 좌시하지 않겠다는 강력한 신호", "장기채 숏(매도) 포지션 구축 억제 효과"],
        ],
        col_widths=[3.0, 3.8, 5.0, 6.0],
    )

    r.h2("3) 7월 FOMC 의사록과 통화·재정 정책의 엇박자")
    r.p("7월 FOMC 의사록은 3명의 위원이 25bp 금리 인상을 주장하는 등 다소 매파적인 면모를 보였습니다. 그러나 최근 고용과 소비가 둔화되는 조짐을 보이면서 시장은 연준의 추가 인상 가능성을 낮게 평가하고 있습니다.")
    r.callout(
        "정책 줄다리기 구도",
        [
            "Fed (연방준비제도): 매파적 스탠스 유지 (인플레 경계)",
            "Treasury (재무부): 장기금리 상승 적극 방어 (국채 바이백 확대 🟢)",
            "결론: 단기적으로는 재무부의 장기금리 안정화 조치가 시장에 더 강한 안전판 역할을 수행 중.",
        ],
        kind="blue",
    )

    r.h2("4) 원/달러 환율 급락(1,400원 하회 시도)과 기업 실적 민감도")
    r.p("원/달러 환율이 1,520원대에서 1,412원대까지 급락하며 1,400원 하향 돌파를 시도하고 있습니다. 이는 단순 달러 약세보다 한국 내부 수급(8월말 법인세 납부, 설비투자 자금 환전, 수출기업 달러 매도 및 환헤지)이 선행했기 때문입니다.")
    r.table(
        ["기업명", "환율 1% 변동 시 EPS 민감도", "환율 1,520 → 1,420원 (-6.6%) 영향", "2027년 순익 기준 이익 조정 규모"],
        [
            ["SK하이닉스", "원/달러 +1% 당 EPS +0.9%", "EPS 약 -5.9% 하향 조정 요인", "2027년 순익 300~400조원 가정 시 18~24조원 조정"],
            ["삼성전자", "원/달러 +1% 당 EPS +0.4%", "EPS 약 -2.6% 하향 조정 요인", "다변화된 사업구조로 하이닉스 대비 환율 민감도 낮음"],
        ],
        col_widths=[3.4, 4.4, 5.0, 5.0],
    )

    # ── Part 2: SK Hynix Shareholder Return ───────────────
    r.h1("SK하이닉스: 40조원 자사주 소각 및 FCF 50% 초과 환원의 파급효과", num="2.")
    r.callout(
        "국내 증시 역사상 최대 규모의 주주환원",
        [
            "40조원 자사주 매입 후 100% 전량 소각 (발행주식의 3.3%, 3개월 내 일 6,452억원 매입)",
            "주식수 3.3% 감소 → 동일 순이익 기준 EPS 3.4% 영구 상승 효과",
            "2025~2027년 누적 FCF '50% 범위 내' → '50% 초과'로 정책 대폭 상향",
        ],
        kind="bull",
    )

    r.add_image(CHARTS_DIR / "skhynix_return_and_valuation.png", width_cm=16.0, caption="SK하이닉스 주주환원 배분 및 본주 시나리오별 적정주가")

    r.h2("1) 공시 세부 내용 및 40조원 소각의 재무적 메커니즘")
    r.p("SK하이닉스는 8월 20일부터 11월 19일까지 62영업일 동안 총 40조원 규모(약 2,407만주)의 자사주를 취득하여 전량 소각하기로 공시했습니다.")
    r.bullet("취득 단가 기준: 전일 종가 166만 2,000원 기준 24,067,388주 (지분 3.3%).")
    r.bullet("매입 속도: 일평균 약 6,452억원의 강력한 매수세가 3개월간 시장에 유입.")
    r.bullet("구조적 효과: ADR 발행으로 희석되었던 지분율을 회복시켜 최대주주(SK스퀘어) 지분율을 원상 복구하고, 주당 내재가치를 즉각 3.4% 레벨업시키는 구조.")

    r.h2("2) 2025~2027년 누적 FCF 565조원 모델링과 추가 환원 여력")
    r.p("회사는 3개년 누적 FCF의 50% 초과 환원을 천명했습니다. 운전자본과 CAPEX를 보수적으로 차감한 3개년 FCF 추정치는 총 565조원에 달합니다.")
    r.table(
        ["구분", "기존 계산 모델", "보수적 FCF 모델 (운전자본 20~30조 추가 차감)", "주주환원 배분 계획"],
        [
            ["2025년 FCF", "179조원", "150조원", "기본 배당 및 조기 환원"],
            ["2026년 FCF", "242조원", "210조원", "40조원 자사주 소각 집행"],
            ["2027년 FCF", "237조원", "205조원", "추가 자사주·현금배당·특별배당"],
            ["3개년 누적 FCF", "658조원", "565조원 (기준)", "50% 초과 기준: 최소 282.5조원 이상"],
            ["기확정분 차감", "-", "△ 40조원 (자사주 소각)", "최소 242.5조원의 추가 환원 재원 잔여"],
        ],
        col_widths=[3.4, 4.0, 5.0, 5.4],
    )
    r.p("※ 참고: 단순 385조 FCF 모델 기준(50% 환원=192.5조)을 적용해도 40조 차감 시 152.5조원의 추가 환원이 필요합니다. 구체적인 환원 방식은 3Q26 실적 발표에서 확정됩니다.")

    r.h2("3) 밸류에이션 재평가: ADR 프리미엄 vs PER 배수 접근법")
    r.p("SK하이닉스는 2분기 말 순현금이 69조원에 달하며 강력한 현금창출력을 보유하고 있습니다. '내재가치 대비 심각한 저평가'를 해소하기 위한 두 가지 적정주가 산출 경로입니다.")
    r.table(
        ["산출 방식", "세부 적용 가정", "산출 적정 주가", "현재가(150만원) 대비 상승여력"],
        [
            ["ADR 프리미엄 정상화", "ADR 163.8$ 대비 정상 프리미엄(+20%) 적용", "190만원", "+26.7%"],
            ["실제 프리미엄 감안", "최근 형성된 30~35% 프리미엄률 적용", "169만 ~ 175만원", "+12.7% ~ +16.7%"],
            ["보수적 26년 PER 6배", "26년 EPS 346K × PER 6배 (27년 성장 배제)", "208만원", "+38.7%"],
            ["보수적 26년 PER 7배", "26년 EPS 346K × PER 7배 (과거 사이클 밴드)", "242만원", "+61.3%"],
        ],
        col_widths=[3.8, 5.4, 4.2, 4.4],
    )

    # ── Part 3: Global Memory Valuation & HBM Debate ──────
    r.h1("글로벌 메모리 밸류에이션 및 HBM 헤게모니 논쟁", num="3.")
    r.callout(
        "핵심 쟁점: HBM 고가격화는 독인가, 초과이익인가?",
        [
            "캐시 우드 & 벤 톰슨의 경고: HBM 가격 급등은 호르무즈 해협 봉쇄와 유사하여 장기적으로 AI 업계의 대체 기술(SRAM, 압축, ASIC) 투자를 자극할 것.",
            "시장 현실과 반론: SRAM은 HBM을 '대체'하는 것이 아니라 워크로드별(SRAM+HBM+DRAM+SSD) '계층적 분업' 구조로 진화 중. 2026~28년 메모리 초과이익 사이클은 견고.",
        ],
        kind="key",
    )

    r.add_image(CHARTS_DIR / "memory_peers_valuation.png", width_cm=16.0, caption="글로벌 메모리 반도체 밸류에이션(PER) 비교")

    r.h2("1) 글로벌 메모리 기업 밸류에이션 비교")
    r.table(
        ["기업명", "주가 / ADR", "2026E PER", "2027E 컨센서스 PER", "2027E 보수적 시나리오 PER"],
        [
            ["SK하이닉스 (본주)", "150.0만원", "4.3배", "3.4배", "5.1배"],
            ["삼성전자 (본주)", "24.75만원", "5.2배", "3.7배", "5.6배"],
            ["SK하이닉스 (ADR)", "$163.80", "6.6배", "5.2배", "7.7배"],
            ["마이크론 (MU)", "$937.11", "7.5배 (Fwd 12M)", "6.25배 (CY27 EPS $150)", "7.5배"],
            ["샌디스크 (SNDK)", "$1,568.37", "7.8배", "7.0배 (FY27 EPS $201)", "8.2배"],
        ],
        col_widths=[3.6, 3.2, 3.4, 4.2, 3.4],
    )
    r.p("한국 메모리 본주는 글로벌 피어(마이크론, 샌디스크) 대비 35~45% 이상 심각하게 디스카운트되어 거래되고 있으며, 40조원 자사주 소각은 이 간극을 메우는 핵심 계기가 될 것입니다.")

    r.h2("2) HBM 대체 vs 분업: 아키텍처 진화 분석")
    r.p("최근 AI 추론 칩 진영에서 나타나는 아키텍처 변화는 HBM의 소멸이 아닌 메모리 계층 구조의 다변화입니다.")
    r.table(
        ["접근 방식", "대표 기업 및 기술", "HBM 영향도", "상용화 단계 및 실질 평가"],
        [
            ["온칩 SRAM 확대", "Cerebras (웨이퍼 스케일), Groq", "HBM 비의존 추론", "대규모 모델 처리 시 용량 한계 및 비용 급증. 특수 추론 특화"],
            ["NVIDIA 아키텍처", "NVIDIA + Groq 기술 도입 시스템", "초기 추론 가속", "SRAM을 1차 캐시로 쓰고 메인 메모리는 HBM/DRAM 계층 유지"],
            ["KV Cache 압축", "소프트웨어 알고리즘 최적화", "HBM 필요용량 절감", "추론 효율을 높이나 전체 토큰 생성량 증가로 총수요 상쇄"],
            ["메모리 계층화", "HBF(High Bandwidth Flash), CXL SSD", "메모리 다변화", "GPU HBM + CPU 메모리 + SSD 계층적 구성으로 AI TCO 최적화"],
        ],
        col_widths=[3.2, 4.4, 3.6, 6.6],
    )

    # ── Part 4: Tech & Semiconductor News ─────────────────
    r.h1("반도체 & AI 하드웨어 주요 동향: 삼성, Marvell, 이수페타시스, 기가비스", num="4.")

    r.h2("1) 삼성전자: 첨단 파운드리(4·5나노) 최대 15% 가격 인상")
    r.p("삼성전자가 AI 반도체 수요 급증과 TSMC 생산능력 포화에 대응하여 SF4(4나노) 등 첨단 파운드리 가격을 최대 15% 전격 인상했습니다.")
    r.add_image(CHARTS_DIR / "samsung_foundry_expansion.png", width_cm=16.0, caption="삼성전자 파운드리 가격 인상률 및 첨단 공정 비중 확대")
    
    r.bullet("공정별 인상폭: 4나노(미·중 고객사 10~15%, 대만 5~10%), 5나노(10~15%), 8나노(약 10%).")
    r.bullet("배경: TSMC 점유율 70%+ 포화로 낙수효과 발생, 평택 SF4 라인(퀄컴 및 차세대 HBM 베이스다이) 풀가동 지속.")
    r.bullet("고객사 파이프라인: 테슬라, 애플, 브로드컴, 엔비디아 신규 추론 칩 수주에 이어 구글과 4나노 칩 생산 협의 중.")
    r.bullet("실적 전환: 2022년 이후 이어진 파운드리 적자를 마감하고 2027년 흑자 전환 기대.")

    r.h2("2) Google – Marvell AI ASIC 전방위 협력 확대")
    r.p("구글이 Marvell과의 커스텀 반도체 파트너십을 대폭 확대하며 Marvell 주가가 +9.9% 급등하고 Broadcom이 -4.6% 하락했습니다.")
    r.table(
        ["항목", "세부 내용", "전략적 함의"],
        [
            ["협력 영역 확대", "AI 추론 가속기 + Storage Controller + NIC + Memory Controller + Near-memory Compute", "Marvell이 단순 칩 설계를 넘어 TPU 주변 생태계 전체로 영역 확장"],
            ["Warrant 발행", "구글에 최대 5,897만주 매입권 부여 (행사가격 $206.58)", "구글과 Marvell 간 강력한 장기 경제적 이해관계 형성"],
            ["Vesting 조건", "구글 관련 Custom 매출 5억$ 달성 시마다 1 tranche 베스팅", "매출 성장과 주식 보상이 완벽히 연동된 장기 계약 (FY2027 Q3~FY2033)"],
            ["경쟁 구도", "Broadcom의 구글 TPU 독점적 지위에 대한 강력한 견제 신호", "빅테크의 커스텀 ASIC 공급망 다변화 가속"],
        ],
        col_widths=[3.2, 7.6, 7.0],
    )

    r.h2("3) 이수페타시스: Multi-Lam 고부가 믹스 개선과 Capa 증설")
    r.p("이수페타시스는 단순 Capa 증설을 넘어 AI용 고다층 PCB인 Multi-Lam 비중 상승에 따른 '이익 레버리지' 구간에 진입했습니다.")
    r.add_image(CHARTS_DIR / "isupetasys_growth.png", width_cm=16.0, caption="이수페타시스 Multi-Lam 비중 및 월 매출 Capa 증설 로드맵")

    r.table(
        ["구분", "2Q26 실적 (YoY)", "주요 내용 및 향후 로드맵"],
        [
            ["매출액", "3,799억원 (+57.4%)", "컨센서스 +4.9% 상회"],
            ["영업이익 / OPM", "771억원 (+83.3%) / 20.3%", "컨센서스 +2.7% 상회, 영업레버리지 본격화"],
            ["Multi-Lam 비중", "1Q 7% → 2Q 11% → 잔고 20%+", "4Q부터 G사 Multi-Lam 전환 + M사 ASIC 양산 본격화"],
            ["판가 인상 효과", "원재료 상승 반영 평균 +15% 인상", "하반기부터 판가 인상 효과 반영되어 이익률 추가 개선"],
            ["Capa 증설 계획", "현재 1,200억 → 27년 2Q 1,500억 → 28년 하반기 1,800억원/월", "2026~2028년 외형 성장 가시성 확보"],
        ],
        col_widths=[3.4, 5.4, 9.0],
    )

    r.h2("4) 기가비스(420770): FC-BGA 검사·수리 장비 독점력 및 대형 수주")
    r.p("기가비스는 일본 반도체 기판 제조회사와 89.5억원(최근 매출 대비 17.1%) 규모의 반도체 기판 검사(AOI) 및 수리(AOR) 장비 공급계약을 체결했습니다.")
    r.bullet("핵심 경쟁력: AOI(불량 검출) + AOR(레이저 미세회로 수리) 기술을 동시 보유한 글로벌 Top-tier.")
    r.bullet("투자 포인트: AI 반도체 확산 → 고사양 FC-BGA(ABF) 기판 채용 증가 → 기판 회로 미세화로 검사·수리 난이도 급상승 → 글로벌 기판사(이비덴, 신코, 유니마이크론, 삼성전기) CAPEX 집행에 따른 영업레버리지 폭발 구조.")

    # ── Part 5: Sector Rotation & Non-Semiconductor ───────
    r.h1("신성장 섹터 분석: 바이오 급등, ESS 재편, 방산, 로봇(Unitree)", num="5.")

    r.h2("1) 헬스케어·바이오 섹터로의 강력한 자금 피벗(Pivot)")
    r.p("모더나와 MSD의 개인맞춤형 mRNA 암 백신 임상 3상 성공으로 나스닥 바이오 지수(NBI)가 +4.86% 급등하며 역사적 신고가를 경신했습니다.")
    r.add_image(CHARTS_DIR / "bio_sector_surge.png", width_cm=16.0, caption="8월 19일 미국 바이오·헬스케어 주요 종목 등락률")
    
    r.bullet("호재 배경: 키트루다 + 모더나 mRNA 암 백신 병용 3상 성공 → 모더나 +77% (장중 +117%), MSD +11.17% 신고가 달성.")
    r.bullet("국내 반사수혜: 알테오젠(키트루다SC 글로벌 확장 및 비소세포폐암 임상 진행), 에스티팜(mRNA 올리고 원료), 올릭스, 알지노믹스.")
    r.bullet("시장 시사점: '금리 하락 = 무조건 기술주 매수' 공식이 깨지고, AI 차익실현 자금이 헬스케어 성장주로 이동하는 섹터 로테이션 진행 중.")

    r.h2("2) 2차전지: LG에너지솔루션 북미 사업 EV → ESS 전격 재편")
    r.bullet("북미 전략 전환: 미국 내 배터리 공장 8곳 중 5곳을 ESS용으로 전환. 북미 매출 과반이 ESS로 이동하며 연말 흑자전환 목표.")
    r.bullet("테슬라 공급: 미시간 랜싱 공장에서 내년부터 테슬라 메가팩용 LFP 배터리 약 43억 달러(약 6조원) 공급 예정.")
    r.bullet("방산 신사업: 미국 정부 및 주요 방산업체와 드론·무인무기체계용 배터리 공급 협상 진행.")

    r.h2("3) 방산: 한화에어로스페이스 미 육군 자주포 사업 단독 수주")
    r.bullet("수주 내용: 미 육군 차륜형 자주포 현대화(MTC) 시제기 공급 업체로 단독 선정 (개발비 1억$, 옵션 포함 2.6억$).")
    r.bullet("전략적 의의: 향후 10조원 규모 본 양산 사업 직결 가능성 확보 + 글로벌 최대 시장인 미국에서 차륜형 레퍼런스 축적.")

    r.h2("4) 피지컬 AI & 휴머노이드: 유니트리(Unitree) 커촹반 상장 분석")
    r.p("중국 휴머노이드 대표 기업 유니트리가 상하이 커촹반 상장 첫날 공모가 대비 5배 이상 급등하며 시총 3,418억 위안을 기록했습니다.")
    r.add_image(CHARTS_DIR / "humanoid_unitree_analysis.png", width_cm=16.0, caption="휴머노이드 대당 소재비 비교 및 유니트리 밸류에이션 분석")

    r.table(
        ["구분", "내용 및 지표", "평가 및 분석"],
        [
            ["상장 결과", "공모가 대비 5배 급등 / 시총 3,418억 RMB (약 71조원)", "중국 정부 및 빅테크(텐센트, 알리바바) 지원 속 로봇 투자 열풍"],
            ["제조 원가 경쟁력", "대당 소재비(BOM) 중국 $4.6만 vs 미국 $13.1만", "중국이 미국의 35% 수준으로 압도적 원가 우위 보유 (JP모건 시장점유율 75% 평가)"],
            ["밸류에이션 평가", "2026E 매출 22억 RMB 기준 PSR 155배", "초고성장 기준(PSR 60배) 대비 2.6배 수준으로 단기 밸류에이션 과열권"],
            ["향후 핵심 과제", "연구·시연 단계에서 실제 산업현장 ROI 검증으로 전환", "미국의 대중국 규제 극복 및 산업용 대량 배치 안정성이 관건"],
        ],
        col_widths=[3.4, 7.0, 7.4],
    )

    # ── Part 6: Comprehensive Strategy & Portfolio ────────
    r.h1("종합 투자 전략 및 대응 매뉴얼", num="6.")
    r.callout(
        "시장 대응 4대 핵심 원칙",
        [
            "1. 매크로: 미 국채 10년물 금리 4.7% 이하 안착 및 8월 26일 엔비디아 실적 발표 전까지 변동성 관리.",
            "2. 대형 반도체: SK하이닉스 40조 소각에 따른 강력한 하방 경직성 확보. 본주-ADR 괴리 축소 및 자사주 매입 집행(일 6,452억)을 활용한 비중 유지/확대.",
            "3. 소부장/부품: 숫자가 증명되는 고부가 믹스 개선주(이수페타시스 Multi-Lam, 기가비스 FC-BGA 검사장비) 중심 압축 대응.",
            "4. 섹터 분산: 미국 바이오 3상 호재에 따른 국내 플랫폼/원료 바이오주(알테오젠 등) 및 ESS 전환 배터리주로 포트폴리오 다변화.",
        ],
        kind="key",
    )

    r.table(
        ["섹터 / 테마", "핵심 추천 / 관심 종목", "투자 포인트 및 촉매(Catalyst)", "리스크 요인 및 확인 지표"],
        [
            ["메모리 대형주", "SK하이닉스\n삼성전자", "• 40조원 자사주 소각 및 FCF 50%+ 환원\n• 삼성 4/5나노 파운드리 단가 15% 인상\n• 글로벌 Peer 대비 극심한 저평가 해소", "• 원/달러 환율 1,400원 급락 시 환율효과 둔화\n• 미 국채금리 5% 재돌파 리스크"],
            ["고부가 소부장·PCB", "이수페타시스\n기가비스", "• Multi-Lam 비중 20%+ 및 판가 +15% 인상\n• 월 Capa 1,200억 → 1,800억 증설\n• FC-BGA 광학검사·레이저수리 독점력", "• 고객사 양산 일정 지연\n• 원자재 가격 변동성"],
            ["바이오 & 헬스케어", "알테오젠\n에스티팜", "• 키트루다SC 비소세포폐암 3상 확장\n• 모더나 mRNA 암백신 3상 성공 반사수혜\n• 글로벌 피벗 자금 유입", "• 후속 임상 데이터 지연\n• 차익실현 매물 출회"],
            ["인프라 & 전력", "LS\nLS일렉트릭", "• 2분기 연속 사상 최대 영업이익(5,956억)\n• 배전설비·변압기 수주잔고 폭발\n• 구리가격 사상 최고치($14,000) 수혜", "• 미국 송전망 인허가 지연\n• 원자재 가격 급락"],
        ],
        col_widths=[3.2, 3.4, 7.2, 4.2],
        first_col_bold=True,
    )

    r.spacer(8)
    r.p("— 8월 19일 마켓 종합 분석 및 전략 보고서 완료. 원문 퀵코멘트 전수 반영 및 시각화 차트 수록.", size=9.5, color=GRAY, align="right")

    r.save(OUT_PATH)


if __name__ == "__main__":
    build()
