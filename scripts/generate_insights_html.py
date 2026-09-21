#!/usr/bin/env python3
"""8/18–9/20 투자 스터디 인사이트 장문 보드. 차트 base64."""

from __future__ import annotations

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import insights_data as D

ROOT = Path("/workspace")
CHARTS = ROOT / "lectures" / "assets" / "insights"
OUT = ROOT / "lectures" / "8월-9월 투자 스터디 인사이트.html"


def uri(name: str) -> str:
    return "data:image/png;base64," + base64.b64encode((CHARTS / name).read_bytes()).decode("ascii")


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
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>8월–9월 투자 스터디 인사이트 정리</title>
<style>
:root {{ --navy:#0f2043; --navy2:#1e407c; --gold:#b8943a; --ink:#1a1a1a;
  --muted:#4b5563; --line:#d5dce6; --bg:#eef1f7; --green:#166534; --red:#991b1b; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--bg); color:var(--ink);
  font-family:"Noto Sans CJK KR","Noto Sans KR","Apple SD Gothic Neo","Malgun Gothic","WenQuanYi Micro Hei",sans-serif;
  word-spacing:.12em; }}
.wrap {{ width:980px; margin:0 auto; padding:22px 18px 40px; }}
.kicker {{ color:var(--gold); font-weight:800; font-size:12px; }}
h1 {{ color:var(--navy); font-size:28px; line-height:1.3; margin:6px 0 10px; }}
h2 {{ color:var(--navy); font-size:20px; border-bottom:2px solid var(--navy); padding-bottom:4px; margin:28px 0 10px; }}
h3 {{ color:var(--navy2); font-size:15px; margin:16px 0 6px; }}
p,li {{ font-size:14px; line-height:1.6; }}
.hero {{ background:var(--navy); color:#fff; border-radius:12px; padding:16px 18px; font-size:15px; line-height:1.6; }}
.hero b {{ color:var(--gold); }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:14px 16px; margin:10px 0; }}
img {{ width:100%; border-radius:8px; border:1px solid var(--line); margin:8px 0; background:#fff; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ background:var(--navy); color:#fff; padding:6px 8px; text-align:left; }}
td {{ padding:6px 8px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:nth-child(even) td {{ background:#f7f9fc; }}
.note,.ok,.risk,.blue {{ padding:8px 10px; border-radius:0 8px 8px 0; font-size:13.2px; margin:8px 0; line-height:1.5; }}
.note {{ background:#fff8e7; border-left:4px solid var(--gold); }}
.ok {{ background:#e8f5e9; border-left:4px solid var(--green); }}
.risk {{ background:#fdecea; border-left:4px solid var(--red); }}
.blue {{ background:#e8f1fb; border-left:4px solid var(--navy2); }}
.foot {{ color:var(--muted); font-size:12px; text-align:right; margin-top:18px; }}
</style>
</head>
<body>
<div class="wrap">
  <div class="kicker">준혁 투자 스터디 추출  ·  2026-08-18 ~ 2026-09-20  ·  funny 저장소</div>
  <h1>투자 인사이트 정리 — 그래프를 앞에 두고, 문장은 뒤에</h1>
  <div class="hero">
    로컬 워커는 연결되어 있지 않아, 이 컴퓨터(클라우드)에 올라와 있는
    <b>funny 저장소의 투자 스터디 전부</b>를 읽었다.
    8월 18일 NON-삼전닉스부터 9월 20일 일요 다이제스트까지 21세션.
    커넥톰·봉직의·클리닉·톤즈 재무모델은 투자 스터디가 아니어서 뺐다.
  </div>

  <h2>한 장으로 보면</h2>
  <div class="card">
    <p><b>공통 분모는 AI CAPEX</b>다. 최종수요는 아무도 못 맞추니 모델·데이터센터·GPU 전망에 기대고, 자금이 빠듯하니 서로 묶는다.</p>
    <p>그래서 확인 축은 세 개다. <b>장비는 수주</b>, <b>SK는 할인율</b>, <b>Atlas는 공장 배치</b>. 9월 들어 네 번째 축이 선명해졌다. <b>약한 고리 = 자금 + 장기금리</b>.</p>
    <div class="note">사이렌(10Y 5% 안착 · WTI 120)은 미발화. 9/18 장중 10Y 5.002는 터치이지 안착이 아니다.</div>
    <img src="{c['01_corpus.png']}" alt="코퍼스"/>
    <img src="{c['24_evolve.png']}" alt="진화"/>
    <img src="{c['02_themes.png']}" alt="테제"/>
  </div>

  <h2>1. 양면 시각 — Dark GPU</h2>
  <div class="card">
    <p>8/18의 출발점. Sacks의 Dark GPU는 “엔비디아 수요가 꺾인다”가 아니다. AI 인프라에 금융이 붙으면 과잉투자 위험이 커진다는 경고다.</p>
    <img src="{c['25_darkgpu.png']}" alt="Dark GPU"/>
    <ul>
      <li>순방향: 수요 → 투자 → GPU 구매 속도가 빨라진다.</li>
      <li>역방향: 가동률 하락 → 임대료/가격 하락 → DC 수익성 → 금융비용 → 투자 축소.</li>
      <li>정치적 반발·전력·인허가가 역설적 브레이크가 될 수 있다.</li>
    </ul>
    <div class="blue">Dark GPU가 현실화되면 가장 먼저 흔들리는 것은 수주 가시성과 할인율이다.</div>
  </div>

  <h2>2. 준혁 프레임은 덮어쓰지 않는다</h2>
  <div class="card">
    <img src="{c['03_frames.png']}" alt="프레임"/>
    <img src="{c['04_siren.png']}" alt="사이렌"/>
    <img src="{c['05_and_gate.png']}" alt="AND"/>
    <table>
      <tr><th>프레임</th><th>선</th><th>최근 관측</th><th>읽는 법</th></tr>
      <tr><td>10Y</td><td>5.00%</td><td>워킹 4.95–5.01 · 장중 5.002</td><td>터치 ≠ 안착</td></tr>
      <tr><td>30Y</td><td>6.0%</td><td>9/15 낙찰 5.308%</td><td>프레임 유지</td></tr>
      <tr><td>TIPS</td><td>3.0%</td><td>8/21 근처 2.94%</td><td>프레임 유지</td></tr>
      <tr><td>Oil</td><td>120</td><td>WTI 100.30 · Brent 103.87</td><td>사이렌 꺼짐</td></tr>
      <tr><td>환원 스타일</td><td>—</td><td>—</td><td>닉스 자사주 vs 삼성 배당/1월</td></tr>
    </table>
    <div class="risk">이은택 Gravity: 붕괴 = (10–20Y가 5.0–5.3%를 추세로 돌파) AND (No Way Back). 9/18은 AND 미충족.</div>
  </div>

  <h2>3. 박스와 W바닥</h2>
  <div class="card">
    <img src="{c['06_kospi_box.png']}" alt="박스"/>
    <p>6/22 고점 {D.KOSPI_PEAK:,.2f} → 7/30 {D.KOSPI_TROUGH:,.2f} ({D.KOSPI_DRAW}%). 9/18 종가 {D.KOSPI_SEP18:,.2f}는 고점 대비 {D.kospi_drawdown_from_peak():.1f}%.</p>
    <p>윤지호: 박스 6,000–7,150, 8,000은 아직 안 연다. 상단의 열쇠는 하이퍼스케일러 현금이 DC나 토큰으로 다시 도느냐.</p>
    <img src="{c['19_flows.png']}" alt="수급"/>
    <p>9/18 수급: 개인 {D.FLOW_RETAIL}조, 기관 +{D.FLOW_INST}, 외인 +{D.FLOW_FOREIGN}, 법인 +{D.FLOW_CORP}. W바닥 서사의 재료이지 바닥 확정이 아니다.</p>
  </div>

  <h2>4. 메모리 — 숫자가 안 가서가 아니라, 숫자를 안 믿어서</h2>
  <div class="card">
    <img src="{c['07_memory_per.png']}" alt="PER"/>
    <img src="{c['08_fair_band.png']}" alt="밴드"/>
    <img src="{c['09_hbm.png']}" alt="Citi"/>
    <img src="{c['20_export.png']}" alt="수출"/>
    <ul>
      <li>8/18 부록: 하이닉스 164.5만 PER 4.8/3.8, 삼성 27.45만 5.7/4.1. ADR 프리미엄 43%.</li>
      <li>9/15: PER이 더 눌림. 이익 폭증 때문이지 “싸다”는 뜻이 아니다.</li>
      <li>Citi 9/18: DRAM 부족 8.7→9.7%, HBM bit +62/+69 (27/28).</li>
      <li>8월 반도체 수출 +209%, 18개월 연속. 수출이 증명을 대신한다.</li>
    </ul>
    <div class="note">강의 산식 밴드: 닉스 175–242만, 삼전 28.7–33.5만. IB 310/400 · 게스트 200만은 합의가 아니다.</div>
  </div>

  <h2>5. 토큰 P↓Q↑ · 엔비디아 현금 · 수주</h2>
  <div class="card">
    <img src="{c['10_token.png']}" alt="토큰"/>
    <img src="{c['11_nvidia.png']}" alt="NVDA"/>
    <img src="{c['12_capex.png']}" alt="CAPEX"/>
    <p>8월 토큰(JPM/OpenRouter): 볼륨 MoM +{D.TOKEN_VOL_MOM}%, YoY {D.TOKEN_VOL_YOY_X}배. 단가 MoM {D.TOKEN_PRICE_MOM}%, YoY {D.TOKEN_PRICE_YOY}%.</p>
    <p>엔비디아 Q2 FY27: 매출 ${D.NVDA_REV}B, GM {D.NVDA_GM}%, OCF/NI {D.NVDA_OCF_NI}%, DSO 45→60, 공급약정 ${D.NVDA_SUPPLY_COMMIT}B(대부분 메모리). FY28 +{D.NVDA_FY28_SUPPLY_CAP}%는 수요 한도가 아니라 공급 천장.</p>
    <p>Dell 백로그 ${D.DELL_BACKLOG}B, Oracle RPO ${D.ORCL_RPO}B. CAPEX peak-out은 아직 숫자로 안 보인다. 속도조절론은 출시 각도와 인프라 속도를 헷갈리면 매도 이유가 된다.</p>
    <div class="ok">Peak-out이 아니라 Timing. KEY: Frontier가 늦어도 Agent만으로 CapEx가 지속되는가. 9/29 DevDay가 첫 숫자 창.</div>
  </div>

  <h2>6. 병목 = 노드 = 돈</h2>
  <div class="card">
    <img src="{c['21_leads.png']}" alt="리드타임"/>
    <img src="{c['18_power.png']}" alt="전력"/>
    <p>연산은 풀렸다. 지금은 메모리, 다음 영수증은 전력·후공정. DC 2030 수요 {D.DC_2030_DEMAND}GW vs 그리드 {D.DC_2030_GRID}GW, 갭 {D.dc_gap()}GW.</p>
    <p>9/5 절단된 사슬: oil → PCE → Fed 경로는 잘렸다. 유가는 기업 비용이지 정책 경로가 아니다. 그래서 Book C는 SEMI 45 / 단기 25 / oil-down 10 / hedge 20.</p>
    <img src="{c['17_bookc.png']}" alt="Book C"/>
  </div>

  <h2>7. 소부장 — 실적 정점 ≠ 주가 정점</h2>
  <div class="card">
    <img src="{c['13_equipment.png']}" alt="장비"/>
    <img src="{c['26_opm.png']}" alt="OPM"/>
    <table>
      <tr><th>종목</th><th>핵심 숫자 (8/18)</th><th>한 줄</th></tr>
      <tr><td>테스</td><td>신규수주 2,823억 QoQ 2배 · 잔고 2,000억+</td><td>DRAM+NAND. BSD가 성장 옵션. 독점이라고 단정 금지.</td></tr>
      <tr><td>한미반도체</td><td>매출 2,511억 · OPM 51.9%</td><td>질문은 TCB 성장률 × 점유율 55–60%. 변수는 한화세미텍.</td></tr>
      <tr><td>원익IPS</td><td>1Q 잔고 ~4,000억 · 안전마진 10.4–11.8만</td><td>2Q 부진 ≠ 수주 훼손. 승부처는 2027 수주.</td></tr>
      <tr><td>리노공업</td><td>OPM 51.3% · 파업 ~4주</td><td>매출보다 마진 훼손. 파업 종료 시 순환매 가능.</td></tr>
    </table>
  </div>

  <h2>8. SK · Atlas</h2>
  <div class="card">
    <img src="{c['14_sk.png']}" alt="SK"/>
    <img src="{c['15_atlas.png']}" alt="Atlas"/>
    <p>대신 SOTP: NAV {D.SK_NAV}조 × 할인 {D.SK_DISC}% → TP {D.SK_TP_DAISHIN}만. 에코플랜트 표 {D.SK_ECO_TABLE}조는 2Q OP 연환산·잔고 {D.SK_ECO_BACKLOG}조 대비 낮다. 재평가만으로 TP {D.SK_REVAL_TP[0]}–{D.SK_REVAL_TP[1]}만도 산출 가능. 기본은 스퀘어(하이닉스)와 이노베이션.</p>
    <p>Atlas: 성능 논쟁 → Fleet × 가동률 × 데이터. 2028 HMGMA, 2030 조립 확대. 모비스 대당 액추에이터 31개, 11월 시제품. 글로비스는 서열·물류 데이터.</p>
  </div>

  <h2>9. H2 포트폴리오 (9/3 계산)</h2>
  <div class="card">
    <img src="{c['16_h2.png']}" alt="H2"/>
    <p>Phase 1, 주식 {D.H2_EQUITY}% / 현금·채권 {D.H2_CASH}%. 삼전닉스는 Hold, 10월 전 추가 없음. 신규자금: 한국금융지주 &gt; NAVER &gt; 모비스 &gt; 한전.</p>
    <p>위성 스터디: 알테오젠은 시밀러가 아니라 ALT-B4(물질특허). 현대제철 합성 TP 42,000 (당시 31,000 대비 +35.5%).</p>
  </div>

  <h2>10. 확인 캘린더와 잠금 규칙</h2>
  <div class="card">
    <img src="{c['22_calendar.png']}" alt="캘린더"/>
    <img src="{c['23_lock.png']}" alt="잠금"/>
    <div class="risk">쓰지 말 것: 10Y 5% 안착, oil 120, Ohio 계약 확정, IB/게스트 가격 합의, UBS 90%=방 합의, GDP 25%=공식, GPU=2008, 속도조절=실제 감속, 월요일 방향.</div>
  </div>

  <h2>가져갈 세 문장</h2>
  <div class="hero">
    <b>1)</b> 소부장: 2Q 숫자보다 수주가 매출로 바뀌는 하반기, 그리고 2027 수주가 다시 증가하는지가 승부처다.<br/>
    <b>2)</b> SK: 할인율이 좁혀질 이유가 늘었다. 그래도 기본은 하이닉스와 이노베이션이다.<br/>
    <b>3)</b> 상단: 하이퍼스케일러 현금이 데이터센터나 토큰으로 다시 도느냐. 답이 나오면 박스가 열린다.
  </div>
  <div class="foot">원문 퀵코멘트·강의노트·하이브리드 모델을 주제별로 재구성. 실시간 시세·매수 추천이 아니다. — 준혁 · 2026-09-20</div>
</div>
</body>
</html>
"""


def write() -> Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html(), encoding="utf-8")
    return OUT


if __name__ == "__main__":
    p = write()
    print(f"Wrote {p} ({p.stat().st_size} bytes)")
