#!/usr/bin/env python3
"""8월 27일 Quick 코멘트 시각화 차트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT_DIR = Path("/workspace/reports/charts")
NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GRAY = "#4B5563"
GREEN = "#166534"
RED = "#991B1B"
ORANGE = "#C2410C"
PURPLE = "#6B21A8"
LIGHT = "#EEF2F8"
OK_BG = "#E8F5E9"
BAD_BG = "#FDECEA"
WARN_BG = "#FFF8E7"
BLUE_BG = "#E8F1FB"
PURPLE_BG = "#F3E8FF"


def _font():
    path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    fm.fontManager.addfont(path)
    name = fm.FontProperties(fname=path).get_name()
    plt.rcParams.update(
        {
            "font.family": name,
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "text.color": NAVY,
        }
    )
    return name


def _save(fig, name: str):
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / name
    fig.savefig(path, bbox_inches="tight", facecolor="white", pad_inches=0.18)
    plt.close(fig)
    print(path)


def _esc(text: str) -> str:
    return text.replace("$", r"\$") if text else text


def _box(ax, x, y, w, h, title, body, fc=LIGHT, ec="#D0D7E2", title_c=NAVY, fs=10.2, bfs=8.3):
    title = _esc(title)
    body = _esc(body)
    ax.add_patch(
        FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.05,
            edgecolor=ec,
            facecolor=fc,
        )
    )
    ax.text(x + 0.12, y + h - 0.16, title, fontsize=fs, fontweight="bold", color=title_c, va="top")
    if body:
        ax.text(x + 0.12, y + h - 0.52, body, fontsize=bfs, color=GRAY, va="top", linespacing=1.32)


def chart_premarket():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.35), dpi=170, gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    names = [
        "ARM",
        "씨게이트",
        "샌디스크",
        "인텔",
        "마이크론",
        "AMD",
        "DRAM지수",
        "SOX",
        "S&P500",
        "나스닥",
        "다우",
        "브로드컴",
        "EWY",
        "SK하이닉스",
        "엔비디아(본장)",
    ]
    vals = [3.93, 3.01, 1.26, 0.87, 0.58, 0.37, 0.27, 0.20, -0.02, -0.08, -0.21, -0.32, -0.54, -0.95, -1.59]
    colors = [GREEN if v >= 0 else RED for v in vals]
    y = np.arange(len(names))
    ax.barh(y, vals, color=colors, height=0.62, zorder=2)
    ax.set_yticks(y, names, fontsize=8.2)
    ax.axvline(0, color="#CBD5E1", lw=1)
    ax.set_xlabel("%")
    ax.set_title("8/26 미 본장  ·  실적 전 눈치 보기 (06:41)", loc="left", color=NAVY, fontsize=12.2)
    ax.set_xlim(-2.4, 5.2)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)
    for i, v in enumerate(vals):
        ax.text(
            v + (0.08 if v >= 0 else -0.08),
            i,
            f"{v:+.2f}%",
            va="center",
            ha="left" if v >= 0 else "right",
            fontsize=7.4,
            color=colors[i],
            fontweight="bold",
        )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("매크로 · 실적 후", loc="left", color=NAVY, fontsize=12.4)
    _box(ax2, 0.15, 7.35, 9.6, 2.4, "7월 PCE", "코어는 예상 충족  ·  헤드라인 소폭 상회", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.8)
    _box(ax2, 0.15, 4.7, 9.6, 2.4, "WTI / 환율 / 10년", "WTI $81대  ·  원/달러 1,384원  ·  미 10년 4.649%", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.8)
    _box(ax2, 0.15, 0.2, 9.6, 4.25, "실적 후 · 국내 함의", "시간외 반도체 전반 상승\n메모리 관련주 긍정적\n코스피 7,000 돌파 시도 가능", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.8)
    fig.tight_layout()
    _save(fig, "01_premarket.png")


def chart_korea_close():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.85), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("8/26 국내 마감  ·  코스피 약 +1%  /  코스닥 보합  ·  상승 종목 62%", loc="left", fontsize=13.2, color=NAVY)

    _box(
        ax,
        0.2,
        6.45,
        3.75,
        3.25,
        "지수",
        "코스피 2거래일 연속 상승\n약보합 출발 → 대형주 견인\n외인·기관 동반 순매수\n순환매: 보험·항공·유통·소비",
        fc=OK_BG,
        ec="#86EFAC",
        title_c=GREEN,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        4.15,
        6.45,
        3.75,
        3.25,
        "오른 곳",
        "원전  한전·한전기술 연일 강세\n건설·기계  미-이란 휴전 기대\nSKIET 상한가\n개별 이슈 순환매",
        fc=BLUE_BG,
        ec="#93C5FD",
        title_c=NAVY2,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        8.1,
        6.45,
        3.7,
        3.25,
        "빠진/약한 곳",
        "SK이노  SKIET 흡수합병\n현대차  ID 기대 대비 실망\n지수 상승의 걸림돌\n중국 시장 의문",
        fc=BAD_BG,
        ec="#FCA5A5",
        title_c=RED,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        0.2,
        0.2,
        5.75,
        5.95,
        "부정적 요인",
        "미-이란 갈등 장기화 우려\n미 10년물 4.6%대\n아직 높은 국제 유가\n미 연준 노이즈\n9월 기준금리 인상 가능성\n주요국 높은 국채 금리",
        fc=WARN_BG,
        ec=GOLD,
        title_c=ORANGE,
        fs=12,
        bfs=9.0,
    )
    _box(
        ax,
        6.15,
        0.2,
        5.65,
        5.95,
        "긍정적 요인",
        "국내 EPS 상승률 지속\n메모리 가격 상승세\n메모리 주가 = 과매도·저평가\n하이닉스 ADR → 마이크론 갭\n7월 CPI·PPI로 인상 우려 완화",
        fc=LIGHT,
        ec="#CBD5E1",
        title_c=NAVY,
        fs=12,
        bfs=9.0,
    )
    _save(fig, "02_korea_close.png")


def chart_nvidia_print():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.35), dpi=170, gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    names = ["전사 매출", "Non-GAAP EPS", "Data Center", "Hyperscale", "AI Clouds 등", "3Q 가이던스"]
    beats = [4.28, 6.22, 3.12, 11.64, -6.12, 3.00]
    colors = [GREEN if v >= 0 else RED for v in beats]
    y = np.arange(len(names))
    ax.barh(y, beats, color=colors, height=0.58, zorder=2)
    ax.axvline(0, color="#CBD5E1", lw=1)
    ax.set_yticks(y, names)
    ax.set_xlabel("컨센서스 대비 %")
    ax.set_title(_esc("FY27 2Q vs 컨센서스  ·  매출 +4.3%  /  EPS +6.2%"), loc="left", color=NAVY, fontsize=11.4)
    ax.set_xlim(-8.8, 14.5)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)
    notes = [
        "$96.22 vs $92.27B",
        "$2.22 vs $2.09",
        "$89.02 vs $86.33B",
        "$48.71 vs $43.63B",
        "$40.31 vs $42.94B",
        "$108 vs $104.86B",
    ]
    for i, (v, n) in enumerate(zip(beats, notes)):
        ax.text(
            v + (0.28 if v >= 0 else -0.28),
            i,
            f"{v:+.1f}%",
            va="center",
            ha="left" if v >= 0 else "right",
            fontsize=8.2,
            color=colors[i],
            fontweight="bold",
        )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(0.02, -0.16, "  ".join(notes[:3]), transform=ax.transAxes, fontsize=7.2, color=GRAY)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("실적 자체는 긍정", loc="left", color=NAVY, fontsize=12.2)
    _box(ax2, 0.1, 6.7, 9.7, 2.95, "매출 · 이익", "매출 $96.22B  +106% / +18%\nOP $63.96B  +124% / +19%\nGPM 75.0%  YoY +2.5%p, QoQ 보합", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    _box(ax2, 0.1, 3.45, 9.7, 2.95, "수요", "Blackwell Ultra 램프\n루빈 전환 · 중국 제외 3Q도 강함\n중국 Hopper는 DC의 1% 미만", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.6)
    _box(ax2, 0.1, 0.2, 9.7, 2.95, "유일한 하회", "AI Clouds·Industrial·Enterprise\n$40.31B vs 컨센 $42.94B\n성장은 +138% / +25%", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "03_nvidia_print.png")


def chart_nvidia_cash():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.55), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("현금흐름은 컨센보다 약했다  ·  영업이 아니라 WC + Cash Tax", loc="left", fontsize=13.0, color=NAVY)

    _box(
        ax,
        0.2,
        5.25,
        3.75,
        4.45,
        "OCF / FCF",
        "OCF  $24.08B\n전년 $15.37 / 전분기 $50.34\nFCF  $21.34B\n전년 $13.45 / 전분기 $48.55\n유형·무형 $2.68B",
        fc=WARN_BG,
        ec=GOLD,
        title_c=ORANGE,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        4.15,
        5.25,
        3.75,
        4.45,
        "매출채권",
        "AR  $63.1B\nDSO  45일 → 60일\n일부 IG 고객\n다분기 계약 지불 연장\n매출은 잡히고 현금은 뒤로",
        fc=BAD_BG,
        ec="#FCA5A5",
        title_c=RED,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        8.1,
        5.25,
        3.7,
        4.45,
        "재고 · 환원",
        "재고 $25.8B → $31.6B\n3Q Vera Rubin 준비\n2Q 환원 약 $26.0B\n잔여 매입 한도 $99.0B",
        fc=BLUE_BG,
        ec="#93C5FD",
        title_c=NAVY2,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        0.2,
        0.2,
        11.6,
        4.75,
        "다음 질문",
        "재무 위기나 현금 부족으로 보긴 어렵다.  다만 FCF가 영업이익을 못 따라가면 이익의 질 논란.\n"
        "GPU 수요가 안 꺾이면, 관심은 엔비디아가 수요 실현을 위해 얼마나 많은 신용·자본·리스크를 지느냐.\n"
        "일부 AI 클라우드 계약의 제3자 매출 공유 = 사업모델 확장 가능성.",
        fc=LIGHT,
        ec="#CBD5E1",
        title_c=NAVY,
        fs=11.6,
        bfs=9.0,
    )
    _save(fig, "04_nvidia_cash.png")


def chart_nvidia_segments():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), dpi=170)

    ax = axes[0]
    labels = ["Data Center", "Hyperscale", "AI Clouds 등", "Edge"]
    vals = [89.02, 48.71, 40.31, 7.20]
    yoy = [117, 102, 138, 27]
    colors = [NAVY2, GOLD, PURPLE, GREEN]
    bars = ax.bar(labels, vals, color=colors, width=0.62)
    ax.set_ylabel("십억 달러")
    ax.set_title(_esc("플랫폼 매출  ·  DC $89.02B가 전사 $96.22B의 핵심"), loc="left", color=NAVY, fontsize=11.0)
    ax.set_ylim(0, 108)
    for bar, v, y in zip(bars, vals, yoy):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2.2, f"${v:.1f}B\n+{y}%", ha="center", fontsize=8.2, color=NAVY, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("3Q 가이던스", loc="left", color=NAVY, fontsize=12.2)
    _box(ax2, 0.15, 6.55, 9.6, 3.15, "매출 $108.0B ±2%", "FactSet $104.86B 상회\n중국 Data Center Compute 미포함", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11.2, bfs=8.8)
    _box(ax2, 0.15, 3.35, 9.6, 2.95, "마진 · 비용", "GPM 74.0% ±50bp\nNon-GAAP OpEx 약 $9.0B", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.2, bfs=8.8)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "세율", "FY27 GAAP·Non-GAAP 16~18%", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.2, bfs=8.8)
    fig.tight_layout()
    _save(fig, "05_nvidia_segments.png")


def chart_hanmi():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.85), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("한미약품  ·  HM17321 → 제넨텍(로슈)  ·  선급금 역대 최대", loc="left", fontsize=13.0, color=NAVY)

    _box(
        ax,
        0.2,
        6.35,
        3.75,
        3.35,
        "계약",
        "계약금 $1.9억 ≈ 2,700억\n총 규모 $23.05억 ≈ 3.2조\n선급금 비율 8.2%\n국내 빅파마 L/O 평균 4%",
        fc=OK_BG,
        ec="#86EFAC",
        title_c=GREEN,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        4.15,
        6.35,
        3.75,
        3.35,
        "왜 로슈가 샀나",
        "비만 후발 · 시급성\n에니세파타이드 차별 부족\nRG6652 경구제 차별 부족\nRG6237 2상 2건 실패",
        fc=WARN_BG,
        ec=GOLD,
        title_c=ORANGE,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        8.1,
        6.35,
        3.7,
        3.35,
        "밸류",
        "투자의견 매수 유지\nTP 650,000원  +27.5%\nHM17321 가치 1.7조\n신약가치 합 4.9조",
        fc=BLUE_BG,
        ec="#93C5FD",
        title_c=NAVY2,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        0.2,
        0.2,
        11.6,
        5.85,
        "아직 남았다",
        "선급금은 4Q 실적 반영.  한미사이언스 배분 없이 한미약품이 온전히 수취.\n"
        "1상인데도 선급금 절대액이 역대 단일 에셋 L/O 중 가장 높음.\n"
        "남은 파이프: HM15275(G/G/G, 글로벌 2상) · HM-500197(마이오스타틴, 6월 ADA 전임상).\n"
        "27년 로슈 글로벌 2상 진입 시 대규모 마일스톤.  H.O.P 빅파마 검증 시작.",
        fc=PURPLE_BG,
        ec="#D8B4FE",
        title_c=PURPLE,
        fs=12,
        bfs=9.0,
    )
    _save(fig, "06_hanmi_deal.png")


def chart_ess():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 6.05), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("미국 ESS 4배 성장  ·  EV 캐즘을 ESS가 흡수하기 시작했다", loc="left", fontsize=13.0, color=NAVY)

    _box(
        ax,
        0.2,
        6.45,
        3.75,
        3.25,
        "왜 지금",
        "AI DC → 전력 수요↑\n전력망 부담 → 재생+ESS\n美 ESS 2031년 약 4배\n2Q 매출 비중 확대",
        fc=BLUE_BG,
        ec="#93C5FD",
        title_c=NAVY2,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        4.15,
        6.45,
        3.75,
        3.25,
        "LG엔솔",
        "북미 5대 ESS 거점\n미국 · 캐나다\n연말 50GWh+ 캐파\n2Q ESS 매출 비중 28%",
        fc=OK_BG,
        ec="#86EFAC",
        title_c=GREEN,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        8.1,
        6.45,
        3.7,
        3.25,
        "SDI · SK온",
        "SDI 스텔란티스 JV\n4Q ESS LFP 양산\n2Q 비중 20%\nSK온 조지아 하반기 양산",
        fc=WARN_BG,
        ec=GOLD,
        title_c=ORANGE,
        fs=12,
        bfs=8.8,
    )
    _box(
        ax,
        0.2,
        0.2,
        11.6,
        5.95,
        "밸류체인으로 퍼진다",
        "셀: LG엔솔 · 삼성SDI · SK이노(SK온)\n"
        "PCS: LS ELECTRIC · 효성중공업 · HD현대일렉트릭\n"
        "부품·소재: 신성에스티 · 서진시스템 · 상신이디피\n"
        "LFP: 엘앤에프 · 에코프로비엠 등\n"
        "유휴 EV 라인을 ESS가 흡수 → 가동률·수익성 개선 기대.",
        fc=LIGHT,
        ec="#CBD5E1",
        title_c=NAVY,
        fs=12,
        bfs=9.0,
    )
    _save(fig, "07_ess_shift.png")


def chart_watchlist():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 6.15), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("장 마감 관심 종목  ·  01:25 / 01:26 / 01:30 동일 리스트", loc="left", fontsize=13.0, color=NAVY)

    rows = [
        (0.15, 7.35, "반도체", "삼성전자 · SK하이닉스", BLUE_BG, NAVY2),
        (4.1, 7.35, "소부장", "한미반도체 · 이수페타시스\n원익IPS · 유진테크", LIGHT, NAVY),
        (8.05, 7.35, "로봇", "현대차 · 현대모비스 · 로보티즈", OK_BG, GREEN),
        (0.15, 4.85, "AI 팩토리", "NAVER · SK텔레콤", PURPLE_BG, PURPLE),
        (4.1, 4.85, "전력기기", "HD현대일렉트릭\n효성중공업 · 산일전기", WARN_BG, ORANGE),
        (8.05, 4.85, "조선", "HD현대중공업 · 삼성중공업", BLUE_BG, NAVY2),
        (0.15, 2.35, "바이오", "알테오젠 · 디앤디파마텍", OK_BG, GREEN),
        (4.1, 2.35, "이차전지", "삼성SDI · 엘앤에프", WARN_BG, ORANGE),
        (8.05, 2.35, "신재생 · 재건", "OCI홀딩스\n삼성E&A · HD건설기계", LIGHT, NAVY),
        (0.15, 0.15, "스테이블·가상자산", "NAVER · 카카오페이\n갤럭시아머니트리", PURPLE_BG, PURPLE),
        (4.1, 0.15, "통신장비", "RFHIC · 케이엠더블유", BLUE_BG, NAVY2),
        (8.05, 0.15, "화장품 · 정유", "한국콜마 · 에이피알\nS-OIL", OK_BG, GREEN),
    ]
    for x, y, t, b, fc, c in rows:
        _box(ax, x, y, 3.75, 2.3, t, b, fc=fc, ec="#E5E7EB", title_c=c, fs=11.0, bfs=8.4)
    _save(fig, "08_watchlist.png")


def chart_checkpoints():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.25), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("오늘 이후 체크포인트  ·  숫자는 나왔고, 질과 전환을 본다", loc="left", fontsize=13.0, color=NAVY)

    _box(
        ax,
        0.2,
        5.2,
        5.75,
        4.5,
        "엔비디아",
        "DSO 45→60일 · AR $63.1B\nFCF가 OP를 따라가는가\n금융/보증/리스 관여 규모\nVera Rubin 재고 → 매출\n3Q $108B · 중국 DC 제외",
        fc=BLUE_BG,
        ec="#93C5FD",
        title_c=NAVY2,
        fs=12,
        bfs=9.0,
    )
    _box(
        ax,
        6.15,
        5.2,
        5.65,
        4.5,
        "국내 · 테마",
        "코스피 7,000 시도\n한은 금통위 (8/27)\n한미 HM15275 / HM-500197 L/O\nESS 캐파 전환 · 4Q LFP 양산\n원전 한·미 협력 구체화",
        fc=WARN_BG,
        ec=GOLD,
        title_c=ORANGE,
        fs=12,
        bfs=9.0,
    )
    _box(
        ax,
        0.2,
        0.2,
        11.6,
        4.7,
        "한 줄로 연결",
        "엔비디아 실적은 수요가 살아 있음을 확인했다.  다음 질문은 그 수요를 위해 얼마나 신용을 지느냐.\n"
        "국내에서는 EV 캐즘을 ESS가 보완하고, 한미약품 비만 파이프는 빅파마 검증이 시작됐다.\n"
        "외국인 선물 1조+ 매수.  하락 출발해도 밑받침은 커질 수 있다는 것이 장 마감 코멘트.",
        fc=LIGHT,
        ec="#CBD5E1",
        title_c=NAVY,
        fs=12,
        bfs=9.0,
    )
    _save(fig, "09_checkpoints.png")


def main():
    chart_premarket()
    chart_korea_close()
    chart_nvidia_print()
    chart_nvidia_cash()
    chart_nvidia_segments()
    chart_hanmi()
    chart_ess()
    chart_watchlist()
    chart_checkpoints()


if __name__ == "__main__":
    main()
