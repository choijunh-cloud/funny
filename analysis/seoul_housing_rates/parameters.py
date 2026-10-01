"""관측치와 시나리오 가정.

가격·전세는 다방 '2026년 2분기 아파트 다방여지도'(매일경제 2026-07-30)의
전용 84㎡ 실거래 평균이다. 서초·서울은 기사에 적힌 금액, 나머지 구는
기사에 적힌 서울 평균 대비 비율을 곱해 환산했다. 비율은 정수 퍼센트라
구별 가격은 대략 ±0.07억 안의 반올림 오차가 있다.

차주 연소득과 평균 주담대 약정액은 부동산R114 리서치랩 표
(연합뉴스 2025-08-31)다. 2025년 값이라 모델이 2026년 소득으로 올릴 때는
Assumptions.income_level_up 을 쓴다. 용산 소득이 강남과 같은 1억5,464만원으로
실린 것은 그 표의 숫자 그대로다.

금리 앵커
- 기준금리 3.00%: 2026-08-27 금통위.
- 주담대 가중평균 4.66%: 한은, 2026년 8월 신규취급액.
- 5년 고정 공시 상단 7.29%: 2026-09-15 5대 은행 범위 4.89~7.29%의 상단.
- 8월 평균에는 8월 27일 인상과 9월 은행채 급등이 덜 반영돼 있어
  평균 금리에만 pipeline 0.20%p를 더해 10월 초 현재 금리로 쓴다.
  공시 상단은 9월 15일 관찰값이라 pipeline을 다시 더하지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass


SEOUL_PRICE = 1_359_400_000
SEOUL_JEONSE = 733_420_000


def _from_index(price_pct: float, jeonse_pct: float) -> tuple[int, int]:
    return (
        round(SEOUL_PRICE * price_pct),
        round(SEOUL_JEONSE * jeonse_pct),
    )


@dataclass(frozen=True)
class District:
    name: str
    group: str
    price_84: int
    jeonse_84: int
    income_2025: int
    avg_mortgage_2025: int
    # 2026년 2분기 가격 / 2021~22년 매수가. 오래된 대출 잔액의 현재 LTV를 낮춘다.
    # 공식 구별 국평 지수로 잠근 값이 아니라 구간 가정이다.
    price_multiple_since_2021: float
    # 1보다 크면 같은 금리 충격에서 기대상승률을 더 크게 깎는다.
    expectation_beta: float
    # 보유 주택 중 사업자대출로 레버리지를 채운 코호트 비중. 공식 통계가 아니다.
    biz_share: float

    @property
    def jeonse_ratio(self) -> float:
        return self.jeonse_84 / self.price_84


def _d(
    name: str,
    group: str,
    price: int,
    jeonse: int,
    income_manwon: int,
    mortgage_manwon: int,
    multiple: float,
    expectation_beta: float,
    biz_share: float,
) -> District:
    return District(
        name=name,
        group=group,
        price_84=price,
        jeonse_84=jeonse,
        income_2025=income_manwon * 10_000,
        avg_mortgage_2025=mortgage_manwon * 10_000,
        price_multiple_since_2021=multiple,
        expectation_beta=expectation_beta,
        biz_share=biz_share,
    )


_GN_P, _GN_J = _from_index(2.21, 1.31)
_SP_P, _SP_J = _from_index(1.73, 1.29)
_YS_P, _YS_J = _from_index(1.55, 1.10)
_SD_P, _SD_J = _from_index(1.36, 1.14)
_MP_P, _MP_J = _from_index(1.24, 1.12)

DISTRICTS: tuple[District, ...] = (
    _d("강남구", "강남3구", _GN_P, _GN_J, 15_464, 48_362, 1.40, 1.15, 0.08),
    _d("서초구", "강남3구", 3_370_810_000, 1_177_140_000, 14_953, 46_541, 1.45, 1.20, 0.08),
    _d("송파구", "강남3구", _SP_P, _SP_J, 11_024, 35_000, 1.35, 1.05, 0.10),
    _d("용산구", "마용성", _YS_P, _YS_J, 15_464, 41_038, 1.65, 1.35, 0.12),
    _d("성동구", "마용성", _SD_P, _SD_J, 10_560, 37_081, 1.50, 1.10, 0.13),
    _d("마포구", "마용성", _MP_P, _MP_J, 9_626, 32_302, 1.30, 1.00, 0.15),
    _d("서울", "참고", SEOUL_PRICE, SEOUL_JEONSE, 9_475, 29_557, 1.35, 1.00, 0.12),
)


def mortgage_cap(price: float) -> int:
    """2025-10-16 이후 수도권·규제지역 구입 주담대 한도.

    15억 이하 6억, 15억 초과 25억 이하 4억, 25억 초과 2억.
    """
    if price <= 1_500_000_000:
        return 600_000_000
    if price <= 2_500_000_000:
        return 400_000_000
    return 200_000_000


@dataclass(frozen=True)
class Assumptions:
    psi: float = 0.08
    phi: float = 0.04
    conversion: float = 0.050
    beta_avg: float = 0.85
    beta_upper: float = 0.90
    anchor_avg: float = 0.0466
    pipeline_avg: float = 0.0020
    anchor_upper: float = 0.0729
    base_now: float = 0.0300
    hike: float = 0.0025
    biz_spread: float = 0.025
    income_level_up: float = 0.06
    income_pass_through: float = 0.40
    target_ltv_old: float = 0.65
    mortgage_ltv_old: float = 0.40
    target_ltv_recent: float = 0.55
    mortgage_abs_cap_recent: float = 600_000_000
    biz_cap: float = 800_000_000
    recent_multiple: float = 1.00
    old_weight: float = 0.65
    recent_weight: float = 0.35
    float_share: float = 0.75
    fixed_mortgage_rate: float = 0.040
    amort_years: int = 30
    # 규제 DSR 40%가 아니라, 우회 차주가 매물로 나오는 경제적 한계(총소득 대비).
    dsr_center: float = 0.70
    dsr_slope: float = 14.0
    # 대출 당시 금리. 지금 스트레스 중 이때보다 나빠진 부분만 금리 충격으로 본다.
    origin_mortgage_rate: float = 0.040
    origin_biz_rate: float = 0.055
    # 대출 당시 대비 현재까지 나빠진 상환 스트레스 중 가격에 이미 들어간 비율.
    # 강남은 9월에 하락이 시작됐지만, 86주 상승 가격이 현재 이자를 다 반영했다고 보지 않는다.
    priced_fraction: float = 0.25
    list_prob: float = 0.60
    list_k: float = 1.80
    list_concave: float = 5.0
    dsr_limit: float = 0.40
    jeonse_upper_low: float = 0.065
    jeonse_upper_high: float = 0.085
    jeonse_effect_low: float = 0.012
    jeonse_effect_high: float = -0.025
    share_cap: float = 0.50


def assumption_band(name: str) -> tuple[Assumptions, float, float]:
    """완화된/중앙/심한 가정. 반환은 (가정, 코호트비중 배수, 기대하락 배수)."""
    if name == "central":
        return Assumptions(), 1.0, 1.0
    if name == "mild":
        return (
            Assumptions(
                psi=0.04,
                phi=0.02,
                conversion=0.055,
                biz_spread=0.020,
                target_ltv_old=0.50,
                target_ltv_recent=0.45,
                biz_cap=500_000_000,
                list_k=1.2,
                list_prob=0.40,
                dsr_slope=12.0,
                priced_fraction=0.45,
                income_pass_through=0.55,
                income_level_up=0.08,
            ),
            0.5,
            0.6,
        )
    if name == "severe":
        return (
            Assumptions(
                psi=0.12,
                phi=0.06,
                conversion=0.045,
                biz_spread=0.035,
                target_ltv_old=0.75,
                mortgage_ltv_old=0.40,
                target_ltv_recent=0.65,
                biz_cap=1_000_000_000,
                float_share=0.90,
                list_k=2.4,
                list_prob=0.75,
                dsr_slope=18.0,
                dsr_center=0.65,
                priced_fraction=0.10,
                income_pass_through=0.25,
                income_level_up=0.03,
            ),
            2.0,
            1.4,
        )
    raise KeyError(name)


@dataclass(frozen=True)
class Scenario:
    id: str
    label: str
    hikes: int
    extra_term_premium: float
    g_decline: float
    income_growth: float


def scenario_for_hikes(n: int) -> Scenario:
    """추가 인상 횟수만 바꾸고 은행채 스프레드는 지금 수준을 유지한다."""
    n = int(n)
    return Scenario(
        id=f"hikes_{n}",
        label=f"추가 {n}회",
        hikes=n,
        extra_term_premium=0.0,
        g_decline=min(0.036, 0.0045 * n),
        income_growth=min(0.06, 0.012 * n),
    )


def eight_percent_scenario(assumptions: Assumptions | None = None) -> Scenario:
    """추가 4회에 더해 주담대 평균이 8%가 되도록 기간프리미엄을 벌린다."""
    a = assumptions or Assumptions()
    avg_after_four = (
        a.anchor_avg + a.pipeline_avg + a.beta_avg * 4 * a.hike
    )
    extra = 0.08 - avg_after_four
    return Scenario(
        id="mortgage_8",
        label="주담대 평균 8%",
        hikes=4,
        extra_term_premium=extra,
        g_decline=0.030,
        income_growth=0.06,
    )


HEADLINE_IDS = ("hikes_1", "hikes_4", "mortgage_8")
