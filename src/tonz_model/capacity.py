"""물리적 진료 용량 → 매출 상한 역산.

'월 10억을 하려면 하루 몇 명을 봐야 하는가'를 세 개의 병목으로 교차 검증한다.
  1) 의사 병목  : 의사-일수 × 1인 1일 환자수
  2) 시설 병목  : 시술실 수 × 실당 회전
  3) 인력 병목  : 시술 인력 수 × 1인 1일 시술 건수
셋 중 가장 낮은 것이 진짜 천장이다.
"""

from __future__ import annotations

from dataclasses import dataclass

from .params import CapacityParams


@dataclass(frozen=True)
class CapacityProfile:
    doctor_days_per_month: float
    doctor_limited_patients_day: float
    room_limited_patients_day: float
    staff_limited_patients_day: float
    binding_constraint: str
    max_patients_day: float
    max_patients_month: float

    def max_revenue_month(self, ticket: float) -> float:
        return self.max_patients_month * ticket


def profile(cap: CapacityParams, n_employed: int | None = None) -> CapacityProfile:
    n_emp = cap.employed_doctors if n_employed is None else n_employed
    doctor_days = (
        cap.couple_doctors * cap.couple_days_per_month
        + n_emp * cap.employed_days_per_month
    )
    doctor_limited_day = doctor_days * cap.ppd_hard_cap / cap.open_days_per_month
    room_limited_day = cap.treatment_rooms * cap.room_turns_per_day
    staff_limited_day = cap.clinical_staff * cap.treatments_per_staff_day

    limits = {
        "의사": doctor_limited_day,
        "시술실": room_limited_day,
        "시술인력": staff_limited_day,
    }
    binding = min(limits, key=limits.get)
    max_day = limits[binding]
    return CapacityProfile(
        doctor_days_per_month=doctor_days,
        doctor_limited_patients_day=doctor_limited_day,
        room_limited_patients_day=room_limited_day,
        staff_limited_patients_day=staff_limited_day,
        binding_constraint=binding,
        max_patients_day=max_day,
        max_patients_month=max_day * cap.open_days_per_month,
    )


def patients_needed(revenue_month: float, ticket: float, cap: CapacityParams) -> dict:
    """목표 월매출 -> 필요 환자수 역산."""
    per_month = revenue_month / ticket
    per_day = per_month / cap.open_days_per_month
    prof = profile(cap)
    per_doctor_day = per_month / prof.doctor_days_per_month
    return {
        "월_환자수": per_month,
        "일_환자수": per_day,
        "의사1인_1일_환자수": per_doctor_day,
        "시설_대비_가동률": per_day / prof.max_patients_day,
        "의사_한계_대비": per_doctor_day / cap.ppd_hard_cap,
        "물리적_실현가능": per_day <= prof.max_patients_day
        and per_doctor_day <= cap.ppd_hard_cap,
    }


def sustainable_revenue(cap: CapacityParams, ppd: float, ticket: float) -> float:
    """주어진 생산성/객단가에서 실제 낼 수 있는 월매출 (병목 반영)."""
    prof = profile(cap)
    patients = min(prof.doctor_days_per_month * ppd, prof.max_patients_month)
    return patients * ticket
