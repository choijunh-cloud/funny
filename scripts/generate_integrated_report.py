#!/usr/bin/env python3
"""8/18–20 통합 보고서 일괄 생성."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_integrated_docx import CHART_DIR, build as build_docx
from generate_integrated_html import build as build_html

README = Path("/workspace/reports/README.md")


def main():
    html = build_html()
    docx = build_docx(CHART_DIR)
    prev = README.read_text(encoding="utf-8") if README.exists() else ""
    block = """
# 2026.08.18–20 통합 시각화 보고서

업로드 워드 11개를 한 권으로 재구성했습니다.

| 파일 | 용도 |
|---|---|
| `2026-08-18-20-통합-시각화보고서.html` | 인터랙티브 (Chart.js) |
| `../lectures/8월 18-20일 통합 시장 시각화 보고서.docx` | 인쇄·배포, 차트 삽입 |
| `charts_integrated/*.png` | 정적 차트 |

```bash
python3 scripts/test_integrated_numbers.py
python3 scripts/generate_integrated_report.py
```
"""
    if "2026.08.18–20 통합" not in prev:
        README.write_text(prev.rstrip() + "\n" + block, encoding="utf-8")
    print(f"html {html} ({html.stat().st_size})")
    print(f"docx {docx} ({docx.stat().st_size})")


if __name__ == "__main__":
    main()
