#!/usr/bin/env python3
"""Generate HTML / Markdown / JSON visuals for the panel regime baseline."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from charts_regime import render_all
from panel_regime_model import (
    ASSET_KEYS,
    ASSET_LABELS_KO,
    FACTOR_LABELS_KO,
    HORIZONS,
    run_baseline,
)

ROOT = Path("/workspace")
REPORTS = ROOT / "reports"
CHARTS = REPORTS / "charts_regime"
HTML_PATH = REPORTS / "2026-08-21-regime-dashboard.html"
STANDALONE_PATH = REPORTS / "2026-08-21-regime-standalone.html"
MD_PATH = REPORTS / "VIEW_THIS_REPORT.md"
JSON_PATH = REPORTS / "2026-08-21-regime-baseline.json"
PDF_PATH = REPORTS / "2026-08-21-regime-baseline.pdf"
README_PATH = REPORTS / "README.md"


def _pt(value: float) -> str:
    return f"{value:,.0f}"


def write_json(snapshot: dict) -> None:
    JSON_PATH.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")


def write_readme() -> None:
    README_PATH.write_text(
        """# 패널 합성 국면 모델 — 결과 보기

| 파일 | 여는 방법 |
|---|---|
| `VIEW_THIS_REPORT.md` | Cursor·GitHub에서 바로 보임 |
| `2026-08-21-regime-standalone.html` | 다운로드 후 브라우저. 인터넷 불필요 |
| `2026-08-21-regime-dashboard.html` | 브라우저. Chart.js 차트 |
| `2026-08-21-regime-baseline.pdf` | 차트 7쪽 PDF |
| `charts_regime/*.png` | 정적 차트 |
| `2026-08-21-regime-baseline.json` | 원숫자 스냅샷 |

재생성:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/generate_regime_report.py
python3 scripts/test_regime_baseline.py
```

투자 참고용 · 투자 권유 아님
""",
        encoding="utf-8",
    )


def write_markdown(snapshot: dict) -> None:
    h = snapshot["horizons"]
    e = snapshot["execution"]
    regimes = snapshot["regimes"]

    def regime_row(code: str) -> str:
        cells = " | ".join(f"{h[hz]['disp'][code]}%" for hz in HORIZONS)
        return f"| {code} | {regimes[code]['name']} | {cells} |"

    def alloc_row(asset: str) -> str:
        cells = " | ".join(f"{h[hz]['alloc'][asset]*100:.1f}%" for hz in HORIZONS)
        return f"| {ASSET_LABELS_KO[asset]} | {cells} |"

    def kospi_row(label: str, key: str) -> str:
        cells = " | ".join(_pt(h[hz]["proj"][key]) for hz in HORIZONS)
        return f"| {label} | {cells} |"

    factor_keys = list(h["3M"]["physical"]) + list(h["3M"]["financial"])

    def factor_row(key: str) -> str:
        cells = []
        for hz in HORIZONS:
            bucket = "physical" if key in h[hz]["physical"] else "financial"
            cells.append(f"{h[hz][bucket][key]:+.2f}")
        return f"| {FACTOR_LABELS_KO[key]} | {' | '.join(cells)} |"

    upside_3m = (h["3M"]["proj"]["p90"] / e["kospi"] - 1.0) * 100
    down_3m = (h["3M"]["proj"]["p10"] / e["kospi"] - 1.0) * 100
    vs_mean_3m = (h["3M"]["proj"]["expected_level"] / e["kospi"] - 1.0) * 100
    vs_p50_12m = (e["kospi"] / h["12M"]["proj"]["p50"] - 1.0) * 100

    md = f"""# 패널 합성 국면 모델 — 베이스라인 결과

**2026-08-21** · 3M / 6M / 12M 소프트맥스 국면 · 코스피 혼합 분위수 · 클러스터 실행 점검

투자 참고용 · 투자 권유 아님 · 배분 변경은 사람 검토 필요

## 한 줄 결론

3개월은 **후기검증(B) 33%**가 1위다. 시계를 1년으로 늘리면 **연착륙·순환(C) 28%**가 1위가 된다. 실행 등급은 **NORMAL**. DDR5 현물 프리미엄 **+18.5%**가 메모리 스트레스를 차단했고, 코스피 **6,852**는 12개월 혼합분포 중앙값(6,870)과 거의 같다.

## KPI

| 항목 | 값 | 읽기 |
|---|---|---|
| 3M 상태벡터 | P **{h['3M']['p']:+.3f}** / F **{h['3M']['f']:+.3f}** | 실물은 강한데 금융은 살짝 눌림 |
| 6M 상태벡터 | P **{h['6M']['p']:+.3f}** / F **{h['6M']['f']:+.3f}** | 실물 모멘텀 완화 |
| 12M 상태벡터 | P **{h['12M']['p']:+.3f}** / F **{h['12M']['f']:+.3f}** | 원점 근처, 순환 구간 |
| 주도 국면 | 3M **B 33%** · 6M **B 29%** · 12M **C 28%** | 시계가 길수록 B → C |
| 실행 트리거 | **{e['level']}** | 스트레스 클러스터 0개 |
| 현물 프리미엄 | **{e['spread']:+.1f}%** | 52.73 / 44.50, DDR5 16Gb |
| 코스피 낙폭 | **{e['drawdown']*100:+.1f}%** | 6,852 / 고점 9,360 |
| 선행 PER | **{e['forward_pe']:.1f} / {e['valuation_ceiling']:.1f}** | 천장 아래 |

## 1. 상태공간 궤적

실물(P)은 3개월 +0.51에서 12개월 +0.03으로 빠지고, 금융(F)은 −0.17에서 −0.04로 조금 회복한다. 점은 A/B 사이(3M)에서 C 쪽으로 미끄러진다.

![상태공간](charts_regime/state_space.png)

| 시계 | P | F | 1위 | 2위 | 3위 |
|---|---:|---:|---|---|---|
| 3M | {h['3M']['p']:+.3f} | {h['3M']['f']:+.3f} | B {h['3M']['disp']['B']}% | B* {h['3M']['disp']['B*']}% | A {h['3M']['disp']['A']}% |
| 6M | {h['6M']['p']:+.3f} | {h['6M']['f']:+.3f} | B {h['6M']['disp']['B']}% | C {h['6M']['disp']['C']}% | A {h['6M']['disp']['A']}% |
| 12M | {h['12M']['p']:+.3f} | {h['12M']['f']:+.3f} | C {h['12M']['disp']['C']}% | B {h['12M']['disp']['B']}% | D {h['12M']['disp']['D']}% |

## 2. 국면 확률

![국면확률](charts_regime/regime_probs.png)

| 국면 | 이름 | 3M | 6M | 12M |
|---|---|---:|---:|---:|
{chr(10).join(regime_row(code) for code in regimes)}

A(재가속)는 22→14%, D(방어)는 7→20%. 단기 낙관과 장기 방어가 동시에 섞인다.

## 3. 정책 배분

확률가중 정책이다. 자동 리밸런싱이 아니다.

![배분](charts_regime/allocation.png)

| 자산 | 3M | 6M | 12M |
|---|---:|---:|---:|
{chr(10).join(alloc_row(asset) for asset in ASSET_KEYS)}

반도체 35.2%→31.4%, 현금 20.5%→24.3%. 전력망·비반도체 수출은 거의 고정이다.

## 4. 코스피 혼합 분위수

각 국면 앵커 밴드를 균등분포로 보고, 국면 확률로 섞은 뒤 분위수를 이분 탐색했다.

![코스피](charts_regime/kospi_fan.png)

| 항목 | 3M | 6M | 12M |
|---|---:|---:|---:|
{kospi_row("평균", "expected_level")}
{kospi_row("P10", "p10")}
{kospi_row("P50", "p50")}
{kospi_row("P90", "p90")}

현 6,852 기준:

- 3M 평균까지 **{vs_mean_3m:+.1f}%**, P10 **{down_3m:+.1f}%**, P90 **{upside_3m:+.1f}%**
- 12M P50(6,870) 대비 **{vs_p50_12m:+.1f}%** — 현재 레벨이 1년 중앙값에 붙어 있다

국면 앵커(전 시계 동일): A 8,200–9,300 · B 7,200–8,100 · B* 6,400–7,300 · C 6,200–7,000 · D 5,200–5,800

## 5. 팩터

![팩터](charts_regime/factor_heatmap.png)

| 팩터 | 3M | 6M | 12M |
|---|---:|---:|---:|
{chr(10).join(factor_row(key) for key in factor_keys)}

실물(메모리·AI 수요·공급 규율)은 시계가 길수록 빠지고, 중국 수급은 더 음수다. 금융은 금리·환율과 외국인 수급이 회복되고, AI 자금조달만 −0.20 → −0.25로 남는다.

## 6. 실행 리스크

![실행](charts_regime/execution.png)

**등급: {e['level']}** · 활성 클러스터 없음

| 점검 | 값 | 임계 | 결과 |
|---|---|---|---|
| DDR5 16Gb 현·선 스프레드 | {e['spread']:+.1f}% (52.73 vs 44.50) | ≤0% 스트레스, ≤5% 감시 | 양호 |
| 실적 전망 | {e['earnings_outlook']:+.2f} | 스프레드≤0 이고 ≤−0.25면 memory | 미발동 |
| AI 자금조달 | {e['ai_financing']:+.2f} | ≤−0.50 | 미발동 |
| 금리·환율 + 외국인 | 평균 {(e['rates_fx']+e['foreign_flows'])/2:+.2f} | ≤−0.40 | 미발동 |
| 선행 PER | {e['forward_pe']:.1f} | 천장 {e['valuation_ceiling']:.1f} | 미발동 |
| 코스피 낙폭 | {e['drawdown']*100:+.1f}% | ≤−40% 딥 드로우다운 | 감시 문구만 |

엔진 메시지:

- {e['messages'][0]}
- {e['messages'][1]}
- {e['messages'][2]}

## 의사결정 규칙

배분 숫자는 국면 확률의 가중 평균이다. **자동 매매·자동 리밸런싱 신호가 아니다.** 할당 조정은 사람 검토가 필요하다.

관측일: 현물 2026-08-14, 계약 2026-07-31, 갭 14일(비교 가능). 코스피 6,852 / 롤링 고점 9,360.
"""
    MD_PATH.write_text(md, encoding="utf-8")


def write_standalone(snapshot: dict, chart_paths: dict) -> None:
    h = snapshot["horizons"]
    e = snapshot["execution"]

    def img(name: str) -> str:
        raw = Path(chart_paths[name]).read_bytes()
        return "data:image/png;base64," + base64.b64encode(raw).decode("ascii")

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>패널 합성 국면 모델 — 베이스라인 (오프라인)</title>
<style>
body {{ font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; background:#F3F5F9; color:#1A1A1A; margin:0; padding:28px 18px 64px; }}
.wrap {{ max-width:980px; margin:0 auto; }}
.hero {{ background:#0F2043; color:#fff; border-radius:16px; padding:28px 30px; }}
.hero h1 {{ margin:8px 0; font-size:26px; }}
.hero p {{ color:#C5D0E0; }}
.kpi {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin:18px 0; }}
.kpi div {{ background:#fff; border:1px solid #D5DCE6; border-radius:12px; padding:12px; }}
.kpi b {{ display:block; font-size:20px; color:#0F2043; }}
.kpi span {{ color:#5B6573; font-size:12px; }}
h2 {{ color:#0F2043; border-bottom:3px solid #0F2043; padding-bottom:6px; }}
img {{ width:100%; background:#fff; border:1px solid #D5DCE6; border-radius:12px; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; background:#fff; }}
th {{ background:#0F2043; color:#fff; padding:8px; text-align:left; }}
td {{ padding:8px; border-bottom:1px solid #D5DCE6; }}
.call {{ background:#EEF2F8; border-left:4px solid #1E407C; padding:12px 14px; border-radius:0 10px 10px 0; }}
@media (max-width:800px) {{ .kpi {{ grid-template-columns:1fr 1fr; }} }}
</style>
</head>
<body>
<div class="wrap">
<div class="hero">
  <div style="color:#B8943A;font-weight:700;font-size:12px;">PANEL SYNTHESIS · 2026-08-21 · {e['level']}</div>
  <h1>실물은 식고, 국면은 B에서 C로</h1>
  <p>3개월 후기검증(B) 33%. 1년 연착륙·순환(C) 28%. 현물 프리미엄 +18.5%. 코스피 6,852는 12개월 중앙값에 붙어 있다.</p>
</div>
<div class="kpi">
  <div><span>3M 상태</span><b>P {h['3M']['p']:+.2f}</b><span>F {h['3M']['f']:+.2f} · B {h['3M']['disp']['B']}%</span></div>
  <div><span>12M 상태</span><b>P {h['12M']['p']:+.2f}</b><span>F {h['12M']['f']:+.2f} · C {h['12M']['disp']['C']}%</span></div>
  <div><span>현물 프리미엄</span><b>{e['spread']:+.1f}%</b><span>DDR5 16Gb</span></div>
  <div><span>코스피 낙폭</span><b>{e['drawdown']*100:+.1f}%</b><span>6,852 / 9,360</span></div>
</div>
<div class="call">배분 숫자는 국면 확률의 가중 평균이다. 자동 리밸런싱이 아니다. 투자 권유 아님.</div>
<h2>1. 상태공간</h2>
<img src="{img('state_space')}" alt="상태공간"/>
<h2>2. 국면 확률</h2>
<img src="{img('regime_probs')}" alt="국면 확률"/>
<h2>3. 정책 배분</h2>
<img src="{img('allocation')}" alt="정책 배분"/>
<table>
<tr><th>자산</th><th>3M</th><th>6M</th><th>12M</th></tr>
{''.join(f"<tr><td>{ASSET_LABELS_KO[a]}</td><td>{h['3M']['alloc'][a]*100:.1f}%</td><td>{h['6M']['alloc'][a]*100:.1f}%</td><td>{h['12M']['alloc'][a]*100:.1f}%</td></tr>" for a in ASSET_KEYS)}
</table>
<h2>4. 코스피 혼합 분위수</h2>
<img src="{img('kospi_fan')}" alt="코스피"/>
<table>
<tr><th>항목</th><th>3M</th><th>6M</th><th>12M</th></tr>
<tr><td>평균</td><td>{_pt(h['3M']['proj']['expected_level'])}</td><td>{_pt(h['6M']['proj']['expected_level'])}</td><td>{_pt(h['12M']['proj']['expected_level'])}</td></tr>
<tr><td>P10</td><td>{_pt(h['3M']['proj']['p10'])}</td><td>{_pt(h['6M']['proj']['p10'])}</td><td>{_pt(h['12M']['proj']['p10'])}</td></tr>
<tr><td>P50</td><td>{_pt(h['3M']['proj']['p50'])}</td><td>{_pt(h['6M']['proj']['p50'])}</td><td>{_pt(h['12M']['proj']['p50'])}</td></tr>
<tr><td>P90</td><td>{_pt(h['3M']['proj']['p90'])}</td><td>{_pt(h['6M']['proj']['p90'])}</td><td>{_pt(h['12M']['proj']['p90'])}</td></tr>
</table>
<h2>5. 팩터</h2>
<img src="{img('factor_heatmap')}" alt="팩터"/>
<h2>6. 실행 리스크</h2>
<img src="{img('execution')}" alt="실행"/>
<p>{e['messages'][0]}<br/>{e['messages'][1]}<br/>{e['messages'][2]}</p>
</div>
</body>
</html>
"""
    STANDALONE_PATH.write_text(html, encoding="utf-8")


def write_pdf(chart_paths: dict) -> None:
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.image as mpimg
    import matplotlib.pyplot as plt

    pages = [
        ("state_space", "1. 상태공간 궤적"),
        ("regime_probs", "2. 국면 확률"),
        ("allocation", "3. 정책 배분"),
        ("kospi_fan", "4. 코스피 혼합 분위수"),
        ("factor_heatmap", "5. 팩터 스냅샷"),
        ("execution", "6. 실행 트리거"),
    ]
    with PdfPages(PDF_PATH) as pdf:
        fig, ax = plt.subplots(figsize=(11.0, 8.5))
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        fig.patch.set_facecolor("#0F2043")
        ax.text(0.08, 0.72, "PANEL SYNTHESIS", color="#B8943A", fontsize=14, fontweight="bold")
        ax.text(0.08, 0.58, "국면 모델 베이스라인", color="white", fontsize=28, fontweight="bold")
        ax.text(0.08, 0.46, "2026-08-21  ·  3M B 33%  ·  12M C 28%  ·  NORMAL", color="#C5D0E0", fontsize=13)
        ax.text(0.08, 0.28, "실물은 식고 국면은 B에서 C로 미끄러진다.\n현물 프리미엄 +18.5%. 코스피 6,852는 12개월 중앙값 근처.", color="#E8EDF7", fontsize=13)
        ax.text(0.08, 0.10, "투자 참고용 · 투자 권유 아님 · 배분 변경은 사람 검토", color="#8b97b0", fontsize=10)
        pdf.savefig(fig)
        plt.close(fig)
        for key, title in pages:
            fig, ax = plt.subplots(figsize=(11.0, 8.5))
            ax.axis("off")
            ax.set_title(title, loc="left", fontsize=14, color="#0F2043", pad=12)
            ax.imshow(mpimg.imread(chart_paths[key]))
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)


def write_html(snapshot: dict) -> None:
    h = snapshot["horizons"]
    e = snapshot["execution"]
    payload = json.dumps(
        {
            "horizons": HORIZONS,
            "codes": list(snapshot["regimes"]),
            "names": {c: snapshot["regimes"][c]["name"] for c in snapshot["regimes"]},
            "centroids": {
                c: [snapshot["regimes"][c]["p_coord"], snapshot["regimes"][c]["f_coord"]]
                for c in snapshot["regimes"]
            },
            "states": {hz: [h[hz]["p"], h[hz]["f"]] for hz in HORIZONS},
            "disp": {hz: h[hz]["disp"] for hz in HORIZONS},
            "alloc": {hz: [h[hz]["alloc"][a] * 100 for a in ASSET_KEYS] for hz in HORIZONS},
            "assets": [ASSET_LABELS_KO[a] for a in ASSET_KEYS],
            "proj": {hz: h[hz]["proj"] for hz in HORIZONS},
            "spot": e["kospi"],
            "factors": {
                "labels": [FACTOR_LABELS_KO[k] for k in list(h["3M"]["physical"]) + list(h["3M"]["financial"])],
                "values": {
                    hz: [
                        *(h[hz]["physical"][k] for k in h[hz]["physical"]),
                        *(h[hz]["financial"][k] for k in h[hz]["financial"]),
                    ]
                    for hz in HORIZONS
                },
            },
        },
        ensure_ascii=False,
    )

    def chips(hz: str) -> str:
        order = sorted(h[hz]["disp"], key=lambda c: h[hz]["disp"][c], reverse=True)
        top = order[0]
        return f"{top} {h[hz]['disp'][top]}%"

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>2026.08.21 패널 합성 국면 모델 — 베이스라인</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.3/dist/chart.umd.min.js"></script>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600;700&display=swap" rel="stylesheet"/>
  <style>
    :root {{
      --bg:#0b0f17; --surface:#121826; --surface2:#1a2235; --border:#2a3550;
      --text:#e8edf7; --muted:#8b97b0; --accent:#3b82f6; --gold:#B8943A;
      --green:#22c55e; --red:#ef4444; --amber:#f59e0b; --purple:#a855f7;
      --radius:14px; --shadow:0 8px 32px rgba(0,0,0,.35);
    }}
    * {{ box-sizing:border-box; margin:0; padding:0; }}
    html {{ scroll-behavior:smooth; }}
    body {{ font-family:'Noto Sans KR',sans-serif; background:var(--bg); color:var(--text); line-height:1.65; font-size:15px; }}
    .layout {{ display:grid; grid-template-columns:240px 1fr; min-height:100vh; }}
    nav {{ position:sticky; top:0; height:100vh; overflow:auto; background:var(--surface); border-right:1px solid var(--border); padding:22px 14px; }}
    nav .brand {{ color:var(--gold); font-size:11px; font-weight:700; letter-spacing:.08em; text-transform:uppercase; margin-bottom:14px; }}
    nav a {{ display:block; padding:8px 10px; border-radius:8px; color:var(--muted); text-decoration:none; font-size:13px; }}
    nav a:hover {{ background:var(--surface2); color:var(--text); }}
    main {{ padding:28px 36px 72px; max-width:1240px; }}
    .hero {{
      background:linear-gradient(135deg,#1e3a5f 0%,#0f172a 52%,#1a1040 100%);
      border:1px solid var(--border); border-radius:20px; padding:32px 34px; margin-bottom:22px;
    }}
    .hero h1 {{ font-size:26px; font-weight:800; line-height:1.3; margin:6px 0 8px; }}
    .hero p {{ color:#94a3b8; max-width:820px; }}
    .badge-row {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:16px; }}
    .badge {{ padding:4px 11px; border-radius:999px; font-size:12px; font-weight:600; border:1px solid var(--border); background:rgba(255,255,255,.05); }}
    .badge.g {{ border-color:#14532d; color:#86efac; background:rgba(34,197,94,.12); }}
    .badge.a {{ border-color:#78350f; color:#fcd34d; background:rgba(245,158,11,.12); }}
    .badge.b {{ border-color:#1e3a8a; color:#93c5fd; background:rgba(59,130,246,.12); }}
    .kpi {{ display:grid; grid-template-columns:repeat(5,1fr); gap:12px; margin-bottom:22px; }}
    .kpi .c, .card {{ background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); padding:16px 18px; box-shadow:var(--shadow); }}
    .kpi h3 {{ font-size:11px; color:var(--muted); }}
    .kpi .v {{ font-family:'IBM Plex Mono',monospace; font-size:22px; font-weight:700; margin-top:4px; }}
    .kpi .s {{ font-size:12px; color:var(--muted); margin-top:3px; }}
    section {{ margin-bottom:36px; scroll-margin-top:18px; }}
    section > h2 {{ font-size:20px; font-weight:700; margin-bottom:6px; display:flex; align-items:center; gap:10px; }}
    section > h2::before {{ content:''; width:4px; height:20px; background:var(--accent); border-radius:2px; }}
    .lead {{ color:var(--muted); font-size:14px; margin-bottom:14px; }}
    .grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; }}
    .chart {{ position:relative; height:340px; }}
    .chart.tall {{ height:400px; }}
    .call {{ border-left:3px solid var(--accent); background:rgba(59,130,246,.08); padding:12px 14px; border-radius:0 10px 10px 0; margin:14px 0; }}
    .call.warn {{ border-color:var(--amber); background:rgba(245,158,11,.08); }}
    table {{ width:100%; border-collapse:collapse; font-size:13px; margin-top:12px; }}
    th {{ background:#0f172a; color:#cbd5e1; text-align:left; padding:8px 10px; }}
    td {{ padding:8px 10px; border-bottom:1px solid var(--border); }}
    tr:nth-child(even) td {{ background:rgba(255,255,255,.02); }}
    .mono {{ font-family:'IBM Plex Mono',monospace; }}
    footer {{ color:var(--muted); font-size:12px; margin-top:28px; }}
    @media (max-width:1100px) {{
      .layout {{ grid-template-columns:1fr; }}
      nav {{ position:relative; height:auto; }}
      .kpi, .grid-2 {{ grid-template-columns:1fr; }}
      main {{ padding:18px 14px 56px; }}
    }}
  </style>
</head>
<body>
<div class="layout">
<nav>
  <div class="brand">Panel Synthesis</div>
  <a href="#top">요약</a>
  <a href="#state">상태공간</a>
  <a href="#regime">국면 확률</a>
  <a href="#alloc">정책 배분</a>
  <a href="#kospi">코스피 혼합</a>
  <a href="#factor">팩터</a>
  <a href="#exec">실행 리스크</a>
</nav>
<main>
  <div class="hero" id="top">
    <div class="badge-row"><span class="badge b">BASELINE 2026-08-21</span><span class="badge g">TRIGGER {e['level']}</span></div>
    <h1>패널 합성 국면 모델<br/>실물은 식고, 국면은 B에서 C로 미끄러진다</h1>
    <p>3개월은 후기검증(B) 33%. 1년은 연착륙·순환(C) 28%. 현물 프리미엄 +18.5%가 메모리 스트레스를 끄고, 코스피 6,852는 12개월 혼합 중앙값에 붙어 있다. 배분 숫자는 사람 검토용이다.</p>
    <div class="badge-row">
      <span class="badge">3M {chips('3M')}</span>
      <span class="badge">6M {chips('6M')}</span>
      <span class="badge a">12M {chips('12M')}</span>
      <span class="badge g">스트레스 0 / 4</span>
    </div>
  </div>

  <div class="kpi">
    <div class="c"><h3>3M 상태</h3><div class="v">P {h['3M']['p']:+.2f}</div><div class="s">F {h['3M']['f']:+.2f} · B {h['3M']['disp']['B']}%</div></div>
    <div class="c"><h3>12M 상태</h3><div class="v">P {h['12M']['p']:+.2f}</div><div class="s">F {h['12M']['f']:+.2f} · C {h['12M']['disp']['C']}%</div></div>
    <div class="c"><h3>3M 코스피 평균</h3><div class="v">{_pt(h['3M']['proj']['expected_level'])}</div><div class="s">P50 {_pt(h['3M']['proj']['p50'])} · P90 {_pt(h['3M']['proj']['p90'])}</div></div>
    <div class="c"><h3>현물 프리미엄</h3><div class="v" style="color:var(--green)">{e['spread']:+.1f}%</div><div class="s">DDR5 16Gb 52.73 / 44.50</div></div>
    <div class="c"><h3>코스피 낙폭</h3><div class="v" style="color:var(--amber)">{e['drawdown']*100:+.1f}%</div><div class="s">6,852 / 고점 9,360</div></div>
  </div>

  <section id="state">
    <h2>상태공간 궤적</h2>
    <p class="lead">실물 축은 +0.51 → +0.03, 금융 축은 −0.17 → −0.04. 3개월은 A/B/B* 삼각 경합, 12개월은 원점의 C.</p>
    <div class="card"><div class="chart tall"><canvas id="stateChart"></canvas></div></div>
    <table>
      <tr><th>시계</th><th>P</th><th>F</th><th>1위</th><th>2위</th><th>3위</th></tr>
      <tr><td>3M</td><td class="mono">{h['3M']['p']:+.3f}</td><td class="mono">{h['3M']['f']:+.3f}</td><td>B {h['3M']['disp']['B']}%</td><td>B* {h['3M']['disp']['B*']}%</td><td>A {h['3M']['disp']['A']}%</td></tr>
      <tr><td>6M</td><td class="mono">{h['6M']['p']:+.3f}</td><td class="mono">{h['6M']['f']:+.3f}</td><td>B {h['6M']['disp']['B']}%</td><td>C {h['6M']['disp']['C']}%</td><td>A {h['6M']['disp']['A']}%</td></tr>
      <tr><td>12M</td><td class="mono">{h['12M']['p']:+.3f}</td><td class="mono">{h['12M']['f']:+.3f}</td><td>C {h['12M']['disp']['C']}%</td><td>B {h['12M']['disp']['B']}%</td><td>D {h['12M']['disp']['D']}%</td></tr>
    </table>
  </section>

  <section id="regime">
    <h2>국면 확률</h2>
    <p class="lead">거리 제곱을 온도로 나눈 소프트맥스. 온도는 3M 0.52 / 6M 0.68 / 12M 0.78 — 시계가 길수록 분포가 평평해진다.</p>
    <div class="card"><div class="chart"><canvas id="regimeChart"></canvas></div></div>
    <div class="call">A는 22→14%로 줄고 D는 7→20%로 는다. 단기 재가속과 장기 방어가 한 모델 안에 같이 있다.</div>
  </section>

  <section id="alloc">
    <h2>정책 배분</h2>
    <p class="lead">국면별 정책 가중치의 확률 평균. 반도체 35.2%→31.4%, 현금 20.5%→24.3%.</p>
    <div class="card"><div class="chart"><canvas id="allocChart"></canvas></div></div>
    <table>
      <tr><th>자산</th><th>3M</th><th>6M</th><th>12M</th></tr>
      {''.join(f"<tr><td>{ASSET_LABELS_KO[a]}</td><td class='mono'>{h['3M']['alloc'][a]*100:.1f}%</td><td class='mono'>{h['6M']['alloc'][a]*100:.1f}%</td><td class='mono'>{h['12M']['alloc'][a]*100:.1f}%</td></tr>" for a in ASSET_KEYS)}
    </table>
  </section>

  <section id="kospi">
    <h2>코스피 혼합 분위수</h2>
    <p class="lead">국면 앵커 밴드를 균등분포로 섞었다. 현 6,852는 12M P50(6,870)과 같고, 3M 평균(7,388)보다는 아래다.</p>
    <div class="card"><div class="chart tall"><canvas id="kospiChart"></canvas></div></div>
    <table>
      <tr><th>항목</th><th>3M</th><th>6M</th><th>12M</th></tr>
      <tr><td>평균</td><td class="mono">{_pt(h['3M']['proj']['expected_level'])}</td><td class="mono">{_pt(h['6M']['proj']['expected_level'])}</td><td class="mono">{_pt(h['12M']['proj']['expected_level'])}</td></tr>
      <tr><td>P10</td><td class="mono">{_pt(h['3M']['proj']['p10'])}</td><td class="mono">{_pt(h['6M']['proj']['p10'])}</td><td class="mono">{_pt(h['12M']['proj']['p10'])}</td></tr>
      <tr><td>P50</td><td class="mono">{_pt(h['3M']['proj']['p50'])}</td><td class="mono">{_pt(h['6M']['proj']['p50'])}</td><td class="mono">{_pt(h['12M']['proj']['p50'])}</td></tr>
      <tr><td>P90</td><td class="mono">{_pt(h['3M']['proj']['p90'])}</td><td class="mono">{_pt(h['6M']['proj']['p90'])}</td><td class="mono">{_pt(h['12M']['proj']['p90'])}</td></tr>
    </table>
  </section>

  <section id="factor">
    <h2>팩터 스냅샷</h2>
    <p class="lead">메모리·AI 실물 수요는 빠지고, 금리·환율과 외국인 수급은 회복. AI 자금조달만 음수로 남는다.</p>
    <div class="card"><div class="chart tall"><canvas id="factorChart"></canvas></div></div>
  </section>

  <section id="exec">
    <h2>실행 리스크</h2>
    <p class="lead">클러스터 0개 → NORMAL. 딥 드로우다운(−40%)과 PER 천장은 아직 아니다.</p>
    <div class="grid-2">
      <div class="card">
        <h3 style="color:#94a3b8;font-size:13px;margin-bottom:8px;">트리거 보드</h3>
        <table>
          <tr><th>점검</th><th>값</th><th>결과</th></tr>
          <tr><td>현·선 스프레드</td><td class="mono">{e['spread']:+.1f}%</td><td>양호</td></tr>
          <tr><td>실적 전망</td><td class="mono">{e['earnings_outlook']:+.2f}</td><td>memory 미발동</td></tr>
          <tr><td>AI 자금조달</td><td class="mono">{e['ai_financing']:+.2f}</td><td>임계 −0.50 미달</td></tr>
          <tr><td>유동성 평균</td><td class="mono">{(e['rates_fx']+e['foreign_flows'])/2:+.2f}</td><td>임계 −0.40 미달</td></tr>
          <tr><td>선행 PER</td><td class="mono">{e['forward_pe']:.1f} / {e['valuation_ceiling']:.1f}</td><td>천장 아래</td></tr>
          <tr><td>낙폭</td><td class="mono">{e['drawdown']*100:+.1f}%</td><td>−40% 아님</td></tr>
        </table>
      </div>
      <div class="card">
        <h3 style="color:#94a3b8;font-size:13px;margin-bottom:8px;">엔진 메시지</h3>
        <div class="call">{e['messages'][0]}</div>
        <div class="call warn">{e['messages'][1]}</div>
        <div class="call">{e['messages'][2]}</div>
      </div>
    </div>
  </section>

  <footer>관측: 현물 2026-08-14, 계약 2026-07-31. 투자 참고용 · 투자 권유 아님 · 배분 변경은 사람 검토.</footer>
</main>
</div>
<script>
const D = {payload};
const REGIME_COLORS = {{A:'#22c55e',B:'#3b82f6','B*':'#a855f7',C:'#f59e0b',D:'#ef4444'}};
const HZ_COLORS = {{'3M':'#93c5fd','6M':'#60a5fa','12M':'#B8943A'}};
const ASSET_COLORS = ['#38bdf8','#a78bfa','#f59e0b','#34d399','#94a3b8'];

Chart.defaults.color = '#8b97b0';
Chart.defaults.borderColor = '#2a3550';
Chart.defaults.font.family = "'Noto Sans KR', sans-serif";

new Chart(document.getElementById('stateChart'), {{
  type: 'scatter',
  data: {{
    datasets: [
      ...D.codes.map(code => ({{
        label: code,
        data: [{{x:D.centroids[code][0], y:D.centroids[code][1]}}],
        backgroundColor: REGIME_COLORS[code],
        pointRadius: 11,
      }})),
      {{
        label: '궤적',
        data: D.horizons.map(hz => ({{x:D.states[hz][0], y:D.states[hz][1]}})),
        showLine: true,
        borderColor: '#B8943A',
        backgroundColor: '#B8943A',
        pointRadius: 7,
        pointStyle: 'rectRot',
      }}
    ]
  }},
  options: {{
    responsive:true, maintainAspectRatio:false,
    plugins: {{
      legend: {{ labels: {{ boxWidth:10 }} }},
      tooltip: {{ callbacks: {{ label: ctx => `${{ctx.dataset.label}}  P ${{ctx.parsed.x.toFixed(2)}}  F ${{ctx.parsed.y.toFixed(2)}}` }} }}
    }},
    scales: {{
      x: {{ title: {{display:true, text:'실물 P'}}, min:-0.55, max:0.9 }},
      y: {{ title: {{display:true, text:'금융 F'}}, min:-0.85, max:0.5 }}
    }}
  }}
}});

new Chart(document.getElementById('regimeChart'), {{
  type: 'bar',
  data: {{
    labels: D.codes.map(c => c),
    datasets: D.horizons.map(hz => ({{
      label: hz,
      data: D.codes.map(c => D.disp[hz][c]),
      backgroundColor: HZ_COLORS[hz],
    }}))
  }},
  options: {{
    responsive:true, maintainAspectRatio:false,
    plugins: {{ legend: {{ position:'top' }} }},
    scales: {{ y: {{ beginAtZero:true, max:42, title: {{display:true, text:'%'}} }} }}
  }}
}});

new Chart(document.getElementById('allocChart'), {{
  type: 'bar',
  data: {{
    labels: D.horizons,
    datasets: D.assets.map((name, i) => ({{
      label: name,
      data: D.horizons.map(hz => D.alloc[hz][i]),
      backgroundColor: ASSET_COLORS[i],
      stack: 'alloc',
    }}))
  }},
  options: {{
    responsive:true, maintainAspectRatio:false,
    scales: {{
      x: {{ stacked:true }},
      y: {{ stacked:true, max:100, title: {{display:true, text:'%'}} }}
    }}
  }}
}});

new Chart(document.getElementById('kospiChart'), {{
  type: 'bar',
  data: {{
    labels: D.horizons,
    datasets: [
      {{
        label: 'P10–P90',
        data: D.horizons.map(hz => [D.proj[hz].p10, D.proj[hz].p90]),
        backgroundColor: 'rgba(59,130,246,.28)',
        borderColor: '#60a5fa',
        borderWidth: 1,
        barPercentage: 0.35,
      }},
      {{
        label: '평균',
        type: 'scatter',
        data: D.horizons.map((hz, i) => ({{x:i, y:D.proj[hz].expected_level}})),
        backgroundColor: '#B8943A',
        pointStyle: 'rectRot',
        pointRadius: 7,
      }},
      {{
        label: 'P50',
        type: 'scatter',
        data: D.horizons.map((hz, i) => ({{x:i, y:D.proj[hz].p50}})),
        backgroundColor: '#e8edf7',
        pointRadius: 5,
      }}
    ]
  }},
  options: {{
    responsive:true, maintainAspectRatio:false,
    plugins: {{
      annotation: undefined,
      tooltip: {{ callbacks: {{ label: ctx => ctx.dataset.label + ' ' + (Array.isArray(ctx.raw) ? ctx.raw.map(v=>Math.round(v)).join('–') : Math.round(ctx.parsed.y)) }} }}
    }},
    scales: {{
      y: {{ min:5000, max:9500, title: {{display:true, text:'KOSPI'}} }},
      x: {{ type:'category', labels: D.horizons }}
    }}
  }}
}});

new Chart(document.getElementById('factorChart'), {{
  type: 'bar',
  data: {{
    labels: D.factors.labels,
    datasets: D.horizons.map(hz => ({{
      label: hz,
      data: D.factors.values[hz],
      backgroundColor: HZ_COLORS[hz],
    }}))
  }},
  options: {{
    indexAxis: 'y',
    responsive:true, maintainAspectRatio:false,
    scales: {{ x: {{ min:-1, max:1, title: {{display:true, text:'점수'}} }} }}
  }}
}});
</script>
</body>
</html>
"""
    HTML_PATH.write_text(html, encoding="utf-8")


def main() -> None:
    snapshot = run_baseline()
    REPORTS.mkdir(parents=True, exist_ok=True)
    chart_paths = render_all(snapshot, CHARTS)
    write_json(snapshot)
    write_html(snapshot)
    write_standalone(snapshot, chart_paths)
    write_markdown(snapshot)
    write_pdf(chart_paths)
    write_readme()
    print(f"wrote {HTML_PATH}")
    print(f"wrote {STANDALONE_PATH}")
    print(f"wrote {MD_PATH}")
    print(f"wrote {PDF_PATH}")
    print(f"wrote {JSON_PATH}")
    print(f"wrote charts in {CHARTS}")


if __name__ == "__main__":
    main()
