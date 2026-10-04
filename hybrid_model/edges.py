"""패널 장점만 남긴 목표 지수.

채점에서 떨어진 축은 기권이다. 함수는 그날 그 사람이 가리키는 코스피를
돌려주고, None 이면 그 날은 경로를 밀지 않는다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable, Sequence

from hybrid_model.model import ScoredPanel

SAMSUNG_LAST = date(2026, 10, 8)
HYNIX_LAST = date(2026, 10, 15)
TURN_LATE = date(2026, 10, 20)
MIDTERM = date(2026, 11, 3)


@dataclass(frozen=True)
class Tape:
    day: date
    kospi: float
    us10y: float
    foreign_week: float
    samsung_on: bool
    hynix_on: bool
    core_cpi: float | None
    weekly_close: float | None
    sessions_after_gap: int
    kospi_at_gap: float | None


VoteFn = Callable[[Tape], float | None]


@dataclass(frozen=True)
class Edge:
    name: str
    strength: str
    rule: str
    weight: float
    vote: VoteFn

    def cast(self, tape: Tape) -> float | None:
        """그날의 목표 코스피. 기권이면 None."""
        if self.weight <= 0:
            return None
        return self.vote(tape)


def _in_gap(tape: Tape) -> bool:
    return not tape.hynix_on and tape.sessions_after_gap <= 8


def _lee_yh(tape: Tape) -> float | None:
    if tape.samsung_on or tape.hynix_on:
        return 7050 if tape.kospi < 7100 else 7000
    if tape.foreign_week > 0:
        return 7300
    if _in_gap(tape):
        return 6700
    return None


def _yoon(tape: Tape) -> float | None:
    if tape.samsung_on or tape.hynix_on:
        return 7020
    if tape.foreign_week > 0:
        return 7250
    if _in_gap(tape):
        return 6750
    return None


def _hwang(tape: Tape) -> float | None:
    if tape.day >= TURN_LATE and tape.foreign_week > 0:
        return 7250
    if tape.kospi >= 7100:
        return 6980
    if tape.day >= TURN_LATE and not tape.hynix_on:
        return 6880
    return None


def _lee_jh(tape: Tape) -> float | None:
    if tape.weekly_close is not None and tape.weekly_close >= 7200:
        return 7600
    if tape.kospi >= 7000:
        return 6960
    return None


def _park_bc(tape: Tape) -> float | None:
    if tape.kospi <= 6100:
        return 5900
    if tape.kospi >= 7100:
        return 6880
    return None


def _park_hs(tape: Tape) -> float | None:
    if tape.kospi >= 7300:
        return 7150
    if tape.kospi <= 6600:
        return 6750
    if not tape.hynix_on and tape.foreign_week > 0:
        return 7300
    return None


def _park_gh(tape: Tape) -> float | None:
    if tape.kospi >= 7500:
        return 7300
    if tape.us10y >= 5.3:
        return 6800
    return None


def _cpi_hot(tape: Tape) -> bool:
    return tape.core_cpi is not None and tape.core_cpi > 0.2


def _hong(tape: Tape) -> float | None:
    if _cpi_hot(tape):
        return 6600
    if tape.us10y < 5.0:
        return None
    return 6880 if tape.kospi >= 7100 else 6920


def _al(tape: Tape) -> float | None:
    if tape.kospi <= 6400:
        return 6600
    if _cpi_hot(tape):
        return 6620 if tape.day < MIDTERM else 6900
    return 6720 if tape.day < MIDTERM else 7350


def _kang(tape: Tape) -> float | None:
    if tape.us10y < 5.0:
        return 7400
    return None


def _eun(tape: Tape) -> float | None:
    if tape.us10y < 5.0:
        return None
    if tape.core_cpi is not None and tape.core_cpi > 0.2:
        return 6400
    return 6780


def _kim_hg(tape: Tape) -> float | None:
    if tape.samsung_on or tape.hynix_on:
        return 7040
    if tape.foreign_week > 0 and not _cpi_hot(tape):
        return None
    if _cpi_hot(tape):
        return 6500
    return 6760


def _lee_ys(tape: Tape) -> float | None:
    if _in_gap(tape) or tape.kospi >= 7200:
        return None
    return 7180


def _kim_jy(tape: Tape) -> float | None:
    if _in_gap(tape) or tape.kospi >= 7100:
        return None
    return 7050


def _han(tape: Tape) -> float | None:
    if tape.kospi < 6800 and tape.us10y >= 5.0:
        return 6900
    return None


def _lee_gh(tape: Tape) -> float | None:
    if tape.kospi < 6800 and 5.0 <= tape.us10y <= 5.5:
        return 6950
    return None


def _kim_ms(tape: Tape) -> float | None:
    if tape.day.month in (10, 11):
        return 6900
    return None


def _silent(_: Tape) -> None:
    return None


# 장점 한 줄, 규칙 한 줄, 투표. 없는 이름은 기권.
_RULES: dict[str, tuple[str, str, VoteFn]] = {
    "이영훈": (
        "자사주가 매도를 받아 주는 구조를 읽는다",
        "자사주 중엔 7,050. 소진 후 8세션은 6,700. 외인 주간 플러스면 7,300",
        _lee_yh,
    ),
    "윤지호": (
        "자사주 소진일을 직접 계산한다",
        "자사주 중엔 7,020. 소진 후 8세션은 6,750. 외인 플러스면 7,250",
        _yoon,
    ),
    "황유현": (
        "되돌림 저항과 10월 중하순 변곡",
        "7,100 위는 6,980으로 되돌림. 10/20 이후 외인 플러스면 7,250, 아니면 6,880",
        _hwang,
    ),
    "이진호": (
        "7,200 주봉이 유일한 돌파선",
        "주봉 7,200 전엔 7,000 위에서 6,960. 주봉 안착 뒤에만 7,600",
        _lee_jh,
    ),
    "박병창": (
        "7,100~7,500 분할매도, 6,100 이탈 매도",
        "7,100 이상이면 6,880. 6,100 이하면 5,900. 그 사이는 기권",
        _park_bc,
    ),
    "박현상": (
        "7,500 박스와 자사주 종료 후 외인 복귀",
        "7,300 위는 7,150. 6,600 아래는 6,750. 소진 후 외인 플러스면 7,300",
        _park_hs,
    ),
    "박근형": (
        "뉴스 소화와 7,500 매물대",
        "7,500 위는 7,300. 10Y 5.3 이상이면 6,800. 그 외 기권",
        _park_gh,
    ),
    "홍춘욱": (
        "고점에서는 인하가 없고 장은 재미없다",
        "10Y 5% 위면 6,920, 지수가 7,100 위면 6,880",
        _hong,
    ),
    "알상무": (
        "10월은 조심, 11/3 중간선거 뒤가 낫다",
        "11/3 전 6,720. 이후 7,350. 6,400 아래면 6,600에서 받음",
        _al,
    ),
    "강건우": (
        "5.0 사이렌과 인상=불확실성 해소",
        "10Y 5% 아래일 때만 7,400. 사이렌이 켜진 동안은 기권",
        _kang,
    ),
    "이은택": (
        "조건①은 켜졌고 조건②는 CPI",
        "10Y 5% 위면 6,780. 근원 CPI MoM 0.2 초과면 6,400",
        _eun,
    ),
    "김학균": (
        "환원은 바닥 장치이고 랠리 동력이 아니다",
        "자사주 중엔 7,040. 걷히고 외인이 없으면 6,760. 외인 플러스면 기권",
        _kim_hg,
    ),
    "이영수": (
        "P→Q, 전고점은 올해 말이 아니다",
        "공백 8세션에는 기권. 그 외 7,200 아래면 7,180",
        _lee_ys,
    ),
    "김장열": (
        "부족은 맞고 레벨은 상단으로 치우친다",
        "공백 8세션과 7,100 위에는 기권. 그 외 목표는 7,050",
        _kim_jy,
    ),
    "한지영": (
        "금리 레벨보다 속도",
        "6,800이 깨지고 10Y가 5% 위일 때만 6,900으로 되돌림",
        _han,
    ),
    "이건희": (
        "5%는 뉴노멀",
        "6,800이 깨지고 10Y가 5.0~5.5일 때만 6,950",
        _lee_gh,
    ),
    "김민수": (
        "대형 IPO가 유동성을 흡수한다",
        "10~11월 목표는 6,900",
        _kim_ms,
    ),
}

_SILENT: dict[str, str] = {
    "문남중": "연준 경로는 다섯 번 기각. 그 축으로는 투표하지 않음",
    "박세익": "4.5% 임계는 폐기. 금리 레벨 투표 없음",
    "문홍철": "4분기 금리 하락은 기각",
    "이선엽": "구두 수치는 버림",
    "빈센트": "적중 0. FIMA·표결 규칙은 없음",
    "박명석": "결론과 기전이 어긋나 방향 규칙을 만들지 않음",
    "김대호": "기전 오류. 방향 규칙 없음",
    "김광석": "잭슨홀 매파를 놓쳐 10월 규칙을 두지 않음",
    "박사주": "반증 불가 명제는 시뮬에서 제외",
    "이건규": "FOMC는 부분 적중뿐이라 경로 규칙 없음",
    "Quick 코멘트": "1층은 높지만 10월 방향 규칙은 없음",
    "김중손": "채점에서 장점 규칙을 뽑지 않음",
}


def _weight(panel: ScoredPanel) -> float:
    if panel.composite is not None:
        return panel.composite
    return panel.shrunk


def build_edges(panels: Sequence[ScoredPanel]) -> tuple[Edge, ...]:
    edges: list[Edge] = []
    for panel in panels:
        rule = _RULES.get(panel.name)
        if rule is None:
            reason = _SILENT.get(panel.name, "10월 경로에 쓸 장점이 없음")
            edges.append(Edge(panel.name, reason, "기권", 0.0, _silent))
            continue
        strength, text, vote = rule
        edges.append(Edge(panel.name, strength, text, _weight(panel), vote))
    return tuple(edges)
