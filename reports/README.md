# 하이브리드 추정 리포트

| 파일 | 용도 |
|---|---|
| `VIEW_THIS_REPORT.md` | GitHub에서 바로 보는 요약 |
| `2026-09-03-hybrid-synthesis.html` | 브라우저용 단독 HTML |
| `2026-09-03-hybrid-synthesis.json` | 원숫자 스냅샷 |
| `2026-09-03-hybrid-portfolio.csv` | 1억 기준 주문용 CSV |

재생성:

```bash
python3 -m hybrid_synthesis --all-scenarios
python3 -m unittest hybrid_synthesis.tests.test_model hybrid_synthesis.tests.test_portfolio
```

투자 참고용 · 투자 권유 아님
