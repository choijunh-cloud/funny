#!/usr/bin/env python3
"""Verify hyperscaler cash-capex acceleration and beneficiary price leads.

Data are pulled from SEC company facts and Yahoo daily closes, then cached
under data/cache. Rerun with --refresh after a new 10-Q.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capex_accel.backtest import (
    confirmed_acceleration_peaks,
    cross_correlation,
    gain_share,
    growth_cycle_peaks,
    months_between,
    price_high_around,
)
from capex_accel.metrics import build_frame, extend_with_targets, future_quarter_to_beat, next_quarter_thresholds
from capex_accel.plotting import plot_gain_share, plot_history, plot_lead_times, plot_prices, plot_scenarios
from capex_accel.prices import fetch_prices, price_asof
from capex_accel.report import render
from capex_accel.sec_capex import annual_sums, combined_cash, load_company_quarters

BASE_A = [10.8, -6.2, 13.7, -15.3, 0.1, 4.9]
REACCEL_A = [10.8, -6.2, 38.7, -15.3, 0.1, 4.9]
CHECKPOINTS = [date(2024, 12, 31), date(2025, 6, 30), date(2025, 12, 31), date(2026, 3, 31)]
GAIN_START = date(2023, 1, 3)
Q4_ASSUMPTION = 200.0


def _mean_corr_phrase(table: dict[str, dict[int, float | None]]) -> str:
    lags = sorted(next(iter(table.values())))
    means = {}
    for lag in lags:
        vals = [name_lags[lag] for name_lags in table.values() if name_lags[lag] is not None]
        if not vals:
            continue
        means[lag] = sum(vals) / len(vals)
    best = max(means, key=lambda lag: means[lag])
    return f"{best:+d}분기(평균 상관 {means[best]:+.2f})"


def _current_rally(rows, signal: date) -> dict:
    subset = [(d, px) for d, px in rows if d >= date(2024, 1, 1)]
    peak_d, peak_px = max(subset, key=lambda item: item[1])
    after = [px for d, px in subset if d >= peak_d]
    trough = min(after)
    last_d, last_px = subset[-1]
    confirmed = trough <= peak_px * 0.75
    return {
        "peak_date": peak_d.isoformat(),
        "peak_price": peak_px,
        "lag_months": months_between(peak_d, signal),
        "current_drawdown": last_px / peak_px - 1,
        "trough_drawdown": trough / peak_px - 1,
        "last_date": last_d.isoformat(),
        "note": (
            f"고점 후 최대 {trough / peak_px - 1:.0%}, 10월 초 {last_px / peak_px - 1:.0%}"
            if confirmed
            else "10월에도 고점 부근. 25% 조정 없음"
        ),
        "drawdown": trough / peak_px - 1,
    }


def run(refresh: bool = False) -> dict:
    series = load_company_quarters(refresh=refresh)
    quarters, totals, by_q = combined_cash(series)
    frame = build_frame(quarters, totals)
    prices = fetch_prices(refresh=refresh)

    q2 = date(2026, 6, 30)
    i_q2 = frame.index(q2)
    # 2026 Q3 is one quarter ahead, so its year-ago cash print is 2025 Q3,
    # three quarter-steps before 2026 Q2. i-4 would be 2025 Q2.
    thresholds = next_quarter_thresholds(
        c_prev_year=frame.c[i_q2 - 3],
        increment=frame.increment[i_q2],
        acceleration=frame.acceleration[i_q2],
    )
    q1_2027_threshold = future_quarter_to_beat(
        anchor_c=frame.value(date(2026, 3, 31), "c"),
        anchor_a=frame.acceleration[i_q2],
        intervening_increment=Q4_ASSUMPTION - frame.value(date(2025, 12, 31), "c"),
    )

    extensions = {
        "base": extend_with_targets(frame.quarters, frame.c, frame.increment[i_q2], BASE_A),
        "reaccel": extend_with_targets(frame.quarters, frame.c, frame.increment[i_q2], REACCEL_A),
    }
    scenario_paths = {}
    for name, built in extensions.items():
        hist = [
            (q, a)
            for q, a in zip(frame.quarters, frame.acceleration)
            if a is not None and q >= date(2025, 12, 31)
        ]
        scenario_paths[name] = hist + [(row["quarter"], row["acceleration"]) for row in built]

    def year_sum(rows, year: int) -> float:
        return sum(row["c"] for row in rows if row["quarter"].year == year)

    h1 = frame.value(date(2026, 3, 31), "c") + frame.value(q2, "c")
    annual_2025 = annual_sums(by_q, 2025)["TOTAL"]
    msft_fy = sum(
        by_q[q]["MSFT"]
        for q in (date(2025, 9, 30), date(2025, 12, 31), date(2026, 3, 31), date(2026, 6, 30))
    )

    growth_peaks = growth_cycle_peaks(frame)
    accel_peaks = confirmed_acceleration_peaks(frame)

    leads = []
    for peak in growth_peaks:
        signal = peak["quarter"]
        label = f"{signal.year} Q{(signal.month - 1) // 3 + 1} 성장률"
        for name, rows in prices.items():
            info = price_high_around(rows, signal)
            leads.append(
                {
                    "cycle": label,
                    "name": name,
                    "peak_date": None if info["peak_date"] is None else info["peak_date"].isoformat(),
                    "lag_months": info["lag_months"],
                    "drawdown": info["drawdown"],
                    "status": info["status"],
                    "current_drawdown": info["drawdown"],
                    "note": info["status"],
                }
            )

    signal_now = q2
    for name, rows in prices.items():
        info = _current_rally(rows, signal_now)
        info["cycle"] = "2026 Q2 가속도 후보"
        info["name"] = name
        leads.append(info)

    shares = {}
    multiples = {}
    rally_peaks = {}
    for name, rows in prices.items():
        high = _current_rally(rows, signal_now)
        peak_day = date.fromisoformat(high["peak_date"])
        rally_peaks[name] = peak_day
        shares[name] = [
            {**row, "checkpoint": row["checkpoint"].isoformat()}
            for row in gain_share(rows, GAIN_START, peak_day, CHECKPOINTS)
        ]
        start_px = price_asof(rows, GAIN_START)
        peak_px = price_asof(rows, peak_day)
        multiples[name] = peak_px[1] / start_px[1]

    corr_full = cross_correlation(frame, prices, "acceleration", start=date(2018, 3, 31), end=q2)
    corr_pre = cross_correlation(
        frame, prices, "acceleration", start=date(2018, 3, 31), end=date(2023, 12, 31)
    )

    frame_rows = []
    parts = {}
    for i, qe in enumerate(frame.quarters):
        frame_rows.append(
            {
                "quarter": qe.isoformat(),
                "c": frame.c[i],
                "ttm": frame.ttm[i],
                "increment": frame.increment[i],
                "acceleration": frame.acceleration[i],
                "ttm_yoy": frame.ttm_yoy[i],
                "ttm_yoy_change": frame.ttm_yoy_change[i],
                "quarterly_yoy": frame.quarterly_yoy[i],
            }
        )
        parts[qe.isoformat()] = by_q[qe]

    base_2026_future = [row["c"] for row in extensions["base"] if row["quarter"].year == 2026]
    result = {
        "frame_rows": frame_rows,
        "parts": parts,
        "latest": frame_rows[-1],
        "thresholds": thresholds,
        "q4_assumption": Q4_ASSUMPTION,
        "q1_2027_threshold": q1_2027_threshold,
        "growth_peaks": [
            {"quarter": p["quarter"].isoformat(), "value": p["value"], "trough": p["trough"]}
            for p in growth_peaks
        ],
        "acceleration_peaks": [
            {"quarter": p["quarter"].isoformat(), "value": p["value"]} for p in accel_peaks
        ],
        "leads": leads,
        "shares": shares,
        "multiples": multiples,
        "scenario_totals": {
            "base_q3": extensions["base"][0]["c"],
            "base_q4": extensions["base"][1]["c"],
            "base_2026": h1 + sum(base_2026_future),
            "base_2027": year_sum(extensions["base"], 2027),
            "reaccel_2027": year_sum(extensions["reaccel"], 2027),
            "reaccel_a_q1": extensions["reaccel"][2]["acceleration"],
        },
        "annual_2025": annual_2025,
        "h1_2026": h1,
        "msft_fy2026": msft_fy,
        "gs_rate_on_four": annual_2025 * 1.94,
        "growth_if_680": 680 / annual_2025 - 1,
        "corr_summary": {
            "full": _mean_corr_phrase(corr_full),
            "pre_ai": _mean_corr_phrase(corr_pre),
        },
        "price_end": max(rows[-1][0] for rows in prices.values()).isoformat(),
        "prices": prices,
        "scenario_paths": scenario_paths,
        "rally_peaks": rally_peaks,
        "frame": frame,
    }
    return result


def _write_outputs(result: dict) -> None:
    out = ROOT / "output"
    fig = out / "figures"
    art = Path("/opt/cursor/artifacts")
    fig.mkdir(parents=True, exist_ok=True)
    art.mkdir(parents=True, exist_ok=True)

    csv_path = out / "capex_quarterly.csv"
    with csv_path.open("w", newline="") as handle:
        fields = [
            "quarter",
            "c",
            "ttm",
            "increment",
            "acceleration",
            "ttm_yoy",
            "ttm_yoy_change",
            "quarterly_yoy",
            "MSFT",
            "GOOGL",
            "AMZN",
            "META",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in result["frame_rows"]:
            parts = result["parts"][row["quarter"]]
            writer.writerow({**row, **parts})

    frame = result["frame"]
    plot_history(frame, fig / "capex_acceleration.png")
    plot_scenarios(frame, result["scenario_paths"], fig / "capex_scenarios.png")
    plot_prices(result["prices"], result["rally_peaks"], fig / "beneficiary_prices.png")
    plot_gain_share(result["shares"], fig / "priced_in_share.png")
    plot_lead_times(result["leads"], fig / "lead_times.png")

    note = render(result)
    report_path = ROOT / "analysis" / "CAPEX_ACCELERATION.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(note)

    for name in (
        "capex_acceleration.png",
        "capex_scenarios.png",
        "beneficiary_prices.png",
        "priced_in_share.png",
        "lead_times.png",
    ):
        target = art / name
        target.write_bytes((fig / name).read_bytes())
    (art / "CAPEX_ACCELERATION.md").write_text(note)
    (art / "capex_quarterly.csv").write_bytes(csv_path.read_bytes())

    keep = {
        key: result[key]
        for key in (
            "thresholds",
            "q1_2027_threshold",
            "growth_peaks",
            "acceleration_peaks",
            "scenario_totals",
            "annual_2025",
            "h1_2026",
            "msft_fy2026",
            "gs_rate_on_four",
            "growth_if_680",
            "corr_summary",
            "multiples",
            "leads",
        )
    }
    (out / "summary.json").write_text(json.dumps(keep, indent=2, default=str))
    (art / "summary.json").write_text(json.dumps(keep, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    result = run(refresh=args.refresh)
    _write_outputs(result)
    q = result["frame_rows"][-1]
    print(
        f"2026 Q2 cash {q['c']:.2f}  A {q['acceleration']:.2f}  "
        f"TTM growth {q['ttm_yoy'] * 100:.1f}%"
    )
    print(
        "Q3 thresholds: "
        f"stay positive {result['thresholds']['stay_positive']:.1f}, "
        f"new high {result['thresholds']['new_high']:.1f}"
    )
    print("growth peaks", result["growth_peaks"])
    print("wrote analysis/CAPEX_ACCELERATION.md")


if __name__ == "__main__":
    main()
