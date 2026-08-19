#!/usr/bin/env python3
"""8/19 시각화 브리핑 PDF. HTML 보고서와 같은 숫자를 쓴다."""

from __future__ import annotations

import io
from datetime import date
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from scripts import aug19_visual_data as d

OUT = Path("/workspace/reports/2026-08-19-visual-brief.pdf")
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
FONT = "WQYMicroHei"

NAVY = colors.HexColor("#0F2043")
NAVY2 = colors.HexColor("#1E407C")
GOLD = colors.HexColor("#B8943A")
GRAY = colors.HexColor("#4B5563")
INK = colors.HexColor("#1F2937")
RED = colors.HexColor("#DC2626")
GREEN = colors.HexColor("#16A34A")
LIGHT = colors.HexColor("#EEF2F8")

C_BLUE = "#1E407C"
C_CYAN = "#0891B2"
C_GREEN = "#16A34A"
C_RED = "#DC2626"
C_AMBER = "#D97706"
C_GRAY = "#64748B"


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont(FONT, FONT_PATH))
    fm.fontManager.addfont(FONT_PATH)
    plt.rcParams["font.family"] = fm.FontProperties(fname=FONT_PATH).get_name()
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["axes.edgecolor"] = "#D0D7E2"
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.color"] = "#EEF2F8"
    plt.rcParams["grid.linewidth"] = 0.8


def styles() -> dict[str, ParagraphStyle]:
    return {
        "h1": ParagraphStyle("h1", fontName=FONT, fontSize=16, leading=22, textColor=NAVY, spaceBefore=10, spaceAfter=8),
        "h2": ParagraphStyle("h2", fontName=FONT, fontSize=12, leading=16, textColor=NAVY2, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontName=FONT, fontSize=9.5, leading=14, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=6),
        "bullet": ParagraphStyle("bullet", fontName=FONT, fontSize=9.5, leading=13.5, textColor=INK, leftIndent=12, spaceAfter=2),
        "cap": ParagraphStyle("cap", fontName=FONT, fontSize=8, leading=11, textColor=GRAY, alignment=TA_CENTER, spaceAfter=8),
        "kpi_v": ParagraphStyle("kpi_v", fontName=FONT, fontSize=14, leading=17, textColor=NAVY, alignment=TA_CENTER),
        "kpi_l": ParagraphStyle("kpi_l", fontName=FONT, fontSize=7.5, leading=10, textColor=GRAY, alignment=TA_CENTER),
        "cover_k": ParagraphStyle("cover_k", fontName=FONT, fontSize=10, leading=14, textColor=colors.HexColor("#CBD5E1")),
        "cover_t": ParagraphStyle("cover_t", fontName=FONT, fontSize=24, leading=32, textColor=colors.white),
        "foot": ParagraphStyle("foot", fontName=FONT, fontSize=8, textColor=GRAY, alignment=TA_CENTER),
        "th": ParagraphStyle("th", fontName=FONT, fontSize=8, leading=11, textColor=colors.white, alignment=TA_CENTER),
        "td": ParagraphStyle("td", fontName=FONT, fontSize=8, leading=11, textColor=INK, alignment=TA_CENTER),
        "tdl": ParagraphStyle("tdl", fontName=FONT, fontSize=8, leading=11, textColor=INK, alignment=TA_LEFT),
    }


def fig_img(fig, width=16 * cm, ratio=0.48) -> Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=170, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img = Image(buf, width=width, height=width * ratio)
    img.hAlign = "CENTER"
    return img


def kpi_table(s: dict) -> Table:
    items = [
        ("원/달러 가정", "1,420", "1,520 대비 −6.6%"),
        ("SKH EPS 타격", "−5.9%", "27년 순익 18~24조"),
        ("자사주 소각", "40조", "시총 3.3% · EPS +3.4%"),
        ("최소 환원", "192.5조", "잔여 152.5조+"),
        ("SKH 27 PER", "3.4배", "본주 150만 · 보수 5.1"),
    ]
    cells = []
    for lbl, val, sub in items:
        inner = Table(
            [[Paragraph(val, s["kpi_v"])], [Paragraph(lbl, s["kpi_l"])], [Paragraph(sub, s["kpi_l"])]],
            colWidths=[3.2 * cm],
        )
        inner.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("BOX", (0, 0), (-1, -1), 0.4, colors.HexColor("#D0D7E2")),
        ]))
        cells.append(inner)
    t = Table([cells], colWidths=[3.4 * cm] * 5)
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2)]))
    return t


def simple_table(s: dict, headers: list[str], rows: list[list[str]], widths: list[float]) -> Table:
    head = [Paragraph(h, s["th"]) for h in headers]
    body = [[Paragraph(c, s["tdl"] if i == 0 else s["td"]) for i, c in enumerate(row)] for row in rows]
    t = Table([head, *body], colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#D5DCE6")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    t.setStyle(TableStyle(style))
    return t


def chart_yields():
    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    labels = ["10Y 고점", "10Y 마감", "10Y 바이백", "30Y 고점", "30Y 마감", "30Y 바이백"]
    vals = [4.75, 4.705, 4.64, 5.34, 5.285, 5.19]
    cols = [C_RED, C_AMBER, C_GREEN, C_RED, C_AMBER, C_GREEN]
    ax.bar(labels, vals, color=cols, width=0.62)
    ax.axhline(4.7, color=C_GREEN, ls="--", lw=1, label="10Y 안정 4.7%")
    ax.axhline(5.0, color=C_RED, ls="--", lw=1, label="10Y 스트레스 5.0%")
    ax.set_ylim(4.4, 5.55)
    ax.set_ylabel("%")
    ax.legend(fontsize=8)
    ax.set_title("미국 국채 — 장중 고점 vs 진정", loc="left", fontsize=11, color=C_BLUE)
    fig.tight_layout()
    return fig


def chart_fx():
    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    xs = ["고점", "현재", "DXY−3~4%", "국내공급", "수요존"]
    ys = [d.USD_KRW_HIGH, d.USD_KRW_NOW, d.USD_KRW_DXY_DOWNSIDE, d.USD_KRW_KR_SUPPLY_DOWNSIDE, d.USD_KRW_DEMAND_ZONE]
    ax.plot(xs, ys, color=C_CYAN, marker="o", lw=2.2)
    ax.fill_between(range(len(ys)), ys, 1280, color=C_CYAN, alpha=0.12)
    ax.set_ylim(1280, 1560)
    ax.set_title("원/달러 시나리오 (원문 가정)", loc="left", fontsize=11, color=C_BLUE)
    fig.tight_layout()
    return fig


def chart_beta():
    fig, ax = plt.subplots(figsize=(8.2, 2.6))
    ax.barh(["삼성전자", "SK하이닉스"], [d.SEC_FX_BETA, d.SKH_FX_BETA], color=[C_BLUE, "#7C3AED"], height=0.45)
    ax.set_xlim(0, 1.15)
    ax.set_xlabel("원/달러 +1% → EPS %")
    ax.set_title("환율 민감도", loc="left", fontsize=11, color=C_BLUE)
    fig.tight_layout()
    return fig


def chart_fcf():
    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    x = np.arange(4)
    w = 0.36
    ax.bar(x - w / 2, list(d.FCF_BASE) + [d.FCF_BASE_SUM], w, label="기본", color=C_BLUE)
    ax.bar(x + w / 2, list(d.FCF_CONSERVATIVE) + [d.FCF_CONSERVATIVE_SUM], w, label="보수(WC 차감)", color=C_GRAY)
    ax.set_xticks(x)
    ax.set_xticklabels(["2025E", "2026E", "2027E", "3년 합"])
    ax.set_ylabel("조원")
    ax.legend()
    ax.set_title("SK하이닉스 FCF — 기본 vs 보수", loc="left", fontsize=11, color=C_BLUE)
    fig.tight_layout()
    return fig


def chart_return():
    fig, ax = plt.subplots(figsize=(8.2, 3.2))
    labs = ["25~27 FCF", "최소 50%", "확정 40조", "추가 필요"]
    vals = [d.FCF_CUM_25_27, d.FCF_RETURN_MIN, d.SKH_BUYBACK_JO, d.FCF_RETURN_REMAINING]
    ax.bar(labs, vals, color=[C_BLUE, C_GREEN, C_AMBER, C_CYAN], width=0.58)
    ax.set_ylabel("조원")
    ax.set_title("환원 구조 (2025~2027 프로그램)", loc="left", fontsize=11, color=C_BLUE)
    fig.tight_layout()
    return fig


def chart_per():
    fig, ax = plt.subplots(figsize=(8.2, 3.4))
    labs = ["SKH 본주", "삼성전자", "SKH ADR", "마이크론", "샌디스크"]
    y26 = [4.3, 5.2, 6.6, 7.5, 0]
    y27 = [3.4, 3.7, 5.2, 6.25, 7.8]
    x = np.arange(len(labs))
    ax.bar(x - 0.18, y26, 0.36, label="26 / Fwd", color=C_BLUE)
    ax.bar(x + 0.18, y27, 0.36, label="27년", color=C_CYAN)
    ax.set_xticks(x)
    ax.set_xticklabels(labs)
    ax.legend()
    ax.set_title("Forward PER", loc="left", fontsize=11, color=C_BLUE)
    fig.tight_layout()
    return fig


def chart_hbm():
    fig, ax = plt.subplots(figsize=(8.2, 3.3))
    labs = ["Bull\nAI+50% / 효율+20%", "Bear\nAI+20% / 효율+30%"]
    x = np.arange(2)
    ax.bar(x - 0.25, [50, 20], 0.24, label="AI 증가", color=C_GREEN)
    ax.bar(x, [20, 30], 0.24, label="효율 개선", color=C_AMBER)
    ax.bar(x + 0.25, [25.0, -7.7], 0.24, label="순 메모리 수요", color=C_BLUE)
    ax.axhline(0, color="#94A3B8", lw=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(labs)
    ax.set_ylabel("%")
    ax.legend(fontsize=8)
    ax.set_title("순 메모리 수요 = AI 증가 − 효율 개선", loc="left", fontsize=11, color=C_BLUE)
    fig.tight_layout()
    return fig


def chart_foundry():
    fig, ax = plt.subplots(figsize=(8.2, 3.1))
    labs = ["SF4 중·미", "SF4 대만", "SF5", "8나노"]
    lo = [10, 5, 10, 10]
    hi = [15, 10, 15, 10]
    x = np.arange(4)
    ax.bar(x - 0.18, lo, 0.36, label="하단", color=C_GRAY)
    ax.bar(x + 0.18, hi, 0.36, label="상단", color=C_BLUE)
    ax.set_xticks(x)
    ax.set_xticklabels(labs)
    ax.set_ylabel("%")
    ax.legend()
    ax.set_title("삼성 파운드리 신규주문 인상", loc="left", fontsize=11, color=C_BLUE)
    fig.tight_layout()
    return fig


def chart_mrvl():
    fig, ax = plt.subplots(figsize=(7.4, 2.8))
    ax.bar(["Marvell", "Broadcom"], [9.9, -4.6], color=[C_GREEN, C_RED], width=0.45)
    ax.axhline(0, color="#94A3B8", lw=0.8)
    ax.set_ylabel("%")
    ax.set_title("8/19 미장 — 구글 TPU 생태계 확대", loc="left", fontsize=11, color=C_BLUE)
    fig.tight_layout()
    return fig


def chart_supply():
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.2))
    axes[0].plot(["1Q 매출", "2Q 매출", "수주잔고"], [7, 11, 20], color="#7C3AED", marker="o", lw=2)
    axes[0].fill_between(range(3), [7, 11, 20], color="#7C3AED", alpha=0.12)
    axes[0].set_title("이수페타시스 Multi-Lam %", loc="left", fontsize=10, color=C_BLUE)
    x = np.arange(2)
    axes[1].bar(x - 0.18, [847, 1785], 0.36, label="매출", color=C_BLUE)
    axes[1].bar(x + 0.18, [121, 721], 0.36, label="OP", color=C_GREEN)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(["2025", "2026E"])
    axes[1].legend(fontsize=8)
    axes[1].set_title("기가비스 억", loc="left", fontsize=10, color=C_BLUE)
    fig.tight_layout()
    return fig


def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, A4[1] - 12 * mm, A4[0], 12 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont(FONT, 8)
    canvas.drawString(16 * mm, A4[1] - 8 * mm, "2026.08.19 시장 브리핑  ·  매크로 · 환율 · 주주환원 · AI 반도체")
    canvas.setFillColor(colors.HexColor("#E5E7EB"))
    canvas.rect(0, 0, A4[0], 10 * mm, fill=1, stroke=0)
    canvas.setFillColor(GRAY)
    canvas.setFont(FONT, 8)
    canvas.drawString(16 * mm, 4 * mm, "Quick 코멘트 재구성  ·  투자 참고 · 권유 아님")
    canvas.drawRightString(A4[0] - 16 * mm, 4 * mm, f"{doc.page}")
    canvas.restoreState()


def build() -> None:
    register_fonts()
    s = styles()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
        title="2026.08.19 시장 브리핑",
        author="준혁",
    )
    story = []

    cover = Table(
        [
            [Paragraph("MARKET INTELLIGENCE  ·  VISUAL BRIEF", s["cover_k"])],
            [Paragraph("2026.08.19 시장 브리핑", s["cover_t"])],
            [Paragraph("매크로의 역습, 원화 강세, 그리고 주주환원", s["cover_t"])],
            [Spacer(1, 6 * mm)],
            [Paragraph(
                "전쟁→유가→금리  |  원/달러 1,520→1,420  |  SK하이닉스 40조 소각·FCF 50%+  |  "
                "HBM은 영구 가격결정력이 아니다  |  구글–마벨  |  삼성 파운드리 +15%",
                s["cover_k"],
            )],
            [Spacer(1, 8 * mm)],
            [Paragraph(f"발행 {date.today().strftime('%Y.%m.%d')}  ·  원문 Quick 코멘트 07:09~23:50 재구성", s["cover_k"])],
            [Paragraph("투자 참고용 · 매수·매도 추천 아님 · 법적 자료 아님", s["cover_k"])],
        ],
        colWidths=[17.8 * cm],
    )
    cover.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 18),
        ("RIGHTPADDING", (0, 0), (-1, -1), 18),
        ("TOPPADDING", (0, 0), (0, 0), 20),
        ("BOTTOMPADDING", (0, -1), (0, -1), 18),
        ("TOPPADDING", (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-2, -2), 4),
    ]))
    story.append(cover)
    story.append(Spacer(1, 8 * mm))
    story.append(kpi_table(s))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "오늘을 한 문장으로: AI 수요가 갑자기 꺾인 것이 아니라, 금리·환율·섹터 로테이션이 높은 밸류에이션을 압박했고, "
        "하이닉스는 환원으로 방어선을 쳤다.",
        s["body"],
    ))

    story.append(Paragraph("1. 매크로 — 전쟁보다 금리", s["h1"]))
    story.append(Paragraph(
        "이란·호르무즈 → 유가 → 인플레 우려 → 미 국채금리 → 고PER 성장주. 재무부 바이백(20억→40억 달러)은 속도 조절이지 "
        "재정적자·인플레·AI 자금수요의 해법이 아니다. 실무 금리는 10년물. 4.7% 이하 안정이 단기 최대 변수, 5% 고착이면 위험자산 회피 확대.",
        s["body"],
    ))
    story.append(fig_img(chart_yields()))
    story.append(Paragraph("도표 1. 미국 10년·30년 국채 — 장중 고점, 마감, 바이백 이후", s["cap"]))
    story.append(Paragraph(
        "2024.8 엔캐리 당시 USD/JPY 152→142대와 함께 닛케이 −19.5%, 코스피 −11.9%. 지금은 157~159에서 반등 중이라 "
        "1차 충격은 엔캐리 청산보다 글로벌 금리/밸류 압박으로 보는 편이 타당하다. 단기 추는 전쟁 매크로 쪽으로 기울어 있으나 "
        "토큰 수요→AI CAPEX 궤도는 금리 1~2회 인상만으로 꺾이기 어렵다는 것이 기본 가정이다.",
        s["body"],
    ))

    story.append(Paragraph("2. 환율 — 국내 달러 공급이 먼저 세졌다", s["h1"]))
    story.append(Paragraph(
        "1,400원 아래는 달러인덱스만의 이야기가 아니다. 법인세·설비투자, 수출기업 달러 매도, 환헤지 비중 상승이 달러-원을 먼저 끌어내렸고 "
        "고환율 잔여 물량이 하락을 가속했다. 추가 하락의 핵심 변수는 달러: 인상 기대가 되돌려지면 DXY 99→96~97. "
        "DXY만 3~4% 하락해도 하단 약 1,360원, 국내 공급이 더해지면 1,340원대. 리스크는 외국인 매도, 이란/유가, 1,350원 부근 달러 수요.",
        s["body"],
    ))
    story.append(fig_img(chart_fx(), ratio=0.44))
    story.append(Paragraph("도표 2. 원/달러 경로 가정 — 1,520 → 1,420 → 1,360/1,340", s["cap"]))
    story.append(fig_img(chart_beta(), ratio=0.34))
    story.append(Paragraph(
        f"도표 3. 환율 베타. 1,520→1,420(−{abs(d.FX_DROP_PCT)*100:.1f}%) × SKH 0.9 = EPS 약 −{d.SKH_EPS_HIT_PCT:.1f}%. "
        f"27년 순익 300~400조라면 약 {d.SKH_NI_ADJ_LOW:.0f}~{d.SKH_NI_ADJ_HIGH:.0f}조 조정. 26년 하반기 환율 조정 가능성 16.3조. "
        "삼성전자 카드 원문의 ‘SK하이닉스 EPS +0.4%’는 맥락상 삼성전자 민감도.",
        s["cap"],
    ))

    story.append(PageBreak())
    story.append(Paragraph("3. SK하이닉스 주주환원 — 40조는 시작", s["h1"]))
    story.append(Paragraph(
        "정책 기간은 2025~2027년. 192.5조는 2027년 한 해에 주는 돈이 아니다. 2028년 102.5조는 FCF 모델 참고치이지 회사 정책이 아니다. "
        "기준은 누적 FCF의 ‘50% 이상’. 이미 40조 소각이 있으니 50%만 적용해도 잔여 152.5조+. 구체 규모는 3Q26 실적 발표.",
        s["body"],
    ))
    story.append(fig_img(chart_return(), ratio=0.42))
    story.append(Paragraph("도표 4. 385조 × 50% = 192.5조. 확정 40조, 추가 152.5조+", s["cap"]))
    story.append(fig_img(chart_fcf(), ratio=0.44))
    story.append(Paragraph("도표 5. 연도별 FCF. 보수안은 운전자본 등 20~30조 차감, 3년 합 565조", s["cap"]))
    story.append(simple_table(
        s,
        ["항목", "숫자", "읽는 법"],
        [
            ["자사주 소각", "40조 · 2,407만주 · 3.3%", "8/20~11/19 전량 소각, EPS +3.4%"],
            ["일평균 매입", "6,452억 × 62일", "400,024억 ≈ 40.0조"],
            ["환원 기준", "누적 FCF 50% 이상", "기존 50% 범위 내에서 상향"],
            ["추가 발표", "3Q26 실적", "자사주·현금·특별배당 검토"],
        ],
        [4.2 * cm, 5.4 * cm, 8.2 * cm],
    ))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("4. 메모리 밸류 — 본주 · ADR · 피어", s["h1"]))
    story.append(fig_img(chart_per(), ratio=0.44))
    story.append(Paragraph("도표 6. 본주 150만/24.75만, ADR $163.8(1,390원=228만). ADR 프리미엄 +52%", s["cap"]))
    story.append(simple_table(
        s,
        ["종목", "26 PER", "27 PER", "함의"],
        [
            ["SKH 본주 150만", "4.3", "3.4", "보수 27 PER 5.1 · 사이클 6~7배 시 208~242만"],
            ["삼성 24.75만", "5.2", "3.7", "보수 27 PER 5.6 · 사이클 6~7배 시 28.7~33.5만"],
            ["SKH ADR $163.8", "6.6", "5.2", "마이크론 대비 −17%. 정상 프리미엄 +20%면 본주 190만"],
            ["마이크론 $937", "Fwd12 7.5", "CY27 6.25", "CY27 EPS $150"],
            ["샌디스크 $1,568", "—", "FY27 7.8", "FY27 EPS $201"],
        ],
        [4.4 * cm, 3.2 * cm, 3.4 * cm, 6.8 * cm],
    ))

    story.append(PageBreak())
    story.append(Paragraph("5. HBM 논쟁 — 가격결정력은 영구가 아니다", s["h1"]))
    story.append(Paragraph(
        "‘HBM이 비싸서 수요가 곧 꺾인다’는 타당성이 낮다. ‘비쌀수록 효율화·대체 유인이 커진다’는 타당성이 높다. "
        "SRAM ≠ HBM. 대체가 아니라 분업이다. Cerebras·Groq·NVIDIA+Groq·KV 압축은 이미 현실. "
        "2026~28년 초과이익의 양날의 검이 2028년 이후 효율화 촉진이다.",
        s["body"],
    ))
    story.append(fig_img(chart_hbm(), ratio=0.44))
    story.append(Paragraph("도표 7. Bull 순수요 약 +25%, Bear 약 −8%. 핵심 변수는 AI 증가율 − 메모리 효율 개선률", s["cap"]))

    story.append(Paragraph("6. 삼성 파운드리 · 구글–마벨", s["h1"]))
    story.append(fig_img(chart_foundry(), ratio=0.40))
    story.append(Paragraph("도표 8. SF4 신규주문 최대 +15%. TSMC 포화, 중국 수요, 평택 SF4 풀가동. 이르면 내년 흑자 전환 기대", s["cap"]))
    story.append(fig_img(chart_mrvl(), width=14 * cm, ratio=0.40))
    story.append(Paragraph(
        "도표 9. 마벨 +9.9% / 브로드컴 −4.6%. 워런트 5,897만주, 행사가 $206.58, Google 커스텀 매출 $5억마다 1 tranche, FY27 Q3~FY33.",
        s["cap"],
    ))

    story.append(Paragraph("7. 소부장 · 엔비디아 프리뷰", s["h1"]))
    story.append(fig_img(chart_supply(), ratio=0.42))
    story.append(Paragraph("도표 10. 이수페타시스 Multi-Lam 7→11→잔고 20%+. 기가비스 25년 847/121억 → 26E 1,785/721억", s["cap"]))
    story.append(Paragraph(
        "NVIDIA: Beat보다 CAPEX 지속과 Rubin(3Q26). Q3 $108B(+90%), Q4 $120B(+77%여도 절대액 확대). "
        "Hyperscaler 2027 CAPEX ≥ $1T(+33%). OpenAI Q2 $6.7B(+18% QoQ), 손실 $9.3→$12.3B. "
        "8/26 실적과 ‘순환 금융 vs 최종 수요’가 단기 변수. 금리 하락에도 기술주가 약했던 이유는 AI→헬스케어 로테이션.",
        s["body"],
    ))

    story.append(Paragraph("8. 관전 포인트", s["h1"]))
    story.append(Paragraph("• 매크로: 10Y 4.7% 안정 vs 5% 돌파. 유가 $90 vs $100. USD/JPY가 150 초반으로 깨지면 2024.8형 엔캐리 의심.", s["bullet"]))
    story.append(Paragraph("• 환율: DXY 99 vs 96~97. 1,350원 부근 달러 수요. 외국인 순매도.", s["bullet"]))
    story.append(Paragraph("• 반도체: 8/26 엔비디아. 하이닉스 3Q26 추가 환원. 마벨 tranche. Multi-Lam 4Q 전환.", s["bullet"]))
    story.append(Paragraph(
        "국내 기관의 고민은 AI를 줄일지가 아니라 대형주 익스포저 vs 변압기·소부장 믹스다. "
        "임계점 전에는 글로벌 자금이 AI 비중을 크게 줄이기 어렵다.",
        s["body"],
    ))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("원문 Quick 코멘트를 도표로 재구성한 참고 자료입니다. 투자 판단은 각자.", s["cap"]))

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
