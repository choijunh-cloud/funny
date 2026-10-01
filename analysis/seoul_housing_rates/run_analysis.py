"""시나리오를 돌려 표, CSV, 차트를 만든다.

실행:
    python3 -m analysis.seoul_housing_rates.run_analysis
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

from analysis.seoul_housing_rates.model import (
    DistrictResult,
    backtest_2022,
    evaluate,
    rate_state,
    rate_that_exhausts_cap,
    sequential_contributions,
)
from analysis.seoul_housing_rates.parameters import (
    DISTRICTS,
    Assumptions,
    Scenario,
    assumption_band,
    eight_percent_scenario,
    scenario_for_hikes,
)

FONT = "WenQuanYi Micro Hei"
COLORS = {
    "강남구": "#0F2043",
    "서초구": "#1E407C",
    "송파구": "#4C6A9C",
    "용산구": "#B45309",
    "성동구": "#C2410C",
    "마포구": "#9A3412",
    "서울": "#6B7280",
}


def _font() -> None:
    path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    font_manager.fontManager.addfont(path)
    plt.rcParams["font.family"] = FONT
    plt.rcParams["axes.unicode_minus"] = False


def _pct(x: float) -> str:
    return f"{100 * x:+.1f}%"


def _lvl(x: float) -> str:
    return f"{100 * x:.1f}%"


def _pp(x: float) -> str:
    return f"{100 * x:.2f}%p"


def _rate(x: float) -> str:
    return f"{100 * x:.2f}%"


def _eok(won: float) -> str:
    return f"{won / 100_000_000:.2f}억"


def _man(won_per_year: float) -> str:
    return f"{won_per_year / 10_000:,.0f}만원"


def headline_scenarios(assumptions: Assumptions) -> list[Scenario]:
    shin = scenario_for_hikes(1)
    four = scenario_for_hikes(4)
    shock = eight_percent_scenario(assumptions)
    return [
        Scenario("hikes_1", "신현송 6개월 (추가 1회)", shin.hikes, shin.extra_term_premium, shin.g_decline, shin.income_growth),
        Scenario("hikes_4", "추가 4회, 스프레드 유지", four.hikes, four.extra_term_premium, four.g_decline, four.income_growth),
        shock,
    ]


def _rows(results: list[DistrictResult]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for r in results:
        old = next(v for v in r.vintages if v.name.startswith("2021"))
        recent = next(v for v in r.vintages if v.name.startswith("2025"))
        rows.append(
            {
                "band": r.band,
                "scenario": r.scenario,
                "district": r.district,
                "group": r.group,
                "price_eok": round(r.price / 1e8, 2),
                "jeonse_ratio": round(r.jeonse_ratio, 3),
                "gross_yield": round(r.gross_yield, 4),
                "base": round(r.rates_new.base, 4),
                "mortgage_avg": round(r.rates_new.mortgage_avg, 4),
                "mortgage_upper": round(r.rates_new.mortgage_upper, 4),
                "biz_rate": round(r.rates_new.biz, 4),
                "price_change": round(r.price_ratio - 1.0, 4),
                "cap_channel": round(r.cap_ratio - 1.0, 4),
                "listing_channel": round(r.listing_impact, 4),
                "income_channel": round(r.income_effect, 4),
                "jeonse_channel": round(r.jeonse_effect, 4),
                "listing_share_of_stock": round(r.listing_share, 4),
                "latent_distress": round(r.latent_distress, 4),
                "forward_distress": round(r.forward_distress, 4),
                "biz_share_used": round(r.share_used, 3),
                "old_dsr_origin": round(old.dsr_origin, 3),
                "old_dsr_now": round(old.dsr_now, 3),
                "old_dsr_new": round(old.dsr_new, 3),
                "recent_dsr_origin": round(recent.dsr_origin, 3),
                "recent_dsr_now": round(recent.dsr_now, 3),
                "recent_dsr_new": round(recent.dsr_new, 3),
                "recent_biz_eok": round(recent.biz / 1e8, 2),
                "recent_mortgage_eok": round(recent.mortgage / 1e8, 2),
                "regulated_payment_now_man": round(r.regulated_service_now / 1e4, 1),
                "regulated_payment_new_man": round(r.regulated_service_new / 1e4, 1),
                "new_buyer_binding": r.new_loan_binding,
                "new_buyer_loan_eok": round(r.new_loan / 1e8, 2),
            }
        )
    return rows


def render_report(results: list[DistrictResult], out_dir: Path) -> str:
    a = Assumptions()
    spot = rate_state(0, 0.0, a)
    four = rate_state(4, 0.0, a)
    shock = eight_percent_scenario(a)
    shock_rates = rate_state(shock.hikes, shock.extra_term_premium, a)
    central = [r for r in results if r.band == "central"]
    lines: list[str] = []
    lines.append("서울 강남3구·마용성 금리 충격 추정")
    lines.append("기준 시점: 2026년 10월 초. 가격 기준: 2026년 2분기 전용 84㎡ 실거래 평균.")
    lines.append("이 문서는 조건부 계산이다. 코호트 비중과 기대수익률 수정은 관측된 통계가 아니다.")
    lines.append("")
    lines.append("[금리 경로]")
    lines.append(
        f"지금 기준 {_rate(spot.base)}, 주담대 평균 {_rate(spot.mortgage_avg)} "
        f"(8월 4.66% + 파이프라인 0.20%p), 공시 상단 {_rate(spot.mortgage_upper)}, "
        f"사업자대출 {_rate(spot.biz)}."
    )
    lines.append(
        f"추가 4회: 기준 {_rate(four.base)}, 주담대 평균 {_rate(four.mortgage_avg)}, "
        f"공시 상단 {_rate(four.mortgage_upper)}, 사업자대출 {_rate(four.biz)}."
    )
    lines.append(
        f"평균 8% 경로: 4회에 기간프리미엄 {_pp(shock.extra_term_premium)}를 더한다. "
        f"공시 상단 {_rate(shock_rates.mortgage_upper)}, 사업자대출 {_rate(shock_rates.biz)}."
    )
    eight_hikes = rate_state(8, 0.0, a)
    lines.append(
        "4회만으로는 가중평균이 8%가 되지 않는다. 8%에 닿는 것은 우대 없는 공시 상단이다. "
        "평균까지 8%가 되려면 은행채 스프레드가 약 2.3%p 더 벌어져야 한다."
    )
    lines.append(
        f"인상 횟수를 8회로 늘려도 스프레드가 그대로면 기준 {_rate(eight_hikes.base)}, "
        f"평균 {_rate(eight_hikes.mortgage_avg)}, 상단 {_rate(eight_hikes.mortgage_upper)}다. "
        "8회와 평균 8%는 다른 경로다."
    )
    lines.append(f"2022년 캡레이트 재현: 가격 { _pct(backtest_2022()) } (수익률 2.3%, 주담대 +3.2%p, 기대 -2.5%p).")
    lines.append("")
    lines.append("[중앙 가정 가격 변화]")
    lines.append(
        "구 | 시나리오 | 합산 | 금리 | 기대수정 | 사업자 매물 | 소득 | 전세 | "
        "고점 DSR 당시→지금→이후 | 평균금리 대출 | 상단금리 대출"
    )
    order = ["hikes_1", "hikes_4", "mortgage_8"]
    labels = {
        "hikes_1": "추가1회",
        "hikes_4": "추가4회",
        "mortgage_8": "평균8%",
    }
    for district in DISTRICTS:
        for sid in order:
            r = next(x for x in central if x.district == district.name and x.scenario == sid)
            recent = next(v for v in r.vintages if v.name.startswith("2025"))
            rate_c, growth_c, listed, income, jeonse = (p[1] for p in sequential_contributions(r))
            lines.append(
                f"{r.district} | {labels[sid]} | {_pct(r.price_ratio - 1)} | "
                f"{_pct(rate_c)} | {_pct(growth_c)} | {_pct(listed)} | {_pct(income)} | {_pct(jeonse)} | "
                f"{_lvl(recent.dsr_origin)}→{_lvl(recent.dsr_now)}→{_lvl(recent.dsr_new)} | "
                f"{r.new_loan_binding} {_eok(r.new_loan)} | "
                f"{r.new_loan_upper_binding} {_eok(r.new_loan_at_upper)}"
            )
    lines.append("")
    lines.append("[가정 범위, 추가 4회]")
    lines.append("구 | 완화 | 중앙 | 심화")
    for district in DISTRICTS:
        cells = []
        for band in ("mild", "central", "severe"):
            r = next(
                x
                for x in results
                if x.district == district.name and x.scenario == "hikes_4" and x.band == band
            )
            cells.append(_pct(r.price_ratio - 1))
        lines.append(f"{district.name} | {cells[0]} | {cells[1]} | {cells[2]}")
    lines.append("")
    lines.append("[평균 8% 경로의 가정 범위]")
    lines.append("구 | 완화 | 중앙 | 심화")
    for district in DISTRICTS:
        cells = []
        for band in ("mild", "central", "severe"):
            r = next(
                x
                for x in results
                if x.district == district.name and x.scenario == "mortgage_8" and x.band == band
            )
            cells.append(_pct(r.price_ratio - 1))
        lines.append(f"{district.name} | {cells[0]} | {cells[1]} | {cells[2]}")
    lines.append("")
    lines.append("[현금흐름: 규제 주담대 평균 잔액 vs 고점 우회 코호트]")
    lines.append("규제 잔액은 2025년 R114 평균 약정액이고 사업자대출이 없다.")
    lines.append("우회 코호트는 매수가의 40% 주담대(절대액은 6억 한도)와 목표 LTV 55%를 메우는 사업자대출(최대 8억)이다.")
    four_r = [r for r in central if r.scenario == "hikes_4"]
    shock_r = [r for r in central if r.scenario == "mortgage_8"]
    for left, right in zip(four_r, shock_r):
        recent_now = next(v for v in left.vintages if v.name.startswith("2025"))
        recent_shock = next(v for v in right.vintages if v.name.startswith("2025"))
        lines.append(
            f"{left.district}: 규제잔액 {_eok(left.regulated_balance)} "
            f"연상환 {_man(left.regulated_service_now)} → 4회 {_man(left.regulated_service_new)} "
            f"/ 8%경로 {_man(right.regulated_service_new)}. "
            f"우회(주담대 {_eok(recent_now.mortgage)}+사업자 {_eok(recent_now.biz)}) "
            f"연상환 {_man(recent_now.service_now)} → 4회 {_man(recent_now.service_new)} "
            f"/ 8%경로 {_man(recent_shock.service_new)} "
            f"(소득 {_eok(left.income_future)})."
        )
    lines.append("")
    lines.append("[DSR이 금액한도를 깎기 시작하는 주담대 평균금리]")
    for district in DISTRICTS:
        income = district.income_2025 * (1 + a.income_level_up)
        cap = float(
            next(r for r in central if r.district == district.name and r.scenario == "hikes_4").new_loan_cap
        )
        breakeven = rate_that_exhausts_cap(cap, income * a.dsr_limit, 30)
        if breakeven is None:
            text = "연 20% 안에서는 금액한도가 먼저 걸린다"
        else:
            text = _lvl(breakeven)
        lines.append(f"{district.name}: 한도 {_eok(cap)}, 차주소득 {_eok(income)}, 한도가 풀리는 금리 {text}")
    lines.append("")
    lines.append("[이미 오른 금리의 미반영 스트레스와 추가 인상의 한계효과]")
    lines.append("매물 채널 = 코호트 비중 × (미반영 스트레스 + 추가 인상 스트레스) × 매도확률.")
    lines.append("미반영은 대출 당시(주담대 4.0%, 사업자 5.5%) 대비 현재 악화분 중 75%다.")
    lines.append("구 | 미반영 distress | 4회 추가 distress | 8% 추가 distress | 4회 매물비중 | 8% 매물비중")
    for district in DISTRICTS:
        one = next(x for x in central if x.district == district.name and x.scenario == "hikes_1")
        four_row = next(x for x in central if x.district == district.name and x.scenario == "hikes_4")
        eight_row = next(x for x in central if x.district == district.name and x.scenario == "mortgage_8")
        lines.append(
            f"{district.name} | {_lvl(one.latent_distress)} | {_lvl(four_row.forward_distress)} | "
            f"{_lvl(eight_row.forward_distress)} | {_lvl(four_row.listing_share)} | {_lvl(eight_row.listing_share)}"
        )
    lines.append("")
    lines.append("[읽기]")
    lines.append("강남·서초 국평은 주담대 한도가 2억이라, 규제 대출의 월 상환은 금리가 8%여도 소득 대비로 작다.")
    lines.append("가격이 움직이는 주된 이유는 임대수익률이 1%대라 요구수익률, 특히 기대상승률 수정에 민감해서다.")
    lines.append("추가 1회와 추가 4회의 차이만 인상 횟수의 한계효과다. 양쪽에 공통으로 깔린 하락에는 이미 오른 금리의 미반영분이 들어 있다.")
    lines.append("마포·성동·송파는 우회 코호트의 DSR이 높아 매물 채널이 더 크고, 용산은 2021년 매수분이 가격 상승으로 빚 부담이 줄었다.")
    lines.append("서울 평균 국평은 한도가 6억이라 평균금리가 8%가 되면 신규 대출은 금액한도보다 DSR에 먼저 걸린다.")
    lines.append("코호트 비중을 0으로 두면 매물 채널은 사라지고 금리·기대·소득·전세만 남는다.")
    lines.append("")
    lines.append(f"산출 폴더: {out_dir}")
    text = "\n".join(lines) + "\n"
    (out_dir / "report.txt").write_text(text, encoding="utf-8")
    return text


def _save(fig: plt.Figure, out_dir: Path, artifacts: Path, name: str) -> None:
    for folder in (out_dir, artifacts):
        folder.mkdir(parents=True, exist_ok=True)
        fig.savefig(folder / name, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_price_bars(results: list[DistrictResult], out_dir: Path, artifacts: Path) -> None:
    _font()
    central = [r for r in results if r.band == "central" and r.district != "서울"]
    scenarios = ["hikes_1", "hikes_4", "mortgage_8"]
    labels = ["추가 1회", "추가 4회", "평균 8%"]
    districts = [d.name for d in DISTRICTS if d.name != "서울"]
    fig, ax = plt.subplots(figsize=(11.2, 6.2))
    import numpy as np

    x = np.arange(len(districts))
    width = 0.25
    palette = ["#94A3B8", "#1E407C", "#991B1B"]
    for i, (sid, label, color) in enumerate(zip(scenarios, labels, palette)):
        vals = [
            100
            * (
                next(r for r in central if r.district == name and r.scenario == sid).price_ratio
                - 1
            )
            for name in districts
        ]
        bars = ax.bar(x + (i - 1) * width, vals, width, label=label, color=color)
        for bar, val in zip(bars, vals):
            inside = abs(val) >= 4
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                val - 0.45 if inside else val - 0.25,
                f"{val:.0f}",
                ha="center",
                va="top",
                fontsize=7,
                color="white" if inside else "#111827",
            )
    ax.axhline(0, color="#111827", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(districts)
    ax.set_ylabel("2026년 2분기 국평 대비 가격 변화 (%)")
    ax.set_title("중앙 가정: 금리 경로별 가격 변화")
    ax.legend(frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    _save(fig, out_dir, artifacts, "price_change_by_district.png")


def plot_waterfall(results: list[DistrictResult], out_dir: Path, artifacts: Path) -> None:
    _font()
    import numpy as np

    picks = [("강남구", "hikes_4"), ("마포구", "hikes_4"), ("강남구", "mortgage_8"), ("마포구", "mortgage_8")]
    titles = ["강남 추가 4회", "마포 추가 4회", "강남 평균 8%", "마포 평균 8%"]
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 7.4), sharey=True)
    for ax, (district, sid), title in zip(axes.ravel(), picks, titles):
        result = next(
            r for r in results if r.band == "central" and r.district == district and r.scenario == sid
        )
        parts = sequential_contributions(result)
        names = [p[0] for p in parts] + ["합산"]
        values = [100 * p[1] for p in parts]
        total = 100 * (result.price_ratio - 1)
        cumulative = 0.0
        for i, value in enumerate(values):
            color = "#166534" if value >= 0 else "#991B1B"
            ax.bar(i, value, bottom=cumulative, color=color, width=0.72)
            cumulative += value
        ax.bar(len(values), total, color="#0F2043", width=0.72)
        ax.axhline(0, color="#111827", linewidth=0.6)
        ax.set_xticks(np.arange(len(names)))
        ax.set_xticklabels(names, rotation=20, ha="right")
        ax.set_title(f"{title}  {total:.1f}%")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("채널별 기여 (순서대로 곱한 뒤 차이, 합이 총변화)", y=1.01)
    fig.tight_layout()
    _save(fig, out_dir, artifacts, "channel_waterfall.png")


def plot_payments(results: list[DistrictResult], out_dir: Path, artifacts: Path) -> None:
    _font()
    import numpy as np

    districts = [d.name for d in DISTRICTS if d.name != "서울"]
    central = [r for r in results if r.band == "central"]
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.6), sharey=False)
    x = np.arange(len(districts))
    width = 0.25

    def series(scenario: str, attr: str) -> list[float]:
        vals = []
        for name in districts:
            r = next(v for v in central if v.district == name and v.scenario == scenario)
            if attr == "reg":
                vals.append(r.regulated_service_new / 12 / 10_000)
            else:
                recent = next(v for v in r.vintages if v.name.startswith("2025"))
                vals.append(recent.service_new / 12 / 10_000)
        return vals

    now_reg = []
    now_bypass = []
    for name in districts:
        r = next(v for v in central if v.district == name and v.scenario == "hikes_4")
        now_reg.append(r.regulated_service_now / 12 / 10_000)
        recent = next(v for v in r.vintages if v.name.startswith("2025"))
        now_bypass.append(recent.service_now / 12 / 10_000)

    for ax, base, four, shock, title in (
        (
            axes[0],
            now_reg,
            series("hikes_4", "reg"),
            series("mortgage_8", "reg"),
            "규제 주담대만 (R114 평균 잔액)",
        ),
        (
            axes[1],
            now_bypass,
            series("hikes_4", "bypass"),
            series("mortgage_8", "bypass"),
            "고점 우회 코호트 (주담대+사업자)",
        ),
    ):
        ax.bar(x - width, base, width, label="지금", color="#94A3B8")
        ax.bar(x, four, width, label="추가 4회", color="#1E407C")
        ax.bar(x + width, shock, width, label="평균 8%", color="#991B1B")
        ax.set_xticks(x)
        ax.set_xticklabels(districts, rotation=0)
        ax.set_ylabel("월 상환액 (만원)")
        ax.set_title(title)
        ax.legend(frameon=False, fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.suptitle("같은 대출 잔액의 월 상환액", y=1.02)
    fig.tight_layout()
    _save(fig, out_dir, artifacts, "payment_shock.png")


def plot_hike_path(out_dir: Path, artifacts: Path) -> None:
    _font()
    a = Assumptions()
    names = ["강남구", "서초구", "송파구", "용산구", "성동구", "마포구"]
    xs = list(range(0, 9))
    fig, ax = plt.subplots(figsize=(10.4, 5.8))
    for name in names:
        district = next(d for d in DISTRICTS if d.name == name)
        ys = [
            100 * (evaluate(district, scenario_for_hikes(n), a).price_ratio - 1) for n in xs
        ]
        ax.plot(xs, ys, marker="o", label=name, color=COLORS[name], linewidth=2)
    ax.axhline(0, color="#111827", linewidth=0.7)
    ax.set_xlabel("기준금리 추가 인상 횟수 (회당 0.25%p, 스프레드 유지)")
    ax.set_ylabel("가격 변화 (%)")
    ax.set_title("스프레드가 유지될 때 인상 횟수와 가격")
    ax.set_xticks(xs)
    ax.legend(ncol=3, frameon=False)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    _save(fig, out_dir, artifacts, "hike_count_path.png")


def plot_heatmap(out_dir: Path, artifacts: Path) -> None:
    _font()
    import numpy as np

    a = Assumptions()
    spot = rate_state(0, 0.0, a)
    four = rate_state(4, 0.0, a)
    shares = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30]
    targets = [0.050, 0.055, 0.060, 0.070, 0.080, 0.090]
    fig, axes = plt.subplots(1, 2, figsize=(12.2, 5.4))
    for ax, name in zip(axes, ("강남구", "마포구")):
        district = next(d for d in DISTRICTS if d.name == name)
        grid = []
        for target in targets:
            extra = target - four.mortgage_avg
            dr = target - spot.mortgage_avg
            g = min(0.045, 0.008 + 0.70 * max(0.0, dr))
            scenario = Scenario(
                id="slice",
                label="slice",
                hikes=4,
                extra_term_premium=extra,
                g_decline=g,
                income_growth=0.05,
            )
            row = []
            for share in shares:
                result = evaluate(district, scenario, a, share_override=share)
                row.append(100 * (result.price_ratio - 1))
            grid.append(row)
        data = np.array(grid)
        image = ax.imshow(data, cmap="RdBu", vmin=-35, vmax=5, aspect="auto")
        ax.set_xticks(range(len(shares)))
        ax.set_xticklabels([f"{int(100 * s)}" for s in shares])
        ax.set_yticks(range(len(targets)))
        ax.set_yticklabels([f"{100 * t:.1f}" for t in targets])
        ax.set_xlabel("사업자대출 코호트 비중 (%)")
        ax.set_ylabel("주담대 평균금리 (%)")
        ax.set_title(name)
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                ax.text(j, i, f"{data[i, j]:.0f}", ha="center", va="center", color="#111827", fontsize=8)
        fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, label="%")
    fig.suptitle("소득 +5%를 고정한 뒤 코호트 비중과 평균금리", y=1.02)
    fig.tight_layout()
    _save(fig, out_dir, artifacts, "share_rate_heatmap.png")


def run(out_dir: Path, artifacts: Path) -> list[DistrictResult]:
    results: list[DistrictResult] = []
    for band in ("mild", "central", "severe"):
        assumptions, share_scale, g_scale = assumption_band(band)
        for scenario in headline_scenarios(assumptions):
            for district in DISTRICTS:
                results.append(
                    evaluate(
                        district,
                        scenario,
                        assumptions,
                        share_scale=share_scale,
                        g_scale=g_scale,
                        band=band,
                    )
                )
    out_dir.mkdir(parents=True, exist_ok=True)
    artifacts.mkdir(parents=True, exist_ok=True)
    rows = _rows(results)
    with (out_dir / "results.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    (out_dir / "results.json").write_text(
        json.dumps(rows, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    report = render_report(results, out_dir)
    plot_price_bars(results, out_dir, artifacts)
    plot_waterfall(results, out_dir, artifacts)
    plot_payments(results, out_dir, artifacts)
    plot_hike_path(out_dir, artifacts)
    plot_heatmap(out_dir, artifacts)
    (artifacts / "report.txt").write_text(report, encoding="utf-8")
    (artifacts / "results.csv").write_text((out_dir / "results.csv").read_text(encoding="utf-8"), encoding="utf-8")
    print(report)
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("/workspace/analysis/seoul_housing_rates/output"),
    )
    parser.add_argument(
        "--artifacts",
        type=Path,
        default=Path("/opt/cursor/artifacts"),
    )
    args = parser.parse_args()
    run(args.out, args.artifacts)


if __name__ == "__main__":
    main()
