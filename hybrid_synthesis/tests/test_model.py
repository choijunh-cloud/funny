"""Lock the 2026-09-03 hybrid-synthesis arithmetic."""

from __future__ import annotations

import math
import unittest
from dataclasses import replace
from datetime import date

from hybrid_synthesis.model import (
    HARD_LANDING_DRAWDOWN,
    PCE_PARTIAL_CUT_ROOM,
    HybridInputs,
    Phase,
    Scenario,
    ai_expansion,
    baseline_inputs,
    evaluate,
    evaluate_all_scenarios,
    infer_phase,
    scenario_inputs,
)


class RateArithmeticTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inputs = baseline_inputs()

    def test_real_policy_and_neutral(self) -> None:
        self.assertAlmostEqual(self.inputs.real_policy_rate(), 0.05, places=12)
        self.assertAlmostEqual(self.inputs.real_neutral_rate(), 1.10, places=12)
        self.assertAlmostEqual(self.inputs.rate_gap(), -1.05, places=12)

    def test_structural_cut_closed_while_inverted(self) -> None:
        self.assertFalse(self.inputs.structural_cut_open())
        opened = replace(self.inputs, fed_funds=5.00, pce_yoy=3.50)
        self.assertGreater(opened.rate_gap(), 0.0)
        self.assertTrue(opened.structural_cut_open())

    def test_partial_cut_room_at_pce_3_5(self) -> None:
        self.assertEqual(PCE_PARTIAL_CUT_ROOM, 3.50)
        self.assertFalse(self.inputs.partial_cut_room())
        self.assertTrue(replace(self.inputs, pce_yoy=3.50).partial_cut_room())
        self.assertFalse(replace(self.inputs, pce_yoy=3.51).partial_cut_room())

    def test_hard_landing_uses_traded_ust_not_shadow(self) -> None:
        self.assertGreaterEqual(self.inputs.effective_ust10(), 4.80)
        self.assertLess(self.inputs.effective_ust10(), 5.00)
        self.assertFalse(self.inputs.hard_landing())
        self.assertTrue(replace(self.inputs, ust10=5.00).hard_landing())
        self.assertEqual(HARD_LANDING_DRAWDOWN, (-0.15, -0.10))


class BaselineSnapshotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snap = evaluate()

    def test_phase_one_on_3_september(self) -> None:
        self.assertEqual(self.snap.as_of, date(2026, 9, 3))
        self.assertEqual(self.snap.phase, Phase.CONVERGENCE)
        self.assertFalse(self.snap.structural_cut_open)
        self.assertFalse(self.snap.partial_cut_room)
        self.assertFalse(self.snap.hard_landing)

    def test_formula_identity(self) -> None:
        terms = self.snap.formula_terms()
        self.assertAlmostEqual(terms["M"], terms["R"] * terms["A"] + terms["D"], places=12)
        self.assertAlmostEqual(self.snap.defense["D"], 0.312, places=10)
        self.assertAlmostEqual(self.snap.expansion["A"], 1.2619022951120897, places=12)
        self.assertAlmostEqual(self.snap.relief["R"], 0.15549013826935323, places=12)
        self.assertAlmostEqual(self.snap.momentum, 0.508213362349393, places=12)
        self.assertGreater(self.snap.relief["R"], 0.10)
        self.assertLess(self.snap.relief["R"], 0.25)

    def test_nvidia_other_demand_share(self) -> None:
        self.assertAlmostEqual(self.snap.expansion["other_demand_share"], 40.0 / 89.0, places=12)

    def test_kospi_holds_phase_one_band(self) -> None:
        self.assertEqual(self.snap.kospi["band_low"], 6400.0)
        self.assertEqual(self.snap.kospi["band_high"], 6600.0)
        self.assertGreaterEqual(self.snap.kospi["expected"], 6400.0)
        self.assertLessEqual(self.snap.kospi["expected"], 6600.0)
        self.assertAlmostEqual(self.snap.kospi["expected"], 6600.0, places=8)

    def test_sixty_forty_book(self) -> None:
        self.assertAlmostEqual(self.snap.equity_weight, 0.60, places=12)
        self.assertAlmostEqual(self.snap.sleeves["CORE_SEMI"], 0.50, places=12)
        self.assertAlmostEqual(self.snap.sleeves["AI_CONNECT"], 0.25, places=12)
        self.assertAlmostEqual(self.snap.sleeves["MACRO_HEDGE"], 0.15, places=12)
        self.assertAlmostEqual(self.snap.sleeves["COSMETICS"], 0.10, places=12)
        self.assertAlmostEqual(sum(self.snap.sleeves.values()), 1.0, places=12)

    def test_phase_calendar(self) -> None:
        base = baseline_inputs()
        self.assertEqual(infer_phase(base), Phase.CONVERGENCE)
        self.assertEqual(infer_phase(replace(base, as_of=date(2026, 11, 20), pce_yoy=3.45)), Phase.PIVOT)
        self.assertEqual(infer_phase(replace(base, as_of=date(2027, 7, 1))), Phase.SUPERCYCLE)
        self.assertEqual(infer_phase(replace(base, bigtech_fcf_positive=True)), Phase.SUPERCYCLE)


class MechanismTests(unittest.TestCase):
    def test_cxmt_hbm_defends_korea_dram(self) -> None:
        low = ai_expansion(replace(baseline_inputs(), cxmt_hbm_intensity=0.0))
        high = ai_expansion(replace(baseline_inputs(), cxmt_hbm_intensity=1.0))
        self.assertGreater(high["cxmt_dram_defense"], low["cxmt_dram_defense"])
        self.assertGreater(high["A_china"], low["A_china"])

    def test_ymtc_nand_is_a_drag(self) -> None:
        low = ai_expansion(replace(baseline_inputs(), ymtc_nand_share=0.0))
        high = ai_expansion(replace(baseline_inputs(), ymtc_nand_share=0.20))
        self.assertGreater(high["ymtc_nand_drag"], low["ymtc_nand_drag"])
        self.assertLess(high["A_china"], low["A_china"])

    def test_fcf_turn_lifts_expansion(self) -> None:
        before = ai_expansion(baseline_inputs())
        after = ai_expansion(replace(baseline_inputs(), bigtech_fcf_positive=True))
        self.assertAlmostEqual(before["A_fcf"], 0.86, places=12)
        self.assertAlmostEqual(after["A_fcf"], 1.32, places=12)
        self.assertGreater(after["A"], before["A"])

    def test_hard_landing_cuts_risk_assets_ten_to_fifteen(self) -> None:
        snap = evaluate(scenario_inputs(Scenario.HARD_LANDING), scenario=Scenario.HARD_LANDING)
        self.assertTrue(snap.hard_landing)
        self.assertEqual(snap.phase, Phase.CONVERGENCE)
        self.assertAlmostEqual(snap.equity_weight, 0.45, places=12)
        spot = snap.inputs.kospi_spot
        self.assertAlmostEqual(snap.kospi["band_low"], spot * 0.85, places=12)
        self.assertAlmostEqual(snap.kospi["band_high"], spot * 0.90, places=12)
        shock = snap.kospi["expected"] / spot - 1.0
        self.assertGreaterEqual(shock, HARD_LANDING_DRAWDOWN[0] - 1e-12)
        self.assertLessEqual(shock, HARD_LANDING_DRAWDOWN[1] + 1e-12)

    def test_scenario_path_is_monotonic_in_momentum(self) -> None:
        all_snaps = evaluate_all_scenarios()
        self.assertLess(all_snaps["hard_landing"].momentum, all_snaps["base"].momentum)
        self.assertLess(all_snaps["base"].momentum, all_snaps["early_pivot"].momentum)
        self.assertLess(all_snaps["early_pivot"].momentum, all_snaps["fcf_inflection"].momentum)
        self.assertGreater(all_snaps["early_pivot"].kospi["expected"], 7800.0)
        self.assertGreater(all_snaps["fcf_inflection"].kospi["expected"], 8800.0)
        self.assertTrue(math.isfinite(all_snaps["jawboning"].momentum))


if __name__ == "__main__":
    unittest.main()
