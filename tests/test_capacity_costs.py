import numpy as np

from tonz_model import capacity
from tonz_model.costs import monthly_costs
from tonz_model.params import CapacityParams, CostParams, ModelParams
from tonz_model.units import from_eok


def test_binding_constraint_identified():
    cap = CapacityParams()
    prof = capacity.profile(cap)
    assert prof.max_patients_day == min(
        prof.doctor_limited_patients_day,
        prof.room_limited_patients_day,
        prof.staff_limited_patients_day,
    )
    assert prof.binding_constraint in {"의사", "시술실", "시술인력"}


def test_patients_needed_inverts_revenue():
    cap = CapacityParams()
    need = capacity.patients_needed(from_eok(10.0), 14.0, cap)
    implied_revenue = need["월_환자수"] * 14.0
    assert abs(implied_revenue - from_eok(10.0)) < 1.0


def test_infeasible_flagged_for_extreme_target():
    cap = CapacityParams()
    need = capacity.patients_needed(from_eok(30.0), 10.0, cap)
    assert not need["물리적_실현가능"]


def test_doctor_comp_switches_from_guarantee_to_incentive():
    cost, cap = CostParams(), CapacityParams()
    low = monthly_costs(from_eok(5.0), cost=cost, cap=cap).doctors
    high = monthly_costs(from_eok(20.0), cost=cost, cap=cap).doctors
    guarantee_total = (
        cap.employed_doctors * cost.doctor_net_guarantee * cost.doctor_gross_up
    )
    assert float(low) == guarantee_total  # 저매출: 최저보장이 구속
    assert float(high) > guarantee_total  # 고매출: 인센티브가 구속


def test_staff_cost_scales_with_headcount():
    cost, cap = CostParams(), CapacityParams()
    a = monthly_costs(from_eok(9.0), cost=cost, cap=cap, staff_headcount=50).staff
    b = monthly_costs(from_eok(9.0), cost=cost, cap=cap, staff_headcount=25).staff
    assert float(a) == 2 * float(b)


def test_costs_are_vectorized():
    cost, cap = CostParams(), CapacityParams()
    rev = np.array([from_eok(5.0), from_eok(10.0), from_eok(15.0)])
    cb = monthly_costs(rev, cost=cost, cap=cap)
    assert cb.total.shape == rev.shape
    assert np.all(np.diff(cb.total) > 0)


def test_fifty_staff_fixed_cost_in_expected_range():
    p = ModelParams()
    from tonz_model.costs import fixed_cost_annual

    fixed = fixed_cost_annual(p.cost, p.capacity)
    # 직원 50명 + 봉직의 최저보장 + 임대 + 기타 → 연 60~75억 사이여야 한다
    assert from_eok(60.0) < fixed < from_eok(75.0)
