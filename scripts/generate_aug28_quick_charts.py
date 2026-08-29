#!/usr/bin/env python3
"""8월 28일 Quick 코멘트 시각화 차트."""

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


def chart_us_close():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.45), dpi=170, gridspec_kw={"width_ratios": [1.2, 1]})

    ax = axes[0]
    names = [
        "옥타",
        "세일즈포스",
        "크라우드스트라이크",
        "엔비디아",
        "크레도",
        "브로드컴",
        "인텔",
        "아스트라랩스",
        "SOX",
        "SK하이닉스 ADR",
        "나스닥",
        "S&P500",
        "다우",
        "마이크론",
        "샌디스크",
        "마벨",
    ]
    vals = [28.6, 22.0, 20.5, 8.7, 6.1, 4.5, 4.4, 4.3, 2.33, 2.3, 1.57, 0.72, 0.20, -0.3, -1.0, -1.5]
    colors = [GREEN if v >= 0 else RED for v in vals]
    y = np.arange(len(names))
    ax.barh(y, vals, color=colors, height=0.62, zorder=2)
    ax.set_yticks(y, names, fontsize=8.0)
    ax.axvline(0, color="#CBD5E1", lw=1)
    ax.set_xlabel("%")
    ax.set_title("8/27 미 본장  ·  GPU·네트워크 강세, 메모리는 시큰둥 (05:38)", loc="left", color=NAVY, fontsize=11.6)
    ax.set_xlim(-4.5, 34)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)
    for i, v in enumerate(vals):
        ax.text(
            v + (0.25 if v >= 0 else -0.25),
            i,
            f"{v:+.1f}%" if abs(v) >= 1 else f"{v:+.2f}%",
            va="center",
            ha="left" if v >= 0 else "right",
            fontsize=7.2,
            color=colors[i],
            fontweight="bold",
        )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("한 줄 해석", loc="left", color=NAVY, fontsize=12.2)
    _box(ax2, 0.15, 6.85, 9.6, 2.9, "지수", "NASDAQ 26,541  +1.57%\nS&P500 7,731  +0.72%\nDow 53,569  +0.20%\nSOX 11,882.17  +2.33%", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    _box(ax2, 0.15, 3.55, 9.6, 3.05, "엔비디아 +8.7%", "FY2027(FY28) 매출 약 +70%\nAI CAPEX 피크아웃 우려를 다시 눌렀다\nSOX보다 엔비디아가 훨씬 강함", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.6)
    _box(ax2, 0.15, 0.2, 9.6, 3.1, "차별화", "가속기/네트워크 강세\n마이크론 −0.3% · 샌디스크 −1.0%\n마벨 −1.5%는 차익실현", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "01_us_close.png")


def chart_korea_close():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.9), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("8/27 국내 마감  ·  코스피 +1.5%대  /  코스닥 +1.6%대  ·  외인 선물 1.5조+", loc="left", fontsize=12.6, color=NAVY)

    _box(ax, 0.2, 6.45, 3.75, 3.25, "지수", "양대 지수 상승 마감\n코스피 갭상승 후 일부 반납\n코스닥 상승 폭 확대\n한은 기준금리 3.00% 연속 인상", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.6)
    _box(ax, 4.15, 6.45, 3.75, 3.25, "오른 곳", "대형 반도체 갭상승\n소부장 · 전력기기 · 전선\n2차전지 (ESS 1GW+ 검토)\nLS ELECTRIC · HD현대일렉", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.6)
    _box(ax, 8.1, 6.45, 3.7, 3.25, "흐름", "삼전·닉스 장중 반납\n전력기기 = 미 현지생산 수혜\n잭슨홀 경계로 탄력 제한\n내일도 상승 추세에 무게", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=8.6)
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
        "국내 EPS 상승률 지속\n메모리 가격 상승세\n메모리 주가 과매도·저평가\n하이닉스 ADR → 마이크론 갭\n7월 CPI·PPI로 인상 우려 완화\n엔비디아 호실적·가이던스",
        fc=LIGHT,
        ec="#CBD5E1",
        title_c=NAVY,
        fs=12,
        bfs=9.0,
    )
    _save(fig, "02_korea_close.png")


def chart_nvidia_print():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.4), dpi=170, gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    names = ["전사 매출", "Non-GAAP EPS", "Data Center", "Edge Computing", "3Q 가이던스"]
    beats = [
        (96.22 / 92.29 - 1) * 100,
        (2.46 / 2.09 - 1) * 100,
        (89.02 / 85.83 - 1) * 100,
        (7.19 / 6.61 - 1) * 100,
        (108.0 / 104.57 - 1) * 100,
    ]
    colors = [GREEN] * 5
    y = np.arange(len(names))
    ax.barh(y, beats, color=colors, height=0.55, zorder=2)
    ax.axvline(0, color="#CBD5E1", lw=1)
    ax.set_yticks(y, names)
    ax.set_xlabel("컨센서스 대비 %")
    ax.set_title(_esc("FY27 2Q vs 컨센  ·  매출 $96.22B  /  EPS $2.46  (첨부 PDF)"), loc="left", color=NAVY, fontsize=10.8)
    ax.set_xlim(0, 22)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)
    notes = ["$96.22 vs $92.29B", "$2.46 vs $2.09", "$89.02 vs $85.83B", "$7.19 vs $6.61B", "$108 vs $104.57B"]
    for i, (v, n) in enumerate(zip(beats, notes)):
        ax.text(v + 0.25, i, f"{v:+.1f}%  {n}", va="center", ha="left", fontsize=7.6, color=GREEN, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("가이던스 = 공급 상한", loc="left", color=NAVY, fontsize=12.2)
    _box(ax2, 0.1, 6.7, 9.7, 3.05, "FY28 +70%", "시장 예상 +40% 중반을 크게 상회\n실제 수요 기준은 약 +100%\n1년 앞 가이던스는 처음", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    _box(ax2, 0.1, 3.45, 9.7, 2.95, "3Q $108B ±2%", "중국향 DC 컴퓨팅 미포함\nGPM 74.0% ±50bp vs 컨센 74.8%", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.6)
    _box(ax2, 0.1, 0.2, 9.7, 2.95, "Non-하이퍼스케일러", "2Q 45.3% ← 1Q 42.8%\n← 4Q 32.3% ← 3Q 31.4%\n저변 확대가 뚜렷", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "03_nvidia_print.png")


def chart_gpm_path():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.35), dpi=170, gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    xs = ["2Q\n75.0%", "3Q 가이드\n74.0%", "4Q\n71~72%", "FY28\n72~73%"]
    ys = [75.0, 74.0, 71.5, 72.5]
    ax.plot([0, 1, 2, 3], ys, color=NAVY2, lw=2.4, marker="o", ms=8, zorder=3)
    ax.fill_between([0, 1, 2, 3], [74.5, 73.5, 71.0, 72.0], [75.5, 74.5, 72.0, 73.0], color="#93C5FD", alpha=0.28)
    ax.set_xticks([0, 1, 2, 3], xs, fontsize=9)
    ax.set_ylim(69.5, 76.5)
    ax.set_ylabel("Gross Margin %")
    ax.set_title("엔비디아 GPM 경로  ·  메모리 원가 → 가격 전가", loc="left", color=NAVY, fontsize=11.6)
    ax.axhline(75, color="#CBD5E1", ls="--", lw=1)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#EEF2F8")

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("왜 72~73%에서 멈추나", loc="left", color=NAVY, fontsize=12.2)
    _box(ax2, 0.1, 6.7, 9.7, 3.05, "인정한 것", "메모리 가격 급등\nGP 75% → 71~72% 하락\n2027년 초(FY28 1Q) 제품 가격 인상", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    _box(ax2, 0.1, 3.45, 9.7, 2.95, "핵심 차이", "AI 서버 가격 +15%\n≠ NVIDIA GPU ASP +15%\n상승분 상당수는 메모리 ASP", fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=11, bfs=8.6)
    _box(ax2, 0.1, 0.2, 9.7, 2.95, "메모리에 의미", "원가 전가 가격결정력 확인\n수요가 안 꺾이면 추가 인상 여지\n약정 +$1,500억 QoQ = 선점", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "04_gpm_path.png")


def chart_capex_split():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.45), dpi=170)

    ax = axes[0]
    labels = ["NVIDIA", "NVIDIA향\nHBM", "나머지\n서버 부품"]
    vals = [315, 81, 130]
    colors = [NAVY2, GOLD, GREEN]
    bars = ax.bar(labels, vals, color=colors, width=0.62)
    ax.set_ylabel("조원")
    ax.set_title("2027 서버/AI 인프라 CAPEX 증가 +525조원", loc="left", color=NAVY, fontsize=11.4)
    ax.set_ylim(0, 380)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 8, f"+{v}조", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("Top 5 Hyperscaler만 보면", loc="left", color=NAVY, fontsize=12.2)
    _box(ax2, 0.15, 6.7, 9.6, 3.05, "525 − 315 − 81 ≈ 130조", "나머지 부품이 경쟁할 추가 예산\nDRAM/eSSD가 전부 가져가지 못함", fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.2, bfs=8.8)
    _box(ax2, 0.15, 3.45, 9.6, 2.95, "CSP만으로는", "2027년 DRAM/eSSD 가격이\n지금보다 계속 폭등한다고\n보기는 어렵다", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.2, bfs=8.8)
    _box(ax2, 0.15, 0.2, 9.6, 2.95, "스윙 팩터", "Neo Cloud · Sovereign AI\nEnterprise · Industrial\n이 추가 수요가 가격의 핵심 변수", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11.2, bfs=8.8)
    fig.tight_layout()
    _save(fig, "05_capex_split.png")


def chart_network_map():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.85), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("네트워크 칩 한눈에  ·  마벨 / 아스테라랩스 / 크레도", loc="left", fontsize=13.0, color=NAVY)

    _box(ax, 0.2, 5.35, 3.75, 4.35, "Marvell (MRVL)", "맞춤형 ASIC + 초고속 네트워크\n커스텀 AI ASIC · 광통신\nSerDes/DSP · 이더넷 스위치\n하이퍼스케일러 TPU/ASIC 생산", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.6)
    _box(ax, 4.15, 5.35, 3.75, 4.35, "Astera Labs (ALAB)", "서버 안의 데이터 고속도로\nPCIe/CXL 리타이머 · 스위치\nCXL 메모리 컨트롤러\nGPU↔CPU↔메모리↔스토리지", fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=8.6)
    _box(ax, 8.1, 5.35, 3.7, 4.35, "Credo (CRDO)", "데이터센터 내 서버 간 연결\nAEC 액티브 전기 케이블\nSerDes/DSP가 핵심\n고속·저전력, 신호 손실 축소", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.6)
    _box(
        ax,
        0.2,
        0.2,
        11.6,
        4.85,
        "용어",
        "PCIe = 부품 간 고속 통로 (GPU↔CPU↔SSD↔NIC)\n"
        "리타이머 = 고속도로 중간 신호 재생소. 약해진 신호를 다시 깨끗하게.\n"
        "SerDes = 여러 데이터를 한 줄로 압축(Serialize)했다가 다시 풀어줌(Deserialize)\n"
        "AEC = 케이블 안에 신호 보정 반도체가 들어간 고속 전기 케이블\n"
        "Custom ASIC이 커질수록 SerDes/고속 연결 부품 수요가 같이 증가.",
        fc=LIGHT,
        ec="#CBD5E1",
        title_c=NAVY,
        fs=12,
        bfs=8.8,
    )
    _save(fig, "06_network_map.png")


def chart_memory_val():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.45), dpi=170)

    ax = axes[0]
    names = ["샌디스크\nFY27", "마이크론\nFwd 12M", "마이크론\nCY27", "하이닉스 ADR\n26년", "하이닉스 ADR\n27년", "하이닉스 본주\n26년", "하이닉스 본주\n27년", "삼성 본주\n26년", "삼성 본주\n27년"]
    pers = [7.4, 7.5, 6.2, 6.4, 5.1, 4.9, 4.0, 5.5, 4.0]
    colors = [GOLD, GOLD, GOLD, NAVY2, NAVY2, GREEN, GREEN, PURPLE, PURPLE]
    bars = ax.bar(range(len(names)), pers, color=colors, width=0.7)
    ax.set_xticks(range(len(names)), names, fontsize=7.2)
    ax.set_ylabel("PER (배)")
    ax.set_title("8/27 기준 메모리 PER  ·  본주가 더 싸 보인다", loc="left", color=NAVY, fontsize=11.4)
    ax.set_ylim(0, 9.2)
    for bar, v in zip(bars, pers):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.15, f"{v}", ha="center", fontsize=8.2, color=NAVY, fontweight="bold")
    ax.axhline(8, color=RED, ls="--", lw=1, alpha=0.7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title(_esc("가격 · 이익 (8/27)"), loc="left", color=NAVY, fontsize=12.2)
    _box(ax2, 0.1, 6.7, 9.7, 3.05, "현주가", "하이닉스 본주 173만 / ADR 161.61$=223만\n삼성 26.6만 · MU 935.39$ · SNDK 1484.95$\nADR 프리미엄 29%", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.4)
    _box(ax2, 0.1, 3.45, 9.7, 2.95, "27년 이익 (기본)", "하이닉스 OP 392조 / EPS 436K\n삼성 OP 543조 / EPS 66.4K\nYoY OP +25% · EPS +38%", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.4)
    _box(ax2, 0.1, 0.2, 9.7, 2.95, "보수 시나리오", "하이닉스 250~260조 / 290~300K\n삼성 355~370조 / 43~45K\n27년 성장 0 가정 시 PER 6~7배", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.4)
    fig.tight_layout()
    _save(fig, "07_memory_val.png")


def chart_micron_sca():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.85), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("마이크론으로 읽는 시장  ·  수요는 강하다, 영구 이익인지를 의심한다", loc="left", fontsize=12.6, color=NAVY)

    _box(ax, 0.2, 5.25, 3.75, 4.45, "긍정", "고객 요구량 > 공급 50%\nSCA 가격 Floor\n2027 HBM 재협상\nNvidia·HS AI CAPEX 지속", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.8)
    _box(ax, 4.15, 5.25, 3.75, 4.45, "SCA", "16개 계약\nDRAM 약 20% · NAND 약 1/3\n전부 체결 시 매출 40% Floor/Ceiling\nFloor = 과거 최고 분기 GM보다 높음", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.6)
    _box(ax, 8.1, 5.25, 3.7, 4.45, "2027 = HBM", "산업 HBM ASP +79%\nMicron HBM +72%\nHBM4E $30/GB+\n일반 DRAM 상승률은 둔화", fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=8.6)
    _box(
        ax,
        0.2,
        0.2,
        11.6,
        4.75,
        "부정 · 해석의 여지",
        "DRAM 가격 상승률 둔화 · 높은 이익 지속 불확실 · SCA 2030 종료 · 이후 미국 생산/R&D $250B+ CAPEX\n"
        "Floor가 과거 최고 GM보다 높다 = 반대로 최악 시 마진 20%p 하락도 불가능하지는 않다?\n"
        "그래도 그 최악 PER이 8배 이하라면 비싼가, 가 자문.",
        fc=WARN_BG,
        ec=GOLD,
        title_c=ORANGE,
        fs=12,
        bfs=8.8,
    )
    _save(fig, "08_micron_sca.png")


def chart_marvell():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.35), dpi=170)

    ax = axes[0]
    years = ["FY27", "FY28"]
    revs = [12, 18]
    bars = ax.bar(years, revs, color=[NAVY2, GOLD], width=0.5)
    ax.set_ylabel("십억 달러")
    ax.set_title(_esc("Marvell 매출  ·  FY27 $12B(+45%) → FY28 $18B(+50%)"), loc="left", color=NAVY, fontsize=10.8)
    ax.set_ylim(0, 22)
    for bar, v, g in zip(bars, revs, ["+45%", "+50%"]):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.4, f"${v}B\n{g}", ha="center", fontsize=10, color=NAVY, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("컨콜은 강한데이 주가는 −6%대", loc="left", color=NAVY, fontsize=12.0)
    _box(ax2, 0.1, 6.7, 9.7, 3.05, "가이던스", "3Q FY27 $31.5억 vs 컨센 $30.3억\nDC +60% · Custom ASIC FY28 2배+\nFY29 가속 · 공급 선급 $10억", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    _box(ax2, 0.1, 3.45, 9.7, 2.95, "Google 워런트", "프로그램 매출은 기존 Custom 목표에 포함\n숨은 업사이드가 아님\n기대 대비 서프라이즈 부족 가능", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    _box(ax2, 0.1, 0.2, 9.7, 2.95, "Peers", "CRDO 본장 +4.8% / AH −1%\nALAB +6% / AH −1%대\nAVGO +4% · 펀더 이슈 아님", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "09_marvell.png")


def chart_power_gs():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.4), dpi=170)

    ax = axes[0]
    names = ["효성중공업", "HD현대일렉트릭", "LS일렉트릭"]
    upside = [48.7, 16.0, 14.1]
    colors = [GREEN, GOLD, GRAY]
    bars = ax.bar(names, upside, color=colors, width=0.55)
    ax.set_ylabel("현재가 대비 상승여력 %")
    ax.set_title(_esc("골드만삭스 Initiate  ·  효성 Buy / 현대일렉·LS Neutral"), loc="left", color=NAVY, fontsize=11.0)
    ax.set_ylim(0, 60)
    tps = ["TP 416만\n현 279.7만", "TP 85만\n현 73.3만", "TP 23만\n현 20.15만"]
    for bar, v, t in zip(bars, upside, tps):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 1.2, f"+{v:.1f}%\n{t}", ha="center", fontsize=8.2, color=NAVY, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("트럼프 전력망 비상사태 + BBU", loc="left", color=NAVY, fontsize=12.0)
    _box(ax2, 0.1, 6.7, 9.7, 3.05, "직접 수혜 강도", "BESS >>> BBU\n변압기·발전기·BESS·인버터·차단기\n120일 후 DOE 가이드라인", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    _box(ax2, 0.1, 3.45, 9.7, 2.95, "국내 현지 공장", "효성 멤피스 · HD현대일렉 앨라배마\nLS 유타 배전반\n10MVA+ 중국 비중은 이미 낮음", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    _box(ax2, 0.1, 0.2, 9.7, 2.95, "효성 TP 체크", "컨센 425만과 크게 다르지 않음\n아직 안전마진 20%밖\n목표주가의 80% 이상 추격 자제", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "10_power_gs.png")


def chart_cosmetics():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 6.05), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("K-뷰티 3사  ·  서구권 · 채널 확장 · 물류 정상화", loc="left", fontsize=13.0, color=NAVY)

    _box(ax, 0.2, 5.15, 3.75, 4.55, "아모레퍼시픽", "2Q 매출 1.1759조 +17%\nOP 1,173억 +59% (컨센 +19%)\n북미 +57% · EMEA +63%\n서구권 51% > 아시아 첫 추월", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.4)
    _box(ax, 4.15, 5.15, 3.75, 4.55, "에이피알", "북미 QoQ +1,000억\n아마존 500 / 오프라인+틱톡 500\n유럽 418→838→1,451억\n항공비 100억+ → 해상 전환", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.4)
    _box(ax, 8.1, 5.15, 3.7, 4.55, "실리콘투", "글렌우드 6.72% 블록딜 완료\nCVC 3,000억 · Douglas 시너지\n26E 매출 1.63조 +46%\nOP 2,998억 · OPM 18.4%", fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=8.4)
    _box(
        ax,
        0.2,
        0.2,
        11.6,
        4.65,
        "공통 축",
        "지역: 미국 → 유럽.  채널: Amazon → Target/Walmart/Boots + TikTok Shop.  물류: 항공 → 해상.\n"
        "코스알엑스 RX라인 30%+가 스네일뮤신을 추월.  라네즈·이니스프리·에스트라·일리윤도 채널별 성과.\n"
        "아모레 재평가: 12MF PER 30배 내외 글로벌 멀티브랜드 수렴.  11:02 실리콘투 포인트는 에이피알 문안이 중복 첨부됨.",
        fc=LIGHT,
        ec="#CBD5E1",
        title_c=NAVY,
        fs=12,
        bfs=8.8,
    )
    _save(fig, "11_cosmetics.png")


def chart_skt():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.85), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("SK텔레콤 데이터센터  ·  호라이즌(현재) / 하이퍼(미래)  ·  모두의 AI", loc="left", fontsize=12.4, color=NAVY)

    _box(ax, 0.2, 5.25, 5.75, 4.45, "SK호라이즌 = 기존 318MW", "기존 137 + 울산 100 + 구로 75\n해저케이블 포함\nEV 6.3조 · 3조 조달\nSKT 51 / KKR 29 / IMM 20", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.8)
    _box(ax, 6.15, 5.25, 5.65, 4.45, "SK하이퍼 = GW급", "2029년부터 단계적 5GW\n향후 최대 15GW\nAI 데이터센터 성장축\n이익 귀속은 아직 빈칸", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=8.8)
    _box(
        ax,
        0.2,
        0.2,
        11.6,
        4.75,
        "주가 · 정책",
        "단기 중립~긍정 (가치 확인 + 현금 3조).  중장기는 SK하이퍼에서 SKT가 얼마를 버느냐.\n"
        "09:34 데일리안: 정부 '모두의 AI' 사업자에 SKT · KT · 카카오.  카톡·전화 AI 베타 9월 언급이 주변 기사에 있음.",
        fc=LIGHT,
        ec="#CBD5E1",
        title_c=NAVY,
        fs=12,
        bfs=8.8,
    )
    _save(fig, "12_skt_horizon.png")


def chart_kv_cache():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.4), dpi=170)

    ax = axes[0]
    labels = ["K+V", "Layer", "KV Head", "Head Dim", "Context", "BF16"]
    vals = [2, 80, 8, 128, 131072, 2]
    ax.barh(range(len(labels)), [1] * 6, color=[NAVY2, GOLD, PURPLE, GREEN, ORANGE, GRAY], height=0.6)
    ax.set_yticks(range(len(labels)), [f"{a}  =  {b:,}" if b > 100 else f"{a}  =  {b}" for a, b in zip(labels, vals)])
    ax.set_xticks([])
    ax.set_title("128K Context → 약 40GB KV Cache", loc="left", color=NAVY, fontsize=12.0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.set_xlim(0, 1.35)
    for i, note in enumerate(["두 개(Key, Value)", "처리 단계 80번", "관심 영역 8개", "그릇 크기 128", "131,072 토큰", "숫자당 2 Byte"]):
        ax.text(1.02, i, note, va="center", fontsize=8.4, color=GRAY)

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("공식", loc="left", color=NAVY, fontsize=12.2)
    _box(
        ax2,
        0.1,
        5.35,
        9.7,
        4.4,
        "KV Cache = 2 × Layer × KV Head × Head Dim × Context × Bytes",
        "2 × 80 × 8 × 128 × 131,072 × 2\n= 42,949,672,960 Byte\n= 40 GiB 정확",
        fc=BLUE_BG,
        ec="#93C5FD",
        title_c=NAVY2,
        fs=10.4,
        bfs=9.2,
    )
    _box(ax2, 0.1, 0.25, 9.7, 4.8, "왜 메모리인가", "K = 어디를 찾아볼 것인가 (색인)\nV = 찾아낸 실제 정보\nContext가 길수록, Layer가 많을수록\nHBM/DRAM KV가 커진다", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.8)
    fig.tight_layout()
    _save(fig, "13_kv_cache.png")


def chart_watch_check():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 6.2), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("관심 종목 (23:46)  ·  눌림목 선호는 2차전지·건설/DC·변압기·화장품", loc="left", fontsize=12.2, color=NAVY)

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
    _save(fig, "14_watchlist.png")


def chart_side_themes():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 6.15), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("옆 테마  ·  키옥시아 · MLCC · 관세 · 원전 · 현대차 로봇", loc="left", fontsize=12.8, color=NAVY)

    _box(ax, 0.2, 6.45, 3.75, 3.25, "키옥시아 NAND", "Fab3 1조엔+ · 전체 5조엔+\n2029년 이후 · SanDisk 공동\nYMTC 점유 14% 동률\nNAND 영향은 DRAM의 1/3", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.4, bfs=8.4)
    _box(ax, 4.15, 6.45, 3.75, 3.25, "삼성전기 MLCC", "4Q26 OEM 인상 확대\nX5R +25~30% · X6S +10~20%\nKey = 일본 3사 동참 여부\n대만·중국 +10~20%", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.4, bfs=8.4)
    _box(ax, 8.1, 6.45, 3.7, 3.25, "반도체 관세", "폴리티코 전면 관세 검토\nMade in USA = 회피 수단\n인디애나 HBM이 전략 자산\n쿠팡 301조와 연결 가능", fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=11.4, bfs=8.4)
    _box(ax, 0.2, 0.2, 5.75, 5.95, "웨스팅하우스 3대 조건", "① 밸류·손실 분담 (승자의 저주)\n② 의결권·IP, 시공 하청 방지\n③ 투 트랙, APR1400 독립\n도시바 WEC 인수가 반면교사\n미국·동유럽 800억달러 선점 기회", fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=11.6, bfs=8.6)
    _box(ax, 6.15, 0.2, 5.65, 5.95, "현대차 로봇 분리", "Target P/E 17배 → TP 60만 (−7.7%)\n중국 EV4 12M Fwd 18.9배 대비 10% 할인\n본체는 자동차, 로봇 멀티플 직접 적용 어려움\n자회사 장점: 투자 유치·적자 격리·BD IPO\n재평가 효과는 제한적", fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=11.6, bfs=8.6)
    _save(fig, "15_side_themes.png")


def chart_portfolio():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.55), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("포트 · 규칙 · 체크포인트  ·  매크로 이슈 없고 전약이면 신규 접근", loc="left", fontsize=12.4, color=NAVY)

    _box(ax, 0.2, 5.2, 3.75, 4.5, "포트 (07:54)", "AI 관련 ~50%\n반도체/변압기/2차전지\nNon-AI 20~30%\n건설·원전·DC · 화장품\n현금 20~30% · 조선 제한", fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.6)
    _box(ax, 4.15, 5.2, 3.75, 4.5, "규칙 (22:42)", "목표주가는 보수적 기준\n고목표-컨센 추종 자제\nTP의 80% 이상 추격 자제\n60% 이하시 손절 확실히\n영향력 있는 TP 하향은 장기", fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=8.6)
    _box(ax, 8.1, 5.2, 3.7, 4.5, "선호 (08:46)", "대형 반도체보다 눌림목\n2차전지 · 건설/DC\n변압기 · 화장품\n어게인 태조이방원\n원화강세: 식음료·신재생·철강", fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.6)
    _box(
        ax,
        0.2,
        0.2,
        11.6,
        4.7,
        "앞으로 볼 것",
        "잭슨홀 · 비CSP(Neo Cloud/Sovereign/Enterprise) 수요 · HBM 2027 재협상 · 일본 MLCC 동참\n"
        "관세율·면제 조건 · SK하이퍼 이익 귀속 · 효성 안전마진 20% · Rubin/SOCAMM(심텍·티엘비)\n"
        "2차전지는 할인율·실적·정책 3조건 충족. 단기 급등 → 눌림목 또는 분할. 미 금리 안정이 전제.",
        fc=LIGHT,
        ec="#CBD5E1",
        title_c=NAVY,
        fs=12,
        bfs=8.8,
    )
    _save(fig, "16_portfolio.png")


def main():
    chart_us_close()
    chart_korea_close()
    chart_nvidia_print()
    chart_gpm_path()
    chart_capex_split()
    chart_network_map()
    chart_memory_val()
    chart_micron_sca()
    chart_marvell()
    chart_power_gs()
    chart_cosmetics()
    chart_skt()
    chart_kv_cache()
    chart_watch_check()
    chart_side_themes()
    chart_portfolio()


if __name__ == "__main__":
    main()
