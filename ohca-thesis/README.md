# OHCA 심장효소 논문 학습 노트

최준혁 전공의 논문과 이후 재분석을 한곳에 모아 둔 폴더입니다.

- [ANALYSIS.md](ANALYSIS.md) — 원문·재분석·대시보드를 교차검증한 학습 메모
- [dashboards/OHCA_학습통합브리핑.html](dashboards/OHCA_학습통합브리핑.html) — 한 화면 브리핑
- [dashboards/OHCA_cTnI_감별분석.html](dashboards/OHCA_cTnI_감별분석.html)
- [dashboards/OHCA_NonSTEMI_핵심분석.html](dashboards/OHCA_NonSTEMI_핵심분석.html)
- [dashboards/OHCA_감별지표_종합순위.html](dashboards/OHCA_감별지표_종합순위.html)

핵심만: 초기 1회 효소는 AMI 원인 OHCA를 가르지 못한다. serial CK-MB는 전체에서만 살아나고, Non-STEMI에서는 나이가 유일한 단독 신호다. 논문 본문의 STEMI 95.5%와 이후 분석의 55.2%는 원자료로 다시 세어야 한다.

## 새 논문 초고 (p&lt;0.05 결과로 재구성)

- [paper/새논문_기획과결과.md](paper/새논문_기획과결과.md) — 주제 변경 이유와 유의 결과 목록
- [paper/MANUSCRIPT.md](paper/MANUSCRIPT.md) — 영문 IMRaD 초고
- [dashboards/OHCA_새논문_유의결과.html](dashboards/OHCA_새논문_유의결과.html)
- `paper/figures/` — AUC·OR·CK-MB·나이 컷오프 그림
- 환자 단위 값을 만들어 내지 않음. 기존 코호트의 유의 결과만 사용.

## ACES 점수 (침상용)

Non-STEMI OHCA에서 culprit 가능성을 Age 3 + shockable 2 + 남성 1 + CK-MB Δ 1로 근사한 점수입니다. STEMI는 적용하지 않습니다.

- [score/ACES_SCORE.md](score/ACES_SCORE.md) — 배점 근거
- [dashboards/OHCA_ACES_calculator.html](dashboards/OHCA_ACES_calculator.html) — 계산기
- [score/ACES_pocket_card.png](score/ACES_pocket_card.png)
- `score/aces.py` — 같은 규칙의 함수

정수 점수의 AUC는 아직 환자 단위로 다시 구하지 않았습니다. 외부검증 전입니다.
