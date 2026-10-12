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
    rich = data["expected_tp"]
    fair = data["reasonable"]["target"]
    sc = data["scenarios"]
    mc = data["mc2"]
    coe = data["wacc"]["base"]["coe"]
    dps = data["fact"]["dps"]
    pw_roll = data["reasonable"]["model_prob_pw"]
    rows = sorted([
        ("Tail, 정합배수", data["reasonable"]["roll12m"]["Tail"], "#7A1F1F"),
        ("Bear, 정합배수", data["reasonable"]["roll12m"]["Bear"], "#B45309"),
        ("확률가중 DCF 12개월", pw_roll, "#64748B"),
        ("합리적인 목표", fair, "#0F2043"),
        ("Base, 정합배수", data["reasonable"]["roll12m"]["Base"], "#1D4E89"),
        ("Hold 하우스 평균", sum(data["cons"]["hold_tps"]) / 2, "#94A3B8"),
        ("종가를 자본비용으로 굴림", data["reasonable"]["price_rolled_at_coe"], "#94A3B8"),
        ("Bull, 정합배수", data["reasonable"]["roll12m"]["Bull"], "#166534"),
        ("셀사이드 평균", data["cons"]["tp_mean"], "#B8943A"),
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
        ax.text(val + 8, i, f"\\${val:.0f}", va="center", ha="left", fontsize=9, color="#111827", fontproperties=prop)
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
    for x, label, color, style in (
        (price, "종가", "#111827", "--"),
        (fair, "합리적인 목표", "#B8943A", "-"),
        (mc["p50"], "배수법 중앙값", "#0F766E", "--"),
    ):
        ax2.axvline(x, color=color, lw=1.2, ls=style, zorder=3)
    ax2.set_xlim(50, 900)
    ax2.set_xlabel("12개월 주가 시뮬레이션", fontproperties=prop, fontsize=10)
    ax2.set_ylabel("표본 수", fontproperties=prop, fontsize=10)
    ax2.set_title(f"Monte Carlo v2  n={mc['n']:,}  seed={mc['seed']}", fontproperties=prop, fontsize=13, loc="left", color="#0F2043")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.grid(axis="y", color="#E5E1D8", zorder=0)
    note = (
        f"p5 \\${mc['p5']:.0f}   p50 \\${mc['p50']:.0f}   p95 \\${mc['p95']:.0f}\n"
        f"P(종가 상회) {mc['p_above_price']:.0%}    P(<300달러) {mc['p_below_300']:.0%}"
    )
    ax2.legend(
        [plt.Line2D([0], [0], color="#111827", lw=1.2, ls="--"),
         plt.Line2D([0], [0], color="#B8943A", lw=1.4),
         plt.Line2D([0], [0], color="#0F766E", lw=1.2, ls="--")],
        [f"종가 \\${price:.0f}", f"합리적인 목표 \\${fair:.0f}", f"배수법 중앙값 \\${mc['p50']:.0f}"],
        prop=prop, frameon=False, loc="upper right", fontsize=8,
    )
    ax2.text(0.98, 0.04, note, transform=ax2.transAxes, ha="right", va="bottom", fontsize=9,
             fontproperties=prop, color="#1F2937",
             bbox=dict(boxstyle="round,pad=0.35", fc="#FFFFFF", ec="#E5E1D8"))

    fig.suptitle(f"Broadcom (AVGO)  합리적인 12개월 목표주가  \\${fair:.0f}   ({fair / price - 1:+.0%})",
                 fontproperties=prop, fontsize=16, color="#0F2043", x=0.02, ha="left")
    fig.text(0.02, 0.012,
             f"기준일 2026-10-09.  왼쪽 점선 = 종가 {price:.2f}달러.  목표가는 할인율과 맞는 12개월 가치.  배수법 기대값 {rich:.0f}달러는 종가를 자본비용으로 굴린 값과 같다.",
             fontproperties=prop, fontsize=8, color="#4B5563")
    fig.tight_layout(rect=(0, 0.04, 1, 0.93))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=140)
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
