"""Lock document 4 — 절단된 사슬 — transfer-model v2 arithmetic."""

from __future__ import annotations

import unittest

from hybrid_synthesis.model import evaluate
from hybrid_synthesis.portfolio import build_portfolio
from hybrid_synthesis.universe import by_ticker
from hybrid_synthesis import v2


class ChainCutTests(unittest.TestCase):
    def test_brent_still_ninety_six(self) -> None:
        self.assertEqual(v2.OIL_BRENT, 96.0)

    def test_cut_threshold_and_oil_transfer(self) -> None:
        self.assertAlmostEqual(v2.real_neutral(), 1.10, places=12)
        self.assertAlmostEqual(v2.cut_threshold_pi(), 2.65, places=12)
        self.assertAlmostEqual(v2.oil_pce_transfer(), 0.735, places=12)
        self.assertAlmostEqual(v2.residual_gap_after_oil(), 0.315, places=12)

    def test_hike_path_walks_back_after_waller(self) -> None:
        self.assertEqual(v2.HIKE_JACKSON_HOLE, 0.35)
        self.assertEqual(v2.HIKE_SEP3, 0.63)
        self.assertEqual(v2.HIKE_AFTER_WALLER, 0.50)

    def test_waller_threshold_sits_above_cut_line(self) -> None:
        self.assertGreater(v2.WALLER_CORE_THRESHOLD, v2.cut_threshold_pi())
        self.assertGreater(v2.PCE_CORE, v2.WALLER_CORE_THRESHOLD)
        self.assertLess(v2.PCE_TRIMMED, v2.cut_threshold_pi())
        self.assertGreater(v2.PCE_HEADLINE, v2.cut_threshold_pi())


class ScenarioReweightTests(unittest.TestCase):
    def test_probabilities_sum_to_one(self) -> None:
        self.assertAlmostEqual(sum(v2.v1_probs().values()), 1.0, places=12)
        self.assertAlmostEqual(sum(v2.v2_probs().values()), 1.0, places=12)

    def test_s3_tail_moves_to_s1_and_s4(self) -> None:
        self.assertAlmostEqual(v2.v1_probs()["S3"] - v2.v2_probs()["S3"], 0.07, places=12)
        self.assertAlmostEqual(v2.v2_probs()["S1"] - v2.v1_probs()["S1"], 0.04, places=12)
        self.assertAlmostEqual(v2.v2_probs()["S4"] - v2.v1_probs()["S4"], 0.02, places=12)
        self.assertAlmostEqual(v2.v2_probs()["S2"] - v2.v1_probs()["S2"], 0.01, places=12)

    def test_year_end_levels(self) -> None:
        self.assertAlmostEqual(v2.index_expected_v1(), 7337.95, places=2)
        self.assertAlmostEqual(v2.index_expected_v2(), 7383.21, places=2)
        self.assertAlmostEqual(v2.index_return_v2() * 100.0, 12.22, places=2)
        self.assertAlmostEqual(v2.s3_index_return_v2() * 100.0, -7.28, places=2)

    def test_supply_wall_is_per_not_eyeball(self) -> None:
        wall = v2.supply_wall()
        self.assertAlmostEqual(wall["released_tn"], 64.0, places=12)
        self.assertAlmostEqual(wall["days"], 3.838, places=2)
        self.assertAlmostEqual(wall["per_cut"], 0.230, places=2)
        self.assertAlmostEqual(wall["s1_level_v1"], 8255.0, places=4)
        self.assertAlmostEqual(wall["s1_level_v2"], 7960.0, places=0)


class BookCTests(unittest.TestCase):
    def test_ten_names_and_bucket_identity(self) -> None:
        self.assertEqual(len(v2.BOOK_C), 10)
        self.assertAlmostEqual(sum(item.weight_v3 for item in v2.BOOK_C), 100.0, places=12)
        buckets = v2.bucket_weights()
        self.assertAlmostEqual(buckets["SEMI"], 0.45, places=12)
        self.assertAlmostEqual(buckets["SHORT_DURATION"], 0.25, places=12)
        self.assertAlmostEqual(buckets["OIL_DOWN"], 0.10, places=12)
        self.assertAlmostEqual(buckets["HEDGE"], 0.20, places=12)

    def test_samsung_equals_hynix(self) -> None:
        weights = v2.book_weights()
        self.assertAlmostEqual(weights["000660"], weights["005930"], places=12)
        self.assertAlmostEqual(weights["000660"], 0.135, places=12)

    def test_oil_bucket_halves_when_policy_leg_is_cut(self) -> None:
        self.assertAlmostEqual(v2.OIL_POLICY_DECAY, 0.55, places=12)
        self.assertAlmostEqual(v2.oil_expected_v1(), 11.30, places=2)
        self.assertAlmostEqual(v2.oil_expected_v2(), 5.78, places=2)
        self.assertAlmostEqual(v2.OIL_BUCKET_V2["S1"] / v2.OIL_BUCKET_V1["S1"], 0.55, places=2)
        self.assertEqual(v2.OIL_BUCKET_V2["S3"], v2.OIL_BUCKET_V1["S3"])
        self.assertEqual(v2.OIL_BUCKET_V2["S4"], v2.OIL_BUCKET_V1["S4"])

    def test_adopted_book_beats_index_on_both_axes(self) -> None:
        self.assertAlmostEqual(v2.book_c_expected(), 12.47, places=12)
        self.assertAlmostEqual(v2.book_c_s3(), -5.13, places=12)
        self.assertAlmostEqual(v2.excess_vs_index(), 0.25, places=2)
        self.assertAlmostEqual(v2.downside_defense(), 2.15, places=2)

    def test_doc3_alpha_is_shaved_twice(self) -> None:
        self.assertAlmostEqual(v2.doc3_excess_v1(), 1.09, places=2)
        self.assertAlmostEqual(v2.doc3_excess_v2(), 0.83, places=2)

    def test_semi_cap_is_coefficient_not_probability(self) -> None:
        self.assertAlmostEqual(v2.SEMI_CAP, 0.469, places=12)
        self.assertAlmostEqual(v2.semi_s3_line(0.469), v2.s3_index_return_v2() * 100.0, places=2)

    def test_no_name_swap(self) -> None:
        self.assertEqual(
            [item.ticker for item in v2.BOOK_C],
            [
                "000660",
                "005930",
                "071050",
                "402340",
                "105560",
                "012330",
                "267260",
                "079550",
                "003490",
                "015760",
            ],
        )
        for item in v2.BOOK_C:
            self.assertEqual(by_ticker(item.ticker).market, "KOSPI")


class TapeIdentityTests(unittest.TestCase):
    def test_credit_cxmt_rack_hbm(self) -> None:
        self.assertAlmostEqual(v2.credit_interest_tn(), 2.97, places=12)
        self.assertAlmostEqual(v2.cxmt_ni_margin(), 15.0 / 29.0, places=12)
        self.assertAlmostEqual(v2.rack_multiple(), 60.0, places=12)
        self.assertAlmostEqual(v2.hbm_share_sum(), 1.14, places=12)

    def test_ledger_and_self_score(self) -> None:
        self.assertEqual(sum(v2.LEDGER.values()), 21)
        self.assertEqual(v2.LEDGER, {"confirmed": 9, "partial": 6, "rejected": 3, "unconfirmed": 3})
        self.assertEqual(v2.SELF_SCORE, {"win": 3, "loss": 2, "pending": 1})

    def test_phase1_book_is_untouched(self) -> None:
        held = [item.ticker for item in build_portfolio(evaluate()).holdings]
        self.assertNotIn("079550", held)
        self.assertNotIn("071050", held)
        self.assertEqual(held[0], "005930")
        self.assertEqual(held[1], "000660")
        self.assertAlmostEqual(held.__len__(), 14)


class SnapshotTests(unittest.TestCase):
    def test_snapshot_carries_the_cut(self) -> None:
        snap = v2.snapshot()
        self.assertEqual(snap["title"], "절단된 사슬")
        self.assertEqual(snap["chain_cut"]["policy_path"], "cut")
        self.assertEqual(snap["chain_cut"]["cost_path"], "live")
        self.assertAlmostEqual(snap["index"]["expected_v2"], 7383.21, places=2)
        self.assertAlmostEqual(snap["book_c"]["buckets"]["OIL_DOWN"], 0.10, places=12)


if __name__ == "__main__":
    unittest.main()
