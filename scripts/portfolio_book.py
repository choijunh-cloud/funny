"""9/21 스터디 실행 북.

9/3 하이브리드 H2 + 9/5 Book C를 뼈대로 두고,
9/16 FOMC 인상 · 9/18 종가 · 10Y 터치 · 유가 100을 반영한다.

규칙
  준혁 프레임은 덮어쓰지 않는다.
  삼전닉스는 10월 전 추가 금지. 이미 있으면 홀드.
  신규 자금: 한금융 > 네이버 > 모비스 > 한전.
  한미·레인보우·2차전지는 넣지 않는다.
  IB/게스트 가격은 목표로 쓰지 않는다.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from insights_data import (
    FRI_BRENT,
    FRI_WTI,
    HYNIX_SEP18,
    KOSPI_SEP18,
    OIL_SIREN,
    SAMSUNG_SEP18,
    TENY_FRI_PRINT,
    TENY_WORKING_HI,
    TENY_WORKING_LO,
)

AS_OF = "2026-09-21"
REF_KRW = 100_000_000  # 1억 원 기준
EQUITY_PCT = 60.0
CASH_PCT = 40.0

# Book C 목표 (주식 슬리브 내부)
BOOK_C = [
    ("SEMI", 45.0),
    ("SHORT_DURATION", 25.0),
    ("OIL_DOWN", 10.0),
    ("HEDGE", 20.0),
]

# 9/3 북 대비 9/18 잠근 종가. 나머지 종가는 9/3 스냅만 있고 잠그지 않음.
PX = {
    "005930": ("9/18", SAMSUNG_SEP18),
    "000660": ("9/18", HYNIX_SEP18),
}

HOLDINGS = [
    {
        "ticker": "CASH",
        "name": "현금·초단기",
        "sleeve": "CASH",
        "book_c": "CASH",
        "weight": 40.0,
        "action": "KEEP",
        "role": "운전석",
        "line": "10Y 워킹밴드 4.95–5.01, WTI 100. 터치에 비중만 줄이는 자리.",
    },
    {
        "ticker": "005930",
        "name": "삼성전자",
        "sleeve": "SEMI",
        "book_c": "SEMI",
        "weight": 10.0,
        "action": "HOLD",
        "role": "코어",
        "line": "9/3 25.0만 → 9/18 26.1만. 배당/1월 축. 10월 전 추가 없음.",
    },
    {
        "ticker": "000660",
        "name": "SK하이닉스",
        "sleeve": "SEMI",
        "book_c": "SEMI",
        "weight": 8.0,
        "action": "HOLD",
        "role": "코어",
        "line": "9/3 159.6만 → 9/18 185.7만. 자사주 축. 추격 매수 금지.",
    },
    {
        "ticker": "402340",
        "name": "SK스퀘어",
        "sleeve": "SEMI",
        "book_c": "SEMI",
        "weight": 4.0,
        "action": "HOLD",
        "role": "클러스터",
        "line": "하이닉스 프록시. 삼성+닉스와 합산 한도. NAV·홀딩 할인.",
    },
    {
        "ticker": "009150",
        "name": "삼성전기",
        "sleeve": "CONNECT",
        "book_c": "SEMI",
        "weight": 3.0,
        "action": "DIP",
        "role": "병목",
        "line": "칩이 아니라 기판. FC-BGA가 랙의 병목.",
    },
    {
        "ticker": "007660",
        "name": "이수페타시스",
        "sleeve": "CONNECT",
        "book_c": "SEMI",
        "weight": 2.0,
        "action": "DIP",
        "role": "연결",
        "line": "AI 가속기 고다층 PCB. 소형. 추격 금지.",
    },
    {
        "ticker": "071050",
        "name": "한국금융지주",
        "sleeve": "NEW",
        "book_c": "SHORT_DURATION",
        "weight": 8.0,
        "action": "BUY1",
        "role": "신규 1",
        "line": "반도체와 상관 낮음. 지금 넣는 돈의 1순위.",
    },
    {
        "ticker": "105560",
        "name": "KB금융",
        "sleeve": "RATES",
        "book_c": "SHORT_DURATION",
        "weight": 4.0,
        "action": "DIP",
        "role": "금리",
        "line": "단기물·환원. 전고점 추격 없음.",
    },
    {
        "ticker": "055550",
        "name": "신한지주",
        "sleeve": "RATES",
        "book_c": "SHORT_DURATION",
        "weight": 3.0,
        "action": "DIP",
        "role": "금리",
        "line": "은행 바스켓 2축. 한금융·KB와 한도 공유.",
    },
    {
        "ticker": "015760",
        "name": "한국전력",
        "sleeve": "NEW",
        "book_c": "OIL_DOWN",
        "weight": 3.5,
        "action": "BUY4",
        "role": "신규 4",
        "line": "선납·송전망. 유가→정책 경로가 잘린 뒤에도 비용 헤지.",
    },
    {
        "ticker": "003490",
        "name": "대한항공",
        "sleeve": "OIL",
        "book_c": "OIL_DOWN",
        "weight": 2.5,
        "action": "DIP",
        "role": "유가",
        "line": "유류비·외화부채. 눌림만. 코어 아님.",
    },
    {
        "ticker": "012330",
        "name": "현대모비스",
        "sleeve": "NEW",
        "book_c": "HEDGE",
        "weight": 5.0,
        "action": "BUY3",
        "role": "신규 3 · Atlas",
        "line": "대당 액추에이터 31. 레인보우 대신 이쪽. 11월 시제품.",
    },
    {
        "ticker": "035420",
        "name": "NAVER",
        "sleeve": "NEW",
        "book_c": "HEDGE",
        "weight": 4.5,
        "action": "BUY2",
        "role": "신규 2",
        "line": "멀티플 압축. 금리 안정 시 가장 빨리 리레이팅.",
    },
    {
        "ticker": "079550",
        "name": "LIG넥스원",
        "sleeve": "HEDGE",
        "book_c": "HEDGE",
        "weight": 1.5,
        "action": "HOLD",
        "role": "방산 헤지",
        "line": "Book C 방어 축. 작게. 테마 추격 금지.",
    },
    {
        "ticker": "034020",
        "name": "두산에너빌리티",
        "sleeve": "HEDGE",
        "book_c": "HEDGE",
        "weight": 1.0,
        "action": "WATCH",
        "role": "전력",
        "line": "왼쪽 꼬리 두꺼움. 추격 금지. 한도가 전부다.",
    },
]

EXCLUDE = [
    ("042700", "한미반도체", "PER 게이트 · 점유율 확인 전 신규 금지"),
    ("277810", "레인보우로보틱스", "Atlas는 모비스. 상용화 전 테마 금지"),
    ("373220", "LG에너지솔루션", "2차전지 고PBR. 어떤 슬리브에도 없음"),
    ("006400", "삼성SDI", "셀 업황 회복 전"),
    ("003600", "SK", "에코플랜트는 할인율 재료. 기본은 스퀘어·닉스"),
    ("196170", "알테오젠", "위성 스터디. 코어 북 아님"),
    ("004020", "현대제철", "위성 TP. 코어 북 아님"),
]

RULES = [
    "이미 삼전닉스가 있으면 팔지 말고, 더 넣지도 않는다.",
    "빈 돈은 한금융 → 네이버 → 모비스 → 한전 순으로만 넣는다.",
    "9/18 급등 뒤 반도체를 새로 사지 않는다.",
    "10Y 5.0–5.3 추세 AND No Way Back 전에는 주식 60을 넘기지 않는다.",
    "oil 120 · Ohio 계약 · IB 목표가로는 비중을 바꾸지 않는다.",
]

PHASE = (
    "Phase 1 박스 운전. KOSPI는 9/3 예상 6,600을 지나 9/18 6,894. "
    "박스 상단 7,150 전이고 10Y는 터치, 유가는 90에서 100대로 올라왔다. "
    "그래서 주식 60을 유지하되 반도체 추격은 접고, 신규 4종목에 실행을 몰아준다."
)


def krw(weight: float) -> int:
    return int(round(REF_KRW * weight / 100.0))


def sleeve_weights() -> dict[str, float]:
    out: dict[str, float] = {}
    for h in HOLDINGS:
        out[h["sleeve"]] = out.get(h["sleeve"], 0.0) + h["weight"]
    return out


def book_c_weights() -> dict[str, float]:
    """주식 60 내부 비중(% of equity)."""
    eq = [h for h in HOLDINGS if h["sleeve"] != "CASH"]
    tot = sum(h["weight"] for h in eq)
    out: dict[str, float] = {}
    for h in eq:
        out[h["book_c"]] = out.get(h["book_c"], 0.0) + h["weight"] / tot * 100.0
    return out


def buy_order() -> list[dict]:
    order = {"BUY1": 1, "BUY2": 2, "BUY3": 3, "BUY4": 4}
    rows = [h for h in HOLDINGS if h["action"] in order]
    return sorted(rows, key=lambda h: order[h["action"]])


def total_weight() -> float:
    return round(sum(h["weight"] for h in HOLDINGS), 4)


def equity_weight() -> float:
    return round(sum(h["weight"] for h in HOLDINGS if h["sleeve"] != "CASH"), 4)


def semi_cluster() -> float:
    names = {"005930", "000660", "402340"}
    return round(sum(h["weight"] for h in HOLDINGS if h["ticker"] in names), 4)


def tape_note() -> str:
    return (
        f"KOSPI {KOSPI_SEP18:,.2f} · 삼성 {SAMSUNG_SEP18/10000:.1f}만 · "
        f"닉스 {HYNIX_SEP18/10000:.1f}만 · 10Y {TENY_WORKING_LO}–{TENY_WORKING_HI} "
        f"(터치 {TENY_FRI_PRINT}) · WTI {FRI_WTI} / Brent {FRI_BRENT} · 사이렌 {OIL_SIREN:.0f} 꺼짐"
    )
