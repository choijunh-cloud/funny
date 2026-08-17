"""월간 비용 계산. 스칼라/넘파이 배열 모두 지원.

핵심 포인트: 이 병원의 비용은 '고정 58억' 이나 '고정 70억' 같은 단일 상수가 아니다.
  - 직원 50명 인건비 = 진짜 고정비 (매출이 반토막나도 그대로 나감)
  - 봉직의 보수 = 준변동비 (최저보장 vs 인센티브 중 큰 값)
  - 마케팅 = 하한 있는 변동비
  - 재료/수수료 = 순수 변동비
이 구분이 BEP와 상환여력을 좌우한다.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np

from .params import CapacityParams, CostParams


class CostBreakdown(NamedTuple):
    staff: np.ndarray | float
    doctors: np.ndarray | float
    rent: np.ndarray | float
    marketing: np.ndarray | float
    other_fixed: np.ndarray | float
    variable: np.ndarray | float

    @property
    def total(self):
        return (
            self.staff
            + self.doctors
            + self.rent
            + self.marketing
            + self.other_fixed
            + self.variable
        )


def employed_production_share(
    n_employed: np.ndarray | float, cap: CapacityParams
) -> np.ndarray | float:
    """전체 진료매출 중 봉직의(부부 제외)가 만들어내는 비중."""
    emp_days = np.asarray(n_employed, dtype=float) * cap.employed_days_per_month
    couple_days = cap.couple_doctors * cap.couple_days_per_month
    total = emp_days + couple_days
    return np.where(total > 0, emp_days / np.maximum(total, 1e-9), 0.0)


def monthly_costs(
    revenue: np.ndarray | float,
    *,
    cost: CostParams,
    cap: CapacityParams,
    n_employed_doctors: np.ndarray | float | None = None,
    staff_headcount: np.ndarray | float | None = None,
    wage_index: np.ndarray | float = 1.0,
    rent_index: np.ndarray | float = 1.0,
) -> CostBreakdown:
    """월 비용 항목별 산출 (만원)."""
    rev = np.asarray(revenue, dtype=float)
    n_emp = (
        cap.employed_doctors if n_employed_doctors is None else np.asarray(n_employed_doctors, float)
    )
    heads = cost.staff_headcount if staff_headcount is None else np.asarray(staff_headcount, float)

    staff = heads * cost.staff_avg_monthly_pay * cost.staff_burden_multiple * wage_index

    share = employed_production_share(n_emp, cap)
    production_per_doctor = np.where(
        np.asarray(n_emp, float) > 0, rev * share / np.maximum(np.asarray(n_emp, float), 1e-9), 0.0
    )
    guarantee = cost.doctor_net_guarantee * cost.doctor_gross_up * wage_index
    per_doctor_cost = np.maximum(guarantee, cost.doctor_incentive_rate * production_per_doctor)
    doctors = per_doctor_cost * np.asarray(n_emp, float)

    rent = cost.rent_annual / 12.0 * rent_index
    marketing = np.maximum(cost.marketing_floor_annual / 12.0, cost.marketing_rate * rev)
    other = cost.other_fixed_annual / 12.0 * rent_index
    variable = cost.variable_rate * rev

    return CostBreakdown(
        staff=staff,
        doctors=doctors,
        rent=rent * np.ones_like(rev),
        marketing=marketing,
        other_fixed=other * np.ones_like(rev),
        variable=variable,
    )


def fixed_cost_annual(cost: CostParams, cap: CapacityParams) -> float:
    """'고정비 몇 억' 논쟁을 정리하기 위한 참고치.

    봉직의는 최저보장이 걸리는 구간(=저매출 구간)에서만 고정비로 본다.
    """
    doctors = (
        cap.employed_doctors * cost.doctor_net_guarantee * cost.doctor_gross_up * 12.0
    )
    return (
        cost.staff_annual
        + doctors
        + cost.rent_annual
        + cost.other_fixed_annual
        + cost.marketing_floor_annual
    )
