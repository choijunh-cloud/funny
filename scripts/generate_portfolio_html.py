#!/usr/bin/env python3
"""9/21 실행 북 한 장."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import portfolio_book as B

ROOT = Path("/workspace")
CHARTS = ROOT / "lectures" / "assets" / "portfolio"
OUT = ROOT / "lectures" / "9월 21일 스터디 포트폴리오 한장.html"
OUT_MD = ROOT / "reports" / "2026-09-21-portfolio.md"


def uri(name: str) -> str:
    return "data:image/png;base64," + base64.b64encode((CHARTS / name).read_bytes()).decode("ascii")


def rows_html() -> str:
    parts = []
    for h in B.HOLDINGS:
        won = B.krw(h["weight"])
        parts.append(
            f"<tr><td>{h['ticker']}</td><td>{h['name']}</td><td>{h['weight']:.1f}%</td>"
            f"<td>{won:,}</td><td>{h['action']}</td><td>{h['role']}</td>"
            f"<td>{h['line']}</td></tr>"
        )
    return "".join(parts)


def html() -> str:
    c = {n: uri(n) for n in [
        "01_alloc.png", "02_bookc.png", "03_names.png",
        "04_newmoney.png", "05_actions.png", "06_flow.png",
    ]}
    buys = "".join(
        f"<tr><td>{h['action']}</td><td>{h['name']}</td><td>{h['weight']:.1f}%</td>"
        f"<td>{B.krw(h['weight']):,}</td><td>{h['line']}</td></tr>"
        for h in B.buy_order()
    )
    excl = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in B.EXCLUDE)
    rules = "".join(f"<li>{r}</li>" for r in B.RULES)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>9월 21일 스터디 포트폴리오</title>
<style>
:root {{ --navy:#0f2043; --navy2:#1e407c; --gold:#b8943a; --ink:#1a1a1a;
  --muted:#4b5563; --line:#d5dce6; --bg:#eef1f7; --green:#166534; --red:#991b1b; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans CJK KR","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic","WenQuanYi Micro Hei",sans-serif;
  word-spacing:.12em; }}
.board {{ width:1100px; margin:0 auto; padding:18px 16px 28px; }}
.kicker {{ color:var(--gold); font-weight:800; font-size:12px; }}
h1 {{ color:var(--navy); font-size:24px; line-height:1.3; margin:6px 0 10px; }}
.hero {{ background:var(--navy); color:#fff; border-radius:12px; padding:14px 16px; font-size:14px; line-height:1.55; }}
.hero b {{ color:var(--gold); }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:12px 14px; margin:10px 0; }}
.card h2 {{ margin:0 0 8px; color:var(--navy); font-size:16px; border-bottom:2px solid var(--navy); padding-bottom:4px; }}
img {{ width:100%; border-radius:8px; border:1px solid var(--line); margin:6px 0; background:#fff; }}
table {{ width:100%; border-collapse:collapse; font-size:12.2px; }}
th {{ background:var(--navy); color:#fff; padding:5px 7px; text-align:left; }}
td {{ padding:5px 7px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:nth-child(even) td {{ background:#f7f9fc; }}
.note,.ok,.risk {{ padding:8px 10px; border-radius:0 8px 8px 0; font-size:13px; margin:8px 0; line-height:1.5; }}
.note {{ background:#fff8e7; border-left:4px solid var(--gold); }}
.ok {{ background:#e8f5e9; border-left:4px solid var(--green); }}
.risk {{ background:#fdecea; border-left:4px solid var(--red); }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
.foot {{ color:var(--muted); font-size:11px; text-align:right; }}
</style>
</head>
<body>
<div class="board">
  <div class="kicker">2026.09.21  ·  스터디 실행 북  ·  1억 기준  ·  {B.tape_note()}</div>
  <h1>지금 넣는 돈은 한금융·네이버·모비스·한전. 삼전닉스는 이미 있으면 홀드, 없으면 추격하지 않는다</h1>
  <div class="hero">
    {B.PHASE}
    <b>주식 {B.EQUITY_PCT:.0f} / 현금 {B.CASH_PCT:.0f}.</b>
    반도체 클러스터(삼성+닉스+스퀘어)는 {B.semi_cluster():.0f}%. 9/3 북의 30%에서 줄였다.
  </div>
  <div class="grid">
    <div class="card"><h2>배분</h2><img src="{c['01_alloc.png']}" alt="60/40"/></div>
    <div class="card"><h2>Book C</h2><img src="{c['02_bookc.png']}" alt="Book C"/></div>
  </div>
  <div class="card">
    <h2>1억을 지금 넣는다면</h2>
    <img src="{c['06_flow.png']}" alt="자금 흐름"/>
    <img src="{c['05_actions.png']}" alt="실행 카드"/>
    <img src="{c['04_newmoney.png']}" alt="신규 4"/>
    <table>
      <tr><th>순</th><th>종목</th><th>비중</th><th>금액</th><th>이유</th></tr>
      {buys}
    </table>
    <div class="ok">신규 4종목 합 21.0% = 2,100만. 분할로 넣는다. 한 날에 다 사지 않는다.</div>
  </div>
  <div class="card">
    <h2>전체 북</h2>
    <img src="{c['03_names.png']}" alt="종목 바"/>
    <table>
      <tr><th>코드</th><th>이름</th><th>%</th><th>원</th><th>액션</th><th>역할</th><th>한 줄</th></tr>
      {rows_html()}
    </table>
  </div>
  <div class="card">
    <h2>넣지 않는 것</h2>
    <table>
      <tr><th>코드</th><th>이름</th><th>이유</th></tr>
      {excl}
    </table>
    <div class="risk">이미 삼전닉스가 있으면 그 비중은 유지하고, 빈 자리만 신규 4로 채운다. 없으면 지금 가격에 코어를 새로 키우지 않는다.</div>
  </div>
  <div class="card">
    <h2>규칙</h2>
    <ul>{rules}</ul>
    <div class="note">투자 권유가 아니다. 스터디 북의 실행판이다. 10Y AND가 켜지거나 oil 120이 켜지면 주식 60을 먼저 줄인다.</div>
  </div>
  <div class="foot">기준 {B.AS_OF} · 삼성·닉스 가격만 9/18 종가 · 나머지 종가는 비중 설계이지 지정가 아님</div>
</div>
</body>
</html>
"""


def md() -> str:
    lines = [
        f"# 9/21 스터디 포트폴리오",
        "",
        B.PHASE,
        "",
        B.tape_note(),
        "",
        "| 코드 | 이름 | % | 금액 | 액션 | 한 줄 |",
        "|---|---|---:|---:|---|---|",
    ]
    for h in B.HOLDINGS:
        lines.append(
            f"| {h['ticker']} | {h['name']} | {h['weight']:.1f} | {B.krw(h['weight']):,} | {h['action']} | {h['line']} |"
        )
    lines += [
        "",
        "## 신규 자금",
        "",
        "| 순 | 이름 | % | 금액 |",
        "|---|---|---:|---:|",
    ]
    for h in B.buy_order():
        lines.append(f"| {h['action']} | {h['name']} | {h['weight']:.1f} | {B.krw(h['weight']):,} |")
    lines += ["", "## 규칙", ""] + [f"- {r}" for r in B.RULES]
    return "\n".join(lines) + "\n"


def write() -> tuple[Path, Path]:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html(), encoding="utf-8")
    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text(md(), encoding="utf-8")
    return OUT, OUT_MD


if __name__ == "__main__":
    a, b = write()
    print(a, a.stat().st_size)
    print(b)
