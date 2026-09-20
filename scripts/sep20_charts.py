#!/usr/bin/env python3
"""9월 20일 일요일 다이제스트 차트. 한글은 WenQuanYi / Noto CJK."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager, text as mtext
from matplotlib.patches import FancyBboxPatch

from sep20_data import (
    CXL_UTIL_NOW,
    CXL_UTIL_POOL,
    FRI_DOW_PCT,
    FRI_NASDAQ_PCT,
    FRI_SOX_PCT,
    FRI_SPX_PCT,
    FRI_WTI,
    OIL_SIREN,
    TENY_FRI_PRINT,
    TENY_SIREN,
    TENY_WORKING_HI,
    TENY_WORKING_LO,
    THU_DOW_PCT,
    THU_NASDAQ_PCT,
    THU_SOX_NAMES,
    THU_SOX_PCT,
    THU_SPX_PCT,
    THU_TENY_CMT,
)

OUT = Path("/workspace/lectures/assets/sep20")
FONT_DIR = Path("/workspace/lectures/assets/fonts")
NAVY = "#0F2043"
NAVY2 = "#1E407C"
GOLD = "#B8943A"
GREEN = "#166534"
RED = "#991B1B"
GRAY = "#4B5563"
BLUE = "#3B6F9E"
LIGHT = "#EEF2F8"
AMBER = "#B45309"


def _ensure_kr_font() -> Path:
    local = FONT_DIR / "NotoSansKR-Regular.otf"
    if local.exists() and local.stat().st_size > 100_000:
        return local
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        import urllib.request

        url = "https://github.com/googlefonts/noto-cjk/raw/main/Sans/OTF/Korean/NotoSansCJKkr-Regular.otf"
        urllib.request.urlretrieve(url, local)
        if local.exists() and local.stat().st_size > 100_000:
            return local
    except Exception:
        pass
    return Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")


def _font() -> None:
    for p in (_ensure_kr_font(), Path("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")):
        if p.exists():
            font_manager.fontManager.addfont(str(p))
            name = font_manager.FontProperties(fname=str(p)).get_name()
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["axes.edgecolor"] = "#D5DCE6"
    plt.rcParams["axes.labelcolor"] = NAVY
    plt.rcParams["xtick.color"] = GRAY
    plt.rcParams["ytick.color"] = GRAY


def _save(fig, name: str) -> Path:
    for artist in fig.findobj(mtext.Text):
        txt = artist.get_text()
        if txt and " " in txt:
            artist.set_text(txt.replace(" ", "\u3000"))
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    fig.savefig(path, dpi=160, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return path


def _box(ax, x, y, w, h, facecolor, edge=NAVY, lw=1.2):
    p = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        facecolor=facecolor,
        edgecolor=edge,
        linewidth=lw,
        transform=ax.transAxes,
        clip_on=False,
    )
    ax.add_patch(p)
    return p


def chart_clock() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(11.2, 3.6))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("시계 분리: 목 PDF / 금 종가 / 토 대담 / 일 휴장", loc="left", color=NAVY, fontsize=13, pad=8)
    layers = [
        (0.02, "#E8F1FB", "목 9/17", "미국 안도 반등\nSOX +3.1 · 10년 4.94\nPDF 3편 원문"),
        (0.265, "#E8F5E9", "금 9/18", "FOMC·BOJ 다음날\n나스닥 +0.40 · SOX +2.78\nWTI 100.30달러"),
        (0.51, "#FFF8E7", "토 9/19", "메인 8편 소화\n게스트 논리만\n새 테이프 없음"),
        (0.755, "#F3F4F6", "일 9/20", "한국 휴장\n추가 대담 4+TG\n사이렌 미발화"),
    ]
    for x, color, title, body in layers:
        _box(ax, x, 0.12, 0.225, 0.72, color)
        ax.text(x + 0.112, 0.70, title, ha="center", va="center", fontsize=13, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(x + 0.112, 0.38, body, ha="center", va="center", fontsize=10, color=GRAY, transform=ax.transAxes, linespacing=1.45)
    return _save(fig, "01_clock.png")


def chart_tape() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.4, 4.2))
    labels = ["다우", "S&P", "나스닥", "SOX"]
    thu = [THU_DOW_PCT, THU_SPX_PCT, THU_NASDAQ_PCT, THU_SOX_PCT]
    fri = [FRI_DOW_PCT, FRI_SPX_PCT, FRI_NASDAQ_PCT, FRI_SOX_PCT]
    x = range(len(labels))
    w = 0.36
    b1 = ax.bar([i - w / 2 for i in x], thu, w, color=NAVY2, label="목 9/17 (PDF)")
    b2 = ax.bar([i + w / 2 for i in x], fri, w, color=GOLD, label="금 9/18 종가")
    ax.axhline(0, color="#D5DCE6", lw=1)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels)
    ax.set_ylabel("%")
    ax.set_title("같은 SOX라도 날이 다르다: 목 안도 vs 금 FOMC 다음날", loc="left", color=NAVY, fontsize=12)
    ax.legend(frameon=False, loc="upper left")
    for bars in (b1, b2):
        for rect in bars:
            h = rect.get_height()
            ax.text(
                rect.get_x() + rect.get_width() / 2,
                h + (0.08 if h >= 0 else -0.22),
                f"{h:+.2f}" if abs(h) < 1 else f"{h:+.1f}",
                ha="center",
                va="bottom" if h >= 0 else "top",
                fontsize=8,
                color=NAVY,
            )
    ax.set_ylim(-0.8, 4.0)
    fig.tight_layout()
    return _save(fig, "02_tape.png")


def chart_siren() -> Path:
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8))

    ax = axes[0]
    ax.set_xlim(4.6, 5.4)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel("미 10년물 %")
    ax.set_title("10년물: 터치 ≠ 안착. 사이렌 꺼짐", loc="left", color=NAVY, fontsize=11)
    ax.axvspan(TENY_WORKING_LO, TENY_WORKING_HI, color="#FFF8E7", label="워킹 4.95-5.01")
    ax.axvline(TENY_SIREN, color=RED, ls="--", lw=1.4, label="안착선 5.00")
    ax.plot([THU_TENY_CMT], [0.45], "o", color=NAVY2, ms=11)
    ax.text(THU_TENY_CMT, 0.62, f"목 {THU_TENY_CMT:.2f}", ha="center", fontsize=8, color=NAVY2)
    ax.plot([TENY_FRI_PRINT], [0.28], "D", color=GOLD, ms=9)
    ax.text(5.05, 0.18, f"금 장중 {TENY_FRI_PRINT:.3f}", ha="left", fontsize=8, color=AMBER)
    ax.text(4.62, 0.88, "문홍철: 장중 터치 ≠ 종가 5% 위", fontsize=8.5, color=GRAY, va="top")
    ax.legend(frameon=False, loc="upper right", fontsize=8)

    ax = axes[1]
    ax.set_xlim(90, 125)
    ax.set_ylim(0, 1)
    ax.set_yticks([])
    ax.set_xlabel("WTI $")
    ax.set_title("유가: 100.30달러 ≪ 120. 사이렌 꺼짐", loc="left", color=NAVY, fontsize=11)
    ax.axvspan(90, 105, color="#E8F5E9")
    ax.axvline(OIL_SIREN, color=RED, ls="--", lw=1.4, label="사이렌 120")
    ax.plot([FRI_WTI], [0.4], "o", color=NAVY, ms=12)
    ax.text(FRI_WTI, 0.58, f"금 정산 ${FRI_WTI:.2f}", ha="center", fontsize=9, color=NAVY)
    ax.text(91, 0.82, "김학균: 유가 100$+ 가\n상단을 막았다 (판단)", fontsize=8.5, color=GRAY, va="top")
    ax.legend(frameon=False, loc="upper right", fontsize=8)
    fig.tight_layout()
    return _save(fig, "03_siren.png")


def chart_ai_panel() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(10.6, 4.0))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.set_title("MAIN 4 — 합의 세탁 금지. 세 갈래가 남는다", loc="left", color=NAVY, fontsize=13)
    cols = [
        (0.03, "#E8F1FB", "김광석", "구조 전환", "수출 9→20→25→40%\n8–9월 서술 48%\n한은 3.3 / 2.9\n반도체 국가 재편"),
        (0.35, "#FDECEA", "김영익", "기술=혁명\n주식=거품", "1930s · 닷컴 비유\n자본은 파괴된다\n한국 베타가 크다\n10Y–밸류 축"),
        (0.67, "#E8F5E9", "정주용", "인프라 미완", "DC 5조$는 비전\n스팟 안 떨어지면\n아직 버블 아님\n철도 안 놓고 버블?"),
    ]
    for x, color, name, tag, body in cols:
        _box(ax, x, 0.08, 0.30, 0.78, color)
        ax.text(x + 0.15, 0.76, name, ha="center", fontsize=13, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(x + 0.15, 0.60, tag, ha="center", fontsize=11, fontweight="bold", color=NAVY2, transform=ax.transAxes)
        ax.text(x + 0.15, 0.32, body, ha="center", va="center", fontsize=9.5, color=GRAY, transform=ax.transAxes, linespacing=1.45)
    return _save(fig, "04_ai_panel.png")


def chart_rate_camp() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(10.8, 4.1))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("금리인상 = 무조건 악재 공식 거부 — 이유는 네 갈래", loc="left", color=NAVY, fontsize=13)
    rows = [
        ("박병창", "선반영 · 성장↑금리↑", "추가 인상은 12월 한 차례 가설. 본인 입으로 estimate."),
        ("염승환", "다음날 소화 규칙", "첫날 조정 후 금리·유가 빠지면 신호. 동행=투자 시대."),
        ("김학균", "유가·장기금리가 상단", "기준 ~4% vs 시장 ~5.3%. 둘만 안정되면 방향 +."),
        ("문홍철", "터치 vs 종가", "장중 5% ≠ 종가 5% 위. 성장·달러·재정과 결합."),
    ]
    for i, (name, tag, body) in enumerate(rows):
        y = 0.78 - i * 0.22
        _box(ax, 0.02, y, 0.96, 0.19, LIGHT)
        ax.text(0.04, y + 0.12, name, fontsize=12, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(0.22, y + 0.12, tag, fontsize=11, fontweight="bold", color=NAVY2, transform=ax.transAxes)
        ax.text(0.04, y + 0.045, body, fontsize=10, color=GRAY, transform=ax.transAxes)
    return _save(fig, "05_rate_camp.png")


def chart_intel_chain() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(11.0, 3.6))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("인텔 × 하이닉스 오하이오 — 탐색이지 계약이 아니다", loc="left", color=NAVY, fontsize=13)
    nodes = [
        (0.08, "하이닉스\n미국 디램?"),
        (0.30, "오하이오\n임차 또는 JV"),
        (0.52, "인디애나\nHBM 패키징"),
        (0.74, "미국산\n메모리 공급"),
        (0.92, "파운드리\n신뢰?"),
    ]
    for i, (x, label) in enumerate(nodes):
        _box(ax, x - 0.08, 0.38, 0.16, 0.36, "#E8F1FB")
        ax.text(x, 0.56, label, ha="center", va="center", fontsize=9, color=NAVY, transform=ax.transAxes)
        if i < len(nodes) - 1:
            ax.annotate(
                "",
                xy=(nodes[i + 1][0] - 0.085, 0.56),
                xytext=(x + 0.085, 0.56),
                xycoords=ax.transAxes,
                textcoords=ax.transAxes,
                arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.8),
            )
    ax.text(
        0.5,
        0.16,
        "로이터 9/16 소스. 하이닉스 ‘결정된 사항 없음’. 인텔은 추측이라 함. 제품 종류 미확인. 이미 반영? = 미잠금",
        ha="center",
        fontsize=9,
        color=RED,
        transform=ax.transAxes,
    )
    return _save(fig, "06_intel_chain.png")


def chart_sox_thu() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.6, 4.4))
    names = [n for n, _ in reversed(THU_SOX_NAMES)]
    vals = [v for _, v in reversed(THU_SOX_NAMES)]
    colors = [GOLD if n in ("ARM", "INTC") else NAVY2 for n in names]
    ax.barh(names, vals, color=colors)
    ax.set_xlabel("%")
    ax.set_title("목 9/17 SOX 개별 — PDF 인용 · 금요 종가와 섞지 말 것", loc="left", color=NAVY, fontsize=12)
    for y, v in enumerate(vals):
        ax.text(v + 0.08, y, f"+{v:.1f}", va="center", fontsize=8, color=NAVY)
    ax.set_xlim(0, 10.2)
    fig.tight_layout()
    return _save(fig, "07_sox_thu.png")


def chart_shipyard() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(10.6, 3.8))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("조선 — 이익↑ 멀티플↓. 리레이팅 3축은 수주 확인 전", loc="left", color=NAVY, fontsize=13)
    cols = [
        (0.03, "4행정 중속 엔진", "AIDC 전력 병목\nHD현대 육상 4GW는\n2030 캐파 목표\n한화엔진은 수주 가능성"),
        (0.35, "FDC 부유식 DC", "삼성중 2Q28 목표\nM3와 엔지니어링\nEPC 본계약은 아직\n한화오션 60MW AiP"),
        (0.67, "글로벌 함정", "해군 현대화\n수상함·잠수함 파이프\n핵심은 실제 전투함\n수주 연결 여부"),
    ]
    for x, title, body in cols:
        _box(ax, x, 0.10, 0.30, 0.74, "#FFF8E7")
        ax.text(x + 0.15, 0.72, title, ha="center", fontsize=12, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(x + 0.15, 0.38, body, ha="center", va="center", fontsize=9.5, color=GRAY, transform=ax.transAxes, linespacing=1.45)
    return _save(fig, "08_shipyard.png")


def chart_cxl() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.2, 4.0))
    labels = ["서버 할당\n~70% 중\n절반 미사용", "클라우드\n활성 ~35%", "풀링 후\n70–80%\n(회사)"]
    vals = [35, CXL_UTIL_NOW, CXL_UTIL_POOL]
    colors = [GRAY, NAVY2, GOLD]
    bars = ax.bar(labels, vals, color=colors)
    ax.set_ylabel("%")
    ax.set_ylim(0, 100)
    ax.set_title("엑시나 CXL — 스폰서 주장. HBM 대체가 아니라 보완", loc="left", color=NAVY, fontsize=12)
    for rect, v in zip(bars, vals):
        ax.text(rect.get_x() + rect.get_width() / 2, v + 2, f"{v}%", ha="center", fontsize=10, color=NAVY)
    ax.text(0.5, -0.22, "제목 ‘1만배’는 비전·은유. 공식 수요예측 아님.", ha="center", fontsize=9, color=RED, transform=ax.transAxes)
    fig.tight_layout()
    return _save(fig, "09_cxl.png")


def chart_calendar() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(10.8, 3.4))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("시계 — 주간 문장에 다년 서사를 넣지 말 것", loc="left", color=NAVY, fontsize=13)
    items = [
        (0.04, "이번 주~추석", "월·화·수 3거래일\n홀드·추격 금지\n10Y 터치 관전\noil ≪ 120"),
        (0.28, "배당 창", "삼전 기준일\n~9/28–30\n캘린더만"),
        (0.50, "10월 실적", "마이크론 10/1\n삼성 잠정 10/8\n닉스·삼성 10/20"),
        (0.72, "다년 · 넣지 말 것", "AI 혁명 vs 거품\nCXL · 821조\n금리–주가 단계론\nBOJ/엔캐리"),
    ]
    for i, (x, title, body) in enumerate(items):
        color = "#FDECEA" if i == 3 else LIGHT
        _box(ax, x, 0.10, 0.22, 0.74, color)
        ax.text(x + 0.11, 0.70, title, ha="center", fontsize=11, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(x + 0.11, 0.38, body, ha="center", va="center", fontsize=9, color=GRAY, transform=ax.transAxes, linespacing=1.4)
    return _save(fig, "10_calendar.png")


def chart_matrix() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(10.8, 5.0))
    guests = ["박병창", "이주연", "김민수", "김광석", "김영익", "정주용", "김학균", "문홍철", "염승환"]
    themes = ["금리≠악재", "10년 터치", "AI 호황", "밸류 경계", "수급 60일"]
    # 2=강긍정/동의, 1=부분, 0=해당없음/침묵, -1=반대 축
    grid = [
        [2, 1, 2, 0, 0],
        [1, 0, 1, 0, 2],
        [1, 2, 2, 0, 1],
        [0, 1, 2, 0, 0],
        [0, 2, 0, 2, 0],
        [0, 1, 2, 0, 0],
        [2, 2, 2, 0, 0],
        [2, 2, 1, 0, 0],
        [2, 1, 2, 0, 1],
    ]
    cmap = matplotlib.colors.ListedColormap(["#F3F4F6", "#FDECEA", "#FFF8E7", "#C6E6C8"])
    bounds = [-1.5, -0.5, 0.5, 1.5, 2.5]
    norm = matplotlib.colors.BoundaryNorm(bounds, cmap.N)
    im = ax.imshow(grid, cmap=cmap, norm=norm, aspect="auto")
    ax.set_xticks(range(len(themes)))
    ax.set_xticklabels(themes, fontsize=8)
    ax.set_yticks(range(len(guests)))
    ax.set_yticklabels(guests, fontsize=9)
    ax.set_title("패널 온도 — 합의처럼 보이지 않게. 회색=해당 축 발화 약함", loc="left", color=NAVY, fontsize=12)
    for i in range(len(guests)):
        for j in range(len(themes)):
            mark = {2: "●", 1: "◐", 0: "·", -1: "×"}[grid[i][j]]
            ax.text(j, i, mark, ha="center", va="center", fontsize=11, color=NAVY)
    fig.tight_layout()
    return _save(fig, "11_matrix.png")


def chart_flows() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    labels = ["외인\n(방송 ~1조)", "기관\n(방송 ~1.8조)"]
    vals = [1.0, 1.8]
    ax.bar(labels, vals, color=[NAVY2, GOLD])
    ax.set_ylabel("조 원")
    ax.set_title("815 금 19:00 촬영 수급 — 공시 원문 재대조", loc="left", color=NAVY, fontsize=12)
    for i, v in enumerate(vals):
        ax.text(i, v + 0.05, f"{v:.1f}조", ha="center", fontsize=10, color=NAVY)
    ax.set_ylim(0, 2.4)
    ax.text(0.5, -0.22, "토 PM 찐시황(촬영 토 10:30)과 시계가 다름.", ha="center", fontsize=9, color=RED, transform=ax.transAxes)
    fig.tight_layout()
    return _save(fig, "12_flows.png")


def chart_addon() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(11.0, 4.4))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("추가 대담 4 — MAIN이 아니다. 합의 세탁 금지", loc="left", color=NAVY, fontsize=13)
    cols = [
        (0.02, "#E8F1FB", "홍기빈", "암묵지·커먼스", "LLM은 도서관\n다음은 월드모델\n동작 데이터=평생 자산\n한 번 팔면 끝 아님"),
        (0.265, "#FDECEA", "박정호", "속도조절=면피", "CEO가 먼저 감속하면 됨\n훈련 중단은 반대\n검수 속도 < 개발\n소버린으로 따라잡기"),
        (0.51, "#FFF8E7", "신환종", "스티키 인플레", "10Y 터치는 관전\n안착 아님\n금=CB 대체 수요\n4분기는 신중"),
        (0.755, "#E8F5E9", "김효진", "자금이 약한 고리", "아스트라=에이전트\nCapEx는 돈 문제\nGPU 유동화는 초입\n10Y는 발목이지 끝 아님"),
    ]
    for x, color, name, tag, body in cols:
        _box(ax, x, 0.08, 0.225, 0.80, color)
        ax.text(x + 0.112, 0.76, name, ha="center", fontsize=12, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(x + 0.112, 0.62, tag, ha="center", fontsize=10, fontweight="bold", color=NAVY2, transform=ax.transAxes)
        ax.text(x + 0.112, 0.32, body, ha="center", va="center", fontsize=9, color=GRAY, transform=ax.transAxes, linespacing=1.4)
    return _save(fig, "13_addon.png")


def chart_ubs() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(8.8, 4.2))
    years = ["2025", "2026", "2027"]
    mem = [71, 367, 923]
    other = [435, 631, 524]
    x = range(len(years))
    b1 = ax.bar(list(x), mem, color=GOLD, label="메모리 (UBS 추정)")
    b2 = ax.bar(list(x), other, bottom=mem, color=NAVY2, label="비메모리 (UBS 추정)")
    ax.set_xticks(list(x))
    ax.set_xticklabels(years)
    ax.set_ylabel("십억 달러")
    ax.set_title("UBS AI CapEx — IB 추정. 방 합의·공식 전망 아님", loc="left", color=NAVY, fontsize=12)
    ax.legend(frameon=False, loc="upper left", fontsize=8)
    for i, (m, o) in enumerate(zip(mem, other)):
        ax.text(i, m + o + 20, f"{m + o}", ha="center", fontsize=9, color=NAVY)
    ax.set_ylim(0, 1650)
    ax.text(0.5, -0.22, "증가분 ~90%가 메모리 가격이라는 문장도 IB 추정. 잠금 금지.", ha="center", fontsize=9, color=RED, transform=ax.transAxes)
    fig.tight_layout()
    return _save(fig, "14_ubs.png")


def chart_physical() -> Path:
    _font()
    fig, ax = plt.subplots(figsize=(11.0, 4.0))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("피지컬 AI와 2027 PCB — 비전이지 수주 확정이 아니다", loc="left", color=NAVY, fontsize=13)
    left = [
        (0.03, "암묵지", "찌개·자전거·용접\n말로 안 됨\n센서 조끼는 수집\n협조가 병목"),
        (0.27, "커먼스", "한 번 스캔≠표준\n양파 썰기도 무한\n소득 흐름이 있어야\n노동이 협조"),
    ]
    for x, title, body in left:
        _box(ax, x, 0.10, 0.22, 0.74, "#E8F1FB")
        ax.text(x + 0.11, 0.70, title, ha="center", fontsize=11, fontweight="bold", color=NAVY, transform=ax.transAxes)
        ax.text(x + 0.11, 0.38, body, ha="center", va="center", fontsize=9, color=GRAY, transform=ax.transAxes, linespacing=1.4)
    nodes = [
        (0.54, "두산\nCCL"),
        (0.66, "이수\nMLB"),
        (0.78, "심텍\n모듈"),
        (0.90, "티엘비\nSoCAMM"),
    ]
    ax.text(0.72, 0.86, "브로커 유니버스 2027. 목표가≠합의", ha="center", fontsize=9, color=RED, transform=ax.transAxes)
    for i, (x, label) in enumerate(nodes):
        _box(ax, x - 0.055, 0.28, 0.11, 0.42, "#FFF8E7")
        ax.text(x, 0.49, label, ha="center", va="center", fontsize=8.5, color=NAVY, transform=ax.transAxes)
        if i < len(nodes) - 1:
            ax.annotate(
                "",
                xy=(nodes[i + 1][0] - 0.06, 0.49),
                xytext=(x + 0.06, 0.49),
                xycoords=ax.transAxes,
                textcoords=ax.transAxes,
                arrowprops=dict(arrowstyle="->", color=GOLD, lw=1.5),
            )
    ax.text(0.72, 0.14, "휴머노이드 필수 아님 · 바클레이즈 대량 보급은 2035 전후 시나리오", ha="center", fontsize=8.5, color=GRAY, transform=ax.transAxes)
    return _save(fig, "15_physical.png")


def main() -> None:
    paths = [
        chart_clock(),
        chart_tape(),
        chart_siren(),
        chart_ai_panel(),
        chart_rate_camp(),
        chart_intel_chain(),
        chart_sox_thu(),
        chart_shipyard(),
        chart_cxl(),
        chart_calendar(),
        chart_matrix(),
        chart_flows(),
        chart_addon(),
        chart_ubs(),
        chart_physical(),
    ]
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
