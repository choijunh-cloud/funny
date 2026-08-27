# 8월 26–27일 Quick 코멘트 시각화

01:25–22:32 Quick 코멘트 전체를 주제별로 재배치하고 차트로 읽기 쉽게 만든 브리핑. 엔비디아 FY27 2Q · <strong>공식 IR(보도자료·CFO·IR 덱) 한글 심층</strong> · Kimi K3 · KV 기초 포함.

## 읽는 파일

- **시각화 본문:** [2026-08-26-quick-comment-brief.html](2026-08-26-quick-comment-brief.html)
- **PDF가 안 열리면:** [2026-08-26-quick-comment-brief-pages.html](2026-08-26-quick-comment-brief-pages.html) (27쪽을 이미지로 스크롤)
- **PDF:** [2026-08-26-quick-comment-brief.pdf](2026-08-26-quick-comment-brief.pdf) · [../lectures/8월 26일 Quick 코멘트 시각화.pdf](../lectures/8월%2026일%20Quick%20코멘트%20시각화.pdf) (A4, 원문 부록은 HTML)
- **복사·공유용 문안:** [../lectures/8월 26일 Quick 코멘트 시각화.md](../lectures/8월%2026일%20Quick%20코멘트%20시각화.md)
- **차트:** `reports/charts/`

## 재생성

```bash
python3 -m pip install -r requirements.txt
python3 scripts/generate_aug26_quick_charts.py
python3 scripts/export_aug26_brief_pdf.py
```

로컬에서 HTML을 보려면 `reports/`에서 정적 서버를 띄운다.

```bash
python3 -m http.server 8765 --directory reports
```
