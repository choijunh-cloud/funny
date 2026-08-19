#!/usr/bin/env python3
"""8/19 시각화 보고서에 쓰는 환율·FCF·밸류 산술 검증."""

from __future__ import annotations

from scripts import aug19_visual_data as d


def almost(a: float, b: float, tol: float = 0.05) -> None:
    assert abs(a - b) < tol, f"{a} != {b} (tol={tol})"


def main() -> None:
    # 환율 1,520 → 1,420 = -6.58%, 베타 0.9 → EPS -5.92% ≈ -5.9%
    almost(d.FX_DROP_PCT * 100, -6.5789, 0.01)
    almost(d.SKH_EPS_HIT_PCT, 5.92, 0.02)

    # 27년 순익 300~400조 × 5.92% ≈ 17.8~23.7조 → 원문 18~24조
    almost(d.SKH_NI_ADJ_LOW, 17.76, 0.05)
    almost(d.SKH_NI_ADJ_HIGH, 23.68, 0.05)

    # 자사주 3.3%, 일매입 × 영업일 ≈ 40조
    almost(d.SKH_BUYBACK_PCT, 3.295, 0.01)
    assert d.SKH_DAILY_BUY_EOK * d.SKH_TRADING_DAYS == 400_024
    almost(d.SKH_EPS_ACCRETION_PCT, 3.41, 0.02)

    # FCF
    assert d.FCF_CUM_25_27 * 0.5 == 192.5
    assert 192.5 - 40 == 152.5
    assert sum(d.FCF_BASE) == 658
    assert sum(d.FCF_CONSERVATIVE) == 565

    # 사이클 PER 6~7배
    assert d.SKH_26_EPS * 6 == 2_076_000
    assert d.SKH_26_EPS * 7 == 2_422_000
    assert d.SEC_26_EPS * 6 == 287_400
    assert d.SEC_26_EPS * 7 == 335_300

    # ADR $163.8 × 1,390 × 10 = 2,276,820원 (원문 228만원)
    almost(d.SKH_ADR_KRW, 2_276_820, 1)
    almost(d.SKH_IMPLIED_NORMAL, 1_897_350, 50)
    almost(d.SKH_IMPLIED_RECENT_LO, 1_686_533, 50)
    almost(d.SKH_IMPLIED_RECENT_HI, 1_751_400, 50)

    # 피어 PER
    almost(d.MU_CY27_PER, 6.25, 0.01)
    almost(d.SNDK_PER, 7.80, 0.02)

    # 키옥시아
    almost(d.KIOXIA_RET_1 * 100, 3.25, 0.05)
    almost(d.KIOXIA_RET_2 * 100, 4.04, 0.05)
    almost(d.KIOXIA_RET_CUM * 100, 7.42, 0.05)

    # 유니트리 PSR
    almost(d.UNITREE_PSR, 155.36, 0.05)

    # HBM 순수요: (1+ai)/(1+eff) - 1
    bull = (1 + d.HBM_BULL["ai"]) / (1 + d.HBM_BULL["eff"]) - 1
    bear = (1 + d.HBM_BEAR["ai"]) / (1 + d.HBM_BEAR["eff"]) - 1
    almost(bull * 100, 25.0, 0.1)
    almost(bear * 100, -7.69, 0.1)

    print("aug19 visual number checks OK")


if __name__ == "__main__":
    main()
