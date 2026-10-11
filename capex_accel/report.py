"""Korean verification note. Numbers come from the computed result dict."""

from __future__ import annotations

from datetime import date


def _b(value: float | None, digits: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{digits}f}"


def _eok(billions: float | None, digits: int = 0) -> str:
    """USD billions to 억 or 조 달러. 1 billion USD = 10억 달러."""
    if billions is None:
        return "—"
    if abs(billions) >= 1000:
        return f"{billions / 1000:.2f}조 달러"
    eok = billions * 10
    if digits == 0:
        return f"{eok:,.0f}억 달러"
    return f"{eok:,.{digits}f}억 달러"


def _pct(value: float | None, digits: int = 0) -> str:
    if value is None:
        return "—"
    return f"{value * 100:.{digits}f}%"


def _q(d: date) -> str:
    return f"{d.year} Q{(d.month - 1) // 3 + 1}"


def render(result: dict) -> str:
    f = result["frame_rows"]
    latest = result["latest"]
    th = result["thresholds"]
    parts = result["parts"]
    peaks = result["growth_peaks"]
    leads = result["leads"]
    shares = result["shares"]
    scenarios = result["scenario_totals"]
    corr = result["corr_summary"]

    def row(qe: str) -> dict:
        return next(item for item in f if item["quarter"] == qe)

    q1 = row("2026-03-31")
    q2 = row("2026-06-30")
    lines = []
    a = lines.append
    a("# 하이퍼스케일러 현금 CapEx 가속도 검증")
    a("")
    a(f"기준일: 현금 CapEx는 2026년 2분기 공시까지, 주가는 {result['price_end']}까지.")
    a("대상: 마이크로소프트, 알파벳, 아마존, 메타의 현금 유형자산 취득액 합계. 비현금 리스 취득액은 빼 두었습니다.")
    a("")
    a("## 결론")
    a("")
    a(
        f"공시로 확인되는 가속도 `A_q`는 2026년 2분기에 표본 최대인 **{_b(q2['acceleration'])}** 입니다. "
        f"1분기 {_b(q1['acceleration'])}에서 아직 올라가는 중입니다. "
        "2026년 2~3분기를 고점으로 보는 판단은 3분기 집행이 2분기 가속도를 넘지 않을 때의 조건부 추정입니다."
    )
    a("")
    a(
        f"3분기 4사 현금 CapEx가 **{_eok(th['new_high'])}**를 넘으면 2분기보다 높은 가속도가 나옵니다. "
        f"**{_eok(th['stay_positive'])}**를 밑돌면 가속도 자체가 음수로 돌아섭니다. "
        f"그 사이면 가속도는 양수이지만 2분기가 고점으로 남습니다."
    )
    a("")
    a(
        "주가 고점의 시차는 종목마다 다릅니다. 메모리(삼성전자, SK하이닉스, Micron)와 SOX, Broadcom은 "
        "2026년 6월에 고점을 찍고 조정에 들어갔습니다. 시차는 2분기 말 대비 약 0개월입니다. "
        "NVDA와 TSMC는 2026년 10월 첫 주에 신고가입니다. "
        "메모리 상승분의 대부분은 2025년까지가 아니라 2026년 상반기에 가격에 들어갔습니다."
    )
    a("")
    a("## 지표")
    a("")
    a("최근 4분기 합계를 `T_q`라고 하면")
    a("")
    a("- 증가액 `D_q = T_q - T_{q-1} = c_q - c_{q-4}`")
    a("- 가속도 `A_q = D_q - D_{q-1}`")
    a("")
    a("`A_q`가 음수라는 것은 전년보다 더 쓰는 금액이 줄어든다는 뜻입니다. 투자액 자체가 줄어든다는 뜻이 아닙니다.")
    a("")
    a("## 2026년 상반기 공시")
    a("")
    a("아래 표의 단위는 십억 달러입니다. 165.1은 1,651억 달러입니다.")
    a("")
    a("| 분기 | MSFT | Alphabet | Amazon | Meta | 합계 | TTM | 증가액 D | 가속도 A | TTM 증가율 |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for qe in ("2025-03-31", "2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31", "2026-06-30"):
        item = row(qe)
        p = parts[qe]
        a(
            f"| {_q(date.fromisoformat(qe))} | {_b(p['MSFT'])} | {_b(p['GOOGL'])} | {_b(p['AMZN'])} | {_b(p['META'])} "
            f"| {_b(item['c'])} | {_b(item['ttm'])} | {_b(item['increment'])} | {_b(item['acceleration'])} "
            f"| {_pct(item['ttm_yoy'])} |"
        )
    a("")
    a(
        f"2026년 1분기 합계 {_b(q1['c'], 2)}, 2분기 합계 {_b(q2['c'], 2)}. "
        f"가속도는 {_b(q1['acceleration'], 2)}, {_b(q2['acceleration'], 2)}입니다. "
        "이전에 적었던 1,298억, 1,651억, 11.6, 19와 반올림 범위에서 같습니다."
    )
    a("")
    a(
        f"마이크로소프트 FY2026(2025년 7월~2026년 6월) 현금 CapEx 합계는 **{_eok(result['msft_fy2026'], 1)}**이며, "
        "10-K의 additions to property and equipment와 일치합니다."
    )
    a("")
    a("## 고점 분기는 연간 총액만으로 정해지지 않습니다")
    a("")
    a(
        f"기본 경로(2026년 4사 현금 6,800억 달러, 2027년 1.02조 달러)를 분기에 풀어 쓰면 "
        f"2026년 3분기 약 {_eok(scenarios['base_q3'])}, 4분기 약 {_eok(scenarios['base_q4'])}입니다. "
        f"이 경로는 3분기가 {_eok(th['new_high'])} 아래라서 계산상 고점이 2분기에 남고, "
        f"2027년 합계는 {_eok(scenarios['base_2027'])}입니다."
    )
    a("")
    a(
        "같은 6,800억 달러라도 3분기에 집행이 몰리면 고점 분기가 바뀝니다. "
        f"3분기가 {_eok(th['new_high'])}를 넘고 4분기가 그만큼 작아도 연간 총액은 6,800억 달러일 수 있습니다."
    )
    a("")
    a("| 확인할 공시 | 기준 | 의미 |")
    a("|---|---:|---|")
    a(f"| 2026년 3분기 4사 현금 PP&E | {_eok(th['stay_positive'])} 미만 | 가속도가 음수로 전환. 2분기가 고점 |")
    a(f"| 2026년 3분기 4사 현금 PP&E | {_eok(th['stay_positive'])} ~ {_eok(th['new_high'])} | 가속도는 양수, 그러나 2분기보다 낮음 |")
    a(f"| 2026년 3분기 4사 현금 PP&E | {_eok(th['new_high'])} 초과 | 2분기보다 높은 가속도 |")
    a(
        f"| 2027년 1분기 | 4분기 집행액에 의존 | 4분기를 {_eok(result['q4_assumption'])}로 두면 "
        f"**{_eok(result['q1_2027_threshold'])}** 초과 시 2026년 2분기를 넘는 새 고점 |"
    )
    a("")
    a(
        f"재가속 경로(2027년 1.12조 달러, 연초 집행)의 2027년 1분기 가속도는 {_b(scenarios['reaccel_a_q1'])}로 "
        f"2026년 2분기 {_b(q2['acceleration'])}보다 큽니다. 2027년 합계는 {_eok(scenarios['reaccel_2027'])}입니다. "
        "이 분기는 가정이 조금만 바뀌어도 움직입니다."
    )
    a("")
    a("## 성장률 고점과는 다른 시계")
    a("")
    a(
        f"TTM 증가율은 2026년 2분기 **{_pct(q2['ttm_yoy'])}**까지 계속 올랐습니다. "
        f"분기 증가율은 **{_pct(q2['quarterly_yoy'])}**입니다. "
        "증가율 자체의 고점은 아직 공시에 없습니다."
    )
    a("")
    a(
        "증가율의 변화(가속도가 아니라 성장률의 1차 차분)는 2024년 3분기에 가장 컸고, "
        "2025년에는 거의 0 근처까지 둔화됐다가 2026년 상반기에 다시 커졌습니다. "
        "그 재가속은 2024년 3분기의 변화폭보다 작습니다. "
        "금액의 2차 차분 `A_q`와 성장률의 변화는 고점 시기가 다릅니다. "
        "이번 검증의 2차 미분은 금액 `C(t)`의 가속도입니다."
    )
    a("")
    a("골드만삭스 9월 공개 전망으로 인용된 8,000억 → 1.2조 → 1.4조는 오라클 등을 포함한 더 넓은 집합이고, 회계 정의도 이 4사 현금 합계와 다릅니다. ")
    a(
        f"이 4사의 2025년 현금 합계는 **{_eok(result['annual_2025'])}**입니다. "
        f"여기에 +94%를 곱하면 2026년 약 {_eok(result['gs_rate_on_four'])}이고, "
        f"상반기 {_eok(result['h1_2026'])}를 빼면 하반기 평균이 {_eok(th['new_high'])}를 넘습니다. "
        f"그 성장률을 이 4사에 그대로 적용하면 가속도 고점은 2분기가 아닙니다. "
        f"4사 현금 6,800억 달러(2025년 대비 약 {_pct(result['growth_if_680'])}) 경로에서만 2분기 고점이 기본값이 됩니다."
    )
    a("")
    a("## 과거 성장률 고점과 주가 고점")
    a("")
    a("완료된 TTM 증가율 사이클은 두 개입니다. 고점 이후 6분기 안에 증가율이 15%포인트 이상 내려간 경우만 골랐습니다.")
    a("")
    a("| 성장률 고점 | TTM 증가율 | 이후 6분기 중 저점 |")
    a("|---|---:|---:|")
    for peak in peaks:
        a(f"| {_q(date.fromisoformat(peak['quarter']))} | {_pct(peak['value'])} | {_pct(peak['trough'])} |")
    a("")
    a(
        "주가 고점은 성장률 고점 전후 약 9~12개월 안에서, 25% 하락이 나오기 직전의 고가입니다. "
        "한 번 25%가 깨진 뒤의 신고가는 다음 다리로 보고 이 사이클 고점에서 뺍니다. "
        "시차가 음수면 주가가 먼저 고점을 만들었습니다."
    )
    a("")
    a("| 사이클 | 종목 | 주가 고점 | 시차(개월) | 구간 내 최대 하락 | 판정 |")
    a("|---|---|---|---:|---:|---|")
    status_ko = {
        "drawdown_top": "25% 하락",
        "high_without_25pct": "고점은 있으나 1년 내 25% 하락 없음",
        "window_edge": "구간 안 순환 고점 없음",
        "no_price": "가격 없음",
    }
    for row_ in leads:
        if row_["cycle"].startswith("2026"):
            continue
        if row_.get("status") == "window_edge":
            a(f"| {row_['cycle']} | {row_['name']} | — | — | — | 구간 안 순환 고점 없음 |")
            continue
        lag = "—" if row_["lag_months"] is None else f"{row_['lag_months']:+.1f}"
        dd = "—" if row_["drawdown"] is None else _pct(row_["drawdown"])
        a(
            f"| {row_['cycle']} | {row_['name']} | {row_['peak_date']} | {lag} | {dd} | "
            f"{status_ko.get(row_.get('status'), row_.get('status'))} |"
        )
    a("")
    yoy = {row["quarter"]: row["ttm_yoy"] for row in f}
    a(
        f"2018년 증가율은 2분기 {_pct(yoy.get('2018-06-30'))}, 3분기 {_pct(yoy.get('2018-09-30'))}, "
        f"4분기 {_pct(yoy.get('2018-12-31'))}로 한 분기에 뾰족하지 않습니다. "
        "그 평탄 구간보다 메모리는 4~5개월 먼저 고점을 만들었고, NVDA는 3분기 말과 같은 달입니다. "
        "2021년은 갈립니다. 삼성전자와 SK하이닉스는 증가율 고점보다 4~6개월 앞섰고, "
        "NVDA, Broadcom, SOX, TSMC, Micron은 5~7개월 뒤에 고점을 만들었습니다. "
        "2018년의 SOX, Broadcom, TSMC는 그해 하락 이후 가격이 다시 전고점을 넘어서, 이 규칙에서는 그 해 고점이 잠기지 않았습니다."
    )
    a("")
    a("완료된 사이클이 두 개뿐입니다. 종목별 시차를 하나의 중위 선행개월로 줄이지 않습니다.")
    a("")
    a("## 이번 사이클, 2026년 2분기 후보 기준")
    a("")
    a("아래 시차는 2026년 6월 30일 대비입니다. 2분기가 가속도 고점이라는 전제가 3분기 공시로 깨지면 시차도 다시 재야 합니다.")
    a("")
    a("| 종목 | 2024년 이후 고점 | 10월 9일 대비 고점 낙폭 | 6월 30일 대비 시차 | 상태 |")
    a("|---|---|---:|---:|---|")
    for row_ in leads:
        if not row_["cycle"].startswith("2026"):
            continue
        lag = "—" if row_["lag_months"] is None else f"{row_['lag_months']:+.1f}개월"
        dd = "—" if row_["current_drawdown"] is None else _pct(row_["current_drawdown"])
        a(f"| {row_['name']} | {row_['peak_date']} | {dd} | {lag} | {row_['note']} |")
    a("")
    a("2023년 1월 3일부터 그 고점까지의 상승분 중, 각 시점까지 이미 반영된 비율입니다. NVDA와 TSMC의 고점은 10월 신고가라서 아직 25% 조정으로 확인된 고점이 아닙니다.")
    a("")
    a("| 종목 | 2024말 | 2025 중반 | 2025말 | 2026 1분기말 | 고점까지 배수 |")
    a("|---|---:|---:|---:|---:|---:|")
    for name, rows_ in shares.items():
        by = {row["checkpoint"]: row for row in rows_}
        def share(day: str) -> str:
            item = by.get(day)
            if item is None or item["share_of_gain"] is None:
                return "—"
            return _pct(item["share_of_gain"])
        multiple = result["multiples"][name]
        a(
            f"| {name} | {share('2024-12-31')} | {share('2025-06-30')} | {share('2025-12-31')} "
            f"| {share('2026-03-31')} | {multiple:.1f}x |"
        )
    a("")
    a(
        "Micron, SK하이닉스, 삼성전자는 2025년 말까지 사이클 상승분의 약 20%만 반영돼 있었고, "
        "나머지는 2026년 상반기 가격에 들어갔습니다. "
        "NVDA는 2025년 말 이미 약 4분의 3이 반영돼 있었고 10월에도 고점 부근입니다."
    )
    a("")
    a("## 수익률과 가속도의 시차 상관")
    a("")
    a(
        "분기 로그수익률과 `A_q`의 상관은 표본이 작고, 2026년 상반기 메모리 급등이 전체를 끌어올립니다. "
        f"2018~2023년만 보면 상관이 가장 큰 시차는 {corr['pre_ai']}. "
        f"2026년 2분기까지 넣으면 {corr['full']}. "
        "가격이 가속도를 안정적으로 몇 분기 선행한다는 상관 구조는 이 표본에서 확인되지 않습니다."
    )
    a("")
    a("## 한계")
    a("")
    a("- 4사 현금 PP&E는 골드만삭스 하이퍼스케일러 총액, 회사 가이던스 CapEx와 범위가 다릅니다. 마이크로소프트는 FY2026 현금 1,159억 달러 위에 금융리스 데이터센터 취득 246억 달러가 따로 있습니다.")
    a("- 아마존 2016~2017은 XBRL 계정 변경을 이어 붙인 값입니다. 2018년 이후, 그리고 이번 사이클 판단에는 그 이음새가 들어가지 않습니다.")
    a("- 분기 CapEx는 지급 시점에 출렁입니다. `A_q` 한 분기의 고점은 그 출렁임일 수 있어서, 3분기 한 번으로 고점을 확정하지 않는 편이 맞습니다.")
    a("- 완료된 성장률 사이클은 두 개입니다. 시차의 중위값을 다음 사이클의 예측으로 쓰면 과합니다.")
    a("- 주가는 배당을 재투자하지 않은 분할 조정 종가입니다.")
    a("")
    a("재현: `python scripts/run_capex_acceleration.py`")
    a("")
    a("![현금 CapEx와 가속도](../output/figures/capex_acceleration.png)")
    a("")
    a("![가정 경로의 가속도](../output/figures/capex_scenarios.png)")
    a("")
    a("![수혜주 주가](../output/figures/beneficiary_prices.png)")
    a("")
    a("![고점까지 상승분의 반영 비율](../output/figures/priced_in_share.png)")
    a("")
    a("![성장률 고점 대비 주가 고점 시차](../output/figures/lead_times.png)")
    a("")
    return "\n".join(lines)
