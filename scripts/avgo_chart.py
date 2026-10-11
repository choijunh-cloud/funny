#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""avgo_model_output.json → 12개월 가치 차트."""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "avgo_model_output.json"
OUT = Path("/opt/cursor/artifacts/avgo_target.png")
FONT = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"


def main() -> None:
    import json

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    font_manager.fontManager.addfont(FONT)
    prop = font_manager.FontProperties(fname=FONT)
    plt.rcParams["axes.unicode_minus"] = False

    price = data["price"]
    target = data["expected_tp"]
    sc = data["scenarios"]
    mc = data["mc2"]
    coe = data["wacc"]["base"]["coe"]
    dps = data["fact"]["dps"]
    pw_roll = data.get("verification", {}).get("pw_dcf_roll_12m")
    if pw_roll is None:
        pw_roll = sum(sc[k]["p"] * (data["scen_dcf"][k] * (1 + coe) - dps) for k in sc)
    rows = sorted([
        ("Tail 9x", sc["Tail"]["tp"], "#7A1F1F"),
        ("Bear 12x", sc["Bear"]["tp"], "#B45309"),
        ("DCF 확률가중, 12개월 롤", pw_roll, "#64748B"),
        ("DCF Base, 12개월 롤", data["dcf"]["roll12m"]["base"], "#64748B"),
        ("Hold 하우스 평균", sum(data["cons"]["hold_tps"]) / 2, "#94A3B8"),
        ("SOTP FY27", data["sotp"]["now"]["value_ps"], "#1E407C"),
        ("확률가중 목표가", target, "#0F2043"),
        ("MC v2 중앙값", mc["p50"], "#1E407C"),
        ("Base 16x", sc["Base"]["tp"], "#1D4E89"),
        ("UBS형 EV/FCF", data["sotp"]["ubs"]["ps"], "#0F766E"),
        ("SOTP FY28", data["sotp"]["fwd"]["value_ps"], "#0F766E"),
        ("셀사이드 평균", data["cons"]["tp_mean"], "#B8943A"),
        ("Bull 19x", sc["Bull"]["tp"], "#166534"),
    ], key=lambda r: r[1])

    fig, axes = plt.subplots(1, 2, figsize=(12.4, 6.6), gridspec_kw={"width_ratios": [1.15, 1]})
    fig.patch.set_facecolor("#F7F5F0")
    ax = axes[0]
    ax.set_facecolor("#F7F5F0")
    y = list(range(len(rows)))
    vals = [r[1] for r in rows]
    colors = [r[2] for r in rows]
    ax.barh(y, vals, color=colors, height=0.72, zorder=2)
    ax.axvline(price, color="#111827", lw=1.1, ls="--", zorder=3)
    for i, (label, val, _) in enumerate(rows):
        ax.text(val + 8, i, f"${val:.0f}", va="center", ha="left", fontsize=9, color="#111827", fontproperties=prop)
    ax.set_yticks(y)
    ax.set_yticklabels([r[0] for r in rows], fontproperties=prop, fontsize=10)
    ax.set_xlim(0, 820)
    ax.set_xlabel("달러 / 주", fontproperties=prop, fontsize=10)
    ax.set_title("12개월 가치 비교", fontproperties=prop, fontsize=13, loc="left", color="#0F2043")
    ax.tick_params(axis="x", labelsize=9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", color="#E5E1D8", zorder=0)

    ax2 = axes[1]
    ax2.set_facecolor("#F7F5F0")
    edges = mc["hist_edges"]
    hist = mc["hist"]
    widths = [edges[i + 1] - edges[i] for i in range(len(hist))]
    ax2.bar(edges[:-1], hist, width=widths, align="edge", color="#1E407C", alpha=0.85, zorder=2)
    for x, label, color in (
        (price, "종가", "#111827"),
        (target, "목표가", "#B8943A"),
        (mc["p50"], "중앙값", "#0F766E"),
    ):
        ax2.axvline(x, color=color, lw=1.2, ls="--" if label != "목표가" else "-", zorder=3)
    ax2.set_xlim(50, 900)
    ax2.set_xlabel("12개월 주가 시뮬레이션", fontproperties=prop, fontsize=10)
    ax2.set_ylabel("표본 수", fontproperties=prop, fontsize=10)
    ax2.set_title(f"Monte Carlo v2  n={mc['n']:,}  seed={mc['seed']}", fontproperties=prop, fontsize=13, loc="left", color="#0F2043")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", color="#E5E1D8", zorder=0)
    note = (
        f"p5 ${mc['p5']:.0f}   p50 ${mc['p50']:.0f}   p95 ${mc['p95']:.0f}\n"
        f"P(종가 상회) {mc['p_above_price']:.0%}    P(<$300) {mc['p_below_300']:.0%}"
    )
    ax2.legend(
        [plt.Line2D([0], [0], color="#111827", lw=1.2, ls="--"),
         plt.Line2D([0], [0], color="#B8943A", lw=1.4),
         plt.Line2D([0], [0], color="#0F766E", lw=1.2, ls="--")],
        [f"종가 ${price:.0f}", f"목표가 ${target:.0f}", f"중앙값 ${mc['p50']:.0f}"],
        prop=prop, frameon=False, loc="upper right", fontsize=8,
    )
    ax2.text(0.98, 0.04, note, transform=ax2.transAxes, ha="right", va="bottom", fontsize=9,
             fontproperties=prop, color="#1F2937",
             bbox=dict(boxstyle="round,pad=0.35", fc="#FFFFFF", ec="#E5E1D8"))

    fig.suptitle(f"Broadcom (AVGO)  12개월 목표가  ${target:.0f}   ({target / price - 1:+.0%})",
                 fontproperties=prop, fontsize=16, color="#0F2043", x=0.02, ha="left")
    fig.text(0.02, 0.012,
             f"기준일 2026-10-09.  왼쪽 점선 = 종가 ${price:.2f}.  목표가 = Tail/Bear/Base/Bull의 FY28 EPS × 9/12/16/19x, 확률 10/25/42/23%.",
             fontproperties=prop, fontsize=8, color="#4B5563")
    fig.tight_layout(rect=(0, 0.04, 1, 0.93))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
