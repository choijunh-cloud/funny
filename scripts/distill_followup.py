#!/usr/bin/env python3
"""10월 9일 전후 퀵코멘트·주말 인터뷰를 같은 규칙으로 추가 증류한다.

숫자는 이 원문 안의 표현만 쓴다. 10월 8일 카드와 겹치는 오픈AI 회계 설명은
새 사실만 보탠다.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from distill_insights import (
    DEFAULT_MD,
    Fact,
    FactSpec,
    Insight,
    Play,
    Report,
    assert_grounded,
    clean_transcript,
    extract_facts,
    fact_list,
    normalize,
    pick_evidence,
    stitch,
    write_report,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FOLLOW = ROOT / "sources" / "quick_oct9.txt"
OUT_MD = ROOT / "lectures" / "10월 9-11일 추가 인사이트.md"
OUT_DOCX = ROOT / "lectures" / "10월 9-11일 추가 인사이트.docx"
OUT_JSON = ROOT / "lectures" / "10월 9-11일 추가 인사이트.json"
COMBINED_MD = ROOT / "lectures" / "10월 8-11일 투자 인사이트.md"

FOLLOW_FACTS: list[FactSpec] = [
    FactSpec("cut", "부품 주문", r"(15~20%) 축소", True),
    FactSpec("bom", "BOM", r"(약 38%) 증가", True),
    FactSpec("px1199", "프로 시작가", r"(1,199달러)", True),
    FactSpec("px1299", "프로맥스 시작가", r"(1,299달러)"),
    FactSpec("plus100", "가격 인상폭", r"(100달러) 높아"),
    FactSpec("phone_share", "스마트폰 비트 비중", r"출하량의 (30%)"),
    FactSpec("bit_drop", "비트 수요 감소", r"(4\.5~6\.0%) 줄이는"),
    FactSpec("breakeven", "손익분기 가격", r"(\+4\.7~6\.4%)"),
    FactSpec("asp10", "가격 10% 가정", r"(10% 상승)한다면"),
    FactSpec("rev_up", "매출 증가 계산", r"(3\.4~5\.1%) 증가"),
    FactSpec("mu_ytd", "마이크론 연초 이후", r"(\+226\.2%)"),
    FactSpec("hynix_ytd", "하이닉스 연초 이후", r"(\+158\.2%)"),
    FactSpec("sec_ytd", "삼성 연초 이후", r"(\+103\.9%)"),
    FactSpec("elf_ytd", "ELF 연초 이후", r"(\+40\.4%)"),
    FactSpec("tiger", "화장품 ETF", r"(\+21\.1%)"),
    FactSpec("sec_jul", "삼성 7월 말 이후", r"(\+26\.6%)"),
    FactSpec("mu_jul", "마이크론 7월 말 이후", r"(\+25\.0%)"),
    FactSpec("elf_jul", "ELF 7월 말 이후", r"(\+32\.8%)"),
    FactSpec("hynix_jul", "하이닉스 7월 말 이후", r"(-2\.2%)"),
    FactSpec("elf_sep", "ELF 9월 말 이후", r"(\+8\.2%)"),
    FactSpec("igv", "IGV", r"(\+5\.8%)"),
    FactSpec("ulta", "ULTA", r"(\+4\.4%)"),
    FactSpec("hynix_sep", "하이닉스 9월 말 이후", r"(-5\.7%)"),
    FactSpec("mu_sep", "마이크론 9월 말 이후", r"(-3\.4%)"),
    FactSpec("spacex", "스페이스X", r"(\+1\.25%)"),
    FactSpec("tmobile", "T모바일", r"(-13\.27%)"),
    FactSpec("att", "AT&T", r"(-9\.85%)"),
    FactSpec("vz", "버라이즌", r"(-8\.75%)"),
    FactSpec("cci", "크라운캐슬", r"(\+15\.6%)"),
    FactSpec("amt", "아메리칸타워", r"(\+9\.3%)"),
    FactSpec("lite", "루멘텀", r"(\+5\.22%)"),
    FactSpec("lite_prev", "루멘텀 전일", r"(-5\.62%)"),
    FactSpec("soldout", "광학 완판", r"(2029년 초)까지"),
    FactSpec("gap70", "2027 충족률", r"(약 70%)를 충족"),
    FactSpec("short28", "공급 부족", r"(2028년)까지 이어질"),
    FactSpec("turn50", "과거 거래대금", r"(50조 이상)"),
    FactSpec("turn20", "최근 거래대금", r"(20조 초반)"),
    FactSpec("us_share", "미국계 비중", r"(43\.8%)"),
    FactSpec("uk_was", "영국계 이전", r"(9%대)"),
    FactSpec("uk_now", "영국계 현재", r"(7% 6%대)"),
    FactSpec("cap25", "종목 한도", r"(한 종목당 25%)"),
    FactSpec("cap50", "상위 3종목", r"(50%를 넘으면)"),
    FactSpec("fx1500", "이전 환율", r"(1500원)을 받고"),
    FactSpec("fx1300", "현재 환율", r"(1,300원)을 보고"),
    FactSpec("mu_tp", "마이크론 목표", r"(3,000달러)"),
    FactSpec("mu_per", "마이크론 배수", r"(19배)"),
    FactSpec("kr_per", "삼전닉스 배수", r"(다섯 배섯 배)"),
    FactSpec("dram28", "서피스 디램", r"(28기가)"),
    FactSpec("oil106", "유가 고점", r"(106달러)"),
    FactSpec("midterm", "중간선거", r"(11월 3일)"),
    FactSpec("hike", "10월 인상 확률", r"(10% 대)로 떨어"),
    FactSpec("wage", "임금", r"(0\.1%)밖에"),
    FactSpec("ai60", "AI 비중", r"(AI를 60)"),
    FactSpec("bond25", "금리 자산", r"(한 25 정도)"),
    FactSpec("gold15", "금 비중", r"(15는 저는 금)"),
    FactSpec("ust_rare", "미국 10년", r"(5\.2% 5\.3%)"),
    FactSpec("ust1990", "비교 시점", r"(1990년도)"),
    FactSpec("sec50", "5월 삼성 상상", r"(50만 원가)"),
    FactSpec("hynix280", "5월 하이닉스 상상", r"(280만 원가)"),
    FactSpec("sec27", "5월 말 삼성 한계", r"(27만 원)"),
    FactSpec("own_low", "외국인 비중 반론", r"(많이 낮지 않습니다)"),
    FactSpec("own_hist", "외국인 비중 다른 말", r"(역대급으로)"),
    FactSpec("retail190", "상반기 개인", r"(190조원)"),
    FactSpec("inst53", "금융투자", r"(53조원)"),
    FactSpec("for200", "외국인 매도", r"(200조원)"),
    FactSpec("top7500", "4분기 상단", r"(7,500포인트)"),
    FactSpec("top8000", "4분기 상단 끝", r"(8천 정도)"),
    FactSpec("dxy", "달러인덱스", r"(102까지)"),
    FactSpec("krw", "원화", r"(1350원대)"),
    FactSpec("ust53", "10년 고점", r"(5\.3까지)"),
    FactSpec("swing", "박스 목표", r"(10%에서 15%)"),
    FactSpec("hy_per", "현대차 PER", r"(아홉배)"),
    FactSpec("kia_per", "기아 PER", r"(다섯 배)"),
    FactSpec("op3", "현대차 컨센서스", r"(3조 정도)"),
    FactSpec("op26", "하향 눈높이", r"(2조 6천)"),
    FactSpec("bd100", "보스턴 가치", r"(100조 정도)"),
    FactSpec("atlas", "아틀라스 배치", r"(메타플랜트)"),
    FactSpec("lamp", "램프 매각", r"(6,억 정도)"),
    FactSpec("payback", "데이터센터 회수", r"(3년이면 본전)"),
    FactSpec("dc_margin", "임대 마진", r"(80%가 넘어요)"),
    FactSpec("bond30", "장기채", r"(30년짜리)"),
    FactSpec("ust6", "10년 상단 언급", r"(6% 넘기는)"),
    FactSpec("issue77", "30년물 첫 발행", r"(7\.7이었어요)"),
    FactSpec("y1980", "1980년 30년", r"(12%였습니다)"),
    FactSpec("gold5k", "금 고점", r"(5,000달러)"),
    FactSpec("gold4k", "금 현재", r"(4,000달러)"),
    FactSpec("goldw", "금 비중 제안", r"(5에서 10%)"),
    FactSpec("brazil", "브라질 달러채", r"(브라질)"),
    FactSpec("gap36", "ARR 차이", r"(36%나)"),
    FactSpec("oracle_buy", "오라클 내부자", r"(350만 달러)"),
    FactSpec("burn", "현금 소진 보도", r"(2,780억)"),
    FactSpec("sox", "SOX", r"(SOX -3\.4%)"),
    FactSpec("insurance", "인버스 보험", r"(0\.1%)"),
]


def build_followup_insights(book: dict[str, Fact], lines: list[str]) -> list[Insight]:
    def has(*ids: str) -> bool:
        return all(item in book for item in ids)

    def v(fid: str) -> str:
        return book[fid].value

    insights: list[Insight] = []
    insights.append(
        Insight(
            title="아이폰 주문 축소는 부정 뉴스, DRAM 매출 산수는 따로다",
            stance="조건부 긍정",
            horizon="주문 지속성을 확인할 때까지",
            verdict=(
                f"닛케이 보도의 아이폰 18 Pro 부품 주문 축소는 {v('cut')}다. "
                f"트렌드포스는 256GB 프로 제조원가가 {v('bom')} 는다고 했고, "
                f"미국 시작가는 {v('px1199')}, {v('px1299')}, 전작보다 {v('plus100')} 높다. "
                "다른 변수가 그대로면 이 뉴스 자체는 부정이다. "
                f"다만 스마트폰용 DRAM을 비트 출하량의 {v('phone_share')}로 두면, "
                f"스마트폰 수요 감소는 전체 비트 수요를 {v('bit_drop')} 요인이다. "
                f"손익분기 가격 상승률은 {v('breakeven')}이고, "
                f"평균가격이 {v('asp10')}하면 매출 증가 계산은 {v('rev_up')}다."
            ),
            action="볼 곳은 스마트폰 판매 둔화 자체가 아니라 서버·AI 수요가 DRAM 가격 결정력을 유지하는가다. 27년 HBM 중심 가격 기대가 더 큰 변수다.",
            avoid="부품 주문 감소를 완제품 판매 감소와 같은 숫자로 쓰지 않는다. 애플이 메모리를 아예 빼는 시나리오로 쓰지 않는다.",
            facts=fact_list(
                book,
                ["cut", "bom", "px1199", "px1299", "plus100", "phone_share", "bit_drop", "breakeven", "asp10", "rev_up"],
            ),
            keywords=["15~20%", "38%", "4.5", "DRAM", "아이폰"],
        )
    )
    insights.append(
        Insight(
            title="애플의 다섯 카드 중 이번 보도는 생산량 조절이다",
            stance="관망",
            horizon="초기 판매 확인",
            verdict=(
                "원가 흡수는 판매가격, 마진, 제품 구성, 메모리 사양, 생산량 조절로 나뉜다. "
                "보도대로라면 이번 선택은 다섯 번째, 재고와 현금흐름을 지키는 생산량 조절이다. "
                "가격을 더 올리면 판매량과 교체 주기가 위험하고, AI 기능을 위해 RAM을 무조건 줄이기도 어렵다."
            ),
            action="주문이 다시 늘면 판매 회복, 주문이 판매 감소로 이어지면 지속 악재로 업그레이드한다.",
            avoid="가격 100달러 인상을 수요가 이미 확인된 전가로 단정하지 않는다.",
            facts=fact_list(book, ["plus100", "px1199", "px1299"]),
            keywords=["생산량 조절", "마진 일부", "1,199", "주문"],
        )
    )
    insights.append(
        Insight(
            title="누적 수익은 메모리, 최근 수익은 소프트웨어와 화장품",
            stance="로테이션",
            horizon="7월 말·9월 말 이후",
            verdict=(
                f"연초 이후는 마이크론 {v('mu_ytd')}, 하이닉스 {v('hynix_ytd')}, 삼성 {v('sec_ytd')}가 앞이고 "
                f"화장품 ELF는 {v('elf_ytd')}, TIGER 화장품은 {v('tiger')}다. "
                f"7월 말 이후는 삼성 {v('sec_jul')}, 마이크론 {v('mu_jul')}, ELF {v('elf_jul')}가 강했고 하이닉스는 {v('hynix_jul')}다. "
                f"9월 말 이후는 ELF {v('elf_sep')}, IGV {v('igv')}, ULTA {v('ulta')}가 올랐고 "
                f"하이닉스 {v('hynix_sep')}, 마이크론 {v('mu_sep')}은 빠졌다."
            ),
            action="올해 누적과 최근 한 달을 같은 문장으로 말하지 않는다. 최근 상대 강도는 미국 소프트웨어·화장품이다.",
            avoid="연초 이후 메모리 수익률로 최근 한국 메모리 조정을 덮지 않는다.",
            facts=fact_list(
                book,
                ["mu_ytd", "hynix_ytd", "sec_ytd", "elf_ytd", "tiger", "sec_jul", "mu_jul", "elf_jul", "hynix_jul", "elf_sep", "igv", "ulta", "hynix_sep", "mu_sep"],
            ),
            keywords=["226.2", "ELF", "9월 말", "소프트웨어"],
        )
    )
    insights.append(
        Insight(
            title="10월 9일, 지수 반등과 반도체 회복은 다른 일이다",
            stance="선별",
            horizon="광통신 수주가 이익으로 확인될 때까지",
            verdict=(
                "9일 지수와 일부 대형 기술주는 반등했지만 SOX·엔비디아·TSMC·메모리는 약세였다. "
                "소프트웨어 ETF, 오라클, AI 클라우드 인프라는 반등했다. "
                f"스페이스X는 {v('spacex')}, T-모바일 {v('tmobile')}, AT&T {v('att')}, 버라이즌 {v('vz')}다. "
                f"크라운캐슬 {v('cci')}, 아메리칸타워 {v('amt')}다. "
                f"루멘텀은 전일 {v('lite_prev')} 뒤 {v('lite')}다. "
                f"광학 부품은 {v('soldout')} 완판, 2027년 수요의 {v('gap70')} 못할 수 있고 부족은 {v('short28')} 전망이다."
            ),
            action="관심의 이동은 AI 수익성 검증에서 광통신 병목과 인프라 선별이다. 공급 부족이 매출·이익이 되는지는 증설 속도와 밸류에이션을 같이 본다.",
            avoid="스타링크 모바일을 통신 인프라 수요 소멸로 쓰지 않는다. 기지국·소형셀은 같은 날 반대로 움직였다.",
            facts=fact_list(
                book,
                ["spacex", "tmobile", "att", "vz", "cci", "amt", "lite", "lite_prev", "soldout", "gap70", "short28", "sox"],
            ),
            keywords=["루멘텀", "스타링크", "크라운캐슬", "SOX", "광통신"],
        )
    )
    insights.append(
        Insight(
            title="한국만 발목이 잡힌 이유는 거래대금과 헤지펀드 한도다",
            stance="관망",
            horizon="금리 안정과 펀드 한도가 풀릴 때까지",
            verdict=(
                f"거래대금은 하루 {v('turn50')}에서 {v('turn20')} 또는 그 아래로 줄었다. "
                f"8월 말 미국계는 {v('us_share')}이고, 영국계는 {v('uk_was')}에서 {v('uk_now')}로 낮아졌다. "
                "7·8월 미국계는 사고 영국계가 팔았다는 구분이다. "
                "영국계는 헤지펀드라 손실이 커지면 매니저가 교체되는 돈이다. "
                f"펀드 규정은 {v('cap25')}가 넘지 않고, 상위 세 종목 합산이 {v('cap50')} 안 된다. "
                f"환율은 결과다. 이전 {v('fx1500')}을 받던 구간이 지금 {v('fx1300')}이다. "
                "환전 주체가 삼성·하이닉스라 그 위로 크게 가는 쪽은 쉽지 않고, 지금 레벨의 원화 강세는 외국인 환차익 쪽에 가깝다."
            ),
            action="외국인 매도를 국적 없이 한 덩어리로 쓰지 않는다. 미국계 장기 자금과 영국계 헤지펀드를 나눈다.",
            avoid="환율이 올랐기 때문에 주가가 빠졌다는 인과로 쓰지 않는다.",
            facts=fact_list(
                book,
                ["turn50", "turn20", "us_share", "uk_was", "uk_now", "cap25", "cap50", "fx1500", "fx1300"],
            ),
            keywords=["50조 이상", "영국계", "43.8%", "환율은 결과", "한 종목당 25%"],
        )
    )
    insights.append(
        Insight(
            title="금리는 방향은 인정하고, 속도는 헤지펀드 숏의 오버슈팅으로 본다",
            stance="조건부 매수",
            horizon="11월 3일 중간선거와 다음 주 물가",
            verdict=(
                "낮은 금리에서 중립까지는 지수에 플러스이고, 중립을 넘은 긴축에서도 지수는 버틸 수 있다. "
                "대신 오르는 종목 수는 줄어든다. "
                "지금 금리 급등은 헤지펀드의 미국 국채 공매도가 역사상 많다는 포지션 이야기다. "
                f"10월 인상 확률은 {v('hike')}로 떨어졌고, 시간당 임금은 전월 대비 {v('wage')}다. "
                f"유가는 고점 {v('oil106')}에서 90불대 또는 80대 후반이다. "
                f"촉매는 {v('midterm')} 중간선거와 다음 주 수요일 소비자물가다. "
                f"마이크론은 데이비스가 {v('mu_tp')}로 올리고 {v('mu_per')}를 적용했다. "
                f"삼성·하이닉스는 {v('kr_per')}쯤이고, 서피스에는 {v('dram28')}가 들어간다."
            ),
            action="금리 레벨보다 상승 속도가 급한지를 본다. 물가가 예상보다 높지 않으면 국채 숏 청산이 반도체 수급의 조건이 된다.",
            avoid="9월에 돈 번 사람이 많았다는 말로 장을 설명하지 않는다. 상반기 급등장을 일반 장으로 두지 않는다.",
            facts=fact_list(book, ["hike", "wage", "oil106", "midterm", "mu_tp", "mu_per", "kr_per", "dram28", "ust53"]),
            keywords=["공매도 포지션", "3,000달러", "11월 3일", "28기가", "종목수"],
        )
    )
    insights.append(
        Insight(
            title="같은 고금리에 포트가 세 갈래다",
            stance="분산",
            horizon="이번 금리 사이클",
            verdict=(
                f"알상무는 100 중 {v('ai60')} 담고, 나머지 중 {v('bond25')}는 금리 자산, {v('gold15')}이다. "
                f"미국 10년 {v('ust_rare')}는 {v('ust1990')}에 봤던 금리라는 표현이다. "
                "그는 금리 하락을 믿지 않으면서도 아무도 안 말할 때 채권 ETF를 소량 산다. "
                f"신환종은 {v('bond30')}를 이 사이클에 사서 쿠폰을 길게 받자고 하고, 10년은 {v('ust6')} 갈 수도 있다고 본다. "
                f"30년물 첫 발행은 {v('issue77')}, 그 뒤 고점 구간은 {v('y1980')} "
                f"금은 {v('gold5k')} 갔다가 {v('gold4k')}이고 자산의 {v('goldw')}를 말한다. "
                f"{v('brazil')} 달러채는 비과세 쿠폰으로 은퇴 인컴에 넣자는 제안이다. "
                f"서준식은 국내 주식 100%를 유지하고, 미국 지수 인버스를 {v('insurance')}만 심리 보험으로 시작했다."
            ),
            action="성장은 AI·반도체, 인컴은 긴 금리, 방어는 금으로 기능을 나눈다. 이름만 주식·채권으로 나누고 전부 위험자산이면 분산이 아니다.",
            avoid="안전한데 수익률만 높다는 상품을 사지 않는다. 스테이블코인 단일통화를 기정사실로 두지 않는다.",
            facts=fact_list(
                book,
                ["ai60", "bond25", "gold15", "ust_rare", "ust1990", "bond30", "ust6", "issue77", "y1980", "gold5k", "gold4k", "goldw", "brazil", "insurance", "sec50", "hynix280", "sec27"],
            ),
            keywords=["AI를 60", "30년짜리", "5,000달러", "브라질", "국내 주식"],
        )
    )
    insights.append(
        Insight(
            title="4분기 상단은 제한, 외국인 비중 진단은 갈린다",
            stance="박스",
            horizon="올해 남은 분기와 연말·연초",
            verdict=(
                f"코스피는 올해 글로벌 주요 증시 상승률 1위라는 평가와 함께, 4분기 상단을 {v('top7500')}에서 {v('top8000')}로 둔다. "
                "삼성·하이닉스 전고점은 올해 남은 분기에 힘들다는 쪽이다. 절대 저평가는 인정한다. "
                f"상반기 개인 {v('retail190')}, 금융투자 {v('inst53')}, 외국인 매도 {v('for200')}을 넘는다. "
                f"한 화자는 외국인 비중이 {v('own_hist')} 낮다고 하고, 다른 화자는 {v('own_low')} 거의 비슷하다고 한다. "
                f"달러인덱스는 {v('dxy')}, 원화는 {v('krw')} 중반이다. "
                f"박스 안 목표 수익은 {v('swing')}다. "
                "AI 사이클 중단이 아니라 GPU, 디램, 낸드, 기판, 네트워크, 그다음 CPU로 매기가 이동한다는 설명이다."
            ),
            action="시황, 섹터, 종목 순서로 본다. 산타·연초는 반도체 장비 조정 이후와 ESS·태양광을 후보로 두되, 선거 전 불확실성에서는 보유 기간을 짧게 한다.",
            avoid="원화 강세만으로 외국인 순매수가 이미 와야 했다고 쓰지 않는다. 채권 자본차익을 무위험으로 쓰지 않는다.",
            facts=fact_list(
                book,
                ["top7500", "top8000", "retail190", "inst53", "for200", "own_hist", "own_low", "dxy", "krw", "swing", "ust53"],
            ),
            keywords=["190조", "역대급", "많이 낮지", "7,500", "1350"],
        )
    )
    insights.append(
        Insight(
            title="현대차는 로봇이 올리고 로봇이 내렸다",
            stance="보유",
            horizon="2027년 전후, 배치 기준은 2028년",
            verdict=(
                "상반기 상승 모멘텀도 로봇, 조정 이유도 로봇이다. 본업 서프라이즈로 하단을 받기 어렵다. "
                f"3분기 눈높이는 {v('op3')}에서 {v('op26')}까지 내려온 언급이 있다. "
                f"보스턴다이내믹스 기업가치 {v('bd100')}와 수천억 적자가 동시에 말하고, "
                f"아틀라스 배치는 {v('atlas')} 공장, 시점은 2028년도이다. "
                f"연말 이익 기준 현대차 {v('hy_per')}, 기아 {v('kia_per')}라 자동차 실적만으로 싸다고 보지 않는다. "
                f"모비스 램프 매각은 {v('lamp')}이고 매출은 2조 정도로 말한다."
            ),
            action="보유자는 유지한다. 현대차는 50만 원 아래를 매수 구간, 그 위를 수익 구간으로 나눈다. 그룹 안에서는 액추에이터인 모비스를 먼저 본다.",
            avoid="로봇 모멘텀이 사라졌다고 쓰지 않는다. IPO 일정이 확정됐다고 쓰지도 않는다.",
            facts=fact_list(book, ["op3", "op26", "bd100", "atlas", "hy_per", "kia_per", "lamp"]),
            keywords=["현대차", "아홉배", "메타플랜트", "2조 6천", "보스턴"],
        )
    )
    insights.append(
        Insight(
            title="GPU 담보 대출은 지금 금융공학, 나중 뇌관은 담보 가치다",
            stance="주시",
            horizon="엔비디아 추세와 금리가 꺾이기 전",
            verdict=(
                f"하이퍼스케일러가 회사채만 찍던 자리에서, 칩과 데이터센터를 담보로 돈을 빌리는 구조가 나왔다. "
                f"아마존은 {v('payback')} 뽑는다고 했고, 데이터센터 임대 마진은 {v('dc_margin')} "
                "감가상각보다 담보 가격과 임대 수익률이 무너질 때가 주택담보대출과 같은 위험이다. "
                "착공이 막히면 반도체에는 부정이고, 기존 네오클라우드 임대료에는 호재라는 바벨이다. "
                f"오픈AI 680억과 500억은 {v('gap36')} 차이이고, 하락은 수요 붕괴보다 집계 논란, 유가 100달러 이상, 차익실현이 겹친 것으로 본다. "
                f"오라클 이사 매수는 {v('oracle_buy')}, 현금 소진 보도는 {v('burn')} 달러이나 회사 측이 정확성에 의문을 제기했다."
            ),
            action="당장은 엔비디아 추세와 하이일드 스프레드를 본다. 경고가 나와도 주가가 더 가는 구간이 있으니, 처음부터 붕괴로 단정하지 않고 담보 가치가 훼손될 때 비중을 줄인다.",
            avoid="장부 밖 거래를 이미 터진 위기로 쓰지 않는다. 공매도 잔고는 월 2회·시차 공개라 당일 확인이 안 된다. 안전한 고수익 상품은 피한다.",
            facts=fact_list(book, ["payback", "dc_margin", "gap36", "oracle_buy", "burn", "sox"]),
            keywords=["3년이면 본전", "80%가 넘", "네오클라우드", "36%나", "350만 달러"],
        )
    )
    for insight in insights:
        insight.evidence = pick_evidence(lines, insight.keywords, insight.facts)
    return insights


def build_followup_plays(book: dict[str, Fact]) -> list[Play]:
    def v(fid: str) -> str:
        return book[fid].value if fid in book else ""

    return [
        Play(f"아이폰 부품 주문 {v('cut')}가 실제 판매 감소로 이어지면", "DRAM 뉴스의 지속 악재로 올린다"),
        Play(f"DRAM 평균가격이 {v('asp10')}하고 공급 부족이 유지되면", f"비트 수요 {v('bit_drop')} 감소보다 매출 {v('rev_up')} 계산을 먼저 본다"),
        Play("서버·AI가 가격 결정력을 잃으면", "스마트폰 둔화를 업황 훼손으로 올린다"),
        Play(f"미국 10년 {v('ust53')} 속도가 물가 확인 후 완만해지면", "외국인 반도체 매수 여지를 연다"),
        Play(f"코스피가 {v('top7500')}에서 {v('top8000')} 안에 있으면", f"목표 {v('swing')}의 짧은 매매로 본다"),
        Play("광통신 완판이 이익으로 확인되면", "GPU·메모리 다음 병목으로 다룬다"),
        Play("엔비디아 추세와 담보 가치가 함께 꺾이면", "GPU 담보 대출을 뇌관 쪽으로 옮긴다"),
        Play("현대차가 50만 원 아래면", "보유와 분할 매수 구간으로 둔다"),
    ]


def build_followup_headline(book: dict[str, Fact]) -> str:
    def v(fid: str) -> str:
        return book[fid].value

    return (
        f"아이폰 18 Pro 부품 주문은 {v('cut')} 축소, 256GB 제조원가는 {v('bom')}다. "
        f"스마트폰 DRAM 비중 {v('phone_share')} 전제에서 비트 수요 감소 {v('bit_drop')}는 "
        f"가격 {v('breakeven')}면 상쇄되고, {v('asp10')}하면 매출 증가 계산은 {v('rev_up')}다. "
        f"한국 거래대금은 {v('turn50')}에서 {v('turn20')}으로 줄었고, "
        f"4분기 상단은 {v('top7500')}에서 {v('top8000')}다. "
        f"한 갈래의 포트는 {v('ai60')} 담고, 금리 자산은 {v('bond25')}, 나머지는 금이다."
    )


def build_followup_report(raw: str, source_name: str) -> Report:
    lines = clean_transcript(raw)
    flat = normalize("\n".join(lines))
    book, missing = extract_facts(flat, FOLLOW_FACTS)
    insights = build_followup_insights(book, lines)
    headline = stitch(build_followup_headline(book))
    plays = [Play(stitch(play.when), stitch(play.then)) for play in build_followup_plays(book)]
    for insight in insights:
        insight.verdict = stitch(insight.verdict)
        insight.action = stitch(insight.action)
        insight.avoid = stitch(insight.avoid)
    assert_grounded(headline, flat, "추가 헤드라인")
    for play in plays:
        assert_grounded(play.when + " " + play.then, flat, play.when)
    for insight in insights:
        blob = "\n".join([insight.title, insight.verdict, insight.action, insight.avoid])
        assert_grounded(blob, flat, insight.title)
        for fact in insight.facts:
            if fact.value not in flat:
                raise LookupError(f"{insight.title} 팩트 누락: {fact.value}")
        for quote in insight.evidence:
            if normalize(quote) not in flat:
                raise LookupError(f"앵커 누락: {quote}")
        if not insight.evidence:
            raise LookupError(f"앵커 없음: {insight.title}")
    return Report(
        headline=headline,
        plays=plays,
        insights=insights,
        facts=list(book.values()),
        missing=missing,
        line_count=len(lines),
        source_name=source_name,
        title="10월 9-11일 추가 인사이트",
        subtitle="애플 DRAM, 광통신, 주말 인터뷰를 이어서 증류",
        doc_header="10/9-11 추가 인사이트  ·  퀵코멘트 · 주말 인터뷰",
    )


def write_combined(base_md: Path, follow_md: Path, dest: Path) -> None:
    base = base_md.read_text(encoding="utf-8") if base_md.exists() else ""
    follow = follow_md.read_text(encoding="utf-8") if follow_md.exists() else ""
    dest.write_text(base.rstrip() + "\n\n---\n\n" + follow, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="10월 9일 이후 코멘트를 추가 증류한다.")
    parser.add_argument("--source", type=Path, default=DEFAULT_FOLLOW)
    parser.add_argument("--md", type=Path, default=OUT_MD)
    parser.add_argument("--docx", type=Path, default=OUT_DOCX)
    parser.add_argument("--json", type=Path, default=OUT_JSON)
    parser.add_argument("--base-md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--combined", type=Path, default=COMBINED_MD)
    args = parser.parse_args()
    raw = args.source.read_text(encoding="utf-8")
    report = build_followup_report(raw, args.source.name)
    write_report(report, args.md, args.docx, args.json)
    write_combined(args.base_md, args.md, args.combined)
    print(
        f"lines={report.line_count} facts={len(report.facts)} "
        f"insights={len(report.insights)} missing={len(report.missing)}"
    )
    print(report.headline)
    if report.missing:
        print("missing", ",".join(report.missing))


if __name__ == "__main__":
    main()
