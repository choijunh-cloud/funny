#!/usr/bin/env python3
"""8/18–9/20 투자 스터디 인사이트 한 장. 차트는 base64 내장."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import insights_data as D

ROOT = Path("/workspace")
CHARTS = ROOT / "lectures" / "assets" / "insights"
OUT = ROOT / "lectures" / "8월-9월 투자 스터디 인사이트 한장.html"
OUT_ALIAS = ROOT / "reports" / "VIEW_THIS_REPORT.html"


def uri(name: str) -> str:
    raw = (CHARTS / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def html() -> str:
    c = {n: uri(n) for n in [
        "01_corpus.png", "02_themes.png", "03_frames.png", "04_siren.png",
        "05_and_gate.png", "06_kospi_box.png", "07_memory_per.png", "08_fair_band.png",
        "09_hbm.png", "10_token.png", "11_nvidia.png", "12_capex.png",
        "13_equipment.png", "14_sk.png", "15_atlas.png", "16_h2.png",
        "17_bookc.png", "18_power.png", "19_flows.png", "20_export.png",
        "21_leads.png", "22_calendar.png", "23_lock.png", "24_evolve.png",
        "25_darkgpu.png", "26_opm.png",
    ]}
    theses = "".join(
        f"<tr><td>{t['id']}</td><td><b>{t['title']}</b><br/>{t['line']}</td><td>{t['watch']}</td></tr>"
        for t in D.THESES
    )
    checks = "".join(
        f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in D.CHECKPOINTS
    )
    h2 = "".join(
        f"<tr><td>{i}</td><td>{n}</td><td>{pw:.1f}%</td><td>{w:.1f}%</td><td>{act}</td></tr>"
        for i, (n, pw, w, act) in enumerate(D.H2_TOP10, 1)
    )
    unlock = "".join(f"<li>{x}</li>" for x in D.DO_NOT_LOCK)
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>8월–9월 투자 스터디 인사이트 — 한 장</title>
<style>
:root {{ --navy:#0f2043; --navy2:#1e407c; --gold:#b8943a; --ink:#1a1a1a;
  --muted:#4b5563; --line:#d5dce6; --bg:#eef1f7; --green:#166534; --red:#991b1b; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans CJK KR","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic","WenQuanYi Micro Hei",sans-serif;
  word-spacing:.12em; }}
.board {{ width:1320px; margin:0 auto; padding:16px 16px 28px; }}
.kicker {{ color:var(--gold); font-weight:800; font-size:12px; letter-spacing:.03em; }}
h1 {{ color:var(--navy); font-size:24px; line-height:1.28; margin:4px 0 8px; }}
.hero {{ background:var(--navy); color:#fff; border-radius:12px; padding:13px 16px; margin-bottom:8px; font-size:13.8px; line-height:1.55; }}
.hero b {{ color:var(--gold); }}
.kpi {{ display:grid; grid-template-columns:repeat(8,1fr); gap:6px; margin-bottom:8px; }}
.kpi div {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:7px 8px; }}
.kpi h3 {{ margin:0; font-size:10.4px; color:var(--navy2); font-weight:800; }}
.kpi .n {{ font-size:15px; font-weight:800; color:var(--navy); margin-top:2px; }}
.kpi p {{ margin:2px 0 0; font-size:10.3px; color:var(--muted); line-height:1.28; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:10px 12px; }}
.card.wide {{ grid-column:1/-1; }}
.card h2 {{ margin:0 0 6px; color:var(--navy); font-size:15px; border-bottom:2px solid var(--navy); padding-bottom:3px; }}
.card p, .card li {{ font-size:12.3px; line-height:1.45; margin:0 0 4px; }}
.card ul {{ margin:0 0 4px; padding-left:17px; }}
img {{ width:100%; border-radius:8px; border:1px solid var(--line); display:block; margin:4px 0; background:#fff; }}
table {{ width:100%; border-collapse:collapse; font-size:11.4px; margin:4px 0; }}
th {{ background:var(--navy); color:#fff; padding:4px 6px; text-align:left; }}
td {{ padding:4px 6px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:nth-child(even) td {{ background:#f7f9fc; }}
.note,.ok,.risk,.blue {{ padding:6px 8px; border-radius:0 8px 8px 0; font-size:11.9px; margin:5px 0 0; line-height:1.4; }}
.note {{ background:#fff8e7; border-left:4px solid var(--gold); }}
.ok {{ background:#e8f5e9; border-left:4px solid var(--green); }}
.risk {{ background:#fdecea; border-left:4px solid var(--red); }}
.blue {{ background:#e8f1fb; border-left:4px solid var(--navy2); }}
.foot {{ color:var(--muted); font-size:10.6px; margin-top:10px; text-align:right; }}
@media print {{
  html,body {{ background:#fff; }}
  .board {{ width:auto; max-width:100%; padding:8px; }}
  .kpi {{ grid-template-columns:repeat(4,1fr); }}
  .card {{ break-inside:avoid; }}
}}
</style>
</head>
<body>
<div class="board">
  <div class="kicker">2026.09.20  ·  준혁 스터디 통합  ·  8/18–9/20  ·  원문 코멘트·강의 숫자만  ·  IB/게스트 잠금 금지</div>
  <h1>장비는 수주, SK는 할인율, Atlas는 배치. 매크로는 5% 터치가 아니라 AND다</h1>
  <div class="hero">
    공통 분모는 <b>AI CAPEX</b>다. 수요를 정확히 예측할 수 없으니 모델·데이터센터·GPU에 기대고, 자금이 빠듯하니 서로 묶는다.
    8월은 소부장·NAV·Dark GPU, 9월은 장기금리·토큰 P↓Q↑·박스·하이퍼스케일러 현금으로 초점이 이동했다.
    <b>약한 고리 = 자금 + 장기금리.</b> 사이렌(10Y 5% 안착 · oil 120)은 아직 꺼져 있다.
  </div>

  <div class="kpi">
    <div><h3>KOSPI 9/18</h3><div class="n">{D.KOSPI_SEP18:,.2f}</div><p>+{D.KOSPI_SEP18_PCT}% · 박스 안</p></div>
    <div><h3>하이닉스 9/18</h3><div class="n">{D.HYNIX_SEP18/10000:.1f}만</div><p>+{D.HYNIX_SEP18_PCT}%</p></div>
    <div><h3>삼성 9/18</h3><div class="n">{D.SAMSUNG_SEP18/10000:.1f}만</div><p>+{D.SAMSUNG_SEP18_PCT}%</p></div>
    <div><h3>10Y 프레임</h3><div class="n">{D.TENY_FRAME:.2f}%</div><p>터치 {D.TENY_FRI_PRINT} · 안착 아님</p></div>
    <div><h3>WTI</h3><div class="n">${D.FRI_WTI:.1f}</div><p>사이렌 {D.OIL_SIREN:.0f} 미발화</p></div>
    <div><h3>NVDA OCF/NI</h3><div class="n">{D.NVDA_OCF_NI}%</div><p>DSO 45→60</p></div>
    <div><h3>Oracle RPO</h3><div class="n">${D.ORCL_RPO:.0f}B</div><p>신규 AI ${D.ORCL_NEW_AI:.0f}B</p></div>
    <div><h3>H2 주식 비중</h3><div class="n">{D.H2_EQUITY}%</div><p>9/3 하이브리드 · 현금 {D.H2_CASH}%</p></div>
  </div>

  <div class="grid">
    <div class="card wide">
      <h2>0. 무엇을 읽었나</h2>
      <p>funny 저장소의 투자 스터디 21세션 (8/18 NON-삼전닉스부터 9/20 일요 다이제스트). 커넥톰·봉직·클리닉은 제외.</p>
      <img src="{c['01_corpus.png']}" alt="스터디 코퍼스 타임라인"/>
      <img src="{c['24_evolve.png']}" alt="관점 진화"/>
    </div>

    <div class="card wide">
      <h2>1. 여덟 테제</h2>
      <table>
        <tr><th>ID</th><th>한 줄</th><th>확인</th></tr>
        {theses}
      </table>
      <img src="{c['02_themes.png']}" alt="테제 무게"/>
    </div>

    <div class="card">
      <h2>2. 준혁 프레임 · 사이렌</h2>
      <img src="{c['03_frames.png']}" alt="프레임"/>
      <img src="{c['04_siren.png']}" alt="사이렌"/>
      <div class="note">터치 ≠ 안착. 5%는 위험 신호이지 방아쇠가 아니다.</div>
    </div>
    <div class="card">
      <h2>3. Gravity AND · 박스</h2>
      <img src="{c['05_and_gate.png']}" alt="AND 게이트"/>
      <img src="{c['06_kospi_box.png']}" alt="KOSPI 박스"/>
      <div class="blue">윤지호 박스 6,000–7,150. 8,000은 아직 안 연다. 고점 대비 9/18은 {D.kospi_drawdown_from_peak():.1f}%.</div>
    </div>

    <div class="card">
      <h2>4. 메모리 — 저PER을 싸다고 읽지 말 것</h2>
      <img src="{c['07_memory_per.png']}" alt="메모리 PER"/>
      <img src="{c['08_fair_band.png']}" alt="밸류 밴드"/>
      <img src="{c['09_hbm.png']}" alt="Citi HBM"/>
      <div class="note">밴드(닉스 175–242만 · 삼전 28.7–33.5만)는 강의 산식. IB 310/400 · 게스트 200만은 보관만.</div>
    </div>
    <div class="card">
      <h2>5. 토큰 · 엔비디아 · 수주</h2>
      <img src="{c['10_token.png']}" alt="토큰 P Q"/>
      <img src="{c['11_nvidia.png']}" alt="엔비디아 현금"/>
      <img src="{c['12_capex.png']}" alt="CAPEX 백로그"/>
      <div class="ok">P↓여도 Q가 더 늘면 된다. 수요 100 · 공급 70. 질문은 누가 신용을 연장하는가.</div>
    </div>

    <div class="card">
      <h2>6. Dark GPU · 전력</h2>
      <img src="{c['25_darkgpu.png']}" alt="Dark GPU"/>
      <img src="{c['18_power.png']}" alt="DC 전력"/>
      <img src="{c['21_leads.png']}" alt="리드타임"/>
      <div class="risk">병목=노드=돈. 연산은 풀렸고 지금은 메모리, 다음 영수증은 전력·후공정.</div>
    </div>
    <div class="card">
      <h2>7. 소부장 · SK · Atlas</h2>
      <img src="{c['13_equipment.png']}" alt="소부장"/>
      <img src="{c['26_opm.png']}" alt="OPM"/>
      <img src="{c['14_sk.png']}" alt="에코플랜트"/>
      <img src="{c['15_atlas.png']}" alt="Atlas"/>
      <div class="blue">테스=BSD 퀄, 한미=점유율 55–60, 원익=3체크. 에코 표 2.1조는 낮다. Atlas는 배치.</div>
    </div>

    <div class="card">
      <h2>8. H2 포트 · Book C</h2>
      <img src="{c['16_h2.png']}" alt="H2 Top10"/>
      <img src="{c['17_bookc.png']}" alt="Book C"/>
      <table>
        <tr><th>#</th><th>종목</th><th>PW</th><th>기존</th><th>액션</th></tr>
        {h2}
      </table>
      <div class="note">9/3 계산. 신규자금 우선: 한금융 &gt; 네이버 &gt; 모비스 &gt; 한전. 10월 전 삼전닉스 추가 매수 없음.</div>
    </div>
    <div class="card">
      <h2>9. 수급 · 수출 · 캘린더</h2>
      <img src="{c['19_flows.png']}" alt="수급"/>
      <img src="{c['20_export.png']}" alt="수출"/>
      <img src="{c['22_calendar.png']}" alt="캘린더"/>
      <table>
        <tr><th>때</th><th>확인할 것</th><th>축</th></tr>
        {checks}
      </table>
    </div>

    <div class="card wide">
      <h2>10. 합의 세탁 금지</h2>
      <img src="{c['23_lock.png']}" alt="잠금 규칙"/>
      <ul>{unlock}</ul>
      <div class="risk">속도조절을 실제 감속으로 읽지 않는다. Ohio는 탐색이다. GPU 유동화는 초입이지 2008이 아니다.</div>
    </div>
  </div>

  <div class="hero" style="margin-top:8px">
    가져갈 세 문장.
    <b>1)</b> 소부장은 하반기 매출화와 2027 수주가 승부처다.
    <b>2)</b> SK 할인율이 좁혀질 이유는 늘었지만 기본은 하이닉스와 이노베이션이다.
    <b>3)</b> 상단은 하이퍼스케일러 현금이 데이터센터나 토큰으로 다시 도는지에서 열린다.
  </div>
  <div class="foot">원문 퀵코멘트·강의·하이브리드 모델을 주제별로 재구성. 숫자는 스터디 스냅샷이며 실시간 시세가 아니다. — 준혁</div>
</div>
</body>
</html>
"""


def write() -> Path:
    text = html()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8")
    OUT_ALIAS.parent.mkdir(parents=True, exist_ok=True)
    OUT_ALIAS.write_text(text, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    p = write()
    print(f"Wrote {p} ({p.stat().st_size} bytes)")
