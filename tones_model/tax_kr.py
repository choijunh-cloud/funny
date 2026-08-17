"""
2024–2026 종합소득세 + 지방소득세 + 지역가입자 4대보험 근사 엔진.

부부 10% 선취는 필요경비가 거의 없는 사업소득으로 본다.
건보·장기요양은 상한을 적용한다. 국민연금은 기준소득월액 상한.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

# 과세표준 상한(원), 세율, 누진공제(원) — 2024년 이후 현행
BRACKETS: List[Tuple[int, float, int]] = [
    (14_000_000, 0.06, 0),
    (50_000_000, 0.15, 1_260_000),
    (88_000_000, 0.24, 5_760_000),
    (150_000_000, 0.35, 15_440_000),
    (300_000_000, 0.38, 19_940_000),
    (500_000_000, 0.40, 25_940_000),
    (1_000_000_000, 0.42, 35_940_000),
    (10**15, 0.45, 65_940_000),
]

BASIC_DEDUCTION = 1_500_000          # 본인 기본공제
LOCAL_TAX_RATE = 0.10

# 2026 근사 상한
NHIS_MONTHLY_CAP = 4_913_010         # 건보료 월 상한
NHIS_RATE = 0.0709                   # 지역가입자 소득정률 근사
LTC_RATE = 0.1295                    # 장기요양 / 건보료
NPS_MONTHLY_BASE_CAP = 6_370_000     # 기준소득월액 상한
NPS_RATE = 0.09


@dataclass
class TaxResult:
    gross_annual: int
    taxable: int
    income_tax: int
    local_tax: int
    nhis: int
    ltc: int
    nps: int
    net_after_income_tax: int
    net_takehome: int
    effective_income_tax_rate: float
    effective_all_in_rate: float

    def monthly_takehome_man(self) -> float:
        return self.net_takehome / 12 / 10_000

    def monthly_after_tax_man(self) -> float:
        """소득세+지방세만 차감 (검증식 3.1%와 비교용)."""
        return self.net_after_income_tax / 12 / 10_000


def income_tax(taxable: int) -> int:
    if taxable <= 0:
        return 0
    for cap, rate, deduction in BRACKETS:
        if taxable <= cap:
            return max(0, int(taxable * rate - deduction))
    return 0


def assess_person(gross_annual_won: int) -> TaxResult:
    """1인 연 사업소득(원) → 세후·실수령."""
    taxable = max(0, gross_annual_won - BASIC_DEDUCTION)
    itax = income_tax(taxable)
    local = int(itax * LOCAL_TAX_RATE)
    after_tax = gross_annual_won - itax - local

    monthly_income = max(0, gross_annual_won / 12)
    nhis_m = min(monthly_income * NHIS_RATE, NHIS_MONTHLY_CAP)
    ltc_m = nhis_m * LTC_RATE
    nps_m = min(monthly_income, NPS_MONTHLY_BASE_CAP) * NPS_RATE
    nhis = int(nhis_m * 12)
    ltc = int(ltc_m * 12)
    nps = int(nps_m * 12)

    takehome = after_tax - nhis - ltc - nps
    return TaxResult(
        gross_annual=gross_annual_won,
        taxable=taxable,
        income_tax=itax,
        local_tax=local,
        nhis=nhis,
        ltc=ltc,
        nps=nps,
        net_after_income_tax=after_tax,
        net_takehome=takehome,
        effective_income_tax_rate=(itax + local) / gross_annual_won if gross_annual_won else 0.0,
        effective_all_in_rate=(itax + local + nhis + ltc + nps) / gross_annual_won if gross_annual_won else 0.0,
    )


def couple_from_monthly_revenue_eok(monthly_eok: float, couple_share: float = 0.10) -> dict:
    """월매출(억) → 부부 각 5% 사업소득 가정으로 1인·합산 실수령(만원/월)."""
    annual_couple = monthly_eok * 100_000_000 * 12 * couple_share
    per_person = int(annual_couple / 2)
    one = assess_person(per_person)
    return {
        "1인_세전_연_원": per_person,
        "1인_소득세실효": round(one.effective_income_tax_rate, 4),
        "1인_올인실효": round(one.effective_all_in_rate, 4),
        "1인_세후월_만": round(one.monthly_after_tax_man()),
        "1인_실수령월_만": round(one.monthly_takehome_man()),
        "부부_세후월_만": round(one.monthly_after_tax_man() * 2),
        "부부_실수령월_만": round(one.monthly_takehome_man() * 2),
        "검증식_1인월_만": round(monthly_eok * 10_000 * 0.031),
        "검증식_부부월_만": round(monthly_eok * 10_000 * 0.062),
    }
