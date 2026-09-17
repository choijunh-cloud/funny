#!/usr/bin/env python3
"""9월 17일 AI·반도체 시장 코멘트 HTML 브리핑."""

from __future__ import annotations

from pathlib import Path

OUT = Path("/workspace/lectures/9월 17일 AI·반도체 시장 코멘트.html")
CHART = Path("/workspace/lectures/assets/sep17")


def img(name: str, alt: str) -> str:
    rel = f"assets/sep17/{name}"
    if not (CHART / name).exists():
        return f'<p class="muted">차트 없음: {name}</p>'
    return f'<img src="{rel}" alt="{alt}"/>'


def build() -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>9월 17일 AI·반도체 시장 코멘트</title>
<style>
:root {{
  --navy:#0f2043; --navy2:#1e407c; --gold:#b8943a; --ink:#1a1a1a;
  --muted:#4b5563; --line:#d5dce6; --bg:#eef1f7; --green:#166534; --red:#991b1b;
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--bg); color:var(--ink);
  font-family:"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR","WenQuanYi Micro Hei",sans-serif; }}
.wrap {{ width:min(1240px,96vw); margin:0 auto; padding:18px 12px 40px; }}
.kicker {{ color:var(--gold); font-weight:800; font-size:12px; letter-spacing:.04em; }}
h1 {{ color:var(--navy); font-size:28px; line-height:1.25; margin:4px 0 8px; }}
h2 {{ margin:0 0 8px; color:var(--navy); font-size:17px; border-bottom:2px solid var(--navy); padding-bottom:5px; }}
h3 {{ margin:12px 0 6px; color:var(--navy2); font-size:14px; }}
.sub {{ color:var(--muted); margin:0 0 14px; font-size:13.5px; }}
.hero {{ background:var(--navy); color:#fff; border-radius:14px; padding:16px 18px; margin-bottom:12px; font-size:14.5px; line-height:1.55; }}
.hero b {{ color:var(--gold); }}
.kpi {{ display:grid; grid-template-columns:repeat(6,1fr); gap:8px; margin-bottom:12px; }}
.kpi div {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:9px 10px; }}
.kpi h3 {{ margin:0; font-size:11px; color:var(--navy2); border:0; padding:0; }}
.kpi .n {{ font-size:16px; font-weight:800; color:var(--navy); margin-top:3px; }}
.kpi p {{ margin:3px 0 0; font-size:11px; color:var(--muted); line-height:1.35; }}
.cols {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:13px 14px; margin-bottom:10px; }}
.card p, .card li {{ font-size:13px; line-height:1.5; margin:0 0 6px; }}
.card ul {{ margin:0 0 6px; padding-left:18px; }}
.wide {{ grid-column:1/-1; }}
img {{ width:100%; border-radius:8px; border:1px solid var(--line); display:block; margin:6px 0; background:#fff; }}
table {{ width:100%; border-collapse:collapse; font-size:12.2px; margin:6px 0 4px; }}
th {{ background:var(--navy); color:#fff; padding:5px 7px; text-align:left; }}
td {{ padding:5px 7px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:nth-child(even) td {{ background:#f7f9fc; }}
.pos {{ color:var(--green); font-weight:700; }}
.neg {{ color:var(--red); font-weight:700; }}
.note, .ok, .risk, .blue {{ padding:8px 10px; border-radius:0 8px 8px 0; font-size:12.6px; margin:7px 0; line-height:1.45; }}
.note {{ background:#fff8e7; border-left:4px solid var(--gold); }}
.ok {{ background:#e8f5e9; border-left:4px solid var(--green); }}
.risk {{ background:#fdecea; border-left:4px solid var(--red); }}
.blue {{ background:#e8f1fb; border-left:4px solid var(--navy2); }}
.flow {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:8px 0; }}
.chip {{ background:#eef2f8; color:var(--navy); border-radius:999px; padding:4px 10px; font-size:12px; font-weight:700; }}
.arrow {{ color:var(--gold); font-weight:800; }}
.tag {{ display:inline-block; font-size:10.5px; font-weight:800; padding:1px 6px; border-radius:999px; margin-right:4px; }}
.tag.f {{ background:#e8f5e9; color:var(--green); }}
.tag.p {{ background:#fff8e7; color:#7a5c12; }}
.tag.i {{ background:#e8f1fb; color:var(--navy2); }}
.tag.x {{ background:#fdecea; color:var(--red); }}
footer {{ color:var(--muted); font-size:11.5px; text-align:right; margin-top:8px; }}
@media (max-width:900px) {{
  .kpi, .cols {{ grid-template-columns:1fr 1fr; }}
}}
</style>
</head>
<body>
<div class="wrap">
<p class="kicker">2026.09.17  ·  FOMC 다음날  ·  퀵코멘트 + 첨부 PDF 주제별 재구성</p>
<h1>9월 17일 AI·반도체 시장 코멘트</h1>
<p class="sub">금리 경로 · 속도조절론 · OpenAI DevDay · 하이닉스–인텔 · 데이터센터 전력 TAM</p>

<div class="hero">
<b>한 장 결론.</b> 이번 인상은 침체형이 아니다. 강한 경기 + 인플레 + AI 자본수요다.
속도조절은 개발 <b>각도</b> 이야기다. 45도에서 35도로 낮춰도 7월까지 보던 수요는 안 줄어든다.
DevDay(9/29)에서 볼 것은 더 똑똑한 모델이 아니라 <b>Agent 사용량 · API 토큰 · 기업 배포</b>다.
하이닉스–인텔 오하이오는 <b>탐색</b>이다. 전력 161GW는 사실이고, AEMA는 병목 완화이지 변압기 대체가 아니다.
</div>

<div class="kpi">
  <div><h3>FOMC</h3><div class="n">3.75–4.00%</div><p>+25bp 만장일치. 중앙값 4.1 / 4.1 / 3.9</p></div>
  <div><h3>GDP / Core PCE</h3><div class="n">2.3 → 2.4</div><p>27년 Core PCE 2.5 유지. 성장만 +0.1%p</p></div>
  <div><h3>9/16 美</h3><div class="n">10Y 5.04%</div><p>WTI $105.8 · S&amp;P −0.45 · SOX +0.4</p></div>
  <div><h3>KOSPI</h3><div class="n">6,717.97</div><p>+1.37%. 하이닉스 +4.08% · 삼전 +2.01%</p></div>
  <div><h3>DevDay</h3><div class="n">9/29</div><p>Fort Mason. 모델보다 Agent 배포</p></div>
  <div><h3>DC 전력</h3><div class="n">161GW</div><p>2026 +31%. 2030 종이 갭 268GW</p></div>
</div>

<div class="card">
<h2>읽는 법</h2>
<p><span class="tag f">사실</span>연준 SEP · OpenAI · Reuters · TrendForce · 거래소
<span class="tag p">부분</span>방향은 맞지만 숫자·범위가 다름
<span class="tag i">해석</span>논리로 쓰되 확정처럼 쓰지 말 것
<span class="tag x">금지</span>Ohio 확정 · 12→8단 전면전환 · AEMA=전력기기 소멸 · 속도조절=캡엑스 종료</p>
</div>

<div class="cols">
  <div class="card">
    <h2>1. FOMC — 인상은 선반영, 경로는 중앙값</h2>
    {img("01_fomc_dots.png", "FOMC 점도표 중앙값")}
    <table>
      <tr><th>항목</th><th>2026</th><th>2027</th><th>2028</th><th>장기</th></tr>
      <tr><td>연방기금 중앙값</td><td>4.1</td><td>4.1</td><td>3.9</td><td>3.2</td></tr>
      <tr><td>6월 중앙값</td><td>3.8</td><td>3.6</td><td>3.4</td><td>3.1</td></tr>
      <tr><td>실질 GDP</td><td>2.3</td><td>2.4</td><td>2.2</td><td>2.0</td></tr>
      <tr><td>Core PCE</td><td>3.4</td><td>2.5</td><td>2.2</td><td>—</td></tr>
    </table>
    <p><span class="tag f">사실</span>만장일치 +25bp. Warsh는 자기 점을 다시 안 냈다. 27년 성장 2.4 &gt; 26년 2.3, Core PCE 2.5 유지.</p>
    <p><span class="tag p">부분</span>‘올해 1회 후 내년 동결’은 중앙값. 2027년 4.375 점이 8명. 장기 3.0%는 중앙값 3.2.</p>
    <div class="blue">침체형 인상이 아니다. 강한 경기 + 인플레 + AI 자본수요. 2022년과 구별해서 본다. 상단이 보이면 스마트머니는 미리 움직인다. 지금 당장 성장주 프리미엄이 돌아온다는 뜻은 아니다.</div>
  </div>
  <div class="card">
    <h2>2. 9/16 — 매크로 부담, 반도체 차별화</h2>
    {img("04_macro_vs_chips.png", "매크로 대비 반도체 차별화")}
    <ul>
      <li>WTI $105.83 · 브렌트 $108.75 · 美 10년 장중 5.041%.</li>
      <li>Dow/S&amp;P/Nasdaq 하락, SOX는 약 <span class="pos">+0.4%</span>. 코멘트의 +0.5~0.6는 약간 큼.</li>
      <li>KOSPI <span class="pos">6,717.97 (+1.37%)</span> 4일 하락 종료. 기관 +1.21조, 외인 −1.68조.</li>
      <li>하이닉스 <span class="pos">+4.08%</span> / 삼성 <span class="pos">+2.01%</span>. 코멘트 +3.6/+1.8은 종가보다 작다.</li>
      <li>카카오페이 약 <span class="neg">−11.5%</span> — CLARITY 절차표결 부결.</li>
    </ul>
    <div class="note">웰스파고 S&amp;P 연말 7,950→7,700. 근거는 주식 비중 72%와 금리 5%이지 AI 수요 둔화가 아니다.</div>
    <div class="ok">유가·금리라는 최악의 조합에서도 SOX가 플러스, 코스피가 6,700을 지킨 것이 당일 메시지.</div>
  </div>
</div>

<div class="card">
  <h2>3. 속도조절론 — 각도는 낮춰도 수요는 유지</h2>
  <div class="flow">
    <span class="chip">35도 · 4–6월 예상</span><span class="arrow">→</span>
    <span class="chip">45도+ · Astra 충격</span><span class="arrow">→</span>
    <span class="chip">30~35도 · 속도조절</span><span class="arrow">→</span>
    <span class="chip">수요 100은 유지</span>
  </div>
  <div class="cols">
    <div>
      <p>속도조절 얘기 자체가 속도가 너무 빠르기 때문에 나왔다. 프론티어 학습을 숨 고르기 해도 <b>추론·에이전트</b>가 더 크고 더 빠르다. 가드레일 보강 자체가 연산을 늘린다.</p>
      <p>이미 만들어 둔 프론티어만으로도 수요가 넘친다. 모델사 베스트는 비싼 Astra급 경쟁을 잠시 늦추고 토큰 매출에 집중하는 것이다. 중국이 같이 멈춰 줄지는 별개다.</p>
    </div>
    <div>
      <div class="note">“지금 동결해도 활용 가치는 전체의 5~10%.” 속도조절 ≠ AI 중단. 상용화·추론이 본게임.</div>
      <div class="ok">Broadcom Hock Tan: 27–28 매출 전망 수정 이유 없다. Anthropic이 최대 커스텀 칩 고객. Peak-out보다 Duration Extension.</div>
      <div class="risk">Politico: 일시 중단 50% vs 계속 발전 31%. 여론 ≠ 캡엑스 결정.</div>
    </div>
  </div>
</div>

<div class="cols">
  <div class="card">
    <h2>4. DevDay 9/29 — 모델보다 Agent</h2>
    <p><span class="tag f">사실</span>화 9/29 Fort Mason. 키노트 10:00 PT, Sam Altman, 라이브 무료. 공식은 개발자·API·도구 배포 행사.</p>
    <table>
      <tr><th>축</th><th>내용</th><th>인프라</th></tr>
      <tr><td>Agent</td><td>답변 → 웹·코딩·업무 수행</td><td>토큰·추론량</td></tr>
      <tr><td>API</td><td>기업 서비스에 모델 탑재</td><td>AI 서버</td></tr>
      <tr><td>Deployment</td><td>실험 → 기업 업무</td><td>GPU·DRAM·HBM</td></tr>
    </table>
    <div class="flow">
      <span class="chip">Astra 배포</span><span class="arrow">→</span>
      <span class="chip">DevDay</span><span class="arrow">→</span>
      <span class="chip">Agent 대량 깔림</span>
    </div>
    <div class="blue">확인할 세 숫자: Agent 사용량 · API/토큰 · 기업 배포 속도. 확인되면 캡엑스는 학습 GPU에서 <b>추론 컴퓨팅 + 메모리</b>로 확장.</div>
    <p>벤치마크 95%가 20턴이면 36%. 실전은 재시도 능력. 평가가 IQ에서 업무 성공률로 이동하면 미국 모델 우위가 다시 보인다. <span class="tag i">해석</span></p>
  </div>
  <div class="card">
    <h2>5. 공포 — 맡기지 말고</h2>
    <p>과장과 자기이익(대중 우위, 추론 집중)이 배경일 수 있다. 인류애 담론보다 <b>소수 독점 결정</b>이 더 큰 이슈. FACT는 컴퓨팅이 턱없이 부족하다는 것.</p>
    <p>가드레일은 필요하되 다양한 목소리가 들어가면 느려진다. 종말 시나리오는 규제를 서두르는 쪽에 유리하다.</p>
    <table>
      <tr><th>쪽</th><th>입장</th></tr>
      <tr><td>Suleyman / Nadella</td><td>의식·권리를 학습시키지 말 것. deliberate pacing</td></tr>
      <tr><td>Anthropic</td><td>의식 불확실 → welfare·rights 논의 가능</td></tr>
      <tr><td>Zuckerberg / Jensen</td><td>조직적 감속 부정</td></tr>
    </table>
    <div class="note">투자로 번역할 것은 멸종 10%가 아니라 규제화 → 개발 속도 → 그래도 추론 수요.</div>
  </div>
</div>

<div class="card">
  <h2>6. 하이닉스–인텔 — Ohio는 탐색, Base Die는 별축</h2>
  <p><span class="tag f">사실</span>Reuters 9/16: 미국 첫 메모리 생산 탐색. ①Ohio 일부 임차 ②인텔+대형 CSP JV. 하이닉스 “결정 없다”, 인텔 “추측”. 산자부: 국가핵심기술이면 심사. 제품 종류는 Reuters도 못 확인.</p>
  <table>
    <tr><th>시나리오</th><th>하는 일</th><th>신규 수요</th><th>지금</th></tr>
    <tr><td>A. Base Die</td><td>로직 Base Die</td><td>선단 로직 장비</td><td>업계 검토. Ohio와 별개</td></tr>
    <tr><td>B. DRAM 전공정</td><td>하이닉스 웨이퍼</td><td>전공정 장비 대규모</td><td>파급 최대. 미확정</td></tr>
    <tr><td>C. HBM</td><td>DRAM→HBM</td><td>DRAM+후공정</td><td>미확정</td></tr>
    <tr><td>D. 패키징</td><td>HBM 패키징</td><td>본딩·검사</td><td>인디애나가 이미 이 축</td></tr>
  </table>
  <div class="flow">
    <span class="chip">한국 DRAM</span><span class="arrow">→</span>
    <span class="chip">Ohio 전공정?</span><span class="arrow">→</span>
    <span class="chip">Indiana HBM</span><span class="arrow">→</span>
    <span class="chip">Intel Base Die?</span>
  </div>
  <div class="risk">오늘 뉴스만으로 소부장을 바로 연결하지 말 것. Base Die → EMIB → Ohio 계약을 단계로 본다. HBM4는 TSMC Base Die, HBM4E는 TSMC+Intel 가능성. ‘삼성 유리’는 Base Die 가치가 컨트롤러/IP로 갈 수 있어 ④⑤가 약하다.</div>
  <p>HBM 단수 ↓ ≠ 수요 ↓. 대역폭은 유지·상향, 용량은 계층화(DDR/SOCAMM/CXL/SSD). 8단 옵션은 확인, NVIDIA 12→8 전면 전환은 관측.</p>
</div>

<div class="cols">
  <div class="card">
    <h2>7. 데이터센터 전력 TAM</h2>
    {img("02_dc_power_gap.png", "데이터센터 전력 수요와 그리드 갭")}
    {img("03_ai_server_share.png", "AI 서버 전력 비중")}
    <p><span class="tag f">사실</span>TrendForce 9/16. 2026 161GW(+31%), AI 서버 33.4%. 2025까지 그리드 수용, 2026부터 어긋남, 2028 이후 확대. 2030 수요 490.7 vs 그리드 222.6.</p>
    <div class="note">268GW는 종이 갭. 현장발전(BTM)은 분모에 없다. 반대로 계통·송배전 지연은 실제 부족을 만든다. 미국 갭 170GW+.</div>
  </div>
  <div class="card">
    <h2>AEMA — 유연 부하, 대체 아님</h2>
    <p><span class="tag f">사실</span>9/16 NVIDIA·Google·Emerald AI 출범. Anthropic, National Grid, AES, RWE, Constellation, NRG 등 합류.</p>
    <div class="flow">
      <span class="chip">항상 500MW</span><span class="arrow">→</span>
      <span class="chip">부족 시 350–400</span><span class="arrow">→</span>
      <span class="chip">접속 단축</span>
    </div>
    <p>100GW는 AEMA/NVIDIA 주장(유틸리티 1,281GW의 약 7.8%). Emerald 25%/40% 실증은 코멘트. 공식 블로그에는 그 숫자가 없다.</p>
    <div class="blue">NVIDIA가 GPU에서 AI Factory + 전력 운영 플랫폼으로 영역을 넓힌다. DC가 늘면 절대 전력·변압기 수요는 같이 는다. AEMA는 병목을 깎는다.</div>
    <h3>리드타임 — 병목은 GPU가 아님</h3>
    <table>
      <tr><th>부품</th><th>상태</th><th>지금 / 균형</th></tr>
      <tr><td>ABF</td><td>Very Tight</td><td>48–56주 / 12주</td></tr>
      <tr><td>HDD</td><td>Very Tight</td><td>50주 / 16주</td></tr>
      <tr><td>DRAM</td><td>Very Tight</td><td>20주 / 8주</td></tr>
      <tr><td>MLCC</td><td>Tight</td><td>30주 / 12주</td></tr>
      <tr><td>GPU</td><td>Balanced</td><td>20–30주 / 동일</td></tr>
    </table>
  </div>
</div>

<div class="card">
  <h2>8. 개별 · 포트</h2>
  <div class="cols">
    <div>
      <ul>
        <li><b>삼성</b> Taylor Tesla AI 칩 시제품. cHBM Base Die 2-track.</li>
        <li><b>두산</b> 3년 7,551억 고급 CCL. 가동률 100%+.</li>
        <li><b>대덕전자</b> Tesla·Marvell·Renesas LTA. 선수금 &gt; 8,000억 투자라는 전언. 기판 LTA는 Take or Pay보다 약함.</li>
        <li><b>하나마이크론</b> 베트남 4Q26, 비메모리 확대. P/E 10배 이하.</li>
        <li><b>마이크론</b> 512GB DDR5 RDIMM, 27H2. 실질 신규 capa 2028 이후. FY27 캡엑스 $450억+.</li>
        <li><b>조선 3사</b> OP +30%, 시총 −39%, 12M P/E 14배 미만. 엔진·FDC·함정이 수주로 확인돼야 리레이팅.</li>
      </ul>
    </div>
    <div>
      <div class="blue">바벨 예: AI 40–50 / Non-AI 30 / 현금성 20–30. 7월 말 바닥은 지났다. 6,000 쌍바닥은 새 악재가 필요하다.</div>
      <p>다음 숫자: <b>10/1 마이크론</b>부터 실적 시즌. Anthropic IPO 10–11월은 수급. 중간선거 11/3. Blue Wave ≠ 전국 DC 중단.</p>
      <p>원/달러 1,300원대 초반이 바닥이었을 가능성. 4Q 대미투자 달러 수요. 백화점 외인. 원화 강세 배팅은 재검토.</p>
      <p>올릭스: 오버행 해소 + ALK7(OLX501A). 4Q 경쟁사 데이터가 타깃 유효성. 오버행 = 주가 상승은 신한 전망.</p>
    </div>
  </div>
</div>

<div class="hero">
<b>클로징.</b> 주식은 적응의 동물이다. 예상된 인상·예상된 발언이면 심리는 ‘27년 기다릴 수 있다’로 간다.
그 사이 AI 수요는 학습 각도 논쟁과 따로 움직인다. 가을 확인 포인트는 셋.
<b>DevDay 에이전트 깔림 · Ohio/Base Die 계약 · 전력을 그리드+BTM+유연부하로 메우는 속도.</b>
</div>
<footer>원문 퀵코멘트(9/16 23:37–9/17 17:56)와 첨부 PDF를 주제별로 재구성. 종가·SEP·공식 페이지로 숫자를 고침.</footer>
</div>
</body>
</html>
"""


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    html = build()
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
