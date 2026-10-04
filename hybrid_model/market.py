"""10/2 좌표, 레벨 사다리, 자사주 시계.

자사주 시계는 잔여 금액 ÷ 일일 페이스로 세션 수를 센다.
첫 세션은 10/2 다음 거래일이다. KRX 휴장(10/5 개천절 대체휴일, 10/9 한글날)을 넣으면
하이닉스 8번째 세션은 10/16이다. 원장이 적은 ~10/15는 10/6 개장부터 주말 빼고
10/9를 영업일로 센 날짜라, 그 앵커도 같이 돌려준다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

MARKET_ASOF = date(2026, 10, 2)
DOCUMENT_ASOF = date(2026, 10, 4)
REOPEN = date(2026, 10, 6)

# 10/3 개천절은 토요일이고, 대체휴일이 10/5다. 한글날은 10/9 금요일.
KRX_HOLIDAYS = frozenset({date(2026, 10, 5), date(2026, 10, 9)})


@dataclass(frozen=True)
class Market:
    asof: date = MARKET_ASOF
    kospi: float = 7003.74
    kospi_change_pct: float = 0.46
    us10y: float = 5.28
    us10y_intraday_high: float = 5.34
    us30y: float = 5.63
    usdkrw: float = 1350.6
    brent: float = 102.0
    foreign_ytd_tn: float = -190.5
    foreign_month_tn: float = -20.0
    foreign_week_tn: float = -8.42
    foreign_day_tn: float = -0.14
    individual_day_tn: float = -1.79
    oct_hike_prob: float = 0.19
    micron_beat: bool = True
    micron_reaction_pct: float = -3.0
    micron_guide_bn: float = 61.5
    core_cpi_mom: float | None = None
    july_headline_cpi: float = 3.4
    samsung_op_tn: float | None = None
    samsung_reaction_pct: float | None = None
    weekly_close: float | None = None
    dec_hike_prob: float | None = None
    vix: float = 15.3
    export_semi_bn: float = 60.3
    export_semi_yoy: float = 262.8
    export_total_yoy: float = 83.5


SNAPSHOT = Market()


@dataclass(frozen=True)
class Level:
    name: str
    price: float
    role: str
    source: str
    live: bool = True


LEVELS: tuple[Level, ...] = (
    Level("박현상 박스 상단", 7500, "resistance", "박현상 · 박병창 분할매도 상단"),
    Level("황유현 50% 되돌림", 7324, "resistance", "황유현"),
    Level("이진호 주봉 시한", 7200, "breakout", "이진호 · 박병창 분할매도 하단은 7,100"),
    Level("박병창 분할매도 하단", 7100, "resistance", "박병창"),
    Level("10/2 종가", 7003.74, "spot", "실측"),
    Level("9/30 저점", 6838, "support", "추석 후"),
    Level("9/2 저점", 6562, "support", "C 시나리오 이탈선"),
    Level("박현상 전저점", 6300, "support", "6,300~6,400 · 알상무 하단 6,200"),
    Level("알상무 저점 하단", 6200, "support", "알상무 6,400~6,200"),
    Level("박병창 이탈 매도", 6100, "trigger", "6,000~6,100 트리거. 거리 −13.6%는 중점 6,050"),
    Level("하이브리드 v1.0 폐기선", 5263, "floor", "박세익 저점. v1.1 사다리에서 뺌", live=False),
)

SELL_TRIGGER_MID = 6050.0


@dataclass(frozen=True)
class LevelView:
    level: Level
    distance_pct: float


def level_views(spot: float, levels: tuple[Level, ...] = LEVELS) -> tuple[LevelView, ...]:
    return tuple(LevelView(level, (level.price - spot) / spot * 100) for level in levels)


def distance_pct(spot: float, price: float) -> float:
    return (price - spot) / spot * 100


@dataclass(frozen=True)
class Buyback:
    name: str
    budget_tn: float
    spent_tn: float
    clock_remaining_tn: float
    daily_tn: float
    published_date: date
    note: str
    shares_per_day: int | None = None
    drawn_pct: float = 0
    drawn_remaining_tn: float = 0


def _samsung_daily() -> float:
    # 잔여 0.7조를 개장 3세션(10/6~8)에 나눠 쓴다는 것이 시계의 입력이다.
    return 0.7 / 3


BUYBACKS: tuple[Buyback, ...] = (
    Buyback(
        name="삼성전자",
        budget_tn=15.0,
        spent_tn=13.36,
        clock_remaining_tn=0.7,
        daily_tn=_samsung_daily(),
        published_date=date(2026, 10, 8),
        drawn_pct=95,
        drawn_remaining_tn=0.7,
        note=(
            "시계는 잔여 5%(0.7조)를 10/6~8에 소진한다고 둔다. "
            "같이 적힌 13.36조/15조는 잔여 1.64조라 5%와 맞지 않아, 날짜를 만든 0.7조를 시계 입력으로 쓴다."
        ),
    ),
    Buyback(
        name="SK하이닉스",
        budget_tn=40.0,
        spent_tn=30.64,
        clock_remaining_tn=40.0 - 30.64,
        daily_tn=1.2,
        published_date=date(2026, 10, 15),
        shares_per_day=650_000,
        drawn_pct=73,
        drawn_remaining_tn=9.4,
        note=(
            "30.64조/40조면 잔여 9.36조, 일 1.2조면 8세션이다. "
            "막대의 73%(잔여 27%≈10.8조)와 본문의 9.4조는 서로 다르고, 시계는 집행액에서 잔여를 뺀다. "
            "원장 앵커 ~10/15는 10/9 한글날을 영업일로 센 날짜다."
        ),
    ),
)


@dataclass(frozen=True)
class ClockResult:
    name: str
    budget_tn: float
    spent_tn: float
    remaining_tn: float
    daily_tn: float
    sessions: int
    exhaust_date: date
    session_dates: tuple[date, ...]
    published_date: date
    note: str
    shares_per_day: int | None
    implied_price_won: float | None
    reported_remaining_tn: float
    drawn_pct: float = 0
    drawn_remaining_tn: float = 0


def is_trading_day(day: date, holidays: frozenset[date]) -> bool:
    return day.weekday() < 5 and day not in holidays


def iter_sessions(after: date, holidays: frozenset[date]):
    day = after
    while True:
        day += timedelta(days=1)
        if is_trading_day(day, holidays):
            yield day


def session_on(first: date, n: int, holidays: frozenset[date]) -> date:
    """first 를 1번째로 보고 n번째 거래일을 돌려준다."""
    if n < 1:
        raise ValueError("세션 번호는 1 이상")
    if not is_trading_day(first, holidays):
        raise ValueError("첫 세션이 휴장이다")
    day = first
    for _ in range(n - 1):
        day = next(iter_sessions(day, holidays))
    return day


def project_clock(
    program: Buyback,
    asof: date = MARKET_ASOF,
    holidays: frozenset[date] = KRX_HOLIDAYS,
) -> ClockResult:
    if program.daily_tn <= 0:
        raise ValueError("일일 페이스는 양수")
    if program.clock_remaining_tn < 0:
        raise ValueError("잔여는 음수가 될 수 없다")
    dates: list[date] = []
    left = program.clock_remaining_tn
    for session in iter_sessions(asof, holidays):
        dates.append(session)
        left -= program.daily_tn
        if left <= 1e-6:
            break
        if len(dates) > 80:
            raise RuntimeError("소진 시계가 너무 길다")
    implied = None
    if program.shares_per_day:
        implied = program.daily_tn * 1e12 / program.shares_per_day
    return ClockResult(
        name=program.name,
        budget_tn=program.budget_tn,
        spent_tn=program.spent_tn,
        remaining_tn=program.clock_remaining_tn,
        daily_tn=program.daily_tn,
        sessions=len(dates),
        exhaust_date=dates[-1],
        session_dates=tuple(dates),
        published_date=program.published_date,
        note=program.note,
        shares_per_day=program.shares_per_day,
        implied_price_won=implied,
        reported_remaining_tn=program.budget_tn - program.spent_tn,
        drawn_pct=program.drawn_pct,
        drawn_remaining_tn=program.drawn_remaining_tn,
    )


def project_clocks(asof: date = MARKET_ASOF) -> tuple[ClockResult, ...]:
    return tuple(project_clock(program, asof=asof) for program in BUYBACKS)
