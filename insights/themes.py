"""채널 어휘로 코멘트를 테마에 놓는다. 순서는 읽는 순서다."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    key: str
    label: str
    # 판단이 분명할수록 위로. 숫자 밀도는 가중치가 아니다.
    weight: int
    order: int
    keys: tuple[str, ...]
    anchors: tuple[str, ...]


THEMES: tuple[Theme, ...] = (
    Theme(
        "macro_rates",
        "금리와 수요",
        5,
        10,
        ("금리", "국채", "10년", "30년", "연준", "윌리엄스", "PCE", "유가", "WTI", "이란", "호르무즈", "헤지펀드", "구인", "비둘기", "스태그"),
        ("금리", "유가", "연준"),
    ),
    Theme(
        "market_tape",
        "수급과 장세",
        4,
        20,
        ("코스피", "KOSPI", "코스닥", "KOSDAQ", "외국인", "소부장", "눈치", "상승종목", "야간선물", "리밸런싱", "한미반도체", "배당락"),
        ("코스피", "외국인", "수급"),
    ),
    Theme(
        "memory_valuation",
        "메모리 값의 괴리",
        5,
        30,
        ("PER", "프리미엄", "할인", "괴리", "ADR", "환율", "컨센", "BPS", "본주"),
        ("괴리", "할인", "프리미엄", "PER"),
    ),
    Theme(
        "samsung_dispersion",
        "삼성 눈높이의 갈림",
        5,
        40,
        ("유안타", "BNK", "흥국", "초호황", "ASP", "PBR", "ROE", "4Q", "3Q", "3분기"),
        ("초호황", "ASP", "목표주가"),
    ),
    Theme(
        "micron_print",
        "마이크론이 방향",
        5,
        50,
        ("가이던스", "GPM", "QoQ", "510억", "실적발표"),
        ("마이크론",),
    ),
    Theme(
        "hbm",
        "HBM 8단의 뜻",
        5,
        60,
        ("HBM", "8단", "12단", "CoWoS", "피에스케이", "MR-MUF", "리플로우", "베이스 다이", "NCF", "Cube", "큐브"),
        ("HBM", "8단", "병목"),
    ),
    Theme(
        "ai_supply",
        "AI 서버 공급망",
        4,
        70,
        ("리드타임", "ABF", "TrendForce", "MLCC", "기판", "HDD", "HAMR", "Blackwell", "Rubin", "Low-CTE"),
        ("ABF", "리드타임", "기판"),
    ),
    Theme(
        "parts_alliance",
        "부품 공급망 재편",
        2,
        80,
        ("TDK", "Taiyo", "자본제휴", "인덕터"),
        ("TDK", "자본제휴"),
    ),
    Theme(
        "ai_demand",
        "AI가 일을 더 하는 방향",
        4,
        90,
        (
            "Astra",
            "아스트라",
            "dots",
            "닷츠",
            "GPT",
            "소버린",
            "중앙은행",
            "Muse",
            "뮤즈",
            "안전마진",
            "토큰",
            "오픈AI",
            "OpenAI",
            "Optionality",
            "에이전트",
        ),
        ("에이전트", "토큰", "소버린", "메타"),
    ),
    Theme(
        "tesla_fsd",
        "테슬라 유럽 승인",
        4,
        100,
        ("FSD", "TCMV", "전역", "표결", "자동차기술위원회"),
        ("FSD", "전역", "표결"),
    ),
    Theme(
        "tesla_roadster",
        "테슬라 Roadster",
        2,
        110,
        ("Roadster", "로드스터", "냉가스", "부양"),
        ("Roadster", "냉가스"),
    ),
    Theme(
        "equipment",
        "TSMC와 장비 사이클",
        3,
        120,
        ("TSMC", "2나노", "웰스파고", "Silicon", "실리콘 프레리", "웨이퍼", "N2"),
        ("2나노", "TSMC", "장비"),
    ),
    Theme(
        "sofc",
        "전력과 SOFC",
        3,
        130,
        ("Bloom", "SOFC", "코세스", "서진", "비나텍", "두산퓨얼셀", "미코", "연료전지"),
        ("SOFC", "Bloom", "수주"),
    ),
    Theme(
        "sdi",
        "삼성SDI와 ESS",
        3,
        140,
        ("삼성SDI", "ESS", "AMPC", "BBU", "GWh", "제이피", "JP모건", "유상증자"),
        ("ESS", "삼성SDI"),
    ),
    Theme(
        "method",
        "종목을 고르는 체",
        3,
        150,
        ("커버종목", "시총", "수주 이력", "60~80", "수천억"),
        ("커버", "시총", "수주"),
    ),
)

THEME_BY_KEY = {theme.key: theme for theme in THEMES}
