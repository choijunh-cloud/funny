#!/usr/bin/env python3
"""
톤즈 부평점 — BEP / 부부 실수령 / 엑시트 정밀 추정 모델
============================================================
확정 식 (대화에서 검증된 구조):
  부부 선취 = 매출 × 10%
  변동비     = 매출 × 30%
  고정비 F   = 인건비(의사+직원50) + 임대 + 마케팅 + 기타
  연 상환여력 = 매출 × 0.60 − F
  1인 세후   = 월매출 × 3.1%   (10%/2 × (1−0.38))
  부부 세후  = 월매출 × 6.2%

무이자 90억 캡 가정. 이자·연대보증·90% 정의 변경 시 결과 전면 재계산.
X MCP는 이 환경에서 인증 불가 → 공개 peer(데일리팜·국세청 TASIS)로 보정.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np

RNG = np.random.default_rng(20260817)

# ---------------------------------------------------------------------------
# 단위: 원 (원 단위로 내부 계산, 출력은 억/만원)
# ---------------------------------------------------------------------------
EOK = 100_000_000  # 1억
MAN = 10_000  # 1만


@dataclass(frozen=True)
class PeerBenchmarks:
    """공개 데이터 앵커 (2026-08 기준 수집)."""

    nts_derm_avg_annual_2023: float = 12.7226 * EOK  # 국세청 피부·비뇨기과 평균
    bupyeong_derm_avg_monthly: float = 1.2092 * EOK  # 데일리팜 부평역 500m 피부과 20곳
    bupyeong_derm_median_monthly: float = 0.8810 * EOK
    # Medigate 로컬(대화 실사 prior) — 공개 교차검증 불가, prior로만 사용
    bupyeong5_avg_monthly_prior: float = 2.98 * EOK
    bupyeong5_top20_monthly_prior: float = 6.82 * EOK
    toxnfill_franchise_avg_monthly_prior: float = 4.2 * EOK


PEERS = PeerBenchmarks()


@dataclass
class CostDraw:
    n_doctors: int
    doctor_monthly_pay: float  # 1인 총비용(급여+부담금)
    n_staff: int
    staff_monthly_pay: float
    rent_annual: float
    marketing_annual: float
    other_fixed_annual: float

    @property
    def doctor_payroll_annual(self) -> float:
        return self.n_doctors * self.doctor_monthly_pay * 12

    @property
    def staff_payroll_annual(self) -> float:
        return self.n_staff * self.staff_monthly_pay * 12

    @property
    def fixed_annual(self) -> float:
        return (
            self.doctor_payroll_annual
            + self.staff_payroll_annual
            + self.rent_annual
            + self.marketing_annual
            + self.other_fixed_annual
        )


def draw_cost(rng: np.random.Generator) -> CostDraw:
    """직원 50명 포함 현실적 고정비 분포."""
    n_doctors = int(rng.integers(8, 11))  # 8~10
    # 의사 1인 총비용: 세전 급여 + 4대보험 사용자분 등 ≈ 2,500~3,200만
    doctor_monthly = rng.uniform(2_500_0000, 3_200_0000)
    n_staff = 50
    # 직원 1인 총비용(4대보험·퇴직충당 포함) 350~420만
    staff_monthly = rng.uniform(350_0000, 420_0000)
    # 300~500평 부평: 연 6~9억
    rent = rng.uniform(6.0 * EOK, 9.0 * EOK)
    marketing = rng.uniform(4.0 * EOK, 7.0 * EOK)
    other = rng.uniform(4.0 * EOK, 6.5 * EOK)
    return CostDraw(
        n_doctors=n_doctors,
        doctor_monthly_pay=doctor_monthly,
        n_staff=n_staff,
        staff_monthly_pay=staff_monthly,
        rent_annual=rent,
        marketing_annual=marketing,
        other_fixed_annual=other,
    )


def draw_physical_revenue(rng: np.random.Generator, n_doctors: int) -> dict[str, float]:
    """
    물리적 수용력 기반 월 매출.
    월 가동 28일(월 2일 휴무 구조), 의사당 일 환자·객단가 분포.
    경험 전무 + 고강도 지속 페널티를 utilization에 반영.
    """
    # 의사당 일 환자: 로그정규, 중앙 ~25, 꼬리 상한 ~38
    ppd = float(np.clip(rng.lognormal(mean=np.log(25), sigma=0.22), 16, 38))
    # 객단가: 쁘띠 볼륨 12~17만 중심, 수면패키지 믹스 시 상단
    ticket = float(np.clip(rng.lognormal(mean=np.log(145_000), sigma=0.18), 100_000, 220_000))
    # 가동일: 기본 28, 번아웃/이탈 시 하락
    days = float(np.clip(rng.normal(27.5, 0.8), 24, 28))
    # 의사 가동률 (이탈·병가·교육): 0.85~0.98
    util = float(np.clip(rng.beta(12, 2), 0.75, 0.99))
    # 무경험 부부 운영 페널티 (채용/유지/품질 관리): 평균 −6%
    inexperience = float(np.clip(rng.normal(0.94, 0.04), 0.82, 1.0))
    # 황아름 잔류 효과: +0~12%
    founder = float(np.clip(rng.normal(1.06, 0.03), 0.98, 1.14))

    daily_patients = n_doctors * ppd * util
    monthly_patients = daily_patients * days
    monthly_rev = monthly_patients * ticket * inexperience * founder

    return {
        "patients_per_doctor_day": ppd,
        "ticket": ticket,
        "days": days,
        "utilization": util,
        "inexperience_factor": inexperience,
        "founder_factor": founder,
        "daily_patients": daily_patients * inexperience * founder,  # effective demand-served proxy
        "monthly_patients": monthly_patients * inexperience * founder,
        "monthly_revenue": monthly_rev,
        "annual_revenue": monthly_rev * 12,
    }


def repayment_capacity_annual(annual_revenue: float, fixed_annual: float) -> float:
    """연 상환여력 = 0.60R − F (음수면 상환 불가)."""
    return 0.60 * annual_revenue - fixed_annual


def years_to_exit(annual_capacity: float, principal: float = 90 * EOK) -> float:
    if annual_capacity <= 0:
        return float("inf")
    return principal / annual_capacity


def take_home_monthly(monthly_revenue: float, tax_rate: float = 0.38) -> dict[str, float]:
    """10% 선취 → 부부 균분 → 실효세율."""
    couple_pre_tax = monthly_revenue * 0.10
    couple_after_tax = couple_pre_tax * (1.0 - tax_rate)
    one_after_tax = couple_after_tax / 2.0
    return {
        "couple_pre_tax": couple_pre_tax,
        "couple_after_tax": couple_after_tax,
        "one_after_tax": one_after_tax,
        "coeff_one": one_after_tax / monthly_revenue if monthly_revenue else 0.0,
    }


def bep_monthly(fixed_annual: float, years: float | None = None, principal: float = 90 * EOK) -> float:
    """
    years=None → 운영 손익분기 (상환여력=0)
    years=T   → T년 완제에 필요한 월매출
    """
    if years is None:
        annual_needed = fixed_annual / 0.60
    else:
        annual_needed = (fixed_annual + principal / years) / 0.60
    return annual_needed / 12.0


def fmt_eok(x: float) -> str:
    if not np.isfinite(x):
        return "∞"
    return f"{x / EOK:.2f}억"


def fmt_man(x: float) -> str:
    if not np.isfinite(x):
        return "∞"
    return f"{x / MAN:,.0f}만"


def run_monte_carlo(n_paths: int = 50_000) -> dict[str, Any]:
    fixed_list = []
    monthly_rev_list = []
    annual_cap_list = []
    exit_years_list = []
    couple_th_list = []
    one_th_list = []
    daily_pat_list = []
    cost_components = {
        "doctor": [],
        "staff": [],
        "rent": [],
        "marketing": [],
        "other": [],
        "fixed_total": [],
    }
    phys_meta = {
        "ppd": [],
        "ticket": [],
        "days": [],
        "util": [],
        "n_doctors": [],
    }

    for _ in range(n_paths):
        cost = draw_cost(RNG)
        phys = draw_physical_revenue(RNG, cost.n_doctors)
        annual_r = phys["annual_revenue"]
        monthly_r = phys["monthly_revenue"]
        cap = repayment_capacity_annual(annual_r, cost.fixed_annual)
        exit_y = years_to_exit(cap)
        th = take_home_monthly(monthly_r)

        fixed_list.append(cost.fixed_annual)
        monthly_rev_list.append(monthly_r)
        annual_cap_list.append(cap)
        exit_years_list.append(exit_y)
        couple_th_list.append(th["couple_after_tax"])
        one_th_list.append(th["one_after_tax"])
        daily_pat_list.append(phys["daily_patients"])

        cost_components["doctor"].append(cost.doctor_payroll_annual)
        cost_components["staff"].append(cost.staff_payroll_annual)
        cost_components["rent"].append(cost.rent_annual)
        cost_components["marketing"].append(cost.marketing_annual)
        cost_components["other"].append(cost.other_fixed_annual)
        cost_components["fixed_total"].append(cost.fixed_annual)

        phys_meta["ppd"].append(phys["patients_per_doctor_day"])
        phys_meta["ticket"].append(phys["ticket"])
        phys_meta["days"].append(phys["days"])
        phys_meta["util"].append(phys["utilization"])
        phys_meta["n_doctors"].append(cost.n_doctors)

    fixed = np.array(fixed_list)
    monthly_rev = np.array(monthly_rev_list)
    annual_cap = np.array(annual_cap_list)
    exit_years = np.array(exit_years_list)
    couple_th = np.array(couple_th_list)
    one_th = np.array(one_th_list)
    daily_pat = np.array(daily_pat_list)

    # 유한 엑시트만으로 분위수
    finite_exit = exit_years[np.isfinite(exit_years)]

    def pct(a: np.ndarray, ps=(5, 25, 50, 75, 95)) -> dict[str, float]:
        return {f"p{p}": float(np.percentile(a, p)) for p in ps}

    # 목표 달성 확률
    prob_op_bep = float(np.mean(annual_cap > 0))
    prob_10y = float(np.mean(np.isfinite(exit_years) & (exit_years <= 10)))
    prob_7y = float(np.mean(np.isfinite(exit_years) & (exit_years <= 7)))
    prob_6y = float(np.mean(np.isfinite(exit_years) & (exit_years <= 6)))

    # 중앙 고정비 기준 결정론 BEP
    f_med = float(np.median(fixed))
    deterministic_bep = {
        "fixed_median_annual_eok": f_med / EOK,
        "operating_bep_monthly_eok": bep_monthly(f_med) / EOK,
        "exit_10y_monthly_eok": bep_monthly(f_med, 10) / EOK,
        "exit_7y_monthly_eok": bep_monthly(f_med, 7) / EOK,
        "exit_6y_monthly_eok": bep_monthly(f_med, 6) / EOK,
    }

    # 매출 밴드 → 실수령 역산 표 (결정론, 중앙 고정비)
    band_edges = [5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 12.5, 14.0]
    band_table = []
    for m in band_edges:
        mr = m * EOK
        ar = mr * 12
        cap = repayment_capacity_annual(ar, f_med)
        th = take_home_monthly(mr)
        band_table.append(
            {
                "monthly_rev_eok": m,
                "one_takehome_man": th["one_after_tax"] / MAN,
                "couple_takehome_man": th["couple_after_tax"] / MAN,
                "annual_capacity_eok": cap / EOK,
                "exit_years": years_to_exit(cap) if cap > 0 else None,
                "above_operating_bep": ar * 0.60 > f_med,
            }
        )

    # 물리적 그리드 (의사10 · 28일 · util 반영 없이 raw)
    phys_grid = []
    for ppd in (22, 25, 28, 32, 35):
        for ticket_man in (12, 14, 15, 16):
            mr = 10 * ppd * (ticket_man * 10_000) * 28
            ar = mr * 12
            cap = repayment_capacity_annual(ar, f_med)
            th = take_home_monthly(mr)
            phys_grid.append(
                {
                    "ppd": ppd,
                    "ticket_man": ticket_man,
                    "daily_patients": 10 * ppd,
                    "monthly_rev_eok": mr / EOK,
                    "couple_takehome_man": th["couple_after_tax"] / MAN,
                    "exit_years": (years_to_exit(cap) if cap > 0 else None),
                    "hits_7y": cap > 0 and years_to_exit(cap) <= 7,
                }
            )

    # peer 배수
    rev_med = float(np.median(monthly_rev))
    peer_multiples = {
        "vs_bupyeong_derm_avg": rev_med / PEERS.bupyeong_derm_avg_monthly,
        "vs_nts_derm_monthly_equiv": rev_med / (PEERS.nts_derm_avg_annual_2023 / 12),
        "vs_toxnfill_prior": rev_med / PEERS.toxnfill_franchise_avg_monthly_prior,
        "vs_bupyeong5_avg_prior": rev_med / PEERS.bupyeong5_avg_monthly_prior,
        "vs_bupyeong5_top20_prior": rev_med / PEERS.bupyeong5_top20_monthly_prior,
    }

    # 응급의학 기회비용 비교 (사용자: DN OOOO, 월 3,000만)
    em_one = 3_000 * MAN
    em_compare = {
        "em_monthly_takehome_man": 3000,
        "model_one_p50_man": float(np.median(one_th) / MAN),
        "model_one_p25_man": float(np.percentile(one_th, 25) / MAN),
        "model_one_p75_man": float(np.percentile(one_th, 75) / MAN),
        "prob_one_exceeds_em_3000": float(np.mean(one_th >= em_one)),
        "couple_p50_man": float(np.median(couple_th) / MAN),
    }

    # 고강도 지속 가능 가정 스트레스: utilization 하한 경로
    # (별도 재샘플 없이 하위 20% 매출 경로를 번아웃 프록시로)
    stress_idx = monthly_rev <= np.percentile(monthly_rev, 20)
    stress = {
        "share": 0.20,
        "monthly_rev_p50_eok": float(np.median(monthly_rev[stress_idx]) / EOK),
        "couple_th_p50_man": float(np.median(couple_th[stress_idx]) / MAN),
        "prob_exit_within_10y": float(
            np.mean(np.isfinite(exit_years[stress_idx]) & (exit_years[stress_idx] <= 10))
        ),
        "prob_negative_capacity": float(np.mean(annual_cap[stress_idx] <= 0)),
    }

    cost_summary = {k: pct(np.array(v)) for k, v in cost_components.items()}
    # convert to eok for readability
    cost_summary_eok = {
        k: {pk: vv / EOK for pk, vv in d.items()} for k, d in cost_summary.items()
    }

    return {
        "n_paths": n_paths,
        "assumptions": {
            "couple_share": 0.10,
            "variable_cost_ratio": 0.30,
            "repayment_margin_ratio": 0.60,
            "principal_eok": 90,
            "interest": 0.0,
            "tax_rate": 0.38,
            "one_takehome_coeff": 0.031,
            "couple_takehome_coeff": 0.062,
            "staff_count": 50,
            "operating_days_target": 28,
            "formula": "annual_capacity = 0.60*R - F; exit_years = 90eok / capacity",
        },
        "peers": asdict(PEERS),
        "cost_distribution_eok": cost_summary_eok,
        "deterministic_bep_at_median_fixed": deterministic_bep,
        "revenue_monthly_eok": {k: v / EOK for k, v in pct(monthly_rev).items()},
        "daily_patients": pct(daily_pat),
        "annual_capacity_eok": {k: v / EOK for k, v in pct(annual_cap).items()},
        "exit_years_finite_only": {
            **{k: v for k, v in pct(finite_exit).items()},
            "share_infinite_or_never": float(1.0 - len(finite_exit) / n_paths),
        },
        "takehome": {
            "one_man": {k: v / MAN for k, v in pct(one_th).items()},
            "couple_man": {k: v / MAN for k, v in pct(couple_th).items()},
        },
        "probabilities": {
            "operating_surplus": prob_op_bep,
            "exit_within_10y": prob_10y,
            "exit_within_7y": prob_7y,
            "exit_within_6y": prob_6y,
        },
        "peer_multiples_at_median_rev": peer_multiples,
        "em_opportunity_cost": em_compare,
        "burnout_stress_bottom20": stress,
        "band_table": band_table,
        "physical_grid": phys_grid,
        "physical_drivers": {
            "ppd": pct(np.array(phys_meta["ppd"])),
            "ticket": pct(np.array(phys_meta["ticket"])),
            "days": pct(np.array(phys_meta["days"])),
            "util": pct(np.array(phys_meta["util"])),
            "n_doctors_mean": float(np.mean(phys_meta["n_doctors"])),
        },
    }


def print_report(res: dict[str, Any]) -> str:
    bep = res["deterministic_bep_at_median_fixed"]
    lines = []
    a = lines.append

    a("=" * 72)
    a("톤즈 부평점 — 코딩 정밀 추정 (몬테카를로 50,000 paths)")
    a("=" * 72)
    a("")
    a("[확정 식]")
    a("  연 상환여력 = 매출×0.60 − 고정비F")
    a("  1인 세후    = 월매출×3.1%  |  부부 세후 = 월매출×6.2%")
    a("  직원 50명 포함, 무이자 90억 캡")
    a("")

    a("[1] 고정비 분포 (직원 50명 반영, 억)")
    for k in ("doctor", "staff", "rent", "marketing", "other", "fixed_total"):
        d = res["cost_distribution_eok"][k]
        a(f"  {k:12s}  p25={d['p25']:.1f}  p50={d['p50']:.1f}  p75={d['p75']:.1f}")
    a("")

    a("[2] 중앙 고정비 기준 결정론 BEP / 완제 선")
    a(f"  고정비 중앙값     {bep['fixed_median_annual_eok']:.1f}억/년")
    a(f"  운영 손익분기     월 {bep['operating_bep_monthly_eok']:.2f}억")
    a(f"  10년 완제         월 {bep['exit_10y_monthly_eok']:.2f}억")
    a(f"  7년 완제          월 {bep['exit_7y_monthly_eok']:.2f}억")
    a(f"  6년 완제          월 {bep['exit_6y_monthly_eok']:.2f}억")
    a("")

    a("[3] 물리 수용력 기반 매출 분포 (월, 억)")
    r = res["revenue_monthly_eok"]
    a(f"  p5={r['p5']:.2f}  p25={r['p25']:.2f}  p50={r['p50']:.2f}  p75={r['p75']:.2f}  p95={r['p95']:.2f}")
    dp = res["daily_patients"]
    a(
        f"  일 환자 p50={dp['p50']:.0f}명  "
        f"(p25={dp['p25']:.0f}, p75={dp['p75']:.0f})"
    )
    a("")

    a("[4] 부부 실수령 (세후, 만원/월)")
    c = res["takehome"]["couple_man"]
    o = res["takehome"]["one_man"]
    a(f"  부부 p25={c['p25']:.0f}  p50={c['p50']:.0f}  p75={c['p75']:.0f}")
    a(f"  1인  p25={o['p25']:.0f}  p50={o['p50']:.0f}  p75={o['p75']:.0f}")
    a("")

    a("[5] 엑시트 확률")
    p = res["probabilities"]
    a(f"  운영 흑자(상환여력>0)  {p['operating_surplus']*100:.1f}%")
    a(f"  10년 내 완제           {p['exit_within_10y']*100:.1f}%")
    a(f"  7년 내 완제            {p['exit_within_7y']*100:.1f}%")
    a(f"  6년 내 완제            {p['exit_within_6y']*100:.1f}%")
    ey = res["exit_years_finite_only"]
    a(
        f"  유한 엑시트 중앙값     {ey['p50']:.1f}년 "
        f"(미완제/영구적자 비중 {ey['share_infinite_or_never']*100:.1f}%)"
    )
    a("")

    a("[6] Peer 배수 (모델 중앙 월매출 기준)")
    m = res["peer_multiples_at_median_rev"]
    a(f"  vs 부평역 피부과 평균(데일리팜)     ×{m['vs_bupyeong_derm_avg']:.1f}")
    a(f"  vs 국세청 피부·비뇨기과 평균        ×{m['vs_nts_derm_monthly_equiv']:.1f}")
    a(f"  vs 톡스앤필 가맹 prior              ×{m['vs_toxnfill_prior']:.1f}")
    a(f"  vs 부평5동 평균 prior               ×{m['vs_bupyeong5_avg_prior']:.1f}")
    a(f"  vs 부평5동 상위20% prior            ×{m['vs_bupyeong5_top20_prior']:.1f}")
    a("")

    a("[7] 응급의학 DN-OOOO 월 3,000만 대비 (1인)")
    em = res["em_opportunity_cost"]
    a(f"  모델 1인 p50={em['model_one_p50_man']:.0f}만  "
      f"(p25={em['model_one_p25_man']:.0f}, p75={em['model_one_p75_man']:.0f})")
    a(f"  1인이 EM 3,000만 이상일 확률        {em['prob_one_exceeds_em_3000']*100:.1f}%")
    a("")

    a("[8] 매출 밴드 → 부부 실수령 역산표 (중앙 고정비)")
    a(f"  {'월매출':>8} {'1인':>8} {'부부':>8} {'연상환여력':>10} {'엑시트':>8}")
    for row in res["band_table"]:
        ey = f"{row['exit_years']:.1f}년" if row["exit_years"] else "불가"
        a(
            f"  {row['monthly_rev_eok']:6.1f}억 "
            f"{row['one_takehome_man']:7.0f}만 "
            f"{row['couple_takehome_man']:7.0f}만 "
            f"{row['annual_capacity_eok']:8.1f}억 "
            f"{ey:>8}"
        )
    a("")

    a("[9] 물리 그리드 (의사10·28일·util 100% 가정 — 상한 점검)")
    a(f"  {'ppd':>4} {'객단가':>6} {'일환자':>6} {'월매출':>8} {'부부실수령':>10} {'7년':>4}")
    for row in res["physical_grid"]:
        if row["ticket_man"] not in (14, 15):
            continue
        ey = f"{row['exit_years']:.1f}" if row["exit_years"] else "—"
        hit = "Y" if row["hits_7y"] else "N"
        a(
            f"  {row['ppd']:4d} "
            f"{row['ticket_man']:5d}만 "
            f"{row['daily_patients']:5d} "
            f"{row['monthly_rev_eok']:6.1f}억 "
            f"{row['couple_takehome_man']:8.0f}만 "
            f"{hit:>4} ({ey})"
        )
    a("")

    a("[10] 번아웃/하위20% 스트레스")
    s = res["burnout_stress_bottom20"]
    a(f"  하위20% 월매출 중앙 {s['monthly_rev_p50_eok']:.2f}억")
    a(f"  부부 실수령 중앙    {s['couple_th_p50_man']:.0f}만")
    a(f"  10년 완제 확률      {s['prob_exit_within_10y']*100:.1f}%")
    a(f"  상환여력≤0 확률     {s['prob_negative_capacity']*100:.1f}%")
    a("")

    a("[한계]")
    a("  · X(트위터) MCP 미인증 → SNS 보정 불가. 공개 peer만 사용.")
    a("  · Medigate 로컬 prior는 비공개라 peer 배수 참고용.")
    a("  · 이자·연대보증·'매출90%' 정의·OPEX 부담주체 변경 시 전면 재계산.")
    a("=" * 72)
    return "\n".join(lines)


def validate_formula() -> None:
    """대화 확정 앵커와 식 정합 검증."""
    # F=58억 → 운영 BEP 월 8.055…억 ≈ 8.1억
    assert abs(bep_monthly(58 * EOK) / EOK - 58 / 0.6 / 12) < 1e-9
    assert abs(bep_monthly(58 * EOK) / EOK - 8.055555) < 1e-4
    # F=70억 → 월 9.722…억
    assert abs(bep_monthly(70 * EOK) / EOK - 70 / 0.6 / 12) < 1e-9
    # 실수령 계수
    th = take_home_monthly(10 * EOK, tax_rate=0.38)
    assert abs(th["coeff_one"] - 0.031) < 1e-12
    assert abs(th["couple_after_tax"] / (10 * EOK) - 0.062) < 1e-12
    # 7년 완제: F=70, need (70+90/7)/0.6/12
    expect = (70 + 90 / 7) / 0.6 / 12
    assert abs(bep_monthly(70 * EOK, 7) / EOK - expect) < 1e-9


def anchor_scenarios(fixed_annual: float) -> list[dict[str, Any]]:
    """대화 앵커 매출을 같은 식에 재투영."""
    anchors = [
        ("채팅 EV", 6.4),
        ("결제 하한", 6.8),
        ("물리 Base(25×14만)", 9.8),
        ("패키지 중심", 9.2),
        ("운영 BEP(중앙F)", bep_monthly(fixed_annual) / EOK),
        ("7년 완제선", bep_monthly(fixed_annual, 7) / EOK),
        ("자기신고", 12.1),
    ]
    rows = []
    for name, m in anchors:
        mr = m * EOK
        cap = repayment_capacity_annual(mr * 12, fixed_annual)
        th = take_home_monthly(mr)
        rows.append(
            {
                "name": name,
                "monthly_rev_eok": round(m, 2),
                "one_man": th["one_after_tax"] / MAN,
                "couple_man": th["couple_after_tax"] / MAN,
                "annual_capacity_eok": cap / EOK,
                "exit_years": (years_to_exit(cap) if cap > 0 else None),
            }
        )
    return rows


def main() -> None:
    validate_formula()
    res = run_monte_carlo(50_000)
    f_med = res["deterministic_bep_at_median_fixed"]["fixed_median_annual_eok"] * EOK
    res["anchor_scenarios"] = anchor_scenarios(f_med)
    report = print_report(res)
    # append anchors to report
    extra = ["", "[11] 앵커 재투영 (중앙 고정비)",
             f"  {'앵커':16s} {'월매출':>8} {'1인':>8} {'부부':>8} {'엑시트':>8}"]
    for row in res["anchor_scenarios"]:
        ey = f"{row['exit_years']:.1f}년" if row["exit_years"] else "불가"
        extra.append(
            f"  {row['name']:16s} {row['monthly_rev_eok']:6.2f}억 "
            f"{row['one_man']:7.0f}만 {row['couple_man']:7.0f}만 {ey:>8}"
        )
    report = report + "\n".join(extra) + "\n"
    print(report)

    out_dir = Path("/workspace")
    (out_dir / "tonz_model_results.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    (out_dir / "tonz_model_report.txt").write_text(report, encoding="utf-8")

    # 요약 마크다운
    bep = res["deterministic_bep_at_median_fixed"]
    p = res["probabilities"]
    c = res["takehome"]["couple_man"]
    o = res["takehome"]["one_man"]
    r = res["revenue_monthly_eok"]
    md = f"""# 톤즈 부평점 BEP·실수령·엑시트 정밀 추정

코딩 몬테카를로 **50,000 paths** (시드 20260817).  
확정 식: `연 상환여력 = 매출×0.60 − F`, `1인 세후 = 월매출×3.1%`, `부부 = ×6.2%`.

## 핵심 결과

| 항목 | 수치 |
|------|------|
| 고정비 중앙값 (직원 50명 포함) | **{bep['fixed_median_annual_eok']:.1f}억/년** |
| 운영 손익분기 | 월 **{bep['operating_bep_monthly_eok']:.2f}억** |
| 7년 완제 선 | 월 **{bep['exit_7y_monthly_eok']:.2f}억** |
| 6년 완제 선 | 월 **{bep['exit_6y_monthly_eok']:.2f}억** |
| 모델 월매출 중앙(p50) | **{r['p50']:.2f}억** (p25–p75: {r['p25']:.2f}–{r['p75']:.2f}) |
| 부부 월 실수령 중앙 | **{c['p50']:.0f}만** (p25–p75: {c['p25']:.0f}–{c['p75']:.0f}) |
| 1인 월 실수령 중앙 | **{o['p50']:.0f}만** |
| 7년 내 완제 확률 | **{p['exit_within_7y']*100:.1f}%** |
| 10년 내 완제 확률 | **{p['exit_within_10y']*100:.1f}%** |
| 운영 흑자 확률 | **{p['operating_surplus']*100:.1f}%** |

## 해석

- **월급(선취 10%)은 매출만 되면 나옴.** 병원이 적자여도 선취가 유지되면 부부 실수령은 발생.
- **6–7년 엑시트는 월 ~{bep['exit_7y_monthly_eok']:.1f}억 이상이 필요.** 물리적으로는 의사 10명 × 일 28명 × 객단가 15만 근처.
- **현실 분포 중앙은 그 선보다 낮음** → 월급은 나오되 소유권 확보는 확률 게임.
- 응급의학 DN-OOOO 월 3,000만 대비, 모델 1인 p50은 대체로 **낮거나 비슷**하고 3,000만 초과 확률은 낮음.

## Peer 보정

- 데일리팜 부평역 피부과 평균 월 1.21억, 국세청 피부·비뇨기과 연 12.7억(월 ~1.06억).
- 모델 중앙 매출은 부평 평균의 약 **{res['peer_multiples_at_median_rev']['vs_bupyeong_derm_avg']:.0f}배** (대형·다인원 네트워크 전제).
- X MCP는 이 환경에서 인증 불가로 SNS 보정 미반영.

## 재현

```bash
python3 tonz_bep_model.py
```

산출물: `tonz_model_results.json`, `tonz_model_report.txt`
"""
    (out_dir / "README.md").write_text(md, encoding="utf-8")


if __name__ == "__main__":
    main()
