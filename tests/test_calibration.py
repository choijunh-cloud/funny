import math

from tonz_model import calibration
from tonz_model.params import DemandParams
from tonz_model.units import from_eok


def test_prior_reproduces_anchors():
    prior = calibration.fit_revenue_prior()
    assert abs(prior.median_monthly * 12 - from_eok(110.0)) < 1.0
    # p15 / p85 가 결제하한·자기신고 앵커를 ±3% 안에서 재현
    lo = prior.quantile(0.15) * 12
    hi = prior.quantile(0.85) * 12
    assert abs(lo / from_eok(82.0) - 1.0) < 0.03
    assert abs(hi / from_eok(145.0) - 1.0) < 0.03


def test_implied_demand_matches_default_params():
    d = calibration.implied_demand(ticket_median=14.0)
    defaults = DemandParams()
    assert abs(d["patients_median_monthly"] - defaults.monthly_patients_median) < 5.0
    assert abs(d["demand_sigma"] - defaults.sigma) < 0.01


def test_variance_decomposition_is_consistent():
    d = calibration.implied_demand()
    total = math.sqrt(d["demand_sigma"] ** 2 + d["ticket_sigma"] ** 2)
    assert abs(total - d["revenue_sigma"]) < 1e-9
