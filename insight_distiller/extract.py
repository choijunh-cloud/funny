"""라벨이 붙은 숫자와 판단 문장을 근거와 함께 뽑는다."""

from __future__ import annotations

import re

from insight_distiller.models import Chunk, Fact
from insight_distiller.textutil import (
    compact,
    money_b,
    money_b_from_eok,
    signed_pct,
    snippet,
    split_bracket_sections,
)

BROKER_ALIASES = (
    ("흥국", ("흥국", "릉국", "흠국", "층국")),
    ("DS", ("DS투자", "05투자", "DS")),
    ("유안타", ("유안타", "TESA")),
    ("키움", ("키움",)),
    ("BNK", ("BNK",)),
    ("하나", ("하나증권", "하나")),
    ("신한", ("신한",)),
    ("NH", ("NH",)),
)


def extract(chunks: list[Chunk]) -> list[Fact]:
    found: list[Fact] = []
    for chunk in chunks:
        found.extend(_from_chunk(chunk))
    return _dedupe(found)


def _dedupe(facts: list[Fact]) -> list[Fact]:
    grouped: dict[tuple[str, str], list[Fact]] = {}
    for fact in facts:
        grouped.setdefault((fact.key, fact.display), []).append(fact)
    chosen: list[Fact] = []
    for items in grouped.values():
        items.sort(key=lambda fact: fact.quality, reverse=True)
        best = items[0]
        best.support = len({item.source for item in items})
        best.mentions = len(items)
        chosen.append(best)
    return chosen


def _from_chunk(chunk: Chunk) -> list[Fact]:
    text = chunk.text
    facts: list[Fact] = []
    facts.extend(_micron(text, chunk))
    facts.extend(_samsung_ranges(text, chunk))
    facts.extend(_samsung_tables(text, chunk))
    facts.extend(_sfa(text, chunk))
    facts.extend(_flags(text, chunk))
    return facts


def _add(facts: list[Fact], chunk: Chunk, key: str, display: str, start: int, end: int) -> None:
    if not display:
        return
    facts.append(
        Fact(
            key=key,
            display=display,
            snippet=snippet(chunk.text, start, end),
            source=chunk.source,
            locator=chunk.locator,
            quality=chunk.quality,
            kind=chunk.kind,
        )
    )


def _micron(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    sections = split_bracket_sections(text)
    fq4 = sections.get("FQ4 실적", "")
    annual = sections.get("FY26 연간", "")
    product = sections.get("제품별 FQ4", "")
    segment = sections.get("사업부별 FQ4", "")
    guidance = sections.get("가이던스", "")
    sca = sections.get("SCA·RPO", "") + sections.get("SCA·RPO ", "")
    market = sections.get("시장 전망", "") + sections.get("기술·증설", "")

    match = re.search(
        r"매출\s+([\d,]+(?:\.\d+)?)억\s*달러\s*\(QoQ\s*\+?([\d.]+)%\s*,\s*YoY\s*\+?([\d.]+)%\)",
        fq4 or text,
    )
    if match and (fq4 or "379" in match.group(0)):
        _add(facts, chunk, "mu_q4_revenue", money_b_from_eok(match.group(1)), match.start(), match.end())
        _add(facts, chunk, "mu_q4_qoq", signed_pct(match.group(2)), match.start(), match.end())
        _add(facts, chunk, "mu_q4_yoy", signed_pct(match.group(3)), match.start(), match.end())

    match = re.search(r"매출\s*\$?([\d.]+)\s*B\s*\(\+?([\d.]+)%\s*QoQ,\s*\+?([\d.]+)%\s*YoY\)", text)
    if match:
        _add(facts, chunk, "mu_q4_revenue", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_q4_qoq", signed_pct(match.group(2)), match.start(), match.end())
        _add(facts, chunk, "mu_q4_yoy", signed_pct(match.group(3)), match.start(), match.end())

    match = re.search(
        r"Q4 revenue rose\s+([\d.]+)%\s+QoQ and\s+([\d.]+)%\s+YoY to a record \$?([\d.]+)\s*B",
        text,
        re.I,
    )
    if match:
        _add(facts, chunk, "mu_q4_revenue", money_b(float(match.group(3))), match.start(), match.end())
        _add(facts, chunk, "mu_q4_qoq", signed_pct(match.group(1)), match.start(), match.end())
        _add(facts, chunk, "mu_q4_yoy", signed_pct(match.group(2)), match.start(), match.end())

    for body, key in ((fq4, "mu_q4_gpm"), (text, "mu_q4_gpm")):
        match = re.search(r"매출총이익률\s+([\d.]+)%\s*\(\+?([\d.]+)bp\)", body)
        if match and (body == fq4 or "87.0" in match.group(0) or "87%" in match.group(0)):
            _add(facts, chunk, key, f"{match.group(1)}%", match.start(), match.end())
            break
    match = re.search(r"GPM\s*([\d.]+)%\s*\(\+?([\d.]+)bp", text)
    if match:
        _add(facts, chunk, "mu_q4_gpm", f"{match.group(1)}%", match.start(), match.end())
    match = re.search(r"gross margin reached\s+([\d.]+)%", text, re.I)
    if match:
        _add(facts, chunk, "mu_q4_gpm", f"{match.group(1)}%", match.start(), match.end())

    match = re.search(r"영업이익\s+([\d,]+(?:\.\d+)?)억\s*달러\s*\(이익률\s*([\d.]+)%\)", fq4 or "")
    if match:
        _add(facts, chunk, "mu_q4_op", money_b_from_eok(match.group(1)), match.start(), match.end())
        _add(facts, chunk, "mu_q4_opm", f"{match.group(2)}%", match.start(), match.end())
    match = re.search(r"OP\s*\$?([\d.]+)\s*B\s*/\s*OPM\s*([\d.]+)%", text)
    if match:
        _add(facts, chunk, "mu_q4_op", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_q4_opm", f"{match.group(2)}%", match.start(), match.end())
    match = re.search(r"Operating income jumped to \$?([\d.]+)\s*B on an\s+([\d.]+)%", text, re.I)
    if match:
        _add(facts, chunk, "mu_q4_op", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_q4_opm", f"{match.group(2)}%", match.start(), match.end())
    match = re.search(r"영업이익\s*\$?([\d.]+)\s*B[^\n]{0,40}?영업이익률\s*약\s*([\d.]+)\s*%", text)
    if match:
        _add(facts, chunk, "mu_q4_op_summary", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_q4_opm_summary", f"{match.group(2)}%", match.start(), match.end())

    match = re.search(r"EPS\s+(\d+(?:\.\d+)?)달러\s*\(QoQ", fq4 or text)
    if match:
        _add(facts, chunk, "mu_q4_eps", f"${match.group(1)}", match.start(), match.end())
    match = re.search(r"(?:Non-GAAP )?EPS\s*\$?(\d+\.\d+)", text)
    if match and match.group(1).startswith("33."):
        _add(facts, chunk, "mu_q4_eps", f"${match.group(1)}", match.start(), match.end())

    match = re.search(r"조정 FCF\s+([\d,]+(?:\.\d+)?)억\s*달러", fq4 or "")
    if match:
        _add(facts, chunk, "mu_q4_fcf", money_b_from_eok(match.group(1)), match.start(), match.end())
    match = re.search(r"FCF\s*\$?([\d.]+)\s*B", text)
    if match:
        _add(facts, chunk, "mu_q4_fcf", money_b(float(match.group(1))), match.start(), match.end())
    match = re.search(r"adjusted FCF rose to \$?([\d.]+)\s*B", text, re.I)
    if match:
        _add(facts, chunk, "mu_q4_fcf", money_b(float(match.group(1))), match.start(), match.end())

    match = re.search(r"영업현금흐름\s+([\d,]+(?:\.\d+)?)억", fq4 or "")
    if match:
        _add(facts, chunk, "mu_q4_ocf", money_b_from_eok(match.group(1)), match.start(), match.end())
    match = re.search(r"영업현금흐름\s*\$?([\d.]+)\s*B", text)
    if match:
        _add(facts, chunk, "mu_q4_ocf", money_b(float(match.group(1))), match.start(), match.end())

    match = re.search(r"DRAM\s+([\d,]+(?:\.\d+)?)억\s*달러\s*\(비중\s*([\d.]+)%\s*,\s*QoQ\s*\+?([\d.]+)%\)", product or "")
    if match:
        _add(facts, chunk, "mu_dram_revenue", money_b_from_eok(match.group(1)), match.start(), match.end())
        _add(facts, chunk, "mu_dram_mix", f"{match.group(2)}%", match.start(), match.end())
        _add(facts, chunk, "mu_dram_qoq", signed_pct(match.group(3)), match.start(), match.end())
    match = re.search(r"DRAM\s*\$?([\d.]+)\s*B\s*\(\+?([\d.]+)%\s*QoQ\)", text)
    if match:
        _add(facts, chunk, "mu_dram_revenue", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_dram_qoq", signed_pct(match.group(2)), match.start(), match.end())
    if "ASP 10%대 후반" in (product or text):
        where = (product or text).find("ASP 10%대 후반")
        _add(facts, chunk, "mu_dram_asp", "10%대 후반", where, where + 12)
    if "ASP 약 30%" in (product or text) or "ASP +~30%" in text:
        where = text.find("30%")
        _add(facts, chunk, "mu_nand_asp", "약 +30%", max(0, where - 20), where + 3)

    match = re.search(r"NAND\s+([\d,]+(?:\.\d+)?)억\s*달러\s*\(비중\s*([\d.]+)%\s*,\s*QoQ\s*\+?([\d.]+)%\)", product or "")
    if match:
        _add(facts, chunk, "mu_nand_revenue", money_b_from_eok(match.group(1)), match.start(), match.end())
        _add(facts, chunk, "mu_nand_mix", f"{match.group(2)}%", match.start(), match.end())
        _add(facts, chunk, "mu_nand_qoq", signed_pct(match.group(3)), match.start(), match.end())
    match = re.search(r"NAND\s*\$?([\d.]+)\s*B\s*\(\+?([\d.]+)%\s*QoQ\)", text)
    if match:
        _add(facts, chunk, "mu_nand_revenue", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_nand_qoq", signed_pct(match.group(2)), match.start(), match.end())

    for label, key in (
        ("CMBU", "mu_cloud"),
        ("CDBU", "mu_core_dc"),
        ("MCBU", "mu_mobile"),
        ("AEBU", "mu_auto"),
    ):
        match = re.search(rf"{label}\s+([\d,]+(?:\.\d+)?)억\s*달러\s*\(([^)]*)\)", segment or "")
        if match:
            tail = match.group(2)
            qoq = re.search(r"QoQ\s*([+\-][\d.]+)%|\(([\+\-][\d.]+)%\)", "(" + tail + ")")
            extra = ""
            qoq_match = re.search(r"([+\-][\d.]+)%", tail)
            if qoq_match:
                extra = f", QoQ {qoq_match.group(1)}%"
            _add(
                facts,
                chunk,
                key,
                money_b_from_eok(match.group(1)) + extra,
                match.start(),
                match.end(),
            )
            del qoq

    match = re.search(r"Cloud Memory revenue grew to \$?([\d.]+)\s*B, while Core Data Center reached \$?([\d.]+)\s*B", text, re.I)
    if match:
        _add(facts, chunk, "mu_cloud", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_core_dc", money_b(float(match.group(2))), match.start(), match.end())
    match = re.search(r"Mobile and Client revenue rose to \$?([\d.]+)\s*B; Automotive and Embedded hit \$?([\d.]+)\s*B", text, re.I)
    if match:
        _add(facts, chunk, "mu_mobile", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_auto", money_b(float(match.group(2))), match.start(), match.end())

    match = re.search(r"매출\s+([\d,]+(?:\.\d+)?)억\s*달러\s*\(\+?([\d.]+)%\)", annual or "")
    if match:
        _add(facts, chunk, "mu_fy_revenue", money_b_from_eok(match.group(1)), match.start(), match.end())
        _add(facts, chunk, "mu_fy_revenue_yoy", signed_pct(match.group(2)), match.start(), match.end())
    match = re.search(r"EPS\s+(\d+(?:\.\d+)?)달러", annual or "")
    if match:
        _add(facts, chunk, "mu_fy_eps", f"${match.group(1)}", match.start(), match.end())
    match = re.search(r"FY2026 revenue reached \$?([\d.]+)\s*B, while non-GAAP EPS came in at \$?(\d+(?:\.\d+)?)", text, re.I)
    if match:
        _add(facts, chunk, "mu_fy_revenue", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_fy_eps", f"${match.group(2)}", match.start(), match.end())
    match = re.search(r"현금·투자자산\s+([\d,]+)억", text)
    if match:
        _add(facts, chunk, "mu_fy_cash", money_b_from_eok(match.group(1)), match.start(), match.end())
    match = re.search(r"with \$?([\d.]+)\s*B in cash", text, re.I)
    if match:
        _add(facts, chunk, "mu_fy_cash", money_b(float(match.group(1))), match.start(), match.end())

    match = re.search(
        r"조정 EPS:\s*\$?([\d.]+)\s*~\s*([\d.]+)\s*→\s*시장 예상\s*\$?([\d.]+)",
        text,
    )
    if match:
        _add(facts, chunk, "mu_q1_eps_low", f"${match.group(1)}", match.start(), match.end())
        _add(facts, chunk, "mu_q1_eps_high", f"${match.group(2)}", match.start(), match.end())
        _add(facts, chunk, "mu_q1_eps_cons", f"${match.group(3)}", match.start(), match.end())
    match = re.search(
        r"매출:\s*\$?([\d.]+)\s*~\s*([\d.]+)\s*B\s*→\s*시장 예상\s*\$?([\d.]+)\s*B",
        text,
    )
    if match:
        _add(facts, chunk, "mu_q1_rev_low", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_q1_rev_high", money_b(float(match.group(2))), match.start(), match.end())
        _add(facts, chunk, "mu_q1_rev_cons", money_b(float(match.group(3))), match.start(), match.end())
    match = re.search(r"중간값 기준 매출\s*\$?([\d.]+)\s*B[^\n]{0,30}?([+\d.]+)\s*%", text)
    if match:
        _add(facts, chunk, "mu_q1_rev_mid", money_b(float(match.group(1))), match.start(), match.end())
        _add(facts, chunk, "mu_q1_rev_qoq", signed_pct(match.group(2)), match.start(), match.end())
    match = re.search(r"FQ1 매출\s+([\d,]+)억\s*±\s*([\d,]+)억\s*달러,\s*매출총이익률\s*약\s*([\d.]+)%", guidance or text)
    if match:
        _add(facts, chunk, "mu_q1_rev_mid", money_b_from_eok(match.group(1)), match.start(), match.end())
        _add(facts, chunk, "mu_q1_gpm", f"{match.group(3)}%", match.start(), match.end())
    match = re.search(r"EPS\s+(\d+(?:\.\d+)?)\s*±\s*([\d.]+)달러", guidance or "")
    if match and float(match.group(1)) >= 20:
        _add(facts, chunk, "mu_q1_eps_mid", f"${match.group(1)}", match.start(), match.end())
    match = re.search(r"Non-GAAP gross margin \(%\)\s*~?([\d.]+)", text, re.I)
    if match and float(match.group(1)) < 95:
        _add(facts, chunk, "mu_q1_gpm", f"{match.group(1)}%", match.start(), match.end())
    if "GPM은 컨센 소폭 하회" in text or "GPM은 컨센서스 소폭 하회" in text:
        where = text.find("GPM")
        _add(facts, chunk, "mu_q1_gpm_below_cons", "컨센서스 소폭 하회", where, where + 20)
    if "매출총이익률 저점" in text or ("인센티브" in text and "저점" in text and "마진" in text or "GPM" in text):
        where = text.find("저점")
        if where >= 0 and ("인센티브" in text or "성과급" in text):
            _add(facts, chunk, "mu_gpm_trough", "차분기 마진은 성과급·인센티브 반영 저점, 이후 상승", where, where + 4)

    sca_body = sca or text
    match = re.search(r"16\s*건?\s*[→\-]\s*26\s*건", text)
    if not match:
        match = re.search(r"16건[^\n]{0,40}?26개", text)
    if match:
        _add(facts, chunk, "sca_count", "16건 → 26건", match.start(), match.end())
    match = re.search(r"SCA\s*(\d+)건 체결", sca_body)
    if match:
        _add(facts, chunk, "sca_signed", f"{match.group(1)}건", match.start(), match.end())
    match = re.search(r"2030년까지[^\n]{0,30}?(\d+)\s*%\s*이상", text)
    if match:
        _add(facts, chunk, "sca_2030_share", f"{match.group(1)}% 이상", match.start(), match.end())
    match = re.search(r"2030년 매출\s*~?(\d+)\s*%", text)
    if match:
        _add(facts, chunk, "sca_2030_target", f"약 {match.group(1)}%", match.start(), match.end())
    if "3/4은 가격" in text or "75% 가량" in text or "75%가량은" in text:
        where = text.find("가격")
        _add(facts, chunk, "sca_price_fixed", "약 75%는 가격 구조 확정", max(0, where - 30), where + 10)
    match = re.search(r"고객 (?:재무 )?약정\s*\$?([\d.]+)\s*B", text)
    if match:
        _add(facts, chunk, "sca_commitment", money_b(float(match.group(1))), match.start(), match.end())
    match = re.search(r"고객 재무 약정\s+([\d,]+)억\s*달러", text)
    if match:
        _add(facts, chunk, "sca_commitment", money_b_from_eok(match.group(1)), match.start(), match.end())
    match = re.search(r"RPO\s*~?\$?([\d.]+)\s*B", text)
    if match:
        _add(facts, chunk, "sca_rpo", money_b(float(match.group(1))), match.start(), match.end())
    match = re.search(r"RPO\s*약\s*([\d,]+)억\s*달러", text)
    if match:
        _add(facts, chunk, "sca_rpo", money_b_from_eok(match.group(1)), match.start(), match.end())
    if "2027년 생산량 75%+" in text or "75%+ 선계약" in text or "75% 이상 이미" in text:
        where = text.find("75%")
        _add(facts, chunk, "supply_2027_committed", "2027년 생산 75%+ 약정", where, where + 12)
    if "2027~28" in text and "공급" in text:
        where = text.find("2027")
        _add(facts, chunk, "supply_tight", "2027~2028년 공급 부족", where, where + 16)
    if "클린룸" in text and ("건설" in text or "Capex" in text or "캡엑스" in text.lower()):
        where = text.find("클린룸")
        _add(facts, chunk, "capex_cleanroom", "증액분 상당 부분이 클린룸·건설", where, where + 8)
    if "공급부족 장기화" in compact(text):
        where = text.find("공급")
        _add(facts, chunk, "supply_keyword", "핵심 키워드는 공급부족 장기화", where, where + 12)
    if market and "수급 균형 회복 시점은 가시성 없음" in market:
        where = market.find("가시성")
        _add(facts, chunk, "supply_no_visibility", "수급 균형 회복 시점 가시성 없음", where, where + 8)

    for name, pattern in (
        ("mu_rev_cons_table", r"Revenue \(\$B\)\s+([\d.]+)\s+([\d.]+)\s+Beat"),
    ):
        del name, pattern
    return facts


def _samsung_ranges(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    match = re.search(r"27년\s*OP:\s*(\d+)\s*~\s*(\d+)\s*조", text)
    if match:
        _add(facts, chunk, "sec_op_2027", f"{match.group(1)}~{match.group(2)}조원", match.start(), match.end())
    match = re.search(r"28년\s*OP:\s*(\d+)\s*~\s*(\d+)\s*조", text)
    if match:
        _add(facts, chunk, "sec_op_2028", f"{match.group(1)}~{match.group(2)}조원", match.start(), match.end())
    gaps = list(re.finditer(r"격차\s*(\d+)\s*조", text))
    if gaps:
        _add(facts, chunk, "sec_op_2027_gap", f"{gaps[0].group(1)}조원", gaps[0].start(), gaps[0].end())
    if len(gaps) > 1:
        _add(facts, chunk, "sec_op_2028_gap", f"{gaps[1].group(1)}조원", gaps[1].start(), gaps[1].end())
    match = re.search(r"TP:\s*(\d+)\s*~\s*(\d+)\s*만원", text)
    if match:
        _add(facts, chunk, "sec_tp", f"{match.group(1)}~{match.group(2)}만원", match.start(), match.end())
    match = re.search(r"유안타\s*(\d+)\s*만원", text)
    if match:
        _add(facts, chunk, "sec_tp_yuanta", f"{match.group(1)}만원", match.start(), match.end())
    match = re.search(r"Target PBR:\s*([\d.]+)\s*~\s*([\d.]+)\s*배", text)
    if match:
        _add(facts, chunk, "sec_pbr", f"{match.group(1)}~{match.group(2)}배", match.start(), match.end())
    match = re.search(r"ROE:\s*(\d+)\s*~\s*(\d+)\s*%", text)
    if match:
        _add(facts, chunk, "sec_roe", f"{match.group(1)}~{match.group(2)}%", match.start(), match.end())
    match = re.search(r"4Q\s*DRAM\s*ASP\s*\+?\s*(\d+)\s*~\s*(\d+)\s*%", text)
    if match:
        _add(facts, chunk, "sec_dram_asp_4q", f"+{match.group(1)}~{match.group(2)}%", match.start(), match.end())
    match = re.search(r"NAND\s*\+?\s*(\d+)\s*~\s*(\d+)\s*%", text)
    if match and "DRAM ASP" in text[max(0, match.start() - 40) : match.start() + 5]:
        _add(facts, chunk, "sec_nand_asp_4q", f"+{match.group(1)}~{match.group(2)}%", match.start(), match.end())
    match = re.search(r"DRAM/NAND\s*ASP\s*\+?\s*(\d+)\s*%\s*/\s*\+?\s*(\d+)\s*%", text)
    if match:
        _add(facts, chunk, "sec_asp_3q", f"DRAM +{match.group(1)}% / NAND +{match.group(2)}%", match.start(), match.end())
    match = re.search(r"3Q26 OP[^\n]{0,40}?(\d+\.?\d*)\s*~\s*(\d+\.?\d*)", text)
    if not match:
        match = re.search(r"(\d+\.\d)\s*~\s*(\d+\.\d).{0,12}?(\d+\.\d)\s*~\s*(\d+\.\d).{0,20}?([\d,]+)\s*~\s*([\d,]+)", text)
    return facts


def _samsung_tables(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    if chunk.kind not in {"pdf_ocr", "pdf_text", "txt"} and "조원" not in text:
        return facts
    facts.extend(_broker_op_rows(text, chunk))
    facts.extend(_asp_rows(text, chunk))
    facts.extend(_valuation_rows(text, chunk))
    facts.extend(_heungkuk(text, chunk))
    facts.extend(_hana_fx(text, chunk))
    return facts


def _broker_name(raw: str) -> str | None:
    compact_name = re.sub(r"[ㄱ-ㅎㅏ-ㅣ\s]", "", raw or "")
    if compact_name in {"05", "DS", "Ds"}:
        return "DS"
    for canonical, aliases in BROKER_ALIASES:
        if any(alias in compact_name for alias in aliases):
            return canonical
    return None


def _broker_op_rows(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    pattern = re.compile(
        r"(?P<name>[가-힣ㄱ-ㅎㅏ-ㅣA-Za-z0-9]{1,16})\s+(?P<date>\d{1,2}/\d{1,2})\s+"
        r"(?P<q3>\d+\.\d+)\s+(?P<q4>\d+\.\d+)\s+(?P<tp>[\d,]{5,9})"
    )
    seen: set[tuple[str, str]] = set()
    for match in pattern.finditer(text):
        q3 = float(match.group("q3"))
        q4 = float(match.group("q4"))
        tp = int(match.group("tp").replace(",", ""))
        if not (80 <= q3 <= 150 and 80 <= q4 <= 180 and 200_000 <= tp <= 900_000):
            continue
        broker = _broker_name(match.group("name")) or match.group("name")
        date = match.group("date")
        if (broker, date) in seen:
            continue
        seen.add((broker, date))
        display = f"{broker} ({date}) 3Q {q3:.1f}조 / 4Q {q4:.1f}조 / TP {tp // 10000}만원"
        _add(facts, chunk, "sec_broker_op", display, match.start(), match.end())
    return facts


def _asp_rows(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    pattern = re.compile(
        r"(?P<name>[^()\n]{0,16})\((?P<date>\d{1,2}/\d{1,2})\)\s+"
        r"(?P<a>[+\-]?\d+)\s+(?P<bg>[+\-]?\d+)\s+(?P<opm>\d+|[-—=])\s+(?P<q4>[+\-]?\d+)"
    )
    sections = re.split(r"NAND", text, maxsplit=1)
    labeled = [("DRAM", sections[0])]
    if len(sections) > 1:
        labeled.append(("NAND", sections[1]))
    for kind, body in labeled:
        for match in pattern.finditer(body):
            asp = int(match.group("a"))
            bg = int(match.group("bg"))
            q4 = int(match.group("q4"))
            if not (0 <= abs(asp) <= 40 and 0 <= abs(bg) <= 20 and 0 <= abs(q4) <= 40):
                continue
            broker = _broker_name(match.group("name")) or "미식별"
            opm = match.group("opm")
            opm_text = f"{opm}%" if opm.isdigit() else "미제시"
            display = (
                f"{kind} {broker} ({match.group('date')}) "
                f"3Q ASP {signed_pct(match.group('a'))} / B/G {signed_pct(match.group('bg'))} "
                f"/ OPM {opm_text} / 4Q ASP {signed_pct(match.group('q4'))}"
            )
            _add(facts, chunk, "sec_asp_row", display, match.start(), match.end())
    return facts


def _roe_text(value: str) -> str:
    repaired = _repair_multiple(value, "roe")
    if repaired == "미제시":
        return repaired
    return f"{repaired}%"


def _repair_multiple(value: str, kind: str) -> str:
    if value in {"-", "—", "미제시"}:
        return "미제시"
    number = float(value)
    if kind == "per" and number > 20:
        number = number / 10
    elif kind == "pbr" and number > 10:
        number = number / 10
    elif kind == "roe" and number > 100:
        number = number / 10
    text = f"{number:.1f}".rstrip("0").rstrip(".")
    return text


def _valuation_rows(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    pattern = re.compile(
        r"(?P<name>흠국|층국|릉국|흥국|05|DS|유안타|키움|BNK|하나|신한|NH)\s+"
        r"(?P<tp>\d{2,3})\s+(?P<op27>\d{3})\s+(?P<op28>미제시|\d{3})\s+"
        r"(?P<per>\d+\.?\d*)\s+(?P<pbr>\d+\.?\d*)\s+(?P<roe>[-—]|\d+\.?\d*)"
    )
    for match in pattern.finditer(text):
        op27 = int(match.group("op27"))
        if not (200 <= op27 <= 800):
            continue
        broker = _broker_name(match.group("name")) or match.group("name")
        op28 = match.group("op28")
        op28_text = f"{op28}조" if op28.isdigit() else "미제시"
        display = (
            f"{broker} TP {match.group('tp')}만원 / 27년 {op27}조 / 28년 {op28_text} / "
            f"PER {_repair_multiple(match.group('per'), 'per')}배 / "
            f"PBR {_repair_multiple(match.group('pbr'), 'pbr')}배 / "
            f"ROE {_roe_text(match.group('roe'))}"
        )
        _add(facts, chunk, "sec_valuation", display, match.start(), match.end())
    return facts


def _heungkuk(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    match = re.search(r"103\.6\s*조원\s*\(\+?\s*(\d+)\s*%", text)
    if match:
        _add(facts, chunk, "heung_q3_op", f"103.6조원 ({signed_pct(match.group(1))} QoQ)", match.start(), match.end())
    match = re.search(r"114\.9\s*조원\s*\(\+?\s*(\d+)\s*%", text)
    if match:
        _add(facts, chunk, "heung_q4_op", f"114.9조원 ({signed_pct(match.group(1))} QoQ)", match.start(), match.end())
    match = re.search(r"DS.{0,40}?104\.0\d*\s*(?:조원|조)?\s*\(\+?\s*(\d+)\s*%", text, re.I | re.S)
    if match:
        _add(facts, chunk, "heung_ds_q3", f"104.0조원 ({signed_pct(match.group(1))})", match.start(), match.end())
    match = re.search(r"DX.{0,80}?(-?\d+\.\d)\s*조", text, re.I | re.S)
    if match:
        _add(facts, chunk, "heung_dx", f"{match.group(1)}조원", match.start(), match.end())
    match = re.search(r"2026\d?\s*OP.{0,40}?(\d+\.\d)\s*조원\s*\(\+?\s*([\d,]+)\s*%", text, re.S)
    if match:
        _add(facts, chunk, "heung_op_2026", f"{match.group(1)}조원 ({signed_pct(match.group(2).replace(',', ''))})", match.start(), match.end())
    match = re.search(
        r"2027\d?\s*E?\s*OP.{0,50}?(\d{3}\.\d)\d*\s*(?:조원|조)?\s*\(\+?\s*([\d.]+)\s*%",
        text,
        re.S,
    )
    if match:
        _add(facts, chunk, "heung_op_2027", f"{match.group(1)}조원 ({signed_pct(match.group(2))})", match.start(), match.end())
    match = re.search(r"2025년\s*27%\s*.{0,12}2026년?\s*35%\s*.{0,12}2027년\s*41%", text, re.S)
    if match:
        _add(facts, chunk, "hbm_wafer_mix", "2025년 27% → 2026년 35% → 2027년 41%", match.start(), match.end())
    elif "웨이퍼" in text and re.search(r"2025년\s*27%", text) and "35%" in text and re.search(r"2027년\s*41%", text):
        where = text.find("2025년")
        _add(facts, chunk, "hbm_wafer_mix", "2025년 27% → 2026년 35% → 2027년 41%", where, where + 12)
    if re.search(r"3배\s*이상", text) and "웨이퍼" in text:
        where = text.find("3배")
        _add(facts, chunk, "hbm_wafer_multiple", "범용 DRAM 대비 웨이퍼 소모 3배 이상", where, where + 4)
    match = re.search(r"2026년\s*40%\s*[>→\-]\s*2027년\s*80%", text)
    if match:
        _add(facts, chunk, "hbm4_mix", "매출 비중 2026년 40% → 2027년 80%", match.start(), match.end())
    if re.search(r"\+?\s*100%\s*이상", text) and "HBM" in text:
        where = text.find("100%")
        _add(facts, chunk, "hbm_asp_2027", "+100% 이상", where, where + 4)
    if "110조" in text and "재원" in text:
        where = text.find("110조")
        _add(facts, chunk, "sec_return_base", "최근 3년 잔여재원 가정 110조원", where, where + 5)
    if re.search(r"3Q\s*30조", text) and re.search(r"4Q\s*40조\s*배당", text) and re.search(r"자사주\s*40조", text):
        where = text.find("40조")
        _add(facts, chunk, "sec_return_split", "3Q 배당 30조 + 4Q 배당 40조 + 자사주 소각 40조원", where, where + 8)
    elif re.search(r"4Q\s*40조\s*배당", text) and re.search(r"자사주\s*40조", text):
        where = text.find("40조")
        _add(facts, chunk, "sec_return_split", "4Q 배당 40조 + 자사주 소각 40조원", where, where + 8)
    match = re.search(r"2026년\s*368조.{0,8}2027년\s*555조", text)
    if match:
        _add(facts, chunk, "heung_op_bridge", "2026년 368조 → 2027년 555조원", match.start(), match.end())
    if "600조" in text and "140조" in text:
        where = text.find("600조")
        _add(facts, chunk, "sec_return_fcf", "FCF 50% 환원 시 약 600조원, 기존 3년 140조원 대비 4배 이상", where, where + 20)
    if "1cnm" in text or "1cnm" in text.replace(" ", ""):
        where = text.find("1c")
        _add(facts, chunk, "sec_1cnm", "1cnm 수율 개선과 HBM4 램프업", where, where + 8)
    if "Foundry" in text or "파운드리" in text:
        if "HBM4" in text and ("Base" in text or "베이스" in text or "턴키" in text):
            where = text.find("파운드리") if "파운드리" in text else text.find("Foundry")
            _add(facts, chunk, "sec_turnkey", "메모리와 파운드리 턴키, HBM4 베이스 다이", where, where + 8)
    return facts


def _hana_fx(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    match = re.search(r"27년 영업이익을\s*(\d+)\s*%?\s*정도\s*하향\s*(\d+)\s*조", compact(text))
    if not match:
        match = re.search(r"영업이익을\s*(\d+)%정도 하향\s*(\d+)조", compact(text))
    if match:
        _add(facts, chunk, "hana_2027_op", f"{match.group(2)}조원 (약 {match.group(1)}% 하향)", match.start(), match.end())
    if "1350" in text and "1400" in text and "삼성" in text:
        where = text.find("1350")
        _add(facts, chunk, "fx_assumption", "원/달러 가정 1,400원대 → 1,350원", where, where + 4)
    if "다시 약세" in compact(text) and "1400" in text:
        where = text.find("약세")
        _add(facts, chunk, "fx_view", "강의 시각은 2027년 원화 재약세(1,400원대)", where, where + 4)
    return facts


def _sfa(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    if "SFA" not in text and "056190" not in text and "자사주" not in text:
        return facts
    match = re.search(r"신규수주\s*([\d.]+)\s*조", text)
    if match:
        _add(facts, chunk, "sfa_orders", f"{match.group(1)}조원", match.start(), match.end())
    match = re.search(r"\+?\s*65\.6\s*%", text)
    if match and ("수주" in text or "YoY" in text or "10Y" in text or "신규" in text):
        _add(facts, chunk, "sfa_orders_yoy", "+65.6%", match.start(), match.end())
    if re.search(r"75\s*%", text) and "2023" in text:
        where = text.find("75")
        _add(facts, chunk, "sfa_legacy_2023", "2023년 디스플레이·2차전지 비중 75%", where, where + 3)
    if re.search(r"52\s*%", text) and "1H26" in text:
        where = text.find("52")
        _add(facts, chunk, "sfa_legacy_1h26", "2026년 상반기 52%", where, where + 2)
    if re.search(r"70\s*%", text) and ("비디스플레이" in text or "비디" in text or "비중 70" in text):
        where = text.find("70%")
        _add(facts, chunk, "sfa_new_mix", "2026년 비디스플레이·2차전지 수주 비중 70%", where, where + 3)
    match = re.search(r"자사주\s*19\s*%", text)
    if match:
        _add(facts, chunk, "sfa_cancel", "자사주 19% 소각", match.start(), match.end())
    match = re.search(r"22\s*%\s*보유", text)
    if match:
        _add(facts, chunk, "sfa_treasury", "자사주 22% 보유", match.start(), match.end())
    match = re.search(r"704\s*만\s*주(?:\(19%\))?", text)
    if match:
        _add(facts, chunk, "sfa_shares", "임직원 보상 3% 제외 약 704만 주", match.start(), match.end())
    if "SFA" in text and any(token in text for token in ("OHT", "전장이송", "전공정")):
        where = text.find("반도체")
        _add(facts, chunk, "sfa_semi", "반도체 전공정 이송으로 사업 확장", max(0, where), where + 6)
    return facts


def _flags(text: str, chunk: Chunk) -> list[Fact]:
    facts: list[Fact] = []
    flat = compact(text)
    rules = [
        ("solidigm", ("솔리다임", "미확정"), "솔리다임 상장은 미확정, 기준은 주주가치"),
        ("hbm4e_foundry", ("HBM4E", "파운드리"), "HBM4E 베이스 다이는 파운드리 공정"),
        ("hbm4e_codesign", ("HBM4E", "공동 설계"), "HBM4E는 엔비디아와 공동 설계"),
        ("techwing_unconfirmed", ("Techwing", "직접"), "테크윙 수혜는 장비 채택 확인이 따로 필요"),
        ("tes_catchup", ("테스", "catch"), "테스는 전공정 장비 대비 수익률 격차 축소 후보"),
        ("equip_no_bad_news", ("소부장", "나쁜 뉴스"), "소부장에 별도 악재는 없고 개별 실적·밸류로 접근"),
        ("higher_for_longer", ("Higher for longer",), "미국 금리는 higher for longer로 해석"),
        ("pce_soft", ("PCE", "낮"), "PCE는 예상보다 낮게 발표"),
        ("japan_governance", ("ROIC", "자본배분"), "일본 기업개혁은 주주환원에서 ROIC·자본배분으로 이동"),
        ("korea_governance", ("상법", "주주"), "한국은 이익이 일반주주로 연결되는지가 핵심"),
        ("hbm_price_121", ("121%",), "내년 HBM 가격 +121%"),
        ("foreign_sell", ("21조", "외국인"), "9월 외국인 순매도 약 21조원 언급"),
        ("test_socket", ("테스트 소켓", "ISC"), "테스트 소켓 ISC·티에스이·티에프이 순환 언급"),
    ]
    for key, needles, display in rules:
        if all(needle in text or needle in flat for needle in needles):
            where = text.find(needles[0])
            if where < 0:
                where = 0
            _add(facts, chunk, key, display, where, where + len(needles[0]))
    if "HBM4E" in text and ("foundry process" in text.lower() or "파운드리 공정" in text):
        where = text.find("HBM4E")
        _add(facts, chunk, "hbm4e_foundry", "HBM4E는 파운드리 공정 기반", where, where + 6)
    if "in-house" in text and "아닙니다" in text:
        where = text.find("in-house")
        _add(facts, chunk, "hbm4e_not_inhouse", "HBM4E는 HBM4와 같은 자체 베이스 다이가 아님", where, where + 8)
    if re.search(r"테스트 소켓.{0,120}30%|영업 ?이익률.{0,40}30%", text, re.S):
        where = text.find("30%")
        _add(facts, chunk, "socket_margin", "테스트 소켓 영업이익률 30% 이상", max(0, where - 40), where + 3)
    if "바이오" in text and "로봇" in text and "축소" in text:
        where = text.find("바이오")
        _add(facts, chunk, "trim_bio_robot", "바이오·로봇은 비중이 크면 반등 때 축소", where, where + 4)
    if "WTI" in text and re.search(r"90달러", text):
        where = text.find("WTI")
        _add(facts, chunk, "wti", "WTI 90달러대", where, where + 3)
    if re.search(r"50%\s*이하", text) and "금리" in text:
        where = text.find("50%")
        _add(facts, chunk, "hike_odds", "금리 인상 확률 50% 아래", where, where + 3)
    if "레이저텍" in text:
        where = text.find("레이저텍")
        _add(facts, chunk, "japan_equip_tape", "일본 장비주(레이저텍 등)와 국내 소부장이 동행", where, where + 4)
    if "10년" in text and "5.2" in text:
        match = re.search(r"5\.\d{2,3}", text)
        if match and "국채" in text[max(0, match.start() - 80) : match.end() + 40] or "10년" in text[max(0, match.start() - 40) : match.end() + 20]:
            _add(facts, chunk, "ust10", f"미 10년물 {match.group(0)}%", match.start(), match.end())
    match = re.search(r"1356", text)
    if match and "환율" in text:
        _add(facts, chunk, "fx_spot", "원/달러 1,356원대", match.start(), match.end())
    return facts
