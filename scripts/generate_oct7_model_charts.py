#!/usr/bin/env python3
"""정밀 모델 차트."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager

import oct7_model as M

OUT = Path("/workspace/output/oct7/charts")
OUT.mkdir(parents=True, exist_ok=True)
REP = Path("/workspace/reports/charts")
REP.mkdir(parents=True, exist_ok=True)

NAVY, NAVY2, GOLD, GREEN, RED, GRAY, LINE, BG = (
    "#0f2043", "#1e407c", "#b8943a", "#166534", "#991b1b", "#4b5563", "#d5dce6", "#f4f6fb",
)

_font = "DejaVu Sans"
for path in (
    "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
):
    if Path(path).exists():
        font_manager.fontManager.addfont(path)
        _font = font_manager.FontProperties(fname=path).get_name()
        break


def style():
    plt.rcParams.update({
        "font.family": _font,
        "axes.unicode_minus": False,
        "figure.facecolor": BG,
        "axes.facecolor": "white",
        "axes.edgecolor": LINE,
        "text.color": NAVY,
        "axes.labelcolor": NAVY,
        "xtick.color": GRAY,
        "ytick.color": GRAY,
    })


def save(fig, name: str):
    fig.tight_layout()
    for d in (OUT, REP):
        fig.savefig(d / name, dpi=160)
    plt.close(fig)


def chart_cpu_paths(cpu: dict):
    style()
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    years = np.array([2025, 2026, 2027, 2028, 2030])
    colors = {"Citi May": "#94a3b8", "Citi Oct": NAVY2, "Mizuho": GOLD}
    for p in cpu["paths"]:
        ys = [p["y2025"], p["y2026_implied"], p["y2027_implied"], p["y2028_implied"], p["y2030"]]
        ax.plot(years, ys, "o-", color=colors[p["name"]], lw=2.4, label=f"{p['name']} ({p['cagr_pct']})")
    ax.set_title("서버 CPU TAM 경로 (2026~28 = CAGR 역산)")
    ax.set_ylabel("$B")
    ax.grid(axis="y", color=LINE)
    ax.legend(frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "10_cpu_tam_paths.png")


def chart_muse_heatmap(grid: list[dict]):
    style()
    # DAU=100 only, rows=intensity, cols=active
    intens = ["현재실측", "고도화", "복잡Agent"]
    acts = [0.05, 0.15, 0.30]
    mat = np.zeros((len(intens), len(acts)))
    for r in grid:
        if r["dau_m"] != 100:
            continue
        i = intens.index(r["name"])
        j = acts.index(r["active_ratio"])
        mat[i, j] = r["physical_PB"]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    im = ax.imshow(mat, cmap="Blues")
    ax.set_xticks(range(3), ["활성5%", "활성15%", "활성30%"])
    ax.set_yticks(range(3), intens)
    ax.set_title("Muse DRAM Physical PB (DAU 1억)")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, f"{mat[i, j]:.0f}", ha="center", va="center", color="black", fontsize=11)
    fig.colorbar(im, ax=ax, fraction=0.046, label="PB")
    save(fig, "11_muse_dram_heatmap.png")


def chart_val_reeval(val: dict):
    style()
    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    labels = ["현재", "31%할인\n유지", "15%할인", "MU패리티\n5.8x"]
    skh = [
        178.4,
        val["reevaluation_27y"]["skh"]["at_31pct_discount"],
        val["reevaluation_27y"]["skh"]["at_15pct_discount"],
        val["reevaluation_27y"]["skh"]["at_mu_parity_5.8x"],
    ]
    sec = [
        27.3,
        val["reevaluation_27y"]["sec"]["at_31pct_discount"],
        val["reevaluation_27y"]["sec"]["at_15pct_discount"],
        val["reevaluation_27y"]["sec"]["at_mu_parity_5.8x"],
    ]
    x = np.arange(len(labels))
    ax.bar(x - 0.18, skh, 0.36, color=NAVY2, label="SK하이닉스 (만)")
    ax.bar(x + 0.18, [s * 5 for s in sec], 0.36, color=GOLD, label="삼성×5 (만, 스케일)")
    for i, (a, b) in enumerate(zip(skh, sec)):
        ax.text(i - 0.18, a + 4, f"{a:.0f}", ha="center", fontsize=9)
        ax.text(i + 0.18, b * 5 + 4, f"{b:.1f}", ha="center", fontsize=9, color=GOLD)
    ax.set_xticks(x, labels)
    ax.set_title("27Y 재평가 맵 (EPS 인정 시 PER 시나리오)")
    ax.set_ylabel("만원")
    ax.legend(frameon=False)
    ax.grid(axis="y", color=LINE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "12_val_reeval.png")


def chart_capex(capex: dict):
    style()
    fig, ax = plt.subplots(figsize=(8.2, 4.2))
    names = [s["name"] for s in capex["scenarios"]]
    spend = [s["enterprise_ai_spend_multiple"] for s in capex["scenarios"]]
    infra = [s["infra_compute_proxy_multiple"] for s in capex["scenarios"]]
    x = np.arange(len(names))
    ax.bar(x - 0.18, spend, 0.36, color=RED, label="기업 $지출")
    ax.bar(x + 0.18, infra, 0.36, color=GREEN, label="인프라 compute")
    ax.axhline(1.0, color=GRAY, ls="--", lw=1)
    ax.set_xticks(x, names, rotation=15)
    ax.set_title("CapEx 역설: 지출 vs 인프라 (t0=1)")
    ax.legend(frameon=False)
    ax.grid(axis="y", color=LINE)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    save(fig, "13_capex_paradox.png")


def main():
    m = M.run_model()
    chart_cpu_paths(m["cpu"])
    chart_muse_heatmap(m["muse"]["grid"])
    chart_val_reeval(m["valuation"])
    chart_capex(m["capex"])
    print("charts:", sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
