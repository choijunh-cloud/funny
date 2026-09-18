#!/usr/bin/env python3
"""9월 18일 영상·퀵코멘트를 시각화 보드로 합친다. 차트는 base64 내장."""

from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path("/workspace")
CHARTS = ROOT / "lectures" / "assets" / "sep18"
OUT = ROOT / "lectures" / "9월 18일 AI·반도체 시장 코멘트 한장.html"


def uri(name: str) -> str:
    raw = (CHARTS / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def html() -> str:
    c1, c2, c3, c4, c5, c6, c7, c8, c9 = (
        uri("01_market_rebound.png"),
        uri("02_flows.png"),
        uri("03_boj_yen.png"),
        uri("04_nodes.png"),
        uri("09_flywheel.png"),
        uri("05_memory_gap.png"),
        uri("06_us_footprint.png"),
        uri("08_generac.png"),
        uri("07_korea_gdp.png"),
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>9월 18일 AI·반도체 시장 코멘트 — 시각화 보드</title>
<style>
:root {{ --navy:#0f2043; --navy2:#1e407c; --gold:#b8943a; --ink:#1a1a1a;
  --muted:#4b5563; --line:#d5dce6; --bg:#eef1f7; --green:#166534; --red:#991b1b; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans CJK KR","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic","WenQuanYi Micro Hei",sans-serif;
  word-spacing:.12em; }}
.board {{ width:1320px; margin:0 auto; padding:16px 16px 22px; }}
.kicker {{ color:var(--gold); font-weight:800; font-size:12px; letter-spacing:.03em; }}
h1 {{ color:var(--navy); font-size:25px; line-height:1.22; margin:4px 0 8px; }}
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
.flow {{ display:flex; flex-wrap:wrap; gap:5px; align-items:center; margin:5px 0; }}
.flow span {{ background:var(--navy); color:#fff; padding:3px 8px; border-radius:999px; font-size:11px; font-weight:700; }}
.flow i {{ color:var(--gold); font-style:normal; font-weight:800; }}
.tag {{ display:inline-block; font-size:10px; font-weight:800; padding:0 5px; border-radius:999px; margin-right:3px; }}
.tag.f {{ background:#e8f5e9; color:var(--green); }}
.tag.p {{ background:#fff8e7; color:#7a5c12; }}
.tag.i {{ background:#e8f1fb; color:var(--navy2); }}
.src {{ display:grid; grid-template-columns:repeat(3,1fr); gap:6px; }}
.src div {{ background:#f7f9fc; border-radius:8px; padding:7px 8px; font-size:11.3px; line-height:1.38; }}
.src b {{ color:var(--navy); display:block; margin-bottom:2px; }}
.foot {{ color:var(--muted); font-size:10.6px; margin-top:8px; text-align:right; }}
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
  <div class="kicker">2026.09.18  ·  FOMC 다음날 + BOJ 인상일  ·  영상 5편 + 퀵코멘트  ·  시각화 보드</div>
  <h1>산은 넘었다. 노드는 메모리 → 전력. 미국 3축은 아직 검토다</h1>
  <div class="hero">
    <b>한 장.</b> 연준·BOJ가 올린 뒤에도 주식은 안도했다. 알려진 인상은 악재가 아니었다.
    정지훈의 프레임은 그대로다. <b>병목=노드=돈</b>. 연산은 풀렸고 지금은 메모리다.
    에너지는 가장 복제하기 어렵다. Amazon–Generac $24억이 그 영수증이다.
    하이닉스 미국은 Indiana(확정) · Ohio(협의) · New York(검토) 세 줄이다. 확정 뉴스가 아니다.
  </div>

  <div class="kpi">
    <div><h3>KOSPI</h3><div class="n">6,894.23</div><p>+178.82 · +2.66% · 고가 6,914</p></div>
    <div><h3>코스닥</h3><div class="n">827.12</div><p>+4.94 · +0.60% · 4일 연속</p></div>
    <div><h3>삼전 / 닉스</h3><div class="n">+3.4 / +6.4</div><p>26.1만 · 185.7만</p></div>
    <div><h3>BOJ</h3><div class="n">1.25%</div><p>7–2 · 아사다·사토 반대</p></div>
    <div><h3>원/달러</h3><div class="n">1,383.3</div><p>+1.1원 · 엔 157.12</p></div>
    <div><h3>국고 10년</h3><div class="n">4.466%</div><p>−4.0bp · 장기물 낙폭</p></div>
    <div><h3>개인 매도</h3><div class="n">−3.59조</div><p>기관+1.50 · 법인+1.67</p></div>
    <div><h3>젠슨</h3><div class="n">칩 2배</div><p>대수. 매출 +70%는 FY28</p></div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>1. 9/18 장 — 금리 산 다음의 안도</h2>
      <img src="{c1}" alt="9/18 시장 반등"/>
      <ul>
        <li><span class="tag f">사실</span>KOSPI <span class="pos">6,894.23 (+2.66%)</span>. 6,900은 장중만. 오른 종목 407 vs 내린 종목 463 — 시총 상단이 밀었다.</li>
        <li>9/17 美: 다우 +0.6 · S&amp;P +1.1 · 나스닥 +1.7 · SOX +3.1. 전날 10년 5% 부담의 되돌림.</li>
        <li>WTI는 다시 $100 아래. 브렌트 약 $102.3(−1.7%). 유가·금리가 같이 꺾인 날.</li>
      </ul>
      <div class="ok">문남중·박승진·빈센트·입담화의 공통점: 이번 인상은 침체형이 아니다. 성장이 있는 인상.</div>
    </div>
    <div class="card">
      <h2>2. 수급 — 개인은 팔고, 자사주가 받았다</h2>
      <img src="{c2}" alt="9/18 수급"/>
      <ul>
        <li><span class="tag f">사실</span>KRX 정규: 개인 <span class="neg">−3.59조</span> · 기관 +1.50조 · 외인 +0.43조 · 기타법인 +1.67조.</li>
        <li>외인은 하이닉스 <span class="pos">+1.33조</span>, 삼성 <span class="neg">−0.46조</span>. 8거래일 만에 순매수 전환.</li>
        <li><span class="tag p">부분</span>방송의 “매일 1.6조 자사주”는 당일 기타법인 숫자와 섞인 듯. 당일 1.67조는 사실, 매일 평균은 아님.</li>
      </ul>
      <div class="note">입담화: 추석 전 개인 3조 매도. “급하지 않으면 팔지 말라.” 최근 10년 추석 전 5일 KOSPI −0.42%, 후 +0.68%.</div>
    </div>

    <div class="card">
      <h2>3. BOJ — 31년 만의 1.25%, 엔은 반대로</h2>
      <img src="{c3}" alt="BOJ 인상과 엔 약세"/>
      <table>
        <tr><th>항목</th><th>숫자</th><th>판정</th></tr>
        <tr><td>정책금리</td><td>1.00 → 1.25%, 9/24 시행</td><td>사실 · 7–2</td></tr>
        <tr><td>반대</td><td>아사다(신선식품제외 CPI&lt;2%) · 사토(가속 없음)</td><td>사실</td></tr>
        <tr><td>성명</td><td>Continue to raise. 7월과 문구 변화 제한</td><td>사실</td></tr>
        <tr><td>엔</td><td>157.12(+1.15) · 원/엔 880.27</td><td>사실</td></tr>
        <tr><td>방송 원/달러</td><td>“1,587 / 87.50”</td><td>오역. 종가 1,383.3</td></tr>
        <tr><td>국고 10년</td><td>방송 −2.5bp / 4.46</td><td>종가 −4.0bp / 4.466</td></tr>
      </table>
      <div class="blue">문남중: 미·일 10년 스프레드 약 2%p면 엔캐리 청산은 어렵다. 일본 기업의 미국 직접투자 비중이 커졌다.</div>
    </div>
    <div class="card">
      <h2>4. 매크로 합의 — 금리보다 성장, 5%는 상수 아님</h2>
      <ul>
        <li><b>박승진</b> 점도표는 시장(내년 1.8회)보다 낮다. 올해 한 번 더 후 내년 동결이 중앙값. Warsh는 자기 점을 안 냈다. 앞을 조이고 뒤를 덜어 주는 그림.</li>
        <li><b>빈센트</b> GDP 2.3→2.4, 실업 4.1 고정, 코어 PCE는 내년 하락. 수요+공급 양면 인상. 월가는 앞으로 1년 100bp를 이미 가정하고 움직인다.</li>
        <li><b>문남중</b> 7월 PCE 3.7 − 기금 3.75 ≈ 실질정책금리 +0.05. 플러스 구간에서는 주식이 버틴다.</li>
        <li><b>증시각도기</b> 대출금리는 국채보다 늦게 오른다. 긴축 효과는 약 6개월 시차 → 28년을 조심.</li>
      </ul>
      <div class="risk">다음 흔들림: 10년 5% 재돌파 · WTI $105–110 · 12월 추가 인상 · 하이퍼스케일러 부외리스($1.7조 표 vs $3조 추정, 박승진).</div>
    </div>

    <div class="card wide">
      <h2>5. 오늘의 지도 — 노드와 두 개의 플라이휠 (정지훈)</h2>
      <div class="grid">
        <div>
          <img src="{c4}" alt="노드 병목 순서"/>
        </div>
        <div>
          <img src="{c5}" alt="디지털·피지컬 AI 플라이휠"/>
        </div>
      </div>
      <div class="flow"><span>연산 병목 해제</span><i>→</i><span>메모리 전 영역</span><i>→</i><span>에너지(가장 어려움)</span><i>→</i><span>자본 노드</span></div>
      <ul>
        <li>플라이휠은 아마존 냅킨이다. 이익을 <b>못</b> 내는 게 아니라 <b>안</b> 낸다. 임계를 넘으면 마지막 노드인 캐피탈이 스스로 돈다.</li>
        <li>PC–윈텔은 한 사이클. AI는 디지털(토큰)과 피지컬(로봇·공장)이 시차를 두고 같이 뜬다.</li>
        <li>토큰 전략이 갈렸다. Anthropic = 같은 토큰을 약 5배 비싸게 받아도 잔류(측정치, 해석). Google = Flash + 워크스페이스 번들. OpenAI = 가격↓ → 일을 더 시킨다.</li>
        <li>메타 Bailey 광스위치 4대 → GPU 유휴 줄고 효율 <b>+40%</b> → 엔비디아 Lumentum 투자 → 광·코닝 테마. 병목을 푸는 쪽이 한동안 가격을 받는다.</li>
        <li>SMR이 뜨는 이유 중 하나: 기존 화력 인프라에 들어간다. 공기를 줄인다.</li>
      </ul>
      <div class="note">에너지가 풀리면 실리콘 병목이 다시 올라온다. 다음 견인차는 삼전·닉스만이 아닐 수 있다.</div>
    </div>

    <div class="card">
      <h2>6. 메모리 — 지속학습이 부족을 2031까지</h2>
      <img src="{c6}" alt="Citi 메모리 수급 갭"/>
      <ul>
        <li><span class="tag f">사실</span>Citi: 지속학습이 HBM·서버 DDR5·eSSD 수요를 동시에 끌어올린다. 부족을 2031까지 연장할 수 있다.</li>
        <li>HBM 비트 +62%(27) / +69%(28). DRAM 부족 −8.7 → −9.7. NAND −6.1 → −5.5.</li>
        <li>젠슨 9/17: “내년 칩을 올해의 두 배 판다.” <span class="tag p">부분</span>대수지, 매출 2배 아님. FY28 매출 가이던스는 약 $673B(+70%).</li>
        <li>대만 매체 4Q DRAM +20% / NAND +30% QoQ. 퀵코멘트도 원소스를 못 박지 못함. 방향만.</li>
      </ul>
      <div class="ok">에이전틱으로 가면 중간산출·컨텍스트가 쌓인다. HBM이 아니어도 메모리는 끝없이 는다.</div>
    </div>
    <div class="card">
      <h2>7. 하이닉스 미국 3축 + CXMT NAND</h2>
      <img src="{c7}" alt="하이닉스 미국 3축"/>
      <table>
        <tr><th>축</th><th>상태</th><th>의미</th></tr>
        <tr><td>Indiana</td><td>HBM 후공정 진행</td><td>$40억+ · 2029H2</td></tr>
        <tr><td>Ohio × Intel</td><td>9/16 협의</td><td>제품 종류 미정 · 탐색</td></tr>
        <tr><td>NY Solidigm</td><td>9/18 검토</td><td>NAND 전공정 · 다롄 분산</td></tr>
        <tr><td>CXMT 베이징</td><td>같은 날 Reuters</td><td>NAND R&amp;D·시험. 양산 아님</td></tr>
      </table>
      <div class="risk">미국 NAND는 원가가 높다. 보조금·LTA·경제성이 투자 결정 변수. ‘미국 Fab 확정’으로 쓰지 말 것.</div>
    </div>

    <div class="card">
      <h2>8. 전력 — 영수증이 나오기 시작했다</h2>
      <img src="{c8}" alt="Amazon Generac 계약"/>
      <ul>
        <li><span class="tag f">사실</span>Amazon–Generac 8-K. 비상발전기 27–28년 $24억, 워런트 한도 $80억. UPS가 아니다.</li>
        <li>가온전선 장중 +18~22%(고가 32.6만). LS에코·대한·일진 동반. 입담화: 가온 밸류 이미 비싸다. LS·일진·산일·현대일렉·효성을 보라.</li>
        <li>PJM: 9/16 최대발전·부하관리 경보. 백업발전 동원 권한을 DOE에 신청. 공개 명령 202-26-41은 9/1–8. 9/17–18 신규 발령은 보도 기준.</li>
      </ul>
      <div class="blue">캡엑스가 GPU에서 뒤단(전선·변압기·비상전원)으로 번지는 증거. AEMA는 유연 부하이지 변압기 대체가 아니다.</div>
    </div>
    <div class="card">
      <h2>9. 한국 성장 — Citi 3.7 / 3.1 / 3.0</h2>
      <img src="{c9}" alt="Citi vs 한은 성장률"/>
      <ul>
        <li>반도체 수출 +175%(26) / +41%(27). 실질 +3.2%p, 명목 +15.6%p. 명목 GDP 25%는 1981년 이후 최고 가정.</li>
        <li>한은 8월 3.3 / 2.9보다 위. LTA 선수금이 투자를 고정한다.</li>
        <li>문남중: 원화가 1,300초까지 내려온 구간은 삼전·닉스 환차손 3–5조 부담. 지금은 1,380대로 되돌림.</li>
        <li>빈센트: 펀더멘털은 아래, 심리는 위 → 환율은 횡보. 1,400 재돌파해도 예전 같은 공포는 덜할 것.</li>
      </ul>
    </div>

    <div class="card wide">
      <h2>10. 다섯 방송이 겹치는 곳 · 갈리는 곳</h2>
      <div class="src">
        <div><b>정지훈 · 노드</b>병목이 돈이다. 지금은 메모리. 다음 에너지는 효율·광·SMR. 디지털+피지컬 이중 플라이휠.</div>
        <div><b>증시각도기</b>KOSPI 6,900 턱밑. 외인 매도 정지. BOJ 인상에도 엔 약세. Generac → 전선. 속도조절 기구 무산.</div>
        <div><b>문남중</b>불확실성 제거. 실질정책금리 +. 엔캐리 과장. 속도조절은 노이즈. 추석 전 쉬고 후에 반등. HBM·전력·DC.</div>
        <div><b>박승진</b>점도표 &lt; 시장. 12월 인상 가능성. 반도체는 최전방이라 변동성 큼 → XLK·IYW·BAI·CHAT. 내년 이익증가율 둔화, 소비 바닥.</div>
        <div><b>빈센트</b>높은 물가·금리 패러다임. 5% 집착 말 것. AI 속도조절은 정치+노이즈. 시대 주식=AI 하드웨어. CXMT는 옛 문법으로 끝장 아님.</div>
        <div><b>입담화</b>산 하나 넘음. 미중 너무 친해지면 2차전지·통신·태양광 반사익 축소. 투톱 홀드, 소부장 ETF, 기판·MLCC 동행. 21일 전력망 특집.</div>
      </div>
      <table>
        <tr><th>주제</th><th>합의</th><th>온도 차</th></tr>
        <tr><td>금리 vs 주식</td><td>성장 있는 인상이면 버틴다</td><td>박승진·빈센트는 울퉁불퉁, 증시각도기는 28년 시차</td></tr>
        <tr><td>속도조절</td><td>노이즈. 중국은 안 멈춤</td><td>빈센트는 중간선거·데이터센터 정치로 치환</td></tr>
        <tr><td>주도</td><td>메모리 + 전력 + DC</td><td>박승진은 종목 대신 IT ETF, 입담화는 소부장·기판</td></tr>
        <tr><td>미국 공장</td><td>탐색·검토</td><td>주가에 이미 기대가 들어갔는지는 미확인</td></tr>
        <tr><td>밸류에이션</td><td>이익이 금리를 상쇄해야 한다</td><td>BofA −3%/10년, NZ Super 평균회귀는 경고이지 컨센 아님</td></tr>
      </table>
    </div>

    <div class="card wide">
      <h2>11. 개별 · 쓰지 말 것 · 가을 확인</h2>
      <div class="grid">
        <div>
          <ul>
            <li><b>규제기구</b> WSJ: 젠슨·저커버그·머스크가 업계 자율규제기구를 막았다. 최소규제 기조. 주정부·전력 인허가는 남는다.</li>
            <li><b>골드만 중국</b> 싸게 깔고 점유 후 올린다. 로봇청소기·변압기·H형강. 전기차·로봇택시는 아직 내부 출혈.</li>
            <li><b>모건스탠리</b> 중국 35년까지 산업 전환 투자. 방송 15조 vs 본문 10조 달러 — 숫자 혼선. 방향만.</li>
            <li><b>Berkshire</b> 일본 상사 지분 10–15% 추가 검토(블룸버그). 금리 올라도 일본 실물.</li>
            <li><b>Anthropic IPO</b> 방송의 “10월 말 $2조, 이미 흑자”는 내부 전언 수준. 사실로 쓰지 말 것.</li>
            <li><b>소부장</b> 자율공시 막혀 가이던스 없음. 밸류 20–90배는 의미 약함. 입담화는 ETF를 바구니로.</li>
          </ul>
        </div>
        <div>
          <div class="risk">쓰지 말 것 = Ohio/NY 투자 확정 · 젠슨 2배=매출 2배 · 원/달러 1,587 · 매일 1.6조 자사주 · CXMT NAND 즉각 공급 해소 · 속도조절=캡엑스 종료 · AEMA=전력기기 소멸</div>
          <div class="ok">사실로 쓸 것 = KOSPI 6,894.23 · BOJ 1.25% 7–2 · Solidigm 검토 · Citi 메모리 2031 · Generac $24억/$80억 · 젠슨 칩 대수 2배 · 원/달러 1,383.3</div>
          <div class="hero" style="margin:8px 0 0;">
            <b>가을 확인 넷.</b> 10/1 마이크론 마진 · DevDay(9/29) 에이전트·토큰 · Ohio/NY가 계약으로 넘어가는지 · 10년 5%와 유가 $100이 다시 붙는지.
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="foot">출처 교차: 거래소·연합뉴스·BOJ 성명·Reuters(Solidigm/CXMT/Generac)·Citi·CNBC(젠슨)·8-K. 영상=정지훈, 증시각도기, 문남중, 박승진, 빈센트, 입담화 + 퀵코멘트. 사실/부분/해석을 갈랐다.</div>
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
