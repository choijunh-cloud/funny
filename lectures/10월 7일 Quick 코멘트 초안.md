# 10월 7일 Quick 코멘트 초안 (게시용)

paste에 없거나 짧게만 있던 주제 중심. 톤은 기존 Quick 코멘트와 맞춤.

---

## Quick 코멘트 — MUSE에서 메모리는

Muse의 VM은 새 기술이 아닙니다. 기존 VM을 ‘개인 AI마다 상시 존재하는 컴퓨터’로 쓰는 변화입니다.

수혜 순서: 1차 서버 DRAM → 2차 CXL / SSD·NAND.

구조는 단순합니다.

- Muse Spark(LLM) = 두뇌
- Muse Secure VM = 그 두뇌가 일할 개인 컴퓨터 (CPU + memory + storage + browser)

관측상 VM은 약 8GB가 보이지만, 실제 사용은 약 3GB입니다.
따라서 지금은 “8GB × Agent 수”가 아니라 “실제 평균 3GB × 동시 활성 Agent 수”로 봐야 합니다.

진짜 옵션은 앞으로입니다.

현재 8GB 할당 / ~3GB 사용  
→ 고도화 16GB / 6~10GB  
→ 복잡 Agent 32GB+ / 10~20GB+

CPU는 idle이면 거의 0이라 oversubscribe가 쉽지만, DRAM은 working state를 남겨야 해서 공유가 어렵습니다. Agent가 고도화될수록 DRAM 밀도가 올라가는 이유입니다.

---

## Quick 코멘트 — AMD·씨티·미즈호, CPU 시장 상향

씨티는 Agentic AI를 반영해 서버 CPU TAM을 2025년 $29B → 2030년 $300B로 올렸습니다. 5월 전망($131.5B) 대비 한 단계 점프입니다.

미즈호는 2030년 약 $209B, Agentic CPU 비중 4%→30%, DRAM·NAND 출하 비트의 22~30%까지 Agent가 가져갈 수 있다고 봅니다.

$300B는 공격적입니다. 다만 방향성은 분명합니다.

Chatbot: 질문 → 답변 → 대기  
Agent: 목표 → 검색/판단 → 실행 → 재실행 (수시간~24시간)

그래서 CPU:GPU가 1:4~8에서 1:1 쪽으로 이동할 수 있고, 특정 workload에선 CPU tool processing이 latency의 대부분을 차지할 수 있습니다.

투자 연결고리: Agentic AI → Inference 폭증 → GPU+CPU+Memory+Networking → 데이터센터 CAPEX 장기화.

---

## Quick 코멘트 — 피에스케이홀딩스, AI가 커질수록 CoWoS·EMIB

한화 리포트 TP 27만원. 이전 타사보다 한 단계 높고, 중요한 것은 이익전망이 더 높다는 점입니다. 수치가 뒷받침되면 최근 상승에도 차익실현을 서두를 필요는 낮아 보입니다. 신규는 눌림목 분할, 안전마진 30% 근처면 더 긍정적. 손절은 칼같이.

핵심 한 줄: AI 반도체가 커질수록 CoWoS·HBM·OSAT·EMIB 후공정 CAPEX가 같이 늘고, 피에스케이홀딩스는 그 교집합에 있습니다.

- CoWoS/HBM: Reflow
- OSAT: Descum
- Intel EMIB: Reflow + Descum 모두 공급 가능 → 추가 레벨업 옵션

EMIB는 CoWoS의 의미 있는 대안으로 부상 중이고, Intel도 New Mexico·Penang 중심으로 Advanced Packaging CAPA를 키웁니다.

---

## Quick 코멘트 — 중간선거, 본질은 전력 수급과 비용

미 중간선거의 에너지 쟁점은 ‘친환경 vs 화석연료’ 프레임보다 전력 수급 안정과 affordability입니다.

AI 데이터센터 전력수요가 반(反)데이터센터 논쟁을 키우지만, 정치권의 해법은 DC 억제가 아니라 공급 확대와 가격 안정입니다.

공화당: 원전·가스터빈·ESS·가스망  
민주당: 신재생·원전 + 비용 부담 완화  
→ 접점이 넓어지고 있습니다.

민주당이 최소 하원을 확보하면 IRA 전면 복원보다는 신재생 보조금·세액공제 일부 연장/수정 가능성이 더 현실적입니다. 선거 이후에도 원전·가스·ESS·신재생 다변화 투자는 이어질 가능성이 큽니다.

---

## Quick 코멘트 — 중국 AI 저가 논쟁 (재확인)

경제성은 토큰당 가격이 아니라 작업 완료 총비용(TCO)입니다.

판정:
- 중국 AI가 가격만큼 싸지는 않다 → 타당
- 미국 AI가 전반적으로 더 싸다 → 부분타당
- 기업 AI 지출이 폭증하지 않는다 → 부분타당
- 그러므로 AI CapEx가 과도하다 → 비약

단위비용 하락을 인프라 수요 둔화로 연결하면 안 됩니다. Agentic AI 사용량 폭증이 이를 상쇄할 수 있습니다.
