#!/usr/bin/env python3
"""8월 26일 Quick 코멘트 시각화 차트."""

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
TEAL = "#0F766E"
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


def chart_us_overnight():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.1), dpi=170, gridspec_kw={"width_ratios": [1.2, 1]})

    ax = axes[0]
    names = ["EWY", "하이닉스 ADR", "마이크론", "엔비디아", "SOX", "나스닥", "S&P500", "다우"]
    vals = [3.5, 2.7, 2.5, 2.2, 1.4, 0.7, 0.3, 0.3]
    colors = [GREEN if v >= 0 else RED for v in vals]
    y = np.arange(len(names))
    ax.barh(y, vals, color=colors, height=0.62, zorder=2)
    ax.set_yticks(y, names)
    ax.axvline(0, color="#CBD5E1", lw=1)
    ax.set_xlabel("%")
    ax.set_title("8/25 미국장  ·  금리↓ 유가↓ 반도체↑", loc="left", color=NAVY, fontsize=13)
    ax.set_xlim(0, 4.3)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)
    for i, v in enumerate(vals):
        ax.text(v + 0.08, i, f"{v:+.1f}%", va="center", ha="left", fontsize=8.5, color=colors[i], fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    rows = [
        (7.7, "미 10년 / 2년", "4.623% (−1.7%)  /  4.176% (−1.4%)", OK_BG, GREEN),
        (5.7, "WTI", "82.4달러  (−3.3%)", OK_BG, GREEN),
        (3.7, "금리인상 확률", "9월 25bp 39.6→31.2%  ·  12월 50bp 0%", WARN_BG, ORANGE),
        (1.7, "읽기", "우호 매크로 + 반도체 반등  ·  실적 전 경계는 남음", BLUE_BG, NAVY2),
    ]
    for y0, t, b, fc, c in rows:
        _box(ax2, 0.15, y0, 9.6, 1.75, t, b, fc=fc, ec="#E5E7EB", title_c=c, fs=11, bfs=9.2)
    ax2.set_title("매크로는 우호  ·  초점은 실적", loc="left", color=NAVY, fontsize=13)
    fig.tight_layout()
    _save(fig, "01_us_overnight.png")


def chart_korea_close():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.7), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("8/26 국내 마감  ·  코스피 +0.97%  /  코스닥 −0.03%", loc="left", fontsize=14, color=NAVY)

    _box(ax, 0.2, 6.55, 3.75, 3.1, "지수",
         "코스피 +0.97%\n120일선 돌파 시도\n소비자신뢰 부진 +\n금리·유가↓ → 하방 완화\n오후 현대차 ID 후 Sell-on",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=9.0)
    _box(ax, 4.15, 6.55, 3.75, 3.1, "오른 곳",
         "원전  한전기술 +13.6%\n두산에너빌리티 +6.3%\n보험  ·  금통위 앞 고금리\n항공·건설  유가↓ + 중동재건",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 8.1, 6.55, 3.7, 3.1, "빠진 곳",
         "방산·해운  중동 긴장 완화\nSK이노베이션 −11.0%\nSKIET 흡수합병\n재무 부담 우려\n현대차 장중 +3.1 → −3.1",
         fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=12, bfs=9.0)

    _box(ax, 0.2, 0.25, 5.75, 5.9, "슈퍼위크 변수",
         "美 7월 PCE + 2Q GDP 수정치\nNVIDIA 실적  →  매출보다 GPM\n8/27 한국은행 금통위\n8/27 Marvell FY2Q\n\nAI 칩 가격↑ → 빅테크 수익성 논란\n순환금융 논란 · $5,000억 플랫폼\n중국향 H200 · Rubin 양산\n→ 삼성·하이닉스 HBM 물량",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)
    _box(ax, 6.15, 0.25, 5.65, 5.9, "투자 시사점",
         "지금은 실적 숫자보다\nNVIDIA의 AI 투자 수익성 메시지\n\n① 이벤트 전 변동성 확대 가능\n② GPM·Rubin·H200 = HBM 방향\n③ 코스피 120일선 안착 = 단기 추세\n④ AI CAPEX 지속 + 메모리 가격 사이클",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.0)
    _save(fig, "02_korea_close.png")


def chart_hyundai_cid():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 6.0), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("현대차 CID  ·  판매량보다 Mix + 원가절감으로 OPM 9%+α", loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 6.7, 3.75, 2.95, "2030 목표 상향",
         "영업이익률  7~8% → 9%+α\n판매목표  555만대 유지\n대외환경 악화에도\n수익성 목표는 공격 상향",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11.5, bfs=8.8)
    _box(ax, 4.15, 6.7, 3.75, 2.95, "이익률의 핵심",
         "미국 부품 현지화 80%\nHEV 비중  25% → 50%\nGenesis HEV · 후륜 HEV\n동일차종 HEV 수익성 > ICE",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.5, bfs=8.8)
    _box(ax, 8.1, 6.7, 3.7, 2.95, "장기 옵션",
         "Boston Dynamics\n2028년 3만대 유지\n2026년 내 생산거점\nAtria AI 광주→새만금",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=11.5, bfs=8.8)

    _box(ax, 0.2, 3.35, 5.75, 3.05, "주가 관점  ·  미국보다 유럽",
         "미국: 이미 M/S 약 6%  ·  SUV·HEV 입증 완료\n유럽: BEV 중심 추가 개선 필요\n4Q26 이후 IONIQ 3 = 유럽 M/S 회복 핵심\n중국 EV 유럽 수익성 둔화 → 탈환 가능성",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.5, bfs=8.8)
    _box(ax, 6.15, 3.35, 5.65, 3.05, "투자포인트 vs 필자 의견",
         "포인트: Mix + 현지화로 수익성 레버리지\n단기 변수: IONIQ 3 유럽 판매/점유율\n필자: 주가 중립  ·  투자 매력은 못 느낌\n(증권사 후가 요약 ≠ 필자 의견)",
         fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=11.5, bfs=8.8)

    _box(ax, 0.2, 0.2, 11.6, 2.85, "자사주 소각 = Sell the news",
         "250만 5,606주  ·  약 7,891억원  ·  이미 보유한 자사주 소각 (신규 매입 아님)\n"
         "TSR 35%+ · 최소배당 1만원 · 분기 2,500원 재확인  ·  시총 대비 1% 미만\n"
         "장중 +3.1% → 13:52 공시 후 −3.1%  ·  종가 40만 8천원 (−3.09%)  ·  기대는 신규 매입+즉시 소각",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.4, bfs=9.0)
    _save(fig, "03_hyundai.png")


def chart_marvell():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.35), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Marvell  ·  AI Networking + Custom XPU 동시 성장  (8/27 FY2Q)", loc="left", fontsize=13.5, color=NAVY)

    steps = [
        (0.2, "Hyperscaler\nAI 투자 확대", BLUE_BG, NAVY2),
        (2.6, "자체 XPU\n(Custom ASIC)", BLUE_BG, NAVY2),
        (5.0, "Amazon Trainium\n+ Google Chip", OK_BG, GREEN),
        (7.4, "Marvell\n설계·개발 수요", WARN_BG, ORANGE),
        (9.8, "FY29 Custom\n~$10B 목표", PURPLE_BG, PURPLE),
    ]
    for x, t, fc, c in steps:
        _box(ax, x, 6.35, 2.15, 3.25, t.split("\n")[0], t.split("\n")[1], fc=fc, ec="#E5E7EB", title_c=c, fs=10.4, bfs=8.6)
    for x in [2.3, 4.7, 7.1, 9.5]:
        ax.annotate("", xy=(x + 0.22, 7.9), xytext=(x - 0.05, 7.9),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY2, lw=1.5))

    _box(ax, 0.2, 3.15, 5.75, 2.9, "Susquehanna",
         "목표가  $230 → $265  상향\n핵심: Networking + Custom XPU\nNVIDIA 의존 낮추는 ASIC 수혜\nAmazon + Google 2대 고객",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 6.15, 3.15, 5.65, 2.9, "숫자",
         "FY28 Custom  $4B\nFY29 Custom  $10B\n성장 가속 구간\n아마존/구글 간접 체크",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)
    _box(ax, 0.2, 0.2, 11.6, 2.65, "왜 NVIDIA 못지않게 중요한가",
         "Custom ASIC은 GPU 시장의 또 다른 축.  마벨 실적은 하이퍼스케일러의 자체 칩 투자 속도와 재상승 모멘텀을 동시에 확인하는 창구.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.5, bfs=9.2)
    _save(fig, "04_marvell.png")


def chart_ai_loop():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.35), dpi=170)

    ax = axes[0]
    cats = ["5%\n$4,550억", "7.5%\n$6,830억", "10%\n$9,100억"]
    vals = [455, 683, 910]
    colors = [NAVY2, TEAL, GOLD]
    x = np.arange(3)
    bars = ax.bar(x, vals, 0.58, color=colors)
    ax.set_xticks(x, cats, fontsize=9.2)
    ax.set_ylabel("십억 달러")
    ax.set_ylim(0, 1100)
    ax.set_title("AI 노출 Payroll $9.1조 의 절감 시나리오", loc="left", color=NAVY, fontsize=12)
    for i, v in enumerate(vals):
        ax.text(i, v + 25, f"{v}", ha="center", fontsize=10, fontweight="bold", color=NAVY)
    ax.axhline(364, color=ORANGE, ls="--", lw=1.1)
    ax.text(2.45, 380, "재투자 $3,640억", fontsize=8, color=ORANGE, ha="right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("누가 $3,640억을 가져가는가", loc="left", color=NAVY, fontsize=12)
    _box(ax2, 0.15, 7.35, 9.6, 2.25, "기준 시나리오",
         "절감 $9,100억 × 40% 재투자 = $3,640억  ≈  500조원\nAI 부가가치 $2.6~4.4조 대비 충분히 감당 가능",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.8)
    _box(ax2, 0.15, 3.85, 9.6, 3.2, "분배 사슬",
         "① AI Cloud  →  ② GPU / ASIC  →  ③ HBM·DRAM\n④ 네트워크 · 스토리지 · 전력 / 데이터센터",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=9.0)
    _box(ax2, 0.15, 0.25, 9.6, 3.3, "메모리의 다음 질문",
         "지속성 = 가치 크기보다 절감액이 CAPEX로 얼마나 전환되나\nAI 가치 → 지불능력 → AI CAPEX → 메모리 Content/가격",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.8)
    fig.tight_layout()
    _save(fig, "05_ai_loop.png")


def chart_kv_cache():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), dpi=170)

    ax = axes[0]
    agents = [1, 2, 4, 8, 16]
    kv = [40, 80, 160, 320, 640]
    colors = [GREEN, GREEN, ORANGE, RED, RED]
    ax.bar([str(a) for a in agents], kv, color=colors, width=0.62, zorder=2)
    ax.axhline(192, color=NAVY2, ls="--", lw=1.4)
    ax.text(4.45, 205, "HBM 192GB", fontsize=8.5, color=NAVY2, ha="right")
    ax.set_xlabel("동시 Agent 수  (각 128K Context)")
    ax.set_ylabel("KV Cache (GB)")
    ax.set_title("Agent 수 2배  →  KV Cache 거의 2배", loc="left", color=NAVY, fontsize=12.5)
    ax.set_ylim(0, 720)
    for i, v in enumerate(kv):
        ax.text(i, v + 14, f"{v}GB", ha="center", fontsize=8.6, fontweight="bold", color=NAVY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#EEF2F8", zorder=0)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("왜 128K = 40GB 인가  (70B 예시)", loc="left", color=NAVY, fontsize=12.5)
    _box(ax2, 0.1, 5.55, 9.7, 4.1, "token당 KV",
         "2 × Layer80 × KV Head8 × Dim128 × BF16(2B)\n= 327,680 bytes  ≈  320KB / token\n× 128K token  ≈  40GB / Agent",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.2, bfs=9.0)
    _box(ax2, 0.1, 0.25, 9.7, 5.0, "주의",
         "특정 모델 구조 + BF16 가정.\n모든 모델이 128K에서 정확히 40GB는 아님.\nHBM에는 Weight · Activation · Runtime도 들어감.\nAgent 4개 = KV 160GB → 남는 HBM은 32GB뿐.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.2, bfs=8.8)
    fig.tight_layout()
    _save(fig, "06_kv_cache.png")


def chart_memory_tiering():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.55), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Memory Tiering  ·  HBM이 DRAM을 대체하는 게 아니다", loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 6.35, 3.75, 3.25, "HBM  192GB",
         "Hot  ·  지금 쓰는 KV\n초고속 · 초고가\nAgent 4개면 거의 포화\n8개면 불가능",
         fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=12.5, bfs=9.0)
    _box(ax, 4.15, 6.35, 3.75, 3.25, "Local DRAM  1~2TB+",
         "Warm  ·  덜 쓰는 KV\nDDR5 용량 계층\nHBM 넘친 State를 받음",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12.5, bfs=9.0)
    _box(ax, 8.1, 6.35, 3.7, 3.25, "CXL  수TB+",
         "Cold / inactive State\nDDR 채널을 안 늘리고\n별도 계층으로 용량 확장",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12.5, bfs=9.0)

    for x in [3.95, 7.9]:
        ax.annotate("", xy=(x + 0.15, 7.9), xytext=(x - 0.08, 7.9),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY2, lw=1.6))

    _box(ax, 0.2, 3.15, 5.75, 2.9, "용량 레이스",
         "Concurrent KV  160 → 480 → 1,000GB\nTotal Agent State  500GB → 2TB\nHBM  192 → 576GB\nState 증가 > HBM 증가",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.5, bfs=8.8)
    _box(ax, 6.15, 3.15, 5.65, 2.9, "병목의 성격",
         "핵심은 대역폭보다 용량\nActive Working Set은 일부\n어디에 저장하느냐가 문제\nHBM 부족 → DRAM·CXL 수요↑",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=11.5, bfs=8.8)
    _box(ax, 0.2, 0.2, 11.6, 2.65, "한 줄",
         "과거: AI 성능↑ → GPU/HBM↑.   Agentic AI: Agent 수↑ + Context↑ + 동시처리↑ → KV↑ → HBM 부족 → 서버 DRAM↑ + CXL↑",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11.5, bfs=9.2)
    _save(fig, "07_memory_tiering.png")


def chart_dpc_churn():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.7), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("1DPC vs 2DPC  ·  그리고 KV Churn이 만드는 트래픽", loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 5.35, 5.75, 4.3, "DPC = DIMMs Per Channel",
         "1DPC  속도·신호 우선   예: DDR5-6400\n2DPC  용량 우선   예: DDR5-5600 이하\n\n12채널 × 1DPC × 128GB = 1.5TB\n12채널 × 2DPC × 128GB = 3.0TB\n채널↑ = 핀·다이·전력·비용·난이도↑\n→ 무한 채널 대신 CXL",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 6.15, 5.35, 5.65, 4.3, "KV Churn + Tool calling",
         "Churn = 기억한 KV를 버리고 새로 넣는 빈도\nTool calling = 외부 도구 호출\n\nFootprint(용량)와 Churn(교체)이\n동시에 높아지면\n용량 + 트래픽이 같이 커진다",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)

    _box(ax, 0.2, 0.2, 11.6, 4.85, "Transfer Overlap Ratio",
         "데이터 이동 중 GPU가 동시에 계산할 수 있는 비율.\n"
         "이동 100ms 중 70ms 계산 = Overlap 70%  →  성능 손실 작음.\n"
         "Overlap 0%  →  GPU Stall (데이터가 올 때까지 GPU가 논다).\n"
         "HBM↔DRAM/CXL 이동량(GB/Call) × 낮은 Overlap = 대역폭 병목.\n"
         "CPU Q가 둔화돼도  채널 × DPC × DIMM용량  때문에 DRAM 수요는 늘 수 있다.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.0)
    _save(fig, "08_dpc_churn.png")


def chart_soulbrain():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.55), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("솔브레인  ·  HF 물량보다 HSN(고선택비 인산계) 성장", loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 6.35, 5.75, 3.25, "왜 인산계인가",
         "3D NAND: Si₃N₄ 선택 제거\n176 → 236 → 300 → 400단\n단수↑ = 공정 중요도·사용량↑\nHSN 시장 약 2,500억\n마진 18~20%+  vs  HF 약 10%",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.8)
    _box(ax, 6.15, 6.35, 5.65, 3.25, "밸류 · LS투자",
         "2028F PER 8.9x  ·  장비사 대비 할인\nTP 50만원  ·  12MF PER 18.9x\n2027~28년 이익 +30% 내외 지속\nWSPM↑ · 가동률↑ · 비메모리 기여",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.8)

    _box(ax, 0.2, 3.05, 5.75, 3.0, "삼성전자",
         "HF   솔브레인 + 이엔에프\nHSN  솔브레인 독점 공급",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.2)
    _box(ax, 6.15, 3.05, 5.65, 3.0, "SK하이닉스",
         "HF   솔브레인 + 이엔에프\nHSN  솔브레인 + LTCAM\nLTCAM은 176단부터 진입\n300단대로 비중 확대",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=9.0)
    _box(ax, 0.2, 0.2, 11.6, 2.55, "투자 포인트",
         "단순 bit growth가 아니라  ① HBM 생산↑ → ② 3D NAND 고단화 → ③ 공정 complexity↑ → ④ 소재 사용량/ASP↑\n직접 경쟁 이엔에프  ·  부분 경쟁 후성·케이씨텍·한솔케미칼",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.5, bfs=9.0)
    _save(fig, "09_soulbrain.png")


def chart_cosmetics_socamm():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.7), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("화장품 선별  ·  SOCAMM (심텍 · 티엘비)", loc="left", fontsize=14, color=NAVY)

    _box(ax, 0.2, 5.2, 5.75, 4.45, "실리콘투  ·  Top Pick",
         "12MF PER 12.3배  ·  유통사로도 저평가\n영국 Boots 비중↑ + iHerb 회복\n3Q GPM 31% 전망\n멕시코 가동 + 브라질 법인\n커버리지 +32.7% vs 코스피 +0.8%",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=9.0)
    _box(ax, 6.15, 5.2, 5.65, 4.45, "APR  ·  고성장",
         "3Q 매출 +100.1% YoY\n브랜드 평균 +22.6%를 크게 상회\n12MF PER 22.1 vs 3사 평균 20.8\n2026 유럽 4,734억 (+321%)\nUlta SKU + 스킨부스터",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)

    _box(ax, 0.2, 0.2, 11.6, 4.7, "SOCAMM  ·  티엘비 수주가 가이던스를 끌어올림",
         "2Q 수주잔고  362억 → 1,318억.  올해 소캠 가이던스  200 → 500 → 700억 (세 차례 상향).  내년 약 1,500억.\n"
         "관련주 = 심텍 + 티엘비.  목표주가 괴리 30%+ · 2027 PER 10배 초반 으로 밸류는 비슷.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.2)
    _save(fig, "10_cosmetics_socamm.png")


def chart_side_themes():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.15), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("환율 · 미국 에너지 PPP · 호르무즈", loc="left", fontsize=14, color=NAVY)

    _box(ax, 0.2, 5.15, 3.75, 4.5, "환율",
         "삼전닉스 150조 푼다\n달러 매도 봇물\n1,340원 선까지\n밀릴 수 있다는 관측\n디지털타임스",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 4.15, 5.15, 3.75, 4.5, "미국 에너지 PPP",
         "에너지·비료 플랜트 등\n투자개발형(PPP) 참여 제안\n8/27 설명회 약 40개사\n1월 김윤덕 장관 방미 때\nDOE가 먼저 제안",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=9.0)
    _box(ax, 8.1, 5.15, 3.7, 4.5, "호르무즈",
         "러 통신: 미·이란 휴전\n호르무즈 자유통항\n트럼프: 미 해군이\n기뢰 모두 제거\n100% 컨펌은 없음",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)
    _box(ax, 0.2, 0.25, 11.6, 4.55, "연결",
         "유가 −3.3%는 항공·건설에 우호, 방산·해운 모멘텀은 약화.\n"
         "8/27 미국 건설사업 설명회는 한미 에너지/원전 1호 프로젝트 기대와 같은 줄기.\n"
         "원/달러 하락은 수출 대형주의 환차익·수급(달러 매도) 이슈로 따로 추적.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.2)
    _save(fig, "11_side_themes.png")


def chart_checkpoints():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.15), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("슈퍼위크 체크포인트  ·  숫자보다 수익성 메시지", loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 5.2, 5.75, 4.45, "NVIDIA에서 볼 것",
         "매출보다 GPM 가이던스\nAI 투자 수익성 논란 해소 여부\n순환금융 · $5,000억 플랫폼\n중국향 H200 출하\nRubin 양산 → HBM 물량",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 6.15, 5.2, 5.65, 4.45, "같은 주 다른 창구",
         "7월 PCE + 2Q GDP 수정치\n8/27 한은 금통위\n8/27 Marvell FY2Q\nCustom $4B→$10B 경로 확인\nIONIQ 3 / 유럽은 4Q26 변수",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)
    _box(ax, 0.2, 0.25, 11.6, 4.6, "메모리로 연결하면",
         "AI가 절감한 비용의 일부가 Cloud → GPU/ASIC → HBM/DRAM으로 흐른다.\n"
         "Agentic AI는 HBM 용량 부족을 DRAM·CXL 수요로 바꾼다.  DRAM은 얼마까지 오를 수 있는가 — 강의에서.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.2)
    _save(fig, "12_checkpoints.png")


def main():
    chart_us_overnight()
    chart_korea_close()
    chart_hyundai_cid()
    chart_marvell()
    chart_ai_loop()
    chart_kv_cache()
    chart_memory_tiering()
    chart_dpc_churn()
    chart_soulbrain()
    chart_cosmetics_socamm()
    chart_side_themes()
    chart_checkpoints()
    print("done", len(list(OUT_DIR.glob("*.png"))), "charts")


if __name__ == "__main__":
    main()
