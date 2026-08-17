#!/usr/bin/env python3
"""톤즈 부평점 MSO 딜 정밀 모델 엔트리."""

from __future__ import annotations

from pathlib import Path

from tones_model.engine import ClinicEngine
from tones_model.params import ModelParams
from tones_model.physical import monthly_from_physical, theoretical_ppd
from tones_model.report import build_payload, write_charts, write_json, write_markdown
from tones_model.tax_kr import couple_from_monthly_revenue_eok


def _print_header(title: str) -> None:
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


def main() -> None:
    p = ModelParams()
    eng = ClinicEngine(p)
    root = Path(__file__).resolve().parent

    _print_header("톤즈 부평점 MSO — 정밀 재무 모델")
    print(f"고정비 중앙 {p.fixed_cost_eok}억 | 변동 {p.variable_rate:.1%} | MSO순마진 {p.mso_net_rate:.1%}")
    print(f"진료의사 FTE {p.treating_doctors} | 직원 {p.staff_headcount} | 가동일 {p.work_days_high}")
    print("비용 분해:", p.cost_breakdown())
    print("물리 상한:", theoretical_ppd(p))

    _print_header("[BEP] 고정비 시나리오별 필요 월매출")
    bep = eng.bep_table()
    for key in (
        "운영_손익분기_base",
        "10년_완제_base",
        "7년_완제_base",
        "6년_완제_base",
    ):
        v = bep[key]
        print(f"  {key:22s}  월 {v['월매출_억']:.2f}억  (연 {v['연매출_억']:.0f}억)")

    _print_header("[실수령] 검증식 vs 정밀세무 (부부)")
    print(f"  {'월매출':>7} {'1인검증':>8} {'부부검증':>8} {'1인실수령':>9} {'부부실수령':>9} {'연상환':>8} {'엑시트':>7}")
    for m in (6.5, 7.5, 8.5, 9.7, 10.5, 11.5, 11.8, 12.5):
        s = eng.analyze(m)
        print(
            f"  {s.monthly_eok:6.1f}억 {s.person_verified_man:7,.0f}만 {s.couple_verified_man:7,.0f}만 "
            f"{s.person_takehome_man:8,.0f}만 {s.couple_takehome_man:8,.0f}만 "
            f"{s.repay_eok:7.1f}억 {s.exit_years:6.1f}년"
        )

    _print_header("[물리] 의사당 환자 × 객단가 → 월매출 (28일, 11 FTE)")
    print(f"  {'PPD':>5} {'객단가':>6} {'월매출':>7} {'부부실수령':>10} {'엑시트':>7} {'7년':>4}")
    for ppd in (22, 25, 28, 30):
        for tix in (14, 14.5, 15, 16):
            m = monthly_from_physical(ppd, tix, p.treating_doctors, p.work_days_high)
            s = eng.analyze(m)
            print(
                f"  {ppd:4}명 {tix:5.1f}만 {s.monthly_eok:6.2f}억 "
                f"{s.couple_takehome_man:9,}만 {s.exit_years:6.1f}년 {'Y' if s.exit_7 else 'N':>4}"
            )

    print("\n풀 시뮬레이션 실행 중 (4 priors × 40,000 paths)...")
    payload = build_payload(p)

    out_json = root / "tones_model_results.json"
    out_md = root / "reports" / "tones_precision_report.md"
    chart_dir = root / "reports" / "charts"
    write_json(payload, out_json)
    write_markdown(payload, out_md)
    charts = write_charts(payload, chart_dir)

    mc = payload["monte_carlo"]
    _print_header("[MC] 10년 월별 경로")
    for name, key in (("Conservative", "conservative"), ("Base", "base"), ("Optimistic", "optimistic"), ("Base+6%", "base_6pct")):
        x = mc[key]
        print(
            f"  {name:14s} 월중앙 {x['월매출_중앙']:.2f}억 | 부부 {x['부부_실수령_중앙_만']:,}만 | "
            f"7년 {x['7년내_완제']:5.1f}% | 10년 {x['10년내_완제']:5.1f}% | 잔액중앙 {x['10년후_잔액_중앙_억']}억"
        )

    ev = payload["band_ev"]
    _print_header("[밴드 EV]")
    print(f"  기대 월매출 {ev['기대_월매출_억']}억 | 기대 부부실수령 {ev['기대_부부실수령_만']:,}만")

    _print_header("[응급의 비교] DN-OOOO 월 3,000만")
    for r in payload["em_compare"]["rows"]:
        print(
            f"  톤즈 월{r['월매출_억']:.1f}억 → 1인 {r['톤즈_1인실수령_만']:,}만 "
            f"(응급의 대비 {r['차이_만']:+,}만) | 부부 {r['톤즈_부부_만']:,}만"
        )

    # 정합성 체크
    tax = couple_from_monthly_revenue_eok(10.0)
    assert tax["검증식_1인월_만"] == 3100
    assert abs(eng.operating_bep() - 70 / 0.60 / 12) < 1e-9
    print("\n산출:", out_json)
    print("보고서:", out_md)
    print("차트:", ", ".join(charts))
    print("정합성 체크 통과.")


if __name__ == "__main__":
    main()
