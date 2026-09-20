# 8월–9월 투자 스터디 인사이트

funny 저장소에 쌓인 투자 스터디(8/18–9/20)를 읽어 테제·숫자·확인 캘린더로 재구성한 시각화 보고서.

## 산출물

- `lectures/8월-9월 투자 스터디 인사이트 한장.html` — 차트 26장 한 장 보드 (이 파일을 연다)
- `lectures/8월-9월 투자 스터디 인사이트.html` — 같은 차트 + 장문
- `reports/VIEW_THIS_REPORT.html` — 한 장 보드 별칭
- `reports/2026-09-20-study-insights.md` — 텍스트 정리
- `lectures/assets/insights/*.png` — 차트 26장

## 다시 만들기

```bash
python3 scripts/generate_insights_all.py
python3 scripts/test_insights_numbers.py
```

## 규칙

- 준혁 프레임(10Y 5% · 30Y 6% · TIPS 3.0 · 닉스 자사주 vs 삼성 배당/1월)은 덮어쓰지 않는다
- 사이렌(10Y 5% 안착 · oil 120)은 미발화
- IB 목표가·게스트 가격·UBS 경로·Ohio 계약·GDP 25%는 잠금 금지
- 숫자는 스터디 스냅샷이며 실시간 시세가 아니다
- 커넥톰·봉직·클리닉·톤즈는 이 보고서에 넣지 않는다
