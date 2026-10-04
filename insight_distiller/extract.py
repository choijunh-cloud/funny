"""Pull valuation rows and scalar facts out of quick-comment text."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


def _prep(text: str) -> str:
    return (
        text.replace("**", "")
        .replace("\u00a0", " ")
        .replace("\u200b", "")
    )


def _win(text: str, anchor: str, span: int = 900) -> str:
    i = text.find(anchor)
    if i < 0:
        return ""
    return text[i : i + span]


def _g(pattern: str, text: str, flags: int = 0) -> re.Match[str] | None:
    if not text:
        return None
    return re.search(pattern, text, flags)


@dataclass
class Facts:
    companies: list[dict] = field(default_factory=list)
    scalars: dict = field(default_factory=dict)

    def public(self) -> dict:
        return {
            "companies": self.companies,
            "scalars": {k: v for k, v in self.scalars.items() if v not in (None, "", [], {})},
        }


def _add_company(facts: Facts, **row) -> None:
    facts.companies.append({k: v for k, v in row.items() if v not in (None, "")})


def extract_facts(corpus: str) -> Facts:
    text = _prep(corpus)
    facts = Facts()
    s = facts.scalars

    h = _win(text, "SK하이닉스 (본주", 500)
    m = _g(r"SK하이닉스\s*\(본주\s*([\d.]+)만원\)\s*26년\s*PER\s*([\d.]+)배,\s*27년\s*PER\s*([\d.]+)배", h)
    if m:
        s["hynix_price"], s["hynix_per_26"], s["hynix_per_27"] = m.groups()

    sam = _win(text, "삼성전자 (", 400)
    m = _g(r"삼성전자\s*\(([\d.]+)만원\)\s*26년\s*PER\s*([\d.]+)배,\s*27년\s*PER\s*([\d.]+)배", sam)
    if m:
        s["samsung_price"], s["samsung_per_26"], s["samsung_per_27"] = m.groups()

    he = _win(text, "SK하이닉스 (원)", 220)
    m = _g(
        r"26년\s*([\d.]+)조/\s*([\d.]+)K\s*27년\s*([\d.]+)조/\s*([\d.]+)K",
        he,
    )
    if m:
        s["hynix_op_26"], s["hynix_eps_26"], s["hynix_op_27"], s["hynix_eps_27"] = m.groups()

    se = _win(text, "삼성전자 (원)", 220)
    m = _g(
        r"26년\s*([\d.]+)조/\s*([\d.]+)K\s*27년\s*([\d.]+)조/\s*([\d.]+)K",
        se,
    )
    if m:
        s["samsung_op_26"], s["samsung_eps_26"], s["samsung_op_27"], s["samsung_eps_27"] = m.groups()

    m = _g(r"YoY\s*\+(\d+)%이상/\s*\+(\d+)%,\s*\+(\d+)%", text)
    if m:
        s["yoy_op"], s["yoy_hynix_eps"], s["yoy_samsung_eps"] = m.groups()

    fx = _win(text, "원화강세", 450)
    m = _g(r"원화강세\s*([\d~%]+)\s*=>\s*삼전닉스\s*([\d~%]+)", fx)
    if m:
        s["fx_move"], s["fx_price_hit"] = m.groups()
    m = _g(r"환율\s*(\d+)\s*추정", fx)
    if m:
        s["fx_consensus"] = m.group(1)
    m = _g(r"=>\s*(\d{3,4})로 변경", fx)
    if m:
        s["fx_alt"] = m.group(1)
    m = _g(r"약\s*(\d+)%\s*현재 컨센", fx)
    if m:
        s["fx_consensus_cut"] = m.group(1)
    m = _g(r"할인율\s*(-?\d+)%\s*초반", text)
    if m:
        s["micron_discount"] = m.group(1)
    m = _g(r"과거\s*(-?\d+~-?\d+)%", text)
    if m:
        s["discount_band"] = m.group(1)

    scn = _win(text, "보수적가정", 350)
    m = _g(r"26년 PER\s*~(\d+)배\s*\(과거 사이클 주식\s*(\d+~\d+)배\)", scn)
    if m:
        s["floor_per"], s["cycle_per_band"] = m.groups()
    m = _g(r"(\d{3}~\d{3})만", scn)
    if m:
        s["hynix_floor"] = m.group(1)
    m = _g(r"(\d+\.\d+만~\d+\.\d+만원)", scn)
    if m:
        s["samsung_floor"] = m.group(1)

    if s.get("hynix_price"):
        _add_company(
            facts,
            group="memory",
            name="SK하이닉스",
            price=f"{s['hynix_price']}만 원",
            y26=_join_metrics(
                f"PER {s.get('hynix_per_26')}배" if s.get("hynix_per_26") else None,
                f"영업이익 {s['hynix_op_26']}조" if s.get("hynix_op_26") else None,
                f"EPS {s['hynix_eps_26']}K" if s.get("hynix_eps_26") else None,
            ),
            y27=_join_metrics(
                f"PER {s.get('hynix_per_27')}배" if s.get("hynix_per_27") else None,
                f"영업이익 {s['hynix_op_27']}조" if s.get("hynix_op_27") else None,
                f"EPS {s['hynix_eps_27']}K" if s.get("hynix_eps_27") else None,
            ),
        )
    if s.get("samsung_price"):
        _add_company(
            facts,
            group="memory",
            name="삼성전자",
            price=f"{s['samsung_price']}만 원",
            y26=_join_metrics(
                f"PER {s.get('samsung_per_26')}배" if s.get("samsung_per_26") else None,
                f"영업이익 {s['samsung_op_26']}조" if s.get("samsung_op_26") else None,
                f"EPS {s['samsung_eps_26']}K" if s.get("samsung_eps_26") else None,
            ),
            y27=_join_metrics(
                f"PER {s.get('samsung_per_27')}배" if s.get("samsung_per_27") else None,
                f"영업이익 {s['samsung_op_27']}조" if s.get("samsung_op_27") else None,
                f"EPS {s['samsung_eps_27']}K" if s.get("samsung_eps_27") else None,
            ),
        )

    mic = _win(text, "마이크론 (", 450)
    m = _g(r"마이크론\s*\(([\d.]+)달러\)", mic)
    if m:
        s["micron_price"] = m.group(1)
    m = _g(r"FY27 EPS \(26년 9월~27년 8월\)\s*([\d.]+)달러 PER\s*([\d.]+)배", mic)
    if m:
        s["micron_fy_eps"], s["micron_fy_per"] = m.groups()
    m = _g(r"CY27 EPS \(컨센 추정\)\s*([\d.]+)달러 PER\s*([\d.]+)배", mic)
    if m:
        s["micron_cy_eps"], s["micron_cy_per"] = m.groups()
    if s.get("micron_price"):
        _add_company(
            facts,
            group="memory",
            name="마이크론",
            price=f"{s['micron_price']}달러",
            y26=_join_metrics(
                f"FY27 EPS {s['micron_fy_eps']}달러" if s.get("micron_fy_eps") else None,
                f"PER {s['micron_fy_per']}배" if s.get("micron_fy_per") else None,
            ),
            y27=_join_metrics(
                f"CY27 EPS {s['micron_cy_eps']}달러" if s.get("micron_cy_eps") else None,
                f"PER {s['micron_cy_per']}배" if s.get("micron_cy_per") else None,
            ),
        )

    sd = _win(text, "Sandisk", 250)
    m = _g(r"Sandisk\s*\(([\d.]+)달러\)", sd)
    if m:
        s["sandisk_price"] = m.group(1)
    m = _g(r"FY27 EPS\s*([\d.]+)달러 기준 PER\s*([\d.]+)배", sd)
    if m:
        s["sandisk_eps"], s["sandisk_per"] = m.groups()
    if s.get("sandisk_price"):
        _add_company(
            facts,
            group="memory",
            name="샌디스크",
            price=f"{s['sandisk_price']}달러",
            y26="",
            y27=_join_metrics(
                f"FY27 EPS {s['sandisk_eps']}달러" if s.get("sandisk_eps") else None,
                f"PER {s['sandisk_per']}배" if s.get("sandisk_per") else None,
            ),
        )

    adr = _win(text, "SK하이닉스 ADR", 550)
    m = _g(r"SK하이닉스 ADR\s*([\d.]+)\s*=\s*([\d,.]+)만원\s*\(([\d,]+)원/달러", adr)
    if m:
        s["adr_usd"], s["adr_krw"], s["adr_fx"] = m.groups()
    m = _g(r"26년\s*PER\s*([\d.]+)배,\s*27년\s*PER\s*([\d.]+)배", adr)
    if m:
        s["adr_per_26"], s["adr_per_27"] = m.groups()
    m = _g(r"본주대비\s*(\d+)%\s*프리미엄", adr)
    if m:
        s["adr_premium"] = m.group(1)
    m = _g(r"(\d+)%시 본주\s*(\d+)만\s*=>\s*(\d+)%시\s*(\d+)만", adr)
    if m:
        s["adr_prem_a"], s["adr_local_a"], s["adr_prem_b"], s["adr_local_b"] = m.groups()
    if s.get("adr_usd"):
        _add_company(
            facts,
            group="memory",
            name="하이닉스 ADR",
            price=f"{s['adr_usd']}달러 = {s.get('adr_krw')}만 원",
            y26=f"PER {s['adr_per_26']}배" if s.get("adr_per_26") else "",
            y27=_join_metrics(
                f"PER {s['adr_per_27']}배" if s.get("adr_per_27") else None,
                f"본주 대비 {s['adr_premium']}% 프리미엄" if s.get("adr_premium") else None,
            ),
        )

    stx = _win(text, "Seagate (", 420)
    m = _g(r"Seagate\s*\(([\d.]+)달러\)", stx)
    if m:
        s["stx_price"] = m.group(1)
    m = _g(r"FY27 EPS\s*([\d.]+)달러 기준 PER\s*(\d+)배", stx)
    if m:
        s["stx_eps"], s["stx_per"] = m.groups()
    if s.get("stx_price"):
        _add_company(
            facts,
            group="hdd",
            name="시게이트",
            price=f"{s['stx_price']}달러",
            y26="",
            y27=_join_metrics(
                f"FY27 EPS {s['stx_eps']}달러" if s.get("stx_eps") else None,
                f"PER {s['stx_per']}배" if s.get("stx_per") else None,
            ),
        )

    wdc = _win(text, "Western Digital (", 420)
    m = _g(r"Western Digital\s*\(([\d.]+)달러\)", wdc)
    if m:
        s["wdc_price"] = m.group(1)
    m = _g(r"FY27 EPS\s*([\d.]+)달러 기준 PER\s*(\d+)배", wdc)
    if m:
        s["wdc_eps"], s["wdc_per"] = m.groups()
    if s.get("wdc_price"):
        _add_company(
            facts,
            group="hdd",
            name="웨스턴디지털",
            price=f"{s['wdc_price']}달러",
            y26="",
            y27=_join_metrics(
                f"FY27 EPS {s['wdc_eps']}달러" if s.get("wdc_eps") else None,
                f"PER {s['wdc_per']}배" if s.get("wdc_per") else None,
            ),
        )

    m = _g(r"약\s*([\d.]+)억달러", _win(text, "필리핀", 200))
    if m:
        s["toshiba_capex"] = m.group(1)
    m = _g(r"WDC\s*(\d+)%\s*\+\s*STX\s*(\d+)%\s*\+\s*Toshiba\s*(\d+)%", text)
    if m:
        s["share_wdc"], s["share_stx"], s["share_toshiba"] = m.groups()
    m = _g(r"합산 점유율이 약\s*(\d+)%\s*→\s*(\d+)%", text)
    if m:
        s["share_from"], s["share_to"] = m.groups()
    m = _g(
        r"2025년 3월 말\s*([\d.]+)배\s*→\s*2025년 12월\s*([\d.]+)배\s*→\s*2026년 6월\s*([\d.]+)배\s*→\s*9월 말\s*([\d.]+)배",
        text,
    )
    if m:
        s["wdc_pe_path"] = " → ".join(f"{x}배" for x in m.groups())
    if re.search(r"2028\s*이후", text):
        s["hdd_impact"] = "2028 이후"

    opt = _win(text, "광통신주 강세의 본질", 350)
    m = _g(
        r"코히런트 \(\+([\d.]+)%, 전일 \+([\d.]+)%\), 루멘텀홀딩스 \(\+([\d.]+)%, 전일 \+([\d.]+)%\), 크레도 3일연속상승 \(\+([\d.]+)%, \+([\d.]+)%, \+([\d.]+)%\)",
        opt,
    )
    if m:
        (
            s["cohr_w"],
            s["cohr_d"],
            s["lite_w"],
            s["lite_d"],
            s["crdo_1"],
            s["crdo_2"],
            s["crdo_3"],
        ) = m.groups()

    m = _g(r"목표주가\s*\$(\d+)", text)
    if m:
        s["cohr_tp"] = m.group(1)
    m = _g(r"FY2027 1Q 매출 \$(\d+)M,\s*\+([\d.]+)%", text)
    if m:
        s["crdo_rev"], s["crdo_yoy"] = m.groups()
    m = _g(r"FY2027 매출 성장률\s*(\d+)%\+", text)
    if m:
        s["crdo_guide"] = m.group(1)
    m = _g(r"광통신 매출을 \$(\d+)m", text, re.I)
    if m:
        s["crdo_optical"] = m.group(1)
    if "20개 고객" in text:
        s["cohr_engagements"] = "20"

    dos = _win(text, "광모듈용 CCL", 400)
    m = _g(
        r"1Q26\s*([\d,]+)억\s*→\s*2Q26\s*([\d,]+)억,\s*3Q26\s*([\d,]+)억\(\+([\d]+)% QoQ\)",
        dos,
    )
    if m:
        s["ccl_1q"], s["ccl_2q"], s["ccl_3q"], s["ccl_qoq"] = m.groups()

    san = _win(text, "산일전기", 1100)
    m = _g(r"매출 CAGR\s*([\d.]+)%,\s*영업이익 CAGR\s*([\d.]+)%", san)
    if m:
        s["sanil_sales_cagr"], s["sanil_op_cagr"] = m.groups()
    m = _g(r"영업이익률\s*([\d.]+)%\(FY26\)\s*→\s*([\d.]+)%\(FY28\)", san)
    if m:
        s["sanil_opm_26"], s["sanil_opm_28"] = m.groups()
    m = _g(r"FY28F PER\s*(\d+)배 vs LS Electric 약\s*(\d+)배", san)
    if m:
        s["sanil_per"], s["ls_per"] = m.groups()
    if "154kV" in san:
        s["sanil_154"] = "2028"
    if "Bloom Energy" in san:
        s["sanil_bloom"] = "벤더 등록"

    it = _win(text, "인텍플러스", 900)
    m = _g(r"3Q26E 매출\s*(\d+)억\(\+(\d+)%\)\s*/\s*OP\s*(\d+)억", it)
    if m:
        s["intech_sales"], s["intech_sales_yoy"], s["intech_op"] = m.groups()
    m = _g(r"수주잔고\s*([\d,]+)억 추정\(2Q\s*([\d,]+)억\)", it)
    if m:
        s["intech_backlog"], s["intech_backlog_prev"] = m.groups()
    m = _g(r"4Q 신규수주\s*([\d,]+)억", it)
    if m:
        s["intech_orders"] = m.group(1)
    m = _g(r"2027E 매출 \+(\d+)% / OP \+(\d+)%", it)
    if m:
        s["intech_sales_27"], s["intech_op_27"] = m.groups()
    m = _g(r"TP\s*([\d.]+)만원,\s*2027E EPS\s*([\d,]+)원\s*×\s*Target PER\s*([\d.]+)배", it)
    if m:
        s["intech_tp"], s["intech_eps"], s["intech_per"] = m.groups()
    m = _g(r"외국인 보유율\s*([\d.]+)%\s*→\s*([\d.]+)%", it)
    if m:
        s["intech_foreign_from"], s["intech_foreign_to"] = m.groups()
    m = _g(r"([\d,]+)억\s*→\s*([\d,]+)억 확대", it)
    if m:
        s["intech_capa_from"], s["intech_capa_to"] = m.groups()

    m = _g(r"시장컨센대비\s*\+(\d+)%", text)
    if m:
        s["semco_revision"] = m.group(1)
    m = _g(r"안전마진\s*([\d~%]+)", text)
    if m:
        s["semco_margin"] = m.group(1)
    if "FY2028 생산 개시" in text:
        s["shinko"] = "FY2028"
    if "2030년부터 캐파" in text:
        s["unimicron"] = "2030"

    port = _win(text, "기본포트", 450)
    m = _g(r"AI쪽\s*([\d~%]+)\s*\(삼전닉스\s*([\d~%]+)\s*소부장\s*([\d~%]+)\)", port)
    if m:
        s["port_ai"], s["port_memory"], s["port_materials"] = m.groups()
    m = _g(r"2차전지\s*(\d+%)", port)
    if m:
        s["port_battery"] = m.group(1)
    m = _g(r"건설/조선\s*(\d+%)", port)
    if m:
        s["port_infra"] = m.group(1)
    m = _g(r"현금\s*(\d+%)유지", port)
    if m:
        s["port_cash_light"] = m.group(1)
    m = _g(r"현금\s*(\d+%)(?!유지)", port)
    if m:
        s["port_cash"] = m.group(1)

    m = _g(r"([\d.]+)만명 vs\.?\s*컨센\s*([\d.]+)만명", text)
    if m:
        s["jobs_actual"], s["jobs_cons"] = m.groups()
    m = _g(r"전월\s*([\d.]+)만명", text)
    if m:
        s["jobs_prior"] = m.group(1)
    m = _g(r"3개월 평균 약\s*(\d+)만명", text)
    if m:
        s["jobs_3m"] = m.group(1)
    m = _g(r"(\d+)만명 하향조정", text)
    if m:
        s["jobs_revision"] = m.group(1)
    m = _g(r"시간당 평균임금 YoY\s*([\d.]+)%\s*→\s*연초\s*([\d.]+)%", text)
    if m:
        s["wage"], s["wage_start"] = m.groups()

    m = _g(r"7월\s*([\d.]+)%\s*→\s*개정\s*([\d.]+)%\s*→\s*8월\s*([\d.]+)%", text)
    if m:
        s["pce_july_old"], s["pce_july"], s["pce_august"] = m.groups()
    m = _g(r"3개월 연율\s*≈\s*([\d.]+)%.*?6개월 연율\s*≈\s*([\d.]+)%", text, re.S)
    if m:
        s["pce_3m"], s["pce_6m"] = m.groups()

    m = _g(r"10년물이\s*([\d.]+)%로 재상승", text)
    if m:
        s["ust10"] = m.group(1)
    m = _g(r"([\d.]+)% 급등 후\s*([\d.]+)%대", text)
    if m:
        s["ust10_spike"], s["ust10_back"] = m.groups()
    m = _g(
        r"금리는\s*\+(\d+)bp\s*가까이 상승했는데도 SOX \+([\d.]+)%, MU \+([\d.]+)%, KOSDAQ \+([\d.]+)%",
        text,
    )
    if m:
        s["rate_bp"], s["sox_window"], s["mu_window"], s["kosdaq_window"] = m.groups()
    m = _g(r"고용 쇼크에도 SOX \+([\d.]+)%", text)
    if m:
        s["sox_day"] = m.group(1)
    if "10월 추가 금리인상 전망 철회" in text or "10월 금리인상 전망을 낮추" in text:
        s["gs_october"] = "철회"
    if "12월 인상도 없을" in text or "12월로 연기" in text:
        s["gs_december"] = "없을 수 있음"
    if "$100" in text:
        s["oil"] = "100달러 이상"
    if "이란" in text:
        s["iran"] = "변수"

    m = _g(
        r"코스닥 \(\+([\d.]+)%\)\s*코스피 \(-([\d]+)%\)\s*코스닥비중\s*(\d+)%\s*=>\s*(\d+)%",
        text,
    )
    if m:
        s["kosdaq_turn"], s["kospi_turn"], s["kosdaq_share_from"], s["kosdaq_share_to"] = m.groups()

    burry = _win(text, "경제적 수명", 500)
    m = _g(r"(\d)년 vs (\d)년 vs (\d)년", burry)
    if m:
        s["gpu_life"] = " / ".join(f"{x}년" for x in m.groups())
    if "CoreWeave" in text:
        s["gpu_life_names"] = "NVIDIA · CoreWeave · Oracle · Microsoft · Meta"
    m = _g(r"\$(\d+)bn", text)
    if m:
        s["avgo_financing"] = m.group(1)

    return facts


def _join_metrics(*parts: str | None) -> str:
    return " · ".join(p for p in parts if p)
