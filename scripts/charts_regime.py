"""Static charts for the panel synthesis regime baseline."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Mapping

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.patches import FancyBboxPatch

from panel_regime_model import ASSET_KEYS, ASSET_LABELS_KO, FACTOR_LABELS_KO, HORIZONS

FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
)
for _path in FONT_CANDIDATES:
    if Path(_path).exists():
        font_manager.fontManager.addfont(_path)
        plt.rcParams["font.family"] = font_manager.FontProperties(fname=_path).get_name()
        break

plt.rcParams.update(
    {
        "axes.unicode_minus": False,
        "figure.facecolor": "#F4F6FA",
        "axes.facecolor": "#FFFFFF",
        "axes.edgecolor": "#D5DCE6",
        "axes.labelcolor": "#1A1A1A",
        "xtick.color": "#4B5563",
        "ytick.color": "#4B5563",
        "text.color": "#1A1A1A",
        "axes.titleweight": "bold",
        "axes.titlesize": 13,
        "axes.labelsize": 10,
        "font.size": 10,
    }
)

NAVY = "#0F2043"
GOLD = "#B8943A"
REGIME_COLORS = {
    "A": "#16A34A",
    "B": "#2563EB",
    "B*": "#7C3AED",
    "C": "#D97706",
    "D": "#DC2626",
}
HORIZON_COLORS = {"3M": "#0F2043", "6M": "#1E407C", "12M": "#B8943A"}
ASSET_COLORS = {
    "Semiconductor": "#0284C7",
    "AI_Compute": "#7C3AED",
    "Power_Grid": "#D97706",
    "Non_Semi_Export": "#059669",
    "Cash": "#64748B",
}


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def chart_state_space(snapshot: Mapping[str, Any], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 6.4))
    ax.axhline(0, color="#CBD5E1", lw=1)
    ax.axvline(0, color="#CBD5E1", lw=1)
    ax.set_xlim(-0.55, 0.92)
    ax.set_ylim(-0.85, 0.52)
    ax.set_xlabel("실물 축 P  (강함 →)")
    ax.set_ylabel("금융 축 F  (여유 →)")
    ax.set_title("이축 상태공간 — 국면 중심점과 베이스라인 궤적")

    for code, meta in snapshot["regimes"].items():
        ax.scatter(
            meta["p_coord"],
            meta["f_coord"],
            s=220,
            c=REGIME_COLORS[code],
            zorder=3,
            edgecolors="white",
            linewidths=1.2,
        )
        ax.annotate(
            code,
            (meta["p_coord"], meta["f_coord"]),
            textcoords="offset points",
            xytext=(8, 7),
            fontsize=11,
            fontweight="bold",
            color=REGIME_COLORS[code],
        )

    xs, ys = [], []
    for horizon in HORIZONS:
        row = snapshot["horizons"][horizon]
        xs.append(row["p"])
        ys.append(row["f"])
        ax.scatter(
            row["p"],
            row["f"],
            s=90,
            c=HORIZON_COLORS[horizon],
            marker="D",
            zorder=4,
            edgecolors="white",
        )
        ax.annotate(
            horizon,
            (row["p"], row["f"]),
            textcoords="offset points",
            xytext=(8, -12),
            fontsize=10,
            fontweight="bold",
            color=HORIZON_COLORS[horizon],
        )
    ax.plot(xs, ys, color=GOLD, lw=2.2, zorder=2)
    ax.annotate(
        "",
        xy=(xs[-1], ys[-1]),
        xytext=(xs[-2], ys[-2]),
        arrowprops=dict(arrowstyle="->", color=GOLD, lw=2.0),
    )
    ax.text(
        0.02,
        0.97,
        "실물 강 · 금융 여유 → A\n실물 강 · 금융 경색 → B*\n원점 근처 → C / B",
        transform=ax.transAxes,
        va="top",
        fontsize=8.5,
        color="#4B5563",
        bbox=dict(boxstyle="round,pad=0.35", facecolor="#F8FAFC", edgecolor="#E2E8F0"),
    )
    _save(fig, path)


def chart_regime_probs(snapshot: Mapping[str, Any], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    codes = list(snapshot["regimes"])
    x = range(len(codes))
    width = 0.24
    for i, horizon in enumerate(HORIZONS):
        vals = [snapshot["horizons"][horizon]["disp"][code] for code in codes]
        ax.bar(
            [p + (i - 1) * width for p in x],
            vals,
            width=width,
            color=HORIZON_COLORS[horizon],
            label=horizon,
        )
        for pos, val in zip([p + (i - 1) * width for p in x], vals):
            ax.text(pos, val + 0.6, f"{val}", ha="center", va="bottom", fontsize=8, color=NAVY)
    ax.set_xticks(list(x))
    ax.set_xticklabels([f"{c}\n{snapshot['regimes'][c]['name'].split('(')[0].strip()[3:]}" for c in codes])
    ax.set_ylim(0, 42)
    ax.set_ylabel("확률 (%)")
    ax.set_title("국면 확률 — 시계가 길수록 B → C 로 이동")
    ax.legend(frameon=False, ncol=3, loc="upper right")
    _save(fig, path)


def chart_allocation(snapshot: Mapping[str, Any], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.0))
    y = range(len(HORIZONS))
    left = [0.0] * len(HORIZONS)
    for asset in ASSET_KEYS:
        widths = [snapshot["horizons"][h]["alloc"][asset] * 100.0 for h in HORIZONS]
        bars = ax.barh(
            list(y),
            widths,
            left=left,
            color=ASSET_COLORS[asset],
            label=ASSET_LABELS_KO[asset],
            height=0.62,
        )
        for bar, width, start in zip(bars, widths, left):
            if width >= 8:
                ax.text(
                    start + width / 2,
                    bar.get_y() + bar.get_height() / 2,
                    f"{width:.1f}",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=8.5,
                    fontweight="bold",
                )
        left = [s + w for s, w in zip(left, widths)]
    ax.set_yticks(list(y))
    ax.set_yticklabels(HORIZONS)
    ax.set_xlim(0, 100)
    ax.set_xlabel("배분 (%)")
    ax.set_title("정책 배분 — 반도체 우세가 줄고 현금이 늘어남")
    ax.legend(ncol=5, frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    fig.subplots_adjust(bottom=0.22)
    _save(fig, path)


def chart_kospi_fan(snapshot: Mapping[str, Any], path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    spot = snapshot["execution"]["kospi"]
    for i, horizon in enumerate(HORIZONS):
        proj = snapshot["horizons"][horizon]["proj"]
        ax.plot([i, i], [proj["p10"], proj["p90"]], color=HORIZON_COLORS[horizon], lw=8, alpha=0.22, solid_capstyle="round")
        ax.plot([i, i], [proj["p10"], proj["p90"]], color=HORIZON_COLORS[horizon], lw=2.4)
        ax.scatter([i], [proj["p50"]], s=70, c=HORIZON_COLORS[horizon], zorder=4)
        ax.scatter([i], [proj["expected_level"]], s=55, marker="D", c=GOLD, zorder=5, edgecolors=NAVY, linewidths=0.6)
        ax.text(i + 0.08, proj["p90"] + 60, f"P90 {proj['p90']:.0f}", fontsize=8, color=HORIZON_COLORS[horizon])
        ax.text(i + 0.08, proj["p10"] - 140, f"P10 {proj['p10']:.0f}", fontsize=8, color=HORIZON_COLORS[horizon])
        ax.text(i + 0.08, proj["p50"] + 70, f"P50 {proj['p50']:.0f}", fontsize=8, color=NAVY)
    ax.axhline(spot, color="#DC2626", ls="--", lw=1.2, label=f"현 코스피 {spot:,.0f}")
    ax.set_xticks(range(len(HORIZONS)))
    ax.set_xticklabels(HORIZONS)
    ax.set_ylabel("코스피 (pt)")
    ax.set_title("코스피 혼합 분위수 — 막대는 P10~P90, 원=P50, 마름모=평균")
    ax.set_ylim(5000, 9600)
    ax.legend(frameon=False, loc="upper right")
    _save(fig, path)


def chart_factor_heatmap(snapshot: Mapping[str, Any], path: Path) -> None:
    physical_keys = list(snapshot["horizons"]["3M"]["physical"])
    financial_keys = list(snapshot["horizons"]["3M"]["financial"])
    keys = physical_keys + financial_keys
    matrix = [[snapshot["horizons"][h]["physical" if k in physical_keys else "financial"][k] for h in HORIZONS] for k in keys]
    fig, ax = plt.subplots(figsize=(7.6, 5.8))
    image = ax.imshow(matrix, cmap="RdBu", vmin=-1, vmax=1, aspect="auto")
    ax.set_xticks(range(len(HORIZONS)))
    ax.set_xticklabels(HORIZONS)
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels([FACTOR_LABELS_KO[k] for k in keys])
    ax.set_title("팩터 스냅샷 — 실물 모멘텀은 줄고 금융은 부분 회복")
    for i, row in enumerate(matrix):
        for j, val in enumerate(row):
            ax.text(j, i, f"{val:+.2f}", ha="center", va="center", fontsize=9, color="#111827")
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="점수 [-1, +1]")
    ax.axhline(4.5, color=NAVY, lw=1.1)
    _save(fig, path)


def chart_execution(snapshot: Mapping[str, Any], path: Path) -> None:
    exe = snapshot["execution"]
    fig, axes = plt.subplots(1, 4, figsize=(10.6, 3.6))
    cards = [
        ("현물 프리미엄", exe["spread"], 25.0, "+18.5% 양호", "#166534", "#E8F5E9"),
        ("고점 대비 낙폭", exe["drawdown"] * 100, -40.0, "-26.8% 감시", "#7A5C12", "#FFF8E7"),
        ("선행 PER", exe["forward_pe"], exe["valuation_ceiling"], f"{exe['forward_pe']:.1f} / {exe['valuation_ceiling']:.1f}", "#1E407C", "#E8F1FB"),
        ("스트레스 클러스터", float(len(exe["clusters"])), 4.0, f"{len(exe['clusters'])} / 4", "#166534", "#E8F5E9"),
    ]
    for ax, (title, value, ref, caption, color, fill) in zip(axes, cards):
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")
        box = FancyBboxPatch((0.04, 0.08), 0.92, 0.84, boxstyle="round,pad=0.03,rounding_size=0.08", facecolor=fill, edgecolor="#D5DCE6")
        ax.add_patch(box)
        ax.text(0.5, 0.78, title, ha="center", fontsize=10, color="#4B5563")
        if title == "선행 PER":
            shown = f"{value:.1f}x"
        elif title == "스트레스 클러스터":
            shown = f"{int(value)}"
        else:
            shown = f"{value:+.1f}%"
        ax.text(0.5, 0.46, shown, ha="center", fontsize=20, fontweight="bold", color=color)
        ax.text(0.5, 0.22, caption, ha="center", fontsize=8.5, color="#4B5563")
    fig.suptitle("실행 트리거 — 스트레스 0개, 등급 NORMAL", fontsize=13, fontweight="bold", color=NAVY, y=1.02)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def render_all(snapshot: Mapping[str, Any], out_dir: Path) -> Dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "state_space": out_dir / "state_space.png",
        "regime_probs": out_dir / "regime_probs.png",
        "allocation": out_dir / "allocation.png",
        "kospi_fan": out_dir / "kospi_fan.png",
        "factor_heatmap": out_dir / "factor_heatmap.png",
        "execution": out_dir / "execution.png",
    }
    chart_state_space(snapshot, paths["state_space"])
    chart_regime_probs(snapshot, paths["regime_probs"])
    chart_allocation(snapshot, paths["allocation"])
    chart_kospi_fan(snapshot, paths["kospi_fan"])
    chart_factor_heatmap(snapshot, paths["factor_heatmap"])
    chart_execution(snapshot, paths["execution"])
    return paths
