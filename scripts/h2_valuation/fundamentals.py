"""Pull TTM financials and fiscal-year consensus out of yfinance frames."""

from __future__ import annotations

import pandas as pd

ASOF = pd.Timestamp("2026-10-09")


def _naive_index(obj: pd.Series) -> pd.Series:
    s = obj.copy()
    s.index = pd.to_datetime(s.index)
    if getattr(s.index, "tz", None) is not None:
        s.index = s.index.tz_convert("UTC").tz_localize(None)
    s.index = s.index.normalize()
    s = pd.to_numeric(s, errors="coerce")
    s = s[~s.index.duplicated(keep="last")].sort_index()
    return s.dropna()


def series_from(df: pd.DataFrame | None, names: list[str]) -> pd.Series | None:
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return None
    lookup = {str(i).strip().lower(): i for i in df.index}
    for name in names:
        key = name.lower()
        if key in lookup:
            s = _naive_index(df.loc[lookup[key]])
            if len(s):
                return s
    return None


def _cell(df: pd.DataFrame | None, period: str, col: str):
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return None
    if period not in df.index or col not in df.columns:
        return None
    v = df.loc[period, col]
    try:
        if pd.isna(v):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None


def ttm_sum(q: pd.Series | None, asof: pd.Timestamp = ASOF) -> tuple[float | None, pd.Timestamp | None]:
    if q is None or len(q) < 4:
        return None, None
    hist = q[q.index <= asof]
    if len(hist) < 4:
        return None, None
    last4 = hist.iloc[-4:]
    span = (last4.index[-1] - last4.index[0]).days
    if span < 200 or span > 400:
        return None, None
    if last4.index[-1] < asof - pd.Timedelta(days=230):
        return None, None
    return float(last4.sum()), pd.Timestamp(last4.index[-1])


def latest(q: pd.Series | None, asof: pd.Timestamp = ASOF) -> float | None:
    if q is None or q.empty:
        return None
    hist = q[q.index <= asof]
    if hist.empty:
        return None
    return float(hist.iloc[-1])


def extract(raw: dict, asof: pd.Timestamp = ASOF, usd_per_local: float = 1.0, currency: str = "USD") -> dict:
    """Reduce raw yfinance payloads to the scalars the DCF uses."""
    out: dict = {"ok": False, "flags": []}
    q_inc = raw.get("q_inc")
    a_inc = raw.get("a_inc")
    q_cf = raw.get("q_cf")
    a_cf = raw.get("a_cf")
    q_bs = raw.get("q_bs")
    a_bs = raw.get("a_bs")
    info = raw.get("info") or {}

    q_rev = series_from(q_inc, ["Total Revenue", "Operating Revenue"])
    q_oi = series_from(q_inc, ["Operating Income", "EBIT"])
    q_pretax = series_from(q_inc, ["Pretax Income"])
    q_tax = series_from(q_inc, ["Tax Provision"])
    q_da = series_from(q_inc, ["Reconciled Depreciation"])
    q_int = series_from(q_inc, ["Interest Expense"])
    q_dil = series_from(q_inc, ["Diluted Average Shares"])
    a_rev = series_from(a_inc, ["Total Revenue", "Operating Revenue"])
    a_oi = series_from(a_inc, ["Operating Income", "EBIT"])
    q_capex = series_from(q_cf, ["Capital Expenditure"])
    a_capex = series_from(a_cf, ["Capital Expenditure"])
    q_da_cf = series_from(q_cf, ["Depreciation And Amortization", "Depreciation Amortization Depletion"])
    a_da_cf = series_from(a_cf, ["Depreciation And Amortization", "Depreciation Amortization Depletion"])
    q_debt = series_from(q_bs, ["Total Debt"])
    q_cash = series_from(
        q_bs,
        [
            "Cash Cash Equivalents And Short Term Investments",
            "Cash And Cash Equivalents",
        ],
    )
    q_net_debt = series_from(q_bs, ["Net Debt"])
    a_debt = series_from(a_bs, ["Total Debt"])
    a_cash = series_from(
        a_bs,
        [
            "Cash Cash Equivalents And Short Term Investments",
            "Cash And Cash Equivalents",
        ],
    )

    rev_ttm, rev_end = ttm_sum(q_rev, asof)
    oi_ttm, _ = ttm_sum(q_oi, asof)
    pretax_ttm, _ = ttm_sum(q_pretax, asof)
    tax_ttm, _ = ttm_sum(q_tax, asof)
    if rev_ttm is None or oi_ttm is None or rev_ttm <= 0:
        out["flags"].append("no_ttm")
        return out

    margin = oi_ttm / rev_ttm
    margins = []
    if a_rev is not None and a_oi is not None:
        both = pd.concat([a_rev.rename("r"), a_oi.rename("o")], axis=1).dropna()
        both = both[both["r"] > 0].tail(3)
        if len(both):
            margins = (both["o"] / both["r"]).tolist()
    med = float(pd.Series(margins).median()) if margins else margin
    if margin <= 0:
        margin_term = margin
        margin0 = margin
        out["flags"].append("negative_ebit")
    elif med > 0.10:
        # Through-cycle margin is usable. Fade a peak down; recover only half a trough.
        margin_term = med if margin > med else margin + 0.5 * (med - margin)
        margin0 = 0.5 * margin + 0.5 * margin_term
    else:
        # A loss or subscale history is not the steady-state margin of a now-profitable firm.
        margin_term = min(margin, max(med, 0.5 * margin))
        margin0 = 0.5 * margin + 0.5 * margin_term
        out["flags"].append("margin_ramp")

    if pretax_ttm is not None and pretax_ttm > 0 and tax_ttm is not None:
        raw_tax = tax_ttm / pretax_ttm
        if raw_tax < 0 or raw_tax > 0.40:
            tax = 0.15
            out["flags"].append("tax_forced_15")
        else:
            tax = float(min(0.25, max(0.12, raw_tax)))
            if abs(tax - raw_tax) > 1e-9:
                out["flags"].append("tax_clipped")
    else:
        tax = 0.15
        out["flags"].append("tax_forced_15")

    da_ttm, da_end = ttm_sum(q_da_cf, asof)
    da_base = rev_ttm
    if da_ttm is None:
        da_ttm, da_end = ttm_sum(q_da, asof)
    if da_ttm is None and a_da_cf is not None and a_rev is not None and len(a_da_cf) and len(a_rev):
        da_ttm = abs(float(a_da_cf.iloc[-1]))
        da_base = float(a_rev.iloc[-1])
        da_end = a_da_cf.index[-1]
    capex_ttm, capex_end = ttm_sum(q_capex, asof)
    capex_base = rev_ttm
    if capex_ttm is None and a_capex is not None and a_rev is not None and len(a_capex) and len(a_rev):
        capex_ttm = float(a_capex.iloc[-1])
        capex_base = float(a_rev.iloc[-1])
        capex_end = a_capex.index[-1]
    if da_ttm is None or capex_ttm is None or da_base <= 0 or capex_base <= 0:
        out["flags"].append("no_da_capex")
        return out

    da_ratio = abs(da_ttm) / da_base
    capex_ratio = abs(capex_ttm) / capex_base
    # Do not replace cash capex with amortization of acquired intangibles.
    da_ratio = float(min(0.45, max(0.002, da_ratio)))
    capex_ratio = float(min(0.55, max(0.002, capex_ratio)))
    if capex_ratio > 0.54:
        out["flags"].append("capex_clipped")
    if capex_ratio + 0.005 < da_ratio * 0.35:
        out["flags"].append("capex_below_da")

    int_ttm, _ = ttm_sum(q_int, asof)
    interest = abs(int_ttm) if int_ttm is not None else None

    info_debt = _f(info.get("totalDebt"))
    info_cash = _f(info.get("totalCash"))
    bs_debt = latest(q_debt, asof)
    if bs_debt is None:
        bs_debt = latest(a_debt, asof)
    bs_cash = latest(q_cash, asof)
    if bs_cash is None:
        bs_cash = latest(a_cash, asof)
    gross_debt = info_debt if info_debt is not None else bs_debt
    cash = info_cash if info_cash is not None else bs_cash
    if gross_debt is None:
        gross_debt = 0.0
        out["flags"].append("debt_missing")
    if cash is None:
        cash = 0.0
        out["flags"].append("cash_missing")
    net_debt = gross_debt - cash
    bs_net = latest(q_net_debt, asof)
    if bs_net is not None and abs(net_debt - bs_net) > max(1e9, 0.25 * max(abs(net_debt), abs(bs_net), 1.0)):
        out["flags"].append("net_debt_info_vs_bs")

    so = _f(info.get("sharesOutstanding"))
    dil = latest(q_dil, asof)
    shares = so
    if dil and so and abs(dil - so) / so < 0.15:
        shares = dil
    elif dil and not so:
        shares = dil
    if not shares or shares <= 0:
        out["flags"].append("no_shares")
        return out

    beta = _f(info.get("beta"))
    if beta is None or not (0.2 < beta < 3.5):
        beta = 1.20
        out["flags"].append("beta_default_1.20")

    # Consensus mapping. yearAgoRevenue tells us whether 0y is the open year.
    rev_est = raw.get("rev_est")
    est0 = _cell(rev_est, "0y", "avg")
    est1 = _cell(rev_est, "+1y", "avg")
    yago0 = _cell(rev_est, "0y", "yearAgoRevenue")
    analysts_0y = _cell(rev_est, "0y", "numberOfAnalysts")
    analysts_1y = _cell(rev_est, "+1y", "numberOfAnalysts")
    last_fy_end = pd.Timestamp(a_rev.index[-1]) if a_rev is not None and len(a_rev) else None
    last_fy_rev = float(a_rev.iloc[-1]) if a_rev is not None and len(a_rev) else None
    latest_q = pd.Timestamp(q_rev[q_rev.index <= asof].index[-1])

    ytd = 0.0
    if last_fy_end is not None:
        ytd_slice = q_rev[(q_rev.index > last_fy_end) & (q_rev.index <= asof)]
        ytd = float(ytd_slice.sum()) if len(ytd_slice) else 0.0

    mode = "missing"
    if last_fy_rev and yago0 and abs(yago0 - last_fy_rev) / last_fy_rev < 0.08:
        mode = "open"  # 0y is the year after the last reported FY
    elif last_fy_rev and est0 and abs(est0 - last_fy_rev) / last_fy_rev < 0.08:
        mode = "rolled"  # 0y still points at the completed FY
    elif est0:
        mode = "open"
        out["flags"].append("consensus_map_unchecked")

    if mode == "open":
        fy0 = est0
        fy1 = est1
        analysts = analysts_1y if fy1 else analysts_0y
    elif mode == "rolled":
        fy0 = est1
        fy1 = None
        analysts = analysts_1y
    else:
        fy0 = None
        fy1 = None
        analysts = None
        out["flags"].append("no_revenue_consensus")

    if last_fy_end is None:
        out["flags"].append("no_fy_end")
        return out

    fy_end = pd.Timestamp(last_fy_end)
    guard = 0
    while fy_end <= asof or fy_end <= latest_q:
        fy_end = fy_end + pd.DateOffset(years=1)
        guard += 1
        if guard > 8:
            out["flags"].append("fy_end_failed")
            return out
    fy_start = fy_end - pd.DateOffset(years=1)
    total_days = max((fy_end - fy_start).days, 1)
    elapsed = (asof - fy_start).days / total_days
    elapsed = float(min(0.98, max(0.0, elapsed)))

    g_outer = None
    if fy0 and fy1 and fy0 > 0:
        g_outer = fy1 / fy0 - 1.0
    if mode == "rolled" and fy0 and last_fy_rev:
        g_into = fy0 / last_fy_rev - 1.0
    elif fy0 and rev_ttm:
        g_into = fy0 / rev_ttm - 1.0
    else:
        g_into = None

    quarters = _pit_quarters(q_rev, q_oi, q_debt, q_cash, q_dil)

    out.update(
        {
            "ok": fy0 is not None and fy0 > 0,
            "rev_ttm": rev_ttm,
            "oi_ttm": oi_ttm,
            "margin_ttm": margin,
            "margin0": float(min(0.62, max(-0.20, margin0))),
            "margin_term": float(min(0.62, max(0.03, margin_term))) if margin_term > 0 else margin_term,
            "tax": tax,
            "da_ratio": da_ratio,
            "capex_ratio": capex_ratio,
            "interest": interest,
            "gross_debt": gross_debt,
            "cash": cash,
            "net_debt": net_debt,
            "bs_net_debt": bs_net,
            "shares_model": shares,
            "shares_out": so,
            "shares_diluted": dil,
            "market_cap_info": _f(info.get("marketCap")),
            "ev_info": _f(info.get("enterpriseValue")),
            "beta_raw": _f(info.get("beta")),
            "beta": float(min(1.80, max(0.70, beta))),
            "fy0": fy0,
            "fy1": fy1,
            "ytd": ytd,
            "elapsed": elapsed,
            "fy_end": str(fy_end.date()),
            "last_fy_end": str(pd.Timestamp(last_fy_end).date()),
            "last_fy_rev": last_fy_rev,
            "latest_q": str(latest_q.date()),
            "mode": mode,
            "g_outer": g_outer,
            "g_into": g_into,
            "analysts": None if analysts is None else int(analysts),
            "est0": est0,
            "est1": est1,
            "yago0": yago0,
            "quarters": quarters,
            "rev_end": None if rev_end is None else str(rev_end.date()),
            "currency": currency or "USD",
            "usd_per_local": usd_per_local,
        }
    )
    if currency and currency != "USD":
        if usd_per_local is None or usd_per_local <= 0:
            out["ok"] = False
            out["flags"].append("fx_missing")
            return out
        for k in (
            "rev_ttm", "oi_ttm", "interest", "gross_debt", "cash", "net_debt",
            "bs_net_debt", "fy0", "fy1", "ytd", "last_fy_rev", "est0", "est1",
        ):
            if out.get(k) is not None:
                out[k] = out[k] * usd_per_local
        for q in out.get("quarters") or []:
            for k in ("ebit", "revenue", "debt", "cash"):
                if q.get(k) is not None:
                    q[k] = q[k] * usd_per_local
        out["ev_info"] = None
        out["flags"].append(f"fx_{currency}")
    if not out["ok"]:
        out["flags"].append("no_fy0")
    return out


def _pit_quarters(q_rev, q_oi, q_debt, q_cash, q_dil) -> list[dict]:
    if q_rev is None or q_oi is None:
        return []
    dates = [d for d in q_rev.index if d in q_oi.index]
    rows = []
    for i in range(3, len(dates)):
        window = dates[i - 3 : i + 1]
        span = (window[-1] - window[0]).days
        if span < 200 or span > 400:
            continue
        ebit = float(sum(q_oi[d] for d in window))
        rev = float(sum(q_rev[d] for d in window))
        if rev <= 0:
            continue
        debt = _at(q_debt, window[-1])
        cash = _at(q_cash, window[-1])
        shares = _at(q_dil, window[-1])
        rows.append(
            {
                "period_end": str(pd.Timestamp(window[-1]).date()),
                "available": str((pd.Timestamp(window[-1]) + pd.Timedelta(days=45)).date()),
                "ebit": ebit,
                "revenue": rev,
                "debt": debt,
                "cash": cash,
                "shares": shares,
            }
        )
    return rows


def _at(s: pd.Series | None, dt) -> float | None:
    if s is None or dt not in s.index:
        return None
    v = s.loc[dt]
    if pd.isna(v):
        return None
    return float(v)


def _f(v):
    try:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return None
        return float(v)
    except (TypeError, ValueError):
        return None
