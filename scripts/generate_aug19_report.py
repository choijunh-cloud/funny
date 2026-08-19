#!/usr/bin/env python3
"""2026-08-19 데일리 시장 리포트 HTML 생성.

차트는 scripts/svg_charts.py 의 인라인 SVG. 외부 JS CDN 없이 오프라인·인쇄가 된다.
"""

from __future__ import annotations

import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import svg_charts as ch
from aug19_report_data import (
    ADR,
    ALTEOGEN,
    BIO_0819,
    BIO_INDEX,
    BUYBACK,
    CONFLICTS,
    FCF_2028_REF,
    FCF_SCENARIOS,
    FOUNDRY_HIKE,
    FOUNDRY_MIX,
    FX,
    GIGAVIS,
    HANWHA_AERO,
    HBM_CASES,
    ISU,
    LGES,
    LS_GROUP,
    MARVELL_GOOGLE,
    NVDA_PREVIEW,
    OIL,
    OPENAI,
    PEER_BUYBACK,
    RATES,
    TARGETS,
    TIMELINE,
    TREASURY_BUYBACK,
    TRIGGERS,
    UNITREE,
    US_CHIPS_0818,
    US_MEMORY,
    US_SESSION_0818,
    US_SESSION_0819,
    VALUATION,
    YEN_CARRY_2024,
)

OUT_DIR = Path("/workspace/reports")
OUT_HTML = OUT_DIR / "2026-08-19-daily-market-report.html"

NAVY = ch.NAVY
BLUE = ch.BLUE
GOLD = ch.GOLD
RED = ch.RED
GREEN = ch.GREEN
AMBER = ch.AMBER
SKY = ch.SKY
PALE = ch.PALE


def _h(s) -> str:
    return escape(str(s))


def fig(svg: str, caption: str) -> str:
    return (
        f'<figure class="fig"><div class="fig-inner">{svg}</div>'
        f"<figcaption>{_h(caption)}</figcaption></figure>"
    )


def p(*parts: str) -> str:
    return "<p>" + "".join(parts) + "</p>"


def note(kind: str, title: str, body: str) -> str:
    return (
        f'<aside class="note {kind}"><strong>{_h(title)}</strong>'
        f"<div>{body}</div></aside>"
    )


def table(headers, rows, caption: str = "") -> str:
    th = "".join(f"<th>{_h(h)}</th>" for h in headers)
    body = []
    for row in rows:
        tds = "".join(f"<td>{c}</td>" for c in row)
        body.append(f"<tr>{tds}</tr>")
    cap = f"<caption>{_h(caption)}</caption>" if caption else ""
    return f'<div class="table-wrap"><table>{cap}<thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table></div>'


CSS = """
:root {
  --navy: #0f2043; --navy2: #1e407c; --gold: #b8943a; --ink: #1a2230;
  --muted: #5c6674; --line: #d7dee8; --paper: #f4f1ea; --card: #ffffff;
  --good: #1f8a4c; --bad: #c0392b; --warn: #d98c1f; --soft: #eef2f8;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0; color: var(--ink); background: var(--paper);
  font: 15.5px/1.7 "NanumGothic", "Noto Sans KR", "Malgun Gothic", sans-serif;
}
.page { max-width: 1080px; margin: 0 auto; padding: 28px 28px 80px; }
header.hero {
  background: linear-gradient(135deg, #0f2043 0%, #1e407c 70%, #3a5f9a 100%);
  color: #fff; border-radius: 16px; padding: 36px 40px 28px; margin-bottom: 28px;
  position: relative; overflow: hidden;
}
header.hero::after {
  content: ""; position: absolute; right: -60px; top: -80px; width: 280px; height: 280px;
  background: radial-gradient(circle, rgba(184,148,58,.35), transparent 70%);
}
.kicker { letter-spacing: .16em; font-size: 12px; color: #d4c08a; font-weight: 700; }
header.hero h1 { font-size: 30px; line-height: 1.35; margin: 8px 0 10px; }
header.hero .lead { color: #d7e2f3; max-width: 780px; margin: 0; }
.meta { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; }
.chip {
  font-size: 12px; padding: 4px 10px; border-radius: 999px;
  background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.18);
}
.chip.g { background: rgba(31,138,76,.22); }
.chip.r { background: rgba(192,57,43,.25); }
.chip.a { background: rgba(217,140,31,.25); }

nav.toc {
  background: var(--card); border: 1px solid var(--line); border-radius: 12px;
  padding: 16px 20px; margin-bottom: 28px;
}
nav.toc h2 { font-size: 13px; color: var(--muted); margin: 0 0 8px; letter-spacing: .08em; }
nav.toc ol { margin: 0; padding-left: 20px; columns: 2; }
nav.toc a { color: var(--navy2); text-decoration: none; }
nav.toc a:hover { text-decoration: underline; }

section { margin: 0 0 36px; break-inside: avoid; }
section > h2 {
  font-size: 21px; color: var(--navy); margin: 0 0 6px;
  padding-bottom: 8px; border-bottom: 2px solid var(--navy);
}
section > h2 .num {
  display: inline-block; min-width: 28px; color: var(--gold); margin-right: 6px;
}
.sub { color: var(--muted); margin: 0 0 16px; font-size: 14px; }
h3 { font-size: 16px; color: var(--navy2); margin: 22px 0 8px; }
p { margin: 0 0 10px; }
strong { color: var(--navy); }

.fig { margin: 14px 0 8px; }
.fig-inner {
  background: var(--card); border: 1px solid var(--line); border-radius: 12px;
  padding: 10px 12px 4px;
}
figcaption { font-size: 12.5px; color: var(--muted); margin: 6px 4px 0; }

.note {
  border-radius: 10px; padding: 12px 14px; margin: 12px 0; border-left: 4px solid var(--navy2);
  background: var(--soft);
}
.note.warn { border-color: var(--warn); background: #fff8e7; }
.note.bad { border-color: var(--bad); background: #fdecea; }
.note.good { border-color: var(--good); background: #e8f5e9; }
.note strong { display: block; margin-bottom: 4px; }

.table-wrap { overflow-x: auto; margin: 12px 0 16px; }
table { width: 100%; border-collapse: collapse; background: var(--card); font-size: 13.5px; }
caption { text-align: left; font-weight: 700; color: var(--navy); padding: 0 0 6px; }
th, td { border: 1px solid var(--line); padding: 7px 9px; vertical-align: top; }
th { background: var(--navy); color: #fff; font-weight: 600; text-align: left; }
tr:nth-child(even) td { background: #f7f9fc; }
.good { color: var(--good); font-weight: 700; }
.bad { color: var(--bad); font-weight: 700; }
.warn { color: var(--warn); font-weight: 700; }
.vtime { list-style: none; margin: 0 0 16px; padding: 0; border-left: 3px solid var(--line); }
.vtime li { position: relative; padding: 8px 0 8px 22px; display: flex; gap: 14px; align-items: baseline; }
.vtime li::before {
  content: ""; position: absolute; left: -7px; top: 16px; width: 11px; height: 11px;
  border-radius: 50%; background: var(--navy2); border: 2px solid #fff;
}
.vtime time { flex: 0 0 52px; font-weight: 700; color: var(--navy); font-variant-numeric: tabular-nums; }
.vtime .t-bad::before { background: var(--bad); }
.vtime .t-good::before { background: var(--good); }
.vtime .t-warn::before { background: var(--warn); }
.vtime .t-neu::before { background: var(--navy2); }

.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 14px; }
@media (max-width: 860px) {
  .grid2, .grid3, nav.toc ol { grid-template-columns: 1fr; columns: 1; }
  header.hero { padding: 24px 20px; }
  .page { padding: 16px 12px 48px; }
}

footer {
  margin-top: 40px; padding-top: 16px; border-top: 1px solid var(--line);
  color: var(--muted); font-size: 12.5px;
}
@media print {
  body { background: #fff; }
  .page { max-width: none; padding: 0; }
  header.hero { break-after: avoid; }
  section { break-inside: avoid; }
  nav.toc { break-after: page; }
}
"""


def section_cover() -> str:
    return f"""
<header class="hero">
  <div class="kicker">DAILY MARKET BRIEF · 2026.08.19</div>
  <h1>금리의 역습 위에 올라온 주주환원,<br>그리고 환율이 깎는 메모리 이익</h1>
  <p class="lead">
    8월 19일 코멘트의 축은 세 갈래다.
    첫째, 미·이란 리스크가 유가·장기금리를 거쳐 반도체 밸류에이션을 눌렀다.
    둘째, SK하이닉스 40조원 자사주 소각이 그 하락을 받아냈다.
    셋째, 원/달러가 1,400원 아래로 내려오며 2027년 순익 가정에
    18~24조원 규모 조정 가능성이 열렸다.
  </p>
  <div class="meta">
    <span class="chip r">10년물 4.708% → 바이백 후 4.64%</span>
    <span class="chip a">WTI 84달러 · 브렌트 90/100 라인</span>
    <span class="chip g">SK하이닉스 40조 소각 · FCF 50%+</span>
    <span class="chip">원/달러 1,412 → 하단 1,360~1,340 조건부</span>
    <span class="chip">엔비디아 실적 8/26</span>
  </div>
</header>
<nav class="toc">
  <h2>목차</h2>
  <ol>
    <li><a href="#s1">한눈에 보는 스코어보드</a></li>
    <li><a href="#s2">하루의 흐름</a></li>
    <li><a href="#s3">매크로: 전쟁 → 유가 → 금리</a></li>
    <li><a href="#s4">미국장 두 세션</a></li>
    <li><a href="#s5">SK하이닉스 주주환원</a></li>
    <li><a href="#s6">밸류에이션 맵</a></li>
    <li><a href="#s7">원/달러와 실적 민감도</a></li>
    <li><a href="#s8">엔캐리 체크리스트</a></li>
    <li><a href="#s9">HBM 대체 논쟁</a></li>
    <li><a href="#s10">삼성 파운드리 · 소부장</a></li>
    <li><a href="#s11">개별 종목</a></li>
    <li><a href="#s12">글로벌 AI 이벤트</a></li>
    <li><a href="#s13">앞으로 볼 트리거</a></li>
  </ol>
</nav>
"""


def section_scoreboard() -> str:
    tiles = ch.tiles(
        [
            ("미 10년물 (8/18 종가)", f"{RATES['us10y_close']}%", f"장중 {RATES['us10y_intraday']}% → 종가 {RATES['us10y_chg_pct']}%", "warn"),
            ("미 10년물 (바이백 후)", f"{RATES['us10y_after_buyback']}%", "재무부 매입 2배 확대 이후", "good"),
            ("미 30년물", f"{RATES['us30y_close']}%", f"장중 {RATES['us30y_intraday']}% / 이후 {RATES['us30y_after_buyback']}%", "warn"),
            ("WTI", f"${OIL['wti_now']:.0f}", f"안정 {OIL['brent_stable']:.0f} · 위험 {OIL['brent_danger']:.0f} (브렌트)", "bad"),
            ("원/달러", f"{FX['spot_ref']:,.0f}원", f"ADR 환산 {FX['adr_fx']:,.0f}원", "warn"),
            ("SOX 8/18", "-4.98%", "EWY -8.08% · 야간선물 -4.29%", "bad"),
            ("SK하이닉스 소각", "40조원", f"발행주식 {BUYBACK['share_pct']}% · EPS +{BUYBACK['eps_uplift_pct']}%", "good"),
            ("국채 바이백", f"${TREASURY_BUYBACK['after_bn']:.0f}B", f"${TREASURY_BUYBACK['before_bn']:.0f}B → 2배", "good"),
        ]
    )
    return f"""
<section id="s1">
  <h2><span class="num">01</span>한눈에 보는 스코어보드</h2>
  <p class="sub">수치는 8/19 코멘트에 적힌 값이다. 세션이 다른 금리는 병기했다.</p>
  {fig(tiles, "그림 1. 8월 19일 핵심 숫자 8개")}
  {note("warn", "공식은 깨졌다",
       "장기금리 하락이 기술주 상승으로 이어지지 않았다. 8/19 미국장은 금리보다 "
       "<strong>AI → 헬스케어 로테이션</strong>이 더 강했다.")}
</section>
"""


def section_timeline() -> str:
    tone_cls = {"key": "t-key", "bad": "t-bad", "good": "t-good", "warn": "t-warn", "neutral": "t-neu"}
    items = []
    for tstr, txt, tone in TIMELINE:
        items.append(
            f'<li class="{tone_cls.get(tone, "t-neu")}"><time>{_h(tstr)}</time><span>{_h(txt)}</span></li>'
        )
    return f"""
<section id="s2">
  <h2><span class="num">02</span>하루의 흐름</h2>
  <p class="sub">새벽 매크로 충격 → 장중 개별 호재 → 폐장 후 40조 소각 → 밤 환율·HBM 논쟁.</p>
  <ol class="vtime">{"".join(items)}</ol>
  {p("정규장 마감 코멘트의 표현을 그대로 옮기면, ",
     "<strong>금리 상승으로 촉발된 이틀 하락을 주주환원책이 막는 모습</strong>",
     "이었다. 선물은 장 막판 매도 수량을 줄이며 800억대에 그쳤고, ",
     "이는 ‘내일 추가 하락이 제한될 수 있다’는 시그널로 읽혔다.")}
</section>
"""


def section_macro() -> str:
    chain = ch.chain_h(
        [
            ("미·이란 협상 시한 종료", "bad"),
            ("호르무즈 리스크", "bad"),
            ("유가 상승", "warn"),
            ("인플레 우려", "warn"),
            ("미 국채금리 상승", "bad"),
            ("고PER 밸류 압박", "bad"),
        ],
        per_line=8,
    )
    rate = ch.threshold_scale(
        [
            (RATES["us10y_after_buyback"], f"바이백 후 {RATES['us10y_after_buyback']}%", 1),
            (RATES["us10y_close"], f"8/18 종가 {RATES['us10y_close']}%", 0),
            (RATES["us10y_intraday"], f"장중 {RATES['us10y_intraday']}%", 2),
        ],
        [
            (4.40, RATES["safe_line"], "#1f8a4c", "4.7% 이하 · 성장주 부담 완화"),
            (RATES["safe_line"], RATES["danger_line"], "#d98c1f", "부담 구간"),
            (RATES["danger_line"], 5.20, "#c0392b", "5% 돌파 · 위험자산 회피"),
        ],
        4.40,
        5.20,
        unit="%",
        axis_label="미국 10년물 — 단기 최대 변수 (30년물은 언론용)",
    )
    oil = ch.threshold_scale(
        [
            (OIL["wti_now"], f"WTI ${OIL['wti_now']:.0f}", 0),
            (OIL["brent_stable"], f"브렌트 안정 ${OIL['brent_stable']:.0f}", 1),
            (OIL["brent_danger"], f"악순환 ${OIL['brent_danger']:.0f}", 0),
        ],
        [
            (70, OIL["brent_stable"], "#1f8a4c", "충격 완화"),
            (OIL["brent_stable"], OIL["brent_danger"], "#d98c1f", "인플레 재점화"),
            (OIL["brent_danger"], 115, "#c0392b", "금리 악순환"),
        ],
        70,
        115,
        unit="$",
        dec=0,
        axis_label="유가 임계선 — 이번 조정의 출발점",
    )
    buyback = ch.bar_v_group(
        ["국채 바이백(10억 달러)", "미국 국가부채(조 달러)"],
        [
            {"name": "기존", "values": [TREASURY_BUYBACK["before_bn"], None], "color": PALE},
            {"name": "확대 후 / 현재", "values": [TREASURY_BUYBACK["after_bn"], TREASURY_BUYBACK["us_debt_tn"]], "color": BLUE},
        ],
        dec=0,
        height=280,
    )
    return f"""
<section id="s3">
  <h2><span class="num">03</span>매크로: 전쟁 → 유가 → 금리</h2>
  <p class="sub">핵심 악재는 전쟁 그 자체가 아니라, 전쟁이 만들어 낸 금리였다.</p>
  {fig(chain, "그림 3. 8/19 새벽 코멘트가 그린 전달 경로")}
  {fig(rate, "그림 4. 미국 10년물 위치. 4.7% 이하 안정 vs 5.0% 돌파가 단기 분기점")}
  {fig(oil, "그림 5. 유가 임계선. 현재 WTI는 안정 구간, 확전 시 90~100이 다음 문")}
  {p("허재환(유진)의 «금리는 무죄»는 같은 숫자를 다른 프레임으로 읽는다. ",
     f"미국 성장 {RATES['us_growth']}, 물가 {RATES['us_cpi']}, 명목성장 {RATES['us_nominal_growth']}. ",
     f"기준금리 {RATES['policy_rate_pain_lo']:.0f}~{RATES['policy_rate_pain_hi']:.0f}%, ",
     f"장기금리 {RATES['long_rate_pain_lo']:.0f}~{RATES['long_rate_pain_hi']:.0f}%가 ",
     "성장에 타격을 주는 구간이며, 지금은 그 직전이다. ",
     "국내 급락의 더 큰 이유는 2주 만에 코스피 +25%, SOX +21% 이후의 차익실현이라는 해석이다.")}
  {fig(buyback, "그림 6. 재무부 장기채 바이백 2배 확대. 부채 40조 달러는 그대로")}
  {note("warn", "바이백은 방어선이지 해결이 아니다",
       "장기채 수급을 일시적으로 완화할 뿐, 재정적자 · 인플레 · AI CAPEX 자금 수요는 그대로다. "
       f"7월 FOMC 의사록은 매파적({TREASURY_BUYBACK['fomc_hike_votes']}명 25bp 인상 주장)이었고, "
       "시장은 고용·소비 둔화를 이유로 추가 인상 확률을 낮게 본다. "
       "<strong>당장은 Treasury &gt; Fed</strong>가 금리 경로를 잡고 있다.")}
  {note("bad", "FT 이란 보도의 정확한 독해",
       "「이란이 유럽을 공격하기로 결정했다」가 아니다. 트럼프가 추가 확전할 경우를 대비해 "
       "불가리아·키프로스 등 남동부 유럽 미군 시설과 호르무즈 해저 인프라 타격을 "
       "<em>검토</em>하고 있다는 내부 인사 인용이다.")}
</section>
"""


def section_us() -> str:
    s18 = ch.bar_h(US_SESSION_0818, pos_color=GREEN, neg_color=RED)
    chips = ch.bar_h(US_CHIPS_0818, pos_color=GREEN, neg_color=RED)
    s19 = ch.bar_h(US_SESSION_0819, pos_color=GREEN, neg_color=RED)
    bio = ch.bar_h(BIO_0819, pos_color=GREEN, neg_color=RED)
    bio_idx = ch.bar_h(BIO_INDEX, pos_color=GREEN, neg_color=RED)
    return f"""
<section id="s4">
  <h2><span class="num">04</span>미국장 두 세션</h2>
  <p class="sub">8/18은 금리 충격의 반도체 투매, 8/19는 마벨·바이오가 주도한 로테이션.</p>
  <h3>8월 18일 (한국 19일 새벽) — 금리 쇼크</h3>
  {fig(s18, "그림 7. 8/18 미국 지수. 한국 익스포저(EWY)가 SOX보다 더 맞았다")}
  {fig(chips, "그림 8. 같은 세션 반도체 종목. 메모리·스토리지가 GPU보다 낙폭이 컸다")}
  <h3>8월 19일 — 마벨 vs 브로드컴, 그리고 바이오</h3>
  {fig(s19, "그림 9. 8/19 마감. 마벨 +9.9% / 브로드컴 -4.6%가 당일 특이쌍")}
  {fig(bio, "그림 10. 모더나 암백신 3상. 종목별 등락 목록(07:52) 기준 +77%")}
  {fig(bio_idx, "그림 11. 바이오 지수. NBI 7,300 부근 역사적 신고가")}
  {note("warn", "모더나 등락률은 원문에 세 값이 있다",
       "같은 세션에 대해 +77% / +117.22% / +177%가 각각 적혀 있다. "
       "차트는 종목 리스트의 +77%를 썼다. 시가총액은 MSD 3,690억달러, 모더나 559억달러.")}
  {p("로테이션의 함의는 단순하다. ",
     "<strong>금리 하락 = 기술주 매수</strong> 공식만 보고 안도하면 안 된다. ",
     f"다음 확인 포인트는 {NVDA_PREVIEW['earnings_date']} 엔비디아 실적이다. ",
     "AI 투자심리가 다시 붙는지, 헬스케어로 성장주 자금이 더 빠지는지가 갈린다.")}
</section>
"""


def _fcf_rows():
    rows = []
    for name, spec in FCF_SCENARIOS.items():
        half = spec["cum"] * 0.5
        extra = half - BUYBACK["amount_trn"]
        detail = " / ".join(f"{v:.0f}" for v in spec["detail"]) if spec["detail"] else "—"
        rows.append(
            [
                _h(name),
                f"{spec['cum']:.0f}조",
                detail,
                f"{half:.1f}조",
                f"{extra:.1f}조",
            ]
        )
    return rows


def section_buyback() -> str:
    wf2 = ch.waterfall(
        [
            ("최소 환원 192.5", 192.5, "base"),
            ("이미 확정 40조", 40, "minus"),
            ("추가 필요 152.5", 152.5, "total"),
        ],
        height=280,
    )
    kx = PEER_BUYBACK["키옥시아"]
    kline = ch.line_chart(
        [kx["p0_label"], kx["p1_label"], kx["p2_label"]],
        [{"name": "키옥시아 (엔)", "values": [kx["p0"], kx["p1"], kx["p2"]], "color": NAVY}],
        unit="",
        dec=0,
        height=260,
        y_min=45000,
        y_max=52000,
    )
    donut = ch.donut(BUYBACK["share_pct"], f"{BUYBACK['share_pct']}%", "발행주식 소각", color=GOLD)
    return f"""
<section id="s5">
  <h2><span class="num">05</span>SK하이닉스 주주환원</h2>
  <p class="sub">국내 상장사 자사주 소각 역대 최대. 정책은 ‘50% 범위 내’에서 ‘50% 이상’으로 바뀌었다.</p>
  <div class="grid2">
    <div>{fig(donut, "그림 12. 40조 = 발행주식 약 3.3%, EPS +3.4%")}</div>
    <div>
      {p(f"취득가액 <strong>40조원</strong>, 전일 종가 {BUYBACK['ref_price']:,}원 기준 약 {BUYBACK['shares_to_buy']/10_000:,.0f}만주. ")}
      {p(f"{BUYBACK['start']} ~ {BUYBACK['end']}, {BUYBACK['trading_days']} 영업일 × 일 {BUYBACK['daily_krw_bn']:,.1f}억원.")}
      {p(f"2분기 말 순현금 약 {BUYBACK['net_cash_trn']:.0f}조. ADR 발행으로 희석된 SK스퀘어 지분율을 ",
         "소각으로 발행 이전 수준에 가깝게 되돌리는 구조다.")}
      {p("회사는 현 주가가 내재가치 대비 저평가라고 직접 밝혔다. ",
         f"추가 규모·방식은 <strong>{BUYBACK['next_guide']}</strong>에 안내.")}
    </div>
  </div>
  {fig(wf2, "그림 13. 원문 A(누적 FCF 385조) 기준 환원 분해. 192.5조는 2027년 일시 지급이 아니다")}
  {table(
      ["FCF 베이스", "3년 누적", "연도별 (조원)", "50% 환원", "40조 제외 추가분"],
      _fcf_rows(),
      "표 1. 원문에 서로 다른 FCF가 있어 병기한다. 2028년 102.5조는 모델 참고치일 뿐 회사 정책이 아니다.",
  )}
  {note("warn", "192.5조를 오해하지 말 것",
       f"2025~2027 프로그램 기간 동안의 누적 환원이다. 2028년 {FCF_2028_REF}조는 "
       "FCF의 50%를 임의 적용한 참고치이며, 별도 정책이 나와야 한다. "
       "회사는 이미 ‘50% 초과’로 목표를 올렸고 특별배당도 검토 중이다.")}
  <h3>피어 자사주 — 규모만으로 주가가 가지 않는다</h3>
  {fig(kline, "그림 14. 키옥시아 8,000억엔 매입. 발표 전일 대비 +7.4%, 시황이 약할 때는 소폭")}
  {p("샌디스크 $140억 추가 승인은 8/5~8/7 ",
     f"<span class='bad'>{PEER_BUYBACK['샌디스크']['drawdown']}%</span> 구간에 나와 ",
     f"+{PEER_BUYBACK['샌디스크']['rebound']:.0f}%의 직접 원인이 아니었다. ",
     "8/13 Investor Day 이후 장기 성장률·마진 재평가가 본격 반등의 몸통이고, ",
     "바이백은 그 위에 EPS 레버리지를 더한 요인이다.")}
  {p(f"하이닉스 환원 규모 확대(항목 2~3)를 얼마나 가격에 넣을지에 따라 ",
     f"직관적 상승폭은 <strong>+{BUYBACK['expected_move_lo']:.0f}~{BUYBACK['expected_move_hi']:.0f}%</strong>로 봤다. ",
     "ADR은 장중 +5.2%(163.8달러)까지 갔다가 +0.3%로 마감했다.")}
</section>
"""


def section_valuation() -> str:
    sk, ss = VALUATION["SK하이닉스"], VALUATION["삼성전자"]
    pers = ch.bar_v_group(
        ["SK하이닉스", "삼성전자", "마이크론", "샌디스크"],
        [
            {"name": "26년 / Forward", "values": [sk["per26"], ss["per26"], US_MEMORY["마이크론"]["fwd12m_per"], US_MEMORY["샌디스크"]["per_fy27"]], "color": PALE},
            {"name": "27년 컨센", "values": [sk["per27"], ss["per27"], US_MEMORY["마이크론"]["per_cy27"], None], "color": BLUE},
            {"name": "27년 보수", "values": [sk["per_cons"], ss["per_cons"], None, None], "color": GOLD},
        ],
        unit="배",
        dec=1,
        height=320,
        cat_notes=["본주 150만원", "24.75만원", f"${US_MEMORY['마이크론']['price']}", f"${US_MEMORY['샌디스크']['price']}"],
    )
    targets = ch.range_bars(
        [
            ("SK하이닉스 26년 PER 6~7배", TARGETS["SK하이닉스"][0] / 10000, TARGETS["SK하이닉스"][1] / 10000, NAVY, "성장 없음 가정"),
            ("삼성전자 26년 PER 6~7배", TARGETS["삼성전자"][0] / 10000, TARGETS["삼성전자"][1] / 10000, BLUE, "성장 없음 가정"),
            ("ADR 정상 프리미엄(+20%) 역산", ADR["implied_at_normal"] / 10000, ADR["implied_at_normal"] / 10000, GOLD, "본주 190만"),
            ("ADR 최근 프리미엄(30~35%) 역산", ADR["implied_recent_lo"] / 10000, ADR["implied_recent_hi"] / 10000, AMBER, "본주 169~175만"),
        ],
        140,
        260,
        unit="만원",
        label_w=280,
        ref=(150, "본주 150만"),
    )
    return f"""
<section id="s6">
  <h2><span class="num">06</span>밸류에이션 맵</h2>
  <p class="sub">본주 150만원 / 24.75만원 기준. ADR은 장중 고가 163.8달러·1,390원 환산.</p>
  {fig(pers, "그림 15. 메모리 4사 PER. 하이닉스 본주는 마이크론 대비 할인이 과거(-20~-50%)보다 좁다")}
  {table(
      ["", "주가", "26년 OP / EPS", "27년 OP / EPS", "보수 시나리오"],
      [
          ["SK하이닉스", "150만원",
           f"{sk['op26']:.0f}조 / {sk['eps26']/1000:.0f}천원",
           f"{sk['op27']:.0f}조 / {sk['eps27']/1000:.0f}천원",
           f"{sk['op_cons']} / {sk['eps_cons_lo']/1000:.0f}~{sk['eps_cons_hi']/1000:.0f}천원"],
          ["삼성전자", "24.75만원",
           f"{ss['op26']:.0f}조 / {ss['eps26']/1000:.1f}천원",
           f"{ss['op27']:.0f}조 / {ss['eps27']/1000:.1f}천원",
           f"{ss['op_cons']} / {ss['eps_cons_lo']/1000:.0f}~{ss['eps_cons_hi']/1000:.0f}천원"],
      ],
      "표 2. 영업이익·EPS 컨센서스와 보수 밴드",
  )}
  {fig(targets, "그림 16. 26년 실적에 과거 사이클 배수(4~8배 중 6~7배)만 적용한 기계적 밴드")}
  {p(f"ADR 프리미엄은 본주 대비 <strong>{ADR['premium_now']:.0f}%</strong>로 비정상적으로 넓다. ",
     f"TSMC 참고 {ADR['premium_normal']-5:.0f}%·정상 +{ADR['premium_normal']:.0f}%를 적용하면 본주 {ADR['implied_at_normal']/10000:.0f}만, ",
     f"최근 실제 30~35%를 적용하면 {ADR['implied_recent_lo']/10000:.0f}~{ADR['implied_recent_hi']/10000:.0f}만. ",
     f"마이크론 대비 ADR 할인은 {ADR['gap_vs_micron']:.0f}% (과거 {ADR['gap_history']}).")}
</section>
"""


def section_fx() -> str:
    drop = (FX["scenario_from"] - FX["scenario_to"]) / FX["scenario_from"] * 100
    axis = ch.threshold_scale(
        [
            (FX["spot_ref"], f"코멘트 시점 {FX['spot_ref']:.0f}", 0),
            (FX["scenario_to"], f"가정 {FX['scenario_to']:.0f}", 1),
            (FX["usdkrw_floor_calc"], f"DXY만으로 {FX['usdkrw_floor_calc']:.0f}", 2),
            (FX["usdkrw_floor_ext"], f"공급 가세 {FX['usdkrw_floor_ext']:.0f}", 0),
        ],
        [
            (1320, FX["usd_demand_zone"], "#4a80c4", "달러 수요 증가 가능"),
            (FX["usd_demand_zone"], 1400, "#d98c1f", "추가 강세 구간"),
            (1400, 1550, "#1f8a4c", "수출주 환익 구간"),
        ],
        1320,
        1550,
        unit="",
        dec=0,
        axis_label="원/달러 — 1,400 붕괴는 달러인덱스만으로 설명되지 않는다",
    )
    sens = ch.bar_v_group(
        ["원/달러 +1%", "1,520→1,420 (약 -6.6%)"],
        [
            {"name": "삼성전자 EPS", "values": [FX["sens_samsung"], FX["sens_samsung"] * drop], "color": BLUE},
            {"name": "SK하이닉스 EPS", "values": [FX["sens_hynix"], FX["sens_hynix"] * drop], "color": GOLD},
        ],
        unit="%",
        dec=1,
        height=300,
    )
    adj = ch.range_bars(
        [
            ("2027 순익 300~400조 가정 시 이익 조정", 18, 24, GOLD, "EPS -5.9% 적용"),
            ("26년 하반기 환율 반영", 16.3, 16.3, AMBER, "별도 코멘트"),
        ],
        0,
        30,
        unit="조원",
        label_w=300,
        dec=1,
    )
    chain = ch.chain_v(
        [
            ("국내 수급: 8월말 법인세 + 설비투자 원화 수요", "key"),
            ("수출기업 달러 매도 · 환헤지 비중 상승", "neutral"),
            ("달러-원 하락 → 고환율대 추가 매도", "warn"),
            ("환율 하락 가속 (1,400원 하회)", "bad"),
        ],
        width=700,
        node_w=520,
    )
    return f"""
<section id="s7">
  <h2><span class="num">07</span>원/달러와 실적 민감도</h2>
  <p class="sub">“달러 약세 때문에 원화가 강해졌다”가 아니라, 한국 달러 공급이 먼저 떨어뜨렸다.</p>
  {fig(chain, "그림 17. 1,400원 하회의 국내 수급 경로")}
  {fig(axis, "그림 18. 달러인덱스 3~4% 하락 시 계산상 1,360원, 공급 가세 시 1,340원대")}
  {p(f"추가 하락의 핵심 변수는 달러다. 시장은 연준 인상 1~2회를 일부 반영 중이며, ",
     f"기대가 되돌려지면 미국 금리 하락 → DXY {FX['dxy_now']:.0f} → {FX['dxy_target_lo']:.0f}~{FX['dxy_target_hi']:.0f} → ",
     "달러-원 추가 하락이 열린다. 1,300원대 중반은 이 조건부 경로의 끝이다.")}
  {fig(sens, "그림 19. 환율 민감도. 하이닉스가 삼성전자의 두 배 이상")}
  {fig(adj, "그림 20. 1,520→1,420 가정 시 하이닉스 EPS 약 -5.9%, 이익 18~24조 조정")}
  {note("bad", "원화 추가 강세의 세 리스크",
       "① 외국인 국내주식 매도 확대  ② 미국-이란 / 유가  ③ 1,350원 부근 달러 수요 증가. "
       "수출주 원화약세 효과는 3Q에 빠르게 줄어들 수 있다.")}
</section>
"""


def section_yen() -> str:
    nk = YEN_CARRY_2024["nikkei"]
    ks = YEN_CARRY_2024["kospi"]
    crash = ch.bar_v_group(
        ["Nikkei", "KOSPI"],
        [
            {"name": "7/31→8/5", "values": [(nk["0805"] / nk["0731"] - 1) * 100, (ks["0805"] / ks["0731"] - 1) * 100], "color": RED},
            {"name": "8/6 반등", "values": [nk["0806_pct"], ks["0806_pct"]], "color": GREEN},
        ],
        unit="%",
        dec=1,
        height=300,
        cat_notes=[f"{nk['0731']:,}→{nk['0805']:,}", f"{ks['0731']:,}→{ks['0805']:,}"],
    )
    return f"""
<section id="s8">
  <h2><span class="num">08</span>엔캐리 체크리스트</h2>
  <p class="sub">일본 금리 상승만으로 엔캐리 청산을 단정하지 말 것. 달러/엔 경로가 판별식이다.</p>
  {fig(crash, "그림 21. 2024년 8월형 청산. 하루 펀더멘털 변화가 아니라 레버리지 청산의 증거")}
  {p("당시 USD/JPY는 약 152~153에서 142~145로 6%대 급락했다. ",
     "8/2에 이미 닛케이 -5.81%, 코스피 -3.65%가 나왔고 주말 후 8/5 투매, ",
     "8/6에 각각 +10.23% / +3.30%로 바로 되돌렸다.")}
  {p(f"현재 달러/엔은 {YEN_CARRY_2024['now_usdjpy_lo']:.0f}~{YEN_CARRY_2024['now_usdjpy_hi']:.0f}에서 반등 중이다. ",
     "이 상태라면 일본 장기금리 상승의 1차 충격은 엔캐리보다 ",
     "<strong>글로벌 채권금리 상승 / 밸류에이션 압박</strong> 쪽에 가깝다. ",
     f"2026년에도 159→155→150으로 빠르게 내려가면 그때가 2024년 8월형을 의심할 단계다.")}
  {note("good", "흡수 조건",
       "엔화가 안정되고, 미국 금리가 안정되며, 일본 국채 입찰이 견조하면 "
       "이번 움직임은 일본의 금리 정상화 과정으로 흡수될 가능성이 높다. "
       "미 기준금리 인하가 2024년과 비슷한 패턴을 부를 수 있으나, 미·이란 종전이 임박하지 않는 한 쉽지 않다.")}
</section>
"""


def section_hbm() -> str:
    matrix = ch.quad_matrix(
        ("대체 vs 분업", "완전 대체 시도", "계층적 분업"),
        ("타당성", "높음", "낮음"),
        [
            ("가격 급등 = 수요 즉시 붕괴", "HBM이 비싸졌으니 메모리 수요가 곧 꺾인다. 타당성 낮음.", "bad"),
            ("가격 급등 = 효율화 유인", "고객이 SRAM·압축·경량화·ASIC에 투자할 경제적 유인이 커진다. 타당성 높음.", "good"),
            ("공급자 = 호르무즈", "벤 톰슨 비유. 단기 지대는 가능하나 장기 대체 공급망을 부른다.", "warn"),
            ("SRAM ≠ HBM", "없애는 것이 아니라 workload별 SRAM+HBM+DRAM+SSD 최적 조합.", "neutral"),
        ],
    )
    cases = ch.progress_bars(
        [
            (HBM_CASES[0][0], 90, GREEN, HBM_CASES[0][1]),
            (HBM_CASES[1][0], 90, GREEN, HBM_CASES[1][1]),
            (HBM_CASES[2][0], 90, GREEN, HBM_CASES[2][1]),
            (HBM_CASES[3][0], 90, GREEN, HBM_CASES[3][1]),
            (HBM_CASES[4][0], 55, AMBER, HBM_CASES[4][1]),
        ],
        label_w=170,
        dec=0,
    )
    demand = ch.bar_v_group(
        ["추론 +50%", "메모리 효율 +20%", "추론 +20%", "메모리 효율 +30%"],
        [
            {"name": "원문 예시 속도", "values": [50, 20, 20, 30], "color": BLUE},
        ],
        unit="%",
        dec=0,
        height=260,
        cat_notes=["수요 증가 우위", "", "효율화 우위", ""],
    )
    return f"""
<section id="s9">
  <h2><span class="num">09</span>HBM 대체 논쟁 — 캐시 우드 · 벤 톰슨</h2>
  <p class="sub">「왜 메모리주를 사지 않는가」는 ‘현재 메모리주가 틀렸다’가 아니라 ‘가격결정력은 영구가 아니다’라는 경고로 읽는 것이 타당하다.</p>
  {fig(matrix, "그림 22. 두 거물 논리의 재배치. 핵심 변수는 AI 연산 증가율 − 메모리 효율 개선률")}
  {fig(cases, "그림 23. 이미 현실에서 나타나는 우회. 높음 4 · 진행 중 1")}
  {fig(demand, "그림 24. 같은 방향의 두 속도. 효율화가 앞서면 수요 증가세만 꺾인다")}
  {p("결론을 문장으로 고정하면 이렇다. ",
     "<strong>HBM 가격 상승은 2026~28년 메모리 업체의 초과이익을 만들지만, ",
     "지나치면 2028년 이후 효율화·대체 기술을 촉진하는 양날의 검이다.</strong> ",
     "헤게모니 싸움(메모리 vs 비메모리)으로 프레임이 굳어지는 것은 부담이다.")}
</section>
"""


def section_foundry() -> str:
    hike = ch.range_bars(
        [(a, b, c, GOLD if c >= 15 else BLUE) for a, b, c in FOUNDRY_HIKE],
        0,
        20,
        unit="%",
        label_w=280,
        dec=0,
    )
    mix = ch.bar_v_group(
        ["AI·HPC 매출 비중", "첨단공정 매출 비중", "TSMC 점유율(참고)"],
        [
            {"name": "2025 말", "values": [sum(FOUNDRY_MIX["ai_hpc_2025"]) / 2, None, None], "color": PALE},
            {"name": "올해(가이던스)", "values": [FOUNDRY_MIX["ai_hpc_2026"], FOUNDRY_MIX["adv_node_2026"], FOUNDRY_MIX["tsmc_share"]], "color": BLUE},
        ],
        unit="%",
        dec=0,
        height=280,
    )
    capa = ch.roadmap(
        [(a, b, c) for a, b, c in ISU["capa"]],
        unit="억원/월",
        height=280,
    )
    ml = ch.line_chart(
        [a for a, _ in ISU["multilam"]],
        [{"name": "Multi-Lam 비중", "values": [b for _, b in ISU["multilam"]], "color": NAVY}],
        unit="%",
        dec=0,
        height=250,
        y_min=0,
        y_max=28,
    )
    return f"""
<section id="s10">
  <h2><span class="num">10</span>삼성 파운드리 · 이수페타시스 · 기가비스</h2>
  <p class="sub">TSMC 포화 → 삼성 가격 협상력. 기판·검사 장비는 AI → FC-BGA/Multi-Lam으로 연결된다.</p>
  <h3>삼성전자 파운드리 판가</h3>
  {fig(hike, "그림 25. 신규 주문 기준 최대 +15%. Reuters 2026-08-19")}
  {fig(mix, "그림 26. 첨단·AI 믹스 상승. 평택 SF4는 퀄컴 + 자체 HBM 베이스다이로 풀가동")}
  {p("적자 파운드리의 흑자 전환이 내년으로 거론된다. 고객 파이프라인은 테슬라·애플·브로드컴·엔비디아 추론칩에 이어 ",
     "구글 4나노 협의. 중국 팹리스의 해외 파운드리 의존도도 배경이다.")}
  <h3>이수페타시스 — Capa가 아니라 Multi-Lam 레버리지</h3>
  {fig(ml, "그림 27. Multi-Lam 1Q 7% → 2Q 11% → 수주잔고 20%+")}
  {fig(capa, "그림 28. 월 매출 Capa 1,200 → 1,500(27.2Q) → 1,800(28H2)")}
  {table(
      ["2Q26", "금액", "YoY", "컨센 대비"],
      [
          ["매출", f"{ISU['rev']:,.0f}억원", f"<span class='good'>+{ISU['rev_yoy']}%</span>", f"+{ISU['rev_beat']}%"],
          ["영업이익", f"{ISU['op']:,.0f}억원", f"<span class='good'>+{ISU['op_yoy']}%</span>", f"+{ISU['op_beat']}%"],
          ["OPM", f"{ISU['opm']}%", "—", "—"],
      ],
  )}
  {p(f"하반기 판가 약 +{ISU['price_hike']:.0f}%, 4Q부터 G사 Multi-Lam 전환 + M사 ASIC 양산. ",
     f"2027 영업이익은 컨센 대비 +{ISU['op27_upside']:.0f}% 전후 상향 여지. ",
     f"Peer 하락으로 타깃 멀티플 {ISU['multiple_old']}배 → {ISU['multiple_new']}배. ",
     "주가 조정 = 실적 상향 국면의 매수 기회라는 논리.")}
  <h3>기가비스 — 기판의 눈과 레이저 수리공</h3>
  {p(f"일본 기판사에 검사·수리장비 {GIGAVIS['contract']}억원 ({GIGAVIS['contract_ratio']}%, ",
     f"{GIGAVIS['period']}). 2025 매출 {GIGAVIS['rev25']:.0f}억 / OP {GIGAVIS['op25']:.0f}억 → ",
     f"2026E {GIGAVIS['rev26e']:,.0f}억 / {GIGAVIS['op26e']:,.0f}억 (메리츠). ",
     f"증권사 컨센 TP {GIGAVIS['tp']/10000:.0f}만원, 26년 실적 기준으로는 비싸고 27년 성장이 초점. ",
     "분할 접근 후보.")}
</section>
"""


def section_names() -> str:
    ls_bars = ch.bar_h(
        [(n, op, GREEN if (yoy or 0) > 0 else AMBER) for n, op, qoq, yoy, _ in LS_GROUP["subs"]],
        unit="억원",
        dec=0,
        pos_color=GREEN,
        label_w=130,
    )
    lges = ch.donut(LGES["plants_to_ess"] / LGES["plants_total"] * 100, f"{LGES['plants_to_ess']}/{LGES['plants_total']}", "북미 공장 ESS 전환", color=GREEN)
    return f"""
<section id="s11">
  <h2><span class="num">11</span>개별 종목 — 방산 · 전선 · 배터리 · 바이오</h2>
  <h3>한화에어로스페이스 — 미 육군 MTC 단독 선정</h3>
  {p(f"{HANWHA_AERO['program']}. 시제기 {HANWHA_AERO['initial_usd_mn']}백만달러, ",
     f"옵션 포함 {HANWHA_AERO['option_total_usd_mn']}백만달러. ",
     f"{HANWHA_AERO['years']}년간 기본 {HANWHA_AERO['units_base']}문 + 옵션 {HANWHA_AERO['units_option']}문. ",
     f"양산은 약 {HANWHA_AERO['mass_production_trn']:.0f}조원 규모 사업 진입으로 읽힌다. ",
     "궤도형(K9) 1위에 차륜형 미국 레퍼런스가 더해지는 지점이다.")}
  <h3>LS — 자회사 이익 체력의 구조적 상승</h3>
  {p(f"연결 OP {LS_GROUP['op']:,.0f}억원 (<span class='good'>+{LS_GROUP['op_qoq']}% QoQ, +{LS_GROUP['op_yoy']}% YoY</span>), 2분기 연속 최대. ",
     f"26/27년 OP 전망 +{LS_GROUP['op26_up']}% / +{LS_GROUP['op27_up']}%. 구리 ${LS_GROUP['copper']:,}. ",
     f"자사주 {LS_GROUP['treasury_pct']}% ({LS_GROUP['treasury_shares']:,}주) — 소각 의무화로 하반기 논의.")}
  {fig(ls_bars, "그림 29. 주요 자회사 2Q 영업이익 (억원)")}
  <h3>LG에너지솔루션 — 북미 EV → ESS</h3>
  <div class="grid2">
    <div>{fig(lges, "그림 30. 북미 EV 공장 8곳 중 5곳 ESS 전환")}</div>
    <div>
      {p(f"랜싱 {LGES['lansing_gwh']}GWh+, 테슬라 메가팩 LFP ${LGES['tesla_usd_bn']}B (약 {LGES['tesla_krw_trn']}조). ",
         "연말 ESS 흑자 전환 목표. 드론·무인체계 배터리 협상은 다음 축.")}
    </div>
  </div>
  <h3>알테오젠 — 키트루다SC가 상업화 구간에 들어왔다</h3>
  {p(f"키트루다SC 2Q 매출 ${ALTEOGEN['keytruda_sc_q2_usd_mn']}M, 미국 출시 후 {ALTEOGEN['quarters_since_launch']}개 분기. ",
     "엑셀리시스가 잔잘린티닙 병용 3상에 키트루다SC를 쓰는 첫 외부 사례. ",
     "엔허투 폐암 1차 청신호와 맞물려 ADC SC 옵션 가치가 커진다. ",
     f"MSD 시총 ${ALTEOGEN['msd_mktcap_usd_bn']:.0f}B, 모더나 ${ALTEOGEN['moderna_mktcap_usd_bn']:.1f}B.")}
</section>
"""


def section_global() -> str:
    nvda = ch.bar_v_group(
        ["Q3 매출", "Q4 매출(둔화 가정)"],
        [{"name": "십억 달러", "values": [NVDA_PREVIEW["q3_rev_bn"], NVDA_PREVIEW["q4_rev_bn"]], "color": GREEN}],
        unit="B",
        dec=0,
        height=260,
        cat_notes=[f"YoY +{NVDA_PREVIEW['q3_yoy']:.0f}%", f"YoY +{NVDA_PREVIEW['q4_yoy']:.0f}%"],
    )
    openai = ch.bar_v_group(
        ["분기 매출", "영업손실"],
        [
            {"name": "직전", "values": [None, OPENAI["op_loss_prev_bn"]], "color": PALE},
            {"name": "Q2", "values": [OPENAI["q2_rev_bn"], OPENAI["op_loss_bn"]], "color": RED},
        ],
        unit="B",
        dec=1,
        height=260,
    )
    psr = ch.bar_h(
        [
            ("시장 CAGR 정당화선 (PSR)", UNITREE["psr_bar"], BLUE),
            ("Unitree 종가 PSR", UNITREE["psr"], RED),
        ],
        unit="배",
        dec=0,
        pos_color=RED,
        label_w=220,
    )
    warrant = ch.chain_h(
        [
            ("Custom 매출 $5억", "neutral"),
            ("1 tranche 베스팅", "key"),
            (f"최대 {MARVELL_GOOGLE['warrant_shares']/10000:,.1f}만주", "warn"),
            (f"행사가 ${MARVELL_GOOGLE['strike']}", "good"),
        ],
        per_line=11,
    )
    return f"""
<section id="s12">
  <h2><span class="num">12</span>글로벌 AI 이벤트</h2>
  <h3>Google × Marvell — TPU 주변 생태계 공유</h3>
  {fig(warrant, f"그림 31. Warrant는 FY2027 Q3~FY2033. 매출과 주식 보상이 연동")}
  {p("적용 영역은 추론 가속기 + 스토리지 컨트롤러 + NIC + 메모리 인터페이스 + 니어메모리 컴퓨트. ",
     "브로드컴의 TPU 독점에 대한 견제 신호로 읽혔고, 마감 기준 마벨 ",
     f"<span class='good'>+{MARVELL_GOOGLE['marvell_move']}%</span> / 브로드컴 ",
     f"<span class='bad'>{MARVELL_GOOGLE['avgo_move']}%</span>.")}
  <h3>NVIDIA Q2 FY27 프리뷰 — Beat보다 Rubin과 CAPEX</h3>
  {fig(nvda, "그림 32. 성장률이 +77%로 둔화돼도 Q4 매출은 $120B")}
  {p(f"Rubin은 {NVDA_PREVIEW['rubin_start']}, 칩 {NVDA_PREVIEW['rubin_chips']}개 · 랙 {NVDA_PREVIEW['rubin_racks']}개, ",
     f"추론 {NVDA_PREVIEW['rubin_inference_x']}배 · AI Factory {NVDA_PREVIEW['rubin_aifactory_x']}배, ",
     f"랙 가격 ${NVDA_PREVIEW['rubin_rack_lo']}~{NVDA_PREVIEW['rubin_rack_hi']}M (Blackwell Ultra의 약 {NVDA_PREVIEW['blackwell_multiple']:.0f}배). ",
     f"Top5 하이퍼스케일러 2027 CAPEX ≥ ${NVDA_PREVIEW['hyperscaler_capex_tn']:.0f}T (+{NVDA_PREVIEW['hyperscaler_capex_growth']:.0f}%). ",
     f"GM {NVDA_PREVIEW['gm']:.0f}% 유지와 circular financing 논쟁이 관전 포인트.")}
  {fig(openai, f"그림 33. OpenAI Q2 매출 ${OPENAI['q2_rev_bn']}B (QoQ +{OPENAI['q2_qoq']:.0f}%), 손실은 ${OPENAI['op_loss_prev_bn']}B → ${OPENAI['op_loss_bn']}B")}
  {p("매출 증가 + 손실 확대가 SOX -2.12%로 연결된 경로: 회수기간 장기화 우려 → 인프라 투자기업 부담 → GPU·HBM·네트워크 단기 우려.")}
  <h3>Unitree — 상장 첫날 5배, PSR 155배</h3>
  {fig(psr, "그림 34. ‘시장 31%면 PSR 60배’ 프레임 대비 종가는 약 2.6배")}
  {p(f"공모 조달 약 ${UNITREE['ipo_raise_usd_bn']}B, 상장 후 시총 {UNITREE['post_ipo_cny_100mn']:.2f}억 위안, ",
     f"종가 시총 {UNITREE['close_mktcap_cny_100mn']:.0f}억 위안 / 26년 매출 {UNITREE['rev26_cny_100mn']:.0f}억 위안. ",
     f"휴머노이드 소재비 중국 ${UNITREE['bom_china_usd_k']:.0f}k vs 미국 ${UNITREE['bom_us_usd_k']:.0f}k (35%). ",
     f"JP모건은 중국 점유 {UNITREE['jpm_china_share']:.0f}%, 유니트리 미국 매출 비중은 {UNITREE['us_rev_share']:.0f}%. ",
     f"1Q 순이익 {UNITREE['q1_profit_cny_mn']}백만 위안 ({UNITREE['q1_profit_yoy']}%). 상업화 이전이 가장 큰 리스크다.")}
</section>
"""


def section_triggers() -> str:
    rows = []
    for name, now, ok, ng, why, t in TRIGGERS:
        rows.append(
            [
                _h(name),
                _h(now),
                f"<span class='good'>{_h(ok)}</span>",
                f"<span class='bad'>{_h(ng)}</span>",
                _h(why),
            ]
        )
    conflicts = "".join(f"<li><strong>{_h(k)}</strong> — {_h(v)}</li>" for k, v in CONFLICTS)
    return f"""
<section id="s13">
  <h2><span class="num">13</span>앞으로 볼 트리거</h2>
  <p class="sub">무게 중심은 여전히 &lt;전쟁발 매크로 vs 투자의지 vs 토큰 수요&gt;의 왼쪽이다. 궤도 자체가 꺾였다고 보기는 어렵다.</p>
  {table(["변수", "현재 (코멘트)", "안정", "위험", "왜 보는가"], rows)}
  {p("국내 기관의 고민은 AI 비중을 줄일지보다, ",
     "<strong>대형주 익스포저 vs 변압기/소부장 믹스</strong>다. ",
     "글로벌 자금의 선호 순서는 빅테크 → 파운드리 → 메모리, 미국 → 일본 → 한국.")}
  <h3>원문에서 숫자가 갈리는 곳</h3>
  <ul>{conflicts}</ul>
</section>
"""


def footer() -> str:
    return """
<footer>
  이 자료는 2026년 8월 19일 채팅 코멘트를 재구성한 참고용 브리프다.
  매수·매도 추천이 아니며 투자 판단과 책임은 각 독자에게 있다. 법적 자료로 사용할 수 없다.
  원문 수치를 우선했고, 상충하는 값은 각주에 남겼다. 재계산은 <code>scripts/test_aug19_report_numbers.py</code>.
</footer>
"""


def build() -> str:
    body = "".join(
        [
            section_cover(),
            section_scoreboard(),
            section_timeline(),
            section_macro(),
            section_us(),
            section_buyback(),
            section_valuation(),
            section_fx(),
            section_yen(),
            section_hbm(),
            section_foundry(),
            section_names(),
            section_global(),
            section_triggers(),
            footer(),
        ]
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>2026.08.19 데일리 시장 리포트</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="page">
  {body}
  </div>
</body>
</html>
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    html = build()
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"wrote {OUT_HTML} ({OUT_HTML.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
