"""응급의학과 전문의 잔류(Day-Night-Off×4) vs 이 딜 — 정량 비교.

비교 축 3개
  1) 현금: 10년 세후 현금흐름의 현재가치
  2) 시간: 시간당 세후 단가 (근무시간 정규화)
  3) 리스크: 하위 10% 시나리오에서 무엇이 남는가

주의: 부부 딜이므로 '2인 합산 대 2인 합산'으로 맞춘다.
     (응급의학 잔류 시 배우자 소득은 별도이므로, 1인 기준 비교도 함께 제시)
"""

from __future__ import annotations

import numpy as np

from . import tax
from .params import ModelParams
from .simulate import SimResult


def em_cashflows(p: ModelParams) -> np.ndarray:
    """응급의학 잔류 1인의 월 세후 현금흐름 (120개월)."""
    c = p.career
    T = p.sim.horizon_months
    months = np.arange(T)
    return c.em_net_monthly * (1.0 + c.em_growth_annual) ** (months / 12.0)


def npv(monthly: np.ndarray, annual_rate: float) -> np.ndarray:
    """월별 현금흐름 -> 현재가치. (paths, months) 또는 (months,)"""
    T = monthly.shape[-1]
    disc = (1.0 + annual_rate) ** (-np.arange(T) / 12.0)
    return (monthly * disc).sum(axis=-1)


def income_with_fallback(res: SimResult) -> np.ndarray:
    """병원 종료 이후에는 부부가 봉직의로 복귀한다고 가정한 소득 경로.

    종료 = 소득 0 으로 두면 하방을 과장한다. 의사 면허는 남기 때문에
    폐업 후에는 시장 봉직 수준으로 돌아간다고 보는 게 공정하다.
    """
    p = res.params
    T = p.sim.horizon_months
    months = np.arange(T)[None, :]
    ended = (res.end_month >= 0)[:, None] & (months >= res.end_month[:, None])
    fallback = 2.0 * p.career.fallback_net_monthly_per_person
    return np.where(ended, fallback, res.couple_net_monthly)


def operating_income_stats(res: SimResult) -> dict:
    """병원이 살아있는 동안의 부부 세후 월수령 (조건부 통계)."""
    p = res.params
    T = p.sim.horizon_months
    months = np.arange(T)[None, :]
    ended = (res.end_month >= 0)[:, None] & (months >= res.end_month[:, None])
    mask = ~ended
    tot = (res.couple_net_monthly * mask).sum(axis=1)
    cnt = mask.sum(axis=1)
    avg = np.where(cnt > 0, tot / np.maximum(cnt, 1), np.nan)
    avg = avg[~np.isnan(avg)]
    return {
        "부부_세후월_영업중_p10": float(np.quantile(avg, 0.10)),
        "부부_세후월_영업중_중앙": float(np.quantile(avg, 0.50)),
        "부부_세후월_영업중_p90": float(np.quantile(avg, 0.90)),
    }


def deal_value(res: SimResult) -> dict:
    """딜의 10년 가치 분포 (부부 2인 합산, 만원)."""
    p = res.params
    c = p.career
    r = c.discount_annual
    T = p.sim.horizon_months

    pv_income = npv(income_with_fallback(res), r)

    # 초기 투입 10억 (t=0)
    equity = p.deal.couple_equity

    # 개인 추가부담(환수·추징): 발생 시점을 모르므로 5년차 시점 할인
    pv_liability = res.couple_extra_liability * (1.0 + r) ** (-5.0)

    # 10년 시점 잔여가치
    owned = res.owned
    ebitda = np.maximum(res.final_clinic_ebitda_annual, 0.0)
    equity_value = np.where(owned, ebitda * c.exit_multiple, 0.0)

    # 미완제 잔액 처리: 탕감/연장/청구를 확률로 섞는다
    rng = np.random.default_rng(p.sim.seed + 7)
    u = rng.random(res.balance_end.shape[0])
    d = p.deal
    forgiven = u < d.unpaid_forgiven_prob
    extended = (u >= d.unpaid_forgiven_prob) & (
        u < d.unpaid_forgiven_prob + d.unpaid_extended_prob
    )
    claimed = ~(forgiven | extended)
    unpaid = ~owned
    residual = np.zeros_like(res.balance_end)
    # 탕감: 잔액 소멸 + 소유권 이전 → 병원 가치 획득
    residual = np.where(unpaid & forgiven, ebitda * c.exit_multiple, residual)
    # 연장: 소유권 미확보, 가치 0 (계속 상환)
    # 청구: 연대보증이면 잔액이 개인 채무
    if d.personal_guarantee:
        residual = np.where(unpaid & claimed, -res.balance_end, residual)
    residual = np.where(res.sham_hit | res.closed, np.minimum(residual, 0.0), residual)

    pv_terminal = (equity_value * owned + residual * unpaid) * (1.0 + r) ** (-T / 12.0)

    total = pv_income + pv_terminal - equity - pv_liability
    return {
        "pv_income": pv_income,
        "pv_terminal": pv_terminal,
        "pv_liability": pv_liability,
        "equity": equity,
        "total": total,
    }


def compare(res: SimResult) -> dict:
    p = res.params
    c = p.career
    em_1 = em_cashflows(p)
    em_pv_1 = float(npv(em_1, c.discount_annual))
    em_pv_2 = em_pv_1 * 2.0  # 부부 둘 다 동급으로 일한다고 가정한 상한 비교

    # 부부(무수련 GP)의 진짜 대안: 미용 봉직의 2인
    T = p.sim.horizon_months
    months = np.arange(T)
    fallback_pair = (
        2.0 * c.fallback_net_monthly_per_person * (1.0 + c.em_growth_annual) ** (months / 12.0)
    )
    fallback_pv_2 = float(npv(fallback_pair, c.discount_annual))

    dv = deal_value(res)
    total = dv["total"]

    op = operating_income_stats(res)
    deal_net_1p_month = income_with_fallback(res).mean(axis=1) / 2.0
    # 시간당은 '실제로 병원에서 일하는 동안'의 소득으로 계산해야 공정하다
    deal_hourly = np.array(
        [op["부부_세후월_영업중_중앙"] / 2.0 / c.deal_hours_per_month]
    )
    em_hourly = c.em_net_monthly / c.em_hours_per_month

    def q(a, x):
        return float(np.quantile(a, x))

    return {
        **op,
        "EM_1인_월세후": c.em_net_monthly,
        "EM_1인_시간당": em_hourly,
        "EM_1인_10년PV": em_pv_1,
        "EM_2인_10년PV": em_pv_2,
        "딜_1인_월세후_중앙": q(deal_net_1p_month, 0.5),
        "딜_1인_월세후_p10": q(deal_net_1p_month, 0.10),
        "딜_1인_월세후_p90": q(deal_net_1p_month, 0.90),
        "딜_1인_시간당_중앙": float(deal_hourly[0]),
        "시간당_배율_중앙(딜/EM)": float(deal_hourly[0]) / em_hourly,
        "딜_2인_10년PV_중앙": q(total, 0.5),
        "딜_2인_10년PV_p10": q(total, 0.10),
        "딜_2인_10년PV_p25": q(total, 0.25),
        "딜_2인_10년PV_p75": q(total, 0.75),
        "딜_2인_10년PV_p90": q(total, 0.90),
        "부부_봉직대안_2인_10년PV": fallback_pv_2,
        "P(딜PV > 부부 봉직대안)": float((total > fallback_pv_2).mean()),
        "P(딜PV > EM 2인PV)": float((total > em_pv_2).mean()),
        "P(딜PV > EM 1인PV)": float((total > em_pv_1).mean()),
        "P(딜PV < 0)": float((total < 0).mean()),
        "딜_초과수익_기대(2인,PV)": float(total.mean() - em_pv_2),
    }
