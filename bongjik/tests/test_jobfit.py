# -*- coding: utf-8 -*-
import unittest

from bongjik.jobfit_v2 import (
    CUT_CONFIRM,
    CUT_SCREEN,
    CUT_UNIT,
    SAFE_FLOOR,
    SAFE_SCREEN,
    estimate_offer,
    evaluate_postings,
    prepare,
    target_bands,
    POSTING_EXAMPLES,
)


class JobFitV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool, cls.fin, cls.ov = prepare()
        cls.by_name = {d["h"]: d for d in cls.pool}

    def test_pool_size(self):
        self.assertGreaterEqual(len(self.pool), 68)
        rankable = [d for d in self.pool if d.get("rankable")]
        self.assertGreaterEqual(len(rankable), 65)
        self.assertGreaterEqual(len(self.fin), 60)

    def test_bestian_excluded(self):
        d = next(x for x in self.pool if "베스티안" in x["h"])
        self.assertFalse(d["rankable"])
        self.assertIsNone(d.get("comp_rank"))

    def test_fire_hospital_provisional(self):
        d = self.by_name["국립소방병원"]
        self.assertIsNone(d["tot"])
        self.assertIsNone(d["pp"])
        self.assertTrue(d.get("incomplete"))

    def test_nazareth_override(self):
        naz = next(d for d in self.pool if "나사렛" in d["h"])
        self.assertEqual(naz["cash2"], 2800)
        self.assertEqual(naz["incen_src"], "실측")
        est = naz["mpat"] * 0.354 * naz["acu"] * 3
        self.assertLess(abs(est - 276) / 276, 0.08)
        self.assertGreaterEqual(naz["comp_rank"], 15)

    def test_kyunghee_and_jinju_top(self):
        kh = self.by_name["경희의료원(회기)"]
        jj = self.by_name["진주경상대"]
        self.assertLessEqual(kh["comp_rank"], 5)
        self.assertLessEqual(jj["comp_rank"], 5)
        seoul = [d for d in self.fin if d.get("zone") == "서울"]
        self.assertEqual(seoul[0]["h"], "경희의료원(회기)")

    def test_redcross_avoid(self):
        o = self.by_name["인천적십자(병당O)"]
        self.assertEqual(o["verdict"], "AVOID")
        self.assertIn(o["verdict_why"], ("회피리스트", "법적D", "한산약백업"))

    def test_dc_spendable(self):
        anyang = self.by_name["안양샘병원"]
        self.assertEqual(anyang["retire_type"], "dc_in_net")
        self.assertAlmostEqual(anyang["cash_spendable"], anyang["cash2"] * 12 / 13, places=2)
        jinju = self.by_name["진주경상대"]
        self.assertEqual(jinju["retire_type"], "separate")
        self.assertEqual(jinju["cash_spendable"], jinju["cash2"])

    def test_confirm_set_quality(self):
        confirm = [d for d in self.pool if d["verdict"] == "PASS_CONFIRM"]
        self.assertGreaterEqual(len(confirm), 6)
        self.assertTrue(all((d.get("safe") or 0) >= SAFE_FLOOR for d in confirm))
        self.assertTrue(all((d.get("pp2") or 0) >= CUT_CONFIRM for d in confirm))

    def test_screen_looser_than_confirm(self):
        screen = {d["h"] for d in self.pool if d["verdict"] in ("PASS_SCREEN", "PASS_CONFIRM")}
        confirm = {d["h"] for d in self.pool if d["verdict"] == "PASS_CONFIRM"}
        self.assertTrue(confirm.issubset(screen))

    def test_personal_prefers_seoul(self):
        kh = self.by_name["경희의료원(회기)"]
        jj = self.by_name["진주경상대"]
        self.assertGreater(kh["commute"], jj["commute"])
        self.assertLessEqual(kh["personal_rank"], 6)

    def test_residual_attached(self):
        kh = self.by_name["경희의료원(회기)"]
        self.assertIsNotNone(kh["pp2_exp"])
        self.assertIsNotNone(kh["pp2_resid"])
        self.assertGreater(kh["pp2"], CUT_UNIT)

    def test_target_bands(self):
        bands = target_bands(self.pool)
        self.assertIn("서울균형", bands)
        self.assertGreaterEqual(bands["확정통과"]["n"], 5)
        seoul = bands["서울균형"]
        self.assertIsNotNone(seoul["pp2"])
        self.assertGreaterEqual(seoul["pp2"]["p50"], CUT_SCREEN)

    def test_estimate_offer(self):
        est = estimate_offer(zone="서울", backup="강", pp=2000, hours=120, pool=self.pool)
        self.assertEqual(est["목표통장_확정"], round(CUT_CONFIRM * 2000 / 12))
        self.assertEqual(est["목표통장_스크리닝"], round(CUT_SCREEN * 2000 / 12))
        self.assertGreater(est["목표통장_확정"], est["목표통장_스크리닝"])
        self.assertIsNotNone(est["시간당_추정"])
        self.assertLessEqual(est["시간당_추정"], 2.0)

    def test_evaluate_postings(self):
        cards = evaluate_postings(self.pool, POSTING_EXAMPLES, self.ov)
        self.assertEqual(len(cards), 3)
        names = {c["h"] for c in cards}
        self.assertTrue(names)
        seran = next(c for c in cards if "세란" in c["h"])
        self.assertIn(seran["verdict"], ("HOLD", "AVOID", "PASS_SCREEN"))
        osan = next(c for c in cards if "오산" in c["h"])
        self.assertIsNotNone(osan["pp2"])
        self.assertGreaterEqual(osan["safe"], SAFE_FLOOR)

    def test_market_score_ignores_commute(self):
        """시장 1위가 통근 가산만으로 바뀌지 않는지 — 진주는 통근 -5여도 시장 상위 가능."""
        jj = self.by_name["진주경상대"]
        self.assertEqual(jj["commute"], -5)
        self.assertLessEqual(jj["comp_rank"], 5)
        self.assertGreater(jj["personal_rank"], jj["comp_rank"])


if __name__ == "__main__":
    unittest.main()
