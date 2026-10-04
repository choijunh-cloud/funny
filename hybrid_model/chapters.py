"""스코어카드에서 빠졌던 장. 적중률·확률은 Report 에서 읽고, 문장은 narrative 에서 읽는다."""

from __future__ import annotations

from html import escape

from hybrid_model.ledger import AXIS_LABEL, OPEN_CALLS
from hybrid_model.market import distance_pct
from hybrid_model.model import Report
from hybrid_model.narrative import (
    CALENDAR,
    DOSSIERS,
    EVENTS,
    EXPORTS,
    KOSPI_CLOSES,
    METAPHOR,
    METHOD,
    PROFILE_ORDER,
    YIELD_RUNGS,
)

STYLE = """
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:10px;margin:14px 0}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px}
.kpi .k{font-size:11px;color:var(--mut)} .kpi .v{font-family:var(--mono);font-size:20px;font-weight:600;margin:4px 0}
.kpi .s{font-size:11px;color:var(--mut)}
.method{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.mstep{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px;font-size:12.5px}
.mstep b{display:block;color:var(--gold);font-family:var(--mono);font-size:11px;margin-bottom:4px}
.chip{display:inline-block;font-size:11px;padding:1px 7px;border-radius:10px;border:1px solid var(--line);margin:2px 2px 2px 0}
.chip.ok{border-color:var(--teal);color:var(--teal)} .chip.bad{border-color:var(--rose);color:var(--rose)}
.pgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.pc{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px}
.ph{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:6px}
.ph b{font-size:15px} .aff{color:var(--mut);font-size:12px}
.ax{font-size:10px;color:#0E141F;padding:1px 6px;border-radius:3px;font-weight:700}
.ax.macro{background:var(--gold)} .ax.flow{background:var(--teal)} .ax.level{background:var(--blue)}
.ax.semi{background:var(--rose)} .ax.frame{background:var(--violet)}
.rt{margin-left:auto;font-family:var(--mono);font-weight:600} .sig{font-size:12px;color:var(--gold);margin-bottom:6px}
.key{font-size:12px;color:var(--mut);line-height:1.6;margin:0}
.cal{list-style:none;margin:0;padding:0;border-left:2px solid var(--line)}
.ci{display:grid;grid-template-columns:90px 1fr;gap:10px;padding:7px 0 7px 14px;position:relative;font-size:13px}
.ci::before{content:"";position:absolute;left:-6px;top:13px;width:10px;height:10px;border-radius:50%;background:var(--mut)}
.ci.flow::before{background:var(--teal)} .ci.semi::before{background:var(--rose)}
.ci.macro::before{background:var(--gold)} .ci.frame::before{background:var(--violet)}
.cd{font-family:var(--mono);font-size:12px;color:var(--mut)}
.wgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}
.wc{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px}
.wk{font-size:11px;color:var(--mut)} .wv{font-family:var(--mono);font-weight:600;margin:3px 0} .wr{font-size:11px;color:var(--violet)}
.meta{background:var(--card);border:1px dashed var(--line);border-radius:8px;padding:14px}
.meta h3{color:var(--gold);margin:0 0 8px}
.hbar{display:grid;grid-template-columns:110px 1fr auto;gap:8px;align-items:center;margin:6px 0}
.hbar i{display:block;height:14px;border-radius:3px;background:var(--blue)}
.hbar i.up{background:var(--rose)}
.rung{display:grid;grid-template-columns:64px 1fr;gap:8px;align-items:center;margin:4px 0;padding:4px 8px;border-radius:4px;background:#1C2535}
.rung.now{background:rgba(184,134,28,.35)}
.scatter{width:100%;height:auto;display:block}
.legend{display:flex;gap:12px;flex-wrap:wrap;font-size:11px;color:var(--mut);margin:6px 0}
.lg{display:inline-flex;align-items:center;gap:5px}
.sw{width:10px;height:10px;border-radius:50%;display:inline-block}
"""

AXIS_COLOR = {
    "macro": "#B8861C",
    "flow": "#28A886",
    "level": "#3E9BC0",
    "semi": "#D66F7C",
    "frame": "#937CD8",
}


def _chips(names: tuple[str, ...], kind: str) -> str:
    return "".join(f'<span class="chip {kind}">{escape(name)}</span>' for name in names)


def kpis(report: Report) -> str:
    panels = report.panels
    calls = sum(panel.n for panel in panels)
    hits = sum(panel.panel.hits for panel in panels)
    partials = sum(panel.panel.partials for panel in panels)
    misses = sum(panel.panel.misses for panel in panels)
    leader = report.leaderboard(True)[0]
    market = report.market
    samsung, hynix = report.clocks
    cards = (
        ("채점 패널", f"{len(panels)}명", "방송·피드 원장 1~7권"),
        ("채점 완료 콜", f"{calls}건", f"✓{hits} △{partials} ✗{misses} · 진행중 {OPEN_CALLS}"),
        ("본선 1위 적중률", f"{leader.hit_pct}%", f"{leader.name}({leader.panel.affiliation}) N={leader.n}"),
        ("코스피 10/2", f"{market.kospi:,.2f}", f"{market.kospi_change_pct:+.2f}% · 7,000 회복"),
        ("美 10Y / 30Y", f"{market.us10y:.2f} / {market.us30y:.2f}%", f"장중 {market.us10y_intraday_high:.2f} · 30Y 2002년 이후 최고"),
        ("자사주 잔여", f"하닉 {100 - hynix.drawn_pct:.0f}%", f"삼성 {100 - samsung.drawn_pct:.0f}% · 소진 {samsung.exhaust_date.month}/{samsung.exhaust_date.day} · 하닉 계산 {hynix.exhaust_date.month}/{hynix.exhaust_date.day}"),
    )
    body = "".join(
        f'<div class="kpi"><div class="k">{escape(label)}</div><div class="v">{escape(value)}</div><div class="s">{escape(sub)}</div></div>'
        for label, value, sub in cards
    )
    return f'<div class="kpis">{body}</div>'


def method() -> str:
    steps = "".join(f'<div class="mstep"><b>{escape(title)}</b>{escape(text)}</div>' for title, text in METHOD)
    return f'<h2>01 · 채점 방법</h2><div class="method">{steps}</div>'


def scatter(report: Report) -> str:
    left, right, top, bot = 64, 1040, 28, 390
    width, height = 1080, 440

    def x_of(n: int) -> float:
        return left + (n / 16) * (right - left)

    def y_of(rate: float) -> float:
        return bot - rate * (bot - top)

    grids = []
    for pct in (0, 25, 50, 75, 100):
        y = y_of(pct / 100)
        grids.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#1C2535"/>'
            f'<text x="{left - 8}" y="{y + 3:.1f}" fill="#8A95A8" font-size="10" text-anchor="end">{pct}</text>'
        )
    for n in range(0, 17, 2):
        x = x_of(n)
        grids.append(
            f'<text x="{x:.1f}" y="{bot + 16:.1f}" fill="#8A95A8" font-size="10" text-anchor="middle">{n}</text>'
        )
    y50 = y_of(0.5)
    x6 = x_of(6)
    guides = (
        f'<line x1="{left}" y1="{y50:.1f}" x2="{right}" y2="{y50:.1f}" stroke="#8A95A8" stroke-dasharray="3 3"/>'
        f'<text x="{right}" y="{y50 - 4:.1f}" fill="#8A95A8" font-size="10" text-anchor="end">동전 던지기 50%</text>'
        f'<line x1="{x6:.1f}" y1="{top}" x2="{x6:.1f}" y2="{bot}" stroke="#8A95A8" stroke-dasharray="3 3"/>'
        f'<text x="{x6 + 4:.1f}" y="{top + 12}" fill="#8A95A8" font-size="10">N≥6 본선</text>'
    )
    dots = []
    placed: list[tuple[float, float]] = []
    for panel in report.panels:
        x = x_of(panel.n)
        y = y_of(panel.hit_rate)
        radius = 7 if panel.composite_pct is not None and panel.composite_pct >= 65 else 5
        color = AXIS_COLOR[panel.panel.axis]
        label_y = y - 8
        while any(abs(x - px) < 54 and abs(label_y - py) < 12 for px, py in placed):
            label_y += 12
        placed.append((x, label_y))
        anchor = "end" if x > 980 else "start"
        lx = x - 8 if anchor == "end" else x + 8
        dots.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius}" fill="{color}" stroke="#0E141F" stroke-width="2"/>'
            f'<text x="{lx:.1f}" y="{label_y:.1f}" fill="#E6EAF2" font-size="11" text-anchor="{anchor}">{escape(panel.name)}</text>'
        )
    legend = "".join(
        f'<span class="lg"><i class="sw" style="background:{color}"></i>{escape(AXIS_LABEL[axis])}</span>'
        for axis, color in AXIS_COLOR.items()
    )
    svg = (
        f'<svg id="scatter" viewBox="0 0 {width} {height}" class="scatter" role="img">'
        f'{"".join(grids)}{guides}{"".join(dots)}</svg>'
    )
    return (
        '<h2>03 · 표본 수 × 적중률</h2><div class="card">'
        f'<div class="legend">{legend}<span class="lg">큰 점 = 종합 65점 이상</span></div>'
        f"{svg}"
        '<p class="mut">김장열은 가장 많이 말하고 63%다. 우하단은 문남중·이선엽. 수급·레벨이 위쪽에 모이고, 매크로는 인상 쪽과 인하 쪽으로 갈린다.</p>'
        "</div>"
    )


def events() -> str:
    rows = []
    for event in EVENTS:
        rows.append(
            "<tr>"
            f"<td>{escape(event.title)}</td>"
            f"<td>{_chips(event.hit, 'ok')}</td>"
            f"<td>{_chips(event.miss, 'bad')}</td>"
            "</tr>"
        )
    return (
        '<h2>05 · 결정적 채점 6건</h2><div class="card"><table><thead><tr>'
        "<th>이벤트 (실측)</th><th>맞힌 쪽</th><th>틀린 쪽</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        "<p class=\"mut\">9월 FOMC 인상(12:0)이 가장 많은 패널을 갈랐다. 4.5%·4.75%·5.0% 임계는 전부 돌파됐고 코스피는 7,000이다. 상단 7,100~7,500은 세 번 거부됐다.</p>"
        "</div>"
    )


def dossiers(report: Report) -> str:
    by_name = {panel.name: panel for panel in report.panels}
    cards = []
    for name in PROFILE_ORDER:
        panel = by_name[name]
        cards.append(
            '<article class="pc"><div class="ph">'
            f"<b>{escape(name)}</b>"
            f'<span class="aff">{escape(panel.panel.affiliation)}</span>'
            f'<span class="ax {panel.panel.axis}">{escape(AXIS_LABEL[panel.panel.axis])}</span>'
            f'<span class="rt">{panel.hit_pct}% <small>N{panel.n}</small></span></div>'
            f'<div class="sig">{escape(panel.panel.signature)}</div>'
            f'<p class="key">{escape(DOSSIERS[name])}</p></article>'
        )
    return f'<h2>06 · 상위 패널 12 — 시그니처와 채점 근거</h2><div class="pgrid">{"".join(cards)}</div>'


def kospi_chart(report: Report) -> str:
    spot = report.market.kospi
    prices = [spot if price is None else price for _, price in KOSPI_CLOSES]
    labels = [label for label, _ in KOSPI_CLOSES]
    hi, lo = 7600, 5200
    top, bot = 36, 250
    left, right = 56, 760

    def y_of(price: float) -> float:
        return top + (hi - price) / (hi - lo) * (bot - top)

    n = len(prices)
    xs = [left + i * (right - left) / (n - 1) for i in range(n)]
    grids = []
    for price in (5200, 5600, 6000, 6400, 6800, 7200, 7600):
        y = y_of(price)
        grids.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#1C2535"/>'
            f'<text x="48" y="{y + 3:.1f}" fill="#8A95A8" font-size="10" text-anchor="end">{price:,}</text>'
        )
    line = " ".join(f"{xs[i]:.1f},{y_of(prices[i]):.1f}" for i in range(n))
    dots = []
    ticks = []
    for i, price in enumerate(prices):
        dots.append(f'<circle cx="{xs[i]:.1f}" cy="{y_of(price):.1f}" r="3.2" fill="#E6EAF2"/>')
        if labels[i]:
            ticks.append(
                f'<text x="{xs[i]:.1f}" y="276" fill="#8A95A8" font-size="10" text-anchor="middle">{labels[i]}</text>'
            )
    last = n - 1
    label = (
        f'<text x="{xs[last] - 4:.1f}" y="{y_of(prices[last]) - 8:.1f}" fill="#E6EAF2" font-size="11" text-anchor="end">{spot:,.2f}</text>'
        f'<text x="{xs[10]:.1f}" y="{y_of(prices[10]) - 8:.1f}" fill="#8A95A8" font-size="10" text-anchor="middle">9/23 {prices[10]:,.0f}</text>'
    )
    up = distance_pct(spot, 7100)
    down = distance_pct(spot, 6100)
    svg = (
        '<svg viewBox="0 0 820 300" class="scatter" role="img">'
        f'{"".join(grids)}<polyline points="{line}" fill="none" stroke="#E6EAF2" stroke-width="2"/>'
        f'{"".join(dots)}{"".join(ticks)}{label}</svg>'
    )
    return (
        '<h2>08 · 코스피 좌표</h2><div class="card">'
        f"<h3>코스피 {spot:,.2f} — 상단 존 7,100~7,500 바로 아래</h3>{svg}"
        f'<p class="mut">확정 종가 15점. x축은 등간격이라 사이 거래일은 생략된다. '
        f"7,100까지 {up:+.1f}%, 매도 트리거 6,100까지 {down:+.1f}%.</p></div>"
    )


def yield_ladder(report: Report) -> str:
    market = report.market
    rungs = [(price, text, False) for price, text, _ in YIELD_RUNGS]
    rungs.append((market.us10y, f"현재 10Y ({market.asof.month}/{market.asof.day}) · 장중 고점 {market.us10y_intraday_high:.2f}", True))
    rungs.append((market.us30y, "현재 30Y · 2002년 이후 최고", True))
    rungs.sort(key=lambda item: item[0])
    rows = []
    for price, text, current in rungs:
        klass = "rung now" if current else "rung"
        rows.append(
            f'<div class="{klass}"><span class="num">{price:.2f}</span><span>{escape(text)}</span></div>'
        )
    return (
        '<h2>금리 사다리</h2><div class="card">'
        f'{"".join(rows)}'
        '<p class="mut">4.50·4.70·4.75·5.00·5.30·5.35는 종가 아래에 있다. 이은택 조건①(5.0~5.3 추세 돌파)만 경고로 살아 있다.</p></div>'
    )


def tape(report: Report) -> str:
    market = report.market
    foreign = (
        ("1~9월 누적", market.foreign_ytd_tn),
        ("9월 한 달", market.foreign_month_tn),
        ("9/28~10/2 주간", market.foreign_week_tn),
        ("10/2 하루", market.foreign_day_tn),
    )
    span = max(abs(value) for _, value in foreign)

    def row(label: str, value: float, up: bool) -> str:
        width = abs(value) / span * 100
        klass = "up" if up else ""
        return (
            '<div class="hbar">'
            f"<span>{escape(label)}</span>"
            f'<span><i class="{klass}" style="width:{width:.1f}%"></i></span>'
            f'<span class="num">{value:+.1f}{"%" if up else "조"}</span></div>'
        )

    foreign_rows = "".join(row(label, value, False) for label, value in foreign)
    export_rows = "".join(row(label, value, True) for label, value in EXPORTS)
    return (
        '<div class="grid2">'
        '<section class="card"><h3>외국인 순매도</h3>'
        f"{foreign_rows}"
        f'<p class="mut">1~9월 {market.foreign_ytd_tn:.1f}조 중 삼전·하닉 계열 4종목이 93.4%. '
        f"주간 {market.foreign_week_tn:.2f}조, 10/2 당일 {market.foreign_day_tn:.2f}조, 개인 {market.individual_day_tn:.2f}조.</p></section>"
        '<section class="card"><h3>9월 수출</h3>'
        f"{export_rows}"
        f'<p class="mut">반도체 ${market.export_semi_bn:.0f}억({market.export_semi_yoy:+.1f}%). '
        "가이던스 상회 뒤 주가가 빠진 마이크론과 같이 보면, 호재가 가격에 들어간 상태다.</p></section>"
        "</div>"
    )


def calendar() -> str:
    items = "".join(
        f'<li class="ci {axis}"><span class="cd">{escape(when)}</span><span>{escape(text)}</span></li>'
        for when, axis, text in CALENDAR
    )
    return (
        '<h2>09 · 10월의 일곱 시계</h2><div class="card"><ul class="cal">'
        f"{items}</ul>"
        '<p class="mut">자사주에서 실적으로, 실적에서 외인으로 바통이 넘어가는 2주(10/8~10/22)가 이번 달의 본편이다. 10/6 개장 전에는 어느 시나리오도 채점되지 않는다.</p></div>'
    )


def watch(report: Report) -> str:
    market = report.market
    samsung, hynix = report.clocks
    cells = (
        ("외인 주간 순매수", f"9월 {market.foreign_month_tn:.0f}조 · 주간 {market.foreign_week_tn:.2f}조", "주간 +전환 = A→B / −10조 지속 = C"),
        ("기타법인(자사주)", f"삼성 {samsung.drawn_pct:.0f}% · 하닉 {hynix.drawn_pct:.0f}%", "하닉 65만주/일에서 이탈하면 소진 시계가 움직인다"),
        ("美 10Y / 30Y", f"{market.us10y:.2f} / {market.us30y:.2f}", "5.0 하회 = B 지지 · 5.3+ 고착 = 이은택 ①"),
        ("美 9월 CPI (10/14)", f"7월 헤드라인 {market.july_headline_cpi:.1f}", "근원 재가속 = 조건② 노웨이백"),
        ("삼성 3Q (10/8)", "컨센 110조+", "≥115 서프라이즈 = B · 110대 인라인 후 하락 = 매도 재료 소진"),
        ("원달러", f"{market.usdkrw:,.1f}", "1,320 하회 = 수출주 4Q 추정 하향(강건우)"),
        ("브렌트", f"${market.brent:.0f}", "<$90 재개 = B · >$110 = 헤드라인 물가 재점화"),
        ("코스피 레벨", f"{market.kospi:,.0f}", "7,200 주봉 돌파 = B · 6,562 이탈 = C · 6,100 = 박병창 매도"),
    )
    body = "".join(
        f'<div class="wc"><div class="wk">{escape(title)}</div><div class="wv">{escape(value)}</div><div class="wr">{escape(rule)}</div></div>'
        for title, value, rule in cells
    )
    return f'<h2>13 · 감시 8칸</h2><div class="wgrid">{body}</div>'


def metaphor() -> str:
    paragraphs = "".join(f"<p>{escape(text)}</p>" for text in METAPHOR)
    return (
        '<h2>14 · 방파제가 걷히는 날의 항구</h2><div class="meta">'
        "<h3>두 달 동안 가장 잘 맞힌 사람들은 파도가 아니라 방파제를 본 사람들이었다</h3>"
        f"{paragraphs}</div>"
    )
