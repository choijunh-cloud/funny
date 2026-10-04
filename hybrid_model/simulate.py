"""장점 규칙을 하루씩 겹쳐 10/6~12/30 경로를 만든다.

그날 목표들의 가중 평균을 만들고, 종가는 그 목표와의 간격의 12%를 좁힌다.
기준 경로는 10Y 5.28·외인 주간 -8.42를 유지한다.
B는 10/16에 10Y 4.90, 10/22에 외인 주간 +3.
C는 10/14에 10Y 5.40·외인 -12·근원 CPI 0.35.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from hybrid_model.edges import HYNIX_LAST, SAMSUNG_LAST, Edge, Tape, build_edges
from hybrid_model.market import KRX_HOLIDAYS, SNAPSHOT
from hybrid_model.model import ScoredPanel

STEP = 0.12
START = date(2026, 10, 6)
END = date(2026, 12, 30)
HOLIDAYS = KRX_HOLIDAYS | {date(2026, 12, 25)}
MARKS = (
    date(2026, 10, 8),
    date(2026, 10, 16),
    date(2026, 10, 30),
    date(2026, 11, 13),
    date(2026, 11, 30),
    date(2026, 12, 30),
)


@dataclass(frozen=True)
class Exog:
    name: str
    foreign_steps: tuple[tuple[date, float], ...]
    yield_steps: tuple[tuple[date, float], ...]
    cpi_day: date | None
    cpi: float | None


BASE = Exog("기준", (), (), None, None)
BULL = Exog("B", ((date(2026, 10, 22), 3.0),), ((date(2026, 10, 16), 4.90),), None, None)
BEAR = Exog(
    "C",
    ((date(2026, 10, 14), -12.0),),
    ((date(2026, 10, 14), 5.40),),
    date(2026, 10, 14),
    0.35,
)


@dataclass(frozen=True)
class Point:
    day: date
    kospi: float


@dataclass(frozen=True)
class PanelSim:
    name: str
    strength: str
    rule: str
    weight: float
    solo_end: float | None
    solo_min: float | None
    avg_vote: float | None
    contribution: float


@dataclass(frozen=True)
class PathSim:
    name: str
    points: tuple[Point, ...]
    end: float
    low: float
    low_day: date

    def mark(self, day: date) -> float | None:
        for point in self.points:
            if point.day == day:
                return point.kospi
        return None


@dataclass(frozen=True)
class Bundle:
    panels: tuple[PanelSim, ...]
    paths: tuple[PathSim, ...]


def trading_days(start: date = START, end: date = END) -> tuple[date, ...]:
    days: list[date] = []
    day = start
    while day <= end:
        if day.weekday() < 5 and day not in HOLIDAYS:
            days.append(day)
        day += timedelta(days=1)
    return tuple(days)


def _lookup(steps: tuple[tuple[date, float], ...], day: date, default: float) -> float:
    value = default
    for stamp, level in steps:
        if day >= stamp:
            value = level
    return value


def _tape(day: date, kospi: float, exog: Exog, weekly_close: float | None, sessions_after_gap: int, kospi_at_gap: float | None) -> Tape:
    return Tape(
        day=day,
        kospi=kospi,
        us10y=_lookup(exog.yield_steps, day, SNAPSHOT.us10y),
        foreign_week=_lookup(exog.foreign_steps, day, SNAPSHOT.foreign_week_tn),
        samsung_on=day <= SAMSUNG_LAST,
        hynix_on=day <= HYNIX_LAST,
        core_cpi=exog.cpi if exog.cpi_day is not None and day >= exog.cpi_day else None,
        weekly_close=weekly_close,
        sessions_after_gap=sessions_after_gap,
        kospi_at_gap=kospi_at_gap,
    )


def run_path(
    edges: tuple[Edge, ...],
    exog: Exog,
    only: str | None = None,
) -> tuple[PathSim, dict[str, float], dict[str, list[float]]]:
    kospi = SNAPSHOT.kospi
    weekly_close: float | None = SNAPSHOT.kospi
    sessions_after_gap = 0
    kospi_at_gap: float | None = None
    points = [Point(date(2026, 10, 2), kospi)]
    low = kospi
    low_day = points[0].day
    contribution = {edge.name: 0.0 for edge in edges}
    votes: dict[str, list[float]] = {edge.name: [] for edge in edges}
    active = [edge for edge in edges if edge.weight > 0 and (only is None or edge.name == only)]
    for day in trading_days():
        if not (day <= HYNIX_LAST):
            sessions_after_gap += 1
            if kospi_at_gap is None:
                kospi_at_gap = kospi
        else:
            sessions_after_gap = 0
        tape = _tape(day, kospi, exog, weekly_close, sessions_after_gap, kospi_at_gap)
        casts: list[tuple[Edge, float]] = []
        for edge in active:
            bias = edge.cast(tape)
            if bias is None:
                continue
            casts.append((edge, bias))
            votes[edge.name].append(bias)
        if casts:
            den = sum(edge.weight for edge, _ in casts)
            target = sum(edge.weight * aim for edge, aim in casts) / den
            move = STEP * (target - kospi)
            for edge, aim in casts:
                contribution[edge.name] += STEP * (edge.weight / den) * (aim - kospi)
            kospi += move
        if day.weekday() == 4:
            weekly_close = kospi
        points.append(Point(day, kospi))
        if kospi < low:
            low = kospi
            low_day = day
    marked = tuple(point for point in points if point.day in MARKS or point.day == date(2026, 10, 2))
    return (
        PathSim(exog.name if only is None else only, marked, kospi, low, low_day),
        contribution,
        votes,
    )


def run_bundle(panels: tuple[ScoredPanel, ...]) -> Bundle:
    edges = build_edges(panels)
    base, contribution, votes = run_path(edges, BASE)
    bull, _, _ = run_path(edges, BULL)
    bear, _, _ = run_path(edges, BEAR)
    rows: list[PanelSim] = []
    for edge in edges:
        if edge.weight <= 0:
            rows.append(PanelSim(edge.name, edge.strength, edge.rule, 0.0, None, None, None, 0.0))
            continue
        solo, _, _ = run_path(edges, BASE, only=edge.name)
        sample = votes[edge.name]
        avg = sum(sample) / len(sample) if sample else None
        rows.append(
            PanelSim(
                edge.name,
                edge.strength,
                edge.rule,
                edge.weight,
                solo.end,
                solo.low,
                avg,
                contribution[edge.name],
            )
        )
    return Bundle(tuple(rows), (base, bull, bear))


def format_sim(bundle: Bundle) -> str:
    lines = ["", "장점 시뮬  10/6~12/30  ·  하루 종가는 가중 목표까지 간격의 12%를 좁힘", ""]
    lines.append("합산 경로")
    header = "  날짜      " + "  ".join(f"{path.name:>6}" for path in bundle.paths)
    lines.append(header)
    days = [point.day for point in bundle.paths[0].points]
    for day in days:
        cells = []
        for path in bundle.paths:
            level = path.mark(day)
            cells.append(f"{level:8,.0f}" if level is not None else f"{'':>8}")
        lines.append(f"  {day.isoformat()}  " + "  ".join(cells))
    for path in bundle.paths:
        lines.append(f"  {path.name} 저점 {path.low:,.0f} ({path.low_day.isoformat()})  종가 {path.end:,.0f}")
    lines.append("")
    lines.append("패널별 장점  ·  혼자 돌린 12/30  ·  합산 기준경로 기여")
    voting = [row for row in bundle.panels if row.weight > 0]
    voting.sort(key=lambda row: -abs(row.contribution))
    for row in voting:
        if row.avg_vote is None:
            lines.append(f"  {row.name:<8} 가중 {row.weight:.2f}  기준 경로에서는 구간이 안 닿아 기권")
            lines.append(f"           {row.strength}")
            continue
        lines.append(
            f"  {row.name:<8} 가중 {row.weight:.2f}  평균목표 {row.avg_vote:,.0f}  "
            f"혼자 {row.solo_end:,.0f}  기여 {row.contribution:+,.0f}pt"
        )
        lines.append(f"           {row.strength}")
    silent = [row.name for row in bundle.panels if row.weight <= 0]
    lines.append("  기권: " + ", ".join(silent))
    return "\n".join(lines) + "\n"


def sim_html(bundle: Bundle) -> str:
    head = "".join(f"<th>{path.name}</th>" for path in bundle.paths)
    rows = []
    for day in [point.day for point in bundle.paths[0].points]:
        cells = "".join(
            f"<td class='num'>{path.mark(day):,.0f}</td>" if path.mark(day) is not None else "<td></td>"
            for path in bundle.paths
        )
        rows.append(f"<tr><td class='num'>{day.isoformat()}</td>{cells}</tr>")
    people = []
    ordered = sorted(
        (row for row in bundle.panels if row.weight > 0),
        key=lambda row: -abs(row.contribution),
    )
    for row in ordered:
        people.append(
            "<tr>"
            f"<td>{row.name}</td>"
            f"<td>{row.strength}<br><span class='mut'>{row.rule}</span></td>"
            f"<td class='num'>{row.weight:.2f}</td>"
            f"<td class='num'>{row.solo_end:,.0f}</td>"
            f"<td class='num'>{row.contribution:+,.0f}</td>"
            "</tr>"
        )
    return (
        "<h2>15 · 장점만 모아 돌린 시뮬</h2><div class='card'>"
        "<p class='mut'>각 목표는 그 사람이 맞힌 축만 쓴다. 종가는 매일 가중 목표까지 간격의 12%를 좁힌다. "
        "기준은 10Y 5.28·외인 -8.42 유지. B는 10/16에 10Y 4.90, 10/22에 외인 +3. "
        "C는 10/14에 10Y 5.40·외인 -12·근원 CPI 0.35.</p>"
        f"<table><thead><tr><th>날짜</th>{head}</tr></thead><tbody>{''.join(rows)}</tbody></table>"
        "<table><thead><tr><th>패널</th><th>장점 · 규칙</th><th>가중</th><th>혼자 12/30</th><th>기준 기여</th></tr></thead>"
        f"<tbody>{''.join(people)}</tbody></table></div>"
    )

