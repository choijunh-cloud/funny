"""Lock the audited SEC series and the Q3 acceleration thresholds."""

import csv
from pathlib import Path

import pytest

from capex_accel.metrics import acceleration_identity, next_quarter_thresholds

CSV = Path(__file__).resolve().parents[1] / "output" / "capex_quarterly.csv"


def _rows():
    with CSV.open() as handle:
        return list(csv.DictReader(handle))


def test_2026_cash_and_acceleration_match_filings():
    by = {row["quarter"]: row for row in _rows()}
    assert float(by["2026-03-31"]["c"]) == pytest.approx(129.75, abs=0.02)
    assert float(by["2026-06-30"]["c"]) == pytest.approx(165.05, abs=0.02)
    assert float(by["2026-03-31"]["acceleration"]) == pytest.approx(11.56, abs=0.03)
    assert float(by["2026-06-30"]["acceleration"]) == pytest.approx(18.96, abs=0.03)
    msft_fy = sum(float(by[q]["MSFT"]) for q in ("2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"))
    assert msft_fy == pytest.approx(115.948, abs=0.01)
    levels = [float(row["c"]) for row in _rows()]
    i = [row["quarter"] for row in _rows()].index("2026-06-30")
    assert float(by["2026-06-30"]["acceleration"]) == pytest.approx(acceleration_identity(levels, i))


def test_q3_threshold_uses_2025_q3_not_q2():
    by = {row["quarter"]: row for row in _rows()}
    thresholds = next_quarter_thresholds(
        c_prev_year=float(by["2025-09-30"]["c"]),
        increment=float(by["2026-06-30"]["increment"]),
        acceleration=float(by["2026-06-30"]["acceleration"]),
    )
    assert thresholds["stay_positive"] == pytest.approx(174.1, abs=0.15)
    assert thresholds["new_high"] == pytest.approx(193.0, abs=0.15)
    # The 2026 Q2 print itself is not the hurdle for Q3.
    assert thresholds["new_high"] > float(by["2026-06-30"]["c"])
