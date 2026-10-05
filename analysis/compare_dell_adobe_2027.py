#!/usr/bin/env python3
"""Compare Dell and Adobe at end-2027 with the same valuation method.

Both use the October 2, 2026 close, a frozen diluted share count, no credit
for buybacks after that count, and the next fiscal year the market can see
on December 31, 2027. Dell's FY2029 ends January 2029. Adobe's FY2028 ends
December 2028. The holding period is the same 15 months.

Adobe's base multiple is not Dell's 19x. Nineteen times was a hardware
judgment. Adobe's 16x is the center of 14-18x: subscription margins on one
side, AI seat risk on the other. The current 9.7x and a mechanical 19x are
both shown beside it.
"""

from __future__ import annotations

import datetime as dt
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_dell_2027_target import build_model as build_dell

D = Decimal
ART = Path("/opt/cursor/artifacts")
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"

NAVY = "#0F2043"
ADOBE = "#C23B22"
BLUE = "#2F5D9F"
GOLD = "#B8943A"
SLATE = "#5C6B7A"
GREEN = "#1B7A45"
INK = "#1A1A1A"
GRID = "#E6EAF0"

START = dt.date(2026, 10, 2)
END = dt.date(2027, 12, 31)
HOLD_YEARS = D("15") / D("12")
SEGMENTS = ("문서·소비자", "크리에이티브·마케팅", "제품·서비스")


def money(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(D(places), rounding=ROUND_HALF_UP)


def nearest_10(value: Decimal) -> Decimal:
    return (value / D("10")).quantize(D("1"), rounding=ROUND_HALF_UP) * D("10")


def cagr(future: float, current: float, years: float) -> float:
    return (future / current) ** (1.0 / years) - 1.0


def build_adobe() -> dict:
    """Guidance midpoint, then two years of slower growth and frozen shares."""
    revenue = (D("26.576") + D("26.626")) / 2
    eps_guide = (D("24.45") + D("24.50")) / 2
    levels = {
        "문서·소비자": (D("7.470") + D("7.490")) / 2,
        "크리에이티브·마케팅": (D("18.242") + D("18.272")) / 2,
    }
    levels["제품·서비스"] = revenue - levels["문서·소비자"] - levels["크리에이티브·마케팅"]
    growth = {
        "FY2027": {"문서·소비자": D("0.12"), "크리에이티브·마케팅": D("0.09"), "제품·서비스": D("0")},
        "FY2028": {"문서·소비자": D("0.10"), "크리에이티브·마케팅": D("0.08"), "제품·서비스": D("0")},
    }
    # Model assumptions, not disclosed segment margins. The faster piece
    # carries the lower incremental margin because of AI inference and freemium.
    incremental = {"문서·소비자": D("0.30"), "크리에이티브·마케팅": D("0.48"), "제품·서비스": D("0.10")}
    oi = {"FY2026": revenue * D("0.45")}
    books = {"FY2026": dict(levels)}
    for year, previous in (("FY2027", "FY2026"), ("FY2028", "FY2027")):
        book = {}
        extra = D("0")
        for name in SEGMENTS:
            step = books[previous][name] * growth[year][name]
            book[name] = books[previous][name] + step
            extra += step * incremental[name]
        books[year] = book
        oi[year] = oi[previous] + extra

    shares_guide = D("0.400")
    shares = D("0.389")
    ni_guide = eps_guide * shares_guide
    ni = {year: oi[year] * D("0.82") for year in oi}
    # FY2026 net income stays on the guidance identity. Later years use the
    # company's 18% non-GAAP tax and approximately zero non-operating income.
    ni["FY2026"] = ni_guide
    eps_constant = {year: ni[year] / shares for year in ni}
    return {
        "revenue": {year: sum(books[year].values()) for year in books},
        "books": books,
        "growth": growth,
        "incremental": incremental,
        "oi": oi,
        "ni": ni,
        "eps_guide": eps_guide,
        "eps_constant": eps_constant,
        "shares_guide": shares_guide,
        "shares": shares,
        "margin": {year: oi[year] / sum(books[year].values()) for year in books},
    }


def stress(base: dict, growth_path: dict, incremental: dict) -> dict:
    book = dict(base["books"]["FY2026"])
    oi = base["oi"]["FY2026"]
    for year in ("FY2027", "FY2028"):
        extra = D("0")
        nxt = {}
        for name in SEGMENTS:
            step = book[name] * growth_path[year][name]
            nxt[name] = book[name] + step
            extra += step * incremental[name]
        book = nxt
        oi = oi + extra
    revenue = sum(book.values())
    ni = oi * D("0.82")
    eps = ni / base["shares"]
    return {"revenue": revenue, "oi": oi, "margin": oi / revenue, "ni": ni, "eps": eps}


def gordon(ni: Decimal, rate: Decimal, shares: Decimal, growth: Decimal = D("0.03")) -> Decimal:
    return ni / (rate - growth) / shares


def pv(price: float, dividend: float, rate: float) -> float:
    """Dell dividends use the recent mid-quarter schedule. Adobe pays none."""
    pay_dates = [
        dt.date(2026, 10, 30),
        dt.date(2027, 1, 30),
        dt.date(2027, 5, 1),
        dt.date(2027, 7, 31),
        dt.date(2027, 10, 30),
    ]
    value = sum(dividend / (1 + rate) ** ((day - START).days / 365.25) for day in pay_dates)
    value += price / (1 + rate) ** ((END - START).days / 365.25)
    return value


def dell_pack(model: dict) -> dict:
    price = D("562.52")
    eps = model["eps"]["FY2029"]
    per = eps * 19
    anchor = nearest_10(per)
    ni = model["ni"]["FY2029"]
    guide_eps = model["eps"]["FY2027"]
    return {
        "name": "델",
        "price": price,
        "guide_eps": guide_eps,
        "value_eps": eps,
        "current_per": price / guide_eps,
        "base_per": D("19"),
        "exact": per,
        "anchor": anchor,
        "low_per": eps * 18,
        "high_per": eps * 20,
        "ni": ni,
        "dcf10": gordon(ni, D("0.10"), model["shares"]),
        "dcf12": gordon(ni, D("0.12"), model["shares"]),
        "revenue": (D("192"), model["rev28"], model["rev29"]),
        "eps_path": (guide_eps, model["eps"]["FY2028"], eps),
        "oi_margin": (D("25") / model["rev28"], D("27.5") / model["rev29"]),
        "incr_margin": sum(model["delta_oi"].values()) / sum(model["delta_rev"].values()),
        "dividend": D("0.63"),
        "bear_eps": D("17.6"),
        "bear_per": D("15"),
        "bull_eps": D("45"),
        "bull_per": D("22"),
        "shares": model["shares"],
    }


def adobe_pack(model: dict) -> dict:
    price = D("237.69")
    eps = model["eps_constant"]["FY2028"]
    per16 = eps * 16
    guide = model["eps_guide"]
    ni = model["ni"]["FY2028"]
    sbc = model["revenue"]["FY2028"] * D("0.083") * D("0.82")
    return {
        "name": "어도비",
        "price": price,
        "guide_eps": guide,
        "constant_guide_eps": model["eps_constant"]["FY2026"],
        "value_eps": eps,
        "eps_path": (
            model["eps_constant"]["FY2026"],
            model["eps_constant"]["FY2027"],
            eps,
        ),
        "current_per": price / guide,
        "base_per": D("16"),
        "exact": per16,
        "anchor": nearest_10(per16),
        "low_per": eps * 14,
        "high_per": eps * 18,
        "same_19": eps * 19,
        "ni": ni,
        "sbc_after_tax": sbc,
        "dcf10": gordon(ni, D("0.10"), model["shares"]),
        "dcf12": gordon(ni, D("0.12"), model["shares"]),
        "dcf10_sbc": gordon(ni - sbc, D("0.10"), model["shares"]),
        "dcf12_sbc": gordon(ni - sbc, D("0.12"), model["shares"]),
        "revenue": tuple(model["revenue"][y] for y in ("FY2026", "FY2027", "FY2028")),
        "oi_margin": (model["margin"]["FY2026"], model["margin"]["FY2028"]),
        "incr_margin": (
            (model["oi"]["FY2028"] - model["oi"]["FY2027"])
            / (model["revenue"]["FY2028"] - model["revenue"]["FY2027"])
        ),
        "dividend": D("0"),
        "shares": model["shares"],
        "model": model,
    }


def factors(price: Decimal, guide_eps: Decimal, value_eps: Decimal, target_per: Decimal) -> tuple[float, float, float]:
    earnings = float(value_eps / guide_eps)
    multiple = float(target_per / (price / guide_eps))
    return earnings, multiple, earnings * multiple


def ann_return(price: Decimal, target: Decimal, dividend: Decimal) -> float:
    terminal = float(target + dividend * 5)
    return cagr(terminal, float(price), float(HOLD_YEARS))


def configure_font() -> None:
    fm.fontManager.addfont(FONT)
    plt.rcParams["font.family"] = "WenQuanYi Micro Hei"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["text.parse_math"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"
    plt.rcParams["text.color"] = INK


def style_ax(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#D5DBE3")
    ax.spines["bottom"].set_color("#D5DBE3")
    ax.grid(axis="y", color=GRID, zorder=0)
    ax.set_axisbelow(True)


def chart_path(dell: dict, adobe: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 6.0))
    labels = ["가이던스 연도", "이듬해", "2027년 말이\n보는 연도"]
    x = [0, 1, 2]
    panels = (
        (axes[0], "매출, 가이던스 연도 = 100", dell["revenue"], adobe["revenue"]),
        (axes[1], "상수 주식수 EPS, 가이던스 연도 = 100", dell["eps_path"], adobe["eps_path"]),
    )
    for ax, title, dell_vals, adobe_vals in panels:
        dell_idx = [float(v / dell_vals[0] * 100) for v in dell_vals]
        adobe_idx = [float(v / adobe_vals[0] * 100) for v in adobe_vals]
        ax.plot(x, dell_idx, color=NAVY, marker="o", lw=2.4, ms=8, label="델", zorder=3)
        ax.plot(x, adobe_idx, color=ADOBE, marker="o", lw=2.4, ms=8, label="어도비", zorder=3)
        for i, (d_val, a_val) in enumerate(zip(dell_idx, adobe_idx)):
            if i == 0:
                ax.text(i, 96.2, "100", color=SLATE, ha="center", va="top", fontsize=10)
                continue
            ax.text(i, d_val + 2.0, f"{d_val:.0f}", color=NAVY, ha="center", fontsize=10)
            ax.text(i, a_val - 3.6, f"{a_val:.0f}", color=ADOBE, ha="center", va="top", fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylim(90, 150)
        ax.set_title(title, loc="left", fontsize=13, color=NAVY, pad=10)
        ax.legend(frameon=False, loc="upper left")
        style_ax(ax)
    fig.suptitle("같은 세 칸  :  가이던스, 이듬해, 2027년 말이 보는 회계연도", fontsize=15, color=NAVY, x=0.02, ha="left")
    fig.text(
        0.02,
        0.02,
        "델 매출은 평가 연도까지 35 늘 때 EPS는 27 는다. 어도비는 둘 다 18 안팎이다. 어도비 EPS는 3.89억 주 고정이다.",
        color=SLATE,
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.90))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_margin(dell: dict, adobe: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.8))
    ax = axes[0]
    vals = [float(dell["incr_margin"] * 100), float(adobe["incr_margin"] * 100)]
    bars = ax.bar([0, 1], vals, color=[NAVY, ADOBE], width=0.62, zorder=3)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 1.2, f"{val:.1f}%", ha="center", color=INK, fontsize=14)
    ax.set_ylim(0, 62)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["델\n평가 연도 추가분", "어도비\n평가 연도 추가분"])
    ax.set_ylabel("퍼센트")
    ax.set_title("추가 매출 1달러가 남기는 영업이익", loc="left", fontsize=13, color=NAVY, pad=10)
    style_ax(ax)

    ax = axes[1]
    series = (
        ("델", [float(dell["oi_margin"][0] * 100), float(dell["oi_margin"][1] * 100)], NAVY),
        ("어도비", [float(adobe["oi_margin"][0] * 100), float(adobe["oi_margin"][1] * 100)], ADOBE),
    )
    for i, (name, pair, color) in enumerate(series):
        ax.plot([0, 1], pair, color=color, marker="o", lw=2.4, ms=8, label=name, zorder=3)
        ax.text(-0.08, pair[0], f"{pair[0]:.1f}%", color=color, ha="right", va="center", fontsize=11)
        ax.text(1.08, pair[1], f"{pair[1]:.1f}%", color=color, ha="left", va="center", fontsize=11)
    ax.set_xlim(-0.45, 1.45)
    ax.set_ylim(0, 60)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["다리 연도\n또는 가이던스", "평가 연도"])
    ax.set_title("연결 영업이익률", loc="left", fontsize=13, color=NAVY, pad=10)
    ax.legend(frameon=False, loc="center right")
    style_ax(ax)
    fig.suptitle("이익이 매출을 따라가는 정도", fontsize=15, color=NAVY, x=0.02, ha="left")
    fig.text(
        0.02,
        0.02,
        "델의 다리 연도 영업이익률은 FY2028 250억 / 매출 2,255억. 평가 연도는 표기 275억 / 2,585억.",
        color=SLATE,
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.07, 1, 0.90))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_value(rows: list[tuple[str, float, float]], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(13.2, 6.6))
    ys = list(range(len(rows) - 1, -1, -1))
    ax.axvline(100, color=INK, lw=1, ls=":", zorder=1)
    for y, (label, dell_idx, adobe_idx) in zip(ys, rows):
        ax.plot([dell_idx, adobe_idx], [y, y], color="#E1E6ED", lw=2, zorder=2)
        ax.scatter([dell_idx], [y], s=70, color=NAVY, zorder=4)
        ax.scatter([adobe_idx], [y], s=70, color=ADOBE, zorder=4)
        ax.text(dell_idx, y + 0.28, f"{dell_idx:.0f}", color=NAVY, ha="center", fontsize=9)
        ax.text(adobe_idx, y - 0.34, f"{adobe_idx:.0f}", color=ADOBE, ha="center", fontsize=9)
        ax.text(-2, y, label, ha="right", va="center", color=INK, fontsize=11)
    ax.scatter([], [], s=70, color=NAVY, label="델")
    ax.scatter([], [], s=70, color=ADOBE, label="어도비")
    ax.legend(frameon=False, loc="lower right")
    ax.set_yticks([])
    ax.set_xlabel("2026년 10월 2일 주가 = 100")
    ax.set_title("2027년 말 가치, 오늘 주가 대비", loc="left", fontsize=15, color=NAVY, pad=12)
    hi = max(max(d, a) for _, d, a in rows)
    ax.set_xlim(-8, hi + 28)
    ax.set_ylim(-0.7, len(rows) - 0.2)
    style_ax(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID)
    fig.text(
        0.02,
        0.015,
        "100 아래는 오늘보다 낮다. 델 기본은 620달러, 어도비 기본은 16배를 10달러 단위로 맞춘 값. 약세·강세는 스트레스다.",
        color=SLATE,
        fontsize=10,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render(dell: dict, adobe: dict, bear: dict, bull: dict) -> str:
    d_earn, d_mult, d_combo = factors(dell["price"], dell["guide_eps"], dell["value_eps"], dell["anchor"] / dell["value_eps"])
    a_earn, a_mult, a_combo = factors(adobe["price"], adobe["guide_eps"], adobe["value_eps"], D("16"))
    a_flat_mult = factors(adobe["price"], adobe["guide_eps"], adobe["value_eps"], adobe["current_per"])
    lines = [
        "델과 어도비, 2027년 말 같은 방법 비교",
        "",
        "평가일 2027-12-31. 보유는 2026-10-02 종가부터 15개월.",
        "델이 그때 보는 이익은 FY2029(2029년 1월 종료). 어도비가 보는 이익은 FY2028(2028년 12월 종료).",
        "둘 다 그 사이 자사주 매입을 넣지 않는다. 어도비 배당은 0이다.",
        "",
        "어도비 가이던스 중간값, 2026-09-10",
        f"  매출 {adobe['revenue'][0]:.3f}B  조정 EPS {adobe['guide_eps']:.3f}  영업이익률 45%  세율 18%",
        f"  연간 희석 주식 4.00억 주, 4분기 가이던스 3.89억 주를 이후 고정",
        f"  같은 순이익을 3.89억 주로 나누면 EPS {adobe['constant_guide_eps']:.2f}",
        f"  문서·소비자 {adobe['model']['books']['FY2026']['문서·소비자']:.3f}  "
        f"크리에이티브·마케팅 {adobe['model']['books']['FY2026']['크리에이티브·마케팅']:.3f}  "
        f"제품·서비스 {adobe['model']['books']['FY2026']['제품·서비스']:.3f}",
        "",
        "어도비 추정",
    ]
    for year in ("FY2027", "FY2028"):
        book = adobe["model"]["books"][year]
        lines.append(
            f"  {year}  매출 {adobe['revenue'][['FY2026','FY2027','FY2028'].index(year)]:.2f}  "
            f"문서 {book['문서·소비자']:.2f}  크리에이티브 {book['크리에이티브·마케팅']:.2f}  "
            f"기타 {book['제품·서비스']:.2f}  영업이익 {adobe['model']['oi'][year]:.2f}  "
            f"마진 {float(adobe['model']['margin'][year])*100:.2f}%  "
            f"EPS {adobe['eps_path'][['FY2026','FY2027','FY2028'].index(year)]:.2f}"
        )
    lines += [
        f"  평가 연도 추가 매출의 영업이익률 {float(adobe['incr_margin'])*100:.1f}%",
        f"  델의 같은 비율 {float(dell['incr_margin'])*100:.1f}%",
        "",
        "가격",
        f"  델 현재 {dell['price']}  가이던스 PER {float(dell['current_per']):.2f}배  "
        f"19배 {dell['exact']:.2f}  10달러 단위 {dell['anchor']}  "
        f"현금흐름 {dell['dcf12']:.0f}~{dell['dcf10']:.0f}",
        f"  어도비 현재 {adobe['price']}  가이던스 PER {float(adobe['current_per']):.2f}배  "
        f"16배 {adobe['exact']:.2f}  10달러 단위 {adobe['anchor']}  "
        f"14배 {adobe['low_per']:.2f}  18배 {adobe['high_per']:.2f}  기계적 19배 {adobe['same_19']:.2f}",
        f"  어도비 현금흐름, 순이익 {adobe['dcf12']:.0f}~{adobe['dcf10']:.0f}  "
        f"세후 주식보상 차감 {adobe['dcf12_sbc']:.0f}~{adobe['dcf10_sbc']:.0f}",
        "",
        "15개월 연환산, 델은 배당 5회 포함",
        f"  델 기본 {ann_return(dell['price'], dell['anchor'], dell['dividend'])*100:.2f}%",
        f"  어도비 16배 {ann_return(adobe['price'], adobe['anchor'], D('0'))*100:.2f}%",
        f"  어도비 오늘 배수 유지 {ann_return(adobe['price'], adobe['value_eps']*adobe['current_per'], D('0'))*100:.2f}%",
        f"  어도비 주식수 고정 후 이익만 {cagr(float(adobe['value_eps']), float(adobe['constant_guide_eps']), float(HOLD_YEARS))*100:.2f}%",
        f"  어도비 19배 기계 적용 {ann_return(adobe['price'], nearest_10(adobe['same_19']), D('0'))*100:.2f}%",
        "",
        "가격 배수 분해, 가이던스 EPS에서 평가 EPS까지",
        f"  델 이익 {d_earn:.3f}  배수 {d_mult:.3f}  곱 {d_combo:.3f}",
        f"  어도비 16배  이익 {a_earn:.3f}  배수 {a_mult:.3f}  곱 {a_combo:.3f}",
        f"  어도비 배수 유지  이익 {a_flat_mult[0]:.3f}  배수 {a_flat_mult[1]:.3f}  곱 {a_flat_mult[2]:.3f}",
        "",
        "현재가치, 할인율 10%와 12%, 배당은 15개월에 다섯 번",
        f"  델 620  10% {pv(620, 0.63, 0.10):.2f}  12% {pv(620, 0.63, 0.12):.2f}",
        f"  어도비 {adobe['anchor']}  10% {pv(float(adobe['anchor']), 0, 0.10):.2f}  "
        f"12% {pv(float(adobe['anchor']), 0, 0.12):.2f}",
        f"  어도비 오늘 배수 가격 10% {pv(float(adobe['value_eps']*adobe['current_per']), 0, 0.10):.2f}",
        "",
        "스트레스",
        f"  어도비 약세 EPS {bear['eps']:.2f}  매출 {bear['revenue']:.2f}  마진 {float(bear['margin'])*100:.1f}%  "
        f"10배 {bear['eps']*10:.2f}",
        f"  어도비 강세 EPS {bull['eps']:.2f}  매출 {bull['revenue']:.2f}  마진 {float(bull['margin'])*100:.1f}%  "
        f"22배 {bull['eps']*22:.2f}  오늘 배수 {bull['eps']*adobe['current_per']:.2f}",
        f"  델 약세 {dell['bear_eps']*dell['bear_per']:.0f}  강세 {dell['bull_eps']*dell['bull_per']:.0f}",
        "",
    ]
    return "\n".join(lines)


def check(dell: dict, adobe: dict) -> None:
    model = adobe["model"]
    for year in ("FY2026", "FY2027", "FY2028"):
        assert abs(sum(model["books"][year].values()) - model["revenue"][year]) < D("0.0000001")
        assert abs(model["eps_constant"][year] * model["shares"] - model["ni"][year]) < D("0.0000001")
    built = build_dell()
    assert built["eps"]["FY2029"] == D("32.40")
    assert built["rev29"] == D("258.5")
    assert abs(dell["incr_margin"] - sum(built["delta_oi"].values()) / D("33")) < D("0.0001")
    assert nearest_10(D("615.60")) == D("620")
    assert adobe["anchor"] == nearest_10(adobe["exact"])
    assert model["margin"]["FY2026"] == D("0.45") or abs(model["oi"]["FY2026"] / model["revenue"]["FY2026"] - D("0.45")) < D("0.0001")


def main() -> None:
    dell_model = build_dell()
    adobe_model = build_adobe()
    dell = dell_pack(dell_model)
    adobe = adobe_pack(adobe_model)
    bear = stress(
        adobe_model,
        {
            "FY2027": {"문서·소비자": D("0"), "크리에이티브·마케팅": D("-0.08"), "제품·서비스": D("-0.10")},
            "FY2028": {"문서·소비자": D("-0.02"), "크리에이티브·마케팅": D("-0.08"), "제품·서비스": D("-0.10")},
        },
        {"문서·소비자": D("0.40"), "크리에이티브·마케팅": D("0.60"), "제품·서비스": D("0.20")},
    )
    bull = stress(
        adobe_model,
        {
            "FY2027": {"문서·소비자": D("0.16"), "크리에이티브·마케팅": D("0.12"), "제품·서비스": D("0")},
            "FY2028": {"문서·소비자": D("0.14"), "크리에이티브·마케팅": D("0.11"), "제품·서비스": D("0")},
        },
        {"문서·소비자": D("0.42"), "크리에이티브·마케팅": D("0.55"), "제품·서비스": D("0.10")},
    )
    check(dell, adobe)
    flat = adobe["value_eps"] * adobe["current_per"]
    rows = [
        ("강세", float(dell["bull_eps"] * dell["bull_per"] / dell["price"] * 100), float(bull["eps"] * 22 / adobe["price"] * 100)),
        ("기본 목표", float(dell["anchor"] / dell["price"] * 100), float(adobe["anchor"] / adobe["price"] * 100)),
        ("오늘 배수 유지", float(dell["current_per"] * dell["value_eps"] / dell["price"] * 100), float(flat / adobe["price"] * 100)),
        ("현금흐름 10%", float(dell["dcf10"] / dell["price"] * 100), float(adobe["dcf10"] / adobe["price"] * 100)),
        ("현금흐름 12%", float(dell["dcf12"] / dell["price"] * 100), float(adobe["dcf12"] / adobe["price"] * 100)),
        ("약세", float(dell["bear_eps"] * dell["bear_per"] / dell["price"] * 100), float(bear["eps"] * 10 / adobe["price"] * 100)),
    ]
    report = render(dell, adobe, bear, bull)
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "dell_adobe_comparison.txt").write_text(report, encoding="utf-8")
    configure_font()
    chart_path(dell, adobe, ART / "dell_adobe_path.png")
    chart_margin(dell, adobe, ART / "dell_adobe_margin.png")
    chart_value(rows, ART / "dell_adobe_value.png")
    print(report)


if __name__ == "__main__":
    main()
