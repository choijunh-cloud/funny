"""CapEx level, dollar increment, and acceleration.

Definitions, matched to a quarterly cash series c_q (billions of USD):

    T_q = c_q + c_{q-1} + c_{q-2} + c_{q-3}     trailing four-quarter sum
    D_q = T_q - T_{q-1} = c_q - c_{q-4}         dollar YoY increment
    A_q = D_q - D_{q-1} = T_q - 2 T_{q-1} + T_{q-2}
                                                acceleration, $B per quarter^2

A negative A_q means the dollar increment is shrinking. It does not mean
capex itself is falling.

    g_q = T_q / T_{q-4} - 1                     YoY growth of the TTM level
    quarterly_yoy_q = c_q / c_{q-4} - 1
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


def quarter_end(year: int, quarter: int) -> date:
    if quarter not in (1, 2, 3, 4):
        raise ValueError(f"quarter must be 1..4, got {quarter}")
    month_day = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
    month, day = month_day[quarter]
    return date(year, month, day)


def add_quarters(qe: date, n: int) -> date:
    idx = (qe.month - 1) // 3
    absolute = qe.year * 4 + idx + n
    year, q = divmod(absolute, 4)
    return quarter_end(year, q + 1)


def trailing_sum(values: list[float], window: int = 4) -> list[float | None]:
    out: list[float | None] = []
    for i in range(len(values)):
        if i < window - 1:
            out.append(None)
        else:
            out.append(float(sum(values[i - window + 1 : i + 1])))
    return out


def first_difference(values: list[float | None]) -> list[float | None]:
    out: list[float | None] = []
    for i, value in enumerate(values):
        prev = values[i - 1] if i else None
        if value is None or prev is None:
            out.append(None)
        else:
            out.append(float(value - prev))
    return out


def yoy_ratio(values: list[float | None], lag: int = 4) -> list[float | None]:
    out: list[float | None] = []
    for i, value in enumerate(values):
        base = values[i - lag] if i >= lag else None
        if value is None or base in (None, 0):
            out.append(None)
        else:
            out.append(float(value / base - 1.0))
    return out


@dataclass(frozen=True)
class CapexFrame:
    quarters: list[date]
    c: list[float]
    ttm: list[float | None]
    increment: list[float | None]
    acceleration: list[float | None]
    ttm_yoy: list[float | None]
    ttm_yoy_change: list[float | None]
    quarterly_yoy: list[float | None]

    def index(self, qe: date) -> int:
        return self.quarters.index(qe)

    def value(self, qe: date, field: str) -> float | None:
        return getattr(self, field)[self.index(qe)]


def build_frame(quarters: list[date], c: list[float]) -> CapexFrame:
    if len(quarters) != len(c):
        raise ValueError("quarters and c must have the same length")
    if quarters != sorted(quarters):
        raise ValueError("quarters must be sorted")
    for i in range(1, len(quarters)):
        if add_quarters(quarters[i - 1], 1) != quarters[i]:
            raise ValueError(f"gap between {quarters[i - 1]} and {quarters[i]}")
    ttm = trailing_sum(c, 4)
    increment = first_difference(ttm)
    acceleration = first_difference(increment)
    ttm_yoy = yoy_ratio(ttm, 4)
    ttm_yoy_change = first_difference(ttm_yoy)
    quarterly_yoy = yoy_ratio(c, 4)
    return CapexFrame(
        quarters=list(quarters),
        c=list(c),
        ttm=ttm,
        increment=increment,
        acceleration=acceleration,
        ttm_yoy=ttm_yoy,
        ttm_yoy_change=ttm_yoy_change,
        quarterly_yoy=quarterly_yoy,
    )


def acceleration_identity(c: list[float], i: int) -> float:
    """A_q = (c_q - c_{q-4}) - (c_{q-1} - c_{q-5}). Requires i >= 5."""
    return (c[i] - c[i - 4]) - (c[i - 1] - c[i - 5])


def next_quarter_thresholds(c_prev_year: float, increment: float, acceleration: float) -> dict[str, float]:
    """Cash print next quarter that would keep A positive, or set a new high.

    next_c > c_same_quarter_last_year + D_q        keeps acceleration positive
    next_c > c_same_quarter_last_year + D_q + A_q  sets a higher acceleration than quarter q
    """
    stay_positive = c_prev_year + increment
    new_high = c_prev_year + increment + acceleration
    return {"stay_positive": stay_positive, "new_high": new_high}


def future_quarter_to_beat(anchor_c: float, anchor_a: float, intervening_increment: float) -> float:
    """Level of a later quarter that would make its acceleration exceed anchor_a.

    For 2027Q1 vs 2026Q2, intervening_increment is c_2026Q4 - c_2025Q4,
    and anchor_c is c_2026Q1. Derived from

        A_future = (c_future - c_future_lag4) - intervening_increment
        A_future > A_anchor
    """
    return anchor_c + intervening_increment + anchor_a


def extend_with_targets(
    quarters: list[date],
    c: list[float],
    start_increment: float,
    target_acceleration: list[float],
) -> list[dict]:
    """Append quarters whose acceleration equals target_acceleration.

    The year-ago base for each new quarter is c four quarters earlier, including
    quarters appended by this function. That is what makes a Q3 assumption
    flow into the next year's Q3.
    """
    levels = list(c)
    built: list[dict] = []
    prev_d = start_increment
    cursor = quarters[-1]
    for target_a in target_acceleration:
        cursor = add_quarters(cursor, 1)
        base = levels[-4]
        increment = prev_d + target_a
        level = base + increment
        levels.append(level)
        built.append(
            {
                "quarter": cursor,
                "c": level,
                "increment": increment,
                "acceleration": target_a,
            }
        )
        prev_d = increment
    return built


def chain_from_acceleration(
    yoy_base: list[float],
    start_increment: float,
    target_acceleration: list[float],
) -> tuple[list[float], list[float], list[float]]:
    """Build future cash levels that realize a path of A_q.

    yoy_base[k] is c of the same quarter one year before the k-th future quarter,
    which may itself be a just-built future level once the horizon exceeds 4 quarters.
    """
    if len(yoy_base) != len(target_acceleration):
        raise ValueError("yoy_base and target_acceleration length mismatch")
    levels: list[float] = []
    increments: list[float] = []
    acceleration: list[float] = []
    prev_d = start_increment
    for base, target_a in zip(yoy_base, target_acceleration):
        d = prev_d + target_a
        level = base + d
        levels.append(level)
        increments.append(d)
        acceleration.append(target_a)
        prev_d = d
    return levels, increments, acceleration


def local_peaks(
    quarters: list[date],
    values: list[float | None],
    *,
    min_value: float,
    decline: float,
    lookforward: int,
    min_gap: int = 6,
) -> list[dict]:
    """Local maxima that are followed by a material decline.

    A peak at i requires value[i] >= neighbors, value[i] >= min_value, and
    some later point within `lookforward` quarters at least `decline` lower.
    Peaks closer than `min_gap` quarters keep the larger value.
    """
    found: list[dict] = []
    for i in range(1, len(values) - 1):
        cur = values[i]
        left = values[i - 1]
        right = values[i + 1]
        if cur is None or left is None or right is None:
            continue
        if cur < left or cur < right or cur < min_value:
            continue
        window = [v for v in values[i + 1 : i + 1 + lookforward] if v is not None]
        if not window or min(window) > cur - decline:
            continue
        item = {
            "quarter": quarters[i],
            "value": cur,
            "trough": min(window),
            "index": i,
        }
        if found and i - found[-1]["index"] < min_gap:
            if cur > found[-1]["value"]:
                found[-1] = item
        else:
            found.append(item)
    return found
