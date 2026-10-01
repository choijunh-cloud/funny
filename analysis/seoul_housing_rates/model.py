"""강남3구·마용성 가격을 금리 경로에 연결하는 조건부 모델.

가격 배수는 네 채널의 곱이다.

1. 캡레이트. 전월세전환율로 환산한 임대수익률이 주담대 평균금리와
   기대상승률 수정분만큼 오른다. 임대료(전세)를 고정하면
   가격 배수 = 기존 수익률 / 새 요구 수익률.
   psi·phi는 2022년 인상 사이클에서 서울 거래가격이 대략 한 자릿수 후반에서
   10% 중반 빠지던 폭에 맞게 잡아 두었다. 수익률이 낮은 강남·서초는
   같은 수익률 상승이라도 가격 낙폭이 더 크다.

2. 사업자대출 코호트. 평균 차주가 아니라, 규제 주담대 위에 사업자대출을
   얹어 산 보유 주택만 따로 둔다. 금리가 오르기 전과 후의 부채상환비율
   차이만큼만 순증 매물로 친다. 이미 힘든 차주를 한 번 더 세지 않기 위해서다.
   코호트 비중은 공식 통계가 아니므로 결과 표에서 배수로 흔들어 본다.

3. 소득. 시나리오 구간의 명목소득 증가분 중 일부만 가격으로 전달된다.
   반도체 경기 때문에 신현송 총재가 말한 소득 개선이 여기 들어 있다.

4. 전세. 주담대 공시 상단이 낮을 때는 전세 부족이 매매를 받치고,
   상단이 8%대를 넘으면 전세대출도 비싸져 그 받침이 줄어든다.

보유세 개편, 재건축 호재, 호가와 실거래의 괴리는 넣지 않았다.
9월 넷째 주 강남3구·용산의 주간 하락은 모델의 입력이 아니라
이미 밖에 나와 있는 초기 가격 반응이다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from analysis.seoul_housing_rates.parameters import (
    Assumptions,
    District,
    Scenario,
    mortgage_cap,
)


@dataclass(frozen=True)
class RateState:
    base: float
    mortgage_avg: float
    mortgage_upper: float
    biz: float
    extra_term_premium: float
    hikes: int


@dataclass(frozen=True)
class VintageStress:
    name: str
    weight: float
    purchase_price: float
    mortgage: float
    biz: float
    dsr_origin: float
    dsr_now: float
    dsr_new: float
    distress_origin: float
    distress_now: float
    distress_new: float
    service_origin: float
    service_now: float
    service_new: float


@dataclass(frozen=True)
class DistrictResult:
    district: str
    group: str
    scenario: str
    band: str
    price: float
    jeonse_ratio: float
    gross_yield: float
    income_now: float
    income_future: float
    rates_now: RateState
    rates_new: RateState
    cap_ratio: float
    cap_yield_new: float
    cap_dy: float
    dy_rate: float
    dy_g: float
    g_decline: float
    listing_share: float
    latent_distress: float
    forward_distress: float
    listing_impact: float
    income_effect: float
    jeonse_effect: float
    price_ratio: float
    vintages: tuple[VintageStress, ...]
    regulated_balance: float
    regulated_service_now: float
    regulated_service_new: float
    new_loan_cap: float
    new_loan_dsr: float
    new_loan: float
    new_loan_binding: str
    new_loan_at_upper: float
    new_loan_upper_binding: str
    share_used: float


def annuity_payment(principal: float, annual_rate: float, years: int) -> float:
    """월 원리금. principal이 0이면 0."""
    if principal <= 0:
        return 0.0
    n = years * 12
    if annual_rate <= 0:
        return principal / n
    r = annual_rate / 12.0
    growth = (1.0 + r) ** n
    return principal * r * growth / (growth - 1.0)


def max_principal(annual_debt_service: float, annual_rate: float, years: int) -> float:
    """연간 원리금 한도로 빌릴 수 있는 원금."""
    if annual_debt_service <= 0:
        return 0.0
    monthly = annual_debt_service / 12.0
    n = years * 12
    if annual_rate <= 0:
        return monthly * n
    r = annual_rate / 12.0
    growth = (1.0 + r) ** n
    return monthly * (growth - 1.0) / (r * growth)


def rate_state(
    hikes: int,
    extra_term_premium: float,
    assumptions: Assumptions | None = None,
) -> RateState:
    a = assumptions or Assumptions()
    base = a.base_now + hikes * a.hike
    avg = a.anchor_avg + a.pipeline_avg + a.beta_avg * hikes * a.hike + extra_term_premium
    upper = a.anchor_upper + a.beta_upper * hikes * a.hike + extra_term_premium
    biz = max(avg + a.biz_spread, upper)
    return RateState(
        base=base,
        mortgage_avg=avg,
        mortgage_upper=upper,
        biz=biz,
        extra_term_premium=extra_term_premium,
        hikes=hikes,
    )


def gross_yield(district: District, conversion: float) -> float:
    return district.jeonse_ratio * conversion


def cap_rate_ratio(
    y0: float,
    delta_rate: float,
    g_decline: float,
    assumptions: Assumptions,
) -> tuple[float, float, float]:
    """수익률 고정 임대료 기준 가격 배수, 수익률 상승폭, 새 요구 수익률."""
    dy = assumptions.psi * delta_rate + assumptions.phi * g_decline
    y1 = y0 + dy
    if y1 <= 0.001:
        raise ValueError("요구 수익률이 0에 가까워 가격 배수를 둘 수 없습니다.")
    return y0 / y1, dy, y1


def distress_prob(dsr: float, assumptions: Assumptions) -> float:
    x = assumptions.dsr_slope * (dsr - assumptions.dsr_center)
    if x > 50.0:
        return 1.0
    if x < -50.0:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def listing_price_impact(extra_share: float, assumptions: Assumptions) -> float:
    extra = max(0.0, extra_share)
    return -assumptions.list_k * extra / (1.0 + assumptions.list_concave * extra)


def jeonse_price_effect(mortgage_upper: float, jeonse_ratio: float, assumptions: Assumptions) -> float:
    low = assumptions.jeonse_upper_low
    high = assumptions.jeonse_upper_high
    if mortgage_upper <= low:
        base = assumptions.jeonse_effect_low
    elif mortgage_upper >= high:
        base = assumptions.jeonse_effect_high
    else:
        t = (mortgage_upper - low) / (high - low)
        base = assumptions.jeonse_effect_low + t * (
            assumptions.jeonse_effect_high - assumptions.jeonse_effect_low
        )
    return base * (0.70 + 0.60 * jeonse_ratio)


def _balances(
    price_now: float,
    multiple: float,
    target_ltv: float,
    mortgage_ltv: float,
    biz_cap: float,
    mortgage_abs_cap: float | None,
) -> tuple[float, float, float]:
    purchase = price_now / multiple
    mortgage = mortgage_ltv * purchase
    if mortgage_abs_cap is not None:
        mortgage = min(mortgage, mortgage_abs_cap)
    biz = min(biz_cap, max(0.0, target_ltv * purchase - mortgage))
    return purchase, mortgage, biz


def _mortgage_service(
    balance: float,
    floating_rate: float,
    assumptions: Assumptions,
) -> float:
    floating = annuity_payment(balance, floating_rate, assumptions.amort_years)
    fixed = annuity_payment(balance, assumptions.fixed_mortgage_rate, assumptions.amort_years)
    monthly = assumptions.float_share * floating + (1.0 - assumptions.float_share) * fixed
    return monthly * 12.0


def _debt_service(
    mortgage: float,
    biz: float,
    mortgage_rate: float,
    biz_rate: float,
    assumptions: Assumptions,
    blend_fixed: bool = True,
) -> float:
    if blend_fixed:
        mortgage_service = _mortgage_service(mortgage, mortgage_rate, assumptions)
    else:
        mortgage_service = annuity_payment(mortgage, mortgage_rate, assumptions.amort_years) * 12.0
    return mortgage_service + biz * biz_rate


def _vintages(
    district: District,
    income_now: float,
    income_future: float,
    now: RateState,
    new: RateState,
    assumptions: Assumptions,
) -> tuple[VintageStress, ...]:
    specs = (
        (
            "2021-22 저금리",
            assumptions.old_weight,
            district.price_multiple_since_2021,
            assumptions.target_ltv_old,
            assumptions.mortgage_ltv_old,
            None,
        ),
        (
            "2025-26 고점",
            assumptions.recent_weight,
            assumptions.recent_multiple,
            assumptions.target_ltv_recent,
            assumptions.mortgage_ltv_old,
            assumptions.mortgage_abs_cap_recent,
        ),
    )
    out: list[VintageStress] = []
    for name, weight, multiple, target, mort_ltv, abs_cap in specs:
        purchase, mortgage, biz = _balances(
            district.price_84,
            multiple,
            target,
            mort_ltv,
            assumptions.biz_cap,
            abs_cap,
        )
        service_origin = _debt_service(
            mortgage,
            biz,
            assumptions.origin_mortgage_rate,
            assumptions.origin_biz_rate,
            assumptions,
            blend_fixed=False,
        )
        service_now = _debt_service(mortgage, biz, now.mortgage_avg, now.biz, assumptions)
        service_new = _debt_service(mortgage, biz, new.mortgage_avg, new.biz, assumptions)
        dsr_origin = service_origin / income_now
        dsr_now = service_now / income_now
        dsr_new = service_new / income_future
        out.append(
            VintageStress(
                name=name,
                weight=weight,
                purchase_price=purchase,
                mortgage=mortgage,
                biz=biz,
                dsr_origin=dsr_origin,
                dsr_now=dsr_now,
                dsr_new=dsr_new,
                distress_origin=distress_prob(dsr_origin, assumptions),
                distress_now=distress_prob(dsr_now, assumptions),
                distress_new=distress_prob(dsr_new, assumptions),
                service_origin=service_origin,
                service_now=service_now,
                service_new=service_new,
            )
        )
    return tuple(out)


def _new_buyer_loan(
    price: float,
    income: float,
    mortgage_rate: float,
    assumptions: Assumptions,
) -> tuple[float, float, float, str]:
    cap = float(mortgage_cap(price))
    capacity = income * assumptions.dsr_limit
    dsr_max = max_principal(capacity, mortgage_rate, assumptions.amort_years)
    loan = min(cap, dsr_max)
    if dsr_max < cap - 1.0:
        binding = "DSR"
    else:
        binding = "금액한도"
    return cap, dsr_max, loan, binding


def evaluate(
    district: District,
    scenario: Scenario,
    assumptions: Assumptions | None = None,
    share_scale: float = 1.0,
    g_scale: float = 1.0,
    band: str = "central",
    share_override: float | None = None,
) -> DistrictResult:
    a = assumptions or Assumptions()
    now = rate_state(0, 0.0, a)
    new = rate_state(scenario.hikes, scenario.extra_term_premium, a)
    y0 = gross_yield(district, a.conversion)
    g_decline = scenario.g_decline * district.expectation_beta * g_scale
    delta_rate = new.mortgage_avg - now.mortgage_avg
    dy_rate = a.psi * delta_rate
    dy_g = a.phi * g_decline
    cap_ratio, dy, y1 = cap_rate_ratio(y0, delta_rate, g_decline, a)

    income_now = district.income_2025 * (1.0 + a.income_level_up)
    income_future = income_now * (1.0 + scenario.income_growth)
    vintages = _vintages(district, income_now, income_future, now, new, a)
    latent_distress = 0.0
    forward_distress = 0.0
    for vintage in vintages:
        # 대출 당시보다 나빠진 부분만 금리 충격이다. 그중 priced_fraction은 이미 가격에 들어갔다고 본다.
        stress_now = max(0.0, vintage.distress_now - vintage.distress_origin)
        stress_new = max(0.0, vintage.distress_new - vintage.distress_origin)
        priced = a.priced_fraction * stress_now
        latent_distress += vintage.weight * max(0.0, stress_now - priced)
        forward_distress += vintage.weight * max(0.0, stress_new - stress_now)
    if share_override is None:
        share = district.biz_share * share_scale
    else:
        share = share_override
    share = min(a.share_cap, max(0.0, share))
    listing_share = share * (latent_distress + forward_distress) * a.list_prob
    list_impact = listing_price_impact(listing_share, a)
    income_effect = a.income_pass_through * scenario.income_growth
    jeonse_effect = jeonse_price_effect(new.mortgage_upper, district.jeonse_ratio, a)
    price_ratio = cap_ratio * (1.0 + list_impact) * (1.0 + income_effect) * (1.0 + jeonse_effect)

    reg_now = _mortgage_service(district.avg_mortgage_2025, now.mortgage_avg, a)
    reg_new = _mortgage_service(district.avg_mortgage_2025, new.mortgage_avg, a)
    cap, dsr_max, loan, binding = _new_buyer_loan(
        district.price_84, income_future, new.mortgage_avg, a
    )
    _, _, loan_upper, binding_upper = _new_buyer_loan(
        district.price_84, income_future, new.mortgage_upper, a
    )
    return DistrictResult(
        district=district.name,
        group=district.group,
        scenario=scenario.id,
        band=band,
        price=float(district.price_84),
        jeonse_ratio=district.jeonse_ratio,
        gross_yield=y0,
        income_now=income_now,
        income_future=income_future,
        rates_now=now,
        rates_new=new,
        cap_ratio=cap_ratio,
        cap_yield_new=y1,
        cap_dy=dy,
        dy_rate=dy_rate,
        dy_g=dy_g,
        g_decline=g_decline,
        listing_share=listing_share,
        latent_distress=latent_distress,
        forward_distress=forward_distress,
        listing_impact=list_impact,
        income_effect=income_effect,
        jeonse_effect=jeonse_effect,
        price_ratio=price_ratio,
        vintages=vintages,
        regulated_balance=float(district.avg_mortgage_2025),
        regulated_service_now=reg_now,
        regulated_service_new=reg_new,
        new_loan_cap=cap,
        new_loan_dsr=dsr_max,
        new_loan=loan,
        new_loan_binding=binding,
        new_loan_at_upper=loan_upper,
        new_loan_upper_binding=binding_upper,
        share_used=share,
    )


def backtest_2022(assumptions: Assumptions | None = None) -> float:
    """2021~22년 주담대 +3.2%p, 기대수익률 -2.5%p, 당시 수익률 2.3%의 가격 변화."""
    a = assumptions or Assumptions()
    ratio, _, _ = cap_rate_ratio(0.023, 0.032, 0.025, a)
    return ratio - 1.0


def rate_that_exhausts_cap(
    principal: float,
    annual_capacity: float,
    years: int,
    lo: float = 0.005,
    hi: float = 0.20,
) -> float | None:
    """금액 한도 대출의 연 원리금이 상환여력과 같아지는 금리. 없으면 None."""
    if annuity_payment(principal, lo, years) * 12.0 > annual_capacity:
        return lo
    if annuity_payment(principal, hi, years) * 12.0 < annual_capacity:
        return None
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        payment = annuity_payment(principal, mid, years) * 12.0
        if payment > annual_capacity:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


def sequential_contributions(result: DistrictResult) -> list[tuple[str, float]]:
    """곱으로 쌓인 채널을, 합이 총 변화율과 같은 순서 기여로 푼다."""
    y0 = result.gross_yield
    r0 = 1.0
    r_rate = y0 / (y0 + result.dy_rate)
    r_g = result.cap_ratio
    r_list = r_g * (1.0 + result.listing_impact)
    r_income = r_list * (1.0 + result.income_effect)
    r_jeonse = r_income * (1.0 + result.jeonse_effect)
    return [
        ("금리", r_rate - r0),
        ("기대수정", r_g - r_rate),
        ("사업자 매물", r_list - r_g),
        ("소득", r_income - r_list),
        ("전세", r_jeonse - r_income),
    ]
