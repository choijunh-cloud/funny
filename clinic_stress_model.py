#!/usr/bin/env python3
"""Transparent clinic capacity and debt-service stress model.

All money inputs and outputs are in 억 원 (KRW 100 million).
This is a planning model, not an appraisal, tax opinion, or legal opinion.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean
from typing import Iterable
import argparse
import json
import math
import random


@dataclass(frozen=True)
class Assumptions:
    # Staffing / capacity
    doctors: int = 10
    operating_days_per_month: int = 28
    patients_per_doctor_per_day: float = 25.0
    average_revenue_per_patient_won: int = 150_000

    # Annual P&L: all amounts are 억 원
    annual_fixed_cost: float = 70.0
    variable_cost_ratio: float = 0.30
    owner_draw_ratio: float = 0.10  # combined draw for both owners
    owner_effective_tax_rate: float = 0.38

    # Acquisition payment. Principal is not tax deductible.
    acquisition_balance: float = 90.0
    local_corporate_tax_surcharge: float = 0.10


def validate(a: Assumptions) -> None:
    if a.doctors <= 0 or a.operating_days_per_month <= 0:
        raise ValueError("doctors and operating_days_per_month must be positive")
    if a.patients_per_doctor_per_day < 0 or a.average_revenue_per_patient_won < 0:
        raise ValueError("patient volume and revenue per patient cannot be negative")
    for field in ("variable_cost_ratio", "owner_draw_ratio", "owner_effective_tax_rate",
                  "local_corporate_tax_surcharge"):
        value = getattr(a, field)
        if not 0 <= value < 1:
            raise ValueError(f"{field} must be between 0 and 1")
    if a.variable_cost_ratio + a.owner_draw_ratio >= 1:
        raise ValueError("variable cost plus owner draw must leave a positive contribution margin")
    if a.annual_fixed_cost < 0 or a.acquisition_balance < 0:
        raise ValueError("fixed cost and acquisition balance cannot be negative")


def monthly_revenue_from_capacity(a: Assumptions) -> float:
    """Monthly sales in 억 원 from appointments and realised revenue per appointment."""
    return (
        a.doctors
        * a.operating_days_per_month
        * a.patients_per_doctor_per_day
        * a.average_revenue_per_patient_won
        / 100_000_000
    )


def korean_corporate_income_tax(taxable_income: float, a: Assumptions) -> float:
    """Approximate Korean corporate income tax, including local income-tax surcharge.

    `taxable_income` is in 억 원. The national tax brackets used here are
    9% to 2억, 19% to 200억, 21% to 3,000억, and 24% above that. The function
    does not model losses carried forward, deductions, tax credits, or VAT.
    """
    if taxable_income <= 0:
        return 0.0
    remaining = taxable_income
    lower = 0.0
    national_tax = 0.0
    for upper, rate in ((2.0, 0.09), (200.0, 0.19), (3000.0, 0.21), (math.inf, 0.24)):
        taxable_band = min(remaining, upper - lower)
        if taxable_band <= 0:
            break
        national_tax += taxable_band * rate
        remaining -= taxable_band
        lower = upper
    return national_tax * (1 + a.local_corporate_tax_surcharge)


def annual_financials(monthly_revenue: float, a: Assumptions) -> dict[str, float]:
    """Cash waterfall assuming owners are paid before company profit tax."""
    annual_revenue = monthly_revenue * 12
    variable_cost = annual_revenue * a.variable_cost_ratio
    owner_draw_pre_tax = annual_revenue * a.owner_draw_ratio
    ebit = annual_revenue - variable_cost - owner_draw_pre_tax - a.annual_fixed_cost
    corporate_tax = korean_corporate_income_tax(ebit, a)
    debt_service_cash = ebit - corporate_tax
    combined_owner_take_home = owner_draw_pre_tax * (1 - a.owner_effective_tax_rate)

    return {
        "annual_revenue": annual_revenue,
        "variable_cost": variable_cost,
        "owner_draw_pre_tax": owner_draw_pre_tax,
        "ebit_before_corporate_tax": ebit,
        "corporate_tax": corporate_tax,
        "cash_available_for_principal": debt_service_cash,
        "combined_owner_take_home": combined_owner_take_home,
        "per_owner_monthly_take_home": combined_owner_take_home / 2 / 12,
    }


def solve_monthly_revenue_for_annual_cash(target_cash: float, a: Assumptions) -> float:
    """Find the sales required to generate target annual post-corporate-tax cash."""
    if target_cash < 0:
        raise ValueError("target cash cannot be negative")
    # The progressive tax schedule makes a closed form needlessly fragile.
    # Cash available is monotonic in sales, so a bisection search is exact
    # enough for planning and avoids incorrectly applying a marginal rate to
    # all taxable income.
    low, high = 0.0, 1.0
    while annual_financials(high, a)["cash_available_for_principal"] < target_cash:
        high *= 2
    for _ in range(80):
        midpoint = (low + high) / 2
        if annual_financials(midpoint, a)["cash_available_for_principal"] < target_cash:
            low = midpoint
        else:
            high = midpoint
    return high


def break_even_summary(a: Assumptions, terms: Iterable[int] = (6, 7, 10)) -> dict[str, float]:
    """Return operating and fully-funded repayment sales thresholds."""
    validate(a)
    result = {
        "operating_ebit_break_even_monthly_revenue": (
            a.annual_fixed_cost / (1 - a.variable_cost_ratio - a.owner_draw_ratio) / 12
        )
    }
    for years in terms:
        result[f"{years}_year_principal_repayment_monthly_revenue"] = (
            solve_monthly_revenue_for_annual_cash(a.acquisition_balance / years, a)
        )
    return result


def patients_needed(monthly_revenue: float, a: Assumptions) -> dict[str, float]:
    """Translate monthly sales target into daily clinic and doctor workload."""
    patients_per_month = monthly_revenue * 100_000_000 / a.average_revenue_per_patient_won
    per_day = patients_per_month / a.operating_days_per_month
    return {
        "patients_per_month": patients_per_month,
        "patients_per_day": per_day,
        "patients_per_doctor_per_day": per_day / a.doctors,
    }


def payoff_years(monthly_revenue: float, a: Assumptions) -> float:
    cash = annual_financials(monthly_revenue, a)["cash_available_for_principal"]
    return math.inf if cash <= 0 else a.acquisition_balance / cash


def capacity_stress_test(
    a: Assumptions,
    iterations: int = 50_000,
    seed: int = 20260817,
) -> dict[str, float]:
    """Monte Carlo sensitivity, not a statistical p-value.

    Triangular ranges deliberately must be replaced by observed monthly data:
    patient load 18/25/32 per doctor-day; realised revenue 120k/150k/180k won.
    The output reports an assumption-driven scenario frequency, not population
    inference. It cannot establish p < 0.05.
    """
    if iterations <= 0:
        raise ValueError("iterations must be positive")
    validate(a)
    rng = random.Random(seed)
    sales: list[float] = []
    payoff: list[float] = []
    for _ in range(iterations):
        daily_patients = rng.triangular(18, 32, 25)
        revenue_per_patient = rng.triangular(120_000, 180_000, 150_000)
        monthly_sales = (
            a.doctors * a.operating_days_per_month * daily_patients * revenue_per_patient / 100_000_000
        )
        sales.append(monthly_sales)
        payoff.append(payoff_years(monthly_sales, a))

    thresholds = break_even_summary(a)
    finite_payoff = [x for x in payoff if math.isfinite(x)]
    return {
        "iterations": iterations,
        "mean_monthly_revenue": mean(sales),
        "p10_monthly_revenue": percentile(sales, 10),
        "p50_monthly_revenue": percentile(sales, 50),
        "p90_monthly_revenue": percentile(sales, 90),
        "probability_operating_ebit_positive": sum(
            x >= thresholds["operating_ebit_break_even_monthly_revenue"] for x in sales
        ) / iterations,
        "probability_7_year_payoff": sum(x <= 7 for x in payoff) / iterations,
        "probability_10_year_payoff": sum(x <= 10 for x in payoff) / iterations,
        "median_payoff_years_if_cash_positive": percentile(finite_payoff, 50) if finite_payoff else math.inf,
    }


def percentile(values: list[float], p: float) -> float:
    if not values:
        return math.nan
    ordered = sorted(values)
    index = (len(ordered) - 1) * p / 100
    lower, upper = math.floor(index), math.ceil(index)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (index - lower)


def build_report(a: Assumptions) -> dict[str, object]:
    validate(a)
    current_monthly_revenue = monthly_revenue_from_capacity(a)
    return {
        "assumptions": asdict(a),
        "capacity_implied_monthly_revenue": current_monthly_revenue,
        "capacity_implied_annual_financials": annual_financials(current_monthly_revenue, a),
        "thresholds": break_even_summary(a),
        "patient_load_at_thresholds": {
            label: patients_needed(value, a)
            for label, value in break_even_summary(a).items()
        },
        "payoff_years_at_capacity": payoff_years(current_monthly_revenue, a),
        "scenario_sensitivity": capacity_stress_test(a),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--doctors", type=int, default=10)
    parser.add_argument("--days", type=int, default=28)
    parser.add_argument("--patients-per-doctor-day", type=float, default=25)
    parser.add_argument("--revenue-per-patient", type=int, default=150_000)
    parser.add_argument("--fixed-cost", type=float, default=70)
    parser.add_argument("--variable-cost-ratio", type=float, default=0.30)
    parser.add_argument("--owner-draw-ratio", type=float, default=0.10)
    parser.add_argument("--owner-tax-rate", type=float, default=0.38)
    parser.add_argument("--local-corporate-tax-surcharge", type=float, default=0.10)
    parser.add_argument("--balance", type=float, default=90)
    args = parser.parse_args()
    assumptions = Assumptions(
        doctors=args.doctors,
        operating_days_per_month=args.days,
        patients_per_doctor_per_day=args.patients_per_doctor_day,
        average_revenue_per_patient_won=args.revenue_per_patient,
        annual_fixed_cost=args.fixed_cost,
        variable_cost_ratio=args.variable_cost_ratio,
        owner_draw_ratio=args.owner_draw_ratio,
        owner_effective_tax_rate=args.owner_tax_rate,
        local_corporate_tax_surcharge=args.local_corporate_tax_surcharge,
        acquisition_balance=args.balance,
    )
    print(json.dumps(build_report(assumptions), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
