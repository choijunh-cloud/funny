# 8월 28일 알테오젠 ALT-B4 분석

하나증권 7/14 리포트(「시밀러가 아닌 ALT-B4를 쓴 이유」)를 청구항·라벨·MSD 2Q26 숫자로 검증하고, 8/4 실적과 8/5 $365mn L/O까지 업데이트한 강의용 브리핑.

## 읽는 파일

- **핵심요약 (한 장):** [2026-08-28-alteogen-alt-b4-core.html](2026-08-28-alteogen-alt-b4-core.html) · [../lectures/8월 28일 알테오젠 ALT-B4 분석.md](../lectures/8월%2028일%20알테오젠%20ALT-B4%20분석.md)
- **시각화 본문:** [2026-08-28-alteogen-alt-b4.html](2026-08-28-alteogen-alt-b4.html)
- **PDF가 안 열리면:** [2026-08-28-alteogen-alt-b4-pages.html](2026-08-28-alteogen-alt-b4-pages.html)
- **PDF:** [2026-08-28-alteogen-alt-b4.pdf](2026-08-28-alteogen-alt-b4.pdf) · [../lectures/8월 28일 알테오젠 ALT-B4 분석.pdf](../lectures/8월%2028일%20알테오젠%20ALT-B4%20분석.pdf)
- **차트:** `reports/charts/`

## 재생성

```bash
python3 -m pip install -r requirements.txt
python3 scripts/generate_aug28_alteogen_charts.py
python3 scripts/check_aug28_alteogen_coverage.py
python3 scripts/export_aug28_alteogen_pdf.py
python3 scripts/rasterize_aug28_alteogen_pdf.py
```

로컬에서 HTML을 보려면 `reports/`에서 정적 서버를 띄운다.

```bash
python3 -m http.server 8765 --directory reports
```
