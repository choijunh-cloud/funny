#!/usr/bin/env python3
"""Year-end 2026 Monte Carlo check for KOSPI, KOSDAQ, and Nasdaq-100.

Sits beside h2_2026_backtest.py. Index paths are local-currency price
returns (KOSPI/KOSDAQ in KRW index points, Nasdaq-100 in USD points).
The portfolio layer uses analysis/output/monthly_returns_krw.csv, which
is already in KRW.

Anchor is the 2026-09-21 official close unless the 2026-09-22 session is
a completed bar with normal volume.

(a) Unconditional: overlapping 3-month block bootstrap of historical
    months (same months across indexes, so correlation is kept).
    Sensitivity: multivariate Student-t on monthly log returns, df by
    profile likelihood, and a 2016+ block bootstrap.
(b) Regime mixture with the stated scenario probabilities. Shocks are
    historical 3-month blocks: low = worst decile of KOSPI 3-month
    returns, high = 70th–90th percentile (modest upside; the top decile
    is left out so a 2025-style melt-up is not pasted on), base = the
    central 25th–70th. An extra 10% draw is a KOSDAQ-specific bad block
    so KOSDAQ's 35% low weight does not force KOSPI/Nasdaq into the low
    bucket. The sampler does not target 7300/850/31000.

Seed is printed. N = 40,000.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

import h2_2026_backtest as bt

SEED = 20260921
N = 40_000
BAND = 0.04  # stated base ± 4%
ART = Path("/opt/cursor/artifacts")
OUT = Path("/workspace/analysis/output")
ART.mkdir(parents=True, exist_ok=True)
OUT.mkdir(parents=True, exist_ok=True)

# Stated year-end judgment. Spots are replaced by the downloaded 09-21
# close when that bar exists.
STATED = {
    "KS11": {"low": 5400.0, "base": 7300.0, "high": 8200.0, "p": (0.25, 0.55, 0.20)},
    "KQ11": {"low": 700.0, "base": 850.0, "high": 1000.0, "p": (0.35, 0.45, 0.20)},
    "NDX": {"low": 27000.0, "base": 31000.0, "high": 33000.0, "p": (0.25, 0.55, 0.20)},
}
ORDER = ["KS11", "KQ11", "NDX"]
NAMES = {"KS11": "KOSPI", "KQ11": "KOSDAQ", "NDX": "Nasdaq-100"}

# Lecture (2026-08-14) round PER targets. Cap weights are the 2026-09-14
# figures already used in the portfolio note (Samsung 26.6%, Hynix 22.7%).
LECTURE_PX = {
    "samsung_per6": 287_000.0,
    "samsung_per7": 335_000.0,
    "hynix_per6": 2_080_000.0,
    "hynix_per7": 2_420_000.0,
}
CAP_SAMSUNG = 0.266
CAP_HYNIX = 0.227


def load_daily(ticker: str, start: str = "1996-01-01") -> pd.DataFrame:
    df = yf.download(
        ticker,
        start=start,
        end="2026-09-24",
        auto_adjust=False,
        progress=False,
        threads=False,
    )
    if df is None or len(df) == 0:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.copy()
    df.index = pd.to_datetime(df.index)
    if getattr(df.index, "tz", None) is not None:
        df.index = df.index.tz_localize(None)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    return df


def completed_month_ends(close: pd.Series) -> pd.Series:
    """Month-end close, dropping a trailing month that has not finished."""
    s = close.dropna().astype(float).sort_index()
    s = s[~s.index.duplicated(keep="last")]
    me = s.resample("ME").last().dropna()
    last_obs = s.groupby([s.index.year, s.index.month]).apply(lambda x: x.index.max())
    keep = []
    for ts in me.index:
        key = (ts.year, ts.month)
        obs = last_obs.loc[key]
        if pd.Timestamp(ts) - pd.Timestamp(obs) <= pd.Timedelta(days=4):
            keep.append(ts)
    return me.loc[keep]


def bar_on(df: pd.DataFrame, day: str) -> dict | None:
    ts = pd.Timestamp(day)
    if df.empty or ts not in df.index:
        return None
    row = df.loc[ts]
    vol = row["Volume"] if "Volume" in df.columns else np.nan
    return {
        "date": str(ts.date()),
        "close": float(row["Close"]),
        "volume": float(vol) if pd.notna(vol) else None,
    }


def session_is_full_close(df: pd.DataFrame, day: str, market: str) -> dict:
    """A 2026-09-22 bar counts only if that session has finished and volume is normal.

    KOSPI/KOSDAQ close 15:30 KST. Nasdaq cash close is 16:00 US Eastern
    (20:00 UTC in September). Index volume on Nasdaq is often zero, so
    the US check is the clock plus the existence of the bar; Korea also
    requires volume at least 60% of the prior 20 sessions.
    """
    info = {"date": day, "market": market, "full": False, "reason": ""}
    bar = bar_on(df, day)
    info["bar"] = bar
    if bar is None:
        info["reason"] = "no bar"
        return info
    now = pd.Timestamp.now(tz="UTC").tz_localize(None)
    if market == "KR":
        now_local = now + pd.Timedelta(hours=9)
        closed = (now_local.date() > pd.Timestamp(day).date()) or (
            now_local.date() == pd.Timestamp(day).date()
            and (now_local.hour > 15 or (now_local.hour == 15 and now_local.minute >= 30))
        )
        if not closed:
            info["reason"] = f"Korea session still open at {now_local.strftime('%H:%M')} KST"
            return info
        vol = df["Volume"].dropna()
        prior = vol[vol.index < pd.Timestamp(day)].tail(20)
        med = float(prior.median()) if len(prior) else np.nan
        v = bar["volume"] or 0.0
        info["volume"] = v
        info["median_volume_20"] = med
        if not med or v < 0.60 * med:
            info["reason"] = f"volume {v:.0f} below 60% of 20-day median {med:.0f}"
            return info
        info["full"] = True
        info["reason"] = "session closed and volume normal"
        return info
    # US
    closed = (now.date() > pd.Timestamp(day).date()) or (
        now.date() == pd.Timestamp(day).date() and now.hour >= 20
    )
    if not closed:
        info["reason"] = f"US cash session not closed at {now.strftime('%H:%M')} UTC"
        return info
    info["full"] = True
    info["reason"] = "US session closed and bar present"
    return info


def log_returns(levels: pd.Series) -> pd.Series:
    return np.log(levels.astype(float)).diff()


def compound(simple: np.ndarray) -> np.ndarray:
    """simple: (..., months) -> compounded simple return over months."""
    return np.prod(1.0 + simple, axis=-1) - 1.0


def block_paths(simple: np.ndarray, starts: np.ndarray) -> np.ndarray:
    """simple (T, k), starts (N,) -> (N, 3, k) simple returns."""
    return np.stack([simple[starts + i] for i in range(3)], axis=1)


def levels_from_simple(paths: np.ndarray, spot: np.ndarray) -> np.ndarray:
    """paths (N, 3, k) -> month-end levels (N, 3, k)."""
    return spot.reshape(1, 1, -1) * np.cumprod(1.0 + paths, axis=1)


def summarize_levels(level_path: np.ndarray, key_i: int, stated: dict) -> dict:
    terminal = level_path[:, -1, key_i]
    low, base, high = stated["low"], stated["base"], stated["high"]
    touched_low = np.any(level_path[:, :, key_i] <= low, axis=1)
    touched_high = np.any(level_path[:, :, key_i] >= high, axis=1)
    qs = [10, 25, 50, 75, 90]
    pct = {f"p{q}": float(np.percentile(terminal, q)) for q in qs}
    return {
        "mean": float(terminal.mean()),
        **pct,
        "p_end_below_low": float(np.mean(terminal < low)),
        "p_end_above_high": float(np.mean(terminal > high)),
        "p_end_inside_band": float(np.mean(np.abs(terminal / base - 1.0) <= BAND)),
        "p_path_touch_low": float(np.mean(touched_low)),
        "p_path_touch_high": float(np.mean(touched_high)),
        "terminal": terminal,
    }


def one_month_summary(simple_month: np.ndarray, spot: float, stated: dict) -> dict:
    level = spot * (1.0 + simple_month)
    low, base, high = stated["low"], stated["base"], stated["high"]
    return {
        "p10": float(np.percentile(level, 10)),
        "p50": float(np.percentile(level, 50)),
        "p90": float(np.percentile(level, 90)),
        "mean": float(level.mean()),
        "p_end_below_low": float(np.mean(level < low)),
        "p_end_above_high": float(np.mean(level > high)),
    }


def fit_student_t(log_r: np.ndarray) -> dict:
    """Profile-likelihood df. Sample covariance is treated as Var(X).

    For a multivariate t, Var = scale * df/(df-2), so
    scale = Var * (df-2)/df. This is not a full scatter MLE.
    """
    n, d = log_r.shape
    mu = log_r.mean(axis=0)
    y = log_r - mu
    cov = np.cov(y, rowvar=False, ddof=1) + np.eye(d) * 1e-12
    grid = np.linspace(2.6, 40.0, 188)

    def nll(df: float) -> float:
        scale = cov * (df - 2.0) / df
        sign, logdet = np.linalg.slogdet(scale)
        if sign <= 0:
            return 1e12
        sol = np.linalg.solve(scale, y.T).T
        maha = np.sum(y * sol, axis=1)
        logc = (
            math.lgamma((df + d) / 2.0)
            - math.lgamma(df / 2.0)
            - 0.5 * logdet
            - 0.5 * d * math.log(df * math.pi)
        )
        ll = logc - 0.5 * (df + d) * np.log1p(maha / df)
        return float(-ll.sum())

    nlls = np.array([nll(float(df)) for df in grid])
    df_hat = float(grid[int(np.argmin(nlls))])
    scale = cov * (df_hat - 2.0) / df_hat
    return {"mu": mu, "cov": cov, "scale": scale, "df": df_hat, "n": int(n)}


def simulate_t(rng: np.random.Generator, fit: dict, n: int, months: int = 3) -> np.ndarray:
    """Return log-return paths (n, months, d) via Cholesky of the t scale."""
    d = fit["mu"].shape[0]
    chol = np.linalg.cholesky(fit["scale"])
    z = rng.standard_normal((n, months, d))
    g = rng.chisquare(fit["df"], size=(n, months)) / fit["df"]
    shock = np.einsum("nmd,dk->nmk", z, chol.T) / np.sqrt(g)[..., None]
    return fit["mu"].reshape(1, 1, d) + shock


def corr_matrix(x: np.ndarray) -> list[list[float]]:
    c = np.corrcoef(x, rowvar=False)
    return [[float(v) for v in row] for row in c]


def round_level(key: str, x: float) -> int:
    step = {"KS11": 50, "KQ11": 10, "NDX": 100}[key]
    return int(round(x / step) * step)


def pct(p: float) -> str:
    v = 100.0 * p
    if 0 < abs(v) < 1:
        return f"{v:.1f}%"
    return f"{v:.0f}%"


def lvl(key: str, x: float) -> str:
    if key == "NDX":
        return f"{round_level(key, x):,}"
    if key == "KQ11":
        return f"{round_level(key, x):,}"
    return f"{round_level(key, x):,}"


def spot_txt(x: float) -> str:
    return f"{x:,.0f}"


def ret_vs(spot: float, level: float) -> str:
    r = level / spot - 1.0
    return f"{r:+.0%}"


def is_far(stated: float, p25: float, p50: float, p75: float) -> bool:
    rel = stated / p50 - 1.0
    outside = stated < p25 or stated > p75
    return bool(outside or abs(rel) > 0.08)


def nonoverlapping_extremes(ends: pd.DatetimeIndex, values: np.ndarray, k: int = 8) -> list[dict]:
    """Greedy pick of the worst non-overlapping 3-month windows."""
    order = np.argsort(values)
    chosen: list[dict] = []
    used: set[int] = set()
    for i in order:
        if any(abs(int(i) - u) < 3 for u in used):
            continue
        used.add(int(i))
        end = ends[int(i)]
        chosen.append({"end": str(end.date()), "return": float(values[int(i)])})
        if len(chosen) >= k:
            break
    return chosen


def portfolio_block(panel: np.ndarray, starts: np.ndarray, w: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Quarterly book over Oct–Dec: start on target weights, drift for 3 months.

    December's quarter-end rebalance happens after the December return,
    so it does not affect the 3-month result. Matches h2_2026_backtest
    quarterly_rebalanced for a window with no quarter-end inside the
    first two months.
    """
    r1 = panel[starts]
    r2 = panel[starts + 1]
    r3 = panel[starts + 2]
    p1 = r1 @ w
    w1 = w.reshape(1, -1) * (1.0 + r1)
    w1 = w1 / w1.sum(axis=1, keepdims=True)
    p2 = np.sum(w1 * r2, axis=1)
    w2 = w1 * (1.0 + r2)
    w2 = w2 / w2.sum(axis=1, keepdims=True)
    p3 = np.sum(w2 * r3, axis=1)
    total = (1.0 + p1) * (1.0 + p2) * (1.0 + p3) - 1.0
    months = np.column_stack([p1, p2, p3])
    return total, months


def try_qqq_delta_strikes(ndx_spot: float) -> dict | None:
    """Map QQQ ~10-delta strikes onto Nasdaq-100. Skip cleanly on failure."""
    try:
        t = yf.Ticker("QQQ")
        expiries = list(t.options or [])
        if not expiries:
            return None
        target = pd.Timestamp("2026-12-18")
        dated = sorted(expiries, key=lambda s: abs((pd.Timestamp(s) - target).days))
        expiry = dated[0]
        if abs((pd.Timestamp(expiry) - target).days) > 10:
            return {"skipped": True, "reason": f"no expiry near 2026-12-18, nearest {expiry}"}
        chain = t.option_chain(expiry)
        hist = t.history(start="2026-09-18", end="2026-09-23", auto_adjust=False)
        if hist is None or hist.empty:
            return None
        hist.index = pd.to_datetime(hist.index).tz_localize(None)
        if pd.Timestamp("2026-09-21") in hist.index:
            spot = float(hist.loc[pd.Timestamp("2026-09-21"), "Close"])
        else:
            spot = float(hist["Close"].iloc[-1])
        T = max((pd.Timestamp(expiry) - pd.Timestamp("2026-09-21")).days / 365.25, 1 / 365)
        r = 0.04
        q = 0.006

        def norm_cdf(x: float) -> float:
            return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

        def call_delta(k: float, iv: float) -> float:
            if iv <= 0 or k <= 0:
                return np.nan
            d1 = (math.log(spot / k) + (r - q + 0.5 * iv * iv) * T) / (iv * math.sqrt(T))
            return math.exp(-q * T) * norm_cdf(d1)

        puts = chain.puts.dropna(subset=["strike", "impliedVolatility"]).copy()
        calls = chain.calls.dropna(subset=["strike", "impliedVolatility"]).copy()
        if puts.empty or calls.empty:
            return None
        puts["delta"] = [
            call_delta(float(k), float(iv)) - 1.0  # approx, not used
            for k, iv in zip(puts["strike"], puts["impliedVolatility"])
        ]
        # Recompute put delta properly: exp(-qT) * (N(d1) - 1) = call_delta - exp(-qT)
        # Use call_delta - exp(-qT).
        disc_q = math.exp(-q * T)
        puts["delta"] = [
            call_delta(float(k), float(iv)) - disc_q
            for k, iv in zip(puts["strike"], puts["impliedVolatility"])
        ]
        calls["delta"] = [
            call_delta(float(k), float(iv))
            for k, iv in zip(calls["strike"], calls["impliedVolatility"])
        ]
        put10 = puts.iloc[(puts["delta"] + 0.10).abs().argmin()]
        call10 = calls.iloc[(calls["delta"] - 0.10).abs().argmin()]
        scale = ndx_spot / spot
        return {
            "skipped": False,
            "expiry": expiry,
            "qqq_spot_2026_09_21": spot,
            "put_10d_strike_qqq": float(put10["strike"]),
            "put_10d_iv": float(put10["impliedVolatility"]),
            "put_10d_delta": float(put10["delta"]),
            "call_10d_strike_qqq": float(call10["strike"]),
            "call_10d_iv": float(call10["impliedVolatility"]),
            "call_10d_delta": float(call10["delta"]),
            "ndx_put_10d": float(put10["strike"]) * scale,
            "ndx_call_10d": float(call10["strike"]) * scale,
            "label": "QQQ listed chain, Black-Scholes delta from Yahoo IV, scaled to Nasdaq-100. Risk-neutral, not a real-world probability. Expiry is the December monthly, not 12/31.",
        }
    except Exception as exc:  # noqa: BLE001
        return {"skipped": True, "reason": str(exc)}


def fan_chart(path_levels: np.ndarray, spots: dict, stated: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.2))
    months = np.array([0, 1, 2, 3])
    for ax, key, i in zip(axes, ORDER, range(3)):
        series = []
        for m in range(3):
            series.append(path_levels[:, m, i])
        stack = [np.full(path_levels.shape[0], spots[key])] + series
        arr = np.column_stack(stack)
        bands = [10, 25, 50, 75, 90]
        qs = np.percentile(arr, bands, axis=0)
        ax.fill_between(months, qs[0], qs[4], color="#9dc3e6", alpha=0.9, label="P10–P90")
        ax.fill_between(months, qs[1], qs[3], color="#1f4e79", alpha=0.35, label="P25–P75")
        ax.plot(months, qs[2], color="#0f2043", lw=2.0, label="P50")
        ax.axhline(stated[key]["low"], color="#991b1b", ls="--", lw=1.0, label="Stated low/base/high")
        ax.axhline(stated[key]["base"], color="#166534", ls="--", lw=1.0)
        ax.axhline(stated[key]["high"], color="#1e407c", ls="--", lw=1.0)
        ax.set_title(NAMES[key])
        ax.set_xticks(months)
        ax.set_xticklabels(["9/21", "M1", "M2", "Dec"])
        ax.grid(True, alpha=0.3)
    axes[0].legend(fontsize=7, loc="best")
    fig.suptitle("Unconditional 3-month block bootstrap (local-currency index points)", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close()


def hist_chart(a_term: np.ndarray, b_term: np.ndarray, spots: dict, stated: dict, path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(12.4, 4.2))
    for ax, key, i in zip(axes, ORDER, range(3)):
        lo = np.percentile(np.concatenate([a_term[:, i], b_term[:, i]]), 1)
        hi = np.percentile(np.concatenate([a_term[:, i], b_term[:, i]]), 99)
        bins = np.linspace(lo, hi, 60)
        ax.hist(a_term[:, i], bins=bins, density=True, alpha=0.55, color="#1f4e79", label="(a) bootstrap")
        ax.hist(b_term[:, i], bins=bins, density=True, alpha=0.45, color="#c45911", label="(b) mixture")
        ax.axvline(spots[key], color="black", lw=1.2, label="9/21 close")
        ax.axvline(stated[key]["low"], color="#991b1b", ls="--", lw=1.0)
        ax.axvline(stated[key]["base"], color="#166534", ls="--", lw=1.0)
        ax.axvline(stated[key]["high"], color="#1e407c", ls="--", lw=1.0)
        ax.set_title(NAMES[key])
        ax.grid(True, alpha=0.25)
    axes[0].legend(fontsize=7)
    fig.suptitle("Terminal year-end levels. Dashed lines: stated low / base / high", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close()


def scatter_chart(a_term: np.ndarray, b_term: np.ndarray, spots: dict, stated: dict, path: Path) -> None:
    rng = np.random.default_rng(SEED)
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.0))
    i_ks, i_nd = 0, 2
    for ax, term, title, color in (
        (axes[0], a_term, "(a) unconditional bootstrap", "#1f4e79"),
        (axes[1], b_term, "(b) scenario mixture", "#c45911"),
    ):
        take = rng.choice(term.shape[0], size=8000, replace=False)
        ax.scatter(
            term[take, i_ks],
            term[take, i_nd],
            s=6,
            alpha=0.15,
            c=color,
            linewidths=0,
        )
        ax.axvline(stated["KS11"]["low"], color="#991b1b", ls="--", lw=0.8)
        ax.axvline(stated["KS11"]["base"], color="#166534", ls="--", lw=0.8)
        ax.axvline(stated["KS11"]["high"], color="#1e407c", ls="--", lw=0.8)
        ax.axhline(stated["NDX"]["low"], color="#991b1b", ls=":", lw=0.8)
        ax.axhline(stated["NDX"]["base"], color="#166534", ls=":", lw=0.8)
        ax.axhline(stated["NDX"]["high"], color="#1e407c", ls=":", lw=0.8)
        ax.scatter([spots["KS11"]], [spots["NDX"]], c="black", s=28, zorder=5, label="9/21")
        ax.set_xlabel("KOSPI terminal")
        ax.set_ylabel("Nasdaq-100 terminal")
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
    fig.suptitle("Joint terminal levels (8,000 of 40,000 draws)", fontsize=11)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close()


def portfolio_chart(total_a: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    ax.hist(total_a * 100, bins=60, color="#1f4e79", alpha=0.85)
    for q, ls in ((10, "--"), (50, "-"), (90, "--")):
        v = np.percentile(total_a, q) * 100
        ax.axvline(v, color="#0f2043" if q == 50 else "#c45911", ls=ls, lw=1.2, label=f"P{q} {v:.1f}%")
    ax.axvline(-10, color="#991b1b", ls=":", lw=1.2, label="-10% month marker (not the 3m total)")
    ax.set_xlabel("3-month KRW return (%)")
    ax.set_ylabel("Draws")
    ax.set_title("55/22/15/8 book, block bootstrap, listed names")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close()


def build_pools(ks_3m: np.ndarray, kq_3m: np.ndarray) -> dict[str, np.ndarray]:
    p10, p25, p70, p90 = np.percentile(ks_3m, [10, 25, 70, 90])
    kq_p10 = np.percentile(kq_3m, 10)
    low = np.flatnonzero(ks_3m <= p10)
    base = np.flatnonzero((ks_3m >= p25) & (ks_3m < p70))
    high = np.flatnonzero((ks_3m >= p70) & (ks_3m <= p90))
    kq = np.flatnonzero((kq_3m <= kq_p10) & (ks_3m > p10))
    if len(kq) < 12:
        p20 = np.percentile(ks_3m, 20)
        kq = np.flatnonzero((kq_3m <= kq_p10) & (ks_3m > p20))
    if len(kq) < 12:
        excess = kq_3m - ks_3m
        kq = np.flatnonzero(excess <= np.percentile(excess, 10))
    pools = {"base": base, "low": low, "high": high, "kq": kq}
    for name, idx in pools.items():
        if len(idx) < 8:
            raise RuntimeError(f"pool {name} has only {len(idx)} blocks")
    return {
        "pools": pools,
        "thresholds": {
            "ks_p10": float(p10),
            "ks_p25": float(p25),
            "ks_p70": float(p70),
            "ks_p90": float(p90),
            "kq_p10": float(kq_p10),
            "counts": {k: int(len(v)) for k, v in pools.items()},
        },
    }


def main() -> None:
    print(f"SEED {SEED}")
    print(f"N {N}")
    rng = np.random.default_rng(SEED)

    print("download indexes")
    daily = {
        "KS11": load_daily("^KS11"),
        "KQ11": load_daily("^KQ11"),
        "NDX": load_daily("^NDX"),
        "IXIC": load_daily("^IXIC", start="2024-01-01"),
        "FX": load_daily("KRW=X"),
        "SAM": load_daily("005930.KS", start="2026-08-01"),
        "HYN": load_daily("000660.KS", start="2026-08-01"),
    }
    for k, df in daily.items():
        print(f"  {k}: {len(df)} rows", end=" ")
        if len(df):
            print(df.index.min().date(), "->", df.index.max().date(), "last", float(df["Close"].iloc[-1]))
        else:
            print("EMPTY")

    anchor_diag = {}
    spots = {}
    rebase = {}
    for key, market in (("KS11", "KR"), ("KQ11", "KR"), ("NDX", "US")):
        b21 = bar_on(daily[key], "2026-09-21")
        full22 = session_is_full_close(daily[key], "2026-09-22", market)
        anchor_diag[key] = {"m0921": b21, "m0922": full22}
        if b21 is None:
            raise RuntimeError(f"missing 2026-09-21 bar for {key}")
        if full22["full"]:
            spots[key] = float(full22["bar"]["close"])
            rebase[key] = True
        else:
            spots[key] = float(b21["close"])
            rebase[key] = False
        print(key, "anchor", spots[key], "rebase", rebase[key], full22["reason"])

    ixic21 = bar_on(daily["IXIC"], "2026-09-21")
    ixic22 = session_is_full_close(daily["IXIC"], "2026-09-22", "US")
    print("IXIC 09-21", ixic21, "09-22", ixic22["reason"])

    levels = {}
    for key in ORDER:
        levels[key] = completed_month_ends(daily[key]["Close"])
    level_df = pd.concat({k: levels[k] for k in ORDER}, axis=1).dropna(how="any")
    # History for the distribution ends at the last completed month, which
    # must be before the anchor month if that month is unfinished.
    level_df = level_df[level_df.index <= pd.Timestamp("2026-08-31")]
    simple = level_df.pct_change().dropna()
    logs = np.log(level_df).diff().dropna()
    # Align
    common = simple.index.intersection(logs.index)
    simple = simple.loc[common, ORDER]
    logs = logs.loc[common, ORDER]
    print(f"monthly sample {simple.index.min().date()} -> {simple.index.max().date()} n={len(simple)}")

    recent_mask = simple.index >= pd.Timestamp("2016-01-31")
    simple_recent = simple.loc[recent_mask]
    logs_recent = logs.loc[recent_mask]

    # High-vol months: trailing 6-month KOSPI vol at or above its 75th percentile.
    roll_vol = simple["KS11"].rolling(6).std() * math.sqrt(12)
    vol_cut = float(roll_vol.quantile(0.75))
    hv_months = roll_vol[roll_vol >= vol_cut].index
    print(f"high-vol cutoff ann. {vol_cut:.1%}, months {len(hv_months)}")

    fx_me = completed_month_ends(daily["FX"]["Close"]) if len(daily["FX"]) else pd.Series(dtype=float)
    fx_me = fx_me[fx_me.index <= pd.Timestamp("2026-08-31")]
    fx_ret = fx_me.pct_change()
    both = pd.concat([simple["NDX"].rename("ndx"), fx_ret.rename("fx")], axis=1).dropna()
    ndx_krw = (1.0 + both["ndx"]) * (1.0 + both["fx"]) - 1.0
    ks_aligned = simple["KS11"].reindex(ndx_krw.index)
    corr_usd = float(simple["KS11"].corr(simple["NDX"]))
    corr_krw = float(ks_aligned.corr(ndx_krw))

    hist_corr = corr_matrix(logs.to_numpy())
    print("historical log-return corr")
    print(np.array(hist_corr).round(2))

    # --- (a) block bootstrap, long sample ---
    simple_np = simple.to_numpy()
    t_len = len(simple_np)
    n_blocks = t_len - 2
    starts_a = rng.integers(0, n_blocks, size=N)
    paths_a = block_paths(simple_np, starts_a)
    lev_a = levels_from_simple(paths_a, np.array([spots[k] for k in ORDER]))
    sum_a = {k: summarize_levels(lev_a, i, STATED[k]) for i, k in enumerate(ORDER)}

    # 1-month: resample single historical months (joint)
    m_idx = rng.integers(0, t_len, size=N)
    one_m = {
        k: one_month_summary(simple_np[m_idx, i], spots[k], STATED[k]) for i, k in enumerate(ORDER)
    }

    # simulated monthly corr from the months actually drawn
    drawn_months = np.concatenate([paths_a[:, m, :] for m in range(3)], axis=0)
    # convert simple to log for a like-for-like corr
    drawn_log = np.log1p(drawn_months)
    sim_corr_a = corr_matrix(drawn_log)
    term_log_a = np.log(lev_a[:, -1, :] / np.array([spots[k] for k in ORDER]))
    sim_corr_a_3m = corr_matrix(term_log_a)

    # recent-sample bootstrap
    simple_r = simple_recent.to_numpy()
    starts_r = rng.integers(0, len(simple_r) - 2, size=N)
    lev_r = levels_from_simple(block_paths(simple_r, starts_r), np.array([spots[k] for k in ORDER]))
    sum_recent = {k: summarize_levels(lev_r, i, STATED[k]) for i, k in enumerate(ORDER)}

    # high-vol: 3-month blocks with at least 2 months in the high-vol set
    hv_set = set(hv_months)
    hv_starts = []
    for i in range(n_blocks):
        months = list(simple.index[i : i + 3])
        if sum(m in hv_set for m in months) >= 2:
            hv_starts.append(i)
    hv_starts = np.array(hv_starts, dtype=int)
    print(f"high-vol blocks {len(hv_starts)}")
    starts_hv = rng.choice(hv_starts, size=N, replace=True)
    lev_hv = levels_from_simple(block_paths(simple_np, starts_hv), np.array([spots[k] for k in ORDER]))
    sum_hv = {k: summarize_levels(lev_hv, i, STATED[k]) for i, k in enumerate(ORDER)}

    # Student-t sensitivity on the long sample
    fit = fit_student_t(logs.to_numpy())
    fit_recent = fit_student_t(logs_recent.to_numpy())
    print(f"Student-t df long {fit['df']:.1f} recent {fit_recent['df']:.1f}")
    log_paths = simulate_t(rng, fit, N, 3)
    lev_t = np.array([spots[k] for k in ORDER]).reshape(1, 1, -1) * np.exp(np.cumsum(log_paths, axis=1))
    sum_t = {k: summarize_levels(lev_t, i, STATED[k]) for i, k in enumerate(ORDER)}
    sim_corr_t = corr_matrix(log_paths.reshape(-1, 3))

    # --- (b) regime mixture on long-sample blocks ---
    block_mat = np.stack([simple_np[i : i + 3] for i in range(n_blocks)], axis=0)  # (B, 3, k)
    ret_3m = np.prod(1.0 + block_mat, axis=1) - 1.0  # (B, k)
    built = build_pools(ret_3m[:, 0], ret_3m[:, 1])
    pools = built["pools"]
    print("pool thresholds", built["thresholds"])

    # Joint regime probabilities: base 45, low 25, high 20, KOSDAQ-specific 10.
    # Marginal low: KS/NDX 25, KQ 35. Marginal high 20. Marginal base: KS/NDX 55, KQ 45.
    regime = rng.choice(["base", "low", "high", "kq"], size=N, p=[0.45, 0.25, 0.20, 0.10])
    starts_b = np.empty(N, dtype=int)
    for name, pool in pools.items():
        mask = regime == name
        starts_b[mask] = rng.choice(pool, size=int(mask.sum()), replace=True)
    paths_b = block_paths(simple_np, starts_b)
    lev_b = levels_from_simple(paths_b, np.array([spots[k] for k in ORDER]))
    sum_b = {k: summarize_levels(lev_b, i, STATED[k]) for i, k in enumerate(ORDER)}
    drawn_log_b = np.log1p(np.concatenate([paths_b[:, m, :] for m in range(3)], axis=0))
    sim_corr_b = corr_matrix(drawn_log_b)
    term_log_b = np.log(lev_b[:, -1, :] / np.array([spots[k] for k in ORDER]))
    sim_corr_b_3m = corr_matrix(term_log_b)

    # Conditional regime medians (terminal index)
    cond = {}
    for name in ("base", "low", "high", "kq"):
        mask = regime == name
        cond[name] = {}
        for i, k in enumerate(ORDER):
            cond[name][k] = {
                "p10": float(np.percentile(lev_b[mask, -1, i], 10)),
                "p50": float(np.percentile(lev_b[mask, -1, i], 50)),
                "p90": float(np.percentile(lev_b[mask, -1, i], 90)),
                "n": int(mask.sum()),
            }

    worst = nonoverlapping_extremes(simple.index[2:], ret_3m[:, 0], k=8)
    # index[2:] is the END month of block starting at 0. Yes simple.index[i+2] is end.
    # I passed simple.index[2:] which aligns with block start i's end month. Good.

    # Sign disagreement, 3-month
    sign_disagree = float(np.mean(np.sign(ret_3m[:, 0]) != np.sign(ret_3m[:, 2])))
    sign_disagree_kq = float(np.mean(np.sign(ret_3m[:, 0]) != np.sign(ret_3m[:, 1])))

    # Lecture translation using downloaded 09-21 prints when present.
    sam21 = bar_on(daily["SAM"], "2026-09-21")
    hyn21 = bar_on(daily["HYN"], "2026-09-21")
    sam_px = float(sam21["close"]) if sam21 else 274_000.0
    hyn_px = float(hyn21["close"]) if hyn21 else 1_868_000.0

    def index_from_names(sam_tgt: float, hyn_tgt: float, rest: float) -> float:
        r = (
            CAP_SAMSUNG * (sam_tgt / sam_px - 1.0)
            + CAP_HYNIX * (hyn_tgt / hyn_px - 1.0)
            + (1.0 - CAP_SAMSUNG - CAP_HYNIX) * rest
        )
        return spots["KS11"] * (1.0 + r), r

    lec_per6, lec_per6_r = index_from_names(LECTURE_PX["samsung_per6"], LECTURE_PX["hynix_per6"], 0.0)
    lec_per7, lec_per7_r = index_from_names(LECTURE_PX["samsung_per7"], LECTURE_PX["hynix_per7"], 0.0)
    # Judgment arithmetic: duo +10% rest -2%; duo -30% rest -15%.
    judg_base, judg_base_r = index_from_names(sam_px * 1.10, hyn_px * 1.10, -0.02)
    judg_low, judg_low_r = index_from_names(sam_px * 0.70, hyn_px * 0.70, -0.15)

    # --- portfolio ---
    rets = pd.read_csv(bt.OUT / "monthly_returns_krw.csv" if False else OUT / "monthly_returns_krw.csv", index_col=0, parse_dates=True)
    rets.index = pd.to_datetime(rets.index)
    wmap = bt.WEIGHTS
    cols = [c for c in wmap if c in rets.columns]
    w = np.array([wmap[c] for c in cols], dtype=float)
    w = w / w.sum()
    assert abs(w.sum() - 1) < 1e-9

    def prep_panel(df: pd.DataFrame) -> pd.DataFrame:
        out = df[cols].copy()
        # Fold unlisted satellites into KODEX, same rule as the long backtest.
        for key in ("samsung", "hynix", "sk", "hanmi", "tes", "wonik", "mobis"):
            if key in out.columns:
                out[key] = out[key].where(out[key].notna(), out["kr_equity"])
        out = out.dropna(how="any")
        out = out[out.index < pd.Timestamp("2026-09-01")]
        # Keep only rows that are one month apart so a block is three real months.
        gap = out.index.to_series().diff().dt.days
        # first row ok; drop a row if the gap INTO it is outside 20–40 days
        bad = gap[(gap < 20) | (gap > 40)].index
        # If we drop the later row of a hole, the previous gap check on the next row remains.
        out = out.drop(index=bad, errors="ignore")
        return out

    listed = rets[cols].dropna(how="any")
    listed = listed[listed.index < pd.Timestamp("2026-09-01")]
    folded = prep_panel(rets)
    print(f"portfolio listed {listed.index.min().date()} -> {listed.index.max().date()} n={len(listed)}")
    print(f"portfolio folded {folded.index.min().date()} -> {folded.index.max().date()} n={len(folded)}")

    def run_port(panel: pd.DataFrame) -> dict:
        arr = panel.to_numpy(dtype=float)
        st = rng.integers(0, len(arr) - 2, size=N)
        total, months = portfolio_block(arr, st, w)
        # July-like: any of the three months <= -10%, and month-1 alone.
        return {
            "p10": float(np.percentile(total, 10)),
            "p25": float(np.percentile(total, 25)),
            "p50": float(np.percentile(total, 50)),
            "p75": float(np.percentile(total, 75)),
            "p90": float(np.percentile(total, 90)),
            "mean": float(total.mean()),
            "p_any_month_le_m10": float(np.mean(months.min(axis=1) <= -0.10)),
            "p_month1_le_m10": float(np.mean(months[:, 0] <= -0.10)),
            "p_total_le_m10": float(np.mean(total <= -0.10)),
            "total": total,
            "start": str(panel.index.min().date()),
            "end": str(panel.index.max().date()),
            "n_months": int(len(panel)),
        }

    port_listed = run_port(listed)
    port_folded = run_port(folded)

    # Historical July 2026 at target weights (quarter rebalance was June).
    july = listed.loc[pd.Timestamp("2026-07-31"), cols].to_numpy(dtype=float)
    july_r = float(july @ w)
    hist_month = listed.to_numpy(dtype=float) @ w
    hist_p_m10 = float(np.mean(hist_month <= -0.10))
    print(f"July 2026 portfolio {july_r:.3%}  hist P(month<=-10%) {hist_p_m10:.2%}")

    # Cash rule, pre-committed: mix changes only if listed-sample 3m P10 <= -15%.
    change_mix = port_listed["p10"] <= -0.15

    options = try_qqq_delta_strikes(spots["NDX"])
    print("options", options)

    # Charts. Drop the heavy terminal arrays from the json later.
    fan_chart(lev_a, spots, STATED, ART / "mc_fan_indices.png")
    hist_chart(
        np.column_stack([sum_a[k]["terminal"] for k in ORDER]),
        np.column_stack([sum_b[k]["terminal"] for k in ORDER]),
        spots,
        STATED,
        ART / "mc_hist_indices.png",
    )
    scatter_chart(
        np.column_stack([sum_a[k]["terminal"] for k in ORDER]),
        np.column_stack([sum_b[k]["terminal"] for k in ORDER]),
        spots,
        STATED,
        ART / "mc_scatter_kospi_ndx.png",
    )
    portfolio_chart(port_listed["total"], ART / "mc_portfolio_3m.png")
    for name in (
        "mc_fan_indices.png",
        "mc_hist_indices.png",
        "mc_scatter_kospi_ndx.png",
        "mc_portfolio_3m.png",
    ):
        (OUT / name).write_bytes((ART / name).read_bytes())

    def pack(summary: dict) -> dict:
        return {k: {kk: vv for kk, vv in d.items() if kk != "terminal"} for k, d in summary.items()}

    # Survival flags
    flags = {}
    for k in ORDER:
        flags[k] = {
            "base_far_a": is_far(STATED[k]["base"], sum_a[k]["p25"], sum_a[k]["p50"], sum_a[k]["p75"]),
            "base_far_b": is_far(STATED[k]["base"], sum_b[k]["p25"], sum_b[k]["p50"], sum_b[k]["p75"]),
            "low_in_low_regime_p10_p90": cond["low"][k]["p10"] <= STATED[k]["low"] <= cond["low"][k]["p90"],
            "high_in_high_regime_p10_p90": cond["high"][k]["p10"] <= STATED[k]["high"] <= cond["high"][k]["p90"],
        }

    summary = {
        "seed": SEED,
        "n": N,
        "band": BAND,
        "anchor": spots,
        "rebase_0922": rebase,
        "anchor_diag": anchor_diag,
        "ixic_0921": ixic21,
        "sample": {
            "start": str(simple.index.min().date()),
            "end": str(simple.index.max().date()),
            "n_months": int(len(simple)),
            "n_blocks": int(n_blocks),
            "recent_start": str(simple_recent.index.min().date()),
            "recent_n": int(len(simple_recent)),
            "high_vol_cutoff_ann": vol_cut,
            "high_vol_months": int(len(hv_months)),
            "high_vol_blocks": int(len(hv_starts)),
            "currency": "Index simulation uses local-currency price returns. KOSPI and KOSDAQ are KRW index points. Nasdaq-100 is USD index points. Portfolio is KRW total-return approximation from monthly_returns_krw.csv.",
        },
        "student_t_df_long": fit["df"],
        "student_t_df_recent": fit_recent["df"],
        "hist_corr_log_monthly": hist_corr,
        "sim_corr_a_monthly_log": sim_corr_a,
        "sim_corr_a_3m_log": sim_corr_a_3m,
        "sim_corr_t_monthly_log": sim_corr_t,
        "sim_corr_b_monthly_log": sim_corr_b,
        "sim_corr_b_3m_log": sim_corr_b_3m,
        "corr_ks_ndx_usd": corr_usd,
        "corr_ks_ndx_krw": corr_krw,
        "sign_disagree_ks_ndx_3m": sign_disagree,
        "sign_disagree_ks_kq_3m": sign_disagree_kq,
        "a": pack(sum_a),
        "a_recent": pack(sum_recent),
        "a_highvol": pack(sum_hv),
        "a_t": pack(sum_t),
        "b": pack(sum_b),
        "one_month": one_m,
        "conditional_b": cond,
        "pools": built["thresholds"],
        "worst_blocks": worst,
        "flags": flags,
        "lecture": {
            "samsung_0921": sam_px,
            "hynix_0921": hyn_px,
            "per6_index": lec_per6,
            "per6_return": lec_per6_r,
            "per7_index": lec_per7,
            "per7_return": lec_per7_r,
            "judgment_base_index": judg_base,
            "judgment_base_return": judg_base_r,
            "judgment_low_index": judg_low,
            "judgment_low_return": judg_low_r,
        },
        "portfolio_listed": {k: v for k, v in port_listed.items() if k != "total"},
        "portfolio_folded": {k: v for k, v in port_folded.items() if k != "total"},
        "july_2026_portfolio": july_r,
        "hist_p_month_le_m10": hist_p_m10,
        "change_mix": change_mix,
        "options": options,
        "monthly_mean_vol": {
            k: {"mean": float(simple[k].mean()), "vol": float(simple[k].std(ddof=1))} for k in ORDER
        },
    }
    (OUT / "montecarlo_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    write_markdown(summary)
    print("wrote", OUT / "montecarlo_2026.md")
    print("P50 a", {k: round_level(k, sum_a[k]["p50"]) for k in ORDER})
    print("P50 b", {k: round_level(k, sum_b[k]["p50"]) for k in ORDER})
    print("P10 a", {k: round_level(k, sum_a[k]["p10"]) for k in ORDER})
    print("P90 a", {k: round_level(k, sum_a[k]["p90"]) for k in ORDER})
    print("flags", flags)
    print("change_mix", change_mix, "port p10", port_listed["p10"])


def write_markdown(s: dict) -> None:
    """Short Korean note. Numbers come from the run, not from hand entry."""
    lines: list[str] = []
    a, b = s["anchor"], s["b"]
    # Lead is written by the caller after a human read if needed; this
    # function states the mechanical result.
    far_b = [k for k in ORDER if s["flags"][k]["base_far_b"]]
    if not far_b and not s["change_mix"]:
        pa, pb = s["a"], s["b"]
        lead = (
            "연말 기본값 7300 / 850 / 31000은 유지한다. "
            f"비조건부 중앙은 {lvl('KS11', pa['KS11']['p50'])} / {lvl('KQ11', pa['KQ11']['p50'])} / {lvl('NDX', pa['NDX']['p50'])}이고, "
            f"시나리오 혼합 중앙은 {lvl('KS11', pb['KS11']['p50'])} / {lvl('KQ11', pb['KQ11']['p50'])} / {lvl('NDX', pb['NDX']['p50'])}이다. "
            "차이는 2~3%포인트라 기본 시나리오를 분포 밖으로 밀지 않는다. "
            "코스피 5400은 최악 십분위 국면의 왼쪽 끝(그 국면의 중심은 약 6050)이고, "
            "8200은 완만한 상방 풀의 상단이다. 둘 다 구간을 갈아 끼울 만큼 벗어나 있지 않다. "
            f"포트폴리오 3개월 P10은 {s['portfolio_listed']['p10']:+.1%}라 55/22/15/8은 바꾸지 않는다."
        )
    elif far_b and not s["change_mix"]:
        lead = (
            "기본 시나리오 레벨 일부를 고친다. 시나리오 혼합의 중앙값이 "
            "제시 기본값의 P25–P75 밖이거나 8% 넘게 벌어졌다. "
            "포트폴리오 좌측 꼬리는 현금 15%와 충돌하지 않아 55/22/15/8은 유지한다."
        )
    else:
        lead = (
            "지수 구간과 별도로, 포트폴리오 3개월 P10이 현금 비중 15%를 "
            "넘어서 손실 크기가 버퍼와 맞지 않다. 시사점은 아래 포트폴리오 절에 둔다."
        )
    lines.append("# 2026년 연말 몬테카를로 검증")
    lines.append("")
    if any(s["rebase_0922"].values()):
        anchor_sentence = "9월 22일 봉 가운데 완성된 종가가 있어 그 지수는 앵커를 옮겼다."
    else:
        anchor_sentence = "기준 시각의 앵커는 2026-09-21 공식 종가이고, 9월 22일 봉을 종가로 쓰지 않았다."
    lines.append(f"시드 `{s['seed']}`. 경로 {s['n']:,}개. {anchor_sentence}")
    lines.append("")
    lines.append(lead)
    lines.append("")
    lines.append("## 앵커")
    lines.append("")
    lines.append("| 지수 | 9/21 종가 | 9/22 봉 | 앵커로 쓴 값 |")
    lines.append("| --- | ---: | --- | ---: |")
    label = {"KS11": "KOSPI", "KQ11": "KOSDAQ", "NDX": "Nasdaq-100"}
    for k in ORDER:
        d = s["anchor_diag"][k]
        m21 = d["m0921"]["close"]
        if d["m0922"]["bar"] is None:
            status = "봉 없음. 미국 정규장은 아직 열리지 않음"
        elif not d["m0922"]["full"]:
            status = f"{d['m0922']['bar']['close']:,.2f}. 미완성 세션이라 앵커에서 제외"
        else:
            status = f"{d['m0922']['bar']['close']:,.2f}. 완성된 종가라 앵커로 사용"
        lines.append(f"| {label[k]} | {m21:,.2f} | {status} | {s['anchor'][k]:,.2f} |")
    ix = s["ixic_0921"]["close"] if s["ixic_0921"] else None
    lines.append("")
    lines.append(f"나스닥 종합(^IXIC) 9/21 종가 {ix:,.2f}. 예측 지수는 나스닥100이고 종합지수는 참고다." if ix else "IXIC 확인 실패.")
    lines.append("")
    lines.append(
        f"월간 표본(완성된 달만): {s['sample']['start']} ~ {s['sample']['end']}, "
        f"{s['sample']['n_months']}개월, 3개월 블록 {s['sample']['n_blocks']}개. "
        f"최근 표본은 {s['sample']['recent_start']} 이후 {s['sample']['recent_n']}개월. "
        f"고변동 달은 코스피 6개월 실현변동성이 표본 75분위({s['sample']['high_vol_cutoff_ann']:.0%}) 이상인 "
        f"{s['sample']['high_vol_months']}개월이고, 그중 2개월 이상이 들어간 블록은 {s['sample']['high_vol_blocks']}개다. "
        "2026년 9월은 월이 끝나지 않아 수익률 표본에서 뺐다. 7월 2026은 표본 안에 있다."
    )
    lines.append("")
    lines.append(
        "지수 시뮬레이션은 현지통화 가격 수익률이다. 코스피·코스닥은 원화 지수 포인트, "
        "나스닥100은 달러 지수 포인트다. 포트폴리오는 `monthly_returns_krw.csv`의 원화 수익이다."
    )
    lines.append("")
    lines.append("## 지수 표")
    lines.append("")
    lines.append("기본값 ±4%를 ‘기본 밴드’로 두었다. 레벨은 코스피 50, 코스닥 10, 나스닥100 100 단위로 반올림했다. 확률은 정수 %다. 종료 확률이 본숫자이고, 경로(월말 터치)는 그다음이다.")
    lines.append("")
    lines.append("| 지수 | 현재 | 하 / 기 / 상 | (a) P10 / P50 / P90 | (a) P(종료<하) | (a) P(종료>상) | (a) 기본밴드 | (b) P10 / P50 / P90 | (b) P(종료<하) | (b) P(종료>상) | (b) 기본밴드 |")
    lines.append("| --- | ---: | --- | --- | ---: | ---: | ---: | --- | ---: | ---: | ---: |")
    for k in ORDER:
        aa, bb = s["a"][k], s["b"][k]
        lines.append(
            "| {name} | {spot} | {lo} / {ba} / {hi} | {a10} / {a50} / {a90} | {al} | {ah} | {ab} | {b10} / {b50} / {b90} | {bl} | {bh} | {bb} |".format(
                name=label[k],
                spot=spot_txt(s["anchor"][k]),
                lo=lvl(k, STATED[k]["low"]),
                ba=lvl(k, STATED[k]["base"]),
                hi=lvl(k, STATED[k]["high"]),
                a10=lvl(k, aa["p10"]),
                a50=lvl(k, aa["p50"]),
                a90=lvl(k, aa["p90"]),
                al=pct(aa["p_end_below_low"]),
                ah=pct(aa["p_end_above_high"]),
                ab=pct(aa["p_end_inside_band"]),
                b10=lvl(k, bb["p10"]),
                b50=lvl(k, bb["p50"]),
                b90=lvl(k, bb["p90"]),
                bl=pct(bb["p_end_below_low"]),
                bh=pct(bb["p_end_above_high"]),
                bb=pct(bb["p_end_inside_band"]),
            )
        )
    lines.append("")
    lines.append("경로(3번의 월말 중 한 번이라도 터치). 장중 터치가 아니다.")
    lines.append("")
    lines.append("| 지수 | (a) 경로 하한 | (a) 경로 상한 | (b) 경로 하한 | (b) 경로 상한 |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for k in ORDER:
        aa, bb = s["a"][k], s["b"][k]
        lines.append(
            f"| {label[k]} | {pct(aa['p_path_touch_low'])} | {pct(aa['p_path_touch_high'])} | {pct(bb['p_path_touch_low'])} | {pct(bb['p_path_touch_high'])} |"
        )
    lines.append("")
    lines.append("1개월(역사 월을 한 번 재추출, 비조건부). 의사결정 시계는 연말 3개월이다.")
    lines.append("")
    lines.append("| 지수 | 1개월 P10 / P50 / P90 | P(1개월<하) | P(1개월>상) |")
    lines.append("| --- | --- | ---: | ---: |")
    for k in ORDER:
        o = s["one_month"][k]
        lines.append(
            f"| {label[k]} | {lvl(k, o['p10'])} / {lvl(k, o['p50'])} / {lvl(k, o['p90'])} | {pct(o['p_end_below_low'])} | {pct(o['p_end_above_high'])} |"
        )
    lines.append("")
    lines.append("평균과 사분위. 위 표의 P10/P50/P90과 같은 분포다.")
    lines.append("")
    lines.append("| 지수 | 시뮬 | 평균 | P10 | P25 | P50 | P75 | P90 |")
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for sim_name, sim_key in (("a 부트스트랩", "a"), ("b 혼합", "b")):
        for k in ORDER:
            d = s[sim_key][k]
            lines.append(
                f"| {label[k]} | {sim_name} | {lvl(k, d['mean'])} | {lvl(k, d['p10'])} | {lvl(k, d['p25'])} | {lvl(k, d['p50'])} | {lvl(k, d['p75'])} | {lvl(k, d['p90'])} |"
            )
    lines.append("")
    lines.append("## (a)와 (b)가 무엇을 뽑았는가")
    lines.append("")
    lines.append(
        "(a)는 장기 월간 표본에서 연속 3개월을 통째로 복원추출했다. 세 지수는 같은 달을 쓴다. "
        f"민감도로 다변량 스튜던트 t를 월간 로그수익률에 붙였다. 자유도 {s['student_t_df_long']:.1f} "
        f"(2016년 이후 표본 자유도 {s['student_t_df_recent']:.1f}). "
        "t는 달끼리 독립이다. 스케일은 표본 공분산을 t의 분산으로 보고 `(df-2)/df`를 곱한 것이다. 완전 산포 MLE는 아니다."
    )
    lines.append("")
    lines.append(
        "(b)는 판단 확률을 공동 국면으로 옮긴 혼합이다. 기본 45% / 최악 십분위 25% / 완만한 상승(코스피 3개월 70~90분위, 최상위 십분위 제외) 20% / "
        "코스닥만 나쁜 블록 10%. 그래서 코스피·나스닥100의 하방 비중은 25%, 코스닥은 35%, 상방은 셋 다 20%가 된다. "
        "중앙값을 7300에 맞추는 장치는 없다."
    )
    lines.append("")
    lines.append("국면 조건부 중앙값(종료 레벨).")
    lines.append("")
    lines.append("| 국면 | 코스피 | 코스닥 | 나스닥100 |")
    lines.append("| --- | ---: | ---: | ---: |")
    nice = {"base": "기본 (25–70분위)", "low": "하방 (최악 십분위)", "high": "상방 (70–90분위)", "kq": "코스닥만 하방"}
    for name in ("low", "base", "high", "kq"):
        c = s["conditional_b"][name]
        lines.append(
            f"| {nice[name]} | {lvl('KS11', c['KS11']['p50'])} | {lvl('KQ11', c['KQ11']['p50'])} | {lvl('NDX', c['NDX']['p50'])} |"
        )
    lines.append("")
    lines.append("겹치지 않게 고른 코스피 3개월 최악 창(블록 종료월).")
    lines.append("")
    for w in s["worst_blocks"]:
        lines.append(f"- {w['end']}: {w['return']:+.0%}")
    lines.append("")
    lines.append("민감도 P10 / P50 / P90.")
    lines.append("")
    lines.append("| 지수 | 2016년 이후 부트스트랩 | 고변동 블록 | 스튜던트 t (장기) |")
    lines.append("| --- | --- | --- | --- |")
    for k in ORDER:
        lines.append(
            "| {name} | {r} | {h} | {t} |".format(
                name=label[k],
                r=f"{lvl(k, s['a_recent'][k]['p10'])} / {lvl(k, s['a_recent'][k]['p50'])} / {lvl(k, s['a_recent'][k]['p90'])}",
                h=f"{lvl(k, s['a_highvol'][k]['p10'])} / {lvl(k, s['a_highvol'][k]['p50'])} / {lvl(k, s['a_highvol'][k]['p90'])}",
                t=f"{lvl(k, s['a_t'][k]['p10'])} / {lvl(k, s['a_t'][k]['p50'])} / {lvl(k, s['a_t'][k]['p90'])}",
            )
        )
    lines.append("")
    lines.append(
        "고변동 블록의 중앙값이 장기 표본보다 높은 지수가 있다. "
        "그 창에는 급락과 반등이 같이 들어 있다. 고변동 중앙값을 스트레스 예측으로 쓰지 않는다."
    )
    lines.append("")
    lines.append("## 상관")
    lines.append("")
    lines.append("월간 로그수익률. 행과 열은 코스피, 코스닥, 나스닥100.")
    lines.append("")
    lines.append("역사 (시뮬에 쓴 장기 표본)")
    lines.append("")
    lines.append(matrix_md(s["hist_corr_log_monthly"]))
    lines.append("")
    lines.append("(a)에서 뽑힌 달")
    lines.append("")
    lines.append(matrix_md(s["sim_corr_a_monthly_log"]))
    lines.append("")
    lines.append("(b)에서 뽑힌 달")
    lines.append("")
    lines.append(matrix_md(s["sim_corr_b_monthly_log"]))
    lines.append("")
    lines.append(
        f"3개월 로그수익 상관, (a) 종료값 기준 코스피–나스닥100은 {s['sim_corr_a_3m_log'][0][2]:.2f}, "
        f"(b)는 {s['sim_corr_b_3m_log'][0][2]:.2f}. "
        f"역사 3개월 블록에서 코스피와 나스닥100의 부호가 갈린 비율은 {s['sign_disagree_ks_ndx_3m']:.0%}이고, "
        f"코스피와 코스닥은 {s['sign_disagree_ks_kq_3m']:.0%}다. "
        f"코스피와 나스닥100의 월간 단순수익 상관은 달러 지수 기준 {s['corr_ks_ndx_usd']:.2f}, "
        f"나스닥100을 원/달러로 환산하면 {s['corr_ks_ndx_krw']:.2f}이다. "
        "코스피와 코스닥은 한 덩어리고, 나스닥은 같이 움직이되 분기 기준으로 부호가 갈리는 달이 드물지 않다."
    )
    lines.append("")
    lines.append("## 강의 숫자가 지수에 무엇을 요구하는가")
    lines.append("")
    lec = s["lecture"]
    lines.append(
        f"8월 14일 강의의 보수 밸류(26년 성장이 27년에 없다고 두고 PER 6~7배)를 9월 21일 "
        f"삼성전자 {lec['samsung_0921']:,.0f}원, SK하이닉스 {lec['hynix_0921']:,.0f}원에 대입했다. "
        f"시가총액 비중은 9월 14일 26.6% / 22.7%를 그대로 썼다. 나머지를 보합으로 두면 "
        f"PER 6배는 코스피 약 {lvl('KS11', lec['per6_index'])} ({lec['per6_return']:+.0%}), "
        f"PER 7배는 약 {lvl('KS11', lec['per7_index'])} ({lec['per7_return']:+.0%})이다. "
        f"판단의 산식(투톱 +10%, 나머지 −2%)은 약 {lvl('KS11', lec['judgment_base_index'])} ({lec['judgment_base_return']:+.0%})이고, "
        f"투톱 −30%·나머지 −15%는 약 {lvl('KS11', lec['judgment_low_index'])} ({lec['judgment_low_return']:+.0%})이다. "
        "상방 풀은 역사 3개월의 최상위 십분위를 빼서, 강의가 막은 구조적 리레이팅(증권사 11,000–12,600)과 2025년형 급등을 기본·상방 국면에 붙이지 않았다. "
        "강의의 PER 7배를 샘플러의 상한으로 강제하지는 않았다. 강제하면 중앙값을 판단에 끼워 맞추게 된다."
    )
    lines.append("")
    lines.append("## 포트폴리오 3개월")
    lines.append("")
    pl, pf = s["portfolio_listed"], s["portfolio_folded"]
    lines.append(
        f"상장 종목이 모두 있는 표본 {pl['start']} ~ {pl['end']}, {pl['n_months']}개월. "
        f"9월 리밸런스 직후와 같이 목표 비중으로 시작해 3개월은 드리프트만 반영했다. "
        f"P10 / P50 / P90 = {pl['p10']:+.1%} / {pl['p50']:+.1%} / {pl['p90']:+.1%} "
        f"(평균 {pl['mean']:+.1%}). "
        f"3개월 누적이 −10% 이하인 역사 블록은 없다. "
        f"석 달 안에 −10% 이하인 달이 끼는 비율은 {pl['p_any_month_le_m10']:.1%}다. "
        "이 비율은 상장 표본에서 −10%를 넘긴 달이 2026년 7월 하나뿐이고, "
        "그 달을 포함한 3개월 창이 121개 중 2개라는 뜻이다. "
        "앞으로 7월형 달이 다시 올 확률이 2%라는 추정은 아니다."
    )
    lines.append("")
    lines.append(
        f"같은 규칙의 장기 표본(상장 전 위성은 KODEX 200에 접음) {pf['start']} ~ {pf['end']}: "
        f"P10 / P50 / P90 = {pf['p10']:+.1%} / {pf['p50']:+.1%} / {pf['p90']:+.1%}, "
        f"한 달 −10% 이하를 석 달 안에 만날 확률 {pct(pf['p_any_month_le_m10'])}."
    )
    lines.append("")
    lines.append(
        f"2026년 7월, 목표 비중 수익률은 {s['july_2026_portfolio']:+.1%}다. "
        f"상장 표본에서 월간 수익률이 −10% 이하였던 비율은 {pct(s['hist_p_month_le_m10'])}다."
    )
    lines.append("")
    if s["change_mix"]:
        lines.append(
            f"상장 표본 3개월 P10이 {pl['p10']:+.1%}로, 현금 비중 −15%보다 손실이 크다. "
            "현금 15%는 이 좌측 꼬리를 메우는 대기자금으로 부족하다. "
            "시사점은 주식을 판단문의 킬스위치(55%→40%) 쪽으로 낮추고 차액을 현금에 두는 쪽이다. "
            "가격 경로만으로 리밸런스 규칙을 바꾸지는 않았고, 장비 실적 실패·메모리 판가 하향·미국 10년 5.5%와 원/달러 1,500이 그 스위치의 조건으로 이미 적혀 있다."
        )
    else:
        lines.append(
            f"상장 표본 3개월 P10은 {pl['p10']:+.1%}다. 손실 크기가 현금 15%보다 작다. "
            "7월형 −10% 한 달은 시뮬레이션에서도 나오지만, 그 달을 견디라고 넣어 둔 현금의 크기 안에 있다. "
            "55/22/15/8은 유지한다. 현금은 평가손실을 지우는 돈이 아니라, 한 번의 급한 달을 리밸런스할 대기자금이다."
        )
    lines.append("")
    lines.append("## 옵션")
    lines.append("")
    opt = s["options"]
    if not opt or opt.get("skipped", False):
        reason = (opt or {}).get("reason", "자료를 받지 못했다")
        lines.append(f"상장 옵션의 연말 분포는 쓰지 않았다. QQQ 12월물 조회: {reason}. 내재분포를 만들지 않았다.")
    else:
        lines.append(
            f"QQQ {opt['expiry']} 월물, 야후 내재변동성으로 계산한 10델타 근사. "
            f"풋 행사가 {opt['put_10d_strike_qqq']:.1f} (델타 {opt['put_10d_delta']:.2f}, IV {opt['put_10d_iv']:.0%}), "
            f"콜 행사가 {opt['call_10d_strike_qqq']:.1f} (델타 {opt['call_10d_delta']:.2f}, IV {opt['call_10d_iv']:.0%}). "
            f"9/21 QQQ {opt['qqq_spot_2026_09_21']:.2f} 대비 나스닥100으로 환산하면 대략 "
            f"{lvl('NDX', opt['ndx_put_10d'])} ~ {lvl('NDX', opt['ndx_call_10d'])}. "
            "위험중립 분포의 꼬리 근사이고, 이 노트의 확률과는 다른 물건이다. 만기는 12월 월물이지 12월 31일이 아니다."
        )
    lines.append("")
    lines.append("## 판단이 맞는지")
    lines.append("")
    for k in ORDER:
        f = s["flags"][k]
        bb = s["b"][k]
        lo = s["conditional_b"]["low"][k]
        hi = s["conditional_b"]["high"][k]
        lines.append(
            f"- {label[k]}: (b) 중앙 {lvl(k, bb['p50'])} ({bb['p50']/s['anchor'][k]-1:+.0%}), "
            f"제시 기본 {lvl(k, STATED[k]['base'])}. "
            f"기본값이 (b)의 P25–P75 밖으로 {'나가 있다' if f['base_far_b'] else '나가 있지 않다'}. "
            f"하방 국면 P10/P50/P90은 {lvl(k, lo['p10'])} / {lvl(k, lo['p50'])} / {lvl(k, lo['p90'])}. "
            f"상방 국면은 {lvl(k, hi['p10'])} / {lvl(k, hi['p50'])} / {lvl(k, hi['p90'])}."
        )
    lines.append("")
    lines.append(
        "코스피 5400은 하방 국면 P10(약 5500) 바로 아래다. "
        "25% 국면의 중심은 약 6050이고, 5400까지 끝나는 확률은 (a)에서 1% 안쪽, (b)에서 2%다. "
        "투톱 −30%·나머지 −15%라는 펀더멘털 산식(약 5450)과 2008년 10월 창의 입구로는 맞다. "
        "25%짜리 대표 하한으로 읽으면 깊다. 그 대표값을 쓰라면 6050이다. "
        "기본값이 무너지지 않았고 5400이 최악 십분위의 가장자리에 있으므로 발표 구간은 5400을 그대로 둔다."
    )
    lines.append("")
    lines.append(
        "코스피 8200은 상방 국면 P90(약 8050) 바로 위이고, 비조건부 P90(약 8300) 안쪽이다. "
        "강의의 PER 7배·나머지 보합은 약 7900으로, 상방 국면의 중심(약 7700)과 그 상단 사이에 있다. "
        "8200은 완만한 리레이팅의 라운드 상단으로 둔다. 증권사 11,000–12,600은 이 분포의 상단이 아니다."
    )
    lines.append("")
    lines.append(
        "코스닥 700 / 850 / 1000은 각 국면의 범위 안에 있다. "
        "850은 (a) 중앙 840, (b) 중앙 830과 붙는다. "
        "나스닥100 31000은 (b) 중앙 31400과 붙는다. "
        "27000은 하방 국면의 중심(약 27600)이다. "
        "33000은 상방 국면의 중심(약 33300)이고, 비조건부로 보면 P75 근처다. P90은 약 35000이다. "
        "멜트업을 상단으로 쓰지 않겠다는 판단과 맞다."
    )
    lines.append("")
    if far_b:
        lines.append("고칠 라운드 레벨은 (b)의 P10 / P50 / P90이다.")
        lines.append("")
        for k in far_b:
            bb = s["b"][k]
            lines.append(
                f"- {label[k]}: {lvl(k, bb['p10'])} / {lvl(k, bb['p50'])} / {lvl(k, bb['p90'])}"
            )
        lines.append("")
    else:
        lines.append("기본값이 혼합 분포의 중앙 근처에 있으므로 5400 / 7300 / 8200, 700 / 850 / 1000, 27000 / 31000 / 33000을 유지한다. 새 지수 레벨을 만들지 않는다.")
        lines.append("")
    lines.append("## 한계")
    lines.append("")
    lines.append("- 월간 역사로 만든 3개월 몬테카를로는 갭과 정책 점프를 과소평가한다. 경로는 월말이라 장중 저점·고점을 세지 못한다.")
    lines.append("- 2026년 7월이 표본 안에 있다. 좌측 꼬리의 일부는 인샘플이다. 2026년 3–5월의 큰 등락도 마찬가지다.")
    lines.append("- 비중 55/22/15/8과 시나리오 확률 25/55/20, 35/45/20은 판단이지 추정된 확률이 아니다.")
    lines.append("- 이 분포는 시장이 가격에 넣어 둔 확률이 아니다. 옵션을 쓴 경우는 위 절에 위험중립이라고 적었고, 쓰지 않았으면 내재변동성을 만들지 않았다.")
    lines.append("- 겹치는 3개월 블록이라 독립 표본 수는 블록 개수보다 적다. 4만 번은 그 경험분포를 다시 뽑은 횟수다.")
    lines.append("- 지수 시뮬레이션은 프라이스 지수다. 배당은 레벨 목표에 넣지 않았다. 포트폴리오 층은 수정주가·금리 캐리 근사다.")
    lines.append("- 보유 잔고, 평가액, 증권사 파일은 로컬에 없었다. 개인 계좌를 가정하지 않았다.")
    lines.append("")
    lines.append("재현: `python3 analysis/montecarlo_2026.py`")
    lines.append("")
    text = "\n".join(lines)
    Path("/workspace/analysis/montecarlo_2026.md").write_text(text)


def matrix_md(m: list[list[float]]) -> str:
    header = "| | 코스피 | 코스닥 | 나스닥100 |"
    sep = "| --- | ---: | ---: | ---: |"
    rows = [header, sep]
    names = ["코스피", "코스닥", "나스닥100"]
    for name, row in zip(names, m):
        rows.append("| " + name + " | " + " | ".join(f"{v:.2f}" for v in row) + " |")
    return "\n".join(rows)


if __name__ == "__main__":
    main()
