"""Hybrid Synthesis Model for KOSPI momentum and phase inference.

Market momentum is not a list of headlines. It is the product of how fast
macro pressure is lifting and how fast AI profits are expanding, plus a
domestic flow floor that can hold the index while foreigners sell.

    M = R * A + D

R  Macro-pressure relief in [0, 1]. Rate inversion, UST supply, oil, FX.
A  AI profit-expansion coefficient, typically [0.8, 2.2].
D  Domestic supply defense in [0, 1]. ISA, Samsung dividend, KEPCO prepay.

This module is deterministic. Every baseline number is taken from the
2026-09-03 five-video synthesis (Moon Nam-jung, Yoon Yeo-sam, Kim Min-soo,
Noh Geun-chang / Kang Kwan-woo) and is overrideable for live re-runs.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, fields, replace
from datetime import date
from enum import Enum
from typing import Any, Mapping


def clamp(value: float, low: float, high: float) -> float:
    if not math.isfinite(value):
        raise ValueError(f"value must be finite, got {value!r}")
    return min(high, max(low, value))


def _finite(name: str, value: float, *, low: float | None = None, high: float | None = None) -> float:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite, got {value!r}")
    if low is not None and value < low:
        raise ValueError(f"{name} must be >= {low}, got {value}")
    if high is not None and value > high:
        raise ValueError(f"{name} must be <= {high}, got {value}")
    return value


class Phase(str, Enum):
    CONVERGENCE = "1"
    PIVOT = "2"
    SUPERCYCLE = "3"


class Scenario(str, Enum):
    BASE = "base"
    JAWBONING = "jawboning"
    HARD_LANDING = "hard_landing"
    EARLY_PIVOT = "early_pivot"
    FCF_INFLECTION = "fcf_inflection"


PHASES: dict[Phase, dict[str, Any]] = {
    Phase.CONVERGENCE: {
        "name": "고통의 수렴 및 바닥 테스트",
        "window": "2026-09-03 ~ 2026-10-08",
        "kospi_band": (6400.0, 6600.0),
        "equity_weight": 0.60,
        "sleeves": {
            "CORE_SEMI": 0.50,
            "AI_CONNECT": 0.25,
            "MACRO_HEDGE": 0.15,
            "COSMETICS": 0.10,
        },
        "narrative": (
            "10년물 4.8%, 유가 $90, 9월 FOMC 동결. 외국인 파생 매도가 지수를 억누르지만 "
            "반도체 선행 P/E 5.7배와 자사주 매입이 6,400~6,600 하단을 지킨다."
        ),
    },
    Phase.PIVOT: {
        "name": "매크로 피벗 & 밸류에이션 정상화",
        "window": "2026-4Q ~ 2027-1Q",
        "kospi_band": (7800.0, 9200.0),
        "equity_weight": 0.65,
        "sleeves": {
            "CORE_SEMI": 0.52,
            "AI_CONNECT": 0.23,
            "MACRO_HEDGE": 0.15,
            "COSMETICS": 0.10,
        },
        "narrative": (
            "유가 $80대, 4분기 PCE 3.5% 하회로 인하 룸 오픈. 삼성 특별배당과 ISA 40조가 "
            "숏커버를 부르며 반도체 P/E가 7.5배로 리레이팅된다."
        ),
    },
    Phase.SUPERCYCLE: {
        "name": "FCF 흑자 전환 & AI 슈퍼 사이클",
        "window": "2027-2Q 이후",
        "kospi_band": (8800.0, 10500.0),
        "equity_weight": 0.70,
        "sleeves": {
            "CORE_SEMI": 0.42,
            "AI_CONNECT": 0.38,
            "MACRO_HEDGE": 0.12,
            "COSMETICS": 0.08,
        },
        "narrative": (
            "하이퍼스케일러 ASIC 외부 판매로 AI FCF가 플러스 전환. NVL72·HBM4가 열리며 "
            "병목이 연산에서 연결(CPO·FC-BGA·스위치)로 이동한다."
        ),
    },
}

# 10-year UST thresholds from the Yoon Yeo-sam block.
UST_COMFORT = 4.20
UST_VALUATION_STRESS = 4.50
UST_HARD_LANDING = 5.00
HARD_LANDING_DRAWDOWN = (-0.15, -0.10)

# Fed cut arithmetic from the Moon Nam-jung block.
PCE_PARTIAL_CUT_ROOM = 3.50
INFLATION_TARGET = 2.00


@dataclass(frozen=True)
class HybridInputs:
    """Observable / assumed inputs. Override any field to re-run the model."""

    as_of: date = date(2026, 9, 3)

    fed_funds: float = 3.75
    pce_yoy: float = 3.70
    fed_neutral: float = 3.10
    inflation_target: float = INFLATION_TARGET

    ust10: float = 4.80
    ig_issuance_bn: float = 220.0
    bytedance_loan_bn: float = 30.0
    ig_spread_over_ust: float = 0.75

    oil_brent: float = 90.0
    fx_distortion: float = 0.75
    usdjpy: float = 156.4
    jawboning_intensity: float = 0.55

    kospi_spot: float = 6500.0
    semi_fwd_pe: float = 5.70
    semi_target_pe: float = 7.50

    nvidia_dc_bn: float = 89.0
    nvidia_hyperscaler_bn: float = 48.0
    nvidia_other_bn: float = 40.0
    nvl72_share: float = 0.61
    nvl72_next_year: float = 0.90
    google_external_asic_2028_bn: float = 250.0
    bigtech_fcf_positive: bool = False
    fcf_turn_date: date = date(2027, 7, 1)

    cxmt_hbm_intensity: float = 0.35
    ymtc_nand_share: float = 0.14

    isa_inflow_tn: float = 0.0
    isa_full_tn: float = 40.0
    samsung_special_div_prob: float = 0.70
    kepco_prepay_signal: float = 1.0
    texas_infra_bn: float = 25.0

    def __post_init__(self) -> None:
        for field in fields(self):
            value = getattr(self, field.name)
            if field.type is float or field.name in {
                "fed_funds",
                "pce_yoy",
                "fed_neutral",
                "inflation_target",
                "ust10",
                "oil_brent",
            }:
                if isinstance(value, float):
                    _finite(field.name, value)
        _finite("ust10", self.ust10, low=0.0)
        _finite("pce_yoy", self.pce_yoy, low=0.0)
        _finite("nvl72_share", self.nvl72_share, low=0.0, high=1.0)
        _finite("nvl72_next_year", self.nvl72_next_year, low=0.0, high=1.0)
        _finite("fx_distortion", self.fx_distortion, low=0.0, high=1.0)
        _finite("cxmt_hbm_intensity", self.cxmt_hbm_intensity, low=0.0, high=1.0)
        _finite("ymtc_nand_share", self.ymtc_nand_share, low=0.0, high=1.0)
        _finite("samsung_special_div_prob", self.samsung_special_div_prob, low=0.0, high=1.0)
        _finite("kepco_prepay_signal", self.kepco_prepay_signal, low=0.0, high=1.0)
        if self.nvidia_dc_bn <= 0.0:
            raise ValueError("nvidia_dc_bn must be positive")

    def other_demand_share(self) -> float:
        return clamp(self.nvidia_other_bn / self.nvidia_dc_bn, 0.0, 1.0)

    def real_policy_rate(self) -> float:
        """Fed funds minus trailing PCE. Baseline: 3.75 - 3.70 = 0.05."""
        return self.fed_funds - self.pce_yoy

    def real_neutral_rate(self) -> float:
        """Stated neutral minus inflation target. Baseline: 3.10 - 2.00 = 1.10."""
        return self.fed_neutral - self.inflation_target

    def rate_gap(self) -> float:
        """Need real policy > real neutral before a structural cut is possible."""
        return self.real_policy_rate() - self.real_neutral_rate()

    def structural_cut_open(self) -> bool:
        return self.rate_gap() > 0.0

    def partial_cut_room(self) -> bool:
        """Jawboning ends only after PCE prints ≤ 3.5 even if the gap is still negative."""
        return self.pce_yoy <= PCE_PARTIAL_CUT_ROOM

    def issuance_pressure(self) -> float:
        """AI IG issuance + ByteDance loans as a 0–1 crowding-out score."""
        return clamp((self.ig_issuance_bn + self.bytedance_loan_bn) / 300.0, 0.0, 1.0)

    def effective_ust10(self) -> float:
        """Shadow 10-year used for diagnosis, not for the hard-landing tripwire.

        The traded 4.8% print already embeds the supply shock. Adding the full
        issuance pile on top would falsely fire the 5.0% crash rule on day one.
        """
        return self.ust10 + 0.10 * self.issuance_pressure() + 0.05 * self.jawboning_intensity

    def hard_landing(self) -> bool:
        """Mechanical 10–15% risk-asset shock only when the *traded* 10-year hits 5.0%."""
        return self.ust10 >= UST_HARD_LANDING


def baseline_inputs() -> HybridInputs:
    return HybridInputs()


def scenario_inputs(name: Scenario, base: HybridInputs | None = None) -> HybridInputs:
    src = base or baseline_inputs()
    if name is Scenario.BASE:
        return src
    if name is Scenario.JAWBONING:
        return replace(src, jawboning_intensity=0.90, ust10=4.90)
    if name is Scenario.HARD_LANDING:
        return replace(src, ust10=5.05, oil_brent=96.0, fx_distortion=0.90, jawboning_intensity=0.80)
    if name is Scenario.EARLY_PIVOT:
        return replace(
            src,
            as_of=date(2026, 11, 20),
            pce_yoy=3.45,
            oil_brent=81.0,
            ust10=4.35,
            fx_distortion=0.40,
            jawboning_intensity=0.20,
            isa_inflow_tn=18.0,
            samsung_special_div_prob=0.90,
        )
    if name is Scenario.FCF_INFLECTION:
        return replace(
            src,
            as_of=date(2027, 7, 15),
            pce_yoy=3.20,
            oil_brent=78.0,
            ust10=4.10,
            fx_distortion=0.25,
            jawboning_intensity=0.10,
            nvl72_share=0.90,
            bigtech_fcf_positive=True,
            isa_inflow_tn=40.0,
            samsung_special_div_prob=1.0,
            cxmt_hbm_intensity=0.55,
        )
    raise ValueError(f"unknown scenario: {name}")


def infer_phase(inputs: HybridInputs) -> Phase:
    if inputs.hard_landing() and inputs.as_of < date(2027, 4, 1):
        return Phase.CONVERGENCE
    if inputs.as_of >= date(2027, 4, 1) or inputs.bigtech_fcf_positive:
        return Phase.SUPERCYCLE
    if inputs.as_of >= date(2026, 10, 8):
        if inputs.partial_cut_room() or inputs.as_of >= date(2026, 12, 1):
            return Phase.PIVOT
        return Phase.CONVERGENCE
    return Phase.CONVERGENCE


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def macro_relief(inputs: HybridInputs) -> dict[str, float]:
    """R in [0, 1] and its four additive parts."""
    gap = inputs.rate_gap()
    if inputs.structural_cut_open():
        r_rates = 0.55 + 0.45 * _logistic(gap / 0.35)
    elif inputs.partial_cut_room():
        r_rates = 0.38 + 0.12 * _logistic((PCE_PARTIAL_CUT_ROOM - inputs.pce_yoy) / 0.15)
    else:
        r_rates = 0.08 + 0.12 * _logistic(gap / 0.40)

    ust = inputs.ust10
    if ust >= UST_HARD_LANDING:
        r_ust = 0.04
    elif ust >= UST_VALUATION_STRESS:
        r_ust = 0.38 * (UST_HARD_LANDING - ust) / (UST_HARD_LANDING - UST_VALUATION_STRESS)
    elif ust >= UST_COMFORT:
        r_ust = 0.38 + 0.42 * (UST_VALUATION_STRESS - ust) / (UST_VALUATION_STRESS - UST_COMFORT)
    else:
        r_ust = 0.80 + 0.20 * clamp((UST_COMFORT - ust) / 0.40, 0.0, 1.0)

    r_supply = clamp(1.0 - 0.70 * inputs.issuance_pressure(), 0.0, 1.0)
    r_oil = clamp((92.0 - inputs.oil_brent) / 22.0, 0.0, 1.0)
    r_fx = clamp(1.0 - inputs.fx_distortion, 0.0, 1.0)

    r = clamp(
        0.36 * r_rates + 0.28 * r_ust + 0.10 * r_supply + 0.16 * r_oil + 0.10 * r_fx,
        0.0,
        1.0,
    )
    return {
        "R": r,
        "R_rates": r_rates,
        "R_ust": r_ust,
        "R_supply": r_supply,
        "R_oil": r_oil,
        "R_fx": r_fx,
        "real_policy": inputs.real_policy_rate(),
        "real_neutral": inputs.real_neutral_rate(),
        "rate_gap": gap,
        "effective_ust10": inputs.effective_ust10(),
        "issuance_pressure": inputs.issuance_pressure(),
    }


def ai_expansion(inputs: HybridInputs) -> dict[str, float]:
    """A typically in [0.8, 2.2]. Demand mix × rack lock-in × FCF × China paradox."""
    other_share = inputs.other_demand_share()
    a_demand = 0.95 + 0.90 * other_share
    a_rack = 0.82 + 0.40 * (0.65 * inputs.nvl72_share + 0.35 * inputs.nvl72_next_year)
    if inputs.bigtech_fcf_positive or inputs.as_of >= inputs.fcf_turn_date:
        a_fcf = 1.32
    elif inputs.as_of >= date(2027, 1, 1):
        a_fcf = 1.08
    else:
        a_fcf = 0.86
    asic_optional = 1.0 + 0.04 * clamp(inputs.google_external_asic_2028_bn / 250.0, 0.0, 1.2)
    # CXMT HBM on 15-16nm DUV without EUV: low-yield, wafer-hungry → KR DRAM defense.
    # YMTC 14% NAND + Xtacking: medium-term NAND price risk, eSSD still gated.
    a_china = 1.0 + 0.18 * inputs.cxmt_hbm_intensity - 0.12 * (inputs.ymtc_nand_share / 0.14)
    a = clamp(a_demand * a_rack * a_fcf * asic_optional * a_china, 0.70, 2.40)
    return {
        "A": a,
        "A_demand": a_demand,
        "A_rack": a_rack,
        "A_fcf": a_fcf,
        "A_asic": asic_optional,
        "A_china": a_china,
        "other_demand_share": other_share,
        "cxmt_dram_defense": 0.18 * inputs.cxmt_hbm_intensity,
        "ymtc_nand_drag": 0.12 * (inputs.ymtc_nand_share / 0.14),
    }


def domestic_defense(inputs: HybridInputs) -> dict[str, float]:
    """D in [0, 1]. Three dams: ISA, Samsung special dividend, KEPCO/infra."""
    d_isa = 0.45 * clamp(inputs.isa_inflow_tn / inputs.isa_full_tn, 0.0, 1.0)
    # A 70% special-div probability is a bid, not a completed 40조 ISA print.
    d_div = 0.06 + 0.16 * inputs.samsung_special_div_prob
    d_infra = 0.12 * inputs.kepco_prepay_signal + 0.02 * clamp(inputs.texas_infra_bn / 25.0, 0.0, 1.5)
    d = clamp(d_isa + d_div + d_infra, 0.0, 1.0)
    return {"D": d, "D_isa": d_isa, "D_div": d_div, "D_infra": d_infra}


def market_momentum(relief: Mapping[str, float], expansion: Mapping[str, float], defense: Mapping[str, float]) -> float:
    return float(relief["R"]) * float(expansion["A"]) + float(defense["D"])


def project_kospi(inputs: HybridInputs, momentum: float, phase: Phase) -> dict[str, float]:
    """Map M into an index path using the semiconductor PE / EPS identity.

    Phase-1 support 6,400–6,600 is the user's STT band. A 10-year print at 5.0%
    applies a mechanical 10–15% hard landing on risk assets.
    """
    implied_eps = inputs.kospi_spot / inputs.semi_fwd_pe
    pe = inputs.semi_fwd_pe + (inputs.semi_target_pe - inputs.semi_fwd_pe) * clamp((momentum - 0.45) / 1.20, 0.0, 1.0)
    eps_factor = 0.97 + 0.22 * clamp(momentum / 2.0, 0.0, 1.0)
    continuous = implied_eps * pe * eps_factor

    low, high = PHASES[phase]["kospi_band"]
    mid = 0.5 * (low + high)
    expected = 0.40 * continuous + 0.60 * mid

    if inputs.hard_landing():
        shock_low, shock_high = HARD_LANDING_DRAWDOWN
        expected = inputs.kospi_spot * (1.0 + 0.5 * (shock_low + shock_high))
        low = inputs.kospi_spot * (1.0 + shock_low)
        high = inputs.kospi_spot * (1.0 + shock_high)
    else:
        expected = clamp(expected, low, high)

    return {
        "expected": expected,
        "band_low": low,
        "band_high": high,
        "implied_eps": implied_eps,
        "projected_pe": pe,
        "eps_factor": eps_factor,
        "continuous": continuous,
    }


def equity_weight_for(inputs: HybridInputs, phase: Phase, relief: Mapping[str, float]) -> float:
    if inputs.hard_landing():
        return 0.45
    _ = relief
    return float(PHASES[phase]["equity_weight"])


@dataclass(frozen=True)
class HybridSnapshot:
    as_of: date
    scenario: str
    phase: Phase
    phase_name: str
    phase_window: str
    phase_narrative: str
    inputs: HybridInputs
    relief: dict[str, float]
    expansion: dict[str, float]
    defense: dict[str, float]
    momentum: float
    kospi: dict[str, float]
    equity_weight: float
    sleeves: dict[str, float]
    structural_cut_open: bool
    partial_cut_room: bool
    hard_landing: bool

    def formula_terms(self) -> dict[str, float]:
        return {
            "R": self.relief["R"],
            "A": self.expansion["A"],
            "D": self.defense["D"],
            "M": self.momentum,
            "R_times_A": self.relief["R"] * self.expansion["A"],
        }

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "as_of": self.as_of.isoformat(),
            "scenario": self.scenario,
            "phase": self.phase.value,
            "phase_name": self.phase_name,
            "phase_window": self.phase_window,
            "phase_narrative": self.phase_narrative,
            "inputs": _inputs_to_dict(self.inputs),
            "relief": self.relief,
            "expansion": self.expansion,
            "defense": self.defense,
            "momentum": self.momentum,
            "formula": self.formula_terms(),
            "kospi": self.kospi,
            "equity_weight": self.equity_weight,
            "cash_bond_weight": 1.0 - self.equity_weight,
            "sleeves": self.sleeves,
            "structural_cut_open": self.structural_cut_open,
            "partial_cut_room": self.partial_cut_room,
            "hard_landing": self.hard_landing,
        }
        return payload


def _inputs_to_dict(inputs: HybridInputs) -> dict[str, Any]:
    raw = asdict(inputs)
    raw["as_of"] = inputs.as_of.isoformat()
    raw["fcf_turn_date"] = inputs.fcf_turn_date.isoformat()
    return raw


def evaluate(inputs: HybridInputs | None = None, *, scenario: Scenario = Scenario.BASE) -> HybridSnapshot:
    src = inputs if inputs is not None else scenario_inputs(scenario)
    relief = macro_relief(src)
    expansion = ai_expansion(src)
    defense = domestic_defense(src)
    momentum = market_momentum(relief, expansion, defense)
    phase = infer_phase(src)
    meta = PHASES[phase]
    kospi = project_kospi(src, momentum, phase)
    equity = equity_weight_for(src, phase, relief)
    return HybridSnapshot(
        as_of=src.as_of,
        scenario=scenario.value,
        phase=phase,
        phase_name=str(meta["name"]),
        phase_window=str(meta["window"]),
        phase_narrative=str(meta["narrative"]),
        inputs=src,
        relief=relief,
        expansion=expansion,
        defense=defense,
        momentum=momentum,
        kospi=kospi,
        equity_weight=equity,
        sleeves=dict(meta["sleeves"]),
        structural_cut_open=src.structural_cut_open(),
        partial_cut_room=src.partial_cut_room(),
        hard_landing=src.hard_landing(),
    )


def evaluate_all_scenarios(base: HybridInputs | None = None) -> dict[str, HybridSnapshot]:
    src = base or baseline_inputs()
    return {item.value: evaluate(scenario_inputs(item, src), scenario=item) for item in Scenario}
