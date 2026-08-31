#!/usr/bin/env python3
"""Build the Hyundai Steel 2Q26 research dashboard from valuation.json."""

from __future__ import annotations

import json
from pathlib import Path

from analysis.valuation import ROOT, compute, load

OUT_HTML = ROOT / "dashboard" / "index.html"
OUT_JSON = ROOT / "output" / "valuation.json"


def won(n: float) -> str:
    return f"{int(round(n)):,}"


def build() -> dict:
    result = compute(load())
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    payload = json.dumps(result, ensure_ascii=False)
    OUT_HTML.write_text(HTML.replace("__VALUATION_JSON__", payload), encoding="utf-8")
    return result


HTML = r"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>현대제철 004020 · 2Q26 합성 목표주가</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&family=Noto+Serif+KR:wght@600;700&display=swap" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {
    --ink: #141820;
    --muted: #5c6570;
    --navy: #0e2a47;
    --navy-2: #1a3f66;
    --crimson: #c41e1e;
    --forest: #1b6b4a;
    --gold: #b8954a;
    --paper: #f3efe4;
    --card: #fffdf8;
    --line: #ddd6c8;
    --chip: #ece6d8;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--paper); color: var(--ink); font-family: "Noto Sans KR", sans-serif; }
  body { font-size: 15px; line-height: 1.55; }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 28px 20px 80px; }
  header.hero { background: var(--navy); color: #f7f1e4; border-radius: 18px; padding: 28px 32px 26px; position: relative; overflow: hidden; }
  header.hero:after { content: ""; position: absolute; right: -40px; top: -40px; width: 220px; height: 220px; border: 18px solid rgba(184,149,74,.25); border-radius: 50%; }
  .kicker { letter-spacing: .14em; font-size: 12px; color: var(--gold); font-weight: 700; }
  h1 { font-family: "Noto Serif KR", serif; font-size: 34px; margin: 8px 0 6px; font-weight: 700; }
  .sub { color: #c9d2dc; max-width: 720px; }
  .hero-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-top: 22px; }
  .kpi { background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.1); border-radius: 12px; padding: 14px 16px; }
  .kpi b { display: block; font-size: 28px; font-weight: 900; letter-spacing: -.03em; }
  .kpi span { display: block; font-size: 12px; color: #b7c2ce; margin-bottom: 4px; }
  .kpi.accent b { color: #f3c96b; }
  .kpi.up b { color: #8ee0b8; }
  section { margin-top: 28px; }
  h2 { font-family: "Noto Serif KR", serif; font-size: 22px; margin: 0 0 12px; color: var(--navy); }
  h3 { font-size: 15px; margin: 0 0 8px; color: var(--navy); }
  .card { background: var(--card); border: 1px solid var(--line); border-radius: 14px; padding: 18px 20px; }
  .grid-2 { display: grid; grid-template-columns: 1.15fr .85fr; gap: 14px; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
  .grid-5 { display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 10px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { padding: 8px 8px; border-bottom: 1px solid var(--line); text-align: right; vertical-align: top; }
  th:first-child, td:first-child { text-align: left; white-space: nowrap; }
  th { color: var(--muted); font-weight: 700; font-size: 11px; letter-spacing: .04em; }
  .take { background: #fff; border-left: 4px solid var(--gold); padding: 10px 14px; margin: 0 0 8px; }
  .chip { display: inline-block; background: var(--chip); border-radius: 999px; padding: 2px 8px; font-size: 11px; color: var(--navy); font-weight: 700; }
  .chip.buy { background: #e7f6ee; color: var(--forest); }
  .chip.cut { background: #fdecea; color: var(--crimson); }
  .chip.keep { background: #eef3f8; color: var(--navy-2); }
  .model { min-height: 0; }
  .model .who { font-size: 12px; color: var(--muted); }
  .model p { margin: 8px 0 0; font-size: 13px; color: #2c333a; }
  .bar-row { display: grid; grid-template-columns: 88px 1fr 72px; gap: 8px; align-items: center; margin: 8px 0; font-size: 12px; }
  .track { height: 14px; background: #efe8d8; border-radius: 99px; position: relative; }
  .fill { height: 100%; border-radius: 99px; background: var(--navy); }
  .mark { position: absolute; top: -3px; width: 2px; height: 20px; background: var(--crimson); }
  .ff { margin: 14px 0; }
  .ff-row { display: grid; grid-template-columns: 140px 1fr 70px; gap: 10px; align-items: center; margin: 12px 0; }
  .ff-track { position: relative; height: 18px; background: linear-gradient(90deg, #efe8d8, #d9e4d2); border-radius: 99px; }
  .ff-range { position: absolute; top: 4px; height: 10px; background: var(--navy); opacity: .85; border-radius: 99px; }
  .ff-mid { position: absolute; top: -2px; width: 4px; height: 22px; background: var(--gold); border-radius: 2px; }
  .ff-now { position: absolute; top: -5px; width: 0; height: 0; border-left: 5px solid transparent; border-right: 5px solid transparent; border-top: 7px solid var(--crimson); }
  .scenario { border-top: 4px solid var(--navy); }
  .scenario.bull { border-top-color: var(--forest); }
  .scenario.bear { border-top-color: var(--crimson); }
  .scenario .prob { color: var(--muted); font-size: 12px; }
  .scenario b.tp { font-size: 26px; display: block; margin: 6px 0; }
  ul.tight { margin: 8px 0 0; padding-left: 18px; }
  ul.tight li { margin: 4px 0; }
  .note { font-size: 12px; color: var(--muted); }
  footer { margin-top: 36px; color: var(--muted); font-size: 12px; border-top: 1px solid var(--line); padding-top: 14px; }
  canvas { max-height: 320px; }
  @media (max-width: 900px) {
    .hero-grid, .grid-2, .grid-3, .grid-5 { grid-template-columns: 1fr; }
    h1 { font-size: 26px; }
  }
</style>
</head>
<body>
<div class="wrap">
  <header class="hero">
    <div class="kicker">RESEARCH NOTE · 2Q26 REVIEW · 2026.08.31</div>
    <h1>현대제철 004020</h1>
    <p class="sub">5개 증권사 모델을 분해해 장점만 합성했습니다. 키움의 12mf PBR, 대신의 피어 산식, iM의 SOTP, 한화의 사업부 분해, 하나의 스프레드 경로를 한 가격으로 모았습니다.</p>
    <div class="hero-grid">
      <div class="kpi accent"><span>합성 목표주가</span><b id="tp">—</b></div>
      <div class="kpi"><span>투자의견</span><b id="rating">BUY</b></div>
      <div class="kpi up"><span>최근 종가 대비</span><b id="upside">—</b></div>
      <div class="kpi"><span>적용 12mf PBR</span><b id="tpPbr">—</b></div>
    </div>
  </header>

  <section>
    <h2>한 줄 결론</h2>
    <div class="take">2분기는 턴어라운드에 성공했지만 컨센서스(759억)를 <b>24% 하회</b>했습니다. 미스의 핵심은 자회사가 아니라 <b>별도 고로</b>입니다.</div>
    <div class="take">하반기 경로는 수렴합니다. 합성 3Q 영업이익 <b>1,143억</b>, 4Q <b>1,583억</b>. 차강판·후판 인상이 고로 스프레드를 되돌리는 그림입니다.</div>
    <div class="take">주가는 리포트 직후 24,800원에서 8/28 <b>31,000원</b>까지 이미 25% 반등했습니다. 남은 업사이드는 밸류업 발표와 3Q 확인입니다. 목표주가 <b>42,000원</b>, 상승여력 <b>35.5%</b>.</div>
  </section>

  <section>
    <h2>증권사 목표주가와 우리가 가져올 점</h2>
    <div class="grid-2">
      <div class="card"><canvas id="tpChart"></canvas><p class="note" style="margin-top:8px">빨간 점선: 8/28 종가 31,000원 · 금선: 합성 42,000원</p></div>
      <div class="card">
        <table id="brokerTable"></table>
        <p class="note">한화는 2Q 추정(728억)이 실제(577억)에 가장 가깝고, iM만 목표주가를 하향했습니다. 하나 5만원은 4Q 가정(2,379억)이 과합니다.</p>
      </div>
    </div>
    <div class="grid-5" style="margin-top:12px" id="modelCards"></div>
  </section>

  <section>
    <h2>2Q26 실적 — 무엇이 어긋났나</h2>
    <div class="grid-2">
      <div class="card">
        <table>
          <thead><tr><th>연결</th><th>잠정</th><th>컨센</th><th>괴리</th><th>QoQ</th><th>YoY</th></tr></thead>
          <tbody>
            <tr><td>매출액</td><td>6.11조</td><td>6.15조</td><td>-0.6%</td><td>+6.4%</td><td>+2.7%</td></tr>
            <tr><td>영업이익</td><td>577억</td><td>759억</td><td style="color:#c41e1e">-24%</td><td>+268%</td><td>-43%</td></tr>
            <tr><td>지배순이익</td><td>84억</td><td>166억</td><td style="color:#c41e1e">-49%</td><td>흑전</td><td>-75%</td></tr>
            <tr><td>별도 영업이익</td><td>111억</td><td>—</td><td>컨센 -66%</td><td>흑전</td><td>—</td></tr>
          </tbody>
        </table>
      </div>
      <div class="card">
        <h3>사업부 브릿지 (한화·하나·키움 합성)</h3>
        <ul class="tight">
          <li><b>봉형강 +</b> 판매 140만톤(+9%QoQ), ASP +6만원, 롤마진 약 +3만원. 전기로가 반등을 끌었습니다.</li>
          <li><b>고로 −</b> ASP +4.0만원 vs 투입원가 +4.5만원. 원료탄 시차 반영으로 스프레드가 줄었습니다.</li>
          <li><b>판매량</b> 442만톤(+4%QoQ)으로 고정비는 완화. 방향은 맞았고 강도가 부족했습니다.</li>
          <li><b>자회사</b> 일회성(IFC 매각, 관세 환급)이 소멸. 본업 미스가 핵심입니다.</li>
        </ul>
      </div>
    </div>
  </section>

  <section>
    <h2>분기 영업이익 경로 — 아웃라이어를 버린 합성</h2>
    <div class="card"><canvas id="opChart"></canvas>
      <p class="note">3Q는 iM 1,460억을, 4Q는 하나 2,379억을 절사. 합성 3Q 1,143억 → 4Q 1,583억. 연간 영업이익은 분기합 3,460억 전후.</p>
    </div>
  </section>

  <section>
    <h2>연간 추정치 분산</h2>
    <div class="grid-2">
      <div class="card"><canvas id="fyOpChart"></canvas></div>
      <div class="card">
        <table id="fyTable"></table>
        <p class="note">2027 영업이익은 대신 9,510억을 제외한 절사평균 6,081억을 사용합니다. ROE 2.8%를 그대로 쓰면 배수가 과해집니다.</p>
      </div>
    </div>
  </section>

  <section>
    <h2>목표주가 축구장 — 방법별 교집합</h2>
    <div class="card">
      <div class="note" style="margin-bottom:8px">막대 = 방법별 밴드 · 금색 막대 = 중앙값 · 빨간 삼각 = 최근 종가 31,000원</div>
      <div id="football"></div>
      <p class="note">12mf PBR·SOTP·증권사 품질가중이 4.2만원 부근에서 겹칩니다. EV/EBITDA만 미국 전기로 차입 부담으로 3.6만원까지 내려갑니다.</p>
    </div>
  </section>

  <section>
    <h2>가중 합성</h2>
    <div class="grid-2">
      <div class="card"><canvas id="weightChart"></canvas></div>
      <div class="card">
        <table id="weightTable"></table>
        <p class="note" style="margin-top:10px">가중 평균 원값 41,832원 → <b>42,000원</b>으로 반올림. 리포트 기준가 24,800원 대비 +69%, 8/28 종가 31,000원 대비 +35.5%.</p>
      </div>
    </div>
  </section>

  <section>
    <h2>시나리오</h2>
    <div class="grid-3" id="scenarios"></div>
  </section>

  <section>
    <h2>컨콜에서 가격에 남는 것</h2>
    <div class="grid-2">
      <div class="card">
        <h3>촉매</h3>
        <ul class="tight">
          <li>3~4분기 <b>기업가치 제고·주주환원</b> 발표. 11월 저PBR 하위 25% 명단.</li>
          <li>8월~27년 2월 내수 차강판 <b>최소 +5만원</b>, 조선 후판 인상 추진.</li>
          <li>3Q 원료 투입단가 하향 안정. 고로 ASP +3.8만원 vs 투입 +0.3만원(하나).</li>
          <li>AIDC 1GW당 18~20만톤, 메모리팹 1기당 10만톤. 전 강종 패키지 수주.</li>
          <li>당진 복합 프로세스 양산, 탄소 −20% 강판. K-스틸법 지원 근거.</li>
        </ul>
      </div>
      <div class="card">
        <h3>리스크</h3>
        <ul class="tight">
          <li>중국 완제품 수출 월 1천만톤 상회, 하반기 내수 부진 시 아시아 가격 재약세.</li>
          <li>건설 수요는 반도체 클러스터로 소폭 회복에 그치고 절대량은 과거 평균 하회.</li>
          <li>2026~28년 연간 Capex 2조원대, 순차입금 7조 상회. 미국 전기로 회수 시차.</li>
          <li>중국산 H형강 반덤핑 재심 연장 불발 시 형강 믹스 악화.</li>
          <li>ROE가 2%를 넘기지 못하면 0.30x 재평가는 지연됩니다.</li>
        </ul>
      </div>
    </div>
  </section>

  <footer>
    자료: 키움·한화·하나·대신·iM 2Q26 리포트(2026.08.04), 현대제철 컨콜, FnGuide(컨센 목표주가 44,182원 / 17개사, 종가 31,000원 2026.08.28).
    본 문서는 공개 리포트의 재구성이며 투자 권유가 아닙니다. 합성 목표주가는 모델 가정의 결과입니다.
  </footer>
</div>
<script id="valuation" type="application/json">__VALUATION_JSON__</script>
<script>
const V = JSON.parse(document.getElementById("valuation").textContent);
const won = n => Math.round(n).toLocaleString("ko-KR");
document.getElementById("tp").textContent = won(V.target.tp) + "원";
document.getElementById("rating").textContent = V.target.rating;
document.getElementById("upside").textContent = "+" + V.target.upside_vs_latest + "%";
document.getElementById("tpPbr").textContent = V.target.target_pbr + "x";

const brokerRows = V.brokers.map(b => {
  const act = b.tp_action === "하향" ? "cut" : b.tp_action === "재개" ? "keep" : "keep";
  return `<tr>
    <td>${b.name}<br><span class="chip ${act}">${b.tp_action}</span></td>
    <td>${won(b.tp)}</td>
    <td>${b.method}</td>
    <td>${b.q3_op}</td>
    <td>${b.y2026.op}</td>
    <td>${b.y2027.op}</td>
  </tr>`;
}).join("");
document.getElementById("brokerTable").innerHTML = `
  <thead><tr><th>증권사</th><th>TP</th><th>산식</th><th>3Q OP</th><th>26 OP</th><th>27 OP</th></tr></thead>
  <tbody>${brokerRows}
    <tr><td><b>합성</b></td><td><b>${won(V.target.tp)}</b></td><td>4방법 가중</td><td>${V.blend.q3_op}</td><td>${V.blend.fy26_op}</td><td>${V.blend.fy27_op}</td></tr>
  </tbody>`;

document.getElementById("modelCards").innerHTML = V.brokers.map(b => `
  <div class="card model">
    <div class="who">${b.analyst}</div>
    <h3>${b.name} · ${won(b.tp)}</h3>
    <span class="chip buy">가져올 점</span>
    <p>${b.strength}</p>
    <span class="chip cut" style="margin-top:8px">버릴 점</span>
    <p>${b.weakness}</p>
  </div>`).join("");

const fyBody = V.brokers.map(b => `<tr>
  <td>${b.name}</td><td>${b.y2026.op}</td><td>${b.y2027.op}</td>
  <td>${b.y2026.eps}</td><td>${b.y2026.bps}</td><td>${b.y2026.roe}%</td>
</tr>`).join("");
document.getElementById("fyTable").innerHTML = `
  <thead><tr><th></th><th>26E OP</th><th>27E OP</th><th>26E EPS</th><th>26E BPS</th><th>26E ROE</th></tr></thead>
  <tbody>${fyBody}
    <tr><td><b>합성</b></td><td><b>${V.blend.fy26_op}</b></td><td><b>${V.blend.fy27_op}</b></td>
    <td>${V.blend.fy26_eps}</td><td>${V.blend.fy26_bps}</td><td>—</td></tr>
  </tbody>`;

const methods = V.methods;
const axisMin = 20000, axisMax = 52000;
const scale = v => ((v - axisMin) / (axisMax - axisMin) * 100);
const now = V.meta.price_latest;
document.getElementById("football").innerHTML = methods.map(m => `
  <div class="ff-row">
    <div>${m.name}<div class="note">${m.source}</div></div>
    <div class="ff-track">
      <div class="ff-range" style="left:${scale(m.low)}%;width:${scale(m.high)-scale(m.low)}%"></div>
      <div class="ff-mid" style="left:${scale(m.mid)}%"></div>
      <div class="ff-now" style="left:${scale(now)}%"></div>
    </div>
    <div style="text-align:right;font-weight:700">${won(m.mid)}</div>
  </div>`).join("");

const wBody = methods.filter(m => m.weight > 0).map(m => `<tr>
  <td>${m.name}</td><td>${won(m.mid)}</td><td>${(m.weight*100).toFixed(0)}%</td>
  <td>${won(m.mid * m.weight)}</td>
</tr>`).join("");
document.getElementById("weightTable").innerHTML = `
  <thead><tr><th>방법</th><th>중앙값</th><th>가중</th><th>기여</th></tr></thead>
  <tbody>${wBody}<tr><td><b>목표주가</b></td><td colspan="3"><b>${won(V.target.tp)}원</b></td></tr></tbody>`;

document.getElementById("scenarios").innerHTML = V.scenarios.map(s => `
  <div class="card scenario ${s.id}">
    <div class="prob">${s.name} · 확률 ${(s.prob*100).toFixed(0)}%</div>
    <b class="tp">${won(s.tp)}원</b>
    <div class="note">PBR ${s.pbr}x</div>
    <p>${s.thesis}</p>
  </div>`).join("");

const navy = "#0e2a47", gold = "#b8954a", crimson = "#c41e1e";
const names = V.brokers.map(b => b.name);
new Chart(document.getElementById("tpChart"), {
  type: "bar",
  data: {
    labels: names,
    datasets: [{
      label: "목표주가",
      data: V.brokers.map(b => b.tp),
      backgroundColor: ["#1a3f66","#245886","#0e2a47","#3a6a93","#6b4a2a"]
    }]
  },
  options: {
    indexAxis: "y",
    plugins: {
      legend: { display: false },
      annotation: {}
    },
    scales: {
      x: {
        min: 20000, max: 52000,
        grid: { color: "#eee6d6" },
        ticks: { callback: v => (v/1000)+"k" }
      },
      y: { grid: { display: false } }
    }
  },
  plugins: [{
    id: "refLines",
    afterDraw(chart) {
      const {ctx, chartArea, scales} = chart;
      const draw = (xVal, color) => {
        const x = scales.x.getPixelForValue(xVal);
        ctx.save();
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.setLineDash([5,4]);
        ctx.beginPath(); ctx.moveTo(x, chartArea.top); ctx.lineTo(x, chartArea.bottom); ctx.stroke();
        ctx.restore();
      };
      draw(31000, crimson);
      draw(42000, gold);
    }
  }]
});

new Chart(document.getElementById("opChart"), {
  type: "bar",
  data: {
    labels: V.q_path.labels,
    datasets: [
      { type: "line", label: "합성", data: V.q_path.actual_or_blend, borderColor: gold, backgroundColor: gold, tension: .25, pointRadius: 5 },
      ...V.brokers.map((b, i) => ({
        type: "bar",
        label: b.name,
        data: [null, null, b.q3_op, b.q4_op],
        backgroundColor: ["#1a3f66","#4a7ca8","#0e2a47","#7a9bb8","#b8954a"][i],
        hidden: false
      }))
    ]
  },
  options: {
    plugins: { legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 11 } } } },
    scales: { y: { title: { display: true, text: "영업이익 십억원" }, grid: { color: "#eee6d6" } } }
  }
});

new Chart(document.getElementById("fyOpChart"), {
  type: "bar",
  data: {
    labels: names,
    datasets: [
      { label: "2026E OP", data: V.brokers.map(b => b.y2026.op), backgroundColor: navy },
      { label: "2027E OP", data: V.brokers.map(b => b.y2027.op), backgroundColor: gold }
    ]
  },
  options: {
    plugins: { legend: { position: "bottom" } },
    scales: { y: { title: { display: true, text: "십억원" }, grid: { color: "#eee6d6" } } }
  }
});

new Chart(document.getElementById("weightChart"), {
  type: "doughnut",
  data: {
    labels: methods.filter(m => m.weight>0).map(m => m.name),
    datasets: [{
      data: methods.filter(m => m.weight>0).map(m => m.weight),
      backgroundColor: [navy, "#3a6a93", "#7a9bb8", gold]
    }]
  },
  options: { plugins: { legend: { position: "bottom" } }, cutout: "58%" }
});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    r = build()
    print(f"wrote {OUT_HTML}")
    print(f"TP {r['target']['tp']}")
