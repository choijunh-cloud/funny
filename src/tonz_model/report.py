"""마크다운 리포트 생성."""

from __future__ import annotations

import numpy as np

from . import capacity, deterministic as det
from .costs import fixed_cost_annual, monthly_costs
from .params import ModelParams
from .units import fmt_eok, fmt_man, from_eok, to_eok


def table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |"]
    out.append("|" + "|".join(["---"] * len(headers)) + "|")
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def pct(x: float, digits: int = 1) -> str:
    return f"{x * 100:.{digits}f}%"


# --------------------------------------------------------------------------
def assumptions_section(p: ModelParams) -> str:
    c, cap = p.cost, p.capacity
    ref = from_eok(10.0)  # 월 10억 기준으로 비용 구조를 보여준다
    cb = monthly_costs(ref, cost=c, cap=cap)
    rows = [
        ["직원 인건비", f"{c.staff_headcount}명 × {c.staff_avg_monthly_pay:.0f}만 × 부대 {c.staff_burden_multiple:.2f}", fmt_eok(float(cb.staff) * 12), "고정"],
        ["봉직의 보수", f"{cap.employed_doctors}명, 세후보장 {c.doctor_net_guarantee:.0f}만 vs 인센티브 {pct(c.doctor_incentive_rate,0)}", fmt_eok(float(cb.doctors) * 12), "준변동"],
        ["임대+관리", f"{c.pyeong:.0f}평 × 평당 {c.rent_per_pyeong_month:.0f}만 × (1+{c.management_fee_ratio:.2f})", fmt_eok(float(cb.rent) * 12), "고정"],
        ["마케팅", f"매출의 {pct(c.marketing_rate,0)} (하한 {fmt_eok(c.marketing_floor_annual,0)}/년)", fmt_eok(float(cb.marketing) * 12), "변동+하한"],
        ["기타 고정", "전산·보험·유지보수·리스·세무 등", fmt_eok(float(cb.other_fixed) * 12), "고정"],
        ["변동비", f"재료 {pct(c.consumables_rate,0)} + 카드 {pct(c.card_fee_rate,1)} + 플랫폼 {pct(c.platform_fee_rate,1)}", fmt_eok(float(cb.variable) * 12), "변동"],
        ["**합계**", "월 10억 기준", f"**{fmt_eok(float(cb.total) * 12)}**", ""],
    ]
    body = table(["항목", "산식", "연간(월매출 10억 기준)", "성격"], rows)
    fixed = fixed_cost_annual(c, cap)
    return (
        "## 1. 비용 구조 (여기서부터 다시 시작)\n\n"
        "지금까지 대화에서 고정비가 30억 → 58억 → 70억으로 널뛴 이유는 "
        "'무엇을 고정비로 볼 것인가'가 정해지지 않아서다. 이 모델은 항목별로 분해하고 "
        "봉직의 보수를 준변동비(최저보장 vs 인센티브 중 큰 값)로 처리한다.\n\n"
        + body
        + f"\n\n- 매출과 무관하게 나가는 **진짜 고정비: 연 {fmt_eok(fixed)}** "
        f"(직원 {c.staff_headcount}명 + 봉직의 최저보장 + 임대 + 기타 + 마케팅 하한)\n"
        f"- 변동비율 합계: {pct(c.variable_rate)} + 마케팅 {pct(c.marketing_rate,0)}\n"
    )


def capacity_section(p: ModelParams) -> str:
    cap = p.capacity
    prof = capacity.profile(cap)
    rows = [
        ["의사 병목", f"의사-일수 {prof.doctor_days_per_month:.0f} × 1인한계 {cap.ppd_hard_cap:.0f}명 ÷ {cap.open_days_per_month:.0f}일", f"{prof.doctor_limited_patients_day:.0f}명/일"],
        ["시술실 병목", f"{cap.treatment_rooms}실 × {cap.room_turns_per_day:.0f}회전", f"{prof.room_limited_patients_day:.0f}명/일"],
        ["시술인력 병목", f"{cap.clinical_staff}명 × {cap.treatments_per_staff_day:.0f}건", f"{prof.staff_limited_patients_day:.0f}명/일"],
        ["**실질 천장**", f"구속 제약: **{prof.binding_constraint}**", f"**{prof.max_patients_day:.0f}명/일**"],
    ]
    cap_table = table(["병목", "산식", "1일 환자 상한"], rows)

    tickets = [12.0, 14.0, 16.0, 18.0]
    ceil_rows = []
    for tk in tickets:
        ceil_rows.append(
            [f"{tk:.0f}만원", fmt_eok(prof.max_revenue_month(tk)), fmt_eok(prof.max_revenue_month(tk) * 12)]
        )
    ceil = table(["객단가", "물리적 최대 월매출", "연환산"], ceil_rows)

    targets = {
        "운영 손익분기": det.operating_bep(p),
        "10년 완제": det.required_revenue(p, 10),
        "7년 완제": det.required_revenue(p, 7),
        "6년 완제": det.required_revenue(p, 6),
    }
    rev_rows = []
    for label, rev in targets.items():
        cells = [label, fmt_eok(rev)]
        for tk in (12.0, 14.0, 16.0):
            need = capacity.patients_needed(rev, tk, cap)
            mark = "" if need["물리적_실현가능"] else " ⚠"
            cells.append(f"{need['일_환자수']:.0f}명/일 (의사당 {need['의사1인_1일_환자수']:.0f}){mark}")
        rev_rows.append(cells)
    need_tbl = table(
        ["목표", "필요 월매출", "객단가 12만", "객단가 14만", "객단가 16만"], rev_rows
    )
    return (
        "## 2. 물리적 용량 — 하루에 몇 명을 봐야 하는가\n\n"
        + cap_table
        + "\n\n"
        + ceil
        + "\n\n### 목표별 필요 환자수 역산\n\n"
        + need_tbl
        + "\n\n⚠ = 시설/인력 물리 한계를 초과하는 조합 (그 객단가로는 불가능)\n"
    )


def bep_section(p: ModelParams) -> str:
    import dataclasses

    rows = []
    for label, years in [("운영 손익분기", None), ("10년 완제", 10), ("7년 완제", 7), ("6년 완제", 6)]:
        for rate, rname in [(0.0, "무이자"), (0.06, "이자 6%")]:
            pp = dataclasses.replace(p, deal=dataclasses.replace(p.deal, interest_annual=rate))
            rev = det.operating_bep(pp) if years is None else det.required_revenue(pp, years)
            need = det.required_monthly_payment(pp, years) * 12 if years else 0.0
            rows.append(
                [
                    label,
                    rname,
                    fmt_eok(rev),
                    fmt_eok(rev * 12),
                    fmt_eok(need) if years else "—",
                ]
            )
    t = table(["목표", "이자 조건", "필요 월매출", "연환산", "필요 연상환액"], rows)
    clinic = det.clinic_bep(p)
    return (
        "## 3. BEP와 기간별 필요 매출\n\n"
        + t
        + f"\n\n- 병원 자체 손익분기(부부 선취 무시, 매출=OPEX): **{fmt_eok(clinic)}/월**\n"
        f"- 부부 10% 선취를 얹은 MSO 기준 손익분기: **{fmt_eok(det.operating_bep(p))}/월**\n"
        "- 이 차이가 '부부는 흑자인데 병원은 적자'인 구간의 폭이다.\n"
    )


def takehome_section(p: ModelParams) -> str:
    rows = []
    for eok in [5, 6, 7, 8, 9, 10, 11, 12, 14]:
        rev = from_eok(eok)
        th = det.couple_take_home(rev, p)
        yrs = det.payoff_years(rev, p)
        rows.append(
            [
                fmt_eok(rev, 0),
                fmt_man(th["1인_세전_월"]),
                fmt_man(th["1인_세후_월"]),
                fmt_man(th["부부_세후_월"]),
                pct(th["실효부담률"]),
                fmt_eok(th["상환여력_연"], 1),
                "불가" if yrs == float("inf") else f"{yrs:.1f}년",
            ]
        )
    t = table(
        ["월매출", "1인 세전", "1인 세후", "부부 세후", "실효부담률", "연 상환여력", "완제 소요"],
        rows,
    )
    return (
        "## 4. 매출별 실수령·상환여력 (정적 가정)\n\n"
        "세금은 '38% 일괄'이 아니라 종합소득세 누진 + 지방소득세 + 국민연금 + 건강보험(상한 적용)으로 계산했다.\n\n"
        + t
        + "\n\n실효부담률이 매출과 함께 올라가기 때문에, "
        "'1인 세후 = 월매출 × 3.1%' 같은 선형 계수는 고매출 구간에서 실수령을 과대평가한다.\n"
    )


def mc_section(summary: dict, p: ModelParams) -> str:
    s = summary
    rows = [
        ["6년 내 완제 (소유권 확보)", pct(s["P(6년내 완제)"])],
        ["7년 내 완제", pct(s["P(7년내 완제)"])],
        ["10년 내 완제", pct(s["P(10년내 완제)"])],
        ["폐업 또는 적발로 종료", pct(s["P(폐업/적발)"])],
        ["  └ 5년 내 종료", pct(s["P(5년내 종료)"])],
        ["사무장병원 적발", pct(s["P(사무장병원 적발)"])],
        ["창업자(황아름) 이탈", pct(s["P(창업자 이탈)"])],
        ["부부 번아웃/근무 정상화", pct(s["P(번아웃/근무정상화)"])],
        ["  └ 3년 내", pct(s["P(3년내 번아웃)"])],
        ["누적적자로 선취율 재협상", pct(s["P(재협상으로 선취율 인하)"])],
    ]
    t1 = table(["사건", "10년 내 발생확률"], rows)
    rows2 = [
        ["3년차 월매출", fmt_eok(s["매출_3년차_월_p10"]), fmt_eok(s["매출_3년차_월_중앙"]), fmt_eok(s["매출_3년차_월_p90"])],
        ["5년차 월매출", "—", fmt_eok(s["매출_5년차_월_중앙"]), "—"],
        [
            "부부 합산 세후 월수령(1~5년)",
            fmt_man(s["부부세후월_1~5년_p10"]),
            fmt_man(s["부부세후월_1~5년_중앙"]),
            fmt_man(s["부부세후월_1~5년_p90"]),
        ],
    ]
    t2 = table(["지표", "p10", "중앙값", "p90"], rows2)
    med = s["완제_중앙연수"]
    med_s = "10년 내 미완제" if med != med else f"{med:.1f}년"
    return (
        f"## 5. 몬테카를로 ({s['n_paths']:,}경로 × 120개월)\n\n"
        + t1
        + "\n\n"
        + t2
        + f"\n\n- 완제 경로들의 완제 시점 중앙값: {med_s}\n"
        f"- 10년 후 잔액 중앙값: {fmt_eok(s['잔액_10년후_중앙'])}\n"
        f"- 개인 추가부담(환수·세무추징) 기대값: {fmt_eok(s['개인추가부담_기대값'])}\n"
    )


def scenario_section(scen: dict[str, dict]) -> str:
    rows = []
    for key, s in scen.items():
        rows.append(
            [
                key,
                s["설명"],
                pct(s["P(7년내 완제)"]),
                pct(s["P(10년내 완제)"]),
                fmt_man(s["부부세후월_1~5년_중앙"]),
                fmt_eok(s["매출_3년차_월_중앙"]),
            ]
        )
    return (
        "## 6. 시나리오 / 스트레스 테스트\n\n"
        + table(
            ["키", "설명", "P(7년 완제)", "P(10년 완제)", "부부 세후월(중앙)", "3년차 월매출(중앙)"],
            rows,
        )
        + "\n"
    )


def tornado_section(rows: list[dict]) -> str:
    body = []
    for r in rows:
        body.append(
            [
                r["파라미터"],
                f"{r['low']}",
                f"{r['high']}",
                pct(r["metric_low"]),
                pct(r["metric_high"]),
                pct(r["swing"]),
            ]
        )
    return (
        "## 7. 민감도 (토네이도, 지표 = 7년 내 완제 확률)\n\n"
        + table(["파라미터", "low", "high", "low일 때", "high일 때", "스윙"], body)
        + "\n"
    )


def feasibility_section(rows: list[dict], sched: dict, p: ModelParams) -> str:
    body = []
    for r in rows:
        body.append(
            [
                r["목표"],
                fmt_eok(r["필요_월매출"]),
                f"{r['z']:+.2f}σ",
                pct(r["p_단년도_달성"]),
                pct(r["p_유지"]),
                "—" if r["p_실제완제"] != r["p_실제완제"] else pct(r["p_실제완제"]),
            ]
        )
    t = table(
        ["목표", "필요 월매출", "앵커 대비", "단년도 달성확률", "그 기간 평균 유지확률", "실제 완제확률"],
        body,
    )
    surv = ", ".join(f"{y}년 {pct(s, 0)}" for y, s in sched["생존곡선"])
    return (
        "## 9. '통계적으로 가능한가' — 두 층으로 나눠 답하기\n\n"
        "도달과 유지는 다른 질문이다. 단년도 기준으로는 어떤 목표도 p<0.05로 기각되지 않는다. "
        "확률을 죽이는 건 '6~7년 연속' 쪽이다.\n\n"
        + t
        + "\n\n### 월 2일 휴무의 지속가능성\n\n"
        f"- 월 2일 휴무 체제가 유지될 확률: {surv}\n"
        f"- 근무 정상화/번아웃까지 걸리는 시간 중앙값: {sched['중앙_유지연수']:.1f}년\n"
        f"- 10년 내내 유지할 확률: **{pct(sched['P(끝까지 유지)'])}**\n\n"
        "즉 '월 2일 휴무로 6~7년'은 시나리오가 아니라 가정이다. "
        "모델은 그 가정이 깨지는 시점(중앙 3년 이내)을 이미 반영하고 있다.\n"
    )


def breakeven_section(rows: list[dict]) -> str:
    body = []
    for r in rows:
        if r["도달불가"] or r["필요값"] is None:
            body.append([r["레버"], f"{r['현재값']:g} {r['단위']}", "탐색 범위 내 도달 불가", "—", "—"])
            continue
        body.append(
            [
                r["레버"],
                f"{r['현재값']:g} {r['단위']}",
                f"{r['필요값']:,.2f} {r['단위']}" if r["단위"] != "명" else f"{r['필요값']:,.0f} {r['단위']}",
                f"×{r['배율']:.2f}" if r["배율"] else "—",
                pct(r["달성확률"]),
            ]
        )
    return (
        "## 8. 역산: 무엇이 참이어야 '7년 완제 반반'이 되는가\n\n"
        "레버를 하나씩만 움직여 7년 완제 확률이 50%가 되는 지점을 찾았다. "
        "다른 조건은 기준값 그대로다.\n\n"
        + table(["레버", "현재 가정", "필요 수준", "배율", "그때 확률"], body)
        + "\n"
    )


def career_section(c: dict, p: ModelParams) -> str:
    rows = [
        [
            "월 세후 (1인, 병원 영업 중)",
            fmt_man(c["EM_1인_월세후"]),
            f"{fmt_man(c['부부_세후월_영업중_중앙'] / 2)} (p10 {fmt_man(c['부부_세후월_영업중_p10'] / 2)} ~ p90 {fmt_man(c['부부_세후월_영업중_p90'] / 2)})",
        ],
        [
            "월 세후 (1인, 10년 평균·폐업 후 봉직 복귀 포함)",
            fmt_man(c["EM_1인_월세후"]),
            f"{fmt_man(c['딜_1인_월세후_중앙'])} (p10 {fmt_man(c['딜_1인_월세후_p10'])} ~ p90 {fmt_man(c['딜_1인_월세후_p90'])})",
        ],
        ["월 근무시간", f"{p.career.em_hours_per_month:.0f}h", f"{p.career.deal_hours_per_month:.0f}h"],
        ["시간당 세후", f"{c['EM_1인_시간당']:.1f}만/h", f"{c['딜_1인_시간당_중앙']:.1f}만/h"],
        ["10년 PV (1인)", fmt_eok(c["EM_1인_10년PV"]), "—"],
        ["10년 PV (2인 합산)", fmt_eok(c["EM_2인_10년PV"]), f"{fmt_eok(c['딜_2인_10년PV_중앙'])} (p10 {fmt_eok(c['딜_2인_10년PV_p10'])} ~ p90 {fmt_eok(c['딜_2인_10년PV_p90'])})"],
    ]
    t = table(["항목", "응급의학 잔류 (D-N-Off×4)", "이 딜"], rows)
    return (
        "## 10. 대안과의 비교\n\n"
        + t
        + f"\n\n- 딜의 시간당 단가는 응급의학(D-N-Off×4)의 **{c['시간당_배율_중앙(딜/EM)']:.2f}배**\n"
        f"- 부부의 진짜 대안(미용 봉직의 2인, 1인 세후 {fmt_man(p.career.fallback_net_monthly_per_person)}) "
        f"10년 PV: {fmt_eok(c['부부_봉직대안_2인_10년PV'])}\n"
        f"- **P(딜 10년 PV > 부부가 그냥 봉직의로 일했을 때) = {pct(c['P(딜PV > 부부 봉직대안)'])}**\n"
        f"- P(딜 10년 PV > 부부가 각자 EM급으로 벌었을 때) = {pct(c['P(딜PV > EM 2인PV)'])}\n"
        f"- **P(딜 10년 PV < 0, 즉 투입 10억도 못 건짐) = {pct(c['P(딜PV < 0)'])}**\n"
    )
