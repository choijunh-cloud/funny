"""금리·상환·가격 배수의 부호와 산술 검증."""

from __future__ import annotations

import unittest

from analysis.seoul_housing_rates.model import (
    annuity_payment,
    backtest_2022,
    distress_prob,
    evaluate,
    max_principal,
    rate_state,
    rate_that_exhausts_cap,
    sequential_contributions,
)
from analysis.seoul_housing_rates.parameters import (
    DISTRICTS,
    Assumptions,
    assumption_band,
    eight_percent_scenario,
    mortgage_cap,
    scenario_for_hikes,
)


def _district(name: str):
    return next(d for d in DISTRICTS if d.name == name)


class AnnuityTests(unittest.TestCase):
    def test_one_eok_four_percent_thirty_years(self):
        monthly = annuity_payment(100_000_000, 0.04, 30)
        self.assertGreater(monthly, 470_000)
        self.assertLess(monthly, 485_000)

    def test_roundtrip(self):
        principal = 480_000_000
        rate = 0.0571
        monthly = annuity_payment(principal, rate, 30)
        rebuilt = max_principal(monthly * 12, rate, 30)
        self.assertAlmostEqual(rebuilt, principal, delta=1.0)

    def test_higher_rate_raises_payment(self):
        low = annuity_payment(200_000_000, 0.0466, 30)
        high = annuity_payment(200_000_000, 0.08, 30)
        self.assertGreater(high, low)


class CapTests(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(mortgage_cap(1_500_000_000), 600_000_000)
        self.assertEqual(mortgage_cap(1_500_000_001), 400_000_000)
        self.assertEqual(mortgage_cap(2_500_000_000), 400_000_000)
        self.assertEqual(mortgage_cap(2_500_000_001), 200_000_000)
        self.assertEqual(mortgage_cap(_district("강남구").price_84), 200_000_000)
        self.assertEqual(mortgage_cap(_district("마포구").price_84), 400_000_000)
        self.assertEqual(mortgage_cap(_district("서울").price_84), 600_000_000)

    def test_gangnam_cap_does_not_bind_dsr_at_eight_percent(self):
        a = Assumptions()
        result = evaluate(_district("강남구"), eight_percent_scenario(a), a, band="central")
        self.assertEqual(result.new_loan_binding, "금액한도")
        self.assertEqual(result.new_loan, 200_000_000)

    def test_sub_15_eok_dsr_binds_at_eight_percent(self):
        a = Assumptions()
        mapo = _district("마포구")
        income = mapo.income_2025 * (1 + a.income_level_up) * (1.06)
        capacity = income * a.dsr_limit
        loan = max_principal(capacity, 0.08, 30)
        self.assertLess(loan, 600_000_000)
        self.assertGreater(loan, 300_000_000)


class RatePathTests(unittest.TestCase):
    def test_four_hikes_do_not_lift_the_average_to_eight(self):
        state = rate_state(4, 0.0)
        self.assertAlmostEqual(state.base, 0.04, places=10)
        self.assertAlmostEqual(state.mortgage_avg, 0.0571, places=10)
        self.assertAlmostEqual(state.mortgage_upper, 0.0819, places=10)
        self.assertLess(state.mortgage_avg, 0.065)
        self.assertGreater(state.mortgage_upper, 0.08)

    def test_eight_percent_scenario_hits_the_average(self):
        a = Assumptions()
        scenario = eight_percent_scenario(a)
        state = rate_state(scenario.hikes, scenario.extra_term_premium, a)
        self.assertAlmostEqual(state.mortgage_avg, 0.08, places=10)
        self.assertGreater(state.extra_term_premium, 0.02)
        self.assertGreater(state.mortgage_upper, state.mortgage_avg)

    def test_business_rate_is_at_least_the_upper_mortgage_rate(self):
        state = rate_state(4, 0.0)
        self.assertGreaterEqual(state.biz, state.mortgage_upper)
        self.assertGreaterEqual(state.biz, state.mortgage_avg + 0.025 - 1e-12)


class PriceTests(unittest.TestCase):
    def test_2022_backtest_is_a_low_double_digit_decline(self):
        change = backtest_2022()
        self.assertLess(change, -0.08)
        self.assertGreater(change, -0.18)

    def test_lower_yield_district_falls_more_on_the_cap_rate(self):
        a = Assumptions()
        scenario = scenario_for_hikes(4)
        gangnam = evaluate(_district("강남구"), scenario, a)
        mapo = evaluate(_district("마포구"), scenario, a)
        self.assertLess(gangnam.gross_yield, mapo.gross_yield)
        self.assertLess(gangnam.cap_ratio, mapo.cap_ratio)

    def test_more_hikes_do_not_raise_prices(self):
        a = Assumptions()
        for district in DISTRICTS:
            mild = evaluate(district, scenario_for_hikes(1), a).price_ratio
            mid = evaluate(district, scenario_for_hikes(4), a).price_ratio
            hard = evaluate(district, eight_percent_scenario(a), a).price_ratio
            self.assertGreater(mild, mid)
            self.assertGreater(mid, hard)

    def test_headline_ranges_stay_inside_sanity_bounds(self):
        a = Assumptions()
        for district in DISTRICTS:
            four = evaluate(district, scenario_for_hikes(4), a)
            shock = evaluate(district, eight_percent_scenario(a), a)
            self.assertGreater(four.price_ratio, 0.75)
            self.assertLess(four.price_ratio, 1.05)
            self.assertGreater(shock.price_ratio, 0.50)
            self.assertLess(shock.price_ratio, four.price_ratio)

    def test_mapo_lists_more_than_gangnam_when_the_average_hits_eight(self):
        a = Assumptions()
        scenario = eight_percent_scenario(a)
        gangnam = evaluate(_district("강남구"), scenario, a)
        mapo = evaluate(_district("마포구"), scenario, a)
        self.assertGreater(mapo.listing_share, gangnam.listing_share)
        self.assertGreater(mapo.forward_distress, 0.0)

    def test_channel_contributions_sum_to_the_price_change(self):
        result = evaluate(_district("송파구"), eight_percent_scenario())
        total = sum(value for _, value in sequential_contributions(result))
        self.assertAlmostEqual(total, result.price_ratio - 1.0, places=9)

    def test_zero_business_share_removes_listing_channel(self):
        a = Assumptions()
        result = evaluate(
            _district("마포구"),
            scenario_for_hikes(4),
            a,
            share_override=0.0,
        )
        self.assertEqual(result.listing_impact, 0.0)
        self.assertEqual(result.listing_share, 0.0)

    def test_distress_rises_with_dsr(self):
        a = Assumptions()
        self.assertLess(distress_prob(0.30, a), distress_prob(0.50, a))
        self.assertLess(distress_prob(0.50, a), distress_prob(0.70, a))
        self.assertGreater(distress_prob(0.30, a), 0.0)
        self.assertLess(distress_prob(0.90, a), 1.0)

    def test_bands_are_ordered(self):
        scenario = scenario_for_hikes(4)
        ratios = []
        for name in ("mild", "central", "severe"):
            assumptions, share_scale, g_scale = assumption_band(name)
            result = evaluate(
                _district("강남구"),
                scenario,
                assumptions,
                share_scale=share_scale,
                g_scale=g_scale,
                band=name,
            )
            ratios.append(result.price_ratio)
        self.assertGreater(ratios[0], ratios[1])
        self.assertGreater(ratios[1], ratios[2])


class BreakevenTests(unittest.TestCase):
    def test_two_eok_cap_stays_inside_dsr_through_twenty_percent(self):
        a = Assumptions()
        income = _district("강남구").income_2025 * (1 + a.income_level_up)
        capacity = income * 0.40
        payment = annuity_payment(200_000_000, 0.08, 30) * 12
        self.assertLess(payment, capacity * 0.4)
        found = rate_that_exhausts_cap(200_000_000, capacity, 30, hi=0.20)
        self.assertIsNone(found)


if __name__ == "__main__":
    unittest.main()
