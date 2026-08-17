"""몬테카를로 시뮬레이터.

월 단위 120개월, 경로 병렬(numpy 벡터화).
모델링 대상:
  - 진료 생산성/객단가의 경로별 이질성 + 월별 노이즈 + 계절성 + 인수 직후 램프
  - 봉직의 이탈/충원 (매출 = 의사수 × 생산성 구조라 이게 1차 리스크)
  - 창업자 이탈, 부부 번아웃(월 2일 휴무의 지속가능성), 가격경쟁
  - 의료사고(세데이션 포함), 사무장병원 적발, 명의자 과세 리스크
  - MSO 정산 워터폴: 부부 10% 선취 → 나머지로 OPEX → 남으면 원금 상환
  - 누적 적자에 따른 재협상(선취율 인하)·폐업
  - 완제 후 소유권 이전 → 잔여이익 전부 부부 귀속
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import tax
from .capacity import profile
from .costs import monthly_costs
from .params import ModelParams


def _monthly_hazard(annual: float) -> float:
    annual = min(max(annual, 0.0), 0.999999)
    return 1.0 - (1.0 - annual) ** (1.0 / 12.0)


def _lognormal(rng, median: float, sigma: float, size: int) -> np.ndarray:
    return median * np.exp(rng.normal(0.0, sigma, size))


@dataclass
class SimResult:
    payoff_month: np.ndarray  # 완제 월 (미완제는 -1)
    revenue: np.ndarray  # (paths, months) 월매출
    couple_net_monthly: np.ndarray  # (paths, months) 부부 합산 세후 월수령
    surplus: np.ndarray  # (paths, months) MSO 상환여력
    balance_end: np.ndarray  # 10년 후 잔액
    owned: np.ndarray  # 10년 내 소유권 확보 여부
    closed: np.ndarray  # 폐업/적발로 종료
    end_month: np.ndarray  # 종료 시점 (미종료는 -1)
    sham_hit: np.ndarray
    founder_left: np.ndarray
    burnout: np.ndarray
    burnout_month: np.ndarray
    major_incident: np.ndarray
    renegotiated: np.ndarray
    couple_extra_liability: np.ndarray  # 환수·세무추징 등 개인 부담
    final_clinic_ebitda_annual: np.ndarray  # 소유권 가치 산정용
    params: ModelParams = field(repr=False, default=None)

    def q(self, arr: np.ndarray, qs=(0.05, 0.25, 0.5, 0.75, 0.95)) -> dict:
        return {f"p{int(x * 100)}": float(np.quantile(arr, x)) for x in qs}


def simulate(p: ModelParams, n_paths: int | None = None, seed: int | None = None) -> SimResult:
    cfg = p.sim
    n = n_paths or cfg.n_paths
    T = cfg.horizon_months
    rng = np.random.default_rng(cfg.seed if seed is None else seed)

    cap, cost, deal, risk, dem = p.capacity, p.cost, p.deal, p.risk, p.demand
    prof = profile(cap)

    # ---- 경로별 고정 효과 ----
    demand_base = _lognormal(rng, dem.monthly_patients_median, dem.sigma, n)
    growth = rng.normal(dem.growth_median_annual, dem.growth_sigma_annual, n)
    ticket_base = _lognormal(rng, cap.ticket_median, cap.ticket_sigma, n)
    ticket_drift = rng.normal(cap.ticket_drift_annual, cap.ticket_drift_sigma, n)
    cost_level = _lognormal(rng, 1.0, 0.06, n)  # 인건비/기타고정 수준 불확실성
    founder_hit = np.clip(_lognormal(rng, risk.founder_exit_revenue_hit, 0.5, n), 0.0, 0.6)

    # ---- 상태 ----
    staff = np.full(n, float(cost.staff_headcount))
    n_emp = np.full(n, float(cap.employed_doctors))
    balance = np.full(n, deal.principal)
    couple_share = np.full(n, deal.couple_share)
    rev_mult = np.ones(n)  # 창업자 이탈·번아웃·사고 누적 효과
    ticket_mult = np.ones(n)
    couple_days = np.full(n, cap.couple_days_per_month)
    alive = np.ones(n, dtype=bool)
    cum_deficit = np.zeros(n)  # MSO 정산 기준 수면 아래 잔고 (재협상 트리거)
    clinic_underwater = np.zeros(n)  # 병원 자체 손실 누적 (폐업 트리거)

    founder_left = np.zeros(n, dtype=bool)
    burnout = np.zeros(n, dtype=bool)
    price_war = np.zeros(n, dtype=bool)
    sham = np.zeros(n, dtype=bool)
    renegotiated = np.zeros(n, dtype=bool)
    major_incident = np.zeros(n, dtype=bool)
    closed = np.zeros(n, dtype=bool)
    extra_liability = np.zeros(n)
    payoff_month = np.full(n, -1, dtype=int)
    burnout_month = np.full(n, -1, dtype=int)
    end_month = np.full(n, -1, dtype=int)  # 폐업/적발로 종료된 월
    incident_rev_penalty_months = np.zeros(n, dtype=int)

    revenue_hist = np.zeros((n, T))
    surplus_hist = np.zeros((n, T))
    couple_gross_hist = np.zeros((n, T))
    ebitda_hist = np.zeros((n, T))

    h_att = _monthly_hazard(risk.doctor_attrition_annual)
    h_founder = _monthly_hazard(risk.founder_exit_annual)
    h_minor = _monthly_hazard(risk.incident_minor_annual)
    h_major = _monthly_hazard(risk.incident_major_annual)
    h_sham = _monthly_hazard(risk.sham_clinic_annual)
    h_taxrisk = _monthly_hazard(risk.tax_attribution_annual)
    h_pricewar = _monthly_hazard(risk.price_war_annual)
    h_renego = _monthly_hazard(deal.renegotiation_annual_prob)
    h_close = _monthly_hazard(risk.closure_annual_prob)

    i_m = deal.interest_annual / 12.0

    for t in range(T):
        yr = t / 12.0
        wage_index = (1.0 + cost.wage_inflation_annual) ** yr
        rent_index = (1.0 + cost.rent_inflation_annual) ** yr
        season = risk.seasonality[t % 12]
        ramp = risk.ramp_initial + (1.0 - risk.ramp_initial) * min(1.0, (t + 1) / risk.ramp_months)

        # --- 이벤트 ---
        # 창업자 이탈
        new_founder = (~founder_left) & (rng.random(n) < h_founder)
        rev_mult = np.where(new_founder, rev_mult * (1.0 - founder_hit), rev_mult)
        founder_left |= new_founder

        # 번아웃 (누적 해저드 상승)
        h_burn = _monthly_hazard(
            min(0.9, risk.burnout_base_annual * (1.0 + yr / risk.burnout_rampup_years))
        )
        new_burn = (~burnout) & (rng.random(n) < h_burn) & alive
        rev_mult = np.where(new_burn, rev_mult * (1.0 - risk.burnout_revenue_hit), rev_mult)
        couple_days = np.where(new_burn, 22.0, couple_days)  # 근무 정상화(주 5.5일)
        burnout_month = np.where(new_burn, t, burnout_month)
        burnout |= new_burn

        # 가격 경쟁
        new_war = (~price_war) & (rng.random(n) < h_pricewar)
        ticket_mult = np.where(new_war, ticket_mult * (1.0 - risk.price_war_ticket_hit), ticket_mult)
        price_war |= new_war

        # 의료사고
        minor = rng.random(n) < h_minor
        major = (rng.random(n) < h_major) & alive
        major_incident |= major
        incident_rev_penalty_months = np.where(major, 12, np.maximum(incident_rev_penalty_months - 1, 0))
        incident_cost = (
            minor * risk.incident_minor_cost + major * risk.incident_major_cost
        )

        # 사무장병원 적발
        new_sham = alive & (rng.random(n) < h_sham)
        sham |= new_sham
        extra_liability += new_sham * risk.sham_clawback
        end_month = np.where(new_sham, t, end_month)
        alive &= ~new_sham

        # 명의자 과세 리스크
        taxrisk = alive & (rng.random(n) < h_taxrisk)
        extra_liability += taxrisk * risk.tax_attribution_cost

        # --- 수요 ---
        demand = (
            demand_base
            * ramp
            * rev_mult
            * season
            * (1.0 + growth) ** yr
            * np.exp(rng.normal(0.0, risk.monthly_noise_sigma, n))
            * np.where(incident_rev_penalty_months > 0, 1.0 - risk.incident_major_revenue_hit, 1.0)
        )

        # --- 공급 조정: 수요에 맞춰 의사/직원을 리사이징 ---
        needed_doctor_days = demand / cap.ppd_target
        target_emp = np.clip(
            (needed_doctor_days - cap.couple_doctors * couple_days) / cap.employed_days_per_month,
            cap.min_employed_doctors,
            cap.employed_doctors,
        )
        leavers = rng.binomial(np.rint(n_emp).astype(int), h_att)
        n_emp = np.maximum(n_emp - leavers, 0.0)
        vacancies = np.maximum(np.rint(target_emp) - n_emp, 0.0)
        hires = rng.binomial(np.rint(vacancies).astype(int), risk.hire_success_monthly)
        n_emp = n_emp + hires

        target_staff = np.clip(
            cost.staff_headcount * demand / dem.monthly_patients_median,
            cost.staff_headcount * cost.staff_min_ratio,
            cost.staff_headcount * cost.staff_max_ratio,
        )
        staff = staff + (target_staff - staff) * cost.staff_adjust_speed

        # --- 실제 소화 가능한 환자수 (수요 vs 3중 병목) ---
        doctor_days = cap.couple_doctors * couple_days + n_emp * cap.employed_days_per_month
        capacity_doctor = doctor_days * cap.ppd_hard_cap
        clinical_staff_now = staff * cap.clinical_staff_ratio
        capacity_facility = (
            np.minimum(
                cap.treatment_rooms * cap.room_turns_per_day,
                clinical_staff_now * cap.treatments_per_staff_day,
            )
            * cap.open_days_per_month
        )
        served = np.minimum(demand, np.minimum(capacity_doctor, capacity_facility))

        ticket = ticket_base * ticket_mult * (1.0 + ticket_drift) ** yr
        revenue = served * ticket * alive

        # --- 비용 ---
        cb = monthly_costs(
            revenue,
            cost=cost,
            cap=cap,
            n_employed_doctors=n_emp,
            staff_headcount=staff,
            wage_index=wage_index * cost_level,
            rent_index=rent_index * cost_level,
        )
        opex = np.where(alive, cb.total + incident_cost, 0.0)

        # --- 워터폴 ---
        if deal.waterfall == "gross_mso_pays_opex":
            couple_gross = couple_share * revenue
            surplus = (1.0 - couple_share) * revenue - opex
        else:  # profit_split
            profit = np.maximum(revenue - opex, 0.0)
            couple_gross = profit * couple_share
            surplus = profit * (1.0 - couple_share)

        # 이자 발생 후 상환
        if i_m > 0:
            balance = np.where(balance > 0, balance * (1.0 + i_m), balance)
        repay = np.clip(surplus, 0.0, None)
        repay = np.minimum(repay, np.maximum(balance, 0.0))
        balance = balance - repay
        newly_paid = (payoff_month < 0) & (balance <= 1e-6) & alive
        payoff_month = np.where(newly_paid, t, payoff_month)

        # 완제 이후: 잔여이익 전부 부부 귀속
        if deal.post_payoff_full_profit:
            post = (payoff_month >= 0) & (payoff_month <= t) & alive
            couple_gross = np.where(post, np.maximum(revenue - opex, 0.0), couple_gross)

        # 적자 누적: '수면 아래 잔고' 개념. 흑자 달에는 다시 줄어든다.
        deficit = np.clip(-surplus, 0.0, None) * alive
        cum_deficit = np.maximum(0.0, cum_deficit - surplus * alive)
        if deal.deficit_adds_to_balance:
            balance += deficit
        if deal.deficit_bearer == "clinic":
            # 명의자(부부)가 운영 적자를 메우는 구조: 선취분에서 먼저 차감,
            # 모자라면 개인 채무로 쌓인다.
            absorbed = np.minimum(couple_gross, deficit)
            couple_gross = couple_gross - absorbed
            extra_liability += deficit - absorbed

        # 재협상 압력 (선취율 인하)
        trigger = (cum_deficit > deal.renegotiation_deficit_trigger) & (~renegotiated) & alive
        do_renego = trigger & (rng.random(n) < h_renego)
        couple_share = np.where(do_renego, deal.renegotiated_couple_share, couple_share)
        renegotiated |= do_renego

        # 폐업: MSO 정산 부족이 아니라 '병원 자체가 돈을 못 버는 상태'가 기준.
        # (사업 자체가 흑자면 본사는 닫는 대신 재협상·비용절감으로 간다)
        clinic_underwater = np.maximum(0.0, clinic_underwater - (revenue - opex) * alive)
        close_risk = (clinic_underwater > risk.closure_deficit_trigger) & alive
        do_close = close_risk & (rng.random(n) < h_close)
        closed |= do_close
        end_month = np.where(do_close, t, end_month)
        alive &= ~do_close

        revenue_hist[:, t] = revenue
        surplus_hist[:, t] = surplus
        couple_gross_hist[:, t] = couple_gross
        ebitda_hist[:, t] = revenue - opex

    # --- 세후 실수령 (연 단위 누진세 적용) ---
    couple_net = np.zeros_like(couple_gross_hist)
    for y in range(T // 12):
        sl = slice(y * 12, (y + 1) * 12)
        annual_gross_pair = couple_gross_hist[:, sl].sum(axis=1)
        annual_net_pair = 2.0 * tax.net_income(annual_gross_pair / 2.0)
        ratio = np.where(annual_gross_pair > 0, annual_net_pair / np.maximum(annual_gross_pair, 1e-9), 0.0)
        couple_net[:, sl] = couple_gross_hist[:, sl] * ratio[:, None]

    owned = payoff_month >= 0
    final_ebitda = ebitda_hist[:, -12:].sum(axis=1)

    return SimResult(
        payoff_month=payoff_month,
        revenue=revenue_hist,
        couple_net_monthly=couple_net,
        surplus=surplus_hist,
        balance_end=balance,
        owned=owned,
        closed=closed,
        end_month=end_month,
        sham_hit=sham,
        founder_left=founder_left,
        burnout=burnout,
        burnout_month=burnout_month,
        major_incident=major_incident,
        renegotiated=renegotiated,
        couple_extra_liability=extra_liability,
        final_clinic_ebitda_annual=final_ebitda,
        params=p,
    )


def summarize(res: SimResult) -> dict:
    p = res.params
    T = p.sim.horizon_months
    pm = res.payoff_month
    paid = pm >= 0
    years = np.where(paid, pm / 12.0, np.nan)
    rev_y3 = res.revenue[:, 24:36].mean(axis=1)
    rev_y5 = res.revenue[:, 48:60].mean(axis=1)
    net_pair = res.couple_net_monthly
    net_y1_5 = net_pair[:, :60].mean(axis=1)
    net_all = net_pair.mean(axis=1)

    def q(a, x):
        a = a[~np.isnan(a)] if np.isnan(a).any() else a
        return float(np.quantile(a, x)) if a.size else float("nan")

    return {
        "n_paths": int(res.revenue.shape[0]),
        "P(6년내 완제)": float((paid & (pm < 72)).mean()),
        "P(7년내 완제)": float((paid & (pm < 84)).mean()),
        "P(10년내 완제)": float(paid.mean()),
        "P(폐업/적발)": float((res.closed | res.sham_hit).mean()),
        "P(3년내 종료)": float((res.end_month >= 0).mean() and ((res.end_month >= 0) & (res.end_month < 36)).mean()),
        "P(5년내 종료)": float(((res.end_month >= 0) & (res.end_month < 60)).mean()),
        "종료_중앙연차": float(np.median(res.end_month[res.end_month >= 0] / 12.0))
        if (res.end_month >= 0).any()
        else float("nan"),
        "P(사무장병원 적발)": float(res.sham_hit.mean()),
        "P(창업자 이탈)": float(res.founder_left.mean()),
        "P(번아웃/근무정상화)": float(res.burnout.mean()),
        "P(3년내 번아웃)": float(((res.burnout_month >= 0) & (res.burnout_month < 36)).mean()),
        "번아웃_중앙발생연차": float(
            np.median(res.burnout_month[res.burnout_month >= 0] / 12.0)
        )
        if (res.burnout_month >= 0).any()
        else float("nan"),
        "P(재협상으로 선취율 인하)": float(res.renegotiated.mean()),
        "완제_중앙연수": q(years, 0.5),
        "완제_p25연수": q(years, 0.25),
        "완제_p75연수": q(years, 0.75),
        "매출_3년차_월_p10": q(rev_y3, 0.10),
        "매출_3년차_월_중앙": q(rev_y3, 0.50),
        "매출_3년차_월_p90": q(rev_y3, 0.90),
        "매출_5년차_월_중앙": q(rev_y5, 0.50),
        "부부세후월_1~5년_p10": q(net_y1_5, 0.10),
        "부부세후월_1~5년_중앙": q(net_y1_5, 0.50),
        "부부세후월_1~5년_p90": q(net_y1_5, 0.90),
        "부부세후월_10년평균_중앙": q(net_all, 0.50),
        "잔액_10년후_중앙": float(np.median(res.balance_end)),
        "개인추가부담_기대값": float(res.couple_extra_liability.mean()),
    }
