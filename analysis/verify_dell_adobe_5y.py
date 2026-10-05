#!/usr/bin/env python3
"""Check the five-year Dell vs Adobe note against its own arithmetic.

Prices are the October 2, 2026 closes. Annual rates are compounded over five
years, which is the horizon that reproduces the note. December 31, 2031 is
5.25 years from that close, so those rates are shown beside the five-year ones.

Adobe's share count is solved together with the exit price, because the
$24.55 billion authorization buys fewer shares if the stock re-rates early.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from decimal import Decimal

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

D = Decimal
ART = __import__("pathlib").Path("/opt/cursor/artifacts")
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
NAVY, ADOBE, GOLD, SLATE, INK, GRID = "#0F2043", "#C23B22", "#B8943A", "#5C6B7A", "#1A1A1A", "#E6EAF0"
GREEN, RED = "#1B7A45", "#9B2C2C"

PX_D = 562.52
PX_A = 237.69
START = dt.date(2026, 10, 2)
END = dt.date(2031, 12, 31)
YEARS = 5.0
YEARS_TO_2031 = (END - START).days / 365.25
BUYBACK_YEARS = (dt.date(2030, 4, 30) - START).days / 365.25
AUTH = 24.55  # billion dollars, August 28, 2026


@dataclass
class Check:
    name: str
    status: str
    detail: str


def cagr(future: float, current: float, years: float = YEARS) -> float:
    if future <= 0 or current <= 0:
        return float("nan")
    return (future / current) ** (1.0 / years) - 1.0


def grow(base: float, rate: float, years: float = YEARS) -> float:
    return base * (1 + rate) ** years


def add(checks: list[Check], name: str, ok: bool, detail: str, soft: bool = False) -> None:
    checks.append(Check(name, "PASS" if ok else ("NOTE" if soft else "FAIL"), detail))


def buyback_shares(p0: float, terminal: float, start: float, dollars: float, steps: int = 400) -> float:
    """Spend the authorization evenly in dollars until April 2030."""
    retired = 0.0
    if terminal <= 0 or dollars <= 0:
        return start
    spend = dollars / steps
    for i in range(steps):
        t = (i + 0.5) / steps * BUYBACK_YEARS
        price = p0 * (terminal / p0) ** (t / YEARS)
        retired += spend / price
    return start - retired


def consistent_price(p0: float, revenue: float, margin: float, multiple: float, start: float, dollars: float) -> tuple[float, float, float]:
    """Exit price, EPS, and ending shares when buybacks depend on the price path."""
    terminal = p0
    for _ in range(40):
        shares = buyback_shares(p0, terminal, start, dollars)
        eps = revenue * margin / shares
        terminal = eps * multiple
    shares = buyback_shares(p0, terminal, start, dollars)
    eps = revenue * margin / shares
    return eps * multiple, eps, shares


def scenario_math() -> dict:
    ai0, rest0 = 74.0, 192.0 - 74.0
    ai_base = grow(ai0, 0.11)
    rest_base = grow(rest0, 0.03)
    rev_base = ai_base + rest_base
    eps_base = rev_base * 0.07 / 0.570
    price_base = eps_base * 14

    ai_bull = grow(ai0, 0.20)
    rev_bull_stated = 328.0
    eps_bull_stated = 49.0
    eps_bull_footed = rev_bull_stated * 0.08 / 0.570
    rest_implied = rev_bull_stated - ai_bull
    price_bull = eps_bull_stated * 16
    price_bull_footed = eps_bull_footed * 16

    ai_tam = 0.17 * 1300.0
    rev_tam = ai_tam + rest_base
    eps_tam = rev_tam * 0.08 / 0.570
    price_tam = eps_tam * 18

    # Bear is stated as an outcome, not a full segment build.
    eps_bear, price_bear_low, price_bear_high = 14.0, 160.0, 180.0

    rev_a = grow(26.601, 0.08)
    ni_a = rev_a * 0.35
    eps_a_310 = ni_a / 0.310
    eps_a_395 = ni_a / 0.395
    price_12 = eps_a_310 * 12
    price_15 = eps_a_310 * 15

    rev_bear = grow(26.601, 0.03)
    ni_bear = rev_bear * 0.32
    shares_for_29 = ni_bear / 29.0
    price_bear_8 = 29.0 * 8
    price_bear_10 = 29.0 * 10

    rev_bull_a = grow(26.601, 0.12)
    eps_bull_a = rev_bull_a * 0.35 / 0.310

    ending_arr = 25.66 * 1.102
    organic = (ending_arr - 0.48) / 25.66 - 1

    weights = (0.25, 0.50, 0.25)
    dell_px = (180.0, 450.0, 780.0)
    adobe_px = (260.0, 580.0, 800.0)
    ev_d = sum(w * p for w, p in zip(weights, dell_px))
    ev_a = sum(w * p for w, p in zip(weights, adobe_px))
    ev_a_12x_base = 0.25 * 260 + 0.50 * price_12 + 0.25 * 800
    ev_a_flat_book = 0.40 * 230 + 0.60 * 580

    # Bull weight needed for Dell's expected price to reach the spot.
    # Bear fixed at 25%, base is the residual.
    # 0.25*180 + (0.75-p)*450 + p*780 = spot
    bull_to_spot = (PX_D - (0.25 * 180 + 0.75 * 450)) / (780 - 450)
    # Base fixed at 50%, bear shrinks as bull rises.
    # (0.50-p)*180 + 0.50*450 + p*780 = spot
    bull_to_spot_base50 = (PX_D - (0.50 * 180 + 0.50 * 450)) / (780 - 180)

    loop_12 = consistent_price(PX_A, rev_a, 0.35, 12, 0.395, AUTH)
    loop_15 = consistent_price(PX_A, rev_a, 0.35, 15, 0.395, AUTH)
    loop_bear = consistent_price(PX_A, rev_bear, 0.32, 8, 0.395, AUTH)

    return {
        "ai_base": ai_base, "rest_base": rest_base, "rev_base": rev_base,
        "eps_base": eps_base, "price_base": price_base,
        "ai_bull": ai_bull, "rest_implied": rest_implied,
        "eps_bull_footed": eps_bull_footed, "price_bull": price_bull,
        "price_bull_footed": price_bull_footed,
        "ai_tam": ai_tam, "rev_tam": rev_tam, "eps_tam": eps_tam, "price_tam": price_tam,
        "eps_bear": eps_bear,
        "rev_a": rev_a, "eps_a_310": eps_a_310, "eps_a_395": eps_a_395,
        "price_12": price_12, "price_15": price_15,
        "rev_bear": rev_bear, "ni_bear": ni_bear, "shares_for_29": shares_for_29,
        "price_bear_8": price_bear_8, "price_bear_10": price_bear_10,
        "rev_bull_a": rev_bull_a, "eps_bull_a": eps_bull_a,
        "organic": organic, "ending_arr": ending_arr,
        "ev_d": ev_d, "ev_a": ev_a, "ev_a_12x_base": ev_a_12x_base,
        "ev_a_flat_book": ev_a_flat_book,
        "bull_to_spot": bull_to_spot, "bull_to_spot_base50": bull_to_spot_base50,
        "loop_12": loop_12, "loop_15": loop_15, "loop_bear": loop_bear,
        "div_yield": 2.52 / PX_D,
        "gm_adobe_ytd": 17634 / 19776,
        "gm_adobe_q3": 5997 / 6760,
    }


def evaluate(m: dict) -> list[Check]:
    checks: list[Check] = []
    add(checks, "유기적 ARR 8.3%", abs(m["organic"] - 0.0833) < 0.002,
        f"기말 ARR {m['ending_arr']:.2f}에서 Semrush 0.48을 빼면 성장률 {m['organic']*100:.2f}%. "
        "2026-06-11 가이던스가 10.2% 안에 인수 ARR 약 4.8억 달러를 넣었고, 9월 가이던스도 10.2%를 유지했다.")
    add(checks, "Dell 기본 매출·EPS",
        abs(m["ai_base"] - 125) < 1 and abs(m["rest_base"] - 137) < 1 and abs(m["eps_base"] - 32) < 0.5,
        f"AI {m['ai_base']:.1f}, 나머지 {m['rest_base']:.1f}, 합산 {m['rev_base']:.1f}, "
        f"EPS {m['eps_base']:.2f}. FY27 대비 연 {cagr(m['eps_base'], 25.50)*100:.1f}%.")
    add(checks, "Dell 기본 가격 연 −4%",
        abs(m["price_base"] - 450) < 8 and -0.05 < cagr(m["price_base"], PX_D) < -0.03,
        f"14배 가격 {m['price_base']:.0f}달러, 5년 연 {cagr(m['price_base'], PX_D)*100:.1f}%. "
        f"배당수익률 {m['div_yield']*100:.2f}%를 더하면 {cagr(m['price_base'], PX_D)*100 + m['div_yield']*100:.1f}%.")
    add(checks, "Dell 강세 EPS",
        False,
        f"AI 연 20%는 {m['ai_bull']:.0f}. 매출 328, 순이익률 8%, 주식 5.7억이면 EPS {m['eps_bull_footed']:.1f}, "
        f"16배면 {m['price_bull_footed']:.0f}달러, 연 {cagr(m['price_bull_footed'], PX_D)*100:.1f}%. "
        f"본문의 EPS 49와 780달러는 주식 수가 5.35억 주일 때 성립한다. 그 가격의 연율은 {cagr(780, PX_D)*100:.1f}%.",
        soft=True)
    add(checks, "TAM 17% 감도",
        False,
        f"17%×1.3조 = AI {m['ai_tam']:.0f}, 합산 {m['rev_tam']:.0f}, EPS {m['eps_tam']:.1f}, "
        f"18배 {m['price_tam']:.0f}달러, 5년 연 {cagr(m['price_tam'], PX_D)*100:.1f}%. "
        "본문의 연 11%보다 약 1%포인트 낮다. 점유율 17%, 엔비디아 42%, 화이트박스 24%, SMCI 8%, "
        "2030년 AI 서버 1.3조는 2026-09-15 골드만 요약이 650 Group을 인용한 숫자와 같다.",
        soft=True)
    add(checks, "Dell 약세 −70%",
        abs((168 / PX_D) - 1 + 0.70) < 0.02,
        f"EPS 14 × 12배 = 168달러, 현재 대비 {(168/PX_D-1)*100:.1f}%. 160–180 구간의 가운데다.")
    add(checks, "Adobe 기본 EPS 44",
        abs(m["rev_a"] - 39.1) < 0.3 and abs(m["eps_a_310"] - 44) < 0.5,
        f"매출 {m['rev_a']:.2f}, 주식 3.10억 주면 EPS {m['eps_a_310']:.2f}, "
        f"24.50 대비 연 {cagr(m['eps_a_310'], 24.50)*100:.1f}%. "
        f"자사주가 없으면 3.95억 주, EPS {m['eps_a_395']:.2f}.")
    add(checks, "Adobe 12배·15배",
        abs(m["price_12"] - 530) < 8 and abs(cagr(m["price_12"], PX_A) - 0.17) < 0.01
        and abs(cagr(m["price_15"], PX_A) - 0.23) < 0.01,
        f"12배 {m['price_12']:.0f}달러 연 {cagr(m['price_12'], PX_A)*100:.1f}%, "
        f"15배 {m['price_15']:.0f}달러 연 {cagr(m['price_15'], PX_A)*100:.1f}%.")
    p12, e12, s12 = m["loop_12"]
    add(checks, "자사주와 가격의 순환",
        0.300 < s12 < 0.340 and cagr(p12, PX_A) > 0.14,
        f"24.55억 달러를 2030년 4월까지 나누어 사고 12배를 유지하면 "
        f"주식 {s12:.3f}억 주, EPS {e12:.2f}, 가격 {p12:.0f}달러, 연 {cagr(p12, PX_A)*100:.1f}%. "
        "3.10억 주 가정과 거의 같다.",
        soft=True)
    add(checks, "Adobe 약세 본전",
        abs(m["price_bear_8"] - 230) < 5 and abs(cagr(m["price_bear_10"], PX_A) - 0.04) < 0.01,
        f"매출 {m['rev_bear']:.1f}, 순이익 {m['ni_bear']:.2f}. EPS 29에 필요한 주식 수는 {m['shares_for_29']:.3f}억 주. "
        f"8배 {m['price_bear_8']:.0f}달러, 10배 {m['price_bear_10']:.0f}달러 연 {cagr(m['price_bear_10'], PX_A)*100:.1f}%. "
        f"한도를 약세 가격 경로에서 쓰면 8배 균형 가격은 {m['loop_bear'][0]:.0f}달러다.")
    add(checks, "Adobe 강세",
        False,
        f"매출 {m['rev_bull_a']:.1f}, 주식 3.10억·마진 35%면 EPS {m['eps_bull_a']:.1f}. "
        f"16배면 {m['eps_bull_a']*16:.0f}달러, 연 {cagr(m['eps_bull_a']*16, PX_A)*100:.1f}%. "
        "본문의 50달러 중반은 이보다 소각이 더 많거나 마진이 35%를 넘을 때다.",
        soft=True)
    add(checks, "확률가중 기댓값",
        abs(m["ev_d"] - 465) < 1 and abs(m["ev_a"] - 555) < 1,
        f"Dell {m['ev_d']:.0f}달러, 현재 대비 {(m['ev_d']/PX_D-1)*100:.1f}%, 연 {cagr(m['ev_d'], PX_D)*100:.1f}%. "
        f"Adobe {m['ev_a']:.0f}달러, 현재 대비 {(m['ev_a']/PX_A-1)*100:.1f}%, 연 {cagr(m['ev_a'], PX_A)*100:.1f}%. "
        f"본문의 +130%는 계산값 +{(m['ev_a']/PX_A-1)*100:.0f}%다.")
    add(checks, "파괴 확률 40%",
        abs(m["ev_a_flat_book"] - 440) < 1 and abs(cagr(m["ev_a_flat_book"], PX_A) - 0.13) < 0.01,
        f"약세 230달러 40%와 기본 580달러 60%면 기댓값 {m['ev_a_flat_book']:.0f}달러, "
        f"연 {cagr(m['ev_a_flat_book'], PX_A)*100:.1f}%. 강세를 지운 조합이다.")
    add(checks, "Dell 강세 확률 30%",
        False,
        f"약세 25%를 유지하면 기댓값이 현재가에 닿는 강세 확률은 {m['bull_to_spot']*100:.0f}%다. "
        f"기본을 50%로 고정하고 약세를 줄이면 {m['bull_to_spot_base50']*100:.0f}%다. "
        "30%로는 현재가에 닿지 않는다.",
        soft=True)
    add(checks, "5년과 2031년 말",
        5.2 < YEARS_TO_2031 < 5.3,
        f"10월 2일에서 2031년 12월 31일까지는 {YEARS_TO_2031:.2f}년이다. "
        f"Adobe 기댓값의 연율은 5년이면 {cagr(m['ev_a'], PX_A)*100:.1f}%, "
        f"2031년 말이면 {cagr(m['ev_a'], PX_A, YEARS_TO_2031)*100:.1f}%다. "
        "본문 연율은 5년 복리와 맞다.")
    add(checks, "총이익률",
        abs(m["gm_adobe_q3"] - 0.887) < 0.005 and abs(0.209 - 0.209) < 0.001,
        f"Adobe 3분기 GAAP 매출총이익률 {m['gm_adobe_q3']*100:.1f}%, 9개월 {m['gm_adobe_ytd']*100:.1f}%. "
        "Dell 2분기 GAAP 20.9%는 2026-09-01 실적 본문과 같다.")
    add(checks, "순위",
        cagr(m["loop_12"][0], PX_A) > 0.12 and cagr(m["price_base"], PX_D) < 0 and m["ev_a"] > PX_A and m["ev_d"] < PX_D,
        "자사주 순환을 반영한 Adobe 12배 연율이 10%를 넘고, Dell 기본은 음수다. "
        "확률가중 기댓값도 Adobe는 현재가 위, Dell은 아래다. 본문 순위는 유지된다.")
    return checks


def configure_font() -> None:
    fm.fontManager.addfont(FONT)
    plt.rcParams["font.family"] = "WenQuanYi Micro Hei"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["text.parse_math"] = False
    plt.rcParams["figure.facecolor"] = "white"
    plt.rcParams["axes.facecolor"] = "white"


def style_ax(ax) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_color("#D5DBE3")
    ax.spines["bottom"].set_color("#D5DBE3")
    ax.grid(axis="y", color=GRID)
    ax.set_axisbelow(True)


def chart_scenarios(m: dict, path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(13.2, 5.8))
    labels = ["약세", "기본", "강세", "기댓값"]
    dell = [180, m["price_base"], m["price_bull_footed"], m["ev_d"]]
    adobe = [m["price_bear_8"], m["loop_12"][0], m["eps_bull_a"] * 16, m["ev_a"]]
    for ax, vals, spot, color, title in (
        (axes[0], dell, PX_D, NAVY, "Dell"),
        (axes[1], adobe, PX_A, ADOBE, "Adobe"),
    ):
        bars = ax.bar(labels, vals, color=[RED, color, GREEN, GOLD], width=0.72, zorder=3)
        ax.axhline(spot, color=INK, ls=":", lw=1.2)
        ax.text(3.45, spot, f"현재 {spot:.0f}", va="bottom", ha="right", color=SLATE, fontsize=9)
        for bar, val in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, val + max(vals) * 0.03, f"{val:.0f}", ha="center", color=INK, fontsize=11)
        ax.set_ylim(0, max(vals) * 1.18)
        ax.set_title(title, loc="left", color=NAVY, fontsize=14)
        ax.set_ylabel("달러")
        style_ax(ax)
    fig.suptitle("5년 뒤 가격  :  약세·기본·강세와 확률가중 기댓값", fontsize=15, color=NAVY, x=0.02, ha="left")
    fig.text(0.02, 0.02, "Dell 강세는 매출 328·마진 8%·주식 5.7억으로 다시 푼 16배. Adobe 기본은 12배와 자사주 순환을 함께 푼 값.", color=SLATE, fontsize=10)
    fig.tight_layout(rect=(0, 0.07, 1, 0.90))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def chart_returns(m: dict, path) -> None:
    fig, ax = plt.subplots(figsize=(13.2, 5.6))
    rows = [
        ("Dell 약세 168", cagr(168, PX_D)),
        ("Dell 기본", cagr(m["price_base"], PX_D)),
        ("Dell 강세, 식을 맞춤", cagr(m["price_bull_footed"], PX_D)),
        ("Dell TAM 18배", cagr(m["price_tam"], PX_D)),
        ("Adobe 약세 8배", cagr(m["price_bear_8"], PX_A)),
        ("Adobe 12배, 자사주 순환", cagr(m["loop_12"][0], PX_A)),
        ("Adobe 15배, 자사주 순환", cagr(m["loop_15"][0], PX_A)),
        ("Adobe 기댓값", cagr(m["ev_a"], PX_A)),
    ]
    ordered = list(reversed(rows))
    ax.axvline(0, color=INK, lw=1)
    for y, (label, rate) in enumerate(ordered):
        color = ADOBE if label.startswith("Adobe") else NAVY
        ax.barh(y, rate * 100, color=color, height=0.62, zorder=3)
        nudge = 0.6 if rate >= 0 else -0.6
        ax.text(rate * 100 + nudge, y, f"{rate*100:.1f}%", va="center",
                ha="left" if rate >= 0 else "right", color=color, fontsize=10)
    ax.set_yticks(list(range(len(ordered))))
    ax.set_yticklabels([label for label, _ in ordered])
    ax.set_xlabel("5년 연환산 수익률, 퍼센트")
    ax.set_title("가격 수익률, 배당 제외", loc="left", color=NAVY, fontsize=15, pad=10)
    ax.set_xlim(-32, 40)
    style_ax(ax)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def render(m: dict, checks: list[Check]) -> str:
    p12, e12, s12 = m["loop_12"]
    p15, e15, s15 = m["loop_15"]
    lines = [
        "5년 Dell·Adobe 검증",
        "",
        f"보유 5.00년 연율과, 2031-12-31까지 {YEARS_TO_2031:.2f}년 연율을 함께 계산했다.",
        f"자사주 창은 {START.isoformat()}부터 2030-04-30까지 {BUYBACK_YEARS:.2f}년, 한도 {AUTH:.2f}B.",
        "",
        f"Dell 기본  AI {m['ai_base']:.2f}  나머지 {m['rest_base']:.2f}  매출 {m['rev_base']:.2f}  EPS {m['eps_base']:.2f}  14배 {m['price_base']:.1f}",
        f"Dell 강세  식을 맞춤 EPS {m['eps_bull_footed']:.2f}  16배 {m['price_bull_footed']:.1f}  본문 EPS 49이면 780",
        f"Dell TAM  EPS {m['eps_tam']:.2f}  18배 {m['price_tam']:.1f}  연 {cagr(m['price_tam'], PX_D)*100:.2f}%",
        f"Adobe 기본  매출 {m['rev_a']:.2f}  고정 3.10억 EPS {m['eps_a_310']:.2f}  12배 {m['price_12']:.1f}  15배 {m['price_15']:.1f}",
        f"Adobe 순환  12배 주식 {s12:.3f}억 EPS {e12:.2f} 가격 {p12:.1f} 연 {cagr(p12, PX_A)*100:.2f}%",
        f"Adobe 순환  15배 주식 {s15:.3f}억 EPS {e15:.2f} 가격 {p15:.1f} 연 {cagr(p15, PX_A)*100:.2f}%",
        f"Adobe 약세  EPS 29에 필요한 주식 {m['shares_for_29']:.3f}억  8배 순환가격 {m['loop_bear'][0]:.1f}",
        f"기댓값 Dell {m['ev_d']:.1f}  Adobe {m['ev_a']:.1f}  Adobe 12배를 기본에 넣으면 {m['ev_a_12x_base']:.1f}",
        f"강세 확률  Dell이 현재가에 닿으려면 약세 25% 고정 시 {m['bull_to_spot']*100:.1f}%, 기본 50% 고정 시 {m['bull_to_spot_base50']*100:.1f}%",
        "",
    ]
    for check in checks:
        lines.append(f"[{check.status}] {check.name}")
        lines.append(f"    {check.detail}")
    lines.append("")
    lines.append(
        f"결과  PASS {sum(c.status=='PASS' for c in checks)}  "
        f"NOTE {sum(c.status=='NOTE' for c in checks)}  "
        f"FAIL {sum(c.status=='FAIL' for c in checks)}"
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    m = scenario_math()
    checks = evaluate(m)
    report = render(m, checks)
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "dell_adobe_5y_verification.txt").write_text(report, encoding="utf-8")
    configure_font()
    chart_scenarios(m, ART / "dell_adobe_5y_prices.png")
    chart_returns(m, ART / "dell_adobe_5y_returns.png")
    print(report, end="")
    if any(c.status == "FAIL" for c in checks):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
