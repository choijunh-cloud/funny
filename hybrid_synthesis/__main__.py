"""CLI: python3 -m hybrid_synthesis [--scenario base] [--out reports]."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

from hybrid_synthesis.model import Scenario, baseline_inputs, evaluate, evaluate_all_scenarios
from hybrid_synthesis.portfolio import build_portfolio
from hybrid_synthesis.report import write_reports


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="KOSPI hybrid synthesis portfolio")
    parser.add_argument("--scenario", choices=[item.value for item in Scenario], default=Scenario.BASE.value)
    parser.add_argument("--all-scenarios", action="store_true")
    parser.add_argument("--out", type=Path, default=Path("reports"))
    parser.add_argument("--ust10", type=float)
    parser.add_argument("--pce", type=float)
    parser.add_argument("--oil", type=float)
    parser.add_argument("--fed", type=float)
    parser.add_argument("--kospi", type=float)
    parser.add_argument("--isa", type=float, help="ISA inflow in trillion KRW")
    parser.add_argument("--fcf-positive", action="store_true")
    parser.add_argument("--as-of", type=str, help="YYYY-MM-DD")
    parser.add_argument("--reference-krw", type=float, default=100_000_000.0)
    parser.add_argument("--json-only", action="store_true")
    return parser.parse_args()


def _apply_overrides(args: argparse.Namespace) -> HybridInputs:
    inputs = baseline_inputs()
    updates: dict[str, object] = {}
    if args.ust10 is not None:
        updates["ust10"] = args.ust10
    if args.pce is not None:
        updates["pce_yoy"] = args.pce
    if args.oil is not None:
        updates["oil_brent"] = args.oil
    if args.fed is not None:
        updates["fed_funds"] = args.fed
    if args.kospi is not None:
        updates["kospi_spot"] = args.kospi
    if args.isa is not None:
        updates["isa_inflow_tn"] = args.isa
    if args.fcf_positive:
        updates["bigtech_fcf_positive"] = True
    if args.as_of:
        updates["as_of"] = date.fromisoformat(args.as_of)
    return replace(inputs, **updates) if updates else inputs


def main() -> None:
    args = _parse_args()
    inputs = _apply_overrides(args)
    scenario = Scenario(args.scenario)
    snapshot = evaluate(inputs, scenario=scenario)
    portfolio = build_portfolio(snapshot, reference_krw=args.reference_krw)
    scenarios = evaluate_all_scenarios(inputs) if args.all_scenarios else {scenario.value: snapshot}

    args.out.mkdir(parents=True, exist_ok=True)
    payload = {
        "portfolio": portfolio.to_dict(),
        "scenarios": {key: item.to_dict() for key, item in scenarios.items()},
    }
    if args.json_only:
        json_path = args.out / "hybrid-synthesis.json"
        json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json_path)
        return

    paths = write_reports(portfolio, scenarios, args.out)
    for path in paths:
        print(path)


if __name__ == "__main__":
    main()
