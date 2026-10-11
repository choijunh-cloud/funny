"""H2 2026 valuation: faded FCFF, reverse DCF, peer multiples, price-factor backtest.

Ranking weights are fixed before results are inspected:
  reverse-DCF gap 25%, visible consensus growth 20%,
  6-month drawdown room 20%, 1-month momentum 20%, volume ratio 15%.
Uncapped DCF upside is not a rank input.
"""

from __future__ import annotations

import json
import pickle
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import replace
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dcf import G_CAP, CashInputs, _self_test, implied_growth, value_fcff  # noqa: E402
from factors import (  # noqa: E402
    PRICE_WEIGHTS,
    features_at,
    forward_return,
    is_extended,
    map_mom,
    map_reverse,
    map_room,
    map_visible,
    map_vol,
    weighted_score,
)
from fundamentals import ASOF, extract  # noqa: E402

ART = Path("/opt/cursor/artifacts")
CACHE = ROOT / "data" / "cache"
UNIVERSE = [
    "CRDO", "CIEN", "FN", "KLAC", "AMAT", "KEYS", "LRCX", "MKSI", "COHR", "AVGO",
    "ASX", "ALAB", "LITE", "ANET", "TSM", "NVDA", "MU", "MCHP", "HPE", "DELL",
    "AMD", "ARM", "INTC", "GFS", "SMCI", "TXN", "MPWR", "LSCC", "ASML",
]
BENCH = ["SMH", "SOXX", "QQQ", "^TNX"]
PEER_GROUPS = {
    "equipment": ["AMAT", "LRCX", "KLAC", "MKSI"],
    "optical": ["CIEN", "COHR", "LITE"],
    "server": ["HPE", "DELL", "SMCI"],
}
LECTURE_FLAG = {
    "INTC": "강의 메모: 파운드리 정치·구조조정. 점수에는 넣지 않음.",
    "GFS": "강의 메모: 레거시 파운드리. 점수에는 넣지 않음.",
    "SMCI": "강의 메모: 법적 이슈. 점수에는 넣지 않음.",
}
ERP = 0.045
INFO_KEYS = [
    "beta", "sharesOutstanding", "totalDebt", "totalCash", "marketCap",
    "enterpriseValue", "trailingPE", "forwardPE", "currency",
]


def _jsonable(v):
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, list):
        return [_jsonable(x) for x in v]
    if isinstance(v, (np.floating,)):
        v = float(v)
    if isinstance(v, (np.integer,)):
        v = int(v)
    if isinstance(v, float) and not np.isfinite(v):
        return None
    return v


def naive_index(obj: pd.DataFrame | pd.Series):
    out = obj.copy()
    idx = pd.to_datetime(out.index)
    if getattr(idx, "tz", None) is not None:
        idx = idx.tz_convert("UTC").tz_localize(None)
    out.index = idx.normalize()
    out = out[~out.index.duplicated(keep="last")].sort_index()
    return out


def load_prices(refresh: bool) -> dict[str, pd.DataFrame]:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "prices_v1.pkl"
    tickers = UNIVERSE + BENCH
    if path.exists() and not refresh:
        with path.open("rb") as f:
            return pickle.load(f)
    df = yf.download(
        tickers,
        start="2019-01-01",
        end="2026-10-11",
        auto_adjust=False,
        progress=False,
        threads=True,
        group_by="column",
    )
    frames = {}
    for t in tickers:
        try:
            sub = pd.DataFrame(
                {
                    "close": df["Close"][t],
                    "adj": df["Adj Close"][t],
                    "volume": df["Volume"][t],
                }
            )
        except Exception as exc:  # noqa: BLE001
            print("price missing", t, exc)
            continue
        sub = naive_index(sub).dropna(how="all")
        frames[t] = sub
    with path.open("wb") as f:
        pickle.dump(frames, f)
    return frames


def _fetch_one(ticker: str) -> dict:
    last_err = None
    for attempt in range(3):
        try:
            tk = yf.Ticker(ticker)
            info = tk.info or {}
            return {
                "info": {k: info.get(k) for k in INFO_KEYS},
                "q_inc": tk.quarterly_income_stmt,
                "a_inc": tk.income_stmt,
                "q_cf": tk.quarterly_cashflow,
                "a_cf": tk.cashflow,
                "q_bs": tk.quarterly_balance_sheet,
                "a_bs": tk.balance_sheet,
                "rev_est": tk.revenue_estimate,
                "eps_est": tk.earnings_estimate,
            }
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(1.5 * (attempt + 1))
    return {"error": str(last_err)}


def load_raw(refresh: bool) -> dict:
    path = CACHE / "raw_v1.pkl"
    if path.exists() and not refresh:
        with path.open("rb") as f:
            return pickle.load(f)
    raw = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futs = {pool.submit(_fetch_one, t): t for t in UNIVERSE}
        for fut in as_completed(futs):
            t = futs[fut]
            raw[t] = fut.result()
            err = raw[t].get("error")
            print("fetched", t, "ERR" if err else "ok", err or "")
    with path.open("wb") as f:
        pickle.dump(raw, f)
    return raw


def spot_on(frame: pd.DataFrame) -> tuple[pd.Timestamp, float]:
    hist = frame.loc[:ASOF].dropna(subset=["close"])
    ts = hist.index[-1]
    return ts, float(hist["close"].iloc[-1])


def build_valuation(ticker: str, spot: float, fin: dict, rf: float) -> dict:
    row = {
        "ticker": ticker,
        "spot": spot,
        "ok": False,
        "flags": list(fin.get("flags") or []),
        "lecture_flag": LECTURE_FLAG.get(ticker),
    }
    if not fin.get("ok"):
        row["flags"].append("fundamentals_incomplete")
        return row

    shares = fin["shares_model"]
    mkt = fin.get("market_cap_info")
    implied_mkt = spot * shares
    if mkt and implied_mkt > 0 and abs(implied_mkt - mkt) / mkt > 0.20:
        shares = mkt / spot
        row["flags"].append("shares_reset_to_market_cap")
    row["shares"] = shares
    row["share_gap"] = None if not mkt else implied_mkt / mkt - 1.0

    beta = fin["beta"]
    ke = rf + beta * ERP
    debt = max(fin["gross_debt"], 0.0)
    equity_m = spot * shares
    if debt + equity_m <= 0:
        row["flags"].append("bad_capital")
        return row
    interest = fin["interest"] or 0.0
    if debt > 0 and interest > 0:
        kd = float(min(0.09, max(0.03, interest / debt)))
    elif debt > 0:
        kd = rf + 0.010
        row["flags"].append("kd_default")
    else:
        kd = rf
    tax = fin["tax"]
    wacc = ke * equity_m / (debt + equity_m) + kd * (1.0 - tax) * debt / (debt + equity_m)
    if wacc < rf:
        wacc = rf
        row["flags"].append("wacc_floored")
    row.update(
        {
            "beta": beta,
            "ke": ke,
            "kd": kd,
            "wacc": wacc,
            "tax": tax,
            "net_debt": fin["net_debt"],
            "gross_debt": debt,
            "cash": fin["cash"],
            "margin_ttm": fin["margin_ttm"],
            "margin0": fin["margin0"],
            "margin_term": fin["margin_term"],
            "da_ratio": fin["da_ratio"],
            "capex_ratio": fin["capex_ratio"],
            "rev_ttm": fin["rev_ttm"],
            "oi_ttm": fin["oi_ttm"],
            "fy0": fin["fy0"],
            "fy1": fin["fy1"],
            "ytd": fin["ytd"],
            "elapsed": fin["elapsed"],
            "fy_end": fin["fy_end"],
            "mode": fin["mode"],
            "g_outer": fin["g_outer"],
            "g_into": fin["g_into"],
            "analysts": fin["analysts"],
            "latest_q": fin["latest_q"],
            "rev_end": fin["rev_end"],
        }
    )
    if fin["margin_ttm"] is None or fin["margin_ttm"] <= 0 or fin["margin_term"] <= 0:
        row["flags"].append("dcf_skipped_margin")
        row["ok"] = True
        return row
    if fin["margin_ttm"] > fin["margin_term"] + 0.15:
        row["flags"].append("peak_margin")

    p = CashInputs(
        fy0_revenue=fin["fy0"],
        ytd_revenue=fin["ytd"],
        elapsed_frac=fin["elapsed"],
        tax=tax,
        margin0=float(min(0.62, max(0.03, fin["margin0"]))),
        margin_term=float(min(0.62, max(0.03, fin["margin_term"]))),
        da_ratio=fin["da_ratio"],
        capex_ratio=fin["capex_ratio"],
        wacc=wacc,
        net_debt=fin["net_debt"],
        shares=shares,
        ttm_revenue=fin["rev_ttm"],
    )
    g_outer = fin["g_outer"]
    if g_outer is not None and fin["fy1"] and fin["fy0"]:
        if g_outer > G_CAP:
            year1 = fin["fy0"] * (1.0 + G_CAP)
            g_base = G_CAP
        else:
            year1 = fin["fy1"]
            g_base = g_outer
        uncapped = value_fcff(p, g1=g_outer, year1_revenue=fin["fy1"])
    else:
        g_src = fin["g_into"] if fin["g_into"] is not None else 0.05
        g_base = min(g_src, G_CAP)
        year1 = None
        uncapped = value_fcff(p, g1=g_src, year1_revenue=None)

    base = value_fcff(p, g1=g_base, year1_revenue=year1)
    g_imp, g_note = implied_growth(p, spot)
    row["g_implied"] = g_imp
    row["g_implied_note"] = g_note
    row["dcf_base"] = base.price
    row["dcf_uncapped"] = uncapped.price
    row["dcf_note"] = base.note
    if base.price and spot > 0:
        row["dcf_upside"] = base.price / spot - 1.0
    else:
        row["dcf_upside"] = None
    if uncapped.price and spot > 0:
        row["dcf_uncapped_upside"] = uncapped.price / spot - 1.0
    else:
        row["dcf_uncapped_upside"] = None

    if g_outer is not None and g_imp is not None:
        row["reverse_gap"] = g_outer - g_imp
    else:
        row["reverse_gap"] = None

    # Sensitivities around the same base year-1 revenue.
    sens = {}
    for name, wacc_i, g_i, y1 in [
        ("wacc_plus_1", wacc + 0.01, g_base, year1),
        ("wacc_minus_1", max(wacc - 0.01, 0.06), g_base, year1),
        ("cap_25", wacc, min(g_base, 0.25), fin["fy0"] * 1.25 if (g_outer or 0) > 0.25 else year1),
        ("cap_45", wacc, 0.45 if (g_outer or 0) > 0.45 else g_base, fin["fy0"] * 1.45 if (g_outer or 0) > 0.45 else year1),
    ]:
        res = value_fcff(replace(p, wacc=wacc_i), g1=g_i, year1_revenue=y1)
        sens[name] = None if res.price is None or spot <= 0 else res.price / spot - 1.0
    row["sensitivity"] = sens
    if base.fcff and fin["fy0"]:
        row["fcff_final"] = base.fcff[-1]
        row["fcff_final_margin"] = base.fcff[-1] / (base.year1_revenue or fin["fy0"])
    if base.price is None or base.note not in ("ok", "tv0"):
        row["flags"].append("dcf_failed")
    if base.note == "tv0":
        row["flags"].append("tv0")
    row["ok"] = True
    row["ev"] = equity_m + fin["net_debt"]
    if fin["oi_ttm"] and fin["oi_ttm"] > 0:
        row["ev_ebit"] = row["ev"] / fin["oi_ttm"]
    else:
        row["ev_ebit"] = None
    if fin["rev_ttm"] > 0:
        row["ev_sales"] = row["ev"] / fin["rev_ttm"]
    return row


def attach_peers(rows: list[dict]) -> None:
    by = {r["ticker"]: r for r in rows}
    for name, members in PEER_GROUPS.items():
        live = [by[m] for m in members if m in by and by[m].get("ev_ebit")]
        margins = [m["margin_ttm"] for m in live if m.get("margin_ttm") is not None]
        ebits = [m["ev_ebit"] for m in live]
        sales = [m["ev_sales"] for m in live if m.get("ev_sales")]
        for m in members:
            if m not in by:
                continue
            r = by[m]
            others_e = [x["ev_ebit"] for x in live if x["ticker"] != m]
            others_s = [x["ev_sales"] for x in live if x["ticker"] != m and x.get("ev_sales")]
            others_m = [x["margin_ttm"] for x in live if x["ticker"] != m and x.get("margin_ttm") is not None]
            r["peer_group"] = name
            r["peer_n"] = len(others_e)
            if len(others_e) >= 2 and r.get("ev_ebit"):
                med_e = float(np.median(others_e))
                r["peer_ev_ebit"] = med_e
                r["ebit_discount"] = med_e / r["ev_ebit"] - 1.0
                if r.get("oi_ttm") and r.get("shares"):
                    fair_ev = med_e * r["oi_ttm"]
                    r["peer_fair"] = (fair_ev - r["net_debt"]) / r["shares"]
                    r["peer_upside"] = r["peer_fair"] / r["spot"] - 1.0
            if len(others_s) >= 2 and r.get("ev_sales"):
                med_s = float(np.median(others_s))
                r["peer_ev_sales"] = med_s
                r["sales_discount"] = med_s / r["ev_sales"] - 1.0
            if others_m and r.get("margin_ttm") is not None:
                r["peer_margin"] = float(np.median(others_m))
                r["margin_mismatch"] = abs(r["margin_ttm"] - r["peer_margin"]) > 0.10
            else:
                r["margin_mismatch"] = False


def _reverse_score(r: dict) -> float | None:
    note = r.get("g_implied_note")
    if "dcf_failed" in r.get("flags", []) or note in (None, "solver nan", "bad inputs", "value not increasing in growth"):
        return None
    analysts = r.get("analysts")
    g_outer = r.get("g_outer")
    if note == "implied g > 100%":
        # Still short of the price at a 100% fade, so the bound is the rich end.
        gap = None if g_outer is None else g_outer - 1.0
        return 0.0 if gap is None else map_reverse(gap, g_outer, analysts)
    if note == "implied g < -25%":
        gap = None if g_outer is None else g_outer - (-0.25)
        return 1.0 if gap is None else map_reverse(gap, g_outer, analysts)
    return map_reverse(r.get("reverse_gap"), g_outer, analysts)


def score_row(r: dict) -> None:
    r["s_mom"] = map_mom(r.get("mom21"))
    r["s_vol"] = map_vol(r.get("vol_ratio"))
    r["s_room"] = map_room(r.get("dd126"), r.get("mom21"), r.get("mom63"))
    r["s_visible"] = map_visible(r.get("g_into"), r.get("analysts"))
    r["s_reverse"] = _reverse_score(r)
    parts = {
        "reverse": r["s_reverse"],
        "visible": r["s_visible"],
        "room": r["s_room"],
        "mom": r["s_mom"],
        "vol": r["s_vol"],
    }
    r["score_full"] = weighted_score(parts, {
        "reverse": 0.25, "visible": 0.20, "room": 0.20, "mom": 0.20, "vol": 0.15,
    })
    r["score_price"] = weighted_score(
        {"mom": r["s_mom"], "room": r["s_room"], "vol": r["s_vol"]},
        PRICE_WEIGHTS,
    )
    r["extended"] = is_extended(r.get("dd126"), r.get("mom63"))
    note = r.get("g_implied_note")
    r["valued"] = note in ("ok", "tv0", "implied g > 100%", "implied g < -25%")
    upside = r.get("dcf_upside")
    gap = r.get("reverse_gap")
    ebit_d = r.get("ebit_discount")
    peer_ok = r.get("peer_n", 0) < 3 or ebit_d is None or ebit_d > -0.10
    if note == "implied g > 100%":
        r["agreement"] = "disagree"
    elif upside is not None and upside > 0 and gap is not None and gap > 0 and peer_ok and "dcf_failed" not in r["flags"]:
        r["agreement"] = "agree"
    elif note == "implied g < -25%" and upside is not None and upside > 0 and peer_ok:
        r["agreement"] = "agree"
    elif (upside is not None and upside > 0) or (gap is not None and gap > 0) or note == "implied g < -25%":
        r["agreement"] = "partial"
    else:
        r["agreement"] = "disagree"
    if "peak_margin" in r.get("flags", []) and r["agreement"] == "agree":
        r["agreement"] = "partial"


def published_weights(bt: dict) -> dict[str, float]:
    """Price factors enter the book only if the 126-day overlap-adjusted t exceeds 1."""
    raw = {"reverse": 0.25, "visible": 0.20}
    tmap = {
        "mom": bt["factors"]["mom21"]["h126"].get("t_adj"),
        "room": bt["factors"]["room"]["h126"].get("t_adj"),
        "vol": bt["factors"]["vol_ratio"]["h126"].get("t_adj"),
    }
    base = {"mom": 0.20, "room": 0.20, "vol": 0.15}
    kept = []
    for key, tstat in tmap.items():
        if tstat is not None and tstat > 1.0:
            raw[key] = base[key]
            kept.append(key)
    total = sum(raw.values())
    weights = {k: v / total for k, v in raw.items()}
    weights["_kept_price"] = kept
    return weights


def apply_published_score(rows: list[dict], weights: dict) -> None:
    use = {k: v for k, v in weights.items() if not k.startswith("_")}
    for r in rows:
        r["rank_gap"] = continuous_gap(r)
        r["flags"] = [f for f in r.get("flags", []) if f not in ("peer_rich_veto", "peer_cheap_bonus")]
        parts = {
            "reverse": r.get("s_reverse"),
            "visible": r.get("s_visible"),
            "room": r.get("s_room"),
            "mom": r.get("s_mom"),
            "vol": r.get("s_vol"),
        }
        r["score"] = weighted_score(parts, use)
        gap = r.get("reverse_gap")
        if r.get("g_implied_note") == "implied g > 100%":
            gap = -1.0
        ebit_d = r.get("ebit_discount")
        sales_d = r.get("sales_discount")
        if (
            r.get("peer_n", 0) >= 3
            and not r.get("margin_mismatch")
            and ebit_d is not None
            and sales_d is not None
            and gap is not None
            and r.get("score") is not None
        ):
            if ebit_d < -0.25 and sales_d < -0.25 and gap < 0:
                r["score"] *= 0.70
                r["flags"].append("peer_rich_veto")
            elif ebit_d > 0.05 and sales_d > 0.05 and gap > 0:
                r["score"] = min(1.0, r["score"] + 0.03)
                r["flags"].append("peer_cheap_bonus")


def _ic(pairs: list[tuple[float, float]]) -> dict:
    if len(pairs) < 8:
        return {"n": len(pairs), "mean_ic": None, "t_raw": None, "t_adj": None}
    rho, _ = stats.spearmanr([a for a, _ in pairs], [b for _, b in pairs])
    return {"rho": None if rho is None or not np.isfinite(rho) else float(rho)}


def backtest(prices: dict[str, pd.DataFrame], raw: dict, fx_by_ticker: dict) -> dict:
    """Survivor-only walk-forward on this fixed list. Not a tradable historical universe."""
    cal = naive_index(prices["QQQ"][["adj"]]).dropna().index
    close, volume = {}, {}
    for t in UNIVERSE:
        if t not in prices:
            continue
        frame = naive_index(prices[t])
        adj = frame["adj"].reindex(cal).ffill(limit=5)
        vol = frame["volume"].reindex(cal).ffill(limit=5)
        close[t] = adj
        volume[t] = vol

    fins = {}
    for t in UNIVERSE:
        rate, ccy = fx_by_ticker.get(t, (1.0, "USD"))
        fin = extract(raw.get(t) or {}, usd_per_local=rate, currency=ccy)
        quarters = []
        for q in fin.get("quarters") or []:
            quarters.append(q)
        fins[t] = quarters

    ic_rows = {k: {"63": [], "126": []} for k in ("mom21", "room", "vol_ratio", "ebit_yield", "price_score")}
    books = []
    # IC sample every 21 sessions; wealth compounds non-overlapping 63-session holds.
    start = 200
    step_ic = 21
    for i in range(start, len(cal) - 63, step_ic):
        dt = cal[i]
        pack = []
        for t, series in close.items():
            feat = features_at(series, volume[t], i)
            if feat["mom21"] is None or feat["dd126"] is None or feat["mom63"] is None:
                continue
            room_s = map_room(feat["dd126"], feat["mom21"], feat["mom63"])
            mom_s = map_mom(feat["mom21"])
            vol_s = map_vol(feat["vol_ratio"])
            score = weighted_score({"mom": mom_s, "room": room_s, "vol": vol_s}, PRICE_WEIGHTS)
            ey = _ebit_yield(fins.get(t) or [], dt, float(series.iloc[i]))
            fwd63 = forward_return(series, i, 63)
            fwd126 = forward_return(series, i, 126) if i + 126 < len(series) else None
            pack.append((t, feat, score, ey, fwd63, fwd126))
        if len(pack) < 12:
            continue
        for horizon, idx in (("63", 4), ("126", 5)):
            usable = [p for p in pack if p[idx] is not None and p[2] is not None]
            if len(usable) < 12:
                continue
            ic_rows["mom21"][horizon].append(_spearman([(p[1]["mom21"], p[idx]) for p in usable]))
            ic_rows["room"][horizon].append(
                _spearman([(map_room(p[1]["dd126"], p[1]["mom21"], p[1]["mom63"]), p[idx]) for p in usable])
            )
            vol_pts = [(p[1]["vol_ratio"], p[idx]) for p in usable if p[1]["vol_ratio"] is not None]
            ic_rows["vol_ratio"][horizon].append(_spearman(vol_pts))
            ey_pts = [(p[3], p[idx]) for p in usable if p[3] is not None]
            ic_rows["ebit_yield"][horizon].append(_spearman(ey_pts))
            ic_rows["price_score"][horizon].append(_spearman([(p[2], p[idx]) for p in usable]))

    wealth_top = 1.0
    wealth_ew = 1.0
    wealth_path = []
    hits = []
    excess = []
    for i in range(start, len(cal) - 63, 63):
        dt = cal[i]
        pack = []
        for t, series in close.items():
            feat = features_at(series, volume[t], i)
            if feat["mom21"] is None or feat["dd126"] is None:
                continue
            score = weighted_score(
                {
                    "mom": map_mom(feat["mom21"]),
                    "room": map_room(feat["dd126"], feat["mom21"], feat["mom63"]),
                    "vol": map_vol(feat["vol_ratio"]),
                },
                PRICE_WEIGHTS,
            )
            fwd = forward_return(series, i, 63)
            if score is None or fwd is None:
                continue
            pack.append((t, score, fwd, is_extended(feat["dd126"], feat["mom63"])))
        if len(pack) < 12:
            continue
        ranked = sorted(pack, key=lambda x: x[1], reverse=True)[:5]
        top_ret = float(np.mean([x[2] for x in ranked]))
        ew_ret = float(np.mean([x[2] for x in pack]))
        gated = [x for x in pack if not x[3]]
        gated_ranked = sorted(gated, key=lambda x: x[1], reverse=True)[:5]
        gated_ret = float(np.mean([x[2] for x in gated_ranked])) if gated_ranked else None
        wealth_top *= 1.0 + top_ret
        wealth_ew *= 1.0 + ew_ret
        wealth_path.append(
            {
                "date": str(pd.Timestamp(dt).date()),
                "top5": [x[0] for x in ranked],
                "top_ret": top_ret,
                "ew_ret": ew_ret,
                "gated_ret": gated_ret,
                "wealth_top": wealth_top,
                "wealth_ew": wealth_ew,
            }
        )
        hits.append(float(np.mean([1.0 if x[2] > 0 else 0.0 for x in ranked])))
        excess.append(top_ret - ew_ret)
        books.append(dt)

    def summarize(series: list[float], horizon: int, step: int) -> dict:
        arr = np.array([x for x in series if x is not None and np.isfinite(x)], dtype=float)
        if len(arr) < 5:
            return {"n": int(len(arr))}
        mean = float(arr.mean())
        std = float(arr.std(ddof=1))
        overlap = max(horizon / step, 1.0)
        n_eff = max(len(arr) / overlap, 1.0)
        return {
            "n": int(len(arr)),
            "mean_ic": mean,
            "t_raw": None if std == 0 else mean / std * np.sqrt(len(arr)),
            "t_adj": None if std == 0 else mean / std * np.sqrt(n_eff),
            "n_eff": n_eff,
        }

    factors = {}
    for name, horizons in ic_rows.items():
        factors[name] = {
            "h63": summarize(horizons["63"], 63, 21),
            "h126": summarize(horizons["126"], 126, 21),
        }
    ex = np.array(excess, dtype=float) if excess else np.array([])
    return {
        "caveat": "유니버스는 2026-10-09에 살아있는 종목만 포함. 상장폐지·편입 이전은 없음.",
        "factors": factors,
        "nonoverlap_63d": {
            "n_holds": len(wealth_path),
            "wealth_top5": wealth_top,
            "wealth_equal": wealth_ew,
            "avg_excess": None if len(ex) == 0 else float(ex.mean()),
            "hit_rate_names": None if not hits else float(np.mean(hits)),
            "beat_ew_rate": None if len(ex) == 0 else float(np.mean(ex > 0)),
            "avg_gated_excess": _avg_gated(wealth_path),
        },
        "path": wealth_path,
    }


def _avg_gated(path: list[dict]) -> float | None:
    vals = [p["gated_ret"] - p["ew_ret"] for p in path if p.get("gated_ret") is not None]
    if not vals:
        return None
    return float(np.mean(vals))


def _spearman(pairs: list[tuple[float, float]]) -> float | None:
    clean = [(a, b) for a, b in pairs if a is not None and b is not None and np.isfinite(a) and np.isfinite(b)]
    if len(clean) < 8:
        return None
    xs = [a for a, _ in clean]
    ys = [b for _, b in clean]
    if np.std(xs) == 0 or np.std(ys) == 0:
        return None
    rho, _ = stats.spearmanr(xs, ys)
    if rho is None or not np.isfinite(rho):
        return None
    return float(rho)


def _ebit_yield(quarters: list[dict], signal_date: pd.Timestamp, price: float) -> float | None:
    avail = [q for q in quarters if pd.Timestamp(q["available"]) <= signal_date]
    if not avail:
        return None
    q = avail[-1]
    if not q.get("shares") or not q.get("ebit") or q["ebit"] <= 0 or price <= 0:
        return None
    debt = q["debt"] or 0.0
    cash = q["cash"] or 0.0
    ev = price * q["shares"] + debt - cash
    if ev <= 0:
        return None
    return float(q["ebit"] / ev)


def continuous_gap(r: dict) -> float:
    """Unclipped consensus-minus-implied growth. Bounds sit outside the solved range."""
    note = r.get("g_implied_note")
    if r.get("reverse_gap") is not None and note in ("ok", "tv0"):
        return float(r["reverse_gap"])
    if note == "implied g < -25%":
        return 0.50
    if note == "implied g > 100%":
        return -1.0
    return -2.0


def charts(rows: list[dict], bt: dict) -> None:
    font_manager.fontManager.addfont("/usr/share/fonts/truetype/wqy/wqy-microhei.ttc")
    plt.rcParams["font.family"] = "WenQuanYi Micro Hei"
    plt.rcParams["axes.unicode_minus"] = False

    both = [r for r in rows if r.get("g_outer") is not None and r.get("g_implied") is not None]
    both = sorted(both, key=lambda r: (r["g_outer"] - r["g_implied"]))
    if both:
        fig, ax = plt.subplots(figsize=(10, 8))
        y = np.arange(len(both))
        ax.barh(y - 0.15, [r["g_implied"] * 100 for r in both], height=0.3, label="가격이 요구하는 성장", color="#4C78A8")
        ax.barh(y + 0.15, [r["g_outer"] * 100 for r in both], height=0.3, label="컨센서스 다음 해 성장", color="#F58518")
        ax.set_yticks(y)
        ax.set_yticklabels([r["ticker"] for r in both])
        ax.axvline(0, color="black", lw=0.6)
        ax.set_xlabel("성장률 %")
        ax.set_title("역DCF 내재 성장 vs 컨센서스 (다음 회계연도)")
        ax.legend(loc="lower right")
        fig.tight_layout()
        fig.savefig(ART / "h2_growth_gap.png", dpi=140)
        plt.close()

    ranked = sorted(rows, key=continuous_gap)
    if ranked:
        fig, ax = plt.subplots(figsize=(10, 8))
        colors = []
        for r in ranked:
            if r.get("extended"):
                colors.append("#B0B0B0")
            elif continuous_gap(r) > 0:
                colors.append("#54A24B")
            else:
                colors.append("#E45756")
        ax.barh([r["ticker"] for r in ranked], [continuous_gap(r) * 100 for r in ranked], color=colors)
        ax.axvline(0, color="black", lw=0.6)
        ax.set_xlabel("컨센서스 성장 − 내재 성장, %p")
        ax.set_title("역DCF 격차 (녹색 = 컨센서스가 더 높음, 회색 = 고점 근접)")
        fig.tight_layout()
        fig.savefig(ART / "h2_scores.png", dpi=140)
        plt.close()

    path = bt.get("path") or []
    if path:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot([p["date"] for p in path], [p["wealth_top"] for p in path], label="가격요인 상위 5")
        ax.plot([p["date"] for p in path], [p["wealth_ew"] for p in path], label="동일가중")
        ax.set_title("63거래일 비중첩 보유, 생존 종목만")
        ax.tick_params(axis="x", labelrotation=60, labelsize=7)
        ax.legend()
        fig.tight_layout()
        fig.savefig(ART / "h2_backtest.png", dpi=140)
        plt.close()


def pct(x, digits=1):
    if x is None or not isinstance(x, (int, float)) or not np.isfinite(x):
        return "—"
    return f"{x * 100:.{digits}f}%"


def num(x, digits=2):
    if x is None or not isinstance(x, (int, float)) or not np.isfinite(x):
        return "—"
    return f"{x:.{digits}f}"


def write_report(rows: list[dict], bt: dict, rf: float, bench: dict, weights: dict) -> str:
    book = [
        r for r in rows
        if r.get("valued") and not r.get("extended")
    ]
    book = sorted(book, key=lambda r: (continuous_gap(r), r.get("dcf_upside") or -9), reverse=True)
    top = book[:10]
    extended = sorted([r for r in rows if r.get("extended")], key=lambda r: r.get("mom63") or 0, reverse=True)
    positive = [r for r in rows if r.get("dcf_upside") is not None and r["dcf_upside"] > 0]
    positive = sorted(positive, key=lambda r: r["dcf_upside"], reverse=True)
    lines = []
    lines.append("H2 2026 DCF / 역DCF / 동종배수 / 가격요인 백테스트")
    lines.append(f"기준 종가: {ASOF.date()} (주말은 직전 정규장). 10년물 {rf * 100:.2f}%. ERP {ERP * 100:.1f}%.")
    lines.append("WACC = rf + clip(beta,0.70,1.80)*4.5% 를 자기자본 비중으로, 세후 부채원가와 가중. WACC는 rf 아래로 내리지 않음.")
    lines.append("기본 DCF는 다음 해 성장을 35%에서 자른 뒤 잔여성장의 60%만 남기며 2.5%로 수렴. 세율은 12~25%, 음수 유효세율은 15%.")
    lines.append("현금 capex가 감가상각보다 크면 초과분의 절반만 잔존가치에 남긴다. 현금 capex가 상각보다 작으면 그대로 둔다.")
    lines.append("TWD·EUR 재무와 컨센서스는 2026-10-09 현물환율로 달러 환산. 주가·주식수는 달러 ADR 기준.")
    lines.append("제품별 SOTP는 세그먼트 EBIT를 공시에서 확정하지 못해 쓰지 않음. 장비 4종, 광통신 3종, 서버 3종만 동종 EV/EBIT·EV/Sales.")
    wtxt = ", ".join(f"{k} {v:.0%}" for k, v in weights.items())
    lines.append(f"구성요소 점수 가중(백테스트에서 126일 t_adj>1인 가격요인만 포함): {wtxt}.")
    lines.append("0~1 점수는 격차가 -15%p보다 나쁠 때 바닥이라 종목이 한 점수로 붙는다. 발표 순서는 그 점수가 아니라 연속 역DCF 격차다.")
    lines.append("100% 성장으로도 주가에 못 미치면 격차를 -100%p로 둔다. 기본 DCF 업사이드가 음수이면 상승여력으로 말하지 않는다.")
    lines.append(f"벤치 1개월: SMH {pct(bench.get('SMH'))}, SOXX {pct(bench.get('SOXX'))}, QQQ {pct(bench.get('QQQ'))}.")
    lines.append("")
    lines.append("== 백테스트 (이 29종 생존자, 가격요인만) ==")
    no = bt["nonoverlap_63d"]
    lines.append(
        f"63거래일 비중첩 {no['n_holds']}회. 상위5 자산 {num(no['wealth_top5'])} vs 동일가중 {num(no['wealth_equal'])}. "
        f"평균초과 {pct(no['avg_excess'])}. 상위5가 동일가중을 이긴 비율 {pct(no['beat_ew_rate'], 0)}. "
        f"종목 양수 비율 {pct(no['hit_rate_names'], 0)}."
    )
    lines.append(f"고점근접 종목을 뺀 뒤 상위5의 동일가중 대비 평균초과 {pct(no['avg_gated_excess'])}.")
    lines.append("IC는 21거래일마다, 보유 63·126일. t_adj는 겹침(보유/21)으로 표본수를 나눈 값.")
    for name, block in bt["factors"].items():
        for h, label in (("h63", "63d"), ("h126", "126d")):
            s = block[h]
            lines.append(
                f"  {name} {label}: n={s.get('n')} meanIC={num(s.get('mean_ic'), 3)} "
                f"t_raw={num(s.get('t_raw'))} t_adj={num(s.get('t_adj'))}"
            )
    lines.append(bt["caveat"])
    lines.append("가격요인은 126일 t_adj가 1을 넘을 때만 발표 순위에 넣는다. 넘지 못하면 진단용으로만 남긴다.")
    lines.append("EBIT 수익률 표본이 작은 것은 분기 재무가 최근 몇 개만 내려오기 때문이다. 가치 요인의 과거 검증으로 쓰지 않는다.")
    lines.append("")
    lines.append("== 기본 DCF 업사이드가 양수인 종목 ==")
    if not positive:
        lines.append("없음. 이 자본비용과 마진 페이드에서는 현재 주가가 기본 현금흐름보다 높다.")
    for r in positive:
        lines.append(
            f"{r['ticker']} dcf {pct(r.get('dcf_upside'))} gap {pct(r.get('reverse_gap'))} "
            f"note {r.get('g_implied_note')} agree {r.get('agreement')} "
            f"ext {r.get('extended')} {r.get('lecture_flag') or ''}"
        )
    lines.append("")
    lines.append("== 모델 상위 10 (가치평가가 끝난 종목, 고점 근접 제외) ==")
    header = (
        "rank ticker score agree px mom21 mom63 dd126 vol g_into g_outer g_impl gap "
        "dcf_up wacc ev/ebit peer_up flags"
    )
    lines.append(header)
    for i, r in enumerate(top, 1):
        lines.append(
            " ".join(
                [
                    str(i),
                    r["ticker"],
                    num(r.get("score"), 3),
                    str(r.get("agreement")),
                    num(r.get("spot"), 2),
                    pct(r.get("mom21")),
                    pct(r.get("mom63")),
                    pct(r.get("dd126")),
                    num(r.get("vol_ratio"), 2),
                    pct(r.get("g_into")),
                    pct(r.get("g_outer")),
                    pct(r.get("g_implied")),
                    pct(r.get("reverse_gap")),
                    pct(r.get("dcf_upside")),
                    pct(r.get("wacc")),
                    num(r.get("ev_ebit"), 1),
                    pct(r.get("peer_upside")),
                    ",".join(r.get("flags") or []),
                ]
            )
        )
    lines.append("")
    lines.append("== 고점 근접으로 뺀 종목 ==")
    for r in extended:
        lines.append(
            f"{r['ticker']} px {num(r.get('spot'), 2)} mom63 {pct(r.get('mom63'))} "
            f"dd {pct(r.get('dd126'))} score {num(r.get('score'), 3)}"
        )
    lines.append("")
    lines.append("== 상위 10 민감도 (기본 대비 업사이드) ==")
    for r in top:
        sens = r.get("sensitivity") or {}
        lines.append(
            f"{r['ticker']} base {pct(r.get('dcf_upside'))} "
            f"W+1 {pct(sens.get('wacc_plus_1'))} W-1 {pct(sens.get('wacc_minus_1'))} "
            f"cap25 {pct(sens.get('cap_25'))} cap45 {pct(sens.get('cap_45'))} "
            f"uncapped {pct(r.get('dcf_uncapped_upside'))} "
            f"FY {r.get('mode')} end {r.get('fy_end')} ytd {num((r.get('ytd') or 0)/1e9, 2)}B "
            f"fy0 {num((r.get('fy0') or 0)/1e9, 2)}B m0 {pct(r.get('margin0'))} "
            f"mt {pct(r.get('margin_term'))} da {pct(r.get('da_ratio'))} cx {pct(r.get('capex_ratio'))}"
        )
    lines.append("")
    lines.append("== 전체 스냅샷 ==")
    for r in sorted(rows, key=lambda x: x.get("score") or -1, reverse=True):
        lines.append(
            f"{r['ticker']} score {num(r.get('score'), 3)} {r.get('agreement')} "
            f"ext {r.get('extended')} px {num(r.get('spot'), 2)} "
            f"gap {pct(r.get('reverse_gap'))} dcf {pct(r.get('dcf_upside'))} "
            f"peer {r.get('peer_group')} {pct(r.get('peer_upside'))} "
            f"flags {','.join(r.get('flags') or [])} {r.get('lecture_flag') or ''}"
        )
    text = "\n".join(lines) + "\n"
    (ART / "h2_valuation_report.txt").write_text(text, encoding="utf-8")
    return text


def load_fx(refresh: bool) -> tuple[dict[str, str], dict[str, float]]:
    """Reporting currency and USD per one unit of that currency, on the as-of date."""
    cur_path = CACHE / "currency_v1.pkl"
    fx_path = CACHE / "fx_v1.pkl"
    if cur_path.exists() and not refresh:
        with cur_path.open("rb") as f:
            currencies = pickle.load(f)
    else:
        currencies = {}

        def _cur(ticker: str) -> tuple[str, str]:
            try:
                info = yf.Ticker(ticker).info or {}
                return ticker, info.get("financialCurrency") or "USD"
            except Exception as exc:  # noqa: BLE001
                print("currency fail", ticker, exc)
                return ticker, "USD"

        with ThreadPoolExecutor(max_workers=6) as pool:
            for fut in as_completed([pool.submit(_cur, t) for t in UNIVERSE]):
                t, ccy = fut.result()
                currencies[t] = ccy
                print("currency", t, ccy)
        with cur_path.open("wb") as f:
            pickle.dump(currencies, f)

    needed = sorted({c for c in currencies.values() if c and c != "USD"})
    if fx_path.exists() and not refresh:
        with fx_path.open("rb") as f:
            fx_close = pickle.load(f)
    else:
        symbols = []
        for ccy in needed:
            if ccy in ("EUR", "GBP", "AUD", "NZD"):
                symbols.append(f"{ccy}USD=X")
            else:
                symbols.append(f"{ccy}=X")
        fx_close = {}
        if symbols:
            df = yf.download(symbols, start="2024-01-01", end="2026-10-11", auto_adjust=False, progress=False, threads=True)
            close = df["Close"] if "Close" in getattr(df, "columns", []) else df
            if isinstance(close, pd.Series):
                close = close.to_frame(symbols[0])
            close = naive_index(close)
            for sym in symbols:
                if sym in close.columns:
                    fx_close[sym] = close[sym].dropna()
        with fx_path.open("wb") as f:
            pickle.dump(fx_close, f)

    rates = {}
    for t, ccy in currencies.items():
        if not ccy or ccy == "USD":
            rates[t] = 1.0
            continue
        if ccy in ("EUR", "GBP", "AUD", "NZD"):
            series = fx_close.get(f"{ccy}USD=X")
            mult = 1.0
        else:
            series = fx_close.get(f"{ccy}=X")
            mult = None  # local per USD; invert
        if series is None or series.loc[:ASOF].dropna().empty:
            print("fx missing", t, ccy)
            rates[t] = None
            continue
        level = float(series.loc[:ASOF].dropna().iloc[-1])
        rates[t] = level if mult == 1.0 else 1.0 / level
    return currencies, rates


def main() -> None:
    refresh = "--refresh" in sys.argv
    ART.mkdir(parents=True, exist_ok=True)
    _self_test()
    prices = load_prices(refresh)
    tnx = naive_index(prices["^TNX"])
    tnx_hist = tnx.loc[:ASOF, "close"].dropna()
    rf = float(tnx_hist.iloc[-1]) / 100.0
    print("rf", rf, "tnx_date", tnx_hist.index[-1].date())
    raw = load_raw(refresh)
    currencies, rates = load_fx(refresh)
    fx_by = {}
    for t in UNIVERSE:
        ccy = currencies.get(t) or "USD"
        rate = rates.get(t)
        fx_by[t] = (0.0 if rate is None else rate, ccy)
        if ccy != "USD":
            print("fx", t, ccy, fx_by[t][0])
    bench = {}
    for b in ("SMH", "SOXX", "QQQ"):
        series = naive_index(prices[b])["adj"].dropna()
        series = series.loc[:ASOF]
        i = len(series) - 1
        bench[b] = features_at(series, naive_index(prices[b])["volume"], i)["mom21"]

    rows = []
    inputs = {}
    for t in UNIVERSE:
        if t not in prices:
            print("no prices", t)
            continue
        ts, spot = spot_on(prices[t])
        fin = extract(raw.get(t) or {}, usd_per_local=fx_by[t][0], currency=fx_by[t][1])
        # Drop bulky quarter path from the stored input snapshot later.
        row = build_valuation(t, spot, fin, rf)
        adj = naive_index(prices[t])
        adj_hist = adj.loc[:ASOF]
        i = len(adj_hist) - 1
        feat = features_at(adj_hist["adj"], adj_hist["volume"], i)
        row.update(feat)
        row["price_date"] = str(ts.date())
        row["rel_smh_1m"] = None if feat["mom21"] is None or bench["SMH"] is None else feat["mom21"] - bench["SMH"]
        score_row(row)
        rows.append(row)
        snap = {k: v for k, v in fin.items() if k != "quarters"}
        snap["spot"] = spot
        snap["price_date"] = str(ts.date())
        inputs[t] = snap
        print(
            t,
            "spot", round(spot, 2),
            "mode", fin.get("mode"),
            "g_into", None if fin.get("g_into") is None else round(fin["g_into"], 3),
            "g_outer", None if fin.get("g_outer") is None else round(fin["g_outer"], 3),
            "gap", None if row.get("reverse_gap") is None else round(row["reverse_gap"], 3),
            "ccy", fin.get("currency"),
            "dcf", None if row.get("dcf_upside") is None else round(row["dcf_upside"], 3),
            "note", row.get("g_implied_note"),
            "flags", ",".join(row.get("flags") or []),
        )

    tsm = next(r for r in rows if r["ticker"] == "TSM")
    asx = next(r for r in rows if r["ticker"] == "ASX")
    if (tsm.get("rev_ttm") or 0) > 500e9 or (asx.get("rev_ttm") or 0) > 80e9:
        raise SystemExit(f"FX scale check failed TSM {tsm.get('rev_ttm')} ASX {asx.get('rev_ttm')}")
    attach_peers(rows)
    for r in rows:
        score_row(r)

    bt = backtest(prices, raw, fx_by)
    weights = published_weights(bt)
    kept = weights.pop("_kept_price", [])
    weights.pop("_kept_price", None)
    apply_published_score(rows, weights)
    bt["published_weights"] = weights
    bt["price_factors_kept"] = kept
    charts(rows, bt)
    report = write_report(rows, bt, rf, bench, weights)
    payload = {
        "asof": str(ASOF.date()),
        "rf": rf,
        "erp": ERP,
        "rows": rows,
        "backtest": {k: v for k, v in bt.items() if k != "path"},
        "backtest_path": bt["path"],
        "bench_mom21": bench,
    }
    (ART / "h2_results.json").write_text(json.dumps(_jsonable(payload), indent=2), encoding="utf-8")
    (ROOT / "data" / "h2_2026-10-09_inputs.json").write_text(
        json.dumps(_jsonable(inputs), indent=2), encoding="utf-8"
    )
    print(report[:4000])
    print("WROTE", ART)


if __name__ == "__main__":
    main()
