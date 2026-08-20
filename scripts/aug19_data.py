"""8/19 공개 퀵코멘트 기준 숫자. 시세·추정은 코멘트 원문이며 실시간 시세가 아님."""

from __future__ import annotations

# ── FX ────────────────────────────────────────────────────
USD_KRW_FROM = 1520
USD_KRW_TO = 1420
USD_KRW_MOVE_PCT = (USD_KRW_TO / USD_KRW_FROM - 1) * 100  # ≈ -6.58
SKH_FX_BETA = 0.9  # 원/달러 +1% → SK하이닉스 EPS +0.9%
SEC_FX_BETA = 0.4  # 원/달러 +1% → 삼성전자 EPS +0.4% (원문 표기 오타 교정)
SKH_EPS_FX_HIT = abs(USD_KRW_MOVE_PCT) * SKH_FX_BETA  # ≈ 5.92
SKH_NI_2027_LOW, SKH_NI_2027_HIGH = 300, 400  # 조원
SKH_NI_ADJ_LOW = SKH_NI_2027_LOW * SKH_EPS_FX_HIT / 100  # ≈ 17.8
SKH_NI_ADJ_HIGH = SKH_NI_2027_HIGH * SKH_EPS_FX_HIT / 100  # ≈ 23.7
SKH_2H26_FX_ADJ = 16.3  # 조원, 26년 하반기 환율 조정 가능성
KRW_FLOOR_DXY = 1360  # 달러인덱스 3~4% 하락 시
KRW_FLOOR_SUPPLY = 1340  # + 한국 달러 공급
DXY_NOW, DXY_DOWNSIDE = 99, (96, 97)
USD_KRW_MORNING = 1412

# ── 주주환원 ──────────────────────────────────────────────
SKH_BUYBACK_KRW_T = 40
SKH_SHARES_M = 730.49
SKH_BUYBACK_PX = 1_662_000
SKH_BUYBACK_SHARES_M = SKH_BUYBACK_KRW_T * 1e12 / SKH_BUYBACK_PX / 1e6  # ≈ 24.07
SKH_BUYBACK_PCT = SKH_BUYBACK_SHARES_M / SKH_SHARES_M * 100  # ≈ 3.29
SKH_EPS_UPLIFT = (1 / (1 - SKH_BUYBACK_PCT / 100) - 1) * 100  # ≈ 3.41
SKH_DAYS = 62
SKH_DAILY_KRW_100M = SKH_BUYBACK_KRW_T * 10000 / SKH_DAYS  # 6,452억
SKH_FCF_2527 = 385
SKH_PAYOUT_MIN = 0.50
SKH_RETURN_MIN = SKH_FCF_2527 * SKH_PAYOUT_MIN  # 192.5
SKH_RETURN_ADD = SKH_RETURN_MIN - SKH_BUYBACK_KRW_T  # 152.5
SKH_FCF_LADDER = (179, 242, 237)
SKH_FCF_CONSERVATIVE = (150, 210, 205)
SKH_FCF_CONSERVATIVE_SUM = sum(SKH_FCF_CONSERVATIVE)  # 565
SKH_NET_CASH_2Q = 69
SKH_LOCAL_PX = 1_500_000
SKH_ADR_HIGH = 163.8
SKH_ADR_CLOSE = 156.16
SKH_ADR_PREMIUM = 0.52
SKH_ADR_NORMAL = 0.20
SKH_ADR_RECENT = (0.30, 0.35)

# PER / 이익 (컨센, 원)
SKH_PER_26, SKH_PER_27, SKH_PER_27_BEAR = 4.3, 3.4, 5.1
SKH_OP_26, SKH_EPS_26 = 266, 346_000
SKH_OP_27, SKH_EPS_27 = 392, 437_000
SKH_OP_26_BEAR = (250, 260)
SKH_EPS_26_BEAR = (290_000, 300_000)

SEC_PX = 247_500
SEC_PER_26, SEC_PER_27, SEC_PER_27_BEAR = 5.2, 3.7, 5.6
SEC_OP_26, SEC_EPS_26 = 391, 47_900
SEC_OP_27, SEC_EPS_27 = 549, 67_200
SEC_OP_26_BEAR = (355, 370)
SEC_EPS_26_BEAR = (43_000, 45_000)

SKH_PER6 = SKH_EPS_26 * 6  # 2,076,000
SKH_PER7 = SKH_EPS_26 * 7  # 2,422,000
SEC_PER6 = SEC_EPS_26 * 6  # 287,400
SEC_PER7 = SEC_EPS_26 * 7  # 335,300

# ADR implied local
SKH_ADR_FX_REF = 1390
SKH_ADR_IMPLIED_LOCAL = int(SKH_ADR_HIGH * SKH_ADR_FX_REF * 10)  # 2,276,820 ≈ 228만
SKH_LOCAL_IF_PREM20 = int(SKH_ADR_IMPLIED_LOCAL / 1.20)  # ≈ 190만
SKH_LOCAL_IF_PREM30 = int(SKH_ADR_IMPLIED_LOCAL / 1.30)
SKH_LOCAL_IF_PREM35 = int(SKH_ADR_IMPLIED_LOCAL / 1.35)

# 피어
MU_PX, MU_F12_PER, MU_CY27_EPS, MU_CY27_PER = 937.11, 7.5, 150, 6.25
SNDK_PX, SNDK_FY27_EPS, SNDK_FY27_PER = 1568.37, 201, 7.8
SKH_ADR_PER26, SKH_ADR_PER27 = 6.6, 5.2
SKH_VS_MU = -0.17  # 마이크론 대비 -17% (과거 -20~-50%)

# ── 매크로 레벨 ───────────────────────────────────────────
US10Y_SOFT, US10Y_HARD = 4.70, 5.00
US10Y_PRINTS = {"장중 부담": 4.75, "장 마감 진정": 4.708, "바이백 후": 4.64}
US30Y_PRINTS = {"고점": 5.34, "장 마감": 5.285, "바이백 후": 5.19}
WTI = 84
BRENT_SOFT, BRENT_HARD = 90, 100
USDJPY_NOW = (157, 159)
USDJPY_2024_FROM, USDJPY_2024_TO = 152.5, 143.5
NIKKEI_2024 = (39102, 31458)  # -19.5%
KOSPI_2024 = (2771, 2442)  # -11.9%
TREASURY_BUYBACK = (20, 40)  # 억 달러

# ── HBM 시나리오 ──────────────────────────────────────────
HBM_SCENARIOS = [
    {"name": "수요 지속", "ai": 50, "eff": 20, "net": 30},
    {"name": "둔화 전환", "ai": 20, "eff": 30, "net": -10},
]

# ── 이수페타시스 ──────────────────────────────────────────
ISU_REV, ISU_REV_BEAT = 3799, 4.9
ISU_OP, ISU_OP_BEAT, ISU_OPM = 771, 2.7, 20.3
ISU_ML = {"1Q": 7, "2Q": 11, "수주잔고": 20}
ISU_CAPA = {"현재": 1200, "27년 2Q": 1500, "28년 하반기": 1800}
ISU_ASP = 15
ISU_MULT = (30.9, 26.0)

# ── 기가비스 ──────────────────────────────────────────────
GIGA_CONTRACT, GIGA_SALES_PCT = 89.5, 17.1
GIGA_25 = {"rev": 847, "op": 121}
GIGA_26E = {"rev": 1785, "op": 721}
GIGA_TP = 190_000

# ── 마벨 워런트 ───────────────────────────────────────────
MRVL_WARRANT_M = 58.97
MRVL_STRIKE = 206.58
MRVL_TRANCHE_USD_M = 500
MRVL_WINDOW = "FY2027 Q3 ~ FY2033"
MRVL_CHG, AVGO_CHG = 9.9, -4.6

# ── 삼성 파운드리 인상 ────────────────────────────────────
FOUNDRY_HIKES = [
    ("4nm SF4 중·미", "10~15%"),
    ("4nm SF4 대만", "5~10%"),
    ("5nm SF5", "10~15%"),
    ("8nm 레거시", "약 10%"),
]

# ── NVIDIA / OpenAI ───────────────────────────────────────
NVDA_Q3 = {"yoy": 90, "rev": 108}
NVDA_Q4 = {"yoy": 77, "rev": 120}
OPENAI_Q2_REV, OPENAI_Q2_QOQ = 6.7, 18
OPENAI_LOSS = (9.3, 12.3)
HS_CAPEX_27, HS_CAPEX_GROWTH = 1000, 33  # $B, %
RUBIN_RACK = (7.0, 8.5)  # $M
RUBIN_INFER_X, RUBIN_FACTORY_X = 35, 10

# ── 유니트리 ──────────────────────────────────────────────
UNITREE_PSR = 155
UNITREE_PSR_FAIR_FRAME = 60
UNITREE_MCAP_CNY = 3418  # 억 위안 종가
UNITREE_SALES_26 = 22  # 억 위안
UNITREE_CAGR = 31
UNITREE_BOM = {"CN": 4.6, "US": 13.1}  # 만 달러
