"""매출 앵커 → 수요 prior 캘리브레이션.

실사에서 나온 세 개의 매출 앵커는 서로 다른 측정 경로에서 나왔고,
그래서 서로 다른 편향을 갖는다.

    결제 하한   연  82억 : 카드/현금 결제 추정 (플랫폼 미포착분 누락 → 하방 편향)
    패키지 중심 연 110억 : 선결제 패키지 구성비를 반영한 추정 (중심)
    자기신고    연 145억 : 본인/브랜드 측 주장 (상방 편향)

이 셋을 각각 p15 / p50 / p85 로 두고 로그정규를 적합한다.
표준정규 z(0.85) = 1.0364.

로그정규 적합 결과가 params.DemandParams 의 기본값 근거다.
검증은 tests/test_calibration.py 에서 한다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .units import from_eok

Z85 = 1.0364334

ANCHOR_LOW_ANNUAL = from_eok(82.0)
ANCHOR_MID_ANNUAL = from_eok(110.0)
ANCHOR_HIGH_ANNUAL = from_eok(145.0)


@dataclass(frozen=True)
class RevenuePrior:
    median_monthly: float
    sigma: float

    def quantile(self, q: float) -> float:
        from statistics import NormalDist

        return self.median_monthly * math.exp(self.sigma * NormalDist().inv_cdf(q))


def fit_revenue_prior(
    low_annual: float = ANCHOR_LOW_ANNUAL,
    mid_annual: float = ANCHOR_MID_ANNUAL,
    high_annual: float = ANCHOR_HIGH_ANNUAL,
) -> RevenuePrior:
    """세 앵커(p15/p50/p85)에 로그정규 적합."""
    sigma_up = math.log(high_annual / mid_annual) / Z85
    sigma_dn = math.log(mid_annual / low_annual) / Z85
    sigma = (sigma_up + sigma_dn) / 2.0
    return RevenuePrior(median_monthly=mid_annual / 12.0, sigma=sigma)


def implied_demand(ticket_median: float = 14.0) -> dict:
    """매출 prior + 객단가 → 월 환자수 prior.

    매출 분산 = 수요 분산 + 객단가 분산 이므로,
    객단가 sigma 를 먼저 정하고 나머지를 수요에 배분한다.
    """
    prior = fit_revenue_prior()
    patients_median = prior.median_monthly / ticket_median
    ticket_sigma = 0.18
    demand_sigma = math.sqrt(max(prior.sigma**2 - ticket_sigma**2, 0.01))
    return {
        "revenue_median_monthly": prior.median_monthly,
        "revenue_sigma": prior.sigma,
        "patients_median_monthly": patients_median,
        "patients_median_daily": patients_median / 28.0,
        "demand_sigma": demand_sigma,
        "ticket_sigma": ticket_sigma,
    }


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    pprint(implied_demand())
