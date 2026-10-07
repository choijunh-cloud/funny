#!/usr/bin/env python3
"""10월 7일 Quick 코멘트 + 첨부 PDF 통합 브리프 (HTML/MD)."""

from __future__ import annotations

from pathlib import Path

import oct7_data as D

LECTURES = Path("/workspace/lectures")
REPORTS = Path("/workspace/reports")
LECTURES.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

HTML_NAME = "10월 7일 Quick 코멘트 분석.html"
MD_NAME = "10월 7일 Quick 코멘트 분석.md"
REPORT_HTML = REPORTS / "2026-10-07-quick-comment-brief.html"
CHART = "../reports/charts"

CSS = """
:root {
  --navy: #0f2043;
  --navy2: #1e407c;
  --gold: #b8943a;
  --ink: #1a1a1a;
  --muted: #4b5563;
  --line: #d5dce6;
  --bg: #f4f6fb;
  --card: #ffffff;
  --green: #166534;
  --green-bg: #e8f5e9;
  --red: #991b1b;
  --red-bg: #fdecea;
  --amber: #7a5c12;
  --amber-bg: #fff8e7;
  --blue-bg: #e8f1fb;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--ink);
  font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", sans-serif;
  line-height: 1.55; }
.wrap { max-width: 980px; margin: 0 auto; padding: 28px 20px 72px; }
.kicker { color: var(--gold); font-weight: 700; letter-spacing: .04em; font-size: 13px; }
h1 { color: var(--navy); font-size: 30px; line-height: 1.25; margin: 6px 0 8px; }
.sub { color: var(--muted); margin: 0 0 18px; }
.hero { background: linear-gradient(135deg, #0f2043 0%, #1e407c 70%, #2a508f 100%);
  color: #fff; border-radius: 16px; padding: 22px 24px; margin-bottom: 18px; }
.hero h2 { margin: 0 0 10px; font-size: 15px; color: var(--gold); }
.hero li { margin: 7px 0; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 14px 0 20px; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; margin: 14px 0 18px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }
.card h3 { margin: 0 0 6px; color: var(--navy2); font-size: 13px; }
.card .num { font-size: 22px; font-weight: 800; color: var(--navy); }
.card p { margin: 6px 0 0; color: var(--muted); font-size: 13px; }
section { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 20px 22px; margin: 0 0 14px; }
section h2 { margin: 0 0 8px; color: var(--navy); font-size: 21px; border-bottom: 3px solid var(--navy); padding-bottom: 8px; }
section h3 { margin: 16px 0 8px; color: var(--navy2); font-size: 16px; }
.callout { border-left: 5px solid var(--navy); background: #eef2f8; padding: 10px 14px; border-radius: 0 10px 10px 0; margin: 10px 0; }
.callout.bull { border-left-color: var(--green); background: var(--green-bg); }
.callout.bear { border-left-color: var(--red); background: var(--red-bg); }
.callout.note { border-left-color: var(--gold); background: var(--amber-bg); }
.callout b { display: block; margin-bottom: 4px; }
table { width: 100%; border-collapse: collapse; font-size: 13.4px; margin: 8px 0 12px; }
th { background: var(--navy); color: #fff; padding: 8px 10px; text-align: left; }
td { padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
tr:nth-child(even) td { background: #f7f9fc; }
.tag { display: inline-block; font-size: 11px; font-weight: 800; padding: 2px 7px; border-radius: 999px; margin-right: 4px; }
.tag.ok { background: var(--green-bg); color: var(--green); }
.tag.est { background: var(--amber-bg); color: var(--amber); }
.tag.bad { background: var(--red-bg); color: var(--red); }
img.chart { width: 100%; border-radius: 10px; border: 1px solid var(--line); margin: 8px 0 4px; background: #fff; }
.cap { color: var(--muted); font-size: 12px; margin: 0 0 10px; }
.footer { color: var(--muted); font-size: 12px; margin-top: 10px; }
nav { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 18px; }
nav a { background: #fff; border: 1px solid var(--line); color: var(--navy2); text-decoration: none;
  padding: 6px 10px; border-radius: 999px; font-size: 12.5px; font-weight: 700; }
@media print {
  body { background: #fff; }
  .wrap { max-width: none; padding: 0; }
  section, .hero { break-inside: avoid; }
  nav { display: none; }
}
@media (max-width: 720px) {
  .grid, .grid3 { grid-template-columns: 1fr; }
  h1 { font-size: 24px; }
}
"""


def _tag(kind: str, text: str) -> str:
    return f'<span class="tag {kind}">{text}</span>'


def build_html() -> str:
    verdict_rows = "".join(
        f"<tr><td>{c}</td><td>{_tag(k, v)}</td></tr>" for c, v, k in D.CHINA_AI["verdicts"]
    )
    mem_rows = "".join(
        f"<tr><td>{n}</td><td>{p}</td><td>{m}</td><td><b>{per}</b></td><td>{note}</td></tr>"
        for n, p, m, per, note in D.MEMORY_VAL["rows"]
    )
    cpu_rows = "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in D.CPU["compare"]
    )
    psk_rows = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in D.PSK["mix"])
    muse_ram = "".join(f"<tr><td>{a}</td><td>{b}</td></tr>" for a, b in D.MUSE["ram_path"])
    paste_blocks = "".join(
        f'<div class="callout note"><b>{p["title"]}</b>{p["body"]}</div>' for p in D.PASTE_ADDONS
    )
    checks = "".join(f"<li>{c}</li>" for c in D.CHECKLIST)
    src = "".join(f"<li><b>{k}</b> — {v}</li>" for k, v in D.SOURCES)

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>10월 7일 Quick 코멘트 분석</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="kicker">2026. 10. 7.  ·  Quick 코멘트 + 첨부 PDF 6개 통합</div>
  <h1>{D.TITLE}</h1>
  <p class="sub">매수·매도 권유가 아닙니다. 원문: 첨부 PDF 6개 + paste Quick 코멘트. HTML: <code>reports/2026-10-07-quick-comment-brief.html</code></p>
  <nav>
    <a href="#top">한 장</a>
    <a href="#china">중국 AI</a>
    <a href="#muse">MUSE</a>
    <a href="#val">메모리 밸류</a>
    <a href="#cpu">CPU TAM</a>
    <a href="#psk">PSK</a>
    <a href="#midterm">중간선거</a>
    <a href="#paste">당일 보강</a>
    <a href="#check">체크</a>
  </nav>

  <div class="hero" id="top">
    <h2>오늘 한 줄</h2>
    <p style="margin:0;font-size:17px;line-height:1.45">{D.ONELINE}</p>
  </div>

  <div class="grid3">
    <div class="card"><h3>씨티 2030 CPU</h3><div class="num">$300B</div><p>2025 $29B → Agentic 상향</p></div>
    <div class="card"><h3>미즈호 2030 CPU</h3><div class="num">$209B</div><p>Agentic CPU 비중 30%</p></div>
    <div class="card"><h3>메모리 PER</h3><div class="num">4~7x</div><p>10/6 종가 한 자리수</p></div>
  </div>

  <img class="chart" src="{CHART}/05_investment_flow.png" alt="투자 연결고리"/>
  <p class="cap">Agentic AI → Inference → GPU+CPU → DRAM/HBM/NAND → 후공정(CoWoS·EMIB)</p>

  <section id="china">
    <h2>1. 중국 AI는 정말 싼가</h2>
    <p>{D.CHINA_AI["thesis"]}</p>
    <ul>{"".join(f"<li>{p}</li>" for p in D.CHINA_AI["points"])}</ul>
    <table>
      <tr><th>주장</th><th>판정</th></tr>
      {verdict_rows}
    </table>
    <img class="chart" src="{CHART}/04_china_ai_verdicts.png" alt="중국 AI 판정"/>
    <div class="callout bear"><b>비약 경계</b>{D.CHINA_AI["punch"]}</div>
  </section>

  <section id="muse">
    <h2>2. MUSE에서 메모리는</h2>
    <p>{D.MUSE["thesis"]}</p>
    <div class="grid3">
      {"".join(f'<div class="card"><h3>{a}</h3><p>{b}</p></div>' for a, b in D.MUSE["stack"])}
    </div>
    <table>
      <tr><th>단계</th><th>할당 / 사용</th></tr>
      {muse_ram}
    </table>
    <img class="chart" src="{CHART}/03_muse_ram.png" alt="Muse RAM 경로"/>
    <ul>{"".join(f"<li>{p}</li>" for p in D.MUSE["points"])}</ul>
    <div class="callout bull"><b>DRAM 업사이드</b>현재는 실제 ~3GB×동시활성. 고도화되면 3→8→16GB로 올라가는 것이 추가 옵션.</div>
  </section>

  <section id="val">
    <h2>3. 메모리 주가·밸류 (10/6 종가)</h2>
    <p>기준: {D.MEMORY_VAL["asof"]}. 수급 이슈와 할인율 이슈를 같이 봅니다.</p>
    <table>
      <tr><th>종목</th><th>가격</th><th>기준</th><th>PER</th><th>메모</th></tr>
      {mem_rows}
    </table>
    <img class="chart" src="{CHART}/02_memory_per.png" alt="메모리 PER"/>
    <div class="grid">
      <div class="callout note"><b>환율</b>{D.MEMORY_VAL["fx"]}</div>
      <div class="callout note"><b>할인·ADR</b>{D.MEMORY_VAL["discount"]}<br/>{D.MEMORY_VAL["adr_premium"]}</div>
    </div>
    <p><b>27년 이익:</b> {D.MEMORY_VAL["eps_27"][0][0]} {D.MEMORY_VAL["eps_27"][0][1]} ({D.MEMORY_VAL["eps_27"][0][2]}) · {D.MEMORY_VAL["eps_27"][1][0]} {D.MEMORY_VAL["eps_27"][1][1]} ({D.MEMORY_VAL["eps_27"][1][2]})</p>
    <div class="callout"><b>보수 시나리오</b>{D.MEMORY_VAL["conservative"]} 27~28년 이익 증가가 확인되면 그 이상을 점진 반영.</div>
  </section>

  <section id="cpu">
    <h2>4. AMD · 씨티 · 미즈호 — CPU 시장 상향</h2>
    <p>{D.CPU["thesis"]}</p>
    <ul>{"".join(f"<li>{p}</li>" for p in D.CPU["why_cpu"])}</ul>
    <h3>씨티</h3>
    <ul>
      <li>5월: {D.CPU["citi"]["may"]}</li>
      <li>10/6: {D.CPU["citi"]["oct"]}</li>
      <li>{D.CPU["citi"]["implied_26"]}</li>
      <li>{D.CPU["citi"]["agentic_cagr"]}</li>
      <li>Muse 산식: {D.CPU["citi"]["muse_math"]}</li>
    </ul>
    <h3>미즈호</h3>
    <ul>
      <li>2030 TAM {D.CPU["mizuho"]["tam_2030"]}</li>
      <li>{D.CPU["mizuho"]["agentic_share"]}</li>
      <li>{D.CPU["mizuho"]["memory_share"]}</li>
      <li>{D.CPU["mizuho"]["names"]}</li>
    </ul>
    <table>
      <tr><th>항목</th><th>씨티</th><th>미즈호</th></tr>
      {cpu_rows}
    </table>
    <img class="chart" src="{CHART}/01_cpu_tam.png" alt="CPU TAM"/>
    <div class="callout note"><b>$300B는 공격적</b>방향성(GPU → CPU → DRAM/HBM → NAND → 서버)이 투자 포인트. 절대 숫자 맹신은 금물.</div>
  </section>

  <section id="psk">
    <h2>5. 피에스케이홀딩스 — CoWoS·EMIB 교집합</h2>
    <p>{D.PSK["thesis"]}</p>
    <div class="callout bull"><b>한화 TP</b>{D.PSK["tp"]}</div>
    <table>
      <tr><th>축</th><th>장비 포인트</th></tr>
      {psk_rows}
    </table>
    <p>{D.PSK["emib"]}</p>
    <div class="callout"><b>운용</b>{D.PSK["stance"]}</div>
  </section>

  <section id="midterm">
    <h2>6. 중간선거 — 전력 수급·affordability</h2>
    <p><b>{D.MIDTERM["title"]}</b></p>
    <ul>{"".join(f"<li>{p}</li>" for p in D.MIDTERM["points"])}</ul>
  </section>

  <section id="paste">
    <h2>7. 당일 Quick 코멘트 보강</h2>
    {paste_blocks}
  </section>

  <section id="check">
    <h2>8. 체크리스트</h2>
    <ul>{checks}</ul>
    <h3>원문</h3>
    <ul>{src}</ul>
    <p class="footer">자동 생성 · scripts/generate_oct7_brief.py · 숫자는 첨부 PDF·Quick 코멘트 기준 · 투자 권유 아님</p>
  </section>
</div>
</body>
</html>
"""


def build_md() -> str:
    lines = [
        f"# {D.TITLE}",
        "",
        f"> {D.DATE}. Quick 코멘트 + 첨부 PDF 6개. HTML: `reports/2026-10-07-quick-comment-brief.html`",
        "",
        "매수·매도 권유가 아닙니다.",
        "",
        "## 한 줄",
        "",
        D.ONELINE,
        "",
        "## 오늘이 더하는 것",
        "",
        "- 토큰 단가 하락 → CapEx 과도 논리는 **비약** (Agent 사용량 상쇄).",
        "- Muse VM DRAM은 **할당 8GB가 아니라 실제 ~3GB**, 고도화가 업사이드.",
        "- 메모리 PER **4~7배** (10/6). 삼전닉스 vs MU 할인 ~31%.",
        "- 서버 CPU TAM: 씨티 **$300B** vs 미즈호 **$209B** (2030).",
        "- PSK: CoWoS/HBM + **EMIB** 레벨업. 한화 TP 27만.",
        "- 중간선거: 반-DC가 아니라 **전력 공급·비용**.",
        "",
        "## 1. 중국 AI",
        "",
        D.CHINA_AI["thesis"],
        "",
    ]
    for p in D.CHINA_AI["points"]:
        lines.append(f"- {p}")
    lines += ["", "| 주장 | 판정 |", "|---|---|"]
    for c, v, _ in D.CHINA_AI["verdicts"]:
        lines.append(f"| {c} | {v} |")
    lines += ["", f"**결론:** {D.CHINA_AI['punch']}", ""]

    lines += ["## 2. MUSE 메모리", "", D.MUSE["thesis"], ""]
    for a, b in D.MUSE["stack"]:
        lines.append(f"- **{a}**: {b}")
    lines += ["", "| 단계 | 할당 / 사용 |", "|---|---|"]
    for a, b in D.MUSE["ram_path"]:
        lines.append(f"| {a} | {b} |")
    lines.append("")
    for p in D.MUSE["points"]:
        lines.append(f"- {p}")

    lines += ["", "## 3. 메모리 밸류 (10/6)", "", "| 종목 | 가격 | 기준 | PER | 메모 |", "|---|---|---|---|---|"]
    for n, p, m, per, note in D.MEMORY_VAL["rows"]:
        lines.append(f"| {n} | {p} | {m} | {per} | {note} |")
    lines += [
        "",
        f"- {D.MEMORY_VAL['fx']}",
        f"- {D.MEMORY_VAL['discount']}",
        f"- {D.MEMORY_VAL['adr_premium']}",
        f"- 보수: {D.MEMORY_VAL['conservative']}",
        "",
        "## 4. CPU TAM (씨티 vs 미즈호)",
        "",
        D.CPU["thesis"],
        "",
    ]
    for p in D.CPU["why_cpu"]:
        lines.append(f"- {p}")
    lines += ["", "| 항목 | 씨티 | 미즈호 |", "|---|---|---|"]
    for a, b, c in D.CPU["compare"]:
        lines.append(f"| {a} | {b} | {c} |")
    lines += [
        "",
        f"- 씨티 5월: {D.CPU['citi']['may']}",
        f"- 씨티 10월: {D.CPU['citi']['oct']}",
        f"- {D.CPU['citi']['implied_26']}",
        f"- 미즈호: {D.CPU['mizuho']['memory_share']}",
        "",
        "## 5. 피에스케이홀딩스",
        "",
        D.PSK["thesis"],
        "",
        f"- {D.PSK['tp']}",
        f"- {D.PSK['emib']}",
        f"- 운용: {D.PSK['stance']}",
        "",
        "## 6. 중간선거",
        "",
        f"**{D.MIDTERM['title']}**",
        "",
    ]
    for p in D.MIDTERM["points"]:
        lines.append(f"- {p}")

    lines += ["", "## 7. 당일 보강", ""]
    for p in D.PASTE_ADDONS:
        lines += [f"### {p['title']}", "", p["body"], ""]

    lines += ["## 8. 체크리스트", ""]
    for c in D.CHECKLIST:
        lines.append(f"- {c}")
    lines += ["", "## 원문", ""]
    for k, v in D.SOURCES:
        lines.append(f"- **{k}** — {v}")
    lines.append("")
    return "\n".join(lines)


def main():
    html = build_html()
    md = build_md()
    (LECTURES / HTML_NAME).write_text(html, encoding="utf-8")
    (LECTURES / MD_NAME).write_text(md, encoding="utf-8")
    # report copy with chart paths relative to reports/
    report_html = html.replace("../reports/charts/", "charts/")
    REPORT_HTML.write_text(report_html, encoding="utf-8")
    (REPORTS / "README.md").write_text(
        "# Oct 7 Quick Comment Brief\n\n"
        "- `2026-10-07-quick-comment-brief.html`\n"
        "- charts in `charts/`\n"
        "- sources in `sources/oct7/`\n",
        encoding="utf-8",
    )
    print("wrote", LECTURES / HTML_NAME)
    print("wrote", LECTURES / MD_NAME)
    print("wrote", REPORT_HTML)


if __name__ == "__main__":
    main()
