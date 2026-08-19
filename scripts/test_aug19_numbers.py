#!/usr/bin/env python3
"""공개 코멘트 산식이 차트·보고서 숫자와 맞는지 검증."""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import aug19_data as d


class TestFx(unittest.TestCase):
    def test_usdkrw_move(self):
        self.assertAlmostEqual(d.USD_KRW_MOVE_PCT, (1420 / 1520 - 1) * 100, places=6)
        self.assertTrue(-6.6 < d.USD_KRW_MOVE_PCT < -6.5)

    def test_skh_eps_hit_matches_comment(self):
        # 원문: EPS 약 -5.9%
        self.assertAlmostEqual(d.SKH_EPS_FX_HIT, abs(d.USD_KRW_MOVE_PCT) * 0.9, places=6)
        self.assertAlmostEqual(d.SKH_EPS_FX_HIT, 5.9, delta=0.08)

    def test_ni_adjustment_18_to_24(self):
        self.assertAlmostEqual(d.SKH_NI_ADJ_LOW, 300 * d.SKH_EPS_FX_HIT / 100, places=6)
        self.assertAlmostEqual(d.SKH_NI_ADJ_HIGH, 400 * d.SKH_EPS_FX_HIT / 100, places=6)
        self.assertGreaterEqual(d.SKH_NI_ADJ_LOW, 17.5)
        self.assertLessEqual(d.SKH_NI_ADJ_HIGH, 24.2)


class TestBuyback(unittest.TestCase):
    def test_share_count_and_eps(self):
        self.assertAlmostEqual(d.SKH_BUYBACK_SHARES_M, 24.07, delta=0.05)
        self.assertAlmostEqual(d.SKH_BUYBACK_PCT, 3.3, delta=0.05)
        self.assertAlmostEqual(d.SKH_EPS_UPLIFT, 3.4, delta=0.08)

    def test_daily_pace(self):
        self.assertAlmostEqual(d.SKH_DAILY_KRW_100M, 6452, delta=2)

    def test_return_math(self):
        self.assertEqual(d.SKH_RETURN_MIN, 192.5)
        self.assertEqual(d.SKH_RETURN_ADD, 152.5)
        self.assertEqual(d.SKH_FCF_CONSERVATIVE_SUM, 565)


class TestValuation(unittest.TestCase):
    def test_per_bands(self):
        self.assertEqual(d.SKH_PER6, 346_000 * 6)
        self.assertEqual(d.SKH_PER7, 346_000 * 7)
        self.assertEqual(d.SEC_PER6, 47_900 * 6)
        self.assertEqual(d.SEC_PER7, 47_900 * 7)
        self.assertAlmostEqual(d.SKH_PER6 / 10_000, 207.6, places=1)
        self.assertAlmostEqual(d.SKH_PER7 / 10_000, 242.2, places=1)
        self.assertAlmostEqual(d.SEC_PER6 / 10_000, 28.74, places=2)
        self.assertAlmostEqual(d.SEC_PER7 / 10_000, 33.53, places=2)

    def test_adr_implied(self):
        self.assertAlmostEqual(d.SKH_ADR_HIGH * d.SKH_ADR_FX_REF * 10 / 10_000, 227.7, delta=0.5)


class TestHbmAndPeers(unittest.TestCase):
    def test_hbm_net(self):
        for s in d.HBM_SCENARIOS:
            self.assertEqual(s["net"], s["ai"] - s["eff"])

    def test_unitree_psr(self):
        self.assertAlmostEqual(d.UNITREE_MCAP_CNY / d.UNITREE_SALES_26, d.UNITREE_PSR, delta=0.5)
        self.assertAlmostEqual(d.UNITREE_PSR / d.UNITREE_PSR_FAIR_FRAME, 2.58, delta=0.05)


class TestNoNans(unittest.TestCase):
    def test_finite(self):
        for name in dir(d):
            if name.startswith("_"):
                continue
            val = getattr(d, name)
            if isinstance(val, (int, float)):
                self.assertTrue(math.isfinite(val), name)


if __name__ == "__main__":
    unittest.main()
