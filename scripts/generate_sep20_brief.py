#!/usr/bin/env python3
"""9월 20일 일요일 오전 다이제스트 강의노트(.docx)."""

from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Inches, Mm, Pt, RGBColor

from sep20_data import ADDON, HAKGYUN_MEMBERSHIP, MAIN, SAT_PM_MAIN

OUT_PATH = Path("/workspace/lectures/9월 20일 일요일 오전 다이제스트.docx")
CHARTS = Path("/workspace/lectures/assets/sep20")

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
NAVY_HEX, NAVY2_HEX, GOLD_HEX = "0F2043", "1E407C", "B8943A"
LIGHT_HEX, GREEN_HEX, RED_HEX = "EEF2F8", "E8F5E9", "FDECEA"
AMBER_HEX, BLUE_HEX, ROW_HEX = "FFF8E7", "E8F1FB", "F7F9FC"


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
    cell._tc.get_or_add_tcPr().append(
        parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill}"/>')
    )


def set_cell_margins(cell, top=60, bottom=60, left=80, right=80):
    cell._tc.get_or_add_tcPr().append(
        parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'<w:top w:w="{top}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/>'
            f'<w:bottom w:w="{bottom}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/>'
            f"</w:tcMar>"
        )
    )


def set_table_borders(table, color="D0D7E2", sz="4"):
    tbl = table._tbl
    tbl_pr = tbl.tblPr if tbl.tblPr is not None else parse_xml(f'<w:tblPr {nsdecls("w")}/>')
    tbl_pr.append(
        parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f'<w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
            f"</w:tblBorders>"
        )
    )


def prevent_row_split(row):
    row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))


def cell_text(cell, text, size=10, bold=False, color=DARK, align="left"):
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
        set_run_font(run, size=size, bold=bold, color=color)
    set_cell_margins(cell)


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
        header = sec.header
        header.is_linked_to_previous = False
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = hp.add_run("9/20 일요일 오전 다이제스트  ·  MAIN 8 + ADDON 4 + PDF 3  ·  강의노트")
        set_run_font(r, size=8.5, color=GRAY)
        footer = sec.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run("Sunday thin  ·  사이렌 미발화  ·  준혁 프레임 유지  ·  ")
        set_run_font(r, size=8, color=GRAY)
        fp._p.append(
            parse_xml(
                f'<w:fldSimple {nsdecls("w")} w:instr=" PAGE ">'
                f'<w:r><w:rPr><w:sz w:val="16"/><w:color w:val="4B5563"/>'
                f'<w:rFonts w:ascii="{KR_FONT}" w:hAnsi="{KR_FONT}" w:eastAsia="{KR_FONT}"/></w:rPr>'
                f"<w:t></w:t></w:r></w:fldSimple>"
            )
        )
        core = self.doc.core_properties
        core.title = "9월 20일 일요일 오전 다이제스트"
        core.author = "준혁"
        core.subject = "Sunday thin · MAIN 8 · ADDON 4 · 9/17 PDF 3"

    def p(self, text, size=11, bold=False, color=DARK, space_after=6, space_before=0):
        para = self.doc.add_paragraph()
        para.paragraph_format.space_after = Pt(space_after)
        para.paragraph_format.space_before = Pt(space_before)
        para.paragraph_format.line_spacing = 1.18
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
        para._p.get_or_add_pPr().append(
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

    def bullet(self, text, level=0, size=11):
        para = self.doc.add_paragraph()
        para.paragraph_format.left_indent = Cm(0.55 + level * 0.45)
        para.paragraph_format.first_line_indent = Cm(-0.35)
        para.paragraph_format.space_after = Pt(2.5)
        para.paragraph_format.line_spacing = 1.15
        run = para.add_run("• " if level == 0 else "– ")
        set_run_font(run, size=size, color=NAVY2 if level == 0 else GRAY)
        run = para.add_run(text)
        set_run_font(run, size=size, color=DARK)
        return para

    def callout(self, text, fill=AMBER_HEX, color=AMBER):
        table = self.doc.add_table(1, 1)
        table.autofit = True
        cell = table.cell(0, 0)
        shade_cell(cell, fill)
        cell_text(cell, text, size=10, color=color)
        set_table_borders(table, color="E5D7A3", sz="4")
        self.doc.add_paragraph()

    def add_chart(self, name, width=16.2):
        path = CHARTS / name
        if not path.exists():
            return
        self.doc.add_picture(str(path), width=Cm(width))
        last = self.doc.paragraphs[-1]
        last.alignment = WD_ALIGN_PARAGRAPH.CENTER

    def table(self, headers, rows, col_w=None, header_fill=NAVY_HEX):
        table = self.doc.add_table(1 + len(rows), len(headers))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True
        set_table_borders(table)
        for i, h in enumerate(headers):
            cell = table.rows[0].cells[i]
            shade_cell(cell, header_fill)
            cell_text(cell, h, size=9, bold=True, color=WHITE)
        for r_i, row in enumerate(rows):
            prevent_row_split(table.rows[r_i + 1])
            for c_i, val in enumerate(row):
                cell = table.rows[r_i + 1].cells[c_i]
                if r_i % 2:
                    shade_cell(cell, ROW_HEX)
                cell_text(cell, val, size=9)
        if col_w:
            for row in table.rows:
                for i, w in enumerate(col_w):
                    row.cells[i].width = Cm(w)
        self.doc.add_paragraph()
        return table


def build() -> Path:
    n = Notes()
    n.p("2026.09.20 일 오전  ·  Asia/Seoul  ·  조회 yt-dlp ~08:22 KST", size=10, color=GRAY, space_after=2)
    n.p("일요일은 장이 쉬고, 새 미국 overnight도 없다", size=18, bold=True, color=NAVY, space_after=8)
    n.callout(
        "한 줄. 금요 FOMC·BOJ 뒤 테이프는 토요 방송에서 이미 읽혔다. "
        "오늘 MAIN 8편은 소화 논리다. 추가 대담 4편(홍기빈·박정호·신환종·김효진)과 텔레그램은 MAIN이 아니다. "
        "가격·IB 목표·500조·UBS 90%는 게스트/IB estimate — 방 합의로 잠그지 않는다. "
        "사이렌(10Y 5% 안착 · oil 120) 미발화. 준혁 프레임 유지."
    )

    n.h1("시계와 테이프", "01")
    n.add_chart("01_clock.png")
    n.bullet("목 9/17: 업로드 PDF 3편. SOX +3.1, 10Y 5.01→4.94, 실업수당 19.6만. FOMC 전날 안도.")
    n.bullet("금 9/18: 나스닥 +0.40 · S&P +0.17 · 다우 −0.18 · SOX +2.78 · WTI 정산 $100.30. 토 AM/PM이 이미 읽음.")
    n.bullet("토 9/19: MAIN 8편 업로드·촬영. 새 테이프 창작 없음.")
    n.bullet("일 9/20: KR 휴장. 각도기 일요 overnight 없음. 당잠사 없음(다음 9/22).")
    n.add_chart("02_tape.png")
    n.add_chart("03_siren.png")
    n.callout(
        "문홍철·김민수·염블리 모두 터치/근접 ≠ 안착. 금 장중 10Y 5.002 보도는 워킹 밴드 안이다. WTI $100.30 ≪ 120.",
        fill=GREEN_HEX,
        color=GREEN,
    )

    n.h1("패널 비교 — 합의 세탁 금지", "02")
    n.add_chart("11_matrix.png")
    n.add_chart("05_rate_camp.png")
    n.table(
        ["주제", "박병창", "염승환", "김학균·이경민", "문홍철"],
        [
            [
                "금리인상",
                "선반영. 성장↑금리↑면 악재 공식 폐기. 12월 한 차례는 가설.",
                "다음날 소화 규칙. 역행→동행(투자 시대).",
                "기준~4% vs 시장~5.3%. 유가·장기금리가 상단.",
                "물가 3%대면 정당. 터치 vs 종가.",
            ],
            [
                "반도체",
                "이벤트 소화 뒤 홀드·분할. CTS는 시장도 못 믿음.",
                "네비우스 +20 · MLCC +30. 병목=OSAT·전력·기판.",
                "AI 사이클 + 추석 전은 판단 구간.",
                "닉스 200만 도발. 잠금 금지.",
            ],
            [
                "리스크",
                "유가·전쟁+12월 인상이 겹치면 타이밍 밀림.",
                "동행 다음 동반 하락은 프레임이지 법칙 아님.",
                "5% 지속(재정) 회의는 학균 축.",
                "엔 약세 구조. 100bp 시나리오.",
            ],
        ],
    )
    n.add_chart("04_ai_panel.png")
    n.table(
        ["주제", "김광석", "김영익", "정주용"],
        [
            [
                "AI",
                "반도체 국가 재편. 수출 40%/48%(방송). 한은 3.3/2.9.",
                "기술은 혁명, 주식은 거품. 한국 베타 큼.",
                "인프라 미완. 스팟 안 떨어지면 아직 버블 아님.",
            ],
            [
                "10Y",
                "성장 축의 배경.",
                "밸류·금리. 사이렌과 근접·관전만.",
                "공통 관전은 5% 근접뿐.",
            ],
        ],
    )
    n.callout(
        "성상현 부부장은 오늘 MAIN 8에 없다. 과거 11월 대선·잭슨홀 대담을 오늘 3자 토론으로 치환하지 않는다.",
        fill=RED_HEX,
        color=RED,
    )

    n.h1("MAIN 8", "03")
    n.table(
        ["#", "채널", "게스트", "시계", "한 줄", "조회"],
        [
            [
                str(m["id"]),
                m["ch"],
                m["guest"],
                m["when"],
                m["title"],
                f"{m['views']:,}",
            ]
            for m in MAIN
        ],
    )
    n.h2("박병창 · 이주연 · 김민수")
    n.bullet("박: 워시가 비둘기파적 인상까지는 안 보여 줌. 그래도 궤는 선반영. 10월 말은 진짜 인상 창이 아님.")
    n.bullet("CTS 삼성~500조 · 닉스 370~380 · 닉스 200만 · 삼전 29~30만은 게스트 개인. SoftBank/OP370과 같이 잠금 금지.")
    n.bullet("이주연: 촬영 금 19:00. 토 overnight 마감이 아님. 외인~1조 · 기관~1.8조(방송) · 60일선. 블룸 가이던스 39~42억.")
    n.bullet("김민수: 10Y 5.04 터치 관찰. 포트 30% · 26조 · 670%는 개인 운용/estimate.")
    n.add_chart("12_flows.png")
    n.h2("경제전쟁꾼 · 문홍철 · 염블리")
    n.bullet("학균: 과거 기준 5.5% 때 시장~5.1% vs 지금 기준 4%인데 시장 5.3%. 장기금리가 더 부담.")
    n.bullet("이경민: 최종 4.5–4.75 시각이 안 바뀐 점이 안도(estimate). SPX +2% ATH도 estimate.")
    n.bullet("문: 코어 PCE 0.2%p 과거치 수정은 해석. 코스피 6900/7000 · 닉스 200만 잠금 금지.")
    n.bullet("염: 영란 동결 · BOJ 인상. IB 310/400/59가 반복돼도 합의 가격 아님. 비밀노트와 다른 편.")

    n.h1("업로드 PDF 3편 — 목 9/17", "04")
    n.h2("미국증시 9/17")
    n.add_chart("07_sox_thu.png")
    n.bullet("금리 5%가 하루 만에 완화 + 유가 공급차질 우려 완화. 침체형 하락이 아님. 실업수당 19.6만.")
    n.bullet("ARM: 하스 CNBC. $2bn은 수요 가시성. 공식 아웃룩은 약 $1bn대. PDF의 ‘목표 달성 자신’은 한 단계 과장.")
    n.bullet("인텔: Tigress $118→$145 Buy(9/16) · Northland OP $120 · Altera 9/15 비밀 S-1 · $2bn+는 Reuters 소스.")
    n.bullet("AI 자율규제기구 무산 — 최소규제 기조. 주정부·전력 인허가는 남음.")
    n.h2("현지 인텔 분위기")
    n.add_chart("06_intel_chain.png")
    n.bullet("블로거 체인: 하이닉스 DRAM → Ohio → Indiana HBM → 미국산 공급 → Foundry 신뢰.")
    n.bullet("Reuters 9/16 탐색. 하이닉스 “결정된 사항 없음”. 인텔 speculation. 제품 종류 미확인. Ohio 2030–31.")
    n.bullet("‘이미 주가에 반영?’은 미잠금. 단순 임차 vs 고객 선투자형 JV가 분기.")
    n.h2("조선업 0917")
    n.add_chart("08_shipyard.png")
    n.bullet("원문: 상선 P·Q 한계, 이익은 고점 초과. 3축이 실제 수주로 확인되면 멀티플 재평가 가능.")
    n.bullet("HD현대 육상 4GW는 2030 캐파 목표(온산 2028 완공 가정). 이미 4GW가 아님. 코반 1,000MW·9,560억은 별도 사실.")
    n.bullet("한화오션 60MW는 AiP·모델 공개. 삼성중 FDC는 2Q28 목표 + M3 엔지니어링. EPC 아직.")
    n.bullet("함정은 파이프라인. 전투함 수주 확정이 리레이팅의 키.")

    n.h1("추가 대담 4 — MAIN 아님", "05")
    n.add_chart("13_addon.png")
    n.table(
        ["#", "채널", "게스트", "시계", "한 줄"],
        [
            [a["id"], a["ch"], a["guest"], a["when"], a["title"]]
            for a in ADDON
        ],
    )
    n.callout(HAKGYUN_MEMBERSHIP, fill=BLUE_HEX, color=NAVY2)
    n.h2("홍기빈 · 박정호")
    n.bullet("홍: LLM=기호 세계. 다음은 월드모델·암묵지. 동작 데이터는 평생 자산. 한 번 팔고 땡이 아니라 데이터 커먼스.")
    n.bullet("블랑샤르 일반재정 vs 자본계정은 학술 아이디어. 샌더스 ASI 금지는 9/3 발표·미통과. 제도 확정으로 쓰지 말 것.")
    n.bullet("박: 속도조절은 면피. 훈련 중단은 반대. 검수 < 개발. 허깅페이스 침입은 양사 공개, 로그 삭제는 풍문.")
    n.bullet("소버린: 미국이 감속 여론에 흔들려도 한국은 같이 쉬지 말 것(판단).")
    n.h2("신환종 · 김효진")
    n.bullet("신: ASR 케비너시=케빈 워시. 10Y 5% 터치는 관전. 안착 아님. 금=중앙은행 대체 수요(판단).")
    n.bullet("달러 60–70 · 금 20% · 브라질 7.5% · 4분기 신중은 게스트 시나리오. 사이렌 미발화.")
    n.bullet("효진: 아스트라=에이전트. 캡엑스 1조$는 어림. 약한 고리는 자금+장기금리. 준혁 프레임과 같은 축.")
    n.bullet("GPU 유동화는 8/10 MOU·초입. 2008 재현으로 잠그지 말 것. 삼전/닉스 우열·HBM 40%는 잠금 금지.")
    n.add_chart("14_ubs.png")
    n.add_chart("15_physical.png")
    n.h2("텔레그램")
    n.bullet("UBS CapEx 경로·증가분 90% 메모리는 IB 추정. UBS WM 다른 글과 결이 다름. 방 합의 아님.")
    n.bullet("바클레이즈: 휴머노이드 대량은 2035 시나리오. 2030은 점진. 꼭 인간형일 필요 없음.")
    n.bullet("트럼프 AI Force·GDP 25%는 9/19 선언. 조직·예산 없음. 속도조절 소송은 소장 단계.")
    n.bullet("PCB 2027=MLB+SoCAMM+ABF. 브로커 EPS·PER는 목표가≠합의. 유니트리 얼라인먼트는 인용.")

    n.h1("CXL · 토 PM 한 줄 · 증류", "06")
    n.add_chart("09_cxl.png")
    n.bullet("스폰서. HBM 부정 아님 · 보완. 활용 35→70–80% · CapEx 절반은 회사 주장. 1만배는 은유.")
    n.table(
        ["편", "ID", "한 줄"],
        [[a, b, c] for a, b, c in SAT_PM_MAIN],
    )
    n.add_chart("10_calendar.png")
    n.h2("공식")
    n.bullet("일 휴장 · 금 종가 확정분 · 목 SOX +3.1 · 네비우스 +20 · MLCC +30 · 사이렌 미발화 · Ohio 탐색.")
    n.h2("역산")
    n.bullet("인상+다음날 반도체 반등 ≈ 가중치는 장기금리·유가 + AI 전가.")
    n.bullet("장중 5% 빈발 + 종가 5% 위 희소 ≈ touch≠settle. 수출 48% + 거품론 ≈ 양쪽 베타.")
    n.h2("가정")
    n.bullet("선반영이 쇼크를 소음화. 60일선+외인=필요조건. CXL은 보완. SoftBank–Apollo · OP370 · CTS 미잠금.")
    n.h2("추정 — 잠금 금지")
    n.bullet("닉스 200만 · 삼전 29~30만 · IB 310/400/59 · 12월 인상 · 최종 4.5–4.75 · 7,000/7,500 · 월요일 방향.")
    n.callout(
        "쓰지 말 것 = 10Y 5% 안착 · oil 120 · Ohio 계약 확정 · ARM $2bn=가이던스 · HD 4GW 이미 가동 · "
        "FDC EPC 확정 · 토 PM 재등록 · 성상현 대담을 오늘 3자로 치환 · 추가 대담을 MAIN으로 · "
        "UBS 90%=합의 · GDP 25%=공식 · 허깅페이스 로그 삭제=확정 · GPU=2008 · A/B·상자 비유 · 가격 재잠금.",
        fill=RED_HEX,
        color=RED,
    )
    n.p(
        "다음 슬롯: 월요 당잠사·각도기 · SOX/10Y/WTI 재교차 · Apollo 한 줄 · 프리미어 해소. "
        "추석 3거래일 · 미중 회담(목) · 삼전 배당 ~9/28–30 · 마이크론 10/1.",
        size=10,
        color=GRAY,
    )

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    n.doc.save(OUT_PATH)
    return OUT_PATH


def main() -> None:
    path = build()
    print(f"Wrote {path} ({path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
