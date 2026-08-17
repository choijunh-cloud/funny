"""'통계적으로 가능한가'를 두 층으로 나눠서 답한다.

층1 — 도달 가능성: 필요 매출이 캘리브레이션된 매출 분포에서 몇 시그마인가.
       (단년도 기준. 여기서는 웬만한 목표가 p<0.05로 기각되지 않는다.)
층2 — 유지 가능성: 그 매출을 6~7년 '연속으로' 내면서 실제로 완제까지 가는가.
       (몬테카를로. 여기서 확률이 급격히 떨어진다.)

이 둘을 섞으면 '가능하다'와 '될 것이다'를 혼동하게 된다.
"""

from __future__ import annotations

import math
from statistics import NormalDist

import numpy as np

from . import deterministic as det
from .calibration import fit_revenue_prior
from .params import ModelParams
from .simulate import SimResult

ND = NormalDist()


def single_year_attainment(p: ModelParams, required_monthly: float) -> dict:
    """단년도에 그 매출을 낼 확률 (실사 앵커 기반 로그정규)."""
    prior = fit_revenue_prior()
    z = math.log(required_monthly / prior.median_monthly) / prior.sigma
    return {
        "필요_월매출": required_monthly,
        "앵커중앙_월매출": prior.median_monthly,
        "z": z,
        "p_달성": 1.0 - ND.cdf(z),
        "상위_몇_퍼센트": (1.0 - ND.cdf(z)) * 100.0,
    }


def sustained_attainment(res: SimResult, required_monthly: float, years: int) -> float:
    """해당 매출을 years 동안 평균적으로 유지할 확률 (경로 기준)."""
    m = years * 12
    avg = res.revenue[:, :m].mean(axis=1)
    return float((avg >= required_monthly).mean())


def table(p: ModelParams, res: SimResult) -> list[dict]:
    rows = []
    targets = [
        ("운영 손익분기", det.operating_bep(p), 10),
        ("10년 완제", det.required_revenue(p, 10), 10),
        ("7년 완제", det.required_revenue(p, 7), 7),
        ("6년 완제", det.required_revenue(p, 6), 6),
    ]
    payoff = {
        6: float(((res.payoff_month >= 0) & (res.payoff_month < 72)).mean()),
        7: float(((res.payoff_month >= 0) & (res.payoff_month < 84)).mean()),
        10: float((res.payoff_month >= 0).mean()),
    }
    for label, req, yrs in targets:
        one = single_year_attainment(p, req)
        rows.append(
            {
                "목표": label,
                "필요_월매출": req,
                "z": one["z"],
                "p_단년도_달성": one["p_달성"],
                "p_유지": sustained_attainment(res, req, yrs),
                "p_실제완제": payoff.get(yrs, float("nan")) if label != "운영 손익분기" else float("nan"),
            }
        )
    return rows


def schedule_sustainability(res: SimResult) -> dict:
    """월 2일 휴무가 몇 년이나 유지되는가."""
    bm = res.burnout_month
    hit = bm >= 0
    surv = []
    for y in (1, 2, 3, 5, 7, 10):
        surv.append((y, float(1.0 - ((bm >= 0) & (bm < y * 12)).mean())))
    return {
        "P(끝까지 유지)": float(1.0 - hit.mean()),
        "중앙_유지연수": float(np.median(bm[hit] / 12.0)) if hit.any() else float("nan"),
        "생존곡선": surv,
    }
