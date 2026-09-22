#!/usr/bin/env python3
"""H2 2026 top-down portfolio backtest.

Horizon of the allocation: 2026-09-22 through 2026-12-31, with a checkpoint
into 1Q 2027 (order-book visibility). This script does not forecast that window.
It reports how the same weights behaved in history.

Returns are in KRW. USD assets are converted with KRW=X (KRW per USD).
Rebalance is quarterly (Mar/Jun/Sep/Dec month-ends), matching the stated rule.
Risk-free hurdle is the US 3-month T-bill yield (^IRX), time-varying.
Korean cash uses a FRED Korea short rate when available, else the US bill.

Look-ahead: weights were chosen on 2026-09-22 and applied to the past.
"""

from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

OUT = Path("/workspace/analysis/output")
ART = Path("/opt/cursor/artifacts")
OUT.mkdir(parents=True, exist_ok=True)
ART.mkdir(parents=True, exist_ok=True)

# Proposed weights. Must sum to 1.
WEIGHTS = {
    "kr_equity": 0.14,
    "samsung": 0.03,
    "hynix": 0.02,
    "sk": 0.02,
    "hanmi": 0.015,
    "tes": 0.01,
    "wonik": 0.005,
    "mobis": 0.01,
    "spy": 0.18,
    "efa": 0.08,
    "xli": 0.04,
    "ief": 0.08,
    "tip": 0.08,
    "ktb": 0.06,
    "usd_cash": 0.06,
    "krw_cash": 0.09,
    "gld": 0.05,
    "dbc": 0.03,
}

# Global 60/40: 60% equity (S&P 65 / EAFE 25 / Korea 10) + 40% US intermediate Treasury.
BM_GLOBAL = {
    "spy": 0.60 * 0.65,
    "efa": 0.60 * 0.25,
    "kr_equity": 0.60 * 0.10,
    "ief": 0.40,
}

# Home-biased 60/40 consistent with a Korea equity research base.
BM_KR = {
    "kr_equity": 0.60,
    "ktb": 0.40,
}

TICKERS = {
    "kr_equity": "069500.KS",  # KODEX 200
    "samsung": "005930.KS",
    "hynix": "000660.KS",
    "sk": "034730.KS",
    "hanmi": "042700.KS",
    "tes": "095610.KQ",  # KOSDAQ. .KS is empty on Yahoo.
    "wonik": "240810.KS",
    "mobis": "012330.KS",
    "spy": "SPY",
    "efa": "EFA",
    "xli": "XLI",
    "ief": "IEF",
    "tip": "TIP",
    "gld": "GLD",
    "dbc": "DBC",
    "bil": "BIL",
    "fx": "KRW=X",
    "irx": "^IRX",
    "gc": "GC=F",
    "cl": "CL=F",
    "ks11": "^KS11",
}

USD_PRICE_KEYS = ["spy", "efa", "xli", "ief", "tip", "gld", "dbc", "bil", "gc", "cl"]
KRW_PRICE_KEYS = ["kr_equity", "samsung", "hynix", "sk", "hanmi", "tes", "wonik", "mobis"]


def _month_end(series: pd.Series) -> pd.Series:
    s = series.dropna().copy()
    s.index = pd.to_datetime(s.index)
    s = s.sort_index()
    # Drop duplicate stamps, keep last print of the day.
    s = s[~s.index.duplicated(keep="last")]
    return s.resample("ME").last().dropna()


def load_yahoo(ticker: str, start: str = "1999-01-01") -> pd.Series:
    df = yf.download(
        ticker,
        start=start,
        end="2026-09-23",
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if df is None or len(df) == 0:
        return pd.Series(dtype=float, name=ticker)
    if isinstance(df.columns, pd.MultiIndex):
        close = df["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
    else:
        close = df["Close"]
    close = pd.Series(close.to_numpy().ravel(), index=pd.to_datetime(df.index), name=ticker)
    return _month_end(close)


def load_fred(series_id: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            raw = resp.read()
    except Exception as exc:  # noqa: BLE001
        print(f"FRED fail {series_id}: {exc}")
        return pd.Series(dtype=float, name=series_id)
    df = pd.read_csv(pd.io.common.BytesIO(raw))
    if df.shape[1] < 2:
        return pd.Series(dtype=float, name=series_id)
    df.columns = ["date", "value"]
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    s = df.dropna().set_index("date")["value"].sort_index()
    s.name = series_id
    # FRED monthly rates are often stamped at month start. Shift to month-end.
    return s.resample("ME").last().dropna()


def yield_total_return(yield_pct: pd.Series, duration: float) -> pd.Series:
    """Constant-maturity approximation: carry minus duration times yield change.

    yield_pct is in percent (5.0 = 5%). Convexity is ignored (second order, small
    next to the duration term at monthly frequency).
    """
    y = yield_pct.astype(float).dropna().sort_index() / 100.0
    dy = y.diff()
    carry = y.shift(1) / 12.0
    tr = carry - duration * dy
    return tr.dropna()


def wealth_from_returns(returns: pd.Series, start_value: float = 1.0) -> pd.Series:
    r = returns.fillna(0.0)
    w = (1.0 + r).cumprod() * start_value
    return w


def quarterly_rebalanced(returns: pd.DataFrame, weights: dict[str, float]) -> pd.Series:
    """Hold drifted weights inside a quarter. Reset at Mar/Jun/Sep/Dec month-ends,
    with the new weights earning the following month's return.
    """
    cols = [c for c in weights if c in returns.columns]
    w = np.array([weights[c] for c in cols], dtype=float)
    w = w / w.sum()
    rets = returns[cols].dropna(how="any")
    if rets.empty:
        return pd.Series(dtype=float)
    values = w.copy()
    out = []
    idx = []
    for i, (dt, row) in enumerate(rets.iterrows()):
        r = row.to_numpy(dtype=float)
        asset_end = values * (1.0 + r)
        port_r = asset_end.sum() / values.sum() - 1.0
        out.append(port_r)
        idx.append(dt)
        # Rebalance at calendar quarter ends so the NEXT month starts on target.
        if dt.month in (3, 6, 9, 12):
            values = w * asset_end.sum()
        else:
            values = asset_end
    return pd.Series(out, index=pd.DatetimeIndex(idx), name="port")


def max_drawdown(returns: pd.Series) -> float:
    w = wealth_from_returns(returns)
    peak = w.cummax()
    dd = w / peak - 1.0
    return float(dd.min()) if len(dd) else np.nan


def calendar_year_returns(returns: pd.Series) -> pd.Series:
    if returns.empty:
        return pd.Series(dtype=float)
    return (1.0 + returns).groupby(returns.index.year).prod() - 1.0


def summarize(returns: pd.Series, rf_monthly: pd.Series, label: str) -> dict:
    r = returns.dropna()
    if r.empty:
        return {"label": label, "n_months": 0}
    rf = rf_monthly.reindex(r.index).ffill().fillna(0.0)
    excess = r - rf
    years = len(r) / 12.0
    growth = float((1.0 + r).prod())
    cagr = growth ** (1.0 / years) - 1.0 if years > 0 else np.nan
    vol = float(r.std(ddof=1) * np.sqrt(12.0))
    ex_mean = float(excess.mean() * 12.0)
    ex_vol = float(excess.std(ddof=1) * np.sqrt(12.0))
    sharpe = ex_mean / ex_vol if ex_vol > 0 else np.nan
    yrs = calendar_year_returns(r)
    worst_year = float(yrs.min()) if len(yrs) else np.nan
    worst_year_label = int(yrs.idxmin()) if len(yrs) else None
    return {
        "label": label,
        "start": str(r.index.min().date()),
        "end": str(r.index.max().date()),
        "n_months": int(len(r)),
        "cagr": cagr,
        "vol": vol,
        "max_drawdown": max_drawdown(r),
        "sharpe": sharpe,
        "worst_year": worst_year,
        "worst_year_label": worst_year_label,
        "total_return": growth - 1.0,
        "rf_mean_annualized": float(rf.mean() * 12.0),
    }


def slice_window(returns: pd.Series, start: str, end: str) -> pd.Series:
    return returns.loc[(returns.index >= start) & (returns.index <= end)]


def main() -> None:
    assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-9, sum(WEIGHTS.values())

    prices: dict[str, pd.Series] = {}
    for key, ticker in TICKERS.items():
        print(f"download {key} {ticker}")
        prices[key] = load_yahoo(ticker)
        print(f"  {key}: {len(prices[key])} months", end="")
        if len(prices[key]):
            print(f" {prices[key].index.min().date()} -> {prices[key].index.max().date()}")
        else:
            print(" EMPTY")

    # Korea long-term government bond yield (percent). Duration haircut to ~5y
    # so the 6% sleeve behaves like intermediate KTBs, not a 10y+ position.
    kr_yield = load_fred("IRLTLT01KRM156N")
    print(f"FRED KR long yield: {len(kr_yield)}")
    # Korea 3-month interbank rate, percent. Fallback: policy-like short rate.
    kr_short = load_fred("IR3TIB01KRM156N")
    if kr_short.empty:
        kr_short = load_fred("IRSTCI01KRM156N")
    print(f"FRED KR short: {len(kr_short)}")

    fx = prices["fx"]
    fx_ret = fx.pct_change()

    krw_rets = pd.DataFrame(index=fx.index)
    for key in KRW_PRICE_KEYS:
        krw_rets[key] = prices[key].pct_change()
    for key in USD_PRICE_KEYS:
        usd_ret = prices[key].pct_change()
        # Align on the union; FX conversion only where both exist.
        both = pd.concat([usd_ret.rename("u"), fx_ret.rename("f")], axis=1).dropna()
        krw_rets.loc[both.index, key] = (1.0 + both["u"]) * (1.0 + both["f"]) - 1.0

    # Cash: yield accrual, no price FX on the KRW leg. USD cash is T-bill yield
    # plus the FX move (the bill is a USD asset).
    irx = prices["irx"].reindex(krw_rets.index).ffill()
    # ^IRX is a percent yield. Cap insane prints.
    irx = irx.where((irx > -1) & (irx < 25))
    usd_bill_m = (1.0 + irx / 100.0) ** (1.0 / 12.0) - 1.0
    krw_rets["usd_cash"] = (1.0 + usd_bill_m) * (1.0 + fx_ret) - 1.0

    if not kr_short.empty:
        ks = kr_short.reindex(krw_rets.index).ffill() / 100.0
        krw_rets["krw_cash"] = (1.0 + ks) ** (1.0 / 12.0) - 1.0
    else:
        krw_rets["krw_cash"] = usd_bill_m

    if not kr_yield.empty:
        # FRED often stops a month early. Hold the last yield flat so the
        # final month earns carry and zero price change, instead of dropping
        # the whole sample at that month.
        yld = kr_yield.copy()
        if len(fx):
            yld = yld.reindex(yld.index.union(fx.index)).ffill()
        ktb_local = yield_total_return(yld, duration=5.0)
        krw_rets["ktb"] = ktb_local.reindex(krw_rets.index)
    else:
        # Duration proxy only. Same economic bet as IEF, wrong currency mix.
        krw_rets["ktb"] = krw_rets["ief"]

    # KODEX 200 on Yahoo begins in 2007. Before that, use KOSPI price index
    # plus a flat 1.5%/yr dividend assumption so the pre-ETF segment is not
    # a pure price index. 1.5% is an assumption, not a reconstructed dividend.
    if "ks11" in prices and len(prices["ks11"]):
        ks_ret = prices["ks11"].pct_change() + 0.015 / 12.0
        kodex = krw_rets["kr_equity"]
        krw_rets["kr_equity"] = kodex.where(kodex.notna(), ks_ret)

    # Commodity sleeve: DBC total-return-ish ETF when alive, else 70% crude
    # price + 30% gold price (both futures, not collateralized total return).
    dbc = krw_rets["dbc"]
    crude = krw_rets["cl"]
    gold_fut = krw_rets["gc"]
    fallback_cmdty = 0.70 * crude + 0.30 * gold_fut
    krw_rets["dbc"] = dbc.where(dbc.notna(), fallback_cmdty)

    # Gold sleeve: GLD when alive, else gold futures (price return).
    krw_rets["gld"] = krw_rets["gld"].where(krw_rets["gld"].notna(), gold_fut)

    # USD cash before BIL is irrelevant; we use the bill yield directly.
    # TIPS before TIP inception: fall back to IEF (nominal) and flag it.
    krw_rets["tip"] = krw_rets["tip"].where(krw_rets["tip"].notna(), krw_rets["ief"])

    krw_rets = krw_rets.sort_index()
    krw_rets.to_csv(OUT / "monthly_returns_krw.csv")

    # Coverage report for the satellite names.
    coverage = {}
    for key in WEIGHTS:
        s = krw_rets[key].dropna()
        coverage[key] = {
            "start": str(s.index.min().date()) if len(s) else None,
            "end": str(s.index.max().date()) if len(s) else None,
            "n": int(len(s)),
        }
    print(json.dumps(coverage, indent=2))

    # Full-sample book starts when every satellite used at its real weight exists.
    # Names that list late are NOT back-filled with the index in this track;
    # a second track folds pre-listing satellites into KODEX 200.
    core_cols = list(WEIGHTS.keys())
    full = krw_rets[core_cols].dropna(how="any")
    print(f"complete-panel months: {len(full)} {full.index.min().date() if len(full) else None}")

    port_full = quarterly_rebalanced(full, WEIGHTS)
    bm_g = quarterly_rebalanced(full, BM_GLOBAL)
    bm_k = quarterly_rebalanced(full, BM_KR)

    # Long track: before each single-name starts, fold its weight into kr_equity.
    # Build a month-by-month weight path only for diagnostics; for returns, fill
    # missing single-name months with kr_equity return and document the fold.
    folded = krw_rets.copy()
    single = ["samsung", "hynix", "sk", "hanmi", "tes", "wonik", "mobis"]
    for key in single:
        folded[key] = folded[key].where(folded[key].notna(), folded["kr_equity"])
    long_cols = list(WEIGHTS.keys())
    long_panel = folded[long_cols].dropna(how="any")
    # Start at 2004-07 so the regime window is inside a defined sample,
    # but keep the panel's natural start if later.
    port_long = quarterly_rebalanced(long_panel, WEIGHTS)
    bm_g_long = quarterly_rebalanced(long_panel, BM_GLOBAL)
    bm_k_long = quarterly_rebalanced(long_panel, BM_KR)

    rf = usd_bill_m.reindex(port_long.index).ffill()

    windows = {
        "full_listed": (port_full, bm_g, bm_k, "모든 개별종목 상장 이후"),
        "long_folded": (port_long, bm_g_long, bm_k_long, "장기(미상장 위성은 KODEX200으로 접음)"),
    }

    results = []
    curves = {}

    def add_block(tag: str, port: pd.Series, g: pd.Series, k: pd.Series, start: str | None, end: str | None):
        if start:
            port, g, k = slice_window(port, start, end), slice_window(g, start, end), slice_window(k, start, end)
        block_rf = rf.reindex(port.index).ffill()
        for series, name in (
            (port, "proposed"),
            (g, "bm_global_60_40"),
            (k, "bm_kr_60_40"),
        ):
            stats = summarize(series, block_rf, f"{tag}:{name}")
            results.append(stats)
        # Store curves on a common start inside the slice.
        if len(port):
            curves[tag] = pd.DataFrame(
                {
                    "proposed": wealth_from_returns(port),
                    "bm_global_60_40": wealth_from_returns(g.reindex(port.index).fillna(0)),
                    "bm_kr_60_40": wealth_from_returns(k.reindex(port.index).fillna(0)),
                }
            )

    add_block("listed_full", port_full, bm_g, bm_k, None, None)
    add_block("long_full", port_long, bm_g_long, bm_k_long, None, None)
    # Regime analogue: Fed mid-cycle hiking, growth held, oil rising.
    # June 2004 (hike cycle underway) through June 2006 (last hike to 5.25%).
    add_block("regime_2004_2006", port_long, bm_g_long, bm_k_long, "2004-06-30", "2006-06-30")
    # This-year path. Weights are chosen at the END of this window: look-ahead.
    add_block("path_2026_ytd_lookahead", port_full, bm_g, bm_k, "2025-12-31", "2026-09-30")

    results = [r for r in results if not str(r["label"]).startswith("stress_2022")]
    curves.pop("stress_2022", None)
    use_listed = len(port_full) > 0 and port_full.index.min() <= pd.Timestamp("2022-01-31")
    if use_listed:
        add_block("stress_2022", port_full, bm_g, bm_k, "2022-01-31", "2022-12-31")
    else:
        add_block("stress_2022", port_long, bm_g_long, bm_k_long, "2022-01-31", "2022-12-31")

    stats_df = pd.DataFrame(results)
    stats_df.to_csv(OUT / "backtest_stats.csv", index=False)
    print(stats_df.to_string(index=False))

    # Latest prices for the report (last available close on or before 2026-09-22).
    last_prices = {}
    for key, series in prices.items():
        if len(series):
            last_prices[key] = {
                "date": str(series.index.max().date()),
                "close": float(series.iloc[-1]),
            }
    (OUT / "last_prices.json").write_text(json.dumps(last_prices, indent=2))
    (OUT / "coverage.json").write_text(json.dumps(coverage, indent=2))
    (OUT / "stats.json").write_text(json.dumps(results, indent=2, default=str))

    # Year-by-year for the long track.
    yearly = pd.DataFrame(
        {
            "proposed": calendar_year_returns(port_long),
            "bm_global_60_40": calendar_year_returns(bm_g_long),
            "bm_kr_60_40": calendar_year_returns(bm_k_long),
        }
    )
    yearly.to_csv(OUT / "calendar_years_long.csv")

    yearly_listed = pd.DataFrame(
        {
            "proposed": calendar_year_returns(port_full),
            "bm_global_60_40": calendar_year_returns(bm_g),
            "bm_kr_60_40": calendar_year_returns(bm_k),
        }
    )
    yearly_listed.to_csv(OUT / "calendar_years_listed.csv")

    plot_curves(curves)
    plot_weights()
    print("wrote outputs to", OUT, "and", ART)


def plot_curves(curves: dict[str, pd.DataFrame]) -> None:
    # Primary chart: long sample + regime window.
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 4.6))
    specs = [
        ("long_full", "Long sample, quarterly rebalance (KRW)"),
        ("regime_2004_2006", "Regime window Jun 2004–Jun 2006 (KRW)"),
    ]
    for ax, (key, title) in zip(axes, specs):
        df = curves.get(key)
        if df is None or df.empty:
            ax.set_title(title + " (no data)")
            continue
        ax.plot(df.index, df["proposed"], label="Proposed", color="#1f4e79", lw=2.0)
        ax.plot(df.index, df["bm_global_60_40"], label="Global 60/40", color="#c45911", lw=1.5)
        ax.plot(df.index, df["bm_kr_60_40"], label="Korea 60/40", color="#548235", lw=1.5)
        ax.set_title(title, fontsize=10)
        ax.set_ylabel("Growth of 1")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "equity_curves.png", dpi=140)
    fig.savefig(ART / "equity_curves.png", dpi=140)
    plt.close()

    # Drawdowns on the long sample.
    df = curves.get("long_full")
    if df is not None and not df.empty:
        fig, ax = plt.subplots(figsize=(10.5, 4.2))
        for col, color, label in (
            ("proposed", "#1f4e79", "Proposed"),
            ("bm_global_60_40", "#c45911", "Global 60/40"),
            ("bm_kr_60_40", "#548235", "Korea 60/40"),
        ):
            w = df[col]
            dd = w / w.cummax() - 1.0
            ax.plot(dd.index, dd.values, label=label, color=color, lw=1.4)
        ax.set_title("Drawdown, long sample (KRW, quarterly rebalance)", fontsize=11)
        ax.set_ylabel("Drawdown")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(OUT / "drawdowns.png", dpi=140)
        fig.savefig(ART / "drawdowns.png", dpi=140)
        plt.close()

    df22 = curves.get("stress_2022")
    if df22 is not None and not df22.empty:
        fig, ax = plt.subplots(figsize=(8.2, 4.0))
        ax.plot(df22.index, df22["proposed"], label="Proposed", color="#1f4e79", lw=2)
        ax.plot(df22.index, df22["bm_global_60_40"], label="Global 60/40", color="#c45911", lw=1.5)
        ax.plot(df22.index, df22["bm_kr_60_40"], label="Korea 60/40", color="#548235", lw=1.5)
        ax.set_title("Stress window 2022 (inflation + hikes, growth did not hold)", fontsize=10)
        ax.set_ylabel("Growth of 1")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(OUT / "stress_2022.png", dpi=140)
        fig.savefig(ART / "stress_2022.png", dpi=140)
        plt.close()


def plot_weights() -> None:
    labels = {
        "kr_equity": "KODEX 200",
        "samsung": "Samsung Elec",
        "hynix": "SK hynix",
        "sk": "SK Inc",
        "hanmi": "Hanmi Semi",
        "tes": "TES",
        "wonik": "Wonik IPS",
        "mobis": "Hyundai Mobis",
        "spy": "S&P 500",
        "efa": "EAFE",
        "xli": "US Industrials",
        "ief": "US 7-10Y UST",
        "tip": "US TIPS",
        "ktb": "Korea intermediate gov",
        "usd_cash": "USD T-bills",
        "krw_cash": "KRW cash",
        "gld": "Gold",
        "dbc": "Commodities",
    }
    groups = {
        "Equity": ["kr_equity", "samsung", "hynix", "sk", "hanmi", "tes", "wonik", "mobis", "spy", "efa", "xli"],
        "Bonds": ["ief", "tip", "ktb"],
        "Cash": ["usd_cash", "krw_cash"],
        "Alts": ["gld", "dbc"],
    }
    colors = {"Equity": "#1f4e79", "Bonds": "#5b9bd5", "Cash": "#7f8c8d", "Alts": "#c45911"}
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    y = 0
    yticks = []
    ylabels = []
    for g, keys in groups.items():
        for k in keys:
            ax.barh(y, WEIGHTS[k] * 100, color=colors[g], height=0.7)
            yticks.append(y)
            ylabels.append(labels[k])
            y += 1
        y += 0.4
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=8)
    ax.set_xlabel("Weight (%)")
    ax.set_title("H2 2026 allocation (sums to 100%)")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "weights.png", dpi=140)
    fig.savefig(ART / "weights.png", dpi=140)
    plt.close()


if __name__ == "__main__":
    main()
