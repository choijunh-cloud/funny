#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("/workspace/scripts")))
import oct7_model as M


def test_cagr_and_cpu_paths():
    assert abs(M.cagr(29, 300, 5) - ((300 / 29) ** 0.2 - 1)) < 1e-9
    cpu = M.build_cpu_tam()
    assert len(cpu["paths"]) == 3
    oct_ = next(p for p in cpu["paths"] if p["name"] == "Citi Oct")
    assert oct_["y2030"] == 300
    assert oct_["y2026_implied"] > 40
    bridge = cpu["bridge_oct_vs_may"]
    assert bridge["delta_2030_B"] == 300 - 131.5
    assert bridge["if_non_agentic_fixed_at_may"]["implied_agentic_share"] > 0.7


def test_muse_overstate():
    rows = M.build_muse_grid()
    assert len(rows) == 3 * 3 * 3
    info = M.muse_insights(rows)
    base = info["anchor_1e8_dau"]["base_active15_current"]
    assert base["used_gb"] == 3
    assert base["naive_overstate_vs_physical"] > 2  # 8/3 / sharing ~2.4+
    bull = info["anchor_1e8_dau"]["bull_active30_complex"]
    assert bull["physical_PB"] > base["physical_PB"]


def test_valuation_bands():
    val = M.build_valuation()
    # 7x * 349/10 = 244.3
    assert abs(val["conservative_26y_no_growth"]["skh_man"]["7"] - 244.3) < 0.2
    assert abs(val["conservative_26y_no_growth"]["sec_man"]["7"] - 33.53) < 0.2
    assert val["reevaluation_27y"]["skh"]["at_mu_parity_5.8x"] > 250
    assert 15 < val["mu_tp_debate"]["davidson_per_on_cy27_180"] < 20
    assert 17 < val["mu_tp_debate"]["davidson_per_on_fy27_165"] < 20
    assert val["adr"]["premium"] > 0.3
    assert abs(val["adr"]["adr_krw_man"] - 244.6) < 0.1


def test_capex_divergence():
    c = M.build_capex_paradox()
    agent = next(s for s in c["scenarios"] if s["name"] == "Bull_agentic")
    assert agent["infra_compute_proxy_multiple"] > agent["enterprise_ai_spend_multiple"]
    assert c["verdicts_from_source"]["그러므로_CapEx_과도"] == "비약"


def test_full_render():
    m = M.run_model()
    md = M.render_precise_md(m)
    assert "Physical PB" in md or "Physical" in md
    assert "$300" in md or "300" in md
    assert "재평가" in md
    assert len(md) > 2500


if __name__ == "__main__":
    test_cagr_and_cpu_paths()
    test_muse_overstate()
    test_valuation_bands()
    test_capex_divergence()
    test_full_render()
    print("ok")
