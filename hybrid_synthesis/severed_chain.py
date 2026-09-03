"""Write document 4 (절단된 사슬) as a standalone HTML + JSON bundle."""

from __future__ import annotations

import json
from pathlib import Path

from hybrid_synthesis.v2 import snapshot

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


def render_html() -> str:
    head = (TEMPLATE_DIR / "severed_head.html").read_text(encoding="utf-8")
    body = (TEMPLATE_DIR / "severed_body.html").read_text(encoding="utf-8")
    script = (TEMPLATE_DIR / "severed_chain.js").read_text(encoding="utf-8")
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
{head}
</head>
<body>
{body}
<script>
{script}
</script>
</body>
</html>
"""


def write_v2_reports(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    html_path = out_dir / "2026-09-05-severed-chain.html"
    json_path = out_dir / "2026-09-05-severed-chain.json"
    md_path = out_dir / "SEVERED_CHAIN.md"
    html_path.write_text(render_html(), encoding="utf-8")
    payload = snapshot()
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(_markdown(payload), encoding="utf-8")
    return [html_path, json_path, md_path]


def _markdown(payload: dict) -> str:
    book = payload["book_c"]
    idx = payload["index"]
    lines = [
        "# 절단된 사슬 — 하이브리드 전이 모형 v2",
        "",
        payload["disclaimer"],
        "",
        f"- 기준일 `{payload['as_of']}` · KOSPI `{payload['index_spot']:,.2f}` · 브렌트 `${payload['oil_brent']:.0f}`",
        f"- 확률가중 연말 **{idx['expected_v2']:,.0f}** (v1 {idx['expected_v1']:,.0f})",
        f"- 인상확률 35% → 63% → **50%** · S3 꼬리 20% → **13%** · S1 상단 8,255 → **7,960**",
        f"- 채택 북 C 초과수익 **+0.24%p** · S3 하방 방어 **{book['downside_defense']:+.2f}%p**",
        "",
        "## 북 C (이름 유지, 무게만 이동)",
        "",
        "| # | 코드 | 종목 | 버킷 | v3 |",
        "|---:|---|---|---|---:|",
    ]
    for item in book["names"]:
        lines.append(
            f"| {item['rank']} | `{item['ticker']}` | {item['name']} | {item['bucket']} | {item['weight_v3']:.1f}% |"
        )
    lines += [
        "",
        "반도체 45 / 짧은듀레이션 25 / 유가↓ 10 / 헤지 20. 삼성 = 하이닉스 13.5%.",
        "",
        "```bash",
        "python3 -m hybrid_synthesis --doc4",
        "python3 -m unittest hybrid_synthesis.tests.test_v2",
        "```",
        "",
    ]
    return "\n".join(lines)
