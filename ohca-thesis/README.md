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

## 탐색적 세 변수 가설 (점수 아님)

ACES·포켓 카드·층·CK-MB 1점은 폐기했습니다. 3–2–1은 4변수 β의 잔여이며 **최종 배점이 아닙니다.** 0.808은 CK-MB가 들어 있는 중첩 AUC이지 Door 성능이 아닙니다.

원자료가 오면 Age(연속)+shockable+sex를 다시 적합합니다. 보정 AUC가 0.70을 넘을 때만 점수를 남깁니다.

- [score/OHCA_ARS.md](score/OHCA_ARS.md)
- [dashboards/OHCA_ARS_draft.html](dashboards/OHCA_ARS_draft.html) — 연구용 산술, 임상 사용 금지, 층 없음
