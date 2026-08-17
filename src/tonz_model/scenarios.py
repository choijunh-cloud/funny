"""시나리오·스트레스 테스트·민감도(토네이도).

계약서 미확인 조항이 이 딜의 분산을 지배하기 때문에,
'조항이 이렇게 적혀 있으면 결과가 이렇게 바뀐다'를 각각 돌려본다.
"""

from __future__ import annotations

import dataclasses
from typing import Callable

from .params import ModelParams, replace_nested
from .simulate import simulate, summarize

Mutator = Callable[[ModelParams], ModelParams]


def _chain(*muts: Mutator) -> Mutator:
    def f(p: ModelParams) -> ModelParams:
        for m in muts:
            p = m(p)
        return p

    return f


def _set(path: str, value):
    return lambda p: replace_nested(p, path, value)


SCENARIOS: dict[str, tuple[str, Mutator]] = {
    "base": ("기준 (무이자 90억 캡, 10% 선취, 직원 50명)", lambda p: p),
    "interest_6pct": (
        "계약에 이자 6% (총 지불 113억 상당)",
        _set("deal.interest_annual", 0.06),
    ),
    "profit_split": (
        "'매출 90%'가 아니라 '정산이익의 90%'인 경우",
        _set("deal.waterfall", "profit_split"),
    ),
    "deficit_to_balance": (
        "적자달의 손실이 원금에 얹히는 구조",
        _set("deal.deficit_adds_to_balance", True),
    ),
    "no_guarantee": ("연대보증 없음", _set("deal.personal_guarantee", False)),
    "founder_stays": (
        "창업자 잔류가 계약상 의무 (이탈 없음)",
        _set("risk.founder_exit_annual", 0.0),
    ),
    "founder_exits_y2": (
        "창업자 조기 이탈 (연 40% 해저드)",
        _set("risk.founder_exit_annual", 0.40),
    ),
    "doctor_exodus": (
        "봉직의 이탈 급증 (연 50%) + 채용난",
        _chain(_set("risk.doctor_attrition_annual", 0.50), _set("risk.hire_success_monthly", 0.35)),
    ),
    "price_war": (
        "객단가 20% 하락 (경쟁 진입)",
        _chain(_set("capacity.ticket_median", 11.2), _set("risk.price_war_annual", 0.25)),
    ),
    "demand_shock": (
        "환자 수요 20% 감소",
        _set("demand.monthly_patients_median", 5_238.0),
    ),
    "clinic_bears_deficit": (
        "운영 적자를 명의자(부부)가 메우는 구조",
        _set("deal.deficit_bearer", "clinic"),
    ),
    "couple_share_7": (
        "부부 선취를 7%로 낮춰 상환 가속",
        _set("deal.couple_share", 0.07),
    ),
    "couple_share_5": (
        "부부 선취 5% (월급 포기하고 소유권 우선)",
        _set("deal.couple_share", 0.05),
    ),
    "lean_staffing": (
        "인력 램프업 (직원 32명으로 시작)",
        _chain(_set("cost.staff_headcount", 32), _set("cost.marketing_rate", 0.06)),
    ),
    "heavy_staffing": (
        "직원 58명 + 급여 인플레",
        _chain(_set("cost.staff_headcount", 58), _set("cost.staff_avg_monthly_pay", 420.0)),
    ),
    "schedule_normalized": (
        "부부 주 5일 근무로 정상화 (월 8일 휴무)",
        _chain(_set("capacity.couple_days_per_month", 22.0), _set("risk.burnout_base_annual", 0.06)),
    ),
    "strong_brand": (
        "브랜드/체인 시너지 강함 (수요 +15%, 객단가 +10%)",
        _chain(
            _set("demand.monthly_patients_median", 7_530.0),
            _set("capacity.ticket_median", 15.4),
        ),
    ),
    "bull": (
        "낙관: 자기신고 수준(연 145억) 재현",
        _chain(
            _set("demand.monthly_patients_median", 7_860.0),
            _set("capacity.ticket_median", 17.0),
        ),
    ),
    "revenue_150": (
        "실측 매출이 연 150억대인 경우 (수요 9,800명/월 + 객단가 16만)",
        _chain(
            _set("demand.monthly_patients_median", 9_800.0),
            _set("capacity.ticket_median", 16.0),
        ),
    ),
    "revenue_150_share7": (
        "연 150억대 + 부부 선취 7% 재협상",
        _chain(
            _set("demand.monthly_patients_median", 9_800.0),
            _set("capacity.ticket_median", 16.0),
            _set("deal.couple_share", 0.07),
        ),
    ),
    "legal_crackdown": (
        "MSO 구조 단속 강화 (적발 해저드 연 6%)",
        _chain(_set("risk.sham_clinic_annual", 0.06), _set("risk.tax_attribution_annual", 0.05)),
    ),
    "worst_contract": (
        "최악 조합: 이자 6% + 적자 원금가산 + 연대보증",
        _chain(
            _set("deal.interest_annual", 0.06),
            _set("deal.deficit_adds_to_balance", True),
            _set("deal.personal_guarantee", True),
        ),
    ),
    "best_contract": (
        "최선 조합: 무이자 캡 + 연대보증 없음 + 창업자 잔류 의무",
        _chain(
            _set("deal.personal_guarantee", False),
            _set("risk.founder_exit_annual", 0.0),
            _set("deal.unpaid_forgiven_prob", 0.6),
            _set("deal.unpaid_claimed_prob", 0.0),
            _set("deal.unpaid_extended_prob", 0.4),
        ),
    ),
}


TORNADO_KNOBS: list[tuple[str, str, float, float]] = [
    # (파라미터 경로, 표시명, low, high)
    ("demand.monthly_patients_median", "월 환자수(수요)", 5_200.0, 7_900.0),
    ("capacity.ticket_median", "객단가", 12.0, 16.5),
    ("deal.couple_share", "부부 선취율", 0.06, 0.12),
    ("cost.staff_headcount", "직원 수", 40, 58),
    ("cost.staff_avg_monthly_pay", "직원 평균급여", 340.0, 430.0),
    ("cost.doctor_incentive_rate", "봉직의 인센티브율", 0.18, 0.32),
    ("cost.marketing_rate", "마케팅 비율", 0.05, 0.10),
    ("cost.consumables_rate", "재료비율", 0.17, 0.26),
    ("cost.rent_per_pyeong_month", "평당 임대료", 9.0, 15.0),
    ("capacity.room_turns_per_day", "시술실 회전율", 12.0, 20.0),
    ("deal.interest_annual", "이자율", 0.0, 0.06),
    ("risk.doctor_attrition_annual", "봉직의 이직률", 0.20, 0.45),
    ("risk.founder_exit_annual", "창업자 이탈 해저드", 0.0, 0.30),
    ("risk.sham_clinic_annual", "사무장병원 적발 해저드", 0.005, 0.05),
]


def run_scenarios(base: ModelParams, n_paths: int | None = None) -> dict[str, dict]:
    out = {}
    for key, (label, mut) in SCENARIOS.items():
        p = mut(base)
        res = simulate(p, n_paths=n_paths)
        s = summarize(res)
        s["설명"] = label
        out[key] = s
    return out


BREAKEVEN_LEVERS: list[tuple[str, str, float, float, str]] = [
    # (경로, 표시명, 탐색 하한, 탐색 상한, 단위)
    ("demand.monthly_patients_median", "월 환자수", 6_548.0, 16_000.0, "명/월"),
    ("capacity.ticket_median", "객단가", 14.0, 32.0, "만원"),
    ("cost.staff_headcount", "직원 수", 50.0, 12.0, "명"),
    ("deal.couple_share", "부부 선취율", 0.10, 0.0, "비율"),
    ("capacity.treatment_rooms", "시술실 수", 22.0, 60.0, "실"),
]


def breakeven_conditions(
    base: ModelParams,
    target_prob: float = 0.5,
    metric: str = "P(7년내 완제)",
    n_paths: int = 4_000,
    iters: int = 9,
) -> list[dict]:
    """'무엇이 참이어야 이 딜이 반반이 되는가'를 역산한다.

    레버 하나씩만 움직여서 목표 확률(기본 50%)에 도달하는 값을 이분법으로 찾는다.
    다른 레버가 고정된 단독 조건이므로, 실제로는 조합이 필요하다.
    """
    rows = []
    for path, label, start, end, unit in BREAKEVEN_LEVERS:
        lo, hi = start, end  # lo=현재값(확률 낮음), hi=극단값(확률 높음)
        best = None
        for _ in range(iters):
            mid = (lo + hi) / 2.0
            val = mid if "headcount" not in path else round(mid)
            prob = summarize(simulate(replace_nested(base, path, val), n_paths=n_paths))[metric]
            if prob < target_prob:
                lo = mid
            else:
                hi = mid
                best = (val, prob)
        rows.append(
            {
                "레버": label,
                "현재값": start,
                "필요값": best[0] if best else None,
                "달성확률": best[1] if best else None,
                "단위": unit,
                "도달불가": best is None,
                "배율": (best[0] / start) if best and start else None,
            }
        )
    return rows


def tornado(base: ModelParams, n_paths: int = 6_000, metric: str = "P(7년내 완제)") -> list[dict]:
    rows = []
    center = summarize(simulate(base, n_paths=n_paths))[metric]
    for path, label, low, high in TORNADO_KNOBS:
        lo = summarize(simulate(replace_nested(base, path, low), n_paths=n_paths))[metric]
        hi = summarize(simulate(replace_nested(base, path, high), n_paths=n_paths))[metric]
        rows.append(
            {
                "파라미터": label,
                "경로": path,
                "low": low,
                "high": high,
                "metric_low": lo,
                "metric_high": hi,
                "swing": abs(hi - lo),
                "center": center,
            }
        )
    rows.sort(key=lambda r: r["swing"], reverse=True)
    return rows
