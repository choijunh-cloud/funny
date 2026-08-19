#!/usr/bin/env python3
"""8/19 리포트 원문 수치의 재계산 검증."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from aug19_report_data import (  # noqa: E402
    ADR,
    BUYBACK,
    FCF_SCENARIOS,
    FX,
    PEER_BUYBACK,
    TARGETS,
    UNITREE,
    US_MEMORY,
    VALUATION,
    YEN_CARRY_2024,
)


class DerivedNumbers(unittest.TestCase):
    def test_fx_drop_matches_hynix_eps(self):
        drop = (FX["scenario_from"] - FX["scenario_to"]) / FX["scenario_from"]
        self.assertAlmostEqual(drop * 100, 6.5789, places=3)
        self.assertAlmostEqual(drop * 100 * FX["sens_hynix"], 5.921, places=2)

    def test_fx_profit_adjustment_band(self):
        impact = 0.059
        lo = FX["hynix_net_lo"] * impact
        hi = FX["hynix_net_hi"] * impact
        self.assertAlmostEqual(lo, 17.7, places=1)
        self.assertAlmostEqual(hi, 23.6, places=1)
        self.assertTrue(18 <= lo + 0.5)
        self.assertTrue(hi <= 24)

    def test_buyback_share_and_eps(self):
        pct = BUYBACK["shares_to_buy"] / BUYBACK["total_shares"] * 100
        self.assertAlmostEqual(pct, 3.295, places=2)
        self.assertAlmostEqual(BUYBACK["share_pct"], 3.3, places=1)
        eps = pct / (100 - pct) * 100
        self.assertAlmostEqual(eps, 3.407, places=2)
        self.assertAlmostEqual(BUYBACK["eps_uplift_pct"], 3.4, places=1)
        daily_bn = BUYBACK["amount_trn"] * 1_000 / BUYBACK["trading_days"]
        self.assertAlmostEqual(daily_bn, 645.161, places=2)
        self.assertAlmostEqual(BUYBACK["daily_krw_bn"], 645.2, places=1)

    def test_fcf_scenarios(self):
        self.assertEqual(FCF_SCENARIOS["원문 A (19:21 코멘트)"]["cum"] * 0.5, 192.5)
        self.assertEqual(192.5 - 40, 152.5)
        self.assertEqual(sum(FCF_SCENARIOS["원문 B (19:20 보수적)"]["detail"]), 565.0)
        self.assertEqual(sum(FCF_SCENARIOS["원문 B-기존 계산"]["detail"]), 658.0)

    def test_valuation_pers(self):
        sk = VALUATION["SK하이닉스"]
        ss = VALUATION["삼성전자"]
        self.assertAlmostEqual(sk["price"] / sk["eps26"], 4.335, places=2)
        self.assertAlmostEqual(sk["price"] / sk["eps27"], 3.432, places=2)
        self.assertAlmostEqual(ss["price"] / ss["eps26"], 5.167, places=2)
        self.assertAlmostEqual(ss["price"] / ss["eps27"], 3.683, places=2)
        self.assertEqual(TARGETS["SK하이닉스"][0], sk["eps26"] * 6)
        self.assertEqual(TARGETS["SK하이닉스"][1], sk["eps26"] * 7)
        self.assertEqual(TARGETS["삼성전자"][0], 287_000)
        self.assertAlmostEqual(ss["eps26"] * 6, 287_400, places=0)
        self.assertAlmostEqual(ss["eps26"] * 7, 335_300, places=0)

    def test_adr_premium(self):
        krw = ADR["price_usd"] * FX["adr_fx"]
        self.assertAlmostEqual(krw, 227_682, places=0)
        self.assertAlmostEqual(ADR["krw_equiv"] / VALUATION["SK하이닉스"]["price"] - 1, 0.52, places=2)
        self.assertAlmostEqual(ADR["krw_equiv"] / 1.20, ADR["implied_at_normal"], places=0)
        self.assertAlmostEqual(ADR["krw_equiv"] / 1.30, 1_753_846, places=0)
        self.assertAlmostEqual(ADR["krw_equiv"] / 1.35, 1_688_889, places=0)

    def test_us_memory_pers(self):
        mu = US_MEMORY["마이크론"]
        sd = US_MEMORY["샌디스크"]
        self.assertAlmostEqual(mu["price"] / mu["eps_cy27"], 6.247, places=2)
        self.assertAlmostEqual(sd["price"] / sd["eps_fy27"], 7.803, places=2)

    def test_yen_carry_2024(self):
        nk = YEN_CARRY_2024["nikkei"]
        ks = YEN_CARRY_2024["kospi"]
        self.assertAlmostEqual((nk["0805"] / nk["0731"] - 1) * 100, -19.55, places=2)
        self.assertAlmostEqual((ks["0805"] / ks["0731"] - 1) * 100, -11.87, places=2)

    def test_kioxia_moves(self):
        k = PEER_BUYBACK["키옥시아"]
        self.assertAlmostEqual((k["p1"] / k["p0"] - 1) * 100, 3.247, places=2)
        self.assertAlmostEqual((k["p2"] / k["p1"] - 1) * 100, 4.041, places=2)
        self.assertAlmostEqual((k["p2"] / k["p0"] - 1) * 100, 7.419, places=2)

    def test_unitree_psr(self):
        psr = UNITREE["close_mktcap_cny_100mn"] / UNITREE["rev26_cny_100mn"]
        self.assertAlmostEqual(psr, 155.36, places=1)
        self.assertAlmostEqual(psr / UNITREE["psr_bar"], 2.59, places=2)
        self.assertAlmostEqual(UNITREE["bom_china_usd_k"] / UNITREE["bom_us_usd_k"] * 100, 35.11, places=1)


class ChartSmoke(unittest.TestCase):
    def test_all_chart_helpers_render(self):
        import svg_charts as c

        out = []
        out.append(c.bar_h([("A", -1.3), ("B", 2.1)]))
        out.append(c.bar_v_group(["X", "Y"], [{"name": "s", "values": [1, 2], "color": "#123"}]))
        out.append(c.threshold_scale([(4.7, "now", 0)], [(4.4, 4.7, "#1f8a4c", "ok")], 4.4, 5.2))
        out.append(c.waterfall([("base", 100, "base"), ("cut", 20, "minus"), ("tot", 80, "total")]))
        out.append(c.chain_h([("a", "key"), ("b", "bad")]))
        out.append(c.chain_v([("a", "key"), ("b", "good", "note")]))
        out.append(
            c.quad_matrix(
                ("x", "lo", "hi"),
                ("y", "hi", "lo"),
                [("t", "b", "good")] * 4,
            )
        )
        out.append(c.donut(50, "50%"))
        out.append(c.line_chart(["1", "2"], [{"name": "s", "values": [1, 2], "color": "#123"}]))
        out.append(c.progress_bars([("a", 40, "#123")]))
        out.append(c.roadmap([("now", 10, "n"), ("later", 20, "l")]))
        out.append(c.range_bars([("a", 10, 20, "#123")], 0, 30, ref=(15, "ref")))
        out.append(c.timeline([("09:00", "open", "good")], 8, 12))
        out.append(c.tiles([("t", "1", "+1", "good")]))
        for svg in out:
            self.assertIn("<svg", svg)
            self.assertIn("</svg>", svg)


if __name__ == "__main__":
    unittest.main()
