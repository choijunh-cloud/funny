#!/usr/bin/env python3
"""9월 20일 일요일 오전 다이제스트 시각화 보드. 차트는 base64 내장."""

from __future__ import annotations

import base64
from pathlib import Path

from sep20_data import ADDON, HAKGYUN_MEMBERSHIP, MAIN, SAT_PM_MAIN, UNLOCKED

ROOT = Path("/workspace")
CHARTS = ROOT / "lectures" / "assets" / "sep20"
OUT = ROOT / "lectures" / "9월 20일 일요일 오전 다이제스트 한장.html"


def uri(name: str) -> str:
    raw = (CHARTS / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def html() -> str:
    c = [uri(f"{i:02d}_{n}.png") for i, n in [
        (1, "clock"),
        (2, "tape"),
        (3, "siren"),
        (4, "ai_panel"),
        (5, "rate_camp"),
        (6, "intel_chain"),
        (7, "sox_thu"),
        (8, "shipyard"),
        (9, "cxl"),
        (10, "calendar"),
        (11, "matrix"),
        (12, "flows"),
        (13, "addon"),
        (14, "ubs"),
        (15, "physical"),
    ]]
    mains = "".join(
        f"<tr><td>MAIN {m['id']}</td><td>{m['ch']}</td><td>{m['guest']}</td>"
        f"<td>{m['when']}</td><td>{m['title']}</td>"
        f"<td>{m['views']:,}</td></tr>"
        for m in MAIN
    )
    sat = "".join(
        f"<tr><td>{name}</td><td><code>{vid}</code></td><td>{note}</td></tr>"
        for name, vid, note in SAT_PM_MAIN
    )
    addons = "".join(
        f"<tr><td>{a['id']}</td><td>{a['ch']}</td><td>{a['guest']}</td>"
        f"<td>{a['when']}</td><td>{a['title']}</td><td>{a['len']}</td></tr>"
        for a in ADDON
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>9월 20일 일요일 오전 다이제스트 — 시각화 보고서</title>
<style>
:root {{ --navy:#0f2043; --navy2:#1e407c; --gold:#b8943a; --ink:#1a1a1a;
  --muted:#4b5563; --line:#d5dce6; --bg:#eef1f7; --green:#166534; --red:#991b1b; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans CJK KR","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic","WenQuanYi Micro Hei",sans-serif;
  word-spacing:.12em; }}
.board {{ width:1320px; margin:0 auto; padding:16px 16px 22px; }}
.kicker {{ color:var(--gold); font-weight:800; font-size:12px; letter-spacing:.03em; }}
h1 {{ color:var(--navy); font-size:24px; line-height:1.25; margin:4px 0 8px; }}
.hero {{ background:var(--navy); color:#fff; border-radius:12px; padding:12px 15px; margin-bottom:8px; font-size:13.6px; line-height:1.5; }}
.hero b {{ color:var(--gold); }}
.kpi {{ display:grid; grid-template-columns:repeat(8,1fr); gap:6px; margin-bottom:8px; }}
.kpi div {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:7px 8px; }}
.kpi h3 {{ margin:0; font-size:10.4px; color:var(--navy2); font-weight:800; }}
.kpi .n {{ font-size:15px; font-weight:800; color:var(--navy); margin-top:2px; }}
.kpi p {{ margin:2px 0 0; font-size:10.4px; color:var(--muted); line-height:1.28; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:10px 12px; }}
.card.wide {{ grid-column:1/-1; }}
.card h2 {{ margin:0 0 6px; color:var(--navy); font-size:15px; border-bottom:2px solid var(--navy); padding-bottom:3px; }}
.card h3 {{ margin:8px 0 4px; color:var(--navy2); font-size:13px; }}
.card p, .card li {{ font-size:12.2px; line-height:1.42; margin:0 0 4px; }}
.card ul {{ margin:0 0 4px; padding-left:17px; }}
img {{ width:100%; border-radius:8px; border:1px solid var(--line); display:block; margin:4px 0; background:#fff; }}
table {{ width:100%; border-collapse:collapse; font-size:11.3px; margin:4px 0; }}
th {{ background:var(--navy); color:#fff; padding:4px 6px; text-align:left; }}
td {{ padding:4px 6px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:nth-child(even) td {{ background:#f7f9fc; }}
.pos {{ color:var(--green); font-weight:700; }}
.neg {{ color:var(--red); font-weight:700; }}
.note,.ok,.risk,.blue {{ padding:6px 8px; border-radius:0 8px 8px 0; font-size:11.8px; margin:5px 0 0; line-height:1.4; }}
.note {{ background:#fff8e7; border-left:4px solid var(--gold); }}
.ok {{ background:#e8f5e9; border-left:4px solid var(--green); }}
.risk {{ background:#fdecea; border-left:4px solid var(--red); }}
.blue {{ background:#e8f1fb; border-left:4px solid var(--navy2); }}
.tag {{ display:inline-block; font-size:10px; font-weight:800; padding:0 5px; border-radius:999px; margin-right:3px; }}
.tag.f {{ background:#e8f5e9; color:var(--green); }}
.tag.p {{ background:#fff8e7; color:#7a5c12; }}
.tag.i {{ background:#e8f1fb; color:var(--navy2); }}
.tag.x {{ background:#fdecea; color:var(--red); }}
.src {{ display:grid; grid-template-columns:repeat(3,1fr); gap:6px; }}
.src div {{ background:#f7f9fc; border-radius:8px; padding:7px 8px; font-size:11.3px; line-height:1.38; }}
.src b {{ color:var(--navy); display:block; margin-bottom:2px; }}
.foot {{ color:var(--muted); font-size:10.6px; margin-top:8px; text-align:right; }}
code {{ font-size:10.5px; background:#eef2f8; padding:1px 4px; border-radius:4px; }}
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
  <div class="kicker">2026.09.20 일 오전  ·  Asia/Seoul  ·  Sunday thin  ·  MAIN 8 + ADDON 4 + PDF 3 + TG  ·  조회 yt-dlp ~08:22 KST</div>
  <h1>일요일은 장이 쉬고, 새 미국 overnight도 없다. 게스트 논리를 깊게 깔 날이다</h1>
  <div class="hero">
    금요 FOMC·BOJ 뒤 테이프(반도체 선별 강세 · 10Y 5% 턱 · 유가 ~100)는 <b>토요 방송에서 이미 읽혔다</b>.
    오늘 MAIN 8편은 그 소화 논리다 — 금리인상=무조건 악재 거부(박병창·염블리·김학균·문홍철),
    외인 1조·60일선(이주연), 10Y 터치에 비중만 줄이는 운전(김민수),
    AI=혁명 vs 주식 거품의 패널 갈림(김광석·김영익·정주용), CXL 풀링(엑시나 ※후원), 문홍철의 종가 5% 구분.
    일 AM에 들어온 추가 대담 4편(홍기빈·박정호·신환종·김효진)과 텔레그램 노트는 <b>MAIN이 아니다</b>.
    피지컬 AI·속도조절 면피·스티키 인플레·자금 약한 고리를 같은 잠금 규칙으로 깐다.
    가격 구간·IB 목표·500조 이익·UBS 90%는 estimate일 뿐 <b>방 합의로 잠그지 않는다</b>.
  </div>

  <div class="kpi">
    <div><h3>한국</h3><div class="n">휴장</div><p>일 · 새 KR 테이프 없음</p></div>
    <div><h3>나스닥 금</h3><div class="n pos">+0.40</div><p>26,522.55</p></div>
    <div><h3>S&amp;P 금</h3><div class="n pos">+0.17</div><p>7,650.50</p></div>
    <div><h3>다우 금</h3><div class="n neg">−0.18</div><p>51,682.64</p></div>
    <div><h3>SOX 금 / 목</h3><div class="n">+2.78 / +3.1</div><p>날을 섞지 말 것</p></div>
    <div><h3>10Y 워킹</h3><div class="n">4.95–5.01</div><p>터치 ≠ 안착 · OFF</p></div>
    <div><h3>WTI 금 정산</h3><div class="n">$100.30</div><p>사이렌 120 미발화</p></div>
    <div><h3>준혁 프레임</h3><div class="n">유지</div><p>5% · 6% · TIPS 3.0</p></div>
  </div>

  <div class="grid">
    <div class="card wide">
      <h2>0. 시계 — 목 PDF를 금·토·일로 세탁하지 말 것</h2>
      <img src="{c[0]}" alt="시계 4층"/>
      <p>업로드 PDF 3편(미국증시 9/17 · 조선업 0917 · 현지 인텔 분위기)은 <b>목 9/17 미국장</b> 메모다. FOMC는 <b>금 9/18</b>. 오늘 새 overnight 창은 없다.</p>
    </div>

    <div class="card">
      <h2>1. 테이프 — 목 안도 vs 금 혼조</h2>
      <img src="{c[1]}" alt="목 vs 금 지수"/>
      <ul>
        <li><span class="tag f">사실</span>금: 나스닥 +0.40 · S&amp;P +0.17 · 다우 −0.18 · SOX +2.78 · WTI $100.30(−1.61).</li>
        <li><span class="tag f">사실</span>목: 다우 +0.6 · S&amp;P +1.1 · 나스닥 +1.7 · SOX +3.1. 전일 10Y 5% 부담의 되돌림.</li>
        <li><span class="tag f">사실</span>목 신규실업수당 19.6만(컨센 20.7만). 노동은 아직 견조 — PDF와 교차.</li>
        <li><span class="tag i">해석</span>목 SOX +3.1은 ‘Fed 긴축 종료’가 아니라 기술적·매크로 안도. 금 SOX +2.78은 FOMC 다음날 AI 선별 매수.</li>
      </ul>
      <div class="note">토 AM/PM이 이미 금요 종가를 읽었다. 오늘 숫자를 창작하거나 월요일 방향을 쓰지 않는다.</div>
    </div>
    <div class="card">
      <h2>2. 사이렌 — 둘 다 OFF</h2>
      <img src="{c[2]}" alt="10Y와 유가 사이렌"/>
      <ul>
        <li>사용자 프레임: <b>10Y 5% 안착 · oil 120</b>. 오늘은 둘 다 미발화.</li>
        <li>문홍철: 장중 5% 터치는 잦아도 종가 5% 위 마감은 (거의) 없었다. 지금 4.99/4.95군.</li>
        <li>김민수: “5.04인가”를 보고 비중을 고민 — touch ≠ settle과 정합.</li>
        <li>김학균: 유가 100$+ · 10Y 5%+는 상당 부분 반영(판단). 마지노선 발화 ≠ 안착 잠금.</li>
      </ul>
      <div class="ok">워킹 10Y 4.95–5.01 · 금 장중 5.002 보도 · WTI $100.30. 승격 금지.</div>
    </div>

    <div class="card wide">
      <h2>3. 한눈에 보는 패널 뷰 — 합의 세탁 금지</h2>
      <img src="{c[10]}" alt="패널 온도 매트릭스"/>
      <table>
        <tr><th>분석 주제</th><th>박병창 (삼프로)</th><th>염승환 (함께읽기)</th><th>김학균 · 이경민</th><th>문홍철 (인포맥스)</th></tr>
        <tr><td>금리인상</td><td>선반영. 성장↑금리↑면 악재 공식 폐기. 12월 한 차례는 본인 가설.</td><td>첫날 조정 후 금리·유가 빠지면 소화. 2010년대 역행 → 최근 동행.</td><td>기준 ~4% vs 시장 ~5.3%. 유가·장기금리가 상단. 최종 4.5–4.75는 estimate.</td><td>물가 3%대면 인상 정당. 터치 vs 종가를 가른다.</td></tr>
        <tr><td>반도체</td><td>이벤트 소화 뒤 홀드·분할. CTS 숫자는 못 믿겠다는 시장도 인정.</td><td>네비우스 +20% · MLCC +30% · 병목은 OSAT·전력·기판.</td><td>AI 사이클 + 추석 전은 확언이 아니라 판단 구간.</td><td>닉스 “200만도 안 왔는데 던지듯” — 도발 · 잠금 ❌</td></tr>
        <tr><td>리스크</td><td>유가·전쟁 + 12월 인상이 겹치면 타이밍 밀림.</td><td>동행 다음엔 동반 하락(사이클 종료) — 프레임이지 법칙 아님.</td><td>5% 지속(재정·이자) 회의는 학균 축.</td><td>엔 약세 구조 · 100bp 올려도 엔 약세는 시나리오.</td></tr>
      </table>
      <table>
        <tr><th>분석 주제</th><th>김광석</th><th>김영익</th><th>정주용</th><th>이주연 · 김민수</th></tr>
        <tr><td>AI</td><td>반도체 국가 재편. 수출 40%/48%(방송 통계).</td><td>기술은 혁명, 주식은 거품. 한국 피해가 클 수 있다.</td><td>철도 안 놓고 버블 논하지 말 것. GPU 스팟이 안 떨어지면 아직.</td><td>민수: 반도체 주도 전제. 주연: AI→8인치·SOFC 확산.</td></tr>
        <tr><td>수급·운전</td><td>—</td><td>밸류·금리 축. 사이렌과 “근접·관전”만.</td><td>DC 5조$는 비전.</td><td>주연: 외인~1조·기관~1.8조·60일선. 민수: 불안 시 30%는 개인 운용.</td></tr>
      </table>
      <div class="risk">성상현 부부장은 오늘 MAIN 8에 없다. 과거 11월 대선·잭슨홀 대담을 오늘 비교표에 끌어오지 않는다.</div>
    </div>

    <div class="card">
      <h2>4. AI 3자 — 혁명 / 거품 / 인프라</h2>
      <img src="{c[3]}" alt="김광석 김영익 정주용"/>
      <ul>
        <li><span class="tag f">사실</span>한은 전망 인용 올해 3.3 · 내년 2.9 (방송). 수출 비중 서술 40%/48% — 원표 재대조.</li>
        <li>중국 점유 “24년 75 → 25년 70 → 올해 2Q 63”(창신 도전) — 방송 통계.</li>
        <li>정주용 검증 규칙: GPU 스팟이 안 떨어지면 버블 아직. 엔비디아·팔란티어 OPM 60%대는 approx.</li>
        <li>공통 관전은 미 10Y 5% <b>근접</b>이 밸류 논의의 축이라는 점뿐.</li>
      </ul>
      <div class="blue">수출 48% + 거품론 공존 ≈ 한국은 업사이드와 붕괴 양쪽 베타. 한쪽만으로 세탁 금지.</div>
    </div>
    <div class="card">
      <h2>5. 금리=악재 공식 거부</h2>
      <img src="{c[4]}" alt="네 명의 거부 이유"/>
      <ul>
        <li>박: 비둘기파적 인상은 기대만큼 안 나왔지만, 궤는 선반영. 저성장·저금리에서 성장↑금리↑로 국면 전환.</li>
        <li>염: 금리 읽는 법이 바뀜. 병목은 GPU에서 후공정·전력·기판.</li>
        <li>학균: 과거 기준 5.5% 때 시장 고점 ~5.1% vs 지금 기준 4%인데 시장 5.3%까지 — 장기금리가 더 부담.</li>
        <li>이경민: 최종금리 시각 4.5–4.75가 이벤트 후에도 안 바뀐 점이 안도(estimate). SPX “2%면 ATH”도 estimate.</li>
      </ul>
      <div class="note">역산: 인상 + 다음날 반도체·코스피 반등 ≈ 시장 가중치는 이벤트보다 장기금리·유가 방향 + AI 가격전가.</div>
    </div>

    <div class="card wide">
      <h2>6. MAIN 8 — 채널당 1 · 토 PM 재등록 없음</h2>
      <table>
        <tr><th>슬롯</th><th>채널</th><th>게스트</th><th>시계</th><th>한 줄</th><th>조회 ~08:22</th></tr>
        {mains}
      </table>
      <div class="grid">
        <div>
          <h3>MAIN 1 박병창</h3>
          <ul>
            <li>10월 말은 “진짜” 인상 창이 아니라는 구분.</li>
            <li><span class="tag x">잠금❌</span>CTS 삼성~500조 · 닉스 370~380 · 닉스 200만 · 삼전 29~30만 · 지수 7,500. “제 바람·제 분석”.</li>
            <li>웰스파고 S&amp;P 목표가 하향(7,950→)은 이익 유지·멀티플 삭감식 경계(방송 인용).</li>
          </ul>
          <h3>MAIN 2 이주연 ※촬영 금 19:00</h3>
          <ul>
            <li>토요 overnight 마감 브리핑이 아님. 코스피 60일선 붙음, 코스닥은 이미 위 안착 서술.</li>
            <li>8인치 파운드리 인상 사이클(DS투자 인용) · 블룸 가이던스 39~42억.</li>
            <li>모기지 6.5→7%대는 source approx. 토 PM H6와 시계 분리.</li>
          </ul>
          <h3>MAIN 3 김민수</h3>
          <ul>
            <li>종목 팁·수익 자랑은 digest에서 버린다. 10Y 5%/5.04 터치가 입구.</li>
            <li><span class="tag x">잠금❌</span>포트 30% · 26조 · 매출 비중 670% · 200만/29만.</li>
          </ul>
          <h3>MAIN 5 엑시나 ※후원</h3>
          <ul>
            <li>HBM 슈퍼사이클을 부정하지 않고 확장 메모리로 보완. CXL 표준 2019~.</li>
            <li>활용 35%→70~80% · CapEx 절반 = company claim. 제목 1만배는 은유.</li>
          </ul>
        </div>
        <div>
          <h3>MAIN 6 경제전쟁꾼</h3>
          <ul>
            <li>토 AM CROSS였던 편을 밀도 때문에 Sun MAIN으로 승격. 새 테이프가 아니다.</li>
            <li>코어 CPI 3~4%대에서 ~2.4 서술(approx). 추가 인상 vs “시장금리가 연준을 압박”은 온도차.</li>
          </ul>
          <h3>MAIN 7 문홍철</h3>
          <ul>
            <li>코어 PCE 0.2%p 하향 수정(2021~ 재작성)은 estimate/해석.</li>
            <li>코스피 6,900 안착 미완·추석 전 7,000 가능은 시나리오.</li>
            <li>일본 재정 GDP 대비 적자 −1~2%에 가깝다 — 가정.</li>
          </ul>
          <h3>MAIN 8 염블리 함께읽기 ※비밀노트와 다른 편</h3>
          <ul>
            <li>영란 동결 · BOJ 인상(예상대로). 네비우스 GPU 임대 +20 · AMD 가속기 인상 · MLCC 8월 +30.</li>
            <li>IB 310/400/59가 반복돼도 targets ≠ 합의 가격.</li>
          </ul>
          <img src="{c[11]}" alt="815 수급"/>
        </div>
      </div>
    </div>

    <div class="card">
      <h2>7. PDF A — 9/17 미국증시</h2>
      <img src="{c[6]}" alt="목 SOX 개별"/>
      <ul>
        <li>원인: 금리 5%가 하루 만에 완화 + 유가 공급차질 우려 완화. 침체형 금리 하락이 아님.</li>
        <li>ARM: 르네 하스 CNBC. $2bn은 <b>수요 가시성</b>. 공식 아웃룩은 약 $1bn대에 가깝다. PDF의 “목표 달성 자신”은 한 단계 과장.</li>
        <li>인텔 개별: (1) 하이닉스 Ohio 협력 <b>기대</b> (2) Tigress $118→$145 Buy · Northland OP $120 (3) Altera 9/15 비밀 S-1 · $2bn+는 Reuters 소스.</li>
        <li>AI 자율규제기구 무산(젠슨·저커버그·머스크) — 최소규제 기조. 단기 우호, 주정부·전력 인허가는 남음.</li>
      </ul>
      <div class="note">PDF 경고: 유가 $105–110 + 10Y 재차 5%면 같은 조정 논리 반복 가능. 금요일에 그 턱을 다시 봤다. 안착은 아님.</div>
    </div>
    <div class="card">
      <h2>8. PDF B — 현지 인텔 분위기</h2>
      <img src="{c[5]}" alt="Ohio 체인"/>
      <ul>
        <li>블로거 체인: 하이닉스 미국 DRAM → Ohio Fab → Indiana HBM 패키징 → 미국산 HBM → 인텔 고객·자금·Foundry 신뢰.</li>
        <li><span class="tag f">사실</span>Reuters 9/16: 탐색. 임차 또는 클라우드 JV 시나리오. 제품 종류 미확인. Ohio 가동은 2030–31로 지연된 상태.</li>
        <li>하이닉스: “결정된 사항 없음”. 인텔: speculation 코멘트 거부.</li>
        <li>블로거 질문 “주가가 여기까지이니 반영한 것일까?” — <b>미잠금</b>. 단순 임차 vs 고객 선투자형 JV가 핵심 분기.</li>
      </ul>
      <div class="risk">토 PM·오늘도 SoftBank–Apollo와 같이 웹/공시 잠금 전. ‘미국 Fab 확정’으로 쓰지 말 것.</div>
    </div>

    <div class="card wide">
      <h2>9. PDF C — 조선업 0917. 이익은 이미, 멀티플은 아직</h2>
      <img src="{c[7]}" alt="조선 3축"/>
      <ul>
        <li>원문 한 줄: 상선만 보면 P·Q 성장의 한계. 이익은 과거 고점을 넘겼다. 신규 3축이 <b>실제 수주</b>로 확인되면 낮아진 멀티플을 재평가할 수 있다.</li>
        <li><span class="tag f">사실</span>HD현대중공업 육상 힘센 캐파 4GW는 <b>2030 목표</b>(온산 공장 2028 완공 가정). “이미 4GW”가 아님. 코반에너지 1,000MW · 9,560억 공급계약(8월)은 별도 사실.</li>
        <li><span class="tag p">부분</span>한화엔진 AIDC향 수주는 가능성. 한화오션 60MW는 가스텍 공개 + ABS AiP — 수주 아님.</li>
        <li>삼성중공업 FDC: 2Q28 첫 가동 목표. M3와 엔지니어링 계약(50MW 유닛). EPC 본계약은 의도 단계.</li>
        <li>글로벌 함정은 파이프라인이지 전투함 수주 확정이 아님.</li>
      </ul>
      <div class="ok">815·정지훈 축의 전력 병목과 맞닿는다. 주간 포지션 문장에 ‘조선 리레이팅 확정’을 넣지 말 것.</div>
    </div>

    <div class="card">
      <h2>10. CXL — 스폰서와 매크로를 분리</h2>
      <img src="{c[8]}" alt="CXL 활용률"/>
      <p>병목 정의(동의 가능): 모델↑·유저↑·컨텍스트↑가 동시에 커지면 메모리가 막힌다. HBM은 GPU 패키지 종속·고가.</p>
      <p>가정(회사): 풀링으로 활용 2배 · 동일 성능에 CapEx 절반. MX1 근접연산은 제품 주장.</p>
      <div class="note">HBM 수요를 대체한다는 문장으로 인용하지 말 것. 보완·효율 주장이다.</div>
    </div>
    <div class="card">
      <h2>11. 토 PM MAIN — 한 줄만</h2>
      <table>
        <tr><th>편</th><th>ID</th><th>상태</th></tr>
        {sat}
      </table>
      <div class="blue">숫자 변동 없으면 생략해도 된다. 오늘 보드에 본편으로 다시 올리지 않았다.</div>
      <div class="note">{HAKGYUN_MEMBERSHIP}</div>
    </div>

    <div class="card wide">
      <h2>12b. 추가 대담 4 — MAIN 슬롯 아님 · 토 PM 재등록 아님</h2>
      <img src="{c[12]}" alt="추가 대담 4인"/>
      <table>
        <tr><th>슬롯</th><th>채널</th><th>게스트</th><th>시계</th><th>한 줄</th><th>길이</th></tr>
        {addons}
      </table>
      <div class="risk">유튜브 ID는 원문에 없음. 가짜 ID를 만들지 않는다. 성상현 부부장은 오늘 MAIN 8에도 ADDON에도 없다.</div>
    </div>

    <div class="card">
      <h2>12c. 홍기빈 — 암묵지와 데이터 커먼스</h2>
      <img src="{c[14]}" alt="피지컬 AI와 PCB"/>
      <ul>
        <li><span class="tag i">해석</span>LLM은 기록된 기호 세계를 털었다. 야구방망이로 유리창을 쳤을 때 파편이 어디로 가는지는 월드모델.</li>
        <li>지식노동은 복제가 쉽고, 청소·설거지·용접 같은 암묵지는 피지컬 AI의 병목. 주객이 잠깐 뒤집힌다.</li>
        <li>동작 데이터는 한 번 스캔으로 안 끝난다. 양파 썰기도 경우의 수가 무궁하다. 숙련 노동의 협조가 비용을 줄인다.</li>
        <li>협조 유인이 없으면 테일러식 태업이 재연된다. 한 번에 팔고 땡이 아니라 데이터 커먼스 + 소득 흐름.</li>
        <li>현대차×보스턴다이나믹스는 공장 로봇을 만들 수 있는 자리. 노조 입장에선 세상의 끝. 교착=스테일메이트.</li>
        <li><span class="tag p">부분</span>블랑샤르식 일반재정(균형) vs 자본계정(장기투자)은 학술 아이디어. 한국 미래대응기금 거버넌스는 미정.</li>
        <li>소버린 AI는 와이파이처럼 싸게 쓰는 모델이 아니라 한국 정서·행정·토지 데이터의 인프라. 경부고속도로는 은유.</li>
        <li><span class="tag f">사실</span>샌더스·카사르 ASI 금지법은 9/3 발표·법안 번호 미확인. 통과가 아님. 홍기빈은 자원 투여의 선을 묻는 문제제기로 읽음.</li>
      </ul>
      <div class="note">데이터 커먼스 제도는 전인미답. ‘이미 합의됐다’로 쓰지 말 것. 중국 직진 vs 한국 합의는 효율 논쟁이지 승패 확정이 아님.</div>
    </div>
    <div class="card">
      <h2>12d. 박정호 — 속도조절은 면피에 가깝다</h2>
      <ul>
        <li>지분 있는 창업 CEO가 정말 두렵면 본인 랩부터 감속하면 된다. 화두만 던지고 훈련 중단은 명시 반대.</li>
        <li>검수 속도가 개발을 못 따라간다. 에이전트에 일을 맡긴 뒤 사람을 또 뽑으면 원점이 된다.</li>
        <li><span class="tag p">부분</span>허깅페이스 사건은 2026-07 평가 샌드박스 탈출로 양사 공개가 있다. “GPT가 자백하고 로그를 지웠다”는 게스트 풍문. 확정 사실이 아님.</li>
        <li>정부·양당 모두 감속보다 중국 추월 반대를 우선. 민주당 메시지조차 ‘규제를 빨리, 개발은 하라’.</li>
        <li>아모데이의 외부 평가·민주국가 컨센서스·중국 참여 요청은 하우투가 없다. 박정호는 이를 뻥·면피로 본다(판단).</li>
        <li>소버린: 미국이 여론에 감속하면 한국은 같이 쉬지 말고 월세(API 비용)를 줄일 타이밍.</li>
      </ul>
      <div class="blue">역산: 경고 + 훈련 계속 ≈ 레이스는 안 멈춘다. 준혁 프레임의 ‘약한 고리=자금+장기금리’와 충돌하지 않는다.</div>
    </div>

    <div class="card">
      <h2>12e. 신환종 — 스티키 인플레, 터치 ≠ 안착</h2>
      <ul>
        <li>ASR ‘케비너시’는 케빈 워시(연준 의장 맥락). 메인 6과 같은 인물. 하셋과 섞지 말 것.</li>
        <li>10Y 5% 터치·장기물 부담은 문홍철·김민수와 정합. <b>안착으로 승격하지 않는다</b>.</li>
        <li>자경단은 신자유주의 때 힘. 지금은 케인지안·재정·군비·캡엑스. 공급이 많고 신흥국은 국채 대신 금.</li>
        <li>달러 위상 100→90→60~70, 금 20% 헤지, 브라질 달러채 YTM ~7.5, 원/달러 1,350~1,380은 <span class="tag x">잠금❌</span> 게스트 시나리오.</li>
        <li>AI 디플레(0~1%)는 인프라·휴머노이드·전력 이후. 2027–30은 오히려 인플레 유발 가능(판단).</li>
        <li>4분기 주식은 이란 시각·수급 약화로 신중. 전망이 틀리길 바란다는 본인 말. 월요일 방향 아님.</li>
      </ul>
      <div class="ok">워킹 10Y 4.95–5.01 · WTI $100.30. 신환종이 5%를 말해도 사이렌 OFF.</div>
    </div>
    <div class="card">
      <h2>12f. 김효진 — 아스트라 이후에도 약한 고리는 돈</h2>
      <ul>
        <li>아스트라=에이전트 한 걸음. 긴 업무·더 많은 메모리·더 비싼 요금. HBM만이 아니라 일반 메모리·스토리지도 필요(판단).</li>
        <li>하이퍼스케일러 캡엑스 ‘올해 ~7,500억$ · 내년 ~1조$’는 게스트 어림. UBS 경로와 숫자를 섞어 합의로 만들지 말 것.</li>
        <li>자기 현금 → 회사채·사모·3억 크레딧. 장부를 뜯어보게 된 것이 올해의 난도.</li>
        <li>GPU 유동화(엔비디아×블랙록·KKR·브룩필드 등): 8/10 MOU·동원 목표 ~5,000억$. 시작도 안 한 프레임. 2008 MBS 재현으로 잠그지 말 것.</li>
        <li>10Y 5%는 실적이 좋아도 주가 발목을 잡는 임계(판단). 터치 ≠ 사이클 종료.</li>
        <li>삼전 vs 닉스: 둘 다 좋다는 개인 온도. HBM 점유 40% 기사는 잠금 금지. 자사주 종료 후 수급은 외국인 관전.</li>
      </ul>
      <div class="note">랠리 종료 신호는 기술 구멍이 아니라 돈을 제때 좋은 금리로 못 구하는 것 — 준혁 프레임과 같은 축.</div>
    </div>

    <div class="card wide">
      <h2>12g. 텔레그램 노트 — IB·정치 헤드라인. 합의 아님</h2>
      <img src="{c[13]}" alt="UBS 메모리 추정"/>
      <table>
        <tr><th>항목</th><th>원문 한 줄</th><th>교차</th><th>잠금</th></tr>
        <tr><td>UBS CapEx</td><td>2025 5,060 → 2026 9,980 → 2027 14,470억$. 증가분 ~90%가 메모리 가격.</td><td>2차 보도 9/19. UBS WM 다른 글은 2026 9,000 / 2027 1.2조로 결이 다름.</td><td>IB 추정. 방 합의 ❌</td></tr>
        <tr><td>바클레이즈 휴머노이드</td><td>대량 보급이 2030이 아니라 2035 전후일 수 있다. 꼭 인간형일 필요 없음.</td><td>공식 노트: 2030은 점진($10–25B), 2035 베이스 $40B·낙관 $200B. 피지컬 AI 전체가 더 큼.</td><td>시나리오. 보급 확정 ❌</td></tr>
        <tr><td>유니트리 왕싱싱</td><td>최대 단점은 얼라인먼트. 마지막 몇 cm·mm.</td><td>창업자 발언 인용. 가정 정리 ‘방 정리해’는 비전.</td><td>인용. 일정 아님</td></tr>
        <tr><td>트럼프 AI Force</td><td>AI를 GDP 25% 산업으로. 감속보다 주도권.</td><td>9/19 소셜 선언. 조직·권한·예산 미공개. 25%는 대통령 주장.</td><td>공식 전망 ❌</td></tr>
        <tr><td>속도조절 반독점</td><td>감속 합의가 담합으로 해석될 수 있다.</td><td>9/18 N.D. Cal. 소장 단계. 실제 감속 확인 아님.</td><td>원고 주장</td></tr>
        <tr><td>엘크 녹각</td><td>AI 능력은 뿔이 아니라 효용. GPU는 버려도 재배치.</td><td>은유. 지출폭포·헬멧 모순은 메모.</td><td>프레임이지 수치 아님</td></tr>
        <tr><td>PCB·SoCAMM</td><td>2027 축=고다층 MLB + SoCAMM + ABF/FC-BGA.</td><td>두산CCL→이수 MLB→심텍→티엘비 SoCAMM→대덕/삼성전기. 브로커 EPS·PER는 잠금 금지.</td><td>유니버스. 목표가≠합의</td></tr>
      </table>
      <div class="ok">메모리 가격 상승 → 아시아 생산국 명목 수혜라는 UBS 매크로 문장은 ‘물량이 아니라 가격’ 가정 위에서만 성립. 한국 GDP 리레이팅으로 쓰지 말 것.</div>
    </div>

    <div class="card wide">
      <h2>12. 공식 / 역산 / 가정 / 추정 · 준혁 프레임 유지</h2>
      <div class="src">
        <div><b>공식</b>일 휴장 · 금 종가(나스닥 +0.40 · S&amp;P +0.17 · 다우 −0.18 · SOX +2.78 · WTI $100.30) · 목 SOX +3.1 · 네비우스 +20 · MLCC +30 · 수출 40/48(방송) · 사이렌 미발화 · Ohio 탐색 · Altera 비밀 제출 · Tigress $145 · HD 4GW는 2030 목표 · 샌더스 ASI 금지는 9/3 발표(미통과) · 허깅페이스 침입은 양사 공개(로그 삭제는 풍문) · 트럼프 AI Force는 9/19 선언</div>
        <div><b>역산</b>기준 인상 + 다음날 반도체 반등 ≈ 가중치는 장기금리·유가 + AI 전가. 장중 5% 빈발 + 종가 5% 위 희소 ≈ touch≠settle. 수출 48% + 거품론 공존 ≈ 양쪽 베타. 경고 + 훈련 계속 ≈ 감속 없음. 암묵지 병목 + 협조 부재 ≈ 피지컬 AI는 데이터가 아니라 사회협약.</div>
        <div><b>가정</b>FOMC 2일차·선반영이 쇼크를 소음화. 60일선+외인=박스 탈출 필요조건(충분 아님). CXL은 HBM 보완. SoftBank–Apollo · OP370 · CTS 500/370 미잠금. 블랑샤르 이계정은 아이디어. 데이터 커먼스는 미제도.</div>
        <div><b>추정 ❌</b>닉스 200만 · 삼전 29~30만 · IB 310/400/59 · 12월 추가 인상 · 최종 4.5–4.75 · 코스피 7,000 / 지수 7,500 · 월요일 방향 · Ohio 이미 반영 · UBS 90% · GDP 25% · 달러 60–70 · 금 20% · 휴머노이드 2035 확정 · GPU 5,000억$ 동원 완료.</div>
        <div><b>준혁 프레임</b>10Y 5% · 30Y 6% · TIPS 3.0% · 닉스 buyback vs 삼성 dividend/Jan · AI 약한 고리=자금+장기금리. A/B·상자 비유 없음. 가격 구간 재잠금 없음. 김효진·박정호도 자금·금리를 약한 고리로 본다.</div>
        <div><b>GAP</b>당잠사 9/19 없음 → 다음 9/22. 한경 파이널콜 Sat 없음. 인포맥스 Sat LIVE 없음(금 편으로 밀도 대체). 각도기 일요 overnight 없음. 머니올라 미중 회담 프리미어 대기 → 월 재확인. ADDON 4편의 공식 유튜브 ID 없음.</div>
      </div>
      <img src="{c[9]}" alt="캘린더"/>
      <div class="hero" style="margin-top:8px;">
        <b>다음 슬롯.</b> 월요 정규장 전후 당잠사·각도기 · SOX/10Y/WTI settle 재교차 · Apollo 한 줄 · 프리미어 해소분.
        프로세스: 추석 3거래일 · 미중 회담(목) · 삼전 배당 ~9/28–30 · 마이크론 10/1.
      </div>
    </div>

    <div class="card wide">
      <h2>13. 쓰지 말 것</h2>
      <div class="risk">
        10Y 5% 안착 · oil 120 · SoftBank–Apollo 확정 · 삼성 OP 370조 합의 · CTS 500/370–380을 가이던스로 ·
        IB 310/400/59 = 방 합의 · 닉스 200만 · 삼전 29~30만 · Ohio/하이닉스 계약 확정 · ARM $2bn = 공식 가이던스 ·
        HD현대 육상 4GW 이미 가동 · 한화오션 60MW 수주 · 삼성중 FDC EPC 확정 · 월요일 방향/% ·
        토 PM 6편을 오늘 MAIN으로 재등록 · 성상현 11월 대선 대담을 오늘 3자 토론으로 치환 ·
        추가 대담 4편을 MAIN 9–12로 승격 · 신한 멤버십 김학균을 새 MAIN으로 ·
        UBS 90% = 방 합의 · 트럼프 GDP 25% = 공식 전망 · 허깅페이스 로그 삭제 = 확정 ·
        GPU 유동화 = 2008 · 바클레이즈 2035 = 보급 확정 · 데이터 커먼스 제도 확정 · 속도조절 = 실제 감속 ·
        샌더스 ASI 금지법 통과
      </div>
    </div>
  </div>
  <div class="foot">
    원문: YouTube 자동자막 ko (MAIN 8) · 추가 대담 4 자막(ID 미확인) · 텔레그램 퀵코멘트 · 업로드 PDF 3편 ·
    종가 교차 Reuters/서울경제/MarketScreener · Ohio=Reuters 9/16 · 샌더스=9/3 발표 ·
    허깅페이스=양사 2026-07 공개 · UBS CapEx=2차 보도 9/19 · AI Force=9/19 선언 ·
    GPU 금융=엔비디아 8/10 MOU · WTI 금 정산 $100.30 · 조회 yt-dlp ~08:22 KST.
    사실/부분/해석/잠금금지를 갈랐다. 준혁 프레임 유지.
  </div>
</div>
</body>
</html>
"""


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    text = html()
    OUT.write_text(text, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
