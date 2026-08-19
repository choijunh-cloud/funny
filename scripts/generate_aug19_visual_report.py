#!/usr/bin/env python3
"""8/19 시각화 보고서 일괄 생성: 차트 + HTML + Word."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from charts_aug19 import render_all
from generate_aug19_docx import CHART_DIR, build as build_docx
from generate_aug19_html import build as build_html

README = Path("/workspace/reports/README.md")


def write_readme():
    README.write_text(
        """# 2026.08.19 시장상황 시각화 보고서

당일 공개 퀵코멘트를 **차트·표 중심**으로 재구성했습니다. 매수·매도 추천이 아닙니다.

## 열기

| 파일 | 용도 |
|---|---|
| `2026-08-19-시장상황-시각화보고서.html` | 인터랙티브 차트 (Chart.js, 인터넷 필요) |
| `../lectures/8월 19일 시장상황 시각화 보고서.docx` | 인쇄·배포용. 차트 PNG 삽입 |
| `charts/*.png` | 워드에 넣은 정적 차트 |

## 다시 만들기

```bash
python3 -m pip install -r requirements.txt
cd scripts && python3 generate_aug19_visual_report.py
python3 test_aug19_numbers.py
```

## 범위

매크로(금리·엔캐리·재무부 바이백) · 원/달러 민감도 · 하이닉스 환원 · 본주/ADR 밸류 · HBM 논쟁 · 마벨–구글 · 삼성 파운드리 · NVIDIA/OpenAI · 이수페타시스 · 기가비스.

숫자 원천은 `scripts/aug19_data.py`입니다.
""",
        encoding="utf-8",
    )


def main():
    paths = render_all(CHART_DIR)
    html = build_html()
    docx = build_docx(CHART_DIR)
    write_readme()
    print(f"charts: {len(paths)}")
    print(f"html:   {html} ({html.stat().st_size} bytes)")
    print(f"docx:   {docx} ({docx.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
