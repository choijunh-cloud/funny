#!/usr/bin/env python3
"""NVIDIA FY27 2Q 컨콜 분석 차트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT_DIR = Path("/workspace/reports/nvda-q2-call/charts")
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


def chart_print():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.15), dpi=170, gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    cats = ["매출", "DC", "Hyperscale", "ACIE", "3Q 가이던스"]
    actual = [96.22, 89.02, 48.71, 40.31, 108.0]
    cons = [92.27, 86.33, 43.63, 42.94, 104.86]
    x = np.arange(len(cats))
    ax.bar(x - 0.18, cons, 0.34, color="#CBD5E1", label="컨센")
    ax.bar(x + 0.18, actual, 0.34, color=NAVY2, label="실제/가이드")
    ax.set_xticks(x, cats, fontsize=8.8)
    ax.set_ylabel("십억 달러")
    ax.set_ylim(0, 125)
    ax.set_title("숫자 자체는 이미 강했다", loc="left", color=NAVY, fontsize=13)
    ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for i, (a, c) in enumerate(zip(actual, cons)):
        beat = a - c
        color = GREEN if beat >= 0 else RED
        ax.text(i + 0.18, a + 2.2, f"{beat:+.1f}", ha="center", fontsize=8, fontweight="bold", color=color)
    ax.grid(axis="y", color="#EEF2F8", zorder=0)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("컨콜이 표에 더한 세 문장", loc="left", color=NAVY, fontsize=13)
    _box(ax2, 0.15, 6.85, 9.6, 2.85, "1. 수요 100%  ·  공급 70%",
         "고객 포캐스트는 내년 더블.\n현 공급으로 confidently +70%.",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11.2, bfs=8.8)
    _box(ax2, 0.15, 3.55, 9.6, 2.95, "2. GPM을 공개 리셋",
         "Q3 74%±50bp → Q4 71–72%\nFY28 72–73%  (Q1 가격전가)",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.2, bfs=8.8)
    _box(ax2, 0.15, 0.2, 9.6, 3.0, "3. 순환금융을 직접 받아침",
         "Some will call this circular.\nWe see it differently.",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=11.2, bfs=8.8)
    fig.tight_layout()
    _save(fig, "01_print.png")


def chart_dc_mix():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), dpi=170)

    ax = axes[0]
    labels = ["Hyperscale", "ACIE"]
    qoq = [13, 25]
    yoy = [102, 138]
    x = np.arange(2)
    ax.bar(x - 0.18, qoq, 0.34, color=NAVY2, label="QoQ %")
    ax.bar(x + 0.18, yoy, 0.34, color=GOLD, label="YoY %")
    ax.set_xticks(x, [f"{n}\n$48.7B / $40.3B" for n in labels], fontsize=9)
    ax.set_ylabel("%")
    ax.set_ylim(0, 165)
    ax.set_title("DC $89.0B  ·  ACIE가 순증의 엔진", loc="left", color=NAVY, fontsize=12.5)
    ax.legend(frameon=False, fontsize=8.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for i, (q, y) in enumerate(zip(qoq, yoy)):
        ax.text(i - 0.18, q + 4, f"{q}%", ha="center", fontsize=8.5, fontweight="bold", color=NAVY2)
        ax.text(i + 0.18, y + 4, f"{y}%", ha="center", fontsize=8.5, fontweight="bold", color=ORANGE)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("왜 시장이 ACIE를 못 보나", loc="left", color=NAVY, fontsize=12.5)
    _box(ax2, 0.15, 6.7, 9.6, 2.95, "하이퍼스케일 = 절반만",
         "커스텀 칩·단일 칩 구매가 보이는 쪽.\nQ3는 ACIE가 순증, HS는 Q4 재가속.",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.8)
    _box(ax2, 0.15, 3.4, 9.6, 2.95, "ACIE = 공장 플랫폼",
         "네오클라우드·소버린·엔터프라이즈.\n커스텀 실리콘 의사가 없는 고객.",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.8)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "젠슨",
         "ACIE는 연 100% 성장.\n시간이 지나면 클라우드보다 커질 수 있다.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.8)
    fig.tight_layout()
    _save(fig, "02_dc_mix.png")


def chart_gw_tam():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), dpi=170)

    ax = axes[0]
    gens = ["범용 CPU\n(무어)", "Hopper", "Grace\nBlackwell", "Vera Rubin", "그 다음"]
    vals = [4, 18, 25, 40, 55]
    colors = ["#94A3B8", NAVY2, TEAL, GOLD, PURPLE]
    x = np.arange(5)
    ax.bar(x, vals, 0.58, color=colors)
    ax.set_xticks(x, gens, fontsize=8.6)
    ax.set_ylabel("십억 달러 / GW")
    ax.set_ylim(0, 68)
    ax.set_title("GW당 매출 기회  ·  목표가 무한대", loc="left", color=NAVY, fontsize=12.5)
    for i, v in enumerate(vals):
        label = f"{v}" if i < 4 else "더 높음"
        ax.text(i, v + 1.6, label, ha="center", fontsize=9, fontweight="bold", color=NAVY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#EEF2F8", zorder=0)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("Vera Rubin이 $40B/GW인 이유", loc="left", color=NAVY, fontsize=12.5)
    _box(ax2, 0.15, 6.85, 9.6, 2.85, "풀스택",
         "Vera CPU + Rubin GPU + NVLink\nIB/이더넷 + Groq LPU",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.8)
    _box(ax2, 0.15, 3.55, 9.6, 2.95, "생산성",
         "GB Ultra 대비 처리량/MW 30배\n토큰 비용 1/35",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.8)
    _box(ax2, 0.15, 0.2, 9.6, 3.0, "고객 논리",
         "같은 땅·전력에 더 많은 컴퓨트.\nROI < 1년 이라는 언급까지.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.8)
    fig.tight_layout()
    _save(fig, "03_gw_tam.png")


def chart_margin():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), dpi=170)

    ax = axes[0]
    xs = np.arange(4)
    mid = [75.0, 74.0, 71.5, 72.5]
    lo = [75.0, 73.5, 71.0, 72.0]
    hi = [75.0, 74.5, 72.0, 73.0]
    labels = ["2Q\n실제", "3Q\n가이드", "4Q\n바닥", "FY28\n안착"]
    ax.fill_between(xs, lo, hi, color="#FDE68A", alpha=0.55)
    ax.plot(xs, mid, "o-", color=ORANGE, lw=2.2, ms=7)
    ax.set_xticks(xs, labels, fontsize=9)
    ax.set_ylabel("%")
    ax.set_ylim(69.5, 76.2)
    ax.set_title("GPM 경로  ·  메모리가 회사 마진을 리셋", loc="left", color=NAVY, fontsize=12.5)
    for i, (m, a, b) in enumerate(zip(mid, lo, hi)):
        txt = f"{m:.1f}%" if i in (0, 1) else f"{a:.0f}–{b:.0f}%"
        ax.text(i, m + 0.28, txt, ha="center", fontsize=8.6, fontweight="bold", color=ORANGE)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#EEF2F8", zorder=0)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("콜렛의 프레이밍", loc="left", color=NAVY, fontsize=12.5)
    _box(ax2, 0.15, 6.7, 9.6, 2.95, "직접 말하겠다",
         "원가 상승이 기대를 초과했고\n내년에도 더 올라간다.",
         fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=11, bfs=8.8)
    _box(ax2, 0.15, 3.4, 9.6, 2.95, "오프셋이 있다",
         "메모리 부족 = AI 빌드아웃의 증상.\n원가만 올리는 부품이 아니다.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.8)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "한국 독자",
         "엔비디아 GPM↓ = 삼성·하이닉스 ASP↑\nQ1 가격전가가 다음 협상.",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.8)
    fig.tight_layout()
    _save(fig, "04_margin.png")


def chart_70vs100():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), dpi=170)

    ax = axes[0]
    ax.bar([0], [100], 0.55, color="#93C5FD", label="수요 (고객 포캐스트)")
    ax.bar([1], [70], 0.55, color=NAVY2, label="공급으로 자신 있는 성장")
    ax.plot([-0.35, 1.35], [70, 70], ls="--", color=ORANGE, lw=1.2)
    ax.set_xticks([0, 1], ["수요\n더블", "가이던스\n+70%"], fontsize=10)
    ax.set_ylabel("전년비 성장 %")
    ax.set_ylim(0, 120)
    ax.set_title("갭이 곧 가이던스의 근거", loc="left", color=NAVY, fontsize=12.5)
    ax.text(0, 104, "100%", ha="center", fontsize=11, fontweight="bold", color=NAVY2)
    ax.text(1, 74, "70%", ha="center", fontsize=11, fontweight="bold", color=NAVY)
    ax.annotate("공급 병목\n적어도 FY28 말", xy=(0.5, 85), ha="center", fontsize=8.5, color=ORANGE)
    ax.legend(frameon=False, fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("왜 1년 가이던스를 처음 열었나", loc="left", color=NAVY, fontsize=12.5)
    _box(ax2, 0.15, 6.7, 9.6, 2.95, "가시성",
         "메모리 업스트림 + 토지·전력·셸 다운스트림.\n2–3년 파이프를 같이 본다.",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.8)
    _box(ax2, 0.15, 3.4, 9.6, 2.95, "같은 악보",
         "고객·주주·공급망이 같은 숫자.\n큰 자원을 동시에 넣기 때문.",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.8)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "라스곤 프레이밍",
         "3년 $1T 대비 약 +$200B.\n비제약은 그보다 훨씬 큼.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.8)
    fig.tight_layout()
    _save(fig, "05_70vs100.png")


def chart_engines():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.35), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("콜렛이 말한 성장의 세 엔진", loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 4.55, 3.75, 5.1, "1. 모든 모델",
         "Closed  OpenAI·Anthropic\nGroq·Meta·Gemini\nOpen  TML·Mistral·Qwen\nKimi·GLM·DeepSeek\nMiniMax·Nemotron\n학습·추론·에이전트 하나.",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.7)
    _box(ax, 4.15, 4.55, 3.75, 5.1, "2. AI 공장 풀스택",
         "칩이 아니라 랙·네트워크·CPU.\nHopper $18B/GW\n→ Blackwell $25B\n→ Rubin $40B\nSpectrum-X 이더넷 2.6배\nVera 단독 CPU TAM.",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.7)
    _box(ax, 8.1, 4.55, 3.7, 5.1, "3. CUDA로 칩 밖",
         "소버린·네오클라우드·엔터.\n커스텀 실리콘 안 만드는 시장.\nACIE ≈ DC의 절반.\nDSX 레퍼런스로 더 빨리.",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=8.7)
    _box(ax, 0.2, 0.25, 11.6, 3.95, "Groq는 볼트온, 메인은 NVL72",
         "Groq 3 LPX 양산. Artificial Analysis에서 차선 대비 토큰/초 약 4배. 네비우스가 첫 물량.\n"
         "초저지연·고유기성 = 토큰당 비용↑, 고마진 서비스용. 세상 데이터센터의 대다수는 Vera Rubin NVL72.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)
    _save(fig, "06_engines.png")


def chart_capital():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.35), dpi=170)

    ax = axes[0]
    names = ["제3자 금융\n플랫폼", "공급·캐파\n약정(IR)", "오하이오\n보증", "프론티어\n랩 지분"]
    vals = [500, 279, 108.5, 50]
    colors = [PURPLE, NAVY2, ORANGE, TEAL]
    y = np.arange(len(names))
    ax.barh(y, vals, color=colors, height=0.62)
    ax.set_yticks(y, names, fontsize=8.8)
    ax.set_xlabel("십억 달러  ·  2GW 신용보강은 달러 아님")
    ax.set_title("밸런스시트가 제품이 됐다", loc="left", color=NAVY, fontsize=12.5)
    ax.set_xlim(0, 620)
    for i, v in enumerate(vals):
        ax.text(v + 8, i, f"${v:.0f}B", va="center", fontsize=8.2, color=NAVY, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("두 번 받는 구조", loc="left", color=NAVY, fontsize=12.5)
    _box(ax2, 0.15, 6.7, 9.6, 2.95, "네오클라우드 매출공유",
         "일부 용량 take-or-pay → 대출 가능.\n플로어 위 렌탈을 나눈다. 대출은 안 함.",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=10.8, bfs=8.6)
    _box(ax2, 0.15, 3.4, 9.6, 2.95, "프론티어 랩",
         "지분 ~$50B + 6곳 PE $5,000억+.\n내년 이 랩들 ≈ 매출의 1/4.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=10.8, bfs=8.6)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "리스크 한도라는 주장",
         "장비는 전용 가능. 출하분은 IG\n또는 IG 백스톱 고객이 소비.",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=10.8, bfs=8.6)
    fig.tight_layout()
    _save(fig, "07_capital.png")


def chart_qa():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 6.15), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("Q&A 8문  ·  애널리스트가 판 구멍", loc="left", fontsize=13.5, color=NAVY)

    rows = [
        (0.2, 7.55, "Moore  MS", "왜 1년 가이던스인가", "가시성 + 같은 악보. 수요≫70%.", BLUE_BG, NAVY2),
        (6.15, 7.55, "Muse  Cantor", "추론 점유율", "수명주기 전체 한 시스템. Groq는 볼트온.", OK_BG, GREEN),
        (0.2, 5.15, "Rasgon  Bernstein", "+$200B의 구성", "ACIE + $/GW + 가격. 비제약은 훨씬 큼.", WARN_BG, ORANGE),
        (6.15, 5.15, "Arya  BofA", "$500B + 커스텀칩", "플랫폼 ≠ XPU. 더 일찍 안 넣은 게 후회.", PURPLE_BG, PURPLE),
        (0.2, 2.75, "Arcuri  UBS", "오픈모델 = 적인가", "둘 다 폭증. 성공하는 모델이면 좋다.", BLUE_BG, NAVY2),
        (6.15, 2.75, "Reitzes  Melius", "RSI·AGI", "더 꺾인다. 에이전트가 사람 대체.", OK_BG, GREEN),
        (0.2, 0.25, "Schneider  GS", "제일 아픈 병목", "공급망 전부. 저녁 상대 찍지 않음.", WARN_BG, ORANGE),
        (6.15, 0.25, "Rakers  Wells", "$40B → $60–80B?", "방향은 무한대 / GW. 땅이 희소.", PURPLE_BG, PURPLE),
    ]
    for x, y, t, q, a, fc, c in rows:
        _box(ax, x, y, 5.65, 2.15, f"{t}  ·  {q}", a, fc=fc, ec="#E5E7EB", title_c=c, fs=10.2, bfs=8.5)
    _save(fig, "08_qa.png")


def chart_korea():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.55), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("한국으로 번역하면  ·  메모리가 엔비디아의 마진이자 우리의 ASP", loc="left", fontsize=13.2, color=NAVY)

    _box(ax, 0.2, 6.55, 3.75, 3.15, "공식 IR과 연결",
         "공급약정 $119→$279B\nprimarily memory\nSK hynix 다년 파트너십\n잔여 27–29년에 몰림",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.5, bfs=8.7)
    _box(ax, 4.15, 6.55, 3.75, 3.15, "컨콜이 더한 것",
         "메모리 가격이 기대 초과\n내년에도 더 오른다\n3사와 캐파를 더 늘린다\nQ1에 판가 전가",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.5, bfs=8.7)
    _box(ax, 8.1, 6.55, 3.7, 3.15, "소버린 AI",
         "보도자료: SKT·NAVER\nBrookfield GW급 DSX\n콜: 소버린 +35% QoQ\nYoY 3배+",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11.5, bfs=8.7)

    _box(ax, 0.2, 3.25, 5.75, 2.95, "같은 현상의 두 얼굴",
         "엔비디아 75→71–72% = 비용 충격\n삼성·하이닉스 = 가격·믹스 충격 (반대 부호)\n둘 다 AI 빌드아웃의 증상",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.4, bfs=8.8)
    _box(ax, 6.15, 3.25, 5.65, 2.95, "다음 협상",
         "엔비디아가 캐파를 더 달라고 한다.\n판가 전가는 Q1. 물량 vs 가격의 트레이드.",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=11.4, bfs=8.8)
    _box(ax, 0.2, 0.2, 11.6, 2.75, "워드 〈엔비디아〉 · 〈AI돈벌어 VS 메모리〉와 한 줄로",
         "수요가 안 꺾이면 메모리는 병목이자 가격 결정권. 엔비디아 GPM 바닥 구간이 국내 메모리 실적 레버리지 구간과 겹친다.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.4, bfs=9.0)
    _save(fig, "09_korea.png")


def chart_guide():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.15), dpi=170)

    ax = axes[0]
    q = ["1Q27", "2Q27", "3Q27E", "4Q27?", "FY28"]
    v = [81.6, 96.2, 108.0, None, None]
    ax.plot([0, 1, 2], [81.6, 96.2, 108.0], "o-", color=NAVY2, lw=2.2, ms=7, label="공식")
    ax.plot([2, 3], [108.0, 122], ls="--", color="#94A3B8", lw=1.4)
    ax.scatter([3], [122], color="#94A3B8", s=40, zorder=3)
    ax.set_xticks(range(5), q, fontsize=9)
    ax.set_ylabel("십억 달러")
    ax.set_ylim(70, 140)
    ax.set_title("가이던스는 3Q까지  ·  4Q는 필자 가정", loc="left", color=NAVY, fontsize=12.2)
    ax.text(0, 84.2, "81.6", ha="center", fontsize=8, color=NAVY2)
    ax.text(1, 99.0, "96.2", ha="center", fontsize=8, color=NAVY2)
    ax.text(2, 111.2, "108±2%", ha="center", fontsize=8, color=NAVY2)
    ax.text(3, 125.2, "~122?", ha="center", fontsize=8, color=GRAY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#EEF2F8", zorder=0)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("백오브엔벨로프  (투자 조언 아님)", loc="left", color=NAVY, fontsize=12.2)
    _box(ax2, 0.15, 6.7, 9.6, 2.95, "FY27 윤곽",
         "H1 $177.8B + 3Q $108B = $285.8B.\n4Q $118–125면 연간 ≈ $404–411B.",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=10.8, bfs=8.6)
    _box(ax2, 0.15, 3.4, 9.6, 2.95, "FY28 +70%",
         "그 위에서 ≈ $687–699B.\n증분 한 해 ≈ $280B대.",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=10.8, bfs=8.6)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "3Q 믹스",
         "Vera Rubin ≈ DC의 20%.\n순증은 ACIE, HS는 Q4부터.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=10.8, bfs=8.6)
    fig.tight_layout()
    _save(fig, "10_guide.png")


def chart_watch():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.45), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("다음에 볼 것  ·  숫자보다 구조", loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 5.15, 3.75, 4.5, "확인된 것",
         "2Q $96.2B / GPM 75%\n3Q $108B ±2%\n중국 DC = 0 가정\nRubin 양산, 3Q 20%\nAWS +200만 GPU",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.8)
    _box(ax, 4.15, 5.15, 3.75, 4.5, "열린 것",
         "4Q GPM이 71% 아래?\n가격전가가 붙는 속도\n랩 매출 1/4의 회수\nJalapeño vs 플랫폼\nDSO·AR 정상화",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=8.8)
    _box(ax, 8.1, 5.15, 3.7, 4.5, "깨지면",
         "토큰이 안 팔리면\nIG 백스톱이 약해지면\n메모리 캐파가 안 늘면\n보증 $108.5B가 현실화",
         fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=12, bfs=8.8)
    _box(ax, 0.2, 0.25, 11.6, 4.55, "젠슨이 맞물려 둔 세 조건",
         "① AI가 유용한 일을 한다   ② 토큰이 이익을 낸다   ③ 컴퓨트가 더 있으면 이익이 더 난다.\n"
         "이 세 개가 동시에 참인 한, 병목은 수요가 아니라 공급·전력·신용이다.",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=9.2)
    _save(fig, "11_watch.png")


def chart_deals():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.4), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("딜 맵  ·  컴퓨트를 어디에 심는가", loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 5.2, 3.75, 4.45, "AWS",
         "+200만 GPU\n이번 분기~FY29 2Q\nVera 일부 Rubin 결합\nNemotron on Bedrock\n창고 로봇 풀 피지컬 AI",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.7)
    _box(ax, 4.15, 5.2, 3.75, 4.45, "OpenAI + 오하이오",
         "약 12GW 커밋\nPORTS-Pike 4.25GW\n세대당 ≈ 150만 GPU\n20년, 여러 교체 사이클\n첫 ready FY2029",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.7)
    _box(ax, 8.1, 5.2, 3.7, 4.45, "그 외",
         "다른 랩 선택 2GW 신용\n네오클라우드 3→8GW\nVera: OCI·SpaceXAI·AWS\n유럽 슈퍼컴 35기\nNoetra 일본 DSX",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=8.7)
    _box(ax, 0.2, 0.25, 11.6, 4.6, "클라우드 산업 백로그 > $2T",
         "톱5 하이퍼스케일러 캡엑스 2026 ≈ $8,000억, 2027 ≈ $1.3조.\n"
         "GPU가 켜지면 그들의 매출·마진이 같이 올라간다는 게, 콜렛이 반복한 ‘컴퓨트 = 매출’.",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=9.0)
    _save(fig, "12_deals.png")


def main():
    _font()
    chart_print()
    chart_dc_mix()
    chart_gw_tam()
    chart_margin()
    chart_70vs100()
    chart_engines()
    chart_capital()
    chart_qa()
    chart_korea()
    chart_guide()
    chart_watch()
    chart_deals()
    print("done", OUT_DIR)


if __name__ == "__main__":
    main()
