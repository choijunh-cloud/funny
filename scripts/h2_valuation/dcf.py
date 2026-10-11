"""FCFF DCF with a consensus stub, faded growth, and a reverse-DCF solve.

The spot price is explained by the growth rate the fade must start from.
Uncapped street growth is reported and is not the ranking value.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import brentq


G_TERM = 0.025
FADE = 0.60
N_YEARS = 8
G_CAP = 0.35
NWC_RATIO = 0.05


@dataclass
class CashInputs:
    fy0_revenue: float
    ytd_revenue: float
    elapsed_frac: float
    tax: float
    margin0: float
    margin_term: float
    da_ratio: float
    capex_ratio: float
    wacc: float
    net_debt: float
    shares: float
    ttm_revenue: float


@dataclass
class DcfResult:
    price: float | None
    equity: float | None
    pv_ops: float | None
    year1_revenue: float | None
    g1: float | None
    fcff: list[float]
    note: str


def clip(x: float, lo: float, hi: float) -> float:
    return float(min(hi, max(lo, x)))


def fade_growth(g_prev: float, fade: float = FADE, g_term: float = G_TERM) -> float:
    return g_term + (g_prev - g_term) * fade


def margin_at(year_index: float, margin0: float, margin_term: float) -> float:
    """Year 0 is the stub. Later years step toward the through-cycle margin."""
    gap = margin0 - margin_term
    return margin_term + gap * (0.70 ** year_index)


def _fcff(revenue: float, prev_revenue: float, margin: float, p: CashInputs) -> float:
    ebit = revenue * margin
    da = revenue * p.da_ratio
    capex = revenue * p.capex_ratio
    dnwc = NWC_RATIO * (revenue - prev_revenue)
    dnwc = max(dnwc, -0.02 * revenue)
    return ebit * (1.0 - p.tax) + da - capex - dnwc


def _discount(cash: float, years: float, wacc: float) -> float:
    if years < 0:
        years = 0.0
    return cash / ((1.0 + wacc) ** years)


def project_revenues(fy0: float, g1: float, n: int = N_YEARS) -> list[float]:
    g = g1
    rev = fy0
    out = []
    for _ in range(n):
        rev = rev * (1.0 + g)
        out.append(rev)
        g = fade_growth(g)
    return out


def value_fcff(
    p: CashInputs,
    g1: float,
    year1_revenue: float | None = None,
    g_term: float = G_TERM,
) -> DcfResult:
    """Value one share.

    Stub keeps the unreported part of the current fiscal year.
    Year-1 revenue is the next fiscal year. Pass year1_revenue to force a
    consensus print; otherwise year 1 grows off fy0 at g1 and then fades.
    """
    if p.fy0_revenue <= 0 or p.shares <= 0 or p.wacc <= g_term + 0.015:
        return DcfResult(None, None, None, None, g1, [], "bad inputs")

    elapsed = clip(p.elapsed_frac, 0.0, 0.98)
    fy0 = p.fy0_revenue
    ytd = max(p.ytd_revenue, 0.0)
    fcff: list[float] = []
    pv = 0.0
    # NWC is a stock against the revenue already on the books (TTM).
    # Incremental cash is 5% of growth versus that base, split across the stub.

    if ytd <= fy0 * 0.02:
        earned = fy0 * elapsed
        ahead = fy0 * (1.0 - elapsed)
        if earned > 0:
            c = _fcff(earned, p.ttm_revenue * elapsed, p.margin0, p)
            fcff.append(c)
            pv += _discount(c, 0.04, p.wacc)
        if ahead > 0:
            c = _fcff(ahead, p.ttm_revenue * (1.0 - elapsed), p.margin0, p)
            fcff.append(c)
            pv += _discount(c, max(1.0 - elapsed, 0.02) / 2.0, p.wacc)
        t_fy0_end = max(1.0 - elapsed, 0.02)
    else:
        ahead = max(fy0 - ytd, 0.0)
        remain = clip(1.0 - elapsed, 0.02, 1.0)
        if ahead > 0:
            c = _fcff(ahead, p.ttm_revenue * remain, p.margin0, p)
            fcff.append(c)
            pv += _discount(c, remain / 2.0, p.wacc)
            t_fy0_end = remain
        else:
            t_fy0_end = remain

    if year1_revenue is not None and year1_revenue > 0:
        first = year1_revenue
        g_used = first / fy0 - 1.0
    else:
        g_used = g1
        first = fy0 * (1.0 + g_used)
    if first <= 0:
        return DcfResult(None, None, None, None, g_used, fcff, "year1 revenue <= 0")

    revenues = [first]
    g = g_used
    for _ in range(N_YEARS - 1):
        g = g_term + (g - g_term) * FADE
        revenues.append(revenues[-1] * (1.0 + g))

    prev = fy0
    last_c = 0.0
    for i, rev in enumerate(revenues):
        m = margin_at(i + 1, p.margin0, p.margin_term)
        c = _fcff(rev, prev, m, p)
        fcff.append(c)
        pv += _discount(c, t_fy0_end + i + 0.5, p.wacc)
        prev = rev
        last_c = c

    if last_c <= 0:
        return DcfResult(None, None, pv, first, g_used, fcff, "terminal fcff <= 0")

    tv = last_c * (1.0 + g_term) / (p.wacc - g_term)
    t_end = t_fy0_end + N_YEARS
    pv += _discount(tv, t_end, p.wacc)
    equity = pv - p.net_debt
    px = equity / p.shares
    return DcfResult(px, equity, pv, first, g_used, fcff, "ok")


def implied_growth(p: CashInputs, market_price: float) -> tuple[float | None, str]:
    """Growth from fy0 to the next year that sets model price to the market."""

    def gap(g: float) -> float:
        res = value_fcff(p, g1=g, year1_revenue=None)
        if res.price is None:
            return np.nan
        return res.price - market_price

    lo, hi = -0.25, 1.00
    glo, ghi = gap(lo), gap(hi)
    if not np.isfinite(glo) or not np.isfinite(ghi):
        return None, "solver nan"
    if glo > 0:
        return None, "implied g < -25%"
    if ghi < 0:
        return None, "implied g > 100%"
    # Reject a non-monotonic bracket rather than report a false root.
    if gap(0.20) < glo or gap(0.60) < gap(0.20):
        return None, "value not increasing in growth"
    root = brentq(gap, lo, hi, xtol=1e-4)
    return float(root), "ok"


def _self_test() -> None:
    # Flat 20% margin, tax 15%, DA equals capex, no NWC: FCFF is 17 per 100 of sales.
    p = CashInputs(
        fy0_revenue=100.0,
        ytd_revenue=100.0,  # fiscal year already booked; stub is empty
        elapsed_frac=0.99,
        tax=0.15,
        margin0=0.20,
        margin_term=0.20,
        da_ratio=0.05,
        capex_ratio=0.05,
        wacc=0.10,
        net_debt=0.0,
        shares=1.0,
        ttm_revenue=100.0,
    )
    # ytd ~= fy0 forces the empty-stub branch only when ytd <= 2%. Use ytd=100
    # which is > 2%, ahead = 0, t_fy0_end = 0.08.
    res = value_fcff(p, g1=0.025, year1_revenue=102.5)
    assert res.price is not None and res.note == "ok"
    # Independent Gordon path: growth stays at 2.5%, NWC takes 5% of the increase.
    w = 0.10
    t0 = 0.02
    rev = 102.5
    prev = 100.0
    expected = 0.0
    last = 0.0
    for i in range(8):
        ebit = rev * 0.20
        dnwc = max(0.05 * (rev - prev), -0.02 * rev)
        fcff = ebit * 0.85 + rev * 0.05 - rev * 0.05 - dnwc
        expected += fcff / ((1 + w) ** (t0 + i + 0.5))
        prev = rev
        last = fcff
        rev *= 1.025
    expected += last * 1.025 / (w - 0.025) / ((1 + w) ** (t0 + 8))
    if abs(res.price - expected) > 1e-6:
        raise AssertionError(f"flat DCF {res.price} != {expected}")

    g_imp, note = implied_growth(p, res.price)
    if g_imp is None or abs(g_imp - 0.025) > 0.01:
        raise AssertionError(f"reverse DCF {g_imp} {note}")

    hi = value_fcff(p, g1=0.20)
    lo = value_fcff(p, g1=0.025, year1_revenue=102.5)
    if hi.price is None or lo.price is None or hi.price <= lo.price:
        raise AssertionError("growth did not increase value")

    # Winsor path: a 70% consensus year is replaced by 35% off the same fy0.
    wild = value_fcff(p, g1=0.70, year1_revenue=170.0)
    capped = value_fcff(p, g1=G_CAP, year1_revenue=None)
    if wild.price is None or capped.price is None or wild.price <= capped.price:
        raise AssertionError("uncapped should exceed the 35% cap")
    print("dcf self-test ok", round(res.price, 4), round(capped.price, 4), round(wild.price, 4))


if __name__ == "__main__":
    _self_test()
