#!/usr/bin/env python3
"""Auditable Monte Carlo model for a high-volume aesthetic clinic.

All currency values are KRW. The model deliberately separates physical
throughput, payroll, variable costs, owner distributions, and debt repayment
so the same expense cannot be counted twice.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import NormalDist
from typing import Iterable


BILLION = 1_000_000_000
EOK = 100_000_000
MILLION = 1_000_000


@dataclass(frozen=True)
class Triangular:
    low: float
    mode: float
    high: float

    def draw(self, rng: random.Random) -> float:
        return rng.triangular(self.low, self.high, self.mode)

    def inverse(self, probability: float) -> float:
        probability = min(max(probability, 0.0), 1.0)
        width = self.high - self.low
        split = (self.mode - self.low) / width
        if probability <= split:
            return self.low + math.sqrt(
                probability * width * (self.mode - self.low)
            )
        return self.high - math.sqrt(
            (1.0 - probability) * width * (self.high - self.mode)
        )


@dataclass(frozen=True)
class Assumptions:
    simulations: int = 200_000
    seed: int = 20260817
    debt_krw: float = 9.0 * BILLION
    owner_revenue_share: float = 0.10
    owner_count: int = 2
    nonphysician_staff: int = 50
    owner_days_per_month: float = 28.0
    total_physicians: Triangular = Triangular(8, 10, 12)
    employed_physician_days: Triangular = Triangular(18, 22, 25)
    patients_per_doctor_day: Triangular = Triangular(20, 30, 42)
    realized_revenue_per_visit: Triangular = Triangular(
        110_000, 145_000, 190_000
    )
    # Employer cash cost, not advertised net pay.
    employed_physician_monthly_cost: Triangular = Triangular(
        22 * MILLION, 28 * MILLION, 36 * MILLION
    )
    staff_monthly_gross_pay: Triangular = Triangular(
        2.8 * MILLION, 3.4 * MILLION, 4.1 * MILLION
    )
    staff_employer_load: Triangular = Triangular(0.15, 0.19, 0.24)
    annual_rent_and_management: Triangular = Triangular(
        0.32 * BILLION, 0.48 * BILLION, 0.70 * BILLION
    )
    annual_other_fixed_cost: Triangular = Triangular(
        0.40 * BILLION, 0.70 * BILLION, 1.20 * BILLION
    )
    # Materials, card fees, and performance marketing combined.
    variable_cost_rate: Triangular = Triangular(0.25, 0.30, 0.36)
    patient_ticket_correlation: float = -0.35


@dataclass
class Trial:
    monthly_revenue: float
    daily_patients: float
    total_physicians: int
    doctor_days_per_month: float
    fixed_cost_annual: float
    variable_cost_rate: float
    annual_repayment_cash: float
    annual_repayment_cash_after_corporate_tax: float
    operating_bep_monthly_revenue: float
    years_to_repay: float
    years_to_repay_after_corporate_tax: float
    owner_monthly_net_each: float
    owner_monthly_net_couple: float


def korean_income_tax(gross_income: float) -> float:
    """Approximate Korean comprehensive income tax plus 10% local tax.

    This treats each owner's 5% distribution as taxable income with no
    deductions or other income. National Health Insurance and pension are not
    included because their treatment depends on the actual legal structure.
    """

    brackets = (
        (14 * MILLION, 0.06, 0),
        (50 * MILLION, 0.15, 1.26 * MILLION),
        (88 * MILLION, 0.24, 5.76 * MILLION),
        (150 * MILLION, 0.35, 15.44 * MILLION),
        (300 * MILLION, 0.38, 19.94 * MILLION),
        (500 * MILLION, 0.40, 25.94 * MILLION),
        (1_000 * MILLION, 0.42, 35.94 * MILLION),
        (math.inf, 0.45, 65.94 * MILLION),
    )
    for ceiling, rate, deduction in brackets:
        if gross_income <= ceiling:
            national = max(0.0, gross_income * rate - deduction)
            return national * 1.10
    raise AssertionError("unreachable")


def korean_corporate_tax_2026(tax_base: float) -> float:
    """2026 corporate income tax plus 10% local corporate income tax.

    Acquisition-price amortization, loss carryforwards, tax credits, and other
    adjustments are intentionally excluded. This is therefore a conservative
    tax scenario when acquired goodwill or equipment is tax-depreciable.
    """

    if tax_base <= 0:
        return 0.0
    brackets = (
        (200 * MILLION, 0.10, 0),
        (20 * BILLION, 0.20, 20 * MILLION),
        (300 * BILLION, 0.22, 420 * MILLION),
        (math.inf, 0.25, 9.42 * BILLION),
    )
    for ceiling, rate, deduction in brackets:
        if tax_base <= ceiling:
            national = max(0.0, tax_base * rate - deduction)
            return national * 1.10
    raise AssertionError("unreachable")


def correlated_triangular_pair(
    rng: random.Random,
    first: Triangular,
    second: Triangular,
    correlation: float,
) -> tuple[float, float]:
    """Draw triangular marginals with a Gaussian copula."""

    z1 = rng.gauss(0.0, 1.0)
    z2 = correlation * z1 + math.sqrt(1.0 - correlation**2) * rng.gauss(0.0, 1.0)
    normal = NormalDist()
    return first.inverse(normal.cdf(z1)), second.inverse(normal.cdf(z2))


def run_trial(rng: random.Random, a: Assumptions) -> Trial:
    total_physicians = max(
        a.owner_count, round(a.total_physicians.draw(rng))
    )
    employed_physicians = total_physicians - a.owner_count
    employed_days = a.employed_physician_days.draw(rng)
    doctor_days = (
        a.owner_count * a.owner_days_per_month
        + employed_physicians * employed_days
    )

    patients_per_doctor_day, ticket = correlated_triangular_pair(
        rng,
        a.patients_per_doctor_day,
        a.realized_revenue_per_visit,
        a.patient_ticket_correlation,
    )
    monthly_visits = doctor_days * patients_per_doctor_day
    monthly_revenue = monthly_visits * ticket
    daily_patients = monthly_visits / (365.25 / 12)

    physician_payroll = (
        employed_physicians
        * a.employed_physician_monthly_cost.draw(rng)
        * 12
    )
    staff_payroll = (
        a.nonphysician_staff
        * a.staff_monthly_gross_pay.draw(rng)
        * (1 + a.staff_employer_load.draw(rng))
        * 12
    )
    fixed_cost = (
        physician_payroll
        + staff_payroll
        + a.annual_rent_and_management.draw(rng)
        + a.annual_other_fixed_cost.draw(rng)
    )
    variable_rate = a.variable_cost_rate.draw(rng)
    contribution_rate = 1 - a.owner_revenue_share - variable_rate
    annual_revenue = monthly_revenue * 12
    repayment_cash = annual_revenue * contribution_rate - fixed_cost
    corporate_tax = korean_corporate_tax_2026(repayment_cash)
    repayment_cash_after_tax = repayment_cash - corporate_tax
    operating_bep = fixed_cost / contribution_rate / 12
    years_to_repay = (
        a.debt_krw / repayment_cash if repayment_cash > 0 else math.inf
    )
    years_to_repay_after_tax = (
        a.debt_krw / repayment_cash_after_tax
        if repayment_cash_after_tax > 0
        else math.inf
    )

    owner_gross_each = (
        annual_revenue * a.owner_revenue_share / a.owner_count
    )
    owner_net_each = (
        owner_gross_each - korean_income_tax(owner_gross_each)
    ) / 12

    return Trial(
        monthly_revenue=monthly_revenue,
        daily_patients=daily_patients,
        total_physicians=total_physicians,
        doctor_days_per_month=doctor_days,
        fixed_cost_annual=fixed_cost,
        variable_cost_rate=variable_rate,
        annual_repayment_cash=repayment_cash,
        annual_repayment_cash_after_corporate_tax=repayment_cash_after_tax,
        operating_bep_monthly_revenue=operating_bep,
        years_to_repay=years_to_repay,
        years_to_repay_after_corporate_tax=years_to_repay_after_tax,
        owner_monthly_net_each=owner_net_each,
        owner_monthly_net_couple=owner_net_each * a.owner_count,
    )


def percentile(sorted_values: list[float], probability: float) -> float:
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight


def summarize(values: Iterable[float]) -> dict[str, float]:
    finite = sorted(value for value in values if math.isfinite(value))
    return {
        "p05": percentile(finite, 0.05),
        "p25": percentile(finite, 0.25),
        "p50": percentile(finite, 0.50),
        "p75": percentile(finite, 0.75),
        "p95": percentile(finite, 0.95),
        "mean": sum(finite) / len(finite),
    }


def probability(trials: list[Trial], predicate) -> float:
    return sum(bool(predicate(trial)) for trial in trials) / len(trials)


def simulate(a: Assumptions) -> dict:
    rng = random.Random(a.seed)
    trials = [run_trial(rng, a) for _ in range(a.simulations)]

    results = {
        "assumptions": {
            **asdict(a),
            "currency": "KRW",
            "tax_note": (
                "Approximate comprehensive income tax + 10% local tax; "
                "health insurance, pension, deductions and other income excluded."
            ),
        },
        "distributions": {
            "monthly_revenue": summarize(t.monthly_revenue for t in trials),
            "daily_patients": summarize(t.daily_patients for t in trials),
            "fixed_cost_annual": summarize(t.fixed_cost_annual for t in trials),
            "operating_bep_monthly_revenue": summarize(
                t.operating_bep_monthly_revenue for t in trials
            ),
            "owner_monthly_net_each": summarize(
                t.owner_monthly_net_each for t in trials
            ),
            "owner_monthly_net_couple": summarize(
                t.owner_monthly_net_couple for t in trials
            ),
            "years_to_repay_if_positive": summarize(
                t.years_to_repay for t in trials
            ),
            "years_to_repay_after_corporate_tax_if_positive": summarize(
                t.years_to_repay_after_corporate_tax for t in trials
            ),
        },
        "probabilities": {
            "operating_cashflow_positive": probability(
                trials, lambda t: t.annual_repayment_cash > 0
            ),
            "repay_within_6_years": probability(
                trials, lambda t: t.years_to_repay <= 6
            ),
            "repay_within_7_years": probability(
                trials, lambda t: t.years_to_repay <= 7
            ),
            "repay_within_10_years": probability(
                trials, lambda t: t.years_to_repay <= 10
            ),
            "repay_within_6_years_after_corporate_tax": probability(
                trials, lambda t: t.years_to_repay_after_corporate_tax <= 6
            ),
            "repay_within_7_years_after_corporate_tax": probability(
                trials, lambda t: t.years_to_repay_after_corporate_tax <= 7
            ),
            "repay_within_10_years_after_corporate_tax": probability(
                trials, lambda t: t.years_to_repay_after_corporate_tax <= 10
            ),
            "monthly_revenue_at_least_10b_krw": probability(
                trials, lambda t: t.monthly_revenue >= 1.0 * BILLION
            ),
            "daily_patients_at_least_280": probability(
                trials, lambda t: t.daily_patients >= 280
            ),
        },
        "schedule_comparison": {
            "owners_assumed_workdays_per_year": a.owner_days_per_month * 12,
            "days_off_per_year_at_exactly_two_per_month": 24,
            "reported_korean_physician_average_workdays_2023": 292.8,
            "reported_korean_physician_average_days_off_2023": 72.3,
            "note": (
                "The survey provides no variance or matched control group, "
                "so a p-value for long-term sustainability cannot be computed."
            ),
        },
    }
    return results


def money(value: float) -> str:
    return f"{value / EOK:,.2f}억원"


def render_markdown(result: dict) -> str:
    d = result["distributions"]
    p = result["probabilities"]
    schedule = result["schedule_comparison"]
    lines = [
        "# 톤즈형 대형 미용의원 추정 결과",
        "",
        "## 핵심 결과",
        "",
        "| 지표 | P05 | 중앙값 | P95 |",
        "|---|---:|---:|---:|",
        (
            f"| 월 매출 | {money(d['monthly_revenue']['p05'])} | "
            f"{money(d['monthly_revenue']['p50'])} | "
            f"{money(d['monthly_revenue']['p95'])} |"
        ),
        (
            f"| 일 환자 | {d['daily_patients']['p05']:,.0f}명 | "
            f"{d['daily_patients']['p50']:,.0f}명 | "
            f"{d['daily_patients']['p95']:,.0f}명 |"
        ),
        (
            f"| 연 고정비 | {money(d['fixed_cost_annual']['p05'])} | "
            f"{money(d['fixed_cost_annual']['p50'])} | "
            f"{money(d['fixed_cost_annual']['p95'])} |"
        ),
        (
            f"| 운영 BEP 월매출 | "
            f"{money(d['operating_bep_monthly_revenue']['p05'])} | "
            f"{money(d['operating_bep_monthly_revenue']['p50'])} | "
            f"{money(d['operating_bep_monthly_revenue']['p95'])} |"
        ),
        (
            f"| 1인 월 세후* | {money(d['owner_monthly_net_each']['p05'])} | "
            f"{money(d['owner_monthly_net_each']['p50'])} | "
            f"{money(d['owner_monthly_net_each']['p95'])} |"
        ),
        (
            f"| 부부 월 세후* | "
            f"{money(d['owner_monthly_net_couple']['p05'])} | "
            f"{money(d['owner_monthly_net_couple']['p50'])} | "
            f"{money(d['owner_monthly_net_couple']['p95'])} |"
        ),
        "",
        "*건강보험·연금·공제·타소득 제외. 10%가 실제로 부부에게 과세소득으로 "
        "귀속된다는 가정입니다.",
        "",
        "## 모델 내 확률",
        "",
        f"- 운영현금흐름 흑자: {p['operating_cashflow_positive']:.1%}",
        (
            f"- 6년 내 90억 상환: 세전 {p['repay_within_6_years']:.1%} / "
            f"법인세 후 {p['repay_within_6_years_after_corporate_tax']:.1%}"
        ),
        (
            f"- 7년 내 90억 상환: 세전 {p['repay_within_7_years']:.1%} / "
            f"법인세 후 {p['repay_within_7_years_after_corporate_tax']:.1%}"
        ),
        (
            f"- 10년 내 90억 상환: 세전 {p['repay_within_10_years']:.1%} / "
            f"법인세 후 {p['repay_within_10_years_after_corporate_tax']:.1%}"
        ),
        f"- 월매출 10억 이상: {p['monthly_revenue_at_least_10b_krw']:.1%}",
        f"- 일 환자 280명 이상: {p['daily_patients_at_least_280']:.1%}",
        "",
        "위 확률은 관측 표본에서 검정한 p-value가 아니라 입력 범위에 따른 "
        "모델 확률입니다.",
        "",
        "## 월 2일 휴무 검증",
        "",
        f"- 모델상 원장 근무: 연 {schedule['owners_assumed_workdays_per_year']:.0f}일",
        "- 정확히 매월 2일만 쉬면 연 휴무 24일(연 근무 341일)",
        "- 2023년 조사: 한국 의사 평균 연 근무 292.8일, 평균 휴무 72.3일",
        "- 따라서 월 2일 휴무는 평균보다 연 48.2일 더 일하고, 휴무는 "
        "약 66.8% 적은 극단적 일정입니다.",
        "- 원자료에 분산과 동일 조건 대조군이 없어 장기 지속 가능성에 대한 "
        "p<0.05 검정은 할 수 없습니다.",
        "",
        "## 해석 제한",
        "",
        "- 최근 12개월 실제 카드·현금·패키지 이연매출 자료가 없습니다.",
        "- 환자수와 객단가는 공개자료로 확인되지 않아 입력 범위입니다.",
        "- 90억이 무이자 원금 상한이고 상환 즉시 종료된다고 가정했습니다.",
        "- 10% 선취와 모든 운영비를 동시에 차감했습니다. 계약상 비용 귀속이 "
        "다르면 식을 바꿔야 합니다.",
        "- 법인세는 운영법인의 이익에 부과될 수 있으나, 부부 10%의 세후 계산은 "
        "개인 종합소득세 가정입니다. 법적 사업구조 확인 전 둘을 섞으면 안 됩니다.",
        "- 법인세 후 시나리오는 2026년 세율과 지방세를 적용하고 인수자산 "
        "감가상각은 0원으로 둔 보수값입니다. 영업권·장비의 세무상 취득가액이 "
        "확인되면 상환 결과가 개선될 수 있습니다.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulations", type=int, default=200_000)
    parser.add_argument("--seed", type=int, default=20260817)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    assumptions = Assumptions(simulations=args.simulations, seed=args.seed)
    result = simulate(assumptions)
    if args.json:
        args.json.write_text(
            json.dumps(result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    report = render_markdown(result)
    if args.report:
        args.report.write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
