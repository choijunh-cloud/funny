# -*- coding: utf-8 -*-
import unittest

from bongjik.model import (
    CUT_CONFIRM,
    CUT_SCREEN,
    CUT_UNIT,
    EXPECTED_POOL,
    SAFE_COLLAPSE,
    SAFE_FLOOR,
    SAFE_SCREEN,
    estimate_offer,
    evaluate_postings,
    load_postings,
    make_labels,
    prepare,
    stat_cut,
    target_bands,
)


class UnifiedModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pool, cls.fin, cls.ov = prepare()
        cls.by_name = {d["h"]: d for d in cls.pool}

    def test_pool_size(self):
        self.assertGreaterEqual(len(self.pool), EXPECTED_POOL[0])
        self.assertLessEqual(len(self.pool), EXPECTED_POOL[1])
        rankable = [d for d in self.pool if d.get("rankable")]
        self.assertGreaterEqual(len(rankable), 68)
        self.assertGreaterEqual(len(self.fin), 65)

    def test_nmc_in_pool(self):
        self.assertIn("국립중앙의료원", self.by_name)
        nmc = self.by_name["국립중앙의료원"]
        self.assertEqual(nmc["zone"], "서울")
        self.assertEqual(nmc["commute"], 3)
        self.assertEqual(nmc["incen_src"], "시트인센포함")
        self.assertAlmostEqual(nmc["cash2"], 2210, delta=1)
        self.assertLess(nmc["pp2"], CUT_SCREEN)
        self.assertEqual(nmc["verdict"], "HOLD")

    def test_wonkwang_in_pool(self):
        d = self.by_name["원광산본"]
        self.assertEqual(d["zone"], "수도권")
        self.assertGreaterEqual(d["wlb"], 6.0)
        self.assertLess(d["tot"], 15000)

    def test_bestian_excluded(self):
        d = next(x for x in self.pool if "베스티안" in x["h"])
        self.assertFalse(d["rankable"])
        self.assertIsNone(d.get("comp_rank"))

    def test_fire_hospital_provisional(self):
        d = self.by_name["국립소방병원"]
        self.assertIsNone(d["tot"])
        self.assertIsNone(d["pp"])
        self.assertTrue(d.get("incomplete"))
        self.assertEqual(d["cash2"], 2600)

    def test_nazareth_override(self):
        naz = next(d for d in self.pool if "나사렛" in d["h"])
        self.assertEqual(naz["cash2"], 2800)
        self.assertEqual(naz["incen_src"], "실측")
        est = naz["mpat"] * 0.354 * naz["acu"] * 3
        self.assertLess(abs(est - 276) / 276, 0.08)
        self.assertGreaterEqual(naz["comp_rank"], 15)

    def test_kyunghee_unit_and_seoul_first(self):
        kh = self.by_name["경희의료원(회기)"]
        jj = self.by_name["진주경상대"]
        self.assertAlmostEqual(kh["pp2"], 20.8, delta=0.2)
        self.assertLessEqual(kh["comp_rank"], 5)
        self.assertLessEqual(jj["comp_rank"], 5)
        seoul = [d for d in self.fin if d.get("zone") == "서울"]
        self.assertEqual(seoul[0]["h"], "경희의료원(회기)")

    def test_frame_a_vs_b_named(self):
        """1위가 갈릴 수 있다. 둘 다 상위여야 하고 이름을 숨기지 않는다."""
        a1 = self.fin[0]["h"]
        b1 = min(
            (d for d in self.pool if d.get("v51_rank")),
            key=lambda d: d["v51_rank"],
        )["h"]
        self.assertIn(a1, ("진주경상대", "경희의료원(회기)"))
        self.assertIn(b1, ("진주경상대", "경희의료원(회기)"))
        self.assertLessEqual(self.by_name["진주경상대"]["comp_rank"], 2)
        self.assertLessEqual(self.by_name["경희의료원(회기)"]["v51_rank"], 3)

    def test_redcross_avoid(self):
        o = self.by_name["인천적십자(병당O)"]
        self.assertEqual(o["verdict"], "AVOID")
        self.assertIn(o["verdict_why"], ("회피리스트", "법적D", "한산약백업", "안전붕괴"))

    def test_safety_collapse_veto(self):
        collapsed = [d for d in self.pool if (d.get("safe") or 99) < SAFE_COLLAPSE and d.get("rankable")]
        self.assertTrue(collapsed)
        self.assertTrue(all(d["verdict"] == "AVOID" for d in collapsed))

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
        self.assertLessEqual(kh["personal_rank"], 8)
        nmc = self.by_name["국립중앙의료원"]
        self.assertGreaterEqual(nmc["commute"], kh["commute"])

    def test_nmc_loses_to_samsung_on_unit(self):
        nmc = self.by_name["국립중앙의료원"]
        samsung = self.by_name["강북삼성병원"]
        self.assertGreater(samsung["pp2"], nmc["pp2"])
        self.assertGreater(samsung["safe"], nmc["safe"])
        self.assertEqual(samsung["verdict"], "PASS_CONFIRM")
        self.assertEqual(nmc["verdict"], "HOLD")

    def test_residual_attached(self):
        kh = self.by_name["경희의료원(회기)"]
        self.assertIsNotNone(kh["pp2_exp"])
        self.assertIsNotNone(kh["pp2_resid"])
        self.assertGreater(kh["pp2"], CUT_UNIT)

    def test_target_bands(self):
        bands = target_bands(self.pool)
        self.assertIn("서울균형", bands)
        self.assertIn("출장형", bands)
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

    def test_evaluate_core_postings(self):
        specs = [s for s in load_postings()["evaluate"] if s["name"] in (
            "김포우리(복원)", "세란(신규)", "오산한국(8인·갱신)",
        )]
        cards = evaluate_postings(self.pool, specs, self.ov)
        self.assertEqual(len(cards), 3)
        seran = next(c for c in cards if "세란" in c["h"])
        self.assertIn(seran["verdict"], ("HOLD", "AVOID", "PASS_SCREEN"))
        osan = next(c for c in cards if "오산" in c["h"])
        self.assertIsNotNone(osan["pp2"])
        self.assertGreaterEqual(osan["safe"], SAFE_FLOOR)

    def test_august_holdout_verdicts(self):
        specs = load_postings()["evaluate"]
        cards = {d["h"]: d for d in evaluate_postings(self.pool, specs, self.ov)}
        self.assertEqual(cards["부산동의병원"]["verdict"], "AVOID")
        self.assertIn(cards["부산동의병원"]["verdict_why"], ("회피리스트", "안전붕괴"))
        self.assertEqual(cards["검단탑병원"]["verdict"], "HOLD")
        self.assertEqual(cards["천안충무(보수)"]["verdict"], "HOLD")
        self.assertEqual(cards["천안충무(관대)"]["verdict"], "HOLD")
        self.assertEqual(cards["국립중앙의료원(7인·104h)"]["verdict"], "HOLD")
        kosin = cards["고신대복음병원"]
        self.assertIn(kosin["verdict"], ("HOLD", "PASS_SCREEN"))
        self.assertFalse(kosin["g"]["연환자"])

    def test_market_score_ignores_commute(self):
        jj = self.by_name["진주경상대"]
        self.assertEqual(jj["commute"], -5)
        self.assertLessEqual(jj["comp_rank"], 5)
        self.assertGreater(jj["personal_rank"], jj["comp_rank"])

    def test_l1_cut_stays_in_band(self):
        labels = make_labels(self.pool)
        st = stat_cut(self.pool, labels["L1_종합TOP20(페이포함)"])
        self.assertIsNotNone(st["best_cut"])
        self.assertGreaterEqual(st["best_cut"], 11.0)
        self.assertLessEqual(st["best_cut"], 16.0)
        if st["zone"]:
            self.assertLessEqual(st["zone"][0], CUT_UNIT)
            self.assertGreaterEqual(st["zone"][1], 13.0)

    def test_infer_does_not_double_count_nmc_or_halla(self):
        nmc = self.by_name["국립중앙의료원"]
        halla = self.by_name["제주한라병원"]
        self.assertEqual(nmc["incen_src"], "시트인센포함")
        self.assertEqual(halla["incen_src"], "시트인센포함")
        self.assertEqual(nmc["incen"], 0)
        self.assertEqual(halla["incen"], 0)


if __name__ == "__main__":
    unittest.main()
