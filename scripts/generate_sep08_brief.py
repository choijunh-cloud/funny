#!/usr/bin/env python3
"""9월 8일 Quick 코멘트 + 첨부 PDF 통합 브리프 (HTML/MD)."""

from __future__ import annotations

from pathlib import Path

import sep08_data as D

LECTURES = Path("/workspace/lectures")
REPORTS = Path("/workspace/reports")
LECTURES.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

HTML_NAME = "9월 8일 Quick 코멘트 분석.html"
MD_NAME = "9월 8일 Quick 코멘트 분석.md"
REPORT_HTML = REPORTS / "2026-09-08-quick-comment-brief.html"
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
h1 { color: var(--navy); font-size: 32px; line-height: 1.25; margin: 6px 0 8px; }
.sub { color: var(--muted); margin: 0 0 18px; }
.hero { background: var(--navy); color: #fff; border-radius: 16px; padding: 22px 24px; margin-bottom: 18px; }
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
.flow { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 10px 0 12px; }
.flow span { background: var(--navy); color: #fff; padding: 6px 10px; border-radius: 999px; font-size: 12.5px; font-weight: 700; }
.flow i { color: var(--gold); font-style: normal; font-weight: 800; }
table { width: 100%; border-collapse: collapse; font-size: 13.4px; margin: 8px 0 12px; }
th { background: var(--navy); color: #fff; padding: 8px 10px; text-align: left; }
td { padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
tr:nth-child(even) td { background: #f7f9fc; }
.neg { color: var(--red); font-weight: 700; }
.pos { color: var(--green); font-weight: 700; }
.tag { display: inline-block; font-size: 11px; font-weight: 800; padding: 2px 7px; border-radius: 999px; margin-right: 4px; }
.tag.ok { background: var(--green-bg); color: var(--green); }
.tag.est { background: var(--amber-bg); color: var(--amber); }
.tag.cm { background: var(--blue-bg); color: var(--navy2); }
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
  h1 { font-size: 26px; }
}
"""


def html() -> str:
    c = CHART
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>9월 8일 Quick 코멘트 분석</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="kicker">2026. 9. 8.  ·  Quick 코멘트 + 첨부 10개 PDF 통합</div>
  <h1>9월 8일 분석 — 메모리 선점이 모바일까지 왔다</h1>
  <p class="sub">기존 테제(경기 Good · 메모리 Strong · 밸류 Attractive)는 유지. 오늘 추가된 것은 HBM SCA가 모바일 NAND/LPDDR로 확장됐다는 점, Arm이 Physical AI 표준을 가져가려 한다는 점, 9/10 수급은 펀더멘탈이 아니라는 점이다.</p>
  <nav>
    <a href="#top">한 장</a>
    <a href="#apple">애플 NAND</a>
    <a href="#dram">DRAM 2Q</a>
    <a href="#val">밸류</a>
    <a href="#astra">Astra·CAPEX</a>
    <a href="#arm">Physical AI</a>
    <a href="#flow">수급</a>
    <a href="#geo">중동·유럽</a>
    <a href="#power">전력</a>
    <a href="#cal">일정</a>
    <a href="#port">포트</a>
  </nav>

  <div class="hero" id="top">
    <h2>오늘 한 장</h2>
    <ol>
      <li><b>좋은 소식의 실체</b> — 애플이 키옥시아와 3~5년 NAND 장기계약을 협상 중이며 가격 상한(Price Cap)을 두지 않을 수 있다. 공식 확인은 아직 없다. 의미는 분명하다. 세계에서 가장 센 바이어가 ‘단가 인하’에서 ‘물량 확보’로 돌아섰다.</li>
      <li><b>숫자로 확인된 슈퍼사이클</b> — TrendForce 2Q26 DRAM 매출 <b>${D.DRAM_2Q26_REVENUE_B}B, QoQ +{D.DRAM_2Q26_QOQ_PCT}%</b>. 3Q 계약가는 +{D.DRAM_3Q26_CONTRACT_QOQ[0]}~{D.DRAM_3Q26_CONTRACT_QOQ[1]}%로 둔화하지만 부족은 유지. 상승률 둔화 ≠ 사이클 종료.</li>
      <li><b>9/10은 기회일 수 있다</b> — KRX 반도체 ETF 캡 20% 재조정으로 하이닉스 약 1.24~1.45조, 삼성 0.20~0.24조 기계적 매도. 자사주는 현재 한도의 약 27%만 쓰고 있다. 펀더멘탈 무관 매도에 하락하면 기회.</li>
      <li><b>체인은 데이터센터 밖으로</b> — Arm Total Design for Physical AI, 80사+. RL0~RL5. 한국은 스트라드비전 확인. 모델→컴퓨팅→메모리→인식→액추에이터→현장.</li>
      <li><b>유가 꼬리</b> — 후티, 사우디 본토 타격, 민간 73명 부상, 아람코 시설 포함. 호르무즈가 이미 막힌 뒤라 홍해 프리미엄이 더 중요하다. 로하니의 종전 국민투표론은 반대편 옵션.</li>
    </ol>
  </div>

  <div class="grid3">
    <div class="card"><h3>DRAM 2Q26</h3><div class="num">${D.DRAM_2Q26_REVENUE_B}B</div><p>QoQ +{D.DRAM_2Q26_QOQ_PCT}%. 삼성 39.4% / 하이닉스 24.9% / 마이크론 23.3%</p></div>
    <div class="card"><h3>아이폰 메모리 BOM</h3><div class="num">{D.IPHONE18_MEM_BOM_PCT}%</div><p>초기 {D.IPHONE18_MEM_BOM_START_PCT}% → 3Q26 {D.IPHONE18_MEM_BOM_PCT}% → 1H27 {D.IPHONE18_MEM_BOM_1H27_PCT}%+. 원가 약 {D.IPHONE18_MEM_COST_MULTIPLE}배</p></div>
    <div class="card"><h3>미국 DC 건설</h3><div class="num">${D.US_DC_JUL26_SAAR_B}B</div><p>7월 SAAR. YoY +{D.US_DC_JUL26_YOY_PCT}%. 2021년 초 이후 +{D.US_DC_SINCE_2021_PCT}%</p></div>
    <div class="card"><h3>하이닉스 27E PER</h3><div class="num">{D.HYNIX_27_PER}배</div><p>9/4 본주 {D.HYNIX_KR_PRICE//10000}만. ADR은 5.5배. 과거 사이클 4~8배</p></div>
    <div class="card"><h3>자사주 여력</h3><div class="num">×3.7</div><p>하이닉스 65만→최대 240.7만주. 삼성 200만→732만주</p></div>
    <div class="card"><h3>9/10 ETF 매도</h3><div class="num">~1.5조</div><p>하이닉스 1.24~1.45조 + 삼성 0.20~0.24조. 종가 동시호가</p></div>
  </div>

  <section id="frame">
    <h2>오늘이 기존 테제에 더하는 것</h2>
    <p>9/4~9/5 첨부의 한 줄은 <b>경기 Good + 메모리 펀더멘탈 Strong + 밸류 Attractive → BUY</b>였다. 미국은 소프트웨어가 금리에 눌리고 메모리·스토리지가 실적으로 이를 이긴 날이었다. 한국 삼전닉스는 더뎠다.</p>
    <p>오늘(9/8)은 그 테제를 뒤집지 않는다. <b>수요 선점이 모바일 완제품까지 내려왔다는 확인</b>을 더한다.</p>
    <div class="flow">
      <span>HBM SCA</span><i>→</i>
      <span>서버 DRAM 부족</span><i>→</i>
      <span>Google DDR4 재활용</span><i>→</i>
      <span>애플 NAND LTA</span><i>→</i>
      <span>LPDDR 장기계약 확산</span>
    </div>
    <div class="callout bull">
      <b>한 줄</b>
      AI가 팹을 선점하니 애플도 가격을 포기하고 물량을 산다. 실리콘 사이클(급등→증설→급락)로만 보면 정점과 지속기간을 짧게 잡을 위험이 있다. 다만 애플 계약은 아직 미확인 보도이고, 3Q 가격 상승률은 이미 둔화 국면이다.
    </div>
  </section>

  <section id="apple">
    <h2>1. 애플 NAND — 구매력 역전</h2>
    <p><span class="tag est">추정·미확인</span> 월가견문·TrendForce·이코노미트리뷴 계열. 애플·키옥시아 공식 부인/확인 없음.</p>
    <ul>
      <li>애플 ↔ 키옥시아, <b>{D.APPLE_NAND_YEARS[0]}~{D.APPLE_NAND_YEARS[1]}년 NAND</b> 장기공급 협상. 고정 가격 상한 미설정 가능성.</li>
      <li>기존 애플: 단기 계약 + 공급사 가격경쟁. 지금은 물량 선점 + 장기 계약.</li>
      <li>배경: AI 데이터센터 고객이 프리미엄을 주고 팹을 먼저 가져갔다.</li>
      <li>다음 후보: 삼성·하이닉스·마이크론의 모바일 D램(LPDDR5X/6). 삼성 전체 캐파의 {D.SAMSUNG_LTA_CAPA_PCT[0]}~{D.SAMSUNG_LTA_CAPA_PCT[1]}%를 장기계약에 배정할 계획이라는 언급이 씨티 컨퍼런스에도 있었다.</li>
      <li>폴더블용 NAND 점유 추정: 하이닉스 약 {D.FOLDABLE_NAND_HYNIX_PCT}%, 삼성 {D.FOLDABLE_NAND_SAMSUNG_PCT}%, 나머지 키옥시아 등.</li>
    </ul>
    <img class="chart" src="{c}/02_iphone_bom.png" alt="아이폰 메모리 BOM 비중"/>
    <p class="cap">256GB 아이폰 18 프로 메모리 원가 전년비 약 {D.IPHONE18_MEM_COST_MULTIPLE}배. 첫 폴더블 ASP ${D.FOLDABLE_ASP_USD[0]:,}~{D.FOLDABLE_ASP_USD[1]:,}, 고용량 ${D.FOLDABLE_HIGH_USD:,}+. 9/9 이벤트에서 수요가 가격을 받치는지가 핵심.</p>
    <div class="callout note">
      <b>투자 해석</b>
      모바일 수요 붕괴가 아니라 <b>모바일 공급 잠식</b>이다. PC·폰 고객의 가격 수용력은 이미 약해 3Q 계약가 상승률은 둔화한다. 동시에 애플 같은 큰손은 가격을 열고라도 물량을 묶는다. 소비자 DRAM이 제일 많이 오르는 이유(공급 축소)와 같은 그림이다.
    </div>
  </section>

  <section id="dram">
    <h2>2. DRAM 2Q26 — 물량보다 가격</h2>
    <p><span class="tag ok">확인</span> TrendForce 2026-09-07. 코멘트의 $154.7B / +59.5%와 일치.</p>
    <img class="chart" src="{c}/01_dram_2q26.png" alt="DRAM 벤더 2Q26 매출"/>
    <table>
      <tr><th>회사</th><th>2Q26 매출</th><th>점유</th><th>QoQ</th><th>메모</th></tr>
      <tr><td>삼성전자</td><td class="pos">$60.98B</td><td>39.4%</td><td>+63.4%</td><td>점유 확대. HBM 21→33%(첨부)</td></tr>
      <tr><td>SK하이닉스</td><td>$38.59B</td><td>24.9%</td><td>+37.9%</td><td>점유 28.8→24.9. HBM 1위 50%</td></tr>
      <tr><td>Micron</td><td>$36.00B</td><td>23.3%</td><td>+65.5%</td><td>서버 DRAM 믹스</td></tr>
      <tr><td>CXMT</td><td>$14.62B</td><td>9.5%</td><td>+99.3%</td><td>중국 로컬</td></tr>
      <tr><td>Nanya</td><td>$2.61B</td><td>1.7%</td><td>+68.3%</td><td>레거시 가격</td></tr>
    </table>
    <h3>3Q26 — 둔화이지 반전이 아님</h3>
    <ul>
      <li>컨벤셔널 DRAM 계약가 <b>+{D.DRAM_3Q26_CONTRACT_QOQ[0]}~{D.DRAM_3Q26_CONTRACT_QOQ[1]}% QoQ</b>. NAND는 별도 서베이에서 +10~15%.</li>
      <li>고용량 RDIMM → 저용량 이동. PC·폰의 추가 인상 수용력 약화.</li>
      <li>소비자 DRAM은 공급 축소로 가장 높은 상승률.</li>
      <li>2026~27 Top 3는 선단 전환 중심. 비트 증가는 수요를 다 못 따라감.</li>
    </ul>
    <div class="callout">
      <b>Inference ≠ 곧 HBM</b>
      Prefill/Decode가 다르다. 앞으로는 HBM + DDR5/CXL + NAND/SSD로 계층이 갈린다. Agent State는 2026 160GB → 2028 1TB로 늘어 HBM(192→576GB)보다 빠르다. 병목은 대역폭보다 <b>어디에 저장하느냐</b>.
    </div>
  </section>

  <section id="val">
    <h2>3. 밸류 — 싼가, 피크인가</h2>
    <p><span class="tag cm">9/4 종가</span> 오늘 종가가 아니다. 방향 비교용.</p>
    <img class="chart" src="{c}/06_memory_per.png" alt="메모리 forward PER"/>
    <table>
      <tr><th>종목</th><th>가격 (9/4)</th><th>26E PER</th><th>27E PER</th><th>비고</th></tr>
      <tr><td>마이크론</td><td>${D.MU_PRICE}</td><td>Fwd 8.1</td><td>{D.MU_CY27_PER} (EPS {D.MU_CY27_EPS})</td><td>기준선</td></tr>
      <tr><td>샌디스크</td><td>${D.SNDK_PRICE}</td><td>—</td><td>{D.SNDK_FY27_PER} (EPS {D.SNDK_FY27_EPS})</td><td>7월말 후 +43%</td></tr>
      <tr><td>하이닉스 ADR</td><td>177 / 238만 환산</td><td>{D.HYNIX_ADR_PER_26}</td><td>{D.HYNIX_ADR_PER_27}</td><td>마이크론 대비 −19% (과거 −20~−50)</td></tr>
      <tr><td>하이닉스 본주</td><td>{D.HYNIX_KR_PRICE//10000}만</td><td>{D.HYNIX_26_PER}</td><td>{D.HYNIX_27_PER}</td><td>ADR 대비 {D.HYNIX_ADR_PREMIUM_PCT}% 프리미엄</td></tr>
      <tr><td>삼성전자</td><td>{D.SAMSUNG_KR_PRICE//10000}만</td><td>{D.SAMSUNG_26_PER}</td><td>{D.SAMSUNG_27_PER}</td><td>같은 3.8배</td></tr>
      <tr><td>WD / STX</td><td>$467 / $849</td><td>—</td><td>약 26배</td><td>낸드/HDD는 다른 배수</td></tr>
    </table>
    <p>ADR 프리미엄 30%면 본주 약 183만, 20%면 약 198만. 원화가 10% 더 세지면 삼전닉스 약 <b>{D.WON_PLUS_10_EQUITY_HIT_PCT}%</b> 하락 요인. 국민연금 환헷지 중단(로이터)은 그 원화 강세의 다른 얼굴이다.</p>
    <div class="callout note">
      <b>왜 싸 보여도 잘 안 오르나</b>
      시장은 2027 이익은 보지만 2028~30을 피크로 의심한다. SCA Floor는 하방을 막아주지만, “높은 이익이 유지된다”와 “급락만 안 한다”는 다른 말이다. Stress: GPM −20%p → EPS 약 1/3 → PER 6배대 → 8~9배. 과거처럼 12~16배로 가는 경로는 SCA가 약화한다.
    </div>
    <p>보수 시나리오(26년 이익이 27년에 그대로, PER 6~7배): 하이닉스 210만~245만, 삼성 28.9만~33.7만. 첨부 27년 컨센은 하이닉스 OP 392조 / EPS 436K, 삼성 OP 543조 / EPS 66.4K — 낙관 숫자를 목표가에 그대로 넣지 말라는 뜻으로 읽는다.</p>
  </section>

  <section id="astra">
    <h2>4. Astra — 토큰이 아니라 업무량</h2>
    <p><span class="tag ok">벤치 일부 확인</span> Computer Use 65.7→72.6, AutomationBench 18.1→41.4. 아래 4.2배는 <span class="tag est">가정</span>.</p>
    <img class="chart" src="{c}/05_astra_paradox.png" alt="Astra inference 역설"/>
    <p>Astra는 Sol보다 토큰을 덜 쓴다(일반 −10%, 코딩 에이전트 특정 조건 약 1/3). 토큰 단가는 약 2.5배. 그런데 Agent는 검색→클릭→실행→검증→수정을 반복한다. OpenAI 연구자 사용량: 8월 중순 중간 사용자 하루 $600+, 상위 10% $7,000+.</p>
    <table>
      <tr><th>가정</th><th>계산</th><th>결과</th></tr>
      <tr><td>업무당 토큰 −30%, 업무량 ×3</td><td>0.7 × 3</td><td class="pos">1인 inference ×2.1</td></tr>
      <tr><td>사용자 5억→10억</td><td>2.1 × 2</td><td class="pos">전체 ×4.2</td></tr>
      <tr><td>성공률 80% 8연속 vs 90%</td><td>0.8⁸ vs 0.9⁸</td><td>17% vs 43%</td></tr>
      <tr><td>Astra 예시 원가</td><td>In 2M×$5 + Out 1M×$25</td><td>$35 / task</td></tr>
    </table>
    <p>경쟁 지표는 $/1M tokens가 아니라 <b>$ / 성공한 업무</b>. 안전 모니터링(모든 tool-using inference에 misalignment monitor)은 토큰 효율을 깎아도 데이터센터 일을 늘린다. 파초츠키의 속도조절 + 올트먼 동의는 “인프라 축소”가 아니다. 통제 가능한 Agent 경쟁이다.</p>
    <div class="flow">
      <span>Training</span><i>→</i>
      <span>Reasoning</span><i>→</i>
      <span>Agent</span><i>→</i>
      <span>Autonomous 24h</span>
    </div>
    <p>CAPEX의 성격이 “모델 학습용 DC”에서 “AI 노동력 공급용 DC”로 바뀐다. 회수 쪽 실물: Azure FY26 4Q ${D.AZURE_FY26_Q4_B}B(+{D.AZURE_FY26_Q4_YOY}%), 연간 ${D.AZURE_FY26_B}B. 선행지표는 MFP가 아니라 그 앞단의 <b>소프트웨어 에이전트·업무 프로세스 변화</b>. 1995~2000 미국 노동생산성 1.5%→2.5~2.7%, MFP 0.4%→1.3%는 팩트. 다만 투자 직후가 아니라 수년 시차. 지금은 PC를 까는 단계일 수 있다.</p>
    <div class="callout bear">
      <b>부채 숫자 가드</b>
      “2030년 GDP 대비 기업부채 +12.5%p”는 관측이 아니라 회사채+미개시 리스+구매약정을 부채로 환산한 스트레스. 구매약정 ≠ 부채. NVIDIA 계약상 약정 $366B(공급 $279B)를 전부 부채로 보면 안 된다. 미개시 리스는 개시 때 ROU/리스부채로 올라온다. 금리는 “안 부담”이 아니라 <b>금리 × 부채 × 투자규모</b>. 시장이 보는 임계는 예: 10Y 5%, 30Y 6%(PT) / 코멘트 일부는 30Y 10%까지 언급.
    </div>
  </section>

  <section id="arm">
    <h2>5. Arm Physical AI — 표준을 가져가려 한다</h2>
    <p><span class="tag ok">확인</span> Arm Newsroom / 닛케이 / 스트라드비전 PR 9/7~9/8.</p>
    <img class="chart" src="{c}/07_physical_ai_chain.png" alt="Physical AI 밸류체인"/>
    <ul>
      <li>Arm Total Design for Physical AI. 80사+ — AWS, Hugging Face, NXP, Siemens, Unitree, Qwen, QNX, ECARX, PlusAI.</li>
      <li>Robotics Capability Framework, RL0~RL5. RL5 = 스스로 최적화하며 능력을 올리는 단계. 자동차 SAE의 로봇판.</li>
      <li>TAM 2026 ${D.ARM_PAI_TAM_26_B}B → 2030년대 ${D.ARM_PAI_TAM_30S_B}B+ (약 8배). 회계연도 기준 코멘트와 일치.</li>
      <li>한국 참가 <b>확인 = 스트라드비전</b> (카메라→인식→판단). 삼성전자는 80사 명단에 확인되지 않음. 같은 날 Neoverse CSS-N4 공정 선택지로 삼성 SF2·SF2P가 언급.</li>
    </ul>
    <h3>국내 연결 — 로보티즈 · SDS · PSK</h3>
    <table>
      <tr><th>이름</th><th>역할</th><th>숫자</th><th>체크</th></tr>
      <tr><td>스트라드비전</td><td>Perception</td><td>Arm 연합 합류</td><td>양산 비전 → 로봇 확장</td></tr>
      <tr><td>로보티즈</td><td>액추에이터</td><td>22만→50만대, 매출 390→500→1,000억+</td><td>우즈벡 CAPA, Foxconn, Figure. 2030 $1bn은 목표</td></tr>
      <tr><td>삼성SDS</td><td>RX 통합</td><td>RX ART 2026</td><td>실적 있는 중장기. DC 로봇</td></tr>
      <tr><td>PSK홀딩스</td><td>어드밴스드 패키징 리플로우</td><td>26E 2,792억/+34%, OP 1,088억. 27E 4,014억</td><td>3Q 이연 120억, TSMC/HBM, Intel EMIB-T. TP 19.5만≈27 PER 15배</td></tr>
    </table>
    <p>PIMCO Sharef 프레임과도 맞다. 미국 빅테크 밸류·부채보다 아시아 ‘삽을 파는 기업’ — 삼성, 하이닉스, TSMC.</p>
  </section>

  <section id="flow">
    <h2>6. 수급 — 9/10은 기계적, 자사주는 가변</h2>
    <img class="chart" src="{c}/04_etf_rebal.png" alt="ETF 리밸런싱"/>
    <p>KRX 섹터 단일종목 캡 20%. 추종 ETF 약 {D.KRX_SEMI_ETF_AUM_T}조(보도에 따라 7.67조). 하이닉스 비중 약 {D.HYNIX_WEIGHT_PCT}%, 삼성 약 {D.SAMSUNG_WEIGHT_PCT}%. 집행은 9/10 만기일 종가 동시호가, 지수 적용 9/11. 3분기 배당 추정 21~23조가 같은 날 겹친다.</p>
    <p>유입: 한미반도체 ~3,000억, 주성 1,800억, 테스 1,400억, 리노·이오텍. 2차전지 TOP10은 삼성SDI ~638억 매도. 바이오는 알테오젠 1,060억 매도 / 한미약품 860억 유입.</p>
    <img class="chart" src="{c}/03_buyback_headroom.png" alt="자사주 한도"/>
    <table>
      <tr><th></th><th>총 취득 예정</th><th>현재 신청/일</th><th>1일 한도</th><th>여력</th></tr>
      <tr><td>SK하이닉스</td><td>{D.HYNIX_BUYBACK_TOTAL_M}만주</td><td>{D.HYNIX_BUYBACK_DAILY_NOW_M}만주</td><td>{D.HYNIX_BUYBACK_DAILY_MAX_M}만주</td><td class="pos">약 3.7배</td></tr>
      <tr><td>삼성전자</td><td>{D.SAMSUNG_BUYBACK_TOTAL_M}만주</td><td>{D.SAMSUNG_BUYBACK_DAILY_NOW_M}만주</td><td>{D.SAMSUNG_BUYBACK_DAILY_MAX_M:.1f}만주</td><td class="pos">약 3.66배</td></tr>
    </table>
    <p>9/7 자사주 매입 대금 하이닉스 약 1.1조, 삼성 0.5조. 같은 날 거래대금 10.4조 / 7.9조. 현재 65만·200만은 법적 최대가 아니라 거래소에 낸 <b>당일 주문수량</b>이다. 올릴 수는 있고, 한도는 못 넘는다. 언제 올릴지는 주가·전략.</p>
    <div class="callout bull">
      <b>리밸런싱 하락 = 기회일 수 있음</b>
      금액이 작지는 않다. 그러나 펀더멘탈과 무관하다. 장 막판 변동성만 보면 된다.
    </div>
  </section>

  <section id="geo">
    <h2>7. 중동 · 유럽 — 유가 꼬리, 정치는 분별</h2>
    <p><span class="tag ok">확인</span> CNN/연합 계열. 후티 미사일·드론, 아바 공항, 킹 칼리드 공군기지, 아람코 아바 벌크플랜트·자잔 정유(~400kb/d).</p>
    <ul>
      <li>민간 등 {D.HOUTHI_INJURED}명 부상. 사우디 교도소 공습(9/7) 보복 성격.</li>
      <li>바브엘만데브 장악 공세, 사상 수백. 호르무즈 봉쇄 이후 홍해 가중.</li>
      <li>로하니: “국민 다수가 원하면 명예롭게 종전.” 사실상 국민투표론. 파르스 “위험한 발언.” 정책이 아니라 온건파 메시지.</li>
      <li>유럽 월요 마감(미국 휴장): STOXX600 보합, DAX −0.2%, ASML +2.3%, Infineon +6.9%, WTI $93대에 에너지 강세. ECB는 에너지 물가 vs 경기.</li>
      <li>독일 대안당(AfD) 대승 → KOSPI 전체 악재로 단선 연결하지 말 것. 유럽 경기민감 − / 방산·인프라 + / 한국 방산 중기 +.</li>
    </ul>
    <div class="callout bear">
      <b>임계</b>
      PT 기준 유가 $120이면 종전/휴전 $80 이하가 반대 시나리오. 오늘 뉴스는 리스크 프리미엄이지 공급 쇼크 확정이 아니다. 자잔 피해 규모는 아직 진행형.
    </div>
  </section>

  <section id="power">
    <h2>8. 전력 · 대미투자 · DC 입지</h2>
    <img class="chart" src="{c}/08_us_dc.png" alt="미국 DC 건설"/>
    <p>7월 미국 DC 건설 SAAR <b>${D.US_DC_JUL26_SAAR_B}B</b>, YoY +{D.US_DC_JUL26_YOY_PCT}%, MoM +{D.US_DC_JUL26_MOM_PCT}%. 2021년 초 이후 +{D.US_DC_SINCE_2021_PCT}%. 코멘트: 2023년 말 이후 +$510B, 같은 기간 기타 민간건설 −$1,200B. (건설비이지 서버·GPU가 아님.)</p>
    <p>IIF: 소형 콜로는 대도시, 하이퍼스케일러 캠퍼스는 전력 싼 저밀도. 병목은 GPU가 아니라 <b>POWER</b>. 연방 Build Fast vs 주 Make Them Pay → CAPEX는 유지, 비용 부담 방식이 바뀐다.</p>
    <h3>엔시날 6.3GW — 확정과 검토를 가르기</h3>
    <ul>
      <li>한미전략투자 운영위 9/7 1호 의결 보도. 총 {D.ENCINAL_USD_B}B(약 30조). 1단계 단순주기 {D.ENCINAL_PHASE1_GW}GW → 복합 {D.ENCINAL_CCGT_GW}GW.</li>
      <li>후보: 두산에너빌리티(가스터빈), 삼성물산·현대건설·DL이앤씨(EPC). EPC 최종 확정으로 보기 어려움.</li>
      <li>원전 8기는 <b>별도 검토</b>. 9/18 전후 정식 발표 가능성.</li>
      <li>국내 DC: GS건설, DL이앤씨(하반기 국내 DC 2조 수주 기대는 기대).</li>
    </ul>
    <p>한 줄: 단기 엔시날 → 두산·대형 EPC / 중기 원전 8기(미확정) → 두산·현대·삼성물산 / 국내 AI 인프라 GS ≥ DL.</p>
    <h3>주변 실물 — CCL · TI · CoreWeave · DeepSeek</h3>
    <table>
      <tr><th>항목</th><th>숫자</th><th>읽기</th></tr>
      <tr><td>대만 CCL 8월</td><td>ITEQ 50.4억 +98% / TUC 59.1억 +133% / EMC 201.5억 +130% (TWD)</td><td>가격×고사양×물량. 이수페타시스·두산 CCL</td></tr>
      <tr><td>TI</td><td>올해 3번째 전 포트폴리오 인상</td><td>아날로그·PMIC도 AI 서버 수혜</td></tr>
      <tr><td>CoreWeave</td><td>2Q $2.6B, backlog $104B+, 전력 1.5 vs 계약 3.7GW. 조정OP $128M &lt; 이자 $640M</td><td>Speculative Buy. Top3 72%. EV/S 봐야 함</td></tr>
      <tr><td>DeepSeek→Huawei 950DT</td><td>16만장 × $16,000 = $2.56B, 납기 1년+</td><td>확정 수주라기보다 잠재수요. Nvidia 학습 / Huawei 추론 이원화. 메모리 수율이 병목</td></tr>
    </table>
  </section>

  <section id="cal">
    <h2>9. 이번 주 일정과 Hartnett</h2>
    <table>
      <tr><th>날</th><th>이벤트</th><th>왜 보나</th></tr>
      <tr><td>9/9</td><td>Apple 이벤트</td><td>폴더블·가격 인상. 수요가 받치면 모바일 메모리 논리 강화</td></tr>
      <tr><td>9/10</td><td>Oracle 실적 · Nvidia GS 콘퍼런스 · PPI · 선옵 만기 · ETF 리밸런싱</td><td>하루가 과밀. OCI/CAPEX + 젠슨 발언 + 물가 + 수급</td></tr>
      <tr><td>9/11</td><td>CPI (Core 예상 2.5%) · 지수 적용</td><td>고용 강 + 물가 재상승이면 인하 기대 후퇴</td></tr>
      <tr><td>9/18 전후</td><td>엔시날 정식 발표 가능성</td><td>의결 ≠ 계약. 원전 8기와 분리</td></tr>
    </table>
    <div class="callout note">
      <b>Hartnett “민주당 스윕 → 미증시 −10%+ → AI 거품”</b>
      논리 시나리오로는 가능. 역사적 법칙은 아님. 중간선거 후 6개월 S&amp;P 평균 +14.1%(블랙록). 2018·2022 하락은 선거보다 금리·인플레. −10%는 기본값이 아니라 <b>10Y 5% + CAPEX 둔화 + 수익화 실망 + 스윕</b>이 겹칠 때. 스윕 단독은 −3~−7% 밸류 조정 정도로 보는 편이 맞다. 그리고 스윕이 반드시 금리 하락도 아니다(재정적자).
    </div>
  </section>

  <section id="port">
    <h2>10. 포트 · 임계 · 규칙</h2>
    <p>첨부 PT 그대로: AI 밸류체인 40~50% / Non-AI 20~30% / 현금 30%. 종결욕구를 억제하고, 수치와 내러티브를 같이 본다.</p>
    <table>
      <tr><th>축</th><th>임계</th></tr>
      <tr><td>수급</td><td>2배 ETF, 공매도, 9/10 리밸런싱, 머니 역무브</td></tr>
      <tr><td>매크로</td><td>10Y 5%, 30Y ~6%(PT). 기준금리 2연속 또는 +50bp. 유가 $120</td></tr>
      <tr><td>펀더멘탈</td><td>P&amp;Q, 하이퍼스케일러 CAPEX 증가율, SCA/LTA 유지</td></tr>
      <tr><td>심리</td><td>모르는 뉴스에 FOMO와 FEAR가 동시에</td></tr>
    </table>
    <div class="callout">
      <b>오늘 이후 우선순위</b>
      ① 9/9 애플이 가격을 올려도 수요 이야기를 할 수 있는가<br/>
      ② 9/10 오라클 OCI + 젠슨이 CAPEX를 깎지 않는가<br/>
      ③ 같은 날 삼전닉스 종가 급락을 펀더멘탈로 착각하지 말 것<br/>
      ④ 후티·자잔 피해가 원유 공급 숫자로 바뀌는가<br/>
      ⑤ 자사주 일일 수량이 실제로 상향되는가
    </div>
    <p class="footer">매수·매도 권유가 아닙니다. 애플 NAND LTA, 폴더블 ASP, BOM 34%, 엔시날 EPC, 원전 8기, DeepSeek $2.56B는 보도·추정입니다. DRAM $154.73B, Arm 80사, 후티 73명, DC $75.2B는 교차확인했습니다. 밸류는 9/4 종가입니다.</p>
  </section>
</div>
</body>
</html>
"""


def md() -> str:
    return f"""# 9월 8일 Quick 코멘트 분석

> 2026-09-08. Quick 코멘트(06:18~15:09) + 첨부 PDF 10개. HTML: `reports/2026-09-08-quick-comment-brief.html`

매수·매도 권유가 아닙니다.

## 한 줄

애플이 가격 상한 없는 3~5년 NAND를 논의한다는 보도는, AI가 팹을 선점하자 세계 최강 바이어마저 물량으로 돌아섰다는 뜻이다. 2Q DRAM ${D.DRAM_2Q26_REVENUE_B}B(+{D.DRAM_2Q26_QOQ_PCT}%)가 그 실물이다. 9/10 ETF 매도(하이닉스 1.24~1.45조)는 펀더멘탈이 아니다.

## 오늘이 더하는 것

기존 테제(9/4~5): **경기 Good + 메모리 Strong + 밸류 Attractive**.  
오늘: HBM SCA → 서버 DRAM 부족 → Google DDR4 재활용 → **애플 NAND LTA** → LPDDR 장기계약 확산.

## 1. 애플 NAND (미확인 보도)

- 키옥시아와 {D.APPLE_NAND_YEARS[0]}~{D.APPLE_NAND_YEARS[1]}년, Price Cap 없을 수 있음. 공식 확인 없음.
- 아이폰 18 프로 256GB 메모리 원가 약 {D.IPHONE18_MEM_COST_MULTIPLE}배, BOM {D.IPHONE18_MEM_BOM_START_PCT}% → {D.IPHONE18_MEM_BOM_PCT}% → 1H27 {D.IPHONE18_MEM_BOM_1H27_PCT}%+.
- 폴더블 ASP ${D.FOLDABLE_ASP_USD[0]:,}~{D.FOLDABLE_ASP_USD[1]:,}, 고용량 ${D.FOLDABLE_HIGH_USD:,}+.
- 삼성 캐파 {D.SAMSUNG_LTA_CAPA_PCT[0]}~{D.SAMSUNG_LTA_CAPA_PCT[1]}% LTA. 폴더블 NAND 하이닉스 {D.FOLDABLE_NAND_HYNIX_PCT}% / 삼성 {D.FOLDABLE_NAND_SAMSUNG_PCT}%.
- 9/9 이벤트: 가격을 올려도 수요가 받치는가.

![아이폰 BOM]({CHART}/02_iphone_bom.png)

## 2. DRAM 2Q26 (TrendForce 확인)

| 회사 | 매출 | 점유 | QoQ |
|---|---:|---:|---:|
| 삼성전자 | $60.98B | 39.4% | +63.4% |
| SK하이닉스 | $38.59B | 24.9% | +37.9% |
| Micron | $36.00B | 23.3% | +65.5% |
| CXMT | $14.62B | 9.5% | +99.3% |

3Q 계약가 +{D.DRAM_3Q26_CONTRACT_QOQ[0]}~{D.DRAM_3Q26_CONTRACT_QOQ[1]}%. 상승률 둔화 ≠ 종료. 소비자 DRAM이 제일 많이 오른다(공급 축소). Inference를 HBM과 등치하지 말 것.

![DRAM]({CHART}/01_dram_2q26.png)

## 3. 밸류 (9/4)

하이닉스 본주 {D.HYNIX_27_PER}배 / 삼성 {D.SAMSUNG_27_PER}배 / 마이크론 {D.MU_CY27_PER}배 / ADR 프리미엄 {D.HYNIX_ADR_PREMIUM_PCT}%. 원화 +10% ≈ 주식 −{D.WON_PLUS_10_EQUITY_HIT_PCT}%. 국민연금 환헷지 중단은 그 배경. 시장 질문: 2027 EPS가 피크인가.

![PER]({CHART}/06_memory_per.png)

## 4. Astra · CAPEX · 부채

토큰 효율 −30% × 업무 ×3 = 1인 ×2.1. 사용자 ×2 → 전체 ×4.2 (**가정**). 지표는 Cost per Task Successfully Completed. 80%⁸=17% vs 90%⁸=43%. 안전 모니터링은 compute를 더 쓴다.

![Astra]({CHART}/05_astra_paradox.png)

+12.5%p 기업부채는 스트레스이지 예상치가 아니다. 구매약정 ≠ 부채. NVIDIA $366B 약정도 부채가 아니다.

Azure FY26 $101.9B, 4Q +43%. 1990년대: 생산성 1.5%→2.5~2.7%, MFP 0.4%→1.3%. 시차 있음. 지금은 PC 설치 단계일 수 있다.

## 5. Physical AI

Arm 80사+, TAM $25B→$200B, RL0~RL5. 한국 확인 = **스트라드비전**. 삼성전자는 명단 미확인, SF2/SF2P는 Neoverse 언급. 로보티즈 액추에이터 22만→50만. SDS RX. PSK 26E 매출 2,792억 OPM 39%, TP 19.5만.

![체인]({CHART}/07_physical_ai_chain.png)

## 6. 수급

9/10 하이닉스 ETF −1.24~1.45조, 삼성 −0.20~0.24조. 한미 +3,000억. 자사주 현재/한도 = 65만/240.7만, 200만/732만. 9/7 매입 1.1조+0.5조, 거래대금 10.4조/7.9조. 65만·200만은 고정 방어가 아니다.

![ETF]({CHART}/04_etf_rebal.png)
![자사주]({CHART}/03_buyback_headroom.png)

## 7. 중동 · 유럽

후티→사우디, 부상 {D.HOUTHI_INJURED}, 아람코 자잔. 로하니 종전 국민투표론(강경파 반발). 유럽 보합, ASML +2.3%, Infineon +6.9%. AfD ≠ KOSPI 전체 악재.

## 8. 전력

DC 건설 7월 ${D.US_DC_JUL26_SAAR_B}B SAAR, YoY +{D.US_DC_JUL26_YOY_PCT}%. 엔시날 {D.ENCINAL_GW}GW / ${D.ENCINAL_USD_B}B, 9/7 의결 보도, 9/18 발표 가능. 원전 8기는 검토. DeepSeek 화웨이 16만장 $2.56B는 잠재수요, 납기 1년+.

![DC]({CHART}/08_us_dc.png)

## 9. 일정

9/9 Apple · 9/10 Oracle + Nvidia GS + PPI + 만기/리밸런싱 · 9/11 CPI · 9/18 엔시날.

Hartnett −10%: 스윕 단독이 아니라 10Y 5%+CAPEX 둔화+수익화 실망이 겹칠 때.

## 10. 규칙

AI 40~50 / Non-AI 20~30 / 현금 30. 임계: 10Y 5%, 유가 $120, CAPEX 증가율. 9/10 종가 급락을 펀더멘탈로 읽지 말 것.
"""


def write_all() -> None:
    html_text = html()
    md_text = md()
    (LECTURES / HTML_NAME).write_text(html_text, encoding="utf-8")
    (LECTURES / MD_NAME).write_text(md_text, encoding="utf-8")
    REPORT_HTML.write_text(html_text, encoding="utf-8")
    readme = Path("/workspace/reports/README.md")
    readme.write_text(
        "# reports\n\n"
        "- `2026-09-08-quick-comment-brief.html` — 9월 8일 Quick 코멘트 + 첨부 PDF 통합.\n"
        "- `charts/` — 브리프에 쓰는 그림.\n",
        encoding="utf-8",
    )
    print("wrote", LECTURES / HTML_NAME)
    print("wrote", LECTURES / MD_NAME)
    print("wrote", REPORT_HTML)


if __name__ == "__main__":
    D.assert_all()
    write_all()
