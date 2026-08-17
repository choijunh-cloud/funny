"""정적 손익·BEP·엑시트 엔진. 단위 억(연/월), 실수령은 만원/월."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from tones_model.params import ModelParams
from tones_model.tax_kr import couple_from_monthly_revenue_eok


@dataclass
class StaticResult:
    monthly_eok: float
    annual_eok: float
    variable_eok: float
    fixed_eok: float
    couple_gross_eok: float
    mso_inflow_eok: float
    repay_eok: float
    exit_years: float
    person_verified_man: float
    couple_verified_man: float
    person_tax_man: float
    couple_tax_man: float
    person_takehome_man: float
    couple_takehome_man: float
    effective_tax: float
    operating_ok: bool
    exit_6: bool
    exit_7: bool
    exit_10: bool


class ClinicEngine:
    def __init__(self, p: ModelParams | None = None):
        self.p = p or ModelParams()

    def repay(self, monthly_eok: float, fixed: float | None = None) -> float:
        fixed = self.p.fixed_cost_eok if fixed is None else fixed
        return self.p.mso_net_rate * monthly_eok * 12 - fixed

    def required_monthly(self, years: float, fixed: float | None = None) -> float:
        fixed = self.p.fixed_cost_eok if fixed is None else fixed
        if years <= 0:
            return float("inf")
        return (self.p.debt_eok / years + fixed) / self.p.mso_net_rate / 12

    def operating_bep(self, fixed: float | None = None) -> float:
        fixed = self.p.fixed_cost_eok if fixed is None else fixed
        return fixed / self.p.mso_net_rate / 12

    def analyze(self, monthly_eok: float, fixed: float | None = None) -> StaticResult:
        p = self.p
        fixed = p.fixed_cost_eok if fixed is None else fixed
        annual = monthly_eok * 12
        repay = self.repay(monthly_eok, fixed)
        exit_y = p.debt_eok / repay if repay > 0 else float("inf")
        tax = couple_from_monthly_revenue_eok(monthly_eok, p.couple_share)
        return StaticResult(
            monthly_eok=round(monthly_eok, 3),
            annual_eok=round(annual, 2),
            variable_eok=round(annual * p.variable_rate, 2),
            fixed_eok=round(fixed, 2),
            couple_gross_eok=round(annual * p.couple_share, 2),
            mso_inflow_eok=round(annual * p.mso_share, 2),
            repay_eok=round(repay, 2),
            exit_years=round(exit_y, 2) if exit_y != float("inf") else 999.0,
            person_verified_man=tax["검증식_1인월_만"],
            couple_verified_man=tax["검증식_부부월_만"],
            person_tax_man=tax["1인_세후월_만"],
            couple_tax_man=tax["부부_세후월_만"],
            person_takehome_man=tax["1인_실수령월_만"],
            couple_takehome_man=tax["부부_실수령월_만"],
            effective_tax=tax["1인_소득세실효"],
            operating_ok=repay > 0,
            exit_6=monthly_eok + 1e-9 >= self.required_monthly(6, fixed),
            exit_7=monthly_eok + 1e-9 >= self.required_monthly(7, fixed),
            exit_10=monthly_eok + 1e-9 >= self.required_monthly(10, fixed),
        )

    def bep_table(self) -> Dict[str, Dict[str, float]]:
        out = {}
        for label, years in [("운영_손익분기", None), ("10년_완제", 10), ("7년_완제", 7), ("6년_완제", 6)]:
            for case, fixed in [
                ("lean", self.p.fixed_lean_eok),
                ("base", self.p.fixed_cost_eok),
                ("heavy", self.p.fixed_heavy_eok),
            ]:
                m = self.operating_bep(fixed) if years is None else self.required_monthly(years, fixed)
                key = f"{label}_{case}"
                out[key] = {
                    "월매출_억": round(m, 3),
                    "연매출_억": round(m * 12, 1),
                    "고정비_억": fixed,
                }
        return out

    def revenue_grid(self, values: List[float] | None = None) -> List[StaticResult]:
        if values is None:
            values = [
                5.0, 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.3,
                9.7, 10.0, 10.5, 11.0, 11.5, 11.8, 12.0, 12.5, 13.0, 14.0,
            ]
        return [self.analyze(v) for v in values]

    def interest_total_paid(self, monthly_eok: float, rate: float, years: int = 10) -> Dict:
        """원리금 체감: 매년 상환여력에서 이자를 먼저 떼고 원금 차감."""
        remaining = self.p.debt_eok
        paid_interest = 0.0
        paid_principal = 0.0
        repay = self.repay(monthly_eok)
        for y in range(1, years + 1):
            if remaining <= 0:
                return {
                    "완제년": y - 1,
                    "총이자": round(paid_interest, 2),
                    "총원금": round(paid_principal, 2),
                    "잔액": 0.0,
                }
            interest = remaining * rate
            paid_interest += interest
            remaining += interest
            principal = max(0.0, repay)
            take = min(principal, remaining)
            remaining -= take
            paid_principal += take
        return {
            "완제년": None if remaining > 1e-6 else years,
            "총이자": round(paid_interest, 2),
            "총원금": round(paid_principal, 2),
            "잔액": round(max(0.0, remaining), 2),
        }
