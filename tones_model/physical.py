"""물리적 환자 수용력: 의사 시간 · 룸 · 객단가."""

from __future__ import annotations

from typing import Dict, List

from tones_model.engine import ClinicEngine
from tones_model.params import ModelParams


def theoretical_ppd(p: ModelParams) -> Dict[str, float]:
    """의사 1인 이론 상한과 실용 상한."""
    slots = p.clinic_hours * 60 / p.avg_procedure_min
    practical = slots * p.utilization
    room_cap = p.rooms * (p.clinic_hours * 60 / p.avg_procedure_min) * 0.55
    return {
        "의사1인_이론슬롯": round(slots, 1),
        "의사1인_실용_이용률반영": round(practical, 1),
        "룸제약_일총환자": round(room_cap, 0),
        "의사10명_실용_일총": round(practical * p.treating_doctors, 0),
        "병목": "룸" if room_cap < practical * p.treating_doctors else "의사시간",
    }


def monthly_from_physical(
    ppd: float,
    ticket_man: float,
    doctors: float,
    work_days: int,
) -> float:
    """월매출(억) = 의사수 × 1인당일환자 × 객단가(만) × 가동일 / 10000."""
    return doctors * ppd * ticket_man * work_days / 10_000


def physical_matrix(engine: ClinicEngine) -> List[Dict]:
    p = engine.p
    rows = []
    for ppd in (18, 20, 22, 24, 25, 26, 28, 30, 32, 35):
        for ticket in (12, 13, 14, 14.5, 15, 16, 18):
            for days, day_label in ((p.work_days_high, "월2일휴무"), (p.work_days_normal, "주6일")):
                monthly = monthly_from_physical(ppd, ticket, p.treating_doctors, days)
                s = engine.analyze(monthly)
                rows.append({
                    "의사1인_일환자": ppd,
                    "객단가_만": ticket,
                    "가동": day_label,
                    "가동일": days,
                    "진료의사": p.treating_doctors,
                    "일총환자": round(ppd * p.treating_doctors),
                    "월매출_억": s.monthly_eok,
                    "부부_검증식_만": s.couple_verified_man,
                    "부부_실수령_만": s.couple_takehome_man,
                    "연상환_억": s.repay_eok,
                    "엑시트_년": s.exit_years,
                    "운영흑자": s.operating_ok,
                    "7년": s.exit_7,
                    "6년": s.exit_6,
                })
    return rows


def required_patients(engine: ClinicEngine) -> List[Dict]:
    p = engine.p
    targets = {
        "운영_손익분기": engine.operating_bep(),
        "10년_완제": engine.required_monthly(10),
        "7년_완제": engine.required_monthly(7),
        "6년_완제": engine.required_monthly(6),
    }
    rows = []
    for label, monthly in targets.items():
        for ticket in (12, 14, 14.5, 15, 16, 18):
            for days in (p.work_days_high, p.work_days_normal):
                daily = monthly * 10_000 / (ticket * days)
                rows.append({
                    "목표": label,
                    "필요_월매출_억": round(monthly, 2),
                    "객단가_만": ticket,
                    "가동일": days,
                    "필요_일환자": round(daily),
                    "의사1인_일환자": round(daily / p.treating_doctors, 1),
                    "실용상한대비": round(daily / (theoretical_ppd(p)["의사1인_실용_이용률반영"] * p.treating_doctors), 2),
                })
    return rows
