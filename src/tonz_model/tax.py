"""한국 개인 고소득자(개원의) 세금·준조세 계산.

- 종합소득세 누진세율 (2023년 개편 이후 구조, 2026년 현재 동일 구간 가정)
- 지방소득세 = 산출세액의 10%
- 국민연금(지역가입자, 기준소득월액 상한 적용)
- 건강보험 + 장기요양 (상한 적용)

모든 금액 단위는 **만원/년**.

주의: 이 모델의 부부는 '매출 10% 선취'를 사업소득으로 신고한다고 가정한다.
필요경비를 얼마나 인정받는지(=MSO 지급분을 비용으로 털 수 있는지)가
세후 실수령을 크게 흔드는데, 그 리스크는 scenarios.py 의
`tax_attribution` 이벤트에서 별도로 다룬다.
"""

from __future__ import annotations

import numpy as np

# (과세표준 상한, 세율, 누진공제) — 단위 만원
BRACKETS: list[tuple[float, float, float]] = [
    (1_400.0, 0.06, 0.0),
    (5_000.0, 0.15, 126.0),
    (8_800.0, 0.24, 576.0),
    (15_000.0, 0.35, 1_544.0),
    (30_000.0, 0.38, 1_994.0),
    (50_000.0, 0.40, 2_594.0),
    (100_000.0, 0.42, 3_594.0),
    (float("inf"), 0.45, 6_594.0),
]

LOCAL_TAX_RATE = 0.10  # 지방소득세 = 산출세액의 10%

# 국민연금: 기준소득월액 상한 617만원, 지역가입자 요율 9%
NPS_MONTHLY_CAP_INCOME = 617.0
NPS_RATE = 0.09

# 건강보험: 소득 요율 7.09% + 장기요양(건보료의 12.95%), 월 보험료 상한 약 424.8만원
NHIS_RATE = 0.0709
LTC_RATE = 0.1295
NHIS_MONTHLY_CAP = 424.8


def income_tax(taxable: np.ndarray | float) -> np.ndarray | float:
    """종합소득세 산출세액(지방소득세 제외). 과세표준 기준."""
    t = np.asarray(taxable, dtype=float)
    t = np.maximum(t, 0.0)
    tax = np.zeros_like(t)
    lower = 0.0
    for upper, rate, deduction in BRACKETS:
        in_band = (t > lower) & (t <= upper)
        tax = np.where(in_band, t * rate - deduction, tax)
        lower = upper
    return tax if isinstance(taxable, np.ndarray) else float(tax)


def social_insurance(income: np.ndarray | float) -> np.ndarray | float:
    """국민연금 + 건강보험 + 장기요양 (연간, 만원)."""
    inc = np.maximum(np.asarray(income, dtype=float), 0.0)
    nps = NPS_MONTHLY_CAP_INCOME * NPS_RATE * 12.0 * np.ones_like(inc)
    nps = np.minimum(nps, inc * NPS_RATE)  # 소득이 매우 낮으면 비례
    nhis_monthly = np.minimum(inc / 12.0 * NHIS_RATE, NHIS_MONTHLY_CAP)
    nhis = nhis_monthly * 12.0 * (1.0 + LTC_RATE)
    out = nps + nhis
    return out if isinstance(income, np.ndarray) else float(out)


def net_income(
    gross: np.ndarray | float,
    expense_rate: float = 0.0,
    deductions: float = 300.0,
) -> np.ndarray | float:
    """세전 사업소득 -> 세후 실수령 (연간, 만원).

    expense_rate: 인정 필요경비 비율(기본 0 = 10% 선취분이 그대로 소득).
    deductions: 인적공제 등 소득공제 합계(보수적으로 300만원).
    """
    g = np.maximum(np.asarray(gross, dtype=float), 0.0)
    business_income = g * (1.0 - expense_rate)
    si = social_insurance(business_income)
    # 소득공제 대상은 연금보험료까지만(건강보험료는 세액이 아닌 별도 부담)
    nps = np.minimum(NPS_MONTHLY_CAP_INCOME * NPS_RATE * 12.0, business_income * NPS_RATE)
    taxable = np.maximum(business_income - deductions - nps, 0.0)
    national = income_tax(taxable)
    total_tax = national * (1.0 + LOCAL_TAX_RATE)
    net = business_income - total_tax - si
    return net if isinstance(gross, np.ndarray) else float(net)


def effective_rate(gross: float) -> float:
    """실효 부담률(세금+4대보험 / 세전)."""
    if gross <= 0:
        return 0.0
    return 1.0 - float(net_income(gross)) / gross
