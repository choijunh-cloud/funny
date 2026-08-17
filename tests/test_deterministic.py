import dataclasses

import pytest

from tonz_model import deterministic as det
from tonz_model.params import ModelParams
from tonz_model.units import from_eok


@pytest.fixture
def p():
    return ModelParams()


def test_surplus_is_zero_at_operating_bep(p):
    bep = det.operating_bep(p)
    assert abs(det.economics(bep, p).surplus) < 1.0  # 1만원 오차


def test_clinic_bep_below_operating_bep(p):
    # 부부 10% 선취가 있기 때문에 MSO 기준 손익분기가 더 높다
    assert det.clinic_bep(p) < det.operating_bep(p)


def test_required_revenue_round_trips_to_payoff_years(p):
    for years in (6, 7, 10):
        rev = det.required_revenue(p, years)
        assert abs(det.payoff_years(rev, p) - years) < 0.05


def test_required_revenue_monotone_in_horizon(p):
    r6, r7, r10 = (det.required_revenue(p, y) for y in (6, 7, 10))
    assert r6 > r7 > r10 > det.operating_bep(p)


def test_interest_raises_required_revenue(p):
    p6 = dataclasses.replace(p, deal=dataclasses.replace(p.deal, interest_annual=0.06))
    assert det.required_revenue(p6, 7) > det.required_revenue(p, 7)


def test_cost_components_sum_to_opex(p):
    eco = det.economics(from_eok(10.0), p)
    assert abs(sum(eco.breakdown.values()) - eco.opex) < 1e-6


def test_take_home_effective_rate_reasonable(p):
    th = det.couple_take_home(from_eok(9.0), p)
    assert 0.40 < th["실효부담률"] < 0.55
    assert th["부부_세후_월"] == pytest.approx(th["1인_세후_월"] * 2)


def test_payoff_impossible_below_bep(p):
    assert det.payoff_years(det.operating_bep(p) * 0.9, p) == float("inf")


def _marginal(p, a, b):
    lo = det.economics(from_eok(a), p).surplus
    hi = det.economics(from_eok(b), p).surplus
    return (hi - lo) / from_eok(b - a)


def test_marginal_repayment_capacity_has_two_regimes(p):
    """'매출 90%가 상환에 쓰인다'는 착시다.

    최저보장이 구속되는 저매출 구간에서도 한계 기여는 약 57%,
    인센티브가 구속되는 고매출 구간에서는 약 34%로 더 떨어진다.
    """
    low_regime = _marginal(p, 8.0, 9.0)
    high_regime = _marginal(p, 12.0, 13.0)
    assert 0.50 < low_regime < 0.62
    assert 0.28 < high_regime < 0.40
    assert high_regime < low_regime
