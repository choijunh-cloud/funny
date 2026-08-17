# 응급의학과 봉직 통합 모델 v3

여수 단독 분석부터 12·24·42·52·59·60·61곳, v4.8 포터블, v5.1 축,
v1.2 코드, 2026-06/07 백업, 최종 마스터(72프로필), 8월 홀드아웃까지를
**하나의 파이프라인**으로 묶습니다.

공고가 뜨면 점수 랭킹보다 **게이트 → 시장가 잔차 → 프로파일 목표구간 → 검증 카드** 순으로 읽습니다.

시장 점수(통근 없음, 프레임 A/B)와 개인 점수(옥수동 기본)는 분리합니다.

## 실행

```bash
pip install -r bongjik/requirements.txt
python3 -m bongjik --report
python3 -m bongjik --targets
python3 -m bongjik --posting --holdout
python3 -m bongjik --stats
python3 -m bongjik --lineage
python3 -m bongjik --estimate --zone 서울 --backup 강 --pp 2000 --hours 120
python3 -m unittest bongjik.tests.test_model -v
```

마스터 엑셀이 없어도 `bongjik/data/master_pool.json` 스냅샷으로 돌아갑니다.
엑셀을 갱신하면 `python3 -m bongjik.extract` 로 JSON을 다시 뽑습니다.

## 판정

| 라벨 | 의미 |
|---|---|
| `AVOID` | 법적 D · 월 168h+ · 안전 < 4.0 · 한산+약백업 · 회피 리스트 |
| `PASS_CONFIRM` | 안전≥5.5 AND 단가≥13.1 AND 연환자 통과/구제 |
| `PASS_SCREEN` | 안전≥6.3 AND 단가≥11.1 |
| `HOLD` | 숫자 일부만 좋음. 프로파일이 맞을 때만 보관 |

단가 13.3은 **설명적 컷**입니다. 예측 임계값으로 부르지 않습니다.

## 문서

- [DESIGN.md](DESIGN.md) — 학습 요약, 기존 모델 한계, v3 구조
- `archive/bongjik_model_v12.py` — 2026-07-10 통합 모델 v1.2 원본
- `data/lineage.json` — 12곳→8월 홀드아웃 계보
- `data/overlays.json` — 정성/위생/통근 (점수 축과 분리)
- `data/postings.json` — 평가 카드 + 8월 시트 판정
