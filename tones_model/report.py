"""리포트·차트·JSON 산출."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from tones_model.engine import ClinicEngine, StaticResult
from tones_model.params import ModelParams
from tones_model.physical import physical_matrix, required_patients, theoretical_ppd
from tones_model.simulate import (
    expected_from_bands,
    reality_bands,
    run_paths,
    stress_tests,
    tornado,
)
from tones_model.tax_kr import couple_from_monthly_revenue_eok


def _result_dict(s: StaticResult) -> Dict:
    return asdict(s)


def build_payload(p: ModelParams | None = None) -> Dict[str, Any]:
    p = p or ModelParams()
    eng = ClinicEngine(p)
    bands = reality_bands(eng)
    return {
        "params": {
            "fixed_cost_eok": p.fixed_cost_eok,
            "variable_rate": p.variable_rate,
            "mso_net_rate": p.mso_net_rate,
            "debt_eok": p.debt_eok,
            "treating_doctors": p.treating_doctors,
            "staff_headcount": p.staff_headcount,
            "work_days_high": p.work_days_high,
            "built_fixed_eok": round(p.built_fixed_eok(), 2),
        },
        "cost_breakdown": p.cost_breakdown(),
        "staff_roles": [
            {
                "name": r.name,
                "n": r.headcount,
                "월급여_만": r.monthly_pay_man,
                "연부담_억": round(r.headcount * r.monthly_pay_man * 12 * r.burden / 10_000, 2),
            }
            for r in p.staff_roles
        ],
        "physical_cap": theoretical_ppd(p),
        "bep": eng.bep_table(),
        "revenue_grid": [_result_dict(s) for s in eng.revenue_grid()],
        "required_patients": required_patients(eng),
        "physical_matrix": [
            r for r in physical_matrix(eng)
            if r["가동"] == "월2일휴무" and r["객단가_만"] in (12, 14, 14.5, 15, 16)
            and r["의사1인_일환자"] in (22, 25, 26, 28, 30, 32)
        ],
        "tax_examples": {
            str(m): couple_from_monthly_revenue_eok(m) for m in (6.5, 8.0, 9.7, 11.5, 12.5)
        },
        "monte_carlo": {
            "base": run_paths(p, prior="base"),
            "conservative": run_paths(p, prior="conservative"),
            "optimistic": run_paths(p, prior="optimistic"),
            "base_6pct": run_paths(p, prior="base", interest_rate=0.06),
        },
        "stress": stress_tests(p),
        "tornado": tornado(p),
        "reality_bands": bands,
        "band_ev": expected_from_bands(bands),
        "em_compare": _em_compare(eng, p),
        "interest_compare": {
            "무이자_월11.5": eng.interest_total_paid(11.5, 0.0),
            "6pct_월11.5": eng.interest_total_paid(11.5, 0.06),
            "무이자_월9.7": eng.interest_total_paid(9.7, 0.0),
            "6pct_월9.7": eng.interest_total_paid(9.7, 0.06),
        },
    }


def _em_compare(eng: ClinicEngine, p: ModelParams) -> Dict:
    rows = []
    for m in (7.0, 8.5, 9.7, 11.5, 12.5):
        s = eng.analyze(m)
        rows.append({
            "월매출_억": m,
            "톤즈_1인실수령_만": s.person_takehome_man,
            "응급의_1인_만": p.em_net_monthly_man,
            "차이_만": round(s.person_takehome_man - p.em_net_monthly_man),
            "톤즈_부부_만": s.couple_takehome_man,
            "근무": "월2일휴무 vs DN-OOOO",
        })
    return {
        "pattern": p.em_work_pattern,
        "em_net": p.em_net_monthly_man,
        "rows": rows,
    }


def write_json(payload: Dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_charts(payload: Dict, out_dir: Path) -> List[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    files = []
    grid = payload["revenue_grid"]
    xs = [g["monthly_eok"] for g in grid]
    repay = [g["repay_eok"] for g in grid]
    couple = [g["couple_takehome_man"] for g in grid]

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, repay, marker="o", label="MSO annual repayment (eok)")
    ax.axhline(90 / 7, color="red", ls="--", label="7y run-rate 12.9eok")
    ax.axhline(0, color="gray", lw=0.8)
    ax.set_xlabel("Monthly revenue (eok KRW)")
    ax.set_ylabel("Annual repayment capacity (eok)")
    ax.set_title("Repayment capacity vs monthly revenue (fixed 70eok)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    f1 = out_dir / "repayment_vs_revenue.png"
    fig.tight_layout()
    fig.savefig(f1, dpi=140)
    plt.close(fig)
    files.append(str(f1))

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(xs, couple, marker="o", color="tab:green", label="Couple take-home (man KRW)")
    ax.axhline(6000, color="gray", ls=":", label="60m couple")
    ax.set_xlabel("Monthly revenue (eok KRW)")
    ax.set_ylabel("Couple monthly take-home (10k KRW)")
    ax.set_title("Couple take-home (precise tax) vs revenue")
    ax.legend()
    ax.grid(True, alpha=0.3)
    f2 = out_dir / "couple_takehome.png"
    fig.tight_layout()
    fig.savefig(f2, dpi=140)
    plt.close(fig)
    files.append(str(f2))

    mc = payload["monte_carlo"]["base"]
    years = list(range(1, 11))
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.fill_between(years, mc["연매출경로_P10"], mc["연매출경로_P90"], alpha=0.25, label="P10–P90")
    ax.plot(years, mc["연매출경로_중앙"], marker="o", label="Median annual revenue")
    ax.set_xlabel("Year")
    ax.set_ylabel("Annual revenue (eok)")
    ax.set_title("10-year revenue path (Monte Carlo base prior)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    f3 = out_dir / "mc_revenue_path.png"
    fig.tight_layout()
    fig.savefig(f3, dpi=140)
    plt.close(fig)
    files.append(str(f3))

    # tornado
    t = payload["tornado"]
    labels = [r["레버"][:28] for r in t]
    swings = [r["스윙"] for r in t]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    y = np.arange(len(labels))
    ax.barh(y, swings, color="tab:orange")
    ax.set_yticks(y)
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlabel("Swing in monthly revenue (eok)")
    ax.set_title("Sensitivity (tornado)")
    fig.tight_layout()
    f4 = out_dir / "tornado.png"
    fig.savefig(f4, dpi=140)
    plt.close(fig)
    files.append(str(f4))
    return files


def write_markdown(payload: Dict, path: Path) -> None:
    p = payload
    bd = p["cost_breakdown"]
    bep = p["bep"]
    mc_b = p["monte_carlo"]["base"]
    mc_c = p["monte_carlo"]["conservative"]
    mc_o = p["monte_carlo"]["optimistic"]
    mc_i = p["monte_carlo"]["base_6pct"]
    ev = p["band_ev"]
    cap = p["physical_cap"]

    def row_grid(g):
        st = "흑자" if g["operating_ok"] else "적자"
        e7 = "Y" if g["exit_7"] else "N"
        return (
            f"| {g['monthly_eok']:.1f} | {g['person_verified_man']:,.0f} | {g['couple_verified_man']:,.0f} "
            f"| {g['person_takehome_man']:,.0f} | {g['couple_takehome_man']:,.0f} "
            f"| {g['repay_eok']:.1f} | {g['exit_years']:.1f} | {st} | {e7} |"
        )

    grid_md = "\n".join(row_grid(g) for g in p["revenue_grid"])

    phys_lines = [
        "| 의사당/일 | 객단가 | 일총 | 월매출 | 부부실수령 | 엑시트 | 7년 |",
        "|---:|---:|---:|---:|---:|---:|:---:|",
    ]
    for r in p["physical_matrix"]:
        phys_lines.append(
            f"| {r['의사1인_일환자']} | {r['객단가_만']} | {r['일총환자']} | {r['월매출_억']:.2f} "
            f"| {r['부부_실수령_만']:,} | {r['엑시트_년']:.1f} | {'Y' if r['7년'] else 'N'} |"
        )

    req = [r for r in p["required_patients"] if r["가동일"] == 28 and r["객단가_만"] in (14.5, 15)]
    req_md = "\n".join(
        f"| {r['목표']} | {r['필요_월매출_억']} | {r['객단가_만']} | {r['필요_일환자']} | {r['의사1인_일환자']} |"
        for r in req
    )

    band_md = "\n".join(
        f"| {b['밴드']} | {b['확률']*100:.0f}% | {b['월매출_로']}–{b['월매출_히']} | "
        f"{b['부부_실수령_만']:,} | {b['1인_실수령_만']:,} | {b['엑시트_년']:.1f} | "
        f"{'Y' if b['7년'] else 'N'} | {b['메모']} |"
        for b in p["reality_bands"]
    )

    stress_md = "\n".join(
        f"| {s['시나리오']} | {s['월매출_억']} | {s['부부_실수령_만']:,} | {s['연상환_억']} | {s['엑시트_년']} |"
        for s in p["stress"]
    )

    staff_md = "\n".join(
        f"| {r['name']} | {r['n']} | {r['월급여_만']:.0f} | {r['연부담_억']} |"
        for r in p["staff_roles"]
    )

    em_md = "\n".join(
        f"| {r['월매출_억']} | {r['톤즈_1인실수령_만']:,} | {r['응급의_1인_만']:,.0f} | {r['차이_만']:+,} | {r['톤즈_부부_만']:,} |"
        for r in p["em_compare"]["rows"]
    )

    tax_md = []
    for k, v in p["tax_examples"].items():
        tax_md.append(
            f"| {k} | {v['1인_세전_연_원']/100000000:.2f}억 | {v['1인_소득세실효']*100:.1f}% | "
            f"{v['1인_올인실효']*100:.1f}% | {v['1인_세후월_만']:,} | {v['1인_실수령월_만']:,} | "
            f"{v['부부_실수령월_만']:,} | {v['검증식_1인월_만']:,} |"
        )

    md = f"""# 톤즈 부평점 MSO 딜 — 정밀 재무 모델 보고서

검증식(고정 70억 · 변동 30% · 부부 10% 선취)을 유지한 채, 직원 50명 직종 분해 · 한국 세법 · 물리적 수용력 · 10년 월별 몬테카를로를 얹었다.

## 0. 한 줄 결론

- **운영 손익분기**: 월 **{bep['운영_손익분기_base']['월매출_억']}억** (고정 70억).
- **7년 완제선**: 월 **{bep['7년_완제_base']['월매출_억']}억**. **6년선** 월 **{bep['6년_완제_base']['월매출_억']}억**.
- **다년도 MC (Base prior)**: 월매출 중앙 **{mc_b['월매출_중앙']}억**, 부부 실수령 중앙 **{mc_b['부부_실수령_중앙_만']:,}만**, 7년 완제 **{mc_b['7년내_완제']}%**, 10년 완제 **{mc_b['10년내_완제']}%**.
- **현실 밴드 기대값**: 월 **{ev['기대_월매출_억']}억**, 부부 실수령 **{ev['기대_부부실수령_만']:,}만**. 이 구간은 월급은 나오지만 7년 엑시트는 보통 실패한다.
- 월급(10% 선취)과 소유권(90억 상환)은 **분리된 확률 변수**다.

## 1. 비용 구조 (직원 50명 포함)

분해 합계 **{bd['분해합계']}억** vs 모델 중앙 고정비 **{bd['모델고정비_중앙']}억**.
분해가 중앙보다 낮으면 성과급·야간수당·장비유지 버퍼를 중앙에 넣은 것이다. 민감도는 lean 64 / heavy 78.

| 항목 | 연 억 |
|---|---:|
| 직원 50 인건비(4대보험·퇴직) | {bd['직원50_인건비']} |
| 페이닥터 8명 | {bd['페이닥터_인건비']} |
| 황아름 부원장 | {bd['황아름_인건비']} |
| 임대·관리 (≈338평) | {bd['임대_관리']} |
| 고정 마케팅 | {bd['고정마케팅']} |
| 기타 고정 | {bd['기타고정']} |
| **분해 합계** | **{bd['분해합계']}** |
| **모델 중앙** | **{bd['모델고정비_중앙']}** |

### 직원 50명 직종

| 직종 | 인원 | 월급여(만) | 연 부담(억) |
|---|---:|---:|---:|
{staff_md}

변동비 30% 분해: 재료 22% + 카드 2.2% + 소모 1.5% + 퍼포먼스광고 4.3%.

MSO 상환여력 = `매출 × 60% − 고정비` (90% 유입 − 30% 변동).

## 2. BEP · 엑시트 임계 월매출

| 목표 | lean 64억 | **base 70억** | heavy 78억 |
|---|---:|---:|---:|
| 운영 손익분기 | {bep['운영_손익분기_lean']['월매출_억']} | **{bep['운영_손익분기_base']['월매출_억']}** | {bep['운영_손익분기_heavy']['월매출_억']} |
| 10년 완제 | {bep['10년_완제_lean']['월매출_억']} | **{bep['10년_완제_base']['월매출_억']}** | {bep['10년_완제_heavy']['월매출_억']} |
| 7년 완제 | {bep['7년_완제_lean']['월매출_억']} | **{bep['7년_완제_base']['월매출_억']}** | {bep['7년_완제_heavy']['월매출_억']} |
| 6년 완제 | {bep['6년_완제_lean']['월매출_억']} | **{bep['6년_완제_base']['월매출_억']}** | {bep['6년_완제_heavy']['월매출_억']} |

## 3. 월매출 → 부부 실수령 (검증식 vs 정밀세무)

검증식: 1인 세후 = 월매출 × 3.1%, 부부 × 6.2%.
정밀: 종합소득세 누진 + 지방세 10% + 건보 상한 + 국민연금 상한. 실수령은 4대보험까지 뺀 값.

| 월매출 | 1인검증 | 부부검증 | 1인실수령 | 부부실수령 | 연상환 | 엑시트년 | 운영 | 7년 |
|---:|---:|---:|---:|---:|---:|---:|:---:|:---:|
{grid_md}

### 세무 상세 샘플

| 월매출 | 1인 세전 연 | 소득세실효 | 올인실효 | 1인세후월 | 1인실수령월 | 부부실수령 | 검증식1인 |
|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(tax_md)}

고소득 구간에서 검증식(실효 38%)과 소득세 세후는 거의 같다. 건보·연금까지 빼면 실수령이 검증식보다 **약 8–12% 낮아진다**.

## 4. 물리적 수용력

진료 의사 FTE = 페이 8 + 부부 2 + 황아름 1 = **{p['params']['treating_doctors']}명**.
클리닉 {cap['의사1인_이론슬롯']} 슬롯/의사 (12시간 · 22분), 이용률 68% → 실용 **{cap['의사1인_실용_이용률반영']}명/의사/일**.
병목: **{cap['병목']}**. 룸 제약 일 총원 {cap['룸제약_일총환자']:.0f}명.

| 목표 | 필요월매출 | 객단가 | 필요 일환자 | 의사당 |
|---|---:|---:|---:|---:|
{req_md}

### 물리 매트릭스 (월 2일 휴무 · 28일)

{chr(10).join(phys_lines)}

**7년 완제의 물리 조건**: 의사당 일 28명 × 객단가 15만 전후, 또는 의사당 30명 × 14.5만. 의사당 25명 × 15만은 월급은 나와도 엑시트가 10년을 넘긴다.

## 5. 다년도 몬테카를로 (월별 4만 경로)

포함 동역학: 의사 연 18% 이탈 + 3개월 채용지연, 황아름 연 8% 이탈위험(+12% 매출 리프트), 3년차 이후 번아웃(생산성·가동일 하락), 미용 계절성, 임금 4.5%·객단가 2% 인플레.

| 지표 | Conservative | **Base** | Optimistic | Base+금리6% |
|---|---:|---:|---:|---:|
| 월매출 중앙 | {mc_c['월매출_중앙']} | **{mc_b['월매출_중앙']}** | {mc_o['월매출_중앙']} | {mc_i['월매출_중앙']} |
| 월매출 P25–P75 | {mc_c['월매출_P25']}–{mc_c['월매출_P75']} | **{mc_b['월매출_P25']}–{mc_b['월매출_P75']}** | {mc_o['월매출_P25']}–{mc_o['월매출_P75']} | {mc_i['월매출_P25']}–{mc_i['월매출_P75']} |
| 부부 실수령 중앙 | {mc_c['부부_실수령_중앙_만']:,} | **{mc_b['부부_실수령_중앙_만']:,}** | {mc_o['부부_실수령_중앙_만']:,} | {mc_i['부부_실수령_중앙_만']:,} |
| 1인 실수령 중앙 | {mc_c['1인_실수령_중앙_만']:,} | **{mc_b['1인_실수령_중앙_만']:,}** | {mc_o['1인_실수령_중앙_만']:,} | {mc_i['1인_실수령_중앙_만']:,} |
| 6년 완제 % | {mc_c['6년내_완제']} | **{mc_b['6년내_완제']}** | {mc_o['6년내_완제']} | {mc_i['6년내_완제']} |
| 7년 완제 % | {mc_c['7년내_완제']} | **{mc_b['7년내_완제']}** | {mc_o['7년내_완제']} | {mc_i['7년내_완제']} |
| 10년 완제 % | {mc_c['10년내_완제']} | **{mc_b['10년내_완제']}** | {mc_o['10년내_완제']} | {mc_i['10년내_완제']} |
| 10년 잔액 중앙 | {mc_c['10년후_잔액_중앙_억']} | **{mc_b['10년후_잔액_중앙_억']}** | {mc_o['10년후_잔액_중앙_억']} | {mc_i['10년후_잔액_중앙_억']} |
| 황아름 10년 잔류 % | {mc_c['황아름_10년잔류']} | **{mc_b['황아름_10년잔류']}** | {mc_o['황아름_10년잔류']} | {mc_i['황아름_10년잔류']} |

Base 경로 연매출 중앙: {mc_b['연매출경로_중앙']}
Base 경로 연상환 중앙: {mc_b['연상환경로_중앙']}

정적 스냅샷(매년 같은 월매출)보다 완제 확률이 낮다. 임금 인플레(4.5%)가 객단가 인플레(2%)보다 빠르고, 이탈·번아웃·계절성이 상환 누적을 깎기 때문이다.

**7년 완제 ≈ 10년 완제**가 이 모델의 핵심 결과다. 8–10년차 추가 완제는 Base {mc_b.get('8to10년_추가완제', 0)}%다. 번아웃과 인건비 인플레 때문에 후반기 상환여력이 사라져, 7년까지 못 갚은 경로는 계약 만기까지 잔액이 거의 줄지 않는다. “10년 있으면 어떻게든 갚겠지”는 이 비용 구조에서 성립하지 않는다.

## 6. 현실 밴드 (상권 피어 보정, MC와 별 트랙)

피어: 국세청 피부월 1.06억 · 부평역 1.21억 · 부평5동 평균 2.98억 · 상위20% 6.82억 · 톡스앤필 4.2억.

| 밴드 | 확률 | 월매출 | 부부실수령 | 1인 | 엑시트 | 7년 | 메모 |
|---|---:|---|---:|---:|---:|:---:|---|
{band_md}

확률가중 기대: 월매출 **{ev['기대_월매출_억']}억**, 부부 실수령 **{ev['기대_부부실수령_만']:,}만**, 밴드상 7년 가능 가중 **{ev['밴드가중_7년가능']}%**.

## 7. 스트레스 테스트

기준 물리 = 의사당 25명 × 14.5만 × 11 FTE × 28일.

| 시나리오 | 월매출 | 부부실수령 | 연상환 | 엑시트년 |
|---|---:|---:|---:|---:|
{stress_md}

## 8. 민감도 (7년선 스윙)

| 레버 | 하단 | 상단 | 스윙 |
|---|---:|---:|---:|
{chr(10).join(f"| {t['레버']} | {t['하단_월매출']} | {t['상단_월매출']} | {t['스윙']} |" for t in p['tornado'])}

이자 6%는 같은 월 11.5억에서도 총지급이 불어난다. 무이자 캡 여부가 이 딜에서 가장 비싼 한 줄이다.

무이자 vs 6% (월 11.5억 고정): {p['interest_compare']['무이자_월11.5']} vs {p['interest_compare']['6pct_월11.5']}
월 9.7억(운영 BEP): {p['interest_compare']['무이자_월9.7']} vs {p['interest_compare']['6pct_월9.7']}

## 9. 응급의학 (DN-OOOO, 월 3,000만) 비교

| 톤즈 월매출 | 톤즈 1인 실수령 | 응급의 1인 | 차이 | 톤즈 부부 |
|---:|---:|---:|---:|---:|
{em_md}

1인 기준으로 응급의 3,000만을 넘기려면 톤즈 월매출이 대략 **10억 중반**이 필요하다. 그 아래에서는 매일 출근하면서 돈이 적다. 부부 합산이 커 보이는 것은 2인 풀근무 효과다.

## 10. 해석

1. **월급은 매출의 함수, 소유권은 상환여력의 함수**다. 월 7–9억에서도 부부 4–6천만은 나오지만 병원은 적자고 90억은 줄지 않는다.
2. **6–7년 전언은 낙관 하단**이다. 다년도 Base에서 7년 완제는 {mc_b['7년내_완제']}%, Conservative는 {mc_c['7년내_완제']}%.
3. **월 2일 휴무는 매출을 올리지만 3년차 이후 번아웃 항이 경로를 깎는다.** 가동일 24일로 내려가면 7년선은 사실상 사라진다.
4. 계약서에서 숫자가 바뀌는 조항: 90%의 정의, 이자, 10년 미완제 잔액, 연대보증, OPEX 부담 주체.

실행: `python3 tones_bupyeong_model.py`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(md, encoding="utf-8")
