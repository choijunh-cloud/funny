"""python -m hybrid_model

기본은 10/2 스냅샷의 텍스트 보고서. 인자를 주면 그 좌표로 확률을 다시 계산한다.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, replace
from datetime import date

from hybrid_model.model import HybridModel
from hybrid_model.render import render_html, render_text


def _fraction(text: str) -> float:
    value = float(text)
    if value > 1:
        return value / 100
    return value


def _encoder(value: object):
    if isinstance(value, date):
        return value.isoformat()
    raise TypeError(type(value))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="맞힌 패널의 10월 하이브리드 v1.1")
    parser.add_argument("--json", action="store_true", help="기계가 읽는 JSON")
    parser.add_argument("--html", metavar="PATH", help="HTML 보고서를 이 경로에 쓴다")
    parser.add_argument("--kospi", type=float)
    parser.add_argument("--weekly-close", type=float, dest="weekly_close")
    parser.add_argument("--us10y", type=float)
    parser.add_argument("--us30y", type=float)
    parser.add_argument("--foreign-month", type=float, dest="foreign_month_tn")
    parser.add_argument("--foreign-week", type=float, dest="foreign_week_tn")
    parser.add_argument("--oct-hike", type=_fraction, dest="oct_hike_prob", help="퍼센트. 19 또는 0.19")
    parser.add_argument("--core-cpi", type=float, dest="core_cpi_mom", help="근원 CPI MoM 퍼센트. 예: 0.3")
    parser.add_argument("--samsung-op", type=float, dest="samsung_op_tn")
    parser.add_argument("--samsung-reaction", type=float, dest="samsung_reaction_pct")
    parser.add_argument("--brent", type=float)
    parser.add_argument("--usdkrw", type=float)
    parser.add_argument("--micron-reaction", type=float, dest="micron_reaction_pct")
    parser.add_argument("--dec-hike", type=_fraction, dest="dec_hike_prob")
    return parser


def market_from_args(args: argparse.Namespace):
    changes = {
        key: value
        for key, value in vars(args).items()
        if key not in {"json", "html"} and value is not None
    }
    model = HybridModel()
    if not changes:
        return model
    return HybridModel(replace(model.market, **changes))


def report_dict(report) -> dict:
    weights = report.posterior.as_dict()
    return {
        "version": report.posterior.version,
        "prior_version": report.posterior.prior_version,
        "market_asof": report.market.asof.isoformat(),
        "prior": dict(report.posterior.prior),
        "posterior": weights,
        "clipped": report.posterior.clipped,
        "factors": [
            {
                "id": factor.id,
                "tier": factor.tier,
                "title": factor.title,
                "intensity": factor.intensity,
                "delta": dict(factor.delta),
                "active": factor.active,
                "explain": factor.explain,
            }
            for factor in report.posterior.factors
        ],
        "scenarios": [
            {
                "code": scenario.code,
                "title": scenario.title,
                "weight": weights[scenario.code],
                "paths": [asdict(band) | {"mid": band.mid} for band in scenario.paths],
            }
            for scenario in report.scenarios
        ],
        "leaderboard": [
            {
                "name": panel.name,
                "hit_pct": panel.hit_pct,
                "n": panel.n,
                "main": panel.main,
                "composite_pct": panel.composite_pct,
            }
            for panel in report.panels
        ],
        "clocks": [
            {
                "name": clock.name,
                "remaining_tn": clock.remaining_tn,
                "sessions": clock.sessions,
                "exhaust_date": clock.exhaust_date.isoformat(),
                "krx_date": None if clock.krx_date is None else clock.krx_date.isoformat(),
                "published_date": clock.published_date.isoformat(),
            }
            for clock in report.clocks
        ],
        "flags": list(report.flags),
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = market_from_args(args).run()
    if args.html:
        with open(args.html, "w", encoding="utf-8") as handle:
            handle.write(render_html(report))
    if args.json:
        json.dump(report_dict(report), sys.stdout, ensure_ascii=False, indent=2, default=_encoder)
        sys.stdout.write("\n")
    elif not args.html:
        sys.stdout.write(render_text(report))
    else:
        sys.stdout.write(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
