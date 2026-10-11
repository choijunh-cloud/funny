"""Lead time of beneficiary prices versus capex growth and acceleration.

Two different questions are measured separately:

1. Peak lag. When did the price high occur relative to a capex signal quarter?
   Negative months mean the price topped before the signal quarter ended.
2. Gain share. What fraction of the move from a cycle start to that price high
   was already in the price at earlier checkpoints?

Neither is a forecast. Two completed capex-growth cycles (2018, 2021) are the
whole historical sample on this four-company cash series.
"""

from __future__ import annotations

from datetime import date, timedelta

from capex_accel.metrics import CapexFrame, local_peaks
from capex_accel.prices import price_asof


US_COMPLEX = ("NVDA", "MU", "AVGO", "TSM", "SOX")


def months_between(later: date, earlier: date) -> float:
    return (later - earlier).days / 30.4375


def median_months(values: list[float]) -> float:
    ordered = sorted(values)
    n = len(ordered)
    if n == 0:
        raise ValueError("median of an empty lag sample")
    mid = n // 2
    if n % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def confirmed_lag_medians(leads: list[dict]) -> dict:
    """Median lag of 25% drawdown tops, pooled and for the 2021 US complex.

    2026 rows are a candidate, not a completed growth-rate cycle, so they stay out.
    """
    confirmed = [
        row
        for row in leads
        if row.get("status") == "drawdown_top"
        and not str(row.get("cycle", "")).startswith("2026")
        and row.get("lag_months") is not None
    ]
    us_2021 = [
        row
        for row in confirmed
        if str(row.get("cycle", "")).startswith("2021") and row["name"] in US_COMPLEX
    ]
    return {
        "n": len(confirmed),
        "median": median_months([row["lag_months"] for row in confirmed]),
        "us_2021_n": len(us_2021),
        "us_2021_median": median_months([row["lag_months"] for row in us_2021]),
    }


def growth_cycle_peaks(frame: CapexFrame) -> list[dict]:
    """TTM YoY growth peaks followed by a decline of at least 15 percentage points."""
    return local_peaks(
        frame.quarters,
        frame.ttm_yoy,
        min_value=0.20,
        decline=0.15,
        lookforward=6,
        min_gap=6,
    )


def confirmed_acceleration_peaks(frame: CapexFrame) -> list[dict]:
    """Dollar-acceleration highs that were not exceeded over the next four quarters.

    The threshold is $5B per quarter^2 so small wiggles in a flat period drop out.
    A later new high does not erase the local peak; the caller can see that the
    value was subsequently surpassed by comparing with the sample maximum.
    """
    peaks = local_peaks(
        frame.quarters,
        frame.acceleration,
        min_value=5.0,
        decline=0.0,
        lookforward=4,
        min_gap=4,
    )
    confirmed = []
    for peak in peaks:
        i = peak["index"]
        later = [v for v in frame.acceleration[i + 1 : i + 5] if v is not None]
        if later and max(later) < peak["value"]:
            confirmed.append(peak)
    return confirmed


def price_high_around(
    rows: list[tuple[date, float]],
    signal: date,
    *,
    back_days: int = 275,
    forward_days: int = 370,
    drawdown: float = 0.25,
) -> dict:
    """High before the first 25% break in a window around the signal.

    The window runs from about nine months before the signal quarter-end to
    about twelve months after. Once price has fallen `drawdown` from a running
    high, later new highs are a new leg and are not used as this cycle's top.
    """
    start = signal - timedelta(days=back_days)
    end = min(signal + timedelta(days=forward_days), rows[-1][0])
    subset = [(d, px) for d, px in rows if start <= d <= end]
    if not subset:
        return {"status": "no_price", "peak_date": None, "lag_months": None, "drawdown": None}

    peak_d, peak_px = subset[0]
    armed: tuple[date, float] | None = None
    for d, px in subset[1:]:
        if armed is None:
            if px >= peak_px:
                peak_d, peak_px = d, px
            elif px <= peak_px * (1 - drawdown):
                armed = (peak_d, peak_px)
        elif px > armed[1]:
            # The break was retraced by a higher high, so it was not the cycle top.
            armed = None
            peak_d, peak_px = d, px
    if armed is not None:
        peak_d, peak_px = armed

    after = [px for d, px in subset if d >= peak_d]
    decline = (min(after) / peak_px - 1) if after else 0.0
    if armed is not None:
        status = "drawdown_top"
        lag = months_between(peak_d, signal)
    else:
        on_edge = (end - peak_d).days <= 30
        status = "window_edge" if on_edge else "high_without_25pct"
        lag = None if on_edge else months_between(peak_d, signal)
    return {
        "status": status,
        "peak_date": peak_d,
        "peak_price": peak_px,
        "drawdown": decline,
        "lag_months": lag,
    }


def gain_share(
    rows: list[tuple[date, float]],
    start: date,
    peak: date,
    checkpoints: list[date],
) -> list[dict]:
    p0 = price_asof(rows, start)
    pp = price_asof(rows, peak)
    if p0 is None or pp is None or p0[1] == 0:
        return []
    total = pp[1] / p0[1] - 1
    out = []
    for day in checkpoints:
        if day > peak:
            continue
        px = price_asof(rows, day)
        if px is None:
            continue
        gained = px[1] / p0[1] - 1
        out.append(
            {
                "date": px[0],
                "checkpoint": day,
                "price": px[1],
                "return_from_start": gained,
                "share_of_gain": None if total == 0 else gained / total,
            }
        )
    return out


def cross_correlation(
    frame: CapexFrame,
    prices: dict[str, list[tuple[date, float]]],
    field: str,
    lags: range = range(-4, 5),
    start: date | None = None,
    end: date | None = None,
) -> dict[str, dict[int, float | None]]:
    """corr(quarterly price return_t, capex_signal_{t+lag}).

    Positive lag means the capex signal comes after the return, so the price
    led the signal.
    """
    import math

    quarters = frame.quarters
    signal = getattr(frame, field)

    def qret(rows, qe_prev, qe):
        a = price_asof(rows, qe_prev)
        b = price_asof(rows, qe)
        if a is None or b is None or a[1] <= 0 or b[1] <= 0:
            return None
        return math.log(b[1] / a[1])

    result: dict[str, dict[int, float | None]] = {}
    for name, rows in prices.items():
        result[name] = {}
        for lag in lags:
            xs: list[float] = []
            ys: list[float] = []
            for i in range(1, len(quarters)):
                qe = quarters[i]
                if start and qe < start:
                    continue
                if end and qe > end:
                    continue
                j = i + lag
                if j < 0 or j >= len(signal) or signal[j] is None:
                    continue
                ret = qret(rows, quarters[i - 1], qe)
                if ret is None:
                    continue
                xs.append(ret)
                ys.append(float(signal[j]))
            result[name][lag] = _corr(xs, ys)
    return result


def _corr(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 8:
        return None
    mx = sum(xs) / n
    my = sum(ys) / n
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 0 or vy <= 0:
        return None
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / (vx ** 0.5 * vy ** 0.5)
