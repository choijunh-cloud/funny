"""2026 귀속 종합소득세 + 지방세 + 사업자 사회보험 근사."""

from __future__ import annotations

from dataclasses import dataclass

# 과세표준, 세율, 누진공제 (원)
BRACKETS: tuple[tuple[int, float, int], ...] = (
    (14_000_000, 0.06, 0),
    (50_000_000, 0.15, 1_260_000),
    (88_000_000, 0.24, 5_760_000),
    (150_000_000, 0.35, 15_440_000),
    (300_000_000, 0.38, 19_940_000),
    (500_000_000, 0.40, 25_940_000),
    (1_000_000_000, 0.42, 35_940_000),
    (10**15, 0.45, 65_940_000),
)

NHIS_RATE = 0.0719
LTCI_ON_NHIS = 0.1314
NPS_RATE = 0.095
NPS_CAP_MONTHLY = 6_590_000
BASIC_DEDUCTION = 1_500_000  # 본인 기본공제 근사


@dataclass(frozen=True)
class TaxResult:
    pretax_annual: float
    taxable: float
    income_tax: float
    local_tax: float
    nhis: float
    ltci: float
    nps: float
    total_burden: float
    net_annual: float
    net_monthly: float
    effective_rate: float


def income_tax(taxable: float) -> float:
    if taxable <= 0:
        return 0.0
    rate = 0.06
    deduction = 0
    for upper, r, d in BRACKETS:
        rate, deduction = r, d
        if taxable <= upper:
            break
    return max(taxable * rate - deduction, 0.0)


def self_employed_burden(pretax_annual: float) -> TaxResult:
    """개설자 사업소득 1인. 필요경비 0(10% 선취가 이미 순인출) 가정."""
    pretax = max(float(pretax_annual), 0.0)
    taxable = max(pretax - BASIC_DEDUCTION, 0.0)
    itax = income_tax(taxable)
    local = itax * 0.10
    nhis = pretax * NHIS_RATE
    ltci = nhis * LTCI_ON_NHIS
    monthly_base = min(pretax / 12.0, NPS_CAP_MONTHLY)
    nps = monthly_base * NPS_RATE * 12.0
    total = itax + local + nhis + ltci + nps
    net = pretax - total
    rate = total / pretax if pretax else 0.0
    return TaxResult(
        pretax_annual=pretax,
        taxable=taxable,
        income_tax=itax,
        local_tax=local,
        nhis=nhis,
        ltci=ltci,
        nps=nps,
        total_burden=total,
        net_annual=net,
        net_monthly=net / 12.0,
        effective_rate=rate,
    )


def couple_takehome(annual_revenue_won: float, take_rate: float = 0.10) -> dict:
    """부부 1:1 공동사업. 각자 매출의 5%를 사업소득으로 봄."""
    each_pretax = annual_revenue_won * take_rate / 2.0
    one = self_employed_burden(each_pretax)
    shortcut_one_monthly = annual_revenue_won / 12.0 * (take_rate / 2.0) * 0.62
    return {
        "each_pretax_annual": each_pretax,
        "each_pretax_monthly": each_pretax / 12.0,
        "each_net_monthly": one.net_monthly,
        "couple_net_monthly": one.net_monthly * 2.0,
        "effective_rate": one.effective_rate,
        "shortcut_3_1pct_one_monthly": shortcut_one_monthly,
        "shortcut_overstatement": shortcut_one_monthly - one.net_monthly,
        "detail": one,
    }
