"""Standalone Korean HTML / Markdown / JSON report for the hybrid book."""

from __future__ import annotations

import json
from pathlib import Path

from hybrid_synthesis.model import HybridSnapshot, Scenario
from hybrid_synthesis.portfolio import Portfolio, SLEEVE_ORDER

SLEEVE_KO = {
    "CORE_SEMI": "코어 반도체",
    "AI_CONNECT": "AI 넥스트 소부장",
    "MACRO_HEDGE": "매크로 헷지·인프라",
    "COSMETICS": "데이터 스윙 화장품",
}

ACTION_KO = {
    "CORE_HOLD": "핵심 보유",
    "ACCUMULATE": "분할 매수",
    "TRADE": "스윙",
    "HEDGE": "헷지",
    "WATCH": "관찰",
    "AVOID": "배제",
}


def _pct(value: float, digits: int = 1) -> str:
    return f"{value * 100:.{digits}f}%"


def _won(value: float) -> str:
    return f"{value:,.0f}원"


def _num(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}"


def _holding_rows(portfolio: Portfolio) -> str:
    rows = []
    for item in portfolio.holdings:
        cash = portfolio.reference_krw * item.weight_total
        proxy = ", ".join(item.kosdaq_proxy_of) if item.kosdaq_proxy_of else "—"
        rows.append(
            "<tr>"
            f"<td class='mono'>{item.ticker}</td>"
            f"<td>{item.name}</td>"
            f"<td>{SLEEVE_KO[item.sleeve]}</td>"
            f"<td>{ACTION_KO[item.action]}</td>"
            f"<td class='num'>{item.score:.1f}</td>"
            f"<td class='num'>{_pct(item.weight_total)}</td>"
            f"<td class='num'>{_pct(item.weight_equity)}</td>"
            f"<td class='num'>{_won(cash)}</td>"
            f"<td class='proxy'>{proxy}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _thesis_cards(portfolio: Portfolio) -> str:
    cards = []
    for item in portfolio.holdings:
        cards.append(
            "<article class='thesis'>"
            f"<h4><span class='mono'>{item.ticker}</span> {item.name}"
            f"<em>{_pct(item.weight_total)}</em></h4>"
            f"<p>{item.thesis}</p>"
            "</article>"
        )
    return "\n".join(cards)


def _avoid_rows(portfolio: Portfolio) -> str:
    rows = []
    for item in portfolio.avoid:
        flags = ", ".join(item.avoid_flags) if item.avoid_flags else "—"
        rows.append(
            "<tr>"
            f"<td class='mono'>{item.ticker}</td>"
            f"<td>{item.name}</td>"
            f"<td>{flags}</td>"
            f"<td>{item.thesis}</td>"
            "</tr>"
        )
    for item in portfolio.excluded_non_kospi:
        rows.append(
            "<tr>"
            f"<td class='mono'>{item['ticker']}</td>"
            f"<td>{item['name']} <span class='tag'>KOSDAQ</span></td>"
            f"<td>non_kospi</td>"
            f"<td>{item['reason']}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _scenario_rows(scenarios: dict[str, HybridSnapshot]) -> str:
    labels = {
        Scenario.BASE.value: "기본 (현재)",
        Scenario.JAWBONING.value: "조본잉 강화",
        Scenario.HARD_LANDING.value: "10년물 5.0% 하드랜딩",
        Scenario.EARLY_PIVOT.value: "조기 피벗",
        Scenario.FCF_INFLECTION.value: "FCF 흑자 전환",
    }
    rows = []
    for key, snap in scenarios.items():
        rows.append(
            "<tr>"
            f"<td>{labels.get(key, key)}</td>"
            f"<td>{snap.phase_name}</td>"
            f"<td class='num'>{_num(snap.relief['R'], 3)}</td>"
            f"<td class='num'>{_num(snap.expansion['A'], 3)}</td>"
            f"<td class='num'>{_num(snap.defense['D'], 3)}</td>"
            f"<td class='num'>{_num(snap.momentum, 3)}</td>"
            f"<td class='num'>{_num(snap.kospi['expected'], 0)}</td>"
            f"<td class='num'>{_num(snap.kospi['band_low'], 0)}–{_num(snap.kospi['band_high'], 0)}</td>"
            f"<td class='num'>{_pct(snap.equity_weight)}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def _phase_cards() -> str:
    from hybrid_synthesis.model import PHASES, Phase

    cards = []
    for phase in (Phase.CONVERGENCE, Phase.PIVOT, Phase.SUPERCYCLE):
        meta = PHASES[phase]
        low, high = meta["kospi_band"]
        sleeves = " / ".join(f"{SLEEVE_KO[k]} {_pct(v, 0)}" for k, v in meta["sleeves"].items())
        cards.append(
            "<article class='phase'>"
            f"<div class='phase-kicker'>Phase {phase.value}</div>"
            f"<h3>{meta['name']}</h3>"
            f"<p class='window'>{meta['window']} · 밴드 {low:,.0f}–{high:,.0f}</p>"
            f"<p>{meta['narrative']}</p>"
            f"<p class='sleeves'>{sleeves}</p>"
            "</article>"
        )
    return "\n".join(cards)


def render_html(portfolio: Portfolio, scenarios: dict[str, HybridSnapshot]) -> str:
    snap = portfolio.snapshot
    f = snap.formula_terms()
    kospi = snap.kospi
    rel = snap.relief
    exp = snap.expansion
    den = snap.defense
    cut = "구조적 인하 불가 (역전)" if not snap.structural_cut_open else "구조적 인하 가능"
    partial = "PCE≤3.5 부분 룸 열림" if snap.partial_cut_room else "PCE 부분 룸 닫힘"
    landing = "하드랜딩 트리거 활성" if snap.hard_landing else "하드랜딩 미발동"
    ref = portfolio.reference_krw

    sleeve_bars = []
    for sleeve in SLEEVE_ORDER:
        weight = snap.sleeves[sleeve] * snap.equity_weight
        sleeve_bars.append(
            "<div class='bar-row'>"
            f"<span>{SLEEVE_KO[sleeve]}</span>"
            f"<div class='bar'><i style='width:{weight * 100:.1f}%'></i></div>"
            f"<em>{_pct(weight)}</em>"
            "</div>"
        )

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>통합 하이브리드 추정 모형 · 코스피 포트폴리오</title>
<style>
:root {{
  --navy: #0f2043;
  --navy2: #1e407c;
  --gold: #b8943a;
  --paper: #f6f3ea;
  --ink: #1a1a1a;
  --muted: #5b6472;
  --line: #d7d0c3;
  --good: #166534;
  --bad: #991b1b;
  --warn: #7a5c12;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; background: var(--paper); color: var(--ink);
  font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif;
  line-height: 1.55;
}}
.wrap {{ max-width: 1180px; margin: 0 auto; padding: 28px 20px 64px; }}
header.hero {{
  background: linear-gradient(135deg, var(--navy), #16325c 60%, #2a4d86);
  color: #f8f4ea; border-radius: 18px; padding: 28px 28px 24px;
  box-shadow: 0 16px 40px rgba(15,32,67,.18);
}}
header.hero p.kicker {{ letter-spacing: .12em; font-size: 12px; color: #e6d7a2; margin: 0 0 8px; }}
header.hero h1 {{ margin: 0 0 10px; font-size: 30px; line-height: 1.25; }}
header.hero .formula {{
  font-family: ui-serif, Georgia, serif; font-size: 18px; color: #f3e6c0; margin: 8px 0 14px;
}}
.meta {{ display: flex; flex-wrap: wrap; gap: 8px; }}
.pill {{
  background: rgba(255,255,255,.08); border: 1px solid rgba(255,255,255,.14);
  border-radius: 999px; padding: 4px 10px; font-size: 12px;
}}
.grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 18px 0; }}
.card {{
  background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 14px 14px 12px;
}}
.card .lbl {{ color: var(--muted); font-size: 12px; }}
.card .val {{ font-size: 28px; font-weight: 700; color: var(--navy); }}
.card .sub {{ font-size: 12px; color: var(--muted); }}
section h2 {{
  margin: 28px 0 10px; color: var(--navy); border-left: 5px solid var(--gold);
  padding-left: 10px; font-size: 22px;
}}
p.lead {{ color: #333; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; }}
th, td {{ border-bottom: 1px solid #eee; padding: 8px 8px; text-align: left; font-size: 13px; vertical-align: top; }}
th {{ background: var(--navy); color: #fff; font-weight: 600; }}
td.num, th.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
.proxy {{ color: var(--muted); font-size: 11px; }}
.tag {{ background: #f3e6c0; color: #6a4f12; border-radius: 6px; padding: 1px 6px; font-size: 11px; }}
.phases {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
.phase, .thesis {{ background: #fff; border: 1px solid var(--line); border-radius: 14px; padding: 14px; }}
.phase-kicker {{ color: var(--gold); font-weight: 700; letter-spacing: .08em; font-size: 12px; }}
.phase h3 {{ margin: 4px 0 6px; color: var(--navy); }}
.window, .sleeves {{ color: var(--muted); font-size: 12px; }}
.theses {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }}
.thesis h4 {{ margin: 0 0 6px; color: var(--navy); }}
.thesis h4 em {{ float: right; color: var(--gold); font-style: normal; }}
.bar-row {{ display: grid; grid-template-columns: 150px 1fr 56px; gap: 8px; align-items: center; margin: 6px 0; font-size: 13px; }}
.bar {{ background: #ece6d8; border-radius: 99px; height: 10px; overflow: hidden; }}
.bar i {{ display: block; height: 100%; background: linear-gradient(90deg, var(--navy2), var(--gold)); }}
.callout {{
  background: #fff8e7; border: 1px solid #e6d7a2; border-radius: 12px; padding: 12px 14px; color: #5a4710;
}}
.logic {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
.logic article {{ background: #fff; border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; }}
.logic h3 {{ margin: 0 0 6px; font-size: 16px; color: var(--navy2); }}
footer {{ margin-top: 28px; color: var(--muted); font-size: 12px; }}
@media (max-width: 900px) {{
  .grid, .phases, .theses, .logic {{ grid-template-columns: 1fr; }}
  header.hero h1 {{ font-size: 24px; }}
}}
</style>
</head>
<body>
<div class="wrap">
<header class="hero">
  <p class="kicker">HYBRID SYNTHESIS MODEL · KOSPI ONLY · {snap.as_of.isoformat()}</p>
  <h1>통합 하이브리드 추정 모형으로 짠 코스피 포트폴리오</h1>
  <p class="formula">시장 모멘텀 M = (매크로 압박 해소율 R) × (AI 이익 팽창 계수 A) + (국내 수급 방어력 D)</p>
  <div class="meta">
    <span class="pill">Phase {snap.phase.value} · {snap.phase_name}</span>
    <span class="pill">{snap.phase_window}</span>
    <span class="pill">R {_num(f['R'], 3)} · A {_num(f['A'], 3)} · D {_num(f['D'], 3)} · M {_num(f['M'], 3)}</span>
    <span class="pill">주식 {_pct(snap.equity_weight)} / 채권·현금 {_pct(1 - snap.equity_weight)}</span>
    <span class="pill">{cut} · {partial} · {landing}</span>
  </div>
</header>

<div class="grid">
  <div class="card"><div class="lbl">매크로 해소율 R</div><div class="val">{_num(rel['R'], 3)}</div><div class="sub">실질정책 {rel['real_policy']:+.2f}% vs 실질중립 {rel['real_neutral']:+.2f}% · 유효 10년물 {_num(rel['effective_ust10'])}%</div></div>
  <div class="card"><div class="lbl">AI 팽창 계수 A</div><div class="val">{_num(exp['A'], 3)}</div><div class="sub">기타수요 {_pct(exp['other_demand_share'])} · NVL72 {snap.inputs.nvl72_share:.0%}→{snap.inputs.nvl72_next_year:.0%} · FCF {exp['A_fcf']:.2f}</div></div>
  <div class="card"><div class="lbl">국내 방어력 D</div><div class="val">{_num(den['D'], 3)}</div><div class="sub">ISA {_num(den['D_isa'], 3)} · 배당 {_num(den['D_div'], 3)} · 한전/인프라 {_num(den['D_infra'], 3)}</div></div>
  <div class="card"><div class="lbl">코스피 추정</div><div class="val">{_num(kospi['expected'], 0)}</div><div class="sub">밴드 {_num(kospi['band_low'], 0)}–{_num(kospi['band_high'], 0)} · 선행PE {_num(kospi['projected_pe'])}배</div></div>
</div>

<p class="lead">{snap.phase_narrative}</p>

<section>
  <h2>1. 원인 → 결과 논리</h2>
  <div class="logic">
    <article>
      <h3>금리 역전 = 9월 인하 구조적 불가</h3>
      <p>실질 정책금리 {snap.inputs.fed_funds:.2f} − PCE {snap.inputs.pce_yoy:.2f} = <b>{rel['real_policy']:+.2f}%</b>.
      실질 중립 {snap.inputs.fed_neutral:.2f} − 목표 {snap.inputs.inflation_target:.2f} = <b>{rel['real_neutral']:+.2f}%</b>.
      갭 {rel['rate_gap']:+.2f}%p로 역전 상태다. 케빈 워시류 매파 발언은 인상 예고가 아니라 기대 인플레를 꺾는 조본잉이다.
      4분기 PCE가 3.5% 아래로 내려와야 부분 룸이 열린다.</p>
    </article>
    <article>
      <h3>10년물 폭등 = 물가가 아니라 공급</h3>
      <p>빅테크 AI 설비투자 회사채 {snap.inputs.ig_issuance_bn:.0f}억 달러 + 바이트댄스 대출 {snap.inputs.bytedance_loan_bn:.0f}억 달러가
      국채보다 0.5~1.0%p 높은 이자로 자금을 빨아들인다. 유효 10년물 {_num(rel['effective_ust10'])}%.
      명목 5.0%는 위험자산 10~15% 하드랜딩 임계치.</p>
    </article>
    <article>
      <h3>AI 피크아웃은 숫자와 반대로 움직임</h3>
      <p>엔비디아 DC {snap.inputs.nvidia_dc_bn:.0f}B 중 기타 수요 {snap.inputs.nvidia_other_bn:.0f}B({_pct(exp['other_demand_share'])}).
      하이퍼스케일러 의존 탈피. 랙 통판 {snap.inputs.nvl72_share:.0%}→{snap.inputs.nvl72_next_year:.0%}.
      자체 ASIC 외부 판매가 2027년 2~3분기에 FCF를 플러스로 돌리면 무용론은 소멸한다.</p>
    </article>
    <article>
      <h3>CXMT는 허상, YMTC는 진짜, ISA는 댐</h3>
      <p>CXMT HBM(15~16nm DUV, EUV 없음)은 웨이퍼를 3배 소모해 한국 범용 D램을 역설적으로 방어한다
      (방어항 +{exp['cxmt_dram_defense']:.3f}). YMTC 낸드 점유 {snap.inputs.ymtc_nand_share:.0%}는 중장기 위협
      (드래그 −{exp['ymtc_nand_drag']:.3f}). 생산적 금융 ISA 40조·삼성 특별배당·한전 선납이 외국인 매도를 받친다.</p>
    </article>
  </div>
</section>

<section>
  <h2>2. 3단계 궤적</h2>
  <div class="phases">{_phase_cards()}</div>
</section>

<section>
  <h2>3. 시나리오 비교</h2>
  <table>
    <thead><tr><th>시나리오</th><th>국면</th><th class="num">R</th><th class="num">A</th><th class="num">D</th><th class="num">M</th><th class="num">코스피 기대</th><th class="num">밴드</th><th class="num">주식 비중</th></tr></thead>
    <tbody>{_scenario_rows(scenarios)}</tbody>
  </table>
</section>

<section>
  <h2>4. 실전 자산 배분 (기준 {_won(ref)})</h2>
  <p class="callout">방향이 흐린 장에서는 종목 교체보다 비율 조절이 생존 규칙이다. 주식 {_pct(snap.equity_weight)} / 채권·현금 {_pct(1 - snap.equity_weight)}.
  주식 내부는 코어 반도체 {_pct(snap.sleeves['CORE_SEMI'])} · AI 소부장 {_pct(snap.sleeves['AI_CONNECT'])} · 헷지 {_pct(snap.sleeves['MACRO_HEDGE'])} · 화장품 {_pct(snap.sleeves['COSMETICS'])}.</p>
  {''.join(sleeve_bars)}
  <p>채권·현금 버킷 {_pct(1 - snap.equity_weight)} = {_won(ref * (1 - snap.equity_weight))} (단기 국채·MMF·예수금).</p>
</section>

<section>
  <h2>5. 코스피 편입 종목</h2>
  <table>
    <thead>
      <tr>
        <th>코드</th><th>종목</th><th>슬리브</th><th>행동</th>
        <th class="num">점수</th><th class="num">총비중</th><th class="num">주식내</th><th class="num">금액</th><th>코스닥 대체</th>
      </tr>
    </thead>
    <tbody>{_holding_rows(portfolio)}</tbody>
  </table>
  <div class="theses" style="margin-top:12px">{_thesis_cards(portfolio)}</div>
</section>

<section>
  <h2>6. 절대 배제 · 코스닥 필터</h2>
  <p>유니버스에 코스닥이 들어오면 점수가 높아도 포트폴리오에 넣지 않는다. 심텍·티엘비·디아이는 코스피 기판/장비로 치환했다.</p>
  <table>
    <thead><tr><th>코드</th><th>종목</th><th>플래그</th><th>이유</th></tr></thead>
    <tbody>{_avoid_rows(portfolio)}</tbody>
  </table>
</section>

<footer>
  이 보고서는 2026-09-03 다섯 편 심층 영상의 미시 데이터와 거시 논리를 하나의 추정 모형으로 묶은 연구 노트다.
  투자 권유가 아니며, 입력값(금리, PCE, 유가, ISA 유입)이 바뀌면 <span class="mono">python3 -m hybrid_synthesis</span>로 다시 돌린다.
</footer>
</div>
</body>
</html>
"""


def render_markdown(portfolio: Portfolio, scenarios: dict[str, HybridSnapshot]) -> str:
    snap = portfolio.snapshot
    f = snap.formula_terms()
    lines = [
        "# 통합 하이브리드 추정 모형 · 코스피 포트폴리오",
        "",
        f"- 기준일: `{snap.as_of.isoformat()}`",
        f"- 국면: Phase {snap.phase.value} {snap.phase_name} ({snap.phase_window})",
        f"- 공식: `M = R × A + D` = `{f['R']:.3f} × {f['A']:.3f} + {f['D']:.3f} = {f['M']:.3f}`",
        f"- 코스피 추정: **{snap.kospi['expected']:.0f}** (밴드 {snap.kospi['band_low']:.0f}–{snap.kospi['band_high']:.0f})",
        f"- 자산배분: 주식 {_pct(snap.equity_weight)} / 채권·현금 {_pct(1 - snap.equity_weight)}",
        "",
        "## 편입 종목",
        "",
        "| 코드 | 종목 | 슬리브 | 총비중 | 점수 | 논리 |",
        "|---|---|---|---:|---:|---|",
    ]
    for item in portfolio.holdings:
        thesis = item.thesis.replace("|", "/")
        lines.append(
            f"| {item.ticker} | {item.name} | {SLEEVE_KO[item.sleeve]} | {_pct(item.weight_total)} | {item.score:.1f} | {thesis} |"
        )
    lines += [
        "",
        "## 시나리오",
        "",
        "| 시나리오 | 국면 | R | A | D | M | 코스피 | 주식 |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for key, item in scenarios.items():
        lines.append(
            f"| {key} | {item.phase_name} | {item.relief['R']:.3f} | {item.expansion['A']:.3f} | "
            f"{item.defense['D']:.3f} | {item.momentum:.3f} | {item.kospi['expected']:.0f} | {_pct(item.equity_weight)} |"
        )
    lines += [
        "",
        "## 배제",
        "",
    ]
    for item in portfolio.avoid:
        lines.append(f"- `{item.ticker}` {item.name}: {item.thesis}")
    for item in portfolio.excluded_non_kospi:
        lines.append(f"- `{item['ticker']}` {item['name']} (KOSDAQ): {item['reason']}")
    lines += [
        "",
        "투자 권유 아님. 입력값이 바뀌면 `python3 -m hybrid_synthesis --all-scenarios`로 재추정한다.",
        "",
    ]
    return "\n".join(lines)


def write_reports(
    portfolio: Portfolio,
    scenarios: dict[str, HybridSnapshot],
    out_dir: Path,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    as_of = portfolio.snapshot.as_of.isoformat()
    html_path = out_dir / f"{as_of}-hybrid-synthesis.html"
    md_path = out_dir / "VIEW_THIS_REPORT.md"
    json_path = out_dir / f"{as_of}-hybrid-synthesis.json"
    readme_path = out_dir / "README.md"

    payload = {
        "portfolio": portfolio.to_dict(),
        "scenarios": {key: item.to_dict() for key, item in scenarios.items()},
    }
    html_path.write_text(render_html(portfolio, scenarios), encoding="utf-8")
    md_path.write_text(render_markdown(portfolio, scenarios), encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    csv_path = out_dir / f"{as_of}-hybrid-portfolio.csv"
    csv_lines = ["ticker,name,sleeve,action,score,weight_total,weight_equity,amount_krw"]
    cash_w = portfolio.cash_bond_weight
    csv_lines.append(f"CASH,채권및현금,CASH,HOLD,0,{cash_w:.4f},0,{portfolio.reference_krw * cash_w:.0f}")
    for item in portfolio.holdings:
        csv_lines.append(
            f"{item.ticker},{item.name},{item.sleeve},{item.action},{item.score:.2f},"
            f"{item.weight_total:.4f},{item.weight_equity:.4f},{portfolio.reference_krw * item.weight_total:.0f}"
        )
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    readme_path.write_text(
        "\n".join(
            [
                "# 하이브리드 추정 리포트",
                "",
                f"| 파일 | 용도 |",
                f"|---|---|",
                f"| `VIEW_THIS_REPORT.md` | GitHub에서 바로 보는 요약 |",
                f"| `{html_path.name}` | 브라우저용 단독 HTML |",
                f"| `{json_path.name}` | 원숫자 스냅샷 |",
                f"| `{csv_path.name}` | 1억 기준 주문용 CSV |",
                "",
                "재생성:",
                "",
                "```bash",
                "python3 -m hybrid_synthesis --all-scenarios",
                "python3 -m unittest hybrid_synthesis.tests.test_model hybrid_synthesis.tests.test_portfolio",
                "```",
                "",
                "투자 참고용 · 투자 권유 아님",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return [html_path, md_path, json_path, csv_path, readme_path]
