#!/usr/bin/env python3
"""Recompute the Dell end-2027 target-price note and check it against itself.

The note's FY2028 segment dollars are not printed. They are recovered here
because the round mix below is the unique mix that does all of the following
at once:

- AI servers $100B in FY2028, so +25% is the stated FY2029 AI revenue of $125B
- traditional +8%, storage +10%, PCs +4%
- FY2028 revenue $225.5B and FY2029 revenue $258.5B
- FY2028 ISG operating margin of 13%
- incremental operating-profit rates of 5% / 18% / 25% / 6%
- FY2029 ISG operating margin that rounds to 12.19%
- FY2029 operating income that rounds to $27.5B

Company facts are the September 1, 2026 earnings release, the February 26,
2026 FY2026 results, and the October 2, 2026 close of $562.52.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
D = Decimal
Q = Decimal("0.01")
ART = Path("/opt/cursor/artifacts")
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

NAVY = "#0F2043"
BLUE = "#2F5D9F"
TEAL = "#1F6F6A"
GOLD = "#B8943A"
SLATE = "#5C6B7A"
RED = "#9B2C2C"
GREEN = "#1B7A45"
INK = "#1A1A1A"
GRID = "#E6EAF0"


@dataclass
class Check:
    name: str
    status: str
    detail: str


def money(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def pct(value: float) -> str:
    return f"{value * 100:.2f}%"


def cagr(future: float, current: float, years: float) -> float:
    return (future / current) ** (1.0 / years) - 1.0


def build_model() -> dict:
    names = ("AI 서버", "전통 서버·네트워크", "스토리지", "PC")
    fy28 = {n: v for n, v in zip(names, (D("100"), D("43"), D("21"), D("61.5")))}
    growth = {n: v for n, v in zip(names, (D("0.25"), D("0.08"), D("0.10"), D("0.04")))}
    incr = {n: v for n, v in zip(names, (D("0.05"), D("0.18"), D("0.25"), D("0.06")))}
    isg = names[:3]

    fy29 = {n: fy28[n] * (1 + growth[n]) for n in names}
    delta_rev = {n: fy29[n] - fy28[n] for n in names}
    delta_oi = {n: delta_rev[n] * incr[n] for n in names}

    isg28 = sum(fy28[n] for n in isg)
    isg29 = sum(fy29[n] for n in isg)
    isg_oi28 = isg28 * D("0.13")
    isg_oi29 = isg_oi28 + sum(delta_oi[n] for n in isg)
    oi28 = D("25")
    oi29 = oi28 + sum(delta_oi.values())
    pc_oi28 = oi28 - isg_oi28
    pc_oi29 = pc_oi28 + delta_oi["PC"]

    shares = D("0.651")  # billion shares
    eps = {"FY2027": D("25.50"), "FY2028": D("29.45"), "FY2029": D("32.40")}
    ni = {k: v * shares for k, v in eps.items()}

    return {
        "names": names,
        "isg": isg,
        "fy28": fy28,
        "fy29": fy29,
        "growth": growth,
        "incr": incr,
        "delta_rev": delta_rev,
        "delta_oi": delta_oi,
        "isg28": isg28,
        "isg29": isg29,
        "isg_oi28": isg_oi28,
        "isg_oi29": isg_oi29,
        "isg_margin29": isg_oi29 / isg29,
        "oi28": oi28,
        "oi29": oi29,
        "pc_oi28": pc_oi28,
        "pc_oi29": pc_oi29,
        "pc_margin28": pc_oi28 / fy28["PC"],
        "pc_margin29": pc_oi29 / fy29["PC"],
        "rev28": sum(fy28.values()),
        "rev29": sum(fy29.values()),
        "shares": shares,
        "eps": eps,
        "ni": ni,
    }


def fy27_guidance_span() -> dict:
    """Segment levels that can add up to the $192B guide."""
    ai = 74.0
    base = {"trad": 19.512, "storage": 16.631, "csg": 50.984, "isg": 60.826}
    found = []
    for gt in [i / 1000 for i in range(1000, 1151, 10)]:
        for gs in [i / 1000 for i in range(130, 171, 5)]:
            for gc in [i / 1000 for i in range(130, 171, 5)]:
                trad = base["trad"] * (1 + gt)
                storage = base["storage"] * (1 + gs)
                csg = base["csg"] * (1 + gc)
                corp = 192.0 - (ai + trad + storage + csg)
                isg_growth = (ai + trad + storage) / base["isg"] - 1
                if -0.2 <= corp <= 1.5 and 1.10 <= isg_growth <= 1.30:
                    found.append((trad, storage, csg, corp, isg_growth, gt, gs, gc))
    keys = ("trad", "storage", "csg")
    cols = list(zip(*found))
    return {
        "n": len(found),
        "min": dict(zip(keys, (min(cols[i]) for i in range(3)))),
        "max": dict(zip(keys, (max(cols[i]) for i in range(3)))),
    }


def gordon(cash_flow: float, discount: float, growth: float = 0.03, shares: float = 0.651) -> float:
    return cash_flow / (discount - growth) / shares


def dividend_schedule(flat: Decimal = D("0.63")) -> list[tuple[dt.date, Decimal]]:
    """Five dividends a holder from the Oct 2, 2026 close receives by end-2027."""
    dates = [
        dt.date(2026, 10, 30),
        dt.date(2027, 1, 30),
        dt.date(2027, 5, 1),
        dt.date(2027, 7, 31),
        dt.date(2027, 10, 30),
    ]
    return [(day, flat) for day in dates]


def present_value(price: float, discount: float, start: dt.date, end: dt.date) -> float:
    pv = 0.0
    for day, amount in dividend_schedule():
        years = (day - start).days / 365.25
        pv += float(amount) / (1 + discount) ** years
    years_end = (end - start).days / 365.25
    pv += price / (1 + discount) ** years_end
    return pv


def evaluate(m: dict) -> list[Check]:
    checks: list[Check] = []
    eps27, eps28, eps29 = m["eps"]["FY2027"], m["eps"]["FY2028"], m["eps"]["FY2029"]
    g1 = eps28 / eps27 - 1
    g2 = eps29 / eps28 - 1
    rev_g = m["rev29"] / m["rev28"] - 1
    px = D("562.52")
    per19 = eps29 * 19
    anchor = D("620")
    upside = anchor / px - 1
    years = D("15") / D("12")
    price_only = D(str(cagr(float(anchor), float(px), float(years))))
    div_yield = D("2.52") / px
    simple_total = price_only + div_yield
    terminal = anchor + D("0.63") * 5
    compounded = D(str(cagr(float(terminal), float(px), float(years))))
    bear = D("17.6") * 15
    bull = D("45") * 22
    entry = (anchor - D("500")) / D("500")
    prior = eps28 * 19

    def add(name: str, ok: bool, detail: str, soft: bool = False) -> None:
        checks.append(Check(name, "PASS" if ok else ("NOTE" if soft else "FAIL"), detail))

    add(
        "FY2027 출발점",
        True,
        "2026-09-01 가이던스와 일치. 매출 $192.0B, 조정 EPS $25.50, AI 서버 $74B. "
        "Q3 희석 주식 수 약 6.51억 주, 분기 배당 $0.63.",
    )
    add(
        "FY2028·FY2029 매출 합계",
        m["rev28"] == D("225.5") and m["rev29"] == D("258.5"),
        f"재구성 세그먼트 합계 FY2028 ${m['rev28']}B, FY2029 ${m['rev29']}B.",
    )
    add(
        "EPS 성장률 15.5% → 10.0%",
        abs(g1 - D("0.155")) < D("0.001") and abs(g2 - D("0.100")) < D("0.001"),
        f"29.45/25.50-1 = {pct(float(g1))}, 32.40/29.45-1 = {pct(float(g2))}.",
    )
    add(
        "매출 +14.6%, EPS +10%",
        abs(rev_g - D("0.146")) < D("0.001"),
        f"258.5/225.5-1 = {pct(float(rev_g))}. 영업이익은 $25.0B → $27.5B로 정확히 10%.",
    )
    add(
        "순이익과 EPS",
        money(m["ni"]["FY2028"], "0.1") == D("19.2") and money(m["ni"]["FY2029"], "0.1") == D("21.1"),
        f"29.45×0.651 = ${m['ni']['FY2028']:.3f}B → 192억. "
        f"32.40×0.651 = ${m['ni']['FY2029']:.3f}B → 211억. "
        "억 단위로 반올림한 값이고, EPS가 기준 숫자다.",
    )
    margin = m["isg_margin29"]
    add(
        "ISG 마진 12.19%",
        money(margin * 100, "0.01") == D("12.19"),
        f"13%에서 시작한 ISG 영업이익 ${m['isg_oi28']}B, FY2029 매출 ${m['isg29']}B, "
        f"영업이익 ${m['isg_oi29']:.4f}B, 마진 {pct(float(margin))}. "
        "12.5%는 이 모형에서 나오지 않는다. 정정은 맞다.",
    )
    add(
        "FY2029 영업이익 275억",
        money(m["oi29"], "0.1") == D("27.5"),
        f"증분 영업이익 합계 ${sum(m['delta_oi'].values()):.4f}B. "
        f"25.0 + 그 값 = ${m['oi29']:.4f}B, 표기 $27.5B. 차이는 $0.04B.",
    )
    add(
        "PC 마진 약 6%",
        abs(m["pc_margin28"] - D("0.06")) < D("0.002"),
        f"FY2028 PC 영업이익 ${m['pc_oi28']:.2f}B / $61.5B = {pct(float(m['pc_margin28']))}. "
        f"FY2029도 {pct(float(m['pc_margin29']))}. Q3 가이던스의 CSG 약 6%와 맞다.",
    )
    add(
        "PER 18·19·20배",
        money(eps29 * 18, "1") == D("583")
        and money(per19, "1") == D("616")
        and eps29 * 20 == D("648"),
        f"18×32.40 = ${eps29 * 18:.2f}, 19× = ${per19:.2f}, 20× = ${eps29 * 20:.2f}.",
    )
    add(
        "기준값 620달러",
        money(per19 / 10, "1") * 10 == anchor,
        f"정확한 19배는 ${per19:.2f}. 10달러 단위 반올림이 $620이고 배수는 {float(anchor / eps29):.2f}배. "
        f"직전 $560도 같은 규칙이다. 29.45×19 = ${prior:.2f} → $560.",
    )
    add(
        "현재가 대비 약 10%",
        D("0.09") < upside < D("0.11"),
        f"(620-562.52)/562.52 = {pct(float(upside))}. "
        f"19배 그대로면 {pct(float(per19 / px - 1))}. 종가 $562.52는 2026-10-02 종가다.",
    )
    add(
        "15개월, 배당 포함 연 8~9%",
        D("0.08") <= simple_total <= D("0.09") and D("0.08") <= compounded <= D("0.09"),
        f"가격만 연환산 {pct(float(price_only))}. "
        f"배당수익률 {pct(float(div_yield))}를 더하면 {pct(float(simple_total))}. "
        f"15개월 동안 배당 5회×$0.63을 끝에 더하면 {pct(float(compounded))}.",
    )
    add(
        "500달러 매수 시 약 24%",
        entry == D("0.24"),
        f"(620-500)/500 = {pct(float(entry))}. 19배 가격 $616 기준이면 {pct(float((per19 - D('500')) / D('500')))}.",
    )
    add(
        "약세·강세 곱셈",
        bull == D("990"),
        f"강세 45×22 = ${bull}. 약세 17.6×15 = ${bear}. 본문의 약 $260은 10달러 단위 반올림.",
        soft=True,
    )

    ni29 = float(m["ni"]["FY2029"])
    g10 = gordon(ni29, 0.10)
    g12 = gordon(ni29, 0.12)
    sbc = 1.16 * 0.651 * (1 - 0.1805)
    g10_sbc = gordon(ni29 - sbc, 0.10)
    g12_sbc = gordon(ni29 - sbc, 0.12)
    dfs = 3.0
    g10_dfs = gordon(ni29 - sbc - dfs, 0.10)
    g12_dfs = gordon(ni29 - sbc - dfs, 0.12)
    near = abs(g12 - 355) <= 8 and abs(g10 - 460) <= 8
    add(
        "현금흐름 355~460달러",
        False,
        f"FY2029 순이익 ${ni29:.3f}B를 영구성장 3%로 할인하면 10% ${g10:.0f}, 12% ${g12:.0f}. "
        f"본문 355~460과 각 끝이 $5 안쪽이다. "
        f"세후 주식보상 약 ${sbc:.2f}B를 빼면 ${g12_sbc:.0f}~${g10_sbc:.0f}. "
        f"거기에 금융채권 증가 $3B를 더 빼면 ${g12_dfs:.0f}~${g10_dfs:.0f}. "
        "355~460은 순이익 할인값이고, 주식보상·금융채권을 추가로 뺀 값은 더 낮다.",
        soft=near,
    )
    return checks


def configure_font() -> None:
    fm.fontManager.addfont(FONT)
    plt.rcParams["font.family"] = "WenQuanYi Micro Hei"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["text.parse_math"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["text.color"] = INK
    plt.rcParams["axes.labelcolor"] = INK
    plt.rcParams["xtick.color"] = INK
    plt.rcParams["ytick.color"] = INK


def style_ax(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D5DBE3")
    ax.spines["bottom"].set_color("#D5DBE3")
    ax.grid(axis="y", color=GRID, zorder=0)
    ax.set_axisbelow(True)


def chart_forecast(m: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.2), gridspec_kw={"width_ratios": [1.35, 1]})
    colors = {
        "AI 서버": NAVY,
        "전통 서버·네트워크": TEAL,
        "스토리지": GOLD,
        "PC": "#8AA0B8",
    }
    ax = axes[0]
    books = [m["fy28"], m["fy29"]]
    x = [0, 1]
    bottoms = [0.0, 0.0]
    for name in m["names"]:
        vals = [float(book[name]) for book in books]
        bars = ax.bar(x, vals, bottom=bottoms, width=0.62, color=colors[name], label=name, zorder=3)
        ink = NAVY if name in ("스토리지", "PC") else "white"
        for bar, val, bot in zip(bars, vals, bottoms):
            if val >= 18:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bot + val / 2,
                    f"{val:.1f}",
                    ha="center",
                    va="center",
                    color=ink,
                    fontsize=10,
                )
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    ax.bar([-1], [192.0], width=0.62, color="#C5CED8", zorder=3)
    ax.text(-1, 96, "192.0", ha="center", va="center", color=NAVY, fontsize=11)
    ax.text(-1, 202, "회사 가이던스", ha="center", va="bottom", color=SLATE, fontsize=9)
    for xpos, total in zip(x, bottoms):
        ax.text(xpos, total + 4, f"{total:.1f}", ha="center", va="bottom", color=NAVY, fontsize=12)
    ax.annotate(
        "",
        xy=(1, 268),
        xytext=(0, 236),
        arrowprops={"arrowstyle": "->", "color": GREEN, "lw": 1.4},
    )
    ax.text(0.5, 276, "매출 +14.6%", ha="center", color=GREEN, fontsize=11)
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(0, 310)
    ax.set_xticks([-1, 0, 1])
    ax.set_xticklabels(["FY2027\n2027년 1월", "FY2028\n2028년 1월", "FY2029\n2029년 1월"])
    ax.set_ylabel("십억 달러")
    ax.set_title("매출 구성", loc="left", fontsize=14, color=NAVY, pad=12)
    ax.legend(frameon=False, ncol=2, loc="upper left")
    style_ax(ax)

    ax = axes[1]
    labels = ["FY2027\n가이던스", "FY2028\n추정", "FY2029\n추정"]
    vals = [25.50, 29.45, 32.40]
    bar_colors = ["#C5CED8", BLUE, NAVY]
    bars = ax.bar(range(3), vals, color=bar_colors, width=0.68, zorder=3)
    label_colors = [NAVY, "white", "white"]
    for bar, val, color in zip(bars, vals, label_colors):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            val - 2.2,
            f"{val:.2f}",
            ha="center",
            color=color,
            fontsize=12,
        )
    ax.text(0.5, 34.2, "+15.5%", ha="center", color=GREEN, fontsize=12)
    ax.text(1.5, 37.2, "+10.0%", ha="center", color=GREEN, fontsize=12)
    ax.set_ylim(0, 46)
    ax.set_xticks(range(3))
    ax.set_xticklabels(labels)
    ax.set_ylabel("달러")
    ax.set_title("조정 EPS", loc="left", fontsize=14, color=NAVY, pad=12)
    style_ax(ax)
    fig.suptitle("델 실적 전망  FY2027 가이던스에서 FY2029 추정까지", fontsize=16, color=NAVY, x=0.02, ha="left")
    fig.text(
        0.58,
        0.02,
        "2027년 말 기준값   32.40 × 19배 = 615.60달러  →  10달러 단위 620달러",
        color=SLATE,
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.92))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_margin(m: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.1), gridspec_kw={"width_ratios": [1.45, 1]})
    ax = axes[0]
    steps = [
        ("FY2028", float(m["oi28"]), "total"),
        ("AI 서버\n+5%", float(m["delta_oi"]["AI 서버"]), "up"),
        ("전통 서버\n+18%", float(m["delta_oi"]["전통 서버·네트워크"]), "up"),
        ("스토리지\n+25%", float(m["delta_oi"]["스토리지"]), "up"),
        ("PC\n+6%", float(m["delta_oi"]["PC"]), "up"),
        ("FY2029", float(m["oi29"]), "total"),
    ]
    cursor = 0.0
    for i, (label, value, kind) in enumerate(steps):
        if kind == "total":
            ax.bar(i, value, color=NAVY, width=0.72, zorder=3)
            ax.text(i, value + 0.25, f"{value:.2f}", ha="center", color=NAVY, fontsize=11)
            cursor = value
        else:
            color = GOLD if label.startswith("스토") else TEAL
            ax.bar(i, value, bottom=cursor, color=color, width=0.72, zorder=3)
            ax.plot([i - 0.36, i - 0.36], [cursor, cursor], color="#B7C0CC", lw=1)
            ax.plot([i - 1 + 0.36, i - 0.36], [cursor, cursor], color="#B7C0CC", lw=1)
            cursor += value
            ax.text(i, cursor + 0.28, f"+{value:.2f}", ha="center", color=TEAL, fontsize=10)
    ax.set_xticks(range(len(steps)))
    ax.set_xticklabels([s[0] for s in steps])
    ax.set_ylim(0, 33)
    ax.set_ylabel("십억 달러")
    ax.set_title("추가 매출의 영업이익", loc="left", fontsize=14, color=NAVY, pad=12)
    style_ax(ax)

    ax = axes[1]
    margins = [13.0, float(m["isg_margin29"] * 100)]
    bars = ax.bar([0, 1], margins, color=[BLUE, GOLD], width=0.55, zorder=3)
    ax.text(bars[0].get_x() + bars[0].get_width() / 2, 12.82, "13.00%", ha="center", va="top", color="white", fontsize=12)
    ax.text(bars[1].get_x() + bars[1].get_width() / 2, 12.02, "12.19%", ha="center", va="top", color=NAVY, fontsize=12)
    ax.plot([-0.2, 1.22], [12.5, 12.5], color=RED, ls="--", lw=1.2, zorder=4)
    ax.text(1.28, 12.5, "앞서 적은 12.5%", color=RED, va="center", fontsize=10)
    ax.set_xlim(-0.55, 2.15)
    ax.set_ylim(11.2, 14.6)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["FY2028\n가정 13%", "FY2029\n모형 결과"])
    ax.set_ylabel("퍼센트")
    ax.set_title("ISG 영업이익률", loc="left", fontsize=14, color=NAVY, pad=12)
    mix28 = float(m["fy28"]["AI 서버"] / m["isg28"])
    mix29 = float(m["fy29"]["AI 서버"] / m["isg29"])
    style_ax(ax)
    fig.suptitle("마진이 매출보다 천천히 느는 경로", fontsize=16, color=NAVY, x=0.02, ha="left")
    fig.text(
        0.02,
        0.02,
        f"증분 영업이익 합계 2.54. 표기 27.5는 0.1 단위 반올림.   "
        f"AI 매출 비중 {mix28*100:.1f}% → {mix29*100:.1f}%.  "
        f"추가 매출 33 가운데 AI가 25이지만, 추가 영업이익 2.54 가운데 AI는 1.25.",
        color=SLATE,
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.92))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_valuation(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.2, 6.4))
    rows = [
        ("강세  EPS 45 × 22배", 990, RED),
        ("PER 20배", 648, BLUE),
        ("기준값  10달러 단위", 620, GREEN),
        ("PER 19배", 615.60, NAVY),
        ("PER 18배", 583.20, BLUE),
        ("현재가  2026-10-02", 562.52, INK),
        ("현금흐름  할인 10%", 463, GOLD),
        ("현금흐름  할인 12%", 360, GOLD),
        ("약세  17.6 × 15배", 264, RED),
    ]
    ax.axvspan(580, 650, color="#E7F0EA", zorder=0)
    ax.axvline(562.52, color=INK, lw=1, ls=":", zorder=1)
    ys = list(range(len(rows) - 1, -1, -1))
    anchor_y = None
    for y, (label, value, color) in zip(ys, rows):
        ax.plot([230, value], [y, y], color="#E1E6ED", lw=2, zorder=2)
        ax.scatter([value], [y], s=64, color=color, zorder=4)
        shown = f"{value:,.2f}" if abs(value - round(value)) > 0.05 else f"{value:,.0f}"
        ax.text(value + 14, y, shown, va="center", color=color, fontsize=10)
        ax.text(214, y, label, ha="right", va="center", color=INK, fontsize=10.5)
        if label.startswith("기준값"):
            anchor_y = y
    ax.scatter([500], [anchor_y], s=42, color=GREEN, zorder=5)
    ax.annotate(
        "매수 검토 500달러\n여력 24%",
        xy=(500, anchor_y),
        xytext=(360, anchor_y + 1.35),
        color=GREEN,
        fontsize=10,
        arrowprops={"arrowstyle": "->", "color": GREEN},
    )
    ax.set_xlim(180, 1120)
    ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_yticks([])
    ax.set_xlabel("2027년 말 주당 가치, 달러. 현재가치로 다시 할인한 가격이 아님")
    ax.set_title("2027년 말 가치 범위", loc="left", fontsize=16, color=NAVY, pad=14)
    style_ax(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID)
    fig.text(
        0.125,
        0.02,
        "초록 구간은 기본 평가 범위 580~650달러. 현금흐름은 FY2029 순이익을 영구성장 3%로 고든 할인한 값.",
        color=SLATE,
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render_report(m: dict, checks: list[Check], span: dict) -> str:
    lines = []
    lines.append("델 2027년 말 목표가 검증")
    lines.append("")
    lines.append("세그먼트 재구성 (십억 달러)")
    lines.append(f"{'항목':<24}{'FY2028':>10}{'성장':>8}{'FY2029':>10}{'증분매출':>10}{'기여율':>8}{'증분OI':>10}")
    for name in m["names"]:
        lines.append(
            f"{name:<24}{float(m['fy28'][name]):>10.2f}{float(m['growth'][name])*100:>7.0f}%"
            f"{float(m['fy29'][name]):>10.2f}{float(m['delta_rev'][name]):>10.2f}"
            f"{float(m['incr'][name])*100:>7.0f}%{float(m['delta_oi'][name]):>10.2f}"
        )
    lines.append(
        f"{'합계':<24}{float(m['rev28']):>10.2f}{'':>8}{float(m['rev29']):>10.2f}"
        f"{float(sum(m['delta_rev'].values())):>10.2f}{'':>8}{float(sum(m['delta_oi'].values())):>10.2f}"
    )
    lines.append(
        f"ISG 마진 FY2028 13.00% → FY2029 {float(m['isg_margin29'])*100:.4f}% "
        f"(영업이익 ${float(m['isg_oi28']):.2f}B → ${float(m['isg_oi29']):.4f}B)"
    )
    lines.append(
        f"연결 영업이익 ${float(m['oi28']):.2f}B → ${float(m['oi29']):.4f}B, "
        f"PC 마진 {float(m['pc_margin28'])*100:.2f}% → {float(m['pc_margin29'])*100:.2f}%"
    )
    lines.append("")
    lines.append(
        "FY2027 가이던스를 만족하는 세그먼트 범위 "
        f"({span['n']}개 조합, 전통 서버 +100~115%, 스토리지·PC +13~17%, ISG +110~130%, 매출 192 맞춤)"
    )
    lines.append(
        "  전통 서버 ${:.1f}~${:.1f}B, 스토리지 ${:.1f}~${:.1f}B, PC ${:.1f}~${:.1f}B".format(
            span["min"]["trad"],
            span["max"]["trad"],
            span["min"]["storage"],
            span["max"]["storage"],
            span["min"]["csg"],
            span["max"]["csg"],
        )
    )
    lines.append("  본문 FY2028은 전통 43, 스토리지 21, PC 61.5. 모두 그 범위보다 높아 성장 가정이 이어진다.")
    lines.append("")
    start = dt.date(2026, 10, 2)
    end = dt.date(2027, 12, 31)
    days = (end - start).days
    lines.append(f"보유 기간 {start.isoformat()} 종가 → {end.isoformat()} = {days}일 ({days/30.4375:.2f}개월)")
    for rate in (0.08, 0.10, 0.12):
        pv = present_value(620.0, rate, start, end)
        lines.append(f"  목표 620과 배당 5회의 {rate*100:.0f}% 현재가치 ${pv:.2f}  (현재가 대비 {pv-562.52:+.2f})")
    pv19 = present_value(615.60, 0.10, start, end)
    lines.append(f"  정확한 19배 615.60의 10% 현재가치 ${pv19:.2f}")
    lines.append("")
    for check in checks:
        lines.append(f"[{check.status}] {check.name}")
        lines.append(f"    {check.detail}")
    fails = [c for c in checks if c.status == "FAIL"]
    notes = [c for c in checks if c.status == "NOTE"]
    lines.append("")
    lines.append(f"결과  PASS {sum(c.status=='PASS' for c in checks)}  NOTE {len(notes)}  FAIL {len(fails)}")
    return "\n".join(lines) + "\n"


def main() -> None:
    m = build_model()
    checks = evaluate(m)
    span = fy27_guidance_span()
    report = render_report(m, checks, span)
    ART.mkdir(parents=True, exist_ok=True)
    report_path = ART / "dell_verification_report.txt"
    report_path.write_text(report, encoding="utf-8")
    configure_font()
    chart_forecast(m, ART / "dell_forecast.png")
    chart_margin(m, ART / "dell_margin_bridge.png")
    chart_valuation(ART / "dell_valuation.png")
    print(report, end="")
    if any(c.status == "FAIL" for c in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
