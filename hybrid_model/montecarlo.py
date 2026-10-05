# -*- coding: utf-8 -*-
"""패널 장점 모듈 결합 몬테카를로 — 2026-10-06 ~ 12-30 KOSPI 일간.

모든 파라미터는 MODEL(추론). 각 모듈은 채점에서 살아남은 패널의 층이다.
기본 경로는 2만 개, 시드는 42.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
import numpy as np

S0 = 7003.74
HOLIDAYS = {date(2026, 10, 9), date(2026, 12, 25), date(2026, 12, 31)}
START = date(2026, 10, 6)
END = date(2026, 12, 30)

# v2 영향력(P-only). 0은 그 이름으로는 가중을 주지 않는다. 노근창은 실적 모듈의 자리만 둔다.
W = {
    "박근형": 12.9, "황유현": 9.0, "강건우": 9.0, "이건규": 9.0, "박현상": 8.8,
    "박병창": 8.3, "이영수": 8.0, "홍춘욱": 8.0, "김장열": 4.5, "이영훈": 4.4,
    "윤지호": 4.0, "김민수": 2.9, "김학균": 2.9, "문홍철": 2.9, "이건희": 2.9,
    "김중손": 2.9, "이진호": 0.0, "이은택": 0.0, "한지영": 0.0, "알상무": 0.0, "노근창": 0.0,
}

MODULES = {
    "flow": dict(name="수급 — 자사주 방파제·외인 레짐", panels=["이영훈", "윤지호", "김민수", "박현상", "김학균"]),
    "level": dict(name="레벨 — 7,100~7,500 저항·7,200 주봉 게이트·6,300~6,400 지지", panels=["박병창", "황유현", "이진호", "박현상"]),
    "rate": dict(name="연준·금리 속도 — 인상=해소·10Y 5일 변화", panels=["박근형", "홍춘욱", "강건우", "이건규", "한지영"]),
    "earn": dict(name="실적 — 삼성 10/8·하닉 10/28·호재 소진", panels=["김장열", "이영수", "노근창", "이건규", "박근형"]),
    "tail": dict(name="꼬리 — 이은택 2조건 AND·바닥 장치 소멸", panels=["이은택", "김학균"]),
    "season": dict(name="계절성 — 10월 조심·미드텀 후 강세", panels=["알상무", "강건우"]),
}


def trading_days(start: date = START, end: date = END) -> list[date]:
    days: list[date] = []
    cursor = start
    while cursor <= end:
        if cursor.weekday() < 5 and cursor not in HOLIDAYS:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


DAYS = trading_days()
T = len(DAYS)
INDEX = {day: i for i, day in enumerate(DAYS)}
FRIDAYS = [i for i, day in enumerate(DAYS) if day.weekday() == 4]


def di(month: int, day: int) -> int:
    stamp = date(2026, month, day)
    try:
        return INDEX[stamp]
    except KeyError as exc:
        raise KeyError(f"{stamp} 는 이 시뮬의 영업일이 아니다") from exc


EVENTS = dict(
    ss_end=di(10, 8),
    ss_q3=di(10, 8),
    cpi=di(10, 15),
    bok=di(10, 22),
    hx_q3=di(10, 28),
    fomc1=di(10, 29),
    midterm=di(11, 4),
    nfp=di(11, 9),
    fomc2=di(12, 10),
    oct_last=di(10, 30),
    dec1=di(12, 1),
    nov_last=di(11, 30),
)

for module in MODULES.values():
    module["w"] = sum(W.get(name, 0.0) for name in module["panels"])
_WMEAN = float(np.mean([module["w"] for module in MODULES.values()]))
for module in MODULES.values():
    module["scale_w"] = float(np.clip(module["w"] / _WMEAN, 0.5, 1.5))


def run(
    n: int = 20000,
    seed: int = 42,
    on: dict[str, bool] | None = None,
    scale: dict[str, float] | None = None,
    base_vol: float = 0.015,
    base_drift: float = 0.0,
) -> dict:
    """일간 경로 n개. on 이 False 인 모듈은 그날의 드리프트에서 뺀다."""
    enabled = on or {key: True for key in MODULES}
    strength = scale or {key: 1.0 for key in MODULES}
    rng = np.random.default_rng(seed)
    price = np.full(n, S0)
    y10 = np.full(n, 5.28)
    yield_hist = np.zeros((T + 5, n))
    yield_hist[:5] = 5.28
    path = np.zeros((T, n))

    hx_rate = rng.uniform(0.40, 0.65, n) * 1.84
    hx_left = np.full(n, 10.52)
    ss_left = np.full(n, 0.86)
    draw = rng.random(n)
    samsung_op = np.where(
        draw < 0.20,
        rng.normal(103, 3, n),
        np.where(draw < 0.90, rng.normal(110, 4, n), rng.normal(125, 6, n)),
    )
    hynix_surprise = rng.normal(0.0, 0.05, n)
    cpi_draw = rng.random(n)
    cpi_hot = cpi_draw < 0.35
    cpi_cool = cpi_draw > 0.80
    hike_oct = rng.random(n) < 0.16
    hike_dec = rng.random(n) < np.where(cpi_hot, 0.85, 0.60)
    mid_shock = rng.normal(0, 0.012, n)
    foreign = np.where(rng.random(n) < 0.75, -1, 0)
    broken = np.zeros(n, dtype=bool)
    stress = np.zeros(n, dtype=int)
    stress_hit = np.zeros(n, dtype=bool)
    above_count = np.zeros(n, dtype=int)
    hx_end_day = np.full(n, -1)
    foreign_level = {-1: -1.0, 0: -0.2, 1: 0.6}
    flow_lambda = 0.0020 * strength["flow"]

    for t in range(T):
        drift = np.full(n, base_drift)
        vol = np.full(n, base_vol)
        buyback = np.zeros(n)
        if enabled["flow"]:
            if t <= EVENTS["ss_end"]:
                take = np.minimum(ss_left, 0.43)
                buyback += take
                ss_left -= take
            take = np.minimum(hx_left, hx_rate)
            buyback += take
            hx_left -= take
            just_ended = (hx_left <= 1e-9) & (hx_end_day < 0)
            hx_end_day[just_ended] = t
            foreign_value = np.select(
                [foreign == -1, foreign == 0, foreign == 1],
                [foreign_level[-1], foreign_level[0], foreign_level[1]],
            )
            drift += flow_lambda * (buyback + foreign_value + 0.5)
            post = (hx_end_day >= 0) & (t > hx_end_day)
            p_up = np.where(post, 0.05, 0.025)
            p_up = p_up * np.where(samsung_op > 116, 2.5, 1.0)
            p_up = p_up * np.where(t > EVENTS["ss_q3"], 1.0, 0.6)
            p_up = np.where(stress > 0, 0.005, p_up)
            p_down = np.where(stress > 0, 0.30, 0.03)
            coin = rng.random(n)
            foreign = np.where((foreign == -1) & (coin < p_up), 0, foreign)
            foreign = np.where(
                (foreign == 0) & (coin < p_up * 1.2),
                1,
                np.where((foreign == 0) & (coin > 1 - p_down), -1, foreign),
            )
            foreign = np.where((foreign == 1) & (coin > 1 - p_down * 1.3), 0, foreign)
            if enabled["tail"]:
                vol = np.where(buyback > 0.3, vol * 0.92, vol * (1 + 0.08 * strength["tail"]))

        dy = rng.normal(0, 0.055, n)
        if t == EVENTS["cpi"]:
            dy = dy + np.where(cpi_hot, 0.12, np.where(cpi_cool, -0.10, 0.0))
        if t == EVENTS["fomc1"]:
            dy = dy + np.where(hike_oct, 0.05, -0.03)
        if t == EVENTS["nfp"]:
            dy = dy + rng.normal(0, 0.06, n)
        if t == EVENTS["fomc2"]:
            dy = dy + np.where(hike_dec, 0.02, -0.06)
        y10 = y10 + dy
        yield_hist[t + 5] = y10
        if enabled["rate"]:
            speed = y10 - yield_hist[t]
            drift = drift - 3.0 * strength["rate"] * np.maximum(0, speed - 0.10) / 100
            drift = drift + 3.0 * strength["rate"] * np.maximum(0, -speed - 0.10) / 100 * 0.5
            if t == EVENTS["fomc1"]:
                drift = drift + strength["rate"] * np.where(hike_oct, np.where(cpi_hot, -0.010, 0.005), 0.002)
            if t == EVENTS["fomc2"]:
                drift = drift + strength["rate"] * np.where(hike_dec, np.where(cpi_hot, -0.006, 0.003), 0.004)
            if t == EVENTS["cpi"]:
                drift = drift + strength["rate"] * np.where(cpi_hot, -0.010, np.where(cpi_cool, 0.008, 0.0))

        if enabled["earn"] and t == EVENTS["ss_q3"]:
            surprise = (samsung_op - 112) / 112
            drift = drift + strength["earn"] * (np.clip(0.30 * surprise, -0.04, 0.04) - 0.006)
        if enabled["earn"] and t == EVENTS["hx_q3"]:
            drift = drift + strength["earn"] * (np.clip(0.20 * hynix_surprise, -0.03, 0.03) - 0.004)

        if enabled["tail"]:
            above_count = np.where(y10 > 5.30, above_count + 1, 0)
            trigger = (~stress_hit) & cpi_hot & (t >= EVENTS["cpi"]) & (above_count >= 8)
            stress = np.where(trigger, 25, stress)
            stress_hit = stress_hit | trigger
            active = stress > 0
            drift = drift - np.where(active, 0.0012 * strength["tail"], 0)
            vol = np.where(active, vol * (1 + 0.5 * strength["tail"]), vol)
            if enabled["flow"]:
                foreign = np.where(trigger, -1, foreign)
            stress = np.maximum(stress - 1, 0)

        if enabled["season"]:
            if t < EVENTS["midterm"]:
                drift = drift - 0.0003 * strength["season"]
                vol = vol * (1 - 0.08 * strength["season"])
            else:
                drift = drift + 0.0006 * strength["season"]
            if t == EVENTS["midterm"]:
                drift = drift + mid_shock * strength["season"]

        if enabled["level"]:
            pull = 0.25 * strength["level"]
            resist = (~broken) & (price > 7100)
            drift = drift - np.where(resist, pull * (price - 7100) / 7100, 0)
            resist_high = broken & (price > 7800)
            drift = drift - np.where(resist_high, 0.10 * strength["level"] * (price - 7800) / 7800, 0)
            support = (price < 6400) & (stress == 0)
            drift = drift + np.where(support, 0.20 * strength["level"] * (6400 - price) / 6400, 0)

        shock = rng.standard_t(5, n) / np.sqrt(5 / 3)
        price = price * np.exp(drift - 0.5 * vol ** 2 + vol * shock)
        path[t] = price
        if enabled["level"] and t in FRIDAYS:
            if enabled["flow"]:
                broken = broken | ((price > 7200) & (foreign == 1))
            else:
                broken = broken | (price > 7200)

    return dict(
        path=path,
        ss_op=samsung_op,
        cpi_hot=cpi_hot,
        cpi_cool=cpi_cool,
        hike1=hike_oct,
        hike2=hike_dec,
        stress_hit=stress_hit,
        broken=broken,
        hx_end_day=hx_end_day,
        y10=y10,
        Fend=foreign,
    )


def _pct(values: np.ndarray, q: float) -> float:
    return float(np.percentile(values, q))


def summarize(result: dict) -> dict:
    path = result["path"]
    end = path[-1]
    low = path.min(0)
    friday = path[FRIDAYS]
    hx = result["hx_end_day"]
    hx_done = hx[hx >= 0]
    return dict(
        p5=_pct(end, 5),
        p25=_pct(end, 25),
        p50=_pct(end, 50),
        p75=_pct(end, 75),
        p95=_pct(end, 95),
        mean=float(end.mean()),
        oct50=_pct(path[EVENTS["oct_last"]], 50),
        nov50=_pct(path[EVENTS["nov_last"]], 50),
        up=float((end > S0).mean() * 100),
        A=float(((end >= 6800) & (end <= 7300)).mean() * 100),
        B=float((end > 7300).mean() * 100),
        C=float((end < 6800).mean() * 100),
        touch7200=float((friday.max(0) > 7200).mean() * 100),
        brk=float(result["broken"].mean() * 100),
        lt6562=float((low < 6562).mean() * 100),
        lt6100=float((low < 6100).mean() * 100),
        stress=float(result["stress_hit"].mean() * 100),
        halloween=float((path[EVENTS["oct_last"]] > 6788.88).mean() * 100),
        oct_dd=float(np.percentile(path[: EVENTS["oct_last"] + 1].min(0) / S0 - 1, 50) * 100),
        hx_end=float(np.median(hx_done)) if hx_done.size else -1.0,
    )


def _mask_stats(path: np.ndarray, mask: np.ndarray) -> dict:
    end = path[-1]
    october = path[EVENTS["oct_last"]]
    return dict(
        n=int(mask.sum()),
        oct=float(np.median(october[mask])),
        end=float(np.median(end[mask])),
        up=float((end[mask] > S0).mean() * 100),
        c=float((end[mask] < 6800).mean() * 100),
    )


def conditionals(result: dict) -> dict[str, dict]:
    path = result["path"]
    op = result["ss_op"]
    groups = {
        "삼성 3Q <105조": op < 105,
        "105~115조": (op >= 105) & (op < 115),
        "115~120조": (op >= 115) & (op < 120),
        "≥120조": op >= 120,
        "CPI 과열(35%)": result["cpi_hot"],
        "CPI 중립(45%)": ~result["cpi_hot"] & ~result["cpi_cool"],
        "CPI 둔화(20%)": result["cpi_cool"],
        "이은택 스트레스 발동": result["stress_hit"],
        "스트레스 미발동": ~result["stress_hit"],
        "외인 연말 매수": result["Fend"] == 1,
        "외인 연말 매도": result["Fend"] == -1,
    }
    return {name: _mask_stats(path, mask) for name, mask in groups.items()}


def strategies(result: dict) -> dict[str, dict]:
    path = result["path"]
    n = path.shape[1]
    returns: dict[str, np.ndarray] = {}
    returns["보유 100%"] = path[-1] / S0 - 1

    position = np.ones(n)
    cash = np.zeros(n)
    levels = (7100, 7300, 7500)
    sold = np.zeros((3, n), dtype=bool)
    stopped = np.zeros(n, dtype=bool)
    for t in range(path.shape[0]):
        for i, level in enumerate(levels):
            hit = (~sold[i]) & (path[t] >= level) & (~stopped)
            cash = cash + np.where(hit, (1 / 3) * path[t] / S0, 0)
            position = position - np.where(hit, 1 / 3, 0)
            sold[i] = sold[i] | hit
        exit_all = (~stopped) & (path[t] <= 6100)
        cash = cash + np.where(exit_all, position * path[t] / S0, 0)
        position = np.where(exit_all, 0, position)
        stopped = stopped | exit_all
    returns["박병창 레벨 분할매도"] = position * path[-1] / S0 + cash - 1

    hx = result["hx_end_day"]
    entry = np.where(hx >= 0, np.minimum(hx + 5, EVENTS["dec1"]), EVENTS["dec1"])
    entry_price = path[entry, np.arange(n)]
    returns["수급 확인 후 2차 진입(50+50)"] = 0.5 * (path[-1] / S0 - 1) + 0.5 * (path[-1] / entry_price - 1)

    touched = path <= 6562
    first = np.where(touched.any(0), touched.argmax(0), -1)
    add_price = np.where(first >= 0, path[np.maximum(first, 0), np.arange(n)], np.nan)
    add_return = np.where(first >= 0, 0.15 * (path[-1] / add_price - 1), 0.0)
    returns["알상무 현금 30%·6,562에 15% 추가"] = 0.70 * (path[-1] / S0 - 1) + add_return

    running_max = np.maximum.accumulate(np.vstack([np.full(n, S0), path]), axis=0)[1:]
    drawdown = (path / running_max - 1).min(0)
    table = {}
    for name, series in returns.items():
        table[name] = dict(
            mean=float(series.mean() * 100),
            p50=float(np.median(series) * 100),
            p5=float(np.percentile(series, 5) * 100),
            p95=float(np.percentile(series, 95) * 100),
            loss5=float((series < -0.05).mean() * 100),
        )
    table["보유 최대낙폭 중앙"] = dict(p50=float(np.median(drawdown) * 100))
    return table


def study(n: int = 20000, seed: int = 42) -> dict:
    """기준, 영향력 가중, 모듈을 하나씩 뺀 경우, 모듈을 전부 끈 경우를 같이 돌린다."""
    base_run = run(n=n, seed=seed)
    base = summarize(base_run)
    weighted = summarize(run(n=n, seed=seed, scale={key: MODULES[key]["scale_w"] for key in MODULES}))
    ablation = {}
    for key in MODULES:
        flags = {other: other != key for other in MODULES}
        ablation[key] = summarize(run(n=n, seed=seed, on=flags))
    naive = summarize(run(n=n, seed=seed, on={key: False for key in MODULES}))
    seeds = [summarize(run(n=max(n // 2, 1000), seed=extra))["p50"] for extra in (1, 7, 99, 2026)]
    return dict(
        base=base,
        weighted=weighted,
        ablation=ablation,
        naive=naive,
        seeds=seeds,
        cond=conditionals(base_run),
        strat=strategies(base_run),
        modules={
            key: dict(name=module["name"], panels=module["panels"], w=module["w"], scale_w=module["scale_w"])
            for key, module in MODULES.items()
        },
    )


def _round_dict(row: dict, digits: int = 1) -> dict:
    return {key: round(value, digits) if isinstance(value, float) else value for key, value in row.items()}


def format_study(result: dict) -> str:
    base = result["base"]
    lines = [
        "몬테카를로  2026-10-06~12-30  ·  2만 경로  ·  시드 42  ·  파라미터는 MODEL",
        f"영업일 {T}일  ·  출발 {S0:,.2f}",
        "",
        "12/30 분포 (기준, 모듈 강도 1)",
        f"  5% {base['p5']:,.0f}   25% {base['p25']:,.0f}   중앙 {base['p50']:,.0f}   "
        f"75% {base['p75']:,.0f}   95% {base['p95']:,.0f}   평균 {base['mean']:,.0f}",
        f"  10/30 중앙 {base['oct50']:,.0f}   11/30 중앙 {base['nov50']:,.0f}   "
        f"출발 위 {base['up']:.1f}%",
        f"  연말 6,800~7,300 {base['A']:.1f}%   7,300 위 {base['B']:.1f}%   6,800 아래 {base['C']:.1f}%",
        f"  주봉 7,200 터치 {base['touch7200']:.1f}%   게이트 돌파 {base['brk']:.1f}%   "
        f"6,562 이탈 {base['lt6562']:.1f}%   6,100 이탈 {base['lt6100']:.1f}%",
        f"  이은택 스트레스 {base['stress']:.1f}%   할로윈(10/30>6,788.88) {base['halloween']:.1f}%   "
        f"10월 낙폭 중앙 {base['oct_dd']:.1f}%   하닉 소진 중앙 {DAYS[int(round(base['hx_end']))].isoformat()}",
        "",
        "영향력 가중 (모듈 합이 평균의 0.5~1.5배)",
    ]
    weighted = result["weighted"]
    lines.append(
        f"  중앙 {weighted['p50']:,.0f}   6,800 아래 {weighted['C']:.1f}%   7,300 위 {weighted['B']:.1f}%   "
        f"6,562 이탈 {weighted['lt6562']:.1f}%"
    )
    lines.append("")
    lines.append("모듈을 하나 뺐을 때 중앙값 변화 (기준 대비)")
    for key, row in result["ablation"].items():
        lines.append(
            f"  {MODULES[key]['name']}: 중앙 {row['p50'] - base['p50']:+,.0f}   "
            f"6,800 아래 {row['C'] - base['C']:+.1f}%p   6,562 이탈 {row['lt6562'] - base['lt6562']:+.1f}%p"
        )
    naive = result["naive"]
    lines.append(f"  모듈 전부 끔: 중앙 {naive['p50']:,.0f} (기준 {base['p50']:,.0f})")
    lines.append("시드 1·7·99·2026 중앙값 " + " ".join(f"{value:,.0f}" for value in result["seeds"]))
    lines.append("")
    lines.append("조건부 연말 중앙")
    for name, row in result["cond"].items():
        lines.append(
            f"  {name}: n={row['n']}  10/30 {row['oct']:,.0f}  12/30 {row['end']:,.0f}  "
            f"상승 {row['up']:.0f}%  6,800 아래 {row['c']:.0f}%"
        )
    lines.append("")
    lines.append("같은 경로 위의 매매 규칙, 수익률 %")
    for name, row in result["strat"].items():
        if "mean" not in row:
            lines.append(f"  {name}: 중앙 {row['p50']:.1f}%")
            continue
        lines.append(
            f"  {name}: 평균 {row['mean']:.1f}  중앙 {row['p50']:.1f}  "
            f"5% {row['p5']:.1f}  95% {row['p95']:.1f}  −5% 이하 {row['loss5']:.0f}%"
        )
    return "\n".join(lines) + "\n"


def main(n: int = 20000, out: str | None = None) -> dict:
    result = study(n=n)
    text = format_study(result)
    print(text, end="")
    if out:
        payload = json.loads(json.dumps(result))
        with open(out, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=1)
    return result


if __name__ == "__main__":
    main()
