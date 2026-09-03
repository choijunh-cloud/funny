"""Lock the fused H2 KOSPI Top 10 (broadcast × value × probability)."""

from __future__ import annotations

import unittest

from hybrid_synthesis.model import evaluate
from hybrid_synthesis.portfolio import build_portfolio
from hybrid_synthesis.ranking import (
    BANNED_TICKERS,
    H2_P_BASE,
    H2_P_EASE,
    H2_P_HARD,
    SNAPSHOTS,
    YEAR_END_GAP,
    rank_h2,
)
from hybrid_synthesis.universe import by_ticker


KOSDAQ_AND_BANNED = {"222800", "356860", "003160", "028050", "042700"}


class RankingHygieneTests(unittest.TestCase):
    def test_every_snapshot_resolves_in_the_kospi_universe(self) -> None:
        for card in SNAPSHOTS:
            stock = by_ticker(card.ticker)
            self.assertEqual(stock.market, "KOSPI")
            self.assertEqual(stock.ticker, card.ticker)

    def test_banned_set_covers_kosdaq_and_faded_names(self) -> None:
        self.assertTrue(KOSDAQ_AND_BANNED <= set(BANNED_TICKERS))


class ProbabilityWeightedOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.snap = evaluate()
        cls.book = build_portfolio(cls.snap)
        cls.ranking = rank_h2(cls.snap, cls.book)
        cls.top10 = cls.ranking["top10"]
        cls.tickers = [row["ticker"] for row in cls.top10]
        cls.by_ticker = {row["ticker"]: row for row in cls.ranking["all_pw"]}

    def test_official_top10_order(self) -> None:
        self.assertEqual(
            self.tickers,
            [
                "000660",  # SK하이닉스
                "402340",  # SK스퀘어
                "071050",  # 한국금융지주
                "005930",  # 삼성전자
                "015760",  # 한국전력
                "035420",  # NAVER
                "005935",  # 삼성전자우
                "034020",  # 두산에너빌리티 — 완화 4위, PW는 왼쪽 꼬리로 8위
                "012330",  # 현대모비스
                "003490",  # 대한항공
            ],
        )

    def test_hynix_is_absolute_upside_number_one(self) -> None:
        hynix = self.top10[0]
        self.assertEqual(hynix["ticker"], "000660")
        self.assertAlmostEqual(hynix["fair_value"], 2_300_000, places=0)
        self.assertAlmostEqual(hynix["yearend_target"], 2_053_600, places=0)
        self.assertGreater(hynix["pw_return"], 0.20)

    def test_pw_identity_on_hynix(self) -> None:
        card = next(item for item in SNAPSHOTS if item.ticker == "000660")
        expected = (
            H2_P_EASE * card.ease_return
            + H2_P_BASE * card.base_return
            + H2_P_HARD * card.hard_return
        )
        self.assertAlmostEqual(card.pw_return, expected, places=12)
        self.assertAlmostEqual(
            card.yearend_target,
            card.spot + YEAR_END_GAP * (card.fair_value - card.spot),
            places=6,
        )

    def test_samsung_outranks_doosan_on_probability_weight(self) -> None:
        samsung = self.by_ticker["005930"]
        doosan = self.by_ticker["034020"]
        self.assertLess(samsung["rank"], doosan["rank"])
        self.assertGreater(samsung["pw_return"], doosan["pw_return"])
        self.assertEqual(doosan["rank"], 8)
        self.assertGreater(doosan["ease_return"], 0.25)

    def test_kosdaq_ena_hanmi_stay_out(self) -> None:
        self.assertTrue(KOSDAQ_AND_BANNED.isdisjoint(self.tickers))
        dropped = {row["ticker"] for row in self.ranking["dropped"]}
        self.assertTrue(KOSDAQ_AND_BANNED <= dropped)

    def test_new_money_leads_with_brokerage_not_more_semis(self) -> None:
        new_money = [row["ticker"] for row in self.ranking["new_money_order"][:5]]
        self.assertEqual(new_money[0], "071050")
        self.assertEqual(self.ranking["boxed_new_money"][0], "한국금융지주")
        # Already-owned Hynix / Samsung fall out of the first five.
        self.assertNotIn("000660", new_money)
        self.assertNotIn("005930", new_money)

    def test_sk_square_is_same_semi_factor(self) -> None:
        square = self.by_ticker["402340"]
        self.assertEqual(square["cluster"], "SEMI")
        self.assertEqual(square["rank"], 2)
        new_ranks = {row["ticker"]: row["rank"] for row in self.ranking["new_money_order"]}
        self.assertGreater(new_ranks["402340"], 5)

    def test_boxed_upside_uses_korean_names(self) -> None:
        self.assertEqual(
            self.ranking["boxed_upside"],
            ["SK하이닉스", "SK스퀘어", "한국금융지주", "삼성전자", "한국전력"],
        )

    def test_ranking_does_not_rewrite_the_phase1_book(self) -> None:
        held = [item.ticker for item in self.book.holdings]
        self.assertEqual(
            held,
            [
                "005930",
                "000660",
                "009150",
                "042700",
                "007660",
                "353200",
                "007810",
                "034020",
                "105560",
                "015760",
                "055550",
                "003490",
                "161890",
                "192820",
            ],
        )
        self.assertAlmostEqual(self.book.holdings_weight_sum() + self.book.cash_bond_weight, 1.0, places=4)


if __name__ == "__main__":
    unittest.main()
