"""결정론적 엔진: BEP, 기간별 필요매출, 실수령 역산.

여기서 나오는 숫자는 '매출이 그 수준으로 평평하게 유지된다면' 이라는
가정 위의 값이다. 변동성·이탈·사고를 넣은 결과는 simulate.py 참조.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from . import tax
from .costs import monthly_costs
from .params import ModelParams


@dataclass(frozen=True)
class MonthlyEconomics:
    revenue: float
    couple_gross: float
    mso_receipts: float
    opex: float
    surplus: float  # MSO가 원금 상환에 쓸 수 있는 금액
    clinic_profit: float  # 매출 - 전체 OPEX (부부 선취 전)
    breakdown: dict


def economics(revenue_month: float, p: ModelParams) -> MonthlyEconomics:
    cb = monthly_costs(revenue_month, cost=p.cost, cap=p.capacity)
    opex = float(cb.total)
    if p.deal.waterfall == "gross_mso_pays_opex":
        couple_gross = p.deal.couple_share * revenue_month
        mso_receipts = (1.0 - p.deal.couple_share) * revenue_month
        surplus = mso_receipts - opex
    elif p.deal.waterfall == "profit_split":
        profit = revenue_month - opex
        couple_gross = max(profit, 0.0) * p.deal.couple_share
        mso_receipts = max(profit, 0.0) * (1.0 - p.deal.couple_share)
        surplus = mso_receipts
    else:  # pragma: no cover - 방어
        raise ValueError(f"unknown waterfall: {p.deal.waterfall}")
    return MonthlyEconomics(
        revenue=revenue_month,
        couple_gross=couple_gross,
        mso_receipts=mso_receipts,
        opex=opex,
        surplus=surplus,
        clinic_profit=revenue_month - opex,
        breakdown={
            "직원인건비": float(cb.staff),
            "봉직의보수": float(cb.doctors),
            "임대관리": float(cb.rent),
            "마케팅": float(cb.marketing),
            "기타고정": float(cb.other_fixed),
            "변동비": float(cb.variable),
        },
    )


def _solve_revenue(target_monthly_surplus: float, p: ModelParams) -> float:
    """월 상환여력이 target 이 되는 월매출을 이분법으로 찾는다."""
    lo, hi = 0.0, 5_000_000.0  # 0 ~ 500억/월
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if economics(mid, p).surplus < target_monthly_surplus:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def operating_bep(p: ModelParams) -> float:
    """운영 손익분기 월매출 (MSO 정산 기준 상환여력 0)."""
    return _solve_revenue(0.0, p)


def clinic_bep(p: ModelParams) -> float:
    """병원 자체 손익분기 (매출 = 전체 OPEX). 부부 선취 무시."""
    lo, hi = 0.0, 5_000_000.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if economics(mid, p).clinic_profit < 0.0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def required_monthly_payment(p: ModelParams, years: float) -> float:
    """years 안에 원금을 갚기 위해 필요한 월 상환액."""
    n = years * 12.0
    i = p.deal.interest_annual / 12.0
    if i <= 0:
        return p.deal.principal / n
    return p.deal.principal * i / (1.0 - (1.0 + i) ** (-n))


def required_revenue(p: ModelParams, years: float) -> float:
    """years 완제를 위한 월매출."""
    return _solve_revenue(required_monthly_payment(p, years), p)


def couple_take_home(revenue_month: float, p: ModelParams) -> dict:
    """부부 세후 실수령 (선취분 기준)."""
    eco = economics(revenue_month, p)
    gross_annual_each = eco.couple_gross * 12.0 / 2.0
    net_each = float(tax.net_income(gross_annual_each))
    return {
        "월매출": revenue_month,
        "부부_세전_월": eco.couple_gross,
        "1인_세전_월": eco.couple_gross / 2.0,
        "1인_세후_월": net_each / 12.0,
        "부부_세후_월": net_each / 12.0 * 2.0,
        "실효부담률": 1.0 - net_each / max(gross_annual_each, 1e-9),
        "매출대비_1인세후_비율": (net_each / 12.0) / max(revenue_month, 1e-9),
        "상환여력_연": eco.surplus * 12.0,
        "병원이익_연": eco.clinic_profit * 12.0,
    }


def payoff_years(revenue_month: float, p: ModelParams) -> float:
    """정적 매출 가정 하 완제 소요 연수 (무한대면 inf)."""
    surplus = economics(revenue_month, p).surplus
    if surplus <= 0:
        return float("inf")
    i = p.deal.interest_annual / 12.0
    if i <= 0:
        return p.deal.principal / surplus / 12.0
    if surplus <= p.deal.principal * i:
        return float("inf")  # 이자도 못 갚음
    n = -np.log(1.0 - p.deal.principal * i / surplus) / np.log(1.0 + i)
    return float(n) / 12.0
