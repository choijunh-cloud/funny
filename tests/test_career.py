import numpy as np

from tonz_model import career
from tonz_model.params import ModelParams
from tonz_model.simulate import simulate
from tonz_model.units import from_eok


def test_npv_discounts():
    flat = np.ones(120) * 100.0
    pv = career.npv(flat, 0.05)
    assert pv < 120 * 100.0
    assert pv > 0.7 * 120 * 100.0


def test_zero_rate_npv_is_sum():
    flat = np.ones(12) * 10.0
    assert abs(career.npv(flat, 0.0) - 120.0) < 1e-9


def test_em_baseline_pv_matches_hand_calc():
    p = ModelParams()
    pv = career.npv(career.em_cashflows(p), p.career.discount_annual)
    # 월 3,000만 × 120개월 = 36억, 할인 후 29~32억 구간
    assert from_eok(28.0) < pv < from_eok(33.0)


def test_compare_outputs_present():
    p = ModelParams()
    res = simulate(p, n_paths=800)
    c = career.compare(res)
    for key in ("P(딜PV > EM 2인PV)", "딜_1인_시간당_중앙", "딜_2인_10년PV_중앙"):
        assert key in c
    assert 0.0 <= c["P(딜PV > EM 2인PV)"] <= 1.0
    assert c["EM_1인_시간당"] > 0


def test_hourly_normalization_uses_operating_income():
    p = ModelParams()
    res = simulate(p, n_paths=800)
    c = career.compare(res)
    implied = c["부부_세후월_영업중_중앙"] / 2.0 / p.career.deal_hours_per_month
    assert abs(implied - c["딜_1인_시간당_중앙"]) < 1e-6
    # 근무시간이 2배 이상이므로 월수령이 비슷해도 시간당은 크게 밀린다
    assert c["딜_1인_시간당_중앙"] < c["EM_1인_시간당"]


def test_fallback_income_raises_downside():
    p = ModelParams()
    res = simulate(p, n_paths=800)
    raw = career.npv(res.couple_net_monthly, p.career.discount_annual)
    with_fb = career.npv(career.income_with_fallback(res), p.career.discount_annual)
    assert (with_fb >= raw - 1e-6).all()
    assert with_fb.mean() > raw.mean()
