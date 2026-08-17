import numpy as np
import pytest

from tonz_model.params import ModelParams, replace_nested
from tonz_model.simulate import simulate, summarize

N = 1_500


@pytest.fixture(scope="module")
def base():
    p = ModelParams()
    return p, simulate(p, n_paths=N)


def test_reproducible(base):
    p, res = base
    again = simulate(p, n_paths=N)
    assert np.array_equal(res.payoff_month, again.payoff_month)
    assert np.allclose(res.revenue, again.revenue)


def test_no_nans_and_nonnegative(base):
    _, res = base
    assert np.isfinite(res.revenue).all()
    assert (res.revenue >= 0).all()
    assert np.isfinite(res.couple_net_monthly).all()
    assert (res.couple_net_monthly >= -1e-9).all()


def test_initial_revenue_brackets_audit_anchors(base):
    """1년차 매출 분포가 실사 앵커(연 82/110/145억)를 감싸야 한다."""
    _, res = base
    y1 = res.revenue[:, :12].sum(axis=1)
    p15, p50, p85 = np.quantile(y1, [0.15, 0.5, 0.85])
    # 인수 첫해는 램프(0.88)가 걸리므로 앵커보다 낮게 나오는 게 정상
    assert 60_0000 * 0.9 < p15 < 90_0000
    assert 80_0000 < p50 < 115_0000
    assert 110_0000 < p85 < 160_0000


def test_more_demand_raises_payoff_probability():
    lo = summarize(simulate(replace_nested(ModelParams(), "demand.monthly_patients_median", 5_500.0), n_paths=N))
    hi = summarize(simulate(replace_nested(ModelParams(), "demand.monthly_patients_median", 8_500.0), n_paths=N))
    assert hi["P(10년내 완제)"] > lo["P(10년내 완제)"]


def test_lower_couple_share_speeds_payoff_but_cuts_income():
    p_lo = replace_nested(ModelParams(), "deal.couple_share", 0.05)
    a = summarize(simulate(ModelParams(), n_paths=N))
    b = summarize(simulate(p_lo, n_paths=N))
    assert b["P(10년내 완제)"] > a["P(10년내 완제)"]
    assert b["부부세후월_1~5년_중앙"] < a["부부세후월_1~5년_중앙"]


def test_interest_reduces_payoff_probability():
    p6 = replace_nested(ModelParams(), "deal.interest_annual", 0.06)
    a = summarize(simulate(ModelParams(), n_paths=N))
    b = summarize(simulate(p6, n_paths=N))
    assert b["P(10년내 완제)"] <= a["P(10년내 완제)"]


def test_clinic_bears_deficit_hurts_couple_income():
    p = replace_nested(ModelParams(), "deal.deficit_bearer", "clinic")
    a = summarize(simulate(ModelParams(), n_paths=N))
    b = summarize(simulate(p, n_paths=N))
    assert b["부부세후월_1~5년_중앙"] < a["부부세후월_1~5년_중앙"]
    assert b["개인추가부담_기대값"] > a["개인추가부담_기대값"]


def test_balance_never_negative(base):
    _, res = base
    assert (res.balance_end >= -1e-6).all()


def test_payoff_implies_zero_balance(base):
    _, res = base
    paid = res.payoff_month >= 0
    if paid.any():
        assert np.all(res.balance_end[paid] < 1e-6)


def test_capacity_ceiling_binds_on_upside():
    """수요를 크게 올려도 매출은 시설 한계에서 멈춘다."""
    p = replace_nested(ModelParams(), "demand.monthly_patients_median", 20_000.0)
    res = simulate(p, n_paths=300)
    from tonz_model.capacity import profile

    ceiling = profile(p.capacity).max_patients_month
    implied_patients = res.revenue[:, 24] / np.quantile([14.0], 0.5)
    assert np.median(implied_patients) <= ceiling * 1.35  # 객단가 분산 감안
