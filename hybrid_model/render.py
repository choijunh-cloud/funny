"""텍스트 보고서와 한 장짜리 HTML.

숫자는 Report 에서만 읽고, 이 파일은 서식을 맡는다.
"""

from __future__ import annotations

from html import escape

from hybrid_model import chapters
from hybrid_model.ledger import AXES, AXIS_LABEL, DISCARDED, OPEN_CALLS
from hybrid_model.market import DOCUMENT_ASOF, SELL_TRIGGER_MID, distance_pct
from hybrid_model.model import Report, ScoredPanel
from hybrid_model.scenarios import CODES, SCENARIOS
from hybrid_model.simulate import format_sim, run_bundle, sim_html


def fmt_weight(value: float) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.1f}"


def fmt_signed(value: float) -> str:
    if abs(value) < 1e-9:
        return "0"
    body = fmt_weight(abs(value))
    return f"+{body}" if value > 0 else f"−{body}"


def fmt_pct(value: float, digits: int = 1) -> str:
    rounded = round(value, digits)
    text = f"{rounded:.{digits}f}"
    if rounded > 0:
        return f"+{text}%"
    return f"{text}%"


def render_text(report: Report) -> str:
    market = report.market
    weights = report.posterior.as_dict()
    prior = dict(report.posterior.prior)
    lines: list[str] = [
        f"하이브리드 v{report.posterior.version}  ·  시장 {market.asof.isoformat()}  ·  문서 {DOCUMENT_ASOF.isoformat()}",
        f"코스피 {market.kospi:,.2f}   10Y {market.us10y:.2f}%   30Y {market.us30y:.2f}%   "
        f"외인 9월 {market.foreign_month_tn:.1f}조 / 주간 {market.foreign_week_tn:.2f}조",
        "",
        f"v{report.posterior.prior_version}  {prior['A']:.0f} / {prior['B']:.0f} / {prior['C']:.0f}"
        f"   →   v{report.posterior.version}  "
        f"A {fmt_weight(weights['A'])}   B {fmt_weight(weights['B'])}   C {fmt_weight(weights['C'])}",
    ]
    if report.posterior.clipped:
        lines.append("음수 가중치가 나와 0으로 자른 뒤 100으로 다시 맞췄다.")
    lines.append("")
    lines.append("요인")
    for factor in report.posterior.factors:
        if factor.tier == "watch" and not factor.active:
            continue
        delta = "  ".join(f"{code} {fmt_signed(value)}" for code, value in factor.delta if abs(value) > 1e-9)
        mark = "코어" if factor.tier == "core" else "감시"
        lines.append(f"  [{mark}] {factor.title}  강도 {factor.intensity:.2f}  {delta}")
        lines.append(f"         {factor.explain}")
    quiet = [factor.title for factor in report.posterior.factors if factor.tier == "watch" and not factor.active]
    if quiet:
        lines.append("  꺼진 감시: " + ", ".join(quiet))
    for flag in report.flags:
        lines.append(f"  참고: {flag}")

    lines.extend(["", "경로  (확률은 위 가중, 밴드는 패널 레벨)"])
    for scenario in report.scenarios:
        path = "  ".join(f"{band.label} {band.low:,.0f}~{band.high:,.0f}" for band in scenario.paths)
        lines.append(f"  {scenario.code} {fmt_weight(weights[scenario.code])}%  {scenario.title}")
        lines.append(f"    {path}")

    lines.extend(["", "채점  본선 N≥6"])
    for panel in report.leaderboard(main=True):
        lines.append(_score_line(panel))
    lines.append("참고군 N<6")
    for panel in report.leaderboard(main=False):
        lines.append(_score_line(panel))

    lines.extend(["", f"종합 점수  (진행중 {OPEN_CALLS}건은 분모 제외)"])
    for panel in report.composite_board():
        lines.append(
            f"  {panel.composite_pct:>3}  {panel.name}  "
            f"적중 {panel.hit_pct}%  N{panel.n}  "
            f"1층 {panel.panel.layer1}  반증 {panel.panel.falsifiability}"
        )

    lines.extend(["", "자사주 시계  (문서 달력: 10/5만 휴장, 소진일 = 원장 ~10/15)"])
    for clock in report.clocks:
        gap = ""
        if clock.krx_date and clock.krx_date != clock.exhaust_date:
            gap = f"  ·  한글날 휴장이면 {clock.krx_date.isoformat()}"
        lines.append(
            f"  {clock.name}  잔여 {clock.remaining_tn:.2f}조  "
            f"일 {clock.daily_tn:.2f}조  →  {clock.sessions}세션  {clock.exhaust_date.isoformat()}{gap}"
        )

    lines.extend(["", "종가에서 레벨까지"])
    for view in report.levels:
        if not view.level.live and view.level.role == "floor":
            lines.append(f"  폐기  {view.level.name}  {view.level.price:,.0f}")
            continue
        if view.level.role == "spot":
            continue
        lines.append(f"  {view.level.name}  {view.level.price:,.0f}  {fmt_pct(view.distance_pct)}")
    mid = distance_pct(market.kospi, SELL_TRIGGER_MID)
    lines.append(f"  매도 트리거 중점 6,050  {fmt_pct(mid)}")
    lines.append(format_sim(run_bundle(report.panels)).rstrip("\n"))
    return "\n".join(lines) + "\n"


def _score_line(panel: ScoredPanel) -> str:
    return (
        f"  {panel.hit_pct:>3}%  N{panel.n:<2}  "
        f"✓{panel.panel.hits} △{panel.panel.partials} ✗{panel.panel.misses}  "
        f"{panel.name}"
    )


def render_html(report: Report) -> str:
    weights = report.posterior.as_dict()
    data = " ".join(f'data-{code.lower()}="{fmt_weight(weights[code])}"' for code in CODES)
    body = "\n".join(
        [
            _hero(report),
            chapters.kpis(report),
            chapters.method(),
            _bridge(report),
            _boards(report),
            chapters.scatter(report),
            _composite(report),
            chapters.events(),
            chapters.dossiers(report),
            _axes(),
            chapters.kospi_chart(report),
            _levels(report),
            chapters.yield_ladder(report),
            _clocks(report),
            chapters.tape(report),
            chapters.calendar(),
            _fan(report),
            _paths(report),
            _shocks(report),
            _discarded(),
            chapters.watch(report),
            chapters.metaphor(),
            sim_html(run_bundle(report.panels)),
            _footer(report),
        ]
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>하이브리드 v{escape(report.posterior.version)} — 맞힌 패널의 10월</title>
<style>
:root {{
  --bg:#0E141F; --card:#141C2B; --fg:#E6EAF2; --mut:#8A95A8; --line:#243044;
  --gold:#B8861C; --teal:#28A886; --rose:#D66F7C; --blue:#3E9BC0; --violet:#937CD8;
  --mono:ui-monospace,"JetBrains Mono",Menlo,Consolas,monospace;
  --sans:"Noto Sans KR",system-ui,-apple-system,sans-serif;
  color-scheme:dark;
}}
* {{ box-sizing:border-box }}
body {{ margin:0; background:var(--bg); color:var(--fg); font-family:var(--sans); font-size:14px; line-height:1.55 }}
.wrap {{ max-width:1100px; margin:0 auto; padding:28px 18px 64px }}
.eyebrow {{ font-family:var(--mono); font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--mut) }}
h1 {{ font-size:32px; line-height:1.2; margin:8px 0 }}
h2 {{ font-size:18px; margin:36px 0 12px }}
.lede {{ color:var(--mut); max-width:68ch }}
.weights {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:18px 0 }}
.w {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px }}
.w b {{ font-family:var(--mono); font-size:36px; font-weight:600 }}
.w span {{ display:block; color:var(--mut); font-size:12px; margin-top:4px }}
.w.A {{ border-top:3px solid var(--gold) }} .w.B {{ border-top:3px solid var(--rose) }} .w.C {{ border-top:3px solid var(--blue) }}
.card {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px; margin:12px 0 }}
table {{ width:100%; border-collapse:collapse; font-size:13px }}
th {{ text-align:left; color:var(--mut); font-weight:500; font-size:11px; padding:6px 8px; border-bottom:1px solid var(--line) }}
td {{ padding:7px 8px; border-bottom:1px solid var(--line); vertical-align:top }}
.num {{ font-family:var(--mono); font-variant-numeric:tabular-nums }}
.mut {{ color:var(--mut) }}
.tag {{ font-family:var(--mono); font-size:10px; border:1px solid var(--line); border-radius:3px; padding:1px 6px; color:var(--mut) }}
.tag.core {{ color:var(--gold); border-color:var(--gold) }}
.tag.watch {{ color:var(--violet); border-color:var(--violet) }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:12px }}
.person {{ display:grid; grid-template-columns:92px 1fr 48px; gap:8px; align-items:center; margin:5px 0 }}
.name {{ text-align:right }}
.track {{ display:flex; height:14px; background:#1C2535; border-radius:3px; overflow:hidden }}
.ok {{ background:var(--teal) }} .mid {{ background:var(--gold) }} .bad {{ background:var(--rose) }}
.bar {{ height:8px; background:#1C2535; border-radius:4px; overflow:hidden }}
.bar i {{ display:block; height:100%; background:var(--gold) }}
.formula {{ font-family:var(--mono); font-size:12px; color:var(--mut) }}
.fan {{ width:100%; height:auto; display:block }}
@media (max-width:800px) {{
  .grid2,.weights {{ grid-template-columns:1fr }}
  h1 {{ font-size:26px }}
}}
</style>
<style>
{chapters.STYLE}
</style>
</head>
<body {data}>
<div class="wrap">
{body}
</div>
</body>
</html>
"""


def _hero(report: Report) -> str:
    market = report.market
    weights = report.posterior.as_dict()
    prior = dict(report.posterior.prior)
    cards = []
    blurbs = {
        "A": "박스 후 연말 재도전",
        "B": "7,200 주봉 돌파",
        "C": "자본 공급자가 멈춤",
    }
    for code in CODES:
        cards.append(
            f'<div class="w {code}"><div class="eyebrow">{code}</div>'
            f'<b>{fmt_weight(weights[code])}%</b><span>{escape(blurbs[code])}</span></div>'
        )
    return f"""
<header>
  <div class="eyebrow">Panel Scorecard → October Outlook · {DOCUMENT_ASOF.isoformat()} (일) · 원장 1~7권 + 10/2 실측</div>
  <h1>맞힌 패널의 10월</h1>
  <p class="lede">8월 초부터 9월 말까지 방송·피드에서 교차검증한 29명의 콜 177건을 10/2 종가로 채점했다. 적중률이 높은 축을 지금 좌표에 대입한 것이 이 문서다. 채점과 확률은 추론이며, 태그로 층을 구분했다.</p>
  <p class="lede">8/29 하이브리드 v{escape(report.posterior.prior_version)}은 A{fmt_weight(prior['A'])} B{fmt_weight(prior['B'])} C{fmt_weight(prior['C'])}였다.
  10/2 종가의 네 가지 실측을 더하면 확률은 A{fmt_weight(weights['A'])} · B{fmt_weight(weights['B'])} · C{fmt_weight(weights['C'])}이다.
  채점 177건(✓93 △24 ✗60), 진행중 {OPEN_CALLS}건은 분모에서 빠진다.</p>
</header>
<div class="weights">{''.join(cards)}</div>
<p class="formula">종합 = 0.6×수축적중률 + 0.25×(1층/5) + 0.15×(반증/5) &nbsp;·&nbsp; 수축 = (N×적중률 + 4×0.5) / (N+4)</p>
<div class="card">
  <div class="num">코스피 {market.kospi:,.2f} · 10Y {market.us10y:.2f}% (장중 {market.us10y_intraday_high:.2f}) · 30Y {market.us30y:.2f}% · 외인 9월 {market.foreign_month_tn:.1f}조 · 주간 {market.foreign_week_tn:.2f}조 · 10월 인상 {market.oct_hike_prob * 100:.0f}%</div>
</div>
"""


def _bridge(report: Report) -> str:
    rows = []
    quiet: list[str] = []
    for factor in report.posterior.factors:
        if factor.tier == "watch" and not factor.active:
            quiet.append(factor.title)
            continue
        cells = "".join(f"<td class='num'>{fmt_signed(value)}</td>" for _, value in factor.delta)
        rows.append(
            "<tr>"
            f"<td><span class='tag {factor.tier}'>{'코어' if factor.tier == 'core' else '감시'}</span> {escape(factor.title)}</td>"
            f"<td class='num'>{factor.intensity:.2f}</td>{cells}"
            f"<td class='mut'>{escape(factor.explain)}</td></tr>"
        )
    quiet_line = ""
    if quiet:
        quiet_line = f"<p class='mut'>이번 좌표에서 꺼진 감시: {escape(' · '.join(quiet))}</p>"
    return f"""
<h2>v1.0에서 v1.1로</h2>
<div class="card"><table>
<thead><tr><th>요인</th><th>강도</th><th>A</th><th>B</th><th>C</th><th>입력</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
{quiet_line}
</div>
"""


def _fan(report: Report) -> str:
    weights = report.posterior.as_dict()
    spot = report.market.kospi
    hi, lo = 8200.0, 5800.0
    top, bot = 28.0, 250.0
    xs = (70, 230, 390, 550)

    def y(price: float) -> float:
        return top + (hi - price) / (hi - lo) * (bot - top)

    colors = {"A": "#B8861C", "B": "#D66F7C", "C": "#3E9BC0"}
    shapes = []
    labels = []
    for scenario in SCENARIOS:
        highs = [spot] + [band.high for band in scenario.paths]
        lows = [spot] + [band.low for band in scenario.paths]
        mids = [spot] + [band.mid for band in scenario.paths]
        forward = " ".join(f"{xs[i]:.1f},{y(highs[i]):.1f}" for i in range(4))
        back = " ".join(f"{xs[i]:.1f},{y(lows[i]):.1f}" for i in range(3, -1, -1))
        line = " ".join(f"{xs[i]:.1f},{y(mids[i]):.1f}" for i in range(4))
        shapes.append(
            f'<polygon points="{forward} {back}" fill="{colors[scenario.code]}" fill-opacity="0.22"/>'
            f'<polyline points="{line}" fill="none" stroke="{colors[scenario.code]}" stroke-width="2"/>'
        )
        labels.append(
            f'<text x="640" y="{y(mids[-1]) + 4:.1f}" fill="{colors[scenario.code]}" font-size="12">'
            f'{scenario.code} {fmt_weight(weights[scenario.code])}%</text>'
        )
    grids = []
    for price in (8000, 7500, 7000, 6500, 6000):
        yy = y(price)
        grids.append(
            f'<line x1="56" y1="{yy:.1f}" x2="620" y2="{yy:.1f}" stroke="#1C2535"/>'
            f'<text x="50" y="{yy + 3:.1f}" fill="#8A95A8" font-size="10" text-anchor="end">{price:,}</text>'
        )
    months = ("10/2", "10월", "11월", "12월")
    xticks = "".join(
        f'<text x="{xs[i]}" y="276" fill="#8A95A8" font-size="11" text-anchor="middle">{months[i]}</text>'
        for i in range(4)
    )
    dot = f'<circle cx="{xs[0]}" cy="{y(spot):.1f}" r="4" fill="#E6EAF2"/>'
    svg = (
        f'<svg viewBox="0 0 760 300" class="fan" role="img">'
        f'<rect width="760" height="300" fill="#141C2B"/>'
        f'{"".join(grids)}{"".join(shapes)}{dot}{xticks}{"".join(labels)}</svg>'
    )
    return f'<h2>밴드</h2><div class="card">{svg}<p class="mut">가운데 선은 각 월 밴드의 중점. 확률은 색 옆 숫자이고 밴드는 패널 레벨이다.</p></div>'


def _paths(report: Report) -> str:
    weights = report.posterior.as_dict()
    cards = []
    for scenario in report.scenarios:
        bands = "<br>".join(
            f"<span class='num'>{escape(band.label)} {band.low:,.0f}–{band.high:,.0f}</span>"
            for band in scenario.paths
        )
        cards.append(
            f'<div class="card"><div class="eyebrow">{scenario.code} {fmt_weight(weights[scenario.code])}%</div>'
            f"<h3>{escape(scenario.title)}</h3><p>{escape(scenario.trigger)}</p>"
            f"<p class='mut'>{escape(' · '.join(scenario.panels))}</p><p>{bands}</p></div>"
        )
    return f'<div class="grid2">{"".join(cards)}</div>'


def _shocks(report: Report) -> str:
    base = report.posterior.as_dict()
    rows = [
        '<tr data-shock="base"><td>지금 이 입력</td>'
        + "".join(f"<td class='num'>{fmt_weight(base[code])}</td>" for code in CODES)
        + "</tr>"
    ]
    for shock in report.shocks:
        weights = shock.posterior.as_dict()
        rows.append(
            f'<tr data-shock="{escape(shock.id)}"><td>{escape(shock.title)}</td>'
            + "".join(f"<td class='num'>{fmt_weight(weights[code])}</td>" for code in CODES)
            + "</tr>"
        )
    return f"""
<h2>입력을 바꾸면</h2>
<div class="card"><table>
<thead><tr><th>가정</th><th>A</th><th>B</th><th>C</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<p class="mut">코어 네 개는 10/2 공개 확률에 맞춰 두었다. 감시 규칙의 폭은 방향을 확률로 옮긴 가정이고, 조건②의 +15%p만 문서에 적힌 폭이다.</p>
</div>
"""


def _person_row(panel: ScoredPanel, max_n: int) -> str:
    scale = 100 / max_n
    parts = (
        ("ok", panel.panel.hits),
        ("mid", panel.panel.partials),
        ("bad", panel.panel.misses),
    )
    bars = "".join(
        f'<i class="{kind}" style="width:{count * scale:.2f}%"></i>' for kind, count in parts if count
    )
    return (
        '<div class="person">'
        f'<div class="name">{escape(panel.name)}</div>'
        f'<div class="track" title="✓{panel.panel.hits} △{panel.panel.partials} ✗{panel.panel.misses}">{bars}</div>'
        f'<div class="num">{panel.hit_pct}%</div></div>'
    )


def _boards(report: Report) -> str:
    main = report.leaderboard(True)
    ref = report.leaderboard(False)
    max_n = max(panel.n for panel in report.panels)
    left = "".join(_person_row(panel, max_n) for panel in main)
    right = "".join(_person_row(panel, max_n) for panel in ref)
    top, last = main[0], main[-1]
    return f"""
<h2>02 · 리더보드 — 본선 1위 {escape(top.name)} {top.hit_pct}%, 꼴찌 {escape(last.name)} {last.hit_pct}%</h2>
<div class="grid2">
  <div class="card"><h3>본선 14명 — 수급·레벨이 상단</h3>{left}
  <p class="mut">막대 길이 = 채점 콜 수. 하단 4명(박세익·문홍철·이선엽·문남중)의 공통 기각은 9월 FOMC·금리 레벨.</p></div>
  <div class="card"><h3>참고군 15명 — 순위가 아니라 방향</h3>{right}
  <p class="mut">강건우·박현상·윤지호 88%는 N=4. 알상무 60%는 1,280·바이백 기각이 깎았고 1층은 표본 최상. 빈센트 0%는 N=2.</p></div>
</div>
{chapters.tags("ledger", "score")}
"""


def _composite(report: Report) -> str:
    rows = []
    for panel in report.composite_board():
        width = panel.composite_pct or 0
        rows.append(
            "<tr>"
            f"<td>{escape(panel.name)} <span class='mut'>{escape(panel.panel.affiliation)}</span></td>"
            f"<td><div class='bar'><i style='width:{width}%'></i></div></td>"
            f"<td class='num'>{width}</td>"
            f"<td class='mut'>적중 {panel.hit_pct}% · N{panel.n} · 1층 {panel.panel.layer1} · 반증 {panel.panel.falsifiability}</td>"
            "</tr>"
        )
    by_name = {panel.name: panel for panel in report.panels}
    applied = []
    for name in chapters.APPLY_ORDER:
        panel = by_name[name]
        applied.append(
            "<tr>"
            f"<td>{escape(panel.name)}</td>"
            f"<td>{escape(panel.panel.frame)}</td>"
            f"<td>{escape(panel.panel.now_cast)}</td>"
            f"<td class='mut'>{escape(panel.panel.falsify)}</td>"
            "</tr>"
        )
    return f"""
<h2>04 · 종합 점수 상위 12</h2>
<div class="card"><table>
<thead><tr><th>패널</th><th></th><th>점수</th><th>입력</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<p class="mut">이진호와 알상무가 적중률만으로는 안 보이던 자리로 올라온다. 박병창은 반증가능성 5로 61% 적중을 보강한다. 종합 60 아래는 결론만 취하고 근거는 다시 조달하는 등급이다.</p>
{chapters.tags("model")}</div>
<h2>11 · 10/2 좌표에 대입</h2>
<div class="card"><table>
<thead><tr><th>패널</th><th>검증된 프레임</th><th>지금</th><th>반증 조건</th></tr></thead>
<tbody>{''.join(applied)}</tbody>
</table>
{chapters.tags("ledger", "live", "inf")}</div>
"""


def _levels(report: Report) -> str:
    rows = []
    for view in report.levels:
        if view.level.role == "spot":
            continue
        tag = "" if view.level.live else "폐기 · "
        rows.append(
            "<tr>"
            f"<td>{tag}{escape(view.level.name)}</td>"
            f"<td class='num'>{view.level.price:,.2f}</td>"
            f"<td class='num'>{fmt_pct(view.distance_pct)}</td>"
            f"<td class='mut'>{escape(view.level.source)}</td></tr>"
        )
    mid = distance_pct(report.market.kospi, SELL_TRIGGER_MID)
    rows.append(
        f"<tr><td>매도 트리거 중점</td><td class='num'>6,050</td>"
        f"<td class='num'>{fmt_pct(mid)}</td><td class='mut'>6,000~6,100의 중점. 본문의 −13.6%</td></tr>"
    )
    return f'<h2>레벨까지의 거리</h2><div class="card"><table><tbody>{"".join(rows)}</tbody></table></div>'


def _clocks(report: Report) -> str:
    cards = []
    for clock in report.clocks:
        krx = ""
        if clock.krx_date and clock.krx_date != clock.exhaust_date:
            krx = f" 한글날을 휴장으로 넣으면 {clock.krx_date.isoformat()}."
        width = clock.drawn_pct or (clock.spent_tn / clock.budget_tn * 100)
        cards.append(
            f'<div class="card"><h3>{escape(clock.name)} 자사주 {clock.budget_tn:.0f}조</h3>'
            f'<p class="num">{clock.spent_tn:.2f}조 / {clock.budget_tn:.0f}조 · 막대 {width:.0f}%</p>'
            f'<div class="track"><i class="ok" style="width:{width:.1f}%"></i></div>'
            f'<p class="num">문서 잔여 {clock.drawn_remaining_tn:.1f}조 · {clock.sessions}세션 · {clock.exhaust_date.isoformat()}</p>'
            f'<p class="mut">{escape(clock.note)}{escape(krx)}</p></div>'
        )
    return (
        '<h2>자사주 두 프로그램</h2><div class="grid2">'
        f'{"".join(cards)}</div>{chapters.tags("ledger", "live", "model")}'
    )


def _axes() -> str:
    cards = []
    for note in AXES:
        cards.append(
            f'<div class="card"><div class="eyebrow">{escape(AXIS_LABEL[note.axis])}</div>'
            f'<p>{escape(" · ".join(note.winners))}</p>'
            f'<p>{escape(note.now)}</p>'
            f'<p class="mut">반증 · {escape(note.falsify)}</p></div>'
        )
    return f'<h2>축</h2><div class="grid2">{"".join(cards)}</div>'


def _discarded() -> str:
    rows = "".join(
        f"<tr><td>{escape(item.name)}</td><td>{escape(item.title)}</td><td class='mut'>{escape(item.reason)}</td></tr>"
        for item in DISCARDED
    )
    return f'<h2>채점에서 뺀 프레임</h2><div class="card"><table><tbody>{rows}</tbody></table></div>'


def _footer(report: Report) -> str:
    flags = "".join(f"<li>{escape(flag)}</li>" for flag in report.flags)
    flag_block = f"<ul>{flags}</ul>" if flags else ""
    return f"""
{flag_block}
<footer class="mut">
  원장 = 1~7권의 판정. 실측 = 10/2 마감(서울신문·한경·핀포인트·경향·fnnews·Yahoo Finance·FXStreet·GlobeNewswire). 채점 = 그 둘을 대조한 ✓/△/✗라, 같은 발언을 다르게 채점할 여지가 있다. 추론·MODEL = 가중치 0.6/0.25/0.15, 수축 k=4, 시나리오 A{fmt_weight(report.posterior.weight('A'))}/B{fmt_weight(report.posterior.weight('B'))}/C{fmt_weight(report.posterior.weight('C'))}. 어느 패널도 이 확률을 말하지 않았다.<br>
  채점에 넣지 않은 것: 날짜 없는 목표가, 반증 불가 명제, 진행중 {OPEN_CALLS}건. N&lt;6 참고군의 적중률은 크게 흔들릴 수 있다. 코스피 선은 확정 종가 15점이고 사이 거래일은 생략했다. 10/6 개장 전에는 어떤 시나리오도 채점되지 않는다. 다음 갱신: 10/8 삼성 3Q · 10/14 美 CPI · 하닉 자사주 소진.
</footer>
"""
