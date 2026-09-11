#!/usr/bin/env python3
"""9월 10~11일 Quick 코멘트를 차트 포함 한 장으로."""

from __future__ import annotations

import base64
import subprocess
import time
from pathlib import Path

import fitz

import sep11_data as D

ROOT = Path("/workspace")
CHARTS = ROOT / "reports" / "charts_sep11"
OUT_HTML = ROOT / "reports" / "2026-09-11-oneboard.html"
OUT_LECTURE = ROOT / "lectures" / "9월 11일 Quick 코멘트 한장.html"
OUT_PNG = ROOT / "reports" / "sep11-pages" / "oneboard.png"
ART = Path("/opt/cursor/artifacts")


def uri(name: str) -> str:
    raw = (CHARTS / name).read_bytes()
    return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")


def html() -> str:
    c1, c2, c3, c4 = uri("01_oracle.png"), uri("02_export.png"), uri("03_ust.png"), uri("04_mlcc.png")
    clo, chi = D.orcl_customer_capex()
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<title>9월 11일 Quick 코멘트 — 한 장</title>
<style>
:root {{ --navy:#0f2043; --navy2:#1e407c; --gold:#b8943a; --ink:#1a1a1a;
  --muted:#4b5563; --line:#d5dce6; --bg:#eef1f7; --green:#166534; --red:#991b1b; }}
* {{ box-sizing:border-box; }}
html,body {{ margin:0; padding:0; background:var(--bg); color:var(--ink);
  font-family:"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif; }}
.board {{ width:1240px; margin:0 auto; padding:16px 16px 22px; }}
.kicker {{ color:var(--gold); font-weight:800; font-size:12px; }}
h1 {{ color:var(--navy); font-size:26px; line-height:1.2; margin:4px 0 8px; }}
.hero {{ background:var(--navy); color:#fff; border-radius:12px; padding:13px 16px; margin-bottom:10px; font-size:14px; line-height:1.5; }}
.hero b {{ color:var(--gold); }}
.kpi {{ display:grid; grid-template-columns:repeat(6,1fr); gap:7px; margin-bottom:10px; }}
.kpi div {{ background:#fff; border:1px solid var(--line); border-radius:10px; padding:8px 9px; }}
.kpi h3 {{ margin:0; font-size:10.5px; color:var(--navy2); }}
.kpi .n {{ font-size:17px; font-weight:800; color:var(--navy); }}
.kpi p {{ margin:2px 0 0; font-size:10.8px; color:var(--muted); line-height:1.3; }}
.cols {{ display:grid; grid-template-columns:1fr 1fr; gap:8px; }}
.card {{ background:#fff; border:1px solid var(--line); border-radius:12px; padding:11px 12px; }}
.card h2 {{ margin:0 0 6px; color:var(--navy); font-size:15px; border-bottom:2px solid var(--navy); padding-bottom:4px; }}
.card p, .card li {{ font-size:12.3px; line-height:1.42; margin:0 0 5px; }}
.card ul {{ margin:0 0 5px; padding-left:17px; }}
.wide {{ grid-column:1/-1; }}
img {{ width:100%; border-radius:8px; border:1px solid var(--line); display:block; margin:5px 0; }}
table {{ width:100%; border-collapse:collapse; font-size:11.5px; margin:5px 0; }}
th {{ background:var(--navy); color:#fff; padding:4px 6px; text-align:left; }}
td {{ padding:4px 6px; border-bottom:1px solid var(--line); }}
tr:nth-child(even) td {{ background:#f7f9fc; }}
.pos {{ color:var(--green); font-weight:700; }}
.neg {{ color:var(--red); font-weight:700; }}
.note {{ background:#fff8e7; border-left:4px solid var(--gold); padding:6px 8px; border-radius:0 8px 8px 0; font-size:12px; margin:5px 0; }}
.ok {{ background:#e8f5e9; border-left:4px solid var(--green); padding:6px 8px; border-radius:0 8px 8px 0; font-size:12px; margin:5px 0; }}
.risk {{ background:#fdecea; border-left:4px solid var(--red); padding:6px 8px; border-radius:0 8px 8px 0; font-size:12px; margin:5px 0; }}
.flow {{ display:flex; flex-wrap:wrap; gap:5px; align-items:center; margin:5px 0; }}
.flow span {{ background:var(--navy); color:#fff; padding:3px 7px; border-radius:999px; font-size:11px; font-weight:700; }}
.flow i {{ color:var(--gold); font-style:normal; font-weight:800; }}
.tag {{ font-size:10px; font-weight:800; padding:1px 6px; border-radius:999px; background:#e8f1fb; color:var(--navy2); }}
.foot {{ color:var(--muted); font-size:10.5px; margin-top:8px; text-align:right; }}
@page {{ size: 1280px 4800px; margin:0; }}
</style>
</head>
<body>
<div class="board">
  <div class="kicker">2026. 9. 10~11.  ·  Quick 코멘트 + 미국장 PDF · 국채 TalkFile · 9/11 워드  ·  한 장</div>
  <h1>오라클이 막힌 고리를 풀고, 애플은 NAND에 모델을 넣기 시작했다</h1>
  <div class="hero">
    유가 $100 · 10Y ~5%는 여전히 임계. 그런데 <b>Oracle RPO $664B</b>의 절반이 36개월 내 매출이 되고, 신규 $30B는 선급금·BYOH라 자기 돈이 안 든다. 아이폰 듀오의 온디바이스 AI는 NPU가 아니라 <b>작은 모델 + NAND 계층화</b>다. 9월 초 메모리 수출은 폭발하나 DRAM 단가 MoM −18.8%는 첫 균열. 금리 때문에 삼전닉스를 줄일 이유는, 지금 이익이 나오는 한, 없다.
  </div>
  <div class="kpi">
    <div><h3>Oracle RPO</h3><div class="n">${D.ORCL_RPO_B}B</div><p>QoQ +${D.ORCL_RPO_QOQ_B}B · YoY +${D.ORCL_RPO_YOY_B}B · 36개월 내 50%</p></div>
    <div><h3>OCI</h3><div class="n">+{D.ORCL_OCI_YOY}%</div><p>${D.ORCL_OCI_B}B / Cloud ${D.ORCL_CLOUD_B}B. SaaS는 +{D.ORCL_SAAS_YOY}%</p></div>
    <div><h3>순현금 Capex</h3><div class="n">≤${D.ORCL_FY27_NET_CAPEX_MAX}B</div><p>FY27 ${D.ORCL_FY27_CAPEX[0]}~{D.ORCL_FY27_CAPEX[1]}B 중 고객이 ${clo}~{chi}B</p></div>
    <div><h3>DRAM 수출</h3><div class="n">+{D.DRAM_YOY:.0f}%</div><p>YoY. 단가 MoM <span class="neg">{D.DRAM_ASP_MOM}%</span></p></div>
    <div><h3>30Y 입찰</h3><div class="n">{D.UST30_AUCTION}%</div><p>Indirect {D.UST30_INDIRECT}%. 바이백 51.9/60억$</p></div>
    <div><h3>아이폰 듀오</h3><div class="n">5.4+7.6"</div><p>A20 Pro · 베이퍼챔버. 낙관 26년 600만대</p></div>
  </div>

  <div class="cols">
    <div class="card">
      <h2>1. Oracle — 자금조달 리스크가 한 단계 내려왔다 <span class="tag">공식 확인</span></h2>
      <img src="{c1}" alt="Oracle"/>
      <ul>
        <li>매출 $19.3B(+30%). Cloud $11.6B = OCI $7.4B(+121%) + SaaS $4.2B(+10%). 엔진이 SW→AI IaaS.</li>
        <li>RPO $638B→$664B. 신규 AI 계약 $30B+. <b>RPO의 약 50%가 36개월 내 매출.</b></li>
        <li>Q1 Capex $28.5B, FCF −$5B, 순현금 Capex $18B. FY27 Capex $90~95B, 순현금 ≤$70B.</li>
        <li>신규 계약 대부분이 선급금·BYOH. 자기 자본 추가 부담 없음. FY28 이후 Capex/매출에 반영.</li>
        <li>850MW · GPU 30만장 인도. FY27 매출 ≥$90B, nGAAP EPS $8.10. ATM $20B 완료.</li>
      </ul>
      <div class="ok"><b>막힌 고리.</b> DC 완공 → 현금창출력 ↑ → 자체 조달 부담 ↓ → CDS 완화 가능성. 가이던스는 서프라이즈급 상향은 아님. 코어 MoM은 예상 부합.</div>
    </div>

    <div class="card">
      <h2>2. 국채 · 유가 — 수요 붕괴가 아니다</h2>
      <img src="{c3}" alt="국채"/>
      <p>30Y 5.308%에서 수요가 강했다. 금리가 높아 안 산 게 아니라, 높아지니 샀다. 입찰 직후 2bp 내린 뒤 다시 오른 것은 유가·PPI·재정 압력이 더 강하다는 뜻.</p>
      <p>바이백은 한도 $60억 중 $51.9억. 재무부가 5.3%대를 부담스러워하며 속도를 조절 중. <b>9/24 잔존 20~30년 바이백</b>이 다음 시험대.</p>
      <div class="risk"><b>임계.</b> 유가 $100이 며칠이 아니라 몇 달이냐. 일시적이면 조정 후 정상화. 수개월이면 10Y 5% 안착. $110~120 장기화면 스태그 위험. 10Y 5%는 주식 할인율, 30Y 5%초~6%는 재정·인플레 믿음.</div>
      <p>관찰: SOX 대비 한국 변동성이 낮으면 펀더를 보려는 세력. 울퉁불퉁은 불가피. 10/1 마이크론 + 엔비디아 코멘트.</p>
    </div>

    <div class="card">
      <h2>3. 아이폰 듀오 — 온디바이스는 NPU가 반쪽이다</h2>
      <p>5.4인치 겉 + 7.6인치 속. 18 Pro/Max와 함께 A20 Pro, 커스텀 베이퍼챔버(열을 넓게 분산, 쓰로틀링 ↓). 낙관 출하 26년 600만 · 27년 1,500만대 — <b>한 달 지켜볼 것.</b></p>
      <div class="flow"><span>3B 기본</span><i>→</i><span>2-bit 압축</span><i>→</i><span>LoRA 전문모듈</span><i>→</i><span>NAND에 저장</span></div>
      <table>
        <tr><th>주장</th><th>판단</th></tr>
        <tr><td>PC에서 작은 LLM은 처참하다</td><td class="pos">대체로 맞음</td></tr>
        <tr><td>그러므로 온디바이스는 쓸모없다</td><td class="neg">틀림</td></tr>
        <tr><td>칩·OS에 구워 넣으면 쓸 만하다</td><td class="pos">맞음</td></tr>
        <tr><td>아이폰이 ChatGPT를 대체한다</td><td class="neg">아님</td></tr>
        <tr><td>짧은 기능(요약·사진·메일)은 유리</td><td class="pos">맞음</td></tr>
        <tr><td>복잡한 일은 클라우드와 결합</td><td class="pos">맞음</td></tr>
      </table>
      <p>구조: 쉬운 일 → 아이폰 / 어려운 일 → Private Cloud Compute / 필요 시 ChatGPT. AFM 3 Core Advanced는 sparse. 모델 전체를 DRAM에 올리지 않고 NAND에서 선택 활성화. (별도 보도는 20B sparse, 요청당 1~4B 활성으로 설명.)</p>
      <div class="note"><b>메모리.</b> 모델 압축 → DRAM 부담 ↓. 기능·모듈 증가 → NAND ↑. 온디바이스 = NPU만이 아니라 LPDDR + NAND + 계층화. 9/8 애플 NAND 장기계약과 같은 줄.</div>
    </div>

    <div class="card">
      <h2>4. 9월 초 메모리 수출 — 금액 폭발, 단가는 갈린다 <span class="tag">TRASS 1~10일</span></h2>
      <img src="{c2}" alt="수출"/>
      <table>
        <tr><th></th><th>금액</th><th>YoY</th><th>MoM</th><th>단가 MoM</th></tr>
        <tr><td>메모리</td><td>$10.39B</td><td class="pos">+378%</td><td>+30%</td><td class="neg">−8.2%</td></tr>
        <tr><td>DRAM</td><td>$5.01B</td><td class="pos">+496%</td><td>+8.4%</td><td class="neg">−18.8%</td></tr>
        <tr><td>Flash</td><td>$0.72B</td><td class="pos">+363%</td><td>−7.6%</td><td class="neg">−32.8%</td></tr>
        <tr><td>MCP</td><td>$3.92B</td><td class="pos">+293%</td><td class="pos">+87%</td><td class="pos">+31%</td></tr>
        <tr><td>DRAM모듈</td><td>$3.86B</td><td class="pos">+578%</td><td class="pos">+1,089%</td><td class="pos">+279%</td></tr>
      </table>
      <p>모듈 +1,089%는 전월 기저. 그래도 단가 +279%는 고용량 DIMM 수요. MCP는 금액·단가 동반 상승 = 믹스 개선. <b>DRAM 단가 MoM 하락이 가격 모멘텀의 첫 시그널.</b> 관세청 9/1~10 반도체 $16.5B(+270%).</p>
      <div class="ok"><b>금리 ↑ ≠ 삼전닉스 축소.</b> 먼 성장보다 지금 이익. 금리 지속 → 현재 이익이 완충. 금리 안정 → 밸류 재평가. ETF는 개인 매도에도 유입.</div>
    </div>

    <div class="card">
      <h2>5. MLCC · 두산 · PSK — 전력 vs 신호 vs 소재 vs 장비</h2>
      <img src="{c4}" alt="MLCC"/>
      <p>Global X MLCC ETF(티커 MLCC) 9/11 상장. 벤치 삼성전기 20.3%, 무라타 20.5%, 삼화콘덴서 2.9%.</p>
      <p>아모텍: 시총 3,000억 미만, 거의 상한가. BBC로 AI 광·전기 케이블 진입 → 고용량·고압 교차판매. 매출 26년 490억 → 27년 840억. 상반기 적자라 연간 PER 20~30배. 체크=고객 승인 · BBC 양산 · 고압 매출. 단기 트레이딩 시각 있음.</p>
      <p>두산 전자BG: 증평 가동 109.8% · 김천 102.7%. 태국 2028, 중국 등 증설 검토. 상반기 매출 1.29조. 병목은 Nittobo T-glass 50만㎡ 독점. 추격 합쳐도 못 따라감.</p>
      <p>PSK: Descum(찌꺼기 청소)+Fluxless Reflow(GENEVA). 3Q 매출 825억(+74% QoQ) / OP 350억. 27년 3,893억 / OP 1,504억. HBM+CoWoS+OSAT.</p>
    </div>

    <div class="card">
      <h2>6. 개인정보 과징금 · 앞으로</h2>
      <p>고의·중과실 3년 내 반복 또는 피해 1,000만명+ → 매출 10% 과징금. EDR 지니언스 · 종합보안 안랩 · 문서 파수 · IAM · MDR SK쉴더스(비상장).</p>
      <table>
        <tr><th>날</th><th>볼 것</th></tr>
        <tr><td>이미</td><td>9/11 코어 MoM 예상 부합. 유가→CPI 전이가 아직인지</td></tr>
        <tr><td>9/24</td><td>초장기 바이백 60억을 채우나</td></tr>
        <tr><td>10/1</td><td>마이크론 실적 + 엔비디아 후속 코멘트</td></tr>
        <tr><td>한 달</td><td>아이폰 듀오 수요가 $1,999를 받치나</td></tr>
      </table>
      <div class="note"><b>한 줄.</b> 매크로는 울퉁불퉁. 펀더의 가장 역한 고리(오라클 자금)는 오늘 완화. 온디바이스는 NAND를 같이 보고, 수출은 DRAM 단가 MoM을 같이 보라.</div>
    </div>
  </div>
  <p class="foot">매수·매도 권유가 아닙니다. Oracle RPO·OCI·Capex, 30Y 입찰은 공식/보도 확인. TRASS 1~10일·듀오 출하 600만·아모텍 490→840억은 잠정·추정. AFM 3B는 코멘트 프레임, 별도 보도는 20B sparse.</p>
</div>
</body>
</html>
"""


def write_html() -> Path:
    text = html()
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_LECTURE.parent.mkdir(parents=True, exist_ok=True)
    OUT_PNG.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(text, encoding="utf-8")
    OUT_LECTURE.write_text(text, encoding="utf-8")
    print("wrote", OUT_HTML, OUT_HTML.stat().st_size)
    return OUT_HTML


def render(html_path: Path) -> Path:
    from PIL import Image
    import numpy as np

    pdf = Path("/tmp/sep11_oneboard.pdf")
    udir = Path("/tmp/chrome-sep11")
    udir.mkdir(exist_ok=True)
    if pdf.exists():
        pdf.unlink()
    cmd = [
        "google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
        "--hide-scrollbars", f"--user-data-dir={udir}", "--no-pdf-header-footer",
        "--virtual-time-budget=8000", f"--print-to-pdf={pdf}",
        html_path.resolve().as_uri(),
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        proc.wait(timeout=25)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)
    for _ in range(20):
        if pdf.exists() and pdf.stat().st_size > 20_000:
            break
        time.sleep(0.4)
    if proc.poll() is None:
        proc.kill()
    if not pdf.exists():
        raise SystemExit("pdf not written")
    doc = fitz.open(pdf)
    frames = []
    tmp = Path("/tmp/sep11_one_pages")
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
    arr = np.asarray(canvas)
    bg = np.array([238, 241, 247])
    diff = np.abs(arr.astype(np.int16) - bg).sum(axis=2)
    ys = np.where((diff > 12).any(axis=1))[0]
    xs = np.where((diff > 12).any(axis=0))[0]
    cropped = canvas.crop((
        max(int(xs[0]) - 8, 0), max(int(ys[0]) - 8, 0),
        min(int(xs[-1]) + 8, canvas.width), min(int(ys[-1]) + 16, canvas.height),
    ))
    cropped.save(OUT_PNG, optimize=True)
    print("wrote", OUT_PNG, cropped.size, OUT_PNG.stat().st_size)
    return OUT_PNG


def to_artifact(png: Path) -> Path:
    from PIL import Image
    ART.mkdir(parents=True, exist_ok=True)
    im = Image.open(png).convert("RGB")
    dest = ART / "sep11_oneboard.webp"
    im.save(dest, "WEBP", quality=82, method=4)
    (ART / "sep11_oneboard.png").write_bytes(png.read_bytes())
    print("artifact", dest, dest.stat().st_size)
    return dest


if __name__ == "__main__":
    D.assert_all()
    path = write_html()
    png = render(path)
    to_artifact(png)
    print("sep11 oneboard ok")
