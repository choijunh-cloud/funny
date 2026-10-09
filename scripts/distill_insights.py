#!/usr/bin/env python3
"""방송 대본에서 투자 팩트를 추출하고, 숫자 근거가 있는 인사이트만 증류한다.

원문 타임스탬프를 걷어 낸 뒤 정규식으로 팩트를 뽑는다. 판단 문장에 들어가는
숫자는 그 팩트뿐이며, 대본에 없는 가격·비율은 만들지 않는다.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Mm, Pt, RGBColor

KR_FONT = "맑은 고딕"
NAVY = RGBColor(0x0F, 0x20, 0x43)
NAVY2 = RGBColor(0x1E, 0x40, 0x7C)
GOLD = RGBColor(0xB8, 0x94, 0x3A)
GRAY = RGBColor(0x4B, 0x55, 0x63)
DARK = RGBColor(0x1A, 0x1A, 0x1A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x16, 0x65, 0x34)
RED = RGBColor(0x99, 0x1B, 0x1B)
AMBER = RGBColor(0x7A, 0x5C, 0x12)

NAVY_HEX = "0F2043"
NAVY2_HEX = "1E407C"
GOLD_HEX = "B8943A"
LIGHT_HEX = "EEF2F8"
GREEN_HEX = "E8F5E9"
RED_HEX = "FDECEA"
AMBER_HEX = "FFF8E7"
BLUE_HEX = "E8F1FB"
ROW_HEX = "F7F9FC"
WHITE_HEX = "FFFFFF"

TIMESTAMP_LINE = re.compile(
    r"^(?:"
    r"\d+:\d{2}(?::\d{2})?"
    r"|\d+초"
    r"|\d+분(?: \d+초)?"
    r"|\d+시간(?: \d+분)?(?: \d+초)?"
    r")$"
)
STAGE_LINE = re.compile(r"^\[[^\]]+\]$")
NUMBER_TOKEN = re.compile(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d+")

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "sources" / "paste_copy_2-2.txt"
DEFAULT_MD = ROOT / "lectures" / "10월 8일 투자 인사이트.md"
DEFAULT_DOCX = ROOT / "lectures" / "10월 8일 투자 인사이트.docx"
DEFAULT_JSON = ROOT / "lectures" / "10월 8일 투자 인사이트.json"


@dataclass(frozen=True)
class FactSpec:
    id: str
    label: str
    pattern: str
    required: bool = False


@dataclass(frozen=True)
class Fact:
    id: str
    label: str
    value: str


@dataclass
class Insight:
    title: str
    stance: str
    horizon: str
    verdict: str
    action: str
    avoid: str
    facts: list[Fact] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Play:
    when: str
    then: str


@dataclass
class Report:
    headline: str
    plays: list[Play]
    insights: list[Insight]
    facts: list[Fact]
    missing: list[str]
    line_count: int
    source_name: str

    def to_json(self) -> dict:
        payload = asdict(self)
        payload["insights"] = [
            {k: v for k, v in item.items() if k != "keywords"} for item in payload["insights"]
        ]
        return payload


FACTS: list[FactSpec] = [
    FactSpec("foreign_today", "외인 당일", r"외인은 오늘도 (2조원 정도 팔았습니다)", True),
    FactSpec("foreign_nxt", "NXT 포함", r"(2조 5천억원 팔았)"),
    FactSpec("foreign_prev", "직전일", r"직전일은 (2조 6천억원 팔았)"),
    FactSpec("foreign_week", "이번 주 3일", r"이번주에 (6조 넘게 팔았습니다)", True),
    FactSpec("foreign_month", "최근 한 달", r"한 달 동안 지금 (29조를 팔았어요)"),
    FactSpec("retail", "개인", r"(3조 9천억을 샀어요)"),
    FactSpec("flow_since", "매도 재개", r"(한 달 반 전부터 다시 팔기 시작했죠)"),
    FactSpec("kospi_close", "코스피 종가", r"(6625)로 코스피는 끝났", True),
    FactSpec("session_high", "시초 부근", r"오늘은 시작을 (6,800)에서"),
    FactSpec("session_low", "장 마감 부근", r"마지막에 (6,600)까지 내려갔어요"),
    FactSpec("band", "깨진 하단", r"(6753)이 하단이었는데"),
    FactSpec("worst", "최악 각오", r"한 (6200)까지도 진짜 안 좋으면"),
    FactSpec("ladder", "분할 구간", r"(6500, 6400, 6300) 정도에서 사는 것"),
    FactSpec("rally", "랠리 창", r"(11월, 12월 초) 이럴 때 랠리", True),
    FactSpec("ust", "미국 10년", r"그런데 지금은 (5\.3)이에요", True),
    FactSpec("ust_old", "금리 출발점", r"(4%를 안 넘었습니다)"),
    FactSpec("ust_weeks", "금리 주봉", r"(6주 동안 계속 금리가)"),
    FactSpec("trigger", "매수 확인선", r"10년물 기준으로 (5\.10 아래)", True),
    FactSpec("auction", "10년 입찰", r"어제 오전에 (5\.25, 5\.27)이었다가"),
    FactSpec("auction_high", "입찰 고점", r"(5\.36)까지 올라갔다가"),
    FactSpec("duration", "10년 듀레이션", r"듀레이션이 (8\.2 정도)"),
    FactSpec("samsung_op", "분기 영업이익", r"분기 (107조 4천억)이 나오네요", True),
    FactSpec("samsung_usd", "달러 환산", r"(780억불)의 영업"),
    FactSpec("nvda_bar", "엔비디아 가이던스", r"가이던스를 보면 (700억 불)이거든요"),
    FactSpec("sales", "매출 추정", r"삼성전자 이번에 (195조 매출)"),
    FactSpec("mem_sales", "메모리 매출", r"(140조 정도)가 메모리"),
    FactSpec("mem_op", "메모리 영업이익", r"메모리 반도체가 한 (113조 정도) 영업"),
    FactSpec("foundry", "파운드리+LSI", r"LSI는 (1\.45조 정도 적자)"),
    FactSpec("dx", "DX 적자", r"(3\.5조 이상 적자)"),
    FactSpec("q4", "4분기 메모리", r"(125조 이상) 메모리 반도체에서만"),
    FactSpec("next_year", "내년 메모리", r"(500조 이상) 메모리"),
    FactSpec("model", "내부 모델", r"한 (106조 정도) 나오더라고요"),
    FactSpec("daily", "하루 영업이익", r"하루에 (1조 2천억)씩"),
    FactSpec("sec_px", "삼성 가격", r"(26만 3천원), 하이닉스"),
    FactSpec("hynix_px", "하이닉스 가격", r"하이닉스는 (168만 6천원)"),
    FactSpec("undervalued", "밸류 표현", r"굉장히 너무 (저평가) 돼 있다고"),
    FactSpec("not_now", "타이밍", r"그런데 (지금은 아닌 것 같다)"),
    FactSpec("hynix_trim", "하이닉스 축소", r"(200만원에 파시죠)"),
    FactSpec("surprise", "실적일 반응", r"(영업이 30% 이상 많았을 때)"),
    FactSpec("buyback", "자사주", r"(15조인데 조금 더 하기로)"),
    FactSpec("dividend", "특별배당", r"특별 배당 (30조)를 받겠"),
    FactSpec("etf", "반도체 ETF", r"규모가 한 (19조원) 되고"),
    FactSpec("deposit", "예탁금", r"여전히 (100조 때)는 유지를 하고"),
    FactSpec("hbm3e", "HBM3E", r"한 (2불 정도) 할 겁니다"),
    FactSpec("hbm4", "HBM4", r"HBM 4가 이제 (3불에서 5불)"),
    FactSpec("hbm_asp", "HBM ASP", r"(120% 이상) HBM 가격이 오르는"),
    FactSpec("fcf_when", "FCF 해소", r"그 원인은 (내년 상반기)에는 해소"),
    FactSpec("rebound", "다음 주", r"(주가가 상승할 수 있고)"),
    FactSpec("box", "당일 박스", r"(6,800도 깨지면)"),
    FactSpec("kosdaq_line", "코스닥 선", r"(코스닥 900)"),
    FactSpec("agent_cpu", "에이전트 CPU", r"에이젠틱 AI는 (1억 2천만 개)"),
    FactSpec("gen_cpu", "생성형 CPU", r"생성 AI가 (3천만)"),
    FactSpec("tpu_ext", "구글 외부 판매", r"내년에 (200 한 4, 50만 개)"),
    FactSpec("tsmc_24", "TSMC 2024", r"설비 투자가 (240억 불)"),
    FactSpec("tsmc_26", "TSMC 올해", r"올해가 (680억 불)이에요"),
    FactSpec("tsmc_26b", "TSMC 올해 다른 언급", r"올해가 지금 (650억 불)입니다"),
    FactSpec("tsmc_27", "TSMC 내년", r"내년이 (780억 불)입니다"),
    FactSpec("per_kr", "국내 소부장 PER", r"한 (27배)"),
    FactSpec("per_gl", "해외 장비 PER", r"해외 기업들이 한 (40배점)"),
    FactSpec("jusung_op", "주성 이익 대비", r"(17억인가 나온다)"),
    FactSpec("tier1", "장비 선택", r"지금은 (1등 기업) 조하는게 맞"),
    FactSpec("greenfield", "공장 사이클", r"우리가 (그린 필드)라고"),
    FactSpec("solidigm_sales", "솔리다임 매출", r"매출이 대충한 (250억 달러)"),
    FactSpec("solidigm_ni", "솔리다임 순익", r"(120억 달러 이상)의 순익"),
    FactSpec("solidigm_own", "잔여 지분", r"(80% 이상) 가져가게 되면"),
    FactSpec("openai_net", "오픈AI 순액", r"연환산 매출이 약 (500억 달러)에 근접", True),
    FactSpec("openai_gross", "비교용 총액", r"연환산 매출이 (700억 달러)에 근접했다고"),
    FactSpec("sox", "반도체 지수", r"(SOX -3\.4%)"),
    FactSpec("ndx", "나스닥", r"(나스닥 -1\.25%)"),
    FactSpec("ndx100", "나스닥 100", r"나스닥 백직수가 (1\.39% 하락)"),
    FactSpec("mu_day", "마이크론 당일", r"보시면은 (4\.8%)"),
    FactSpec("commit", "앤트로픽 약정", r"투자해야 될 돈이 (5,180억)"),
    FactSpec("ust_extreme", "국채 고점 표현", r"국채 금리가 (5\.35%)를 기록"),
    FactSpec("eunma", "은마 실거래", r"실거래가는 (31억 3천만 원)"),
    FactSpec("gold_then", "2005년 금 수량", r"금 (48kg)이 있어야"),
    FactSpec("gold_now", "현재 금 수량", r"(18kg)에 금이 있으면"),
    FactSpec("variable", "주담대 변동", r"변동 금리가 (76\.5%)"),
    FactSpec("pay_low", "금리 2.45% 상환", r"2\.45%일 때는 (157만 원)"),
    FactSpec("pay_high", "금리 6.89% 상환", r"(263만 원)입니다"),
    FactSpec("defense", "미국 국방비", r"국방비는 (8,700억 달러)"),
    FactSpec("interest", "미국 이자", r"26년 전망치는 (1조 390억 달러)"),
    FactSpec("mu_dd", "마이크론 고점 대비", r"고점 대비 (10% 조금 빠졌을 뿐)"),
    FactSpec("kr_dd", "한국 메모리 낙폭", r"우리나라는 아직도 (30% 이상 정도)"),
    FactSpec("adr", "ADR 괴리", r"개리가 (40%가 넘어섰어요)"),
    FactSpec("power", "전력 공기", r"전력은 한 (7년 정도)"),
    FactSpec("dc_time", "데이터센터 공기", r"지어지는게 한 (2년 정도면)"),
    FactSpec("spx_bond", "스페이스X 채권", r"(300억 달러)는 채권"),
    FactSpec("spx_loan", "스페이스X 대출", r"(100억 달러)가 대출"),
    FactSpec("lockup", "스페이스X 락업", r"한 (11월 말)까지는 계속"),
    FactSpec("wti", "WTI", r"WTI가 (4\.7%)"),
    FactSpec("fx", "원달러 방향", r"(위쪽으로 잡을 겁니다)"),
    FactSpec("oracle", "오라클", r"(141달러)인데 오라클"),
    FactSpec("kosdaq_trade", "코스닥 매매", r"(888) 갔을 때 잠깐 샀습니다"),
    FactSpec("nvda_sales", "엔비디아 매출", r"매출 (962억 달러)"),
    FactSpec("nvda_dc", "엔비디아 데이터센터", r"데이터센터 매출 (890억 달러)"),
    FactSpec("nvda_yoy", "엔비디아 성장", r"각각 (106%, 117%) 성장"),
    FactSpec("avgo", "브로드컴 경로", r"(2027회계연도 1,150억 달러, 2028회계연도 2,300억 달러)"),
    FactSpec("nvda_margin", "엔비디아 마진", r"(65% 마진)이 더 올라가기"),
    FactSpec("confirm_day", "확정 실적일", r"(10월 29일)"),
    FactSpec("halo", "알테오젠 이슈", r"(할로자임)이 승소를 했습니다"),
    FactSpec("eu_ban", "유럽 판매", r"(유럽 여덟 개 국가)"),
    FactSpec("peptron", "펩트론", r"(펩트론) 이런 건 났는데"),
    FactSpec("early_retail", "장 초반 개인", r"개인 투자자는 (4,578억 원) 순수"),
]


def clean_transcript(raw: str) -> list[str]:
    spoken: list[str] = []
    for line in raw.splitlines():
        text = line.strip()
        if not text or TIMESTAMP_LINE.fullmatch(text) or STAGE_LINE.fullmatch(text):
            continue
        spoken.append(text)
    return spoken


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()


def extract_facts(flat: str) -> tuple[dict[str, Fact], list[str]]:
    found: dict[str, Fact] = {}
    missing: list[str] = []
    for spec in FACTS:
        match = re.search(spec.pattern, flat)
        if not match:
            missing.append(spec.id)
            if spec.required:
                raise LookupError(f"필수 팩트를 대본에서 찾지 못했습니다: {spec.id} / {spec.pattern}")
            continue
        value = match.group(1)
        if value not in flat:
            raise LookupError(f"추출값이 원문에 없습니다: {spec.id}={value}")
        found[spec.id] = Fact(spec.id, spec.label, value)
    return found, missing


def stitch(text: str) -> str:
    """대본 문장 조각이 그대로 붙을 때 마침표를 넣는다."""
    text = re.sub(
        r"(습니다|입니다|했습니다|했어요|했죠|해요|하죠|시죠|예요|이죠|거죠|거예요|아요|어요)(\s+)(?=[가-힣A-Za-z0-9])",
        r"\1. ",
        text,
    )
    return re.sub(r"\s+", " ", text).strip()


def numbers_of(text: str) -> set[str]:
    return set(NUMBER_TOKEN.findall(text))


def assert_grounded(text: str, flat: str, where: str) -> None:
    for token in numbers_of(text):
        if token not in flat and token.replace(",", "") not in flat.replace(",", ""):
            raise LookupError(f"{where}에 대본에 없는 숫자가 있습니다: {token}")


def similar(left: str, right: str) -> float:
    return SequenceMatcher(None, left[:90], right[:90]).ratio()


def pick_evidence(lines: list[str], keywords: list[str], facts: list[Fact], limit: int = 3) -> list[str]:
    values = [fact.value for fact in facts if len(fact.value) >= 10]
    scored: list[tuple[int, int, str]] = []
    for index, line in enumerate(lines):
        if len(line) < 36 or len(line) > 220:
            continue
        if any(noise in line for noise in ("웃음", "죄송합니다", "물리학", "빛의 속도")):
            continue
        keyword_hits = sum(1 for word in keywords if word in line)
        fact_hits = sum(1 for value in values if value and value in line)
        if keyword_hits == 0 and fact_hits == 0:
            continue
        score = keyword_hits + fact_hits * 3
        if re.search(r"\d", line):
            score += 1
        if any(word in line for word in ("생각", "봅니다", "어렵", "아니", "확인", "반등", "팔았", "사도")):
            score += 1
        scored.append((score, index, line))
    scored.sort(key=lambda item: (-item[0], item[1]))
    chosen: list[str] = []
    for _, _, line in scored:
        if any(similar(line, prev) > 0.62 for prev in chosen):
            continue
        chosen.append(line)
        if len(chosen) >= limit:
            break
    return chosen


def fact_list(book: dict[str, Fact], ids: list[str]) -> list[Fact]:
    return [book[item] for item in ids if item in book]


def join_facts(book: dict[str, Fact], ids: list[str]) -> str:
    return " · ".join(f"{book[item].label} {book[item].value}" for item in ids if item in book)


def build_insights(book: dict[str, Fact], lines: list[str]) -> list[Insight]:
    def has(*ids: str) -> bool:
        return all(item in book for item in ids)

    def v(fid: str) -> str:
        return book[fid].value

    insights: list[Insight] = []

    insights.append(
        Insight(
            title="가격은 실적이 아니라 사는 사람이 정한다",
            stance="관망",
            horizon="이번 주~다음 주",
            verdict=(
                "삼성 이익이 커도 외인이 팔면 빠지는 구간이다. "
                f"당일 외인은 {v('foreign_today')} "
                f"NXT를 더하면 {v('foreign_nxt')}고, 직전일은 {v('foreign_prev')}다. "
                f"이번 주는 {v('foreign_week')} 최근 한 달은 {v('foreign_month')} "
                f"개인은 {v('retail')} "
                + (f"{v('flow_since')} " if has("flow_since") else "")
                + "주간 순매도가 줄거나 돌기 전에는 강한 상승을 실적만으로 보지 않는다."
            ),
            action="보유는 유지한다. 외인 주간 매도가 누그러진 뒤에 비중을 늘린다. 신용으로 연휴를 넘기는 매수는 피한다.",
            avoid="‘세계에서 가장 많이 버니 내일 오른다’로 당일 신규 베팅하지 않는다.",
            facts=fact_list(
                book,
                ["foreign_today", "foreign_nxt", "foreign_prev", "foreign_week", "foreign_month", "retail", "flow_since", "early_retail"],
            ),
            keywords=["외인", "외국인", "순매도", "6조", "개인"],
        )
    )

    insights.append(
        Insight(
            title="삼성은 싸 보여도 지금은 조건이 아니다",
            stance="조건부 매수",
            horizon="조건 완화 이후",
            verdict=(
                (f"화자의 밸류 표현은 {v('undervalued')}이고, 타이밍 표현은 {v('not_now')}. " if has("undervalued", "not_now") else "")
                + "같이 말한 조건은 차트, 외국인 매도, 실적 확인, 나스닥, 높은 금리다. "
                + join_facts(book, ["sec_px", "hynix_px", "kospi_close", "session_high", "session_low"])
                + ". 이 중 몇 개가 풀리면 아래에서 평단을 낮추는 자리다."
            ),
            action=(
                "비관일에 고점이 아니라 아래에서 나누어 산다. "
                + (f"하이닉스는 210만 원에서 손절하지 않고, 줄인다면 {v('hynix_trim')} " if has("hynix_trim") else "")
                + (f"코스닥 ‘{v('kosdaq_trade')}’가 화자의 매매이고, 코스피에는 같은 숫자 매매를 쓰지 않는다." if has("kosdaq_trade") else "")
            ),
            avoid="코스피를 666 같은 숫자 미신으로 사지 않는다. 시황에 나온 당일 종목을 추격하지 않는다.",
            facts=fact_list(book, ["undervalued", "not_now", "sec_px", "hynix_px", "kospi_close", "hynix_trim", "kosdaq_trade", "band"]),
            keywords=["저평가", "지금은 아닌", "26만", "하이닉스", "손절"],
        )
    )

    insights.append(
        Insight(
            title="금리 하락을 상상해서 미리 사지 않는다",
            stance="관망",
            horizon="10년물 확인 이후",
            verdict=(
                f"미국 10년은 {v('ust')}이다. "
                + (f"반년 전 비교는 {v('ust_old')}이고, 그 뒤 {v('ust_weeks')} 높아졌다. " if has("ust_old", "ust_weeks") else "")
                + (f"주식은 {v('trigger')}로 내려온 뒤에 본다. " if has("trigger") else "")
                + (f"직전 10년 입찰은 {v('auction')}에서 {v('auction_high')} 올랐다. 한글 시황의 입찰 호조와 금리 상승은 따로 읽는다." if has("auction", "auction_high") else "")
            ),
            action="금리가 실제로 내려온 것을 보고 주식을 산다. 입찰 직후 되돌림만으로 추세 전환이라고 쓰지 않는다.",
            avoid="프랑스 한 나라 탓으로 원인을 좁히지 않는다. 금리 수준보다 누가 그 금리를 견디는지가 붕괴 조건이다.",
            facts=fact_list(book, ["ust", "ust_old", "ust_weeks", "trigger", "auction", "auction_high", "duration", "ust_extreme"]),
            keywords=["금리", "5.3", "5.10", "입찰", "국채"],
        )
    )

    insights.append(
        Insight(
            title="삼성 실적의 본체는 메모리다",
            stance="구조적 긍정",
            horizon="4분기~내년",
            verdict=(
                f"잠정으로 말한 분기 영업이익은 {v('samsung_op')}"
                + (f", 달러 환산은 {v('samsung_usd')}" if has("samsung_usd") else "")
                + (f"이다. 엔비디아 가이던스 {v('nvda_bar')}을 이번 분기에 넘었다는 비교다. " if has("nvda_bar") else ". ")
                + "사업부 추정은 "
                + join_facts(book, ["sales", "mem_sales", "mem_op", "foundry", "dx", "q4", "next_year", "daily", "model"])
                + ". DX와 파운드리 적자는 인정하되, 지금 주가의 기준점은 메모리 쪽이라는 판단이다."
            ),
            action=(
                (f"확정 숫자는 {v('confirm_day')}에 사업부 믹스를 확인한다. " if has("confirm_day") else "")
                + (f"엔비디아 {v('nvda_margin')}은 더 오르기 어렵다는 말이 삼성 이익 규모 비교의 근거다." if has("nvda_margin") else "")
            ),
            avoid="스마트폰·가전 적자만으로 메모리 업황 피크라고 쓰지 않는다.",
            facts=fact_list(
                book,
                ["samsung_op", "samsung_usd", "nvda_bar", "sales", "mem_sales", "mem_op", "foundry", "dx", "q4", "next_year", "daily", "model", "confirm_day", "nvda_margin"],
            ),
            keywords=["107조", "메모리", "영업", "DX", "파운드리"],
        )
    )

    insights.append(
        Insight(
            title="같은 날 시계가 세 개다",
            stance="조건부 매수",
            horizon="다음 주 / 내년 상반기",
            verdict=(
                "단기 시황은 차트·외인·금리가 풀리기 전 관망이다. "
                + (f"실적 게스트는 자사주와 리밸런싱이 끝나면 {v('rebound')} 라고 본다. " if has("rebound") else "")
                + (f"전고점을 누르던 하이퍼스케일러 현금흐름 마이너스는 {v('fcf_when')}에 해소된다고 말한다. " if has("fcf_when") else "")
                + (f"장중 베팅은 {v('box')} 안 되는 것, {v('kosdaq_line')} 사수, 갭 상승 뒤 오후에 다시 밀리지 않는 것이다." if has("box") else "")
            ),
            action="콘텐츠에는 ‘내일 급등’과 ‘내년 상반기 전고점’을 한 문장으로 붙이지 않는다. 시계를 나눠 쓴다.",
            avoid="자사주가 끝나면 무조건 수급 공백이라는 한 방향만 쓰지 않는다. 외국인은 자사주가 받아 줄 때 오히려 비중을 줄인다는 반대 해석이 같은 대본에 있다.",
            facts=fact_list(book, ["rebound", "fcf_when", "box", "kosdaq_line", "buyback", "dividend", "etf", "deposit", "surprise"]),
            keywords=["다음 주", "상반기", "자사주", "리밸런싱", "6,800"],
        )
    )

    insights.append(
        Insight(
            title="HBM은 마진보다 판가가 이익을 키운다",
            stance="구조적 긍정",
            horizon="내년",
            verdict=(
                "마이크론 공시 기준으로 HBM이 섞인 데이터센터 메모리 마진은 스마트폰·PC용보다 낮다. "
                + (f"단가는 HBM3E {v('hbm3e')}, HBM4 {v('hbm4')}. " if has("hbm3e", "hbm4") else "")
                + (f"블렌디드 가격은 {v('hbm_asp')} 쪽으로 말한다. " if has("hbm_asp") else "")
                + (f"에이전트 AI CPU는 생성형 {v('gen_cpu')} 대비 {v('agent_cpu')}라 D램 수요가 커진다는 논리다." if has("gen_cpu", "agent_cpu") else "")
            ),
            action="구글 TPU와 엔비디아가 동시에 늘면 메모리 공급자가 양쪽을 먹는 구도로 쓴다. 엔비디아 점유율 희석과 메모리 물량 증가를 같은 뉴스로 보지 않는다.",
            avoid="HBM 마진이 범용보다 낮다는 사실만으로 삼성 메모리 이익이 꺾인다고 쓰지 않는다.",
            facts=fact_list(book, ["hbm3e", "hbm4", "hbm_asp", "gen_cpu", "agent_cpu", "tpu_ext", "fcf_when"]),
            keywords=["HBM", "2불", "5불", "프리캐시", "TPU"],
        )
    )

    insights.append(
        Insight(
            title="소부장은 1등과 기판만, 방송 당일은 추격하지 않는다",
            stance="조건부 매수",
            horizon="수주가 매출로 바뀌는 동안",
            verdict=(
                (f"국면은 {v('greenfield')}라 전공정 장비가 먼저고 패키징이 뒤따른다. 선택은 {v('tier1')}. " if has("greenfield", "tier1") else "")
                + "순서는 장비, 부품, 소재다. "
                + (f"밸류는 국내 {v('per_kr')}, 해외 {v('per_gl')}까지 좁혀졌다. " if has("per_kr", "per_gl") else "")
                + (f"주성은 {v('jusung_op')} 대비 주가가 앞서 있다는 지적이다. 밀리면 기판, 특히 ABF와 BT 부족이 탑픽으로 남는다." if has("jusung_op") else "")
            ),
            action=(
                "TSMC 설비투자 언급은 "
                + join_facts(book, ["tsmc_24", "tsmc_26", "tsmc_26b", "tsmc_27"])
                + ". 다음 실적에서 내년 투자와 선단 공정 참여를 확인한다. 기사·방송에 나온 뒤에는 6개월 보유이거나, 그렇지 않으면 1~2주 전 기미에서만 들어간다."
            ),
            avoid="2등·3등 유사 장비를 실적 개선 헤드라인만으로 따라가지 않는다.",
            facts=fact_list(book, ["greenfield", "tier1", "per_kr", "per_gl", "jusung_op", "tsmc_24", "tsmc_26", "tsmc_26b", "tsmc_27"]),
            keywords=["소부장", "장비", "1등", "기판", "TSMC", "27배"],
        )
    )

    insights.append(
        Insight(
            title="섹터 온도는 2차전지·로봇과 바이오·조선이 다르다",
            stance="비중 축소",
            horizon="4분기~내년 1월",
            verdict=(
                "2차전지는 9월 북미 물량이 3분기 숫자에는 덜 반영되고 4분기부터 보이므로, 3분기 실적 실망은 매수 기회로 말하는 쪽이 있다. "
                "LG에너지솔루션의 긴 횡보 이탈을 업황 신호로 보고 본체보다 가벼운 소재를 매매한다. "
                + (f"바이오는 {v('halo')} 이후 {v('eu_ban')} 판매 제한 가능성이 알테오젠과 키트루다SC로 연결된다. " if has("halo", "eu_ban") else "")
                + (f"{v('peptron')} 수급이 말라 내년 초까지 펀드가 담기 어렵다는 경고가 있다. " if has("peptron") else "")
                + "조선·방산·원전·전력은 수급이 반도체 대기에 묶여 있고, 로봇은 상대적으로 덜 빠진다."
            ),
            action="바이오 대형 낙폭은 회사 설명 전 추격 매수하지 않고, 반등하면 비중을 줄인다. 조선은 깊게 빠진 자리의 소량 채움까지만 연다.",
            avoid="오늘 오른 2차전지를 차트 좋은 주식으로 일반화하지 않는다. LNG 단가 하락은 주가가 안 갈 때 붙는 설명으로 취급한다.",
            facts=fact_list(book, ["halo", "eu_ban", "peptron"]),
            keywords=["알테오젠", "펩트론", "2차전지", "조선", "로봇", "기판"],
        )
    )

    insights.append(
        Insight(
            title="솔리다임은 단기 악재, 가치는 지분과 보상에 달렸다",
            stance="조건부 매수",
            horizon="상장 구조가 구체화될 때",
            verdict=(
                "주관사 보도가 나올 때마다 흔들려 단기 악재로 취급한다. 회사는 주주 피해가 나면 보상하겠다는 기존 메시지를 반복했다. "
                + (f"숫자로 말한 규모는 매출 {v('solidigm_sales')}, 순익 {v('solidigm_ni')}이다. " if has("solidigm_sales", "solidigm_ni") else "")
                + (f"구주 매각 뒤 {v('solidigm_own')} 연결로 남으면 숨은 스토리지 가치가 본사에 붙을 수 있다는 반대 해석이 있다." if has("solidigm_own") else "")
            ),
            action="루머 당일 하락을 펀더멘털 훼손으로 쓰지 않는다. 신주·구주 비율, 미국 투자 사용처, 잔여 지분, 주주 보상안이 나온 뒤에 판단한다.",
            avoid="국내 중복상장 트라우마와 미국 ADR 반응을 같은 방향으로 단정하지 않는다.",
            facts=fact_list(book, ["solidigm_sales", "solidigm_ni", "solidigm_own"]),
            keywords=["솔리다임", "IPO", "250억", "희석", "보상"],
        )
    )

    insights.append(
        Insight(
            title="오픈AI 500억은 매출 급감이 아니다",
            stance="노이즈",
            horizon="금요일 미국장~월요일 국내",
            verdict=(
                f"회사 자료로 말한 순액 연환산은 {v('openai_net')}이다. "
                + (f"앞서 유통된 {v('openai_gross')}는 앤트로픽 총액 방식에 맞춘 비교용 환산이다. " if has("openai_gross") else "")
                + "순액은 파트너 몫을 뺀 자기 몫만 매출이고, 총액은 결제액 전체를 매출로 잡은 뒤 파트너 몫을 비용 처리한다. "
                + "같은 날 가격은 "
                + " · ".join(v(item) for item in ("sox", "ndx", "ndx100", "mu_day") if has(item))
                + ". 실적이 줄어 주가가 빠진 것이 아니라, 기대가 먼저 들어가 있던 자리에 수익 회수 의심이 붙은 촉매다."
            ),
            action="헤드라인은 ‘쇼크’ 대신 ‘집계 기준 혼선’으로 고친다. 확인할 숫자는 매출총이익, 영업이익, 잉여현금흐름, 클라우드 의무다.",
            avoid="공매도 유도로 단정하지 않는다. 당일 공매도 잔고는 월 2회·시차 공개라 바로 확인되지 않는다.",
            facts=fact_list(book, ["openai_net", "openai_gross", "sox", "ndx", "ndx100", "mu_day", "commit", "nvda_sales", "nvda_dc", "nvda_yoy", "avgo"]),
            keywords=["오픈AI", "500억", "700억", "순액", "총액", "앤트로픽"],
        )
    )

    insights.append(
        Insight(
            title="한국 메모리 낙폭을 미국 수요 붕괴로 읽지 않는다",
            stance="구조적 긍정",
            horizon="분기 실적마다",
            verdict=(
                (f"미국 마이크론은 고점 대비 {v('mu_dd')}이고, 한국 메모리는 {v('kr_dd')} 빠져 있다. " if has("mu_dd", "kr_dd") else "")
                + (f"하이닉스 ADR과 본주의 괴리는 {v('adr')}. " if has("adr") else "")
                + "못 가는 이유로 말한 것은 수요 실종이 아니라 2028년 증설 의심이다. "
                + (f"데이터센터는 {v('dc_time')} 끝나도 전력은 {v('power')} 걸린다." if has("dc_time", "power") else "전력·지역 민원·선거가 일정을 늦춘다.")
            ),
            action="회복은 한 방에 전고점을 회복하는 그림보다, 분기 실적마다 신뢰를 쌓는 그림으로 쓴다. 수요 문장은 강하게, 일정 문장은 분리한다.",
            avoid="고점 대비 한국 낙폭만 보고 업황 종료라고 쓰지 않는다.",
            facts=fact_list(book, ["mu_dd", "kr_dd", "adr", "dc_time", "power"]),
            keywords=["고점 대비", "ADR", "전력은 한", "마이크론 테크놀로지"],
        )
    )

    insights.append(
        Insight(
            title="돈 가치와 금리, 한국은 타격이 빠르다",
            stance="구조",
            horizon="고금리 지속",
            verdict=(
                "명목 자산 상승의 일부를 화폐 가치 하락으로 다시 계산하라는 강의다. "
                + (f"은마 실거래는 {v('eunma')}. " if has("eunma") else "")
                + (f"같은 집을 금으로 재면 과거 {v('gold_then')}, 지금은 {v('gold_now')}이다. " if has("gold_then", "gold_now") else "")
                + (f"미국 10년은 {v('ust_extreme')}를 기록했다는 표현까지 나온다. " if has("ust_extreme") else "")
                + (f"미국 이자 비용은 국방비 {v('defense')}를 넘었고 전망은 {v('interest')}다. " if has("defense", "interest") else "")
                + (f"한국 신규 주담대 변동 비중 {v('variable')}, 같은 대출의 상환액이 {v('pay_low')}에서 {v('pay_high')}으로 뛰는 예가 있다." if has("variable", "pay_low", "pay_high") else "")
            ),
            action="원화 가격 배수를 성과로 쓰기 전에 달러·금 기준을 한 줄 붙인다. 한국 기업·가계는 짧은 차입과 변동금리다.",
            avoid="지난 40년의 금리 하락 규칙으로 레버리지를 설명하지 않는다. 예금만으로 자산을 모으던 시대로 되돌리지 않는다.",
            facts=fact_list(book, ["eunma", "gold_then", "gold_now", "ust_extreme", "defense", "interest", "variable", "pay_low", "pay_high"]),
            keywords=["은마", "48kg", "18kg", "가짜돈", "변동 금리", "1조 390억"],
        )
    )

    insights.append(
        Insight(
            title="레벨과 하지 않을 베팅",
            stance="관망",
            horizon="11월, 12월 초",
            verdict=(
                f"하락은 급락보다 지루한 하락을 예상하고, 랠리 창은 {v('rally')}다. "
                + (f"최악은 {v('worst')}까지이고, 나누어 살 자리는 {v('ladder')}이다. " if has("worst", "ladder") else "")
                + (f"이번 주 하단으로 잡았던 {v('band')}은 이미 깨졌다. " if has("band") else "")
                + "원유는 베팅하지 않고, 금은 20주선이 구름 아래로 빠진 동안 롱을 열지 않는다. "
                + (f"원달러는 {v('fx')}." if has("fx") else "")
            ),
            action="현금이 있으면 6천원 단위로 조바심 손절하지 않고 평단을 낮춘다. 11월·12월 초 창에서 줄이는 쪽을 열어 둔다.",
            avoid=(
                "WTI "
                + (f"{v('wti')} " if has("wti") else "")
                + "같은 뉴스 맞수에는 방향을 걸지 않는다. "
                + (f"오라클 {v('oracle')}와 GPU 담보 차입, 스페이스X의 칩 매수용 빚은 낙관 재료로 포장하지 않는다." if has("oracle") else "")
            ),
            facts=fact_list(book, ["rally", "worst", "ladder", "band", "fx", "wti", "oracle", "spx_bond", "spx_loan", "lockup"]),
            keywords=["12월 초", "6500, 6400", "6200까지", "위쪽으로", "4.7%", "141달러", "20주선"],
        )
    )

    for insight in insights:
        insight.evidence = pick_evidence(lines, insight.keywords, insight.facts)
    return insights


def build_plays(book: dict[str, Fact]) -> list[Play]:
    def v(fid: str, fallback: str) -> str:
        return book[fid].value if fid in book else fallback

    return [
        Play(f"외인이 이번 주에도 {v('foreign_week', '크게')} 같은 규모로 팔면", "강한 상승 베팅을 미룬다"),
        Play(f"미국 10년이 {v('trigger', '하락 확인')}로 내려옴", "그때 주식 매수를 검토한다"),
        Play(f"코스피 {v('ladder', '하단 구간')}", "현금으로 평단을 낮춘다"),
        Play(v("rally", "11월, 12월 초"), "랠리 창으로 보고 차익을 준비한다"),
        Play("하이닉스 210만 원 부근", f"손절하지 않는다. 줄인다면 {v('hynix_trim', '더 아래에서 줄인다')}"),
        Play("소부장 종목이 방송·기사에 등장", "당일 추격하지 않고 1등 장비·기판만 고른다"),
        Play("바이오 반등", "비중을 줄인다"),
        Play("2차전지 3분기 실적 실망", "4분기 반영 전 흔들림으로 보고 소재를 살핀다"),
        Play(f"오픈AI {v('openai_net', '순액')} 대 {v('openai_gross', '총액')}", "매출 급감 헤드라인을 쓰지 않는다"),
        Play("금 20주선이 구름 아래", "롱을 열지 않는다"),
        Play("원유 뉴스가 하루 만에 반대로 남", "방향 베팅을 쉰다"),
        Play("솔리다임 상장 루머", "당일 악재로 적되 보상·잔여 지분을 확인한다"),
    ]


def build_headline(book: dict[str, Fact]) -> str:
    def v(fid: str) -> str:
        return book[fid].value if fid in book else ""

    return (
        f"외인은 오늘 {v('foreign_today')} 이번 주는 {v('foreign_week')} "
        f"코스피는 {v('kospi_close')}로 끝났고, 삼성 분기 영업이익으로 말한 숫자는 {v('samsung_op')}이다. "
        f"가격은 {v('undervalued')}로 보지만 타이밍은 {v('not_now')}. "
        f"신규 매수는 10년물 {v('trigger')}를 확인하거나 {v('ladder')}에서 나누어 사고, 창은 {v('rally')}로 연다. "
        f"오픈AI {v('openai_net')}는 매출이 급감한 숫자가 아니라 순액 기준이다."
    )


def build_report(raw: str, source_name: str) -> Report:
    lines = clean_transcript(raw)
    flat = normalize("\n".join(lines))
    book, missing = extract_facts(flat)
    insights = build_insights(book, lines)
    headline = stitch(build_headline(book))
    plays = [Play(stitch(play.when), stitch(play.then)) for play in build_plays(book)]
    for insight in insights:
        insight.verdict = stitch(insight.verdict)
        insight.action = stitch(insight.action)
        insight.avoid = stitch(insight.avoid)
    assert_grounded(headline, flat, "헤드라인")
    for play in plays:
        assert_grounded(play.when + play.then, flat, f"플레이북 {play.when}")
    for insight in insights:
        blob = "\n".join([insight.verdict, insight.action, insight.avoid, insight.title])
        assert_grounded(blob, flat, insight.title)
        for fact in insight.facts:
            if fact.value not in flat:
                raise LookupError(f"{insight.title} 팩트가 원문에 없습니다: {fact.value}")
        for quote in insight.evidence:
            if normalize(quote) not in flat:
                raise LookupError(f"원문 앵커가 대본에 없습니다: {quote}")
    return Report(
        headline=headline,
        plays=plays,
        insights=insights,
        facts=list(book.values()),
        missing=missing,
        line_count=len(lines),
        source_name=source_name,
    )


def render_markdown(report: Report) -> str:
    lines = [
        "# 10월 8일 투자 인사이트",
        "",
        "방송 대본을 코드로 추출·증류한 결과다. 카드에 적힌 숫자는 대본에서 찾은 표현 그대로다. 공시와 대조하기 전의 발언이다.",
        "",
        f"- 발화 문장 {report.line_count}개",
        f"- 추출 팩트 {len(report.facts)}개",
        f"- 증류 카드 {len(report.insights)}개",
        f"- 패턴은 있으나 이번 대본에서 못 찾은 항목 {len(report.missing)}개",
        "",
        "## 증류",
        "",
        report.headline,
        "",
        "## 조건과 행동",
        "",
        "| 조건 | 행동 |",
        "| --- | --- |",
    ]
    for play in report.plays:
        lines.append(f"| {play.when} | {play.then} |")
    lines += ["", "## 카드", ""]
    for index, insight in enumerate(report.insights, start=1):
        lines += [
            f"### {index}. {insight.title}",
            "",
            f"- 스탠스: {insight.stance}",
            f"- 시계: {insight.horizon}",
            "",
            insight.verdict,
            "",
            f"행동: {insight.action}",
            "",
            f"쓰지 않을 문장: {insight.avoid}",
            "",
            "| 항목 | 대본 표현 |",
            "| --- | --- |",
        ]
        for fact in insight.facts:
            lines.append(f"| {fact.label} | {fact.value} |")
        if insight.evidence:
            lines += ["", "원문 앵커:"]
            for quote in insight.evidence:
                lines.append(f"- {quote}")
        lines.append("")
    if report.missing:
        lines += ["## 이번 대본에서 비어 있는 패턴", "", ", ".join(report.missing), ""]
    lines.append("출처 파일: `" + report.source_name + "`")
    lines.append("")
    return "\n".join(lines)


def set_run_font(run, size=11, bold=False, color=DARK, font=KR_FONT):
    run.font.name = font
    run._element.rPr.rFonts.set(qn("w:eastAsia"), KR_FONT)
    run._element.rPr.rFonts.set(qn("w:ascii"), font)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), font)
    run.font.size = Pt(size)
    run.bold = bold
    run.font.color.rgb = color


def shade_cell(cell, fill: str) -> None:
    cell._tc.get_or_add_tcPr().append(
        parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{fill}"/>')
    )


def set_cell_margins(cell, top=60, bottom=60, left=80, right=80) -> None:
    cell._tc.get_or_add_tcPr().append(
        parse_xml(
            f'<w:tcMar {nsdecls("w")}>'
            f'<w:top w:w="{top}" w:type="dxa"/>'
            f'<w:left w:w="{left}" w:type="dxa"/>'
            f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
            f'<w:right w:w="{right}" w:type="dxa"/>'
            f"</w:tcMar>"
        )
    )


def set_table_borders(table, color="D0D7E2", sz="4") -> None:
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:right w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f"</w:tblBorders>"
    )
    table._tbl.tblPr.append(borders)


def cell_text(cell, text, size=10, bold=False, color=DARK, align="left") -> None:
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.alignment = {
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
    }[align]
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.space_before = Pt(0)
    run = paragraph.add_run(str(text))
    set_run_font(run, size=size, bold=bold, color=color)
    set_cell_margins(cell)


def add_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)
    for index, header in enumerate(headers):
        cell = table.rows[0].cells[index]
        shade_cell(cell, NAVY_HEX)
        cell_text(cell, header, size=9, bold=True, color=WHITE, align="center")
    for row_index, row in enumerate(rows):
        for col_index, value in enumerate(row):
            cell = table.rows[row_index + 1].cells[col_index]
            shade_cell(cell, ROW_HEX if row_index % 2 else WHITE_HEX)
            cell_text(cell, value, size=9, bold=(col_index == 0))
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(6)


def add_callout(doc: Document, title: str, body: list[str], kind: str) -> None:
    palette = {
        "key": (NAVY_HEX, LIGHT_HEX, NAVY),
        "bull": ("166534", GREEN_HEX, GREEN),
        "bear": ("991B1B", RED_HEX, RED),
        "note": (GOLD_HEX, AMBER_HEX, AMBER),
        "blue": (NAVY2_HEX, BLUE_HEX, NAVY2),
    }
    accent, fill, title_color = palette[kind]
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell = table.cell(0, 0)
    shade_cell(cell, fill)
    cell._tc.get_or_add_tcPr().append(
        parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:top w:val="nil"/>'
            f'<w:left w:val="single" w:sz="28" w:space="0" w:color="{accent}"/>'
            f'<w:bottom w:val="nil"/>'
            f'<w:right w:val="nil"/>'
            f"</w:tcBorders>"
        )
    )
    set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
    cell.text = ""
    first = cell.paragraphs[0]
    first.paragraph_format.space_after = Pt(2)
    run = first.add_run(title)
    set_run_font(run, size=10, bold=True, color=title_color)
    for line in body:
        paragraph = cell.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(1)
        paragraph.paragraph_format.space_before = Pt(0)
        run = paragraph.add_run(line)
        set_run_font(run, size=10.5, color=DARK)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_after = Pt(4)


def stance_kind(stance: str) -> str:
    return {
        "관망": "note",
        "조건부 매수": "blue",
        "구조적 긍정": "bull",
        "구조": "key",
        "비중 축소": "bear",
        "노이즈": "note",
    }.get(stance, "key")


def render_docx(report: Report, path: Path) -> None:
    doc = Document()
    section = doc.sections[0]
    section.page_width = Mm(210)
    section.page_height = Mm(297)
    section.left_margin = Mm(16)
    section.right_margin = Mm(16)
    section.top_margin = Mm(16)
    section.bottom_margin = Mm(16)
    normal = doc.styles["Normal"]
    normal.font.name = KR_FONT
    normal.font.size = Pt(11)
    normal.font.color.rgb = DARK
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), KR_FONT)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run("10/8 투자 인사이트  ·  대본 추출 · 증류")
    set_run_font(run, size=8.5, color=GRAY)

    core = doc.core_properties
    core.title = "10월 8일 투자 인사이트"
    core.author = "준혁"
    core.subject = "지표추적자·삼성 실적·오픈AI 매출 논란 증류"

    def paragraph(text: str, size=11, bold=False, color=DARK, before=0, after=6, align="left"):
        para = doc.add_paragraph()
        para.alignment = {
            "left": WD_ALIGN_PARAGRAPH.LEFT,
            "center": WD_ALIGN_PARAGRAPH.CENTER,
        }[align]
        para.paragraph_format.space_before = Pt(before)
        para.paragraph_format.space_after = Pt(after)
        para.paragraph_format.line_spacing = 1.15
        run_ = para.add_run(text)
        set_run_font(run_, size=size, bold=bold, color=color)
        return para

    def heading(text: str, size=16):
        para = paragraph(text, size=size, bold=True, color=NAVY, before=12, after=6)
        para._p.get_or_add_pPr().append(
            parse_xml(
                f'<w:pBdr {nsdecls("w")}>'
                f'<w:bottom w:val="single" w:sz="12" w:space="1" w:color="{NAVY_HEX}"/>'
                f"</w:pBdr>"
            )
        )

    paragraph("10월 8일 투자 인사이트", size=20, bold=True, color=NAVY, after=2, align="center")
    paragraph("추출한 숫자만 남기고 행동으로 증류", size=11, color=GRAY, after=8, align="center")
    paragraph(
        f"발화 {report.line_count}문장  ·  팩트 {len(report.facts)}개  ·  카드 {len(report.insights)}개",
        size=10,
        color=GRAY,
        align="center",
    )
    add_callout(doc, "증류", [report.headline], "key")
    heading("조건과 행동")
    add_table(doc, ["조건", "행동"], [[play.when, play.then] for play in report.plays])

    for index, insight in enumerate(report.insights, start=1):
        heading(f"{index}. {insight.title}")
        add_callout(
            doc,
            f"{insight.stance}  ·  {insight.horizon}",
            [insight.verdict, f"행동  {insight.action}", f"제외  {insight.avoid}"],
            stance_kind(insight.stance),
        )
        if insight.facts:
            paragraph("대본에서 뽑은 표현", size=12, bold=True, color=NAVY2, before=4, after=3)
            add_table(doc, ["항목", "대본 표현"], [[fact.label, fact.value] for fact in insight.facts])
        if insight.evidence:
            paragraph("원문 앵커", size=12, bold=True, color=NAVY2, before=2, after=3)
            for quote in insight.evidence:
                paragraph("· " + quote, size=9.5, color=GRAY, after=2)

    paragraph(
        "숫자는 대본 부분문자열만 사용했다. 발언이며 공시 대조 전이다. 출처: " + report.source_name,
        size=9,
        color=GRAY,
        before=8,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(path)


def write_report(report: Report, md_path: Path, docx_path: Path, json_path: Path) -> None:
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(render_markdown(report), encoding="utf-8")
    json_path.write_text(json.dumps(report.to_json(), ensure_ascii=False, indent=2), encoding="utf-8")
    render_docx(report, docx_path)
    with zipfile.ZipFile(docx_path) as package:
        package.read("word/document.xml")


def main() -> None:
    parser = argparse.ArgumentParser(description="방송 대본에서 투자 인사이트를 추출·증류한다.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--docx", type=Path, default=DEFAULT_DOCX)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    args = parser.parse_args()
    raw = args.source.read_text(encoding="utf-8")
    report = build_report(raw, args.source.name)
    write_report(report, args.md, args.docx, args.json)
    print(f"lines={report.line_count} facts={len(report.facts)} insights={len(report.insights)} missing={len(report.missing)}")
    print(report.headline)
    print(f"md={args.md}")
    print(f"docx={args.docx}")


if __name__ == "__main__":
    main()
