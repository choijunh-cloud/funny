"""Pre-specified price factors. Thresholds are fixed before the backtest runs."""

from __future__ import annotations

import numpy as np
import pandas as pd

# Lecture sleeve that can be computed from prices alone, renormalized
# from 20 / 20 / 15. The other 45 points are current fundamentals.
PRICE_WEIGHTS = {"mom": 0.20 / 0.55, "room": 0.20 / 0.55, "vol": 0.15 / 0.55}
FULL_WEIGHTS = {"reverse": 0.25, "visible": 0.20, "room": 0.20, "mom": 0.20, "vol": 0.15}


def clip(x: float, lo: float, hi: float) -> float:
    return float(min(hi, max(lo, x)))


def map_mom(mom21: float | None) -> float | None:
    if mom21 is None or not np.isfinite(mom21):
        return None
    return clip((mom21 + 0.08) / 0.28, 0.0, 1.0)


def map_vol(vol_ratio: float | None) -> float | None:
    if vol_ratio is None or not np.isfinite(vol_ratio) or vol_ratio <= 0:
        return None
    return clip((vol_ratio - 0.70) / 0.70, 0.0, 1.0)


def map_room(dd126: float | None, mom21: float | None, mom63: float | None) -> float | None:
    """Drawdown is room only when the tape has stopped falling."""
    if dd126 is None or mom21 is None or mom63 is None:
        return None
    if not (np.isfinite(dd126) and np.isfinite(mom21) and np.isfinite(mom63)):
        return None
    if mom63 < -0.08:
        return 0.0
    room = clip(-dd126, 0.0, 0.40)
    gate = clip((mom21 + 0.02) / 0.08, 0.0, 1.0)
    return (room / 0.40) * gate


def map_visible(growth: float | None, analysts: int | None) -> float | None:
    """Orders/guidance visible: positive consensus growth with coverage."""
    if growth is None or not np.isfinite(growth):
        return None
    if growth < 0:
        score = 0.20
    else:
        score = clip(0.45 + growth / 0.20 * 0.45, 0.45, 0.90)
    if analysts is not None and analysts < 5:
        score = min(score, 0.50)
    return score


def map_reverse(gap: float | None, g_cons: float | None, analysts: int | None) -> float | None:
    """Street growth minus the growth embedded in the price. Neutral if unknown."""
    if gap is None or not np.isfinite(gap):
        return None
    adj = gap
    if g_cons is not None and np.isfinite(g_cons) and g_cons > 0.50:
        adj *= 0.50
    if analysts is not None and analysts < 5:
        adj *= 0.50
    return clip((clip(adj, -0.15, 0.15) + 0.15) / 0.30, 0.0, 1.0)


def is_extended(dd126: float | None, mom63: float | None) -> bool:
    if dd126 is None or mom63 is None:
        return False
    return bool(dd126 > -0.05 and mom63 > 0.25)


def weighted_score(parts: dict[str, float | None], weights: dict[str, float]) -> float | None:
    num = 0.0
    den = 0.0
    for k, w in weights.items():
        v = parts.get(k)
        if v is None or not np.isfinite(v):
            continue
        num += w * float(v)
        den += w
    if den <= 0:
        return None
    return num / den


def features_at(close: pd.Series, volume: pd.Series, i: int) -> dict:
    out = {
        "mom21": None,
        "mom63": None,
        "mom126": None,
        "dd126": None,
        "vol_ratio": None,
        "dist_sma200": None,
    }
    if i < 0 or i >= len(close):
        return out
    px = close.to_numpy(dtype=float)
    p = px[i]
    if not np.isfinite(p) or p <= 0:
        return out

    def ret(n: int) -> float | None:
        if i < n:
            return None
        p0 = px[i - n]
        if not np.isfinite(p0) or p0 <= 0:
            return None
        return float(p / p0 - 1.0)

    out["mom21"] = ret(21)
    out["mom63"] = ret(63)
    out["mom126"] = ret(126)
    if i >= 20:
        window = px[i - 125 : i + 1] if i >= 125 else px[: i + 1]
        window = window[np.isfinite(window)]
        if len(window):
            hi = float(np.max(window))
            if hi > 0:
                out["dd126"] = float(p / hi - 1.0)
    if i >= 199:
        sma = float(np.nanmean(px[i - 199 : i + 1]))
        if sma > 0:
            out["dist_sma200"] = float(p / sma - 1.0)
    if volume is not None and i >= 62:
        vol = volume.to_numpy(dtype=float)
        block = vol[i - 62 : i + 1]
        if np.isfinite(block).sum() >= 50:
            long = float(np.nanmean(block))
            short = float(np.nanmean(block[-21:]))
            if long > 0:
                out["vol_ratio"] = short / long
    return out


def forward_return(close: pd.Series, i: int, horizon: int) -> float | None:
    px = close.to_numpy(dtype=float)
    if i + horizon >= len(px):
        return None
    a, b = px[i], px[i + horizon]
    if not np.isfinite(a) or not np.isfinite(b) or a <= 0:
        return None
    return float(b / a - 1.0)
