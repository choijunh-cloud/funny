# 8월 27일 Quick 코멘트 시각화

01:25–09:48 Quick 코멘트 전체를 주제별로 재배치하고 차트로 읽기 쉽게 만든 브리핑. 엔비디아 FY27 2Q 실적·현금흐름, 한미약품 HM17321 L/O, 美 ESS 4배·K배터리 EV 라인 전환, 8/26 장 마감·장전 코멘트를 **누락 없이** 수록.

## 읽는 파일

- **핵심요약 (한 장):** [2026-08-27-quick-comment-core.html](2026-08-27-quick-comment-core.html) · [../lectures/8월 27일 Quick 코멘트 핵심요약.md](../lectures/8월%2027일%20Quick%20코멘트%20핵심요약.md)
- **시각화 본문:** [2026-08-27-quick-comment-brief.html](2026-08-27-quick-comment-brief.html)
- **PDF가 안 열리면:** [2026-08-27-quick-comment-brief-pages.html](2026-08-27-quick-comment-brief-pages.html)
- **PDF:** [2026-08-27-quick-comment-brief.pdf](2026-08-27-quick-comment-brief.pdf) · [../lectures/8월 27일 Quick 코멘트 시각화.pdf](../lectures/8월%2027일%20Quick%20코멘트%20시각화.pdf)
- **복사·공유용 문안:** [../lectures/8월 27일 Quick 코멘트 시각화.md](../lectures/8월%2027일%20Quick%20코멘트%20시각화.md)
- **차트:** `reports/charts/`

## 재생성

```bash
python3 -m pip install -r requirements.txt
python3 scripts/generate_aug27_quick_charts.py
python3 scripts/export_aug27_brief_pdf.py
python3 scripts/rasterize_aug27_brief_pdf.py
python3 scripts/export_aug27_core_pdf.py
```

로컬에서 HTML을 보려면 `reports/`에서 정적 서버를 띄운다.

```bash
python3 -m http.server 8765 --directory reports
```
