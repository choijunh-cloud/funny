"""2026-09-20 일요일 오전 다이제스트 — 잠글 숫자와 잠그지 않을 숫자.

시계
  목 9/17 미국장 = 업로드 PDF 3편 (FOMC 전날 안도 반등)
  금 9/18 미국장 = FOMC/BOJ 다음날 종가 (토 AM/PM에서 이미 읽힘)
  토 9/19 방송   = 오늘 MAIN 8편의 업로드·촬영 슬롯
  일 9/20        = KR 휴장 · 새 overnight 창 없음

준혁 프레임은 덮어쓰지 않는다: 10Y 5% · 30Y 6% · TIPS 3.0% ·
닉스 자사주 vs 삼성 배당/1월 · AI 약한 고리 = 자금+장기금리.
사이렌(10Y 5% 안착 · oil 120)은 미발화.
"""

from __future__ import annotations

# --- 공식: 공개 종가·정기간행 교차 ---
FRI_DOW_PX = 51682.64
FRI_DOW_PCT = -0.18
FRI_SPX_PX = 7650.50
FRI_SPX_PCT = 0.17
FRI_NASDAQ_PX = 26522.55
FRI_NASDAQ_PCT = 0.40  # Reuters 0.40 / 일부 매체 0.39
FRI_SOX_PCT = 2.78
FRI_WTI = 100.30
FRI_WTI_CHG = -1.61
FRI_BRENT = 103.87

THU_DOW_PCT = 0.6
THU_SPX_PCT = 1.1
THU_NASDAQ_PCT = 1.7
THU_SOX_PCT = 3.1
THU_TENY_CMT = 4.94  # 전일 5.01 → 4.94 (PDF는 5%→4.95로 반올림)
THU_CLAIMS = 196_000
THU_CLAIMS_CONSENSUS = 207_000

# 금요 10Y: 장중 5.002 보도 · 워킹 밴드 4.95–5.01. 안착 아님.
TENY_WORKING_LO = 4.95
TENY_WORKING_HI = 5.01
TENY_FRI_PRINT = 5.002
TENY_SIREN = 5.00  # 사용자 프레임 '안착' 기준. 터치 ≠ 안착.
OIL_SIREN = 120.0
THIRTY_Y_FRAME = 6.0
TIPS_FRAME = 3.0

# 목 9/17 SOX 개별 (PDF 인용 · 목 테이프만)
THU_SOX_NAMES = [
    ("ARM", 8.6),
    ("INTC", 7.7),
    ("AMD", 6.4),
    ("SNDK", 6.2),
    ("MU", 5.5),
    ("MRVL", 4.8),
    ("Hynix ADR", 4.6),
    ("NVDA", 2.5),
    ("AVGO", 2.2),
]

# 방송 수급 (815 금 19:00 촬영 · 공시 재대조)
FLOW_FOREIGN_JO = 1.0  # ~1조 순매수
FLOW_INST_JO = 1.8  # ~1조 8천억

# 김광석 방송 통계 (원표 재대조)
EXPORT_YEAR_PCT = 40
EXPORT_AUGSEP_PCT = 48
BOK_THIS = 3.3
BOK_NEXT = 2.9

# 블룸 가이던스 (815 인용 · company guidance)
BLOOM_GUIDE_LO = 3.9
BLOOM_GUIDE_HI = 4.2

# 엑시나 회사 주장 (스폰서)
CXL_UTIL_NOW = 35
CXL_UTIL_POOL = 75  # 70–80 중간

# IB / 게스트 가격 — 잠금 금지
UNLOCKED = {
    "ib_hynix_310": 310,
    "ib_hynix_400": 400,
    "ib_samsung_59": 59,
    "guest_hynix_200": 200,
    "guest_samsung_lo": 29,
    "guest_samsung_hi": 30,
    "cts_samsung_op": 500,
    "cts_hynix_lo": 370,
    "cts_hynix_hi": 380,
    "softbank_apollo_b": 9,
    "samsung_op_370": 370,
    # 일 AM 추가 대담·텔레그램 — 수치 보관만. 방 합의 아님.
    "ubs_ai_2025": 506,
    "ubs_ai_2026": 998,
    "ubs_ai_2027": 1447,
    "ubs_mem_2025": 71,
    "ubs_mem_2026": 367,
    "ubs_mem_2027": 923,
    "ubs_mem_share_2027": 64,
    "ubs_increment_mem_pct": 90,
    "trump_gdp_ai_pct": 25,
    "barclays_humanoid_year": 2035,
    "gpu_abs_target_b": 500,
    "hyojin_capex_2026_t": 1.0,
    "shin_dollar_now": 90,
    "shin_dollar_lo": 60,
    "shin_dollar_hi": 70,
}

# 토 PM MAIN — 재등록 금지, 한 줄만
SAT_PM_MAIN = [
    ("각도기 Sat US", "xG6588IXZJI", "SoftBank–Apollo ~$9B 서사·웹 미확정 그대로."),
    ("815 찐시황", "H6-OAvaZ-Pc", "SOX 상단 돌파·추석 3거래일. 오늘 MAIN2(금 19:00)와 시계 분리."),
    ("삼프로 이지환", "Dm2-8f-Itwc", "외인 선진입·주주환원~300조 서술 유지. 오늘 박병창과 게스트만 다름."),
    ("염블리 비밀노트", "ESX02IP_ZxQ", "IB 310/400/59 · 네비우스 10/1+20% 유지. 목표가≠합의."),
    ("슈카 821조", "93iH1jbSiPw", "재정 레인 유지."),
    ("김작가×김장열", "5nzxKYJ8E_A", "자사주~58/63%·10월 실적창 유지."),
]

MAIN = [
    {
        "id": 1,
        "ch": "삼프로TV",
        "guest": "박병창",
        "yt": "-rdWdJl-REE",
        "views": 3322,
        "len": "52:39",
        "when": "업로드 9/19",
        "title": "금리 인상인데 악재 끝? 오히려 지금이 기회",
    },
    {
        "id": 2,
        "ch": "815머니톡",
        "guest": "이주연",
        "yt": "BIXA-gon66w",
        "views": 120499,
        "len": "24:36",
        "when": "촬영 금 19:00 / 업로드 9/19",
        "title": "외인 1조 · 60일선 · 박스 돌파",
    },
    {
        "id": 3,
        "ch": "김민수의 같이투자",
        "guest": "김민수",
        "yt": "TA68VE-apr0",
        "views": 40113,
        "len": "1:17:50",
        "when": "토 파워섹터 라이브",
        "title": "10Y 5.04 터치 → 비중 운전",
    },
    {
        "id": 4,
        "ch": "김광석TV",
        "guest": "김광석·김영익·정주용",
        "yt": "SmqUrbRbCo4",
        "views": 28362,
        "len": "2:23:36",
        "when": "토 롱폼 AI 토론",
        "title": "AI는 혁명인가, 거품인가",
    },
    {
        "id": 5,
        "ch": "언더스탠딩",
        "guest": "김진영(엑시나) ※후원",
        "yt": "5cOS2mK4l_M",
        "views": 113297,
        "len": "56:36",
        "when": "업로드 9/19",
        "title": "CXL 메모리 풀링 (1부)",
    },
    {
        "id": 6,
        "ch": "한경TV 경제전쟁꾼",
        "guest": "김학균·이경민",
        "yt": "b8LsRaMzib0",
        "views": 97358,
        "len": "51:44",
        "when": "금 19:00 관행 / 업로드 9/18",
        "title": "올렸는데 코스피 반등",
    },
    {
        "id": 7,
        "ch": "인포맥스라이브",
        "guest": "문홍철",
        "yt": "KG9YCdEmzIQ",
        "views": 419858,
        "len": "44:48",
        "when": "금 인포맥스 260918",
        "title": "터치 vs 종가 5%",
    },
    {
        "id": 8,
        "ch": "염블리",
        "guest": "염승환",
        "yt": "E9QKryBfMzQ",
        "views": 79858,
        "len": "52:57",
        "when": "금 장마감 함께읽기",
        "title": "이번엔 호재? 수요 증거",
    },
]

# 일 AM 추가 대담 — MAIN이 아님. 토 PM 재등록도 아님.
ADDON = [
    {
        "id": "A1",
        "ch": "증시작도TV",
        "guest": "홍기빈",
        "yt": "",
        "len": "~40분",
        "when": "주말 대담 · 일 AM 수집",
        "title": "피지컬 AI · 암묵지 · 데이터 커먼스",
    },
    {
        "id": "A2",
        "ch": "역시나박정호",
        "guest": "박정호",
        "yt": "",
        "len": "~48분",
        "when": "주말 대담 · 일 AM 수집",
        "title": "속도조절론 = 면피 · 에이전트 검수 지체",
    },
    {
        "id": "A3",
        "ch": "삼프로TV",
        "guest": "신환종",
        "yt": "",
        "len": "~45분",
        "when": "주말 대담 · 일 AM 수집",
        "title": "스티키 인플레 · 10Y 터치 · 금",
    },
    {
        "id": "A4",
        "ch": "머니리포트",
        "guest": "김효진",
        "yt": "",
        "len": "~38분",
        "when": "주말 대담 · 일 AM 수집",
        "title": "아스트라 · 자금 약한 고리 · GPU 유동화",
    },
]

# 신한 멤버십 김학균은 MAIN 6과 같은 금리 축. 재등록 없음.
HAKGYUN_MEMBERSHIP = (
    "신한 멤버십 김학균은 MAIN 6(한경 경제전쟁꾼)과 같은 금요 금리 축. "
    "정책금리 4% vs 시장 장기물 ~5.3% 서사 유지. 오늘 MAIN·ADDON으로 올리지 않는다."
)

DO_NOT_LOCK = [
    "SoftBank–Apollo 확정 딜",
    "삼성 OP 370조를 합의 숫자로",
    "CTS 삼성 500조 / 닉스 370~380조",
    "IB 목표가 닉스 310/400 · 삼전 59를 합의 가격으로",
    "게스트 상자 닉스 200만 · 삼전 29~30만 · 이익 500조",
    "10Y 5% 안착",
    "oil 120",
    "Ohio × 하이닉스 계약 확정",
    "월요일 방향·종가·%",
    "추석 전후 필연 약세",
    "UBS 90%·CapEx 경로를 방 합의로",
    "트럼프 GDP 25%를 공식 전망으로",
    "Hugging Face 로그 삭제 = 확정 사실",
    "GPU 유동화 = 2008 재현",
    "Barclays 2035를 합의 보급 시점으로",
    "데이터 커먼스 제도 확정",
    "속도조절 = 실제 감속",
    "샌더스 ASI 금지법 통과",
]


def siren_10y_fired() -> bool:
    """안착 = 종가로 5% 위에 자리 잡는 것. 터치·워킹 밴드는 아님."""
    return False


def siren_oil_fired() -> bool:
    return FRI_WTI >= OIL_SIREN
