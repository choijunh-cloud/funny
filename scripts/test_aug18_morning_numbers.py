"""Quick 코멘트 산식 검산."""

from __future__ import annotations

import unittest

from aug18_morning_data import (
    HYNIX,
    MICRON,
    QOQ,
    adr_to_local_man,
    assert_all,
    conservative_tp,
    implied_local_from_premium,
    implied_per,
    local_per,
    qoq_fy_eps,
)


class NumberChecks(unittest.TestCase):
    def test_all_stated_numbers(self):
        rows = assert_all()
        self.assertGreaterEqual(len(rows), 20)
        self.assertTrue(all(c.ok for c in rows))

    def test_qoq_ladder_factor(self):
        # 1 + 1.10 + 1.155 + 1.21275 = 4.46775
        self.assertAlmostEqual(qoq_fy_eps(1.0, QOQ), 4.46775, places=5)

    def test_adr_ten_to_one(self):
        self.assertAlmostEqual(adr_to_local_man(171.38, 1417, 10), 242.84546, places=4)

    def test_local_per_definition(self):
        # 164.5만원 / 34.6만원 = 4.754...
        self.assertAlmostEqual(local_per(164.5, 346), 4.7543, places=3)

    def test_premium_inversion(self):
        self.assertAlmostEqual(implied_local_from_premium(243, 0.20), 202.5, places=4)
        self.assertAlmostEqual(implied_local_from_premium(243, 0.35), 180.0, places=4)

    def test_micron_and_conservative_tp(self):
        self.assertAlmostEqual(implied_per(MICRON["px"], MICRON["cy27_eps"]), 6.745, places=3)
        self.assertAlmostEqual(conservative_tp(HYNIX["eps_26k"], 6), 207.6, places=1)


if __name__ == "__main__":
    unittest.main()
