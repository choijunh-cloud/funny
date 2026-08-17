"""모델 파라미터 일체.

원칙
----
1. 모든 숫자는 (a) 관측된 값, (b) 업계 관행에서 나온 추정, (c) 순수 판단
   중 어디에 속하는지 `note` 로 표시한다.
2. 불확실한 값은 점추정이 아니라 분포(중앙값 + 로그정규 sigma 또는 범위)로 둔다.
3. 단위: 금액=만원, 기간=월.

핵심 관측치 (대화/실사에서 확인된 것)
-----------------------------------
- 인수구조: 총 100억 (부부 현금 10억 = 각 5억, 잔여 90억은 매출 연동 상환)
- 정산: 매출의 10%를 부부가 선취, 90%는 MSO(본사) 귀속
- 목표: 6~7년 내 90억 완제 후 소유권 이전 (10년 계약)
- 규모: 실면적 약 338평(1,119㎡), 직원 약 50명, 진료 의사 10명 수준
- 근무: 부부는 월 2일 휴무 (주 6.5일)
- 창업자(황아름) 잔류: 부원장/브랜드 총괄로 계속 근무
- 상권: 부평5동 피부과 평균 월 2.98억(인천 1위 상권), 상위 20% 6.82억,
        반경 1km 평균 1.61억, 중간값 0.94억
- 유사 네트워크: 톡스앤필 가맹 평균 월 4.2억
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any

from .units import from_eok


@dataclass(frozen=True)
class DemandParams:
    """환자 수요(=매출의 진짜 동인).

    공급(의사 수)이 아니라 수요를 1차 상태변수로 둔다.
    수요가 약하면 병원은 의사·직원을 줄여 대응하기 때문에,
    '의사 10명 고정 × 생산성' 모델은 하방 손실을 과대평가한다.

    캘리브레이션(calibration.py 참조): 실사 매출 앵커
        결제 하한 연 82억 / 패키지 중심 연 110억 / 자기신고 연 145억
    을 각각 p15 / p50 / p85 로 보고 로그정규를 적합한 뒤,
    객단가 중앙값 14만원으로 나눠 월 환자수 중앙값을 얻었다.
    """

    monthly_patients_median: float = 6_548.0  # 월 환자수 (≈ 234명/일)
    sigma: float = 0.21  # 경로별 이질성 (나머지 분산은 객단가 쪽)
    growth_sigma_annual: float = 0.06  # 경로별 성장률 드리프트
    growth_median_annual: float = 0.00  # 성숙 상권, 실질 무성장 가정


@dataclass(frozen=True)
class CapacityParams:
    """물리적 진료 용량. 매출의 상한을 결정한다."""

    couple_doctors: int = 2
    couple_days_per_month: float = 28.0  # 월 2일 휴무
    employed_doctors: int = 8  # 부부 제외 상주 의사 (정원)
    min_employed_doctors: int = 3  # 수요 부진 시 축소 하한
    employed_days_per_month: float = 22.0  # 주 5.5일 가정

    # 의사 1인 1일 목표 부하(이 이상이면 증원, 이하면 감원)
    ppd_target: float = 26.0
    ppd_hard_cap: float = 45.0  # 의사 1인 물리적 한계(시술 위임 극대화)
    # 참고용 점추정 (결정론 계산에서 사용)
    ppd_median: float = 26.0
    ppd_sigma: float = 0.21

    # 시설 병목: 시술실 수 × 실당 1일 회전
    treatment_rooms: int = 22
    room_turns_per_day: float = 16.0

    # 인력 병목: 시술 가능 인력(간호/조무) 수 × 1인 1일 시술 건수
    clinical_staff: int = 30  # 정원 50명 기준 시술 인력 수
    clinical_staff_ratio: float = 0.60  # 전체 직원 중 시술 인력 비중
    treatments_per_staff_day: float = 12.0

    open_days_per_month: float = 28.0  # 연중무휴 가동

    # 객단가(결제 기준). 쁘띠/레이저 혼합, 패키지 선결제 포함.
    ticket_median: float = 14.0  # 만원
    ticket_sigma: float = 0.18
    ticket_drift_annual: float = 0.0  # 명목 객단가 중앙 드리프트
    ticket_drift_sigma: float = 0.02  # 경로별 가격 추세 불확실성


@dataclass(frozen=True)
class CostParams:
    """비용 구조. 단위 만원."""

    # --- 인건비 (직원 50명) ---
    staff_headcount: int = 50
    staff_avg_monthly_pay: float = 380.0  # 간호/조무/상담실장/코디/관리 평균
    staff_burden_multiple: float = 1.18  # 4대보험·퇴직충당·식대 등 부대비용
    # 수요에 맞춘 인력 리사이징 (실무적으로 감원은 느리고 하한이 있다)
    staff_min_ratio: float = 0.55  # 정원 대비 축소 하한
    staff_max_ratio: float = 1.15
    staff_adjust_speed: float = 0.12  # 월별 목표 수렴 속도

    # --- 봉직의 보수: 최저보장 + 인센티브 중 큰 값 (semi-variable) ---
    doctor_net_guarantee: float = 1_900.0  # 세후 보장(월). 톤즈 공고 1,700~2,200 중앙
    doctor_gross_up: float = 1.30  # 세후보장 -> 병원 부담 실비용 배수
    doctor_incentive_rate: float = 0.25  # 본인 진료매출의 %

    # --- 임대 ---
    pyeong: float = 338.0
    rent_per_pyeong_month: float = 12.0  # 부평역 역세권 고층부
    management_fee_ratio: float = 0.25  # 임대료 대비 관리비/공과

    # --- 마케팅: 하한 있는 변동비 ---
    marketing_rate: float = 0.07  # 매출 대비
    marketing_floor_annual: float = from_eok(3.0)

    # --- 기타 고정비 (전산·보험·유지보수·세무·리스·감가 등) ---
    other_fixed_annual: float = from_eok(6.0)

    # --- 변동비: 재료 + 결제수수료 + 플랫폼 수수료 ---
    consumables_rate: float = 0.21  # 톡신/필러/레이저 소모품
    card_fee_rate: float = 0.025
    platform_fee_rate: float = 0.025  # 강남언니·바비톡 등 유입 수수료

    # --- 인플레이션 ---
    wage_inflation_annual: float = 0.035
    rent_inflation_annual: float = 0.02

    @property
    def variable_rate(self) -> float:
        return self.consumables_rate + self.card_fee_rate + self.platform_fee_rate

    @property
    def staff_annual(self) -> float:
        return (
            self.staff_headcount
            * self.staff_avg_monthly_pay
            * 12.0
            * self.staff_burden_multiple
        )

    @property
    def rent_annual(self) -> float:
        return (
            self.pyeong
            * self.rent_per_pyeong_month
            * 12.0
            * (1.0 + self.management_fee_ratio)
        )


@dataclass(frozen=True)
class DealParams:
    """계약 구조."""

    principal: float = from_eok(90.0)  # 90억
    couple_equity: float = from_eok(10.0)  # 부부 현금 10억 (각 5억)
    couple_share: float = 0.10  # 매출의 10% 선취
    contract_years: int = 10
    interest_annual: float = 0.0  # 무이자 캡 가정 (계약서 미확인 → 시나리오로 검증)

    # 워터폴 모드
    #  "gross_mso_pays_opex": 매출 90%가 MSO로, MSO가 전체 OPEX 부담 (기준)
    #  "profit_split":        OPEX 차감 후 이익의 90%를 MSO가 가져감
    waterfall: str = "gross_mso_pays_opex"

    # MSO 정산이 적자인 달의 처리
    #   "mso"    : 본사가 흡수 (부부에게 유리, 기본 가정)
    #   "clinic" : 명의자인 부부가 메움 (선취분에서 차감 + 개인 채무 누적)
    deficit_bearer: str = "mso"
    deficit_adds_to_balance: bool = False  # True면 적자가 원금에 얹힘
    # 누적 적자가 이 수준을 넘으면 재협상 압력 발생 (부부 선취율 인하)
    renegotiation_deficit_trigger: float = from_eok(10.0)
    renegotiation_annual_prob: float = 0.5
    renegotiated_couple_share: float = 0.07

    # 완제 후: 소유권 이전되어 잔여이익 전부 부부 귀속
    post_payoff_full_profit: bool = True
    personal_guarantee: bool = True  # 연대보증 (미확인 → 기본 True로 보수적)

    # 10년 만기까지 미완제일 때의 잔액 처리 (계약서 미확인 → 확률로 처리)
    unpaid_forgiven_prob: float = 0.35
    unpaid_extended_prob: float = 0.45  # 연장(= 계속 상환, 소유권 유예)
    unpaid_claimed_prob: float = 0.20  # 잔액 청구 (연대보증 시 개인 재산)


@dataclass(frozen=True)
class RiskParams:
    """이벤트 해저드. 전부 판단 기반 prior — 토네이도 분석 대상."""

    # 봉직의 이직: 미용 GP 연 이직률 30% 수준
    doctor_attrition_annual: float = 0.30
    hire_success_monthly: float = 0.55  # 결원 1명을 그 달에 채울 확률
    # 창업자(황아름) 이탈
    founder_exit_annual: float = 0.12
    founder_exit_revenue_hit: float = 0.10  # 이탈 시 매출 영구 손실률(중앙)
    # 부부 번아웃: 월 2일 휴무 지속에 따른 누적 해저드
    burnout_base_annual: float = 0.14
    burnout_rampup_years: float = 4.0  # 누적될수록 해저드 상승
    burnout_revenue_hit: float = 0.08  # 근무 정상화에 따른 매출 감소
    # 의료사고(세데이션 포함): 경미/중대
    incident_minor_annual: float = 0.10
    incident_minor_cost: float = from_eok(0.5)
    incident_major_annual: float = 0.02
    incident_major_cost: float = from_eok(5.0)
    incident_major_revenue_hit: float = 0.15
    # 사무장병원(의료법 33조) 적발 -> 경로 종료 + 환수
    sham_clinic_annual: float = 0.015
    sham_clawback: float = from_eok(20.0)
    # 명의자 과세 리스크: MSO 지급분 필요경비 부인
    tax_attribution_annual: float = 0.02
    tax_attribution_cost: float = from_eok(15.0)
    # 경쟁 진입/가격 경쟁
    price_war_annual: float = 0.10
    price_war_ticket_hit: float = 0.10
    # 누적 적자 누적 시 본사 판단에 의한 폐업/구조조정
    closure_deficit_trigger: float = from_eok(25.0)  # 병원 자체 누적손실 기준
    closure_annual_prob: float = 0.22

    # 월별 매출 노이즈(로그정규 sigma)
    monthly_noise_sigma: float = 0.09
    # 계절성: 1~12월 배수 (여름 비수기, 연말·연초 성수기)
    seasonality: tuple[float, ...] = (
        1.05, 1.02, 1.03, 1.00, 1.02, 0.95,
        0.92, 0.90, 0.98, 1.04, 1.08, 1.10,
    )
    # 인수 직후 램프: 명의 변경·창업자 지분 축소에 따른 초기 흔들림
    ramp_initial: float = 0.88
    ramp_months: float = 12.0


@dataclass(frozen=True)
class CareerParams:
    """비교 대상: 응급의학과 전문의 잔류 (Day-Night-Off×4)."""

    em_net_monthly: float = 3_000.0  # 세후 실수령
    em_hours_per_month: float = 124.0  # (Day 11h + Night 13h) × 5.17 사이클
    em_growth_annual: float = 0.02
    deal_hours_per_month: float = 268.0  # 28일 × 9.5시간 (진료+운영)
    discount_annual: float = 0.05
    horizon_years: int = 10
    # 완제 후 소유권 가치 = 정상화 EBITDA × 멀티플
    exit_multiple: float = 3.0
    # 병원이 문을 닫아도 의사는 다시 봉직으로 돌아간다 (1인 세후 월)
    fallback_net_monthly_per_person: float = 1_500.0


@dataclass(frozen=True)
class SimConfig:
    n_paths: int = 30_000
    horizon_months: int = 120
    seed: int = 20260817


@dataclass(frozen=True)
class ModelParams:
    demand: DemandParams = field(default_factory=DemandParams)
    capacity: CapacityParams = field(default_factory=CapacityParams)
    cost: CostParams = field(default_factory=CostParams)
    deal: DealParams = field(default_factory=DealParams)
    risk: RiskParams = field(default_factory=RiskParams)
    career: CareerParams = field(default_factory=CareerParams)
    sim: SimConfig = field(default_factory=SimConfig)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def replace_nested(params: ModelParams, path: str, value: Any) -> ModelParams:
    """'risk.founder_exit_annual' 같은 경로로 파라미터 하나만 바꾼 사본 생성."""
    import dataclasses

    group, attr = path.split(".")
    sub = getattr(params, group)
    new_sub = dataclasses.replace(sub, **{attr: value})
    return dataclasses.replace(params, **{group: new_sub})
