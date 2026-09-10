#!/usr/bin/env python3
"""9월 8일 브리프를 차트 포함 단일 HTML + 한 장 이미지로 만든다."""

from __future__ import annotations

import base64
import subprocess
import time
from pathlib import Path

import fitz

import sep08_data as D

ROOT = Path("/workspace")
CHARTS = ROOT / "reports" / "charts"
OUT_HTML = ROOT / "reports" / "2026-09-08-oneboard.html"
OUT_LECTURE = ROOT / "lectures" / "9월 8일 Quick 코멘트 한장.html"
OUT_PNG = ROOT / "reports" / "sep08-pages" / "oneboard.png"
ART = Path("/opt/cursor/artifacts")


def data_uri(path: Path) -> str:
    raw = path.read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def html() -> str:
    c = {n: data_uri(CHARTS / n) for n in [
        "01_dram_2q26.png",
        "02_iphone_bom.png",
        "03_buyback_headroom.png",
        "04_etf_rebal.png",
        "05_astra_paradox.png",
        "06_memory_per.png",
        "07_physical_ai_chain.png",
        "08_us_dc.png",
    ]}
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>9월 8일 Quick 코멘트 — 한 장</title>
<style>
:root {{
  --navy:#0f2043; --navy2:#1e407c; --gold:#b8943a; --ink:#1a1a1a;
  --muted:#4b5563; --line:#d5dce6; --bg:#eef1f7; --card:#fff;
  --green:#166534; --red:#991b1b; --amber:#7a5c12;
}}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--bg); color:var(--ink);
  font-family:"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif; }}
.board {{ width:1240px; margin:0 auto; padding:18px 18px 28px; background:var(--bg); }}
.kicker {{ color:var(--gold); font-weight:800; font-size:12px; letter-spacing:.04em; }}
h1 {{ color:var(--navy); font-size:28px; line-height:1.2; margin:4px 0 8px; }}
.lede {{ color:var(--muted); font-size:13.5px; margin:0 0 12px; }}
.hero {{ background:var(--navy); color:#fff; border-radius:14px; padding:16px 18px; margin-bottom:12px; }}
.hero b {{ color:var(--gold); }}
.hero p {{ margin:0; font-size:14.5px; line-height:1.55; }}
.kpi {{ display:grid; grid-template-columns:repeat(6,1fr); gap:8px; margin-bottom:12px; }}
.kpi div {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:9px 10px; }}
.kpi h3 {{ margin:0; font-size:11px; color:var(--navy2); }}
.kpi .n {{ font-size:18px; font-weight:800; color:var(--navy); margin-top:2px; }}
.kpi p {{ margin:3px 0 0; font-size:11px; color:var(--muted); line-height:1.35; }}
.cols {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:12px 13px; }}
.card h2 {{ margin:0 0 7px; color:var(--navy); font-size:16px; border-bottom:2px solid var(--navy); padding-bottom:5px; }}
.card h3 {{ margin:8px 0 4px; color:var(--navy2); font-size:13px; }}
.card p, .card li {{ font-size:12.6px; line-height:1.45; margin:0 0 6px; }}
.card ul {{ margin:0 0 6px; padding-left:18px; }}
.wide {{ grid-column:1 / -1; }}
img {{ width:100%; border-radius:8px; border:1px solid var(--line); background:#fff; display:block; margin:6px 0; }}
table {{ width:100%; border-collapse:collapse; font-size:11.8px; margin:6px 0; }}
th {{ background:var(--navy); color:#fff; padding:5px 6px; text-align:left; }}
td {{ padding:5px 6px; border-bottom:1px solid var(--line); vertical-align:top; }}
tr:nth-child(even) td {{ background:#f7f9fc; }}
.pos {{ color:var(--green); font-weight:700; }}
.neg {{ color:var(--red); font-weight:700; }}
.note {{ background:#fff8e7; border-left:4px solid var(--gold); padding:7px 9px; border-radius:0 8px 8px 0; font-size:12.3px; margin:6px 0; }}
.ok {{ background:#e8f5e9; border-left:4px solid var(--green); padding:7px 9px; border-radius:0 8px 8px 0; font-size:12.3px; margin:6px 0; }}
.risk {{ background:#fdecea; border-left:4px solid var(--red); padding:7px 9px; border-radius:0 8px 8px 0; font-size:12.3px; margin:6px 0; }}
.flow {{ display:flex; flex-wrap:wrap; gap:6px; align-items:center; margin:6px 0 8px; }}
.flow span {{ background:var(--navy); color:#fff; padding:4px 8px; border-radius:999px; font-size:11.5px; font-weight:700; }}
.flow i {{ color:var(--gold); font-style:normal; font-weight:800; }}
.foot {{ color:var(--muted); font-size:11px; margin-top:10px; text-align:right; }}
.tag {{ display:inline-block; font-size:10px; font-weight:800; padding:1px 6px; border-radius:999px; background:#e8f1fb; color:var(--navy2); }}
@page {{ size: 1280px 5200px; margin: 0; }}
@media print {{
  html, body {{ background:#eef1f7; }}
  .board {{ width:1240px; margin:0 auto; }}
}}
</style>
</head>
<body>
<div class="board">
  <div class="kicker">2026. 9. 8.  ·  Quick 코멘트 + 첨부 PDF 10개  ·  한 장</div>
  <h1>메모리 선점이 모바일까지 왔다</h1>
  <p class="lede">기존 테제(경기 Good · 메모리 Strong · 밸류 Attractive) 유지. 오늘 추가: 애플 NAND 물량 선점 · Arm Physical AI 표준 · 9/10 ETF는 펀더멘탈이 아님.</p>
  <div class="hero">
    <p><b>한 줄.</b> 애플이 가격 상한 없는 3~5년 NAND를 논의한다는 보도는, AI가 팹을 선점하자 세계 최강 바이어마저 단가에서 물량으로 돌아섰다는 뜻이다. TrendForce 2Q26 DRAM <b>${D.DRAM_2Q26_REVENUE_B}B(+{D.DRAM_2Q26_QOQ_PCT}%)</b>가 실물. 9/10 하이닉스 ETF 매도 1.24~1.45조는 기계적이다. 공식 미확인 보도와 확인 숫자를 섞지 말 것.</p>
  </div>
  <div class="kpi">
    <div><h3>DRAM 2Q26</h3><div class="n">${D.DRAM_2Q26_REVENUE_B}B</div><p>QoQ +{D.DRAM_2Q26_QOQ_PCT}%. 삼성 39.4 / 닉스 24.9 / MU 23.3</p></div>
    <div><h3>아이폰 BOM</h3><div class="n">{D.IPHONE18_MEM_BOM_PCT}%</div><p>{D.IPHONE18_MEM_BOM_START_PCT}% → {D.IPHONE18_MEM_BOM_PCT}% → 1H27 {D.IPHONE18_MEM_BOM_1H27_PCT}%+. 원가 약 {D.IPHONE18_MEM_COST_MULTIPLE}배</p></div>
    <div><h3>미국 DC</h3><div class="n">${D.US_DC_JUL26_SAAR_B}B</div><p>7월 SAAR. YoY +{D.US_DC_JUL26_YOY_PCT}%. 2021 이후 +{D.US_DC_SINCE_2021_PCT}%</p></div>
    <div><h3>닉스 27E PER</h3><div class="n">{D.HYNIX_27_PER}배</div><p>9/4 본주. ADR 5.5배. 과거 사이클 4~8배</p></div>
    <div><h3>자사주 여력</h3><div class="n">×3.7</div><p>닉스 65만→240.7만. 삼성 200만→732만</p></div>
    <div><h3>9/10 ETF</h3><div class="n">~1.5조</div><p>닉스 1.24~1.45조 + 삼성 0.20~0.24조. 종가</p></div>
  </div>

  <div class="cols">
    <div class="card">
      <h2>1. 애플 NAND — 구매력 역전 <span class="tag">미확인 보도</span></h2>
      <ul>
        <li>키옥시아와 3~5년, Price Cap 없을 수 있음. 공식 확인 없음.</li>
        <li>단가 인하+다변화 → 물량 확보+장기 계약. AI가 팹을 먼저 가져감.</li>
        <li>다음 후보: 삼성·닉스·마이크론 LPDDR5X/6. 삼성 캐파 60~70% LTA 언급.</li>
        <li>폴더블 NAND 추정 닉스 30% / 삼성 15% / 나머지 키옥시아.</li>
        <li>폴더블 ASP $2,099~2,299, 고용량 $3,000+. <b>9/9 수요가 가격을 받치는가.</b></li>
      </ul>
      <img src="{c['02_iphone_bom.png']}" alt="아이폰 메모리 BOM"/>
      <div class="note"><b>읽기.</b> 모바일 수요 붕괴가 아니라 공급 잠식. PC·폰 수용력은 약해 3Q 상승률은 둔화. 큰손은 가격을 열고 물량을 묶는다.</div>
    </div>

    <div class="card">
      <h2>2. DRAM 2Q26 — 물량보다 가격 <span class="tag">TrendForce 확인</span></h2>
      <img src="{c['01_dram_2q26.png']}" alt="DRAM 벤더"/>
      <table>
        <tr><th>회사</th><th>매출</th><th>점유</th><th>QoQ</th></tr>
        <tr><td>삼성</td><td class="pos">$60.98B</td><td>39.4%</td><td>+63.4%</td></tr>
        <tr><td>하이닉스</td><td>$38.59B</td><td>24.9%</td><td>+37.9%</td></tr>
        <tr><td>Micron</td><td>$36.00B</td><td>23.3%</td><td>+65.5%</td></tr>
        <tr><td>CXMT</td><td>$14.62B</td><td>9.5%</td><td>+99.3%</td></tr>
      </table>
      <p>3Q 계약가 +13~18%. 상승률 둔화 ≠ 종료. 소비자 DRAM이 제일 많이 오른다(공급 축소).</p>
      <div class="note"><b>Inference ≠ HBM.</b> Agent State 160GB→1TB vs HBM 192→576GB. 병목은 어디에 저장하느냐. HBM+DDR5/CXL+NAND.</div>
    </div>

    <div class="card">
      <h2>3. 밸류 — 싼가, 피크인가 <span class="tag">9/4 종가</span></h2>
      <img src="{c['06_memory_per.png']}" alt="메모리 PER"/>
      <table>
        <tr><th>종목</th><th>27E PER</th><th>메모</th></tr>
        <tr><td>마이크론</td><td>6.8</td><td>기준선. EPS $150</td></tr>
        <tr><td>샌디스크</td><td>8.7</td><td>7월말 후 +43%</td></tr>
        <tr><td>닉스 ADR</td><td>5.5</td><td>MU 대비 −19%</td></tr>
        <tr><td>닉스 본주</td><td>3.8</td><td>ADR 프리미엄 44%</td></tr>
        <tr><td>삼성전자</td><td>3.8</td><td>같은 배수</td></tr>
      </table>
      <p>ADR 30%면 본주 183만, 20%면 198만. 원화 +10% ≈ 주식 −12%. 국민연금 환헷지 중단은 그 배경.</p>
      <div class="note"><b>질문.</b> 2027 EPS가 피크인가. SCA는 급락을 약화시키지만 고이익 유지는 다른 말. 보수(26년 이익 고정, PER 6~7): 닉스 210~245만, 삼성 28.9~33.7만.</div>
    </div>

    <div class="card">
      <h2>4. Astra — 토큰이 아니라 업무량</h2>
      <img src="{c['05_astra_paradox.png']}" alt="Astra 역설"/>
      <p>Computer Use 65.7→72.6, AutomationBench 18.1→41.4. 토큰 −10%~1/3, 단가 2.5배. 지표는 <b>$ / 성공한 업무</b>. 80%⁸=17% vs 90%⁸=43%.</p>
      <p>가정(실적 아님): 토큰 −30% × 업무 ×3 = 1인 ×2.1. 사용자 ×2 → 전체 ×4.2. 안전 모니터링은 compute를 더 쓴다.</p>
      <div class="flow"><span>Training</span><i>→</i><span>Reasoning</span><i>→</i><span>Agent</span><i>→</i><span>24h 노동 DC</span></div>
      <p>Azure FY26 $101.9B, 4Q +43%. 1990년대 생산성 1.5→2.5~2.7%, MFP 0.4→1.3%는 팩트. 시차 있음. 지금은 PC 설치 단계일 수 있음.</p>
      <div class="risk"><b>부채 가드.</b> GDP +12.5%p는 스트레스이지 예상 아님. 구매약정 ≠ 부채. NVDA $366B 약정도 부채 아님. 임계 예: 10Y 5%.</div>
    </div>

    <div class="card wide">
      <h2>5. Arm Physical AI — 로봇 한 종목이 아니다 <span class="tag">공식 확인</span></h2>
      <img src="{c['07_physical_ai_chain.png']}" alt="Physical AI 체인"/>
      <p>Arm Total Design 80사+. RL0~RL5 = 자동차 SAE의 로봇판. TAM $25B → 2030년대 $200B. 한국 확인 = <b>스트라드비전</b>. 삼전은 80사 명단 미확인, Neoverse CSS-N4에 SF2/SF2P 언급.</p>
      <table>
        <tr><th>이름</th><th>역할</th><th>숫자</th><th>체크</th></tr>
        <tr><td>스트라드비전</td><td>Perception</td><td>Arm 합류</td><td>양산 비전 → 로봇</td></tr>
        <tr><td>로보티즈</td><td>액추에이터</td><td>22만→50만대, 390→500→1,000억+</td><td>2030 $1bn은 목표</td></tr>
        <tr><td>삼성SDS</td><td>RX 통합</td><td>RX ART 2026</td><td>실적 있는 중장기</td></tr>
        <tr><td>PSK홀딩스</td><td>패키징 리플로우</td><td>26E 2,792억 / OP 1,088억</td><td>TP 19.5만 ≈ PER 15배</td></tr>
      </table>
    </div>

    <div class="card">
      <h2>6. 9/10 수급 — 기계적, 자사주는 가변</h2>
      <img src="{c['04_etf_rebal.png']}" alt="ETF"/>
      <img src="{c['03_buyback_headroom.png']}" alt="자사주"/>
      <p>캡 20%. ETF ~7.6조. 닉스 36.8% / 삼성 23%. 9/10 종가, 9/11 적용. 한미 +3,000억, 주성 +1,800억, 테스 +1,400억.</p>
      <p>9/7 매입 1.1조+0.5조. 거래대금 10.4조/7.9조. 65만·200만은 당일 신청이지 법적 최대가 아님.</p>
      <div class="ok"><b>리밸런싱 하락 = 기회일 수 있음.</b> 금액은 작지 않다. 펀더멘탈과 무관하다.</div>
    </div>

    <div class="card">
      <h2>7. 중동 · 전력 · 일정</h2>
      <img src="{c['08_us_dc.png']}" alt="미국 DC"/>
      <p><b>후티</b> 사우디 본토, 부상 73, 아람코 자잔(~400kb/d 설비). 공급 쇼크 확정 아님. 로하니 종전 국민투표론. 유럽 보합, ASML +2.3%, Infineon +6.9%. AfD ≠ KOSPI 전체 악재.</p>
      <p><b>엔시날</b> 6.3GW / $22.3B, 9/7 의결 보도. EPC 미확정. 원전 8기는 검토. 9/18 발표 가능.</p>
      <p>DeepSeek→화웨이 16만장 $2.56B는 잠재수요, 납기 1년+. CoreWeave backlog $104B, 조정OP $128M &lt; 이자 $640M.</p>
      <table>
        <tr><th>날</th><th>이벤트</th></tr>
        <tr><td>9/9</td><td>Apple — 가격 올려도 수요가 받치는가</td></tr>
        <tr><td>9/10</td><td>Oracle · Nvidia GS · PPI · 만기/리밸런싱. 종가를 펀더멘탈로 읽지 말 것</td></tr>
        <tr><td>9/11</td><td>CPI Core 예상 2.5%</td></tr>
        <tr><td>9/18 전후</td><td>엔시날 발표 가능. 의결 ≠ 계약</td></tr>
      </table>
      <div class="note"><b>Hartnett −10%.</b> 스윕 단독이 아니라 10Y 5%+CAPEX 둔화+수익화 실망이 겹칠 때. 스윕만이면 −3~−7%.</div>
      <p>포트: AI 40~50 / Non-AI 20~30 / 현금 30. 임계 10Y 5%, 유가 $120, CAPEX 증가율.</p>
    </div>
  </div>
  <p class="foot">매수·매도 권유가 아닙니다. 애플 LTA·폴더블 ASP·BOM 34%·엔시날 EPC·원전 8기·DeepSeek $2.56B는 보도·추정. DRAM $154.73B·Arm 80사·후티 73·DC $75.2B는 교차확인. 밸류는 9/4 종가.</p>
</div>
</body>
</html>
"""


def write_html() -> Path:
    text = html()
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_LECTURE.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(text, encoding="utf-8")
    OUT_LECTURE.write_text(text, encoding="utf-8")
    print("wrote", OUT_HTML, OUT_HTML.stat().st_size)
    return OUT_HTML


def render(html_path: Path) -> Path:
    pdf = Path("/tmp/sep08_oneboard.pdf")
    udir = Path("/tmp/chrome-oneboard")
    udir.mkdir(exist_ok=True)
    cmd = [
        "google-chrome",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--hide-scrollbars",
        f"--user-data-dir={udir}",
        "--no-pdf-header-footer",
        "--virtual-time-budget=8000",
        f"--print-to-pdf={pdf}",
        html_path.resolve().as_uri(),
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        proc.wait(timeout=25)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    # wait briefly if chrome wrote then hung
    for _ in range(20):
        if pdf.exists() and pdf.stat().st_size > 20_000:
            break
        time.sleep(0.4)
    if proc.poll() is None:
        proc.kill()
    if not pdf.exists():
        raise SystemExit("pdf not written")
    from PIL import Image

    doc = fitz.open(pdf)
    frames = []
    tmp = Path("/tmp/sep08_one_pages")
    tmp.mkdir(exist_ok=True)
    for i, page in enumerate(doc):
        pix = page.get_pixmap(matrix=fitz.Matrix(1.55, 1.55), alpha=False)
        p = tmp / f"p{i:02d}.png"
        pix.save(str(p))
        frames.append(Image.open(p).convert("RGB"))
    w = max(im.width for im in frames)
    h = sum(im.height for im in frames)
    canvas = Image.new("RGB", (w, h), (238, 241, 247))
    y = 0
    for im in frames:
        canvas.paste(im, (0, y))
        y += im.height
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    import numpy as np

    arr = np.asarray(canvas)
    bg = np.array([238, 241, 247])
    diff = np.abs(arr.astype(np.int16) - bg).sum(axis=2)
    ys = np.where((diff > 12).any(axis=1))[0]
    xs = np.where((diff > 12).any(axis=0))[0]
    cropped = canvas.crop(
        (max(int(xs[0]) - 8, 0), max(int(ys[0]) - 8, 0),
         min(int(xs[-1]) + 8, canvas.width), min(int(ys[-1]) + 16, canvas.height))
    )
    cropped.save(OUT_PNG, optimize=True)
    print("wrote", OUT_PNG, OUT_PNG.stat().st_size, "pages", len(frames), "px", cropped.size)
    return OUT_PNG


def to_artifact(png: Path) -> Path:
    from PIL import Image

    ART.mkdir(parents=True, exist_ok=True)
    im = Image.open(png).convert("RGB")
    # keep one readable long image
    dest = ART / "sep08_oneboard.webp"
    im.save(dest, "WEBP", quality=82, method=4)
    # also png copy in artifacts if size allows
    dest_png = ART / "sep08_oneboard.png"
    if png.stat().st_size < 8_000_000:
        dest_png.write_bytes(png.read_bytes())
    print("artifact", dest, dest.stat().st_size)
    return dest


if __name__ == "__main__":
    D.assert_all()
    path = write_html()
    png = render(path)
    to_artifact(png)
    print("oneboard ok")
