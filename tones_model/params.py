"""모델 가정. 단위: 억원(연/월 명시), 만원(급여·객단가), 원(세무)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class StaffRole:
    name: str
    headcount: int
    monthly_pay_man: float  # 세전 월급여, 만원
    burden: float = 1.22    # 4대보험 사업주 + 퇴직금 + 식대


@dataclass(frozen=True)
class ModelParams:
    # ── 딜 구조 ──────────────────────────────────────────────
    debt_eok: float = 90.0
    couple_share: float = 0.10
    mso_share: float = 0.90
    interest_rate: float = 0.0          # 무이자 기본. 민감도에서 0.06 사용
    contract_years: int = 10
    couple_equity_eok: float = 10.0     # 부부 각 5억

    # ── 검증식 계수 (이전 합의) ──────────────────────────────
    verified_person_net_rate: float = 0.031  # 월매출×3.1% = 1인 세후

    # ── 변동비 (매출 대비) ──────────────────────────────────
    material_rate: float = 0.22         # 보톡스·필러·레이저 소모품
    card_fee_rate: float = 0.022
    consumable_rate: float = 0.015
    variable_ads_rate: float = 0.043    # 퍼포먼스 광고
    # 합 = 0.30

    # ── 고정비 중앙값 ────────────────────────────────────────
    fixed_cost_eok: float = 70.0        # 연, 직원50+의사+임대+고정마케팅+기타
    fixed_lean_eok: float = 64.0
    fixed_heavy_eok: float = 78.0

    # ── 인력 ────────────────────────────────────────────────
    paid_doctors: int = 8               # 부부·황아름 제외 페이닥터
    couple_doctors: int = 2
    hwang_fte: float = 1.0              # 황아름 잔류 FTE
    staff_headcount: int = 50
    paid_doctor_monthly_man: float = 2300.0   # 총지급, 만원 (net 1,700~2,200 대응)
    hwang_monthly_man: float = 2800.0
    doctor_burden: float = 1.15

    # ── 물리적 수용력 ────────────────────────────────────────
    clinic_hours: float = 12.0          # 10:00–22:00
    rooms: int = 20
    avg_procedure_min: float = 18.0     # 토닝·보톡스 중심 볼륨
    utilization: float = 0.72
    work_days_high: int = 28            # 월 2일 휴무
    work_days_normal: int = 24          # 주 6일
    ticket_man: float = 14.5            # 객단가 중앙, 만원
    ppd_base: float = 25.0              # 의사 1인당 일 환자 (현실 Base)

    # ── 상권·피어 앵커 (2026-08 공개/로컬 데이터) ────────────
    peer_national_derm_monthly: float = 1.06   # 국세청 피부·비뇨 월평균, 억
    peer_bupyeong_500m: float = 1.21
    peer_bupyeong5_avg: float = 2.98
    peer_bupyeong5_p80: float = 6.82
    peer_select_1km: float = 1.61
    peer_toxnfill_avg: float = 4.2

    # ── 물가·임금 ────────────────────────────────────────────
    wage_inflation: float = 0.045
    ticket_inflation: float = 0.02
    rent_inflation: float = 0.03

    # ── 시뮬레이션 ──────────────────────────────────────────
    n_paths: int = 40_000
    seed: int = 42
    horizon_years: int = 10
    months_per_year: int = 12

    # 의사 이탈·채용
    doctor_attrition: float = 0.18      # 연간
    hire_lag_months: int = 3
    min_paid_doctors: int = 5
    max_paid_doctors: int = 12

    # 황아름 잔류 위험
    hwang_annual_leave_hazard: float = 0.08
    hwang_revenue_lift: float = 0.12    # 잔류 시 매출 +12%

    # 번아웃: 월 2일 휴무 지속 시 3년차부터 근무일·생산성 하락
    burnout_start_year: int = 3
    burnout_ppd_drag: float = 0.04      # 연 4%p 누적, 상한 20%
    burnout_day_drop: int = 2           # 3년차부터 격년 −2일

    # 계절성 (1–12월 배수, 평균≈1)
    seasonality: Tuple[float, ...] = (
        0.86, 0.88, 1.04, 1.06, 1.08, 0.96,
        0.92, 0.94, 1.10, 1.12, 1.04, 1.00,
    )

    # 응급의 비교
    em_net_monthly_man: float = 3000.0
    em_work_pattern: str = "DN-OOOO"

    staff_roles: Tuple[StaffRole, ...] = field(default_factory=lambda: (
        StaffRole("실장/부실장", 2, 500),
        StaffRole("상담실장", 2, 450),
        StaffRole("상담사", 10, 350),
        StaffRole("간호/PA", 14, 380),
        StaffRole("피부관리/테라피", 10, 320),
        StaffRole("데스크/코디", 6, 300),
        StaffRole("원무/행정", 3, 320),
        StaffRole("마케팅/디자인", 2, 350),
        StaffRole("시설/미화", 1, 250),
    ))

    @property
    def variable_rate(self) -> float:
        return (
            self.material_rate
            + self.card_fee_rate
            + self.consumable_rate
            + self.variable_ads_rate
        )

    @property
    def mso_net_rate(self) -> float:
        """MSO 유입 − 변동비. 기본 0.90 − 0.30 = 0.60."""
        return self.mso_share - self.variable_rate

    @property
    def treating_doctors(self) -> float:
        """진료 가능 의사 FTE (페이 + 부부 + 황아름)."""
        return self.paid_doctors + self.couple_doctors + self.hwang_fte

    def staff_labor_eok(self) -> float:
        total_man_year = 0.0
        for r in self.staff_roles:
            total_man_year += r.headcount * r.monthly_pay_man * 12 * r.burden
        return total_man_year / 10_000  # 만원 → 억

    def doctor_labor_eok(self) -> float:
        paid = self.paid_doctors * self.paid_doctor_monthly_man * 12 * self.doctor_burden
        hwang = self.hwang_fte * self.hwang_monthly_man * 12 * self.doctor_burden
        return (paid + hwang) / 10_000

    def rent_eok(self) -> float:
        # 338평 × 월 12만 × 12 + 관리비 ≈ 7.0억 중앙
        return 7.0

    def fixed_marketing_eok(self) -> float:
        return 4.0

    def other_fixed_eok(self) -> float:
        return 5.0

    def built_fixed_eok(self) -> float:
        return (
            self.staff_labor_eok()
            + self.doctor_labor_eok()
            + self.rent_eok()
            + self.fixed_marketing_eok()
            + self.other_fixed_eok()
        )

    def cost_breakdown(self) -> Dict[str, float]:
        return {
            "직원50_인건비": round(self.staff_labor_eok(), 2),
            "페이닥터_인건비": round(
                self.paid_doctors * self.paid_doctor_monthly_man * 12 * self.doctor_burden / 10_000, 2
            ),
            "황아름_인건비": round(
                self.hwang_fte * self.hwang_monthly_man * 12 * self.doctor_burden / 10_000, 2
            ),
            "임대_관리": round(self.rent_eok(), 2),
            "고정마케팅": round(self.fixed_marketing_eok(), 2),
            "기타고정": round(self.other_fixed_eok(), 2),
            "분해합계": round(self.built_fixed_eok(), 2),
            "모델고정비_중앙": self.fixed_cost_eok,
        }


# 미용 피부과 계절성 검증용 합
assert abs(sum(ModelParams().seasonality) / 12 - 1.0) < 0.02
