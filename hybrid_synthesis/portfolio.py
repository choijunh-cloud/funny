"""Score KOSPI names and build a phase-aware 60/40 book."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Iterable

from hybrid_synthesis.model import HybridSnapshot, Phase, clamp
from hybrid_synthesis.universe import (
    KOSPI_UNIVERSE,
    NON_KOSPI_EXCLUSIONS,
    Stock,
    kospi_avoid,
    kospi_investable,
)

SLEEVE_ORDER = ("CORE_SEMI", "AI_CONNECT", "MACRO_HEDGE", "COSMETICS")

PHASE_SLEEVE_MULT: dict[Phase, dict[str, float]] = {
    Phase.CONVERGENCE: {
        "CORE_SEMI": 1.12,
        "AI_CONNECT": 0.92,
        "MACRO_HEDGE": 1.18,
        "COSMETICS": 1.00,
        "NONE": 0.70,
    },
    Phase.PIVOT: {
        "CORE_SEMI": 1.22,
        "AI_CONNECT": 1.10,
        "MACRO_HEDGE": 0.96,
        "COSMETICS": 1.04,
        "NONE": 0.70,
    },
    Phase.SUPERCYCLE: {
        "CORE_SEMI": 1.04,
        "AI_CONNECT": 1.38,
        "MACRO_HEDGE": 0.82,
        "COSMETICS": 0.88,
        "NONE": 0.60,
    },
}

SLEEVE_TOP_N = {
    "CORE_SEMI": 2,
    "AI_CONNECT": 5,
    "MACRO_HEDGE": 5,
    "COSMETICS": 2,
}

# Core sleeve is not score-proportional. The note is explicit: Samsung + Hynix only.
CORE_FIXED_SPLIT = {
    "005930": 0.55,
    "000660": 0.45,
}

HEDGE_TILT = {
    "034020": 0.28,
    "105560": 0.24,
    "015760": 0.20,
    "055550": 0.16,
    "003490": 0.12,
}


def _weighted_raw(stock: Stock) -> float:
    return (
        0.22 * stock.ai_earnings
        + 0.16 * stock.connectivity
        + 0.12 * stock.fcf_beta
        + 0.12 * stock.policy_beta
        + 0.10 * stock.valuation_safety
        + 0.08 * stock.liquidity
        + 0.08 * stock.rate_hedge
        + 0.04 * stock.fx_krw_strength
        + 0.06 * stock.cxmt_benefit
        - 0.10 * stock.ymtc_nand_risk
    )


def score_stock(stock: Stock, snapshot: HybridSnapshot) -> float:
    if stock.is_avoid:
        return 0.0
    raw = _weighted_raw(stock)
    phase_mult = PHASE_SLEEVE_MULT[snapshot.phase].get(stock.sleeve, 0.70)
    # Macro relief lifts banks/airlines; AI expansion lifts connect; ISA/div lifts Samsung.
    cycle = 1.0
    cycle += 0.15 * snapshot.relief["R"] * (stock.rate_hedge / 100.0)
    cycle += 0.18 * clamp((snapshot.expansion["A"] - 1.0) / 0.8, 0.0, 1.0) * (stock.connectivity / 100.0)
    cycle += 0.16 * snapshot.defense["D"] * (stock.policy_beta / 100.0)
    cycle += 0.10 * snapshot.expansion["cxmt_dram_defense"] * (stock.cxmt_benefit / 100.0)
    return raw * phase_mult * cycle


def largest_remainder(weights: Iterable[float], total: float = 1.0, ndigits: int = 4) -> list[float]:
    values = [float(weight) for weight in weights]
    if any(weight < 0.0 or not math.isfinite(weight) for weight in values):
        raise ValueError("weights must be finite and non-negative")
    mass = sum(values)
    if mass <= 0.0:
        raise ValueError("weights must have a positive sum")
    scaled = [weight / mass * total for weight in values]
    step = 10 ** (-ndigits)
    floors = [math.floor(weight / step) * step for weight in scaled]
    leftover = round(total - sum(floors), ndigits + 2)
    ranks = sorted(
        range(len(values)),
        key=lambda index: (scaled[index] - floors[index], -index),
        reverse=True,
    )
    units = int(round(leftover / step))
    for index in ranks[:units]:
        floors[index] = round(floors[index] + step, ndigits)
    # Final guard against 0.9999-style drift.
    drift = round(total - sum(floors), ndigits)
    if drift != 0.0:
        floors[ranks[0]] = round(floors[ranks[0]] + drift, ndigits)
    return [round(value, ndigits) for value in floors]


@dataclass(frozen=True)
class Holding:
    ticker: str
    name: str
    sleeve: str
    action: str
    score: float
    weight_equity: float
    weight_total: float
    thesis: str
    kosdaq_proxy_of: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticker": self.ticker,
            "name": self.name,
            "sleeve": self.sleeve,
            "action": self.action,
            "score": self.score,
            "weight_equity": self.weight_equity,
            "weight_total": self.weight_total,
            "thesis": self.thesis,
            "kosdaq_proxy_of": list(self.kosdaq_proxy_of),
        }


@dataclass(frozen=True)
class RankedName:
    stock: Stock
    score: float

    def to_dict(self) -> dict[str, Any]:
        payload = self.stock.to_dict()
        payload["score"] = self.score
        return payload


@dataclass
class Portfolio:
    snapshot: HybridSnapshot
    holdings: list[Holding]
    ranked: list[RankedName]
    avoid: list[Stock] = field(default_factory=list)
    excluded_non_kospi: tuple[dict[str, str], ...] = NON_KOSPI_EXCLUSIONS
    reference_krw: float = 100_000_000.0

    @property
    def cash_bond_weight(self) -> float:
        return 1.0 - self.snapshot.equity_weight

    def holdings_weight_sum(self) -> float:
        return sum(item.weight_total for item in self.holdings)

    def sleeve_weights_total(self) -> dict[str, float]:
        out = {key: 0.0 for key in SLEEVE_ORDER}
        for item in self.holdings:
            out[item.sleeve] = out.get(item.sleeve, 0.0) + item.weight_total
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot": self.snapshot.to_dict(),
            "cash_bond_weight": self.cash_bond_weight,
            "reference_krw": self.reference_krw,
            "holdings": [item.to_dict() for item in self.holdings],
            "ranked": [item.to_dict() for item in self.ranked],
            "avoid": [item.to_dict() for item in self.avoid],
            "excluded_non_kospi": list(self.excluded_non_kospi),
            "sleeve_weights_total": self.sleeve_weights_total(),
            "check": {
                "holdings_plus_cash": self.holdings_weight_sum() + self.cash_bond_weight,
                "all_holdings_kospi": all(item.ticker in {s.ticker for s in KOSPI_UNIVERSE if s.is_kospi} for item in self.holdings),
                "avoid_not_held": not any(item.ticker in {a.ticker for a in self.avoid} for item in self.holdings),
            },
        }


def _select_sleeve(stocks: list[RankedName], sleeve: str) -> list[RankedName]:
    pool = [item for item in stocks if item.stock.sleeve == sleeve and item.stock.action != "WATCH"]
    if sleeve == "CORE_SEMI":
        wanted = {ticker: None for ticker in CORE_FIXED_SPLIT}
        picked = []
        for item in pool:
            if item.stock.ticker in wanted:
                picked.append(item)
        if len(picked) != 2:
            raise RuntimeError("core sleeve must contain Samsung Electronics and SK hynix")
        return picked
    if sleeve == "MACRO_HEDGE":
        by_ticker = {item.stock.ticker: item for item in pool}
        ordered = [by_ticker[ticker] for ticker in HEDGE_TILT if ticker in by_ticker]
        return ordered[: SLEEVE_TOP_N[sleeve]]
    pool.sort(key=lambda item: (-item.score, item.stock.ticker))
    return pool[: SLEEVE_TOP_N[sleeve]]


def _sleeve_internal_weights(picked: list[RankedName], sleeve: str) -> list[float]:
    if sleeve == "CORE_SEMI":
        return [CORE_FIXED_SPLIT[item.stock.ticker] for item in picked]
    if sleeve == "MACRO_HEDGE":
        raw = [HEDGE_TILT[item.stock.ticker] for item in picked]
        return largest_remainder(raw, total=1.0, ndigits=4)
    raw = [max(item.score, 1.0) for item in picked]
    return largest_remainder(raw, total=1.0, ndigits=4)


def build_portfolio(snapshot: HybridSnapshot, *, reference_krw: float = 100_000_000.0) -> Portfolio:
    ranked = [
        RankedName(stock=stock, score=score_stock(stock, snapshot))
        for stock in kospi_investable()
    ]
    ranked.sort(key=lambda item: (-item.score, item.stock.ticker))

    equity = snapshot.equity_weight
    holdings: list[Holding] = []
    for sleeve in SLEEVE_ORDER:
        picked = _select_sleeve(ranked, sleeve)
        if not picked:
            continue
        inner = _sleeve_internal_weights(picked, sleeve)
        sleeve_of_equity = snapshot.sleeves[sleeve]
        sleeve_of_total = equity * sleeve_of_equity
        inner = largest_remainder(inner, total=1.0, ndigits=4)
        totals = largest_remainder(
            [weight * sleeve_of_total for weight in inner],
            total=sleeve_of_total,
            ndigits=4,
        )
        for item, weight_total, weight_inner in zip(picked, totals, inner):
            holdings.append(
                Holding(
                    ticker=item.stock.ticker,
                    name=item.stock.name,
                    sleeve=sleeve,
                    action=item.stock.action,
                    score=item.score,
                    weight_equity=round(weight_inner * sleeve_of_equity, 4),
                    weight_total=weight_total,
                    thesis=item.stock.thesis,
                    kosdaq_proxy_of=item.stock.kosdaq_proxy_of,
                )
            )

    # Reconcile residual so equity + cash = 1 within 1bp.
    held = sum(item.weight_total for item in holdings)
    residual = round(equity - held, 4)
    if abs(residual) >= 0.0001 and holdings:
        first = holdings[0]
        holdings[0] = Holding(
            ticker=first.ticker,
            name=first.name,
            sleeve=first.sleeve,
            action=first.action,
            score=first.score,
            weight_equity=first.weight_equity,
            weight_total=round(first.weight_total + residual, 4),
            thesis=first.thesis,
            kosdaq_proxy_of=first.kosdaq_proxy_of,
        )

    return Portfolio(
        snapshot=snapshot,
        holdings=holdings,
        ranked=ranked,
        avoid=list(kospi_avoid()),
        excluded_non_kospi=NON_KOSPI_EXCLUSIONS,
        reference_krw=reference_krw,
    )
