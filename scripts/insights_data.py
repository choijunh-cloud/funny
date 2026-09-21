"""8/18–9/20 투자 스터디 통합 인사이트 — 잠글 숫자와 잠그지 않을 숫자.

출처는 funny 저장소 강의노트·브리프·하이브리드 포트폴리오.
준혁 프레임은 덮어쓰지 않는다: 10Y 5% · 30Y 6% · TIPS 3.0% ·
닉스 자사주 vs 삼성 배당/1월 · AI 약한 고리 = 자금+장기금리.
사이렌(10Y 5% 안착 · oil 120)은 미발화.
"""

from __future__ import annotations

# --- 준혁 프레임 (덮어쓰지 않음) ---
TENY_FRAME = 5.00
THIRTY_Y_FRAME = 6.0
TIPS_FRAME = 3.0
OIL_SIREN = 120.0
TENY_SIREN = 5.00
TENY_WORKING_LO = 4.95
TENY_WORKING_HI = 5.01
TENY_FRI_PRINT = 5.002  # 9/18 장중 보도. 터치 ≠ 안착.
FRI_WTI = 100.30
FRI_BRENT = 103.87

# --- 금 9/18 공식 종가 ---
FRI_DOW_PX = 51682.64
FRI_DOW_PCT = -0.18
FRI_SPX_PX = 7650.50
FRI_SPX_PCT = 0.17
FRI_NASDAQ_PX = 26522.55
FRI_NASDAQ_PCT = 0.40
FRI_SOX_PCT = 2.78
KOSPI_SEP18 = 6894.23
KOSPI_SEP18_PCT = 2.66
SAMSUNG_SEP18 = 261_000
SAMSUNG_SEP18_PCT = 3.37
HYNIX_SEP18 = 1_857_000
HYNIX_SEP18_PCT = 6.42

# --- FOMC SEP 9/16 ---
FED_BAND = "3.75–4.00"
FED_HIKE_BP = 25
DOT_MEDIAN = [4.1, 4.1, 3.9, 3.2]  # 26 / 27 / 28 / longer
CORE_PCE = [3.4, 2.5, 2.2]
BOJ_RATE = 1.25
USDJPY_SEP18 = 157.12
USDKRW_SEP18 = 1383.3
KR10Y_SEP18 = 4.466

# --- 메모리 PER 스냅 (강의 표, 날짜 태그) ---
# 8/14 종가 기준 (8/18 강의 부록)
AUG18_PER = {
    "hynix_px": 1_645_000,
    "hynix_26": 4.8,
    "hynix_27": 3.8,
    "samsung_px": 274_500,
    "samsung_26": 5.7,
    "samsung_27": 4.1,
    "mu_fwd12": 7.8,
    "mu_cy27": 6.5,
    "sndk_fy27": 8.2,
    "adr_prem": 43,
}
# 9/15 스냅
SEP15_PER = {
    "hynix_px": 1_697_000,
    "hynix_27": 4.3,
    "samsung_px": 249_000,
    "samsung_27": 4.2,
    "mu_cy27": 6.2,
    "sndk_fy27": 7.7,
    "spx_fwd26": 21.0,
    "spx_fwd27": 18.5,
    "earn_yield": 4.76,
}

# Citi 9/18 (스터디 인용)
CITI_DRAM_SHORT = (8.7, 9.7)
CITI_NAND_SHORT = (6.1, 5.5)
CITI_HBM_BIT = (62, 69)  # 27 / 28 %
CITI_DRAM_DEMAND = (30, 35)
CITI_DRAM_SUPPLY = (19, 22)

# 토큰 8월 (JPM/OpenRouter, 9/18 브리프)
TOKEN_VOL_MOM = 47
TOKEN_VOL_YOY_X = 28
TOKEN_SPEND_MOM = 7
TOKEN_SPEND_YOY_X = 12
TOKEN_PRICE_MOM = -28
TOKEN_PRICE_YOY = -56

# NVIDIA Q2 FY27 (컨콜 노트)
NVDA_REV = 96.2
NVDA_GM = 75.0
NVDA_NI = 59.7
NVDA_OCF = 24.1
NVDA_OCF_NI = 40.3
NVDA_AR = 63.1
NVDA_DSO = (45, 60)
NVDA_Q3_REV = 108.0
NVDA_SUPPLY_COMMIT = 279
NVDA_FY28_SUPPLY_CAP = 70  # +70% = supply cap, not demand

# Dell Q2 FY27 (PR 상수)
DELL_Q2_REV = 46.971
DELL_AI_REV = 16.401
DELL_ORDERS = 60.9
DELL_BACKLOG = 95.0
DELL_FY27_REV = (167.0, 192.0)
DELL_FY27_AI = (60.0, 74.0)

# Oracle Q1 FY27
ORCL_REV = 19.3
ORCL_RPO = 664
ORCL_NEW_AI = 30
ORCL_FY27_CAPEX = (90, 95)
ORCL_NET_CASH_CAPEX = 70

# 소부장 2Q26 (8/18)
TES_NEW_ORDERS = 2823  # 억, QoQ 2배
TES_BACKLOG = 2000
HANMI_REV = 2511
HANMI_OPM = 51.9
HANMI_SHARE = (55, 60)
WONIK_BACKLOG_1Q = 4000
WONIK_SAFE_TP = (10.4, 11.8)
LEENO_OPM = 51.3

# SK / 에코플랜트 (8/18)
SK_NAV = 81.7
SK_DISC = 41
SK_TP_DAISHIN = 88
SK_ECO_OP_2Q = 0.534  # 조
SK_ECO_BACKLOG = 26.8
SK_ECO_TABLE = 2.1
SK_ECO_SALES_MIX = [
    ("Asset Lifecycle", 45),
    ("Hi-Tech", 33),
    ("Solution", 18),
    ("Gas & Material", 4),
]
SK_REVAL_TP = (96, 106)

# 하이브리드 H2 (9/3 as-of, 계산)
H2_ASOF_KOSPI = 6600
H2_EQUITY = 60
H2_CASH = 40
H2_TOP10 = [
    ("SK하이닉스", 21.4, 13.5, "Hold"),
    ("SK스퀘어", 16.4, 0.0, "Hold"),
    ("한국금융지주", 14.9, 0.0, "Split #1"),
    ("삼성전자", 13.1, 16.5, "Hold"),
    ("한국전력", 12.8, 1.8, "Split dips"),
    ("NAVER", 12.7, 0.0, "Split dips"),
    ("삼성전자우", 11.9, 0.0, "Hold"),
    ("두산에너빌리티", 11.3, 2.5, "Watch"),
    ("현대모비스", 11.1, 0.0, "Split dips"),
    ("대한항공", 11.0, 1.1, "Split dips"),
]
BOOK_C = [
    ("SEMI", 45),
    ("SHORT_DURATION", 25),
    ("OIL_DOWN", 10),
    ("HEDGE", 20),
]

# DC 전력 TrendForce (9/17)
DC_GW = (122.9, 161.0)
DC_2030_DEMAND = 490.7
DC_2030_GRID = 222.6
DC_GAP = 268.1
AI_SERVER_SHARE = (25.0, 33.4, 40.0)

# 수출 (9/18 브리프)
SEMI_EXPORT_AUG_PCT = 209
TOTAL_EXPORT_AUG_B = 98.25
SEMI_EXPORT_AUG_B = 46.65
SEMI_SHARE_YTD = 40.6

# 수급 9/18
FLOW_RETAIL = -3.59
FLOW_INST = 1.50
FLOW_FOREIGN = 0.43
FLOW_CORP = 1.67

# KOSPI 박스 / W
KOSPI_PEAK = 9114.55  # 6/22
KOSPI_TROUGH = 5593.56  # 7/30
KOSPI_DRAW = -38.6
BOX_LO = 6000
BOX_HI = 7150
GRAVITY_LO = 5.0
GRAVITY_HI = 5.3

# 리드타임 주 (9/15)
LEAD_WEEKS = [
    ("ABF", 52),
    ("HDD", 50),
    ("MLCC", 30),
    ("GPU", 25),
    ("DRAM", 20),
    ("NAND", 16),
]

# 알테오젠 / 현대제철 — 위성 스터디
ALTEOGEN_PX = 320_000
ALTEOGEN_HANA_TP = 580_000
HYUNDAI_STEEL_TP = 42_000
HYUNDAI_STEEL_PX = 31_000

# 잠금 금지 (보관만)
UNLOCKED = {
    "ib_hynix_310": 310,
    "ib_hynix_400": 400,
    "ib_samsung_59": 59,
    "guest_hynix_200": 200,
    "guest_samsung_lo": 29,
    "guest_samsung_hi": 30,
    "cts_samsung_op": 500,
    "samsung_op_370": 370,
    "ubs_ai_2025": 506,
    "ubs_ai_2026": 998,
    "ubs_ai_2027": 1447,
    "ubs_mem_2025": 71,
    "ubs_mem_2026": 367,
    "ubs_mem_2027": 923,
    "ubs_increment_mem_pct": 90,
    "trump_gdp_ai_pct": 25,
    "gpu_abs_target_b": 500,
}

DO_NOT_LOCK = [
    "IB 목표가(닉스 310/400 · 삼전 59)를 합의 가격으로",
    "게스트 상자 닉스 200만 · 삼전 29~30만",
    "10Y 5% 안착 · oil 120",
    "Ohio × 하이닉스 계약 확정",
    "UBS CapEx 경로 · 증가분 90%를 방 합의로",
    "트럼프 GDP 25%를 공식 전망으로",
    "GPU 유동화 = 2008 재현",
    "속도조절 = 실제 감속",
    "월요일 방향·종가·%",
]

# 스터디 코퍼스 (투자만. 커넥톰·봉직·클리닉 제외)
CORPUS = [
    ("8/18", "NON-삼전닉스", "소부장·SK·Atlas", "MAIN"),
    ("8/18", "오전 브리프", "유가·금리 vs 메모리", "MAIN"),
    ("8/19", "시장 시각화", "환율·환원·HBM", "MAIN"),
    ("8/21", "AI 강의", "마이크론 150%·공동설계", "MAIN"),
    ("8/25", "통합 레포트", "회전·Bessent·핵", "MAIN"),
    ("8/26", "NVDA 인쇄", "공급약정 279B", "MAIN"),
    ("8/27", "컨콜 분석", "수요 100 · 공급 70", "MAIN"),
    ("8/28", "규칙", "추격금지·AI 50%", "MAIN"),
    ("8/28", "알테오젠", "ALT-B4 ≠ 시밀러", "SAT"),
    ("8/31", "현대제철", "합성 TP 4.2만", "SAT"),
    ("9/02", "모닝미팅", "유가→금리·Dell", "MAIN"),
    ("9/02", "Dell 콜", "백로그 95B", "MAIN"),
    ("9/03", "H2 포트", "하이브리드 Top10", "MAIN"),
    ("9/05", "절단된 사슬", "oil≠정책경로", "MAIN"),
    ("9/08", "Quick", "애플 NAND·9/10 수급", "MAIN"),
    ("9/11", "한 장", "Oracle·온디바이스", "MAIN"),
    ("9/15", "통합브리핑", "속도조절·Token·PER", "MAIN"),
    ("9/16", "방송노트", "FOMC 전 3방송", "MAIN"),
    ("9/17", "FOMC 익일", "점도표·전력갭", "MAIN"),
    ("9/18", "브리프", "W바닥·박스·토큰", "MAIN"),
    ("9/20", "일요 digest", "MAIN8+ADDON4", "MAIN"),
]

THESES = [
    {
        "id": "T1",
        "title": "양면 시각은 계속된다",
        "line": "최종수요는 아무도 못 맞춘다. 모델·DC·GPU에 기대고, 자금이 딸리니 서로 묶는다.",
        "watch": "수주 가시성 · 할인율 · Dark GPU 역레버리지",
    },
    {
        "id": "T2",
        "title": "약한 고리 = 자금 + 장기금리",
        "line": "AI 수요 부정이 아니라 조달 조건. 5%는 위험 신호이지 방아쇠가 아니다.",
        "watch": "10Y 5.0–5.3 추세 AND No Way Back",
    },
    {
        "id": "T3",
        "title": "P↓여도 Q가 더 늘면 된다",
        "line": "토큰 단가 하락은 수요 파괴가 아니라 사용량 폭증의 반대편.",
        "watch": "9/29 DevDay Agent·API·기업 배포 숫자",
    },
    {
        "id": "T4",
        "title": "병목 = 노드 = 돈",
        "line": "연산은 풀렸고 지금은 메모리, 다음 영수증은 전력·후공정.",
        "watch": "HBM4 · 변압기 50주+ · 모듈 외주",
    },
    {
        "id": "T5",
        "title": "저PER을 싸다고 읽지 말 것",
        "line": "이익 폭증이 PER을 눌렀다. 숫자의 신뢰가 주가다.",
        "watch": "10/1 Micron 마진 · 3Q 하이퍼스케일러 현금",
    },
    {
        "id": "T6",
        "title": "장비는 실적보다 수주가 먼저",
        "line": "2Q 숫자보다 하반기 매출화, 그리고 2027 수주가 다시 증가하는지가 승부처.",
        "watch": "테스 BSD · 한미 점유율 · 원익 3체크",
    },
    {
        "id": "T7",
        "title": "할인율이 좁혀질 이유가 늘었다",
        "line": "에코플랜트 2.1조는 낮다. 그래도 NAV의 기본은 하이닉스와 이노베이션.",
        "watch": "표 2.1조 재평가 · 실트론 대금 사용처",
    },
    {
        "id": "T8",
        "title": "로봇 성능 논쟁은 끝나가고 배치가 시작",
        "line": "Atlas = Fleet × 가동률 × 데이터. 모비스는 부품, 글로비스는 서열.",
        "watch": "11월 시제품 · 2028 HMGMA",
    },
]

CHECKPOINTS = [
    ("상시", "10Y 5.0–5.3 추세 + CPI 3.4 재가속", "Gravity AND"),
    ("상시", "WTI vs 120 · 터치 vs 안착", "사이렌 미발화"),
    ("9/28–30", "삼성 배당 이사회 창", "환원 축"),
    ("9/29", "DevDay Agent·API·배포 숫자", "토큰 Q"),
    ("10/1", "Micron 마진 80%대 후반?", "메모리 증거"),
    ("10월", "닉스 자사주 소화 페이스", "닉스 vs 삼성 스타일"),
    ("3Q 콜", "하이퍼스케일러 현금→DC/토큰", "상단 열쇠"),
    ("탐색", "Ohio·NY 계약으로 넘어가나", "미잠금"),
    ("하반기", "테스 BSD 퀄 · 한미 55–60% · 원익 OP", "소부장"),
    ("2028", "HMGMA 투입 대수·가동시간", "Atlas"),
]

EVOLUTION = [
    ("8월", "NON-삼전닉스 · 수주 · NAV", "Dark GPU는 수요 부정이 아님"),
    ("8월 말", "NVDA 인쇄 후 신용·마진 이전", "수요 100 · 공급 70"),
    ("9/3–5", "H2 포트 · 절단된 사슬", "oil→정책 경로 절단"),
    ("9/8–11", "애플 NAND · Oracle 자금줄", "온디바이스 = NAND 티어링"),
    ("9/15–16", "속도조절 = Timing", "Peak-out 아님"),
    ("9/17–18", "FOMC+BOJ · W바닥 · 박스", "5% 터치 ≠ AND"),
    ("9/20", "일요 논리 고정", "사이렌·IB·Ohio 잠금 금지"),
]


def siren_10y_fired() -> bool:
    return False


def siren_oil_fired() -> bool:
    return FRI_WTI >= OIL_SIREN


def kospi_drawdown_from_peak(px: float = KOSPI_SEP18) -> float:
    return (px / KOSPI_PEAK - 1.0) * 100.0


def nvda_ocf_ni() -> float:
    return round(NVDA_OCF / NVDA_NI * 100.0, 1)


def dc_gap() -> float:
    return round(DC_2030_DEMAND - DC_2030_GRID, 1)
