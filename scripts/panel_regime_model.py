"""
Panel Synthesis Comprehensive State-Space Regime Model
------------------------------------------------------
All-in-One Engine integrating Factor Aggregation, Softmax Regime Probability,
KOSPI Mixture Quantile Projection, and Clustered Execution Risk Review.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, fields
from datetime import date
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple

ASSET_KEYS = (
    "Semiconductor",
    "AI_Compute",
    "Power_Grid",
    "Non_Semi_Export",
    "Cash",
)
ASSET_LABELS_KO = {
    "Semiconductor": "반도체",
    "AI_Compute": "AI 연산",
    "Power_Grid": "전력망",
    "Non_Semi_Export": "비반도체 수출",
    "Cash": "현금",
}
HORIZONS = ("3M", "6M", "12M")
HORIZON_LABELS_KO = {"3M": "3개월", "6M": "6개월", "12M": "12개월"}
FACTOR_LABELS_KO = {
    "memory_price": "메모리 가격",
    "earnings_outlook": "실적 전망",
    "ai_physical_demand": "AI 실물 수요",
    "supply_discipline": "공급 규율",
    "china_memory_supply_balance": "중국 메모리 수급",
    "ai_financing": "AI 자금조달",
    "rates_fx": "금리·환율",
    "foreign_flows": "외국인 수급",
}


def _validate_score(name: str, value: float) -> None:
    if not math.isfinite(value) or not -1.0 <= value <= 1.0:
        raise ValueError(f"{name} must be finite and within [-1.0, 1.0]; got {value!r}")


def _largest_remainder_percentages(values: Sequence[float]) -> Tuple[int, ...]:
    if not values or any(value < 0.0 or not math.isfinite(value) for value in values):
        raise ValueError("values must be a non-empty sequence of finite, non-negative shares")
    total = sum(values)
    if total <= 0.0:
        raise ValueError("values must have a positive sum")
    scaled = [value / total * 100.0 for value in values]
    floors = [math.floor(value) for value in scaled]
    remaining = 100 - sum(floors)
    order = sorted(
        range(len(values)),
        key=lambda index: (scaled[index] - floors[index], -index),
        reverse=True,
    )
    for index in order[:remaining]:
        floors[index] += 1
    return tuple(int(value) for value in floors)


@dataclass(frozen=True)
class MacroFactors:
    memory_price: float
    earnings_outlook: float
    ai_physical_demand: float
    supply_discipline: float
    china_memory_supply_balance: float
    ai_financing: float
    rates_fx: float
    foreign_flows: float

    def __post_init__(self) -> None:
        for model_field in fields(self):
            _validate_score(model_field.name, float(getattr(self, model_field.name)))

    def physical_vector(self) -> Tuple[float, ...]:
        return (
            self.memory_price,
            self.earnings_outlook,
            self.ai_physical_demand,
            self.supply_discipline,
            self.china_memory_supply_balance,
        )

    def financial_vector(self) -> Tuple[float, ...]:
        return (self.ai_financing, self.rates_fx, self.foreign_flows)


@dataclass(frozen=True)
class RegimeCentroid:
    name: str
    p_coord: float
    f_coord: float
    policy_weights: Mapping[str, float]


@dataclass(frozen=True)
class KospiMixtureProjection:
    expected_level: float
    p10: float
    p50: float
    p90: float
    support_low: float
    support_high: float


@dataclass(frozen=True)
class PriceObservation:
    spot_price: float
    contract_price: float
    spot_product: str
    contract_product: str
    spot_unit: str
    contract_unit: str
    spot_as_of: date
    contract_as_of: date

    def __post_init__(self) -> None:
        if not math.isfinite(self.spot_price) or self.spot_price <= 0.0:
            raise ValueError("spot_price must be finite and positive")
        if not math.isfinite(self.contract_price) or self.contract_price <= 0.0:
            raise ValueError("contract_price must be finite and positive")

    def comparability_issues(self, max_gap_days: int = 35) -> Tuple[str, ...]:
        issues = []
        if self.spot_product.strip().casefold() != self.contract_product.strip().casefold():
            issues.append("spot and contract products differ")
        if self.spot_unit.strip().casefold() != self.contract_unit.strip().casefold():
            issues.append("spot and contract units differ")
        gap_days = abs((self.spot_as_of - self.contract_as_of).days)
        if gap_days > max_gap_days:
            issues.append(f"observation dates are {gap_days} days apart")
        return tuple(issues)

    def spread_percent(self) -> float:
        return (self.spot_price - self.contract_price) / self.contract_price * 100.0


@dataclass(frozen=True)
class ExecutionInputs:
    price_observation: Optional[PriceObservation] = None
    earnings_outlook: Optional[float] = None
    ai_financing: Optional[float] = None
    rates_fx: Optional[float] = None
    foreign_flows: Optional[float] = None
    kospi_level: Optional[float] = None
    rolling_high: Optional[float] = None
    forward_pe: Optional[float] = None
    valuation_ceiling: Optional[float] = None

    def __post_init__(self) -> None:
        for name in ("earnings_outlook", "ai_financing", "rates_fx", "foreign_flows"):
            value = getattr(self, name)
            if value is not None:
                _validate_score(name, float(value))
        for name in ("kospi_level", "rolling_high", "forward_pe", "valuation_ceiling"):
            value = getattr(self, name)
            if value is not None and (not math.isfinite(value) or value <= 0.0):
                raise ValueError(f"{name} must be finite and positive when supplied")


@dataclass(frozen=True)
class ExecutionAssessment:
    level: str
    stress_clusters: Tuple[str, ...]
    messages: Tuple[str, ...]


class TwoAxisRegimeClassifier:
    def __init__(self) -> None:
        self.regimes: Dict[str, RegimeCentroid] = {
            "A": RegimeCentroid(
                name="A: Re-acceleration (재가속)",
                p_coord=0.70,
                f_coord=0.30,
                policy_weights={
                    "Semiconductor": 0.45,
                    "AI_Compute": 0.15,
                    "Power_Grid": 0.15,
                    "Non_Semi_Export": 0.15,
                    "Cash": 0.10,
                },
            ),
            "B": RegimeCentroid(
                name="B: Late verification (후기검증)",
                p_coord=0.40,
                f_coord=0.00,
                policy_weights={
                    "Semiconductor": 0.38,
                    "AI_Compute": 0.12,
                    "Power_Grid": 0.16,
                    "Non_Semi_Export": 0.16,
                    "Cash": 0.18,
                },
            ),
            "B*": RegimeCentroid(
                name="B*: Physical boom / financial squeeze (실물호황·신용경색)",
                p_coord=0.55,
                f_coord=-0.65,
                policy_weights={
                    "Semiconductor": 0.32,
                    "AI_Compute": 0.06,
                    "Power_Grid": 0.20,
                    "Non_Semi_Export": 0.17,
                    "Cash": 0.25,
                },
            ),
            "C": RegimeCentroid(
                name="C: Soft landing / rotation (연착륙·순환)",
                p_coord=-0.05,
                f_coord=0.20,
                policy_weights={
                    "Semiconductor": 0.28,
                    "AI_Compute": 0.10,
                    "Power_Grid": 0.18,
                    "Non_Semi_Export": 0.22,
                    "Cash": 0.22,
                },
            ),
            "D": RegimeCentroid(
                name="D: Defensive downside (방어)",
                p_coord=-0.35,
                f_coord=-0.45,
                policy_weights={
                    "Semiconductor": 0.18,
                    "AI_Compute": 0.05,
                    "Power_Grid": 0.15,
                    "Non_Semi_Export": 0.17,
                    "Cash": 0.45,
                },
            ),
        }
        self.weights_p: Dict[str, Tuple[float, ...]] = {
            "3M": (0.18, 0.15, 0.18, 0.10, 0.07),
            "6M": (0.15, 0.13, 0.18, 0.09, 0.10),
            "12M": (0.08, 0.09, 0.16, 0.07, 0.16),
        }
        self.weights_f: Dict[str, Tuple[float, ...]] = {
            "3M": (0.10, 0.12, 0.10),
            "6M": (0.12, 0.14, 0.09),
            "12M": (0.14, 0.20, 0.10),
        }
        self.axis_metric_weights: Dict[str, Tuple[float, float]] = {
            "3M": (1.0, 1.0),
            "6M": (1.0, 1.0),
            "12M": (1.0, 1.0),
        }
        self.temperature: Dict[str, float] = {"3M": 0.52, "6M": 0.68, "12M": 0.78}
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        for horizon in HORIZONS:
            if len(self.weights_p[horizon]) != 5 or len(self.weights_f[horizon]) != 3:
                raise ValueError(f"unexpected factor count for {horizon}")
            if min(self.weights_p[horizon] + self.weights_f[horizon]) < 0.0:
                raise ValueError(f"factor coefficients must be non-negative for {horizon}")
            if self.temperature[horizon] <= 0.0:
                raise ValueError(f"temperature must be positive for {horizon}")

    @staticmethod
    def _weighted_average(values: Sequence[float], weights: Sequence[float]) -> float:
        denominator = sum(weights)
        return sum(v * w for v, w in zip(values, weights)) / denominator

    def compute_state_vector(self, horizon: str, factors: MacroFactors) -> Tuple[float, float]:
        p_val = self._weighted_average(factors.physical_vector(), self.weights_p[horizon])
        f_val = self._weighted_average(factors.financial_vector(), self.weights_f[horizon])
        return p_val, f_val

    def calculate_regime_weights(self, p_val: float, f_val: float, horizon: str) -> Dict[str, float]:
        log_weights = {}
        pw, fw = self.axis_metric_weights[horizon]
        for code, reg in self.regimes.items():
            dist2 = pw * (p_val - reg.p_coord) ** 2 + fw * (f_val - reg.f_coord) ** 2
            log_weights[code] = -dist2 / self.temperature[horizon]
        max_lw = max(log_weights.values())
        shifted = {code: math.exp(v - max_lw) for code, v in log_weights.items()}
        total = sum(shifted.values())
        return {code: v / total for code, v in shifted.items()}

    def compute_policy_allocation(self, regime_weights: Mapping[str, float]) -> Dict[str, float]:
        allocation = {asset: 0.0 for asset in ASSET_KEYS}
        for code, prob in regime_weights.items():
            for asset in ASSET_KEYS:
                allocation[asset] += prob * self.regimes[code].policy_weights[asset]
        return allocation

    def project_kospi_mixture(
        self, regime_weights: Mapping[str, float], anchor_bands: Mapping[str, Tuple[float, float]]
    ) -> KospiMixtureProjection:
        support_low = min(band[0] for band in anchor_bands.values())
        support_high = max(band[1] for band in anchor_bands.values())

        def mixture_cdf(lvl: float) -> float:
            res = 0.0
            for code, prob in regime_weights.items():
                low, high = anchor_bands[code]
                if lvl <= low:
                    cond = 0.0
                elif lvl >= high:
                    cond = 1.0
                else:
                    cond = (lvl - low) / (high - low)
                res += prob * cond
            return res

        def quantile(target: float) -> float:
            low, high = support_low, support_high
            for _ in range(100):
                mid = (low + high) / 2.0
                if mixture_cdf(mid) < target:
                    low = mid
                else:
                    high = mid
            return (low + high) / 2.0

        expected = sum(regime_weights[c] * sum(anchor_bands[c]) / 2.0 for c in regime_weights)
        return KospiMixtureProjection(
            expected_level=expected,
            p10=quantile(0.10),
            p50=quantile(0.50),
            p90=quantile(0.90),
            support_low=support_low,
            support_high=support_high,
        )

    def evaluate_execution_signals(
        self, inputs: ExecutionInputs, max_price_gap_days: int = 35
    ) -> ExecutionAssessment:
        messages = []
        stress_clusters = []
        spread_is_non_positive = False

        if inputs.price_observation is None:
            messages.append("Price spread not evaluated: no observation supplied.")
        else:
            issues = inputs.price_observation.comparability_issues(max_price_gap_days)
            if issues:
                messages.append("Price spread not evaluated: " + "; ".join(issues) + ".")
            else:
                spread = inputs.price_observation.spread_percent()
                spread_is_non_positive = spread <= 0.0
                if spread <= 0.0:
                    messages.append(
                        f"🚨 Comparable spot-contract spread is non-positive ({spread:+.1f}%)."
                    )
                elif spread <= 5.0:
                    messages.append(
                        f"⚠️ Comparable spot premium is narrow ({spread:+.1f}%); monitor."
                    )
                else:
                    messages.append(f"✅ Comparable spot premium is positive ({spread:+.1f}%).")

        if (
            spread_is_non_positive
            and inputs.earnings_outlook is not None
            and inputs.earnings_outlook <= -0.25
        ):
            stress_clusters.append("memory")
            messages.append("Memory stress confirmed by both price and earnings signals.")

        if inputs.ai_financing is not None and inputs.ai_financing <= -0.50:
            stress_clusters.append("ai_financing")
            messages.append("AI financing stress cluster is active.")

        liquidity_vals = [v for v in (inputs.rates_fx, inputs.foreign_flows) if v is not None]
        if len(liquidity_vals) == 2 and sum(liquidity_vals) / 2.0 <= -0.40:
            stress_clusters.append("macro_liquidity")
            messages.append("Macro-liquidity stress is confirmed by rates/FX and foreign flows.")

        if (
            inputs.forward_pe is not None
            and inputs.valuation_ceiling is not None
            and inputs.forward_pe >= inputs.valuation_ceiling
        ):
            stress_clusters.append("valuation")
            messages.append(
                f"Forward P/E ({inputs.forward_pe:.1f}) exceeds ceiling ({inputs.valuation_ceiling:.1f})."
            )

        if inputs.kospi_level is not None and inputs.rolling_high is not None:
            drawdown = inputs.kospi_level / inputs.rolling_high - 1.0
            messages.append(f"KOSPI drawdown from rolling high: {drawdown * 100:+.1f}%.")
            if drawdown <= -0.40:
                messages.append("Deep drawdown detected (Retracement >= 50% zone).")

        c_count = len(stress_clusters)
        level = (
            "DEFENSIVE_REVIEW"
            if c_count >= 3
            else "RISK_REVIEW"
            if c_count == 2
            else "WATCH"
            if c_count == 1
            else "NORMAL"
        )
        messages.append("Decision rule: Allocation adjustment requires human review.")
        return ExecutionAssessment(level, tuple(stress_clusters), tuple(messages))

    @staticmethod
    def display_percentages(regime_weights: Mapping[str, float]) -> Dict[str, int]:
        codes = tuple(regime_weights)
        rounded = _largest_remainder_percentages(tuple(regime_weights[c] for c in codes))
        return dict(zip(codes, rounded))


SUPPLIED_KOSPI_ANCHORS: Dict[str, Dict[str, Tuple[float, float]]] = {
    horizon: {
        "A": (8200.0, 9300.0),
        "B": (7200.0, 8100.0),
        "B*": (6400.0, 7300.0),
        "C": (6200.0, 7000.0),
        "D": (5200.0, 5800.0),
    }
    for horizon in HORIZONS
}

BASELINE_FACTORS: Dict[str, MacroFactors] = {
    "3M": MacroFactors(
        memory_price=0.65,
        earnings_outlook=0.40,
        ai_physical_demand=0.70,
        supply_discipline=0.45,
        china_memory_supply_balance=-0.05,
        ai_financing=-0.20,
        rates_fx=-0.10,
        foreign_flows=-0.22,
    ),
    "6M": MacroFactors(
        memory_price=0.40,
        earnings_outlook=0.20,
        ai_physical_demand=0.60,
        supply_discipline=0.25,
        china_memory_supply_balance=-0.15,
        ai_financing=-0.20,
        rates_fx=0.00,
        foreign_flows=0.00,
    ),
    "12M": MacroFactors(
        memory_price=0.05,
        earnings_outlook=-0.10,
        ai_physical_demand=0.35,
        supply_discipline=0.05,
        china_memory_supply_balance=-0.25,
        ai_financing=-0.25,
        rates_fx=0.08,
        foreign_flows=0.00,
    ),
}

BASELINE_EXECUTION = ExecutionInputs(
    price_observation=PriceObservation(
        spot_price=52.73,
        contract_price=44.50,
        spot_product="DDR5 16Gb",
        contract_product="DDR5 16Gb",
        spot_unit="USD",
        contract_unit="USD",
        spot_as_of=date(2026, 8, 14),
        contract_as_of=date(2026, 7, 31),
    ),
    earnings_outlook=0.40,
    ai_financing=-0.20,
    rates_fx=-0.10,
    foreign_flows=-0.22,
    kospi_level=6852.0,
    rolling_high=9360.0,
    forward_pe=10.2,
    valuation_ceiling=12.5,
)


def run_baseline(model: Optional[TwoAxisRegimeClassifier] = None) -> Dict[str, Any]:
    """Run the supplied August 2026 baseline and return a JSON-ready snapshot."""
    model = model or TwoAxisRegimeClassifier()
    horizons: Dict[str, Any] = {}
    for horizon in HORIZONS:
        factors = BASELINE_FACTORS[horizon]
        p_val, f_val = model.compute_state_vector(horizon, factors)
        weights = model.calculate_regime_weights(p_val, f_val, horizon)
        allocation = model.compute_policy_allocation(weights)
        projection = model.project_kospi_mixture(weights, SUPPLIED_KOSPI_ANCHORS[horizon])
        horizons[horizon] = {
            "p": p_val,
            "f": f_val,
            "weights": weights,
            "disp": model.display_percentages(weights),
            "alloc": allocation,
            "alloc_disp": dict(
                zip(ASSET_KEYS, _largest_remainder_percentages(tuple(allocation[k] for k in ASSET_KEYS)))
            ),
            "proj": asdict(projection),
            "physical": {
                "memory_price": factors.memory_price,
                "earnings_outlook": factors.earnings_outlook,
                "ai_physical_demand": factors.ai_physical_demand,
                "supply_discipline": factors.supply_discipline,
                "china_memory_supply_balance": factors.china_memory_supply_balance,
            },
            "financial": {
                "ai_financing": factors.ai_financing,
                "rates_fx": factors.rates_fx,
                "foreign_flows": factors.foreign_flows,
            },
        }

    assessment = model.evaluate_execution_signals(BASELINE_EXECUTION)
    observation = BASELINE_EXECUTION.price_observation
    assert observation is not None
    kospi = float(BASELINE_EXECUTION.kospi_level or 0.0)
    rolling_high = float(BASELINE_EXECUTION.rolling_high or 0.0)
    return {
        "horizons": horizons,
        "regimes": {
            code: {
                "name": reg.name,
                "p_coord": reg.p_coord,
                "f_coord": reg.f_coord,
                "policy_weights": dict(reg.policy_weights),
            }
            for code, reg in model.regimes.items()
        },
        "anchors": {horizon: dict(bands) for horizon, bands in SUPPLIED_KOSPI_ANCHORS.items()},
        "execution": {
            "level": assessment.level,
            "clusters": list(assessment.stress_clusters),
            "messages": list(assessment.messages),
            "spread": observation.spread_percent(),
            "drawdown": kospi / rolling_high - 1.0,
            "spot": observation.spot_price,
            "contract": observation.contract_price,
            "spot_product": observation.spot_product,
            "spot_as_of": observation.spot_as_of.isoformat(),
            "contract_as_of": observation.contract_as_of.isoformat(),
            "kospi": kospi,
            "rolling_high": rolling_high,
            "forward_pe": BASELINE_EXECUTION.forward_pe,
            "valuation_ceiling": BASELINE_EXECUTION.valuation_ceiling,
            "earnings_outlook": BASELINE_EXECUTION.earnings_outlook,
            "ai_financing": BASELINE_EXECUTION.ai_financing,
            "rates_fx": BASELINE_EXECUTION.rates_fx,
            "foreign_flows": BASELINE_EXECUTION.foreign_flows,
        },
    }


if __name__ == "__main__":
    model = TwoAxisRegimeClassifier()
    print("=" * 80)
    print("  [PANEL SYNTHESIS MASTER REGIME MODEL RUN — BASELINE]")
    print("=" * 80)

    for horizon in HORIZONS:
        p, f = model.compute_state_vector(horizon, BASELINE_FACTORS[horizon])
        weights = model.calculate_regime_weights(p, f, horizon)
        alloc = model.compute_policy_allocation(weights)
        proj = model.project_kospi_mixture(weights, SUPPLIED_KOSPI_ANCHORS[horizon])
        disp = model.display_percentages(weights)

        print(f"\n▶ [{horizon} Horizon] State Vector: P = {p:+.3f}, F = {f:+.3f}")
        print("  • Regime Probabilities :", ", ".join(f"{c}={disp[c]}%" for c in model.regimes))
        print(
            "  • Policy Allocation    :",
            ", ".join(f"{k}={alloc[k]*100:4.1f}%" for k in ASSET_KEYS),
        )
        print(
            "  • KOSPI Mixture Proj.  : "
            f"Mean={proj.expected_level:.0f} pt | P10={proj.p10:.0f} pt | "
            f"P50={proj.p50:.0f} pt | P90={proj.p90:.0f} pt"
        )

    print("\n" + "=" * 80)
    print("  [CLUSTERED RISK & EXECUTION TRIGGER EVALUATION]")
    print("=" * 80)

    assessment = model.evaluate_execution_signals(BASELINE_EXECUTION)
    print(f"Trigger Status: [{assessment.level}]")
    for msg in assessment.messages:
        print(f"  - {msg}")
    print("=" * 80)
