#!/usr/bin/env python3
"""Recompute 2x2 odds ratios from published counts. Do not invent patients."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import chi2_contingency, fisher_exact, norm

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)


def or_ci(a: int, b: int, c: int, d: int, alpha: float = 0.05) -> tuple[float, float, float]:
    odds = (a * d) / (b * c)
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    z = norm.ppf(1 - alpha / 2)
    lo = math.exp(math.log(odds) - z * se)
    hi = math.exp(math.log(odds) + z * se)
    return odds, lo, hi


def analyze(name: str, table: list[list[int]]) -> dict:
    a, b = table[0]
    c, d = table[1]
    odds, lo, hi = or_ci(a, b, c, d)
    _, p_chi, _, _ = chi2_contingency(table, correction=False)
    _, p_f = fisher_exact(table)
    return {
        "name": name,
        "table": table,
        "OR": round(odds, 3),
        "CI95": [round(lo, 3), round(hi, 3)],
        "p_chi2": p_chi,
        "p_fisher": p_f,
        "significant": bool(p_f < 0.05 or p_chi < 0.05),
    }


def main() -> None:
    results = [
        analyze("STEMI", [[37, 7], [30, 33]]),
        analyze("Male sex", [[57, 26], [10, 14]]),
        analyze("Shockable", [[54, 27], [13, 13]]),
        analyze("Hypertension", [[32, 16], [35, 24]]),
        analyze("Diabetes", [[13, 9], [54, 31]]),
        analyze("Prior CAD", [[9, 6], [58, 34]]),
        analyze("cTnI>URL", [[58, 31], [9, 9]]),
    ]
    (ROOT / "verified_2x2.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    for r in results:
        lo, hi = r["CI95"]
        print(
            "{} OR {:.3f} ({:.3f}-{:.3f}) chi2 p={:.4g} Fisher p={:.4g}".format(
                r["name"].ljust(14), r["OR"], lo, hi, r["p_chi2"], r["p_fisher"]
            )
        )
    _figures(results[:6])


def _style() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.linewidth": 0.8,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "font.size": 10,
        }
    )


def _figures(or_rows: list[dict]) -> None:
    _style()
    blue, red, green, amber, gray = "#3b82f6", "#dc2626", "#059669", "#d97706", "#64748b"

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    labels = ["First\ncTnI", "Second\ncTnI", "cTnI Δ", "CK-MB Δ", "Age"]
    all_auc = [0.572, 0.631, 0.530, 0.737, 0.637]
    ns_auc = [0.548, 0.478, 0.524, 0.552, 0.693]
    x = np.arange(len(labels))
    w = 0.36
    b1 = ax.bar(x - w / 2, all_auc, w, color=blue, label="All CAG (N=107)")
    b2 = ax.bar(x + w / 2, ns_auc, w, color=red, label="Non-STEMI (N=63)")
    ax.axhline(0.5, color=gray, ls="--", lw=1)
    ax.set_ylim(0.40, 0.82)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("AUC")
    ax.set_title("Serial CK-MB discriminates in the whole cohort, then collapses without STEMI")
    ax.legend(frameon=False, loc="upper left")
    for bars, vals, sigs in (
        (b1, all_auc, [False, True, False, True, True]),
        (b2, ns_auc, [False, False, False, False, True]),
    ):
        for bar, v, s in zip(bars, vals, sigs):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                v + 0.012,
                "{:.3f}{}".format(v, "*" if s else ""),
                ha="center",
                va="bottom",
                fontsize=8,
                color=green if s else gray,
            )
    fig.tight_layout()
    fig.savefig(FIG / "fig1_auc_all_vs_nonstemi.png", dpi=200)
    plt.close()

    fig, ax = plt.subplots(figsize=(8.2, 4.4))
    labels = ["CK-MB Δ\nalone", "+ Age", "+ Sex", "+ Shockable"]
    all_m = [0.737, 0.829, 0.838, 0.849]
    ns_m = [0.552, 0.766, 0.808, 0.832]
    x = np.arange(len(labels))
    w = 0.36
    b1 = ax.bar(x - w / 2, all_m, w, color=blue, label="All CAG (N=107)")
    b2 = ax.bar(x + w / 2, ns_m, w, color=green, label="Non-STEMI (N=63)")
    ax.set_ylim(0.45, 0.95)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("AUC")
    ax.set_title("Multivariable model restores Non-STEMI discrimination (AUC 0.832)")
    ax.legend(frameon=False)
    for bars, vals in ((b1, all_m), (b2, ns_m)):
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.012, "{:.3f}".format(v), ha="center", fontsize=8)
    fig.tight_layout()
    fig.savefig(FIG / "fig2_multivariable_auc.png", dpi=200)
    plt.close()

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    names = [r["name"] for r in or_rows]
    ors = [r["OR"] for r in or_rows]
    los = [r["CI95"][0] for r in or_rows]
    his = [r["CI95"][1] for r in or_rows]
    ps = [r["p_fisher"] for r in or_rows]
    y = np.arange(len(names))[::-1]
    ax.axvline(1, color=gray, ls="--", lw=1)
    for yi, o, lo, hi, p in zip(y, ors, los, his, ps):
        c = green if p < 0.05 else gray
        ax.plot([lo, hi], [yi, yi], color=c, lw=2)
        ax.plot(o, yi, "o", color=c, ms=8)
        star = " *" if p < 0.05 else ""
        ax.text(max(hi, 1) + 0.25, yi, "OR {:.2f}  p={:.3f}{}".format(o, p, star), va="center", fontsize=8, color=c)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel("Odds ratio for culprit lesion (log scale)")
    ax.set_xscale("log")
    ax.set_xlim(0.3, 16)
    ax.set_title("Categorical predictors of CAG culprit (N=107)")
    fig.tight_layout()
    fig.savefig(FIG / "fig3_or_forest.png", dpi=200)
    plt.close()

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    xs = np.array([1, 2])
    ami, non = [5.6, 70.0], [2.9, 3.3]
    ax.plot(xs, ami, "-o", color=red, lw=2.2, ms=9, label="Culprit present, median")
    ax.plot(xs, non, "-o", color=blue, lw=2.2, ms=9, label="No culprit, median")
    ax.set_xticks(xs)
    ax.set_xticklabels(["1st CK-MB\n(ED arrival)", "2nd CK-MB"])
    ax.set_ylabel("CK-MB (ng/mL)")
    ax.set_title("Second CK-MB separates groups: 70.0 vs 3.3 ng/mL")
    ax.legend(frameon=False, loc="upper left")
    ax.set_ylim(-2, 85)
    fig.tight_layout()
    fig.savefig(FIG / "fig4_ckmb_serial_medians.png", dpi=200)
    plt.close()

    fig, ax = plt.subplots(figsize=(7.4, 4.4))
    cuts = [50, 55, 59, 60, 65, 70]
    ax.plot(cuts, [90.0, 86.7, 83.3, 80.0, 56.7, 40.0], "-o", color=blue, lw=2, label="Sensitivity")
    ax.plot(cuts, [30.3, 45.5, 54.5, 57.6, 66.7, 78.8], "-o", color=amber, lw=2, label="Specificity")
    ax.axvline(59, color=green, ls="--", lw=1.2, label="Youden >=59 y")
    ax.set_xlabel("Age cutoff (years)")
    ax.set_ylabel("%")
    ax.set_ylim(0, 100)
    ax.set_title("Non-STEMI (N=63): age AUC 0.693, p=0.009")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "fig5_age_cutoff_nonstemi.png", dpi=200)
    plt.close()


if __name__ == "__main__":
    main()
