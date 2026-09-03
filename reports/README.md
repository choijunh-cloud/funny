# 하이브리드 추정 리포트

| 파일 | 용도 |
|---|---|
| `VIEW_THIS_REPORT.md` | GitHub에서 바로 보는 요약 |
| `2026-09-03-hybrid-synthesis.html` | 브라우저용 단독 HTML |
| `2026-09-03-hybrid-synthesis.json` | 원숫자 스냅샷 |
| `2026-09-03-hybrid-portfolio.csv` | 1억 기준 주문용 CSV |
| `2026-09-05-severed-chain.html` | 문서4 「절단된 사슬」 (v2) |
| `2026-09-05-severed-chain.json` | v2 원숫자 |
| `SEVERED_CHAIN.md` | 문서4 요약 |

재생성:

```bash
python3 -m hybrid_synthesis --all-scenarios
python3 -m hybrid_synthesis --doc4
python3 -m unittest hybrid_synthesis.tests.test_model hybrid_synthesis.tests.test_portfolio hybrid_synthesis.tests.test_ranking hybrid_synthesis.tests.test_v2
```

투자 참고용 · 투자 권유 아님
