#!/usr/bin/env python3
"""2026.08.19 시장 분석 PDF 레포트 생성."""

from __future__ import annotations

import io
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUT_PATH = Path("/workspace/reports/2026-08-19-market-analysis-report.pdf")
FONT_PATH = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
FONT_NAME = "WQYMicroHei"

# Brand colors
NAVY = colors.HexColor("#0F2043")
NAVY2 = colors.HexColor("#1E407C")
GOLD = colors.HexColor("#B8943A")
GRAY = colors.HexColor("#4B5563")
LIGHT = colors.HexColor("#EEF2F8")
RED = colors.HexColor("#DC2626")
GREEN = colors.HexColor("#16A34A")
AMBER = colors.HexColor("#D97706")


def register_fonts():
    pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH))
    fm.fontManager.addfont(FONT_PATH)
    prop = fm.FontProperties(fname=FONT_PATH)
    plt.rcParams["font.family"] = prop.get_name()
    plt.rcParams["axes.unicode_minus"] = False


def build_styles():
    base = getSampleStyleSheet()
    return {
        "cover_title": ParagraphStyle(
            "cover_title",
            fontName=FONT_NAME,
            fontSize=26,
            leading=34,
            textColor=colors.white,
            alignment=TA_LEFT,
            spaceAfter=12,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            fontName=FONT_NAME,
            fontSize=12,
            leading=18,
            textColor=colors.HexColor("#CBD5E1"),
            alignment=TA_LEFT,
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName=FONT_NAME,
            fontSize=18,
            leading=24,
            textColor=NAVY,
            spaceBefore=16,
            spaceAfter=10,
            borderPadding=4,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName=FONT_NAME,
            fontSize=13,
            leading=18,
            textColor=NAVY2,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            fontName=FONT_NAME,
            fontSize=10,
            leading=15,
            textColor=colors.HexColor("#1F2937"),
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName=FONT_NAME,
            fontSize=10,
            leading=14,
            textColor=colors.HexColor("#374151"),
            leftIndent=14,
            spaceAfter=3,
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName=FONT_NAME,
            fontSize=8.5,
            leading=12,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=10,
        ),
        "footer": ParagraphStyle(
            "footer",
            fontName=FONT_NAME,
            fontSize=8,
            textColor=GRAY,
            alignment=TA_CENTER,
        ),
        "toc": ParagraphStyle(
            "toc",
            fontName=FONT_NAME,
            fontSize=11,
            leading=20,
            textColor=colors.HexColor("#1F2937"),
        ),
        "kpi_val": ParagraphStyle(
            "kpi_val",
            fontName=FONT_NAME,
            fontSize=16,
            leading=20,
            textColor=NAVY,
            alignment=TA_CENTER,
        ),
        "kpi_lbl": ParagraphStyle(
            "kpi_lbl",
            fontName=FONT_NAME,
            fontSize=8,
            leading=11,
            textColor=GRAY,
            alignment=TA_CENTER,
        ),
    }


def fig_to_image(fig, width=16 * cm) -> Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    buf.seek(0)
    img = Image(buf, width=width, height=width * 0.52)
    img.hAlign = "CENTER"
    return img


def make_cover_table(styles) -> Table:
    data = [
        [Paragraph("MARKET INTELLIGENCE REPORT", styles["cover_sub"])],
        [Paragraph("2026.08.19 시장 분석", styles["cover_title"])],
        [Paragraph("매크로 역습 vs AI·반도체 펀더멘탈", styles["cover_title"])],
        [Spacer(1, 8 * mm)],
        [Paragraph(
            "미·이란 → 유가 → 금리 → 성장주 조정 | SK하이닉스 40조 Buyback | "
            "삼성 파운드리 15% | Wood·Thompson HBM 경고",
            styles["cover_sub"],
        )],
        [Spacer(1, 12 * mm)],
        [Paragraph(f"발행일: {date.today().strftime('%Y년 %m월 %d일')}", styles["cover_sub"])],
        [Paragraph("Quick 코멘트 · Reuters · CNBC · Stratechery · ARK 종합", styles["cover_sub"])],
        [Paragraph("투자 참고용 · 투자 권유 아님", styles["cover_sub"])],
    ]
    t = Table(data, colWidths=[17 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 24),
        ("RIGHTPADDING", (0, 0), (-1, -1), 24),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (0, 0), 28),
        ("BOTTOMPADDING", (0, -1), (0, -1), 28),
    ]))
    return t


def kpi_row(styles) -> Table:
    kpis = [
        ("10Y 미국채", "4.69%", "고점 4.75%"),
        ("30Y 미국채", "5.285%", "19년 고점"),
        ("SK Buyback", "40조원", "시총 3.3%"),
        ("삼성 SF4", "+15%", "파운드리 인상"),
    ]
    cells = []
    for lbl, val, sub in kpis:
        cells.append([
            Paragraph(lbl, styles["kpi_lbl"]),
            Paragraph(f"<b>{val}</b>", styles["kpi_val"]),
            Paragraph(sub, styles["kpi_lbl"]),
        ])
    rows = [[c[0], c[1], c[2]] for c in cells]
    # flatten to 4 columns
    t = Table(
        [[Paragraph(lbl, styles["kpi_lbl"]) for lbl, _, _ in kpis],
         [Paragraph(f"<b>{val}</b>", styles["kpi_val"]) for _, val, _ in kpis],
         [Paragraph(sub, styles["kpi_lbl"]) for _, _, sub in kpis]],
        colWidths=[4.1 * cm] * 4,
        rowHeights=[12 * mm, 14 * mm, 10 * mm],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def styled_table(headers, rows, col_widths=None) -> Table:
    data = [headers] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY2),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("FONTSIZE", (0, 1), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def chart_yield():
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    x = ["8/18 AM", "8/18 Peak", "8/18 Close", "8/19 AM", "8/19 Close"]
    ax.plot(x, [4.68, 4.75, 4.706, 4.72, 4.69], "o-", color="#DC2626", lw=2, label="10Y (%)")
    ax.plot(x, [5.25, 5.34, 5.285, 5.30, 5.285], "s-", color="#D97706", lw=2, label="30Y (%)")
    ax.axhline(4.7, color="#16A34A", ls="--", alpha=0.7, label="10Y 4.7% 임계")
    ax.set_ylabel("수익률 (%)")
    ax.set_title("미국 국채금리 추이 (8/18~19)", fontsize=11, fontweight="bold", color="#0F2043")
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(4.5, 5.5)
    return fig


def chart_crash():
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    labels = ["7/31", "8/2", "8/5", "8/6"]
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, [0, -5.81, -19.5, 10.23], w, label="Nikkei (%)", color="#1E407C")
    ax.bar(x + w / 2, [0, -3.65, -11.9, 3.30], w, label="KOSPI (%)", color="#B8943A")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.axhline(0, color="#94A3B8", lw=0.8)
    ax.set_title("8/5 급락·8/6 반등 — 유동성 쇼크", fontsize=11, fontweight="bold", color="#0F2043")
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    return fig


def chart_macro_radar():
    fig, ax = plt.subplots(figsize=(6.5, 6.5), subplot_kw=dict(polar=True))
    labels = ["유가\n안정", "10Y\n4.7%↓", "30Y\n5.3%↓", "지정학\n완화", "엔화\n안정", "Fed\n동결"]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    current = [35, 55, 45, 20, 60, 70]
    target = [85, 90, 85, 80, 75, 85]
    current += current[:1]
    target += target[:1]
    ax.plot(angles, current, "o-", color="#DC2626", label="현재 (8/19)")
    ax.fill(angles, current, alpha=0.15, color="#DC2626")
    ax.plot(angles, target, "o-", color="#16A34A", label="시장 최선")
    ax.fill(angles, target, alpha=0.08, color="#16A34A")
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylim(0, 100)
    ax.set_title("매크로 변수 게이지", fontsize=11, fontweight="bold", color="#0F2043", pad=16)
    ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=8)
    return fig


def chart_dram():
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    x = ["24Q1", "24Q4", "25Q2", "25Q4", "26Q2", "26Q4E"]
    ax.plot(x, [100, 180, 280, 400, 420, 340], "o-", color="#7C3AED", lw=2, label="DRAM/HBM 가격지수")
    ax.plot(x, [100, 140, 185, 240, 300, 360], "s--", color="#0891B2", lw=2, label="AI Capex 지수")
    ax.axvspan(4, 5.5, alpha=0.12, color="#D97706", label="대체 가속 구간")
    ax.set_title("DRAM/HBM 가격 vs AI Capex (2024=100)", fontsize=11, fontweight="bold", color="#0F2043")
    ax.legend(fontsize=7.5, loc="upper left")
    ax.grid(True, alpha=0.3)
    return fig


def chart_hbm_pie():
    fig, ax = plt.subplots(figsize=(5.5, 3.5))
    labels = ["Training\n(HBM)", "Inf. GPU", "Inf. SRAM", "경량화", "ASIC"]
    sizes = [35, 30, 12, 13, 10]
    cols = ["#DC2626", "#D97706", "#16A34A", "#1E407C", "#7C3AED"]
    ax.pie(sizes, labels=labels, autopct="%1.0f%%", colors=cols, startangle=90, textprops={"fontsize": 8})
    ax.set_title("AI 워크로드별 HBM 의존도 (개념)", fontsize=11, fontweight="bold", color="#0F2043")
    return fig


def chart_bandwidth():
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    labels = ["HBM3", "HBM4", "Groq LPU", "Cerebras WSE-3"]
    vals = [1, 1.6, 850, 6300]
    bars = ax.bar(labels, vals, color=["#DC2626", "#D97706", "#16A34A", "#0891B2"])
    ax.set_yscale("log")
    ax.set_ylabel("상대 대역폭 (HBM3=1, log)")
    ax.set_title("메모리 대역폭 비교", fontsize=11, fontweight="bold", color="#0F2043")
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v * 1.15, f"{v:,}x" if v > 10 else f"{v}x", ha="center", fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    return fig


def chart_sk_waterfall():
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    labels = ["누적FCF\n(보수)", "50%환원", "40조\nBuyback", "추가환원", "연CAPEX", "순현금"]
    vals = [565, 192.5, 40, 152.5, 40, 69]
    cols = ["#1E407C", "#16A34A", "#0891B2", "#16A34A", "#D97706", "#7C3AED"]
    ax.bar(labels, vals, color=cols)
    ax.set_ylabel("조원")
    ax.set_title("SK하이닉스 주주환원 추산", fontsize=11, fontweight="bold", color="#0F2043")
    for i, v in enumerate(vals):
        ax.text(i, v + 8, f"{v}", ha="center", fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    return fig


def chart_samsung():
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    labels = ["SF4\n(중·美)", "SF4\n(대만)", "SF5", "8nm"]
    vals = [12.5, 7.5, 12.5, 10]
    ax.bar(labels, vals, color=["#16A34A", "#0891B2", "#16A34A", "#1E407C"])
    ax.set_ylabel("인상률 (%)")
    ax.set_title("삼성 파운드리 공정별 가격 인상 (7월~)", fontsize=11, fontweight="bold", color="#0F2043")
    for i, v in enumerate(vals):
        ax.text(i, v + 0.3, f"+{v}%", ha="center", fontsize=9)
    ax.set_ylim(0, 16)
    ax.grid(True, axis="y", alpha=0.3)
    return fig


def chart_multilam():
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    x = ["1Q25", "2Q25", "4Q25", "1Q26", "2Q26", "수주잔고", "4Q26E"]
    y = [3, 4, 6, 7, 11, 20, 25]
    ax.fill_between(range(len(x)), y, alpha=0.15, color="#7C3AED")
    ax.plot(x, y, "o-", color="#7C3AED", lw=2)
    ax.set_ylabel("Multi-Lam 비중 (%)")
    ax.set_title("이수페타시스 Multi-Lam 믹스 개선", fontsize=11, fontweight="bold", color="#0F2043")
    ax.grid(True, alpha=0.3)
    return fig


def chart_foundry_share():
    fig, ax = plt.subplots(figsize=(5, 3.5))
    labels = ["TSMC 70%", "Samsung 7%", "Intel 8%", "기타 15%"]
    sizes = [70, 7, 8, 15]
    ax.pie(sizes, labels=labels, autopct="", colors=["#DC2626", "#1E407C", "#0891B2", "#94A3B8"],
           startangle=90, textprops={"fontsize": 8})
    ax.set_title("글로벌 파운드리 점유 (2026 Q1)", fontsize=11, fontweight="bold", color="#0F2043")
    return fig


def chart_allocation():
    fig, ax = plt.subplots(figsize=(7.2, 3.2))
    labels = ["미 빅테크", "韓 메모리", "韓 파운드리", "日/台", "소부장", "전력"]
    x = np.arange(len(labels))
    w = 0.35
    ax.bar(x - w / 2, [90, 70, 55, 65, 50, 40], w, label="글로벌", color="#1E407C")
    ax.bar(x + w / 2, [60, 75, 70, 50, 65, 55], w, label="국내 기관", color="#16A34A")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("선호도 (개념)")
    ax.set_title("섹터별 자금 선호 (개념)", fontsize=11, fontweight="bold", color="#0F2043")
    ax.legend(fontsize=8)
    ax.grid(True, axis="y", alpha=0.3)
    return fig


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_NAME, 8)
    canvas.setFillColor(colors.HexColor("#94A3B8"))
    canvas.drawString(1.5 * cm, 1.2 * cm, "2026.08.19 Market Analysis Report")
    canvas.drawRightString(A4[0] - 1.5 * cm, 1.2 * cm, f"p. {doc.page}")
    canvas.restoreState()


def build_pdf():
    register_fonts()
    styles = build_styles()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUT_PATH),
        pagesize=A4,
        leftMargin=1.8 * cm,
        rightMargin=1.8 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.8 * cm,
        title="2026.08.19 시장 분석 리포트",
        author="Market Intelligence",
    )

    story = []

    # Cover
    story.append(Spacer(1, 3 * cm))
    story.append(make_cover_table(styles))
    story.append(PageBreak())

    # TOC
    story.append(Paragraph("목 차", styles["h1"]))
    toc_items = [
        "1. Executive Summary",
        "2. 매크로 역습 — 금리·유가·지정학",
        "3. 단기 핵심 변수 &amp; 시장 영향",
        "4. 메모리 논쟁 — Wood &amp; Thompson Deep Dive",
        "5. HBM 대체 기술 — Cerebras · Groq · GPU",
        "6. SK하이닉스 — 40조 Buyback &amp; FCF 50%+",
        "7. 삼성전자 — 파운드리 15% 인상",
        "8. 공급망 수혜 — 이수페타시스 · 기가비스",
        "9. 투자 프레임 &amp; 결론",
    ]
    for item in toc_items:
        story.append(Paragraph(f"• {item}", styles["toc"]))
    story.append(PageBreak())

    # 1. Executive Summary
    story.append(Paragraph("1. Executive Summary", styles["h1"]))
    story.append(kpi_row(styles))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        "<b>핵심 결론:</b> 8/19 하락의 직접 원인은 AI 수요 약화가 아니라 "
        "<b>미·이란 협상 불확실성 → 유가 상승 → 미 국채금리 급등 → 고PER 성장주 밸류에이션 압박</b> "
        "경로입니다. AI Capex·토큰 수요의 중장기 궤도는 유지되나, 단기 무게중심은 매크로(전쟁·금리)에 치우칩니다.",
        styles["body"],
    ))
    story.append(Paragraph(
        "동시에 SK하이닉스 40조 자사주·소각, 삼성 파운드리 최대 15% 인상 등 "
        "<b>펀더멘탈 호재</b>와 Cathie Wood·Ben Thompson의 "
        "<b>「HBM 고가 = 장기 대체 가속」</b> 구조적 경고가 공존하는 복합 국면입니다.",
        styles["body"],
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(styled_table(
        ["구분", "단기 시그널", "중장기 시그널"],
        [
            ["조정 원인", "유가·금리 쇼크", "AI 사이클 intact"],
            ["Fed", "동결이 최선", "인하 = 24년형 패턴?"],
            ["메모리", "Buyback·HBM 실적", "대체기술·중국 공급"],
            ["파운드리", "삼성 가격↑", "TSMC 분산"],
            ["소부장", "상대적 방어", "CAPEX 레버리지"],
        ],
        [3.5 * cm, 6 * cm, 6 * cm],
    ))
    story.append(PageBreak())

    # 2. Macro
    story.append(Paragraph("2. 매크로 역습 — 금리·유가·지정학", styles["h1"]))
    story.append(Paragraph(
        "미·이란 60일 협상 프레임워크 만료, 트럼프 연장 거부, 이란 「외교 실패 시 공세 전환」 발언 → "
        "시장은 호르무즈 장기 봉쇄를 pricing-in. Deutsche Bank: 「단일 촉매 없이 채권·주식 동반 약세」.",
        styles["body"],
    ))
    story.append(fig_to_image(chart_yield()))
    story.append(Paragraph("그림 1. 10Y 4.75% (20개월 고점), 30Y 5.34% (19년 고점) 후 장 말판 소폭 반전", styles["caption"]))
    story.append(fig_to_image(chart_crash()))
    story.append(Paragraph(
        "그림 2. 8/5 Nikkei -19.5% → 8/6 +10.23%: 펀더멘탈 1일 변화보다 레버리지·포지션 청산(유동성 쇼크)",
        styles["caption"],
    ))

    story.append(Paragraph("2.1 Deep Dive — 이란·호르무즈·FT (8/19)", styles["h2"]))
    for b in [
        "FT: 트럼프 확전 시 이란, 유럽(불가리아 Bezmer·키프로스) 미군 시설 공격 옵션 검토. 호르무즈 해저 인프라 공격 가능성.",
        "「이란이 유럽 공격 결정」이 아닌, 확전 시 대비 시나리오 검토.",
        "7월 미 재정적자 $3030억 (2021.3 이후 최대). 이자비용 연 $1.2조+. AI 기업 회사채 $1.5조 발행 → 국채 vs 테크 채권 경쟁.",
        "JP Morgan: term premium 상승. 10Y 5% 돌파 시 글로벌 위험자산 전면 회피 가능.",
    ]:
        story.append(Paragraph(f"• {b}", styles["bullet"]))
    story.append(PageBreak())

    # 3. Watch variables
    story.append(Paragraph("3. 단기 핵심 변수 &amp; 시장 영향", styles["h1"]))
    story.append(fig_to_image(chart_macro_radar(), width=13 * cm))
    story.append(Paragraph("그림 3. 유가·10Y·30Y·지정학·엔화·Fed — 6축 매크로 게이지", styles["caption"]))
    story.append(styled_table(
        ["변수", "안정", "위험", "현재 (8/19)", "영향"],
        [
            ["브렌트유", "$90 전후", "$100+", "$90+", "인플레 → 금리"],
            ["10Y", "4.7%↓", "5%+", "4.69%", "고PER 할인↑"],
            ["30Y", "5.3%↓", "5.34%+", "5.285%", "성장주 회피"],
            ["USD/JPY", "157~159", "152→150", "157~159", "엔캐리 경계"],
            ["미·이란", "소강", "확전", "협상 결렬", "유가·금리 동반↑"],
        ],
        [2.5 * cm, 2.5 * cm, 2.5 * cm, 2.8 * cm, 5 * cm],
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "<b>결론:</b> 10Y 4.7% 이하 + 유가 안정 + 지정학 소강 = 성장주 부담 완화. "
        "현재 조정은 AI 사이클 훼손보다 「유가발 금리 쇼크」 성격이 강함.",
        styles["body"],
    ))
    story.append(PageBreak())

    # 4. Memory debate
    story.append(Paragraph("4. 메모리 논쟁 — Wood &amp; Thompson Deep Dive", styles["h1"]))
    story.append(fig_to_image(chart_dram()))
    story.append(Paragraph("그림 4. JP Morgan: DRAM 2024~26 +400% (chipflation). Wood: 고가 = 대체 유인", styles["caption"]))
    story.append(fig_to_image(chart_hbm_pie(), width=12 * cm))
    story.append(Paragraph("그림 5. Inference 영역에서 HBM 의존도 먼저 축소 (Wood 핵심 주장)", styles["caption"]))

    story.append(Paragraph("4.1 Cathie Wood (ARK Invest)", styles["h2"]))
    for b in [
        "메모리 = 반도체 공급망에서 「가장 cyclical·commoditized」",
        "「가격 3~10배 = 기술 정상 상태 아님 → 부정적 신호」 (Tesla 코발트 제거 analogy)",
        "Cerebras·Groq: inference에서 외부 HBM 불필요. ARK CBRS 8월 $28M+ 매수",
        "Micron·SK하이닉스 미보유. 가격 급등 = SK·삼성 공급 확대 invitation",
    ]:
        story.append(Paragraph(f"• {b}", styles["bullet"]))

    story.append(Paragraph("4.2 Ben Thompson (Stratechery)", styles["h2"]))
    for b in [
        "「메모리 업체 = 이란, HBM = 호르무즈 해협」",
        "억지력 = 카드를 쓸 수 있다는 것. 실제 사용 → 상대 영구 우회 결심",
        "「UAE·사우디 파이프라인·新항구 → 다시 당하지 않을 것」",
        "Big 3 중국 메모리 문 개방 → 장기 후회 가능 (2026.06 Stratechery)",
        "Apple·Microsoft 등: 알고리즘 최적화, 신규 공급자, 시스템 재설계",
    ]:
        story.append(Paragraph(f"• {b}", styles["bullet"]))

    story.append(Paragraph("4.3 양면 논리", styles["h2"]))
    story.append(styled_table(
        ["관점", "논리", "함의"],
        [
            ["공급 (SK)", "가격 비정상 → 공급 확대 우선", "단기 실적·Buyback"],
            ["Wood", "공급↑ → 장기 가격 정상화", "cyclical peak 경계"],
            ["Thompson", "카드 사용 → 아키텍처 우회", "wallet share 재분배"],
        ],
        [2.5 * cm, 6.5 * cm, 6.5 * cm],
    ))
    story.append(PageBreak())

    # 5. HBM alternatives
    story.append(Paragraph("5. HBM 대체 기술 — Cerebras · Groq · GPU", styles["h1"]))
    story.append(fig_to_image(chart_bandwidth()))
    story.append(Paragraph("그림 6. SRAM machine: Cerebras 21PB/s vs HBM ~3TB/s (수천 배)", styles["caption"]))
    story.append(styled_table(
        ["아키텍처", "온칩 메모리", "HBM", "강점", "약점"],
        [
            ["NVIDIA GPU", "소량 SRAM", "80GB HBM3", "Training+범용", "비용·병목"],
            ["Cerebras WSE-3", "44GB/wafer", "없음", "초고속 inference", "용량·Training"],
            ["Groq LPU", "230MB/chip", "없음", "TTFT <100ms", "대형모델 tiling"],
            ["대체 4종", "—", "—", "SRAM·압축·경량화·ASIC", "Training 한계"],
        ],
        [2.8 * cm, 2.5 * cm, 2.2 * cm, 3.5 * cm, 3.5 * cm],
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Cerebras CS-4 (2026): 매출 $880~890M → 2027 3배+. Groq: Nvidia $200억 인수(2025.12). "
        "AI Capex 총량 유지 전제하, 메모리 wallet share가 GPU/ASIC/SRAM으로 재분배될 수 있음.",
        styles["body"],
    ))
    story.append(PageBreak())

    # 6. SK Hynix
    story.append(Paragraph("6. SK하이닉스 — 40조 Buyback &amp; FCF 50%+", styles["h1"]))
    story.append(fig_to_image(chart_sk_waterfall()))
    story.append(Paragraph("그림 7. 보수 FCF 565조 → 50%+ 환원 192.5조+. 40조 확정 → 추가 152.5조+", styles["caption"]))
    story.append(styled_table(
        ["항목", "내용", "해석"],
        [
            ["규모", "40조 / 2,407만주 (3.3%)", "韓 상장사 역대 최대"],
            ["기간", "8/20~11/19 (62영업일)", "일 ~6,452억 매입"],
            ["FCF", "2025~27 50% 초과", "3Q26(10월) 추가 공개"],
            ["⚠", "2028 102.5조", "모델 참고치 (정책 아님)"],
            ["CAPEX", "연 ~40조+ / 10년 $7200억", "Buyback vs Fab 동시"],
            ["순현금", "2Q26末 ~69조", "재무건전성 충족"],
        ],
        [3 * cm, 6.5 * cm, 5.8 * cm],
    ))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "8/13 Investor Day 이후 성장·마진 재평가 + Buyback = EPS 레버리지. "
        "8/5~7 -15.1% 하락 → Buyback이 +20% 직접 원인은 아님.",
        styles["body"],
    ))
    story.append(PageBreak())

    # 7. Samsung
    story.append(Paragraph("7. 삼성전자 — 파운드리 15% 인상", styles["h1"]))
    story.append(fig_to_image(chart_samsung()))
    story.append(Paragraph("그림 8. TSMC 포화 → 삼성 가격결정력. 2022~ 적자 → 2027 흑자 전환 기대", styles["caption"]))
    story.append(fig_to_image(chart_foundry_share(), width=11 * cm))
    story.append(Paragraph("그림 9. TSMC 70% vs Samsung 7% (Counterpoint 2026 Q1)", styles["caption"]))
    for b in [
        "평택 SF4: 퀄컴 + HBM 베이스다이 풀가동. 중국 팹리스 15% 인상 수용.",
        "고객: Tesla, Apple, Broadcom, Nvidia AI inference, Google 4nm 협의.",
        "2026 파운드리: 첨단 50%+, AI/HPC 30%+ (2025末 15~20%).",
    ]:
        story.append(Paragraph(f"• {b}", styles["bullet"]))
    story.append(PageBreak())

    # 8. Supply chain
    story.append(Paragraph("8. 공급망 수혜 — 이수페타시스 · 기가비스", styles["h1"]))
    story.append(fig_to_image(chart_multilam()))
    story.append(Paragraph("그림 10. Multi-Lam 1Q 7% → 2Q 11% → 수주잔고 20%+. +15% 판가 (하반기~)", styles["caption"]))

    story.append(Paragraph("8.1 이수페타시스 (2Q26)", styles["h2"]))
    story.append(styled_table(
        ["지표", "실적", "YoY", "vs 컨센"],
        [
            ["매출", "3,799억", "+57.4%", "+4.9%"],
            ["영업이익", "771억", "+83.3%", "+2.7%"],
            ["OPM", "20.3%", "↑", "—"],
            ["Capa", "1,200→1,500→1,800억/월", "26~28", "—"],
        ],
        [3 * cm, 4 * cm, 3 * cm, 3.5 * cm],
    ))

    story.append(Paragraph("8.2 기가비스 (420770)", styles["h2"]))
    story.append(styled_table(
        ["항목", "내용"],
        [
            ["사업", "FC-BGA AOI(탐지) + AOR(레이저 수리)"],
            ["계약", "8/18 일본 기판사 89.5억 (매출대비 17.1%)"],
            ["2025", "매출 847억 / OI 121억"],
            ["2026E", "매출 1,785억 / OI 721억 (메리츠)"],
            ["고객", "이비덴, 신코, 유니마이크론, 삼성전기"],
        ],
        [3.5 * cm, 12 * cm],
    ))
    story.append(PageBreak())

    # 9. Framework & conclusion
    story.append(Paragraph("9. 투자 프레임 &amp; 결론", styles["h1"]))
    story.append(fig_to_image(chart_allocation()))
    story.append(Paragraph("그림 11. 글로벌: AI 비중 축소 임계 전 어려움. 국내: 대형주 vs 소부장 믹스", styles["caption"]))

    story.append(Paragraph("9.1 8/19 타임라인", styles["h2"]))
    story.append(styled_table(
        ["시각", "이벤트"],
        [
            ["06:20", "매크로 — 미·이란 → 유가 → 금리 → 기술주 압박"],
            ["11:00", "기가비스 — 일본 89.5억 계약"],
            ["15:52", "SK하이닉스 — 40조 자사주 공시"],
            ["19:56", "삼성 — 파운드리 15% 인상 (Reuters)"],
            ["20:08", "Wood/Thompson — 메모리주 경계 논리"],
            ["장 말판", "10Y 4.708% (-0.34%), 30Y 5.285% (-0.48%)"],
        ],
        [2.5 * cm, 13 * cm],
    ))

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("9.2 최종 판단", styles["h2"]))
    story.append(styled_table(
        ["영역", "판단"],
        [
            ["조정 성격", "AI 사이클 훼손 ✗ / 유가·금리 쇼크 ✓"],
            ["단기 변수", "10Y 4.7%↓, 유가 $90, 미·이란 소강"],
            ["펀더멘탈", "SK Buyback, 삼성 인상, 이수·기가비스 호재 유효"],
            ["구조 리스크", "HBM 고가 → AI 대체 투자 가속 (메모리 vs 비메모리)"],
            ["Fed", "동결이 시장 최선 (인하는 종전 전 어려움)"],
        ],
        [4 * cm, 12 * cm],
    ))

    story.append(Spacer(1, 12 * mm))
    story.append(Paragraph(
        "본 리포트는 Quick 코멘트 및 Reuters, CNBC, Stratechery, ARK Invest 등 공개자료를 "
        "종합·편집한 투자 참고 자료이며, 특정 종목의 매수·매도를 권유하지 않습니다.",
        styles["footer"],
    ))

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f"Generated: {OUT_PATH} ({OUT_PATH.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build_pdf()
