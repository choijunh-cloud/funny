# 패널 합성 국면 모델 — 결과 보기

| 파일 | 여는 방법 |
|---|---|
| `VIEW_THIS_REPORT.md` | Cursor·GitHub에서 바로 보임 |
| `2026-08-21-regime-standalone.html` | 다운로드 후 브라우저. 인터넷 불필요 |
| `2026-08-21-regime-dashboard.html` | 브라우저. Chart.js 차트 |
| `2026-08-21-regime-baseline.pdf` | 차트 7쪽 PDF |
| `charts_regime/*.png` | 정적 차트 |
| `2026-08-21-regime-baseline.json` | 원숫자 스냅샷 |

재생성:

```bash
python3 -m pip install -r requirements.txt
python3 scripts/generate_regime_report.py
python3 scripts/test_regime_baseline.py
```

투자 참고용 · 투자 권유 아님
