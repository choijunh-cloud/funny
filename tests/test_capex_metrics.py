"""Algebra of the second difference and the published 2026 thresholds."""

from datetime import date

import pytest

from capex_accel.metrics import (
    acceleration_identity,
    build_frame,
    extend_with_targets,
    future_quarter_to_beat,
    next_quarter_thresholds,
    quarter_end,
)


def _sample():
    # Eight quarters. Acceleration at the last point uses c[7], c[6], c[3], c[2].
    c = [10.0, 12.0, 11.0, 14.0, 18.0, 21.0, 19.0, 30.0]
    quarters = [quarter_end(2024 + (i // 4), (i % 4) + 1) for i in range(8)]
    # 2024 Q1 .. 2025 Q4
    return quarters, c


def test_acceleration_matches_the_cash_identity():
    quarters, c = _sample()
    frame = build_frame(quarters, c)
    for i in range(5, len(c)):
        assert frame.acceleration[i] == pytest.approx(acceleration_identity(c, i))


def test_gap_in_quarters_is_rejected():
    quarters, c = _sample()
    with pytest.raises(ValueError):
        build_frame(quarters[:3] + quarters[5:], c[:3] + c[5:])


def test_2026_thresholds_from_reported_levels():
    # Levels reproduced from SEC company-facts cash PP&E, $ billions.
    c25_q3 = 97.268
    c25_q4 = 118.635
    c26_q1 = 129.752
    c26_q2 = 165.053
    c25_q1 = 71.904
    c25_q2 = 88.247
    increment = c26_q2 - c25_q2
    acceleration = increment - (c26_q1 - c25_q1)
    thresholds = next_quarter_thresholds(c25_q3, increment, acceleration)
    assert acceleration == pytest.approx(18.96, abs=0.05)
    assert thresholds["new_high"] == pytest.approx(193.0, abs=0.15)
    assert thresholds["stay_positive"] == pytest.approx(174.1, abs=0.15)
    q1_2027 = future_quarter_to_beat(c26_q1, acceleration, 200.0 - c25_q4)
    assert q1_2027 == pytest.approx(230.1, abs=0.2)


def test_stated_acceleration_path_rebuilds_the_annual_totals():
    # History only needs the last four actual quarters plus the latest increment.
    quarters = [
        date(2025, 9, 30),
        date(2025, 12, 31),
        date(2026, 3, 31),
        date(2026, 6, 30),
    ]
    c = [97.27, 118.63, 129.75, 165.05]
    start_d = 165.05 - 88.25
    base = extend_with_targets(quarters, c, start_d, [10.8, -6.2, 13.7, -15.3, 0.1, 4.9])
    reaccel = extend_with_targets(quarters, c, start_d, [10.8, -6.2, 38.7, -15.3, 0.1, 4.9])
    h1 = 129.75 + 165.05
    assert h1 + base[0]["c"] + base[1]["c"] == pytest.approx(680, abs=1.0)
    assert sum(row["c"] for row in base if row["quarter"].year == 2027) == pytest.approx(1020, abs=2)
    assert sum(row["c"] for row in reaccel if row["quarter"].year == 2027) == pytest.approx(1120, abs=2)
    assert base[0]["c"] < 193
    assert reaccel[2]["acceleration"] > base[2]["acceleration"]
