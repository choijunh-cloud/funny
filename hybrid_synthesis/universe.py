"""Investable KOSPI universe for the hybrid synthesis sleeves.

The source notes name several KOSDAQ names (Simmtech, TLB, D.I, L&F).
Those are recorded as exclusions and remapped to KOSPI substitutes so the
portfolio never leaves the KOSPI board.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Literal


Sleeve = Literal["CORE_SEMI", "AI_CONNECT", "MACRO_HEDGE", "COSMETICS", "NONE"]
Action = Literal["CORE_HOLD", "ACCUMULATE", "TRADE", "HEDGE", "WATCH", "AVOID"]


@dataclass(frozen=True)
class Stock:
    ticker: str
    name: str
    name_en: str
    market: Literal["KOSPI", "KOSDAQ"]
    sleeve: Sleeve
    action: Action
    subsector: str
    # Factor scores are 0–100 expert encodings from the five-video synthesis.
    ai_earnings: float
    connectivity: float
    fcf_beta: float
    policy_beta: float
    valuation_safety: float
    liquidity: float
    rate_hedge: float
    fx_krw_strength: float
    cxmt_benefit: float
    ymtc_nand_risk: float
    thesis: str
    avoid_flags: tuple[str, ...] = ()
    kosdaq_proxy_of: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if len(self.ticker) != 6 or not self.ticker.isdigit():
            raise ValueError(f"ticker must be a 6-digit KRX code, got {self.ticker!r}")
        for field in (
            "ai_earnings",
            "connectivity",
            "fcf_beta",
            "policy_beta",
            "valuation_safety",
            "liquidity",
            "rate_hedge",
            "fx_krw_strength",
            "cxmt_benefit",
            "ymtc_nand_risk",
        ):
            value = float(getattr(self, field))
            if not 0.0 <= value <= 100.0:
                raise ValueError(f"{self.ticker} {field} must be in [0, 100], got {value}")

    @property
    def is_kospi(self) -> bool:
        return self.market == "KOSPI"

    @property
    def is_avoid(self) -> bool:
        return self.action == "AVOID" or bool(self.avoid_flags) or not self.is_kospi

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["is_kospi"] = self.is_kospi
        payload["is_avoid"] = self.is_avoid
        return payload


def _s(
    ticker: str,
    name: str,
    name_en: str,
    sleeve: Sleeve,
    action: Action,
    subsector: str,
    scores: tuple[float, ...],
    thesis: str,
    *,
    avoid_flags: tuple[str, ...] = (),
    kosdaq_proxy_of: tuple[str, ...] = (),
    market: Literal["KOSPI", "KOSDAQ"] = "KOSPI",
) -> Stock:
    (
        ai_earnings,
        connectivity,
        fcf_beta,
        policy_beta,
        valuation_safety,
        liquidity,
        rate_hedge,
        fx_krw_strength,
        cxmt_benefit,
        ymtc_nand_risk,
    ) = scores
    return Stock(
        ticker=ticker,
        name=name,
        name_en=name_en,
        market=market,
        sleeve=sleeve,
        action=action,
        subsector=subsector,
        ai_earnings=ai_earnings,
        connectivity=connectivity,
        fcf_beta=fcf_beta,
        policy_beta=policy_beta,
        valuation_safety=valuation_safety,
        liquidity=liquidity,
        rate_hedge=rate_hedge,
        fx_krw_strength=fx_krw_strength,
        cxmt_benefit=cxmt_benefit,
        ymtc_nand_risk=ymtc_nand_risk,
        thesis=thesis,
        avoid_flags=avoid_flags,
        kosdaq_proxy_of=kosdaq_proxy_of,
    )


# Score tuple: AI, connect, FCF, policy, val, liq, rate-hedge, KRW, CXMT, YMTC-risk
KOSPI_UNIVERSE: tuple[Stock, ...] = (
    _s(
        "005930",
        "삼성전자",
        "Samsung Electronics",
        "CORE_SEMI",
        "CORE_HOLD",
        "DRAM/NAND/파운드리/HBM",
        (92, 70, 88, 96, 86, 100, 22, 32, 80, 28),
        "D램·모바일·낸드 두 자릿수 인상과 LTA 70%가 마진을 지킨다. "
        "10% 룰 때문에 자사주가 막히면 3Q/4Q 주당 4,000~4,800원 특별배당으로 우회할 확률이 높다. "
        "4분기 배당/소각 발표 전까지 핵심 코어 매도 금지.",
    ),
    _s(
        "000660",
        "SK하이닉스",
        "SK hynix",
        "CORE_SEMI",
        "CORE_HOLD",
        "HBM/DRAM",
        (97, 58, 92, 72, 80, 98, 16, 26, 90, 10),
        "HBM4 양산과 엔비디아 랙 시스템 잠금이 직접 연결된다. "
        "CXMT가 DUV로 HBM을 억지 생산할수록 중국 레거시 D램이 빠지며 범용 D램 가격을 방어한다. "
        "ADR 수급과 외평 개입은 단기 노이즈일 뿐 실적 궤적을 바꾸지 않는다.",
    ),
    _s(
        "005935",
        "삼성전자우",
        "Samsung Electronics Preferred",
        "CORE_SEMI",
        "WATCH",
        "우선주/배당",
        (88, 60, 80, 94, 88, 72, 20, 30, 70, 28),
        "보통주 대비 배당 민감도가 높아 특별배당 서프라이즈의 현금흐름 포착용이다. "
        "유동성이 보통주보다 얇아 코어 2종목 원칙에서는 기본 편입하지 않는다.",
    ),
    _s(
        "009150",
        "삼성전기",
        "Samsung Electro-Mechanics",
        "AI_CONNECT",
        "ACCUMULATE",
        "FC-BGA/MLCC",
        (74, 97, 88, 42, 70, 88, 12, 22, 22, 6),
        "서버·데이터센터 FC-BGA가 풀가동이고 수요가 캐파를 50% 초과한다. "
        "칩 단품이 아니라 기판이 AI 랙의 병목이다. 심텍/티엘비의 코스피 1순위 대체.",
        kosdaq_proxy_of=("222800", "356860"),
    ),
    _s(
        "007660",
        "이수페타시스",
        "ISU Petasys",
        "AI_CONNECT",
        "ACCUMULATE",
        "AI 고다층 PCB",
        (72, 95, 84, 28, 66, 72, 8, 16, 16, 4),
        "AI 가속기용 고다층 PCB. 영상이 지목한 심텍·티엘비와 같은 '연결성' 버킷의 코스피 순수 플레이.",
        kosdaq_proxy_of=("222800", "356860"),
    ),
    _s(
        "042700",
        "한미반도체",
        "Hanmi Semiconductor",
        "AI_CONNECT",
        "ACCUMULATE",
        "HBM TC 본더/장비",
        (90, 82, 80, 32, 52, 82, 8, 16, 74, 4),
        "HBM4 본딩 장비는 NVL72 랙 확대의 물리적 전제다. 코스피에서 거의 유일한 AI 전공정 장비 순수 노출. "
        "밸류에이션은 비싸므로 추격보다 비중 한도를 지킨다.",
        kosdaq_proxy_of=("003160",),
    ),
    _s(
        "353200",
        "대덕전자",
        "Daeduck Electronics",
        "AI_CONNECT",
        "ACCUMULATE",
        "FC-BGA",
        (64, 92, 80, 22, 70, 66, 6, 14, 12, 4),
        "FC-BGA 증설과 장기계약 선수금이 확인된 기판주. 2027년 분기 캐파 Ramp가 Phase 3 연결 사이클과 맞닿는다.",
        kosdaq_proxy_of=("222800",),
    ),
    _s(
        "007810",
        "코리아써키트",
        "Korea Circuit",
        "AI_CONNECT",
        "ACCUMULATE",
        "FC-BGA/PCIe 스위치 기판",
        (58, 90, 76, 18, 74, 58, 6, 12, 20, 4),
        "브로드컴향 FC-BGA와 PCIe 스위치 기판. 영상이 말한 '스위치 칩'을 코스피에서 기판으로 구현하는 종목.",
        kosdaq_proxy_of=("356860",),
    ),
    _s(
        "011070",
        "엘지이노텍",
        "LG Innotek",
        "AI_CONNECT",
        "WATCH",
        "FC-BGA/카메라",
        (60, 84, 74, 24, 62, 82, 10, 20, 12, 6),
        "대면적 FC-BGA 샘플과 기판 믹스 개선. 카메라 모듈 변동성이 있어 기본 5종에는 넣지 않고 예비 벤치로 둔다.",
    ),
    _s(
        "267260",
        "HD현대일렉트릭",
        "HD Hyundai Electric",
        "AI_CONNECT",
        "WATCH",
        "변압기/데이터센터 전력",
        (48, 78, 72, 44, 48, 78, 18, 22, 4, 2),
        "병목이 연산에서 전력·연결로 넘어가는 Phase 3의 전력 인사이트. Phase 1 기본 5종에는 과밀을 피한다.",
    ),
    _s(
        "014830",
        "한솔케미칼",
        "Hansol Chemical",
        "AI_CONNECT",
        "WATCH",
        "반도체 소재",
        (52, 62, 58, 18, 72, 62, 8, 12, 24, 8),
        "전구체·소재로 HBM/D램 증산에 연동된다. 연결성 코어보다는 2선 소재.",
    ),
    _s(
        "010120",
        "LS ELECTRIC",
        "LS Electric",
        "AI_CONNECT",
        "WATCH",
        "전력기기",
        (40, 70, 60, 36, 58, 70, 16, 24, 4, 2),
        "데이터센터 수배전. Phase 3 전력망 확대 때 슬리브 교체 후보.",
    ),
    _s(
        "298040",
        "효성중공업",
        "Hyosung Heavy Industries",
        "AI_CONNECT",
        "WATCH",
        "변압기",
        (38, 72, 62, 34, 50, 64, 14, 20, 2, 2),
        "초고압 변압기 공급 부족. 전력 병목 테마의 2선.",
    ),
    _s(
        "000990",
        "DB하이텍",
        "DB HiTek",
        "AI_CONNECT",
        "WATCH",
        "8인치 파운드리",
        (44, 40, 42, 16, 68, 60, 8, 14, 18, 6),
        "레거시 파운드리. AI 연결 사이클의 중심이 아니어서 기본 포트에 넣지 않는다.",
    ),
    _s(
        "402340",
        "SK스퀘어",
        "SK Square",
        "CORE_SEMI",
        "WATCH",
        "SK하이닉스 지주",
        (80, 40, 70, 40, 64, 70, 14, 20, 70, 10),
        "하이닉스 홀딩 할인. 코어는 운영사 직접 보유가 더 깔끔하다.",
    ),
    _s(
        "105560",
        "KB금융",
        "KB Financial",
        "MACRO_HEDGE",
        "HEDGE",
        "은행",
        (16, 8, 12, 58, 78, 96, 92, 74, 2, 2),
        "원화 강세 전환 시 BIS 개선 → 주주환원. 전고점 추격은 하지 않고 헷지 한도 안에서만 담는다.",
    ),
    _s(
        "055550",
        "신한지주",
        "Shinhan Financial",
        "MACRO_HEDGE",
        "HEDGE",
        "은행",
        (15, 8, 12, 54, 76, 92, 90, 70, 2, 2),
        "KB와 함께 은행 바스켓의 두 번째 축. 금리 피벗 전 자본비율 여력이 환원으로 연결된다.",
    ),
    _s(
        "086790",
        "하나금융지주",
        "Hana Financial",
        "MACRO_HEDGE",
        "WATCH",
        "은행",
        (14, 6, 10, 50, 74, 86, 86, 68, 2, 2),
        "은행 3선. 기본 4종 한도를 위해 벤치.",
    ),
    _s(
        "316140",
        "우리금융지주",
        "Woori Financial",
        "MACRO_HEDGE",
        "WATCH",
        "은행",
        (12, 6, 10, 48, 72, 84, 84, 66, 2, 2),
        "주주환원 스토리는 있으나 KB/신한 대비 유동성·시가총액에서 밀린다.",
    ),
    _s(
        "034020",
        "두산에너빌리티",
        "Doosan Enerbility",
        "MACRO_HEDGE",
        "HEDGE",
        "가스복합/원전/대미 인프라",
        (28, 42, 38, 78, 54, 88, 32, 42, 2, 2),
        "한미 대미투자 1호 텍사스 가스복합이 $250억 규모로 증액. 원전·가스터빈이 엔지니어링 레버리지.",
    ),
    _s(
        "015760",
        "한국전력",
        "KEPCO",
        "MACRO_HEDGE",
        "HEDGE",
        "유틸리티/송전망",
        (22, 38, 32, 84, 62, 88, 28, 78, 2, 2),
        "한전채 한도 때문에 삼성 20조·SK 5조 전기료 5년 선납을 요구. 송전망 투자와 원화 강세의 이중 수혜.",
    ),
    _s(
        "003490",
        "대한항공",
        "Korean Air",
        "MACRO_HEDGE",
        "HEDGE",
        "항공",
        (10, 6, 10, 22, 56, 82, 16, 92, 2, 2),
        "엔/원 왜곡이 풀리고 원화가 강하면 유류비·외화부채가 동시에 가벼워진다. 매크로 트레이딩 한도.",
    ),
    _s(
        "051600",
        "한전KPS",
        "KEPCO KPS",
        "MACRO_HEDGE",
        "WATCH",
        "발전정비",
        (14, 24, 22, 50, 64, 60, 18, 40, 2, 2),
        "한전 인프라의 2선. 기본 포트는 모회사 한전에 집중.",
    ),
    _s(
        "036460",
        "한국가스공사",
        "KOGAS",
        "MACRO_HEDGE",
        "WATCH",
        "가스",
        (12, 20, 18, 40, 60, 70, 20, 36, 2, 2),
        "텍사스 가스복합의 연료 밸류체인. 직접 수주 레버리지는 두산이 더 크다.",
    ),
    _s(
        "161890",
        "한국콜마",
        "Kolmar Korea",
        "COSMETICS",
        "TRADE",
        "ODM 화장품",
        (8, 6, 8, 26, 82, 72, 12, 44, 2, 2),
        "P/E 15~20배권의 수출 ODM. 매월 화장품 수출 통계에 맞춰 눌림목만 스윙한다. 코어가 아니다.",
    ),
    _s(
        "192820",
        "코스맥스",
        "Cosmax",
        "COSMETICS",
        "TRADE",
        "ODM 화장품",
        (8, 6, 8, 22, 80, 70, 12, 42, 2, 2),
        "콜마와 같은 수출 통계 스윙 바스켓. 중국 회복보다 미국·유럽 ODM 믹스가 포인트.",
    ),
    _s(
        "090430",
        "아모레퍼시픽",
        "Amorepacific",
        "COSMETICS",
        "WATCH",
        "브랜드 화장품",
        (6, 4, 6, 18, 48, 86, 10, 36, 2, 2),
        "브랜드 프리미엄 때문에 밸류에이션 안전장치가 콜마/코스맥스보다 약하다. 기본 10% 슬리브에서 제외.",
    ),
    _s(
        "051900",
        "LG생활건강",
        "LG H&H",
        "COSMETICS",
        "WATCH",
        "브랜드 화장품/생활",
        (6, 4, 6, 16, 50, 84, 10, 34, 2, 2),
        "중국 의존과 멀티플 부담. 데이터 스윙 대상으로 부적합.",
    ),
    _s(
        "373220",
        "LG에너지솔루션",
        "LG Energy Solution",
        "NONE",
        "AVOID",
        "2차전지 셀",
        (20, 10, 16, 12, 28, 90, 8, 20, 2, 2),
        "실적 대비 고PBR 2차전지. 단기 반등은 현금화 구간.",
        avoid_flags=("battery_high_pbr",),
    ),
    _s(
        "006400",
        "삼성SDI",
        "Samsung SDI",
        "NONE",
        "AVOID",
        "2차전지 셀",
        (18, 10, 14, 14, 30, 86, 8, 18, 2, 2),
        "셀 업황 회복 이전의 고평가 구간. 하이브리드 모형의 어떤 슬리브에도 넣지 않는다.",
        avoid_flags=("battery_high_pbr",),
    ),
    _s(
        "003670",
        "포스코퓨처엠",
        "POSCO Future-M",
        "NONE",
        "AVOID",
        "2차전지 소재",
        (16, 8, 12, 10, 24, 80, 6, 16, 2, 2),
        "소재 고PBR. 엘앤에프와 같은 배제 논리의 코스피 버전.",
        avoid_flags=("battery_high_pbr",),
    ),
    _s(
        "028050",
        "삼성E&A",
        "Samsung E&A",
        "NONE",
        "AVOID",
        "플랜트/중동 재건",
        (10, 8, 10, 14, 40, 74, 10, 22, 2, 2),
        "중동 전황 악화로 재건 모멘텀이 소멸. 건설/플랜트 테마 배제.",
        avoid_flags=("faded_theme",),
    ),
    _s(
        "000720",
        "현대건설",
        "Hyundai E&C",
        "NONE",
        "AVOID",
        "건설",
        (8, 6, 8, 12, 42, 76, 10, 20, 2, 2),
        "재건·중동 테마 소멸. 인프라 노출은 두산에너빌리티·한전으로 충분하다.",
        avoid_flags=("faded_theme",),
    ),
    _s(
        "006360",
        "GS건설",
        "GS E&C",
        "NONE",
        "AVOID",
        "건설",
        (6, 4, 6, 10, 38, 70, 8, 18, 2, 2),
        "주택/해외 수주 모멘텀이 모형 트리거와 무관하다.",
        avoid_flags=("faded_theme",),
    ),
    _s(
        "005380",
        "현대차",
        "Hyundai Motor",
        "NONE",
        "WATCH",
        "자동차",
        (24, 18, 20, 20, 58, 96, 20, 30, 2, 2),
        "피지컬 AI의 실질 승자는 자율주행이라는 진단은 있으나, 휴머노이드 테마로 접근하지 않는다. "
        "본 모형의 네 슬리브 밖이다.",
    ),
    _s(
        "012450",
        "한화에어로스페이스",
        "Hanwha Aerospace",
        "NONE",
        "WATCH",
        "방산",
        (18, 16, 16, 24, 46, 88, 14, 22, 2, 2),
        "방산은 별도 사이클. 하이브리드 모형의 매크로 헷지 버킷(은행·전력·항공)과 겹치지 않게 제외.",
    ),
)


NON_KOSPI_EXCLUSIONS: tuple[dict[str, str], ...] = (
    {
        "ticker": "222800",
        "name": "심텍",
        "market": "KOSDAQ",
        "reason": "FC-BGA/모듈 PCB이나 코스닥. 코스피 대체: 삼성전기·이수페타시스·대덕전자.",
    },
    {
        "ticker": "356860",
        "name": "티엘비",
        "market": "KOSDAQ",
        "reason": "서버 PCB. 코스피 대체: 이수페타시스·코리아써키트.",
    },
    {
        "ticker": "003160",
        "name": "디아이",
        "market": "KOSDAQ",
        "reason": "전공정 검사장비. 코스피 대체: 한미반도체(HBM 장비).",
    },
    {
        "ticker": "066970",
        "name": "엘앤에프",
        "market": "KOSDAQ",
        "reason": "PBR 7배권 2차전지 소재. 절대 배제. 코스피 동류(포스코퓨처엠)도 배제.",
    },
    {
        "ticker": "247540",
        "name": "에코프로비엠",
        "market": "KOSDAQ",
        "reason": "2차전지 소재. 절대 배제.",
    },
    {
        "ticker": "277810",
        "name": "레인보우로보틱스",
        "market": "KOSDAQ",
        "reason": "휴머노이드. 원가·자유도·보험 책임 미비. 영상용 테마 접근 금지.",
    },
    {
        "ticker": "454910",
        "name": "두산로보틱스",
        "market": "KOSDAQ",
        "reason": "휴머노이드/협동로봇. 상용화 기회비용. 두산 노출은 에너빌리티로만.",
    },
)


def kospi_investable() -> tuple[Stock, ...]:
    return tuple(stock for stock in KOSPI_UNIVERSE if stock.is_kospi and not stock.is_avoid)


def kospi_avoid() -> tuple[Stock, ...]:
    return tuple(stock for stock in KOSPI_UNIVERSE if stock.is_kospi and stock.is_avoid)


def by_ticker(ticker: str) -> Stock:
    for stock in KOSPI_UNIVERSE:
        if stock.ticker == ticker:
            return stock
    raise KeyError(ticker)
