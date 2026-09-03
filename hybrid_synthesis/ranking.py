"""H2 KOSPI Top 10: one ranking from three conflicting books.

Sources fused here
- Broadcast / five-video note: catalyst, order size, dividend, technicals.
- Conservative valuation bot: EPS × haircut PER, not raw consensus targets.
- Easing-vs-probability note: ceiling rank ≠ buy-now rank; fat left tails drop.

Official order is probability-weighted expected return over Sep–Dec 2026.

    PW = 0.35 × ease + 0.50 × base + 0.15 × hard

Quality (tie-break / conviction) is the requested five-factor score:

    0.35 vis + 0.25 value + 0.15 macro + 0.15 H2 catalyst + 0.10 flow

Hard rules: KOSPI only. DI / Simmtech / TLB stay out. Samsung E&A stays out
(faded rebuild). Hanmi is gated when trailing / forward multiples are extreme.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Mapping

from hybrid_synthesis.model import HybridSnapshot
from hybrid_synthesis.portfolio import Portfolio
from hybrid_synthesis.universe import by_ticker

H2_P_EASE = 0.35
H2_P_BASE = 0.50
H2_P_HARD = 0.15
YEAR_END_GAP = 0.65
BASE_GAP_SHARE = 0.35
HARD_SHOCK = -0.12
PE_GATE = 50.0

# Factor clusters used to stop double-counting Hynix via SK Square.
CLUSTER_SEMI = "SEMI"
CLUSTER_POWER = "POWER"
CLUSTER_FIN = "FIN"
CLUSTER_PLATFORM = "PLATFORM"
CLUSTER_AUTO = "AUTO"
CLUSTER_CONSUMER = "CONSUMER"
CLUSTER_AIR = "AIR"
CLUSTER_EPC = "EPC"


@dataclass(frozen=True)
class NameCard:
    ticker: str
    spot: float
    eps_2026e: float
    consensus_target: float
    conservative_multiple: float
    fair_value: float
    ease_ceiling: float
    left_tail: float
    fwd_pe: float
    cluster: str
    earnings_vis: float
    value_return: float
    macro_fit: float
    h2_catalyst: float
    flow: float
    trigger: str
    invalidation: tuple[str, ...]
    eligible: bool = True
    ineligible_reason: str = ""

    def __post_init__(self) -> None:
        if self.spot <= 0.0:
            raise ValueError(f"{self.ticker} spot must be positive")
        if self.fair_value <= 0.0 or self.ease_ceiling <= 0.0:
            raise ValueError(f"{self.ticker} targets must be positive")

    @property
    def quality(self) -> float:
        return (
            0.35 * self.earnings_vis
            + 0.25 * self.value_return
            + 0.15 * self.macro_fit
            + 0.15 * self.h2_catalyst
            + 0.10 * self.flow
        )

    @property
    def ease_return(self) -> float:
        return self.ease_ceiling / self.spot - 1.0

    @property
    def base_return(self) -> float:
        return BASE_GAP_SHARE * (self.fair_value / self.spot - 1.0)

    @property
    def hard_return(self) -> float:
        return HARD_SHOCK * self.left_tail

    @property
    def pw_return(self) -> float:
        return H2_P_EASE * self.ease_return + H2_P_BASE * self.base_return + H2_P_HARD * self.hard_return

    @property
    def yearend_target(self) -> float:
        return self.spot + YEAR_END_GAP * (self.fair_value - self.spot)

    @property
    def fair_upside(self) -> float:
        return self.fair_value / self.spot - 1.0

    def conviction(self) -> str:
        q = self.quality
        if q >= 78:
            return "A"
        if q >= 72:
            return "A-"
        if q >= 66:
            return "B+"
        if q >= 58:
            return "B"
        return "B-"


# 2026-09-03 KRX closes + FnGuide consensus, then haircut.
# Story names (Doosan, Air) cannot use a 15x EPS tape; ease_ceiling is the
# broadcast / mid-term target after a 0–30% haircut.
SNAPSHOTS: tuple[NameCard, ...] = (
    NameCard(
        "000660",
        1_596_000,
        349_342,
        3_279_565,
        6.6,
        2_300_000,
        2_300_000,
        1.00,
        4.62,
        CLUSTER_SEMI,
        92,
        88,
        62,
        90,
        70,
        "목표가 대비 보수 할인도 44%. NVL72 락인 + CXMT 역설 + FCF 흑자 전환.",
        ("HBM4 인증 지연", "DRAM 계약가 하향", "2027 OP 15% 이상 하향", "10년물 5% 장기 유지"),
    ),
    NameCard(
        "005930",
        250_000,
        48_339,
        487_045,
        6.6,
        320_000,
        320_000,
        0.90,
        5.18,
        CLUSTER_SEMI,
        86,
        90,
        70,
        88,
        95,
        "Fwd P/E 5.2배 + 4,000~4,800원 특별배당 우회 + ISA 1순위.",
        ("HBM4 양산 지연", "파운드리 적자 확대", "FCF 예상 하회", "원화 강세 이익 하향"),
    ),
    NameCard(
        "402340",
        981_000,
        341_357,
        1_938_333,
        3.9,
        1_330_000,
        1_330_000,
        1.25,
        2.87,
        CLUSTER_SEMI,
        74,
        84,
        55,
        72,
        58,
        "가장 싼 하이닉스 우회. NAV↑ → 매각/환원 → 지주 할인 축소.",
        ("하이닉스 실적 하향", "비상장 자회사 손상", "할인 확대"),
    ),
    NameCard(
        "071050",
        186_600,
        50_012,
        319_267,
        4.9,
        245_000,
        245_000,
        0.85,
        3.73,
        CLUSTER_FIN,
        80,
        92,
        68,
        64,
        62,
        "2026E EPS 5.0만 × 4.9배. 반도체와 상관 낮은 성장형 금융.",
        ("거래대금 급감", "PF/PI 손실", "신용비용 상승"),
    ),
    NameCard(
        "015760",
        32_450,
        6_355,
        50_667,
        6.5,
        41_300,
        41_300,
        0.85,
        5.11,
        CLUSTER_POWER,
        78,
        86,
        82,
        84,
        70,
        "삼성 20조+SK 5조 전기료 선납 + 원화 강세 연료비.",
        ("선납 딜 무산", "연료비 재급등", "요금 정치 리스크"),
    ),
    NameCard(
        "035420",
        207_500,
        12_519,
        325_783,
        21.2,
        265_000,
        265_000,
        1.00,
        16.57,
        CLUSTER_PLATFORM,
        70,
        76,
        72,
        68,
        66,
        "낮아진 플랫폼 멀티플. 금리 안정 시 가장 빠른 리레이팅.",
        ("AI 수익화 지연", "광고 회복 실패", "금리 재급등"),
    ),
    NameCard(
        "005935",
        184_100,
        48_339,
        0.0,
        4.76,
        230_400,
        230_400,
        0.70,
        3.81,
        CLUSTER_SEMI,
        82,
        88,
        68,
        80,
        55,
        "보통주 공정가치 32만의 72%. 특별배당 현금흐름 포착.",
        ("배당 서프라이즈 실종", "보통주 괴리 확대"),
    ),
    NameCard(
        "012330",
        423_500,
        45_720,
        735_200,
        11.5,
        525_000,
        525_000,
        0.85,
        9.26,
        CLUSTER_AUTO,
        76,
        84,
        60,
        58,
        64,
        "PBR 0.90 × BPS. 현대차보다 관세·인센티브 직접 노출이 작다.",
        ("A/S 둔화", "전장 투자 실패", "그룹 할인 고착"),
    ),
    NameCard(
        "034020",
        79_200,
        499,
        129_000,
        0.0,
        88_000,
        108_000,  # 완화 시나리오 +36% (방송 10만 + 텍사스 옵션). 기본 적정은 8.8만.
        1.85,
        158.7,
        CLUSTER_POWER,
        48,
        32,
        70,
        86,
        72,
        "텍사스 가스복합 $250억 가스터빈. 천장 10만, 왼쪽 꼬리 큼.",
        ("수주 확정 실패", "2026E PER 150배권 압축", "원전/가스터빈 일정 지연"),
    ),
    NameCard(
        "007660",
        106_000,
        3_712,
        176_667,
        35.0,
        130_000,
        130_000,
        1.40,
        28.56,
        CLUSTER_SEMI,
        72,
        58,
        55,
        80,
        52,
        "심텍·TLB의 코스피 대체. GPU→스위치 PCB→초고다층 MLB.",
        ("고객 집중", "램프업 지연", "30배 멀티플 압축"),
    ),
    NameCard(
        "267260",
        706_000,
        26_440,
        1_181_000,
        32.5,
        860_000,
        860_000,
        1.30,
        26.70,
        CLUSTER_POWER,
        84,
        54,
        62,
        74,
        60,
        "미 전력망·변압기 부족. 산업은 탑3, 가격은 이미 반영.",
        ("수주 둔화", "마진 피크아웃", "멀티플 압축"),
    ),
    NameCard(
        "028260",
        372_000,
        16_510,
        500_714,
        18.0,
        440_000,
        470_000,
        1.00,
        22.53,
        CLUSTER_EPC,
        74,
        68,
        64,
        78,
        62,
        "텍사스 EPC + 스웨덴 1.2GW 원전 4기 + 그룹 밸류업.",
        ("원전 일정 지연", "EPC 마진 훼손", "홀딩 할인 고착"),
    ),
    NameCard(
        "003490",
        29_150,
        909,
        36_700,
        0.0,
        34_500,
        36_700,
        0.70,
        32.07,
        CLUSTER_AIR,
        60,
        58,
        88,
        70,
        64,
        "유류할증 + 원화 강세 비용/부채 + 화물(화장품·장비).",
        ("화물 운임 급락", "유가 급등과 할증 시차", "여객 충격"),
    ),
    NameCard(
        "105560",
        177_900,
        18_392,
        224_889,
        11.4,
        210_000,
        210_000,
        0.70,
        9.67,
        CLUSTER_FIN,
        72,
        74,
        90,
        52,
        70,
        "원화 강세 → RWA↓ → BIS↑ → 환원. 전고점 추격 금지.",
        ("신용비용 상승", "전고점 추격", "금리 역전 장기화"),
    ),
    NameCard(
        "278470",
        406_000,
        15_750,
        534_737,
        31.4,
        495_000,
        495_000,
        1.60,
        25.78,
        CLUSTER_CONSUMER,
        78,
        42,
        48,
        70,
        50,
        "이익 성장은 콜마/코스맥스보다 강하나 PBR 18배권.",
        ("광고비 급증", "해외 성장 둔화", "디바이스 경쟁"),
    ),
    NameCard(
        "009150",
        1_348_000,
        19_852,
        2_350_500,
        40.0,
        1_455_840,
        1_455_840,
        1.50,
        67.90,
        CLUSTER_SEMI,
        76,
        28,
        52,
        82,
        68,
        "FC-BGA 매진. 다만 선행 PER 68배는 추가 확장 전제.",
        ("기판 가격 피크", "68배 멀티플 압축", "MLCC 역풍"),
    ),
    NameCard(
        "003230",
        1_424_000,
        75_108,
        1_856_429,
        20.0,
        1_502_000,
        1_502_000,
        0.90,
        18.96,
        CLUSTER_CONSUMER,
        80,
        40,
        74,
        56,
        48,
        "원화 강세=곡물 원가 하락 + K-푸드 수출. 이미 비싸다.",
        ("수출 둔화", "원가 재상승", "밸류 부담"),
    ),
    NameCard(
        "005180",
        92_000,
        0.0,
        120_000,
        0.0,
        105_000,
        110_000,
        0.90,
        0.0,
        CLUSTER_CONSUMER,
        68,
        52,
        72,
        50,
        40,
        "삼양과 같은 음식료 마진 스프레드. 2선.",
        ("내수 둔화", "원가 재상승"),
    ),
    NameCard(
        "161890",
        150_600,
        8_304,
        169_684,
        19.0,
        157_800,
        161_200,
        0.90,
        18.14,
        CLUSTER_CONSUMER,
        70,
        46,
        50,
        48,
        55,
        "목표가에 근접. 스윙만. 추격 금지.",
        ("수출 통계 꺾임", "ODM 단가 인하"),
    ),
    NameCard(
        "192820",
        282_000,
        14_920,
        298_778,
        20.0,
        298_400,
        298_400,
        0.90,
        18.90,
        CLUSTER_CONSUMER,
        68,
        44,
        50,
        46,
        52,
        "콜마와 같이 괴리 부족. 홀드·추격 금지.",
        ("수출 통계 꺾임", "중국 재악화"),
    ),
    NameCard(
        "042700",
        210_500,
        0.0,
        380_000,
        0.0,
        221_000,
        221_000,
        1.70,
        90.34,
        CLUSTER_SEMI,
        70,
        18,
        48,
        78,
        60,
        "HBM 본더 5년 사이클이나 PER 90·PBR 27. 탑10 게이트.",
        ("HBM 장비 피크", "멀티플 급압축"),
        eligible=False,
        ineligible_reason="선행/후행 멀티플이 게이트(50배)를 넘음",
    ),
    NameCard(
        "028050",
        46_100,
        3_777,
        68_600,
        15.1,
        57_000,
        57_000,
        1.20,
        12.21,
        CLUSTER_EPC,
        58,
        62,
        40,
        28,
        45,
        "중동 재건 모멘텀 소멸. 방송·완화 노트 모두 배제.",
        ("재건 테마 재점화 실패", "20일선 이탈"),
        eligible=False,
        ineligible_reason="faded_theme / 중동 재건 소멸",
    ),
)


BANNED_TICKERS = frozenset(
    {
        "222800",  # 심텍
        "356860",  # 티엘비
        "003160",  # 디아이
        "066970",
        "247540",
        "277810",
        "454910",
        "028050",
        "042700",
    }
)


def snapshots() -> tuple[NameCard, ...]:
    return SNAPSHOTS


def _existing_weights(portfolio: Portfolio | None) -> dict[str, float]:
    if portfolio is None:
        return {}
    return {item.ticker: item.weight_total for item in portfolio.holdings}


def _cluster_weight(weights: Mapping[str, float], cards: Mapping[str, NameCard], cluster: str) -> float:
    return sum(weight for ticker, weight in weights.items() if ticker in cards and cards[ticker].cluster == cluster)


@dataclass(frozen=True)
class RankedRow:
    rank: int
    card: NameCard
    name: str
    pw_return: float
    ease_return: float
    base_return: float
    hard_return: float
    fair_upside: float
    yearend_target: float
    quality: float
    conviction: str
    tier: str
    new_money_score: float
    existing_weight: float
    now_action: str

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self.card)
        payload.update(
            {
                "rank": self.rank,
                "name": self.name,
                "pw_return": self.pw_return,
                "ease_return": self.ease_return,
                "base_return": self.base_return,
                "hard_return": self.hard_return,
                "fair_upside": self.fair_upside,
                "yearend_target": self.yearend_target,
                "quality": self.quality,
                "conviction": self.conviction,
                "tier": self.tier,
                "new_money_score": self.new_money_score,
                "existing_weight": self.existing_weight,
                "now_action": self.now_action,
                "invalidation": list(self.card.invalidation),
            }
        )
        return payload


def _tier(pw: float) -> str:
    if pw >= 0.12:
        return "1"
    if pw >= 0.09:
        return "2"
    return "3"


def _now_action(card: NameCard, existing: float, pw_rank: int) -> str:
    if card.fwd_pe >= 40:
        return "관망 · 추격 금지"
    if card.cluster == CLUSTER_SEMI and existing >= 0.10:
        return "홀드 · 10월 전 확대 금지"
    if card.cluster == CLUSTER_SEMI and existing > 0:
        return "홀드 · 합산 한도 확인"
    if card.ticker == "034020":
        return "관망 · 고점 추격 금지"
    if card.ticker in {"161890", "192820"}:
        return "홀드 · 추격 금지"
    if pw_rank <= 3 and existing < 0.02:
        return "분할 매수 1순위"
    if card.cluster == CLUSTER_FIN:
        return "분할 · 전고점 추격 금지"
    return "분할 · 약한 조정"


def rank_h2(snapshot: HybridSnapshot | None = None, portfolio: Portfolio | None = None) -> dict[str, Any]:
    _ = snapshot
    cards = {card.ticker: card for card in SNAPSHOTS}
    existing = _existing_weights(portfolio)
    cluster_w = {
        cluster: _cluster_weight(existing, cards, cluster)
        for cluster in {card.cluster for card in SNAPSHOTS}
    }

    rows: list[RankedRow] = []
    eligible = [card for card in SNAPSHOTS if card.eligible and card.ticker not in BANNED_TICKERS]
    eligible.sort(key=lambda card: (-card.pw_return, -card.quality, card.ticker))

    for index, card in enumerate(eligible, start=1):
        own = existing.get(card.ticker, 0.0)
        penalty = 0.55 * own + 0.25 * cluster_w.get(card.cluster, 0.0)
        new_money = card.pw_return - penalty
        stock_name = by_ticker(card.ticker).name
        rows.append(
            RankedRow(
                rank=index,
                card=card,
                name=stock_name,
                pw_return=card.pw_return,
                ease_return=card.ease_return,
                base_return=card.base_return,
                hard_return=card.hard_return,
                fair_upside=card.fair_upside,
                yearend_target=card.yearend_target,
                quality=card.quality,
                conviction=card.conviction(),
                tier=_tier(card.pw_return),
                new_money_score=new_money,
                existing_weight=own,
                now_action=_now_action(card, own, index),
            )
        )

    top10 = rows[:10]
    ease_order = sorted(rows, key=lambda row: (-row.ease_return, -row.quality, row.card.ticker))
    new_money_order = sorted(rows, key=lambda row: (-row.new_money_score, -row.quality, row.card.ticker))
    dropped = [
        {
            "ticker": card.ticker,
            "name": by_ticker(card.ticker).name if card.ticker not in {"222800", "356860", "003160"} else card.ticker,
            "reason": card.ineligible_reason,
            "fwd_pe": card.fwd_pe,
        }
        for card in SNAPSHOTS
        if not card.eligible
    ]
    dropped.extend(
        [
            {"ticker": "222800", "name": "심텍", "reason": "코스닥. 이수페타시스·삼성전기로 치환", "fwd_pe": None},
            {"ticker": "356860", "name": "티엘비", "reason": "코스닥. 이수페타시스·코리아써키트로 치환", "fwd_pe": None},
            {"ticker": "003160", "name": "디아이", "reason": "코스닥. 한미반도체는 멀티플 게이트로 탈락", "fwd_pe": None},
            {"ticker": "298040", "name": "효성중공업", "reason": "산업은 맞지만 보수 목표가 대비 이미 비싼 구간", "fwd_pe": None},
            {"ticker": "066970", "name": "엘앤에프", "reason": "2차전지 소재. 이익 가시성 부족", "fwd_pe": None},
            {"ticker": "277810", "name": "레인보우로보틱스", "reason": "휴머노이드 테마. 상용화 전", "fwd_pe": None},
        ]
    )

    boxed_upside = [row.name for row in top10[:5]]
    boxed_new = [row.name for row in new_money_order[:5]]
    return {
        "as_of": "2026-09-03",
        "probs": {"ease": H2_P_EASE, "base": H2_P_BASE, "hard": H2_P_HARD},
        "formula": {
            "pw": "0.35*ease + 0.50*base + 0.15*hard",
            "quality": "0.35*vis + 0.25*value + 0.15*macro + 0.15*catalyst + 0.10*flow",
        },
        "top10": [row.to_dict() | {"name": row.name} for row in top10],
        "all_pw": [row.to_dict() | {"name": row.name} for row in rows],
        "ease_order": [{**row.to_dict(), "name": row.name, "rank": i} for i, row in enumerate(ease_order, start=1)],
        "new_money_order": [
            {**row.to_dict(), "name": row.name, "rank": i} for i, row in enumerate(new_money_order, start=1)
        ],
        "dropped": dropped,
        "boxed_upside": boxed_upside,
        "boxed_new_money": boxed_new,
        "rules": {
            "semi_plus_square_cap": "0.20~0.25 of total book",
            "semi_cluster_cap": "0.40~0.45 of total book",
            "core_satellite": "core 65% / satellite 35%",
            "split_buy": "30% now / 30% at -5~7% / 40% after PCE·oil or foreign cash+futures bid",
        },
    }
