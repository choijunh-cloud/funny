"""딜 현금흐름 항등식.

MSO 잉여 = 매출 × (0.90 − 변동비율) − 연고정비
부부 선취 10%는 병원 잉여에서 빠지고, 병원 적자여도 선취만 유지되면 월급은 나옴.
"""

from __future__ import annotations

from dataclasses import dataclass

from .tax import couple_takehome

EOK = 100_000_000  # 1억 원


@dataclass(frozen=True)
class DealParams:
    fixed_annual_eok: float
    variable_rate: float
    couple_take_rate: float = 0.10
    principal_eok: float = 90.0
    interest_rate: float = 0.0

    @property
    def contribution_margin(self) -> float:
        return self.couple_take_rate * 0 + (1.0 - self.couple_take_rate - self.variable_rate)

    @property
    def mso_share(self) -> float:
        return 1.0 - self.couple_take_rate


def surplus_annual(annual_revenue_eok: float, p: DealParams) -> float:
    """연 상환여력(억). 이자 있으면 원금 잔액 없이 단순 연이자만 차감(1년차 근사)."""
    s = annual_revenue_eok * (p.mso_share - p.variable_rate) - p.fixed_annual_eok
    if p.interest_rate > 0:
        s -= p.principal_eok * p.interest_rate
    return s


def required_revenue(p: DealParams, years: float | None = None) -> float:
    """필요 연매출(억). years=None 이면 운영 손익분기(잉여=0)."""
    cm = p.mso_share - p.variable_rate
    if cm <= 0:
        return float("inf")
    need = 0.0 if years is None else p.principal_eok / years
    if p.interest_rate > 0:
        need += p.principal_eok * p.interest_rate
    return (need + p.fixed_annual_eok) / cm


def exit_years(annual_revenue_eok: float, p: DealParams) -> float:
    s = surplus_annual(annual_revenue_eok, p)
    if s <= 0:
        return float("inf")
    return p.principal_eok / s


def physical_monthly_eok(
    doctors: int,
    patients_per_doctor_day: float,
    ticket_won: float,
    days: int = 28,
) -> float:
    return doctors * patients_per_doctor_day * days * ticket_won / EOK


def implied_daily_patients(monthly_eok: float, ticket_won: float, days: int = 28) -> float:
    if ticket_won <= 0 or days <= 0:
        return float("inf")
    return monthly_eok * EOK / (ticket_won * days)


def monthly_snapshot(monthly_eok: float, p: DealParams) -> dict:
    annual = monthly_eok * 12.0
    s = surplus_annual(annual, p)
    years = exit_years(annual, p)
    take = couple_takehome(annual * EOK, p.couple_take_rate)
    return {
        "monthly_eok": monthly_eok,
        "annual_eok": annual,
        "surplus_annual_eok": s,
        "operating_ok": s + (p.principal_eok * p.interest_rate) > -1e-9
        and annual * (p.mso_share - p.variable_rate) - p.fixed_annual_eok >= 0,
        "exit_years": years,
        "each_net_monthly_won": take["each_net_monthly"],
        "couple_net_monthly_won": take["couple_net_monthly"],
        "each_pretax_monthly_won": take["each_pretax_monthly"],
        "effective_tax_rate": take["effective_rate"],
        "shortcut_3_1pct_one_won": take["shortcut_3_1pct_one_monthly"],
        "shortcut_gap_won": take["shortcut_overstatement"],
    }


def bep_table(p: DealParams) -> dict[str, float]:
    return {
        "operating": required_revenue(p, None) / 12.0,
        "y10": required_revenue(p, 10) / 12.0,
        "y7": required_revenue(p, 7) / 12.0,
        "y6": required_revenue(p, 6) / 12.0,
    }
