"""공개된 채점·확률·시계가 코드에서 다시 나오는지 고정한다."""

from __future__ import annotations

import json
import unittest
from datetime import date
from dataclasses import replace

from hybrid_model.ledger import PANELS, validate_ledger
from hybrid_model.market import (
    SNAPSHOT,
    KRX_HOLIDAYS,
    distance_pct,
    project_clocks,
    session_on,
)
from hybrid_model.model import HybridModel
from hybrid_model.render import render_html, render_text
from hybrid_model.scenarios import PRIOR, compute_posterior, normalize_weights
from hybrid_model.scoring import (
    FALS_WEIGHT,
    HIT_WEIGHT,
    LAYER_WEIGHT,
    composite,
    display_points,
    hit_rate,
    shrink,
)


PUBLISHED_HIT = {
    "이영훈": 75, "이진호": 75, "황유현": 71, "박근형": 68, "이영수": 67,
    "김장열": 63, "김민수": 62, "박명석": 62, "박병창": 61, "이은택": 50,
    "박세익": 44, "문홍철": 43, "이선엽": 31, "문남중": 28,
    "강건우": 88, "박현상": 88, "윤지호": 88, "김광석": 75, "박사주": 75,
    "김학균": 75, "홍춘욱": 70, "한지영": 62, "이건규": 62, "알상무": 60,
    "Quick 코멘트": 50, "이건희": 50, "김중손": 40, "김대호": 40, "빈센트": 0,
}

PUBLISHED_SCORE = {
    "이진호": 76, "알상무": 70, "윤지호": 70, "황유현": 70, "이영수": 70,
    "이영훈": 70, "강건우": 68, "박현상": 68, "Quick 코멘트": 67,
    "김광석": 66, "김학균": 66, "홍춘욱": 66,
}

MAIN_ORDER = [
    "이영훈", "이진호", "황유현", "박근형", "이영수", "김장열", "김민수", "박명석",
    "박병창", "이은택", "박세익", "문홍철", "이선엽", "문남중",
]


class ScoringTests(unittest.TestCase):
    def test_weights_sum_to_one(self):
        self.assertAlmostEqual(HIT_WEIGHT + LAYER_WEIGHT + FALS_WEIGHT, 1.0)

    def test_lee_jinho_composite_is_exact(self):
        rate = hit_rate(4, 1, 1)
        self.assertEqual(rate, 0.75)
        self.assertEqual(shrink(rate, 6), 0.65)
        self.assertEqual(composite(rate, 6, 5, 4), 0.76)

    def test_kim_gwangseok_half_even(self):
        panel = next(panel for panel in PANELS if panel.name == "김광석")
        rate = hit_rate(panel.hits, panel.partials, panel.misses)
        score = composite(rate, panel.n, panel.layer1, panel.falsifiability)
        self.assertAlmostEqual(score, 0.665)
        self.assertEqual(display_points(score), 66)
        self.assertEqual(display_points(0.625), 62)

    def test_ledger_totals_and_published_rates(self):
        validate_ledger()
        report = HybridModel().run()
        self.assertEqual(len(report.panels), 29)
        hits = sum(panel.panel.hits for panel in report.panels)
        partials = sum(panel.panel.partials for panel in report.panels)
        misses = sum(panel.panel.misses for panel in report.panels)
        self.assertEqual((hits, partials, misses), (93, 24, 60))
        got = {panel.name: panel.hit_pct for panel in report.panels}
        self.assertEqual(got, PUBLISHED_HIT)
        scored = {panel.name: panel.composite_pct for panel in report.composite_board()}
        self.assertEqual(scored, PUBLISHED_SCORE)
        self.assertEqual([panel.name for panel in report.leaderboard(True)], MAIN_ORDER)
        self.assertEqual(report.leaderboard(True)[0].hit_pct, 75)
        self.assertEqual(report.leaderboard(True)[-1].name, "문남중")
        self.assertEqual(report.composite_board()[0].name, "이진호")
        self.assertEqual(len(report.leaderboard(False)), 15)

    def test_people_without_layer_scores_stay_out(self):
        report = HybridModel().run()
        names = {panel.name for panel in report.composite_board()}
        self.assertNotIn("박병창", names)
        self.assertNotIn("김장열", names)
        self.assertNotIn("문남중", names)


class ScenarioTests(unittest.TestCase):
    def test_snapshot_is_published_posterior(self):
        posterior = compute_posterior(SNAPSHOT)
        self.assertEqual(posterior.as_dict(), {"A": 50.0, "B": 20.0, "C": 30.0})
        self.assertFalse(posterior.clipped)
        core = [factor for factor in posterior.factors if factor.tier == "core"]
        self.assertEqual(len(core), 4)
        for factor in core:
            self.assertEqual(factor.intensity, 1.0)
        watch = [factor for factor in posterior.factors if factor.tier == "watch"]
        for factor in watch:
            self.assertEqual(factor.intensity, 0.0)
        self.assertEqual(dict(posterior.prior), PRIOR)

    def test_core_deltas_bridge_v10_to_v11(self):
        posterior = compute_posterior(SNAPSHOT)
        total = {"A": 0.0, "B": 0.0, "C": 0.0}
        for factor in posterior.factors:
            if factor.tier != "core":
                continue
            for code, value in factor.delta:
                total[code] += value
        self.assertEqual(total, {"A": -5.0, "B": 0.0, "C": 5.0})

    def test_neutral_market_returns_prior(self):
        quiet = replace(
            SNAPSHOT,
            us10y=5.0,
            us10y_intraday_high=5.0,
            foreign_month_tn=0.0,
            foreign_week_tn=-1.0,
            oct_hike_prob=0.40,
            micron_beat=False,
            micron_reaction_pct=0.0,
            brent=100.0,
            kospi=7000.0,
        )
        self.assertEqual(compute_posterior(quiet).as_dict(), {"A": 55.0, "B": 20.0, "C": 25.0})

    def test_partial_yield_intensity(self):
        market = replace(SNAPSHOT, us10y=5.14)
        weights = compute_posterior(market).as_dict()
        self.assertAlmostEqual(weights["A"], 51.5)
        self.assertAlmostEqual(weights["B"], 20.0)
        self.assertAlmostEqual(weights["C"], 28.5)

    def test_published_shocks(self):
        shocks = {shock.id: shock.posterior.as_dict() for shock in HybridModel().run().shocks}
        self.assertEqual(shocks["y10-490"], {"A": 53.0, "B": 25.0, "C": 22.0})
        self.assertEqual(shocks["y10-535"], {"A": 47.0, "B": 20.0, "C": 33.0})
        self.assertEqual(shocks["week-plus"], {"A": 40.0, "B": 30.0, "C": 30.0})
        self.assertEqual(shocks["core-cpi"], {"A": 35.0, "B": 20.0, "C": 45.0})
        self.assertEqual(shocks["samsung-118"], {"A": 42.0, "B": 28.0, "C": 30.0})
        self.assertEqual(shocks["weekly-7200"], {"A": 35.0, "B": 40.0, "C": 25.0})
        self.assertEqual(shocks["kospi-6500"], {"A": 40.0, "B": 15.0, "C": 45.0})
        self.assertEqual(shocks["brent-85"], {"A": 45.0, "B": 25.0, "C": 30.0})

    def test_cond2_does_not_fire_without_cond1(self):
        market = replace(SNAPSHOT, us10y=4.8, core_cpi_mom=0.4)
        factors = {factor.id: factor.intensity for factor in compute_posterior(market).factors}
        self.assertEqual(factors["euntaek_cond1"], 0.0)
        self.assertEqual(factors["euntaek_cond2"], 0.0)

    def test_cpi_at_point_two_falsifies_cond2(self):
        market = replace(SNAPSHOT, core_cpi_mom=0.2)
        factors = {factor.id: factor.intensity for factor in compute_posterior(market).factors}
        self.assertEqual(factors["euntaek_cond2"], 0.0)

    def test_clip_renormalizes(self):
        weights, clipped = normalize_weights({"A": -5.0, "B": 10.0, "C": 95.0})
        self.assertTrue(clipped)
        self.assertEqual(weights["A"], 0.0)
        self.assertAlmostEqual(sum(weights.values()), 100.0)
        self.assertAlmostEqual(weights["B"], 10 / 105 * 100)
        self.assertAlmostEqual(weights["C"], 95 / 105 * 100)

    def test_path_mids(self):
        report = HybridModel().run()
        bands = {scenario.code: [band.mid for band in scenario.paths] for scenario in report.scenarios}
        self.assertEqual(bands["A"], [6925, 7050, 7250])
        self.assertEqual(bands["B"], [7150, 7300, 7550])
        self.assertEqual(bands["C"], [6575, 6400, 6400])


class MarketTests(unittest.TestCase):
    def test_distances_match_the_writeup(self):
        spot = SNAPSHOT.kospi
        self.assertEqual(round(distance_pct(spot, 7100), 1), 1.4)
        self.assertEqual(round(distance_pct(spot, 6100), 1), -12.9)
        self.assertEqual(round(distance_pct(spot, 6050), 1), -13.6)

    def test_buyback_clocks(self):
        samsung, hynix = project_clocks()
        self.assertEqual(samsung.exhaust_date, date(2026, 10, 8))
        self.assertEqual(samsung.sessions, 3)
        self.assertEqual(samsung.published_date, date(2026, 10, 8))
        self.assertEqual(hynix.sessions, 8)
        self.assertEqual(hynix.exhaust_date, date(2026, 10, 15))
        self.assertEqual(hynix.krx_date, date(2026, 10, 16))
        self.assertEqual(hynix.published_date, date(2026, 10, 15))
        self.assertAlmostEqual(hynix.remaining_tn, 9.36)
        self.assertAlmostEqual(hynix.implied_price_won, 1.2e12 / 650_000)
        # 원장 앵커: 10/6부터 주말만 빼고 8세션이면 10/15.
        self.assertEqual(session_on(date(2026, 10, 6), 8, frozenset()), date(2026, 10, 15))
        self.assertIn(date(2026, 10, 9), KRX_HOLIDAYS)

    def test_snapshot_mentions_intraday_spike(self):
        flags = HybridModel().run().flags
        self.assertTrue(any("장중" in flag for flag in flags))


class RenderTests(unittest.TestCase):
    def test_html_carries_computed_weights(self):
        report = HybridModel().run()
        html = render_html(report)
        self.assertIn('data-a="50"', html)
        self.assertIn('data-b="20"', html)
        self.assertIn('data-c="30"', html)
        self.assertIn('data-shock="core-cpi"', html)
        self.assertIn("이진호", html)
        self.assertIn("76", html)
        self.assertIn("177", html)
        text = render_text(report)
        self.assertIn("A 50", text)
        self.assertIn("B 20", text)
        self.assertIn("C 30", text)
        self.assertIn("문남중", text)
        self.assertIn("2026-10-15", html)
        self.assertIn("2026-10-16", html)
        self.assertIn("소진 ~10/8 · ~10/15", html)
        for marker in (
            "결정적 채점",
            "잭슨홀",
            "9/16 FOMC",
            "시그니처와 채점 근거",
            "10월의 일곱 시계",
            "금리 사다리",
            "9월 수출",
            "감시 8칸",
            "방파제",
            'id="scatter"',
        ):
            self.assertIn(marker, html)
        start = html.index('id="scatter"')
        end = html.index("</svg>", start)
        self.assertEqual(html[start:end].count("<circle"), 29)

    def test_cli_json(self):
        from hybrid_model.__main__ import main
        import io
        from contextlib import redirect_stdout

        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(["--json", "--core-cpi", "0.3"])
        self.assertEqual(code, 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["posterior"], {"A": 35.0, "B": 20.0, "C": 45.0})
        self.assertEqual(payload["version"], "1.1")


if __name__ == "__main__":
    unittest.main()
