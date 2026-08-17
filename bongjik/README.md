# 응급의학과 봉직 JobFit v2

12개→70개 공고 마스터와 v4.8·v5.1·v1.2 파이프라인을 학습한 뒤,
**「좋은 병원」과 「나에게 좋은 조건」을 분리**해 추정하는 모델입니다.

## 한 줄 요약

공고가 뜨면 점수 랭킹보다 **게이트 → 시장가 잔차 → 프로파일 목표구간 → 검증 카드** 순으로 읽습니다.

## 실행

```bash
pip install -r bongjik/requirements.txt
python3 bongjik/jobfit_v2.py --report
python3 bongjik/jobfit_v2.py --targets
python3 bongjik/jobfit_v2.py --posting
python3 bongjik/jobfit_v2.py --estimate --zone 서울 --backup 강 --pp 2000 --hours 120
python3 -m unittest bongjik.tests.test_jobfit -v
```

마스터 엑셀이 없어도 `bongjik/data/master_pool.json` 스냅샷으로 돌아갑니다.

## 문서

- [DESIGN.md](DESIGN.md) — 학습 요약, 기존 모델 한계, v2 구조, 목표 조건 구간
- `bongjik_model_v12.py` — 2026-07-10 통합 모델 v1.2 원본 (참조용)
