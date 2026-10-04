"""패널 채점.

적중률 = (✓ + 0.5×△) / (✓+△+✗)
수축   = (N×적중률 + k×0.5) / (N+k),  k=4,  사전 확률은 동전 던지기 50%
종합   = 0.6×수축 적중률 + 0.25×(1층/5) + 0.15×(반증가능성/5)

화면의 정수 퍼센트는 파이썬 round(은행가 반올림)와 같다.
김민수 62.5% → 62, 김광석 종합 66.5 → 66.
"""

from __future__ import annotations

HIT_WEIGHT = 0.6
LAYER_WEIGHT = 0.25
FALS_WEIGHT = 0.15
SHRINK_K = 4.0
SHRINK_PRIOR = 0.5
LAYER_SCALE = 5.0
MAIN_MIN_N = 6
PARTIAL_CREDIT = 0.5


def hit_rate(hits: int, partials: int, misses: int) -> float:
    n = hits + partials + misses
    if n <= 0:
        raise ValueError("채점 완료 콜이 없다")
    if min(hits, partials, misses) < 0:
        raise ValueError("콜 건수는 음수가 될 수 없다")
    return (hits + PARTIAL_CREDIT * partials) / n


def shrink(rate: float, n: int, k: float = SHRINK_K, prior: float = SHRINK_PRIOR) -> float:
    if n < 0:
        raise ValueError("N은 음수가 될 수 없다")
    return (n * rate + k * prior) / (n + k)


def composite(
    rate: float,
    n: int,
    layer1: int | None,
    falsifiability: int | None,
) -> float | None:
    """1층 또는 반증가능성이 없으면 종합 점수를 만들지 않는다."""
    if layer1 is None or falsifiability is None:
        return None
    if not 1 <= layer1 <= 5 or not 1 <= falsifiability <= 5:
        raise ValueError("1층 정확도와 반증가능성은 1~5")
    shrunk = shrink(rate, n)
    return (
        HIT_WEIGHT * shrunk
        + LAYER_WEIGHT * (layer1 / LAYER_SCALE)
        + FALS_WEIGHT * (falsifiability / LAYER_SCALE)
    )


def display_points(score: float) -> int:
    """0~1 점수를 정수 퍼센트로. round 의 짝수 반올림을 그대로 쓴다."""
    return round(score * 100)
