# 10/7 투자 인사이트 — 정밀 모델 증류

매수·매도 권유 아님. 원문 PDF 6 + paste 숫자만으로 닫힌 식.

## 0. 한 줄

프레임: TCO·Agent 확산. CPU 2030은 $131.5B→$209.0B~$300.0B 밴드. Muse 1억 DAU·활성15%에서 8GB×N은 물리 DRAM을 약 2.9배 과대. 삼전닉스 27Y PER 4.0x; MU 패리티(5.8x) 시 하이닉스≈258만 (현재 대비 44%). 기업 AI $지출 정체≠인프라 피크.

## 1. CapEx 역설 (Spend ≠ Infra)

- 항등식: `Spend ∝ tasks × cost_per_task; Infra ∝ tasks × compute_per_task`
- 판정: CapEx 과도 = **비약**

| 시나리오 | 비용/task | task 배수 | 기업$지출 | 인프라compute | 괴리(infra/spend) |
|---|---:|---:|---:|---:|---:|
| Bear_efficiency | -50% | 1.5x | 0.75x | 1.5x | 2.00x |
| Base | -40% | 3.0x | 1.80x | 3.0x | 1.67x |
| Bull_agentic | -50% | 8.0x | 4.00x | 8.0x | 2.00x |
| Super_agent | -60% | 20.0x | 8.00x | 20.0x | 2.50x |

→ 기업 $지출이 플랫/감소해도 infra compute는 tasks와 함께 증가 가능. ‘지출 안 늘어남’을 CapEx 피크로 번역하는 것이 비약인 이유.

## 2. Muse DRAM 수요 모델

- 식: `Physical DRAM ≈ DAU × active_ratio × used_GB / sharing`
- 금지: `≠ DAU × 8GB (논리적 할당 과대)`

| 시나리오 (DAU 1억) | 활성 | used GB | Physical PB | 8GB×N 과대배수 |
|---|---:|---:|---:|---:|
| Bear·현재실측 | 5% | 3 | 13.6 | 2.93x |
| Base·현재실측 | 15% | 3 | 40.9 | 2.93x |
| Upgrade·고도화 | 15% | 8 | 114.3 | 1.05x |
| Bull·복잡Agent | 30% | 15 | 450.0 | 0.53x |

→ 현재는 used≈3GB·sharing>1로 물리 수요가 작아 보일 수 있으나, 활성률↑와 used_GB↑가 동시에 오면 비선형으로 커진다. CPU oversubscribe와 달리 DRAM sharing≈1에 수렴하는 것이 비대칭 포인트.

## 3. 서버 CPU TAM 경로

| 하우스 | 2025 | 2026E* | 2028E* | 2030 | CAGR | 5년배수 | Agentic |
|---|---:|---:|---:|---:|---:|---:|---|
| Citi May | 29.3 | 39.6 | 72.1 | 132 | 35.0% | 4.5x | $59B (45%) |
| Citi Oct | 29.0 | 46.3 | 117.8 | 300 | 59.6% | 10.3x | 미제시 |
| Mizuho | 25.9 | 39.3 | 90.7 | 209 | 51.8% | 8.1x | $80B (30%) |

- \*2026/28은 각 경로 CAGR 기계 역산 (Citi가 2026을 직접 준 것 아님).
- Oct vs May Δ2030 = **$168.5B**. May non-agentic≈$72.1B 고정 가정 시 Oct $300B를 맞추려면 Agentic≈$228B(약 76%) 필요 — 매우 공격적
- CPU:GPU 1:6 → 1:1 이면 동일 GPU 대비 CPU 소켓 최대 **6x**.
- Muse→NV 브리지: 1억 DAU → GPU 200,000~390,000 · NV 일회성 $7~19B (CPU 매출 직접치 아님).

→ 세 경로는 모두 2025~$26–29B에서 출발해 2030년 4.5~10배. 투자 결정은 ‘$300B 여부’가 아니라 (1) CPU intensity uplift가 지속되는지 (2) Agentic이 DRAM/NAND 비트 20%+를 가져가는지 (미즈호)다.

## 4. 메모리 밸류 · 재평가 맵

기준: 2026-10-06 close, FX 1340원.

| 종목 | 가격 | 27Y PER | vs MU CY27 |
|---|---:|---:|---:|
| Sandisk | 1660.46 USD | 7.2 | — |
| Micron FY27 | 1045.56 USD | 6.3 | — |
| Micron CY27 | 1045.56 USD | 5.8 | — |
| SKH ADR | 182.56 USD | 5.5 | -5% |
| SKH 본주 | 178.4 KRW만 | 4.0 | -31% |
| 삼성전자 | 27.3 KRW만 | 4.0 | -31% |

- ADR 프리미엄 **37%** (ADR 244.6만 / 본주 178.4만).
  프리미엄 축소 시 본주 함의: 30%→188.2만, 20%→203.8만, 10%→222.4만, 0%→244.6만
- FX: 1480→1370 ≈ -7.4% EPS 압력; 원화+5~10% → 주식 -6%~-12%.

### 26Y 이익 동결 + PER 4~8x (보수 천장)

- SKH: 4x→139.6만, 5x→174.5만, 6x→209.4만, 7x→244.3만, 8x→279.2만
- 삼성: 4x→19.2만, 5x→23.9만, 6x→28.7만, 7x→33.5만, 8x→38.3만
- 원문 밴드: {'skh': '209~244만@6~7x', 'sec': '28.7~33.5만@6~7x'}

### 27Y 재평가 (EPS 성장 인정 시)

- SKH 현재 178.4만 → MU패리티 257.5만 (+44%), 15%할인 218.9만 (+23%), 현 할인31% 유지 177.7만 (-0%).
- 삼성 현재 27.3만 → 패리티 39.4만 (+44%) / 15%할인 33.5만 / 31%할인 27.2만.
- 27Y OP/EPS: SKH OP +48%, EPS +27%; 삼성 OP +43%, EPS +42%.

### MU TP 논쟁

- Spot $1046 / Davidson $3000 (+187%, FY27 EPS165 기준 **18.2x**, CY27 EPS180 기준 16.7x).
- 컨센 평균 $1572 (3000 포함 시 $1714).
- Approach(−20~30%): $1100~1258 또는 $1200~1371.
- Davidson 18.2x(FY27 EPS165)≈원문~19x. 컨센 TP $1572는 CY27 EPS180 기준 ~8.7x. 이익보다 배수가 싸움. Approach 앵커는 1200~1371.

## 5. PSK · 중간선거 (옵션/프레임)

- PSK: 한화 TP 27만. 정량 EPS/매출 컨센이 PDF에 없어 배수 모델 불가. 질적 옵션 가치 = P(EMIB양산)×(Reflow+Descum 동시 침투). 확인 지표: Intel EMIB CAPA 가이던스, PSK EMIB 매출 믹스 공시.
- 중간선거: 거짓 프레임 `친환경 vs 화석연료 / 반-데이터센터` → 참 프레임 `전력 수급 안정 + affordability`.
- 원전·가스터빈·ESS·신재생·송배전 — 선거 결과와 무관하게 AI 전력수요 대응 투자는 지속 가능성 높음

## 6. 스코어보드

| 테제 | 강도 | 시그널 |
|---|---|---|
| memory_cheap_vs_history | high | 본주 27Y PER 4.0x vs 과거 사이클 4~8x 하단 |
| agentic_diffusion | high | CPU TAM 상향 + Muse DRAM 비대칭 + Mizuho bit share 22~30% |
| capex_not_peaking_from_token_price | high | Spend/Infra divergence in agentic scenarios |
| cpu_300b_as_point_estimate | low_as_number_high_as_direction | Oct vs May bridge implies ~76% agentic share if non-agentic fixed — fragile |
| psk_emib | medium | Qualitative call option; needs CAPA/mix confirmation |
| midterm_anti_dc | high_as_frame | Falsified frame in source; power supply is the constant |

## 7. 의사결정 규칙

1. CapEx 논쟁은 **task×cost**와 **task×compute**를 분리해서 말할 것.
2. Muse/Agent DRAM은 **활성률·used_GB·sharing** 세 레버 민감도로 말할 것.
3. CPU는 **$300B 점추정 금지**, $131~300B 밴드 + CPU intensity uplift로 말할 것.
4. 삼전닉스는 **4.0x 현 배수 vs 할인율 축소 시나리오**로 업사이드 구간을 말할 것.
5. MU는 **19x 금지**, Approach 1200~1371을 상단 토론 앵커로.
6. PSK는 EMIB 매출 믹스 확인 전 **질적 옵션**으로만.
