#!/usr/bin/env python3
"""Lock the August 2026 baseline arithmetic for the panel regime model."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from panel_regime_model import (
    ASSET_KEYS,
    BASELINE_EXECUTION,
    HORIZONS,
    TwoAxisRegimeClassifier,
    _largest_remainder_percentages,
    run_baseline,
)


class BaselineArithmeticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snapshot = run_baseline()
        cls.model = TwoAxisRegimeClassifier()

    def test_display_percentages_sum_to_100(self) -> None:
        for horizon in HORIZONS:
            self.assertEqual(sum(self.snapshot["horizons"][horizon]["disp"].values()), 100)

    def test_allocation_sums_to_one(self) -> None:
        for horizon in HORIZONS:
            total = sum(self.snapshot["horizons"][horizon]["alloc"].values())
            self.assertAlmostEqual(total, 1.0, places=12)

    def test_state_vectors(self) -> None:
        expected = {
            "3M": (0.5066176470588235, -0.16875),
            "6M": (0.31, -0.06857142857142857),
            "12M": (0.025892857142857134, -0.04318181818181818),
        }
        for horizon, (p_exp, f_exp) in expected.items():
            self.assertAlmostEqual(self.snapshot["horizons"][horizon]["p"], p_exp, places=12)
            self.assertAlmostEqual(self.snapshot["horizons"][horizon]["f"], f_exp, places=12)

    def test_regime_display_percentages(self) -> None:
        expected = {
            "3M": {"A": 22, "B": 33, "B*": 23, "C": 15, "D": 7},
            "6M": {"A": 19, "B": 29, "B*": 17, "C": 22, "D": 13},
            "12M": {"A": 14, "B": 25, "B*": 13, "C": 28, "D": 20},
        }
        for horizon, row in expected.items():
            self.assertEqual(self.snapshot["horizons"][horizon]["disp"], row)

    def test_allocation_one_decimal(self) -> None:
        expected = {
            "3M": {
                "Semiconductor": 35.2,
                "AI_Compute": 10.5,
                "Power_Grid": 16.9,
                "Non_Semi_Export": 17.0,
                "Cash": 20.5,
            },
            "6M": {
                "Semiconductor": 33.6,
                "AI_Compute": 10.3,
                "Power_Grid": 16.8,
                "Non_Semi_Export": 17.4,
                "Cash": 21.9,
            },
            "12M": {
                "Semiconductor": 31.4,
                "AI_Compute": 9.7,
                "Power_Grid": 16.7,
                "Non_Semi_Export": 17.8,
                "Cash": 24.3,
            },
        }
        for horizon, row in expected.items():
            for asset, value in row.items():
                self.assertAlmostEqual(
                    self.snapshot["horizons"][horizon]["alloc"][asset] * 100.0,
                    value,
                    places=1,
                )

    def test_kospi_mixture_rounded(self) -> None:
        expected = {
            "3M": {"expected_level": 7388, "p10": 6335, "p50": 7328, "p90": 8794},
            "6M": {"expected_level": 7227, "p10": 5674, "p50": 7210, "p90": 8735},
            "12M": {"expected_level": 6981, "p10": 5498, "p50": 6870, "p90": 8533},
        }
        for horizon, row in expected.items():
            proj = self.snapshot["horizons"][horizon]["proj"]
            for key, value in row.items():
                self.assertEqual(round(proj[key]), value)

    def test_execution_normal(self) -> None:
        exe = self.snapshot["execution"]
        self.assertEqual(exe["level"], "NORMAL")
        self.assertEqual(exe["clusters"], [])
        self.assertAlmostEqual(exe["spread"], (52.73 - 44.50) / 44.50 * 100.0, places=10)
        self.assertAlmostEqual(exe["drawdown"], 6852.0 / 9360.0 - 1.0, places=12)
        self.assertTrue(exe["spread"] > 5.0)
        self.assertGreater(exe["drawdown"], -0.40)
        self.assertLess(exe["forward_pe"], exe["valuation_ceiling"])

    def test_largest_remainder_tie_break(self) -> None:
        self.assertEqual(sum(_largest_remainder_percentages((0.333, 0.333, 0.334))), 100)

    def test_softmax_weights_are_finite_probabilities(self) -> None:
        for horizon in HORIZONS:
            weights = self.snapshot["horizons"][horizon]["weights"]
            self.assertTrue(all(math.isfinite(v) and v > 0.0 for v in weights.values()))
            self.assertAlmostEqual(sum(weights.values()), 1.0, places=12)

    def test_policy_uses_all_assets(self) -> None:
        for code, centroid in self.model.regimes.items():
            self.assertEqual(set(centroid.policy_weights), set(ASSET_KEYS))
            self.assertAlmostEqual(sum(centroid.policy_weights.values()), 1.0, places=12)
            _ = code

    def test_price_observation_comparable(self) -> None:
        observation = BASELINE_EXECUTION.price_observation
        assert observation is not None
        self.assertEqual(observation.comparability_issues(), ())


if __name__ == "__main__":
    unittest.main()
