"""하이브리드 v1.1.

채점 원장과 10/2 좌표를 한 리포트로 묶는다.
확률은 compute_posterior 한 길만 타고, 밴드는 상위 패널 레벨을 월별로 겹친 것이다.
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from hybrid_model.ledger import PANELS, Panel, validate_ledger
from hybrid_model.market import (
    SNAPSHOT,
    ClockResult,
    LevelView,
    Market,
    level_views,
    project_clocks,
)
from hybrid_model.scenarios import (
    SCENARIOS,
    AppliedFactor,
    Posterior,
    Scenario,
    compute_posterior,
    market_flags,
)
from hybrid_model.scoring import composite, display_points, hit_rate, shrink


@dataclass(frozen=True)
class ScoredPanel:
    panel: Panel
    order: int
    hit_rate: float
    hit_pct: int
    shrunk: float
    composite: float | None
    composite_pct: int | None

    @property
    def n(self) -> int:
        return self.panel.n

    @property
    def main(self) -> bool:
        return self.panel.main

    @property
    def name(self) -> str:
        return self.panel.name


@dataclass(frozen=True)
class Shock:
    id: str
    title: str
    market: Market
    posterior: Posterior


@dataclass(frozen=True)
class Report:
    market: Market
    panels: tuple[ScoredPanel, ...]
    posterior: Posterior
    scenarios: tuple[Scenario, ...]
    clocks: tuple[ClockResult, ...]
    levels: tuple[LevelView, ...]
    shocks: tuple[Shock, ...]
    flags: tuple[str, ...]

    def leaderboard(self, main: bool) -> tuple[ScoredPanel, ...]:
        rows = [panel for panel in self.panels if panel.main is main]
        rows.sort(key=lambda panel: (-panel.hit_rate, -panel.n, panel.order))
        return tuple(rows)

    def composite_board(self) -> tuple[ScoredPanel, ...]:
        rows = [panel for panel in self.panels if panel.composite is not None]
        rows.sort(key=lambda panel: (-(panel.composite or 0), panel.order))
        return tuple(rows)

    def active_factors(self) -> tuple[AppliedFactor, ...]:
        return tuple(factor for factor in self.posterior.factors if factor.active)


SHOCKS: tuple[tuple[str, str, dict[str, float]], ...] = (
    ("y10-490", "10Y 4.90 — 조건① 해제", {"us10y": 4.90}),
    ("y10-535", "10Y 5.35 — 5.3 고착", {"us10y": 5.35}),
    ("week-plus", "외인 주간 +1조", {"foreign_week_tn": 1.0}),
    ("core-cpi", "근원 CPI MoM 0.3 — 조건②", {"core_cpi_mom": 0.3}),
    ("samsung-118", "삼성 3Q 118조", {"samsung_op_tn": 118.0}),
    ("weekly-7200", "주봉 종가 7,200", {"weekly_close": 7200.0}),
    ("kospi-6500", "코스피 6,500", {"kospi": 6500.0}),
    ("brent-85", "브렌트 85", {"brent": 85.0}),
)


def score_panels(panels: tuple[Panel, ...] = PANELS) -> tuple[ScoredPanel, ...]:
    scored: list[ScoredPanel] = []
    for order, panel in enumerate(panels):
        rate = hit_rate(panel.hits, panel.partials, panel.misses)
        score = composite(rate, panel.n, panel.layer1, panel.falsifiability)
        scored.append(
            ScoredPanel(
                panel=panel,
                order=order,
                hit_rate=rate,
                hit_pct=display_points(rate),
                shrunk=shrink(rate, panel.n),
                composite=score,
                composite_pct=None if score is None else display_points(score),
            )
        )
    return tuple(scored)


def build_shocks(market: Market) -> tuple[Shock, ...]:
    shocks: list[Shock] = []
    for shock_id, title, changes in SHOCKS:
        shocked = replace(market, **changes)
        shocks.append(Shock(shock_id, title, shocked, compute_posterior(shocked)))
    return tuple(shocks)


class HybridModel:
    def __init__(self, market: Market | None = None):
        self.market = SNAPSHOT if market is None else market
        validate_ledger()

    def run(self) -> Report:
        return Report(
            market=self.market,
            panels=score_panels(),
            posterior=compute_posterior(self.market),
            scenarios=SCENARIOS,
            clocks=project_clocks(self.market.asof),
            levels=level_views(self.market.kospi),
            shocks=build_shocks(self.market),
            flags=market_flags(self.market),
        )
