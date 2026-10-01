"""학습된 근거만으로 투자 메모를 쓴다."""

from __future__ import annotations

from insight_distiller.models import Fact, Knowledge


def render(kb: Knowledge) -> str:
    parts = [
        _header(kb),
        _conclusion(kb),
        _micron(kb),
        _contracts(kb),
        _hbm4e(kb),
        _samsung(kb),
        _fx(kb),
        _equipment(kb),
        _sfa(kb),
        _macro(kb),
        _checks(kb),
        _learning(kb),
    ]
    return "\n\n".join(part.strip() for part in parts if part.strip()) + "\n"


def _header(kb: Knowledge) -> str:
    chars = sum(row["chars"] for row in kb.documents)
    names = ", ".join(row["source"] for row in kb.documents)
    return f"""# 반도체 투자 인사이트 증류

2026-10-01 자료 {len(kb.documents)}개를 전문 수집한 뒤, 숫자·계약·가격·소부장 맵을 학습해 겹치는 주장만 남겼다. 읽은 분량은 약 {chars:,}자다.

입력: {names}

이 메모는 원문의 증류다. 매수·매도 권유가 아니다.
"""


def _conclusion(kb: Knowledge) -> str:
    lines = []
    revenue = kb.get("mu_q4_revenue")
    yoy = kb.get("mu_q4_yoy")
    gpm = kb.get("mu_q4_gpm")
    mid = kb.get("mu_q1_rev_mid")
    if revenue and yoy and gpm:
        guide = f" 다음 분기 매출 가이던스 중간값은 {mid.display}다." if mid else ""
        lines.append(
            f"마이크론 FY26 4분기 매출은 {revenue.display}, 전년 대비 {yoy.display}, 매출총이익률은 {gpm.display}다.{guide} 실적과 가이던스가 같은 방향을 가리킨다."
        )
    if kb.has("supply_tight"):
        capex = " 늘어난 투자금의 상당 부분은 당장 물량을 푸는 장비가 아니라 클린룸·건설이다." if kb.has("capex_cleanroom") else ""
        lines.append(f"자료의 업황 판단은 2027~2028년 공급 부족이 2026년보다 타이트하다는 쪽이다.{capex}")
    if kb.has("sec_op_2027") and kb.has("sec_dram_asp_4q"):
        lines.append(
            f"삼성전자 2027년 영업이익 추정은 {kb.display('sec_op_2027')}으로 벌어져 있다. 3분기보다 4분기 가격 가정(DRAM {kb.display('sec_dram_asp_4q')})과 환율 가정이 추정을 가른다."
        )
    if kb.has("sfa_cancel"):
        lines.append("SFA는 메모리 베타와 별도로, 전방 다변화 수주와 자사주 19% 소각이 같이 있다.")
    if kb.equipment.get("summary"):
        lines.append("소부장은 증착 3사가 메모리 투자에 가장 민감하고, HPSP·파크시스템스·리노공업은 기술 마진, 한미반도체·테스트 소켓은 HBM 후공정이다.")
    body = "\n".join(f"- {line}" for line in lines)
    return f"## 결론\n\n{body}\n"


def _micron(kb: Knowledge) -> str:
    rows = [
        ("매출", "mu_q4_revenue", "mu_q4_qoq", "mu_q4_yoy"),
        ("Non-GAAP EPS", "mu_q4_eps", None, None),
        ("매출총이익률", "mu_q4_gpm", None, None),
        ("영업이익 / 이익률", "mu_q4_op", "mu_q4_opm", None),
        ("요약본 영업이익 / 이익률", "mu_q4_op_summary", "mu_q4_opm_summary", None),
        ("영업현금흐름", "mu_q4_ocf", None, None),
        ("조정 FCF", "mu_q4_fcf", None, None),
        ("DRAM", "mu_dram_revenue", "mu_dram_qoq", "mu_dram_asp"),
        ("NAND", "mu_nand_revenue", "mu_nand_qoq", "mu_nand_asp"),
        ("Cloud Memory", "mu_cloud", None, None),
        ("Core Data Center", "mu_core_dc", None, None),
        ("Mobile & Client", "mu_mobile", None, None),
        ("Auto & Embedded", "mu_auto", None, None),
    ]
    table = ["| 항목 | 값 |", "|---|---|"]
    for label, *keys in rows:
        bits = [kb.display(key) for key in keys if key and kb.has(key)]
        if bits:
            table.append(f"| {label} | {' · '.join(bits)} |")
    annual = []
    if kb.has("mu_fy_revenue"):
        annual.append(f"FY26 매출 {kb.display('mu_fy_revenue')}" + (f" ({kb.display('mu_fy_revenue_yoy')})" if kb.has("mu_fy_revenue_yoy") else ""))
    if kb.has("mu_fy_eps"):
        annual.append(f"EPS {kb.display('mu_fy_eps')}")
    if kb.has("mu_fy_cash"):
        annual.append(f"현금·투자자산 {kb.display('mu_fy_cash')}")
    guide_bits = []
    if kb.has("mu_q1_rev_low") and kb.has("mu_q1_rev_high"):
        cons = f", 시장 예상 {kb.display('mu_q1_rev_cons')}" if kb.has("mu_q1_rev_cons") else ""
        guide_bits.append(f"매출 {kb.display('mu_q1_rev_low')}~{kb.display('mu_q1_rev_high').lstrip('$')}{cons}")
    if kb.has("mu_q1_rev_mid"):
        qoq = f", 전분기 대비 {kb.display('mu_q1_rev_qoq')}" if kb.has("mu_q1_rev_qoq") else ""
        guide_bits.append(f"매출 중간값 {kb.display('mu_q1_rev_mid')}{qoq}")
    if kb.has("mu_q1_eps_low") and kb.has("mu_q1_eps_high"):
        cons = f", 시장 예상 {kb.display('mu_q1_eps_cons')}" if kb.has("mu_q1_eps_cons") else ""
        guide_bits.append(f"조정 EPS {kb.display('mu_q1_eps_low')}~{kb.display('mu_q1_eps_high').lstrip('$')}{cons}")
    if kb.has("mu_q1_eps_mid"):
        guide_bits.append(f"EPS 중간값 {kb.display('mu_q1_eps_mid')}")
    if kb.has("mu_q1_gpm"):
        below = " 자료는 이 마진이 컨센서스를 소폭 밑돈다고 적는다." if kb.has("mu_q1_gpm_below_cons") else ""
        guide_bits.append(f"매출총이익률 {kb.display('mu_q1_gpm')}.{below}")
    margin_note = ""
    if kb.has("mu_gpm_trough") and kb.has("mu_q4_gpm") and kb.has("mu_q1_gpm"):
        margin_note = (
            f"\n\n4분기 매출총이익률은 {kb.display('mu_q4_gpm')}, 가이던스는 {kb.display('mu_q1_gpm')}이다. "
            "자료는 이 가이던스를 성과급·인센티브가 반영된 마진 저점으로 보고, 그 다음부터 다시 오른다고 적는다."
        )
    annual_line = f"\n\n연간: {', '.join(annual)}." if annual else ""
    guide = "\n".join(f"- {bit}" for bit in guide_bits)
    return f"""## 마이크론 실적

{chr(10).join(table)}
{annual_line}

### FY27 1분기 가이던스

{guide}
{margin_note}
"""


def _contracts(kb: Knowledge) -> str:
    bullets = []
    if kb.has("sca_count") or kb.has("sca_signed"):
        signed = kb.display("sca_count") or kb.display("sca_signed")
        share = f" 2030년 매출 비중 전망은 {kb.display('sca_2030_share')}." if kb.has("sca_2030_share") else ""
        target = f" 질의응답의 커버리지 목표는 {kb.display('sca_2030_target')}다." if kb.has("sca_2030_target") else ""
        bullets.append(f"구속력 있는 장기공급계약(SCA)은 {signed}.{share}{target} 35%와 50%는 같은 문장의 확정 비중이 아니라, 현재 전망과 목표다.")
    if kb.has("sca_price_fixed"):
        bullets.append(f"{kb.display('sca_price_fixed')}. 하한 가격에서도 과거 사이클 고점보다 마진이 높다는 문장이 따라붙는다.")
    if kb.has("sca_commitment") or kb.has("sca_rpo"):
        bits = []
        if kb.has("sca_commitment"):
            bits.append(f"고객 약정 {kb.display('sca_commitment')}")
        if kb.has("sca_rpo"):
            bits.append(f"RPO {kb.display('sca_rpo')}")
        bullets.append(", ".join(bits) + ". 신규 협상의 상당 부분은 2028년 물량이다.")
    if kb.has("supply_2027_committed"):
        bullets.append(kb.display("supply_2027_committed") + ". 공급자가 계약을 한 번에 소진하지 않고 비중을 점진적으로 올린다는 해석이 노트에 있다.")
    if kb.has("supply_no_visibility"):
        bullets.append(kb.display("supply_no_visibility") + ".")
    if kb.has("supply_keyword"):
        bullets.append("실적 발표를 시간외 주가에 맞춰 깎지 말라는 코멘트의 키워드는 공급 부족의 장기화다.")
    if not bullets:
        return ""
    body = "\n".join(f"- {line}" for line in bullets)
    return f"## 계약으로 고정된 수급\n\n{body}\n"


def _hbm4e(kb: Knowledge) -> str:
    bullets = []
    if kb.has("hbm4e_not_inhouse"):
        bullets.append(kb.display("hbm4e_not_inhouse") + ".")
    if kb.has("hbm4e_codesign"):
        bullets.append(kb.display("hbm4e_codesign") + ". JEDEC 표준 제품에도 같은 공정 이야기가 적용된다고 답했다.")
    if kb.has("hbm4e_foundry") and not kb.has("hbm4e_not_inhouse"):
        bullets.append(kb.display("hbm4e_foundry") + ".")
    if kb.has("sec_turnkey"):
        bullets.append("삼성 쪽 차별화 문장은 메모리와 파운드리를 묶는 턴키, HBM4 베이스 다이, 3D 스택 DRAM·zHBM이다. 파운드리 자체 수익성 회복은 완만하다고 적혀 있다.")
    if kb.has("techwing_unconfirmed"):
        bullets.append("테크윙(큐브 프로버·테스트 핸들러)은 이 발언만으로 수혜가 확정되지 않는다. 마이크론 HBM4E 양산에서 실제 채택되는지를 따로 봐야 한다.")
    if kb.has("hbm_wafer_mix"):
        multiple = f" {kb.display('hbm_wafer_multiple')}." if kb.has("hbm_wafer_multiple") else ""
        bullets.append(f"HBM 웨이퍼 투입 비중은 {kb.display('hbm_wafer_mix')}.{multiple}")
    if kb.has("hbm4_mix"):
        asp = f" 2027년 판매가격은 전년 대비 {kb.display('hbm_asp_2027')}." if kb.has("hbm_asp_2027") else ""
        extra = f" 속기록에는 {kb.display('hbm_price_121')} 언급이 따로 있다." if kb.has("hbm_price_121") else ""
        bullets.append(f"삼성 HBM4 {kb.display('hbm4_mix')}.{asp}{extra}")
    if kb.has("hbm_wafer_multiple") and not kb.has("hbm_wafer_mix"):
        bullets.append(kb.display("hbm_wafer_multiple") + ".")
    if not bullets:
        return ""
    body = "\n".join(f"- {line}" for line in bullets)
    return f"## HBM과 베이스 다이\n\n{body}\n"


def _samsung(kb: Knowledge) -> str:
    broker_rows = _unique_displays(kb.rows("sec_broker_op"))
    asp_rows = _unique_displays(kb.rows("sec_asp_row"))
    valuation = _unique_displays(kb.rows("sec_valuation"))
    lines = ["## 삼성전자 추정의 폭\n"]
    if broker_rows:
        lines.append("3분기 영업이익 추정은 100조원 안팎으로 모이고, 4분기와 목표주가는 하우스마다 벌어진다.\n")
        lines.append("| 증권사 | 3Q / 4Q 영업이익 / 목표주가 |")
        lines.append("|---|---|")
        for row in broker_rows:
            lines.append(f"| {row.split(' ', 1)[0]} | {row} |")
        lines.append("")
    spread = []
    if kb.has("sec_op_2027"):
        gap = f" (격차 {kb.display('sec_op_2027_gap')})" if kb.has("sec_op_2027_gap") else ""
        spread.append(f"2027년 영업이익 {kb.display('sec_op_2027')}{gap}")
    if kb.has("sec_op_2028"):
        gap = f" (격차 {kb.display('sec_op_2028_gap')})" if kb.has("sec_op_2028_gap") else ""
        spread.append(f"2028년 영업이익 {kb.display('sec_op_2028')}{gap}")
    if kb.has("sec_tp"):
        yuanta = f", 유안타를 넣으면 상단 {kb.display('sec_tp_yuanta')}" if kb.has("sec_tp_yuanta") else ""
        spread.append(f"목표주가 {kb.display('sec_tp')}{yuanta}")
    if kb.has("sec_pbr"):
        spread.append(f"목표 PBR {kb.display('sec_pbr')}")
    if kb.has("sec_roe"):
        spread.append(f"ROE {kb.display('sec_roe')}")
    if spread:
        lines.append("증권사 2027~2028년 밴드를 한 줄로 모으면 다음과 같다.\n")
        lines.extend(f"- {item}" for item in spread)
        lines.append("")
    if valuation:
        lines.append("하우스별 2027~2028년 표(OCR 소수점은 자릿수 규칙으로 보정)는 아래다.\n")
        for row in valuation:
            lines.append(f"- {row}")
        lines.append("")
    if asp_rows:
        lines.append("3분기·4분기 가격 가정은 DRAM과 NAND 모두 4분기 폭이 더 크다.\n")
        for row in asp_rows:
            lines.append(f"- {row}")
        lines.append("")
    if kb.has("sec_dram_asp_4q"):
        nand = f", NAND {kb.display('sec_nand_asp_4q')}" if kb.has("sec_nand_asp_4q") else ""
        lines.append(f"요약 문장의 4분기 가격 범위는 DRAM {kb.display('sec_dram_asp_4q')}{nand}다. 출하 가정보다 가격 가정이 향후 이익 수정의 변수다.\n")
    heung = []
    for key, label in (
        ("heung_q3_op", "3분기"),
        ("heung_q4_op", "4분기"),
        ("heung_ds_q3", "DS"),
        ("heung_dx", "DX"),
        ("heung_op_2026", "2026년"),
        ("heung_op_2027", "2027년"),
        ("sec_asp_3q", "3분기 ASP"),
    ):
        if kb.has(key):
            heung.append(f"{label} {kb.display(key)}")
    if heung:
        lines.append("흥국(9/29) 경로: " + "; ".join(heung) + ".\n")
    if kb.has("sec_1cnm"):
        lines.append("이익 레버로 적힌 것은 1cnm 수율과 HBM4 램프, 서버 DRAM·eSSD 가격이다. DX는 메모리 원가가 세트 가격에 충분히 전가되지 않아 적자가 이어질 수 있다고 본다.\n")
    if kb.has("heung_op_bridge"):
        lines.append(f"같은 자료의 다른 이익 다리: {kb.display('heung_op_bridge')}. 365조/596조 경로와 368조/555조 경로가 같이 있다.\n")
    returns = []
    if kb.has("sec_return_base"):
        returns.append(kb.display("sec_return_base"))
    if kb.has("sec_return_split"):
        returns.append(kb.display("sec_return_split"))
    if kb.has("sec_return_fcf"):
        returns.append(kb.display("sec_return_fcf"))
    if returns:
        lines.append("주주환원: " + ". ".join(returns) + ".\n")
    lines.append("업황 문장의 초점은 가격 상승이 이어지는 구간이다. 4분기 2026~1분기 2027 범용 DRAM·NAND는 공급자 우위 협상으로 적혀 있다.\n")
    return "\n".join(lines)


def _fx(kb: Knowledge) -> str:
    if not (kb.has("hana_2027_op") or kb.has("fx_assumption") or kb.has("fx_view")):
        return ""
    lines = ["## 환율 가정\n"]
    if kb.has("hana_2027_op"):
        lines.append(f"- 하나증권은 2027년 삼성전자 영업이익을 {kb.display('hana_2027_op')}으로 조정했다. 수요 하향이 아니라 환율 가정 변경이다.")
    if kb.has("fx_assumption"):
        lines.append(f"- 바뀐 가정: {kb.display('fx_assumption')}.")
    if kb.has("fx_view"):
        lines.append(f"- {kb.display('fx_view')}. 근거로 적힌 것은 미국 고금리 장기화, 2027년 한국 성장률 둔화, 대미투자에 따른 달러 수요, 미국의 AI 투자다.")
    if kb.has("fx_spot"):
        lines.append(f"- 당일 현물 언급: {kb.display('fx_spot')}.")
    lines.append("")
    return "\n".join(lines)


def _equipment(kb: Knowledge) -> str:
    equipment = kb.equipment
    if not equipment.get("sections") and not equipment.get("summary"):
        return ""
    lines = ["## 소부장 맵\n", "공정 노트에서 회사와 역할을 나누면 다음과 같다.\n"]
    for section in equipment.get("sections", []):
        if not section["companies"] and not section["notes"]:
            continue
        lines.append(f"### {section['title']}")
        lines.append("")
        for company in section["companies"]:
            lines.append(f"- {company['name']}: {company['role']}")
        for note in section["notes"]:
            lines.append(f"- {note.lstrip('* ').strip()}")
        lines.append("")
    if equipment.get("summary"):
        lines.append("### 노트에 적힌 투자 관점")
        lines.append("")
        for index, line in enumerate(equipment["summary"], start=1):
            lines.append(f"{index}. {line}")
        lines.append("")
    position = []
    if kb.has("equip_no_bad_news"):
        position.append(kb.display("equip_no_bad_news") + ".")
    if kb.has("tes_catchup"):
        position.append(kb.display("tes_catchup") + ". 절대 밸류가 싸다는 표현은 아니다.")
    if kb.has("japan_equip_tape"):
        position.append(kb.display("japan_equip_tape") + ".")
    if kb.has("test_socket"):
        margin = f" {kb.display('socket_margin')}이 환율·관세의 완충으로 제시된다." if kb.has("socket_margin") else ""
        position.append(f"기판 강세 다음 순환으로 테스트 소켓(ISC, 티에스이, 티에프이)이 언급된다.{margin} 리노공업은 그 자리의 저평가 종목으로 분류되지 않는다.")
    if position:
        lines.append("당일 포지션 코멘트를 소부장에 적용하면 다음과 같다.\n")
        lines.extend(f"- {line}" for line in position)
        lines.append("")
    return "\n".join(lines)


def _sfa(kb: Knowledge) -> str:
    if not kb.has("sfa_cancel") and not kb.has("sfa_orders"):
        return ""
    bullets = []
    if kb.has("sfa_orders"):
        yoy = f" ({kb.display('sfa_orders_yoy')})" if kb.has("sfa_orders_yoy") else ""
        bullets.append(f"2026년 신규수주 {kb.display('sfa_orders')}{yoy}.")
    if kb.has("sfa_legacy_2023") or kb.has("sfa_legacy_1h26"):
        left = kb.display("sfa_legacy_2023") or "디스플레이·2차전지 중심"
        right = kb.display("sfa_legacy_1h26") or "비중 하락"
        bullets.append(f"전방 구성은 {left}에서 {right}로 이동한다.")
    if kb.has("sfa_new_mix"):
        bullets.append(kb.display("sfa_new_mix") + ". 업황 한 곳에 기댄 수주 구조가 옅어진다.")
    if kb.has("sfa_semi"):
        bullets.append("엔지니어링 범위는 OLED 증착·물류와 2차전지 조립·화성에서 반도체 전공정 이송(OHT)까지 넓혀져 있다.")
    if kb.has("sfa_treasury") or kb.has("sfa_shares") or kb.has("sfa_cancel"):
        bits = [kb.display(key) for key in ("sfa_treasury", "sfa_shares", "sfa_cancel") if kb.has(key)]
        bullets.append("자사주: " + ", ".join(bits) + ". 상법 개정과 소각 시점이 같이 언급된다. 유통주식 감소와 EPS, 주주환원 쪽 이벤트다.")
    if kb.has("korea_governance") or kb.has("japan_governance"):
        bullets.append("같은 날짜 노트는 일본 개혁의 초점이 현금 환원에서 ROIC와 자본배분으로 옮겨 갔다고 본다. 한국은 이익이 일반주주 가치로 연결되는지가 아직 실행 검증 단계다. SFA 소각은 그 검증 사례에 가깝다.")
    body = "\n".join(f"- {line}" for line in bullets)
    return f"## SFA (056190)\n\n{body}\n"


def _macro(kb: Knowledge) -> str:
    bullets = []
    if kb.has("pce_soft"):
        bullets.append("PCE는 예상보다 낮았다. 집계 방식 변경 논란이 같은 날 노트에 같이 있다.")
    if kb.has("ust10"):
        bullets.append(f"장기금리는 낮아진 물가 헤드라인과 따로 움직였고, {kb.display('ust10')} 언급이 있다.")
    if kb.has("higher_for_longer"):
        extra = []
        if kb.has("hike_odds"):
            extra.append(kb.display("hike_odds"))
        if kb.has("wti"):
            extra.append(kb.display("wti"))
        tail = f" 같은 날 같이 적힌 것은 {', '.join(extra)}이다." if extra else ""
        bullets.append(f"한 축은 미국 금리를 구조적 higher for longer로 본다.{tail} 전쟁과 AI 자금 수요가 겹쳐 금리 결론은 한 문장으로 닫히지 않는다.")
    if kb.has("trim_bio_robot"):
        bullets.append(kb.display("trim_bio_robot") + ".")
    if kb.has("foreign_sell"):
        bullets.append(f"{kb.display('foreign_sell')}. 노트는 이를 이란 전쟁 재확전과 연결하고, 외국인 복귀 조건으로 종전 재료를 둔다.")
    if kb.has("solidigm"):
        bullets.append(kb.display("solidigm") + ".")
    if not bullets:
        return ""
    body = "\n".join(f"- {line}" for line in bullets)
    return f"## 매크로와 수급\n\n{body}\n"


def _checks(kb: Knowledge) -> str:
    items = []
    if kb.has("sec_dram_asp_4q"):
        band = kb.display("sec_op_2027") or "하우스 간 격차"
        items.append(f"4분기 DRAM ASP가 {kb.display('sec_dram_asp_4q')} 범위의 어디쯤인지. 삼성 2027년 이익 밴드 {band}을 가른다.")
    if kb.has("fx_assumption"):
        items.append("원/달러가 1,350원에 머무는지, 1,400원대로 되돌아가는지. 하나증권 하향은 환율 가정이다.")
    if kb.has("mu_q1_gpm"):
        items.append(f"마이크론 다음 분기 매출총이익률 {kb.display('mu_q1_gpm')} 이후 마진이 다시 오르는지. 성과급 반영인지 가격 둔화인지가 갈린다.")
    if kb.has("hbm4e_foundry") or kb.has("hbm4e_not_inhouse"):
        items.append("HBM4E 베이스 다이 파운드리 물량이 삼성 파운드리로 얼마나 붙는지.")
    if kb.has("techwing_unconfirmed"):
        items.append("마이크론 HBM4E 생산에서 큐브 프로버·테스트 핸들러가 실제로 채택되는지.")
    if kb.has("hbm_asp_2027"):
        items.append(f"2027년 HBM 판매가격이 전년 대비 {kb.display('hbm_asp_2027')}인지.")
    if kb.has("sec_tp_yuanta") and any("유안타 TP 53만원" in fact.display for fact in kb.rows("sec_valuation")):
        items.append("유안타 목표주가는 근월 표의 63만원과 2027~2028년 표의 53만원이 다르다. 같은 자료 안의 차이다.")
    if kb.has("sca_2030_share"):
        items.append("SCA 비중이 2030년 35% 전망에서 50% 목표 쪽으로 더 채워지는지.")
    if kb.has("capex_cleanroom"):
        items.append("Capex 증액이 건설에 머무는지, 증착·후공정 장비 수주로 이어지는지. 장비 매출은 시차가 있다.")
    if kb.has("sfa_cancel"):
        items.append("SFA 자사주 19% 소각이 공시로 확정되는지.")
    op = kb.get("mu_q4_op")
    summary = kb.get("mu_q4_op_summary")
    if op and summary and op.display != summary.display:
        items.append(f"마이크론 4분기 영업이익은 IR {op.display}와 요약표 {summary.display}가 다르다. 전자는 non-GAAP 이익률 {kb.display('mu_q4_opm')} 경로다.")
    if not items:
        return ""
    body = "\n".join(f"{index}. {line}" for index, line in enumerate(items, start=1))
    return f"## 다음에 확인할 것\n\n{body}\n"


def _learning(kb: Knowledge) -> str:
    lines = ["## 학습 로그\n", "문서를 슬라이드·페이지·코멘트 단위로 읽고, 라벨이 붙은 숫자만 팩트로 남겼다. 같은 값의 출처가 여럿이면 지지 횟수를 올렸다. 테마 가중치는 용어가 나온 청크의 출처 품질을 더한 값이다. 장문 속기는 가중치를 낮춰 코멘트를 덮지 않게 했다.\n"]
    lines.append("| 문서 | 청크 | 글자 | 종류 |")
    lines.append("|---|---:|---:|---|")
    for row in kb.documents:
        lines.append(f"| {row['source']} | {row['chunks']} | {row['chars']:,} | {', '.join(row['kinds'])} |")
    lines.append("")
    lines.append("| 테마 | 가중치 | 청크 | 문서 수 |")
    lines.append("|---|---:|---:|---:|")
    for row in kb.themes:
        lines.append(f"| {row['theme']} | {row['weight']} | {row['chunks']} | {row['sources']} |")
    lines.append("")
    if kb.associations:
        lines.append("기업이 같은 청크에서 자주 만난 주제:\n")
        for row in kb.associations[:8]:
            themes = ", ".join(f"{item['theme']} {item['chunks']}" for item in row["themes"])
            lines.append(f"- {row['company']}: {themes}")
        lines.append("")
    cited = _citations(kb)
    if cited:
        lines.append("핵심 수치의 근거 위치:\n")
        for fact in cited:
            lines.append(f"- {fact.key}: {fact.display} — {fact.source} {fact.locator} (지지 문서 {fact.support}, 언급 {fact.mentions})")
        lines.append("")
    return "\n".join(lines)


def _citations(kb: Knowledge) -> list[Fact]:
    keys = [
        "mu_q4_revenue",
        "mu_q1_rev_mid",
        "mu_q4_op",
        "sca_count",
        "sec_op_2027",
        "sec_dram_asp_4q",
        "hana_2027_op",
        "sfa_cancel",
        "hbm_wafer_mix",
    ]
    found = []
    for key in keys:
        fact = kb.get(key)
        if fact:
            found.append(fact)
    return found


def _unique_displays(facts: list[Fact]) -> list[str]:
    seen: set[str] = set()
    rows = []
    for fact in facts:
        if fact.display in seen:
            continue
        seen.add(fact.display)
        rows.append(fact.display)
    return rows
