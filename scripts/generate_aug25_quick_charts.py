#!/usr/bin/env python3
"""8월 25일 Quick 코멘트 시각화 차트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = Path("/workspace/reports/charts")
NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GRAY = "#4B5563"
GREEN = "#166534"
RED = "#991B1B"
TEAL = "#0F766E"
ORANGE = "#C2410C"
PURPLE = "#6B21A8"
LIGHT = "#EEF2F8"
OK_BG = "#E8F5E9"
BAD_BG = "#FDECEA"
WARN_BG = "#FFF8E7"
BLUE_BG = "#E8F1FB"


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


def chart_us_overnight():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.05), dpi=170, gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    names = ["다우", "S&P500", "나스닥", "SOX", "엔비디아", "SKHY ADR", "마이크론", "샌디스크"]
    vals = [0.26, -0.28, -0.77, -2.7, -2.9, -4.9, -5.8, -6.5]
    colors = [GREEN if v >= 0 else RED for v in vals]
    y = np.arange(len(names))
    ax.barh(y, vals, color=colors, height=0.62, zorder=2)
    ax.set_yticks(y, names)
    ax.axvline(0, color="#CBD5E1", lw=1)
    ax.set_xlabel("%")
    ax.set_title("8/24 미국장  ·  금리↓에도 반도체 매도", loc="left", color=NAVY, fontsize=13)
    ax.set_xlim(-7.6, 1.4)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)
    for i, v in enumerate(vals):
        ax.text(v + (0.12 if v >= 0 else -0.12), i, f"{v:+.2f}%", va="center",
                ha="left" if v >= 0 else "right", fontsize=8.5, color=colors[i], fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    rows = [
        (8.2, "미 10년", "4.704%  (−3bp)", OK_BG, GREEN),
        (6.35, "미 30년", "5.234%  (−4bp)", OK_BG, GREEN),
        (4.5, "WTI / Brent", "85.01 / 92.17달러  (−2.35%)", OK_BG, GREEN),
        (2.65, "마이크론 / 샌디스크", "910.43 / 1,493.12달러", BAD_BG, RED),
        (0.8, "SKHY ADR", "155.37달러  (−4.9%)", BAD_BG, RED),
    ]
    for y0, t, b, fc, c in rows:
        _box(ax2, 0.15, y0, 9.6, 1.55, t, b, fc=fc, ec="#E5E7EB", title_c=c, fs=11, bfs=10)
    ax2.set_title("우호 매크로 vs. 반도체 차익실현", loc="left", color=NAVY, fontsize=13)
    fig.tight_layout()
    _save(fig, "01_us_overnight.png")


def chart_korea_rotation():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.6), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("순환매 장세  ·  지수 조정 ≠ 전면 위험회피", loc="left", fontsize=14.5, color=NAVY, pad=6)

    _box(ax, 0.2, 5.7, 3.15, 3.7, "빠진 곳",
         "반도체 갭하락\nAI 밸류체인 조정\n코스닥 바이오·2차전지\n전일 상승분 반납\nYMTC IPO · 메모리 급락\n삼성 환원 후 Sell-on",
         fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=12, bfs=9.2)
    _box(ax, 4.45, 6.35, 3.1, 2.4, "자금 이동",
         "반도체 → 대형주·테마\n코스피 6,600선 근접\n포트폴리오 밸런스 필요\nAI vs Non-AI 노출",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.2)
    _box(ax, 8.65, 5.7, 3.15, 3.7, "들어간 곳",
         "화장품  ·  금융\n건설 / 원전·에너지\n방산\n일부 소부장\n심텍 · HPSP\n실리콘투",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=9.2)

    ax.annotate("", xy=(4.35, 7.4), xytext=(3.45, 7.4),
                arrowprops=dict(arrowstyle="-|>", color=NAVY2, lw=2.0))
    ax.annotate("", xy=(8.55, 7.4), xytext=(7.65, 7.4),
                arrowprops=dict(arrowstyle="-|>", color=NAVY2, lw=2.0))

    _box(ax, 0.2, 0.25, 3.7, 4.95, "한미 투자 1호 → 에너지/원전",
         "다음 달 1호 대미투자 발표\n시장은 에너지 분야 주목\n\n두산에너빌리티  +5%\n대우건설          +7%\n현대건설          +11%\n\n프로젝트 구체화 시\n원전·전력 인프라로\n추가 순환매 가능",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.2, bfs=9.0)
    _box(ax, 4.15, 0.25, 3.7, 4.95, "핵심 변수 2개",
         "① 유동성\n재무부 국채 바이백 확대\nTGA 최대 $9,500억 재원\n장기금리 상승 일부 진정\n→ 증시 하방 완화\n\n② 반도체\n엔비디아 실적 대기\n오늘 조정의 중심 =\n반도체 / AI 밸류체인",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.2, bfs=9.0)
    _box(ax, 8.1, 0.25, 3.7, 4.95, "대외변수 · 충격 제한",
         "미국 → 이란 지원\n금융기관 제재\n시행 시점 불명확\n\n캐나다 → 자동차·부품\n/철강 50% 관세 갈등\n내년 시행\n\n당장 시장 충격은 제한적",
         fc="#F3E8FF", ec="#D8B4FE", title_c=PURPLE, fs=11.2, bfs=9.0)
    _save(fig, "02_korea_rotation.png")


def chart_hynix_ps():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.15), dpi=170)

    ax = axes[0]
    cats = ["기존 체계\n현금 80%", "잠정합의\n현금 40%", "수정 시나리오\n주식 40~50%"]
    cash = [20.8, 10.4, 15.6]
    stock_or_defer = [5.2, 15.6, 10.4]
    x = np.arange(3)
    b1 = ax.bar(x, cash, 0.55, color=NAVY2, label="당장 현금")
    b2 = ax.bar(x, stock_or_defer, 0.55, bottom=cash, color=GOLD, label="주식·이연")
    ax.set_xticks(x, cats, fontsize=9.2)
    ax.set_ylim(0, 32)
    ax.set_ylabel("조원")
    ax.set_title("PS 26조 가정  ·  지급 구성", loc="left", color=NAVY, fontsize=13)
    ax.legend(frameon=False, loc="upper right")
    ax.axhline(26, color="#CBD5E1", ls="--", lw=1)
    ax.text(2.48, 26.4, "PS 재원 26조", fontsize=8, color=GRAY, ha="right")
    for i, (c, s) in enumerate(zip(cash, stock_or_defer)):
        ax.text(i, c / 2, f"{c:.1f}", ha="center", va="center", color="white", fontsize=9, fontweight="bold")
        ax.text(i, c + s / 2, f"{s:.1f}", ha="center", va="center", color=NAVY, fontsize=9, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("노조 부결이 바꾸는 것과 안 바꾸는 것", loc="left", color=NAVY, fontsize=13)
    _box(ax2, 0.15, 6.7, 9.6, 2.85, "영향 없음",
         "진행 중인 40조 자사주 매입·소각\n원칙: FCF의 50% 이상을 환원한다",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11.5, bfs=9.6)
    _box(ax2, 0.15, 3.45, 9.6, 2.9, "영향 가능",
         "3분기 실적발표 때 추가 주주환원 금액\n재협상 시 현금↑ → 직원보상용 자사주 매입↓\n주식 비중 20%p↓ 마다 현금 +5.2조 (환원 예상의 2.7%)",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.5, bfs=9.4)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "투표",
         "반대 50.1%  ·  찬성 7,510 vs 반대 7,535  ·  25표 차\n근소 부결 → 큰 탈 없는 재협상 가능성",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.5, bfs=9.4)
    fig.tight_layout()
    _save(fig, "03_hynix_ps.png")


def chart_honam_ladder():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 6.15), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("미국이 원하는 것 ≠ 호남 철회   ·   타협 가능성 높은 순서", loc="left",
                 fontsize=14, color=NAVY, pad=8)

    items = [
        (8.05, "① 가장 현실적", "미국 내 HBM 후공정/패키징 확대\n현재 SK하이닉스 인디애나 프로젝트 방향", OK_BG, GREEN),
        (6.05, "② 중간", "미국 내 메모리 생산라인 일부 확보\n대규모 DRAM Fab보다 특정 제품·공정 중심", BLUE_BG, NAVY2),
        (4.05, "③ 이원화", "미국 Fab + 한국 Fab 투 트랙\n미국 고객용 물량 / 한국 글로벌 대량생산", WARN_BG, ORANGE),
        (2.05, "④ 기업 선호 · 미국 난색", "한국 생산 중심 유지\n경제성은 최고, 미국 정부가 수용하기 어려움", BAD_BG, RED),
    ]
    for y, t, b, fc, c in items:
        _box(ax, 0.2, y, 7.35, 1.8, t, b, fc=fc, ec="#E5E7EB", title_c=c, fs=11.4, bfs=9.2)
        if y > 2.1:
            ax.annotate("", xy=(3.8, y - 0.02), xytext=(3.8, y - 0.18 + 0.05),
                        arrowprops=dict(arrowstyle="-|>", color="#94A3B8", lw=1.4))

    _box(ax, 7.8, 6.15, 4.0, 3.5, "현재 미국 투자",
         "삼성 Taylor  $17B\n대부분 로직 파운드리\n미국 투자 $37B+ 계획\n≠ 미국 메모리 Fab\n\n하이닉스 인디애나 $4B\nHBM 패키징 + R&D\n2028 가동",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.2, bfs=8.8)
    _box(ax, 7.8, 2.05, 4.0, 3.85, "투자자 결론",
         "단기 악재로 볼 필요 없음\n호남 무산 가능성 낮음\n한국 = 대량생산 중심\n미국 = 고객 근접 +\n패키징 + 일부 메모리\n\n9월 1차 명단 핵심:\n하이닉스 미국 메모리 Fab\n포함 여부",
         fc="#F3E8FF", ec="#D8B4FE", title_c=PURPLE, fs=11.2, bfs=8.8)
    _save(fig, "04_honam_ladder.png")


def chart_nuclear_pipeline():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 4.55), dpi=170)
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title("미국 원전 르네상스  ·  정책 → 실제 프로젝트 전환 (2026 하반기)",
                 loc="left", fontsize=13.5, color=NAVY)

    steps = [
        (0.15, "① 정책", "트럼프\n원전 부흥", OK_BG, GREEN, "✓"),
        (2.1, "② 금융", "$175억\n공급망 대출", OK_BG, GREEN, "✓"),
        (4.05, "③ 사업자", "전력사\n프로젝트 선정", WARN_BG, ORANGE, "예정"),
        (6.0, "④ 선발주", "장납기 기자재\n두산에너빌리티", BLUE_BG, NAVY2, "두산"),
        (7.95, "⑤ FID", "최종\n투자결정", WARN_BG, ORANGE, "예정"),
        (9.9, "⑥ EPC", "실제 건설\n현대건설", BLUE_BG, NAVY2, "현대"),
        (11.85, "⑦ 운영", "장기 정비\n한국 밸류체인", LIGHT, NAVY, "VC"),
    ]
    for x, t, b, fc, c, tag in steps:
        _box(ax, x, 1.55, 1.85, 3.55, t, b + f"\n\n{tag}", fc=fc, ec="#E5E7EB", title_c=c, fs=10.4, bfs=8.6)
    for x in [1.95, 3.9, 5.85, 7.8, 9.75, 11.7]:
        ax.annotate("", xy=(x + 0.12, 3.3), xytext=(x - 0.08, 3.3),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY2, lw=1.5))
    ax.text(0.2, 0.35,
            "핵심: FID를 기다리지 않고 장납기 기자재(Long Lead Equipment) 발주가 먼저 나올 수 있다.  AP1000 최대 10기.",
            fontsize=9.4, color=GRAY)
    _save(fig, "05_nuclear_pipeline.png")


def chart_tga_critique():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.7), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("TGA 바이백  ·  QE가 아니라 시장 안정화 신호", loc="left", fontsize=14, color=NAVY)

    _box(ax, 0.2, 6.55, 5.7, 3.05, "무엇인가",
         "TGA = 재무부의 Fed 현금계좌  ≈ $9,500억\n이미 가진 현금으로 장기국채를 사\n금리를 낮추고 유동성 압력을 완화\n8/19 확대 발표만으로 금리 즉각 반응",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.2)
    _box(ax, 6.15, 6.55, 5.65, 3.05, "BofA 프레이밍: QE5?",
         "Fed QE가 아님. 대차 확대 ×\n정책당국이 duration을 직접 관리\n시작했다는 라벨에 가깝다\nTreasury Twist에 더 가깝다",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.2)

    critiques = [
        (0.2, 3.3, "① 신규 유동성?", "TGA 현금 사용.\n돈을 새로 찍지 않음."),
        (3.15, 3.3, "② 규모", "회당 수십억$ vs\n연방부채 $40조+"),
        (6.1, 3.3, "③ 원인", "적자·인플레·텀프리미엄은\n바이백만으로 안 풀림"),
        (9.05, 3.3, "④ 금융억압", "정부가 국채 가격을\n관리한다는 비판"),
    ]
    for x, y, t, b in critiques:
        _box(ax, x, y, 2.75, 2.85, t, b, fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=10.6, bfs=8.5)

    _box(ax, 0.2, 0.2, 11.6, 2.75, "추적 포인트  ·  바이백 자체보다",
         "TGA 잔액 + bill issuance를 같이 볼 것.  바이백을 확대하는데 30년 금리가 안 떨어지고 달러만 약해지면\n"
         "정책이 채권시장을 안정시킨 게 아니라 fiscal risk premium을 키운 신호일 수 있다.\n"
         "그래도 임계점(국채금리 급등)을 막는 안정화 조치는 주식시장에 단기적으로 긍정적.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.4, bfs=9.2)
    _save(fig, "06_tga_framework.png")


def chart_genius_clarity():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.35), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("GENIUS = 돈의 레일   ·   CLARITY = 교통법규", loc="left", fontsize=14, color=NAVY)

    _box(ax, 0.2, 3.35, 5.7, 6.25, "GENIUS Act  ·  스테이블코인 법",
         "대상: USDC · USDT 등 결제 스테이블\n준비자산 1:1  ·  환매 · 공시 · 발행자 규제\n2025.7.18 법제화 완료\n\n투자 함의\n스테이블 성장 → T-bill 수요↑\n현재 시장 약 $3,000억\nCiti 2030 약 $4조\n발행사 미 국채 관련 약 $1,776억\n자문위: 추가 수요 최대 $9,000억",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 6.15, 3.35, 5.65, 6.25, "CLARITY Act  ·  시장구조 법",
         "대상: BTC · ETH · 토큰 전반\nSEC vs CFTC 관할 명확화\nDigital Commodity 개념\n거래소·브로커 CFTC 등록\n2026 의회 심의 중\n\n투자 함의\nCoinbase · 거래소 · DeFi에 더 직접적\n규제 불확실성 해소 →\n크립토 시장 확대 →\n스테이블 사용 확대",
         fc="#F3E8FF", ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=9.0)
    _box(ax, 0.2, 0.2, 11.6, 2.85, "한계 (과장하지 말 것)",
         "스테이블이 미국 국채 문제를 해결한다 = 아직 과장.  발행사 국채 보유는 전체의 1% 미만.\n"
         "은행예금·MMF에서 이동이면 순수 신규 수요가 아닐 수 있음.  금리에 의미 있으려면 시장이 훨씬 더 커져야 함.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.5, bfs=9.2)
    _save(fig, "07_genius_clarity.png")


def chart_sds_robot():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.55), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("삼성SDS  ·  로봇을 만드는 게 아니라 공장 로봇의 OS", loc="left", fontsize=14, color=NAVY)

    stack = [
        (0.2, 7.15, "ERP", "무엇을 얼마나 만들 것인가", LIGHT),
        (0.2, 5.15, "MES", "공장에서 어떻게 생산할 것인가", BLUE_BG),
        (0.2, 3.15, "오케스트레이션", "어떤 로봇이 어떤 일을 할 것인가  ·  SDS", WARN_BG),
        (0.2, 1.15, "로봇", "실제 작업  ·  삼성전자 · 레인보우로보틱스", OK_BG),
    ]
    for x, y, t, b, fc in stack:
        _box(ax, x, y, 5.5, 1.75, t, b, fc=fc, ec="#E5E7EB", title_c=NAVY, fs=12, bfs=9.2)
        if y > 1.2:
            ax.annotate("", xy=(2.8, y - 0.02), xytext=(2.8, y - 0.22),
                        arrowprops=dict(arrowstyle="-|>", color=NAVY2, lw=1.4))

    _box(ax, 6.0, 5.35, 5.8, 4.25, "강세 시나리오 2033~35",
         "삼성 제조 사이트 약 35곳\n× 사이트당 휴머노이드 2,500대\n= 약 8.8만 대\n\nSaaS 약 8,750억원/년\n총매출 약 2.5조 / OP 약 5,000억\n사업가치 약 11조원\nvs 컨센 14.2조 / 8,279억의 18% · 60%",
         fc="#F3E8FF", ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=9.0)
    _box(ax, 6.0, 1.15, 5.8, 3.9, "다음 확인할 3가지",
         "① 구미 19조에서 SDS 역할·투자액\n② 하반기 휴머노이드 투입 팹·공정·대수\n③ Toyota 레퍼런스 이후 외부 고객",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.2)
    _save(fig, "08_sds_stack.png")


def chart_ai_funding():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.2), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("AI 조달  ·  엔비디아는 앱까지, 소프트뱅크는 레버리지까지", loc="left",
                 fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 5.15, 5.7, 4.45, "엔비디아 → 퍼플렉시티",
         "기업가치 $300억+ (약 42조+)\n논의 중 투자\n연환산 매출 $2.5억 미만 → $7.5억+\n검색 → AI 검색 → AI Agent\n(Perplexity Computer)\n별도: Poolside 약 $10억 / EV $120억\nGPU → 모델 → Agent → 서비스 선점",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 6.15, 5.15, 5.65, 4.45, "소프트뱅크 1조엔 개인채",
         "약 $63억 / 8.7조원  ·  7년  4.3~4.9%\n9/4 가격결정  ·  일본 개인채 사상 최대\n용도: AI 투자 + 기존 채권 상환\nOpenAI 추가 $300억 (4·7·10월 각 $100억)\n누적 약 $646억 · 지분 약 13%\n3월 브리지 파이낸싱 $400억도 확보",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)

    _box(ax, 0.2, 0.25, 11.6, 4.5, "자본의 흐름",
         "소프트뱅크 채권·브리지  →  OpenAI $646억  →  AI 데이터센터 / 인프라  →  GPU · HBM 수요\n"
         "엔비디아는 단순 GPU 판매를 넘어 퍼플렉시티·Poolside 등 애플리케이션 승자까지 지분으로 붙잡으려 한다.\n"
         "수요는 실물로 보이지만, 약한 고리는 조달(레버리지)이다.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.4)
    _save(fig, "09_ai_funding.png")


def chart_week_checkpoint():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 4.7), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("8/26이 단기 방향의 변곡점  ·  엔비디아 = 실물수요, PCE = 금리",
                 loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 5.2, 5.7, 4.4, "엔비디아 실적에서 볼 것",
         "실적 + 데이터센터 성장률\n차기 분기 가이던스\nBlackwell / Rubin 수요\nHBM 공급\n\n이 조정이 단순 차익실현인지\nAI 투자 우려의 시작인지 판별",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.2)
    _box(ax, 6.15, 5.2, 5.65, 4.4, "7월 PCE에서 볼 것",
         "Fed 금리인하 기대 확인\n유가 하락은 PCE에 우호적\n\n금리↓ 유가↓ 는 원래 기술주 우호\n그런데 반도체가 더 빠졌다\n= 초점이 실적/CAPEX로 이동",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.2)
    _box(ax, 0.2, 0.25, 5.7, 4.55, "9월",
         "대미 투자 프로젝트 1차 명단\n어떤 반도체 생산능력을\n미국에 줄 것인가\n하이닉스 미국 메모리 Fab 포함 여부\n한미 1호 = 에너지/원전 주목",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=9.2)
    _box(ax, 6.15, 0.25, 5.65, 4.55, "3분기 실적시즌",
         "하이닉스 추가 주주환원 윤곽\n재협상 현금/주식 비율\n삼성·하이닉스 IR 구체성\n(자사주 규모·시기)",
         fc="#F3E8FF", ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=9.2)
    _save(fig, "10_checkpoints.png")


def chart_governance():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 4.35), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.set_title("지분율 올려야 하는 하닉  vs  지분 넘치면 안 되는 삼전", loc="left",
                 fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 0.3, 5.7, 7.3, "SK하이닉스",
         "SK스퀘어는 지주사 → 자회사 20% 이상\nADR 발행 후 지분율 20% 턱밑\n자사주 매입·소각 = 발행주식 ↓\n→ 지분율 자연 상승 (일석이조)\n\n오너 일가 직접 지분 사실상 전무\n배당 확대가 오너 현금흐름에 미미",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=13, bfs=9.4)
    _box(ax, 6.15, 0.3, 5.65, 7.3, "삼성전자",
         "금산법: 금융사 비금융 지분 10% 초과 금지\n삼성생명 8.51% + 화재 1.49% = 10.00%\n대규모 소각 시 10% 초과 → 매도 부담\n\n이재용 1.67% 등 오너 직접 지분\n배당 확대 = 오너 현금 유입",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=13, bfs=9.4)
    _save(fig, "11_governance.png")


def main():
    chart_us_overnight()
    chart_korea_rotation()
    chart_hynix_ps()
    chart_honam_ladder()
    chart_nuclear_pipeline()
    chart_tga_critique()
    chart_genius_clarity()
    chart_sds_robot()
    chart_ai_funding()
    chart_week_checkpoint()
    chart_governance()
    print("done", len(list(OUT_DIR.glob("*.png"))), "charts")


if __name__ == "__main__":
    main()
