"""몬테카를로는 경로 수가 적어도 달력과 요약이 깨지지 않는지만 본다."""

from __future__ import annotations

import unittest

from hybrid_model.montecarlo import DAYS, EVENTS, MODULES, S0, T, run, summarize


class MonteCarloTests(unittest.TestCase):
    def test_calendar_has_the_event_dates(self):
        self.assertEqual(T, 60)
        self.assertEqual(DAYS[0].isoformat(), "2026-10-06")
        self.assertEqual(DAYS[-1].isoformat(), "2026-12-30")
        self.assertEqual(DAYS[EVENTS["cpi"]].isoformat(), "2026-10-15")
        self.assertEqual(DAYS[EVENTS["oct_last"]].isoformat(), "2026-10-30")

    def test_small_run_stays_finite(self):
        result = run(n=400, seed=42)
        self.assertEqual(result["path"].shape, (T, 400))
        summary = summarize(result)
        self.assertFalse(any(value != value for value in summary.values()))
        self.assertGreater(summary["p50"], 4000)
        self.assertLess(summary["p50"], 12000)
        self.assertAlmostEqual(summary["A"] + summary["B"] + summary["C"], 100, delta=0.2)

    def test_turning_modules_off_is_defined(self):
        quiet = summarize(run(n=200, seed=1, on={key: False for key in MODULES}))
        self.assertGreater(quiet["p50"], S0 * 0.5)
