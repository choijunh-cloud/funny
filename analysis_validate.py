import math
from dataclasses import dataclass

# Values transcribed from the chart (units: HKD unless noted)
EPS = {
    "2026E": 18.26,
    "2027E": 19.85,
    "2028E": 21.00,
}
SIGMA = {
    "2026E": 1.81,
    "2027E": 2.43,
    "2028E": 2.96,
}

# cross-validation bars in the chart
CROSS_VAL = {
    "Original": 507,
    "Corrected": 438,
    "Final Core": 387,
    "Final Reported": 511,
    "Final Reported PE30": 591,
    "MC Mean": 493,
}

BASELINE = 500


def price(pe: float, eps: float) -> float:
    return pe * eps


def pct(v: float, base: float = BASELINE) -> float:
    return (v / base - 1.0) * 100


def validate_eps_bars() -> list[str]:
    rows = []
    for y in ("2026E", "2027E", "2028E"):
        low = EPS[y] - SIGMA[y]
        high = EPS[y] + SIGMA[y]
        rows.append(f"{y}: mean={EPS[y]:.2f}, ±σ={SIGMA[y]:.2f}, range=[{low:.2f}, {high:.2f}]")
    return rows


def validate_heatmap_core_row() -> list[str]:
    # Chart states row PE 24x and EPS 16.1..21.0 gives: 387,420,438,454,473,504
    eps_axis = [16.1, 17.5, 18.3, 18.9, 19.7, 21.0]
    observed = [387, 420, 438, 454, 473, 504]
    rows = []
    for e, obs in zip(eps_axis, observed):
        calc = round(price(24, e))
        rows.append(f"PE24 x EPS {e:.1f} => calc={calc}, chart={obs}, diff={calc-obs:+d}")
    return rows


def validate_key_targets() -> list[str]:
    target_511 = round(price(27, EPS["2026E"]))
    target_591 = round(price(30, EPS["2026E"]))
    target_387 = round(price(24, 16.1))
    return [
        f"PE27 x EPS18.26 => {target_511} (chart final reported: {CROSS_VAL['Final Reported']})",
        f"PE30 x EPS19.70 => {round(price(30, 19.7))} (chart final PE30: {CROSS_VAL['Final Reported PE30']})",
        f"PE24 x EPS16.10 => {target_387} (chart final core: {CROSS_VAL['Final Core']})",
        f"MC Mean check: PE27 x EPS18.26 = {target_511}, MC mean shown {CROSS_VAL['MC Mean']} (difference {target_511 - CROSS_VAL['MC Mean']:+d})",
    ]


def validate_percent_labels() -> list[str]:
    labels = {
        "Original": +1.4,
        "Corrected": -12.4,
        "Final Core": -22.6,
        "Final Reported": +2.1,
        "Final Reported PE30": +18.2,
        "MC Mean": -1.4,
    }
    rows = []
    for k, shown in labels.items():
        calc = round(pct(CROSS_VAL[k]), 1)
        rows.append(f"{k}: calc {calc:+.1f}% vs chart {shown:+.1f}%")
    return rows


def main() -> None:
    print("=== EPS bars (mean ± sigma) ===")
    print("\n".join(validate_eps_bars()))

    print("\n=== Heatmap PE24 row arithmetic ===")
    print("\n".join(validate_heatmap_core_row()))

    print("\n=== Key target checks ===")
    print("\n".join(validate_key_targets()))

    print("\n=== % label checks vs 500 HKD baseline ===")
    print("\n".join(validate_percent_labels()))


if __name__ == "__main__":
    main()
