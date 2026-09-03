"""KOSPI hybrid synthesis model: macro × AI fundamentals + domestic flow defense."""

from hybrid_synthesis.model import (
    PHASES,
    HybridInputs,
    HybridSnapshot,
    Phase,
    Scenario,
    baseline_inputs,
    evaluate,
    scenario_inputs,
)
from hybrid_synthesis.portfolio import Portfolio, build_portfolio
from hybrid_synthesis.ranking import rank_h2
from hybrid_synthesis.universe import KOSPI_UNIVERSE, NON_KOSPI_EXCLUSIONS

__all__ = [
    "PHASES",
    "HybridInputs",
    "HybridSnapshot",
    "KOSPI_UNIVERSE",
    "NON_KOSPI_EXCLUSIONS",
    "Phase",
    "Portfolio",
    "Scenario",
    "baseline_inputs",
    "build_portfolio",
    "evaluate",
    "rank_h2",
    "scenario_inputs",
]
