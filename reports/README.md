# 8월 25일 Quick 코멘트 시각화

아침 06:24–11:24 Quick 코멘트 전체를 주제별로 재배치하고 차트로 읽기 쉽게 만든 브리핑.

## 읽는 파일

- **시각화 본문:** [2026-08-25-quick-comment-brief.html](2026-08-25-quick-comment-brief.html)
- **복사·공유용 문안:** [../lectures/8월 25일 Quick 코멘트 시각화.md](../lectures/8월%2025일%20Quick%20코멘트%20시각화.md)
- **차트:** `reports/charts/`

## 재생성

```bash
python3 -m pip install -r requirements.txt
python3 scripts/generate_aug25_quick_charts.py
```

로컬에서 HTML을 보려면 `reports/`에서 정적 서버를 띄운다.

```bash
python3 -m http.server 8765 --directory reports
```
