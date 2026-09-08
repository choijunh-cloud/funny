"""9월 8일 Quick 코멘트 + 첨부 PDF 핵심 숫자.

출처를 구분해 둔다.
- CONFIRMED: 원문 보도/공식 자료에서 교차확인
- ESTIMATE: 리서치·업계 추정, 공식 확인 전
- COMMENT: 당일 Quick 코멘트 수치 (원문 기준)
"""

from __future__ import annotations

# --- DRAM 2Q26 (TrendForce, 2026-09-07) ---
DRAM_2Q26_REVENUE_B = 154.73
DRAM_2Q26_QOQ_PCT = 59.5
DRAM_3Q26_CONTRACT_QOQ = (13, 18)  # conventional DRAM, %
DRAM_VENDORS_2Q26 = [
    # name, revenue $B, share %, qoq %
    ("삼성전자", 60.981, 39.4, 63.4),
    ("SK하이닉스", 38.590, 24.9, 37.9),
    ("Micron", 36.000, 23.3, 65.5),
    ("CXMT", 14.624, 9.5, 99.3),
    ("Nanya", 2.612, 1.7, 68.3),
    ("Winbond", 0.998, 0.6, 75.8),
]

# --- Apple NAND (업계 보도, 미공식) ---
APPLE_NAND_YEARS = (3, 5)
IPHONE18_MEM_BOM_PCT = 34  # TrendForce / 업계, 256GB Pro
IPHONE18_MEM_BOM_START_PCT = 10
IPHONE18_MEM_BOM_1H27_PCT = 40
IPHONE18_MEM_COST_MULTIPLE = 4
FOLDABLE_ASP_USD = (2099, 2299)
FOLDABLE_HIGH_USD = 3000
SAMSUNG_LTA_CAPA_PCT = (60, 70)
FOLDABLE_NAND_HYNIX_PCT = 30
FOLDABLE_NAND_SAMSUNG_PCT = 15

# --- 자사주 (Quick 코멘트, 9/8) ---
HYNIX_BUYBACK_TOTAL_M = 24.07
HYNIX_BUYBACK_DAILY_NOW_M = 0.65
HYNIX_BUYBACK_DAILY_MAX_M = 2.407
SAMSUNG_BUYBACK_TOTAL_M = 53.286
SAMSUNG_BUYBACK_DAILY_NOW_M = 2.00
SAMSUNG_BUYBACK_DAILY_MAX_M = 7.321653
HYNIX_BUYBACK_YDAY_T = 1.1  # 조원, 9/7
SAMSUNG_BUYBACK_YDAY_T = 0.5
HYNIX_TURNOVER_9_7_T = 10.4
SAMSUNG_TURNOVER_9_7_T = 7.9

# --- ETF 리밸런싱 9/10 (증권사 추정 밴드) ---
KRX_SEMI_ETF_AUM_T = 7.6  # ~7.6~7.7조
HYNIX_WEIGHT_PCT = 36.8
SAMSUNG_WEIGHT_PCT = 23.0
WEIGHT_CAP_PCT = 20
HYNIX_ETF_SELL_T = (1.24, 1.45)  # 미래에셋 약 1.2조 등 밴드
SAMSUNG_ETF_SELL_T = (0.20, 0.24)
HANMI_INFLOW_T = 0.30
JUSUNG_INFLOW_T = 0.18
TES_INFLOW_T = 0.14

# --- 밸류 (첨부 PDF, 9/4 종가) ---
MU_PRICE = 1016.59
MU_CY27_EPS = 150
MU_CY27_PER = 6.8
SNDK_PRICE = 1740
SNDK_FY27_EPS = 201
SNDK_FY27_PER = 8.7
HYNIX_KR_PRICE = 1_647_000
HYNIX_26_PER = 4.7
HYNIX_27_PER = 3.8
HYNIX_ADR_PER_26 = 6.8
HYNIX_ADR_PER_27 = 5.5
SAMSUNG_KR_PRICE = 255_000
SAMSUNG_26_PER = 5.3
SAMSUNG_27_PER = 3.8
HYNIX_ADR_PREMIUM_PCT = 44
WON_PLUS_10_EQUITY_HIT_PCT = 12

# --- 미국 DC 건설 (Census, July 2026 SAAR) ---
US_DC_JUL26_SAAR_B = 75.2
US_DC_JUL26_YOY_PCT = 57.2
US_DC_JUL26_MOM_PCT = 6.2
US_DC_SINCE_2021_PCT = 717

# --- Arm Physical AI ---
ARM_PAI_PARTNERS = 80
ARM_PAI_TAM_26_B = 25
ARM_PAI_TAM_30S_B = 200

# --- Astra 시뮬레이션 (코멘트 가정, 확정 실적 아님) ---
ASTRA_TOKEN_EFFICIENCY = 0.70
ASTRA_TASK_MULTIPLE = 3.0
ASTRA_USER_MULTIPLE = 2.0  # 5억 → 10억
# 0.7 * 3 = 2.1, * 2 users = 4.2

# --- CoreWeave (첨부, 9/5) ---
CRWV_2Q26_REV_B = 2.6
CRWV_BACKLOG_B = 104
CRWV_2026E_REV_B = 12.8
CRWV_2027E_REV_B = 19.5
CRWV_POWER_LIVE_GW = 1.5
CRWV_POWER_CONTRACT_GW = 3.7
CRWV_TOP3_REV_PCT = 72
CRWV_ADJ_OPINC_M = 128
CRWV_NET_INTEREST_M = 640

# --- 대미투자 엔시날 ---
ENCINAL_GW = 6.3
ENCINAL_USD_B = 22.3
ENCINAL_PHASE1_GW = 1.4
ENCINAL_CCGT_GW = 4.9

# --- 후티 ---
HOUTHI_INJURED = 73

# --- DeepSeek / Huawei ---
DEEPSEEK_950DT_UNITS = 160_000
DEEPSEEK_UNIT_USD = 16_000
DEEPSEEK_NOTIONAL_B = 2.56

# --- PSK / 로보티즈 (첨부) ---
PSK_26_SALES_B = 2792
PSK_27_SALES_B = 4014
PSK_26_OP_B = 1088
PSK_27_OP_B = 1648
PSK_TP = 195_000
ROBOTIS_25_ACT_M = 0.22
ROBOTIS_26_ACT_M = 0.50
ROBOTIS_25_SALES_B = 390
ROBOTIS_26_SALES_B = 500
ROBOTIS_27_SALES_B = 1000

# --- Azure (첨부 9/5 총망라) ---
AZURE_FY26_Q4_B = 29.4
AZURE_FY26_Q4_YOY = 43
AZURE_FY26_B = 101.9

# --- 일정 ---
APPLE_EVENT = "9/9"
ORACLE_EARNINGS = "9/10"
NVIDIA_GS = "9/10"
PPI = "9/10"
CPI = "9/11"
ETF_REBAL = "9/10"
ENCINAL_ANN = "9/18 전후"


def dram_total() -> float:
    return round(sum(v[1] for v in DRAM_VENDORS_2Q26) + 0.115 + 0.808, 3)


def buyback_upside_multiple(now: float, mx: float) -> float:
    return round(mx / now, 2)


def astra_inference_multiple() -> float:
    return round(ASTRA_TOKEN_EFFICIENCY * ASTRA_TASK_MULTIPLE, 2)


def astra_total_with_users() -> float:
    return round(astra_inference_multiple() * ASTRA_USER_MULTIPLE, 2)


def assert_all() -> None:
    assert DRAM_2Q26_REVENUE_B == 154.73
    assert DRAM_VENDORS_2Q26[0][2] == 39.4
    assert DRAM_VENDORS_2Q26[1][2] == 24.9
    assert buyback_upside_multiple(HYNIX_BUYBACK_DAILY_NOW_M, HYNIX_BUYBACK_DAILY_MAX_M) == 3.7
    assert abs(buyback_upside_multiple(SAMSUNG_BUYBACK_DAILY_NOW_M, SAMSUNG_BUYBACK_DAILY_MAX_M) - 3.66) < 0.01
    assert astra_inference_multiple() == 2.1
    assert astra_total_with_users() == 4.2
    assert DEEPSEEK_950DT_UNITS * DEEPSEEK_UNIT_USD / 1e9 == DEEPSEEK_NOTIONAL_B
    assert abs(ENCINAL_PHASE1_GW + ENCINAL_CCGT_GW - ENCINAL_GW) < 1e-9
    assert ARM_PAI_TAM_30S_B / ARM_PAI_TAM_26_B == 8
    assert IPHONE18_MEM_BOM_PCT == 34
    assert HOUTHI_INJURED == 73


if __name__ == "__main__":
    assert_all()
    print("sep08_data: ok")
