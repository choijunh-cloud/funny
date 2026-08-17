#!/usr/bin/env python3
"""
톤즈 부평점 MSO 딜 재무 모델
검증식: 고정비 70억, 변동비 30%, 부부 10% 선취, 1인 세후 = 월매출 × 3.1%
MSO 상환여력 = 매출의 60% - 고정비 (90% 유입 - 30% 변동비 = 60%)
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple

import numpy as np

# ── 기본 파라미터 ──────────────────────────────────────────────
FIXED_COST = 70.0          # 억원/년 (의사+직원50+임대+마케팅+기타)
VARIABLE_RATE = 0.30       # 매출 대비 변동비
MSO_INFLOW_RATE = 0.90     # MSO 매출 유입
NET_MARGIN_RATE = MSO_INFLOW_RATE - VARIABLE_RATE  # 0.60
DEBT = 90.0                # 억원 (무이자 가정)
COUPLE_SHARE = 0.10
PERSON_NET_RATE = 0.031    # 월매출 대비 1인 세후 (10% × (1-세율38%))
COUPLE_NET_RATE = 0.062
WORK_DAYS = 28
NUM_DOCTORS = 10

# 인건비 상세 (억원/년)
COST_BREAKDOWN = {
    "의사_8~10명": (28, 34),
    "직원_50명": (22, 24),
    "임대료_관리비": (6, 9),
    "마케팅_광고": (4, 7),
    "기타_고정비": (4, 6),
}


@dataclass
class ScenarioResult:
    monthly_revenue: float       # 억
    annual_revenue: float
    person_net_monthly: float    # 만원
    couple_net_monthly: float    # 만원
    annual_repayment: float      # 억
    operating_profit: float      # 억 (MSO 상환여력)
    exit_years: float
    operating_status: str
    exit_6yr: str
    exit_7yr: str


def repayment_capacity(monthly_revenue: float, fixed: float = FIXED_COST) -> float:
    """연간 MSO 상환여력 (억)"""
    return NET_MARGIN_RATE * monthly_revenue * 12 - fixed


def required_monthly_for_exit(years: float, fixed: float = FIXED_COST) -> float:
    """N년 내 90억 완제에 필요한 월매출 (억)"""
    annual_needed = DEBT / years + fixed
    return annual_needed / NET_MARGIN_RATE / 12


def person_net(monthly_revenue: float) -> float:
    """1인 월 세후 실수령 (만원)"""
    return monthly_revenue * 10000 * PERSON_NET_RATE  # 억→만원


def couple_net(monthly_revenue: float) -> float:
    """부부 합산 월 세후 실수령 (만원)"""
    return monthly_revenue * 10000 * COUPLE_NET_RATE


def physical_revenue(daily_patients: int, ticket: float) -> float:
    """물리적 환자수 × 객단가 → 월매출 (억)"""
    return daily_patients * ticket * WORK_DAYS / 10000  # 만원→억


def patients_per_doctor(daily_total: int) -> float:
    return daily_total / NUM_DOCTORS


def analyze_scenario(monthly: float) -> ScenarioResult:
    annual = monthly * 12
    repay = repayment_capacity(monthly)
    exit_y = DEBT / repay if repay > 0 else float("inf")

    op_status = "흑자" if repay > 0 else "적자"
    e6 = "가능" if monthly >= required_monthly_for_exit(6) else "불가"
    e7 = "가능" if monthly >= required_monthly_for_exit(7) else "불가"

    return ScenarioResult(
        monthly_revenue=round(monthly, 2),
        annual_revenue=round(annual, 1),
        person_net_monthly=round(person_net(monthly)),
        couple_net_monthly=round(couple_net(monthly)),
        annual_repayment=round(repay, 2),
        operating_profit=round(repay, 2),
        exit_years=round(exit_y, 1) if exit_y != float("inf") else 999,
        operating_status=op_status,
        exit_6yr=e6,
        exit_7yr=e7,
    )


def bep_table(fixed: float = FIXED_COST) -> Dict[str, float]:
    targets = {
        "운영_손익분기": fixed / NET_MARGIN_RATE / 12,
        "10년_완제": required_monthly_for_exit(10, fixed),
        "7년_완제": required_monthly_for_exit(7, fixed),
        "6년_완제": required_monthly_for_exit(6, fixed),
    }
    return {k: round(v, 2) for k, v in targets.items()}


def physical_matrix() -> List[Dict]:
    """의사 10명 × 일 환자수 × 객단가 매트릭스"""
    rows = []
    for ppd in [20, 22, 25, 28, 30, 32, 35]:
        daily = ppd * NUM_DOCTORS
        for ticket in [12, 13, 14, 15, 16, 18]:
            monthly = physical_revenue(daily, ticket)
            s = analyze_scenario(monthly)
            rows.append({
                "의사1인_일환자": ppd,
                "일총환자": daily,
                "객단가_만원": ticket,
                "월매출_억": s.monthly_revenue,
                "부부_실수령_만": s.couple_net_monthly,
                "연상환_억": s.annual_repayment,
                "엑시트_년": s.exit_years,
                "운영": s.operating_status,
                "7년": s.exit_7yr,
            })
    return rows


def monte_carlo(n_paths: int = 50_000, seed: int = 42) -> Dict:
    """
    매출 시뮬레이션: 물리적 prior 기반
    - 의사당 일환자 ~ TruncNormal(μ=26, σ=4, min=18, max=38)
    - 객단가 ~ TruncNormal(μ=14.5, σ=2, min=11, max=20) 만원
  - 무경험 부부 Downside 보정: μ를 24로 하향한 시나리오 병행
    """
    rng = np.random.default_rng(seed)

    def simulate(mu_ppd: float, sigma_ppd: float = 4.0):
        ppd = np.clip(rng.normal(mu_ppd, sigma_ppd, n_paths), 18, 38)
        ticket = np.clip(rng.normal(14.5, 2.0, n_paths), 11, 20)
        daily = ppd * NUM_DOCTORS
        monthly = daily * ticket * WORK_DAYS / 10000
        repay = NET_MARGIN_RATE * monthly * 12 - FIXED_COST
        exit_y = np.where(repay > 0, DEBT / repay, 999)
        return monthly, repay, exit_y

    # Base (현실적)
    m_base, r_base, e_base = simulate(26)
    # Conservative (무경험 부부)
    m_cons, r_cons, e_cons = simulate(24, 4.5)

    thresholds = {
        "운영_손익분기_9.3억": 9.3,
        "10년_완제_10.4억": 10.4,
        "7년_완제_10.9억": 10.9,
        "6년_완제_11.2억": 11.2,
    }

    def probs(monthly, repay, exit_y, label):
        return {
            "label": label,
            "월매출_평균": round(float(monthly.mean()), 2),
            "월매출_P25": round(float(np.percentile(monthly, 25)), 2),
            "월매출_중앙": round(float(np.median(monthly)), 2),
            "월매출_P75": round(float(np.percentile(monthly, 75)), 2),
            "부부_실수령_중앙_만": round(couple_net(float(np.median(monthly)))),
            "7년내_완제_확률": round(float((exit_y <= 7).mean()) * 100, 1),
            "10년내_완제_확률": round(float((exit_y <= 10).mean()) * 100, 1),
            "운영_흑자_확률": round(float((repay > 0).mean()) * 100, 1),
            **{f"P(>{k.split('_')[-1]})": round(float((monthly >= v).mean()) * 100, 1)
               for k, v in thresholds.items()},
        }

    # 현실 밴드 (확률 가중)
    bands = [
        ("Downside", 0.20, 5.5, 6.5),
        ("Base", 0.40, 6.5, 8.5),
        ("Central", 0.22, 8.5, 10.0),
        ("Optimistic", 0.13, 10.0, 12.0),
        ("Bull", 0.05, 12.0, 14.0),
    ]
    band_results = []
    for name, weight, lo, hi in bands:
        mid = (lo + hi) / 2
        s = analyze_scenario(mid)
        band_results.append({
            "밴드": name,
            "확률": f"{weight*100:.0f}%",
            "월매출_범위": f"{lo}~{hi}억",
            "중앙_월매출": mid,
            "1인_실수령_만": round(person_net(mid)),
            "부부_실수령_만": round(couple_net(mid)),
            "엑시트_년": s.exit_years,
            "7년_가능": s.exit_7yr,
        })

    return {
        "monte_carlo_base": probs(m_base, r_base, e_base, "Base(μ=26명/의사)"),
        "monte_carlo_conservative": probs(m_cons, r_cons, e_cons, "Conservative(μ=24명/의사)"),
        "reality_bands": band_results,
    }


def daily_patient_requirements() -> List[Dict]:
    """목표별 필요 일일 환자수 (객단가별)"""
    targets = [
        ("운영_손익분기", required_monthly_for_exit(FIXED_COST / (DEBT / 999))),  # wrong, use bep
    ]
    beps = bep_table()
    rows = []
    for label, monthly in beps.items():
        for ticket in [12, 14, 15, 16, 18]:
            daily = monthly * 10000 / (ticket * WORK_DAYS)
            rows.append({
                "목표": label,
                "필요_월매출_억": monthly,
                "객단가_만원": ticket,
                "필요_일환자": round(daily),
                "의사1인_일환자": round(daily / NUM_DOCTORS, 1),
            })
    return rows


def main():
    print("=" * 70)
    print("톤즈 부평점 MSO 딜 — 정밀 재무 모델")
    print("=" * 70)

    # 1. 비용 구조
    print("\n[1] 비용 구조 (연간, 억원)")
    total_lo, total_hi = 0, 0
    for k, (lo, hi) in COST_BREAKDOWN.items():
        print(f"  {k:20s}: {lo:>4}~{hi:>4}억")
        total_lo += lo
        total_hi += hi
    print(f"  {'합계':20s}: {total_lo:>4}~{total_hi:>4}억  (모델 고정비: {FIXED_COST}억)")

    # 2. BEP
    print("\n[2] BEP 및 상환 목표 (고정비 70억)")
    beps = bep_table()
    for k, v in beps.items():
        print(f"  {k:15s}: 월 {v:.2f}억 (연 {v*12:.0f}억)")

    # 3. 월매출별 시나리오
    print("\n[3] 월매출별 부부 실수령·엑시트")
    print(f"  {'월매출':>8} {'1인실수령':>10} {'부부실수령':>10} {'연상환':>8} {'엑시트':>8} {'운영':>6} {'7년':>6}")
    for m in [5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.3, 9.8, 10.0, 10.5, 10.9, 11.2, 12.0, 12.5]:
        s = analyze_scenario(m)
        print(f"  {s.monthly_revenue:>7.1f}억 {s.person_net_monthly:>9,.0f}만 {s.couple_net_monthly:>9,.0f}만 "
              f"{s.annual_repayment:>7.1f}억 {s.exit_years:>7.1f}년 {s.operating_status:>6} {s.exit_7yr:>6}")

    # 4. 물리적 수용력
    print("\n[4] 물리적 환자 수용력 → 월매출 (핵심 구간)")
    print(f"  {'의사/일':>8} {'일총':>6} {'객단가':>6} {'월매출':>8} {'부부실수령':>10} {'엑시트':>8} {'7년':>6}")
    matrix = physical_matrix()
    key_rows = [r for r in matrix if r["의사1인_일환자"] in (22, 25, 28, 30, 32, 35)
                and r["객단가_만원"] in (12, 14, 15, 16)]
    for r in key_rows:
        print(f"  {r['의사1인_일환자']:>7}명 {r['일총환자']:>5}명 {r['객단가_만원']:>5}만 "
              f"{r['월매출_억']:>7.1f}억 {r['부부_실수령_만']:>9,.0f}만 {r['엑시트_년']:>7.1f}년 {r['7년']:>6}")

    # 5. 목표별 필요 환자수
    print("\n[5] 목표 달성 필요 일일 환자수")
    bep_labels = bep_table()
    for label, monthly in bep_labels.items():
        for ticket in [14, 15]:
            daily = monthly * 10000 / (ticket * WORK_DAYS)
            print(f"  {label:15s} (월{monthly:.1f}억, 객단가{ticket}만): "
                  f"일 {daily:.0f}명 (의사당 {daily/NUM_DOCTORS:.1f}명)")

    # 6. 몬테카를로
    print("\n[6] 몬테카를로 시뮬레이션 (50,000경로)")
    mc = monte_carlo()
    for key in ["monte_carlo_base", "monte_carlo_conservative"]:
        p = mc[key]
        print(f"\n  [{p['label']}]")
        print(f"    월매출: 평균 {p['월매출_평균']}억, 중앙 {p['월매출_중앙']}억 (P25~P75: {p['월매출_P25']}~{p['월매출_P75']})")
        print(f"    부부 실수령(중앙): {p['부부_실수령_중앙_만']:,}만원")
        print(f"    운영 흑자 확률: {p['운영_흑자_확률']}%")
        print(f"    7년 내 완제: {p['7년내_완제_확률']}%, 10년 내: {p['10년내_완제_확률']}%")
        for k, v in p.items():
            if k.startswith("P(>"):
                print(f"    {k}: {v}%")

    print("\n[7] 현실 밴드별 부부 실수령")
    print(f"  {'밴드':12} {'확률':>5} {'월매출':>12} {'1인':>8} {'부부':>8} {'엑시트':>8} {'7년':>6}")
    for b in mc["reality_bands"]:
        print(f"  {b['밴드']:12} {b['확률']:>5} {b['월매출_범위']:>12} "
              f"{b['1인_실수령_만']:>7,}만 {b['부부_실수령_만']:>7,}만 "
              f"{b['엑시트_년']:>7.1f}년 {b['7년_가능']:>6}")

    # 7. 응급의 비교
    print("\n[8] 응급의학과 전문의(DN OOOO, 월 3,000만) 비교")
    em_net = 3000  # 만원
    base_mid = 7.5  # Base 밴드 중앙
    tones_person = person_net(base_mid)
    print(f"  응급의 1인 실수령:     {em_net:,}만원/월")
    print(f"  톤즈 Base(월7.5억) 1인: {tones_person:,.0f}만원/월  (차이: {tones_person - em_net:+,.0f}만)")
    print(f"  톤즈 Optimistic(월11억): {person_net(11):,.0f}만원/월  (차이: {person_net(11) - em_net:+,.0f}만)")

    # JSON 저장
    output = {
        "parameters": {
            "fixed_cost_억": FIXED_COST,
            "variable_rate": VARIABLE_RATE,
            "debt_억": DEBT,
            "person_net_rate": PERSON_NET_RATE,
            "num_doctors": NUM_DOCTORS,
            "work_days": WORK_DAYS,
        },
        "bep": beps,
        "scenarios": [asdict(analyze_scenario(m)) for m in
                      [5.5, 6.5, 7.5, 8.5, 9.3, 9.8, 10.5, 10.9, 11.2, 12.0]],
        "physical_matrix_sample": key_rows,
        "monte_carlo": mc,
        "cost_breakdown": COST_BREAKDOWN,
    }
    with open("/workspace/tones_model_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("\n결과 저장: tones_model_results.json")


if __name__ == "__main__":
    main()
