#!/usr/bin/env python3
"""11개 원본 워드 산식 검증."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import aug19_data as a
import integrated_data as d


class TestFcf(unittest.TestCase):
    def test_385_is_25_150_210(self):
        self.assertEqual(
            d.SKH_FCF_YEARS["2025A"] + d.SKH_FCF_YEARS["2026E"] + d.SKH_FCF_YEARS["2027E"],
            385,
        )
        self.assertEqual(d.SKH_FCF_CUM["2027E"], 385)
        self.assertEqual(d.SKH_FCF_CUM["2028E"], 590)

    def test_return_floor(self):
        self.assertEqual(385 * 0.5, 192.5)
        self.assertEqual(192.5 - 40, 152.5)


class TestFx(unittest.TestCase):
    def test_eps_59(self):
        self.assertAlmostEqual(a.SKH_EPS_FX_HIT, 5.9, delta=0.08)

    def test_gp_bit_neutral(self):
        total = (1 + d.GP_BIT_DROP / 100) * (1 + d.BIT_GROWTH_NEUTRAL / 100)
        self.assertAlmostEqual(total, 1.0, delta=0.01)


class TestValuation(unittest.TestCase):
    def test_hdd_per(self):
        self.assertAlmostEqual(d.WDC_PX / d.WDC_FY27_EPS, d.WDC_PER, delta=0.2)
        self.assertAlmostEqual(d.STX_PX / d.STX_FY27_EPS, d.STX_PER, delta=0.5)

    def test_unitree_psr(self):
        mid = d.UNITREE_MCAP / 22
        self.assertGreater(mid, 150)
        self.assertLess(mid, 160)
        self.assertAlmostEqual(d.UNITREE_MCAP / d.UNITREE_NI_26E, d.UNITREE_PER, delta=5)

    def test_unitree_ipo(self):
        chg = (d.UNITREE_PX / d.UNITREE_IPO - 1) * 100
        self.assertAlmostEqual(chg, d.UNITREE_IPO_CHG, delta=0.2)


class TestBabaWolf(unittest.TestCase):
    def test_wolf_miss(self):
        self.assertLess(d.WOLF["eps"], d.WOLF["cons_eps"])
        self.assertAlmostEqual(d.WOLF["rev"], d.WOLF["cons_rev"], delta=1)

    def test_nvda_box(self):
        self.assertLess(d.NVDA_Q2["guide_lo"], d.NVDA_Q2["cons_rev"])
        self.assertLessEqual(d.NVDA_Q2["cons_rev"], d.NVDA_Q2["guide_hi"])
        self.assertGreater(d.NVDA_Q2["author"], d.NVDA_Q2["cons_rev"])


class TestSilicon2(unittest.TestCase):
    def test_h1_vs_fy25(self):
        self.assertAlmostEqual(d.SIL_H1["rev"] / d.SIL_FY25_REV, 0.67, delta=0.02)


if __name__ == "__main__":
    unittest.main()
