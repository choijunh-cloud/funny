"""시나리오 확률.

v1.0 (2026-08-29) A55 / B20 / C25 에서 출발한다.
v1.1 은 아래에 적힌 네 가지 코어를 10/2 종가에 대입한 결과이고, 그 합이 A50 / B20 / C30 이다.

  조건① 10Y 5.28        A −3  C +3
  외인 9월 −20조        A −3  C +3
  마이크론 호재 소진    B −2  C +2
  10월 인상 확률 급락   A +1  B +2  C −3
  ─────────────────────────────────
  합                    A −5  B  0  C +5

감시 규칙은 10/2 종가에서 강도가 0이다. 폭은 13번 칸의 방향을 확률로 옮긴 모델 가정이고,
조건②만 문서의 폭(C를 15%p 올려 30→45)을 그대로 쓴다. 그 15%p는 A에서 가져온다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Callable

from hybrid_model.market import Market

PRIOR_VERSION = "1.0"
PRIOR_ASOF = date(2026, 8, 29)
MODEL_VERSION = "1.1"
PRIOR: dict[str, float] = {"A": 55.0, "B": 20.0, "C": 25.0}
CODES = ("A", "B", "C")


def ramp_up(value: float, low: float, high: float) -> float:
    """low 이하 0, high 이상 1, 그 사이 선형."""
    if value <= low:
        return 0.0
    if value >= high:
        return 1.0
    return (value - low) / (high - low)


def ramp_down(value: float, zero_at: float, one_at: float) -> float:
    """zero_at 이상 0, one_at 이하 1. one_at < zero_at."""
    if value >= zero_at:
        return 0.0
    if value <= one_at:
        return 1.0
    return (zero_at - value) / (zero_at - one_at)


def intensity_cond1(market: Market) -> float:
    # 5.00 이하는 0, 10/2 종가 5.28 에서 1. 장중 고점은 쓰지 않는다.
    return ramp_up(market.us10y, 5.0, 5.28)


def intensity_foreign_month(market: Market) -> float:
    # −10조에서 0, −20조 이하에서 1.
    return ramp_down(market.foreign_month_tn, zero_at=-10.0, one_at=-20.0)


def intensity_micron(market: Market) -> float:
    if not market.micron_beat or market.micron_reaction_pct >= 0:
        return 0.0
    return ramp_up(abs(market.micron_reaction_pct), 0.0, 3.0)


def intensity_oct_hike(market: Market) -> float:
    # 40%에서 0, 22% 이하에서 1. 스냅샷 19%(16~22%의 중간)는 만점.
    return ramp_down(market.oct_hike_prob, zero_at=0.40, one_at=0.22)


def intensity_cond2(market: Market) -> float:
    # 조건①이 살아 있고 근원 CPI MoM 이 0.2 를 넘을 때만. ≤0.2 는 반증.
    if market.core_cpi_mom is None or market.us10y < 5.0:
        return 0.0
    return 1.0 if market.core_cpi_mom > 0.2 else 0.0


def intensity_week_positive(market: Market) -> float:
    return 1.0 if market.foreign_week_tn > 0 else 0.0


def intensity_week_deep(market: Market) -> float:
    return 1.0 if market.foreign_week_tn <= -10 else 0.0


def intensity_y10_below(market: Market) -> float:
    return 1.0 if market.us10y < 5.0 else 0.0


def intensity_y10_sticky(market: Market) -> float:
    return 1.0 if market.us10y >= 5.30 else 0.0


def intensity_samsung_surprise(market: Market) -> float:
    if market.samsung_op_tn is None:
        return 0.0
    return 1.0 if market.samsung_op_tn >= 115 else 0.0


def intensity_samsung_inline(market: Market) -> float:
    op = market.samsung_op_tn
    reaction = market.samsung_reaction_pct
    if op is None or reaction is None:
        return 0.0
    return 1.0 if 110 <= op < 115 and reaction < 0 else 0.0


def intensity_weekly_break(market: Market) -> float:
    if market.weekly_close is None:
        return 0.0
    return 1.0 if market.weekly_close >= 7200 else 0.0


def intensity_below_6562(market: Market) -> float:
    return 1.0 if 6100 < market.kospi < 6562 else 0.0


def intensity_park_sell(market: Market) -> float:
    return 1.0 if market.kospi <= 6100 else 0.0


def intensity_brent_reopen(market: Market) -> float:
    return 1.0 if market.brent < 90 else 0.0


def intensity_brent_hot(market: Market) -> float:
    return 1.0 if market.brent > 110 else 0.0


@dataclass(frozen=True)
class Factor:
    id: str
    tier: str
    title: str
    shift: tuple[tuple[str, float], ...]
    intensity: Callable[[Market], float]
    explain: Callable[[Market], str]


def _pct(prob: float) -> str:
    return f"{prob * 100:.0f}%"


FACTORS: tuple[Factor, ...] = (
    Factor(
        "euntaek_cond1",
        "core",
        "이은택 조건①",
        (("A", -3), ("C", 3)),
        intensity_cond1,
        lambda m: f"10Y 종가 {m.us10y:.2f}%. 5.00 이하는 0, 5.28 이상에서 강도 1",
    ),
    Factor(
        "foreign_september",
        "core",
        "외인 9월 순매도",
        (("A", -3), ("C", 3)),
        intensity_foreign_month,
        lambda m: f"월간 {m.foreign_month_tn:.1f}조. −10조에서 0, −20조 이하에서 1",
    ),
    Factor(
        "micron_exhaustion",
        "core",
        "마이크론 호재 소진",
        (("B", -2), ("C", 2)),
        intensity_micron,
        lambda m: (
            f"가이던스 ${m.micron_guide_bn:.1f}B {'상회' if m.micron_beat else '미달'}, "
            f"주가 {m.micron_reaction_pct:+.1f}%. −3%에서 강도 1"
        ),
    ),
    Factor(
        "oct_hike_plunge",
        "core",
        "10월 인상 확률 급락",
        (("A", 1), ("B", 2), ("C", -3)),
        intensity_oct_hike,
        lambda m: f"10월 인상 {_pct(m.oct_hike_prob)} (스냅샷 구간 16~22의 중간). 22% 이하에서 완화 만점",
    ),
    Factor(
        "euntaek_cond2",
        "watch",
        "이은택 조건② 노웨이백",
        (("A", -15), ("C", 15)),
        intensity_cond2,
        lambda m: "근원 CPI MoM > 0.2 이고 조건①이 켜져 있으면 C를 15%p 올린다. 15%p는 A에서 가져온다",
    ),
    Factor(
        "foreign_week_positive",
        "watch",
        "외인 주간 순매수 전환",
        (("A", -10), ("B", 10)),
        intensity_week_positive,
        lambda m: f"주간 {m.foreign_week_tn:.2f}조. 플러스면 수급 공백론을 기각하고 A→B",
    ),
    Factor(
        "foreign_week_deep",
        "watch",
        "외인 주간 −10조",
        (("A", -5), ("C", 5)),
        intensity_week_deep,
        lambda m: f"주간 {m.foreign_week_tn:.2f}조. −10조 이하면 C",
    ),
    Factor(
        "y10_below_5",
        "watch",
        "10Y 5.0% 하회",
        (("C", -5), ("B", 5)),
        intensity_y10_below,
        lambda m: f"10Y {m.us10y:.2f}%. 5.0 아래는 B 지지",
    ),
    Factor(
        "y10_sticky_53",
        "watch",
        "10Y 5.3% 고착",
        (("A", -3), ("C", 3)),
        intensity_y10_sticky,
        lambda m: f"10Y 종가 {m.us10y:.2f}%. 5.30 이상이면 조건① 위에 고착을 한 번 더 얹는다. 장중 고점은 제외",
    ),
    Factor(
        "samsung_surprise",
        "watch",
        "삼성 3Q 서프라이즈",
        (("A", -8), ("B", 8)),
        intensity_samsung_surprise,
        lambda m: "영업이익 115조 이상이면 B",
    ),
    Factor(
        "samsung_inline_sold",
        "watch",
        "삼성 3Q 인라인 후 하락",
        (("A", -5), ("C", 5)),
        intensity_samsung_inline,
        lambda m: "110조대이고 주가가 빠지면 매도 재료 소진 → C",
    ),
    Factor(
        "weekly_break_7200",
        "watch",
        "7,200 주봉 종가",
        (("A", -15), ("C", -5), ("B", 20)),
        intensity_weekly_break,
        lambda m: "주봉 종가 7,200 안착이면 상단 규칙이 깨지고 B. 일중 종가만으로는 켜지지 않는다",
    ),
    Factor(
        "kospi_below_6562",
        "watch",
        "6,562 이탈",
        (("A", -10), ("B", -5), ("C", 15)),
        intensity_below_6562,
        lambda m: "종가가 6,562 아래, 6,100 위면 C",
    ),
    Factor(
        "kospi_park_6100",
        "watch",
        "박병창 매도 트리거",
        (("A", -10), ("B", -5), ("C", 15)),
        intensity_park_sell,
        lambda m: "종가 6,100 이하면 이탈 매도. 6,562 규칙과 겹치지 않게 이 규칙만 켠다",
    ),
    Factor(
        "brent_reopen",
        "watch",
        "호르무즈 재개",
        (("A", -5), ("B", 5)),
        intensity_brent_reopen,
        lambda m: f"브렌트 {m.brent:.0f}. 90 아래면 B",
    ),
    Factor(
        "brent_hot",
        "watch",
        "브렌트 110 상회",
        (("A", -5), ("C", 5)),
        intensity_brent_hot,
        lambda m: f"브렌트 {m.brent:.0f}. 110 위면 헤드라인 물가 재점화 → C",
    ),
)


def _validate_factors() -> None:
    ids = [factor.id for factor in FACTORS]
    if len(ids) != len(set(ids)):
        raise ValueError("요인 id 가 겹친다")
    for factor in FACTORS:
        if factor.tier not in {"core", "watch"}:
            raise ValueError(factor.id)
        total = sum(value for _, value in factor.shift)
        if abs(total) > 1e-9:
            raise ValueError(f"{factor.id} 이동 합이 0이 아니다")
        for code, _ in factor.shift:
            if code not in PRIOR:
                raise ValueError(factor.id)


_validate_factors()


@dataclass(frozen=True)
class AppliedFactor:
    id: str
    tier: str
    title: str
    intensity: float
    delta: tuple[tuple[str, float], ...]
    explain: str

    @property
    def active(self) -> bool:
        return self.intensity > 1e-12


@dataclass(frozen=True)
class Posterior:
    prior_version: str
    version: str
    prior: tuple[tuple[str, float], ...]
    weights: tuple[tuple[str, float], ...]
    factors: tuple[AppliedFactor, ...]
    clipped: bool

    def weight(self, code: str) -> float:
        return dict(self.weights)[code]

    def as_dict(self) -> dict[str, float]:
        return dict(self.weights)


def normalize_weights(raw: dict[str, float]) -> tuple[dict[str, float], bool]:
    clipped = False
    floored: dict[str, float] = {}
    for code in CODES:
        value = raw[code]
        if value < 0:
            clipped = True
            floored[code] = 0.0
        else:
            floored[code] = value
    total = sum(floored.values())
    if total <= 0:
        raise ValueError("시나리오 가중치가 모두 0 이하다")
    return {code: floored[code] * 100.0 / total for code in CODES}, clipped


def compute_posterior(market: Market) -> Posterior:
    raw = dict(PRIOR)
    applied: list[AppliedFactor] = []
    for factor in FACTORS:
        intensity = float(factor.intensity(market))
        if intensity < -1e-9 or intensity > 1 + 1e-9:
            raise ValueError(f"{factor.id} 강도가 0~1 밖이다: {intensity}")
        intensity = min(1.0, max(0.0, intensity))
        delta = {code: 0.0 for code in CODES}
        for code, value in factor.shift:
            delta[code] += value * intensity
        for code in CODES:
            raw[code] += delta[code]
        applied.append(
            AppliedFactor(
                id=factor.id,
                tier=factor.tier,
                title=factor.title,
                intensity=intensity,
                delta=tuple((code, delta[code]) for code in CODES),
                explain=factor.explain(market),
            )
        )
    weights, clipped = normalize_weights(raw)
    return Posterior(
        prior_version=PRIOR_VERSION,
        version=MODEL_VERSION,
        prior=tuple((code, PRIOR[code]) for code in CODES),
        weights=tuple((code, weights[code]) for code in CODES),
        factors=tuple(applied),
        clipped=clipped,
    )


@dataclass(frozen=True)
class PathBand:
    label: str
    low: float
    high: float

    @property
    def mid(self) -> float:
        return (self.low + self.high) / 2


@dataclass(frozen=True)
class Scenario:
    code: str
    title: str
    panels: tuple[str, ...]
    trigger: str
    paths: tuple[PathBand, ...]


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        "A",
        "바통터치 지연 → 박스 후 연말 재도전",
        ("박근형", "황유현", "박현상", "이영훈", "알상무", "박병창"),
        "자사주 소진 후 외인 매도가 이어지고 삼성 3Q가 인라인이면, 10월 중순 6,700~6,850을 본 뒤 연말 7,100~7,500을 다시 본다.",
        (
            PathBand("10월", 6700, 7150),
            PathBand("11월", 6800, 7300),
            PathBand("12월", 7000, 7500),
        ),
    ),
    Scenario(
        "B",
        "조기 점화 — 7,200 주봉 돌파",
        ("이영수", "김장열", "박현상", "강건우"),
        "삼성 3Q 115조 이상, 외인 주간 순매수, 10Y 5.0% 복귀, 브렌트 90 아래가 겹치면 주봉 7,200을 돌파한다.",
        (
            PathBand("10월", 6950, 7350),
            PathBand("11월", 7100, 7500),
            PathBand("12월", 7300, 7800),
        ),
    ),
    Scenario(
        "C",
        "두 번째 파도 — 자본 공급자가 멈춤",
        ("이은택", "김학균", "알상무", "박병창"),
        "근원 CPI 재가속과 10Y 5.3 고착, 외인 월 20조 매도가 이어지고 6,562가 깨지면 하단 사다리로 내려간다.",
        (
            PathBand("10월", 6300, 6850),
            PathBand("11월", 6100, 6700),
            PathBand("12월", 6000, 6800),
        ),
    ),
)


def market_flags(market: Market) -> tuple[str, ...]:
    flags: list[str] = []
    if market.usdkrw < 1320:
        flags.append("원달러 1,320 하회 — 수출주 4Q 추정 하향 경계(강건우). 확률은 이동하지 않는다.")
    if market.us10y < 5.30 <= market.us10y_intraday_high:
        flags.append(
            f"10Y 장중 {market.us10y_intraday_high:.2f}%는 5.3을 넘었으나 종가 {market.us10y:.2f}%라 고착 규칙은 꺼져 있다."
        )
    if (
        market.dec_hike_prob is not None
        and market.dec_hike_prob < 0.5
        and market.us10y < 5.0
    ):
        flags.append("10Y 5.0% 하회와 12월 인상 확률 50% 미만 — 매크로 축 반증 조건.")
    return tuple(flags)
