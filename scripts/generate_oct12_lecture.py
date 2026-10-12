#!/usr/bin/env python3
"""10월 12일 DRAM 셀 구조 강의노트(.docx) 생성."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Mm, Pt, RGBColor

OUT_PATH = Path("/workspace/lectures/10월 12일 DRAM 셀 구조 (6F²·4F²·3D).docx")

# 한국 Windows에서 기본으로 열리는 서체. 없는 환경은 Calibri로 폴백.
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
    """parts: str or (text, bold, color?) tuples."""
    for part in parts:
        if isinstance(part, str):
            run = paragraph.add_run(part)
            set_run_font(run, size=size, color=color)
        else:
            text, bold, *rest = part
            c = rest[0] if rest else color
            run = paragraph.add_run(text)
            set_run_font(run, size=size, bold=bold, color=c)


class Notes:
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
        r = hp.add_run("10/12 DRAM 셀 구조  ·  6F² → 4F² → 3D  ·  강의노트")
        set_run_font(r, size=8.5, color=GRAY)

        footer = sec.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run("영상 녹화용 정리  ·  숫자·시나리오는 공개 보도·당일 코멘트 기준  ·  ")
        set_run_font(r, size=8, color=GRAY)
        fld = parse_xml(
            f'<w:fldSimple {nsdecls("w")} w:instr=" PAGE ">'
            f'<w:r><w:rPr><w:sz w:val="16"/><w:color w:val="4B5563"/>'
            f'<w:rFonts w:ascii="{KR_FONT}" w:hAnsi="{KR_FONT}" w:eastAsia="{KR_FONT}"/></w:rPr>'
            f"<w:t></w:t></w:r></w:fldSimple>"
        )
        fp._p.append(fld)

        core = self.doc.core_properties
        core.title = "10월 12일 DRAM 셀 구조 (6F²·4F²·3D)"
        core.author = "준혁"
        core.subject = "DRAM 6F²·4F²·3D, CXMT VSG, 삼성·SK·마이크론 로드맵, 마린솔루션"

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
        # underline bar
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

    def spacer(self, pt=4):
        p = self.doc.add_paragraph()
        p.paragraph_format.space_after = Pt(pt)
        p.paragraph_format.space_before = Pt(0)

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(path))


def build():
    n = Notes()

    n.p("2026. 10. 12. 강의노트  ·  영상 녹화용", size=10.5, color=GRAY, align="center", space_after=4)
    n.p("DRAM 셀 구조", size=13, bold=True, color=GOLD, align="center", space_after=2)
    n.p("10월 12일  DRAM 셀 구조 진화", size=22, bold=True, color=NAVY, align="center", space_after=2)
    n.p("6F²  →  4F²  →  3D", size=16, bold=True, color=NAVY2, align="center", space_after=8)
    n.p("CXMT VSG  ·  삼성 VCT  ·  SK하이닉스 VG  ·  공정 케이던스", size=11, color=GRAY, align="center", space_after=10)

    n.callout(
        "오늘 한 장으로 보면",
        [
            "CXMT는 2026년 말 서버용 DDR5 RDIMM에 4F²와 수직 서라운딩 게이트(VSG)를 넣겠다고 말했습니다. 출시 목표와 양산 수율은 따로 확인하는 숫자입니다.",
            "삼성·SK하이닉스도 수직 트랜지스터를 연구 중입니다. 다만 검증된 공정과 HBM에 자원을 두면서, 4F² 전면 양산은 서두르지 않는 쪽에 가깝습니다.",
            "구조 전환이 어려우면 공정 이행이 느려지고, DRAM 공급 증가도 함께 느려질 수 있습니다. 추격자 뉴스는 심리에 부담이지만, 그 자체로 주가의 핵심 변수로 단정하지 않습니다.",
        ],
        kind="key",
    )

    n.h2("강의 구성")
    n.table(
        ["파트", "내용", "녹화"],
        [
            ["1", "오늘 CXMT가 말한 것과 말하지 않은 것", "본편"],
            ["2", "6F² → 4F², 방 하나 줄이기", "본편 · 쉬운 설명"],
            ["3", "HBM과 3D DRAM은 다른 말", "본편"],
            ["4", "VSG · VG · VCT, 게이트와 PUC", "심화 · 넘겨도 됨"],
            ["5", "회사별 로드맵과 노드 이름", "본편"],
            ["6", "선두가 서두르지 않는 이유, CXMT의 유인", "본편"],
            ["7", "케이던스가 길어지면 공급도 느려진다", "본편 · 투자 결론"],
            ["8", "오전 노트: 장세, 하이닉스, AI 수요", "시간 되면"],
            ["9", "오전 노트: HD현대마린솔루션 · 골텐스", "시간 되면"],
        ],
        col_widths=[1.8, 9.4, 6.4],
    )

    n.h2("오프닝 멘트 (녹화용)")
    n.p("오늘은 DRAM 방 구조입니다. 지금 대부분의 방은 6F²입니다. 다음 후보는 4F²이고, 그 너머에 셀을 층으로 쌓는 3D DRAM이 있습니다. 오늘 뉴스의 주어는 CXMT입니다. 연말까지 서버용 DDR5에 4F²를 넣겠다고 했습니다. 결론부터 말하면, 이 발표만으로 삼전닉스 주가를 다시 쓰지 않습니다. 볼 것은 수율, 비트당 원가, 그리고 선두 업체들의 공정 전환 속도입니다.")

    # ── 0 ──────────────────────────────────────────────
    n.h1("오늘 숫자 한 장", num="0.")
    n.table(
        ["항목", "숫자", "한 줄"],
        [
            ["CXMT 4F²", "연말 서버 DDR5 RDIMM 계획\nVSG, 4F² 특허 패밀리 300건+ 주장", "출시 일정 ≠ 대량 양산"],
            ["셀 면적", "6F² → 4F²\n면적 −33%, 배열 셀 수 1.5배", "칩 용량·원가는 수율 차감 후"],
            ["CXMT G5", "액티브 하프피치 11.95nm\nG4 대비 총 다이 +50% 이상 주장", "1c·1γ·0a라는 노드명이 아님"],
            ["DRAM 매출 점유 2Q26", "삼성 39.4% · 하이닉스 24.9%\n마이크론 23.3% · CXMT 9.5%", "4위. 추격자 뉴스와 규모는 별개"],
            ["삼성 일정", "ISSCC 2026에 4F²+본딩 시제품\n양산 언급은 2028년 전후", "9월에 D0a 본경로를 본딩으로"],
            ["SK하이닉스", "2025 VG+PUC 시연\n2026 비트라인 차폐·백 게이트", "논문 시연 ≠ 양산 시점"],
            ["메리츠 · 하이닉스", "3Q26 OP 80.1조 vs 컨센 74조\nTP 320만 · 27년 OP 454조", "검증은 27년 이익과 PBR 4배"],
            ["골텐스", "2억 4,750만 달러 · 매출 1.51억 달러\n다올 TP 29만 → 31만", "EBITDA 15배는 자료 기준"],
        ],
        col_widths=[3.8, 7.2, 6.6],
    )
    n.p("점유율은 트렌드포스가 10월 12일 기사에서 인용한 2분기 매출 기준입니다. CXMT 특허 300건대와 G5 다이 증가는 회사 발표입니다.", size=10, color=GRAY)

    # ── 1 ──────────────────────────────────────────────
    n.h1("오늘 CXMT가 말한 것", num="1.")
    n.callout(
        "한 줄 결론",
        [
            "10월 9~10일 상하이 집적회로·칩렛 콘퍼런스에서 차오칸위 CXMT 총재가 연말 서버용 DDR5 RDIMM 계획을 공개했습니다.",
            "도구는 자체 VSG 트랜지스터와 4F² 셀입니다. 제품 스펙, 용량, 속도, 수율, 고객 인증은 이번 발표에 없습니다.",
        ],
        kind="key",
    )

    n.h2("1) 사실로 말할 수 있는 범위")
    n.bullet("행사: 10월 9~10일 상하이. 보도는 12일 연합뉴스, 서울경제, 트렌드포스, 중국 매체.")
    n.bullet("제품 방향: 서버용 DDR5 RDIMM. 모바일 LPDDR이 첫 적용 제품은 아니라고 회사가 설명.")
    n.bullet("기술 설명: 채널을 수직으로 두고 게이트가 채널을 둘러싸 누설전류를 줄이고 셀을 줄인다.")
    n.bullet("회사 주장: 4F² 관련 특허 패밀리 300건 이상.")
    n.bullet("직전 이정표: 9월 G5 플랫폼 양산과 LPDDR6 양산을 발표. G5와 이번 4F²는 같은 발표가 아닙니다.")

    n.h2("2) 이번 발표에 없는 것")
    n.bullet("다이 용량, 속도 등급, 모듈 용량.")
    n.bullet("양산 웨이퍼 규모, 수율, 비트당 원가.")
    n.bullet("서버 고객 인증, 인텔·AMD 플랫폼 검증.")
    n.bullet("칩 전체가 4F²인지, 일부 블록만 4F²인지. 트렌드포스는 머니투데이를 인용해 부분 적용 가능성을 적었습니다.")

    n.callout(
        "서버를 고른 의미",
        [
            "CXMT의 기존 무게중심은 모바일·컨슈머 쪽에 가깝습니다. 서버 DDR5는 24시간 동작과 고속 전송의 오류 허용이 더 빡빡합니다.",
            "그래서 이번 발표는 기술 이름 발표이면서, 서버 시장으로 제품군을 넓히겠다는 사업 발표이기도 합니다.",
        ],
        kind="blue",
    )

    n.h2("3) 주가에 붙이기 전에")
    n.p("4F² 발표가 나온 날 주가가 내린 종목이 있습니다. 그 사실만으로 기술 발표가 하락의 원인이라고 말할 근거는 부족합니다. 같은 날 시장에는 오픈AI 매출 노이즈, 애플 부품 주문 축소, 중동을 포함한 매크로 불안이 겹쳐 있고, CPI를 기다리는 구간입니다.")
    n.p("CXMT 주가에 대한 당일 코멘트는 이렇습니다. 공모가 대비 약 5.6배, 8월 17일 종가 고점 대비 약 21.8% 하락. 이 시세 코멘트는 당일 메모 기준입니다.")
    n.callout(
        "포지션 문장",
        [
            "추격자 뉴스는 거의 항상, 최소한 투자심리에는 부담을 줍니다.",
            "그래도 양산 수율을 보기 전에는 큰 의미를 두지 않습니다. 실제 양산 과정에서 공급 증가 속도가 오히려 느려질 여지도 있습니다.",
            "삼전닉스의 전략과 CXMT의 사정이 다를 뿐입니다.",
        ],
        kind="note",
    )

    # ── 2 ──────────────────────────────────────────────
    n.h1("6F²에서 4F²로", num="2.")
    n.callout(
        "한 줄 결론",
        [
            "DRAM 셀은 트랜지스터 하나와 커패시터 하나입니다. 고집적의 1차 수단은 이 방의 바닥 면적을 줄이는 것입니다.",
            "6F²는 지금 양산의 기본 평면도입니다. 4F²는 그 방을 2F×2F 정사각형으로 줄이려는 다음 평면도입니다.",
        ],
        kind="key",
    )

    n.h2("1) F부터")
    n.p("F는 그 공정에서 반복할 수 있는 최소 피치의 단위입니다. 방 크기를 ‘몇 F²인가’로 부르는 이유는, 선폭이 줄어들어도 방의 모양 비율을 따로 말할 수 있기 때문입니다. 공정 노드 이름(1c, 0a)과 셀 구조 이름(6F², 4F²)은 다른 축입니다. 1c이면서 6F²일 수 있고, 나중에 0a대에서 4F²를 붙일 수 있습니다.")

    n.h2("2) 쉬운 그림")
    n.p("DRAM은 데이터를 저장하는 아주 작은 방입니다. 목표는 더 작게, 더 많이, 더 싸게입니다.")
    n.h3("6F² — 지금 대부분의 방")
    n.bullet("방 하나의 바닥 = 3F × 2F = 6F². 직사각형입니다.", bold_lead="개념. ")
    n.bullet("워드라인과 비트라인이 직각이고, 트랜지스터는 커패시터 옆 평면에 자리를 잡습니다.", bold_lead="배치. ")
    n.bullet("트렌치 커패시터 또는 스택 커패시터. 지금 주류는 스택에 가깝고, 셀 트랜지스터는 묻힌 워드라인·리세스 채널 계열로 미세화를 버텨 왔습니다.", bold_lead="소자. ")
    n.bullet("설계가 익숙하고 기존 라인을 이어 가기 좋습니다. 더 줄이면 전류 제어와 옆 셀 간섭이 동시에 나빠져, 이미 한계에 가깝습니다.", bold_lead="성격. ")
    n.p("비유하면 단층 아파트입니다. 짓기는 안정적이고 수율도 관리된 구조입니다. 대지를 더 잘게 쪼개기가 어려워진 상태입니다.")

    n.h3("4F² — 같은 대지에 칸을 더")
    n.bullet("방 하나의 바닥 = 2F × 2F = 4F². 정사각형입니다.")
    n.bullet("트랜지스터를 옆으로 눕혀 두면 2F×2F 안에 커패시터와 같이 들어가지 않습니다. 그래서 채널을 수직으로 세웁니다.")
    n.bullet("커패시터는 그 수직 트랜지스터 위쪽 공간에 올리는 그림이 공개 설명의 공통분모입니다.")
    n.p("비유하면 같은 대지에 집을 더 촘촘히 짓는 것입니다. 벽과 배관을 수직으로 바꿔야 해서, 방 크기만 10% 줄이는 미세화와는 공정의 종류가 다릅니다.")

    n.h2("3) 33%와 50%를 같이 말한다")
    n.table(
        ["", "6F²", "4F²"],
        [
            ["셀 바닥", "3F × 2F 직사각형", "2F × 2F 정사각형"],
            ["셀 면적", "6", "4  ·  약 33% 감소"],
            ["같은 배열 면적의 셀 수", "1배", "1.5배  ·  약 50% 증가"],
            ["보도가 쓰는 칩 밀도", "기준", "같은 면적에서 약 30~50%"],
            ["비트당 원가", "검증된 공정", "식각·증착·본딩·수율 차감 후"],
        ],
        col_widths=[4.6, 6.5, 6.5],
    )
    n.p("셀만 보면 50%입니다. 칩에는 방 말고 도로와 관리실, 즉 센스앰프와 주변회로가 있습니다. 불량 구제용 여유 셀과 수율도 빼야 합니다. 그래서 제품 용량이 곧바로 50% 는다고 말하지 않습니다. 30~50%라는 보도 범위는 그 간격을 반영합니다.")
    n.callout(
        "원가 문장",
        [
            "4F²의 목표는 웨이퍼 한 장에서 비트를 더 뽑는 것입니다.",
            "식각·증착·본딩·검사 비용이 늘고 수율이 낮으면, 정상 칩으로 팔 수 있는 비트는 오히려 줄 수 있습니다.",
            "면적 절감과 비트당 원가 절감은 같은 문장이 아닙니다.",
        ],
        kind="note",
    )

    n.h2("4) 수도꼭지")
    n.p("트랜지스터는 전기를 켜고 끄는 수도꼭지이고, 게이트는 그 손잡이입니다.")
    n.bullet("수평형: 채널과 게이트가 바닥에 눕습니다. 방을 줄일수록 손잡이가 물줄기를 붙잡는 힘이 약해지고, 옆방과 간섭이 커집니다.", bold_lead="기존. ")
    n.bullet("수직 채널·게이트: 채널을 세워 게이트가 옆에서 감싸거나 제어합니다. 바닥 면적을 줄이면서 전류 제어 길이는 높이로 벌리려는 접근입니다.", bold_lead="4F². ")
    n.p("이 수직 계열 안에서 회사마다 이름이 다릅니다. VSG, VG, VCT입니다. 이름은 4번에서 나누고, 여기까지가 쉬운 설명의 끝입니다.")

    n.callout(
        "녹화 전에 고친 문장 1",
        [
            "초안에 ‘4F²는 주로 MSG, 즉 변형 스태거드 게이트’라는 문장이 있었습니다. 삼성·SK하이닉스·CXMT가 공개한 4F² 용어는 VCT, VG, VSG입니다.",
            "녹화에서는 MSG를 4F²의 대표 구조로 말하지 않습니다.",
        ],
        kind="note",
    )

    # ── 3 ──────────────────────────────────────────────
    n.h1("HBM, 4F², 3D DRAM", num="3.")
    n.callout(
        "한 줄 결론",
        [
            "셋 다 ‘위로’라는 말이 들어가 서로 섞이기 쉽습니다. 쌓는 대상이 다릅니다.",
            "HBM은 이미 파는 제품입니다. 4F²는 아직 한 층의 셀 배열입니다. 3D DRAM은 셀 층 자체를 쌓는 다음 공정입니다.",
        ],
        kind="key",
    )
    n.table(
        ["이름", "쌓는 것", "지금 위치"],
        [
            ["HBM", "완성된 DRAM 다이를 TSV로 적층", "양산 제품. AI 가속기의 대역폭"],
            ["4F²", "셀 안에서 채널을 수직으로. 배열은 한 층", "개발·일부 시연. CXMT는 연말 제품 목표"],
            ["3D DRAM", "낸드처럼 셀 층을 공정으로 여러 층", "연구·장기 로드맵. 대규모 양산 전"],
            ["PUC · 웨이퍼 본딩", "주변회로 웨이퍼를 셀 웨이퍼 아래에 접합", "4F²의 면적 이득을 남기는 보조 구조"],
        ],
        col_widths=[3.8, 7.6, 6.2],
    )
    n.p("HBM이 적층 제품이라는 이유로 3D DRAM의 예시가 되지는 않습니다. HBM 안의 다이도 지금은 6F² 계열 셀입니다. 반대로 4F²를 쓴 다이를 나중에 HBM으로 쌓을 수는 있습니다. 셀 구조와 패키지 적층은 곱해지는 선택입니다.")
    n.p("디일렉은 VCT를 옆으로 쌓는 구조가 3D DRAM의 출발점이라고 전했습니다. SK하이닉스도 4F² 수직 게이트와 3D DRAM을 장기 방향에 같이 올려 두었습니다. 그래서 4F²는 최종 목적지일 수도 있고, 3D로 가기 전의 중간 층일 수도 있습니다.")
    n.callout(
        "기업이 계산하는 것",
        [
            "4F²를 대규모로 깐 뒤 다시 3D로 라인을 바꾸면, 그 교체 비용까지 오늘 투자 판단에 들어옵니다.",
            "4F² 투자는 장기 3D 전환 계획과 붙여서 봅니다.",
        ],
        kind="blue",
    )
    n.callout(
        "녹화 전에 고친 문장 2",
        [
            "초안의 3D 예시에 HBM이 1번으로 들어가 있었습니다. 녹화에서는 HBM을 ‘이미 돈 버는 적층 제품’, 3D DRAM을 ‘셀을 층으로 쌓는 미래 공정’으로 나눠 말합니다.",
        ],
        kind="note",
    )

    # ── 4 ──────────────────────────────────────────────
    n.h1("심화  ·  VSG, VG, VCT", num="4.")
    n.p("여기부터는 어렵습니다. 녹화 시간이 짧으면 이 파트는 넘기고 5번 로드맵으로 가면 됩니다. 넘겨도 오늘 결론은 유지됩니다.", size=10.5, color=AMBER, bold=True)
    n.callout(
        "한 줄 결론",
        [
            "CXMT VSG와 SK하이닉스 VG는 같은 방향의 수직 게이트 계열입니다. 삼성 VCT도 채널을 세운다는 점에서 4F²의 물리 원리가 완전히 다른 기술은 아닙니다.",
            "이름만으로 세 회사의 단면이 같다고 말하거나, 누가 더 낫다고 말하지 않습니다. 공개된 맞대결 성능 자료가 없습니다.",
        ],
        kind="key",
    )

    n.table(
        ["회사", "공개 이름", "강조점", "같이 공개된 것"],
        [
            ["CXMT", "VSG\nVertical Surrounding Gate", "수직 채널을 게이트가 둘러쌈\n누설·단채널 억제, 셀 축소", "연말 서버 DDR5 계획\n특허 패밀리 주장"],
            ["SK하이닉스", "VG\nVertical Gate", "4F² 수직 게이트 셀", "2025 PUC·웨이퍼 본딩\n2026 비트라인 차폐·백 게이트"],
            ["삼성전자", "VCT\nVertical Channel Transistor", "수직 채널. 커패시터를 트랜지스터 위에", "IGZO 채널 연구\n웨이퍼 본딩·PUC 검토"],
        ],
        col_widths=[2.8, 4.2, 5.6, 4.0],
    )

    n.h2("1) 게이트 구조와 주변회로는 별개")
    n.p("수직 게이트는 셀 트랜지스터의 문제입니다. PUC(Peri Under Cell, 셀 아래 주변회로)와 웨이퍼 본딩은 그 옆의 관리실을 지하로 내리는 문제입니다. 하나를 연구한다고 다른 하나까지 양산된 것은 아닙니다.")
    n.bullet("센스앰프, 디코더, 전압 회로를 셀 배열 옆에 두면, 셀을 줄여도 칩에서 남는 면적이 작습니다.")
    n.bullet("주변회로를 다른 웨이퍼에 만들고 셀 웨이퍼 아래에 붙이면, 배열 면적 이득이 제품에 더 많이 남습니다.")
    n.bullet("같은 웨이퍼에 수직 기둥과 주변회로를 같이 두면, 고열 공정이 아래 회로를 망가뜨릴 수 있습니다. 디일렉은 ISSCC 2026 발표를 설명하며, 그래서 셀과 주변을 나눠 구리 하이브리드 본딩으로 붙인다고 적었습니다.")

    n.h2("2) SK하이닉스 — 논문이 말하는 범위")
    n.bullet("2025년 VLSI: 4F² 배열에 수직 게이트와 PUC를 퓨전 본딩·웨이퍼 간 콘택으로 붙여 전기적으로 연결. 백 게이트 바이어스로 문턱전압을 제어. 열처리로 소스·드레인 정션을 맞춰 트랜지스터 특성을 맞춤. 여기서 정션은 웨이퍼 접착면이 아닙니다. 회사가 ‘처음 통합 시연’이라고 적은 범위입니다.")
    n.bullet("2026년 후속: 그 구조 위에서 비트라인 차폐(BLS)와 공유 백 게이트를 봐, 센싱 잡음과 읽기·쓰기를 확인. PUC 자체가 2026년에 처음 붙은 것은 아닙니다.")
    n.p("비트라인 차폐는 줄이 너무 가까워 옆 비트라인이 신호를 오염시키는 문제를 가리기 위한 구조입니다. 백 게이트는 수직 채널의 문턱전압을 몸통 쪽에서 한 번 더 잡는 손잡이입니다.")

    n.h2("3) 삼성 — VCT와 IGZO")
    n.bullet("IGZO는 인듐·갈륨·아연 산화물입니다. 실리콘보다 꺼진 상태의 누설을 낮추려고 채널 소재로 검토합니다. 좁은 셀에서 데이터 보존이 목적입니다.")
    n.bullet("공개 논문의 흐름은 2023년 적층 시연, 2025년 저접촉저항·10년 신뢰성, 2026년 SID 발표로 이어집니다. 소자 숫자로 누설 0.1 aA/μm 미만, 온전류 약 49.5 μA/μm가 논문에 있습니다. 양산 칩 대 CXMT 비교치는 아닙니다.")
    n.bullet("4월 디일렉: 10a 웨이퍼에서 4F²+VCT 워킹다이를 확인. 채널을 실리콘에서 IGZO로 바꿨다는 업계 설명. 워드라인 금속(티타늄나이트라이드와 몰리브덴)은 아직 저울질.")
    n.p("이 연구 결과만으로 삼성 양산용 4F² DRAM 전체 구조가 확정된 것은 아닙니다. 9월 로드맵 수정은 5번에서 말합니다.")

    n.h2("4) CXMT VSG를 읽을 때")
    n.bullet("회사가 강조한 핵심은 ‘둘러싸는 게이트’입니다. 수직 채널의 전기 제어를 게이트가 사방에서 한다는 설명입니다.")
    n.bullet("SK의 VG도 수직 게이트이고, 백 게이트와 비트라인 차폐를 따로 공개했습니다. 이름이 다르다고 단면이 완전히 같다고 말할 수도, 완전히 다르다고 단정할 수도 없습니다.")
    n.bullet("삼성의 IGZO VCT와 CXMT VSG의 속도·누설·수율을 나란히 놓은 자료는 공개되지 않았습니다.")

    n.callout(
        "심화 파트를 한 문장으로 건너뛸 때",
        [
            "세 회사 모두 채널을 세우는 쪽으로 4F²를 연구하고, 게이트 이름과 주변회로 본딩은 별개이며, 누가 양산에서 앞서는지는 수율 전엔 말하지 않는다.",
        ],
        kind="blue",
    )

    # ── 5 ──────────────────────────────────────────────
    n.h1("로드맵과 공정 이름", num="5.")
    n.callout(
        "한 줄 결론",
        [
            "미세화 이름(1a→1b→1c→0a)과 셀 구조(6F²→4F²)와 CXMT 세대명(G3·G4·G5)을 한 줄에 등호로 묶지 않습니다.",
            "삼성 0a의 뜻은 4월 보도와 9월 보도가 다릅니다. 강의에서는 9월 이후를 현재 표로 둡니다.",
        ],
        kind="key",
    )

    n.h2("1) 노드 이름을 먼저 번역")
    n.table(
        ["부르는 말", "누구의 말", "의미"],
        [
            ["1x → 1y → 1z → 1a → 1b → 1c", "삼성·SK 계열", "10나노급 미세화의 순서. 지금 양산 경쟁의 본류"],
            ["1α → 1β → 1γ", "마이크론", "같은 10나노급을 그리스 문자로 부름. 1γ를 1c와 무조건 등호로 두지 않음"],
            ["10a · D0a · 0a", "삼성 서브 10나노 첫 세대", "디일렉은 선폭 추정을 9.5~9.7nm로 적음. 오늘 표의 0a"],
            ["10b · 0b / 10d", "그 다음 세대", "SK의 4F² 착수 시점으로 4월에 10b가 거론. 10d는 3D 전환 언급"],
            ["G3 / G4 / G5", "CXMT 자체 세대", "G3 기존 양산, G4 DDR5 주력, G5는 9월 양산 발표. 4F² 제품명 아님"],
        ],
        col_widths=[5.6, 4.4, 7.6],
    )
    n.p("오늘 코멘트의 ‘6F를 0a까지, 4F는 그 다음’ ‘SK는 0b부터’는 이 번역을 깔고 읽습니다. 0a는 삼성 10a·D0a, 0b는 10b에 대응시켜 말하면 됩니다.")

    n.h2("2) 회사별 베팅")
    n.table(
        ["업체", "6F²를 이어 가는 구간", "4F²", "그 다음"],
        [
            ["삼성전자", "1c까지는 검증된 6F² 연장\n0a의 본경로는 9월 기준 본딩", "VCT는 D0a-V로 분리\n양산 언급은 2028년 전후", "VCT를 층으로 쌓는\n3D DRAM"],
            ["SK하이닉스", "4월 업계 설명: 10a는 6F²\n2026년 1c 출하 확대", "10b부터 4F²·VCT\n삼성보다 한 세대 늦게", "4F²와 3D를\n장기 로드맵에 병기"],
            ["마이크론", "1β·1γ로 기존 구조를 연장", "4F²를 건너뛰는 베팅\n(4월 디일렉)", "3D DRAM 직행\n고위험·고수익"],
            ["CXMT", "G4 주력, G5로 밀도 한 단계\n둘 다 이번 4F² 발표와 별개", "연말 서버 DDR5에 VSG\n부분 적용 가능성", "3D 직행이라는\n4월 중국 서사는 수정"],
        ],
        col_widths=[2.8, 5.2, 4.8, 4.8],
    )

    n.h3("삼성 — 4월과 9월을 둘 다 말한다")
    n.bullet("2026년 2월 ISSCC: 4F²에 VCT와 웨이퍼 간 하이브리드 본딩을 넣은 16Gb급 시제품을 공개했다는 후속 보도.")
    n.bullet("2026년 4월 24일 디일렉: 3월에 만든 10a 웨이퍼에서 워킹다이 확인. 올해 개발 완료, 2027년 품질 테스트, 2028년 양산 이관. 10a·10b·10c에 4F²+VCT, 10d에서 3D. 당시 설명은 SK가 10b에서 4F²를 시작하고, 마이크론과 중국 업체는 4F²를 건너뛴다는 쪽이었습니다.")
    n.bullet("2026년 9월 23일 ZDNet: D0a의 본경로를 VCT에서 B1b, 즉 웨이퍼 투 웨이퍼 하이브리드 본딩으로 바꿈. 원래 D0a로 부르던 VCT는 D0a-V. 본딩은 CMOS 이미지센서와 고적층 낸드에서 이미 써 본 공정이라 양산 위험이 낮다는 해석. 본딩 D0a의 상용화는 일러야 약 2년 뒤, 투자 일정은 내년 중반께 구체화될 수 있다는 업계 추정.")
    n.bullet("2026년 10월 12일 트렌드포스: 삼성은 본딩 상용화를 우선하고, 시장 진입은 2028년 전으로 보기 어려우며, 4F²를 언제 전면 통합할지의 확정 일정은 없다고 정리. 다른 보도는 4F²를 D0a로 개명한 B1b에 넣으려 한다는 시각도 전합니다.")
    n.callout(
        "그래서 오늘 표는 이렇게 읽습니다",
        [
            "‘삼성: 6F²를 0a까지 유지하고, 그 다음 4F².’",
            "9월 이후 이 문장의 정확한 뜻은, 0a의 본경로는 본딩으로 기존 셀 구조를 더 밀고, 4F²·VCT는 D0a-V라는 병행 트랙이라는 것입니다.",
            "‘SK: 0a까지 6F², 0b부터 4F², 삼성보다 한 박자 늦다’는 4월 디일렉의 세대 차이입니다. 삼성이 VCT를 본경로에서 빼면 누가 한 박자 늦은지는 다시 봅니다.",
        ],
        kind="note",
    )

    n.h3("마이크론과 CXMT")
    n.p("마이크론이 4F²를 건너뛰고 3D로 간다는 그림은 4월 업계 설명입니다. 당일 투자 프레임에서는 HBM4에 1β, HBM4E와 차세대 DDR5에 1γ를 쓰는 쪽으로 정리합니다. 고위험·고수익의 구조 베팅과, 당장 팔리는 HBM의 공정 선택이 같이 있습니다.")
    n.p("4월에 ‘중국 업체는 4F²를 건너뛴다’고 한 문장은 오늘로 오면 수정입니다. CXMT는 4F² 서버 제품을 연말 목표로 올려 두었습니다. 건너뛰기가 아니라, 선두보다 제품 일정 발표를 먼저 한 쪽에 가깝습니다. 발표가 양산 리더십은 아닙니다.")

    n.h2("3) G5의 11.95nm")
    n.bullet("2026년 9월 20일 허페이. CXMT가 G5 양산과 24Gb LPDDR5X를 발표.")
    n.bullet("액티브 영역 하프피치 11.95nm. 풀 피치로 보면 23.9nm. 수단은 EUV가 아니라 SAQP, 즉 자가정렬 4중 패터닝.")
    n.bullet("회사 주장: G4 대비 웨이퍼당 총 다이 50% 이상. 총 다이는 웨이퍼에 그릴 수 있는 개수이고, 테스트를 통과한 양품 다이가 아닙니다.")
    n.bullet("2026년 초 자료에서도 G4 비중 확대가 확인됩니다. G3는 기존 양산 기반, G4는 DDR5를 받친 주력, G5는 그 위의 밀도 단계입니다. 4F²는 이 세대명 옆에 병존하는 구조 베팅입니다.")
    n.callout(
        "11.95를 노드 이름과 비교하지 않는 이유",
        [
            "11.95nm는 메모리 배열의 액티브 하프피치입니다. 삼성의 1c, 마이크론의 1γ, 0a의 선폭 추정(9.5~9.7nm)과 같은 자의 숫자가 아닙니다.",
            "외부에서는 G4를 1z 전후, G5를 그보다 한 단계 앞으로 추정하기도 합니다. 어느 추정으로도 G5를 1c나 0a와 같다고 말하면 안 됩니다.",
            "격차는 수율, 비트당 원가, 대규모 출하로 판단합니다. 하프피치 하나로는 부족합니다.",
        ],
        kind="bear",
    )

    n.h2("4) 지금 돈과 연결된 공정")
    n.table(
        ["업체", "당일 프레임에서 볼 적용"],
        [
            ["삼성전자", "1c를 HBM4에 적용했다는 점이, 공개된 기술 적용의 현재 차별점"],
            ["SK하이닉스", "1c 기반 LPDDR6 개발과 HBM4 생산 확대. 2026년 1c 출하는 HBM만이 아니라 범용 DRAM도 포함"],
            ["마이크론", "HBM4에는 1β. 1γ는 HBM4E와 차세대 DDR5"],
            ["CXMT", "G5 밀도는 주목. 수율·비트당 원가·대규모 출하가 확인되기 전엔 격차를 확정하지 않음"],
        ],
        col_widths=[3.6, 14.0],
    )

    # ── 6 ──────────────────────────────────────────────
    n.h1("왜 선두는 서두르지 않나", num="6.")
    n.callout(
        "한 줄 결론",
        [
            "삼성전자와 SK하이닉스 모두 4F²를 개발하고 있습니다. 연구 중인 기술을 언제, 어떤 제품에, 어느 규모로 양산할지는 별도 결정입니다.",
            "CXMT에는 선두와 다른 사업 유인이 있습니다. 소극적인 것이 아니라, 자원 배분이 다른 것입니다.",
        ],
        kind="key",
    )

    n.h2("배경 다섯 가지")
    n.h3("① 셀 면적은 줄고, 제조 난도는 크게 오릅니다")
    n.p("4F²는 기존 셀을 조금 더 작게 줄이는 작업이 아닙니다. 채널과 게이트의 방향을 바꾸고, 누설전류·셀 간 간섭·데이터 보존을 동시에 맞춰야 합니다. 방을 촘촘히 짓는 동시에 배선과 벽 구조를 바꾸는 일에 가깝습니다.")
    n.h3("② 면적 절감이 곧 원가 절감은 아닙니다")
    n.p("새 식각·증착, 추가 본딩, 검사와 수율 관리에 비용이 더 들면 비트당 원가의 개선 폭은 작아집니다. 수율이 낮으면 웨이퍼당 비트는 늘어도 팔 수 있는 칩은 줄어듭니다. 양산 경제성이 나오기 전에 잘 도는 6F² 라인을 급히 대체하기 어렵습니다.")
    n.h3("③ 기존 미세화에도 남은 개선이 있습니다")
    n.p("1c 같은 차세대 공정으로 옮기면 기존 생산 기반을 쓰면서 집적도와 전력 특성을 개선할 수 있습니다. 셀 구조를 전면 교체하는 쪽보다 양산 위험을 관리하기 쉽습니다. SK하이닉스는 2026년 1c 출하 확대를 추진하고, HBM과 범용 DRAM을 같이 늘리는 계획입니다.")
    n.h3("④ HBM에 넣을 자원이 따로 있습니다")
    n.p("HBM은 AI 가속기 수요와 바로 연결됩니다. DRAM 다이와 패키징을 확보하는 일이 당장의 매출·고객과 닿아 있습니다. 인력·자본·생산능력을 4F² 조기 양산에 몰지, 검증된 공정으로 HBM과 범용 DRAM을 늘릴지는 자원 배분 문제입니다.")
    n.h3("⑤ 4F²는 중간 단계일 수 있습니다")
    n.p("SK하이닉스는 4F² 수직 게이트와 3D DRAM을 장기 방향에 같이 올렸습니다. 삼성도 수직 채널과 3D DRAM을 연구해 왔습니다. 4F²를 크게 깐 뒤 다시 구조를 바꾸는 비용까지 보면, 4F² 투자는 3D 전환 계획과 붙여 판단합니다.")

    n.h2("CXMT의 유인은 다릅니다")
    n.bullet("미세공정만으로 선두를 따라가는 속도로는 부족합니다. 새 셀 구조로 밀도와 원가 경쟁력을 만들 유인이 더 큽니다.", bold_lead="기술 격차. ")
    n.bullet("모바일·PC 중심에서 서버 DDR5로 제품 정의를 바꾸려는 전략입니다. 24시간 서버의 신뢰성 기준이 더 높다는 점은 회사도 인정하는 난도입니다.", bold_lead="서버 진입. ")
    n.bullet("연말 출시를 목표로 말했습니다. 양산 수율과 서버 고객 인증은 그 다음 확인 항목입니다.", bold_lead="일정. ")
    n.callout(
        "같은 기술을 다르게 쓰는 이유",
        [
            "선두에게 4F²는 잘 도는 1c·HBM을 대체할 수 있을 때의 선택입니다.",
            "CXMT에게 4F²는 기존 경로만으로는 좁혀지지 않는 격차를 구조로 건너뛰려는 선택입니다.",
        ],
        kind="blue",
    )

    # ── 7 ──────────────────────────────────────────────
    n.h1("케이던스와 투자 결론", num="7.")
    n.callout(
        "한 줄 결론",
        [
            "과거에는 대략 1.5년마다 새 공정이 나오며 비트 공급이 늘었습니다. 지금은 그 주기를 유지하기 어렵습니다.",
            "이행이 느려지면 공급 증가도 둔화될 수 있습니다. DRAM 업황에서는 그 둔화가 가격에 우호적일 수 있습니다. 동시에 기술 개발 CAPEX는 더 무거워집니다.",
        ],
        kind="key",
    )

    n.h2("왜 주기가 길어지나")
    n.h3("이유 1  ·  물리적 한계")
    n.p("패턴이 너무 작아 전자현미경으로도 보기 어렵고, 공정 오차가 바로 불량이 됩니다. 10나노급 아래에서는 워드라인 피치, 비트라인과 스토리지 노드의 간격, 커패시터 종횡비가 동시에 빠듯해집니다.")
    n.h3("이유 2  ·  4F²의 병목은 식각")
    n.p("이론은 채널을 세우면 됩니다. 생산은 그 채널을 무너지지 않게 깎는 일입니다.")
    n.bullet("선 간격이 좁은 상태에서 실리콘을 가늘고 높은 기둥으로 깎아야 합니다. 고종횡비 식각입니다.")
    n.bullet("게이트는 그 기둥 둘레에 고르게 붙어야 합니다. 조금 기울거나 두께가 달라지면 셀이 죽습니다.")
    n.bullet("커패시터도 깊게 파야 용량이 나옵니다. 셀 바닥을 줄일수록 이 구멍은 더 가늘고 깊어집니다.")
    n.p("공개 설명의 문장으로 옮기면, 이론은 쉬운데 실제 생산의 난도가 급격히 올라갑니다.")
    n.h3("이유 3  ·  원가")
    n.p("더 작아지면 비트당 원가가 내려가야 투자가 정당해집니다. 공정 스텝이 늘면 웨이퍼 원가가 올라 방향이 반대가 될 수 있습니다. 수율이 그 사이에 있습니다.")

    n.h2("투자에서 가져갈 두 가지")
    n.callout(
        "1) 공급 증가 속도",
        [
            "테크 마이그레이션이 느려지면 비트 공급 증가가 제한됩니다.",
            "수요가 살아 있는 구간에서 이 둔화는 DRAM 가격에 우호적인 쪽으로 열릴 수 있습니다.",
            "CXMT의 4F² 시도가 당장 대량 양품으로 연결되지 않으면, 그 역시 공급을 즉시 늘리는 뉴스가 아닙니다.",
        ],
        kind="bull",
    )
    n.callout(
        "2) CAPEX 부담",
        [
            "개발이 어려워지면 같은 비트 증가를 만들기 위해 연구개발과 공정 투자가 더 듭니다.",
            "선두에게는 1c·HBM 확대와 4F²·3D 선행 투자가 한 예산 안에서 경쟁합니다.",
        ],
        kind="bear",
    )

    n.h2("확인 포인트")
    n.table(
        ["#", "볼 것", "이렇게 되면"],
        [
            ["1", "CXMT 연말 제품의 스펙·물량·고객", "샘플인지, 서버 인증 양산인지 갈림"],
            ["2", "4F²가 칩 전체인지 일부인지", "부분 적용이면 밀도 효과는 더 작음"],
            ["3", "수율과 비트당 원가", "면적 이득이 원가로 남는지를 결정"],
            ["4", "삼성 D0a 본딩 vs D0a-V", "2028년 전후 무엇이 먼저 라인에 서는가"],
            ["5", "SK 1c 범용 출하, HBM4", "4F²보다 먼저 실적에 닿는 공급"],
            ["6", "선두의 비트 증가율", "케이던스 둔화가 실제 공급 숫자로 보이는가"],
        ],
        col_widths=[1.4, 7.6, 8.6],
    )

    n.h2("본편 클로징 멘트")
    n.p("6F²에서 4F²로 가면 같은 웨이퍼의 칸이 늘고, 그 다음 한계는 셀을 층으로 쌓는 3D로 넘기려 합니다. HBM은 이미 다이를 쌓아 파는 제품이고, 3D DRAM은 그 셀의 공정을 쌓는 이야기입니다. CXMT는 서버 DDR5로 4F² 일정을 먼저 말했습니다. 삼성과 SK하이닉스는 개발은 하되, 1c와 HBM과 본딩으로 위험을 나누고 있습니다. 공급 증가가 느려질 수 있다는 쪽이 오늘 투자 결론이고, 수율이 나오기 전에는 추격 뉴스에 큰 의미를 두지 않습니다.")

    # ── 8 ──────────────────────────────────────────────
    n.h1("오전  ·  장세와 하이닉스", num="8.")
    n.p("아래는 같은 날 오전의 퀵코멘트입니다. DRAM 본편과 직접 연결되는 숫자만 남기고, 장세 코멘트는 당일 판단으로 적습니다.")

    n.h2("1) 메리츠증권 SK하이닉스 — 10월 12일")
    n.callout(
        "리포트 한 줄",
        [
            "3분기 영업이익 80.1조원으로 컨센서스 74조원을 8.2% 웃돌 것으로 보고, 목표주가를 310만원에서 320만원으로 올렸습니다. 투자의견은 매수 유지.",
            "검증 포인트는 2027년 영업이익 454조원 전망이 실현되는지, 그리고 2026~2027년 평균 PBR 4.0배가 정당한지입니다.",
        ],
        kind="key",
    )
    n.table(
        ["항목", "메리츠 추정 · 10월 12일"],
        [
            ["3Q26 영업이익", "80.1조원  ·  전분기 대비 +32%  ·  컨센서스 74조"],
            ["구성", "DRAM 출하 +13% · 판가 +22% · 영업이익 63조"],
            ["낸드", "출하 +4% · 판가 +15% · 영업이익 17조"],
            ["이익률", "영업이익률 약 80%"],
            ["연간", "2026년 영업이익 264조  ·  2027년 454조"],
            ["목표주가", "320만원. 2026~2027 평균 PBR 4.0배. 8일 종가 168.1만원"],
            ["HBM", "판매 비중이 높아 판가 상승을 다 못 받았으나, HBM4 공급으로 이익 기여 본격화"],
            ["모바일", "핵심 고객 계약이 LTA 논의로 재검토되며 공급자에 유리한 조건으로 이동"],
            ["가격 가정", "2027년 1분기 모바일 DRAM 판가 전분기 대비 +65% (한경 인용)"],
        ],
        col_widths=[4.2, 13.4],
    )
    n.p("메리츠는 주주환원이 이어질 것으로 봤습니다. 코멘트의 태도는 목표 상향을 기록하되, 2027년 이익 급증과 PBR 4배의 정당성을 확인 항목으로 남겨 두는 쪽입니다. 김선우 연구원 리포트입니다.")

    n.h2("2) 10월 14일 CPI와 장세")
    n.p("미국 현지 10월 14일 수요일 CPI를 앞둔 구간입니다. 당일 코멘트가 강조한 메커니즘은 베어 스티프닝입니다.")
    n.bullet("10년물 금리 상승폭이 2년물 금리 상승폭보다 큼.")
    n.bullet("장단기 금리차(10년 − 2년)가 확대됨.")
    n.bullet("장기채 가격은 하락 압력을 받고, 주식의 할인율은 올라감. 성장주 밸류에이션이 부담을 받음.")
    n.p("결과별 금리 수치 시나리오는 당일 메모에 숫자가 없어, 녹화에서는 이 메커니즘까지만 말합니다.")
    n.callout(
        "코스피 지지 — 당일 코멘트",
        [
            "AI 노이즈와 매크로 요인을 각각 1%대 중반, 합쳐 약 -3%의 빌미로 봅니다.",
            "1차 기준은 코스피 6400 초반대의 지지 여부입니다.",
            "한국시간 15일 ASML·TSMC 실적은 서프라이즈면 도움이 되고, 그렇지 않으면 영향은 제한적이라는 판단입니다.",
            "포지션은 상대적으로 안정적인 포트폴리오 믹스를 유지하고, 낙폭이 과도할 때만 접근하는 바벨입니다.",
        ],
        kind="note",
    )

    n.h2("3) AI 수요 코멘트 — GPT-6.1 Sol 컨텍스트")
    n.p("당일 오후 코멘트의 프레임은 ‘AI 수요의 방향은 그대로 고성장’입니다. 근거로 올린 제품 변화는 이렇습니다.")
    n.bullet("10월 11일 Thibault Sottiaux: Codex와 ChatGPT Work의 GPT-6.1 Sol 기본 컨텍스트를 27.2만 토큰에서 50만 토큰으로 확대. 발표 표현은 약 80%.")
    n.bullet("목적은 장시간 작업의 컨텍스트 압축(compaction) 빈도를 줄이고, 이전 맥락을 더 오래 유지하는 것.")
    n.bullet("50만을 다수 이용자의 기본값으로 두고, 이용자는 길이를 조절. 모델 최대는 100만 토큰. 기본값은 앞으로 더 올리겠다는 계획.")
    n.bullet("초점은 오래 자율 작업하는 에이전트의 맥락 유지와 작업 연속성.")
    n.p("메모리 강의와의 연결은 한 문장입니다. 컨텍스트와 에이전트 작업이 길어지면 고대역 메모리 수요의 방향 자체는 당일 코멘트에서 유지됩니다. 공급 쪽 변수는 7번의 케이던스입니다.")

    # ── 9 ──────────────────────────────────────────────
    n.h1("오전  ·  HD현대마린솔루션", num="9.")
    n.callout(
        "한 줄 결론",
        [
            "이미 운항 중인 배의 유지·보수·개조와 친환경·디지털 전환으로 오래 버는 회사입니다. 조선 신규 수주 사이클만으로 설명하면 반쪽입니다.",
            "골텐스 인수는 부품 공급에 글로벌 현장 정비망을 붙여, HD현대 배만이 아니라 남의 배(non-captive)까지 가려는 확장입니다. 15배 EBITDA가 맞으려면 교차판매와 반복 현금흐름이 보여야 합니다.",
        ],
        kind="key",
    )

    n.h2("1) 사업을 나눠 본다")
    n.p("비교는 애프터마켓, 엔진 부품, 친환경 개조, 선박 운영 솔루션, 벙커링을 쪼개서 합니다. 실적을 움직이는 것은 신규 수주뿐 아니라 전 세계 운항 선박 수, 선령, 유지보수 수요, 환경 규제입니다.")
    n.bullet("벙커링은 선박에 연료를 넣는 사업입니다. 주유소가 배에 기름을 넣는 그림입니다. HD현대오일뱅크 등과 연료를 조달하고, 국내 항만과 싱가포르 등에서 신조선·운항선에 공급한 뒤 매매 차익에서 물류·운영비를 뺍니다.")
    n.bullet("당일 코멘트: 매출의 약 30% 후반인 벙커링은 거의 본전(BEP)이고, 핵심 애프터마켓 영업이익률은 30%를 크게 넘습니다. 회사 전체 마진만 보면 이 구성이 묻힙니다.")
    n.p("2027년 컨센서스 PER 23배는 당일 코멘트 기준입니다. 중장기 조선 업황에 안정적으로 노출되고 싶은 투자자에게 애프터마켓 수익 구조를 보라는 취지입니다.")

    n.h2("2) 골텐스 — 숫자 검증")
    n.p("다올투자증권 10월 12일: ‘Goltens를 품고, 이제 남의 배도 탐한다.’ 목표주가 29만원에서 31만원. 8일 종가는 21만 9,500원(연합뉴스). 3분기는 환율 부담으로 눈높이가 낮은 구간이고, 애프터마켓 솔루션의 3개월 리드타임과 판가 전가가 수익성 방어의 핵심이라는 코멘트입니다.")
    n.table(
        ["항목", "초안 메모", "확인"],
        [
            ["인수대금", "2.5억 달러\n약 15배 EBITDA", "2억 4,750만 달러(약 3,315억 원)\n매도인 3곳에 각 8,251만 달러"],
            ["재원·종결", "—", "IPO 공모자금, 현금\n공시 예정일 2027-02-28\n골텐스 발표는 26년 4분기 말~27년 1분기 초"],
            ["2025 실적", "매출 1.51억 달러\nEBITDA 1,650만 달러", "매출 약 2,025억 원으로 1.51억 달러와 맞음\n순이익 약 111억 원(공시 보도)\nEBITDA 1,650만 달러는 다올·메모 기준\n2억 4,750만 ÷ 1,650만 = 15.0배"],
            ["거점", "15개국·28개국이\n한 줄에 섞임", "15개국 28개 거점\n수리 거점 28, 워크숍 19, 법인 31"],
            ["사람·고객", "1,300명·2,300명이\n한 줄에 섞임", "숙련 인력 약 1,300명\n인수 측 고객 2,300여 곳·선박 5,500여 척\n골텐스 보도자료는 연 3,700곳 이상 고객"],
        ],
        col_widths=[3.2, 5.4, 9.0],
    )
    n.p("구조는 미국 Goltens New York 지분 100%와 노르웨이 Goltens Oslo 직접 지분 41.07%를 사고, 그룹 내 보유분을 합쳐 실질 100%가 되는 형태입니다. 연합뉴스의 ‘지분 100%’는 이 실질 기준입니다. 기존 CEO 중심의 독립 경영을 유지한다는 방침입니다. 1940년 뉴욕 설립입니다.")

    n.h2("3) 인수가 비싼지 보려면")
    n.bullet("부품·솔루션 공급에 현장 정비망이 붙는 그림. 엔진 제조사를 뺀 MRO 커버리지에서 상위권이라는 회사 설명.")
    n.bullet("HD현대가 만든 배의 캡티브 수요를 넘어, 타사 엔진·타사 조선소 배까지 부품과 정비를 팔 수 있는지가 핵심.")
    n.bullet("다올의 확인 항목: 비계열 부품·솔루션 매출, 반복 수주, 현금흐름이 약 15배 EBITDA를 설명할 만큼 커지는지.")
    n.bullet("회사 발표에 있는 추가 시너지: 힘센(HiMSEN) 육상 발전의 현지 정비. NH투자증권(10월 12일, Not Rated)은 여기에 미국 거점을 통한 육상 발전·데이터센터용 엔진 정비까지 적었습니다. 본편의 주장으로 쓰기보다 NH의 추가 포인트로 구분합니다.")
    n.callout(
        "3분기와 인수 가치를 섞지 않는 문장",
        [
            "3분기는 환율과 판가 전가의 짧은 구간입니다.",
            "골텐스의 가치는 교차판매와 신규 고객이 반복 매출로 나오는지의 긴 구간입니다.",
        ],
        kind="blue",
    )

    n.h2("4) 비교군 — 그대로 겹치지 않는다")
    n.table(
        ["회사", "2025년", "반복 매출", "HD현대마린과 다른 점"],
        [
            ["Wärtsilä\n핀란드", "순매출 69.14억 유로\n비교가능 영업이익률 12.0%", "서비스 52%\n(35.75억 유로)", "선박 엔진·추진·배기가스·디지털·수명주기.\n에너지 사업이 있어 그룹 마진을 그대로 비교하면 왜곡"],
            ["Kongsberg\nMaritime", "매출 271억 NOK\n(271.23억, +10%)\n영업이익률 12.7%", "애프터마켓\n연간 약 54%\n연차 설명은 약 50%", "자동화·추진·제어·해양 기자재.\n부품+벙커링+개조를 한 회사에 묶은 구조는 아님"],
            ["HD현대\n마린솔루션", "당일 코멘트의\n2027년 PER 23배", "AM 영업이익률\n30%대 초과\n벙커링은 BEP", "조선 애프터마켓에 벙커링이 섞인 믹스.\n골텐스로 현장 정비가 추가"],
        ],
        col_widths=[3.3, 4.6, 4.0, 5.7],
    )
    n.p("비교할 축은 서비스 매출 비중, 영업이익률, 장기 서비스 계약, 친환경 기술의 수익화, 설치 기반의 반복 매출입니다. 그룹 전체 숫자를 한 줄로 견주면 에너지·방산·벙커링이 결론을 흐립니다. 콩스베르그 마리타임 매출은 2025년 4분기 보고서, 바르질라는 2025년 연차·결산 기준입니다.")

    # ── close ──────────────────────────────────────────
    n.h1("클로징", num="10.")
    n.callout(
        "녹화에서 가져갈 세 문장",
        [
            "1) 4F²는 6F² 방을 2F×2F로 줄이려고 채널을 세우는 구조입니다. 면적 33% 감소는 셀 기준이고, 비트당 원가는 수율과 공정 비용 다음입니다.",
            "2) CXMT VSG, SK VG, 삼성 VCT는 같은 방향입니다. 삼성 0a의 본경로는 9월 이후 본딩이고, 4F² 전면 양산 일정은 2028년 전후로만 거론됩니다. 출시 발표와 양산 수율은 별도입니다.",
            "3) 공정 주기가 길어지면 비트 공급 증가도 느려질 수 있습니다. 추격 뉴스는 심리에 부담이지만, 오늘 투자 결론의 중심은 그 공급 둔화와 CAPEX입니다.",
        ],
        kind="key",
    )
    n.h2("말하면 이렇게 바꿉니다")
    n.table(
        ["단정하기 쉬운 말", "녹화 문장"],
        [
            ["G5는 1c 또는 0a다", "G5의 11.95nm는 액티브 하프피치다. 노드 이름이 아니다"],
            ["CXMT가 기술로 2년 앞섰다", "출시 목표만 보면 빠르다. 수율·인증·물량은 별도다"],
            ["VSG가 VG보다 좋다", "방향은 같다. 단면과 우열의 공개 비교는 없다"],
            ["4F²면 원가가 내려간다", "칸은 늘고, 원가는 식각·본딩·수율이 결정한다"],
            ["이 뉴스가 주가를 눌렀다", "당일에는 다른 노이즈가 겹쳤다. 원인 단정은 어렵다"],
            ["HBM이 곧 3D DRAM이다", "HBM은 다이 적층 제품, 3D DRAM은 셀 층의 공정이다"],
            ["삼성이 0a에서 4F²를 양산한다", "0a 본경로는 본딩, VCT는 D0a-V. 양산 목표는 2028년 전후"],
        ],
        col_widths=[6.4, 11.2],
        first_col_bold=True,
    )

    n.h2("근거 — 녹화 중 출처를 물을 때")
    n.table(
        ["주제", "출처"],
        [
            ["CXMT 4F² · 서버 DDR5", "연합뉴스·서울경제·트렌드포스, 2026-10-12. 행사 10/9~10 상하이"],
            ["부분 적용 가능성 · 점유율", "트렌드포스 10/12. 2Q26 매출 점유 CXMT 9.5%"],
            ["G5 11.95nm · SAQP", "CXMT 뉴스룸, 2026-09-20 허페이. 총 다이 +50%는 회사 주장"],
            ["삼성 10a 워킹다이", "디일렉, 2026-04-24. ISSCC 2026 VCT·본딩은 디일렉 후속"],
            ["D0a를 본딩으로, VCT는 D0a-V", "ZDNet Korea, 2026-09-23"],
            ["SK VG + PUC", "SK하이닉스 VLSI 2025. 2026년 BLS·백 게이트 논문"],
            ["하이닉스 80.1조 · TP 320만", "메리츠 김선우, 한국경제·매일경제 2026-10-12"],
            ["골텐스 2.475억 달러", "연합뉴스 2026-10-08, 다올 2026-10-12. 거점은 회사 보도자료"],
            ["바르질라 · 콩스베르그", "Wärtsilä 2025 연차. Kongsberg Maritime 2025 4분기 보고서"],
            ["GPT-6.1 Sol 50만 토큰", "Thibault Sottiaux, 2026-10-11. Codex·ChatGPT Work"],
        ],
        col_widths=[5.6, 12.0],
    )
    n.p("시세 코멘트(CXMT 공모가 대비 배수, 8월 17일 고점 대비 하락, 코스피 6400)와 벙커링 비중·애프터마켓 마진, 2027년 PER 23배는 당일 퀵코멘트 기준입니다. 리포트 목표주가는 그 증권사의 추정입니다.", size=10, color=GRAY)

    n.spacer(8)
    n.p("— 10월 12일 DRAM 셀 구조 강의노트. 퀵코멘트(06:45~19:45)를 녹화 순서로 재구성하고, 공개 보도로 숫자·용어를 대조.", size=9.5, color=GRAY, align="right")

    n.save(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
