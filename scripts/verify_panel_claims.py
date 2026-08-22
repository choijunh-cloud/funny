#!/usr/bin/env python3
"""대화록 수치·퀀트 주장에 대한 p<0.05 검증.

출력: scripts/out/panel_verification.json
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf
from scipy import stats

OUT_DIR = Path("/workspace/scripts/out")
OUT_DIR.mkdir(parents=True, exist_ok=True)
ASOF = "2026-08-22"


def flatten_close(df: pd.DataFrame) -> pd.Series:
    if isinstance(df.columns, pd.MultiIndex):
        s = df["Close"].iloc[:, 0]
    else:
        s = df["Close"]
    s = s.dropna()
    s.index = pd.to_datetime(s.index)
    return s


def download_close(ticker: str, start: str, end: str) -> pd.Series:
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    s = flatten_close(df)
    s.name = ticker
    return s


def year_end_price(close: pd.Series, year: int) -> float | None:
    sl = close[close.index.year == year]
    if sl.empty:
        return None
    return float(sl.iloc[-1])


def calendar_returns(close: pd.Series, start_year: int, end_year: int) -> pd.DataFrame:
    rows = []
    for y in range(start_year, end_year + 1):
        p0 = year_end_price(close, y - 1)
        p1 = year_end_price(close, y)
        if p0 is None or p1 is None or p0 <= 0:
            continue
        rows.append({"year": y, "ret": p1 / p0 - 1, "even": y % 2 == 0})
    return pd.DataFrame(rows)


def month_end(close: pd.Series) -> pd.Series:
    return close.resample("ME").last().dropna()


def holding_return(me: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> float | None:
    """Return from start month-end to end month-end (inclusive end)."""
    try:
        p0 = float(me.loc[start])
        p1 = float(me.loc[end])
    except KeyError:
        # nearest available
        before = me[me.index <= start]
        after = me[me.index <= end]
        if before.empty or after.empty:
            return None
        p0 = float(before.iloc[-1])
        p1 = float(after.iloc[-1])
        if before.index[-1].to_period("M") != start.to_period("M"):
            return None
    if p0 <= 0:
        return None
    return p1 / p0 - 1


def welch_ttest(a: np.ndarray, b: np.ndarray) -> dict:
    a, b = np.asarray(a, float), np.asarray(b, float)
    t, p = stats.ttest_ind(a, b, equal_var=False, alternative="two-sided")
    _, p_gt = stats.ttest_ind(a, b, equal_var=False, alternative="greater")
    return {
        "n_a": int(len(a)),
        "n_b": int(len(b)),
        "mean_a": float(np.mean(a)),
        "mean_b": float(np.mean(b)),
        "diff": float(np.mean(a) - np.mean(b)),
        "t": float(t),
        "p_two": float(p),
        "p_greater": float(p_gt),
    }


def mannwhitney(a: np.ndarray, b: np.ndarray) -> dict:
    u, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    _, p_gt = stats.mannwhitneyu(a, b, alternative="greater")
    return {"U": float(u), "p_two": float(p), "p_greater": float(p_gt)}


def ttest_mean(x: np.ndarray, popmean: float = 0.0, alternative: str = "two-sided") -> dict:
    x = np.asarray(x, float)
    t, p = stats.ttest_1samp(x, popmean, alternative=alternative)
    t2, p2 = stats.ttest_1samp(x, popmean, alternative="two-sided")
    return {
        "n": int(len(x)),
        "mean": float(np.mean(x)),
        "t": float(t2),
        "p_two": float(p2),
        "p_alt": float(p),
        "alternative": alternative,
    }


def binomial(k: int, n: int, p0: float = 0.5) -> dict:
    # two-sided exact
    res = stats.binomtest(k, n, p0, alternative="two-sided")
    res_gt = stats.binomtest(k, n, p0, alternative="greater")
    res_lt = stats.binomtest(k, n, p0, alternative="less")
    return {
        "k": k,
        "n": n,
        "rate": k / n if n else None,
        "p_two": float(res.pvalue),
        "p_greater": float(res_gt.pvalue),
        "p_less": float(res_lt.pvalue),
    }


def bh_adjust(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals, float)
    n = len(p)
    order = np.argsort(p)
    ranked = p[order]
    adj = np.empty(n)
    running = 1.0
    for i in range(n - 1, -1, -1):
        running = min(running, ranked[i] * n / (i + 1))
        adj[order[i]] = min(1.0, running)
    return [float(x) for x in adj]


def try_fred(series_id: str) -> pd.Series | None:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    try:
        df = pd.read_csv(url)
    except Exception:
        return None
    if df.shape[1] < 2:
        return None
    df.columns = ["date", "value"]
    df = df[df["value"] != "."]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    s = df.dropna().set_index("date")["value"]
    return s if not s.empty else None


def cross_corr_lead(x: pd.Series, y: pd.Series, max_lag: int = 12) -> dict:
    """y leads x if corr(x_t, y_{t-k}) high for k>0? Convention:
    corr(stock_t, export_{t+k}) for k>0 means stock leads export by k months.
    """
    df = pd.concat([x.rename("stock"), y.rename("export")], axis=1).dropna()
    if len(df) < 36:
        return {"ok": False, "n": int(len(df))}
    s = df["stock"].pct_change()
    e = df["export"].pct_change()
    pair = pd.concat([s.rename("s"), e.rename("e")], axis=1).dropna()
    lags = {}
    best_k, best_r, best_p = None, -np.inf, None
    for k in range(-max_lag, max_lag + 1):
        if k == 0:
            a, b = pair["s"], pair["e"]
        elif k > 0:
            # stock leads export by k months: corr(s_t, e_{t+k})
            a, b = pair["s"].iloc[:-k], pair["e"].iloc[k:]
        else:
            a, b = pair["s"].iloc[-k:], pair["e"].iloc[:k]
        a = np.asarray(a)
        b = np.asarray(b)
        if len(a) < 24:
            continue
        r, p = stats.pearsonr(a, b)
        lags[str(k)] = {"r": float(r), "p": float(p), "n": int(len(a))}
        if r > best_r:
            best_k, best_r, best_p = k, float(r), float(p)
    # also YoY levels
    sy = df["stock"].pct_change(12)
    ey = df["export"].pct_change(12)
    pair_y = pd.concat([sy.rename("s"), ey.rename("e")], axis=1).dropna()
    yoy = {}
    best_yk, best_yr, best_yp = None, -np.inf, None
    for k in range(-max_lag, max_lag + 1):
        if k == 0:
            a, b = pair_y["s"], pair_y["e"]
        elif k > 0:
            a, b = pair_y["s"].iloc[:-k], pair_y["e"].iloc[k:]
        else:
            a, b = pair_y["s"].iloc[-k:], pair_y["e"].iloc[:k]
        a, b = np.asarray(a), np.asarray(b)
        if len(a) < 24:
            continue
        r, p = stats.pearsonr(a, b)
        yoy[str(k)] = {"r": float(r), "p": float(p), "n": int(len(a))}
        if r > best_yr:
            best_yk, best_yr, best_yp = k, float(r), float(p)
    return {
        "ok": True,
        "n_mom": int(len(pair)),
        "n_yoy": int(len(pair_y)),
        "best_mom_lag_stock_leads_export": best_k,
        "best_mom_r": best_r,
        "best_mom_p": best_p,
        "best_yoy_lag_stock_leads_export": best_yk,
        "best_yoy_r": best_yr,
        "best_yoy_p": best_yp,
        "lags_mom": lags,
        "lags_yoy": yoy,
    }


def halloween_conditional(close: pd.Series, first_year: int, last_signal_year: int) -> dict:
    """If Oct close < Aug close in year Y, hold Nov Y -> Apr Y+1."""
    me = month_end(close)
    rows = []
    for y in range(first_year, last_signal_year + 1):
        try:
            aug = me[(me.index.year == y) & (me.index.month == 8)].iloc[-1]
            oct_ = me[(me.index.year == y) & (me.index.month == 10)].iloc[-1]
        except IndexError:
            continue
        if oct_ >= aug:
            continue
        start = pd.Timestamp(year=y, month=10, day=31)
        # align to actual month-end
        start = me[(me.index.year == y) & (me.index.month == 10)].index[-1]
        end_slice = me[(me.index.year == y + 1) & (me.index.month == 4)]
        if end_slice.empty:
            continue
        end = end_slice.index[-1]
        ret = float(me.loc[end] / me.loc[start] - 1)
        rows.append({"year": y, "aug": float(aug), "oct": float(oct_), "ret_nov_apr": ret})
    df = pd.DataFrame(rows)
    if df.empty:
        return {"n": 0, "years": []}
    wins = int((df["ret_nov_apr"] > 0).sum())
    n = int(len(df))
    out = {
        "n": n,
        "wins": wins,
        "win_rate": wins / n,
        "mean": float(df["ret_nov_apr"].mean()),
        "median": float(df["ret_nov_apr"].median()),
        "years": df.to_dict(orient="records"),
        "binomial_vs_50": binomial(wins, n, 0.5),
        "ttest_mean_gt0": ttest_mean(df["ret_nov_apr"].to_numpy(), 0.0, "greater"),
    }
    return out


def halloween_unconditional(close: pd.Series, first_year: int, last_signal_year: int) -> dict:
    """Nov-Apr vs May-Oct every year."""
    me = month_end(close)
    winter, summer = [], []
    for y in range(first_year, last_signal_year + 1):
        oct_s = me[(me.index.year == y) & (me.index.month == 10)]
        apr_s = me[(me.index.year == y + 1) & (me.index.month == 4)]
        apr0 = me[(me.index.year == y) & (me.index.month == 4)]
        if not oct_s.empty and not apr_s.empty:
            winter.append(
                {
                    "year": y,
                    "ret": float(apr_s.iloc[-1] / oct_s.iloc[-1] - 1),
                }
            )
        if not apr0.empty and not oct_s.empty:
            summer.append(
                {
                    "year": y,
                    "ret": float(oct_s.iloc[-1] / apr0.iloc[-1] - 1),
                }
            )
    w = pd.DataFrame(winter)
    s = pd.DataFrame(summer)
    common = sorted(set(w["year"]).intersection(s["year"]))
    w2 = w[w["year"].isin(common)]["ret"].to_numpy()
    s2 = s[s["year"].isin(common)]["ret"].to_numpy()
    return {
        "winter": {
            "n": int(len(w)),
            "mean": float(w["ret"].mean()) if len(w) else None,
            "win_rate": float((w["ret"] > 0).mean()) if len(w) else None,
            "ttest_gt0": ttest_mean(w["ret"].to_numpy(), 0.0, "greater") if len(w) else None,
            "binomial": binomial(int((w["ret"] > 0).sum()), int(len(w))) if len(w) else None,
        },
        "summer": {
            "n": int(len(s)),
            "mean": float(s["ret"].mean()) if len(s) else None,
            "win_rate": float((s["ret"] > 0).mean()) if len(s) else None,
            "ttest_gt0": ttest_mean(s["ret"].to_numpy(), 0.0, "greater") if len(s) else None,
        },
        "winter_minus_summer": welch_ttest(w2, s2) if len(common) >= 5 else None,
        "mw": mannwhitney(w2, s2) if len(common) >= 5 else None,
        "n_paired": int(len(common)),
    }


def odd_even_block(close: pd.Series, start: int, end: int, label: str) -> dict:
    df = calendar_returns(close, start, end)
    odd = df.loc[~df["even"], "ret"].to_numpy()
    even = df.loc[df["even"], "ret"].to_numpy()
    odd_up = int((odd > 0).sum())
    even_up = int((even > 0).sum())
    even_years_up = df.loc[(df["even"]) & (df["ret"] > 0), "year"].tolist()
    odd_years_dn = df.loc[(~df["even"]) & (df["ret"] <= 0), "year"].tolist()
    return {
        "label": label,
        "start": start,
        "end": end,
        "odd_mean": float(np.mean(odd)),
        "even_mean": float(np.mean(even)),
        "odd_up": f"{odd_up}/{len(odd)}",
        "even_up": f"{even_up}/{len(even)}",
        "even_up_years": even_years_up,
        "odd_down_years": odd_years_dn,
        "welch_odd_gt_even": welch_ttest(odd, even),
        "mw_odd_gt_even": mannwhitney(odd, even),
        "binom_odd_up": binomial(odd_up, len(odd)),
        "binom_even_up": binomial(even_up, len(even)),
        "ttest_even_lt0": ttest_mean(even, 0.0, "less"),
        "ttest_odd_gt0": ttest_mean(odd, 0.0, "greater"),
        "years": df.to_dict(orient="records"),
    }


def midterm_house() -> dict:
    # President's party House seat change, midterms 1946-2022 (20 elections)
    # Source: historical House midterm table (standard political-science series)
    # + = gain for president's party
    changes = {
        1946: -55,
        1950: -29,
        1954: -18,
        1958: -48,
        1962: -4,
        1966: -47,
        1970: -12,
        1974: -48,
        1978: -15,
        1982: -26,
        1986: -5,
        1990: -8,
        1994: -54,
        1998: +5,
        2002: +8,
        2006: -30,
        2010: -63,
        2014: -13,
        2018: -41,
        2022: -9,
    }
    vals = np.array(list(changes.values()), float)
    losses = int((vals < 0).sum())
    n = len(vals)
    return {
        "n": n,
        "losses": losses,
        "loss_rate": losses / n,
        "mean_seat_change": float(vals.mean()),
        "exceptions": [y for y, v in changes.items() if v >= 0],
        "binomial_loss_vs_50": binomial(losses, n, 0.5),
        "ttest_mean_lt0": ttest_mean(vals, 0.0, "less"),
        "claim_90pct": abs(losses / n - 0.90) < 1e-9,
    }


def bear_drawdowns(kospi: pd.Series) -> dict:
    """Descriptive peak-to-trough around cited episodes. Not a formal type test."""
    episodes = {
        "2000_dotcom": ("1999-12-01", "2001-09-30"),
        "2008_gfc": ("2007-10-01", "2009-03-31"),
        "1987_not_in_yahoo": None,
        "2020_covid": ("2020-01-01", "2020-03-31"),
        "2026_july": ("2026-05-01", "2026-08-21"),
    }
    out = {}
    for name, window in episodes.items():
        if window is None:
            out[name] = {"note": "KOSPI daily not on Yahoo for 1987"}
            continue
        sl = kospi.loc[window[0] : window[1]]
        if sl.empty:
            out[name] = {"note": "no data"}
            continue
        peak = float(sl.max())
        trough = float(sl.min())
        peak_dt = str(sl.idxmax().date())
        trough_dt = str(sl.idxmin().date())
        dd = trough / peak - 1
        out[name] = {
            "peak": peak,
            "trough": trough,
            "peak_date": peak_dt,
            "trough_date": trough_dt,
            "drawdown": dd,
        }
    return out


def samsung_sk_mechanics(sec: pd.Series, sk: pd.Series, sec_pref: pd.Series) -> dict:
    # recent prices
    def last_on(s, d):
        sl = s[s.index <= pd.Timestamp(d)]
        return None if sl.empty else float(sl.iloc[-1])

    dates = ["2026-08-18", "2026-08-19", "2026-08-20", "2026-08-21"]
    px = {d: last_on(sec, d) for d in dates}
    two_day = None
    if px["2026-08-18"] and px["2026-08-20"]:
        two_day = px["2026-08-20"] / px["2026-08-18"] - 1
    # 8/19 close vs 8/21 regular (pre-aftermarket)
    info = {}
    try:
        t = yf.Ticker("005930.KS")
        info = {
            "shares": t.info.get("sharesOutstanding"),
            "mcap": t.info.get("marketCap"),
            "impliedShares": t.info.get("impliedSharesOutstanding"),
        }
    except Exception as e:
        info = {"error": str(e)}

    # mechanical EPS lift from 3.3% cancellation
    cancel = 0.033
    eps_lift = 1 / (1 - cancel) - 1

    # DPS if 30T cash on common only vs common+pref
    common = 5_969_782_550  # typical post-split outstanding (approx, fact-check)
    pref = 822_886_700
    dps_common_only = 30e12 / common
    dps_both = 30e12 / (common + pref)

    mcap_common = (px["2026-08-21"] or 0) * common
    # pref last
    pref_px = float(sec_pref.dropna().iloc[-1]) if len(sec_pref.dropna()) else None
    mcap_pref = pref_px * pref if pref_px else None
    mcap_tot = (mcap_common + mcap_pref) if mcap_pref else None
    upside_160 = (160e12 / mcap_tot) if mcap_tot else None

    return {
        "samsung_px": px,
        "two_day_ret_18_to_20": two_day,
        "yahoo_info": info,
        "sk_last": float(sk.dropna().iloc[-1]),
        "sk_0818": last_on(sk, "2026-08-18"),
        "sk_0819": last_on(sk, "2026-08-19"),
        "sk_0820": last_on(sk, "2026-08-20"),
        "sk_0821": last_on(sk, "2026-08-21"),
        "cancel_3_3pct_eps_lift": eps_lift,
        "dps_30t_common_only": dps_common_only,
        "dps_30t_common_pref": dps_both,
        "mcap_common_08121": mcap_common,
        "pref_px": pref_px,
        "mcap_total": mcap_tot,
        "arithmetic_upside_160t_over_mcap": upside_160,
        "buyback_daily_krw_if_60_sessions": 40e12 / 60,
        "buyback_daily_shares_if_60": 24_070_000 / 60,
        "buyback_daily_krw_if_65": 40e12 / 65,
        "buyback_daily_shares_if_65": 24_070_000 / 65,
    }


def main():
    end = "2026-08-23"
    print("downloading prices...")
    ks = download_close("^KS11", "1980-01-01", end)
    kq = download_close("^KQ11", "1996-01-01", end)
    spx = download_close("^GSPC", "1980-01-01", end)
    ixic = download_close("^IXIC", "1980-01-01", end)
    sox = download_close("^SOX", "1994-01-01", end)
    sec = download_close("005930.KS", "1990-01-01", end)
    sk = download_close("000660.KS", "1990-01-01", end)
    sec_pref = download_close("005935.KS", "2000-01-01", end)
    kakao = download_close("035720.KS", "2015-01-01", end)

    # save raw month-ends for audit
    for name, s in [
        ("kospi", ks),
        ("kosdaq", kq),
        ("spx", spx),
        ("nasdaq", ixic),
        ("samsung", sec),
        ("skhynix", sk),
    ]:
        month_end(s).to_csv(OUT_DIR / f"{name}_monthend.csv", header=["close"])

    results = {
        "asof": ASOF,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "method": {
            "alpha": 0.05,
            "default": "two-sided; directional claims also report one-sided",
            "odd_even_window": "calendar year returns using prior Dec close; KOSDAQ 1998-2025 (14 even/14 odd), KOSPI same",
            "halloween_conditional": "signal year Y if Oct ME < Aug ME; hold Oct ME -> next Apr ME",
            "multiple_testing": "Benjamini-Hochberg on the core family listed in core_tests",
        },
    }

    results["odd_even"] = {
        "kospi_1998_2025": odd_even_block(ks, 1998, 2025, "KOSPI"),
        "kosdaq_1998_2025": odd_even_block(kq, 1998, 2025, "KOSDAQ"),
        "kospi_1999_2025": odd_even_block(ks, 1999, 2025, "KOSPI"),
        "kosdaq_1999_2025": odd_even_block(kq, 1999, 2025, "KOSDAQ"),
        "spx_1998_2025": odd_even_block(spx, 1998, 2025, "SPX"),
        "nasdaq_1998_2025": odd_even_block(ixic, 1998, 2025, "NASDAQ"),
    }

    results["halloween_conditional"] = {
        "spx_2015": halloween_conditional(spx, 2015, 2025),
        "nasdaq_2015": halloween_conditional(ixic, 2015, 2025),
        "kospi_2015": halloween_conditional(ks, 2015, 2025),
        "kosdaq_2015": halloween_conditional(kq, 2015, 2025),
        "spx_1998": halloween_conditional(spx, 1998, 2025),
        "nasdaq_1998": halloween_conditional(ixic, 1998, 2025),
        "kospi_1998": halloween_conditional(ks, 1998, 2025),
        "kosdaq_1998": halloween_conditional(kq, 1998, 2025),
    }

    results["halloween_unconditional"] = {
        "spx_1998_2025": halloween_unconditional(spx, 1998, 2024),
        "nasdaq_1998_2025": halloween_unconditional(ixic, 1998, 2024),
        "kospi_1998_2025": halloween_unconditional(ks, 1998, 2024),
        "kosdaq_1998_2025": halloween_unconditional(kq, 1998, 2024),
        "spx_2015": halloween_unconditional(spx, 2015, 2024),
        "nasdaq_2015": halloween_unconditional(ixic, 2015, 2024),
        "kospi_2015": halloween_unconditional(ks, 2015, 2024),
    }

    # midterm-year (US even years that are midterms: 2002,06,... vs others) on KOSDAQ/KOSPI
    # All even years already tested. Also isolate US midterm years vs non-midterm.
    midterm_years = set(range(1998, 2026, 4))  # 1998,2002,...,2022, plus 2026 not closed
    # wait 1998 is midterm, 2000 is presidential, 2002 midterm
    # even years: presidential (2000,04,08,12,16,20,24) vs midterm (1998,02,06,10,14,18,22)
    kq_df = calendar_returns(kq, 1998, 2025)
    ks_df = calendar_returns(ks, 1998, 2025)

    def split_cycle(df):
        mid = df[df["year"].isin(midterm_years)]["ret"].to_numpy()
        pres = df[(df["year"] % 4 == 0)]["ret"].to_numpy()  # presidential years
        odd = df[~df["even"]]["ret"].to_numpy()
        return {
            "midterm_mean": float(np.mean(mid)) if len(mid) else None,
            "pres_mean": float(np.mean(pres)) if len(pres) else None,
            "odd_mean": float(np.mean(odd)),
            "welch_odd_vs_midterm": welch_ttest(odd, mid) if len(mid) >= 4 else None,
            "welch_odd_vs_pres": welch_ttest(odd, pres) if len(pres) >= 4 else None,
            "n_mid": int(len(mid)),
            "n_pres": int(len(pres)),
        }

    results["us_cycle_split"] = {
        "kosdaq": split_cycle(kq_df),
        "kospi": split_cycle(ks_df),
        "note": "midterm_years = 1998,2002,...,2022; presidential = year%4==0",
    }

    results["us_midterm_house"] = midterm_house()
    results["bear_drawdowns_kospi"] = bear_drawdowns(ks)

    # lead-lag: SK Hynix / SOX / KOSPI vs Korean exports (total, FRED) as imperfect proxy
    print("trying FRED export series...")
    kor_exp = try_fred("VALEXPKRM052N")
    kor_exp_oecd = try_fred("XTEXVA01KRM667S")
    results["export_series"] = {
        "VALEXPKRM052N": None if kor_exp is None else {"n": int(len(kor_exp)), "last": float(kor_exp.iloc[-1]), "last_date": str(kor_exp.index[-1].date())},
        "XTEXVA01KRM667S": None if kor_exp_oecd is None else {"n": int(len(kor_exp_oecd)), "last": float(kor_exp_oecd.iloc[-1]), "last_date": str(kor_exp_oecd.index[-1].date())},
    }

    sk_m = month_end(sk)
    ks_m = month_end(ks)
    sox_m = month_end(sox)
    if kor_exp is not None:
        kor_m = kor_exp.resample("ME").last()
        results["leadlag_sk_vs_total_exports"] = cross_corr_lead(sk_m, kor_m)
        results["leadlag_kospi_vs_total_exports"] = cross_corr_lead(ks_m, kor_m)
    if kor_exp_oecd is not None:
        kor_m2 = kor_exp_oecd.resample("ME").last()
        results["leadlag_sk_vs_oecd_exports"] = cross_corr_lead(sk_m, kor_m2)
    results["leadlag_sk_vs_sox"] = cross_corr_lead(sk_m, sox_m)
    results["leadlag_kospi_vs_sox"] = cross_corr_lead(ks_m, sox_m)

    results["mechanics"] = samsung_sk_mechanics(sec, sk, sec_pref)

    # Kakao 8/21 move
    k_px = kakao.dropna()
    k_0820 = k_px[k_px.index <= "2026-08-20"]
    k_0821 = k_px[k_px.index <= "2026-08-21"]
    results["kakao_0821"] = {
        "d_0820": float(k_0820.iloc[-1]) if len(k_0820) else None,
        "d_0821": float(k_0821.iloc[-1]) if len(k_0821) else None,
        "ret": (float(k_0821.iloc[-1]) / float(k_0820.iloc[-1]) - 1) if len(k_0820) and len(k_0821) else None,
        "low_0821": None,
    }
    try:
        raw = yf.download("035720.KS", start="2026-08-20", end="2026-08-22", auto_adjust=True, progress=False)
        if isinstance(raw.columns, pd.MultiIndex):
            results["kakao_0821"]["low_0821"] = float(raw["Low"].iloc[-1, 0])
            results["kakao_0821"]["intraday_low_vs_0820"] = float(raw["Low"].iloc[-1, 0]) / float(k_0820.iloc[-1]) - 1
        else:
            results["kakao_0821"]["low_0821"] = float(raw["Low"].iloc[-1])
    except Exception as e:
        results["kakao_0821"]["error"] = str(e)

    # Treasury
    try:
        tnx = download_close("^TNX", "2024-01-01", end)
        tyx = download_close("^TYX", "2024-01-01", end)
        results["rates"] = {
            "us10y_last": float(tnx.iloc[-1]) / 10 if tnx.iloc[-1] > 20 else float(tnx.iloc[-1]),
            "us10y_raw": float(tnx.iloc[-1]),
            "us30y_raw": float(tyx.iloc[-1]),
            "us10y_max_2026": float(tnx[tnx.index >= "2026-01-01"].max()),
            "us30y_max_2026": float(tyx[tyx.index >= "2026-01-01"].max()),
        }
    except Exception as e:
        results["rates"] = {"error": str(e)}

    # Assemble core test family for BH
    core = []

    def add(name, p, extra):
        core.append({"name": name, "p": p, **extra})

    oe_kq = results["odd_even"]["kosdaq_1998_2025"]
    oe_ks = results["odd_even"]["kospi_1998_2025"]
    add("KOSDAQ 홀수해 평균 > 짝수해 평균 (Welch)", oe_kq["welch_odd_gt_even"]["p_two"], {"stat": oe_kq["welch_odd_gt_even"]["t"]})
    add("KOSPI 홀수해 평균 > 짝수해 평균 (Welch)", oe_ks["welch_odd_gt_even"]["p_two"], {"stat": oe_ks["welch_odd_gt_even"]["t"]})
    add("KOSDAQ 짝수해 상승확률 ≠ 50% (이항)", oe_kq["binom_even_up"]["p_two"], {"rate": oe_kq["binom_even_up"]["rate"]})
    add("KOSDAQ 홀수해 상승확률 ≠ 50% (이항)", oe_kq["binom_odd_up"]["p_two"], {"rate": oe_kq["binom_odd_up"]["rate"]})
    add("KOSDAQ 짝수해 평균 < 0 (단측 t)", oe_kq["ttest_even_lt0"]["p_alt"], {"mean": oe_kq["even_mean"]})
    add("KOSPI 홀수해 평균 > 0 (단측 t)", oe_ks["ttest_odd_gt0"]["p_alt"], {"mean": oe_ks["odd_mean"]})

    hc_spx = results["halloween_conditional"]["spx_2015"]
    hc_ix = results["halloween_conditional"]["nasdaq_2015"]
    hc_ks = results["halloween_conditional"]["kospi_2015"]
    if hc_spx["n"]:
        add("조건부로 할로윈 S&P 2015+ 승률 ≠ 50%", hc_spx["binomial_vs_50"]["p_two"], {"n": hc_spx["n"], "wins": hc_spx["wins"]})
        add("조건부 할로윈 S&P 2015+ 평균>0 (단측 t)", hc_spx["ttest_mean_gt0"]["p_alt"], {"mean": hc_spx["mean"]})
    if hc_ix["n"]:
        add("조건부 할로윈 나스닥 2015+ 승률 ≠ 50%", hc_ix["binomial_vs_50"]["p_two"], {"n": hc_ix["n"], "wins": hc_ix["wins"]})
    if hc_ks["n"]:
        add("조건부 할로윈 코스피 2015+ 승률 ≠ 50%", hc_ks["binomial_vs_50"]["p_two"], {"n": hc_ks["n"], "wins": hc_ks["wins"]})

    hu_spx = results["halloween_unconditional"]["spx_1998_2025"]
    if hu_spx["winter_minus_summer"]:
        add("S&P 겨울(11-4) vs 여름(5-10) 1998-2024 (Welch)", hu_spx["winter_minus_summer"]["p_two"], {"diff": hu_spx["winter_minus_summer"]["diff"]})
    hu_ks = results["halloween_unconditional"]["kospi_1998_2025"]
    if hu_ks["winter_minus_summer"]:
        add("KOSPI 겨울 vs 여름 1998-2024 (Welch)", hu_ks["winter_minus_summer"]["p_two"], {"diff": hu_ks["winter_minus_summer"]["diff"]})
    hu_kq = results["halloween_unconditional"]["kosdaq_1998_2025"]
    if hu_kq["winter_minus_summer"]:
        add("KOSDAQ 겨울 vs 여름 1998-2024 (Welch)", hu_kq["winter_minus_summer"]["p_two"], {"diff": hu_kq["winter_minus_summer"]["diff"]})

    add("미 중간선거 집권당 하원 의석 손실 ≠ 50% (1946-2022)", results["us_midterm_house"]["binomial_loss_vs_50"]["p_two"], {"rate": results["us_midterm_house"]["loss_rate"]})
    add("미 중간선거 집권당 평균 의석변화 < 0 (단측 t)", results["us_midterm_house"]["ttest_mean_lt0"]["p_alt"], {"mean": results["us_midterm_house"]["mean_seat_change"]})

    # lead-lag best yoy if available
    for key in ["leadlag_sk_vs_total_exports", "leadlag_kospi_vs_total_exports", "leadlag_sk_vs_sox"]:
        block = results.get(key)
        if block and block.get("ok") and block.get("best_yoy_p") is not None:
            add(f"{key} 최다상관 YoY p", block["best_yoy_p"], {"lag": block["best_yoy_lag_stock_leads_export"], "r": block["best_yoy_r"]})

    ps = [c["p"] for c in core]
    adj = bh_adjust(ps)
    for c, a in zip(core, adj):
        c["p_bh"] = a
        c["pass_raw"] = c["p"] < 0.05
        c["pass_bh"] = a < 0.05
    results["core_tests"] = core
    results["n_pass_raw"] = sum(1 for c in core if c["pass_raw"])
    results["n_pass_bh"] = sum(1 for c in core if c["pass_bh"])
    results["n_core"] = len(core)

    path = OUT_DIR / "panel_verification.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"wrote {path}")
    print(f"core tests {results['n_pass_raw']}/{results['n_core']} raw p<0.05; BH {results['n_pass_bh']}")
    for c in core:
        flag = "PASS" if c["pass_raw"] else "FAIL"
        print(f"  [{flag}] {c['name']}: p={c['p']:.4g}  BH={c['p_bh']:.4g}")


if __name__ == "__main__":
    main()
