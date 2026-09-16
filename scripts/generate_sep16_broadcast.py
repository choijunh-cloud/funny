#!/usr/bin/env python3
"""9월 16일 3영상 통합 강의노트(.docx) 생성."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Mm, Pt, RGBColor

OUT_PATH = Path("/workspace/lectures/9월 16일 시장·반도체·금리 (3영상 통합).docx")

KR_FONT = "맑은 고딕"
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
    tc_pr.append(parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill}"/>'))


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


class Notes:
    def __init__(
        self,
        header="9/16  3영상 통합  ·  노근창 · 박병창 · 금리해설  ·  강의노트",
        footer="타임코드는 각 영상 자체 시계  ·  검증은 2026-09-16 공개 보도  ·  ",
        title="9월 16일 시장·반도체·금리 (3영상 통합)",
        subject="노근창 반도체, 박병창 박스권·FOMC, 금리·자금조달·지배구조",
    ):
        self.header_text = header
        self.footer_text = footer
        self.title_text = title
        self.subject_text = subject
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
        r = hp.add_run(self.header_text)
        set_run_font(r, size=8.5, color=GRAY)

        footer = sec.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run(self.footer_text)
        set_run_font(r, size=8, color=GRAY)
        fld = parse_xml(
            f'<w:fldSimple {nsdecls("w")} w:instr=" PAGE ">'
            f'<w:r><w:rPr><w:sz w:val="16"/><w:color w:val="4B5563"/>'
            f'<w:rFonts w:ascii="{KR_FONT}" w:hAnsi="{KR_FONT}" w:eastAsia="{KR_FONT}"/></w:rPr>'
            f"<w:t></w:t></w:r></w:fldSimple>"
        )
        fp._p.append(fld)

        core = self.doc.core_properties
        core.title = self.title_text
        core.author = "준혁"
        core.subject = self.subject_text

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
                shade_cell(cell, ROW_HEX if r_i % 2 else WHITE_HEX)
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

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(path))


def build():
    n = Notes()

    n.p("2026. 9. 16. 통합노트  ·  세 영상 타임코드 동기화  ·  FOMC 발표 전 녹화분", size=10.5, color=GRAY, align="center", space_after=4)
    n.p("시장 · 반도체 · 금리", size=13, bold=True, color=GOLD, align="center", space_after=2)
    n.p("9월 16일  3영상 하나로", size=22, bold=True, color=NAVY, align="center", space_after=2)
    n.p("노근창  ×  박병창  ×  금리·자금조달 해설", size=16, bold=True, color=NAVY2, align="center", space_after=8)
    n.p("속도조절론 · 삼전닉스 · FOMC 워딩 · 유가/송유관 · 엔비디아 금융플랫폼 · 주주환원", size=11, color=GRAY, align="center", space_after=10)

    n.callout(
        "오늘 한 장으로 보면",
        [
            "세 방송의 교집합: 속도조절론은 노이즈, 캡엑스는 안 멈춘다. 다만 금리가 베이스다.",
            "노근창은 보안 기능 → ASP·비트 수요 증가로 읽고, 박병창은 FOMC 워딩과 12월 2차 인상을 걱정한다.",
            "금리 해설은 5%가 끝이 아니라 신용스프레드·자금조달 조건을 같이 보라고 한다. 엔비디아 5,000억 달러 플랫폼이 그 우회 경로.",
        ],
        kind="key",
    )

    n.h2("영상 세 개 — 시계가 각각 0부터 다시 시작한다")
    n.p("원본 대본은 영상이 바뀔 때마다 00:00으로 리셋됩니다. 아래 V1·V2·V3가 그 자체 시계입니다. 다른 영상 구간을 말할 때는 반드시 V번호를 붙입니다.")
    n.table(
        ["코드", "추정 시점", "길이", "출연", "한 줄"],
        [
            ["V1", "9/16 오전\n(09:47 뉴스)", "약 17분", "진행 + 노근창\n세미콘 리서치 랩", "속도조절=노이즈, 보안이 단가, 배당·바벨"],
            ["V2", "9/16 저녁\n(FOMC 몇 시간 전)", "약 39분", "진행 + 박병창\nMP Partners", "박스권 소화, Bessent 면책, FOMC 워딩"],
            ["V3", "같은 주 전후\n별도 회차", "약 28분", "진행 + 해설\n(대본에 성명 없음)", "5%·신용·베센트 시간벌기·지배구조"],
        ],
        col_widths=[2.0, 3.6, 2.4, 4.2, 5.4],
    )

    n.h1("교차 타임코드", num="0.")
    n.p("같은 주제를 세 영상이 나눠 말합니다. 녹화·편집할 때 이 표만 보고 점프하면 됩니다.")
    n.table(
        ["주제", "V1", "V2", "V3"],
        [
            ["유가·송유관·10년물", "00:08–00:43", "03:32–04:43", "19:14–20:19"],
            ["CLARITY / 스테이블코인", "00:43–01:06", "—", "15:08–18:21"],
            ["속도조절론 원인", "01:33–03:20", "08:08–12:21", "20:43–21:18"],
            ["주가 파급·반등 해석", "03:20–05:22", "08:35–09:05\n15:28–15:59", "—"],
            ["보안 → 칩 단가/비트", "03:53–09:56", "—", "21:18–23:13"],
            ["캡엑스 안 멈춘다", "06:02–08:25", "12:23–15:28", "06:45–09:49"],
            ["삼성 배당·50% 룰", "10:41–11:36", "—", "23:52–26:22"],
            ["DC 40→120GW", "11:36–12:31", "—", "—"],
            ["바벨·소부장·비중", "12:56–15:43", "17:30–18:34", "—"],
            ["코스피 박스권", "—", "01:19–07:55", "13:23–14:15"],
            ["FOMC 시나리오", "06:41–06:57", "16:34–35:20", "—"],
            ["Bessent 면책 불가", "—", "09:11–12:21", "02:51–04:29"],
            ["엔비디아 금융플랫폼", "—", "—", "00:06–09:49"],
            ["시진핑·이란·중간선거", "—", "03:50–04:30", "04:29–06:45"],
            ["지배구조·외국인", "—", "—", "23:30–26:22"],
        ],
        col_widths=[4.2, 4.0, 4.6, 4.8],
    )

    n.callout(
        "녹화 순서 제안",
        [
            "오프닝 매크로(V1 00:08) → 속도조절 한 덩어리(V1 01:33 + V2 09:11) → 펀더멘털·배당(V1 10:12)",
            "→ 박스권·삼전닉스(V2 01:19) → FOMC 워딩(V2 21:07) → 금리·플랫폼(V3 06:45) → 주주환원(V3 23:30)",
        ],
        kind="blue",
    )

    # ── 1. Opening macro ──
    n.h1("오프닝 매크로", num="1.")
    n.h2("V1 00:08–01:06  ·  진행 브리핑")
    n.bullet("09:47쯤 미국 에너지부 라이트(Chris Wright) 장관: 사우디 동서 송유관, 며칠 내 정상화 가능.")
    n.bullet("WTI 하락 전환, 104달러대. 브렌트 108달러대.")
    n.bullet("미국 10년물 5% 돌파 후 4.996%로 후퇴.")
    n.bullet("상원 CLARITY 법안 통과 실패. 스테이블코인·코인 관련주 분위기 위축.")

    n.h2("검증")
    n.table(
        ["발언", "판정", "공개 자료"],
        [
            ["송유관 며칠 내 재가동", "부분", "9/15 CNBC: Wright “days, brief and temporary”.\nAP 관리: 3~5주, 부분 가동 가능. 사우디 공식 일정 없음"],
            ["WTI 104 / 브렌트 108", "사실", "9/15 종가 근처. WTI 105.83, 브렌트 108.75에서 되돌림"],
            ["10년물 4.996%", "사실", "장중 고점 5.041% 후 후퇴. Kiplinger 라이브와 일치"],
            ["CLARITY 한 표 차이 부결", "주의", "9/15 클롯처 49–50. 가결선은 60표.\n과반에도 1표 부족, 가결에는 11표 부족. GENIUS(스테이블)는 2025년 이미 법률"],
        ],
        col_widths=[4.4, 2.2, 11.0],
    )
    n.callout(
        "CLARITY ≠ 스테이블코인 법",
        [
            "V1 진행은 부결을 스테이블코인 관련주로 바로 연결합니다. V3는 스테이블이 T-bill 담보로 유동성을 만든다고 설명합니다.",
            "사실 관계: 2025 GENIUS Act가 스테이블 발행 틀. 2026 CLARITY는 시장구조(SEC/CFTC) 법. 스테이블 리워드·윤리 조항 때문에 민주당이 이탈했습니다.",
        ],
        kind="note",
    )

    # ── 2. Pace ──
    n.h1("속도 조절론", num="2.")
    n.callout(
        "세 사람의 공통점",
        ["캡엑스를 멈추는 사건이 아니다. 심리적 노이즈다. 다만 회복은 느릴 수 있다."],
        kind="key",
    )

    n.h2("V1 01:33–03:20  ·  노근창: 왜 나왔나")
    n.bullet("재료 세 겹: 재귀적 자가개선(RSI) 우려 + Jack Clark의 위험 경고 + Dario Amodei의 바이오·해킹·통제 불가 바이러스 시나리오.")
    n.bullet("Anthropic은 10월 말~11월 초 IPO가 걸려 있고, OpenAI Astra가 AGI에 가까운 방향성을 보여 페이스 조절·숨 고르기가 필요.")
    n.bullet("좋은 의도 + 내부 의도(경쟁·상장 일정)가 겹쳤다고 봄.")
    n.callout(
        "ASR 교정",
        [
            "「엔트로픽이 그만둔 제이콥」→ Jack Clark. 공개 보도상 퇴사가 아니라 Anthropic 공동창업자·정책 책임자로 인터뷰 중.",
            "「아모레이/아모데이」→ Dario Amodei. 「아스트라」→ OpenAI Astra. 「제선왕」→ Jensen Huang.",
        ],
        kind="note",
    )

    n.h2("V1 03:20–05:22  ·  전달 경로와 주가 비대칭")
    n.flow(["일요일 스테이블 담보 주식시장에서 반도체 매도", "월요일 한국 반도체", "나스닥·필라델피아 반도체", "7월과 같은 약한 고리"])
    n.bullet("월요일: 반도체 급락. 아마존·MS·구글은 상승.")
    n.bullet("화요일: 글로벌 반도체 반등, 하이퍼스케일러 하락.")
    n.bullet("해석: 보안·검증 기능이 들어가면 칩이 비싸진다 → 반도체는 호재, 클라우드 원가는 부담.")
    n.bullet("그래서 한국 수요일(오늘)은 미국 화요일의 ‘합리적 재배치’를 따라간 것. 속도조절 임팩트는 상당 부분 종료.")

    n.h2("V1 03:53–09:56  ·  보안이 들어가면 단가가 오른다")
    n.bullet("모델 보안·검증 → 연산칩, HBM 로직다이, DRAM ECC에 기능 추가.")
    n.bullet("생산 기간이 길어지고, 없는 기능이 붙으니 ASP(단가)가 오르는 게 맞다.")
    n.bullet("DRM식 보안을 넣으면 데이터 사이즈가 커진다. 자체 측정으로 DRAM 비트 출하 증가율이 두 자릿수 올라간다. 칩 수가 아니라 비트 기준.")
    n.bullet("Amodei 제안 두 가지: 독립 감시기구, 공개 테스트. 소프트웨어만으로 안 되고 서버·칩에 기능이 들어가야 함.")
    n.p("「속도 조절 = 개발 지연 = 캡엑스 둔화」는 투자자 관점에서 없을 일로 봐도 된다고 단언. Anthropic도 상장하면 주주 리턴을 보여줘야 하므로 담론·서사 수준.", size=10.5)

    n.h2("V1 05:22–07:43  ·  정치·경쟁 프레임")
    n.bullet("Amodei: 글로벌 공조, 대중국 칩 제재 강화(증류·복제 차단).")
    n.bullet("Jensen: Clark 발언은 과학적 근거가 약하다. 네오클라우드가 늘고 있고 하이퍼스케일러가 투자를 줄일 생각 없다.")
    n.bullet("트럼프: AI가 답이다, 말도 안 되는 소리 하지 마라.")
    n.bullet("FOMC·유가·국채가 불안할 때 터져서 심리가 커졌다. 인상 자체 임팩트는 이미 애매하게 소화.")

    n.h2("V2 08:08–16:41  ·  박병창: 노이즈의 정의 + Bessent")
    n.bullet("노이즈 = 잠깐 변동성. 추세 변화에는 그 단어를 쓰지 않는다. 이번 건 해프닝 가능성.")
    n.bullet("가장 유력한 배경: 9/15 베센트 하원 증언. AI 랩에 면책(liability exemption)을 줄 수 없다. 문제 발견·해결·책임은 기업.")
    n.bullet("민주당이 선거를 앞두고 부작용을 이슈화 → 정부와 민간이 사전 논의한 흔적 → 랩들이 ‘우리끼리 선언’을 한 것으로 읽음.")
    n.bullet("산업·반도체 펀더멘털과는 별개. 선점·해자가 있어 챗GPT·클로드·그록이 멈출 수 없다.")
    n.bullet("시티: 기술 진전이 멈춰도 사용자 확산만으로 칩·하드웨어 수요는 남는다.")
    n.bullet("루머형 노이즈는 해명 후에도 주가가 잘 안 오른다. 안전장치는 앞으로도 이슈. 지금은 금리 인상이 더 큰 문제.")

    n.h2("V3 20:43–23:13  ·  해설: 성능이 좋아서 걱정하는 처음")
    n.bullet("AI가 성능이 좋아서 제동해야 한다는 분석은 잘 안 된다. 예전엔 성능이 안 돼서가 문제.")
    n.bullet("반도체 가격이 너무 높아 유지가 안 될 것 같다는 걱정도 50년 사이클(수요→증설→공급과잉)과 다른 언어.")
    n.bullet("규제 없이 가면 Astra급이 GPU를 생성형 시절 10만 개에서 100만 개로 끌어올린다는 이야기. 2028 정점론은 아직 모른다. 추가 수요 확인이 먼저.")

    n.h2("검증")
    n.table(
        ["발언", "판정", "메모"],
        [
            ["Amodei 속도조절 + 알트만·머스크·하사비스 동조", "사실", "9/14–15 헤드라인. 코스피 −3.3%와 겹침"],
            ["Jack Clark 퇴사", "주의", "BBC/NPR: 현직 공동창업자. kill switch·집단행동 문제 발언"],
            ["Bessent 면책 불가", "사실", "9/15 하원 금융위. “blank check on liability” 반대. Mythos 이후 재무부 안전 작업"],
            ["Anthropic 10–11월 IPO", "미확인", "노근창 추정. Bessent는 S-1에 책임 공시가 어렵다고만 언급"],
            ["보안 → DRAM 비트 +두 자릿수", "해석", "논리 가능. 공개된 계량 자료 없음. 세대 교체와 구분 필요"],
            ["월요 반도체↓ / 빅테크↑ → 화요 반대", "부분", "방향 설명은 일관. 분봉·종목별 전수 확인은 별도"],
            ["Astra가 GPU 수요 10배", "해석", "시장 내러티브. 100만 개 수치는 미확인"],
        ],
        col_widths=[5.2, 2.2, 10.2],
    )

    # ── 3. Semis ──
    n.h1("반도체 펀더멘털과 포트폴리오", num="3.")
    n.h2("V1 10:12–12:31  ·  노근창: 이견 여지 없다")
    n.bullet("수요·ASP·수익성에 이견이 없다. 블랙록이 연말 전후로 AI 인프라 희소성 때문에 비중을 다시 확대.")
    n.bullet("중간선거 이후 더 갈 수 있고, 한국 기업은 더 빨리 갈 수 있다. 출발점은 9월 말.")
    n.bullet("미국 = 세계 AI DC 수요의 57%. 현재 처리능력 40GW → 2030년 120GW(3배). 짓는 중이라 예약 없으면 못 받는다.")
    n.bullet("기존 LLM은 계속 돈다. 신모델이 연말→내년 3월로 밀려도 수요 임팩트는 미미.")

    n.h3("주주환원  V1 10:41–11:36")
    n.bullet("50% 룰은 지키되, 1·2분기처럼 기존 분기 배당만 하면 안 되고 초과이익을 돌려야 한다.")
    n.bullet("특별배당을 받으려면 9월 말 또는 늦어도 12월 말 주주명부 등재.")
    n.bullet("삼성 연간 주당 1만 4,000원 가능 → 배당수익률 5%대 = 국채 수준. 내년 PER은 낮고, 이익 성장은 2028년까지.")

    n.h2("V1 12:56–15:43  ·  바벨")
    n.bullet("상반기: 대형 반도체 100. 이제는 칩 60 + 괜찮은 섹터 30~40.")
    n.bullet("반도체 내부: 삼전·닉스만이 아니라 소부장 병행.")
    n.bullet("화장품(변동 적고 우상향), 2차전지(ESS 올해 수요의 약 10%, 레벨2+ 확산 → 전기차 내년 단계 회복).")
    n.bullet("중국산 부담은 있으나 미국 제재가 완충. AI·전기·인터넷이 축. 한국 포지션은 반도체 + 전력기기. 향후 5년 비우면 시장을 이기기 어렵다.")

    n.h2("검증")
    n.table(
        ["발언", "판정", "메모"],
        [
            ["미국 DC 40GW → 2030 120GW", "부분", "EPRI 2024년 35–44GW, 2030년 56–132GW.\nBNEF 2030 설치 118GW. BlackRock 2025년 약 42GW. 40→120은 대략 맞음. 57% 점유는 미확인"],
            ["블랙록 반도체 오버웨이트", "부분", "Wei Li, 칩·하드웨어 오버웨이트 발언은 있음. ‘3년 말 재상향’ 시점 표현은 미확인"],
            ["삼성 연 1만 4,000원 배당", "주의", "공식: 2024–26 FCF 50% 환원. 2026년 9–11조 원 규모, 3Q 현금배당 약 30조 원(10월 이사회).\n에듀일리 3Q DPS 추정치 약 5,570원. 1만 4,000원은 잔여 환원까지 현금으로 가정한 개인 추정"],
            ["9월 말 명부 = 특별배당", "부분", "3Q 배당 세부 조건은 10월 이사회. 명부 기준일을 9월 말로 단정하면 안 됨"],
            ["이익 성장 2028까지", "해석", "삼성 공식은 부족이 2028까지 심화 가능. 모건스탠리는 2028 공급 과잉 경고"],
        ],
        col_widths=[5.0, 2.2, 10.4],
    )

    # ── 4. Box ──
    n.h1("박스권과 삼전닉스", num="4.")
    n.h2("V2 01:19–07:55  ·  박병창")
    n.bullet("6/19 고점 → 7월 말 급락 → 저점 후 7,200 근처(8/18) → 한 달 반 횡보. 살살 빠지며 지친다.")
    n.bullet("급등 기울기만큼 옆으로 가는 기간이 필요하다. 에너지 축적 = 물량 소화. 나갈 사람이 나가야 매수세가 들어온다.")
    n.bullet("악재는 이미 많다. 유가 100달러 위. 한두 주 더 힘든 트리거는 트럼프 “중간선거 끝나야 유가 떨어진다” → 10월 말까지 전쟁·고유가 고착 메시지.")
    n.bullet("그래도 낙폭은 견조. 이 정도면 S&P 기준 10% 이상 빠질 재료인데 안 빠진다 = 위를 보고 있다.")
    n.flow(["악재에도 안 빠짐", "위", "호재에도 안 오름", "아래"])
    n.bullet("미국이 버티니 한국이 6,400(소박스 하단)을 안 깨고 위 박스에 있다. 깨졌으면 그 아래로 갔을 가능성.")
    n.bullet("지수는 자연스러운 횡보. 지겨운 것은 종목으로서의 삼전닉스. 삼성전자는 내려와 약한 반등, 하이닉스(KRX)는 반등 없이 옆걸음. 쇼티지·LTA·실적인데 안 가서 답답.")

    n.h2("V2 35:29–39:17  ·  순환매와 단타 기준")
    n.bullet("주도 섹터가 2~3일을 못 간다. 어제 로봇·바이오, 오늘 전력·광통신.")
    n.bullet("본인 고백: 6월 매도 → 7월 분할 매수 후 폭락 → 직전 최강 반도체 매수 → 자산이 고점과 같아짐 → 30~40% 단기 → 순환에 수익이 안 남.")
    n.bullet("결과가 같으면 가만히 있는 편이 나았다. 단타는 코스피가 6,900~7,000 위로 연속성을 줄 때만. 아래 박스에서는 거래하지 말 것.")

    n.h2("V3 13:23–14:15  ·  유동성 에너지")
    n.bullet("9,000까지 갔다 내려올 때도 실적은 안 망가졌다. 시장 에너지의 맥시멈이 그쯤이었던 것.")
    n.bullet("실적이 두 배여도, 1이어도, 에너지가 끝나면 내려온다. 안 오를 때 핑계를 찾는다.")

    # ── 5. FOMC ──
    n.h1("FOMC — 인상 여부보다 워딩", num="5.")
    n.p("두 방송 모두 한국시간 9/17 03:00(미 동부 9/16 14:00) 발표 전 녹화입니다. 결과는 이 노트에 넣지 않습니다.")

    n.h2("V2 16:34–21:07  ·  확률과 가스라이팅")
    n.bullet("오래전부터 9월 동결로 포트폴리오를 짰다가, 워시 잭슨홀식 연설 이후 “할 수도”로 바꿔 30%만 위험관리.")
    n.bullet("삼전닉스 시장 비중 약 47%. 본인이 40% 안이면 건드리지 말 것. 전력·원전·피지컬AI(로봇) 합쳐 60~70%면 나머지 30%는 현금화 가능 상태로.")
    n.bullet("시장 인상 확률 약 95%. 그런데 이제 인상이 좋다는 분석이 2~3주 만에 만들어졌다.")
    n.bullet("논리: 선제·보험적 인상 → 연준 독립성 → 장기 국채금리 하락 → 안정. 10년 4.5%도, 5%도 괜찮다는 뉴노멀.")
    n.bullet("세뇌가 먹혀 충격이 없으면 누군가 잘 매니징한 것. S&P는 최근 7거래일 하루 오르고 계속 빠져 선반영.")

    n.h2("V2 21:07–24:52  ·  세 갈래")
    n.table(
        ["워딩", "시장"],
        [
            ["가이던스·암시 전무", "하락"],
            ["인상/동결 + 인플레를 크게 걱정 (호미 vs 가래, 더 큰 부담)", "하락"],
            ["선제·보험 + 유가가 주범 + AI 생산성으로 디스인플레, 시간의 문제", "환호 가능"],
        ],
        col_widths=[10.0, 7.6],
        first_col_bold=False,
    )
    n.bullet("인상 시 30년·10년, 심지어 2년도 빠질 수 있다. 2년 4.66% vs 기준 3.50–3.75 = 약 100bp 위 = 25bp 네 번. 과하다. 채권도 오버슈팅.")
    n.bullet("막상 인상하면 국채금리가 내려 “인상이 좋은 것”이 되는 수급 시나리오.")

    n.h2("V2 24:52–35:20  ·  그래도 걱정 — 12월 2차")
    n.bullet("워시는 트럼프 사람인데도 인상을 강행하면 인플레가 심각하다는 역설.")
    n.bullet("한 번으로 안 잡힌다. 9월 하면 12월에도. 월가 내년 추가 인상론. 두 차례면 4.00–4.25%.")
    n.bullet("2008: 부동산 버블 + 직전 인상, 당시 5.25%. 리먼 후 S&P 666 → 지금은 8,000 근처. 18년 에브리싱 랠리.")
    n.bullet("에브리싱의 원인 = 화폐가치 하락. 중물가·중금리로 가면 반대가 정상. “성장이 받쳐 주니 괜찮다”는 타당성을 의심.")
    n.bullet("한국도 이미 두 번 올렸다. 올해 반도체 무역흑자로 더 올리면, 인플레가 클수록 경기는 쪼그라든다.")
    n.bullet("단기: 내일 인상이 호재로 프라이싱 + 연말·연초 시즌 + 10월 잠정실적(환율 눈높이 이미 하향) + 자사주 10/13 종료 후 오름 → 그때 챙겨라(비중 축소).")
    n.bullet("차트: 2011 남유럽, 2015 중국은 작은 조정. 2018·2022 큰 조정 = 금리 인상 해.")
    n.rich([("금리가 베이스다. 좋다고 우기지 말 것. ", True), "Fed·BOJ·BOK가 같이 올리면 저금리의 반대 현상을 받아들여야 한다."])

    n.h2("V1 06:41–06:57 과의 차이")
    n.p("노근창은 “FOMC에서 인상해도 임팩트 별로 없을 것”에 가깝습니다. 박병창은 당일 충격은 작을 수 있어도 9+12월 경로와 에브리싱 역전이 본게임이라고 봅니다. 녹화 때 이 간극을 한 문장으로 붙이면 됩니다.")

    n.callout(
        "숫자 체크 (방송 시점)",
        [
            "기준금리 3.50–3.75%, 선물 인상 확률 90%대 → 3.75–4.00%. 2023년 7월 이후 첫 인상.",
            "2년 4.65–4.66%, 10년 고점 5.041% 후 4.996%. QT는 2025-12-01 종료. 인상+QT 동시는 현재 사실이 아님.",
            "S&P 666(2009 저점) → 8,000 근처, 18년은 맞음. 2008 직전 상단 5.25%도 맞음. 인과(인상=버블붕괴)는 해석.",
        ],
        kind="note",
    )

    # ── 6. Funding ──
    n.h1("금리, 자금조달, 베센트", num="6.")
    n.h2("V3 00:06–09:49  ·  조달 금리가 높아도 사업이 되면")
    n.bullet("구글·OpenAI 조달금리가 높다는 것은 불안의 가격. 그래도 추세가 바로 꺾이지는 않는다. 꺾일 때는 신용스프레드를 같이 봐야 한다.")
    n.bullet("진짜 위기는 걱정이 없을 때. 7월 고점도 경고를 친 사람이 역적이었다.")
    n.bullet("카나리아는 사모펀드. 규모는 전체 부채시장을 신용경색으로 몰아넣을 정도는 아니라서 “별거 아니었다”가 반복. 2008 컨트리와이드 역할.")
    n.bullet("아마존: 데이터센터 3년이면 본전, 이후 전부 수익. 네오클라우드(Nebius, CoreWeave)도 회수 빠르다고 주장.")
    n.bullet("엔비디아: GPU·DC를 담보로 금융 플랫폼. 6개 금융사와 제3자 자본 5,000억 달러. 블랙록·골드만 합류.")
    n.bullet("이자 부담은 남지만, 담보면 대출이 수월. 구글이 2%p 더 줘도 수익이 높으면 상관없다. 핵심은 금리 수준이 아니라 그보다 더 버느냐.")
    n.bullet("이번 금리 상승의 주범은 경기가 아니라 유가. DC가 돈 되면 그래도 빌려준다. 차입 조건은 나빠져도 못 빌리진 않을 것.")

    n.h2("V3 02:51–06:45  ·  베센트는 11/4까지 시간")
    n.bullet("10년물에 매우 민감. 4.8% 넘으면 등장한다는 시장 속설. 지금은 이미 등장.")
    n.bullet("할 수 있는 것과 없는 것이 있다. 목표는 끌어내리기보다 더 안 올라가게 덮는 것. 중간선거(11/4)까지.")
    n.bullet("그 안에 정치가 가시적 성과를 내야 한다. 1차 분수령 = 시진핑 방미(다음 주). 이란은 미·이란만으로 안 되고 중국 카드.")
    n.bullet("시진핑이 조건을 키운다: 트럼프는 중국차 미국 생산을 제안, 중국은 대만 무기 판매 속도 조절을 요구.")
    n.bullet("대만 포기가 아니라 덜 팔라는 거래. 트럼프는 국가이익보다 본인 이익을 우선한 전례가 있어 가능성을 배제 못 함.")

    n.h2("V3 09:49–15:08  ·  5%에 적응")
    n.bullet("뉴스 없는 시장은 걱정거리를 만든다. 구글 +2%p가 정확히 왜 문제인지 미시 설명이 약하다.")
    n.bullet("빅테크 부채비율은 낮아 당장은 견딘다. 일반 기업 2%p는 치명. 금리 < 성장이면 괜찮지만 지금은 유가발 금리다.")
    n.bullet("2010년대 제로금리 세대에게 5%는 낯설다. 예전엔 5%가 싼 편. 적응의 문제.")
    n.bullet("유동성은 이제 금리만으로 안 읽힌다. 각국 정부가 빚으로 돈을 뿌린다.")

    n.h2("V3 15:08–18:21  ·  스테이블코인 = 두 번째 유동성")
    n.bullet("역할 1: 국채금리(단기·장기) 상승을 일부 제어. 역할 2: T-bill 담보로 코인을 찍어 시중에 유통.")
    n.bullet("전통: 정부가 팔고 은행이 사서 이자만. 이제 그 담보로 코인이 돈처럼 돔.")
    n.bullet("여야 모두 돈 쓰고 싶다(바이든도, 트럼프도). 통과가 막힌 핵심은 윤리 — 대통령 일가가 그걸로 돈 벌지 말 것.")
    n.bullet("통과되면 금리가 안 내려가도 유동성은 늘어날 수 있다. 동시에 금리는 높은 채 상수가 된다. 국채는 목표 수익률을 낮추고 빨리 나와야 한다.")

    n.h2("V3 18:21–20:43  ·  출구는 아직 아니다")
    n.bullet("5%면 시장 끝? 숫자 자체에 마법이 없다. 끝이라고 말할 때는 신용지표를 같이 봐라.")
    n.bullet("전쟁 예측은 불가능. 베센트는 시간을 벌 수밖에 없다. 금리가 뛰면 물가+선거가 더 나빠진다.")
    n.bullet("불안할 때가 아니라 마음이 편할 때가 문제. AI 성장은 안 끝났다.")

    n.h2("검증")
    n.table(
        ["발언", "판정", "메모"],
        [
            ["엔비디아 5,000억 달러 플랫폼", "사실", "CNBC 8/17: 6개 운용사와 제3자 자본 $500B DC 금융.\n별건: OpenAI 오하이오 잔존가치 보증 최대 $105B"],
            ["아마존 3년 본전", "미확인", "경영진 코멘트로 회자. 전 사이트 공식 가이던스 아님"],
            ["베센트 11/4까지", "해석", "중간선거 일정은 사실. ‘덮기’ 목표는 해설 프레임"],
            ["시진핑 방미·대만 무기 카드", "부분", "Bessent: 다음 주 이란·중국 금융 논의 계속. 자동차·대만 거래 세부은 미확인"],
            ["4.8%면 베센트 등장", "해석", "이미 5%대에서 바이백·개입. 임계치 속설"],
            ["CLARITY 통과 시 T-bill 유동성", "부분", "GENIUS는 이미 법. CLARITY 부결(49–50). 유동성 경로는 시행·규모에 달림"],
        ],
        col_widths=[5.2, 2.2, 10.2],
    )

    # ── 7. Governance ──
    n.h1("한국 증시 사이즈와 지배구조", num="7.")
    n.h2("V3 23:30–27:43")
    n.bullet("삼성·하이닉스는 한국 시장이 담기에 너무 커졌다. 밸류와 주가의 부조리가 반복된다.")
    n.bullet("떠받치려면 외국인에게 매력적이어야 하고, 그러려면 거버넌스·주주환원이 글로벌 스탠더드여야 한다.")
    n.bullet("글로벌은 잉여현금 100% 환원 자세. 한국은 아직 50%. 사정이 있어도 할인이 남는다.")
    n.bullet("100%의 뜻은 ‘현금 재고를 쌓지 않겠다’는 자세지, 내년 캡엑스를 올해 다 쓰고 주주에게 다시 받겠다는 뜻이 아님.")
    n.bullet("마이크론·샌디스크: 설비투자는 하되 남으면 전부 주주. 삼전닉스 50% 잔여는 캡엑스·불확실성 버퍼.")
    n.bullet("환원 역사가 짧고, 조직은 회장 중심. 눈높이는 이미 글로벌.")
    n.p("클로징: 금리에 너무 쫄지 마라. 출구는 아직 아니다. 다만 5%를 단독 종말 신호로 쓰지 마라.")

    # ── 8. Playbook ──
    n.h1("한 장 플레이북", num="8.")
    n.table(
        ["국면", "세 방송이 겹치는 행동", "갈리는 지점"],
        [
            ["속도조절 헤드라인", "노이즈로 처리. 캡엑스 종료로 읽지 말 것", "노근창: 반도체 호재(ASP).\n박병창: 회복은 느림"],
            ["FOMC 당일", "인상 여부 < 인플레 워딩", "노근창: 임팩트 소진.\n박병창: 12월 2차가 본게임"],
            ["10년 5% 전후", "레벨보다 속도·신용스프레드", "해설: 베센트가 11/4까지 덮기"],
            ["삼전닉스", "비중을 비우지 말 것", "노근창 60%+소부장.\n박병창 40% 유지+30% 현금 버퍼"],
            ["단타", "7,000 위 + 2~3일 연속성", "아래 박스는 가만히"],
            ["10월", "잠정실적·자사주 종료를 촉매로 봄", "박병창: 그때 잘 챙긴다(축소)"],
        ],
        col_widths=[3.6, 7.0, 7.0],
    )

    n.h2("이전 핵심정리와의 연결")
    n.bullet("유지: 금리 속도 > 레벨, GPU·전력 병목, 순환 금융, 부동산·변동금리가 주식보다 현금흐름에 취약.")
    n.bullet("강화: 속도조절은 세 방송 모두 노이즈. Bessent 면책이 정치 배경으로 확인.")
    n.bullet("수정: 연준 QT 현재형 금지. CLARITY를 스테이블 법으로 부르지 말 것. 삼성 1만 4,000원은 추정. 원/달러 1,300원대 고정 아님.")
    n.bullet("쟁점 유지: 삼성 “2028 부족” vs 모건스탠리 “2028 과잉”.")

    # ── 9. Glossary ──
    n.h1("고유명사·ASR 교정", num="9.")
    n.table(
        ["대본", "교정"],
        [
            ["라이트 장관 / 사우드 송유관", "Chris Wright · 사우디 East-West Pipeline (Petroline)"],
            ["클레리티 / 스테이블 코일", "CLARITY Act (시장구조) · stablecoin · 2025 GENIUS Act"],
            ["엔트로픽 / 아모데이 / 제이콥", "Anthropic · Dario Amodei · Jack Clark"],
            ["아스트라 / 제선왕 / 전왕", "OpenAI Astra · Jensen Huang"],
            ["디행 / 에러 커션 / FMC", "DRAM · ECC · FOMC"],
            ["하이퍼스켈러 / 네비오스 / 코유", "hyperscaler · Nebius · CoreWeave"],
            ["케빈오시·케빈노시 / 백선", "Kevin Warsh · Scott Bessent"],
            ["MBDI 5,000억 / 시즌핑", "NVIDIA $500B financing platform · 시진핑"],
            ["재생적 자가 계산", "recursive self-improvement (RSI)"],
            ["피지컬 AI / 소부장 / LTA", "로봇·실물 AI · 소재부품장비 · long-term agreement"],
        ],
        col_widths=[7.2, 10.4],
    )

    n.callout(
        "쓰지 말 것",
        [
            "투자 권유가 아닙니다. 1만 4,000원 배당, 9월 말 명부, 100만 GPU, Anthropic IPO 일정은 방송 추정입니다.",
            "FOMC 결과는 녹화 뒤에 나옵니다. 이 노트는 발표 전 논리만 고정합니다.",
        ],
        kind="bear",
    )

    n.save(OUT_PATH)
    print(f"saved {OUT_PATH}")


if __name__ == "__main__":
    build()
