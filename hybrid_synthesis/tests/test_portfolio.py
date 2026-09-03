"""KOSPI-only book: sleeves, exclusions, and weight identity."""

from __future__ import annotations

import unittest

from hybrid_synthesis.model import Scenario, evaluate, evaluate_all_scenarios, scenario_inputs
from hybrid_synthesis.portfolio import CORE_FIXED_SPLIT, SLEEVE_ORDER, build_portfolio, largest_remainder
from hybrid_synthesis.universe import KOSPI_UNIVERSE, NON_KOSPI_EXCLUSIONS, kospi_investable


class UniverseHygieneTests(unittest.TestCase):
    def test_default_universe_is_kospi(self) -> None:
        self.assertTrue(KOSPI_UNIVERSE)
        self.assertTrue(all(stock.market == "KOSPI" for stock in KOSPI_UNIVERSE))
        self.assertTrue(all(stock.ticker.isdigit() and len(stock.ticker) == 6 for stock in KOSPI_UNIVERSE))

    def test_named_kosdaq_names_are_excluded(self) -> None:
        excluded = {row["ticker"] for row in NON_KOSPI_EXCLUSIONS}
        self.assertGreaterEqual(
            excluded,
            {"222800", "356860", "003160", "066970", "277810", "454910"},
        )
        investable = {stock.ticker for stock in kospi_investable()}
        self.assertTrue(excluded.isdisjoint(investable))

    def test_avoid_flags_on_battery_and_faded_construction(self) -> None:
        flags = {stock.ticker: stock.avoid_flags for stock in KOSPI_UNIVERSE}
        self.assertIn("battery_high_pbr", flags["373220"])
        self.assertIn("battery_high_pbr", flags["006400"])
        self.assertIn("battery_high_pbr", flags["003670"])
        self.assertIn("faded_theme", flags["028050"])


class PortfolioConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.portfolio = build_portfolio(evaluate())
        cls.tickers = [item.ticker for item in cls.portfolio.holdings]

    def test_weights_sum_to_one(self) -> None:
        self.assertAlmostEqual(self.portfolio.holdings_weight_sum(), 0.60, places=4)
        self.assertAlmostEqual(self.portfolio.cash_bond_weight, 0.40, places=12)
        self.assertAlmostEqual(
            self.portfolio.holdings_weight_sum() + self.portfolio.cash_bond_weight,
            1.0,
            places=4,
        )

    def test_core_is_samsung_and_hynix_only(self) -> None:
        core = [item for item in self.portfolio.holdings if item.sleeve == "CORE_SEMI"]
        self.assertEqual({item.ticker for item in core}, set(CORE_FIXED_SPLIT))
        weights = {item.ticker: item.weight_total for item in core}
        self.assertAlmostEqual(weights["005930"], 0.165, places=4)
        self.assertAlmostEqual(weights["000660"], 0.135, places=4)

    def test_connect_sleeve_is_kospi_substitutes(self) -> None:
        connect = [item.ticker for item in self.portfolio.holdings if item.sleeve == "AI_CONNECT"]
        self.assertEqual(
            connect,
            ["009150", "042700", "007660", "353200", "007810"],
        )
        held = set(self.tickers)
        self.assertTrue(held.isdisjoint({"222800", "356860", "003160"}))

    def test_hedge_and_cosmetics(self) -> None:
        hedge = [item.ticker for item in self.portfolio.holdings if item.sleeve == "MACRO_HEDGE"]
        cos = [item.ticker for item in self.portfolio.holdings if item.sleeve == "COSMETICS"]
        self.assertEqual(hedge, ["034020", "105560", "015760", "055550", "003490"])
        self.assertEqual(cos, ["161890", "192820"])

    def test_avoids_never_enter(self) -> None:
        avoid = {item.ticker for item in self.portfolio.avoid}
        self.assertTrue(avoid.isdisjoint(self.tickers))
        self.assertGreaterEqual(avoid, {"373220", "006400", "003670", "028050"})

    def test_watch_names_stay_on_the_bench(self) -> None:
        self.assertNotIn("005935", self.tickers)
        self.assertNotIn("402340", self.tickers)
        self.assertNotIn("090430", self.tickers)
        self.assertNotIn("051900", self.tickers)
        # Ranking overlay names. They must not rewrite the Phase 1 60/40 book.
        self.assertNotIn("071050", self.tickers)
        self.assertNotIn("035420", self.tickers)
        self.assertNotIn("012330", self.tickers)
        self.assertNotIn("028260", self.tickers)
        self.assertNotIn("278470", self.tickers)
        self.assertNotIn("079550", self.tickers)

    def test_all_holdings_are_kospi_universe_members(self) -> None:
        kospi = {stock.ticker for stock in KOSPI_UNIVERSE}
        self.assertTrue(set(self.tickers) <= kospi)
        self.assertEqual(len(self.tickers), len(set(self.tickers)))

    def test_sleeve_order_and_counts(self) -> None:
        self.assertEqual(SLEEVE_ORDER, ("CORE_SEMI", "AI_CONNECT", "MACRO_HEDGE", "COSMETICS"))
        counts = {sleeve: 0 for sleeve in SLEEVE_ORDER}
        for item in self.portfolio.holdings:
            counts[item.sleeve] += 1
        self.assertEqual(counts, {"CORE_SEMI": 2, "AI_CONNECT": 5, "MACRO_HEDGE": 5, "COSMETICS": 2})

    def test_hard_landing_book_stays_kospi_and_more_cash(self) -> None:
        book = build_portfolio(evaluate(scenario_inputs(Scenario.HARD_LANDING), scenario=Scenario.HARD_LANDING))
        self.assertAlmostEqual(book.snapshot.equity_weight, 0.45, places=12)
        self.assertAlmostEqual(book.holdings_weight_sum() + book.cash_bond_weight, 1.0, places=4)
        self.assertTrue({item.ticker for item in book.holdings} <= {s.ticker for s in KOSPI_UNIVERSE})

    def test_phase_three_overweights_connectivity(self) -> None:
        all_snaps = evaluate_all_scenarios()
        phase3 = build_portfolio(all_snaps["fcf_inflection"])
        sleeves = phase3.snapshot.sleeves
        self.assertGreater(sleeves["AI_CONNECT"], sleeves["MACRO_HEDGE"])
        self.assertGreater(sleeves["AI_CONNECT"], 0.30)
        self.assertIn("009150", [item.ticker for item in phase3.holdings])

    def test_largest_remainder_identity(self) -> None:
        parts = largest_remainder((0.3333, 0.3333, 0.3334), total=1.0, ndigits=4)
        self.assertAlmostEqual(sum(parts), 1.0, places=4)
        self.assertTrue(all(part >= 0.0 for part in parts))


if __name__ == "__main__":
    unittest.main()
