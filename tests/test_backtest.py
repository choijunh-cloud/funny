"""보정은 8월 5일 이전만 보고, 확인 구간 종가가 숫자로 남는지 본다."""

from __future__ import annotations

import unittest
from datetime import date

from hybrid_model.backtest import evaluate, load_prices
from hybrid_model.montecarlo import run


class BacktestTests(unittest.TestCase):
    def test_prices_reach_the_october_close(self):
        days, closes = load_prices()
        self.assertEqual(days[0], date(2024, 1, 2))
        self.assertEqual(days[-1], date(2026, 10, 2))
        self.assertAlmostEqual(closes[-1], 7003.74, delta=0.1)

    def test_calibration_uses_only_the_training_window(self):
        fit = evaluate()
        self.assertGreater(fit["scale"], 0.8)
        self.assertLess(fit["scale"], 1.6)
        self.assertGreater(fit["test_n"], 20)
        self.assertGreater(fit["test_coverage"], fit["test_old_coverage"])
        self.assertTrue(fit["cal_band"]["inside"])
        self.assertFalse(fit["use_drift"])

    def test_base_vol_argument_changes_the_width(self):
        narrow = run(n=300, seed=1, on={key: False for key in ("flow", "level", "rate", "earn", "tail", "season")}, base_vol=0.005)
        wide = run(n=300, seed=1, on={key: False for key in ("flow", "level", "rate", "earn", "tail", "season")}, base_vol=0.03)
        self.assertGreater(wide["path"][-1].std(), narrow["path"][-1].std())
