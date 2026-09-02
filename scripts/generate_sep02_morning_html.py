#!/usr/bin/env python3
"""9월 2일 모닝미팅 시각화 HTML + 마크다운."""

from __future__ import annotations

from pathlib import Path

from sep02_morning_data import assert_all

LECTURES = Path("/workspace/lectures")
HTML_PATH = LECTURES / "9월 2일 모닝미팅 정리.html"
MD_PATH = LECTURES / "9월 2일 모닝미팅 정리.md"
REPORT_HTML = Path("/workspace/reports/2026-09-02-morning-brief.html")

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
  line-height: 1.5; }
.wrap { max-width: 980px; margin: 0 auto; padding: 28px 20px 64px; }
.kicker { color: var(--gold); font-weight: 700; letter-spacing: .04em; font-size: 13px; }
h1 { color: var(--navy); font-size: 34px; line-height: 1.2; margin: 6px 0 8px; }
.sub { color: var(--muted); margin: 0 0 22px; }
.hero { background: var(--navy); color: #fff; border-radius: 16px; padding: 22px 24px; margin-bottom: 22px; }
.hero h2 { margin: 0 0 10px; font-size: 16px; color: var(--gold); }
.hero li { margin: 6px 0; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0 22px; }
.card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }
.card h3 { margin: 0 0 6px; color: var(--navy2); font-size: 14px; }
.card .num { font-size: 22px; font-weight: 800; color: var(--navy); }
.card p { margin: 6px 0 0; color: var(--muted); font-size: 13px; }
section { background: var(--card); border: 1px solid var(--line); border-radius: 16px; padding: 20px 22px; margin: 0 0 16px; }
section h2 { margin: 0 0 8px; color: var(--navy); font-size: 22px; border-bottom: 3px solid var(--navy); padding-bottom: 8px; }
section h3 { margin: 16px 0 8px; color: var(--navy2); font-size: 16px; }
.callout { border-left: 5px solid var(--navy); background: #eef2f8; padding: 10px 14px; border-radius: 0 10px 10px 0; margin: 10px 0; }
.callout.bull { border-left-color: var(--green); background: var(--green-bg); }
.callout.bear { border-left-color: var(--red); background: var(--red-bg); }
.callout.note { border-left-color: var(--gold); background: var(--amber-bg); }
.callout b { display: block; margin-bottom: 4px; }
.flow { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 10px 0 14px; }
.flow span { background: var(--navy); color: #fff; padding: 6px 10px; border-radius: 999px; font-size: 13px; font-weight: 700; }
.flow i { color: var(--gold); font-style: normal; font-weight: 800; }
table { width: 100%; border-collapse: collapse; font-size: 13.5px; margin: 8px 0 12px; }
th { background: var(--navy); color: #fff; padding: 8px 10px; text-align: left; }
td { padding: 8px 10px; border-bottom: 1px solid var(--line); vertical-align: top; }
tr:nth-child(even) td { background: #f7f9fc; }
.neg { color: var(--red); font-weight: 700; }
.pos { color: var(--green); font-weight: 700; }
.footer { color: var(--muted); font-size: 12px; text-align: right; margin-top: 8px; }
nav { display: flex; flex-wrap: wrap; gap: 8px; margin: 0 0 20px; }
nav a { background: #fff; border: 1px solid var(--line); color: var(--navy2); text-decoration: none;
  padding: 6px 10px; border-radius: 999px; font-size: 12.5px; font-weight: 700; }
@media print {
  body { background: #fff; }
  .wrap { max-width: none; padding: 0; }
  section, .hero { break-inside: avoid; }
  nav { display: none; }
}
@media (max-width: 720px) { .grid { grid-template-columns: 1fr; } h1 { font-size: 26px; } }
"""


def html() -> str:
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>9월 2일 모닝미팅 정리</title>
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <div class="kicker">2026. 9. 2.  ·  모닝미팅 + TalkFile 통합</div>
  <h1>9월 2일 모닝미팅 정리</h1>
  <p class="sub">원문 3개 PDF를 중복 제거해 강의 순서로 재구성했습니다. Fear는 바닥이 아닙니다. 핵심 악재는 유가→금리입니다.</p>
  <nav>
    <a href="#top">한 장</a>
    <a href="#oil">유가·금리</a>
    <a href="#ism">ISM</a>
    <a href="#jolts">JOLTS</a>
    <a href="#fear">Fear</a>
    <a href="#flow">수급</a>
    <a href="#buyback">자사주</a>
    <a href="#dell">Dell</a>
    <a href="#semco">삼성전기</a>
    <a href="#robot">휴머노이드</a>
  </nav>

  <div class="hero" id="top">
    <h2>오늘 한 장으로 보면</h2>
    <ol>
      <li>이번 하락의 핵심은 <b>유가 → 금리</b>입니다. AI/반도체 펀더멘털 훼손으로 읽기에는 이릅니다. Dell이 사상 최대 수주·백로그로 CAPEX 지속을 재확인했습니다.</li>
      <li>국내 센티는 6월 저점 이후 <b>3개월째 Fear</b>. Fear = 바닥이 아니라, 역사적으로는 조금 더 기다려야 하는 구간입니다. 오래 갈수록 성격은 추가 하락에서 바닥 다지기로 바뀝니다.</li>
      <li>개인 유동성은 반토막이지만 구조적 수급은 안 죽었습니다. <b>자사주 55조 중 43조</b>가 남아 있고, 삼성전기는 플랫폼 LTA로 물량과 가격을 동시에 잡았습니다.</li>
    </ol>
  </div>

  <div class="grid">
    <div class="card"><h3>9월 FOMC 25bp</h3><div class="num">40% → 68.2%</div><p>일주일 만에 기대가 매파로 이동</p></div>
    <div class="card"><h3>SOX vs Nasdaq</h3><div class="num">−2.1% / −1.03%</div><p>반도체 상대 약세 = 금리 + 관망</p></div>
    <div class="card"><h3>Fear 이후 KOSPI</h3><div class="num">6M −5.7% · 12M +4.6%</div><p>단기 아래, 12개월은 플러스</p></div>
    <div class="card"><h3>자사주 잔여</h3><div class="num">43.2조 (78.5%)</div><p>하닉 31.9조 · 속도 유지 시 10/16</p></div>
    <div class="card"><h3>Dell 백로그</h3><div class="num">$950억</div><p>수주 $609억 · AI 매출 $164억</p></div>
    <div class="card"><h3>삼성전기 LTA</h3><div class="num">1.82조 / 3건</div><p>’27E 컴포넌트 매출 17% · OP 18.6%</p></div>
  </div>

  <section id="oil">
    <h2>1. 유가 → 금리, 그게 어제 반도체</h2>
    <div class="callout"><b>한 줄</b>핵심 악재는 지정학 그 자체가 아니라 유가 → 인플레 → 금리 연결고리입니다. SOX가 더 빠진 이유를 침체로 읽지는 않습니다. 중립, 또는 기업의 관망입니다.</div>
    <div class="flow">
      <span>미·이란</span><i>→</i><span>호르무즈</span><i>→</i><span>유가 +5%</span><i>→</i><span>인플레</span><i>→</i><span>Fed 인상</span><i>→</i><span>10Y 4.8%</span><i>→</i><span>성장주 압박</span>
    </div>
    <table>
      <tr><th>지표</th><th>숫자</th><th>의미</th></tr>
      <tr><td>9월 25bp 인상 확률</td><td>1주 전 ~40% → 68.2%</td><td>FOMC 기대가 이번 조정의 코어</td></tr>
      <tr><td>美 10Y</td><td>4.8% 근접</td><td>기술주 할인율 상승</td></tr>
      <tr><td>ISM 가격</td><td>71.1</td><td>물가 압력. 3~5월보다는 낮음</td></tr>
      <tr><td>SOX / Nasdaq</td><td class="neg">−2.1% / −1.03%</td><td>반도체 상대 약세</td></tr>
    </table>
    <div class="callout note"><b>구분</b>단기 주가 조정 ≠ 반도체 업황 악화. 현재 발생한 것은 AI 수요 둔화·메모리 가격 하락·CAPEX 축소가 아니라 금리·유가·지정학 Risk-off입니다.</div>
    <h3>다섯 개만 본다</h3>
    <table>
      <tr><th>#</th><th>체크</th><th>왜</th></tr>
      <tr><td>①</td><td>유가 $90~95</td><td>인플레 지속 여부</td></tr>
      <tr><td>②</td><td>美 10Y 4.8% 안착</td><td>성장주 할인율 고정 여부</td></tr>
      <tr><td>③</td><td>9/4 8월 NFP</td><td>JOLTS 채용 둔화가 일자리로 확인되나</td></tr>
      <tr><td>④</td><td>인상 확률 68% 추가 상승</td><td>더 매파면 조정 장기화</td></tr>
      <tr><td>⑤</td><td>SOX −2% 이후 추가 하락</td><td>수급·센티 확인</td></tr>
    </table>
    <div class="callout"><b>포트</b>지정학→유가→금리는 부정. 다만 고유가+경기둔화를 시장이 이미 다 반영했는지는 개별 지표를 더 봐야 합니다. 과하면 하이에나의 먹잇감. 기본은 밸런스 포트.</div>
  </section>

  <section id="ism">
    <h2>2. ISM — 침체가 아니라 앞단이 약해진다</h2>
    <div class="callout"><b>한 줄</b>8개월 연속 50 이상. 8월 54.6은 7월 55.6에서 한 단계 내려온 것. GDP 환산 +2.4%. 문제는 생산이 아니라 신규주문·수주잔고·고용과 가격 71.1.</div>
    <div class="flow">
      <span>47.9</span><i>→</i><span>52.6</span><i>→</i><span>54.0</span><i>→</i><span>55.6 7월 고점</span><i>→</i><span>54.6 8월</span>
    </div>
    <table>
      <tr><th>구성</th><th>변화</th><th>읽기</th></tr>
      <tr><td>신규주문</td><td class="neg">−3.0p</td><td>앞으로 들어올 일</td></tr>
      <tr><td>수주잔고</td><td class="neg">−3.2p</td><td>쌓여 있는 일</td></tr>
      <tr><td>고용</td><td class="neg">−1.6p</td><td>사람을 뽑는 속도</td></tr>
      <tr><td>현재 생산</td><td>견조</td><td>지금 돌아가는 공장</td></tr>
      <tr><td>가격지수</td><td>71.1</td><td>70+ = 강한 원자재 상승. 23개월 연속</td></tr>
    </table>
    <p>수요↓ 고용↓ 가격↑. 인상도 인하도 어려운 데이터. 결국 — 허무할지라도 — 전쟁 때문에라는 얘기로 돌아옵니다. 스태그플레이션으로 건너뛰는 해석은 과합니다.</p>
  </section>

  <section id="jolts">
    <h2>3. JOLTS — 무너지는 게 아니라 얼어붙는다</h2>
    <div class="callout"><b>한 줄</b>Low Hire · Low Fire. 일자리는 있는데 적극적으로 뽑지 않습니다. 인하 명분은 생기지만 붕괴는 아닙니다. 확인은 9/4 NFP.</div>
    <table>
      <tr><th></th><th>6월 (수정)</th><th>7월</th></tr>
      <tr><td>구인</td><td>718.2만 (당초 735.9 → 하향)</td><td>727.1만</td></tr>
      <tr><td>실업자</td><td>709.4만</td><td>691.6만</td></tr>
      <tr><td>구인/실업자</td><td>1.012배</td><td>1.051배</td></tr>
      <tr><td>채용</td><td>533만</td><td>505만 (3.4→3.2%)</td></tr>
      <tr><td>해고</td><td>177만</td><td>167만 (1.1→1.0%)</td></tr>
    </table>
    <div class="flow"><span>구인 +8.9만</span><i>→</i><span>채용 −27.8만</span><i>→</i><span>해고 ↓</span></div>
    <p>겉숫자는 더 타이트합니다. 실업자가 17.8만 줄었기 때문입니다. 내부는 반대입니다. 기존 인력 유지, 신규 채용 보수. 내구재 제조업 구인만 +7.6~7.9만.</p>
  </section>

  <section id="fear">
    <h2>4. Fear — 바닥이 아니라 조금 더 기다리는 구간</h2>
    <div class="callout bear"><b>한 줄</b>Fear 진입 후 KOSPI 1·3·6개월 평균은 마이너스. 12개월에야 +4.6%. Extreme Fear는 12개월도 −9.2%. “Fear니까 무조건 바닥”은 역사적으로 틀렸습니다.</div>
    <table>
      <tr><th>국면</th><th>1M</th><th>3M</th><th>6M</th><th>12M</th></tr>
      <tr><td>Extreme Greed</td><td class="pos">+2.2%</td><td class="pos">+8.6%</td><td class="pos">+39.3%</td><td class="pos">+51.1%</td></tr>
      <tr><td>Greed</td><td class="pos">+2.2%</td><td class="pos">+3.6%</td><td class="pos">+11.9%</td><td class="pos">+16.7%</td></tr>
      <tr><td>Normal</td><td>0%</td><td class="pos">+4.8%</td><td class="pos">+5.4%</td><td class="pos">+15.6%</td></tr>
      <tr><td>Fear</td><td class="neg">−0.3%</td><td class="neg">−1.4%</td><td class="neg">−5.7%</td><td class="pos">+4.6%</td></tr>
      <tr><td>Extreme Fear</td><td class="neg">−1.7%</td><td class="neg">−3.4%</td><td class="neg">−8.6%</td><td class="neg">−9.2%</td></tr>
    </table>
    <div class="callout note"><b>지금</b>6월 저점 이후 3개월째 Fear. 핵심 신호는 Fear → Normal 전환. 위보다 아래가 조금 더 열려 있지만, 오래 갈수록 추가 하락에서 바닥 다지기로 성격이 바뀝니다. 단일 센티 지표로 바닥을 확정하지 않습니다.</div>
  </section>

  <section id="flow">
    <h2>5. 거래대금 — 돈은 피신이지 소멸이 아니다</h2>
    <div class="callout"><b>한 줄</b>개인 유동성은 급격히 위축. 구조적 수급 기반까지 훼손된 것은 아닙니다. VKOSPI 97→50은 외국인 재진입 문턱을 낮춥니다.</div>
    <table>
      <tr><th>구분</th><th>5~6월</th><th>8월</th><th>변화</th></tr>
      <tr><td>KOSPI 일평균 거래대금</td><td>50조+</td><td>25.8조</td><td class="neg">약 −50%</td></tr>
      <tr><td>상장주식 일평균 회전율</td><td>—</td><td>0.54%</td><td>연중 최저</td></tr>
      <tr><td>투자자예탁금</td><td>140조</td><td>96.7조</td><td class="neg">−40조+</td></tr>
    </table>
    <div class="flow"><span>고점 9,385.6</span><i>→</i><span>5,200선</span><i>→</i><span>7,000 돌파 실패</span></div>
    <p>행선지: 단기 안전자산 약 3.3조 · MMF 1주 +1.6조 · KODEX MM +2,941억 · RISE MM +1,438억 · 미국주식 보관 $1,715억→$1,867억 (+$152억, +8.9%). 신영: 실질예탁금은 순유입. 신용·미수는 반대매매 주의.</p>
  </section>

  <section id="buyback">
    <h2>6. 자사주 — 55조 중 아직 43조</h2>
    <div class="callout bull"><b>한 줄</b>하닉 40조(전량 소각) + 삼전 15조(임직원 보상). 체결 11.84조, 소진 21.5%. 속도 유지 시 약 30거래일·1.5개월 구조적 매수세.</div>
    <table>
      <tr><th></th><th>SK하이닉스</th><th>삼성전자</th><th>합계</th></tr>
      <tr><td>계획</td><td>40조 · 2,407만주 · 3.3% · 전량 소각</td><td>15조 · 약 5,329만주 · 보상</td><td>55조</td></tr>
      <tr><td>체결</td><td>8.78조 · 520만주 (21.6%)</td><td>3.54조</td><td>11.84조 (21.5%)</td></tr>
      <tr><td>잔여</td><td>1,887만주 · 약 31.9조</td><td>—</td><td>약 43.2조</td></tr>
    </table>
    <p>하닉: 하루 약 65만주, 평균 취득가 168.9만원. 같은 속도면 <b>10월 16일</b> 완료 추정. 공식 기간은 8/20–11/19. 전량 소각 → EPS/BPS 개선. 78.4%가 남아 10월 중순까지 수급 안전판. 검산: 3.54+8.78=12.32조, 원문 합계는 11.84조. 잔여·소진률은 원문 합계를 따릅니다.</p>
  </section>

  <section id="dell">
    <h2>7. Dell — CAPEX는 아직 피크아웃이 아니다</h2>
    <div class="callout bull"><b>한 줄</b>본장 −6.8% → 시간외 +6.8%. 수주 $609억 · 백로그 $950억 · AI 매출 $164억(+100%). 하이퍼스케일러 투자가 아직 피크아웃하지 않았다는 전방 확인.</div>
    <table>
      <tr><th></th><th>실적 / 가이드</th><th>컨센</th><th>괴리</th></tr>
      <tr><td>2Q 매출</td><td>$469.7억 (+57.7% / +7.1% QoQ)</td><td>$447.84억</td><td class="pos">+5%</td></tr>
      <tr><td>2Q OP / EPS</td><td>$59.3억 / $7.04</td><td>$41.76억 / $4.90</td><td class="pos">EPS +44%</td></tr>
      <tr><td>3Q 매출 · EPS</td><td>$485~495억 / $6.5±0.1</td><td>$419억 / $4.55</td><td class="pos">+16~17% / +43%</td></tr>
      <tr><td>FY27 매출</td><td>$1,920억 ± $200억</td><td>기존 +$250억</td><td>중간값 +69% YoY</td></tr>
      <tr><td>FY27 AI 서버</td><td>$740억</td><td></td><td>+200% YoY</td></tr>
    </table>
    <table>
      <tr><th>사업</th><th>매출</th><th>YoY</th></tr>
      <tr><td>ISG</td><td>$317.8억</td><td class="pos">+89.2%</td></tr>
      <tr><td>AI Servers</td><td>$164.0억</td><td class="pos">+99.8%</td></tr>
      <tr><td>전통 서버·네트워킹</td><td>$105.3억</td><td class="pos">+122.4%</td></tr>
      <tr><td>Storage</td><td>$48.5억</td><td class="pos">+25.8%</td></tr>
      <tr><td>Client</td><td>$150.3억</td><td class="pos">+20.2%</td></tr>
    </table>
    <p>전통 서버가 AI보다 빠릅니다. GPU를 넘어 서버·네트워크·스토리지로 CAPEX가 확산. 국내: PCB·MLB·전력/냉각·커넥터·메모리·SSD.</p>
  </section>

  <section id="semco">
    <h2>8. 삼성전기 — 플랫폼이 MLCC를 직접 가져간다</h2>
    <div class="callout bull"><b>한 줄</b>ODM·조립업체 → 플랫폼 직접 LTA. 물량 가시성 + 가격 협상력. AI 서버 플랫폼이 MLCC를 전략 조달품목으로 격상.</div>
    <div class="flow"><span>6월 4,540억</span><i>→</i><span>7월 2,951억</span><i>→</i><span>이번 1.07조</span><i>→</i><span>누적 1.82조</span></div>
    <table>
      <tr><th>포인트</th><th>숫자</th></tr>
      <tr><td>직접 LTA</td><td>1.07조 · 2027년 1~12월 공급</td></tr>
      <tr><td>3건 누적</td><td>1.82조 = ’27E 컴포넌트 매출 17%</td></tr>
      <tr><td>이익</td><td>OPM 30% 가정 5,464억 = 컴포넌트 OP 18.6%</td></tr>
      <tr><td>’27E 가정</td><td>판가 7.5원 (+27%) · 출하 1.3조개 (+12%)</td></tr>
      <tr><td>캐파 흡수</td><td>범용 환산 3,000억개 = 캐파의 23%</td></tr>
      <tr><td>Upside</td><td>4Q OEM 직납 판가 인상 · 필리핀 1H27 완공</td></tr>
    </table>
    <div class="flow"><span>물량 확보</span><i>→</i><span>가격 결정력</span><i>→</i><span>이익 레버리지</span></div>
  </section>

  <section id="robot">
    <h2>9. 휴머노이드 — 10억 대, 병목은 전력</h2>
    <div class="callout"><b>머스크 9/1 G20</b>10년 뒤 휴머노이드 10억 대. 1대당 생산성 = 인간 5배. 전 인류를 합친 것보다 높은 생산성. 최대 걸림돌은 전력. AI 반도체 속도 대비 인프라가 턱없이 부족. Dell·데이터센터 병목과 같은 줄.</div>
  </section>

  <section>
    <h2>클로징 네 문장</h2>
    <ol>
      <li>어제 반도체 약세의 1차 원인은 유가→금리. 9월 인상 68%, 10Y 4.8%, 9/4 NFP. 스태그플레이션으로 건너뛰지 않는다.</li>
      <li>Fear는 바닥 신호가 아니다. 3개월째라면 Fear→Normal 전환을 기다린다. 거래대금 반토막은 위험선호 약화이지 수급 소멸이 아니다.</li>
      <li>자사주 43조와 Dell 백로그 $950억은 국내 수급·전방 CAPEX 안전판. 단기 주가와 업황을 같은 시계로 읽지 않는다.</li>
      <li>삼성전기는 플랫폼 LTA로 물량·가격을 동시에 잡았다. 휴머노이드 10억 대의 병목은 전력이라 인프라 이야기로 다시 연결된다.</li>
    </ol>
    <p class="footer">원문: 9월 2일 모닝미팅.pdf · FEAR에서 오래있으면…..pdf · TalkFile_공포, 거래대금, 자사주, 삼성전기, 휴머노이드로봇 10억대, 인간의 5배.pdf</p>
  </section>
</div>
</body>
</html>
"""


MD = """# 9월 2일 모닝미팅 정리

원문 3개 PDF를 중복 제거해 강의 순서로 재구성했습니다.

- 강의노트 Word: `lectures/9월 2일 모닝미팅 정리.docx`
- 브라우저용: `lectures/9월 2일 모닝미팅 정리.html`

원문: 9월 2일 모닝미팅 · FEAR에서 오래있으면 · TalkFile_공포, 거래대금, 자사주, 삼성전기, 휴머노이드로봇

---

## 한 장

이번 하락의 핵심은 **유가 → 금리**입니다. AI/반도체 펀더멘털 훼손으로 읽기에는 이릅니다. Dell이 사상 최대 수주·백로그로 CAPEX 지속을 재확인했습니다.

국내 센티는 6월 저점 이후 **3개월째 Fear**. Fear = 바닥이 아니라, 역사적으로는 조금 더 기다려야 하는 구간입니다. 오래 갈수록 성격은 추가 하락에서 바닥 다지기로 바뀝니다.

개인 유동성은 반토막이지만 구조적 수급은 안 죽었습니다. **자사주 55조 중 43조**가 남아 있고, 삼성전기는 플랫폼 LTA로 물량과 가격을 동시에 잡았습니다.

## 숫자

| 항목 | 핵심 숫자 | 한 줄 |
| --- | --- | --- |
| 유가 · 금리 | 유가 +5% · 10Y 4.8% · 9월 25bp 40%→68.2% | 핵심 악재는 유가→금리 |
| 증시 | SOX −2.1% > Nasdaq −1.03% | 금리 + 관망 |
| ISM 8월 | 54.6 (7월 55.6) · 가격 71.1 · GDP +2.4% | 침체 아님. 강한 확장에서 한 단계 |
| JOLTS 7월 | 구인/실업 1.05 · 채용 −27.8만 · 해고 ↓ | Low Hire · Low Fire |
| Fear | 1M −0.3 · 3M −1.4 · 6M −5.7 · 12M +4.6 | Fear ≠ 바닥 |
| 수급 | 거래대금 50조→25.8조 · 예탁금 140→96.7조 | 위험선호 약화. 기반은 유지 |
| 자사주 | 계획 55조 · 체결 11.84조 (21.5%) | 하닉 잔여 31.9조, 속도 시 10/16 |
| Dell | 수주 $609억 · 백로그 $950억 · FY27 $1,920억 | CAPEX 피크아웃 아직 아님 |
| 삼성전기 | LTA 3건 1.82조 · 매출 17% / OP 18.6% | 물량 + 가격 |
| 휴머노이드 | 10년 10억 대 · 생산성 5배 | 병목은 전력 |

## 확인할 것

1. 유가 $90~95
2. 美 10Y 4.8% 안착
3. 9/4 8월 NFP
4. 9월 인상 확률 68% 추가 상승
5. SOX −2% 이후 추가 하락
6. Fear → Normal 전환

## 네 문장

1. 어제 반도체 약세의 1차 원인은 유가→금리. 스태그플레이션으로 건너뛰지 않는다.
2. Fear는 바닥 신호가 아니다. 거래대금 반토막은 위험선호 약화이지 수급 소멸이 아니다.
3. 자사주 43조와 Dell 백로그 $950억은 수급·전방 안전판. 단기 주가와 업황을 같은 시계로 읽지 않는다.
4. 삼성전기는 플랫폼 LTA로 물량·가격을 동시에 잡았다. 휴머노이드 10억 대의 병목은 전력이다.

매수·매도 권유가 아닙니다.
"""


def build() -> None:
    assert_all()
    LECTURES.mkdir(parents=True, exist_ok=True)
    REPORT_HTML.parent.mkdir(parents=True, exist_ok=True)
    text = html()
    HTML_PATH.write_text(text, encoding="utf-8")
    REPORT_HTML.write_text(text, encoding="utf-8")
    MD_PATH.write_text(MD, encoding="utf-8")
    print(f"Wrote {HTML_PATH} ({HTML_PATH.stat().st_size} bytes)")
    print(f"Wrote {MD_PATH} ({MD_PATH.stat().st_size} bytes)")
    print(f"Wrote {REPORT_HTML}")


if __name__ == "__main__":
    build()
