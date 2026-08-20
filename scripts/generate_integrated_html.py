#!/usr/bin/env python3
"""8/18~20 통합 시각화 보고서 HTML."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import aug19_data as a
import integrated_data as d

OUT = Path("/workspace/reports/2026-08-18-20-통합-시각화보고서.html")

HTML = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>2026.08.18–20 통합 시장 시각화 보고서</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600&display=swap" rel="stylesheet"/>
<style>
:root {{ --navy:#0F2043; --navy2:#1E407C; --gold:#B8943A; --bg:#F3F5F9; --card:#fff; --line:#D5DCE6; --text:#1A1A1A; --muted:#5B6573; --green:#166534; --red:#991B1B; --amber:#7A5C12; --soft:#EEF2F8; }}
* {{ box-sizing:border-box; margin:0; padding:0; }}
body {{ font-family:'Noto Sans KR',sans-serif; background:var(--bg); color:var(--text); line-height:1.65; font-size:15px; }}
.wrap {{ max-width:1200px; margin:0 auto; padding:28px 20px 80px; }}
header.cover {{ background:linear-gradient(135deg,#0F2043,#16325c 50%,#1a1540); color:#fff; border-radius:18px; padding:34px 38px; margin-bottom:20px; }}
.kicker {{ color:#B8943A; font-weight:700; font-size:12px; letter-spacing:.06em; }}
header.cover h1 {{ font-size:26px; font-weight:800; margin:8px 0; line-height:1.3; }}
header.cover p {{ color:#C5D0E0; font-size:14.5px; max-width:820px; }}
.meta {{ margin-top:14px; display:flex; flex-wrap:wrap; gap:7px; }}
.chip {{ font-size:11.5px; padding:4px 10px; border-radius:999px; border:1px solid rgba(255,255,255,.2); }}
.kpi {{ display:grid; grid-template-columns:repeat(6,1fr); gap:8px; margin-bottom:18px; }}
.kpi .c {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:10px 12px; }}
.kpi h3 {{ font-size:10.5px; color:var(--muted); }}
.kpi .v {{ font-family:'IBM Plex Mono',monospace; font-size:17px; font-weight:700; color:var(--navy); }}
.kpi .s {{ font-size:11px; color:var(--muted); }}
nav.toc {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:12px 16px; margin-bottom:24px; display:flex; flex-wrap:wrap; gap:6px 12px; }}
nav.toc a {{ color:var(--navy2); text-decoration:none; font-size:12.5px; font-weight:600; }}
section {{ margin-bottom:34px; scroll-margin-top:12px; }}
section > h2 {{ font-size:19px; color:var(--navy); border-bottom:3px solid var(--navy); padding-bottom:6px; margin-bottom:8px; }}
.lead {{ color:var(--muted); font-size:13.5px; margin-bottom:12px; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
.grid3 {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:14px; padding:14px 16px; }}
.card h3 {{ font-size:13.5px; color:var(--navy2); margin-bottom:8px; }}
.chart {{ position:relative; height:290px; }}
.chart.tall {{ height:340px; }}
.call {{ border-left:4px solid var(--navy); background:var(--soft); padding:11px 13px; border-radius:0 10px 10px 0; margin:10px 0; font-size:13.5px; }}
.call.g {{ border-color:var(--green); background:#E8F5E9; }}
.call.r {{ border-color:var(--red); background:#FDECEA; }}
.call.a {{ border-color:var(--gold); background:#FFF8E7; }}
.call strong {{ display:block; margin-bottom:3px; color:var(--navy); }}
table {{ width:100%; border-collapse:collapse; font-size:12.5px; }}
th {{ background:var(--navy); color:#fff; padding:7px 9px; text-align:left; }}
td {{ padding:7px 9px; border-bottom:1px solid var(--line); }}
tr:nth-child(even) td {{ background:#F7F9FC; }}
.flow {{ text-align:center; font-weight:700; color:var(--navy); margin:8px 0 12px; font-size:13px; }}
.flow span {{ color:var(--gold); }}
.mermaid {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:10px; }}
ul.bul {{ padding-left:18px; }}
ul.bul li {{ margin:3px 0; }}
.src {{ font-size:11.5px; color:var(--muted); margin-top:6px; }}
footer {{ color:var(--muted); font-size:12px; border-top:1px solid var(--line); padding-top:12px; }}
@media (max-width:980px) {{ .kpi,.grid2,.grid3 {{ grid-template-columns:1fr; }} }}
@media print {{ nav.toc {{ display:none; }} .card,section {{ break-inside:avoid; }} }}
</style>
</head>
<body>
<div class="wrap">
<header class="cover">
  <div class="kicker">2026.08.18–20  ·  업로드 워드 11개 통합  ·  시각화 보고서</div>
  <h1>금리와 환율이 할인한 3일,<br/>환원·파운드리·클라우드가 버틴 3일</h1>
  <p>8/18 이란 장기전·엔캐리·실리콘투, 8/19 유가발 금리 쇼크·메모리 NOBUY·하이닉스 환원, 8/20 바이백으로 금리 진정 vs OpenAI·알리바바·울프스피드. 한 권으로 재배열했습니다.</p>
  <div class="meta">
    <span class="chip">10년 4.64% / 30년 5.18%</span>
    <span class="chip">원/달러 1,520→1,420 · SKH EPS −{a.SKH_EPS_FX_HIT:.1f}%</span>
    <span class="chip">하이닉스 40조 + FCF 50%+</span>
    <span class="chip">SOX −2.12% · 마벨 +{a.MRVL_CHG}%</span>
    <span class="chip">공개 자료 기준 · 추천 아님</span>
  </div>
</header>

<div class="kpi">
  <div class="c"><h3>10년물 8/19</h3><div class="v">4.71→4.64</div><div class="s">분기점 4.7 / 5.0</div></div>
  <div class="c"><h3>JGB 10년</h3><div class="v">{d.JGB['10y_now']}%</div><div class="s">3% 경계 · USDJPY {d.USDJPY_NOW}</div></div>
  <div class="c"><h3>코스피 8월 대금</h3><div class="v">25.7조</div><div class="s">5~6월 50조의 반토막</div></div>
  <div class="c"><h3>SKH 환원 하한</h3><div class="v">192.5조</div><div class="s">25+150+210=385 ×50%</div></div>
  <div class="c"><h3>NVDA Q2 컨센</h3><div class="v">${d.NVDA_Q2['cons_rev']:.0f}B</div><div class="s">+{d.NVDA_Q2['cons_yoy']}% · 저자 $93.5B</div></div>
  <div class="c"><h3>BABA Cloud</h3><div class="v">+{d.BABA_CLOUD_YOY}%</div><div class="s">전사 +{d.BABA_REV_YOY}% · EBITA {d.BABA_EBITA_DROP}%</div></div>
</div>

<nav class="toc">
  <a href="#one">0. 한 장</a>
  <a href="#macro">1. 매크로</a>
  <a href="#fx">2. 환율</a>
  <a href="#memory">3. 메모리</a>
  <a href="#return">4. 환원</a>
  <a href="#nm">5. 비메모리</a>
  <a href="#nvda">6. NVDA·OAI</a>
  <a href="#baba">7. BABA·WOLF</a>
  <a href="#unitree">8. 유니트리</a>
  <a href="#sil">9. 실리콘투</a>
  <a href="#close">10. 클로징</a>
</nav>

<section id="one">
  <h2>0. 사흘을 한 장으로</h2>
  <div class="grid3">
    <div class="card"><h3>8/18</h3>이란은 단기전이 아니라 1년 원유 비축·12일 단독작전. JGB 10년 2.945% 30년래 최고, BOJ 9월 80%. 코스피는 7000 회복인데 거래대금은 반토막. 트럼프 한미훈련 축소 = 대북 유화보다 대한 불만 해석. 실리콘투 CVC 3,000억.</div>
    <div class="card"><h3>8/19</h3>핵심 악재는 전쟁이 아니라 금리(30년 5.34→5.285, 10년 4.75→4.708). 하이닉스 40조 소각 + FCF 50%+. 우드·톰슨 NOBUY는 ‘영구 가격결정력 금지’. 삼성 파운드리 +10~15%. 마벨–구글 워런트.</div>
    <div class="card"><h3>8/20</h3>바이백으로 30년 5.18·10년 4.64·달러 −0.8%. 지수는 +인데 SOX −2.12% = OpenAI 성장 둔화. 알리바바 클라우드 +40% vs 이익 압살. 울프스피드 매출 부합·EPS 크게 하회.</div>
  </div>
  <div class="call" style="margin-top:12px"><strong>관통 문장</strong>사흘의 공통분모는 ‘AI 수요가 죽었다’가 아닙니다. <b>할인율(금리·환율)</b>이 가격을 깎고, <b>순환금융·효율화</b>가 내러티브를 흔들고, <b>환원·파운드리·클라우드 CAPEX</b>가 반대편에서 받치는 구조입니다.</div>
</section>

<section id="macro">
  <h2>1. 매크로 — 이란 · 유가 · 엔캐리 · 바이백</h2>
  <p class="lead">원본: 8월 18일(이란·엔캐리·트럼프), 매크로(이란전·유가·엔캐리), 8월 19일 미국장, 8월 20일 미국장.</p>
  <div class="mermaid">
flowchart LR
  A[이란 장기전 준비] --> B[호르무즈·유가]
  B --> C[인플레 우려]
  C --> D[미 10·30년물]
  D --> E[고PER 할인]
  F[JGB 급등] --> G[엔캐리 조건]
  G --> E
  H[재무부 바이백 2배] -.-> D
  </div>
  <div class="grid2" style="margin-top:12px">
    <div class="card"><h3>코스피 거래대금 — 지수는 오고 거래는 안 옴</h3><div class="chart"><canvas id="toChart"></canvas></div>
      <p class="src">8월 일평균 25.7조, 거래량 3.21억주 올해 최저. 5일 외국인 +9.5조 vs 5/7~8/10 −116.7조. 추가 상승의 열쇠는 외국인 지속.</p></div>
    <div class="card"><h3>외국인 수급 스케일</h3><div class="chart"><canvas id="frChart"></canvas></div></div>
  </div>
  <div class="grid2" style="margin-top:12px">
    <div class="card"><h3>일본 금리</h3><div class="chart"><canvas id="jgbChart"></canvas></div></div>
    <div class="card"><h3>2024.8 일별 — 엔화와 지수</h3><div class="chart"><canvas id="crashChart"></canvas></div></div>
  </div>
  <div class="call a"><strong>엔캐리: ‘이미 2024.8’이 아니라 ‘조건이 다시 형성’</strong>위험 5개가 동시에: JGB10 &gt;3% + USD/JPY 급락 + 미 30년 &gt;5.3~5.4% + SOX 급락 + 일본 입찰 부진. 현재 USD/JPY {d.USDJPY_NOW}(157~159 반등)이면 1차 충격은 엔캐리보다 글로벌 금리/밸류. 의심선은 159→155→150 + 닛케이·코스피 동반 붕괴.</div>
  <div class="grid2">
    <div class="card">
      <h3>이란 — 단기 승리가 아닌 소모전</h3>
      <ul class="bul">
        <li>1년치 원유 비축, 최소 12일 외부 지원 없이 작전</li>
        <li>후티·이라크 민병대 ‘저항의 축’ 연계</li>
        <li>이라크·요르단·쿠웨이트·바레인·사우디 미군 시설 공격, 요르단 미군 3명 사망</li>
        <li>경제 악화가 정권의 전쟁 수행력과 국내 지지를 동시에 흔듦</li>
        <li>FT: 확전 시 남동부 유럽 미군 시설·해저 인프라 <em>검토</em> (결정 아님)</li>
      </ul>
    </div>
    <div class="card">
      <h3>모니터 레벨 · 일본의 카드</h3>
      <table>
        <tr><th>변수</th><th>안정</th><th>위험</th></tr>
        <tr><td>브렌트</td><td>$90 전후</td><td>$100+ 악순환</td></tr>
        <tr><td>미 10년</td><td>4.7% 이하</td><td>5.0% 고착</td></tr>
        <tr><td>USD/JPY</td><td>157~159</td><td>155→150 급락</td></tr>
        <tr><td>BOJ</td><td>9월 25bp 선반영</td><td>연속·50bp out-hawk</td></tr>
      </table>
      <p class="src">노무라: 26.9 / 27.1 / 27.4 각 25bp, 최종 1.75%. NISA 개인국채 3.8조엔. 가계 보유 1.8%→5%가 구조적 카드. USD/JPY 동력은 미국 쪽 2년 스프레드.</p>
    </div>
  </div>
  <div class="grid2" style="margin-top:12px">
    <div class="card"><h3>8/19 세션 — 금리 하락 ≠ 반도체 매수</h3><div class="chart"><canvas id="sessChart"></canvas></div></div>
    <div class="card">
      <h3>바이백 = 방어선, 해결책 아님</h3>
      <ul class="bul">
        <li>장기채 $20억→$40억. 30년 5.33→5.18, 10년 4.71→4.64, 달러 −0.8%(3개월 최저)</li>
        <li>S&amp;P +0.21%, 나스닥 +0.16%, 다우 +0.22% — 3일 하락 종료</li>
        <li>SOX −2.12%: OpenAI Q2 $6.7B(+18%), 손실 $9.3B→$12.3B</li>
        <li>구조 3요인 잔존: 재정적자, 인플레, AI 회사채</li>
        <li>7월 FOMC 매파(3명 인상) vs Treasury 방어 → 당장은 Treasury</li>
      </ul>
      <div class="call r"><strong>2024.9 연준 50bp 인하 패턴을 지금 대입하지 말 것</strong>당시엔 실업 4.3% 쇼크 후 9/18 인하. 지금은 미·이란 소강 없이 인하를 가정하기 어렵고, 동결이 주식에 최선으로 남아 있습니다.</div>
    </div>
  </div>
  <div class="call"><strong>트럼프·한미훈련</strong>축소 요구는 대북 유화로 읽히지만, 환구시보는 한국이 대이란 군사행동을 지지하지 않고 대미 투자 1호(반도체)도 아직이라는 불만으로 해석. 산업부는 “대미 전략투자 1호=반도체는 사실과 다르다”.</div>
</section>

<section id="fx">
  <h2>2. 환율 — 국내 수급이 먼저, 이익은 60조 바구니</h2>
  <p class="lead">원본: 환율 전망 및 민감도.</p>
  <div class="flow">법인세·설비 원화수요 <span>→</span> 수출 달러매도 <span>→</span> 헤지 ↑ <span>→</span> 달러-원 하락 <span>→</span> 고환율 잔여매도 <span>→</span> 가속</div>
  <div class="grid2">
    <div class="card"><h3>달러-원 래더</h3><div class="chart"><canvas id="fxL"></canvas></div></div>
    <div class="card"><h3>1,520→1,420 EPS</h3><div class="chart"><canvas id="fxB"></canvas></div></div>
  </div>
  <div class="grid2" style="margin-top:12px">
    <div class="card"><h3>이익 하향 바구니</h3><div class="chart"><canvas id="hit60"></canvas></div></div>
    <div class="card">
      <h3>결론 숫자</h3>
      <ul class="bul">
        <li>삼성 β 0.4 / 하이닉스 β 0.9 (원문 삼성 항목의 ‘하이닉스 +0.4%’는 오타로 교정)</li>
        <li>1,520→1,420 → SKH EPS −{a.SKH_EPS_FX_HIT:.1f}%, 27년 NI 300~400조 → {a.SKH_NI_ADJ_LOW:.0f}~{a.SKH_NI_ADJ_HIGH:.0f}조</li>
        <li>2H26 환율 조정 16.3조</li>
        <li><b>키옥시아 지분평가 + 반도체 가격/이익 + 환율 = 60조 중후반</b> 축소 가능</li>
        <li>4Q 성과급·일회성. OP 10% 성과급은 상반기·컨센에 반영됐다는 가정. 특별 일회성은 여지로 남김</li>
        <li>1,300원대 중반 조건부: DXY −3~4% → 1,360, 공급 가세 → 1,340. 리스크는 외국인 매도·유가·1,350 달러수요</li>
      </ul>
    </div>
  </div>
</section>

<section id="memory">
  <h2>3. 메모리 — NOBUY 논리, 밸류, SCA</h2>
  <p class="lead">원본: 8/19 메모리 NOBUY, memory storage 주가·밸류.</p>
  <div class="grid2">
    <div class="card"><h3>PER 맵 + HDD</h3><div class="chart tall"><canvas id="perH"></canvas></div></div>
    <div class="card"><h3>본주 시나리오 (만원)</h3><div class="chart tall"><canvas id="pxC"></canvas></div></div>
  </div>
  <div class="grid2" style="margin-top:12px">
    <div class="card"><h3>연산 vs 효율</h3><div class="chart"><canvas id="hbmC"></canvas></div></div>
    <div class="card"><h3>SCA 50% 가중 ASP</h3><div class="chart"><canvas id="scaC"></canvas></div></div>
  </div>
  <div class="card" style="margin-top:12px"><h3>시장가 −20%일 때 Total GP</h3><div class="chart"><canvas id="gpC"></canvas></div>
    <p class="src">공통 가정: ASP/bit 100, cost 15, GP 85, GM 85%, SCA 50%. 연간 cost/bit −6%. HBM 프리미엄·믹스 제외. GP/bit −16.6%여도 Bit +20%면 총GP 유지.</p></div>
  <table style="margin-top:12px">
    <tr><th>종목</th><th>가격</th><th>프레임</th><th>PER</th></tr>
    <tr><td>SKH 본주</td><td>150만</td><td>26/27 EPS 346K·437K</td><td>{a.SKH_PER_26} / {a.SKH_PER_27} (보수 27Y {a.SKH_PER_27_BEAR})</td></tr>
    <tr><td>SKH ADR</td><td>${a.SKH_ADR_HIGH} / 종가 ${a.SKH_ADR_CLOSE}</td><td>프리미엄 52%</td><td>{a.SKH_ADR_PER26} / {a.SKH_ADR_PER27} (vs MU −17%)</td></tr>
    <tr><td>삼성</td><td>24.75만</td><td>26/27 EPS 47.9K·67.2K</td><td>{a.SEC_PER_26} / {a.SEC_PER_27}</td></tr>
    <tr><td>MU</td><td>${a.MU_PX:.2f}</td><td>CY27 EPS $150</td><td>F12M {a.MU_F12_PER} / CY27 {a.MU_CY27_PER}</td></tr>
    <tr><td>SNDK</td><td>${a.SNDK_PX:.2f}</td><td>FY27 EPS $201</td><td>{a.SNDK_FY27_PER}배</td></tr>
    <tr><td>WDC</td><td>${d.WDC_PX:.2f}</td><td>FY27 EPS ${d.WDC_FY27_EPS}</td><td>{d.WDC_PER:.0f}배</td></tr>
    <tr><td>STX</td><td>${d.STX_PX:.2f}</td><td>FY27 EPS ${d.STX_FY27_EPS}</td><td>{d.STX_PER:.0f}배</td></tr>
  </table>
  <div class="call"><strong>NOBUY의 정확한 읽기</strong>타당성 낮음: 비싸서 수요가 곧 꺾인다. 타당성 높음: 비쌀수록 효율화 유인. SRAM≠대체, 분업. 26~28 초과이익, 28+ 양날. 헤게모니(메모리 vs 비메모리)로 퍼지면 수급이 버겁습니다.</div>
</section>

<section id="return">
  <h2>4. 주주환원 — 하이닉스 40조는 시작, 샌디스크는 ID</h2>
  <p class="lead">원본: SK하이닉스 주주환원정책 발표.</p>
  <div class="grid2">
    <div class="card"><h3>연도별 보수 FCF</h3><div class="chart tall"><canvas id="fcfY"></canvas></div></div>
    <div class="card"><h3>25~27 프로그램 산식</h3><div class="chart tall"><canvas id="retC"></canvas></div></div>
  </div>
  <div class="grid2" style="margin-top:12px">
    <div class="card"><h3>샌디스크 바이백 분해</h3><div class="chart"><canvas id="sndkC"></canvas></div>
      <p class="src">8/5~8/7 −15.1%. $140억 자체가 +20%의 원인 아님. 8/13 Investor Day(장기 GM ~80%, NBM 장기계약, AI NAND)가 본반등. 키옥시아 8,000억엔 → 누적 +7.4%.</p></div>
    <div class="card">
      <h3>오해 금지</h3>
      <table>
        <tr><th>오해</th><th>정확</th></tr>
        <tr><td>192.5조를 2027에 지급</td><td>25~27 프로그램 누적 하한</td></tr>
        <tr><td>2028 102.5조가 정책</td><td>모델 205조의 50% 참고치</td></tr>
        <tr><td>40조로 종료</td><td>추가 152.5조+, 목표는 50% 초과, 3Q26</td></tr>
        <tr><td>기존 179/242/237과 385 혼용</td><td>385=25+150+210 (보수 25~27)</td></tr>
      </table>
      <p class="src">ADR 희석 → 40조 소각 → SK스퀘어 지분율 복원. 2Q 순현금 69조. 직관적 주가 반응 +5~9%.</p>
    </div>
  </div>
</section>

<section id="nm">
  <h2>5. 비메모리 — 파운드리 인상, 마벨–구글</h2>
  <div class="grid2">
    <div class="card">
      <h3>삼성 파운드리 (Reuters 8/19)</h3>
      <table>
        <tr><th>공정</th><th>인상</th></tr>
        <tr><td>SF4 중·미</td><td>10~15%</td></tr>
        <tr><td>SF4 대만</td><td>5~10%</td></tr>
        <tr><td>SF5</td><td>10~15%</td></tr>
        <tr><td>8nm</td><td>약 10%</td></tr>
      </table>
      <p class="src">TSMC 포화, 중국 팹리스, 평택 SF4 퀄컴+HBM 베이스다이 풀가동. 내년 흑자. 첨단 50%+, AI/HPC 30%+. 테슬라·애플·AVGO·NVDA 추론·구글 4nm.</p>
    </div>
    <div class="card"><h3>마벨 vs 브로드컴</h3><div class="chart"><canvas id="mrvlC"></canvas></div>
      <p class="src">워런트 최대 {a.MRVL_WARRANT_M}만주, 행사가 ${a.MRVL_STRIKE}, Custom Products ${a.MRVL_TRANCHE_USD_M}M마다 vest, {a.MRVL_WINDOW}. TPU 주변(추론·스토리지·NIC·메모리IF·near-memory).</p>
    </div>
  </div>
</section>

<section id="nvda">
  <h2>6. NVIDIA 8/28 · OpenAI · 순환금융</h2>
  <p class="lead">원본: 엔비디아 8.28 실적 앞두고, 8/20 OpenAI 우려.</p>
  <div class="grid2">
    <div class="card"><h3>Q2 매출 박스</h3><div class="chart"><canvas id="nvC"></canvas></div></div>
    <div class="card"><h3>OpenAI 매출 vs 손실</h3><div class="chart"><canvas id="oaiC"></canvas></div></div>
  </div>
  <div class="mermaid" style="margin-top:12px">
flowchart TB
  N[NVIDIA 투자/금융] --> A[AI 기업·DC]
  A --> G[GPU 구매]
  G --> R[엔비디아 매출]
  R --> N
  </div>
  <div class="call"><strong>관전 5문</strong>인프라 수요 · HS CAPEX($1T, +33%) · AI 기업 자금조달 · GM 75% · Blackwell→Rubin(3Q26, 추론 35배, 랙 $7~8.5M). Beat($92B 컨센, 저자 $93.5B)보다 젠슨의 순환금융 설명이 더 중요합니다. Q3 $108B(+90%), Q4 $120B(+77%) — 성장률이 둔화돼도 절대액은 증가.</div>
</section>

<section id="baba">
  <h2>7. 알리바바 · 울프스피드 — CAPEX가 이익을 삼킴</h2>
  <p class="lead">원본: 알리바바, 울프스피드. 8/20 장전 알리바바 FY1Q27.</p>
  <div class="grid2">
    <div class="card"><h3>알리바바 성장 vs 이익</h3><div class="chart"><canvas id="baC"></canvas></div></div>
    <div class="card"><h3>알리바바 배수</h3><div class="chart"><canvas id="baM"></canvas></div></div>
  </div>
  <div class="card" style="margin-top:12px"><h3>Wolfspeed FY4Q26</h3><div class="chart"><canvas id="woC"></canvas></div>
    <p class="src">매출 $149.6M(+24%) 부합, EPS −$2.26 vs −$1.47 하회, GM −20%. AI DC +20% QoQ. 가이던스 $140~160M vs $150.4M. Chapter 11 이후 $46M CB 전환. SiC = EV + AI 전원. 지금은 이익 극대화가 아니라 선투자 구간.</p></div>
  <div class="call a"><strong>같은 그림</strong>알리바바 Cloud +40%(AI가 성장 엔진, 3년 CAPEX 3,800억위안 초과 가능)와 울프스피드 매출 부합·마진 적자는, OpenAI 손실 확대와 같은 문장입니다. <b>AI 인프라 수요는 살아 있고, 그 비용이 당기 이익을 먼저 가져갑니다.</b></div>
</section>

<section id="unitree">
  <h2>8. 유니트리 — IPO가 상업화보다 앞섬</h2>
  <div class="grid2">
    <div class="card"><h3>PSR 프레임</h3><div class="chart"><canvas id="unC"></canvas></div></div>
    <div class="card">
      <h3>2026 기준</h3>
      <table>
        <tr><th>항목</th><th>숫자</th></tr>
        <tr><td>종가</td><td>¥{d.UNITREE_PX}  ·  IPO ¥{d.UNITREE_IPO} 대비 +{d.UNITREE_IPO_CHG}%</td></tr>
        <tr><td>시총</td><td>{d.UNITREE_MCAP:,}억 위안 ≈ ${d.UNITREE_MCAP_USD}B</td></tr>
        <tr><td>26E 매출</td><td>{d.UNITREE_SALES_26[0]}~{d.UNITREE_SALES_26[1]}억 (H1 {d.UNITREE_H1}억 +{d.UNITREE_H1_YOY}%)</td></tr>
        <tr><td>26E 순익</td><td>약 {d.UNITREE_NI_26E}억 (추정) → PER ~{d.UNITREE_PER}배</td></tr>
        <tr><td>PSR</td><td>{d.UNITREE_PSR[0]}~{d.UNITREE_PSR[1]}배 = 60배 프레임의 2.6배</td></tr>
        <tr><td>BOM</td><td>중국 ${d.UNITREE_BOM['CN']}만 vs 미국 ${d.UNITREE_BOM['US']}만 (35%)</td></tr>
      </table>
      <p class="src">시장 CAGR 31%. 중국 휴머노이드·자율주행 점유 ~75%. 미국 매출 13%, 규제 장벽. 다음은 공장 ROI.</p>
    </div>
  </div>
</section>

<section id="sil">
  <h2>9. 실리콘투 — 돈보다 Douglas</h2>
  <p class="lead">원본: 8월 18일 실리콘투 CVC 3,000억.</p>
  <div class="grid2">
    <div class="card"><h3>상반기 지역 성장</h3><div class="chart"><canvas id="siC"></canvas></div></div>
    <div class="card">
      <h3>거래 조건</h3>
      <table>
        <tr><th>항목</th><th>내용</th></tr>
        <tr><td>금액 / 형식</td><td>{d.SIL_CVC:,}억 RCS, {d.SIL_SHARES_M}백만주, 27.9 전환</td></tr>
        <tr><td>발행가</td><td>{d.SIL_ISSUE_PX:,}원 (+{d.SIL_PREM}% 할증)</td></tr>
        <tr><td>희석 / 쿠폰</td><td>{d.SIL_DILUTE}% / 연복리 {d.SIL_COUPON}%, 1년 보호예수</td></tr>
        <tr><td>H1</td><td>매출 {d.SIL_H1['rev']:,}억 +{d.SIL_H1['rev_yoy']}% · OP {d.SIL_H1['op']:,} · OPM {d.SIL_H1['opm']}%</td></tr>
        <tr><td>오버행</td><td>글랜우드 {d.SIL_GLENWOOD}백만주 @ {d.SIL_GLENWOOD_PX:,} — 잔존</td></tr>
      </table>
      <p class="src">핵심은 CVC→Douglas(유럽 22국·2,000점). 직접 거래 이력이 아직 없음. 확인되면 재평가. 3,000억은 재고·물류·현지법인 선점 자금.</p>
    </div>
  </div>
</section>

<section id="close">
  <h2>10. 클로징 — 앞으로 볼 체크리스트</h2>
  <div class="grid3">
    <div class="card"><h3>금리·엔</h3>10년 4.7 vs 5.0. JGB 3% + USDJPY 급락 동시 여부. 20년물 입찰. 바이백 이후에도 재정·유가·AI 회사채는 남음.</div>
    <div class="card"><h3>환율·환원</h3>DXY 99→96~97, 1,350 달러수요. 하이닉스 일 6,452억 소화, 3Q26 추가 환원. 60조 바구니는 키옥시아+가격+환율.</div>
    <div class="card"><h3>8/26 전후</h3>엔비디아 실적(순환금융 설명). SOX가 금리와 다시 같은 방향으로 움직이는지. 마벨 vest·삼성 파운드리 가이던스.</div>
  </div>
  <div class="call g" style="margin-top:12px"><strong>가져갈 네 문장</strong>
    1) 사흘은 AI 수요 파괴가 아니라 할인율 + 차익실현 + 원화 강세입니다.<br/>
    2) 하이닉스 40조는 3.3% 소각이고, 환율·키옥시아·가격을 합치면 이익에서 60조 중후반이 움직일 수 있습니다.<br/>
    3) HBM 가격결정력을 영구로 두지 말 것. SRAM이 HBM을 지운다고 단정하지 말 것.<br/>
    4) 알리바바 클라우드, 울프스피드 AI DC, OpenAI 손실은 같은 그림 — 수요는 있고 이익은 늦게 옵니다.
  </div>
</section>

<footer>
11개 워드(8/18 이란·엔캐리·실리콘투, 8/19 미국장, 8/20 미국장, 메모리 NOBUY, 매크로, 알리바바·울프스피드, 엔비디아 8.28, 유니트리, 환율, memory storage, 하이닉스 환원)를 재구성한 참고 자료입니다. 매수·매도 추천이 아니며 투자 판단은 각 독자의 몫입니다.<br/>
생성: scripts/generate_integrated_html.py
</footer>
</div>
<script>
mermaid.initialize({{ startOnLoad:true, theme:'base', themeVariables:{{ primaryColor:'#EEF2F8', primaryTextColor:'#0F2043', lineColor:'#1E407C', fontFamily:'Noto Sans KR' }} }});
Chart.defaults.font.family = "'Noto Sans KR',sans-serif";
Chart.defaults.color = '#4B5563';
const g = {{ color:'#E5EAF1' }};
const C = {{ n:'#0F2043', n2:'#1E407C', gold:'#B8943A', g:'#166534', r:'#991B1B', a:'#B45309', t:'#0F766E', gy:'#6B7280' }};

new Chart(toChart, {{ type:'bar', data:{{ labels:{list(d.KOSPI_TURNOVER.keys())}, datasets:[{{ data:{list(d.KOSPI_TURNOVER.values())}, backgroundColor:['#1E407C','#1E407C','#1E407C','#1E407C','#B8943A','#B8943A','#B45309','#991B1B'], borderRadius:5 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g, title:{{display:true,text:'조원'}} }} }} }} }});
new Chart(frChart, {{ type:'bar', data:{{ labels:['5/7~8/10 매도','5일 매수'], datasets:[{{ data:[-{d.FOREIGN_SELL_TO_810},{d.FOREIGN_5D_BUY}], backgroundColor:[C.r,C.g], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(jgbChart, {{ type:'bar', data:{{ labels:['2년','5년','10년'], datasets:[{{ data:[{d.JGB['2y']},{d.JGB['5y']},{d.JGB['10y']}], backgroundColor:[C.n2,C.a,C.r], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g, title:{{display:true,text:'%'}} }} }} }} }});
new Chart(crashChart, {{ type:'line', data:{{ labels:{[x[0] for x in d.CRASH_2024]}, datasets:[
  {{ label:'USD/JPY', data:{[x[1] for x in d.CRASH_2024]}, yAxisID:'y', borderColor:C.n2, tension:.25 }},
  {{ label:'Nikkei%', data:{[x[2] for x in d.CRASH_2024]}, yAxisID:'y1', borderColor:C.r, tension:.2 }},
  {{ label:'KOSPI%', data:{[x[3] for x in d.CRASH_2024]}, yAxisID:'y1', borderColor:C.gold, tension:.2 }}
] }}, options:{{ scales:{{ y:{{ reverse:true, grid:g, title:{{display:true,text:'USD/JPY'}} }}, y1:{{ position:'right', grid:{{drawOnChartArea:false}}, title:{{display:true,text:'%'}} }} }} }} }});
new Chart(sessChart, {{ type:'bar', data:{{ labels:['30Y bp','10Y bp','S&P','NDX','SOX','Dow','USD'], datasets:[{{ data:[{(d.SESS_819['us30'][1]-d.SESS_819['us30'][0])*100:.1f},{(d.SESS_819['us10'][1]-d.SESS_819['us10'][0])*100:.1f},{d.SESS_819['spx']},{d.SESS_819['ndx']},{d.SESS_819['sox']},{d.SESS_819['dow']},{d.SESS_819['dxy']}], backgroundColor:[C.g,C.g,C.g,C.g,C.r,C.g,C.r], borderRadius:5 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(fxL, {{ type:'line', data:{{ labels:['1520','1420','1412','1360','1340'], datasets:[{{ data:[1520,1420,1412,1360,1340], borderColor:C.n2, fill:true, backgroundColor:'rgba(30,64,124,.12)', tension:.25, pointRadius:5 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ reverse:true, min:1320, max:1540, grid:g }} }} }} }});
new Chart(fxB, {{ type:'bar', data:{{ labels:['삼성 β0.4','하이닉스 β0.9'], datasets:[{{ data:[{a.USD_KRW_MOVE_PCT*a.SEC_FX_BETA:.2f},{-a.SKH_EPS_FX_HIT:.2f}], backgroundColor:[C.n2,C.r], borderRadius:6 }}] }}, options:{{ indexAxis:'y', plugins:{{ legend:{{display:false}}, title:{{display:true,text:'EPS %'}} }}, scales:{{ x:{{ grid:g }} }} }} }});
new Chart(hit60, {{ type:'bar', data:{{ labels:['2H26 환율','27년 환율 상단','키옥시아+가격+환율'], datasets:[{{ data:[{d.SKH_2H26_FX},{a.SKH_NI_ADJ_HIGH},{d.SKH_TOTAL_HIT}], backgroundColor:[C.n2,C.a,C.r], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}}, title:{{display:true,text:'조원'}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(perH, {{ type:'bar', data:{{ labels:['SKH26','SKH27','ADR27','MU27','SNDK','삼성26','WDC','STX'], datasets:[{{ data:[{a.SKH_PER_26},{a.SKH_PER_27},{a.SKH_ADR_PER27},{a.MU_CY27_PER},{a.SNDK_FY27_PER},{a.SEC_PER_26},{d.WDC_PER},{d.STX_PER}], backgroundColor:[C.n,C.n2,C.t,C.gy,C.gy,C.gold,C.r,C.r], borderRadius:4 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g, title:{{display:true,text:'PER'}} }} }} }} }});
new Chart(pxC, {{ type:'bar', data:{{ labels:['현재','P30%','P35%','정상20%','PER6','PER7'], datasets:[{{ data:[{a.SKH_LOCAL_PX/10000:.1f},{a.SKH_LOCAL_IF_PREM30/10000:.1f},{a.SKH_LOCAL_IF_PREM35/10000:.1f},{a.SKH_LOCAL_IF_PREM20/10000:.1f},{a.SKH_PER6/10000:.1f},{a.SKH_PER7/10000:.1f}], backgroundColor:[C.gy,C.n2,C.n2,C.g,C.gold,C.gold], borderRadius:5 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(hbmC, {{ type:'bar', data:{{ labels:['수요 지속','둔화'], datasets:[{{ label:'AI +', data:[50,20], backgroundColor:C.n2 }},{{ label:'효율 +', data:[20,30], backgroundColor:C.gold }},{{ label:'순수요', data:[30,-10], backgroundColor:C.g }}] }}, options:{{ scales:{{ y:{{ grid:g }} }} }} }});
new Chart(scaC, {{ type:'bar', data:{{ labels:{[s[0] for s in d.SCA_ASP]}, datasets:[{{ data:{[s[1] for s in d.SCA_ASP]}, backgroundColor:C.n2, borderRadius:5 }}] }}, options:{{ indexAxis:'y', plugins:{{ legend:{{display:false}} }}, scales:{{ x:{{ min:60, max:105, grid:g }} }} }} }});
new Chart(gpC, {{ type:'bar', data:{{ labels:['Bit +10%','Bit +20%','Bit +30%'], datasets:[{{ data:[{(1+d.GP_BIT_DROP/100)*1.10*100-100:.1f},{(1+d.GP_BIT_DROP/100)*1.20*100-100:.1f},{(1+d.GP_BIT_DROP/100)*1.30*100-100:.1f}], backgroundColor:[C.a,C.g,C.g], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}}, title:{{display:true,text:'Total GP %'}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(fcfY, {{ type:'bar', data:{{ labels:{list(d.SKH_FCF_YEARS.keys())}, datasets:[{{ label:'연간', data:{list(d.SKH_FCF_YEARS.values())}, backgroundColor:C.n2 }},{{ label:'누적', data:{list(d.SKH_FCF_CUM.values())}, backgroundColor:C.gold }}] }}, options:{{ scales:{{ y:{{ grid:g, title:{{display:true,text:'조원'}} }} }} }} }});
new Chart(retC, {{ type:'bar', data:{{ labels:['25-27 FCF','50%','40조','추가'], datasets:[{{ data:[385,192.5,40,152.5], backgroundColor:[C.n,C.n2,C.gold,C.g], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(sndkC, {{ type:'bar', data:{{ labels:['이미','잔여','신규','여력'], datasets:[{{ data:[{d.SNDK_BB['이미 매입'][0]},{d.SNDK_BB['기존 잔여'][0]},{d.SNDK_BB['신규 승인'][0]},{d.SNDK_BB['향후 여력'][0]}], backgroundColor:[C.gy,C.n2,C.gold,C.g], borderRadius:5 }}] }}, options:{{ plugins:{{ legend:{{display:false}}, title:{{display:true,text:'$B'}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(mrvlC, {{ type:'bar', data:{{ labels:['Marvell','Broadcom'], datasets:[{{ data:[{a.MRVL_CHG},{a.AVGO_CHG}], backgroundColor:[C.g,C.r], borderRadius:8 }}] }}, options:{{ indexAxis:'y', plugins:{{ legend:{{display:false}} }}, scales:{{ x:{{ grid:g }} }} }} }});
new Chart(nvC, {{ type:'bar', data:{{ labels:['가이드↓','컨센','가이드↑','저자'], datasets:[{{ data:[{d.NVDA_Q2['guide_lo']},{d.NVDA_Q2['cons_rev']},{d.NVDA_Q2['guide_hi']},{d.NVDA_Q2['author']}], backgroundColor:[C.gy,C.n2,C.gy,C.gold], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ min:88, max:95, grid:g }} }} }} }});
new Chart(oaiC, {{ type:'bar', data:{{ labels:['매출','손실Q1','손실Q2'], datasets:[{{ data:[{a.OPENAI_Q2_REV},{a.OPENAI_LOSS[0]},{a.OPENAI_LOSS[1]}], backgroundColor:[C.g,C.a,C.r], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}}, title:{{display:true,text:'$B'}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(baC, {{ type:'bar', data:{{ labels:['전사 YoY','Cloud YoY','EBITA'], datasets:[{{ data:[{d.BABA_REV_YOY},{d.BABA_CLOUD_YOY},{d.BABA_EBITA_DROP}], backgroundColor:[C.n2,C.g,C.r], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(baM, {{ type:'bar', data:{{ labels:['Trail PER','Fwd PER','PEG×10','고점낙폭'], datasets:[{{ data:[20.5,19.5,5,33], backgroundColor:[C.n2,C.t,C.g,C.a], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(woC, {{ type:'bar', data:{{ labels:['매출','컨센','|EPS|×10','|컨센EPS|×10','GM','AI DC'], datasets:[{{ data:[{d.WOLF['rev']},{d.WOLF['cons_rev']},{-d.WOLF['eps']*10},{-d.WOLF['cons_eps']*10},{d.WOLF['gm']},{d.WOLF['ai_dc_qoq']}], backgroundColor:[C.n2,C.gy,C.r,C.a,C.r,C.g], borderRadius:5 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(unC, {{ type:'bar', data:{{ labels:['PSR 60','종가 PSR 155','PER 850÷10'], datasets:[{{ data:[60,155,85], backgroundColor:[C.g,C.r,C.a], borderRadius:6 }}] }}, options:{{ plugins:{{ legend:{{display:false}} }}, scales:{{ y:{{ grid:g }} }} }} }});
new Chart(siC, {{ type:'bar', data:{{ labels:['EU','미국','영국','러시아'], datasets:[{{ label:'매출100억', data:{[d.SIL_REG[k][0]/100 for k in d.SIL_REG]}, backgroundColor:C.n2 }},{{ label:'YoY%', data:{[d.SIL_REG[k][1] for k in d.SIL_REG]}, backgroundColor:C.gold }}] }}, options:{{ scales:{{ y:{{ grid:g }} }} }} }});
</script>
</body>
</html>
"""


def build() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(HTML, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"Wrote {p} ({p.stat().st_size} bytes)")
