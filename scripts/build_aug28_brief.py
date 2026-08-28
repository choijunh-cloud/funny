#!/usr/bin/env python3
"""8월 28일 Quick 코멘트 전체 HTML 브리핑 생성."""

from __future__ import annotations

import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from aug28_raw_comments import PDF_RAW, RAW

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "reports" / "2026-08-28-quick-comment-brief.html"


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def raw_block(time: str, title: str, body: str) -> str:
    return (
        f'<details class="raw" open><summary><span class="time">{esc(time)}</span> · {esc(title)}</summary>'
        f'<div class="body">{esc(body)}</div></details>\n'
    )


def pdf_block(title: str, body: str) -> str:
    return (
        f'<details class="raw" open><summary>{esc(title)}</summary>'
        f'<div class="body">{esc(body)}</div></details>\n'
    )


CSS = r"""
    :root {
      --navy: #0f2043;
      --navy2: #1e407c;
      --gold: #b8943a;
      --gray: #4b5563;
      --bg: #f3f5fa;
      --card: #ffffff;
      --ok: #166534;
      --ok-bg: #e8f5e9;
      --warn: #7a5c12;
      --warn-bg: #fff8e7;
      --bad: #991b1b;
      --bad-bg: #fdecea;
      --blue: #1e407c;
      --blue-bg: #e8f1fb;
      --purple: #6b21a8;
      --purple-bg: #f3e8ff;
      --line: #d7deea;
    }
    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; }
    body {
      margin: 0;
      font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR", "WenQuanYi Micro Hei", sans-serif;
      background: var(--bg);
      color: #1a1a1a;
      line-height: 1.58;
    }
    .top {
      position: sticky; top: 0; z-index: 20;
      background: var(--navy);
      color: #fff;
      box-shadow: 0 2px 10px rgba(15,32,67,.18);
    }
    .top-inner { max-width: 1080px; margin: 0 auto; padding: 10px 18px 12px; }
    .brand { font-size: 12px; letter-spacing: .08em; opacity: .75; }
    .brand b { font-size: 15px; letter-spacing: 0; opacity: 1; }
    nav { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
    nav a {
      color: #dbe4f5; text-decoration: none;
      font-size: 12px; font-weight: 700;
      padding: 4px 8px; border-radius: 999px;
      background: rgba(255,255,255,.08);
    }
    nav a:hover { background: var(--gold); color: var(--navy); }
    .wrap { max-width: 1080px; margin: 0 auto; padding: 28px 18px 90px; }
    header { text-align: center; margin: 8px 0 22px; }
    h1 { color: var(--navy); font-size: 30px; margin: 6px 0 8px; letter-spacing: -0.03em; }
    .sub { color: var(--navy2); font-weight: 800; font-size: 17px; }
    .muted { color: var(--gray); font-size: 13.5px; }
    h2 {
      color: var(--navy);
      border-bottom: 3px solid var(--navy);
      padding-bottom: 6px;
      margin-top: 42px;
      font-size: 23px;
    }
    h3 { color: var(--navy2); margin-top: 20px; font-size: 16.5px; }
    .kpis { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 16px 0 8px; }
    .kpi {
      background: #fff; border-radius: 12px;
      padding: 12px 12px 14px;
      border: 1px solid var(--line);
    }
    .kpi span { display: block; font-size: 12px; color: var(--gray); font-weight: 700; }
    .kpi b { display: block; font-size: 19px; color: var(--navy); margin-top: 4px; letter-spacing: -0.03em; }
    .kpi em { font-style: normal; font-size: 12px; color: var(--gray); }
    .kpi.down b { color: var(--bad); }
    .kpi.up b { color: var(--ok); }
    .kpi.warn b { color: #c2410c; }
    .card {
      background: var(--card);
      border-radius: 12px;
      padding: 14px 16px;
      box-shadow: 0 1px 2px rgba(15,32,67,.06);
      margin: 12px 0;
      border: 1px solid #eef1f6;
    }
    .key { border-left: 6px solid var(--navy); background: #eef2f8; }
    .ok { border-left: 6px solid var(--ok); background: var(--ok-bg); }
    .warn { border-left: 6px solid var(--gold); background: var(--warn-bg); }
    .bad { border-left: 6px solid var(--bad); background: var(--bad-bg); }
    .blue { border-left: 6px solid var(--navy2); background: var(--blue-bg); }
    .purple { border-left: 6px solid var(--purple); background: var(--purple-bg); }
    .label { font-size: 12px; font-weight: 800; margin-bottom: 6px; letter-spacing: .02em; }
    .scrollx { overflow-x: auto; -webkit-overflow-scrolling: touch; }
    table { width: 100%; border-collapse: collapse; background: #fff; font-size: 14px; margin: 10px 0 16px; }
    th { background: var(--navy); color: #fff; padding: 8px 10px; text-align: left; }
    td { padding: 8px 10px; border-bottom: 1px solid #e5eaf1; vertical-align: top; }
    tr:nth-child(even) td { background: #f7f9fc; }
    img.chart {
      width: 100%;
      border-radius: 12px;
      background: #fff;
      margin: 8px 0 4px;
      border: 1px solid var(--line);
    }
    .cap { text-align: center; color: var(--gray); font-size: 12.5px; margin: 0 0 16px; }
    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
    ul { padding-left: 20px; margin: 8px 0; }
    ol { padding-left: 22px; margin: 8px 0; }
    li { margin: 4px 0; }
    .time { color: var(--gold); font-weight: 800; font-variant-numeric: tabular-nums; }
    details.raw {
      background: #fff; border: 1px solid var(--line); border-radius: 12px;
      margin: 8px 0; padding: 0 14px;
    }
    details.raw summary {
      cursor: pointer; font-weight: 800; color: var(--navy);
      padding: 12px 0;
    }
    details.raw .body { padding-bottom: 14px; color: #222; font-size: 14.5px; white-space: pre-wrap; }
    footer.note {
      margin-top: 48px; padding-top: 16px;
      border-top: 1px solid var(--line);
      color: var(--gray); font-size: 13px;
    }
    .flow {
      font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
      font-size: 13px; line-height: 1.45;
      background: #0f2043; color: #e8eef8;
      padding: 14px 16px; border-radius: 12px; overflow-x: auto;
      white-space: pre-wrap;
    }
    @media (max-width: 820px) {
      .kpis, .grid, .grid3 { grid-template-columns: 1fr 1fr; }
      h1 { font-size: 24px; }
    }
    @media (max-width: 560px) {
      .kpis, .grid, .grid3 { grid-template-columns: 1fr; }
    }
    .print-only { display: none; }
    @media print {
      @page { size: A4; margin: 11mm 10mm 13mm; }
      html { scroll-behavior: auto; }
      body { background: #fff; }
      .top, nav { display: none; }
      .print-only { display: block; color: var(--gray); font-size: 11.5px; text-align: center; margin: 0 0 10px; }
      .wrap { max-width: none; padding: 0 0 6mm; }
      header { margin: 0 0 10px; }
      h1 { font-size: 20px; margin: 4px 0 6px; }
      h2 { font-size: 15px; margin-top: 12px; break-after: avoid; page-break-after: avoid; }
      h3 { font-size: 13px; break-after: avoid; page-break-after: avoid; }
      .sub { font-size: 13px; }
      .kpis { gap: 6px; margin: 8px 0 6px; }
      .kpi { padding: 8px; break-inside: avoid; page-break-inside: avoid; }
      .kpi b { font-size: 13px; }
      .kpi em, .kpi span { font-size: 10.5px; }
      .card { margin: 8px 0; padding: 10px 12px; }
      .grid > .card, .grid3 > .card, .kpi { break-inside: avoid; page-break-inside: avoid; }
      img.chart {
        break-inside: avoid; page-break-inside: avoid;
        max-height: 86mm; object-fit: contain; object-position: top;
      }
      table { font-size: 10.5px; }
      th, td { padding: 4px 6px; }
      a { color: inherit; text-decoration: none; }
      details.raw { border: none; padding: 0; break-inside: avoid; }
      details.raw summary { display: block; padding: 6px 0 2px; }
      details.raw { break-inside: auto; }
      details.raw .body { display: block !important; font-size: 10.5px; white-space: pre-wrap; }
      footer.note { break-inside: avoid; font-size: 11px; }
    }
"""

BODY = r"""
    <header>
      <div class="muted">2026. 8. 28 Quick 코멘트 · 8/27 저녁 19:43–23:48 + 8/28 05:38–15:09 · 첨부 PDF 5건 · 원문을 주제별로 재배치하고 부록에 한 글자도 빼지 않고 보관</div>
      <h1>+70%는 수요 상한이 아니라 공급 상한</h1>
      <div class="sub">525조 중 엔비디아 315 + HBM 81 · 나머지 130조 · 스윙은 비CSP</div>
      <p class="muted">매수·매도 추천이 아니다. 화장품 워드파일은 첨부에 없었고 11:02–11:05 코멘트로 정리했다. 11:02 실리콘투 문안은 에이피알과 중복 첨부된 원문 그대로 보관한다. 수치 중 EPS $2.46·컨센 매출 $92.29B는 오늘 첨부 PDF 기준이다.</p>
      <p class="print-only">PDF · 2026. 8. 28 · Quick 코멘트·PDF 5건 전부 수록 · 매수·매도 추천 아님</p>
    </header>

    <div class="kpis">
      <div class="kpi up"><span>NVDA 매출 / EPS</span><b>$96.22B / $2.46</b><em>컨센 $92.29B / $2.09 · GPM 75.0%</em></div>
      <div class="kpi up"><span>3Q / FY28</span><b>$108B ±2% / +70%</b><em>중국 DC 제외 · 수요는 약 +100%</em></div>
      <div class="kpi warn"><span>GPM 경로</span><b>75 → 71~72 → 72~73</b><em>FY28 1Q 가격 인상 · 서버+15%≠GPU+15%</em></div>
      <div class="kpi"><span>2027 CAPEX 증가</span><b>+525조</b><em>NVDA 315 · HBM 81 · 잔여 130</em></div>
    </div>
    <div class="kpis">
      <div class="kpi up"><span>미 본장 NVDA / SOX</span><b>+8.7% / +2.33%</b><em>나스닥 26,541 · 메모리는 시큰둥</em></div>
      <div class="kpi up"><span>코스피 / 코스닥</span><b>+1.5% / +1.6%</b><em>외인 선물 1.5조+ · 한은 3.00%</em></div>
      <div class="kpi warn"><span>효성 GS TP</span><b>416만 (+48.7%)</b><em>컨센 425만 · 안전마진 20%밖</em></div>
      <div class="kpi"><span>하이닉스 본주 PER</span><b>26년 4.9 / 27년 4.0</b><em>본주 173만 · ADR 프리미엄 29%</em></div>
    </div>

    <section id="thesis">
      <h2>0. 한 장으로 읽는 오늘</h2>
      <div class="card key">
        엔비디아는 1년 앞 가이던스를 처음 냈다. FY28 +70%(시장 +40% 중반). 실제 수요는 약 +100%라 숫자는 공급 천장에 가깝다.
        메모리 원가로 GPM은 75%에서 71~72%까지 내려가지만 FY28 1Q 가격 인상 후 72~73%로 되돌린다.
        AI 서버 가격 +15%가 GPU ASP +15%는 아니다. 상승분 상당수는 SK하이닉스·삼성전자·마이크론 ASP다.
        Top 5 Hyperscaler CAPEX +525조에서 엔비디아 315조, HBM 81조를 빼면 나머지 부품 예산은 약 130조.
        그래서 CSP만 보면 2027 DRAM/eSSD 추가 폭등은 어렵다. Neo Cloud · Sovereign AI · Enterprise · Industrial이 가격의 핵심 변수다.
      </div>
      <div class="grid">
        <div class="card blue">
          <div class="label">미국장 (05:38 / 06:32)</div>
          엔비디아 +8.7%가 SOX +2.33%보다 훨씬 강했다. GPU→네트워크(크레도 +6.1%, 아스트라 +4.3%, 브로드컴 +4.5%).
          마이크론 −0.3%, 샌디스크 −1.0%, 마벨 −1.5%. 메모리 랠리가 아니라 AI 투자 지속성 베팅.
          소프트웨어(세일즈포스 +22%, 크라우드스트라이크 +20.5%, 옥타 +28.6%)도 동반.
        </div>
        <div class="card ok">
          <div class="label">국내장 (23:46)</div>
          코스피 갭상승 후 +1.5%대, 코스닥 +1.6%대. 삼전닉스 장중 반납, 소부장·전력·전지가 받쳤다.
          한은 기준금리 3.00% 연속 인상. 외인 선물 1.5조+, 이틀 연속 조단위.
          잭슨홀 앞 탄력은 제한. 내일도 상승 추세에 무게. 어게인 태조이방원.
        </div>
      </div>
      <div class="flow">Agentic AI
  → 추론·토큰이 매출이 됨
  → FY28 +70% = 공급 상한 (수요 ~+100%)
  → 메모리 원가 ↑ → NVDA GPM 75→71~72 → 가격 전가 → 72~73
  → CAPEX +525조 = NVDA 315 + HBM 81 + 잔여 130
  → CSP만으로는 DRAM/eSSD 추가 폭등 어려움
  → 스윙 = Neo Cloud / Sovereign / Enterprise / Industrial
  → Custom ASIC ↑ → SerDes/AEC/리타이머 (MRVL·ALAB·CRDO)
  → 국내: 전력 현지생산 · ESS/BBU · 화장품 서구권 · SKT 호라이즌</div>
    </section>

    <section id="nvda">
      <h2>1. 엔비디아 FY27 2Q — 자신감 뿜뿜, 기둥</h2>
      <p class="muted">첨부 PDF 「엔비디아 2분기실적」「엔비디아」. 원문 08:30 · 07:00 신문 “AI 고점론 잠재운 엔비디아”.</p>
      <img class="chart" src="charts/03_nvidia_print.png" alt="엔비디아 FY27 2Q 실적과 가이던스" />
      <p class="cap">첨부 PDF 숫자. 매출 962.2 / 컨센 922.9억달러. DC 890.2 vs 858.3. Edge 71.9 vs 66.1. 3Q 1,080±2% vs 1,045.7. EPS $2.46 vs $2.09.</p>

      <div class="scrollx">
      <table>
        <thead><tr><th>항목</th><th>실제</th><th>컨센서스</th><th>증감</th><th>메모</th></tr></thead>
        <tbody>
          <tr><td>매출</td><td>$96.22B</td><td>$92.29B</td><td>+105.9% YoY / +17.9% QoQ</td><td>첨부 PDF 962.2달러 표기</td></tr>
          <tr><td>Non-GAAP EPS</td><td>$2.46</td><td>$2.09</td><td>+1.5달러 YoY / +0.6달러 QoQ</td><td>8/27 브리프의 $2.22와 다름. 오늘은 첨부 PDF $2.46</td></tr>
          <tr><td>GPM (Non-GAAP)</td><td>75.0%</td><td>75.0%</td><td>+2.5%p YoY / Flat QoQ</td><td>3Q 가이드 74.0% ±50bp vs 컨센 74.8%</td></tr>
          <tr><td>Data Center</td><td>$89.02B</td><td>$85.83B</td><td>+116.6% / +18.3%</td><td>전사 핵심</td></tr>
          <tr><td>Edge Computing</td><td>$7.19B</td><td>$6.61B</td><td>+27.5% / +13.0%</td><td></td></tr>
          <tr><td>3Q 가이던스</td><td>$108.0B ±2%</td><td>$104.57B</td><td>중국향 DC 컴퓨팅 미포함</td><td>Q3 YoY 약 +90%. Q4 +77%여도 $120B</td></tr>
        </tbody>
      </table>
      </div>

      <h3>처음 낸 1년 가이던스</h3>
      <div class="grid3">
        <div class="card ok">
          <div class="label">FY28 +70%</div>
          현 공급에서 confidently. 시장 +40% 중반. 실제 수요 ~+100%. Agent당 연산 15~100배. 클라우드 백로그 $2조+.
        </div>
        <div class="card blue">
          <div class="label">저변</div>
          Non-하이퍼스케일러 2Q 45.3% ← 1Q 42.8% ← 4Q 32.3% ← 3Q 31.4%. Hyperscaler → Neocloud → AI Lab → Enterprise → Sovereign.
        </div>
        <div class="card warn">
          <div class="label">약정 +$1,500억 QoQ</div>
          Commitment 증가 = 메모리 선점. 한국 메모리에 직접 긍정. 3대 메모리와 공급 확대 협력.
        </div>
      </div>

      <h3>Rubin · AI Factory · 수익모델</h3>
      <ul>
        <li>GW당 NVIDIA 매출: Hopper $18B → Blackwell $25B → Vera Rubin $40B. Rubin 3Q DC 약 20%. 4Q27~FY28 하이퍼스케일러 재가속.</li>
        <li>Rubin 미리보기: 3Q26 생산·출하. Full rack-scale, 7개 purpose-built chips, 5개 accelerator racks. 추론 최대 35배, AI Factory 매출 기회 최대 10배. 랙 $7~8.5M (Blackwell Ultra 약 2배).</li>
        <li>ACNE +25% QoQ / +138% YoY, DC의 약 절반. 네오클라우드 3GW(2025말)→8GW(2026말).</li>
        <li>CPU: Grace TTM $5B+, Vera FY28 2배+. Networking +18% QoQ, Spectrum-X +2.6배 YoY. Groq LPU 통합.</li>
        <li>향후: 데이터센터 구축 → Take-or-Pay → 임대 → Revenue Sharing. 플랫폼화.</li>
        <li>실적에서 CPU 언급 = 모듈 SOCAMM → 심텍·티엘비 급등 배경.</li>
      </ul>
      <div class="card purple">
        <div class="label">실적 전 체크리스트 (첨부1 PREVIEW)</div>
        Beat보다 CAPEX 지속성·Rubin 램프. 순환금융, $5,000억 금융 플랫폼, 중국향 H200, Rubin→HBM 물량.
        지난 12분기 EPS 서프라이즈 평균 +10.4%(−12.9%~+30.4%), 매출 +6.7%(+0.7%~+21.4%).
      </div>
    </section>

    <section id="gpm">
      <h2>2. 왜 72~73%에서 멈추나 — 서버 +15% ≠ GPU +15%</h2>
      <p class="muted">원문 19:43 + 첨부4. 이번 실적에서 가장 중요하다고 본 부분.</p>
      <img class="chart" src="charts/04_gpm_path.png" alt="엔비디아 GPM 경로" />
      <p class="cap">3Q 74% → 4Q 71~72% → FY28 1Q 가격 인상 → 72~73% 회복. 원가 100% 흡수가 아니라 전가다.</p>
      <div class="card warn">
        AI 서버 = GPU + HBM + CPU + NIC + PCB + 전원 + 냉각 + 네트워크 + 시스템 조립.
        메모리 가격이 오르면 서버 전체 가격을 올리지만, 상승분 상당수는 메모리 ASP로 이전된다.
        그래서 메모리 가격 상승은 엔비디아 이익을 훼손하는 뉴스인 동시에, 최종 고객에게 전가할 가격결정력이 있다는 뉴스다.
        수요가 안 꺾이면 메모리의 추가 인상 여지. 시장이 +70%를 신뢰하면(본장 +7~8.7%) 27년까지 메모리 가격의 의미 있는 하락은 어렵다.
      </div>
    </section>

    <section id="capex">
      <h2>3. 525조 쪼개기 — Top 5만 보면 폭등은 어렵다</h2>
      <p class="muted">원문 23:48 두 번 + 첨부2. 같은 5줄이 코멘트와 PDF에 반복.</p>
      <img class="chart" src="charts/05_capex_split.png" alt="2027 CAPEX 525조 분해" />
      <p class="cap">525 − 315 − 81 ≈ 129~130조. 나머지 서버 부품이 경쟁할 추가 예산.</p>
      <ol>
        <li>AI 서버 투자는 엄청나게 증가한다. 2027 서버/AI 인프라 CAPEX +525조원.</li>
        <li>그 돈을 메모리 업체가 전부 가져가지 않는다. NVIDIA +315조, NVIDIA향 HBM +81조.</li>
        <li>나머지 서버 부품 추가 예산 약 130조원.</li>
        <li>따라서 Top 5 Hyperscaler CAPEX만 놓고 보면 2027 DRAM/eSSD가 지금보다 계속 폭등한다고 보기는 어렵다.</li>
        <li>Neo Cloud, Sovereign AI, Enterprise, Industrial 등 비CSP가 예상보다 빠르면 이야기가 달라진다. 이 추가 수요가 2027 메모리 가격 추가 상승의 핵심 변수.</li>
      </ol>
      <div class="card blue">
        병목은 GPU가 아니라 전체 인프라. DRAM/HBM + 전력·토지·Shell·웨이퍼·파운드리. LPS(Land·Power·Shell)는 2~3년.
        핵심은 수요가 꺾이느냐가 아니라 공급망이 얼마나 빨리 증설되느냐.
      </div>
    </section>

    <section id="net">
      <h2>4. 네트워크 칩 — 아는 듯 모르는 듯 구분</h2>
      <p class="muted">원문 23:12–23:17. 세 회사 구분은 23:13에 두 번.</p>
      <img class="chart" src="charts/06_network_map.png" alt="마벨 아스테라 크레도 구분" />
      <p class="cap">Marvell = ASIC+네트워크/광통신. Astera Labs = 서버 내부. Credo = 데이터센터 내 서버 간.</p>
      <div class="scrollx">
      <table>
        <thead><tr><th>용어</th><th>한줄</th></tr></thead>
        <tbody>
          <tr><td>PCIe</td><td>GPU↔CPU↔SSD↔NIC가 데이터를 주고받는 고속 연결 통로</td></tr>
          <tr><td>리타이머</td><td>고속도로 중간 신호 재생소. 약해진 신호를 다시 깨끗하게</td></tr>
          <tr><td>SerDes</td><td>Serializer/Deserializer. 여러 데이터를 한 줄로 압축했다가 다시 풂. 칩과 칩 사이 초고속</td></tr>
          <tr><td>AEC (원문 ACE)</td><td>케이블 안에 신호 보정 반도체가 들어간 고속 전기 케이블. Active Electrical Cable</td></tr>
          <tr><td>ALAB</td><td>PCIe/CXL 리타이머, 스위치, CXL 메모리 컨트롤러. AI 서버의 데이터 고속도로</td></tr>
          <tr><td>CRDO</td><td>서버 간 AEC + SerDes/DSP. 신호 손실↓, 고속·저전력</td></tr>
          <tr><td>MRVL</td><td>커스텀 AI ASIC, 광통신, SerDes/DSP, 이더넷 스위치. 하이퍼스케일러 TPU/ASIC 생산</td></tr>
        </tbody>
      </table>
      </div>
    </section>

    <section id="memory">
      <h2>5. 메모리 밸류 · 마이크론 SCA · 2027 HBM</h2>
      <p class="muted">원문 06:24–06:49. 8/27 종가 기준.</p>
      <img class="chart" src="charts/07_memory_val.png" alt="메모리 PER 비교" />
      <p class="cap">ADR 161.61$ = 223만원 (1,382.5원/달러). 본주 173만 대비 29% 프리미엄. 25/20/15%면 본주 178/186/194만.</p>
      <div class="scrollx">
      <table>
        <thead><tr><th></th><th>현주가</th><th>26 PER</th><th>27 PER</th><th>보수 27 PER</th><th>26 OP / EPS</th><th>27 OP / EPS</th><th>보수 27</th></tr></thead>
        <tbody>
          <tr><td>SK하이닉스 본주</td><td>173만원</td><td>4.9배</td><td>4.0배</td><td>5.9배</td><td>266조 / 350K</td><td>392조 / 436K</td><td>250~260조 / 290~300K</td></tr>
          <tr><td>SK하이닉스 ADR</td><td>161.61$ = 223만</td><td>6.4배</td><td>5.1배</td><td>7.6배</td><td colspan="3">마이크론 대비 −18% (과거 −20~−50%)</td></tr>
          <tr><td>삼성전자</td><td>26.6만원</td><td>5.5배</td><td>4.0배</td><td>6.4배</td><td>392조 / 48.1K</td><td>543조 / 66.4K</td><td>355~370조 / 43~45K</td></tr>
          <tr><td>마이크론</td><td>935.39$</td><td colspan="2">Fwd 12M 7.5배 · CY27 EPS 150$ → 6.2배</td><td colspan="4">27년 YoY OP +25% / EPS +38% (삼전닉스 기본)</td></tr>
          <tr><td>샌디스크</td><td>1484.95$</td><td colspan="6">FY27.1Q EPS 45$ 가이드, QoQ +10/+5/+5 가정, FY27 EPS 201$ PER 7.4배</td></tr>
        </tbody>
      </table>
      </div>
      <div class="card">
        다른 접근: 27년 성장 0으로 단순화하고 26년 PER 6~7배(과거 사이클 4~8배) → 하이닉스 210만~245만, 삼성 28.9만~33.7만.
      </div>
      <img class="chart" src="charts/08_micron_sca.png" alt="마이크론 SCA와 HBM" />
      <p class="cap">산제이 메흐로트라: 고객이 공급 약속보다 50% 더 원한다. SCA 16개 = DRAM 20% · NAND 1/3. 전부면 매출 40% Floor/Ceiling.</p>
      <div class="grid">
        <div class="card ok">
          <div class="label">긍정</div>
          수요&gt;공급 50%. SCA로 급락 위험↓. 2027 HBM 재협상. Nvidia·HS CAPEX 지속.
          UBS: 산업 HBM ASP +79%, Micron HBM +72%, HBM4E $30/GB+.
          2026=DRAM, 2027=HBM.
        </div>
        <div class="card bad">
          <div class="label">부정 · 역해석</div>
          DRAM 상승률 둔화. 이익 영구성 의심. SCA 2026~2030, 이후 $250B+ 미국 CAPEX.
          Floor가 과거 최고 분기 GM보다 높다 = 최악 마진 20%pt 하락도 불가능하지는 않다?
          그래도 그 최악 PER이 8배 이하라면 비싼가.
        </div>
      </div>
      <div class="card purple">
        과거엔 이익 급등 후 1~2년 내 반토막이 다반사. 피크 PER 4~8배가 곧 8~16배로 둔갑.
        27년 이익이 보여도 28·29년 “내려가면 어떻게”가 주가 속도를 가른다. 그 견해를 교육하는 과정.
        기민한 투자자는 AI Exposure를 빅테크·파운드리·GPU/ASIC·네트워크·메모리·광통신·장비·소프트웨어 중 어디에, 얼마를, 언제 스위치할지에 모은다.
      </div>
    </section>

    <section id="kv">
      <h2>6. 왜 128K Context가 약 40GB KV Cache인가</h2>
      <p class="muted">첨부5. Agent 문맥이 길수록 메모리가 커지는 이유.</p>
      <img class="chart" src="charts/13_kv_cache.png" alt="KV Cache 공식" />
      <p class="cap">2 × 80 × 8 × 128 × 131,072 × 2 = 42,949,672,960 Byte = 40 GiB 정확. 예문: “삼성전자의 HBM 가격 상승이 실적에 미치는 영향”.</p>
      <ul>
        <li>Layer 80 = 처리 단계를 80번. 각 층마다 KV를 쌓는다.</li>
        <li>KV Head 8 = 관심 영역 8개. Head Dimension 128 = 그릇 크기.</li>
        <li>BF16 = 숫자당 2 Byte. Context 128K = 약 131,072 토큰 (보고서·대화·검색·코드·다른 Agent 결과).</li>
        <li>K = 어디를 찾아볼 것인가(색인). V = 찾아낸 실제 정보. KV Cache = 빨리 찾기 위한 색인+관련 정보.</li>
      </ul>
    </section>

    <section id="marvell">
      <h2>7. 마벨 컨콜 — 산업은 더 강한데 시간외 −6%</h2>
      <p class="muted">원문 07:05–07:34. 전약이면 신규 접근(07:54)의 배경.</p>
      <img class="chart" src="charts/09_marvell.png" alt="마벨 가이던스" />
      <p class="cap">FY27 $12B(+45%) → FY28 $18B(+50%). 3Q $31.5억 vs 컨센 $30.3억. DC +60%. Custom ASIC FY28 2배+, FY29 가속. 선급 $10억.</p>
      <div class="card warn">
        Google 워런트 프로그램 매출은 기존 Custom 목표에 이미 포함. 숨은 업사이드가 아님. “뭔가 더 큰 것”을 기대했다면 빌미.
        시간외 −6%대 = 실적 부진이 아니라 추가 서프라이즈 부족 + 차익. TPU에서 브로드컴 위협 논리에 마벨이 최근 강했고, 브로드컴은 그래서 약하다 오늘 +4%.
        CRDO 본장 +4.8% / AH −1%, ALAB +6% / AH −1%대, AVGO 시간외도 안 빠짐 → Custom ASIC·네트워크 펀더 이슈 없음. ASIC이 커질수록 SerDes 수요↑.
      </div>
    </section>

    <section id="us">
      <h2>8. 8/27 미국 마감 — GPU·네트워크, 메모리는 시큰둥</h2>
      <img class="chart" src="charts/01_us_close.png" alt="8/27 미국 마감" />
      <p class="cap">NASDAQ 26,541 +1.57%. S&amp;P500 7,731 +0.72%. Dow 53,569 +0.20%. SOX 11,882.17 +2.33%.</p>
      <div class="card">
        매파 발언 + 호르무즈로 유가·국채 금리 상승 압력. 전통·방어는 상대 약세. 기술 독주 차별화.
        헤드라인 PCE가 조금 더 높았지만 코어 부합, 큰 의미 없음(첨부3). 주가가 천천히 가면 신규 접근 시점.
      </div>
    </section>

    <section id="korea">
      <h2>9. 8/27 국내 마감 — 갭 뒤 확산, 외인 선물 1.5조+</h2>
      <img class="chart" src="charts/02_korea_close.png" alt="8/27 국내 마감" />
      <p class="cap">대형 반도체 갭상승 후 반납. 코스닥은 전지·소부장이 플러스 전환. LS ELECTRIC · HD현대일렉트릭. ESS 3차 입찰 1GW+ 검토.</p>
      <div class="grid">
        <div class="card bad">
          <div class="label">부정</div>
          미-이란 장기화. 미 10년 4.6%대. 높은 유가. 연준 노이즈. 9월 인상 가능성. 주요국 국채 금리.
        </div>
        <div class="card ok">
          <div class="label">긍정</div>
          EPS 상승률. 메모리 가격. 메모리 주가 과매도·저평가. 하이닉스 ADR→마이크론 갭. 7월 CPI·PPI. 엔비디아 호실적.
        </div>
      </div>
      <div class="card blue">
        미-이란 휴전 가능성↑, 국채 금리 상승 제약 → 내일도 긍정. 전력·전선·반도체·소부장. 그외 전지·바이오·통신장비·기판.
        15:09: 잭슨홀 두고보자. 외인 펀드 레버리지는 청산됐어도 반도체 비중은 높아 자사주로 비중 축소. 기관 수익룰 게임 지속. 주말 강의에서 자세히.
      </div>
    </section>

    <section id="power">
      <h2>10. 전력기기 · BBU/BESS · 트럼프 비상사태</h2>
      <img class="chart" src="charts/10_power_gs.png" alt="골드만삭스 전력기기와 행정명령" />
      <p class="cap">황금양말 Initiate. 효성 Buy 4,160,000 (현 2,797,000, +48.7%) &gt; HD현대일렉 Neutral 850,000 (733,000, +16.0%) &gt; LS Neutral 230,000 (201,500, +14.1%).</p>
      <div class="card warn">
        효성 TP 416만은 컨센 425만과 크게 다르지 않다. 아직 안전마진 20%밖. TP 80% 이상 추격 자제 규칙과 맞물림.
      </div>
      <h3>BBU는 필수라고 단정하지 말 것 (첨부3)</h3>
      <ul>
        <li>BESS = 외부 대형 저수지. UPS = 중앙 비상발전기. BBU = 서버별 에어백. 대체재가 아니라 계층.</li>
        <li>AI GPU는 ms Pulse Load. 고출력·빠른 응답·고속충전·안전·공간효율. 18650/21700·탭리스. InterBattery 2026.3, 8월에도 공식 강조.</li>
        <li>“SDI vs Panasonic 양분”, “BBU 필수”, “CAGR 30%”는 걸러라. 800VDC면 형태가 달라질 수 있다. 모델은 출하×랙당 탑재×ASP.</li>
        <li>규모는 EV보다 훨씬 작다. 질적 고부가. 밸류체인: SDI 셀, 상신이디피 Can, 롯데에너지머티리얼즈 동박.</li>
        <li>행정명령 직접 수혜 강도는 BESS &gt;&gt;&gt; BBU. IEEPA+국가비상사태법. 변압기·대형 발전기·BESS·인버터·고압 차단기·제어 소프트웨어. 디지털 백도어. 중국 인버터 통신장치. EU도 공공 중국산 인버터 금지.</li>
        <li>국내: 효성 멤피스, HD현대일렉 앨라배마, LS 유타. 10MVA+ 중국 비중 이미 낮음 → 물량보다 가격·수주 경쟁력. 120일 후 DOE.</li>
        <li>정전 1번에 30억 증발. 기사 <a href="https://www.newsprime.co.kr/news/article/?no=745311">뉴스프라임</a> · 행정명령 <a href="https://n.news.naver.com/article/119/0003125906?sid=104">데일리안</a>.</li>
      </ul>
    </section>

    <section id="tariff">
      <h2>11. 반도체 관세 · 쿠팡 301 · Made in USA</h2>
      <p class="muted">원문 11:35–11:38. 폴리티코 검토 단계. 확정 아님.</p>
      <div class="card bad">
        시행되면 반도체→서버·PC·게임콘솔까지 전자 공급망 전반. 다만 관세→GPU/CPU/메모리/서버 가격↑→DC 구축비↑→AI CAPEX 둔화라 미국도 HBM·GPU·서버에 과도 관세는 부담.
        일률 고율보다 미국 투자·현지생산 연계 차등. SK하이닉스 인디애나 HBM = 전략 자산. 자동 면제는 아직 아님.
      </div>
      <div class="card warn">
        모레노 상원, 한국 미국기업 규제 → 301조 조사 요청. 반도체 관세 ↔ 쿠팡 이슈가 연결될 수 있다.
        “한국 기업은 미국에서 자유롭게, 미국 기업은 한국에서 차별” 논리. 곧바로 한국 반도체 관세는 아님.
      </div>
    </section>

    <section id="skt">
      <h2>12. SK텔레콤 — 호라이즌 6.3조 / 하이퍼 빈칸 / 모두의 AI</h2>
      <img class="chart" src="charts/12_skt_horizon.png" alt="SK호라이즌과 SK하이퍼" />
      <p class="cap">기존 137 + 울산 100 + 구로 75 = 318MW + 해저케이블. KKR 29% + IMM 20% = 3조. SKT 51% 경영권.</p>
      <div class="card">
        단기 중립~긍정(가치 확인+현금). 중장기는 5~15GW에서 SKT가 얼마를 버느냐.
        빈칸: 누가 운영, 수익성, NVDA/HS 장기계약, 개발이익, 반복수익, SKT·하이퍼·프로젝트·호라이즌 배분.
        09:34 <a href="https://n.news.naver.com/mnews/article/119/0003126434?rc=N&amp;ntype=RANKING&amp;sid=105">데일리안 속보</a>: 정부 ‘모두의 AI’ 사업자 SKT·KT·카카오.
      </div>
    </section>

    <section id="beauty">
      <h2>13. 화장품 — 아모레 · 에이피알 · 실리콘투</h2>
      <p class="muted">원문 11:02–11:05. 요청된 워드파일은 첨부에 없음. 11:02 실리콘투 포인트는 에이피알 문안 중복.</p>
      <img class="chart" src="charts/11_cosmetics.png" alt="K-뷰티 3사" />
      <h3>아모레퍼시픽 2Q26</h3>
      <ul>
        <li>매출 1조 1,759억 +17%. OP 1,173억 +59%. 컨센 OP 983억 대비 +19%. 관세환급 190억 ≈ 인센티브/PS 150억 상쇄. 국내+해외.</li>
        <li>국내 온라인/MBS +15%, 크로스보더 +30%+. 중국 −6%(설화수 점포 79개↓). 북미 +57%. EMEA +63%. 코스알엑스 +55%+, OPM 25%+.</li>
        <li>RX라인 30%+가 Advanced Snail 96 Mucin Power Essence를 추월. 6 Peptide Toner/Booster, Vitamin C 23, Retinol 0.1. 선케어 Amazon 독일 1위.</li>
        <li>라네즈 Amazon Prime Day Top 100. 이니스프리 선케어 세포라. 에스트라 Amazon·세포라 100%+, 북유럽. 일리윤 최초 Amazon Beauty Top 100.</li>
        <li>해외 서구권 51%, 아시아 첫 추월. 12MF PER 30배 내외 로레알·에스티로더형 멀티브랜드 수렴.</li>
      </ul>
      <h3>에이피알</h3>
      <ul>
        <li>프라임데이 7월→6월 조기 → 3Q 공백 우려. 오프라인+TikTok이 상쇄. 북미 QoQ +1,000억 (아마존 500 / 오프라인+틱톡 500).</li>
        <li>Target &gt; Ulta, Walmart 초도 ≈ Ulta. 메디큐브 7월 GMV MoM +40%. 3Q 선매입(Sell-in) 가능.</li>
        <li>유럽 4Q25 418 → 1Q26 838 → 2Q26 1,451억, 6개월 3.5배. 영국 Amazon/TikTok 2025말, Boots. 침투율 낮아 여력 최대.</li>
        <li>2Q 항공 100억+ 비정상. 미국 3Q 해상, 유럽 4Q 해상 → OPM 개선.</li>
      </ul>
      <h3>실리콘투</h3>
      <ul>
        <li>8/27 글렌우드크레딧 6.72% 전량 블록딜. 8/18 CVC 3,000억. Douglas 시너지. 물류거점·재고·MOIDA.</li>
        <li>2026E 매출 1조 6,321억 +46.2%, OP 2,998억 +46.0%, OPM 18.4%. 유럽 +80.9%(폴란드 증설, 영국 창고 10월). 북미 +42.6%(Ulta·Target, 인디 소싱).</li>
      </ul>
    </section>

    <section id="side">
      <h2>14. 옆 테마 — 키옥시아 · MLCC · 원전 · 현대차 로봇</h2>
      <img class="chart" src="charts/15_side_themes.png" alt="키옥시아 MLCC 관세 원전 현대차" />
      <h3>키옥시아 · YMTC · NAND는 1/3</h3>
      <ul>
        <li>Fab3 1조엔+(약 8.7조) ⊂ 2032년까지 5조엔+(약 43조, $310억). 요카이치·기타카미 인프라 + 기타카미 팹3. SanDisk 공동, 2029년 이후. 히로오 오타 · 데이비드 괴켈러.</li>
        <li>2Q NAND 점유: 삼성 25%, 하이닉스 22%, 키옥시아=YMTC 14%. YMTC +22% YoY, +5% QoQ, 상장 추진. 다카이치 내각 전략물자 17개 분야.</li>
        <li>eSSD가 흡수를 못하면 중장기 NAND 가격에 부담. 기술 격차는 DRAM보다 작아 심리에는 부정. 그러나 DRAM이 3배, NAND 영향 1/3 이하.</li>
        <li>링크 <a href="https://news.einfomax.co.kr/news/articleView.html?idxno=4432275">연합인포맥스</a>.</li>
      </ul>
      <h3>삼성전기 MLCC — Key는 일본 3사</h3>
      <ul>
        <li>TrendForce: 4Q26 OEM·ODM 인상, 대리점→고객 전반. X5R +25~30%(수요 조절+고사양 Capa). AI 서버 X6S +10~20%.</li>
        <li>Murata · Taiyo Yuden · Kyocera는 관망. 동참이 추가 판가와 삼성전기 단기 모멘텀의 key. 대만·중국 +10~20%, 가동률 90%.</li>
        <li>광통신 모듈 부족 → 낙수. 전통 ICT·자동차는 보수, 2H26 성수기 제한. <a href="https://buly.kr/BTSFEku">TrendForce</a>.</li>
      </ul>
      <h3>웨스팅하우스 3大 조건</h3>
      <ul>
        <li>배경: 원전 르네상스, 수출 70%+ 러·중. 미국은 IP 있고 시공망 와해 → 한국에 WEC 공동 인수 제안.</li>
        <li>실익: 체코 IP 재협상(50년 로열티·기자재 의무를 배당/개정으로), 미국·동유럽 약 $800억 선점.</li>
        <li>도시바 2006 WEC 무리 인수 → 지연·공사비 → 수조 적자 → 상장폐지.</li>
        <li>3대 조건: ① 밸류·손실 분담(승자의 저주, 공기·원자재 전가 금지) ② 의결권, 시공 하청·IP 불공정 차단 ③ 투 트랙 APR1400 독립.</li>
        <li><a href="https://v.daum.net/v/20260828112641123?from=newsbot&amp;botref=KN&amp;botevent=e">다음 포럼</a>.</li>
      </ul>
      <h3>현대차 로봇 분리 — TP 60만, −7.7%</h3>
      <ul>
        <li>Target P/E 17배, 26~27 평균 EPS → 60만원. 중국 EV4(BYD·리오토·샤오미·Geely) 12M Fwd 18.9배 대비 약 10% 할인. 중국은 본체, 현대는 자회사.</li>
        <li>불리: 본체=저평가 자동차, 로봇 멀티플 직접 적용 어려움, 순수 로봇 IPO가 뜨면 매력 상대 하락.</li>
        <li>장점: 그룹·외부 투자, 투자 부담↓, 초기 적자 연결 완화, Boston Dynamics 외부 투자/상장 시 지분가치.</li>
        <li>결론: 로봇 자체는 긍정, 본체 재평가는 제한적. 영향력 있는 증권사 TP 하향+이유가 뚜렷하면 상당 기간 회복 못 하는 경우가 많다(22:40).</li>
      </ul>
    </section>

    <section id="rules">
      <h2>15. 포트 · 규칙 · 관심주 · 신문</h2>
      <img class="chart" src="charts/16_portfolio.png" alt="포트폴리오와 규칙" />
      <img class="chart" src="charts/14_watchlist.png" alt="관심 종목" />
      <div class="grid3">
        <div class="card blue">
          <div class="label">07:54 포트</div>
          매크로 특별이슈 없고(장중에도 없다 가정) 마벨 하락+메모리 시큰둥 → 전약이면 신규 approach.<br>
          AI ~50% (반도체/변압기/2차전지, 변·전지는 전력).<br>
          Non-AI 20~30% (건설/원전/DC: 현대/대우/삼성에스디에스). 화장품 펀더 이상무, 차익 오케. 조선 제한. 현금 20~30%.<br>
          2차전지: 할인율·실적 턴어라운드·정책(유럽 IAA 한국 우대, 美 EV 세액공제 복원) 대략 충족. 단기 급등 → 눌림목/분할. 미 금리 안정이 전제.
        </div>
        <div class="card warn">
          <div class="label">22:42–22:43 규칙</div>
          목표주가 = 증권사 고목표-컨센이 아닌 보수적 기준.<br>
          TP×80% 이상 추격 자제. 60% 이하 손절 확실히.<br>
          08:46 대형 반도체보다 눌림목에서 2차전지·건설/데이터센터·변압기·화장품 먼저.<br>
          08:25 어게인 태조이방원. 08:04 원화강세: 식음료, 변압기, 신재생(풍력 태양광), 철강.
        </div>
        <div class="card">
          <div class="label">관심 (23:46)</div>
          반도체 삼성전자·SK하이닉스 / 소부장 한미반도체·이수페타시스·원익IPS·유진테크 / 로봇 현대차·현대모비스·로보티즈 / AI팩토리 NAVER·SK텔레콤 / 전력 HD현대일렉트릭·효성중공업·산일전기 / 조선 HD현대중공업·삼성중공업 / 바이오 알테오젠·디앤디파마텍 / 전지 삼성SDI·엘앤에프 / 신재생 OCI홀딩스 / 재건 삼성E&amp;A·HD건설기계 / 스테이블 NAVER·카카오페이·갤럭시아머니트리 / 통신 RFHIC·케이엠더블유 / 화장품 한국콜마·에이피알 / 정유 S-OIL.
        </div>
      </div>
      <h3>8월 28일 신문에서 시장과 겹치는 줄</h3>
      <ul>
        <li>한은 3% 연속, 한미 금리차 0.75%p. 디지털자산기본법 대주주 상한 20%·예외 34% 거론, 금융위 “확정 없음”. 금 ETF 사흘 12조, 금 4600$, 이달 +14%, 美부채 40조$. BTC 일주일 +22%, 9월 클래리티법.</li>
        <li>류제명: 美 AI 100, 中 70, 韓 35. 피지컬 AI는 1강. 현대차 배터리 독립, 출력 2배·충전 40% 단축, 2028 아틀라스, 아이오닉5 웨이모. 포스코 리튬 2공장 2.5만톤, 40% 마진. 엔비디아 “AI 중앙은행”, 인텔·코어위브 투자 78억불, 미수금 631억불.</li>
        <li>경제: 4년제 교육비 2072~2073만 vs 전문대 1281만. 300인 이상 임금 +4.4% vs 미만 +2.3%, 특별급여 +17.2%, 실질임금 3개월 감소. 가계 소득 529만 +4.5%, 이전소득 +20.4%. 누리호 5차 10/7 12:23–13:23, 위성 15기. 김밥 3869원, 삼겹살 2만1321원.</li>
        <li>부동산·사회·국제 헤드라인은 부록 07:00 원문에 전부 있다. 네팔 160명 사망·484명 실종, 한국인 9명 연락두절. 사우디 수에즈·페르시아 우회 +$5/배럴. 트럼프 비핵화 침묵. 베트남 상반기 대미흑자 158조 1위.</li>
      </ul>
    </section>

    <section id="check">
      <h2>16. 앞으로 볼 것</h2>
      <div class="card key">
        잭슨홀 워시. 비CSP 수요가 130조 잔여를 넘느냐. HBM 2027 재협상(+79%/+72%, $30/GB+). 일본 MLCC 동참.
        관세율·면제(인디애나). SK하이퍼 이익 귀속. 효성 안전마진 20%. Rubin 램프와 SOCAMM(심텍·티엘비).
        DSO/현금 질은 어제 브리프의 질문, 오늘은 “전가 + 공급 천장”이 기둥.
        면책: 매수·매도 추천 아님. 단순 참고, 판단은 본인, 법적 자료 활용 불가.
      </div>
    </section>
"""


def main() -> None:
    raw_html = "".join(raw_block(t, title, body) for t, title, body in RAW)
    pdf_html = "".join(pdf_block(title, body) for title, body in PDF_RAW)
    page = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>8월 28일 Quick 코멘트 시각화 · 엔비디아 +70% · CAPEX 525조 · 비CSP</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="top">
    <div class="top-inner">
      <div class="brand">QUICK COMMENT BRIEF · 2026.08.28 · <b>엔비디아 공급상한 + 525조 쪼개기 + 비CSP</b></div>
      <nav>
        <a href="2026-08-28-quick-comment-core.html">핵심요약</a>
        <a href="#thesis">한 줄</a>
        <a href="#nvda">엔비디아</a>
        <a href="#gpm">72~73%</a>
        <a href="#capex">525조</a>
        <a href="#net">네트워크</a>
        <a href="#memory">메모리</a>
        <a href="#kv">KV Cache</a>
        <a href="#marvell">마벨</a>
        <a href="#us">미국</a>
        <a href="#korea">국내</a>
        <a href="#power">전력</a>
        <a href="#tariff">관세</a>
        <a href="#skt">SKT</a>
        <a href="#beauty">화장품</a>
        <a href="#side">옆테마</a>
        <a href="#rules">규칙</a>
        <a href="#check">체크</a>
        <a href="#raw">원문 전체</a>
      </nav>
    </div>
  </div>
  <div class="wrap">
{BODY}
    <section id="raw">
      <h2>부록. 원문 전체 — 코멘트</h2>
      <p class="muted">사용자 붙여넣기 원문을 시각별로 보관. 중복 게시·에이피알/실리콘투 혼선 문안도 삭제하지 않음.</p>
      {raw_html}
      <h2>부록. 원문 전체 — 첨부 PDF 5건</h2>
      {pdf_html}
    </section>
    <footer class="note">
      매수·매도 추천이 아니다. 위 내용은 단순 참고 자료이며 판단은 본인의 몫이다. 법적 자료로 활용이 불가능하다.
      화장품 워드파일은 이번 첨부에 없었다. 차트는 <code>reports/charts/</code>.
    </footer>
  </div>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(page, encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes), comments={len(RAW)}, pdfs={len(PDF_RAW)}")


if __name__ == "__main__":
    main()
