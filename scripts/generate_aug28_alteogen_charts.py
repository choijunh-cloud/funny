#!/usr/bin/env python3
"""8월 28일 알테오젠 ALT-B4 분석 차트."""

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


def chart_misread():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.1), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.2)
    ax.axis("off")
    ax.set_title(
        "시장이 읽은 것  vs  청구항이 말하는 것",
        loc="left",
        color=NAVY,
        fontsize=13.4,
        fontweight="bold",
        pad=8,
    )
    _box(
        ax,
        0.2,
        0.35,
        5.4,
        4.5,
        "기사/시장 오해",
        "“미국 할로자임, 국내 알테오젠이\n쓰는 것과 다른 자체 히알루로니다제”\n\n→ 새로운 효소 플랫폼이 등장했다\n→ ALT-B4 독점성이 깨진다\n→ 빅파마 L/O 매력이 떨어진다",
        fc=BAD_BG,
        ec="#F1B0B0",
        title_c=RED,
        fs=12,
        bfs=10,
    )
    _box(
        ax,
        6.4,
        0.35,
        5.4,
        4.5,
        "확인된 내용",
        "대표청구항 = 정제방법 · 제조방법\n서열로 정의된 신규 단백질이 아님\n\n→ Enhanze 계열 시밀러 공정\n→ 에피스: 플랫폼 사업 계획 없음\n→ 자사 신약/BS에 SC를 붙이려는 내재화",
        fc=OK_BG,
        ec="#A7D4B0",
        title_c=GREEN,
        fs=12,
        bfs=10,
    )
    ax.annotate(
        "",
        xy=(6.3, 2.6),
        xytext=(5.7, 2.6),
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=2.4),
    )
    _save(fig, "01_misread.png")


def chart_claims():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.4), dpi=170)
    ax.axis("off")
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6.2)
    ax.set_title(
        "신규 효소를 청구하려면 대표청구항이 달라야 한다",
        loc="left",
        color=NAVY,
        fontsize=13.2,
        fontweight="bold",
        pad=8,
    )

    headers = ["구분", "대표청구항이 되는 것", "이번 에피스 출원"]
    rows = [
        ["신규 효소\n(물질특허)", "특정 아미노산 서열로\n정의된 단백질/펩타이드", "없음"],
        ["WO2026/142299", "절단된 히알루로니다제를\n제거하는 제조방법", "공정 · CMC"],
        ["WO2026/142300", "카프릴산 + 심층여과로\n불순물(HCP)을 제거하는 정제방법", "공정 · CMC"],
        ["ALT-B4", "물질 + 조성물 + 용도\n+ 제조 특허 포트폴리오", "미국 물질특허 ~2043"],
    ]
    col_w = [2.3, 5.6, 3.5]
    x0, y0, row_h = 0.25, 5.35, 1.15
    x = x0
    for i, h in enumerate(headers):
        _box(ax, x, y0, col_w[i], 0.7, h, "", fc=NAVY, ec=NAVY, title_c="white", fs=10.5)
        x += col_w[i] + 0.1
    for r_i, row in enumerate(rows):
        x = x0
        y = y0 - (r_i + 1) * row_h
        fills = [LIGHT, BLUE_BG, OK_BG if r_i == 3 else WARN_BG]
        for c_i, val in enumerate(row):
            fc = fills[c_i] if c_i else (NAVY if r_i == 3 else LIGHT)
            tc = "white" if (c_i == 0 and r_i == 3) else NAVY
            _box(
                ax,
                x,
                y,
                col_w[c_i],
                row_h - 0.08,
                val,
                "",
                fc=fc,
                ec="#D0D7E2",
                title_c=tc,
                fs=9.4,
            )
            x += col_w[c_i] + 0.1
    ax.text(
        0.25,
        0.18,
        "국제조사(ISA): 핵심 청구항 신규성·진보성 부정. 선행 = 휴온스랩 + 알테오젠 + 2012 카프릴산 특허.",
        fontsize=8.6,
        color=GRAY,
    )
    _save(fig, "02_claims.png")


def chart_why_altb4():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.6), dpi=170)
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 6.4)
    ax.axis("off")
    ax.set_title(
        "빅파마가 Enhanze 시밀러 대신 ALT-B4를 사는 이유",
        loc="left",
        color=NAVY,
        fontsize=13.2,
        fontweight="bold",
        pad=6,
    )
    _box(
        ax,
        0.2,
        3.35,
        5.7,
        2.75,
        "경로 A  ·  Enhanze와 같은 효소",
        "특허 장벽이 무너지면 제품 차별화가 없다.\n같은 효소 → 같은 SC 스토리 → 가격 경쟁.\n조성물 특허는 상대 제품에 붙지 않는다.",
        fc=BAD_BG,
        ec="#F1B0B0",
        title_c=RED,
        fs=11.5,
        bfs=9.6,
    )
    _box(
        ax,
        6.3,
        3.35,
        5.7,
        2.75,
        "경로 B  ·  ALT-B4 (다른 물질)",
        "unit당 항체 capa · 보관 안정성으로 차별화.\n물질특허 존속기간만큼 차별화의 독점 기간.\nQlex 바이오시밀러는 같은 효소가 아니면 어렵다.",
        fc=OK_BG,
        ec="#A7D4B0",
        title_c=GREEN,
        fs=11.5,
        bfs=9.6,
    )
    _box(
        ax,
        0.2,
        0.25,
        11.8,
        2.85,
        "한 줄로 말하면",
        "시밀러 효소는 ‘값싼 복제 도구’이고, ALT-B4는 ‘제품에 붙는 차별화 특허’다.\n"
        "할로자임 물질특허가 2027(미국)·2029(유럽)에 만료되는 것을 빅파마가 모를 리 없다.\n"
        "그래도 MSD·AZ·다이이찌·사노피·GSK·바이오젠이 ALT-B4를 산 것은, 같은 효소로는 장벽이 안 생기기 때문이다.",
        fc=BLUE_BG,
        ec="#B7C9E4",
        title_c=NAVY2,
        fs=12,
        bfs=10.2,
    )
    _save(fig, "03_why_altb4.png")


def chart_capacity():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.35), dpi=170)
    labels = [
        "Herceptin Hylecta\n(Enhanze)",
        "Darzalex Faspro\n(Enhanze)",
        "Keytruda Qlex\n(ALT-B4)",
    ]
    mg = [120, 120, 165]
    colors = [NAVY2, NAVY2, GOLD]
    x = np.arange(len(labels))
    bars = ax.bar(x, mg, color=colors, width=0.55, zorder=2)
    ax.set_xticks(x, labels, fontsize=10)
    ax.set_ylabel("항체 mg  /  히알루로니다제 2,000 units")
    ax.set_ylim(0, 210)
    fig.subplots_adjust(bottom=0.22)
    ax.set_title(
        "같은 2,000 units로 몇 mg의 항체를 넣었는가  ·  라벨 농도",
        loc="left",
        color=NAVY,
        fontsize=13,
        fontweight="bold",
    )
    for b, v in zip(bars, mg):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + 5,
            f"{v} mg",
            ha="center",
            fontsize=12,
            fontweight="bold",
            color=NAVY,
        )
    ax.axhline(120, color="#CBD5E1", ls="--", lw=1, zorder=1)
    ax.text(
        2.0,
        192,
        "+37.5% vs Enhanze 라벨",
        ha="center",
        fontsize=10,
        fontweight="bold",
        color=GOLD,
    )
    ax.annotate(
        "",
        xy=(2, 165),
        xytext=(2, 120),
        arrowprops=dict(arrowstyle="<->", color=GOLD, lw=1.6),
    )
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#EEF2F8", zorder=0)
    fig.text(
        0.01,
        -0.04,
        "출처: Herceptin Hylecta PI 120 mg/2,000 U/mL · Darzalex Faspro PI 120 mg/2,000 U/mL · Keytruda Qlex PI 165 mg/2,000 U/mL\n"
        "한계: 항체가 다르다. 라벨 농도 ≠ 혈중 전달 효율의 헤드투헤드 입증. 하나증권도 “명확한 비교가 되지 않는다”고 적었다.",
        fontsize=8.2,
        color=GRAY,
    )
    _save(fig, "04_capacity.png")


def chart_qlex():
    _font()
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.15), dpi=170, gridspec_kw={"width_ratios": [1.15, 1]})

    ax = axes[0]
    q = ["1Q26", "2Q26"]
    v = [128, 463]
    bars = ax.bar(q, v, color=[NAVY2, GOLD], width=0.52, zorder=2)
    ax.set_title("Keytruda Qlex 분기 매출 ($mn)", loc="left", color=NAVY, fontsize=12.2, fontweight="bold")
    ax.set_ylabel("$ million")
    ax.set_ylim(0, 580)
    for b, val in zip(bars, v):
        ax.text(
            b.get_x() + b.get_width() / 2,
            val + 12,
            f"{val}",
            ha="center",
            fontsize=13,
            fontweight="bold",
            color=NAVY,
        )
    ax.text(0.5, 520, "QoQ +262%   ·   상반기 합 $590mn", ha="center", fontsize=9.4, color=GRAY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#EEF2F8", zorder=0)

    ax = axes[1]
    names = [
        "글로벌 패밀리 대비\n(463 / 8,366)",
        "미국 사업 대비\n(하나 6월 ~9%)",
        "MSD 목표\n(미국 27년 말)",
    ]
    vals = [5.5, 9.0, 35.0]
    colors = [NAVY2, GOLD, GREEN]
    y = np.arange(len(names))
    ax.barh(y, vals, color=colors, height=0.55, zorder=2)
    ax.set_yticks(y, names, fontsize=9.2)
    ax.set_xlabel("%")
    ax.set_xlim(0, 48)
    ax.set_title("전환율 스케일", loc="left", color=NAVY, fontsize=12.2, fontweight="bold")
    for i, val in enumerate(vals):
        label = "5.5%" if i == 0 else ("~9% / 두 자릿수" if i == 1 else "30–40%")
        ax.text(val + 0.8, i, label, va="center", fontsize=9.2, fontweight="bold", color=colors[i])
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#EEF2F8", zorder=0)
    fig.text(
        0.01,
        -0.02,
        "출처: Merck 2026.8.4 실적 · 콜 트랜스크립트(J-code 4월 이후 채택 증가, 미국 두 자릿수) · Reuters CFO 인터뷰 · 하나증권 7/14(6월 integrated WAC ~9%)",
        fontsize=8.1,
        color=GRAY,
    )
    _save(fig, "05_qlex.png")


def chart_timeline():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.2), dpi=170)
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 5.4)
    ax.axis("off")
    ax.set_title(
        "7/14 리포트가 기다리던 것  →  8월에 나온 것",
        loc="left",
        color=NAVY,
        fontsize=13.2,
        fontweight="bold",
        pad=6,
    )
    items = [
        (0.25, "7/2–14", "에피스 PCT 공개\n‘자체 효소’ 오해", WARN_BG, ORANGE),
        (3.15, "8/4", "MSD 2Q\nQlex $463mn", OK_BG, GREEN),
        (6.05, "8/4–5", "비공개 빅파마\n$365mn L/O", BLUE_BG, NAVY2),
        (8.95, "8/6 이후", "하나 TP 58만\n수요 재확인", PURPLE_BG, PURPLE),
    ]
    ax.plot([0.9, 11.1], [3.55, 3.55], color="#D0D7E2", lw=3, zorder=0)
    for x, date, body, fc, tc in items:
        ax.scatter([x + 1.25], [3.55], s=70, color=tc, zorder=2)
        _box(ax, x, 0.35, 2.75, 2.7, date, body, fc=fc, ec="#D0D7E2", title_c=tc, fs=12, bfs=10.4)
    ax.text(
        0.25,
        4.85,
        "리포트 시점(7/14, 279,500원)에는 Qlex 매출·세일즈 마일스톤·추가 빅딜이 아직 숫자로 안 나왔다.",
        fontsize=9.2,
        color=GRAY,
    )
    _save(fig, "06_timeline.png")


def chart_price():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.15), dpi=170)
    labels = ["7/14\n리포트 당시", "8/28\n종가", "하나 12M\n목표주가"]
    vals = [27.95, 32.00, 58.00]
    colors = [NAVY2, GOLD, GREEN]
    bars = ax.bar(labels, vals, color=colors, width=0.5, zorder=2)
    ax.set_ylabel("만원")
    ax.set_ylim(0, 70)
    ax.set_title("주가 vs 목표주가  ·  알테오젠(196170)", loc="left", color=NAVY, fontsize=13, fontweight="bold")
    notes = ["52주 저가권", "+14.5% / 시총 ~17.1조", "현재가 대비 +81%"]
    for b, v, n in zip(bars, vals, notes):
        ax.text(
            b.get_x() + b.get_width() / 2,
            v + 1.6,
            f"{v:.2f}만",
            ha="center",
            fontsize=12,
            fontweight="bold",
            color=NAVY,
        )
        ax.text(b.get_x() + b.get_width() / 2, v + 6.2, n, ha="center", fontsize=8.6, color=GRAY)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", color="#EEF2F8", zorder=0)
    ax.text(
        0.0,
        -0.18,
        "시총: 7/14 14.98조(하나) → 8/28 320,000원 × 53,586,360주 ≈ 17.15조. 목표주가는 투자의견이지 가격 예측의 확정이 아니다.",
        fontsize=8.2,
        color=GRAY,
        transform=ax.transAxes,
    )
    _save(fig, "07_price.png")


def chart_checkpoints():
    _font()
    fig, ax = plt.subplots(figsize=(12.2, 5.5), dpi=170)
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 6.3)
    ax.axis("off")
    ax.set_title("앞으로 숫자로 확인할 네 가지", loc="left", color=NAVY, fontsize=13.2, fontweight="bold")
    _box(
        ax,
        0.2,
        3.3,
        5.8,
        2.7,
        "1) Qlex 전환 속도",
        "미국 두 자릿수 → 27년 말 30–40%.\n3Q 매출이 $463mn에서 더 올라가는가.\n세일즈 마일스톤 추가 인식.",
        fc=OK_BG,
        ec="#A7D4B0",
        title_c=GREEN,
        fs=12,
        bfs=10,
    )
    _box(
        ax,
        6.2,
        3.3,
        5.8,
        2.7,
        "2) 추가 빅파마 L/O",
        "올해 이미 3건(Tesaro, Biogen, 8/5 $365mn).\n하반기 잔여 딜이 Enhanze BS 우려를\n다시 깨는지가 핵심.",
        fc=BLUE_BG,
        ec="#B7C9E4",
        title_c=NAVY2,
        fs=12,
        bfs=10,
    )
    _box(
        ax,
        0.2,
        0.25,
        5.8,
        2.8,
        "3) Intas 등 BS 데이터",
        "Intas는 2021 계약, 개발 5년 차.\n같은 unit으로 항체 capa가 나오는가.\nSandoz는 2024 ALT-B4 종료 → 별도 효소.",
        fc=WARN_BG,
        ec="#E6D39A",
        title_c=ORANGE,
        fs=12,
        bfs=10,
    )
    _box(
        ax,
        6.2,
        0.25,
        5.8,
        2.8,
        "4) Qlex 바이오시밀러 경로",
        "ALT-B4가 아닌 효소로 Qlex BS 허가?\n알테오젠: 원료가 다르면 어렵다.\nIV 키트루다 BS + Enhanze는 별도 임상.",
        fc=PURPLE_BG,
        ec="#D4B3F0",
        title_c=PURPLE,
        fs=12,
        bfs=10,
    )
    _save(fig, "08_checkpoints.png")


def main():
    chart_misread()
    chart_claims()
    chart_why_altb4()
    chart_capacity()
    chart_qlex()
    chart_timeline()
    chart_price()
    chart_checkpoints()


if __name__ == "__main__":
    main()
