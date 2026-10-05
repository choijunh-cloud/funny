# -*- coding: utf-8 -*-
"""코스피 일간 변동성에 몬테카를로를 맞추고, 8/6~10/2로 확인한 뒤 연말을 전망한다.

보정 구간은 2026-08-05까지다. 8/6~10/2는 맞춘 뒤에만 본다.
최근 60일 평균 수익이 0과 구분되지 않으면 전망의 기본 드리프트는 0이다.
"""

from __future__ import annotations

import math
from datetime import date
from pathlib import Path

import numpy as np

from hybrid_model.montecarlo import S0, run, summarize

DATA = Path(__file__).resolve().parents[1] / "data" / "ks11.csv"
TRAIN_END = date(2026, 8, 5)
TEST_END = date(2026, 10, 2)
LOOKBACK = 60
# 분산 1로 맞춘 t(5) 의 5%·95%. 시드 0, 표본 400만으로 고정.
Z05 = -1.5585
Z95 = 1.5596


def load_prices(path: Path = DATA) -> tuple[np.ndarray, np.ndarray]:
    days: list[date] = []
    closes: list[float] = []
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        if not line.strip():
            continue
        stamp, close = line.split(",")
        days.append(date.fromisoformat(stamp))
        closes.append(float(close))
    return np.array(days), np.array(closes, dtype=float)


def _binom_p(hits: int, n: int, p0: float) -> float:
    se = math.sqrt(n * p0 * (1.0 - p0))
    z = (abs(hits - n * p0) - 0.5) / se
    return math.erfc(z / math.sqrt(2.0))


def _coverage(logret: np.ndarray, start: int, end: int, scale: float) -> tuple[int, int]:
    hits = 0
    count = 0
    for i in range(start, end):
        window = logret[i - LOOKBACK : i]
        sig = scale * float(window.std(ddof=1))
        mean = float(window.mean())
        lo = mean + sig * Z05
        hi = mean + sig * Z95
        hits += int(lo <= logret[i] <= hi)
        count += 1
    return hits, count


def fit_vol_scale(logret: np.ndarray, train_end_index: int) -> float:
    """직전 60일 표준편차에 곱을 붙여, 훈련 구간의 하루 90% 구간 적중을 90%에 맞춘다."""
    best_k = 1.0
    best_gap = 1.0
    for k in np.linspace(0.8, 1.6, 33):
        hits, count = _coverage(logret, LOOKBACK, train_end_index, float(k))
        gap = abs(hits / count - 0.90)
        if gap < best_gap:
            best_gap = gap
            best_k = float(k)
    return best_k


def diffuse(start: float, steps: int, sig: float, drift: float, n: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    shock = rng.standard_t(5, size=(steps, n)) / math.sqrt(5 / 3)
    logs = drift - 0.5 * sig ** 2 + sig * shock
    return start * np.exp(logs.sum(axis=0))


def _t_stat(window: np.ndarray) -> float:
    return float(window.mean() / (window.std(ddof=1) / math.sqrt(len(window))))


def evaluate() -> dict:
    days, closes = load_prices()
    logret = np.diff(np.log(closes))
    # logret[i] 는 closes[i] -> closes[i+1]
    train_last = int(np.where(days <= TRAIN_END)[0][-1])
    # 훈련에 쓰는 마지막 수익률의 도착일이 8/5 이전이어야 한다.
    train_ret_end = train_last  # logret index 상한(미포함) = train_last, 도착일 days[train_last]
    scale = fit_vol_scale(logret, train_ret_end)
    train_hits, train_n = _coverage(logret, LOOKBACK, train_ret_end, scale)
    raw_hits, _ = _coverage(logret, LOOKBACK, train_ret_end, 1.0)
    test_idx = [i for i in range(train_ret_end, len(logret)) if days[i + 1] <= TEST_END]
    test_hits = 0
    old_hits = 0
    for i in test_idx:
        window = logret[i - LOOKBACK : i]
        sig = scale * float(window.std(ddof=1))
        mean = float(window.mean())
        if mean + sig * Z05 <= logret[i] <= mean + sig * Z95:
            test_hits += 1
        if -0.5 * (0.015 ** 2) + 0.015 * Z05 <= logret[i] <= -0.5 * (0.015 ** 2) + 0.015 * Z95:
            old_hits += 1
    test_n = len(test_idx)

    start_price = float(closes[train_last])
    steps = int(np.where(days <= TEST_END)[0][-1] - train_last)
    realized = float(closes[np.where(days <= TEST_END)[0][-1]])
    train_returns = logret[np.where(days[1:] >= date(2026, 1, 2))[0][0] : train_ret_end]
    sig_train = float(train_returns.std(ddof=1))
    mean_train = float(train_returns.mean())
    drift_train = mean_train + 0.5 * sig_train ** 2

    old_end = diffuse(start_price, steps, 0.015, 0.0, 12000, 42)
    cal_end = diffuse(start_price, steps, scale * sig_train, drift_train, 12000, 42)
    flat_end = diffuse(start_price, steps, scale * sig_train, 0.0, 12000, 42)

    def band(samples: np.ndarray) -> dict:
        pct = float((samples <= realized).mean() * 100)
        return dict(
            p05=float(np.percentile(samples, 5)),
            p50=float(np.percentile(samples, 50)),
            p95=float(np.percentile(samples, 95)),
            pct=pct,
            inside=5.0 <= pct <= 95.0,
        )

    recent = logret[-LOOKBACK:]
    sig_now = float(recent.std(ddof=1))
    mean_now = float(recent.mean())
    t_now = _t_stat(recent)
    # 양측 정규근사. |t|<1.96 이면 드리프트는 0.
    use_drift = abs(t_now) >= 1.96
    forecast_sig = scale * sig_now
    forecast_drift = (mean_now + 0.5 * forecast_sig ** 2) if use_drift else 0.0
    # 8/5→8/6 급락은 빼고, 8/6 종가 이후만 최근 국면으로 본다.
    calm = logret[train_ret_end + 1 :]
    sig_calm = float(calm.std(ddof=1))
    t_calm = _t_stat(calm)
    calm_sig = scale * sig_calm
    calm_drift = (float(calm.mean()) + 0.5 * calm_sig ** 2) if abs(t_calm) >= 1.96 else 0.0

    return dict(
        scale=scale,
        train_coverage=train_hits / train_n,
        train_raw_coverage=raw_hits / train_n,
        train_n=train_n,
        train_p=_binom_p(train_hits, train_n, 0.90),
        test_coverage=test_hits / test_n,
        test_old_coverage=old_hits / test_n,
        test_n=test_n,
        test_p=_binom_p(test_hits, test_n, 0.90),
        test_old_p=_binom_p(old_hits, test_n, 0.90),
        holdout_start=start_price,
        holdout_end=realized,
        holdout_steps=steps,
        sig_train=sig_train,
        old_band=band(old_end),
        cal_band=band(cal_end),
        flat_band=band(flat_end),
        sig_now=sig_now,
        t_now=t_now,
        forecast_sig=forecast_sig,
        forecast_drift=forecast_drift,
        use_drift=use_drift,
        calm_sig=calm_sig,
        calm_drift=calm_drift,
        t_calm=t_calm,
        sig_calm=sig_calm,
    )


def _binom_p(hits: int, n: int, p0: float) -> float:
    se = math.sqrt(n * p0 * (1.0 - p0))
    z = (abs(hits - n * p0) - 0.5) / se
    return math.erfc(z / math.sqrt(2.0))


def forecast(n: int = 20000, seed: int = 42) -> dict:
    fit = evaluate()
    calibrated = summarize(
        run(n=n, seed=seed, base_vol=fit["forecast_sig"], base_drift=fit["forecast_drift"])
    )
    calm = summarize(run(n=n, seed=seed, base_vol=fit["calm_sig"], base_drift=fit["calm_drift"]))
    original = summarize(run(n=n, seed=seed))
    return dict(fit=fit, calibrated=calibrated, calm=calm, original=original)


def format_forecast(result: dict) -> str:
    fit = result["fit"]
    old = result["original"]
    new = result["calibrated"]
    lines = [
        "보정 백테스트 후 전망  ·  코스피 현물 ^KS11  ·  훈련 ~2026-08-05  ·  확인 2026-08-06~10-02",
        f"하루 90% 구간을 맞추는 변동성 배수 {fit['scale']:.2f}",
        f"훈련 적중 {fit['train_coverage']*100:.1f}% (보정 전 {fit['train_raw_coverage']*100:.1f}%)",
        f"확인 적중 {fit['test_coverage']*100:.1f}%  ·  예전 1.5% 변동성 적중 {fit['test_old_coverage']*100:.1f}%",
        f"8/5 {fit['holdout_start']:,.0f} → 10/2 {fit['holdout_end']:,.0f} ({fit['holdout_steps']}영업일)",
        f"  예전 엔진 5/50/95% {fit['old_band']['p05']:,.0f} / {fit['old_band']['p50']:,.0f} / {fit['old_band']['p95']:,.0f}"
        f"  실제 위치 {fit['old_band']['pct']:.0f}%tile  구간 안 {fit['old_band']['inside']}",
        f"  보정 엔진 5/50/95% {fit['cal_band']['p05']:,.0f} / {fit['cal_band']['p50']:,.0f} / {fit['cal_band']['p95']:,.0f}"
        f"  실제 위치 {fit['cal_band']['pct']:.0f}%tile  구간 안 {fit['cal_band']['inside']}",
        f"최근 60일(7/7~) 변동성 {fit['sig_now']*100:.2f}%/일  t={fit['t_now']:.2f}  "
        f"전망 변동성 {fit['forecast_sig']*100:.2f}%/일  기본 드리프트 {fit['forecast_drift']*100:.3f}%/일",
        f"폭락 이후(8/6~10/2) 변동성 {fit['sig_calm']*100:.2f}%/일  t={fit['t_calm']:.2f}  "
        f"적용 {fit['calm_sig']*100:.2f}%/일",
        "",
        "연말 전망 (모듈 유지)",
        f"  보정 전 1.5%  중앙 {old['p50']:,.0f}  5% {old['p5']:,.0f}  95% {old['p95']:,.0f}  "
        f"6,800 아래 {old['C']:.0f}%  7,300 위 {old['B']:.0f}%",
        f"  최근 60일 변동성  중앙 {new['p50']:,.0f}  5% {new['p5']:,.0f}  95% {new['p95']:,.0f}  "
        f"6,800 아래 {new['C']:.0f}%  7,300 위 {new['B']:.0f}%  10/30 {new['oct50']:,.0f}",
        f"  8월 이후 변동성  중앙 {result['calm']['p50']:,.0f}  5% {result['calm']['p5']:,.0f}  95% {result['calm']['p95']:,.0f}  "
        f"6,800 아래 {result['calm']['C']:.0f}%  7,300 위 {result['calm']['B']:.0f}%  "
        f"6,562 이탈 {result['calm']['lt6562']:.0f}%",
    ]
    return "\n".join(lines) + "\n"


def main() -> dict:
    result = forecast()
    print(format_forecast(result), end="")
    return result


if __name__ == "__main__":
    main()
