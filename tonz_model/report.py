"""모델 실행 → JSON·마크다운·차트."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
from matplotlib import font_manager

from .engine import DealParams, bep_table, implied_daily_patients, monthly_snapshot, physical_monthly_eok
from .simulate import Prior, procedure_count_check, run_mc, stress_cases

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
EOK = 100_000_000


def _font() -> None:
    for name in ("WenQuanYi Micro Hei", "Noto Sans CJK KR", "DejaVu Sans"):
        if any(name.lower() in f.name.lower() for f in font_manager.fontManager.ttflist):
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


def _won(x: float) -> str:
    if abs(x) >= 100_000_000:
        return f"{x / EOK:,.2f}억"
    if abs(x) >= 10_000:
        return f"{x / 10_000:,.0f}만"
    return f"{x:,.0f}원"


def _yrs(y: float | None) -> str:
    if y is None or not np.isfinite(y) or y > 40:
        return "불가/40년+"
    return f"{y:.1f}년"


def build_payload() -> dict:
    packages = {
        "verified_58": DealParams(58.0, 0.30),
        "staff50_bottomup": DealParams(68.0, 0.30),
        "staff50_high": DealParams(76.0, 0.32),
    }
    recommended = "staff50_bottomup"
    p = packages[recommended]
    months = [5.0, 5.5, 6.0, 6.5, 7.0, 7.6, 8.0, 8.5, 9.0, 9.8, 10.1, 11.0, 12.1, 12.5]
    grid = {k: [monthly_snapshot(m, pk) for m in months] for k, pk in packages.items()}
    beps = {k: bep_table(pk) for k, pk in packages.items()}
    mc = run_mc(50_000, 42, Prior())
    stats = mc["stats"]
    capacity_prior = Prior(median_monthly_eok=10.5, sigma=0.22, floor=6.5, cap=16.0, shock_p=0.12)
    mc_cap = run_mc(50_000, 43, capacity_prior)
    stats_cap = mc_cap["stats"]
    stress = stress_cases(stats["rev_p50"], p)
    physical_base = monthly_snapshot(physical_monthly_eok(11, 25, 150_000, 28), p)

    tickets = [120_000, 140_000, 150_000, 160_000, 180_000]
    ppds = [20, 22, 25, 28, 32, 35]
    physical = {
        f"{ppd}x{ticket}": {
            "ppd": ppd,
            "ticket": ticket,
            "monthly_eok": physical_monthly_eok(11, ppd, ticket, 28),
            "daily_patients": 11 * ppd,
        }
        for ppd in ppds
        for ticket in tickets
    }

    proc_checks = [
        procedure_count_check(183_400, share, months_, ticket)
        for share, months_, ticket in (
            (0.35, 62, 150_000),
            (0.40, 62, 180_000),
            (0.35, 6, 150_000),
            (0.20, 12, 150_000),
        )
    ]

    peers = json.loads((ROOT / "data" / "sources.json").read_text())["peers"]
    sources = json.loads((ROOT / "data" / "sources.json").read_text())
    assumptions = json.loads((ROOT / "data" / "assumptions.json").read_text())

    em_net = 30_000_000
    couple_p50 = stats["couple_p50"]
    one_p50 = stats["net1_p50"]

    # serialize mc without huge arrays
    return {
        "recommended_package": recommended,
        "beps": beps,
        "grid": {
            k: [
                {
                    **{kk: (None if isinstance(vv, float) and not np.isfinite(vv) else vv) for kk, vv in row.items()}
                }
                for row in rows
            ]
            for k, rows in grid.items()
        },
        "mc": stats,
        "mc_capacity": stats_cap,
        "physical_base_25x15": {
            k: (None if isinstance(v, float) and not np.isfinite(v) else v) for k, v in physical_base.items()
        },
        "stress": {
            k: {kk: (None if isinstance(vv, float) and not np.isfinite(vv) else vv) for kk, vv in v.items()}
            for k, v in stress.items()
        },
        "physical": physical,
        "procedure_count_checks": proc_checks,
        "peers": peers,
        "clinic": sources["clinic"],
        "nts": sources["nts"],
        "assumptions": assumptions,
        "em_comparison": {
            "em_net_monthly": em_net,
            "deal_one_p50": one_p50,
            "deal_couple_p50": couple_p50,
            "one_vs_em": one_p50 - em_net,
            "hours_note": "EM: DN+OOOO / Deal: 월 2일 휴무",
        },
        "x_status": "X MCP 미인증 — 공개 웹·공공데이터만 사용",
    }


def write_markdown(d: dict) -> str:
    b = d["beps"]["staff50_bottomup"]
    b58 = d["beps"]["verified_58"]
    mc = d["mc"]
    em = d["em_comparison"]
    clinic = d["clinic"]

    def row(pkg: str, m: float) -> dict:
        for r in d["grid"][pkg]:
            if abs(r["monthly_eok"] - m) < 1e-9:
                return r
        return d["grid"][pkg][0]

    lines = [
        "# 톤즈 부평점 딜 — 코드 정밀 추정",
        "",
        "기준일 2026-08-17. 권장 패키지: **직원 50명 바텀업 (고정 68억, 변동 30%, 부부 10% 선취, 무이자 90억)**.",
        "현금흐름 항등식: `상환여력 = 연매출 × (0.90 − 변동비) − 연고정비`.",
        "",
        "## 1. 하드 데이터 (공개)",
        "",
        f"- 주소 {clinic['address']}, 개원 {clinic['opened']}",
        f"- 면적 **{clinic['area_m2']:,}㎡ ≈ {clinic['area_pyeong']}평** (500평 마케팅 수치와 불일치)",
        f"- 의사 **일반의 {clinic['doctors_gp']} / 전문의 {clinic['doctors_specialist']}**, 의료인 {clinic['medical_staff_count']}",
        f"- 체인 {clinic['chain_branches_2026']}지점, 전 지점 누적 시술 {clinic['cumulative_procedures_all_branches_2026_06']:,}건 (2026-06 공식)",
        "- 본점 2025 연매출 150억은 나무위키 자기신고(운명전쟁49). 세무·카드 검증 없음.",
        "- 국세청 피부·비뇨기과 평균 연매출 2023년 12.7억 (월 1.06억).",
        "- 데일리팜 부평역 500m 피부과 평균 월 1.21억, 중간값 0.88억 (n=20).",
        "",
        "## 2. BEP (권장 68억 vs 대화 확정 58억)",
        "",
        "| 목표 | 고정 68억·변동 30% | 고정 58억·변동 30% |",
        "|---|---:|---:|",
        f"| 운영 손익분기 | 월 {b['operating']:.2f}억 | 월 {b58['operating']:.2f}억 |",
        f"| 10년 완제 | 월 {b['y10']:.2f}억 | 월 {b58['y10']:.2f}억 |",
        f"| 7년 완제 | 월 {b['y7']:.2f}억 | 월 {b58['y7']:.2f}억 |",
        f"| 6년 완제 | 월 {b['y6']:.2f}억 | 월 {b58['y6']:.2f}억 |",
        "",
        "대화 후반의 고정 70억·기여마진 63% 식은 `(0.90−0.30)=0.60` 항등식과 맞지 않아 폐기했다.",
        "3.1% 실수령 계수는 실효세 38% 고정 근사다. 실제 누진+건보+연금이면 고매출에서 1인 실수령이 더 낮다.",
        "",
        "## 3. 매출 밴드별 부부 실수령·엑시트 (권장식)",
        "",
        "| 월매출 | 1인 세후 | 부부 세후 | 연 상환여력 | 엑시트 | 3.1%식 1인 | 3.1% 과대 |",
        "|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for m in (5.5, 6.5, 7.6, 8.5, 9.8, 10.1, 12.1):
        r = row("staff50_bottomup", m)
        lines.append(
            f"| {m:.1f}억 | {_won(r['each_net_monthly_won'])} | {_won(r['couple_net_monthly_won'])} | "
            f"{r['surplus_annual_eok']:.1f}억 | {_yrs(r['exit_years'])} | "
            f"{_won(r['shortcut_3_1pct_one_won'])} | {_won(r['shortcut_gap_won'])} |"
        )

    lines += [
        "",
        "## 4. 몬테카를로 (50,000경로, seed=42)",
        "",
        "매출 prior: 로그정규 중앙값 월 7.6억, σ=0.30, 바닥 3.8 / 천장 16.0. "
        "18% 경로에 18% 수요 충격. 고정비 삼각(58, 68, 76), 변동비 삼각(0.26, 0.30, 0.34).",
        "",
        f"- 기대 월매출 평균 {mc['rev_mean']:.2f}억, 중앙 {mc['rev_p50']:.2f}억, P10–P90 {mc['rev_p10']:.2f}–{mc['rev_p90']:.2f}억",
        f"- 1인 실수령 중앙 {_won(mc['net1_p50'])} (P10 {_won(mc['net1_p10'])} / P90 {_won(mc['net1_p90'])})",
        f"- 부부 실수령 중앙 {_won(mc['couple_p50'])} (P10 {_won(mc['couple_p10'])} / P90 {_won(mc['couple_p90'])})",
        f"- 운영 잉여>0 확률 {mc['p_operating_surplus']*100:.1f}%",
        f"- 6년 완제 {mc['p_exit_6']*100:.1f}% · 7년 {mc['p_exit_7']*100:.1f}% · 10년 {mc['p_exit_10']*100:.1f}% · 15년 {mc['p_exit_15']*100:.1f}%",
        f"- 상환 불가(잉여≤0) {mc['p_never']*100:.1f}%",
        f"- 유한 경로 엑시트 중앙값 {_yrs(mc['exit_p50_finite'])}",
        "",
        "6~7년 목표는 통계적으로 ‘불가능’(p<0.05)은 아니지만, 성공 확률이 유의미하게 높지도 않다.",
        "",
        "### 조건부: 이미 고볼륨 본점으로 의자가 차는 경우",
        "",
        "의사 11명 × 일 25명 × 객단가 15만 × 28일은 월 **11.55억**. 이 점을 권장식에 넣으면 "
        f"부부 {_won(d['physical_base_25x15']['couple_net_monthly_won'])}, 엑시트 {_yrs(d['physical_base_25x15']['exit_years'])}.",
        "",
        f"용량 조건부 MC(중앙 10.5억, σ=0.22): 7년 완제 {d['mc_capacity']['p_exit_7']*100:.1f}% · 10년 {d['mc_capacity']['p_exit_10']*100:.1f}% · "
        f"부부 중앙 {_won(d['mc_capacity']['couple_p50'])}.",
        "최근 12개월 실측이 월 10억을 넘으면 이 열이 맞고, 7억대면 위 비조건부 열이 맞다.",
        "",
        "## 5. 물리적 수용력 (의사 11명 × 28일)",
        "",
        "| 의사당 일환자 | 객단가 12만 | 14만 | 15만 | 16만 | 18만 |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for ppd in (20, 22, 25, 28, 32, 35):
        cells = [f"{physical_monthly_eok(11, ppd, t, 28):.1f}억" for t in (120000, 140000, 150000, 160000, 180000)]
        lines.append(f"| {ppd}명 | " + " | ".join(cells) + " |")

    need7 = b["y7"]
    daily_15 = implied_daily_patients(need7, 150_000, 28)
    lines += [
        "",
        f"7년 완제선 월 {need7:.2f}억을 객단가 15만으로 채우려면 **일 {daily_15:.0f}명** "
        f"(의사당 {daily_15/11:.1f}명). 고볼륨 쁘띠에서 물리적으로 가능하나, 공식 사이트는 ‘하루 진료 인원 제한’을 내건다.",
        "",
        "## 6. 누적 시술 183,400건 역산 (전 지점 공식 수치)",
        "",
        "본점 비중·집계 기간을 모르면 150억 자기신고와 충돌한다.",
        "",
    ]
    for c in d["procedure_count_checks"]:
        lines.append(
            f"- 본점 비중 {c['hq_share']:.0%} · {c['months']:.0f}개월 · 객단가 {c['ticket_won']/10000:.0f}만 "
            f"→ 월 내원 {c['monthly_visits']:,.0f} · 월매출 {c['implied_monthly_eok']:.2f}억"
        )
    lines += [
        "",
        "183,400이 5년 전 지점 누적이면 본점 월매출은 2억대 전후가 된다. 2026년 반기 전 지점 수치라면 본점 월 7억 전후까지 올라간다. "
        "**150억(월 12.5억)은 이 공식 건수와 같이 쓰려면 객단가·집계정의가 따로 증명돼야 한다.**",
        "",
        "## 7. Peer",
        "",
        "| 벤치마크 | 월매출 | 신뢰도 |",
        "|---|---:|---|",
    ]
    for p in d["peers"]:
        lines.append(f"| {p['name']} | {p['monthly_eok']:.2f}억 | {p.get('confidence','')} |")

    lines += [
        "",
        "권장 prior 중앙 7.6억은 부평 평균의 약 6.3배, 부평5동 상위 20%(6.82억, Medigate 미검증)를 소폭 상회하는 대형점 위치다.",
        "",
        "## 8. 스트레스 (중앙 매출 기준)",
        "",
        "| 시나리오 | 월매출 | 부부 실수령 | 엑시트 |",
        "|---|---:|---:|---:|",
    ]
    labels = {
        "base": "Base(MC 중앙)",
        "rev_minus_20pct": "매출 −20%",
        "rev_minus_30pct": "매출 −30%",
        "two_doctors_gone_approx_18pct": "의사 2명 이탈 ≈−18%",
        "hwang_exit_minus_15pct": "황아름 이탈 −15%",
        "fixed_plus_10pct": "고정비 +10%",
        "interest_6pct": "이자 6% 부가",
    }
    for k, lab in labels.items():
        s = d["stress"][k]
        ey = s["exit_years"]
        lines.append(
            f"| {lab} | {s['monthly_eok']:.2f}억 | {_won(s['couple_net_monthly_won'])} | {_yrs(ey if ey is not None else float('inf'))} |"
        )

    lines += [
        "",
        "## 9. 응급의학 DN OOOO 월 3,000만과 비교",
        "",
        f"- 현재 1인 실수령 3,000만 vs 딜 1인 중앙 {_won(em['deal_one_p50'])} (차이 {_won(em['one_vs_em'])})",
        f"- 딜 부부 중앙 {_won(em['deal_couple_p50'])} — 두 명이 거의 매일 출근해야 나오는 합산",
        "- 휴무 질: DN 후 Off×4 vs 월 2일. 같은 돈이어도 삶의 질은 현재가 우위",
        "- 딜이 현재 1인 3,000만을 넘기려면 월매출 약 11억+ (낙관 꼬리). 그때도 소유권은 별도 복권",
        "",
        "## 10. 판정",
        "",
        "1. **월급은 통계적으로 닫혀 있다.** 선취 10% 때문에 병원이 적자여도 부부 합산 월 4,000만 전후는 나올 수 있다.",
        "2. **6~7년 소유권은 닫혀 있지 않다.** 권장식 7년선은 월 약 "
        f"{b['y7']:.1f}억. MC 7년 완제 확률 {mc['p_exit_7']*100:.0f}%.",
        "3. **150억/월 12.5억 prior를 기본값으로 쓰면 안 된다.** 자기신고 + 공식 시술건수와 충돌.",
        "4. **고정 30억 모델은 폐기.** 의사 9 + 직원 50이면 인건비만 50억 전후.",
        "5. **계약서 스위치:** 90% 정의, 90억 캡 vs 10년 고정, 미완제 잔액, 연대보증, OPEX 부담 주체, 황아름 지위.",
        "6. 응급의학 전문의 본인이 이 딜로 옮기는 것은 숫자·휴무·리스크 모두 불리.",
        "",
        f"X 보정: {d['x_status']}.",
        "",
    ]
    return "\n".join(lines)


def charts(d: dict, mc_full: dict) -> None:
    _font()
    OUT.mkdir(exist_ok=True)
    p = DealParams(68.0, 0.30)
    xs = np.linspace(4.0, 14.0, 81)
    snaps = [monthly_snapshot(float(x), p) for x in xs]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, [s["surplus_annual_eok"] for s in snaps], color="#1f4e79", lw=2, label="연 상환여력")
    ax.axhline(90 / 7, color="#c0392b", ls="--", label="7년 완제선 12.9억")
    ax.axhline(90 / 10, color="#e67e22", ls=":", label="10년 완제선 9.0억")
    ax.axhline(0, color="#888", lw=0.8)
    ax.set_xlabel("월 매출 (억)")
    ax.set_ylabel("연 상환여력 (억)")
    ax.set_title("고정 68억 · 변동 30% · 무이자 90억")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "surplus_vs_revenue.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, [s["couple_net_monthly_won"] / 10_000 for s in snaps], color="#1f4e79", lw=2, label="부부 세후")
    ax.plot(xs, [s["each_net_monthly_won"] / 10_000 for s in snaps], color="#2980b9", lw=2, label="1인 세후")
    ax.axhline(3000, color="#c0392b", ls="--", label="EM 1인 3,000만")
    ax.set_xlabel("월 매출 (억)")
    ax.set_ylabel("실수령 (만원)")
    ax.set_title("누진 종소세+건보+연금 반영 실수령")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "takehome_vs_revenue.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(mc_full["monthly_eok"], bins=40, color="#5b8fa8", edgecolor="white")
    ax.axvline(d["mc"]["rev_p50"], color="#c0392b", ls="--", label=f"중앙 {d['mc']['rev_p50']:.2f}억")
    ax.axvline(d["beps"]["staff50_bottomup"]["y7"], color="#8e44ad", ls=":", label="7년선")
    ax.set_xlabel("월 매출 (억)")
    ax.set_title("몬테카를로 월매출 분포 (n=50,000)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "mc_revenue_hist.png", dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    finite = mc_full["exit_years"][np.isfinite(mc_full["exit_years"])]
    ax.hist(np.clip(finite, 0, 20), bins=30, color="#7f8c8d", edgecolor="white")
    ax.set_xlabel("엑시트 연수 (20년에서 절단)")
    ax.set_title(f"유한 경로만, 비중 {len(finite)/len(mc_full['exit_years'])*100:.0f}%")
    fig.tight_layout()
    fig.savefig(OUT / "mc_exit_hist.png", dpi=140)
    plt.close(fig)

    peers = d["peers"]
    fig, ax = plt.subplots(figsize=(9, 5))
    names = [p["name"] for p in peers] + ["모델 중앙", "7년 완제선"]
    vals = [p["monthly_eok"] for p in peers] + [d["mc"]["rev_p50"], d["beps"]["staff50_bottomup"]["y7"]]
    colors = ["#95a5a6"] * len(peers) + ["#1f4e79", "#c0392b"]
    ax.barh(names[::-1], vals[::-1], color=colors[::-1])
    ax.set_xlabel("월 매출 (억)")
    ax.set_title("Peer vs 모델")
    fig.tight_layout()
    fig.savefig(OUT / "peer_compare.png", dpi=140)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    payload = build_payload()
    mc_full = run_mc(50_000, 42, Prior())
    md = write_markdown(payload)
    (OUT / "estimate.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "ESTIMATE.md").write_text(md, encoding="utf-8")
    charts(payload, mc_full)
    print(md)


if __name__ == "__main__":
    main()
