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
    c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15 = (
        uri("01_market_rebound.png"),
        uri("02_flows.png"),
        uri("03_boj_yen.png"),
        uri("04_nodes.png"),
        uri("09_flywheel.png"),
        uri("05_memory_gap.png"),
        uri("06_us_footprint.png"),
        uri("08_generac.png"),
        uri("07_korea_gdp.png"),
        uri("10_bottom_shapes.png"),
        uri("11_and_gate.png"),
        uri("12_misery_lead.png"),
        uri("13_box_range.png"),
        uri("14_nvidia_cash.png"),
        uri("15_token_pq.png"),
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
  <div class="kicker">2026.09.18  ·  FOMC 다음날 + BOJ 인상일  ·  영상 10편 + 퀵코멘트  ·  시각화 보드</div>
  <h1>산은 넘었다. 바닥은 W. 박스는 6,000–7,150. 현금이 답을 안 냈다</h1>
  <div class="hero">
    <b>한 장.</b> 이은택: 바닥은 <b>W</b>. 5%는 AND의 한쪽일 뿐 이번 주 터치는 해제됐다.
    윤지호: 위로도 아래로도 쉽지 않은 <b>박스</b>. 8,000은 아직 안 연다. 상단을 여는 열쇠는 하이퍼스케일러가 토큰으로 현금을 다시 만드는 신호.
    엔비디아 마진은 75%인데 현금전환은 40%. 정지훈의 프레임은 그대로다. <b>병목=노드=돈</b>. 연산은 풀렸고 지금은 메모리, 다음 영수증은 전력이다.
  </div>

  <div class="kpi">
    <div><h3>KOSPI</h3><div class="n">6,894.23</div><p>+178.82 · +2.66% · 고가 6,914</p></div>
    <div><h3>코스닥</h3><div class="n">827.12</div><p>+4.94 · +0.60% · 4일 연속</p></div>
    <div><h3>삼전 / 닉스</h3><div class="n">+3.4 / +6.4</div><p>26.1만 · 185.7만</p></div>
    <div><h3>BOJ</h3><div class="n">1.25%</div><p>7–2 · 아사다·사토 반대</p></div>
    <div><h3>원/달러</h3><div class="n">1,383.3</div><p>+1.1원 · 엔 157.12</p></div>
    <div><h3>국고 10년</h3><div class="n">4.466%</div><p>−4.0bp · 장기물 낙폭</p></div>
    <div><h3>개인 매도</h3><div class="n">−3.59조</div><p>9월 초중순만 15조+</p></div>
    <div><h3>미 10년</h3><div class="n">4.95%</div><p>주중 5.04 터치 후 해제</p></div>
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
      <div class="risk">다음 흔들림: 10년 5.0~5.3% <b>추세</b> 돌파 + 인플레 재가속 · WTI $105–110 · 12월 추가 인상 · 부외리스($1.7조 표 vs $3조 추정).</div>
    </div>

    <div class="card">
      <h2>4b. 이은택 — 바닥은 V가 아니라 W</h2>
      <img src="{c10}" alt="V W 트리플 바닥"/>
      <ul>
        <li><span class="tag f">사실</span>고점 6/22 <b>9,114.55</b> → 7/30 <b>5,593.56</b> = <span class="neg">−38.6%</span>. 이사는 “30% 정도”로 반올림.</li>
        <li>25%+ 급락은 10년에 세 번 안팎. V는 희귀(2003 이라크, 2020 팬데믹). 트리플은 1998·2000·2008 위기형.</li>
        <li><span class="tag i">해석</span>제일 많은 건 W(쌍바닥). 기간 조정 2~4개월. 전저점 재방문은 필수가 아니다. 지금은 두 번째 바닥 형성.</li>
        <li><span class="tag f">사실</span>9월 1–10일 개인 순매도 약 <b>15.6조</b>. “첫 바닥 이후 15~17조”와 맞는다. 오늘 −3.59조가 그 연장.</li>
      </ul>
      <div class="note">차트로 전망하지 않는다. 급락 뒤 한 번에 안 털고, 두 번째 바닥에서 지쳐 판다. 그 수급이 가벼워져야 W가 완성된다.</div>
    </div>
    <div class="card">
      <h2>4c. Gravity Rules — 5%는 AND의 한쪽</h2>
      <img src="{c11}" alt="버블 붕괴 AND 게이트"/>
      <ul>
        <li>5월 노트: 빅테크는 캡엑스를 못 멈춘다. 꺾는 쪽은 <b>자본공급자</b>(은행·보험·국부펀드).</li>
        <li><span class="tag f">사실</span>7/22 알파벳 캡엑스 $195–205B로 상향, 다음날 주가 약 −7%. 캡엑스 증액이 붕괴 변수가 아님을 보여 준 날.</li>
        <li>조건 1 <b>Breaking New Highs</b>: 5.0~5.3%를 추세로. 주중 고가 5.041, 금요일 4.951 → 터치 후 해제.</li>
        <li>조건 2 <b>No Way Back</b>: 인플레가 외통수. <span class="tag p">부분</span>이사는 3.0→2.6 하향. 헤드라인은 3.4% 횡보, 코어만 2.5→2.4.</li>
      </ul>
      <div class="ok">둘 다 켜져야 붕괴. 지금은 아님. 5%는 위험 신호이지 방아쇠가 아니다. 노트 3번째 시그널(OpenAI IPO 실패)은 오늘 방송에 안 나옴.</div>
    </div>

    <div class="card">
      <h2>4d. 윤지호 — 박스이지 추세가 아니다</h2>
      <img src="{c13}" alt="코스피 박스 6000-7150"/>
      <ul>
        <li><span class="tag i">해석</span>한줄평: 위로도 아래로도 쉽지 않다. 논트렌딩·박스. 방향 예측보다 <b>지금 주가를 결정하는 힘</b>을 찾으라.</li>
        <li>두 소: AI 과잉투자에 노출된 한국 이익 + 작년 상법·주주환원. 두 곰: 투자 사이클의 자금 한계 + 포퓰리즘·재정적자 → 금리.</li>
        <li><span class="tag p">부분</span>S&amp;P PER 19.5~19.7. FactSet 9/11 선행 19.1, 후행 25.9. 방송이 “역수=20%”라고 한 건 오해. 19.5의 역수는 약 <b>5.1%</b>.</li>
        <li>Fed 모델로는 10년 5%와 선행 이익수익률(~5%)이 붙는다. 주식이 이기려면 앞으로 이익이 더 나와야 한다.</li>
      </ul>
      <div class="note">9–10월은 우려가 가격에 붙는 구간. 8,000 강세장은 아니다. 주식 많은 사람은 반등 축소, 현금은 박스 하단에서. 각자 포트가 답이다.</div>
    </div>
    <div class="card">
      <h2>4e. 엔비디아 — 마진 75, 현금은 40</h2>
      <img src="{c14}" alt="엔비디아 마진 대 현금전환"/>
      <ul>
        <li><span class="tag f">사실</span>Q2 FY27(7/26 마감, 8/26 발표): 매출 $96.2B, GM <b>75.0%</b>, 순이익 $59.7B, 영업현금 $24.1B = 전환 <b>40.3%</b>.</li>
        <li>매출채권 $63.1B. DSO 45→60일. 우량 고객 장기 계약의 결제 연장. 방송의 “외상”은 이 숫자.</li>
        <li><span class="tag p">부분</span>“2분기 이익의 상당액이 지분평가” — Q2 평가이익은 $7.8B(순이익의 13%). 상반기 $23.7B를 한 분기로 말한 듯.</li>
        <li><span class="tag p">부분</span>CDS 프리미엄이 7월부터 올랐다는 말은 공개 시계열을 못 박지 못함. 쓰지 말 것.</li>
      </ul>
      <div class="risk">시장이 묻는 것: 하이퍼스케일러 현금이 다시 도느냐. 답이 없으면 상단이 안 열린다. 나쁜 답이 나오면 꼬꾸라진다.</div>
    </div>

    <div class="card">
      <h2>4f. 토큰 — P↓여도 Q가 더 늘면 된다</h2>
      <img src="{c15}" alt="토큰 가격 하락 사용량 증가"/>
      <ul>
        <li><span class="tag f">사실</span>JPM·OpenRouter 8월: 볼륨 MoM +47% · YoY <b>28배</b>. 지출 +7% · 12배. 가중단가 −28%.</li>
        <li>윤지호: OpenAI가 토큰을 많이 만들어 생태가 돌아가야 한다. 비용↓ + 품질↑. Astra는 너무 비싸다. 속도조절은 코스트 시그널.</li>
        <li><span class="tag i">해석</span>죄수의 딜레마. 배신의 보상이 커서 속도를 진짜로 늦추기는 어렵다. 말이 나온 것 자체가 불안.</li>
        <li><span class="tag p">부분</span>방송 “올해 8월까지 31% · 전년 2,400% · 초당 1,000억”은 원소스가 안 맞는다. 방향만 JPM으로 교정.</li>
      </ul>
      <div class="ok">인포맥스 민수: P는 떨어져도 Q가 더 늘면 하이퍼스케일러를 걱정 마라. 윤지호는 그 신호가 아직 약하다고 본다.</div>
    </div>
    <div class="card">
      <h2>4g. 금요일 주간 — 7,150 네 번째, 순환매</h2>
      <ul>
        <li><b>인포맥스</b> FOMC는 둘째 날이 본심. NH “호미로 막았다”가 나스닥 급등에 맞았다. 아모데이 한 방이 이중바닥.</li>
        <li>코스피 7,150–7,200을 네 번 두드렸다. 코스닥은 “변비” — 힘은 쓰는데 거래가 안 붙는다.</li>
        <li><span class="tag p">부분</span>예탁금 100조 아래. 8/28 약 96.7조. 방송의 “곧 100조”는 이미 깨진 숫자.</li>
        <li><span class="tag p">부분</span>현대차 수출 30%: 산업 수출액 −29.8%. 현대 대수 −48.9%. 해외판매 −8.5%와 섞지 말 것.</li>
        <li><b>황유현</b> 인상은 기정사실화. 남은 퍼즐은 유가. 지수는 추세 전환이 아니다. 전력·전선·화장품·조선엔진.</li>
        <li><span class="tag p">부분</span>개인 7,000 위 물량 150조 · 외인 7월까지 180조 매도 · 삼전 외인 46–47%는 공개 집계를 못 박지 못함.</li>
      </ul>
      <div class="blue">황: 닉스 210–214만은 한 번 연다(해석). 월화수 밀리면 산다. 3·4등주는 사지 마라. 2027 병목은 전력.</div>
    </div>

    <div class="card wide">
      <h2>4h. 소부장 — HBM이 온양을 먹고, Q는 28년에 온다</h2>
      <ul>
        <li><span class="tag f">사실</span>TheElec 9/15: 삼성은 DDR5 모듈·SSD <b>증분</b>을 외주. 천안·온양은 HBM. 파트너는 한양디지텍(베트남)·드림텍(인도)·SFA세미콘(필리핀).</li>
        <li><span class="tag p">부분</span>좌담이 하나마이크론을 삼성 DDR5 파트너로 특정. 확인된 이름은 위 셋. 하나마이크론은 베트남 OSAT 증설 수혜 후보.</li>
        <li>테스트·소켓·OSAT가 7월 말 이후 상대 강도. DI·엑시콘·ISC·하나마이크론·PSK홀딩스. 실적은 삼성 반등보다 약 6개월 후행.</li>
        <li><span class="tag i">해석</span>손희원: 블랙 180만장 → 베라루빈 280만장. 선제 증설은 고객 요청의 흔적. Q사이클은 28년. 지금부터 풀베팅은 아니다.</li>
        <li>원전은 장기 베이스로드. 2차전지는 바닥은 찍었으나 가격 주도권 없음 → 셀(SDI) &gt; 소재, 실적 시즌엔 의심. 광통신은 엔비디아 벤더와 스토리를 가를 것.</li>
        <li><span class="tag p">부분</span>알테오젠 시총 “18조”. 9월 초 약 20.8조. 에코프로 “11조”는 미확인. 상징은 주성이 4위라는 말.</li>
      </ul>
      <div class="note">물리 영수증이 거짓말이 아니다. 효성 변압기 · 두산퓨얼셀 · 두산 CCL · 현대일렉 엔진 · Generac. 주가가 안 가는 이유는 숫자를 안 믿어서다.</div>
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
        <li><span class="tag p">부분</span>이은택: 작년 코스피 +70%면 연초 한은 1.6~1.8은 낮다. 실제 2025년은 <b>+75.6%</b>. 주가가 GDP를 6~12개월 선행.</li>
        <li>문남중: 원화가 1,300초까지 내려온 구간은 삼전·닉스 환차손 3–5조 부담. 지금은 1,380대로 되돌림.</li>
      </ul>
    </div>

    <div class="card wide">
      <h2>9b. 이은택 꿀팁 — 고통지수의 왕, 주가가 GDP를 선행</h2>
      <img src="{c12}" alt="고통지수와 주가 선행"/>
      <ul>
        <li>오쿤 고통지수 = 실업률 + 인플레. 저물가 때는 실업이 왕(실업↑ → 매도). 고물가 때는 인플레가 왕.</li>
        <li><span class="tag p">부분</span>2022 공식: CPI 고점 다음 분기에 산다. 이사는 7월 전후. 실제 고점은 <b>6월 9.1%</b>. S&amp;P 저점 10/12, 코스피 종가 저점 9/30.</li>
        <li>같은 해 주가와 GDP는 약하거나 역. 작년 주가 → 올해 성장. 폭락 뒤 6~12개월은 장기채 쪽.</li>
        <li>한국 10년은 “8부능선”. 국고 종가 4.466%(−4bp). 금리 방향은 은행·보험 트레이딩에 쓴다.</li>
      </ul>
      <div class="blue">내년 GDP로 지금 주가를 끌 수는 없다. 선행하는 쪽이 먼저 간다. 후행을 맞춰 선형을 만들 수 없다.</div>
    </div>

    <div class="card wide">
      <h2>10. 열 방송이 겹치는 곳 · 갈리는 곳</h2>
      <div class="src">
        <div><b>정지훈 · 노드</b>병목이 돈이다. 지금은 메모리. 다음 에너지는 효율·광·SMR. 디지털+피지컬 이중 플라이휠.</div>
        <div><b>이은택 · Gravity</b>바닥은 W. 붕괴는 5.0~5.3 추세 AND No Way Back. 빅테크는 못 멈추고 자본공급자가 멈춘다.</div>
        <div><b>윤지호 · 박스</b>논트렌딩. 8,000 아님. 상단은 하이퍼스케일러 현금·토큰 답이 나와야 연다. 마진 75 ≠ 현금 40.</div>
        <div><b>인포맥스 주간</b>FOMC는 둘째 날. 7,150 네 번째. 토큰 P↓Q↑. 삼성 EPS가 안 꺾이면 전고점. 유가 송유관은 10월.</div>
        <div><b>황유현</b>인상은 기정사실화. 지수는 아직. 순환매·1·2등주. 닉스 210만은 한 번(해석). 월화수 밀리면 산다.</div>
        <div><b>소부장 좌담</b>HBM이 온양을 먹으니 범용은 외주. Q는 28년. 원전 장기, 전지는 셀&gt;소재, 광은 벤더만.</div>
        <div><b>증시각도기</b>KOSPI 6,900 턱밑. 외인 매도 정지. BOJ 인상에도 엔 약세. Generac → 전선. 속도조절 기구 무산.</div>
        <div><b>문남중</b>불확실성 제거. 실질정책금리 +. 엔캐리 과장. 속도조절은 노이즈. 추석 전 쉬고 후에 반등. HBM·전력·DC.</div>
        <div><b>박승진</b>점도표 &lt; 시장. 12월 인상 가능성. 반도체는 최전방이라 변동성 큼 → XLK·IYW·BAI·CHAT. 내년 이익증가율 둔화, 소비 바닥.</div>
        <div><b>빈센트</b>높은 물가·금리 패러다임. 5% 집착 말 것. AI 속도조절은 정치+노이즈. 시대 주식=AI 하드웨어. CXMT는 옛 문법으로 끝장 아님.</div>
        <div><b>입담화</b>산 하나 넘음. 미중 너무 친해지면 2차전지·통신·태양광 반사익 축소. 투톱 홀드, 소부장 ETF, 기판·MLCC 동행. 21일 전력망 특집.</div>
      </div>
      <table>
        <tr><th>주제</th><th>합의</th><th>온도 차</th></tr>
        <tr><td>금리 vs 주식</td><td>성장 있는 인상이면 버틴다. 5% 터치 ≠ 붕괴</td><td>이은택은 AND, 빈센트는 5% 집착 말 것, 윤지호는 5% vs PER 역수(5.1%)</td></tr>
        <tr><td>지수 위치</td><td>급락 뒤 바로 V는 드묾. 7,000 위는 무겁다</td><td>이은택=W 2차, 윤지호=박스, 황=추세 아님, 인포맥스=7,150 네 번째</td></tr>
        <tr><td>속도조절</td><td>중국은 안 멈춤</td><td>윤지호는 코스트 시그널+죄수딜레마. 빈센트는 중간선거 정치</td></tr>
        <tr><td>토큰</td><td>P↓Q↑면 사이클은 산다</td><td>민수는 걱정 마라, 윤지호는 현금 신호가 아직 약하다</td></tr>
        <tr><td>주도</td><td>메모리 + 전력 + DC</td><td>황·소부장은 순환매·후공정, 박승진은 IT ETF</td></tr>
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
          <div class="risk">쓰지 말 것 = Ohio/NY 투자 확정 · 젠슨 2배=매출 2배 · 원/달러 1,587 · 매일 1.6조 자사주 · 10년 5% 터치=버블 붕괴 · 코스피 −30%를 정확한 낙폭 · 헤드라인 물가 하향 확정 · 이윤택(이은택) · CXMT 즉각 공급 해소 · AEMA=전력기기 소멸 · PER 19.5의 역수=20% · 엔비디아 CDS 7월 급등 · 토큰 2,400%·초당 1,000억 · 하나마이크론=삼성 DDR5 확정 파트너 · 외인 7월까지 180조 · 개인 7,000 위 150조 · 예탁금 100조 유지</div>
          <div class="ok">사실로 쓸 것 = KOSPI 6,894.23 · 고점 대비 −38.6%(7/30) · 미 10년 주중 5.04→4.95 · BOJ 1.25% 7–2 · 9월 개인 15조+ · Solidigm 검토 · Citi 메모리 2031 · Generac $24억/$80억 · 원/달러 1,383.3 · 엔비디아 GM 75% / OCF 40.3% · OpenRouter 볼륨 28배 · 삼성 모듈 증분 외주 · 자동차 수출액 −29.8%</div>
          <div class="hero" style="margin:8px 0 0;">
            <b>가을 확인 다섯.</b> 10년 5.0~5.3% <b>추세</b> + 물가 재가속(AND) · 10/1 마이크론 마진 · DevDay(9/29) 토큰·현금 · Ohio/NY가 계약인지 · 3분기, 하이퍼스케일러 현금이 다시 도는지.
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class="foot">출처 교차: 거래소·연합뉴스·BOJ 성명·Reuters·Citi·JPM/OpenRouter·NVIDIA 8/26·TheElec 9/15·산업부 8월 자동차·CNBC·8-K·BLS·Fed H.15·FactSet 9/11·KB증권 Gravity Rules(5/29). 영상=정지훈, 이은택, 윤지호, 인포맥스, 황유현, 소부장 좌담, 증시각도기, 문남중, 박승진, 빈센트, 입담화 + 퀵코멘트. 사실/부분/해석을 갈랐다.</div>
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
