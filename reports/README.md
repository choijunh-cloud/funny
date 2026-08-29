# 8월 28일 Quick 코멘트 시각화

8/27 저녁~8/28 오후 Quick 코멘트와 첨부 PDF 5건(엔비디아 2Q, CAPEX 525조, BBU·중국장비·키옥시아, 엔비디아 자신감, 128K KV Cache)을 주제별로 재배치하고 차트로 읽기 쉽게 만든 브리핑. **원문은 부록에 누락 없이** 수록.

## 읽는 파일

- **PDF가 코드처럼 보이면 (이걸 여세요):** [../lectures/8월 28일 Quick 코멘트 시각화.md](../lectures/8월%2028일%20Quick%20코멘트%20시각화.md) · [2026-08-28-quick-comment-brief-pages.html](2026-08-28-quick-comment-brief-pages.html) · [../열어보기.md](../열어보기.md)
- **핵심요약:** [2026-08-28-quick-comment-core.html](2026-08-28-quick-comment-core.html) · [../lectures/8월 28일 Quick 코멘트 핵심요약.md](../lectures/8월%2028일%20Quick%20코멘트%20핵심요약.md)
- **시각화 본문 HTML:** [2026-08-28-quick-comment-brief.html](2026-08-28-quick-comment-brief.html)
- **PDF (미리보기/Acrobat/Chrome용, Cursor에서는 코드처럼 보임):** [2026-08-28-quick-comment-brief.pdf](2026-08-28-quick-comment-brief.pdf)
- **8/28 방송:** [../lectures/8월 28일 방송 코멘트 정리.md](../lectures/8월%2028일%20방송%20코멘트%20정리.md) · [2026-08-28-broadcast-brief-pages.html](2026-08-28-broadcast-brief-pages.html)
- **차트:** `reports/charts/`

## 재생성

```bash
python3 -m pip install -r requirements.txt
python3 scripts/generate_aug28_quick_charts.py
python3 scripts/build_aug28_brief.py
python3 scripts/check_aug28_coverage.py
python3 scripts/export_aug28_brief_pdf.py
python3 scripts/export_aug28_core_pdf.py
python3 scripts/rasterize_aug28_brief_pdf.py
python3 scripts/generate_aug28_broadcast_charts.py
python3 scripts/build_aug28_broadcast_brief.py
python3 scripts/check_aug28_broadcast_coverage.py
python3 scripts/export_aug28_broadcast_pdf.py
python3 scripts/rasterize_aug28_broadcast_pdf.py
python3 scripts/build_openable_viewers.py
```

로컬에서 HTML을 보려면 `reports/`에서 정적 서버를 띄운다.

```bash
python3 -m http.server 8765 --directory reports
```
