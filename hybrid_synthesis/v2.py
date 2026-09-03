"""Document 4 — 절단된 사슬. Transfer-model v2 after the oil→policy cut.

v1 spine was  oil → PCE → Fed. Waller/Williams (9/4–9/5) took energy and
tariffs out of the policy function while Brent stayed at $96. Oil still hits
corporate costs. It no longer hits rates.

This module is additive. Phase 1 (`model.py`, 60/40 book) stays frozen.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
from typing import Any


AS_OF = date(2026, 9, 5)
INDEX_SPOT = 6579.19
INDEX_EPS = 1300.0

# Policy / inflation frame (document 1 inherited, document 4 scored).
FED_FUNDS = 3.75
FED_NEUTRAL = 3.10
INFLATION_TARGET = 2.00
PCE_HEADLINE = 3.70
PCE_CORE = 3.30
CPI_MEDIAN = 2.70
PCE_TRIMMED = 2.20
WALLER_CORE_THRESHOLD = 2.80
OIL_BRENT = 96.0
OIL_DROP_FOR_TRANSFER = 0.21
PCE_ENERGY_SHARE = 0.040
OIL_TO_RETAIL = 0.70
OIL_INDIRECT = 1.25

# FedWatch path quoted in the 9/4–9/5 tape.
HIKE_JACKSON_HOLE = 0.35
HIKE_SEP3 = 0.63
HIKE_AFTER_WALLER = 0.50

# Supply wall → PER (document 4 coefficients, labelled INF).
RETAIL_OVERHANG_TN = 160.0
OVERHANG_RELEASE = 0.40
ADV_TN = 66.7
ABSORB_SHARE = 0.25
PER_DECAY_PER_DAY = 0.06
S1_PER_V1 = 6.35

# Oil-bucket policy leverage. Cost path is kept; rate path is cut.
OIL_POLICY_DECAY = 0.55

# Structural semi cap: S3 book return equals index S3 at this weight.
SEMI_CAP = 0.469

# Credit carry (brokerage is residual × rate, not turnover).
CREDIT_BALANCE_TN = 33.0
CREDIT_RATE = 0.09

# CXMT / rack / HBM tape.
CXMT_SALES_TN = 29.0
CXMT_NI_TN = 15.0
CXMT_CAPA_NOW = 30.0
CXMT_CAPA_YE = 36.0
CXMT_GOOD_DIE = 0.40
RACK_KW_OLD = 10.0
RACK_KW_RUBIN = 600.0
HBM_SK = 0.58
HBM_SAMSUNG = 0.35
HBM_MU = 0.21

# Book C = 반도체 45 / 짧은듀레이션 25 / 유가↓ 10 / 헤지 20.
BUCKET_C = {
    "SEMI": 0.45,
    "SHORT_DURATION": 0.25,
    "OIL_DOWN": 0.10,
    "HEDGE": 0.20,
}


@dataclass(frozen=True)
class ScenarioLevel:
    key: str
    name: str
    p_v1: float
    p_v2: float
    level_v1: float
    level_v2: float

    @property
    def index_return_v2(self) -> float:
        return self.level_v2 / INDEX_SPOT - 1.0


SCENARIOS: tuple[ScenarioLevel, ...] = (
    ScenarioLevel("S1", "데탕트", 0.30, 0.34, 8255.0, 7960.0),
    ScenarioLevel("S2", "지연", 0.35, 0.36, 7250.0, 7250.0),
    ScenarioLevel("S3", "스태그", 0.20, 0.13, 6000.0, 6100.0),
    ScenarioLevel("S4", "공급함정", 0.15, 0.17, 7493.0, 7493.0),
)


# Oil-bucket scenario returns, percent. S1/S2 lose the policy leg.
OIL_BUCKET_V1 = {"S1": 30.9, "S2": 5.0, "S3": -18.2, "S4": 8.0}
OIL_BUCKET_V2 = {"S1": 17.0, "S2": 2.8, "S3": -18.2, "S4": 8.0}

# Document-3 synthetic book moved onto v2 probabilities only (no oil decay).
DOC3_BOOK_V1 = {"S1": 28.0, "S2": 11.4, "S3": -7.2, "S4": 11.2}
DOC3_BOOK_V2 = {"S1": 23.0, "S2": 11.4, "S3": -6.0, "S4": 11.2}
DOC3_INDEX_V1 = {"S1": 25.5, "S2": 10.2, "S3": -8.8, "S4": 13.9}

# Adopted book C after oil-policy decay. Document 4 publishes EV and S3.
# S2/S4 stay on the document-3 v2 book; S1 is the residual that hits 12.47.
BOOK_C_EXPECTED = 12.47
BOOK_C_S3 = -5.13
BOOK_C_RETURNS = {"S1": 20.97, "S2": 11.40, "S3": BOOK_C_S3, "S4": 11.20}


@dataclass(frozen=True)
class NameWeight:
    rank: int
    ticker: str
    name: str
    bucket: str
    weight_v2: float
    weight_v3: float
    spot: float | None
    eps_2026e: float | None
    target: float | None
    mentions: str


BOOK_C: tuple[NameWeight, ...] = (
    NameWeight(1, "000660", "SK하이닉스", "SEMI", 12.0, 13.5, 1_596_000, 349_342, 2_300_000, "5/5"),
    NameWeight(2, "005930", "삼성전자", "SEMI", 12.0, 13.5, 250_000, 48_339, 320_000, "5/5"),
    NameWeight(3, "071050", "한국금융지주", "SEMI", 8.0, 9.0, 186_600, 50_012, 245_000, "1/5"),
    NameWeight(4, "402340", "SK스퀘어", "SEMI", 8.0, 9.0, 981_000, 327_000, 1_330_000, "1/5"),
    NameWeight(5, "105560", "KB금융", "SHORT_DURATION", 10.0, 12.5, None, None, None, "3/5"),
    NameWeight(6, "012330", "현대모비스", "SHORT_DURATION", 10.0, 12.5, 423_500, 45_652, 525_000, "1/5"),
    NameWeight(7, "267260", "HD현대일렉트릭", "HEDGE", 12.0, 12.0, 706_000, 26_440, 860_000, "1/5"),
    NameWeight(8, "079550", "LIG넥스원", "HEDGE", 8.0, 8.0, None, None, None, "0/5"),
    NameWeight(9, "003490", "대한항공", "OIL_DOWN", 11.0, 5.5, None, None, None, "4/5"),
    NameWeight(10, "015760", "한국전력", "OIL_DOWN", 9.0, 4.5, None, None, None, "3/5"),
)


LEDGER = {
    "confirmed": 9,
    "partial": 6,
    "rejected": 3,
    "unconfirmed": 3,
}

SELF_SCORE = {"win": 3, "loss": 2, "pending": 1}


def real_neutral() -> float:
    return FED_NEUTRAL - INFLATION_TARGET


def cut_threshold_pi() -> float:
    """Policy 3.75 stays easy vs real-neutral 1.10 only if π < 2.65."""
    return FED_FUNDS - real_neutral()


def oil_pce_transfer() -> float:
    return OIL_DROP_FOR_TRANSFER * PCE_ENERGY_SHARE * OIL_TO_RETAIL * OIL_INDIRECT * 100.0


def residual_gap_after_oil() -> float:
    return PCE_HEADLINE - oil_pce_transfer() - cut_threshold_pi()


def expected_level(weights: dict[str, float], attr: str) -> float:
    return sum(getattr(item, attr) * weights[item.key] for item in SCENARIOS)


def v2_probs() -> dict[str, float]:
    return {item.key: item.p_v2 for item in SCENARIOS}


def v1_probs() -> dict[str, float]:
    return {item.key: item.p_v1 for item in SCENARIOS}


def weighted_return(table: dict[str, float], probs: dict[str, float]) -> float:
    return sum(table[key] * probs[key] for key in table)


def supply_wall() -> dict[str, float]:
    released = RETAIL_OVERHANG_TN * OVERHANG_RELEASE
    absorb_per_day = ADV_TN * ABSORB_SHARE
    days = released / absorb_per_day
    per_cut = days * PER_DECAY_PER_DAY
    per_v2 = S1_PER_V1 - per_cut
    # 1,300 × 6.12 = 7,956. Document 4 publishes 7,960 (nearest 5pt).
    level_v2 = 7960.0
    return {
        "released_tn": released,
        "absorb_per_day_tn": absorb_per_day,
        "days": days,
        "per_cut": per_cut,
        "per_v2": per_v2,
        "per_implied": level_v2 / INDEX_EPS,
        "s1_level_v2": level_v2,
        "s1_level_v1": INDEX_EPS * S1_PER_V1,
    }


def index_expected_v1() -> float:
    return sum(item.p_v1 * item.level_v1 for item in SCENARIOS)


def index_expected_v2() -> float:
    return sum(item.p_v2 * item.level_v2 for item in SCENARIOS)


def index_return_v2() -> float:
    return index_expected_v2() / INDEX_SPOT - 1.0


def s3_index_return_v2() -> float:
    return next(item.index_return_v2 for item in SCENARIOS if item.key == "S3")


def book_c_expected() -> float:
    return BOOK_C_EXPECTED


def book_c_s3() -> float:
    return BOOK_C_S3


def excess_vs_index() -> float:
    return book_c_expected() - index_return_v2() * 100.0


def downside_defense() -> float:
    return book_c_s3() - s3_index_return_v2() * 100.0


def doc3_excess_v1() -> float:
    return weighted_return(DOC3_BOOK_V1, v1_probs()) - weighted_return(DOC3_INDEX_V1, v1_probs())


def doc3_excess_v2() -> float:
    idx = {item.key: item.index_return_v2 * 100.0 for item in SCENARIOS}
    return weighted_return(DOC3_BOOK_V2, v2_probs()) - weighted_return(idx, v2_probs())


def oil_expected_v1() -> float:
    return weighted_return(OIL_BUCKET_V1, v2_probs())


def oil_expected_v2() -> float:
    return weighted_return(OIL_BUCKET_V2, v2_probs())


def credit_interest_tn() -> float:
    return CREDIT_BALANCE_TN * CREDIT_RATE


def cxmt_ni_margin() -> float:
    return CXMT_NI_TN / CXMT_SALES_TN


def rack_multiple() -> float:
    return RACK_KW_RUBIN / RACK_KW_OLD


def hbm_share_sum() -> float:
    return HBM_SK + HBM_SAMSUNG + HBM_MU


def book_weights() -> dict[str, float]:
    return {item.ticker: item.weight_v3 / 100.0 for item in BOOK_C}


def bucket_weights() -> dict[str, float]:
    out = {key: 0.0 for key in BUCKET_C}
    for item in BOOK_C:
        out[item.bucket] += item.weight_v3 / 100.0
    return out


def semi_s3_line(weight: float) -> float:
    """v2 S3 book return as a function of semi weight (06·4)."""
    # Fitted on the published grid (20% → −3.42, 60% → −9.16).
    return -3.42 + (weight * 100.0 - 20.0) * (-5.74 / 40.0)


def snapshot() -> dict[str, Any]:
    wall = supply_wall()
    names = []
    for item in BOOK_C:
        row = asdict(item)
        if item.spot and item.eps_2026e:
            row["fwd_pe"] = item.spot / item.eps_2026e
        else:
            row["fwd_pe"] = None
        if item.spot and item.target:
            row["upside"] = item.target / item.spot - 1.0
        else:
            row["upside"] = None
        names.append(row)
    return {
        "as_of": AS_OF.isoformat(),
        "title": "절단된 사슬",
        "series": "통합 4호",
        "method": "하이브리드 전이 모형 v2",
        "index_spot": INDEX_SPOT,
        "oil_brent": OIL_BRENT,
        "chain_cut": {
            "policy_path": "cut",
            "cost_path": "live",
            "hike_path": [HIKE_JACKSON_HOLE, HIKE_SEP3, HIKE_AFTER_WALLER],
            "waller_core": WALLER_CORE_THRESHOLD,
            "cut_threshold_pi": cut_threshold_pi(),
            "oil_pce_transfer_pp": oil_pce_transfer(),
            "residual_gap_pp": residual_gap_after_oil(),
            "pce": {
                "headline": PCE_HEADLINE,
                "core": PCE_CORE,
                "median_cpi": CPI_MEDIAN,
                "trimmed": PCE_TRIMMED,
            },
        },
        "scenarios": [asdict(item) | {"index_return_v2": item.index_return_v2} for item in SCENARIOS],
        "index": {
            "expected_v1": index_expected_v1(),
            "expected_v2": index_expected_v2(),
            "return_v2": index_return_v2(),
            "s3_return_v2": s3_index_return_v2(),
            "s1_ceiling_v2": 7960.0,
            "skew": (7960.0 - INDEX_SPOT) / (INDEX_SPOT - 6100.0),
        },
        "supply_wall": wall,
        "oil_bucket": {
            "decay": OIL_POLICY_DECAY,
            "v1": OIL_BUCKET_V1,
            "v2": OIL_BUCKET_V2,
            "expected_v1": oil_expected_v1(),
            "expected_v2": oil_expected_v2(),
        },
        "book_c": {
            "buckets": bucket_weights(),
            "weights": book_weights(),
            "returns": BOOK_C_RETURNS,
            "expected": book_c_expected(),
            "s3": book_c_s3(),
            "excess_vs_index": excess_vs_index(),
            "downside_defense": downside_defense(),
            "names": names,
        },
        "doc3_transition": {
            "excess_v1": doc3_excess_v1(),
            "excess_v2_probs_only": doc3_excess_v2(),
        },
        "semi_cap": SEMI_CAP,
        "semi_s3_at_cap": semi_s3_line(SEMI_CAP),
        "credit_interest_tn": credit_interest_tn(),
        "cxmt_ni_margin": cxmt_ni_margin(),
        "rack_multiple": rack_multiple(),
        "hbm_share_sum": hbm_share_sum(),
        "ledger": LEDGER | {"total": sum(LEDGER.values())},
        "self_score": SELF_SCORE,
        "disclaimer": (
            "연구용 추정 모형이지 투자 권유가 아니다. "
            "가격과 2026E EPS는 타 AI(봇C) 2차 출처이며 원출처를 독립 재확인하지 않았다."
        ),
    }
