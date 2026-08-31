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

## 정수 초안 (임상 점수 아님)

이전 ACES(포켓 카드, Low/High, CK-MB 1점)는 폐기했습니다. 이름은 CODE ACES 2·캐나다 ACES와 겹치고, 정수 성능·층 우도비가 없으며 CK-MB 1점은 Non-STEMI에서 근거가 없습니다.

남은 것은 **OHCA-ARS** Door 0–6 (나이 3, shockable 2, 남성 1)입니다. 탐색적 산술입니다. 층을 붙이지 않습니다.

- [score/OHCA_ARS.md](score/OHCA_ARS.md)
- [dashboards/OHCA_ARS_draft.html](dashboards/OHCA_ARS_draft.html) — 연구용, 임상 사용 금지
- `score/ars.py`

다음 작업은 Non-STEMI 63명을 이 0–6으로 다시 채점하는 것입니다. 원자료가 필요합니다.
