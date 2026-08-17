"""
다년도 월별 몬테카를로.

각 경로는 10년 × 12개월 현금흐름을 쌓는다.
- 의사 FTE: 이탈 + 채용 지연
- 황아름: 연간 이탈 위험
- 번아웃: 3년차부터 생산성·가동일 하락
- 계절성 + 객단가/임금 인플레
- 무이자 원금 차감 (옵션: 잔액 이자)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np

from tones_model.engine import ClinicEngine
from tones_model.params import ModelParams
from tones_model.physical import monthly_from_physical
from tones_model.tax_kr import couple_from_monthly_revenue_eok


@dataclass
class PathSummary:
    monthly_mean: float
    couple_takehome_mean_man: float
    exit_month: int | None
    remaining_eok: float
    operating_years_positive: int
    hwang_left_year: int | None
    doctor_fte_end: float


def _trunc_normal(rng: np.random.Generator, mu, sigma, lo, hi, size):
    x = rng.normal(mu, sigma, size)
    return np.clip(x, lo, hi)


def run_paths(
    p: ModelParams | None = None,
    n_paths: int | None = None,
    interest_rate: float | None = None,
    prior: str = "base",
) -> Dict:
    p = p or ModelParams()
    n = n_paths or p.n_paths
    rate = p.interest_rate if interest_rate is None else interest_rate
    rng = np.random.default_rng(p.seed + (0 if prior == "base" else 17))

    # prior: 의사당 일환자·객단가 분포
    if prior == "base":
        mu_ppd, sig_ppd = 25.5, 3.6
        mu_tix, sig_tix = 14.5, 1.8
    elif prior == "conservative":
        mu_ppd, sig_ppd = 23.0, 4.0
        mu_tix, sig_tix = 13.8, 1.9
    elif prior == "optimistic":
        mu_ppd, sig_ppd = 28.0, 3.2
        mu_tix, sig_tix = 15.4, 1.6
    else:
        raise ValueError(prior)

    months = p.horizon_years * 12
    season = np.array(p.seasonality, dtype=float)

    # 경로별 고유 생산성 (한 병원의 '체급')
    ppd0 = _trunc_normal(rng, mu_ppd, sig_ppd, 16, 36, n)
    tix0 = _trunc_normal(rng, mu_tix, sig_tix, 11, 20, n)

    remaining = np.full(n, p.debt_eok, dtype=float)
    exit_month = np.full(n, 0, dtype=int)          # 0 = 미완제
    hwang_on = np.ones(n, dtype=bool)
    hwang_left = np.zeros(n, dtype=int)
    paid_fte = np.full(n, float(p.paid_doctors))
    hire_wait = np.zeros(n, dtype=int)

    # 집계
    rev_month = np.zeros((n, months))
    repay_month = np.zeros((n, months))
    couple_man = np.zeros((n, months))

    engine = ClinicEngine(p)

    for m in range(months):
        year = m // 12 + 1
        month_of_year = m % 12
        # 연초 황아름 이탈
        if month_of_year == 0 and year > 1:
            leave = rng.random(n) < p.hwang_annual_leave_hazard
            newly = hwang_on & leave
            hwang_left[newly] = year
            hwang_on[newly] = False

        # 의사 이탈 (월환산)
        monthly_attr = 1 - (1 - p.doctor_attrition) ** (1 / 12)
        leave_doc = rng.random(n) < monthly_attr
        paid_fte = np.clip(paid_fte - leave_doc.astype(float), p.min_paid_doctors, p.max_paid_doctors)
        hire_wait = np.where(leave_doc, p.hire_lag_months, np.maximum(0, hire_wait - 1))
        can_hire = (hire_wait == 0) & (paid_fte < p.paid_doctors)
        paid_fte = np.where(can_hire, np.minimum(paid_fte + 1, p.max_paid_doctors), paid_fte)

        # 번아웃
        burnout_years = max(0, year - p.burnout_start_year + 1)
        ppd_drag = min(0.20, p.burnout_ppd_drag * burnout_years)
        day_drop = min(6, p.burnout_day_drop * ((year - 1) // 2)) if year >= p.burnout_start_year else 0
        work_days = max(22, p.work_days_high - day_drop)

        hwang_fte = np.where(hwang_on, p.hwang_fte, 0.0)
        doctors = paid_fte + p.couple_doctors + hwang_fte
        lift = np.where(hwang_on, 1.0 + p.hwang_revenue_lift, 1.0)

        # 월별 노이즈
        shock = rng.normal(1.0, 0.06, n)
        shock = np.clip(shock, 0.75, 1.25)
        tix = tix0 * ((1 + p.ticket_inflation) ** (year - 1))
        ppd = ppd0 * (1 - ppd_drag)

        monthly = monthly_from_physical(ppd, tix, doctors, work_days)
        monthly = monthly * lift * season[month_of_year] * shock
        rev_month[:, m] = monthly

        # 고정비: 40%는 의사수에 연동, 60%는 인플레만
        scale = 0.60 + 0.40 * (doctors / p.treating_doctors)
        fixed_m = (p.fixed_cost_eok / 12) * scale * ((1 + p.wage_inflation) ** (year - 1))
        variable_m = monthly * p.variable_rate
        mso_in = monthly * p.mso_share
        repay = mso_in - variable_m - fixed_m
        repay_month[:, m] = repay

        # 무이자: 흑자분만 원금 차감. 적자 달에 잔액이 늘지 않음.
        # 이자 있으면 잔액에 월이자를 먼저 얹고, 흑자분으로 상환.
        still = exit_month == 0
        if rate > 0:
            remaining = np.where(still, remaining * (1 + rate / 12), remaining)
        pay = np.maximum(repay, 0.0)
        remaining = np.where(still, remaining - pay, remaining)
        just_done = still & (remaining <= 0)
        exit_month[just_done] = m + 1
        remaining[remaining < 0] = 0.0

        # 월별 부부 실수령은 검증식(×6.2%). 연 집계에서 정밀세무 비율로 보정.
        couple_man[:, m] = monthly * 10_000 * (p.verified_person_net_rate * 2)

    annual_rev = rev_month.reshape(n, p.horizon_years, 12).sum(axis=2)
    annual_repay = repay_month.reshape(n, p.horizon_years, 12).sum(axis=2)
    monthly_mean = rev_month.mean(axis=1)
    # 연말 잔액 분포용: 경로별 마지막 잔액은 remaining. 연도별은 완제 전까지 90-누적흑자.

    exit_years = np.where(exit_month > 0, exit_month / 12.0, 999.0)
    couple_mean = couple_man.mean(axis=1)

    # 정밀세무는 중앙 월매출에서 비율을 구해 검증식 경로에 보정
    # 중앙 월매출에서 비율을 구해 적용
    mid = float(np.median(monthly_mean))
    tax_mid = couple_from_monthly_revenue_eok(mid, p.couple_share)
    adj = tax_mid["부부_실수령월_만"] / max(1.0, tax_mid["검증식_부부월_만"])
    couple_precise = couple_mean * adj

    def pct(x, q):
        return float(np.percentile(x, q))

    def prob(mask):
        return float(np.mean(mask) * 100)

    bep = engine.operating_bep()
    t6 = engine.required_monthly(6)
    t7 = engine.required_monthly(7)
    t10 = engine.required_monthly(10)

    # 연평균 매출이 임계를 넘는 경로 비율 (정적 근사) vs 실제 누적완제
    return {
        "prior": prior,
        "n_paths": n,
        "interest_rate": rate,
        "월매출_평균": round(float(monthly_mean.mean()), 3),
        "월매출_P10": round(pct(monthly_mean, 10), 3),
        "월매출_P25": round(pct(monthly_mean, 25), 3),
        "월매출_중앙": round(pct(monthly_mean, 50), 3),
        "월매출_P75": round(pct(monthly_mean, 75), 3),
        "월매출_P90": round(pct(monthly_mean, 90), 3),
        "부부_검증식_중앙_만": round(pct(couple_mean, 50)),
        "부부_실수령_중앙_만": round(pct(couple_precise, 50)),
        "부부_실수령_P25_만": round(pct(couple_precise, 25)),
        "부부_실수령_P75_만": round(pct(couple_precise, 75)),
        "1인_실수령_중앙_만": round(pct(couple_precise, 50) / 2),
        "운영흑자_연수_중앙": round(float(np.median((annual_repay > 0).sum(axis=1))), 1),
        "6년내_완제": round(prob((exit_month > 0) & (exit_month <= 72)), 2),
        "7년내_완제": round(prob((exit_month > 0) & (exit_month <= 84)), 2),
        "8to10년_추가완제": round(prob((exit_month > 84) & (exit_month <= 120)), 2),
        "10년내_완제": round(prob(exit_month > 0), 2),
        "엑시트년_조건부중앙": (
            round(float(np.median(exit_years[exit_years < 900])), 2)
            if np.any(exit_years < 900) else None
        ),
        "10년후_잔액_중앙_억": round(pct(remaining, 50), 2),
        "10년후_잔액_P75_억": round(pct(remaining, 75), 2),
        "황아름_10년잔류": round(prob(hwang_on), 2),
        "P_월매출>운영BEP": round(prob(monthly_mean >= bep), 2),
        "P_월매출>10년선": round(prob(monthly_mean >= t10), 2),
        "P_월매출>7년선": round(prob(monthly_mean >= t7), 2),
        "P_월매출>6년선": round(prob(monthly_mean >= t6), 2),
        "연매출경로_P10": [round(float(x), 1) for x in np.percentile(annual_rev, 10, axis=0)],
        "연매출경로_중앙": [round(float(x), 1) for x in np.median(annual_rev, axis=0)],
        "연매출경로_P90": [round(float(x), 1) for x in np.percentile(annual_rev, 90, axis=0)],
        "연상환경로_중앙": [round(float(x), 2) for x in np.median(annual_repay, axis=0)],
        "thresholds": {
            "운영BEP": round(bep, 3),
            "10년": round(t10, 3),
            "7년": round(t7, 3),
            "6년": round(t6, 3),
        },
        "tax_mid_sample": tax_mid,
        "adj_takehome_vs_verified": round(adj, 4),
    }


def stress_tests(p: ModelParams | None = None) -> List[Dict]:
    """결정론 스트레스. 기본 월매출을 물리 Base에 고정한 뒤 충격을 가함."""
    p = p or ModelParams()
    eng = ClinicEngine(p)
    base_m = monthly_from_physical(p.ppd_base, p.ticket_man, p.treating_doctors, p.work_days_high)
    shocks = [
        ("기준", 1.00, 1.00, 0.0),
        ("매출-15%", 0.85, 1.00, 0.0),
        ("매출-20%", 0.80, 1.00, 0.0),
        ("매출-30%", 0.70, 1.00, 0.0),
        ("의사2명이탈", 0.82, 1.00, 0.0),  # 11→9 FTE 근사
        ("황아름이탈", 1 / (1 + p.hwang_revenue_lift), 1.00, 0.0),
        ("고정비+10억", 1.00, 1.00, 10.0),
        ("변동비35%", 1.00, 1.00, 0.0),
        ("금리6%", 1.00, 1.00, 0.0),
        ("가동일24일", 24 / 28, 1.00, 0.0),
        ("복합:매출-15%+의사이탈", 0.85 * 0.82, 1.00, 0.0),
    ]
    rows = []
    for name, rev_x, _c, extra_fixed in shocks:
        m = base_m * rev_x
        if name == "변동비35%":
            # 임시 엔진
            q = ModelParams()
            # frozen dataclass — 새 인스턴스
            from dataclasses import replace
            q = replace(p, variable_ads_rate=p.variable_ads_rate + 0.05)
            e2 = ClinicEngine(q)
            s = e2.analyze(m)
            interest = e2.interest_total_paid(m, 0.0)
        elif name == "금리6%":
            s = eng.analyze(m)
            interest = eng.interest_total_paid(m, 0.06)
        else:
            s = eng.analyze(m, fixed=p.fixed_cost_eok + extra_fixed)
            interest = eng.interest_total_paid(m, 0.0)
        rows.append({
            "시나리오": name,
            "월매출_억": round(m, 2),
            "부부_실수령_만": s.couple_takehome_man,
            "연상환_억": s.repay_eok,
            "엑시트_년": s.exit_years if name != "금리6%" else (interest["완제년"] or 999),
            "10년잔액_억": interest.get("잔액", 0 if s.exit_years < 10 else None),
            "운영흑자": s.operating_ok,
        })
    return rows


def tornado(p: ModelParams | None = None) -> List[Dict]:
    """7년 완제 필요 월매출에 대한 민감도."""
    p = p or ModelParams()
    from dataclasses import replace

    def need(pp: ModelParams) -> float:
        return ClinicEngine(pp).required_monthly(7)

    base = need(p)
    rows = []

    a, b = need(replace(p, fixed_cost_eok=64)), need(replace(p, fixed_cost_eok=78))
    rows.append({
        "레버": "fixed cost 64 vs 78",
        "하단_월매출": round(min(a, b), 3),
        "상단_월매출": round(max(a, b), 3),
        "스윙": round(abs(b - a), 3),
    })

    a, b = need(replace(p, material_rate=0.18)), need(replace(p, material_rate=0.26))
    rows.append({
        "레버": "variable 26% vs 34%",
        "하단_월매출": round(min(a, b), 3),
        "상단_월매출": round(max(a, b), 3),
        "스윙": round(abs(b - a), 3),
    })

    r = 0.06
    pmt = p.debt_eok * (r * (1 + r) ** 7) / ((1 + r) ** 7 - 1)
    hi_m = (pmt + p.fixed_cost_eok) / p.mso_net_rate / 12
    rows.append({
        "레버": "interest 0 vs 6%",
        "하단_월매출": round(base, 3),
        "상단_월매출": round(hi_m, 3),
        "스윙": round(abs(hi_m - base), 3),
    })

    t7 = ClinicEngine(p).required_monthly(7)
    rows.append({
        "레버": "ticket 12 vs 16 (25 ppd, 28d)",
        "하단_월매출": round(monthly_from_physical(25, 12, p.treating_doctors, 28), 2),
        "상단_월매출": round(monthly_from_physical(25, 16, p.treating_doctors, 28), 2),
        "스윙": round(
            monthly_from_physical(25, 16, p.treating_doctors, 28)
            - monthly_from_physical(25, 12, p.treating_doctors, 28),
            2,
        ),
        "7년선": round(t7, 2),
    })
    rows.append({
        "레버": "ppd 22 vs 30 (ticket 14.5, 28d)",
        "하단_월매출": round(monthly_from_physical(22, 14.5, p.treating_doctors, 28), 2),
        "상단_월매출": round(monthly_from_physical(30, 14.5, p.treating_doctors, 28), 2),
        "스윙": round(
            monthly_from_physical(30, 14.5, p.treating_doctors, 28)
            - monthly_from_physical(22, 14.5, p.treating_doctors, 28),
            2,
        ),
        "7년선": round(t7, 2),
    })
    return rows


def reality_bands(engine: ClinicEngine) -> List[Dict]:
    """상권·피어로 보정한 주관적 밴드 (MC와 별도)."""
    bands = [
        ("Downside", 0.18, 5.8, 7.0, "부평5동 평균~톡스앤필"),
        ("Base", 0.38, 7.0, 9.0, "대형+체인, 운영BEP 미달 가능"),
        ("Central", 0.24, 9.0, 10.8, "상위 10~15%, 흑자 진입"),
        ("Optimistic", 0.14, 10.8, 12.5, "7년선 근접~돌파"),
        ("Bull", 0.06, 12.5, 15.0, "역사적 상위 5% 재현"),
    ]
    rows = []
    for name, w, lo, hi, note in bands:
        mid = (lo + hi) / 2
        s = engine.analyze(mid)
        rows.append({
            "밴드": name,
            "확률": w,
            "월매출_로": lo,
            "월매출_히": hi,
            "월매출_중앙": mid,
            "1인_검증식_만": s.person_verified_man,
            "부부_검증식_만": s.couple_verified_man,
            "1인_실수령_만": s.person_takehome_man,
            "부부_실수령_만": s.couple_takehome_man,
            "엑시트_년": s.exit_years,
            "7년": s.exit_7,
            "운영흑자": s.operating_ok,
            "메모": note,
        })
    return rows


def expected_from_bands(bands: List[Dict]) -> Dict:
    ev_rev = sum(b["확률"] * b["월매출_중앙"] for b in bands)
    ev_couple = sum(b["확률"] * b["부부_실수령_만"] for b in bands)
    p7 = sum(b["확률"] for b in bands if b["7년"])
    return {
        "기대_월매출_억": round(ev_rev, 2),
        "기대_부부실수령_만": round(ev_couple),
        "밴드가중_7년가능": round(p7 * 100, 1),
    }
