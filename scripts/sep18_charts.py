#!/usr/bin/env python3
"""9월 18일 브리핑용 차트. 한글은 WenQuanYi Micro Hei."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, text as mtext
from matplotlib.patches import FancyBboxPatch

OUT = Path("/workspace/lectures/assets/sep18")
FONT_DIR = Path("/workspace/lectures/assets/fonts")
NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GREEN = "#166534"
RED = "#991B1B"
GRAY = "#4B5563"
BLUE = "#3B6F9E"
LIGHT = "#EEF2F8"


def _ensure_kr_font() -> Path:
    local = FONT_DIR / "NotoSansKR-Regular.otf"
    if local.exists():
        return local
    # 잘못된 확장자로 받은 파일도 재사용
    alt = FONT_DIR / "NotoSansKR-Regular.ttf"
    if alt.exists() and alt.stat().st_size > 1_000_000:
        return alt
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    import urllib.request

    url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Regular.otf"
    urllib.request.urlretrieve(url, local)
    return local


def _font():
    candidates = [
        _ensure_kr_font(),
        Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"),
    ]
    for p in candidates:
        if p.exists():
            font_manager.fontManager.addfont(str(p))
            name = font_manager.FontProperties(fname=str(p)).get_name()
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["axes.formatter.use_mathtext"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["axes.edgecolor"] = "#D5DCE6"
    plt.rcParams["axes.labelcolor"] = NAVY
    plt.rcParams["xtick.color"] = GRAY
    plt.rcParams["ytick.color"] = GRAY


def _save(fig, name: str) -> Path:
    # Noto/WQY CJK 글꼴은 ASCII 공백 폭이 0이라 제목이 붙는다.
    for artist in fig.findobj(mtext.Text):
        txt = artist.get_text()
        if txt and " " in txt:
            artist.set_text(txt.replace(" ", "\u3000"))
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return path


def chart_market() -> Path:
    labels = [
        "KOSPI\n+2.66%",
        "KOSDAQ\n+0.60%",
        "삼성전자\n+3.37%",
        "SK하이닉스\n+6.42%",
        "9/17 SOX\n+3.1%",
        "9/17 나스닥\n+1.7%",
    ]
    vals = [2.66, 0.60, 3.37, 6.42, 3.1, 1.7]
    colors = [NAVY, BLUE, GREEN, GREEN, NAVY2, GOLD]
    fig, ax = plt.subplots(figsize=(8.6, 3.55))
    bars = ax.bar(labels, vals, color=colors, width=0.62)
    for b, v in zip(bars, vals):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + 0.12,
            f"+{v:g}%",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color=NAVY,
        )
    ax.set_ylim(0, 7.6)
    ax.set_ylabel("전일 대비 (%)")
    ax.set_title("9/18 — 금리 산은 넘고, 반도체가 지수를 다시 밀었다", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(
        0.01,
        0.97,
        "KOSPI 6,894.23 (+178.82)  ·  삼성 261,000  ·  하이닉스 1,857,000  ·  SOX는 9/17 종가",
        transform=ax.transAxes,
        fontsize=7.6,
        color=GRAY,
        va="top",
    )
    return _save(fig, "01_market_rebound.png")


def chart_flows() -> Path:
    labels = ["개인", "외국인", "기관", "기타법인"]
    vals = [-3.59, 0.43, 1.50, 1.67]
    colors = [RED if v < 0 else GREEN for v in vals]
    fig, ax = plt.subplots(figsize=(8.6, 3.55))
    bars = ax.bar(labels, vals, color=colors, width=0.55)
    ax.axhline(0, color="#D0D7E2", lw=1)
    for b, v in zip(bars, vals):
        y = v + (0.12 if v >= 0 else -0.22)
        ax.text(
            b.get_x() + b.get_width() / 2,
            y,
            f"{v:+.2f}조",
            ha="center",
            va="bottom" if v >= 0 else "top",
            fontsize=10,
            fontweight="bold",
            color=NAVY,
        )
    ax.set_ylabel("코스피 순매수 (조 원)")
    ax.set_title("개인 3.6조 매도 = 기관·자사주·외인이 받음", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.set_ylim(-4.4, 2.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(
        0.01,
        0.04,
        "KRX 정규장. NXT 합산 시 외인 +0.98 / 기관 +1.72 / 개인 −4.37조. 외인은 하이닉스 +1.33조, 삼성 −0.46조.",
        transform=ax.transAxes,
        fontsize=7.5,
        color=GRAY,
    )
    return _save(fig, "02_flows.png")


def chart_boj_yen() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.55))
    steps = ["2024.3\n마이너스 종료", "2026.6\n1.00%", "2026.9/18\n1.25%"]
    rates = [0.0, 1.00, 1.25]
    ax.plot(steps, rates, "o-", color=NAVY, lw=2.4, ms=8)
    for x, y in zip(steps, rates):
        ax.annotate(f"{y:.2f}%", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=NAVY, fontweight="bold")
    ax.annotate(
        "금리 올렸는데\n달러/엔 157.12\n(+1.15, 약세)",
        xy=(2, 1.25),
        xytext=(1.35, 0.35),
        fontsize=8.5,
        color=RED,
        fontweight="bold",
        arrowprops=dict(arrowstyle="->", color=RED, lw=1.1),
    )
    ax.set_ylim(-0.15, 1.7)
    ax.set_ylabel("BOJ 정책금리 (%)")
    ax.set_title("BOJ는 올렸는데 엔은 약세  —  7-2, 추가 매파 신호는 약함", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(
        0.01,
        0.04,
        "반대 2명: 아사다·사토. 성명은 ‘계속 올리겠다’이나 7월과 문구 변화는 제한. 원/달러 종가 1,383.3.",
        transform=ax.transAxes,
        fontsize=7.5,
        color=GRAY,
    )
    return _save(fig, "03_boj_yen.png")


def chart_nodes() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    boxes = [
        (0.25, 1.55, "1. 연산\nGPU·ASIC", "풀림", GREEN, "#E8F5E9"),
        (2.65, 1.55, "2. 메모리\nHBM·DRAM·NAND", "지금 병목", RED, "#FDECEA"),
        (5.05, 1.55, "3. 에너지\n전력·효율·SMR", "가장 어려움", GOLD, "#FFF8E7"),
        (7.45, 1.55, "4. 자본\n금리·회사채", "마지막 노드", NAVY2, "#E8F1FB"),
    ]
    for x, y, title, tag, edge, fill in boxes:
        rec = FancyBboxPatch((x, y), 2.2, 1.55, boxstyle="round,pad=0.04,rounding_size=0.12", facecolor=fill, edgecolor=edge, lw=1.8)
        ax.add_patch(rec)
        ax.text(x + 1.1, y + 0.95, title, ha="center", va="center", fontsize=10, color=NAVY, fontweight="bold")
        ax.text(x + 1.1, y + 0.32, tag, ha="center", va="center", fontsize=9, color=edge, fontweight="bold")
    for x in (2.45, 4.85, 7.25):
        ax.annotate("", xy=(x + 0.18, 2.3), xytext=(x - 0.18, 2.3), arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.6))
    ax.text(5, 3.85, "노드 = 수급이 깨진 정류장. 거기가 돈 되는 자리", ha="center", fontsize=12, color=NAVY, fontweight="bold")
    ax.text(5, 0.45, "에너지가 풀리면 실리콘 병목이 다시 올라온다  ·  정지훈, 『정지 AI 투자 강의』", ha="center", fontsize=8, color=GRAY)
    return _save(fig, "04_nodes.png")


def chart_memory_gap() -> Path:
    years = ["2027", "2028"]
    dram = [8.7, 9.7]
    nand = [6.1, 5.5]
    x = range(len(years))
    fig, ax = plt.subplots(figsize=(8.6, 3.55))
    w = 0.34
    b1 = ax.bar([i - w / 2 for i in x], dram, width=w, color=NAVY, label="DRAM 부족률")
    b2 = ax.bar([i + w / 2 for i in x], nand, width=w, color=GOLD, label="NAND 부족률")
    for bars in (b1, b2):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.15, f"{b.get_height():g}%", ha="center", fontsize=9, color=NAVY, fontweight="bold")
    ax.set_xticks(list(x))
    ax.set_xticklabels(years)
    ax.set_ylim(0, 12)
    ax.set_ylabel("공급−수요 부족 (%)")
    ax.set_title("Citi: 지속학습 AI가 메모리 부족을 2031년까지 연장", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.legend(frameon=False, loc="upper left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(
        0.99,
        0.04,
        "HBM 비트 수요 +62%(27) / +69%(28). DRAM 수요 +30/+35 vs 공급 +19/+22. NAND +29/+33 vs +21/+25.",
        transform=ax.transAxes,
        ha="right",
        fontsize=7.4,
        color=GRAY,
    )
    return _save(fig, "05_memory_gap.png")


def chart_us_map() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.15)
    ax.axis("off")
    items = [
        (0.3, 1.15, "Indiana\nWest Lafayette", "HBM 후공정\n확정 트랙", "$40억+ · 2029H2", GREEN, "#E8F5E9"),
        (3.5, 1.15, "Ohio\nIntel Fab", "메모리 생산\n협의 중", "DRAM/NAND 미정", GOLD, "#FFF8E7"),
        (6.7, 1.15, "New York\nUpstate", "Solidigm NAND\n검토 단계", "다롄 분산 · 미결정", NAVY2, "#E8F1FB"),
    ]
    ax.text(5, 3.8, "하이닉스 미국 3축 — 한 뉴스처럼 묶지 말 것", ha="center", fontsize=12, color=NAVY, fontweight="bold")
    for x, y, title, mid, bot, edge, fill in items:
        rec = FancyBboxPatch((x, y), 2.95, 2.15, boxstyle="round,pad=0.04,rounding_size=0.12", facecolor=fill, edgecolor=edge, lw=1.8)
        ax.add_patch(rec)
        ax.text(x + 1.48, y + 1.68, title, ha="center", va="center", fontsize=10, color=NAVY, fontweight="bold")
        ax.text(x + 1.48, y + 1.05, mid, ha="center", va="center", fontsize=9.5, color=edge, fontweight="bold")
        ax.text(x + 1.48, y + 0.38, bot, ha="center", va="center", fontsize=8.4, color=GRAY)
    ax.text(5, 0.38, "Reuters 9/16 Ohio · 9/18 Solidigm. 하이닉스 “결정된 사항 없다.” CXMT 베이징 NAND는 같은 날, 별개 축.", ha="center", fontsize=7.6, color=GRAY)
    return _save(fig, "06_us_footprint.png")


def chart_korea_gdp() -> Path:
    years = ["2026", "2027", "2028"]
    citi = [3.7, 3.1, 3.0]
    bok = [3.3, 2.9, None]
    fig, ax = plt.subplots(figsize=(8.6, 3.55))
    ax.plot(years, citi, "o-", color=NAVY, lw=2.4, ms=8, label="Citi 실질 GDP")
    ax.plot(years[:2], bok[:2], "s--", color=GOLD, lw=2.0, ms=7, label="한은 8월")
    for x, y in zip(years, citi):
        ax.annotate(f"{y:.1f}%", (x, y), textcoords="offset points", xytext=(0, 8), ha="center", fontsize=9, color=NAVY, fontweight="bold")
    ax.set_ylim(2.4, 4.2)
    ax.set_ylabel("%")
    ax.set_title("Citi: 반도체 호황이 한국 성장률을 2028년까지 3%대에 묶는다", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.legend(frameon=False, loc="upper right")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(
        0.01,
        0.04,
        "반도체 수출 +175%(26) / +41%(27). 실질 GDP 기여 +3.2%p, 명목 +15.6%p. 명목 GDP 25%는 1981년 이후 최고 가정.",
        transform=ax.transAxes,
        fontsize=7.4,
        color=GRAY,
    )
    return _save(fig, "07_korea_gdp.png")


def chart_power_deal() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.55))
    labels = ["2027–28\n초기 인도", "워런트 한도\n최대 구매"]
    vals = [2.4, 8.0]
    colors = [NAVY, GOLD]
    bars = ax.bar(labels, vals, color=colors, width=0.46)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 0.18, f"${v:g}bn", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.set_ylim(0, 9.4)
    ax.set_ylabel("억 달러")
    ax.set_title("Amazon × Generac — 비상발전기가 캡엑스의 다음 영수증", loc="left", color=NAVY, fontsize=12, pad=10)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.text(
        0.01,
        0.04,
        "8-K 9/16. 비상발전기(UPS가 아님). 아마존 워런트 최대 169만주 @ $200.93. 한국 전선주는 장중 가온 +18~22%.",
        transform=ax.transAxes,
        fontsize=7.5,
        color=GRAY,
    )
    return _save(fig, "08_generac.png")


def chart_bottoms() -> Path:
    fig, axes = plt.subplots(1, 3, figsize=(8.6, 3.75))
    specs = [
        (
            "V자 — 제일 안 나옴",
            [0, 0.35, 0.55, 0.78, 1.0],
            [0.92, 0.52, 0.42, 0.82, 1.00],
            GREEN,
            "2003 이라크 · 2020 팬데믹\n양적완화 없이 드묾",
        ),
        (
            "W자 — 제일 많음",
            [0, 0.22, 0.40, 0.58, 0.78, 1.0],
            [1.00, 0.44, 0.70, 0.48, 0.66, 0.92],
            GOLD,
            "2~4개월 소화 · 전저점 필수 아님\n이은택: 지금 여기",
        ),
        (
            "트리플 — 위기형",
            [0, 0.16, 0.32, 0.48, 0.64, 0.80, 1.0],
            [1.00, 0.52, 0.72, 0.48, 0.70, 0.44, 0.94],
            RED,
            "1998 · 2000 · 2008\n2~3분기 · 지금은 해당 없음",
        ),
    ]
    for ax, (title, xs, ys, color, note) in zip(axes, specs):
        ax.plot(xs, ys, color=color, lw=2.4)
        ax.fill_between(xs, ys, 0.40, color=color, alpha=0.10)
        ax.set_xlim(0, 1)
        ax.set_ylim(0.28, 1.08)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_title(title, color=NAVY, fontsize=10.5, fontweight="bold", pad=8)
        ax.text(0.5, 0.03, note, ha="center", va="bottom", fontsize=8, color=GRAY, transform=ax.transAxes)
        for s in ax.spines.values():
            s.set_color("#D5DCE6")
    fig.suptitle("25%+ 급락 뒤 바닥은 세 종류  —  차트로 전망하지 말고 심리로 읽는다", color=NAVY, fontsize=11.5, fontweight="bold", y=1.02)
    fig.tight_layout()
    return _save(fig, "10_bottom_shapes.png")


def chart_and_gate() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.75))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.text(5, 3.95, "버블 붕괴는 OR가 아니라 AND  —  5월 Gravity Rules", ha="center", fontsize=12, color=NAVY, fontweight="bold")

    left = FancyBboxPatch((0.25, 1.15), 4.3, 2.45, boxstyle="round,pad=0.04,rounding_size=0.12", facecolor="#FFF8E7", edgecolor=GOLD, lw=1.8)
    right = FancyBboxPatch((5.45, 1.15), 4.3, 2.45, boxstyle="round,pad=0.04,rounding_size=0.12", facecolor="#E8F1FB", edgecolor=NAVY2, lw=1.8)
    ax.add_patch(left)
    ax.add_patch(right)
    ax.text(2.4, 3.28, "1. Breaking New Highs", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(7.6, 3.28, "2. No Way Back", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(2.4, 2.45, "10년물 5.0~5.3%\n터치가 아니라 추세 돌파\n이번 주 5.041 → 4.95", ha="center", va="center", fontsize=9, color=GRAY)
    ax.text(7.6, 2.45, "인플레가 외통수여야 함\n헤드라인 3.4% 횡보\n코어 2.5→2.4 하향", ha="center", va="center", fontsize=9, color=GRAY)
    ax.text(2.4, 1.42, "미충족  ·  조건 해제", ha="center", fontsize=10, color=GOLD, fontweight="bold")
    ax.text(7.6, 1.42, "미충족  ·  아직 하향", ha="center", fontsize=10, color=NAVY2, fontweight="bold")
    ax.text(5, 0.55, "AND", ha="center", fontsize=13, color=RED, fontweight="bold")
    ax.text(5, 0.18, "지금은 붕괴 시그널이 아니다. 5%는 위험 신호일 뿐 방아쇠가 아님", ha="center", fontsize=8.2, color=GRAY)
    return _save(fig, "11_and_gate.png")


def chart_misery() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.75))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.text(5, 3.92, "꿀팁 두 개  —  고통지수의 왕 + 주가가 GDP를 선행", ha="center", fontsize=11.5, color=NAVY, fontweight="bold")

    left = FancyBboxPatch((0.25, 0.55), 4.55, 3.05, boxstyle="round,pad=0.04,rounding_size=0.14", facecolor="#FDECEA", edgecolor=RED, lw=1.6)
    right = FancyBboxPatch((5.2, 0.55), 4.55, 3.05, boxstyle="round,pad=0.04,rounding_size=0.14", facecolor="#E8F5E9", edgecolor=GREEN, lw=1.6)
    ax.add_patch(left)
    ax.add_patch(right)
    ax.text(2.52, 3.25, "고통지수 = 실업 + 물가", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(7.47, 3.25, "주가가 GDP를 6~12개월 선행", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(
        2.52,
        2.15,
        "저물가: 실업률이 왕\n실업↑ → 주식 매도\n고물가: 인플레가 왕\n2022 CPI 6월 9.1%\n→ S&P 10/12, 코스피 9/30",
        ha="center",
        va="center",
        fontsize=8.8,
        color=GRAY,
    )
    ax.text(
        7.47,
        2.15,
        "같은 해 주가↔GDP 는 약함\n작년 코스피 → 올해 성장\n2025 +75.6% (이사 70%)\n한은 연초 1.6~1.8\nCiti 지금은 3.7",
        ha="center",
        va="center",
        fontsize=8.8,
        color=GRAY,
    )
    ax.text(5, 0.22, "폭락 뒤 6~12개월은 성장 하향 → 장기채. 내년 GDP로 지금 주가를 끌 수는 없다.", ha="center", fontsize=8, color=GRAY)
    return _save(fig, "12_misery_lead.png")


def chart_flywheel() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.75))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.text(5, 3.88, "AI는 한 바퀴가 아니다  —  디지털과 피지컬이 시차를 두고 동시에 돈다", ha="center", fontsize=11.5, color=NAVY, fontweight="bold")

    left = FancyBboxPatch((0.25, 0.55), 4.55, 3.0, boxstyle="round,pad=0.04,rounding_size=0.14", facecolor="#E8F1FB", edgecolor=NAVY2, lw=1.6)
    right = FancyBboxPatch((5.2, 0.55), 4.55, 3.0, boxstyle="round,pad=0.04,rounding_size=0.14", facecolor="#FFF8E7", edgecolor=GOLD, lw=1.6)
    ax.add_patch(left)
    ax.add_patch(right)
    ax.text(2.52, 3.2, "디지털 AI 플라이휠", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(7.47, 3.2, "피지컬 AI 플라이휠", ha="center", fontsize=11, color=NAVY, fontweight="bold")
    ax.text(2.52, 2.35, "자본 → 에너지 → 토큰\nAnthropic = 명품 단가\nGoogle = 원가 + 번들\nOpenAI = 가격↓ → 사용량↑", ha="center", va="center", fontsize=8.8, color=GRAY)
    ax.text(7.47, 2.35, "로봇 · 공장 · 자동차\n디지털보다 늦게 뜨지만\n같은 메모리·전력 노드를 씀\n다음 견인차는 삼전닉스만이 아님", ha="center", va="center", fontsize=8.8, color=GRAY)
    ax.text(5, 0.22, "이익을 못 내는 게 아니라 안 내는 구간. 임계를 넘으면 캐피탈 노드가 스스로 돈다.", ha="center", fontsize=8, color=GRAY)
    return _save(fig, "09_flywheel.png")


def chart_box() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.75))
    xs = [0.00, 0.18, 0.38, 0.58, 0.78, 1.00]
    ys = [9115, 7800, 5594, 6800, 6400, 6894]
    ax.plot(xs, ys, color=NAVY, lw=2.4)
    ax.fill_between(xs, ys, 5200, color=NAVY2, alpha=0.08)
    ax.axhspan(7150, 7200, color=GOLD, alpha=0.18, zorder=0)
    ax.axhline(9115, color=GOLD, ls="--", lw=1.0)
    ax.axhline(8000, color=RED, ls=":", lw=1.1)
    ax.axhline(6000, color=GRAY, ls="--", lw=1.0)
    ax.axhline(5594, color=RED, ls=":", lw=0.9)
    ax.scatter([1.0], [6894], color=GREEN, s=36, zorder=3)
    ax.text(1.0, 7020, "9/18  6,894", ha="right", fontsize=8, color=GREEN, fontweight="bold")
    ax.text(0.18, 9280, "6/22 고점 9,115", fontsize=7.5, color=GOLD)
    ax.text(0.18, 8120, "윤지호: 8,000은 아직 안 연다", fontsize=7.5, color=RED)
    ax.text(0.50, 7360, "7,150-7,200  네 번째 시도", fontsize=8, color=NAVY, fontweight="bold")
    ax.text(0.18, 6180, "6,000 지지, 트레이딩 바이", fontsize=7.5, color=GRAY)
    ax.text(0.38, 5380, "7/30  5,594", fontsize=7.5, color=RED)
    ax.set_xlim(0, 1)
    ax.set_ylim(5200, 9600)
    ax.set_xticks([])
    ax.set_yticks([5600, 6000, 6900, 7200, 8000, 9100])
    ax.set_title("윤지호 박스  —  위로도 아래로도 쉽지 않다", color=NAVY, fontsize=12, fontweight="bold")
    ax.text(
        0.5,
        -0.08,
        "추세 상승을 기대하기는 어렵다. 답이 나와야 상단이 열린다. 숫자는 종가, 고점, 저점.",
        ha="center",
        va="top",
        fontsize=7.6,
        color=GRAY,
        transform=ax.transAxes,
    )
    return _save(fig, "13_box_range.png")


def chart_nvidia_cash() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.75))
    labels = ["매출총이익률", "순이익 대비 영업현금"]
    vals = [75.0, 40.3]
    colors = [NAVY2, RED]
    bars = ax.bar(labels, vals, color=colors, width=0.55)
    ax.set_ylim(0, 100)
    ax.set_ylabel("퍼센트", color=GRAY)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 2.2, f"{v:.1f} pct", ha="center", fontsize=12, color=NAVY, fontweight="bold")
    ax.set_title("엔비디아 Q2 FY27  —  마진 75, 현금은 40", color=NAVY, fontsize=12, fontweight="bold")
    ax.text(
        0.5,
        -0.16,
        "매출 96.2B, 순이익 59.7B, 영업현금 24.1B. 매출채권 63.1B, DSO 45일에서 60일.\n"
        "지분증권 평가이익 Q2 7.8B / 상반기 23.7B. CDS 7월 급등은 미확인.",
        ha="center",
        va="top",
        fontsize=7.6,
        color=GRAY,
        transform=ax.transAxes,
    )
    return _save(fig, "14_nvidia_cash.png")


def chart_token_pq() -> Path:
    fig, ax = plt.subplots(figsize=(8.6, 3.75))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 4.2)
    ax.axis("off")
    ax.text(5, 3.92, "토큰은 P가 내려도 Q가 더 늘면 돈이 돈다", ha="center", fontsize=12, color=NAVY, fontweight="bold")
    left = FancyBboxPatch((0.25, 0.7), 4.55, 2.85, boxstyle="round,pad=0.04,rounding_size=0.14", facecolor="#FDECEA", edgecolor=RED, lw=1.6)
    right = FancyBboxPatch((5.2, 0.7), 4.55, 2.85, boxstyle="round,pad=0.04,rounding_size=0.14", facecolor="#E8F5E9", edgecolor=GREEN, lw=1.6)
    ax.add_patch(left)
    ax.add_patch(right)
    ax.text(2.52, 3.22, "P  ↓   단가", ha="center", fontsize=12, color=RED, fontweight="bold")
    ax.text(7.47, 3.22, "Q  ↑   사용량", ha="center", fontsize=12, color=GREEN, fontweight="bold")
    ax.text(
        2.52,
        2.05,
        "OpenRouter 가중단가\n8월 MoM -28 pct\nYoY -56 pct\nCiti 추론단가 1.33달러",
        ha="center",
        va="center",
        fontsize=8.8,
        color=GRAY,
    )
    ax.text(
        7.47,
        2.05,
        "OpenRouter 볼륨\n8월 MoM +47 pct\nYoY 28배\n지출은 +7 pct / 12배",
        ha="center",
        va="center",
        fontsize=8.8,
        color=GRAY,
    )
    ax.text(
        5,
        0.28,
        "방송 31 pct, 2,400 pct, 초당 1,000억은 원소스를 못 박지 못함. 방향은 JPM이 받는다.",
        ha="center",
        fontsize=7.8,
        color=GRAY,
    )
    return _save(fig, "15_token_pq.png")


def main():
    _font()
    paths = [
        chart_market(),
        chart_flows(),
        chart_boj_yen(),
        chart_nodes(),
        chart_memory_gap(),
        chart_us_map(),
        chart_korea_gdp(),
        chart_power_deal(),
        chart_flywheel(),
        chart_bottoms(),
        chart_and_gate(),
        chart_misery(),
        chart_box(),
        chart_nvidia_cash(),
        chart_token_pq(),
    ]
    for p in paths:
        print(p, p.stat().st_size)


if __name__ == "__main__":
    main()
