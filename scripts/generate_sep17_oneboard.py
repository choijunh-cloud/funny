#!/usr/bin/env python3
"""9월 17일 퀵코멘트+PDF를 한 장 보드로 합친다. 차트는 base64 내장."""

from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path("/workspace")
CHARTS = ROOT / "lectures" / "assets" / "sep17"
OUT = ROOT / "lectures" / "9월 17일 AI·반도체 시장 코멘트 한장.html"
def uri(name: str) -> str:
    raw = (CHARTS / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def html() -> str:
    c1, c2, c3, c4 = (
        uri("01_fomc_dots.png"),
        uri("04_macro_vs_chips.png"),
        uri("02_dc_power_gap.png"),
        uri("03_ai_server_share.png"),
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>9월 17일 AI·반도체 시장 코멘트 — 한 장</title>
<style>
:root {{ --navy:#0f2043; --navy2:#1e407c; --gold:#b8943a; --ink:#1a1a1a;
  --muted:#4b5563; --line:#d5dce6; --bg:#eef1f7; --green:#166534; --red:#991b1b; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--bg); color:var(--ink);
  font-family:"WenQuanYi Micro Hei","Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif; }}
.board {{ width:1240px; margin:0 auto; padding:14px 14px 16px; }}
.kicker {{ color:var(--gold); font-weight:800; font-size:11.5px; letter-spacing:.03em; }}
h1 {{ color:var(--navy); font-size:24px; line-height:1.22; margin:3px 0 8px; }}
.hero {{ background:var(--navy); color:#fff; border-radius:12px; padding:11px 14px; margin-bottom:8px; font-size:13.4px; line-height:1.48; }}
.hero b {{ color:var(--gold); }}
.kpi {{ display:grid; grid-template-columns:repeat(6,1fr); gap:6px; margin-bottom:8px; }}
.kpi div {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:7px 8px; }}
.kpi h3 {{ margin:0; font-size:10.5px; color:var(--navy2); font-weight:800; }}
.kpi .n {{ font-size:16px; font-weight:800; color:var(--navy); margin-top:2px; }}
.kpi p {{ margin:2px 0 0; font-size:10.6px; color:var(--muted); line-height:1.28; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:10px 11px; }}
.card.wide {{ grid-column:1/-1; }}
.card h2 {{ margin:0 0 5px; color:var(--navy); font-size:14.5px; border-bottom:2px solid var(--navy); padding-bottom:3px; }}
.card p, .card li {{ font-size:12px; line-height:1.4; margin:0 0 4px; }}
.card ul {{ margin:0 0 4px; padding-left:16px; }}
img {{ width:100%; border-radius:8px; border:1px solid var(--line); display:block; margin:4px 0; background:#fff; }}
table {{ width:100%; border-collapse:collapse; font-size:11.2px; margin:4px 0; }}
th {{ background:var(--navy); color:#fff; padding:3px 6px; text-align:left; }}
td {{ padding:3px 6px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:nth-child(even) td {{ background:#f7f9fc; }}
.pos {{ color:var(--green); font-weight:700; }}
.neg {{ color:var(--red); font-weight:700; }}
.note,.ok,.risk,.blue {{ padding:6px 8px; border-radius:0 8px 8px 0; font-size:11.6px; margin:5px 0 0; line-height:1.38; }}
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
.foot {{ color:var(--muted); font-size:10.5px; margin-top:7px; text-align:right; }}
</style>
</head>
<body>
<div class="board">
  <div class="kicker">2026.09.17  ·  FOMC 다음날  ·  퀵코멘트 + 첨부 13개 PDF  ·  한 장</div>
  <h1>각도는 낮춰도 수요는 유지 — Agent 배포 · Ohio 탐색 · 전력 161GW</h1>
  <div class="hero">
    <b>한 장.</b> 이번 인상은 침체형이 아니다. 강한 경기 + 인플레 + AI 자본수요.
    속도조절은 개발 <b>각도</b>다. 45도에서 35도로 낮춰도 7월까지 보던 수요는 안 줄어든다.
    DevDay(9/29)는 더 똑똑한 모델이 아니라 <b>Agent 사용량 · API 토큰 · 기업 배포</b>.
    하이닉스–인텔 오하이오는 <b>탐색</b>. 전력 161GW는 사실. AEMA는 병목 완화이지 변압기 대체가 아니다.
  </div>

  <div class="kpi">
    <div><h3>FOMC</h3><div class="n">3.75–4.00%</div><p>+25bp 만장일치 · 중앙값 4.1 / 4.1 / 3.9</p></div>
    <div><h3>GDP / Core PCE</h3><div class="n">2.3 → 2.4</div><p>27년 Core PCE 2.5 유지</p></div>
    <div><h3>9/16 美</h3><div class="n">10Y 5.04%</div><p>WTI $105.8 · S&amp;P −0.45 · SOX +0.4</p></div>
    <div><h3>KOSPI</h3><div class="n">6,717.97</div><p>+1.37% · 닉스 +4.08% · 삼전 +2.01%</p></div>
    <div><h3>DevDay</h3><div class="n">9/29</div><p>Fort Mason · 모델보다 Agent</p></div>
    <div><h3>DC 전력</h3><div class="n">161GW</div><p>2026 +31% · 2030 종이갭 268GW</p></div>
  </div>

  <div class="grid">
    <div class="card">
      <h2>1. FOMC — 인상은 선반영, 경로는 중앙값</h2>
      <img src="{c1}" alt="FOMC 점도표 중앙값"/>
      <table>
        <tr><th></th><th>26</th><th>27</th><th>28</th><th>장기</th></tr>
        <tr><td>기금 중앙값</td><td>4.1</td><td>4.1</td><td>3.9</td><td>3.2</td></tr>
        <tr><td>6월</td><td>3.8</td><td>3.6</td><td>3.4</td><td>3.1</td></tr>
        <tr><td>GDP</td><td>2.3</td><td>2.4</td><td>2.2</td><td>2.0</td></tr>
        <tr><td>Core PCE</td><td>3.4</td><td>2.5</td><td>2.2</td><td>—</td></tr>
      </table>
      <p><span class="tag f">사실</span>Warsh는 자기 점을 안 냈다. 27년 성장 2.4 &gt; 26년 2.3.</p>
      <p><span class="tag p">부분</span>‘올해 1회 후 내년 동결’은 중앙값. 27년 4.375 점이 8명. 장기 3.0은 중앙값 3.2.</p>
      <div class="blue">침체형 인상이 아니다. 2022년과 구별. 상단이 보이면 스마트머니는 미리 움직인다. 지금 당장 성장주 프리미엄이 돌아온다는 뜻은 아니다.</div>
    </div>
    <div class="card">
      <h2>2. 9/16 — 매크로 부담, 반도체 차별화</h2>
      <img src="{c2}" alt="유가·지수 vs 반도체"/>
      <ul>
        <li>WTI $105.83 · 브렌트 $108.75 · 10년 장중 5.041%.</li>
        <li>SOX 약 <span class="pos">+0.4%</span>. 코멘트 +0.5~0.6는 약간 큼.</li>
        <li>KOSPI <span class="pos">6,717.97 (+1.37%)</span> 4일 하락 종료. 기관 +1.21조, 외인 −1.68조.</li>
        <li>하이닉스 <span class="pos">+4.08%</span> / 삼성 <span class="pos">+2.01%</span> (코멘트 +3.6/+1.8은 종가보다 작음).</li>
        <li>카카오페이 약 <span class="neg">−11.5%</span> — CLARITY 절차표결 부결.</li>
      </ul>
      <div class="note">웰스파고 S&amp;P 7,950→7,700. 근거는 주식 비중 72%와 금리 5%. AI 수요 둔화가 아니다.</div>
      <div class="ok">유가·금리 최악 조합에서도 SOX 플러스, 코스피 6,700 지지.</div>
    </div>

    <div class="card">
      <h2>3. 속도조절 — 각도는 낮춰도 수요 100</h2>
      <div class="flow"><span>35도 4–6월</span><i>→</i><span>45도+ Astra</span><i>→</i><span>30~35도 조절</span><i>→</i><span>수요 100 유지</span></div>
      <p>속도조절 얘기 자체가 속도가 너무 빨라서 나왔다. 프론티어 학습을 숨 고르기 해도 <b>추론·에이전트</b>가 더 크고 더 빠르다. 가드레일 보강 자체도 연산을 늘린다.</p>
      <p>이미 만든 프론티어만으로도 수요가 넘친다. 모델사 베스트는 비싼 Astra급을 잠시 늦추고 토큰 매출에 집중하는 것. 중국이 같이 멈춰 줄지는 별개.</p>
      <div class="note">“지금 동결해도 활용 가치는 전체의 5~10%.” 속도조절 ≠ AI 중단.</div>
      <div class="ok">Broadcom Hock Tan: 27–28 전망 수정 이유 없다. Anthropic이 최대 커스텀 칩 고객. Peak-out보다 Duration Extension.</div>
    </div>
    <div class="card">
      <h2>4. DevDay 9/29 — 모델보다 Agent</h2>
      <p><span class="tag f">사실</span>화 9/29 Fort Mason. 키노트 10:00 PT, Sam Altman, 라이브 무료. 공식은 개발자·API·도구 배포.</p>
      <table>
        <tr><th>축</th><th>내용</th><th>인프라</th></tr>
        <tr><td>Agent</td><td>답변 → 웹·코딩·업무</td><td>토큰·추론량</td></tr>
        <tr><td>API</td><td>기업 서비스에 탑재</td><td>AI 서버</td></tr>
        <tr><td>배포</td><td>실험 → 기업 업무</td><td>GPU·DRAM·HBM</td></tr>
      </table>
      <div class="flow"><span>Astra 배포</span><i>→</i><span>DevDay</span><i>→</i><span>Agent 대량 깔림</span></div>
      <div class="blue">확인할 셋: Agent 사용량 · API/토큰 · 기업 배포. 확인되면 캡엑스는 학습 GPU에서 <b>추론 컴퓨팅+메모리</b>로 확장.</div>
      <p>벤치마크 95%가 20턴이면 36%. 실전은 재시도. 평가가 IQ에서 업무 성공률로 이동. <span class="tag i">해석</span></p>
    </div>

    <div class="card">
      <h2>5. 하이닉스–인텔 — Ohio 탐색, Base Die는 별축</h2>
      <p><span class="tag f">사실</span>Reuters 9/16: 미국 첫 메모리 생산 탐색. ①Ohio 임차 ②인텔+대형 CSP JV. 하이닉스 “결정 없다”, 인텔 “추측”. 제품 종류 미확인.</p>
      <table>
        <tr><th></th><th>하는 일</th><th>수요</th><th>지금</th></tr>
        <tr><td>A Base Die</td><td>로직 Base Die</td><td>선단 로직 장비</td><td>Ohio와 별개</td></tr>
        <tr><td>B DRAM</td><td>웨이퍼 전공정</td><td>장비 대규모</td><td>파급 최대·미확정</td></tr>
        <tr><td>C HBM</td><td>DRAM→HBM</td><td>후공정</td><td>미확정</td></tr>
        <tr><td>D 패키징</td><td>HBM 패키징</td><td>본딩·검사</td><td>인디애나가 이미</td></tr>
      </table>
      <div class="flow"><span>한국 DRAM</span><i>→</i><span>Ohio?</span><i>→</i><span>Indiana HBM</span><i>→</i><span>Intel Base Die?</span></div>
      <div class="risk">뉴스로 소부장을 바로 연결하지 말 것. Base Die → EMIB → Ohio 계약을 단계로. 단수 ↓ ≠ 수요 ↓. 8단 옵션은 확인, NVIDIA 12→8 전면 전환은 관측. Base Die 가치는 컨트롤러/IP로 갈 수 있다.</div>
    </div>
    <div class="card">
      <h2>6. 전력 TAM + AEMA — 유연 부하, 대체 아님</h2>
      <img src="{c3}" alt="데이터센터 전력 수요 vs 그리드"/>
      <img src="{c4}" alt="AI 서버 전력 비중"/>
      <p><span class="tag f">사실</span>TrendForce: 2026 161GW(+31%), AI 서버 33.4%. 2028부터 그리드 갭. 2030 490.7 vs 그리드 222.6. 종이 갭 268GW(미국 170+). BTM은 분모에 없음.</p>
      <p><span class="tag f">사실</span>AEMA 9/16 NVIDIA·Google·Emerald AI. 평소 500MW → 부족 시 350–400. 100GW는 동맹 주장.</p>
      <div class="blue">DC가 늘면 절대 전력·변압기는 같이 는다. AEMA는 병목을 깎는다. 리드타임: ABF 48–56주, HDD 50주, DRAM 20주. GPU는 균형.</div>
    </div>

    <div class="card wide">
      <h2>7. 개별 · 포트 · 확인 셋</h2>
      <div class="grid">
        <div>
          <ul>
            <li><b>삼성</b> Taylor Tesla AI 칩 시제품. cHBM Base Die 2-track.</li>
            <li><b>두산</b> 3년 7,551억 고급 CCL. 가동률 100%+.</li>
            <li><b>대덕전자</b> Tesla·Marvell·Renesas LTA. 선수금&gt;8,000억 전언. 기판 LTA는 Take or Pay보다 약함.</li>
            <li><b>하나마이크론</b> 베트남 4Q26. 비메모리 확대. P/E 10배 이하.</li>
            <li><b>마이크론</b> 512GB DDR5, 27H2. 신규 capa 2028 이후. FY27 캡엑스 $450억+.</li>
            <li><b>조선 3사</b> OP +30%, 시총 −39%, 12M P/E 14배 미만. 엔진·FDC·함정이 수주로 확인돼야 리레이팅.</li>
            <li><b>올릭스</b> 오버행보다 4Q ALK7 경쟁사 데이터와 L/O.</li>
          </ul>
        </div>
        <div>
          <div class="blue">바벨 예: AI 40–50 / Non-AI 30 / 현금성 20–30. 7월 말 바닥은 지났다. 6,000 쌍바닥은 새 악재가 필요하다.</div>
          <p>다음 숫자 <b>10/1 마이크론</b>. Anthropic IPO 10–11월은 수급. 중간선거 11/3. Blue Wave ≠ 전국 DC 중단.</p>
          <p>원/달러 1,300원대 초반이 바닥이었을 가능성. 4Q 대미투자 달러 수요. 백화점 외인. 원화 강세 배팅은 재검토.</p>
          <p>공포·가드레일은 빅테크에 맡기지 말 것. FACT는 컴퓨팅이 턱없이 부족하다는 것. 투자로 번역할 것은 멸종 10%가 아니라 규제화 → 개발 속도 → 그래도 추론 수요.</p>
        </div>
      </div>
      <div class="hero" style="margin:8px 0 0;">
        <b>가을 확인 셋.</b> DevDay에서 에이전트가 얼마나 깔리는지 · Ohio와 Base Die가 계약이 되는지 · 전력을 그리드+BTM+유연부하로 얼마나 메우는지.
      </div>
    </div>
  </div>
  <div class="foot">사실=연준 SEP·거래소·OpenAI·Reuters·TrendForce. 부분=방향은 맞지만 숫자·범위가 다름. 쓰지 말 것=Ohio 확정 · 12→8단 전면전환 · AEMA=전력기기 소멸 · 속도조절=캡엑스 종료.</div>
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
