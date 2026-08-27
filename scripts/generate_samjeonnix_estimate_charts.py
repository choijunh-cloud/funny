#!/usr/bin/env python3
"""삼전닉스 실적 추정 차트 — NVIDIA FY27 2Q 컨콜 기준."""

from __future__ import annotations

from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch

OUT_DIR = Path("/workspace/reports/samjeonnix-estimate/charts")
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


def chart_bridge():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.35), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("NVIDIA 콜 → 삼전닉스 손익  ·  전달 경로 네 개", loc="left", fontsize=13.4, color=NAVY)

    _box(ax, 0.2, 5.15, 2.85, 4.5, "1. 가격",
         "GPM 75→71–72\n메모리 원가 기대 초과\n내년에도 더 오른다\nQ1에 판가 전가",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11.4, bfs=8.6)
    _box(ax, 3.2, 5.15, 2.85, 4.5, "2. 물량",
         "FY28 +70%는 공급숫자\nRubin 3Q DC 20%\n약정 $279B 대부분 메모리\n3사에 캐파 요청",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11.4, bfs=8.6)
    _box(ax, 6.2, 5.15, 2.85, 4.5, "3. 믹스",
         "$18→$25→$40B/GW\nHBM4 램프 + SOCAMM\n서버 DRAM·eSSD 동반\n범용 캐파 구축출",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11.4, bfs=8.6)
    _box(ax, 9.2, 5.15, 2.6, 4.5, "4. 시점",
         "NVDA 3Q = 韓 3Q\nNVDA 4Q 바닥 = 韓 4Q\nFY28 = 캘 2027\nLTA는 후행",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=11.4, bfs=8.6)
    _box(ax, 0.2, 0.25, 11.6, 4.55, "거리와 어긋나는 지점",
         "일부 증권은 3Q 가격 한 자릿수·4Q 감익을 깐다 (키움 닉스 4Q OP 65.6조).\n"
         "콜렛은 메모리가 내년까지 더 오르고, 4Q에 자기 GPM이 바닥이라고 했다. 4Q 감익 가정과 충돌.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.0)
    _save(fig, "01_bridge.png")


def chart_price():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.2), dpi=170)

    ax = axes[0]
    xs = np.arange(4)
    labels = ["2Q\n실제", "3Q\n추정", "4Q\n추정", "2027\n연간"]
    street = [40, 12, 4, 8]
    nvda = [40, 19, 10, 22]
    ax.plot(xs[:3], street[:3], "o--", color="#94A3B8", lw=1.8, ms=6, label="거리식 둔화")
    ax.plot(xs, nvda, "o-", color=ORANGE, lw=2.2, ms=7, label="NVIDIA 콜 베이스")
    ax.set_xticks(xs, labels, fontsize=9)
    ax.set_ylabel("블렌디드 ASP QoQ %  (2027은 YoY)")
    ax.set_ylim(0, 48)
    ax.set_title("가격 경로  ·  둔화가 아니라 고점 연장", loc="left", color=NAVY, fontsize=12.3)
    ax.legend(frameon=False, fontsize=8.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#EEF2F8")

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("가정  ·  필자 베이스", loc="left", color=NAVY, fontsize=12.3)
    _box(ax2, 0.15, 6.7, 9.6, 2.95, "3Q26",
         "DRAM +18~20%  ·  NAND +12~15%\n비트 삼성 +6% / 닉스 +9%  (HBM4)",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    _box(ax2, 0.15, 3.4, 9.6, 2.95, "4Q26",
         "DRAM +8~12%  ·  비트 +5~6%\nNVDA GPM 바닥 = 원가 아직 상승",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.6)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "2027",
         "HBM ASP +50% (UBS +79%는 강세)\n비트 +18%  ·  블렌디드 매출 +45%",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "02_price.png")


def chart_samsung():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.25), dpi=170)

    ax = axes[0]
    q = ["1Q", "2Q", "3QE", "4QE"]
    actual = [57.2, 89.5, None, None]
    base = [57.2, 89.5, 115, 133]
    street = [57.2, 89.5, 114, 120]
    x = np.arange(4)
    ax.plot(x, street, "o--", color="#94A3B8", lw=1.7, ms=6, label="거리 (3Q 114·4Q 120)")
    ax.plot(x, base, "o-", color=NAVY2, lw=2.2, ms=7, label="NVIDIA 베이스")
    ax.scatter([0, 1], [57.2, 89.5], s=70, color=GREEN, zorder=5)
    ax.set_xticks(x, q)
    ax.set_ylabel("영업이익 조원")
    ax.set_ylim(40, 155)
    ax.set_title("삼성전자 분기 OP  ·  4Q가 차이", loc="left", color=NAVY, fontsize=12.3)
    ax.legend(frameon=False, fontsize=8.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for i, v in enumerate(base):
        ax.text(i, v + 4, f"{v:.0f}", ha="center", fontsize=8.5, fontweight="bold", color=NAVY)
    ax.grid(axis="y", color="#EEF2F8")

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("3Q 메모리 브리지  (2Q 120.8조)", loc="left", color=NAVY, fontsize=12.3)
    _box(ax2, 0.15, 6.7, 9.6, 2.95, "비트 +6% × ASP +19%",
         "메모리 매출 152조  ·  Δ+31조\n증분마진 82% → 메모리 OP 115조",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.6)
    _box(ax2, 0.15, 3.4, 9.6, 2.95, "전사",
         "DS ≈ 메모리. DX −1.2조 (칩플레이션)\n3Q OP 115조  ·  거리 114조와 거의 같음",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "4Q",
         "메모리 176조 · OP 134조\n전사 133조  vs 거리 120조",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "03_samsung.png")


def chart_hynix():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.25), dpi=170)

    ax = axes[0]
    x = np.arange(4)
    street = [37.6, 60.5, 78.8, 88]
    base = [37.6, 60.5, 80, 95]
    kiwoom = [37.6, 60.5, 75.2, 65.6]
    ax.plot(x, kiwoom, "s--", color=RED, lw=1.4, ms=5, label="키움 (4Q 감익)")
    ax.plot(x, street, "o--", color="#94A3B8", lw=1.7, ms=6, label="거리식 FY265 잔여")
    ax.plot(x, base, "o-", color=TEAL, lw=2.2, ms=7, label="NVIDIA 베이스")
    ax.set_xticks(x, ["1Q", "2Q", "3QE", "4QE"])
    ax.set_ylabel("영업이익 조원")
    ax.set_ylim(20, 110)
    ax.set_title("SK하이닉스 분기 OP  ·  순수 메모리", loc="left", color=NAVY, fontsize=12.3)
    ax.legend(frameon=False, fontsize=8.0, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for i, v in enumerate(base):
        ax.text(i, v + 3, f"{v:.0f}", ha="center", fontsize=8.5, fontweight="bold", color=NAVY)
    ax.grid(axis="y", color="#EEF2F8")

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("3Q 브리지  (2Q 79.3조 / OP 60.5)", loc="left", color=NAVY, fontsize=12.3)
    _box(ax2, 0.15, 6.7, 9.6, 2.95, "비트 +9% × ASP +18%",
         "매출 102조  ·  거리 93조를 매출에서 상회\nOP 80조  ·  거리 78.8조와 근접",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.6)
    _box(ax2, 0.15, 3.4, 9.6, 2.95, "순이익은 영업으로",
         "2Q 세전 122.7 = OP 60.5 + 키옥시아 등 62\n순익 93.9. EPS는 영업×78%",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "4Q",
         "매출 119조 · OP 95조\n키움 65.6조와 29조 갭 = 핵심 논쟁",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "04_hynix.png")


def chart_fy():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.25), dpi=170)

    ax = axes[0]
    labs = ["삼성\n26E", "삼성\n27E", "닉스\n26E", "닉스\n27E"]
    street = [381, 499, 265, 415]
    base = [395, 555, 273, 410]
    x = np.arange(4)
    ax.bar(x - 0.18, street, 0.34, color="#CBD5E1", label="거리")
    ax.bar(x + 0.18, base, 0.34, color=NAVY2, label="NVIDIA 베이스")
    ax.set_xticks(x, labs, fontsize=9)
    ax.set_ylabel("연간 영업이익 조원")
    ax.set_ylim(0, 640)
    ax.set_title("연간 OP  ·  26년은 4Q, 27년은 가격", loc="left", color=NAVY, fontsize=12.3)
    ax.legend(frameon=False, fontsize=8.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    for i, (s, b) in enumerate(zip(street, base)):
        ax.text(i + 0.18, b + 10, f"{b:.0f}", ha="center", fontsize=8, fontweight="bold", color=NAVY2)
    ax.grid(axis="y", color="#EEF2F8")

    ax2 = axes[1]
    ax2.axis("off")
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.set_title("시나리오 밴드  (조원)", loc="left", color=NAVY, fontsize=12.3)
    _box(ax2, 0.15, 6.7, 9.6, 2.95, "삼성 FY26 OP",
         "보수 371  ·  베이스 395  ·  강세 413\nEPS 4.4만 / 4.8만 / 5.2만",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=11, bfs=8.6)
    _box(ax2, 0.15, 3.4, 9.6, 2.95, "닉스 FY26 OP",
         "보수 236  ·  베이스 273  ·  강세 292\n영업EPS 25만 / 29만 / 31만",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=11, bfs=8.6)
    _box(ax2, 0.15, 0.2, 9.6, 2.9, "2027",
         "삼성 OP 555  ·  닉스 410\n거리 499 / 415와 닉스는 거의 같음",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=11, bfs=8.6)
    fig.tight_layout()
    _save(fig, "05_fy.png")


def chart_crosscheck():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.4), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("크로스체크  ·  NVIDIA 원가와 $279B 약정", loc="left", fontsize=13.3, color=NAVY)

    _box(ax, 0.2, 5.2, 5.75, 4.45, "GPM 3.5%p의 달러",
         "3Q $108B × 3.5%p ≈ $3.8B 추가 COGS\n메모리 70%면 분기 $2.7B ≈ 3.7조\n한·미 3사 분배 시 국내 +2.2조/분기\n가격·비트 모델의 증분과 같은 자릿수",
         fc=BLUE_BG, ec="#93C5FD", title_c=NAVY2, fs=12, bfs=8.7)
    _box(ax, 6.15, 5.2, 5.65, 4.45, "공급약정 $279B",
         "잔여 FY27–29에 $92+$87+$88B\n1,380원 ≈ 3년 367조 조달\n한국 비중 60%면 연 73조\n이미 2Q 런레이트 안에 들어 있음",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=8.7)
    _box(ax, 0.2, 0.25, 11.6, 4.6, "그래서 숫자를 더 올리지 않는 이유",
         "약정은 ‘신규 수요’가 아니라 이미 깔린 조달이다. 콜이 바꾸는 것은 기울기 — 4Q·2027 가격이 안 꺾인다는 것.\n"
         "비트는 캐파 제약. DX 적자와 키옥시아 일회성은 영업과 분리.",
         fc=LIGHT, ec="#CBD5E1", title_c=NAVY, fs=12, bfs=9.0)
    _save(fig, "06_crosscheck.png")


def chart_watch():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.45), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("깨지면 / 확인되면", loc="left", fontsize=13.5, color=NAVY)

    _box(ax, 0.2, 5.15, 3.75, 4.5, "확인",
         "3Q DRAM +18% 근처\nHBM4 삼성 3배 · 닉스 램프\nNVDA 3Q GPM ≈ 74%\nLTA가 가격을 안 깎음",
         fc=OK_BG, ec="#86EFAC", title_c=GREEN, fs=12, bfs=8.8)
    _box(ax, 4.15, 5.15, 3.75, 4.5, "열린 것",
         "4Q가 120인가 133인가\n2027 HBM +50 vs +79\n삼성 HBM 점유율 38%\n용인·M15X 실제 비트",
         fc=WARN_BG, ec=GOLD, title_c=ORANGE, fs=12, bfs=8.8)
    _box(ax, 8.1, 5.15, 3.7, 4.5, "깨짐",
         "토큰 이익 소멸\nNVDA 4Q GPM <70%\n캐파가 가격을 붕괴\nDX 적자 확대 > 메모리",
         fc=BAD_BG, ec="#FCA5A5", title_c=RED, fs=12, bfs=8.8)
    _box(ax, 0.2, 0.25, 11.6, 4.55, "필자",
         "3Q는 거리에서 크게 안 벗어난다. 콜의 추정 가치는 4Q 감익을 취소하고 2027 가격을 유지하는 것.\n"
         "매수·매도 추천이 아니다. 영업 추정이며 키옥시아·지분증권은 제외.",
         fc=PURPLE_BG, ec="#D8B4FE", title_c=PURPLE, fs=12, bfs=9.1)
    _save(fig, "07_watch.png")


def main():
    _font()
    chart_bridge()
    chart_price()
    chart_samsung()
    chart_hynix()
    chart_fy()
    chart_crosscheck()
    chart_watch()
    print("done", OUT_DIR)


if __name__ == "__main__":
    main()
