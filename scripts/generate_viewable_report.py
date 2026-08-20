#!/usr/bin/env python3
"""워드 없이 바로 열리는 보고서: 단독 HTML + PDF + 마크다운."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from charts_integrated import render_all

CHART_DIR = Path("/workspace/reports/charts_integrated")
FONT_NAME = "HYGothic-Medium"
HTML_OUT = Path("/workspace/reports/VIEW_THIS_REPORT.html")
PDF_OUT = Path("/workspace/reports/VIEW_THIS_REPORT.pdf")
MD_OUT = Path("/workspace/reports/VIEW_THIS_REPORT.md")
NAVY = colors.HexColor("#0F2043")
NAVY2 = colors.HexColor("#1E407C")
GOLD = colors.HexColor("#B8943A")
LIGHT = colors.HexColor("#EEF2F8")
GREEN = colors.HexColor("#166534")
RED = colors.HexColor("#991B1B")

# 보고서에 넣을 차트 순서
PAGES = [
    (
        "0. 한 장으로",
        "사흘의 공통분모는 AI 수요 파괴가 아닙니다. 할인율(금리·환율)이 가격을 깎고, 순환금융·효율화가 내러티브를 흔들고, 환원·파운드리·클라우드 CAPEX가 반대편에서 받칩니다.",
        [],
        [
            "8/18: 이란 장기전(1년 원유·12일 작전) + JGB 10년 2.945% + 실리콘투 CVC 3,000억",
            "8/19: 유가발 금리 쇼크. 하이닉스 40조 소각 + FCF 50%+. 삼성 파운드리 +10~15%. 마벨–구글",
            "8/20: 바이백으로 10년 4.64%·30년 5.18%. 지수는 +인데 SOX −2.12%(OpenAI). 알리바바 Cloud +40%",
        ],
    ),
    (
        "1. 코스피 — 지수는 오고 거래는 안 옴",
        "8월 일평균 거래대금 25.7조(5~6월 50조의 반토막). 외국인 5/7~8/10 −116.7조 뒤 5일 +9.5조. 추가 상승의 열쇠는 외국인 지속.",
        ["kospi_turnover", "foreign"],
        [],
    ),
    (
        "2. 엔캐리 — 조건 형성이지 이미 2024.8이 아님",
        "JGB 2년 1.70% / 5년 2.18% / 10년 2.955%. 위험은 금리 자체가 아니라 엔화 급등+레버리지 청산. 현재 USD/JPY 159.43(157~159 반등)이면 1차 충격은 글로벌 금리/밸류. 의심선은 159→155→150 + 닛케이·코스피 동반 붕괴.",
        ["jgb", "crash_2024", "carry_compare"],
        [
            "위험 5개 동시: JGB10>3% + 엔 급등 + 미 30년>5.3~5.4% + SOX 급락 + 일본 입찰 부진",
            "노무라: 26.9/27.1/27.4 각 25bp, 최종 1.75%. NISA 개인국채 3.8조엔",
        ],
    ),
    (
        "3. 8/19 세션 — 금리 하락 ≠ 반도체 매수",
        "재무부 바이백 $20억→$40억. 30년 5.33→5.18, 10년 4.71→4.64, 달러 −0.8%. S&P +0.21%인데 SOX −2.12%. OpenAI Q2 매출 $6.7B(+18%), 손실 $9.3B→$12.3B. 바이백은 방어선이지 재정·인플레·AI 회사채 해결이 아닙니다.",
        ["sess819", "macro_levels"],
        ["브렌트 $90 안정 / $100 악순환. 10년 4.7% 안착 vs 5.0% 고착.", "2024.9 연준 50bp 인하를 지금 대입하지 말 것. 동결이 주식에 최선."],
    ),
    (
        "4. 환율 — 국내 수급이 먼저, 이익은 60조 바구니",
        "법인세·설비 원화수요 → 수출 달러매도 → 헤지 상승 → 달러-원 하락. 1,520→1,420 가정 시 하이닉스 EPS 약 −5.9%(β 0.9), 삼성 −2.6%(β 0.4). 27년 순익 300~400조이면 18~24조. 2H26 환율 16.3조. 키옥시아 지분평가+가격/이익+환율 = 60조 중후반.",
        ["fx_ladder", "fx_sensitivity", "skh_hit60"],
        ["1,300원대 중반은 조건부. DXY −3~4%면 1,360, 공급 가세 시 1,340. 1,350 달러수요·외국인 매도·유가가 리스크."],
    ),
    (
        "5. 메모리 밸류 — 본주 vs ADR vs HDD",
        "본주 26/27 PER 4.3/3.4배. ADR 프리미엄 52%는 과함(정상 +20%면 본주 약 190만). 메모리 6~8배 vs 웨스턴디지털·씨게이트 26배. 같은 스토리지가 아닙니다.",
        ["per_hdd", "adr_premium", "per_map"],
        ["26년 성장 0 + PER 6~7배: 하이닉스 208~242만, 삼성 28.7~33.5만."],
    ),
    (
        "6. HBM NOBUY와 SCA",
        "타당성 낮음: 비싸서 수요가 곧 꺾인다. 타당성 높음: 비쌀수록 효율화 유인. SRAM ≠ 대체, 분업. 26~28 초과이익, 28년 이후 양날. SCA 50%·시장가 −20%·Floor 90% → GP/bit −16.6%. Bit +20%면 총GP 유지.",
        ["hbm_net", "sca_asp", "gp_bit"],
        [],
    ),
    (
        "7. 하이닉스 환원 — 40조는 시작",
        "보수 FCF 2025A 25 + 2026E 150 + 2027E 210 = 385조. 50% = 192.5조(3년 프로그램 누적 하한, 2027 일시 지급 아님). 이미 40조 → 추가 152.5조+. 2028년 205조·102.5조는 정책이 아니라 모델 참고치. 3Q26에 구체화.",
        ["fcf_years", "skh_return", "sndk_bb"],
        ["샌디스크 $140억은 8/5~7 −15.1%와 겹침. 본반등은 8/13 Investor Day. 키옥시아 8,000억엔 누적 +7.4%."],
    ),
    (
        "8. 비메모리 · NVIDIA · OpenAI",
        "삼성 파운드리 SF4 중·미 10~15%. 마벨 워런트 최대 5,897만주, 행사가 $206.58, $5억마다 vest. NVIDIA Q2 컨센 $92B(+96%), 저자 $93.5B. Beat보다 CAPEX 지속·Rubin·순환금융 설명이 핵심.",
        ["mrvl_avgo", "nvda_q2", "nvda_openai"],
        ["Rubin 3Q26, 추론 35배, 랙 $7~8.5M. Top5 2027 CAPEX ≥ $1T(+33%)."],
    ),
    (
        "9. 알리바바 · 울프스피드 — 수요는 있고 이익은 늦게",
        "알리바바 FY1Q27 매출 2,477억위안 +2%, Cloud 432억 +40%, 직전 조정 EBITA −84%. PEG 0.5, 고점 −33%. 울프스피드 매출 $149.6M 부합, EPS −$2.26 vs −$1.47, GM −20%, AI DC +20% QoQ. OpenAI 손실 확대와 같은 그림.",
        ["baba", "baba_mult", "wolf"],
        [],
    ),
    (
        "10. 유니트리 · 실리콘투",
        "유니트리 종가 ¥845(IPO 대비 +460%), 시총 3,418억위안, PSR 155배(60배 프레임의 2.6배), PER ~850배. 다음 관문은 공장 ROI. 실리콘투 CVC 3,000억, 발행가 45,000원(+5.64%), 희석 9.23%. 핵심은 CVC→Douglas. 글랜우드 오버행은 잔존.",
        ["unitree", "silicon2"],
        [],
    ),
]


def img_tag(name: str) -> str:
    p = CHART_DIR / f"{name}.png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f'<img src="data:image/png;base64,{b64}" alt="{name}"/>'


def build_html() -> Path:
    cards = []
    for title, lead, charts, bullets in PAGES:
        figs = "".join(f'<figure>{img_tag(c)}</figure>' for c in charts if (CHART_DIR / f"{c}.png").exists())
        lis = "".join(f"<li>{b}</li>" for b in bullets)
        ul = f"<ul>{lis}</ul>" if lis else ""
        cards.append(f"<section><h2>{title}</h2><p class='lead'>{lead}</p>{ul}{figs}</section>")
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>8/18-20 통합 시장 보고서 (바로보기)</title>
<style>
body {{ margin:0; background:#F3F5F9; color:#1A1A1A; font-family:-apple-system,BlinkMacSystemFont,'Noto Sans KR','Malgun Gothic',sans-serif; line-height:1.65; }}
.wrap {{ max-width:920px; margin:0 auto; padding:24px 16px 64px; }}
header {{ background:#0F2043; color:#fff; border-radius:16px; padding:28px 24px; margin-bottom:20px; }}
header .k {{ color:#B8943A; font-weight:700; font-size:12px; }}
header h1 {{ margin:8px 0; font-size:24px; }}
header p {{ color:#C5D0E0; margin:0; }}
.warn {{ background:#FFF8E7; border-left:4px solid #B8943A; padding:10px 12px; border-radius:0 10px 10px 0; margin:12px 0 20px; }}
section {{ background:#fff; border:1px solid #D5DCE6; border-radius:14px; padding:18px 18px 8px; margin-bottom:16px; }}
h2 {{ color:#0F2043; border-bottom:3px solid #0F2043; padding-bottom:6px; margin:0 0 10px; font-size:18px; }}
.lead {{ color:#4B5563; }}
figure {{ margin:0 0 14px; }}
img {{ width:100%; height:auto; border:1px solid #E5EAF1; border-radius:8px; background:#fff; }}
ul {{ margin:0 0 12px 18px; }}
footer {{ color:#6B7280; font-size:12px; }}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="k">2026.08.18–20 · 워드 없이 바로 보는 통합 보고서</div>
  <h1>금리와 환율이 할인한 3일,<br/>환원·파운드리·클라우드가 버틴 3일</h1>
  <p>업로드 워드 11개를 차트로 재구성했습니다. 이 파일은 인터넷 없이 브라우저에서 열립니다.</p>
</header>
<div class="warn">워드(.docx)가 안 열릴 때 이 HTML 또는 같은 폴더의 VIEW_THIS_REPORT.pdf / VIEW_THIS_REPORT.md 를 여세요. 매수·매도 추천이 아닙니다.</div>
{''.join(cards)}
<footer>생성: scripts/generate_viewable_report.py · 차트 PNG를 파일 안에 내장했습니다.</footer>
</div>
</body>
</html>
"""
    HTML_OUT.write_text(html, encoding="utf-8")
    return HTML_OUT


def build_md() -> Path:
    lines = [
        "# 8/18–20 통합 시장 시각화 보고서",
        "",
        "> **이 파일이 바로보기용입니다.** Cursor·GitHub에서 이미지가 보입니다. 워드가 안 열리면 이 파일 또는 `VIEW_THIS_REPORT.html` / `VIEW_THIS_REPORT.pdf`를 쓰세요.",
        "",
        "사흘의 공통분모는 AI 수요 파괴가 아닙니다. **할인율(금리·환율)**이 가격을 깎고, **순환금융·효율화**가 내러티브를 흔들고, **환원·파운드리·클라우드 CAPEX**가 반대편에서 받칩니다.",
        "",
        "- 매수·매도 추천이 아닙니다. 숫자는 업로드 워드 기준입니다.",
        "",
    ]
    for title, lead, charts, bullets in PAGES:
        lines += [f"## {title}", "", lead, ""]
        for b in bullets:
            lines.append(f"- {b}")
        if bullets:
            lines.append("")
        for c in charts:
            rel = f"charts_integrated/{c}.png"
            if (CHART_DIR / f"{c}.png").exists():
                lines += [f"![{c}]({rel})", ""]
    MD_OUT.write_text("\n".join(lines), encoding="utf-8")
    return MD_OUT


def build_pdf() -> Path:
    pdfmetrics.registerFont(UnicodeCIDFont(FONT_NAME))
    styles = {
        "cover": ParagraphStyle("cover", fontName=FONT_NAME, fontSize=20, leading=28, textColor=colors.white, alignment=TA_LEFT),
        "kicker": ParagraphStyle("kicker", fontName=FONT_NAME, fontSize=9, leading=12, textColor=colors.HexColor("#F3D58A")),
        "sub": ParagraphStyle("sub", fontName=FONT_NAME, fontSize=10, leading=14, textColor=colors.HexColor("#D6DEEA")),
        "h1": ParagraphStyle("h1", fontName=FONT_NAME, fontSize=14, leading=20, textColor=NAVY, spaceBefore=6, spaceAfter=8),
        "body": ParagraphStyle("body", fontName=FONT_NAME, fontSize=9.5, leading=14, textColor=colors.HexColor("#1F2937"), alignment=TA_JUSTIFY, spaceAfter=6),
        "bullet": ParagraphStyle("bullet", fontName=FONT_NAME, fontSize=9.5, leading=13, textColor=colors.HexColor("#374151"), leftIndent=8),
        "foot": ParagraphStyle("foot", fontName=FONT_NAME, fontSize=8, leading=11, textColor=colors.HexColor("#6B7280"), alignment=TA_CENTER),
        "warn": ParagraphStyle("warn", fontName=FONT_NAME, fontSize=9, leading=13, textColor=colors.HexColor("#7A5C12")),
    }

    def header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(NAVY)
        canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont(FONT_NAME, 8)
        canvas.drawString(16 * mm, A4[1] - 8 * mm, "8/18-20 통합 시각화 보고서  ·  VIEW_THIS_REPORT.pdf")
        canvas.setFillColor(colors.HexColor("#E5E7EB"))
        canvas.rect(0, 0, A4[0], 10 * mm, fill=1, stroke=0)
        canvas.setFillColor(colors.HexColor("#6B7280"))
        canvas.setFont(FONT_NAME, 8)
        canvas.drawCentredString(A4[0] / 2, 4 * mm, f"공개 자료 기준 · 추천 아님  ·  {doc.page}")
        canvas.restoreState()

    story = []
    # cover band
    cover = Table(
        [[
            Paragraph("2026.08.18–20  ·  워드 없이 바로 보기", styles["kicker"]),
        ], [
            Paragraph("금리와 환율이 할인한 3일,<br/>환원·파운드리·클라우드가 버틴 3일", styles["cover"]),
        ], [
            Paragraph("이란·엔캐리·유가 금리·원화 강세·하이닉스 환원·HBM·마벨·파운드리·NVIDIA·OpenAI·알리바바·울프스피드·유니트리·실리콘투", styles["sub"]),
        ]],
        colWidths=[178 * mm],
    )
    cover.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), NAVY),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ("TOPPADDING", (0, 0), (-1, 0), 14),
            ("BOTTOMPADDING", (0, -1), (-1, -1), 14),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
        ])
    )
    story.append(cover)
    story.append(Spacer(1, 8 * mm))
    warn = Table([[Paragraph("워드(.docx)가 열리지 않으면 이 PDF 또는 VIEW_THIS_REPORT.html / VIEW_THIS_REPORT.md 를 사용하세요.", styles["warn"])]], colWidths=[178 * mm])
    warn.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FFF8E7")),
        ("BOX", (0, 0), (-1, -1), 0, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBEFORE", (0, 0), (0, -1), 4, GOLD),
    ]))
    story.append(warn)
    story.append(Spacer(1, 4 * mm))

    for title, lead, charts, bullets in PAGES:
        block = [Paragraph(title, styles["h1"]), Paragraph(lead, styles["body"])]
        for b in bullets:
            block.append(Paragraph("• " + b, styles["bullet"]))
        for c in charts:
            p = CHART_DIR / f"{c}.png"
            if p.exists():
                im = Image(str(p), width=170 * mm, height=82 * mm, kind="proportional")
                im.hAlign = "CENTER"
                block.append(Spacer(1, 2 * mm))
                block.append(im)
        story.append(KeepTogether(block))
        story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("위 자료는 업로드 워드 11개를 차트로 재구성한 참고용입니다. 매수·매도 추천이 아닙니다.", styles["foot"]))

    doc = SimpleDocTemplate(
        str(PDF_OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=14 * mm,
        title="8/18-20 통합 시장 시각화 보고서",
        author="준혁",
    )
    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    return PDF_OUT


def main():
    render_all(CHART_DIR)
    html = build_html()
    md = build_md()
    pdf = build_pdf()
    print(f"HTML {html} ({html.stat().st_size} bytes)")
    print(f"MD   {md} ({md.stat().st_size} bytes)")
    print(f"PDF  {pdf} ({pdf.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
