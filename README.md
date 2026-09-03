# 통합 하이브리드 추정 모형 (KOSPI)

다섯 편 심층 영상의 미시 데이터(CXMT, 빅테크 FCF, 회사채 수급)와 거시 논리(금리 역전, 조본잉)를 하나의 식으로 묶는다.

```
M = R × A + D
```

- `R` 매크로 압박 해소율 (실질정책 vs 실질중립, 10년물 공급, 유가, 환율 왜곡)
- `A` AI 이익 팽창 계수 (엔비디아 기타수요, NVL72 랙, FCF 전환, CXMT/YMTC)
- `D` 국내 수급 방어력 (생산적 금융 ISA, 삼성 특별배당, 한전 선납)

포트폴리오는 **코스피만** 담는다. 심텍·티엘비·디아이·엘앤에프는 코스닥이므로 제외하고 코스피 대체 종목으로 치환한다.

## 실행

```bash
python3 -m hybrid_synthesis --all-scenarios
python3 -m hybrid_synthesis --doc4
python3 -m unittest hybrid_synthesis.tests.test_model hybrid_synthesis.tests.test_portfolio hybrid_synthesis.tests.test_ranking hybrid_synthesis.tests.test_v2
```

입력값을 바꿔 재추정:

```bash
python3 -m hybrid_synthesis --ust10 5.05 --oil 96
python3 -m hybrid_synthesis --pce 3.45 --oil 81 --as-of 2026-11-20 --isa 18
python3 -m hybrid_synthesis --fcf-positive --as-of 2027-07-15
```

결과 파일은 `reports/` 에 모인다. 문서4 「절단된 사슬」은 `--doc4` 로 뽑는다. 유가→PCE→연준 경로가 정책단에서 끊긴 뒤의 재가중이다.

## 기본 배분 (Phase 1)

- 주식 60% / 채권·현금 40%
- 주식 내부: 삼성전자·SK하이닉스 50%, AI 소부장 25%, 은행·인프라 15%, 화장품 스윙 10%

투자 권유가 아니다. 연구용 추정 모형이다.
