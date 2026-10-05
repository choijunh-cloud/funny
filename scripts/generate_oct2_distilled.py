#!/usr/bin/env python3
"""검증을 통과한 문장만 모아 증류 노트를 만든다."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import generate_oct2_lecture as lec
import oct2_audit
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Mm, Pt

OUT_PATH = Path("/workspace/lectures/10월 2일 검증과 증류.docx")
KR_FONT = lec.KR_FONT
NAVY = lec.NAVY
NAVY2 = lec.NAVY2
GOLD = lec.GOLD
GRAY = lec.GRAY
DARK = lec.DARK
NAVY_HEX = lec.NAVY_HEX
set_run_font = lec.set_run_font


class Notes(lec.Notes):
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
        r = hp.add_run("10/2 검증과 증류  ·  계산이 남는 의견만")
        set_run_font(r, size=8.5, color=GRAY)

        footer = sec.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = fp.add_run("scripts/oct2_audit.py 결과  ·  원문 입력을 다시 계산  ·  ")
        set_run_font(r, size=8, color=GRAY)
        fld = parse_xml(
            f'<w:fldSimple {nsdecls("w")} w:instr=" PAGE ">'
            f'<w:r><w:rPr><w:sz w:val="16"/><w:color w:val="4B5563"/>'
            f'<w:rFonts w:ascii="{KR_FONT}" w:hAnsi="{KR_FONT}" w:eastAsia="{KR_FONT}"/></w:rPr>'
            f"<w:t></w:t></w:r></w:fldSimple>"
        )
        fp._p.append(fld)

        core = self.doc.core_properties
        core.title = "10월 2일 검증과 증류"
        core.author = "준혁"
        core.subject = "10/2 코멘트 등식 검증과 사용 가능한 투자 의견"


def build():
    audit = oct2_audit.build()
    counts = audit.counts()
    n = Notes()

    n.p("2026. 10. 2. 코멘트  ·  등식 검증 후", size=10.5, color=GRAY, align="center", space_after=4)
    n.p("사용 가능한 의견만", size=13, bold=True, color=GOLD, align="center", space_after=2)
    n.p("10월 2일 검증과 증류", size=22, bold=True, color=NAVY, align="center", space_after=6)
    n.p(
        f"성립 {counts['성립']}   ·   불성립 {counts['불성립']}   ·   판단 {counts['판단']}",
        size=12,
        bold=True,
        color=NAVY2,
        align="center",
        space_after=8,
    )

    n.callout(
        "한 장",
        [
            "하이닉스 184만원은 27년 이익의 4.1배이고, 28년 EPS 28만원을 가정하면 이미 6.6배다. 220~250만원은 그 28만원에 8~9배를 줄 때 나온다. 4~6배면 112~168만원이다.",
            "ADR 195.13달러 × 1,347원 = 26.3만원이다. 263만원과 프리미엄 43%, 본주 202만·219만은 배율 10(ADR 10주 = 본주 1주)일 때만 성립한다. 배율 확인 전에는 확정 목표로 쓰지 않는다.",
            "가격 100→122→90, ASP 하락은 −18~−27%, 매출은 비트 +15~20%와 같이 쓰면 −14~−10%다. 이익은 과거 −70~−80%보다는 완만하고, Base 한복판은 피크 대비 약 −36%다.",
            "성호전자 5~6만원 중반은 30배의 하단이 아니다. 주수를 확인하기 전에는 한 목표가로 말하지 않는다.",
        ],
        kind="key",
    )

    n.h1("증류된 투자 인사이트", num="1.")
    n.p("아래 일곱은 계산이 버틴 문장만 실행으로 바꾼 것이다. 확인이 나오면 유지하고, 폐기 조건이 나오면 그 문장을 내린다.")
    for i, ins in enumerate(audit.insights, 1):
        n.h2(f"{i}) {ins.title}")
        n.p(ins.thesis)
        n.callout("실행", [ins.act], kind="bull")
        n.table(
            ["확인되면 유지", "나오면 폐기"],
            [[ins.confirm, ins.kill]],
            col_widths=[8.8, 8.8],
            first_col_bold=False,
        )

    n.h1("그대로 쓰면 안 되는 문장", num="2.")
    n.p("원문 입력은 그대로 두고, 그 입력으로 다시 풀었을 때 원문 결론과 어긋난 것들이다.")
    fails = [c for c in audit.checks if c.verdict == "불성립"]
    n.table(
        ["항목", "원문", "대신 말할 것"],
        [[c.group, c.author, c.on_air] for c in fails],
        col_widths=[2.6, 5.6, 9.4],
    )
    n.h2("불성립의 계산")
    n.table(
        ["항목", "다시 계산한 값"],
        [[c.group + " · " + c.id, c.computed] for c in fails],
        col_widths=[5.2, 12.4],
    )

    n.h1("계산이 맞은 의견", num="3.")
    n.p("이 문장은 원문과 식이 같다. 방송에 그대로 써도 된다.")
    passed = [c for c in audit.checks if c.verdict == "성립"]
    n.table(
        ["묶음", "쓸 문장"],
        [[c.group, c.on_air] for c in passed],
        col_widths=[3.4, 14.2],
    )

    n.h1("조건이 붙어야 하는 판단", num="4.")
    n.p("식이 아니라 시나리오다. 조건을 붙여서만 말한다.")
    judgments = [c for c in audit.checks if c.verdict == "판단"]
    n.table(
        ["묶음", "입력", "조건 붙여 말할 문장"],
        [[c.group, c.author, c.on_air] for c in judgments],
        col_widths=[2.8, 5.4, 9.4],
    )

    n.h1("지금 포지션에 쓰는 카드", num="5.")
    n.table(
        ["자리", "유지", "숫자"],
        [
            ["지수", "10년물 5%대에서는 베타를 늘리지 않음", "10년 5.28% · SOX +2.4% · 고용 +2.9만"],
            ["하이닉스", "8배 재평가가 열릴 때만 업사이드", "현재 6.6배(EPS 28만) · 8배 224만 · 4배 112만"],
            ["마이크론 비교", "배율과 무관하게 쓰는 상대가치", "본주 27년 4.1배 vs 6.0배, 할인 약 31%"],
            ["ADR", "배율 10일 때만 프리미엄 43%", "배율 1이면 26.3만원. 확인 전 202·219만 확정 금지"],
            ["피크 이후", "매출 −14~−10%, 이익은 피크 대비 약 −36%", "가격 100→122→90 · ASP −18~−27%"],
            ["HDD", "저PER 매수 논리로 받지 않음", "STX 26배 · WDC 23배"],
            ["두산", "규제 헤드라인으로 팔지 않음", "CCL 1,059억 · QoQ +115%"],
            ["성호전자", "주수 확인 전 단일 목표 금지", "희석 후 30배 4.2만 / 희석 전 30배 2.9만"],
            ["포트", "코너에서 합 100. 소부장은 AI 안", "삼전닉스 30 또는 40 + 소부장 20 + 현금 20"],
            ["앤트로픽", "2조는 플랫폼 배수 약 1.8배의 자리", "마진 25%만으로는 약 1.1조 달러"],
        ],
        col_widths=[3.0, 7.6, 7.0],
    )

    n.spacer(6)
    n.p(
        "— scripts/oct2_audit.py. 가격·EPS·환율·비중은 10/2 원문 입력. 새 실적 추정은 넣지 않았다.",
        size=9.5,
        color=GRAY,
        align="right",
    )
    n.save(OUT_PATH)
    print(f"Wrote {OUT_PATH} ({OUT_PATH.stat().st_size} bytes)")
    return audit


if __name__ == "__main__":
    build()
