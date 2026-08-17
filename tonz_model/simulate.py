"""매출·비용 불확실성을 넣은 몬테카를로."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .engine import DealParams
from .tax import couple_takehome

EOK = 100_000_000


@dataclass(frozen=True)
class Prior:
    median_monthly_eok: float = 7.6
    sigma: float = 0.30
    floor: float = 3.8
    cap: float = 16.0
    fixed_low: float = 58.0
    fixed_mode: float = 68.0
    fixed_high: float = 76.0
    var_low: float = 0.26
    var_mode: float = 0.30
    var_high: float = 0.34
    shock_p: float = 0.18
    shock_drop: float = 0.18


def _triangular(rng: np.random.Generator, lo: float, mode: float, hi: float, n: int) -> np.ndarray:
    return rng.triangular(lo, mode, hi, size=n)


def run_mc(
    n: int = 50_000,
    seed: int = 42,
    prior: Prior | None = None,
    couple_take: float = 0.10,
    principal: float = 90.0,
    interest: float = 0.0,
) -> dict:
    prior = prior or Prior()
    rng = np.random.default_rng(seed)
    mu = np.log(prior.median_monthly_eok)
    rev = rng.lognormal(mu, prior.sigma, n)
    shocked = rng.random(n) < prior.shock_p
    rev = np.where(shocked, rev * (1.0 - prior.shock_drop), rev)
    rev = np.clip(rev, prior.floor, prior.cap)
    fixed = _triangular(rng, prior.fixed_low, prior.fixed_mode, prior.fixed_high, n)
    var = _triangular(rng, prior.var_low, prior.var_mode, prior.var_high, n)

    annual = rev * 12.0
    surplus = annual * (1.0 - couple_take - var) - fixed - principal * interest
    years = np.where(surplus > 0, principal / surplus, np.inf)

    each_net = np.empty(n)
    for i, a in enumerate(annual):
        each_net[i] = couple_takehome(a * EOK, couple_take)["each_net_monthly"]

    def p_exit(t: float) -> float:
        return float(np.mean(years <= t))

    return {
        "n": n,
        "seed": seed,
        "monthly_eok": rev,
        "fixed_eok": fixed,
        "variable_rate": var,
        "surplus_eok": surplus,
        "exit_years": years,
        "each_net_monthly_won": each_net,
        "couple_net_monthly_won": each_net * 2.0,
        "stats": {
            "rev_p10": float(np.percentile(rev, 10)),
            "rev_p50": float(np.percentile(rev, 50)),
            "rev_p90": float(np.percentile(rev, 90)),
            "rev_mean": float(np.mean(rev)),
            "net1_p10": float(np.percentile(each_net, 10)),
            "net1_p50": float(np.percentile(each_net, 50)),
            "net1_p90": float(np.percentile(each_net, 90)),
            "couple_p10": float(np.percentile(each_net * 2, 10)),
            "couple_p50": float(np.percentile(each_net * 2, 50)),
            "couple_p90": float(np.percentile(each_net * 2, 90)),
            "p_operating_surplus": float(np.mean(surplus > 0)),
            "p_exit_6": p_exit(6),
            "p_exit_7": p_exit(7),
            "p_exit_10": p_exit(10),
            "p_exit_15": p_exit(15),
            "p_never": float(np.mean(~np.isfinite(years))),
            "exit_p50_finite": float(np.median(years[np.isfinite(years)]))
            if np.any(np.isfinite(years))
            else float("inf"),
        },
    }


def scenario_grid(monthly_points: list[float], p: DealParams) -> list[dict]:
    from .engine import monthly_snapshot

    return [monthly_snapshot(m, p) for m in monthly_points]


def stress_cases(base_monthly: float, p: DealParams) -> dict[str, dict]:
    from .engine import monthly_snapshot

    return {
        "base": monthly_snapshot(base_monthly, p),
        "rev_minus_20pct": monthly_snapshot(base_monthly * 0.80, p),
        "rev_minus_30pct": monthly_snapshot(base_monthly * 0.70, p),
        "two_doctors_gone_approx_18pct": monthly_snapshot(base_monthly * 0.82, p),
        "hwang_exit_minus_15pct": monthly_snapshot(base_monthly * 0.85, p),
        "fixed_plus_10pct": monthly_snapshot(
            base_monthly,
            DealParams(p.fixed_annual_eok * 1.10, p.variable_rate, p.couple_take_rate, p.principal_eok, p.interest_rate),
        ),
        "interest_6pct": monthly_snapshot(
            base_monthly,
            DealParams(p.fixed_annual_eok, p.variable_rate, p.couple_take_rate, p.principal_eok, 0.06),
        ),
    }


def procedure_count_check(cumulative: int, hq_share: float, months: float, ticket_won: float) -> dict:
    hq_cases = cumulative * hq_share
    monthly_visits = hq_cases / months
    monthly_eok = monthly_visits * ticket_won / EOK
    return {
        "hq_share": hq_share,
        "months": months,
        "monthly_visits": monthly_visits,
        "ticket_won": ticket_won,
        "implied_monthly_eok": monthly_eok,
    }
