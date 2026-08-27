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
    ax.set_title("실적 이후 체크포인트  ·  숫자는 나왔다, 질과 수요 저변을 본다", loc="left", fontsize=13.2, color=NAVY)

    _box(ax, 0.2, 5.2, 5.75, 4.45, "엔비디아 이후",
         "FY28 +70% 공급 확신 vs 시장 +40%대\nDSO 45→60일 · AR $63.1B\n금융/보증/리스 관여 규모\nVera Rubin 재고 → 매출 전환\n3Q 가이던스 중국 DC 제외",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 6.15, 5.2, 5.65, 4.45, "같은 주 다른 창구",
         "8/27 한은 금통위\n8/27 Marvell FY2Q\n코스피 7,000 시도\nKimi K3 토큰 사용량·계약\nIONIQ 3 / 유럽은 4Q26",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)
    _box(ax, 0.2, 0.25, 11.6, 4.6, "메모리로 연결하면",
         "Compute = 매출.  2.8T 모델 추론은 GPU뿐 아니라 HBM·DRAM.  Agentic KV + 오픈모델 Cloud 유통이 수요 저변.\n"
         "관심은 수요가 꺾이는가가 아니라, 엔비디아가 그 수요를 위해 얼마나 신용·자본을 제공하는가.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.2)
    _save(fig, "12_checkpoints.png")


def chart_nvidia_print():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.25), dpi=170, gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    names = ["전사 매출", "Non-GAAP EPS", "Data Center", "Hyperscale", "AI Clouds 등", "3Q 가이던스"]
    beats = [4.3, 6.2, 3.1, 11.6, -6.1, 3.0]
    colors = [GREEN if v >= 0 else RED for v in beats]
    y = np.arange(len(names))
    ax.barh(y, beats, color=colors, height=0.58, zorder=2)
    ax.axvline(0, color="#CBD5E1", lw=1)
    ax.set_yticks(y, names)
    ax.set_xlabel("컨센서스 대비 %")
    ax.set_title("FY27 2Q vs FactSet  ·  매출 +4.3%  /  EPS +6.2%  (필자 정정 +18%는 별도)", loc="left", color=NAVY, fontsize=10.6)
    ax.set_xlim(-8.5, 14)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)
    notes = ["$96.22 vs $92.27B", "$2.22 vs $2.09", "$89.02 vs $86.33B", "$48.71 vs $43.63B", "$40.31 vs $42.94B", "$108 vs $104.86B"]
    for i, (v, n) in enumerate(zip(beats, notes)):
        ax.text(v + (0.25 if v >= 0 else -0.25), i, f"{v:+.1f}%", va="center",
                ha="left" if v >= 0 else "right", fontsize=8.2, color=colors[i], fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("자신감 뿜뿜  ·  세 가지 메시지", loc="left", color=NAVY, fontsize=12)
    _box(ax2, 0.1, 6.7, 9.7, 2.95, "① CAPEX의 질",
         "인프라 → 서비스/생산성 → 실제 매출\n토큰이 생산적이고 수익성 있다.  컴퓨트 = 매출",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.8)
    _box(ax2, 0.1, 3.45, 9.7, 2.95, "② 수요 저변",
         "빅테크 + Frontier 연구소 + 스타트업\n+ 오픈모델 + Physical AI",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.8)
    _box(ax2, 0.1, 0.2, 9.7, 2.95, "③ Vera Rubin",
         "Blackwell 공급 확대에서 차세대 양산으로\nFY28 +70%를 현 공급으로 confidently",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.8)
    fig.tight_layout()
    _save(fig, "13_nvidia_print.png")


def chart_nvidia_cash():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.35), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("현금흐름은 약했다  ·  영업 문제가 아니라 WC + Cash Tax", loc="left", fontsize=13.2, color=NAVY)

    _box(ax, 0.2, 5.25, 3.75, 4.4, "FCF / OCF",
         "OCF  $24.08B\n전분기 $50.34B에서 감소\nFCF  $21.34B\n전분기 $48.55B에서 감소\nYoY는 둘 다 증가",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)
    _box(ax, 4.15, 5.25, 3.75, 4.4, "매출채권",
         "AR  $63.1B\nDSO  45일 → 60일\nIG 고객 다분기 계약\n지불기간 연장\n매출은 잡히고 현금은 뒤로",
         fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=12, bfs=9.0)
    _box(ax, 8.1, 5.25, 3.7, 4.4, "재고 · 환원",
         "재고  $25.8B → $31.6B\n3Q Vera Rubin 준비\n2Q 환원 약 $26.0B\n잔여 매입 한도  $99.0B",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 0.2, 0.2, 11.6, 4.75, "그래서 다음에 볼 것",
         "재무 위기나 현금 부족으로 보긴 어렵다.  다만 FCF가 영업이익을 못 따라가면 이익의 질 논란.\n"
         "GPU 수요가 안 꺾이면, 관심은 엔비디아가 수요 실현을 위해 얼마나 많은 신용·자본·리스크를 지느냐.\n"
         "일부 AI 클라우드 계약의 제3자 매출 공유 = 사업모델 확장 가능성.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.6, bfs=9.0)
    _save(fig, "14_nvidia_cash.png")


def chart_afterhours():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.1), dpi=170, gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    names = ["네비우스", "코어위브", "하이닉스 ADR", "마이크론", "샌디스크", "씨게이트", "WD 시간외"]
    vals = [6.3, 5.0, 4.2, 3.6, 3.6, 3.0, 2.7]
    y = np.arange(len(names))
    ax.barh(y, vals, color=GREEN, height=0.62, zorder=2)
    ax.set_yticks(y, names)
    ax.set_xlabel("%  ·  대략 수준")
    ax.set_title("시간외  ·  엔비디아 경쟁주 제외, 메모리·네오클라우드·스토리지", loc="left", color=NAVY, fontsize=11.2)
    ax.set_xlim(0, 7.6)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)
    for i, v in enumerate(vals):
        ax.text(v + 0.12, i, f"{v:.1f}%대", va="center", fontsize=8.4, color=GREEN, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("실적 전 본장 vs 실적 후", loc="left", color=NAVY, fontsize=12)
    _box(ax2, 0.1, 5.35, 9.7, 4.3, "실적 전 눈치 (06:41)",
         "다우 −0.21 / S&P −0.02 / 나스닥 −0.08\n10년 4.649%  ·  WTI $81  ·  원/달러 1,384\n엔비디아 −1.59  ·  EWY −0.54\n씨게이트 본장 +3.01  · ARM +3.93",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.8)
    _box(ax2, 0.1, 0.25, 9.7, 4.8, "실적 후",
         "엔비디아 시간외 약 +4%\n메모리·네오클라우드 동반 상승\n국내: 코스피 7,000 시도 가능\nPCE 코어는 예상 충족, 헤드라인 소폭 상회",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.8)
    fig.tight_layout()
    _save(fig, "15_afterhours.png")


def chart_kimi():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.55), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Kimi K3  ·  중국 모델 × 미국 Cloud  ·  협상 초기, 규모 미확정", loc="left", fontsize=13.2, color=NAVY)

    _box(ax, 0.2, 6.35, 3.75, 3.25, "① Open-weight ≠ 무료",
         "가중치 공개여도 2.8T 직접 운영은\n막대한 GPU·인프라 비용\n현실: Azure/AWS/GCP 호스팅\n사용량 과금",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.4, bfs=8.8)
    _box(ax, 4.15, 6.35, 3.75, 3.25, "② 최대 30% Rev Share",
         "Cloud가 GPU 임대료만 받는 게 아님\n모델 사용의 경제적 가치를\nMoonshot과 공유\n모델 → API/Cloud → 매출",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11.4, bfs=8.8)
    _box(ax, 8.1, 6.35, 3.7, 3.25, "③ Big Tech에도 매력",
         "성능 + 낮은 가격 → 고객 유입\nCloud는 추가 토큰 수요\n중국 모델 ↔ 미국 Cloud\n이해관계 일치 구간",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=11.4, bfs=8.8)
    _box(ax, 0.2, 0.2, 11.6, 5.85, "메모리 시사점",
         "2.8T 파라미터는 추론에서도 막대한 용량·대역폭.  글로벌 Token 사용량이 늘면 GPU뿐 아니라 HBM·DRAM.\n"
         "다만 지금은 협상 초기.  계약 성사와 규모는 미확정.  핵심 추적은 실제 글로벌 Token 사용량.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.2)
    _save(fig, "16_kimi_k3.png")


def chart_kv_formula():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.7), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("왜 128K Context ≈ 40GB 인가  ·  KV = 2 × Layer × Head × Dim × Context × Bytes", loc="left",
                 fontsize=12.4, color=NAVY)

    items = [
        (0.15, "Layer 80", "처리 단계 80번\nLayer마다 KV를 쌓음", BLUE_BG, NAVY2),
        (2.5, "KV Head 8", "관심 영역 8개\nHead↑ → KV↑", OK_BG, GREEN),
        (4.85, "Dim 128", "Head 하나 그릇\n128개 숫자", WARN_BG, ORANGE),
        (7.2, "BF16 2B", "숫자 하나 = 2Byte\nBrain Float 16", LIGHT, NAVY),
        (9.55, "128K Ctx", "약 131,072 token\n한 번에 참고하는 문맥", PURPLE_BG, PURPLE),
    ]
    for x, t, b, fc, c in items:
        _box(ax, x, 5.55, 2.2, 4.1, t, b, fc=fc, ec="#E5E7EB", title_c=c, fs=11.2, bfs=8.6)

    _box(ax, 0.15, 0.2, 11.7, 5.05, "도서관으로 보면",
         "K = 어디를 찾아볼 것인가 (책의 색인/검색어)    V = 찾아낸 실제 정보 (책의 내용)\n"
         "KV Cache = 검색을 빨리 하려고 만들어 둔 색인 + 관련 정보.\n"
         "2(K+V) × 80 × 8 × 128 × 128K × 2B  ≈  40GB.  긴 Context를 80개 Layer에서 저장하기 때문에 커진다.\n"
         "워드파일: <왜 128K Context가 약 40GB의 KV Cache가 되는가>",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _save(fig, "17_kv_formula.png")


def chart_dc_history():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.15), dpi=170)
    labels = ["FY25\nQ1", "Q2", "Q3", "Q4", "FY26\nQ1", "Q2", "Q3", "Q4", "FY27\nQ1", "Q2"]
    hs = [10.93, 13.42, 15.64, 19.95, 22.26, 24.17, 35.14, 42.21, 43.05, 48.71]
    acie = [11.63, 12.85, 15.14, 15.63, 16.85, 16.93, 16.08, 20.10, 32.20, 40.31]
    x = np.arange(len(labels))
    ax.bar(x, hs, 0.62, color=NAVY2, label="Hyperscale")
    ax.bar(x, acie, 0.62, bottom=hs, color=GOLD, label="ACIE")
    ax.set_xticks(x, labels, fontsize=8.4)
    ax.set_ylabel("십억 달러")
    ax.set_title(_esc("Data Center  ·  Hyperscale + ACIE  =  $89.0B  (YoY +117%, QoQ +$13.8B)"), loc="left", color=NAVY, fontsize=12.2)
    ax.legend(frameon=False, loc="upper left")
    ax.set_ylim(0, 105)
    ax.axhline(89.02, color="#CBD5E1", ls="--", lw=1)
    ax.text(9.45, 91.2, "2Q DC $89.0B", fontsize=8, color=GRAY, ha="right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    _save(fig, "18_dc_history.png")


def chart_commitments():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.35), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title(_esc("미래 약정 $366B + 추가 $56B  ·  공급 약정만 $119B → $279B (대부분 메모리)"), loc="left", fontsize=12.4, color=NAVY)

    _box(ax, 0.15, 5.25, 3.8, 4.4, "공급·캐파  $279B",
         "전분기 $119B에서 급증\n대부분 메모리 조달\n잔여 FY27 $92 / 28 $87\n29년 $88  ·  이후 소액",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)
    _box(ax, 4.15, 5.25, 3.75, 4.4, "인프라 약정",
         "클라우드 서비스 $29B\n미개시 DC 리스 $25B\n지분 투자 $25B\n설비투자 $8B",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.0)
    _box(ax, 8.1, 5.25, 3.7, 4.4, "추가 약정  $56B",
         "AI 클라우드 계약 $36B\n제3자용 DC 리스 $20B\n선매출 + 조건 충족 시\n제3자 매출 공유",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=9.0)
    _box(ax, 0.15, 0.2, 11.65, 4.75, "읽는 법",
         "공급 $279B는 ‘앞으로 살 부품’이고, 그 한가운데가 메모리.  한국 삼성·하이닉스 HBM/DRAM 물량과 직결.\n"
         "AI 클라우드 $36B는 인프라를 먼저 팔고, 조건이 되면 네오클라우드의 제3자 매출까지 나누는 구조.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.0)
    _save(fig, "19_commitments.png")


def chart_guarantees():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.45), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title(_esc("보증 $108.5B  ·  SB Energy 오하이오 4.25GW = OpenAI 전용 NVIDIA 사이트"), loc="left", fontsize=12.6, color=NAVY)

    _box(ax, 0.15, 5.35, 5.75, 4.3, "PORTS-Pike (오하이오)",
         "4.25GW  ·  20년 리스  ·  임차인 OpenAI\n보증 한도 $105B  ·  조건 충족 시 단계 발효\n최초 ready는 FY2029\n+3.8GW 추가 옵션\n세대당 ≈ 150만 GPU\n세대당 NVIDIA 매출 ≈ $150~200B",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=8.8)
    _box(ax, 6.15, 5.35, 5.65, 4.3, "그 외 보증 · 부채",
         "AI 클라우드 토지·전력·셸 $3.5B\n보증 합계 $108.5B\n2Q 무담보 시니어노트 $25.0B 발행\n장기부채 $7.5B → $32.4B\n현금+단기채권 $56.6B",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.8)
    _box(ax, 0.15, 0.2, 11.65, 4.85, "핵심",
         "수요가 밸런스시트를 앞지르니, 엔비디아가 토지·전력·셸을 보증하고 금융 플랫폼($5,000억)까지 짠다.\n"
         "20년 동안 같은 사이트에서 인프라를 여러 번 교체하면 매출이 반복된다.  다만 보증이 현실화되면 우발부채.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.0)
    _save(fig, "20_guarantees.png")


def chart_gaap_nongaap():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.15), dpi=170)

    ax = axes[0]
    cats = ["GAAP", "Non-GAAP"]
    ni = [59.69, 53.95]
    bars = ax.bar(cats, ni, 0.52, color=[NAVY2, GOLD])
    ax.set_ylabel("순이익 (십억 달러)")
    ax.set_ylim(0, 78)
    ax.set_title(_esc("순이익  ·  GAAP $59.7B > Non-GAAP $54.0B"), loc="left", color=NAVY, fontsize=11.2)
    for bar, v in zip(bars, ni):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.2, f"{v:.1f}", ha="center", fontsize=10, color=NAVY, fontweight="bold")
    ax.text(0.5, 0.07, _esc("희석 EPS   GAAP $2.46   /   Non-GAAP $2.22"), transform=ax.transAxes, ha="center", fontsize=9.2, color=GRAY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("왜 GAAP 순이익 QoQ는 +2%뿐인가", loc="left", color=NAVY, fontsize=12)
    _box(ax2, 0.15, 5.35, 9.6, 4.3, "지분증권 평가이익",
         "2Q $7.8B  ·  1Q $15.9B\nGAAP 기타이익의 거의 전부\nNon-GAAP는 이 항목을 제외\nFY27부터 SBC도 Non-GAAP에 포함",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.4, bfs=8.8)
    _box(ax2, 0.15, 0.25, 9.6, 4.8, "읽을 숫자",
         "영업 체력 = Non-GAAP OP $64.0B / EPS $2.22\n재무 체력 = FCF $21.3B + 부채 $25B 발행\n투자 체력 = 유가증권·비상장 $94B",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.4, bfs=8.8)
    fig.tight_layout()
    _save(fig, "21_gaap_nongaap.png")


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
    chart_nvidia_print()
    chart_nvidia_cash()
    chart_afterhours()
    chart_kimi()
    chart_kv_formula()
    chart_dc_history()
    chart_commitments()
    chart_guarantees()
    chart_gaap_nongaap()
    print("done", len(list(OUT_DIR.glob("*.png"))), "charts")


if __name__ == "__main__":
    main()
