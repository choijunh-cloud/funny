"""현대제철(004020) 2Q26 리포트 종합 — 모델별 장점 합성 목표주가."""

from __future__ import annotations

import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "estimates.json"


def load() -> dict:
    return json.loads(DATA_PATH.read_text(encoding="utf-8"))


def median(xs: list[float]) -> float:
    return float(statistics.median(xs))


def mean(xs: list[float]) -> float:
    return float(statistics.fmean(xs))


def trimmed(xs: list[float], drop_high: bool = False, drop_low: bool = False) -> float:
    vals = sorted(xs)
    if drop_high and len(vals) > 2:
        vals = vals[:-1]
    if drop_low and len(vals) > 2:
        vals = vals[1:]
    return mean(vals)


def per_share(krw_bn: float, shares: int) -> float:
    return krw_bn * 1_000_000_000 / shares


def compute(raw: dict) -> dict:
    meta = raw["meta"]
    brokers = raw["brokers"]
    shares = meta["shares"]
    price_report = meta["price_report"]
    price_latest = meta["price_latest"]

    def col(year: str, field: str) -> list[float]:
        return [b[year][field] for b in brokers]

    op_2026 = col("y2026", "op")
    op_2027 = col("y2027", "op")
    np_2026 = col("y2026", "np_ctrl")
    np_2027 = col("y2027", "np_ctrl")
    bps_2026 = col("y2026", "bps")
    bps_2027 = col("y2027", "bps")
    ebitda_2026 = col("y2026", "ebitda")
    nd_2026 = [b["y2026"]["net_debt"] for b in brokers]
    q3 = [b["q3_op"] for b in brokers]
    q4 = [b["q4_op"] for b in brokers]
    tps = [b["tp"] for b in brokers]

    # 실적: 아웃라이어를 제거한 절사평균
    blend_2026_op = trimmed(op_2026, drop_high=True)  # drop 하나 426.8
    blend_2027_op = trimmed(op_2027, drop_high=True)  # drop 대신 951
    blend_2026_np = trimmed(np_2026, drop_high=True, drop_low=True)  # drop 키움 159.5 / 한화 69
    blend_2027_np = trimmed(np_2027, drop_high=True)  # drop 대신 550
    blend_q3 = trimmed(q3, drop_high=True)  # drop iM 146
    blend_q4 = trimmed(q4, drop_high=True)  # drop 하나 237.9
    blend_2026_ebitda = median(ebitda_2026)
    blend_2026_nd = median(nd_2026)
    blend_2026_bps = median(bps_2026)
    blend_2027_bps = median(bps_2027)

    # 12mf BPS: 키움 암묵치, iM 명시, 연말 BPS 보간
    kiwoom = next(b for b in brokers if b["id"] == "kiwoom")
    im = next(b for b in brokers if b["id"] == "im")
    kiwoom_implied_bps = kiwoom["tp"] / kiwoom["target_pbr"]
    interpolated_bps = blend_2026_bps + (blend_2027_bps - blend_2026_bps) * (8 / 12)
    bps_12mf = mean([kiwoom_implied_bps, im["bps_used"], interpolated_bps])

    inv_per_share = per_share(meta["investment_assets_2025_krw_bn"], shares)
    steel_bps = bps_12mf - inv_per_share

    # --- 방법 A: 키움 프레임(12mf PBR) × iM 보수성(ROE 1.6%면 0.25x, 밸류업이면 0.30x)
    target_pbr = 0.28
    method_pbr = {
        "id": "pbr",
        "name": "12mf PBR",
        "source": "키움 프레임 + iM 배수 절충",
        "low": round(bps_12mf * 0.22),
        "mid": round(bps_12mf * target_pbr),
        "high": round(bps_12mf * 0.32),
        "weight": 0.35,
        "inputs": {
            "bps_12mf": round(bps_12mf),
            "target_pbr": target_pbr,
            "kiwoom_implied_bps": round(kiwoom_implied_bps),
            "im_bps": im["bps_used"],
            "interpolated_bps": round(interpolated_bps),
        },
        "note": "밸류업·저PBR 명단은 0.30x, 현재 ROE 1.6%는 0.25x. 촉매는 있으나 실적 회복은 더뎌 0.28x.",
    }

    # --- 방법 B: 대신 산식(선행 BPS × 피어조정 P/B), ROE 아웃라이어 제거
    method_peer = {
        "id": "peer_pbr",
        "name": "피어조정 PBR",
        "source": "대신 산식, 2027 ROE는 컨센 1.6% 사용",
        "low": round(blend_2027_bps * 0.22),
        "mid": round(blend_2027_bps * 0.28),
        "high": round(blend_2027_bps * 0.30),
        "weight": 0.0,
        "inputs": {
            "bps_2027e": round(blend_2027_bps),
            "peer_roe": 7.2,
            "peer_pbr": 0.7,
            "company_roe_daishin": 2.8,
            "company_roe_blend": 1.6,
            "mechanical_pbr": round(0.7 * (1.6 / 7.2), 3),
        },
        "note": "대신 공식 0.7×(ROE/7.2)는 순환업 저점에서 0.16x로 붕괴. 산식의 뼈대만 취하고 배수는 0.28x.",
    }

    # --- 방법 C: iM SOTP (모비스 시가 + 제철 장부 할인)
    steel_pbr = 0.17
    sotp_mid = inv_per_share + steel_bps * steel_pbr
    method_sotp = {
        "id": "sotp",
        "name": "SOTP",
        "source": "iM 모비스 지분 + 제철 장부",
        "low": round(inv_per_share + steel_bps * 0.12),
        "mid": round(sotp_mid),
        "high": round(inv_per_share + steel_bps * 0.22),
        "weight": 0.25,
        "inputs": {
            "investment_per_share": round(inv_per_share),
            "steel_bps": round(steel_bps),
            "steel_pbr": steel_pbr,
            "mobis_krw_bn": meta["mobis_stake_krw_bn"],
        },
        "note": "시총이 모비스 지분(2.7조)에 제철 본업을 거의 얹지 않는 구조를 분리 평가.",
    }

    # --- 방법 D: EV/EBITDA (미국 피어 7.1x는 배제, 국내 중기 6.2x)
    ev_multiple = 6.2
    equity_bn = blend_2026_ebitda * ev_multiple - blend_2026_nd
    ev_mid = per_share(equity_bn, shares)
    method_ev = {
        "id": "ev_ebitda",
        "name": "EV/EBITDA",
        "source": "국내 중기 배수, 미국 7.1x 배제",
        "low": round(per_share(blend_2026_ebitda * 5.5 - blend_2026_nd, shares)),
        "mid": round(ev_mid),
        "high": round(per_share(blend_2026_ebitda * 6.8 - blend_2026_nd, shares)),
        "weight": 0.15,
        "inputs": {
            "ebitda_2026e": blend_2026_ebitda,
            "net_debt_2026e": blend_2026_nd,
            "multiple": ev_multiple,
            "equity_krw_bn": round(equity_bn, 1),
        },
        "note": "미국 전기로 투자로 순차입금이 늘어 EV 방식은 가장 보수적. 가중치는 낮춤.",
    }

    # --- 방법 E: 2Q 정확도·산식 투명도로 증권사 TP 재가중
    broker_weighted = sum(b["tp"] * b["weight_broker"] for b in brokers)
    method_broker = {
        "id": "broker_qw",
        "name": "증권사 품질가중",
        "source": "2Q 추정 정확도 + 산식 공개 여부",
        "low": min(tps),
        "mid": round(broker_weighted),
        "high": max(tps),
        "weight": 0.25,
        "inputs": {
            "simple_avg": round(mean(tps)),
            "simple_median": round(median(tps)),
            "fnguide": meta["fnguide_consensus_tp"],
            "weights": {b["name"]: b["weight_broker"] for b in brokers},
        },
        "note": "한화·iM에 가중(추정 정확 / 유일한 하향). 하나 5만원은 가중 축소.",
    }

    methods = [method_pbr, method_peer, method_sotp, method_ev, method_broker]
    weighted_tp = sum(m["mid"] * m["weight"] for m in methods)
    target = int(round(weighted_tp / 1000.0) * 1000)

    scenarios = [
        {
            "id": "bear",
            "name": "약세",
            "prob": 0.20,
            "tp": 28000,
            "pbr": 0.185,
            "thesis": "중국 수출 재확대, 차강판·후판 인상 실패, 밸류업이 선언에 그침",
        },
        {
            "id": "base",
            "name": "기본",
            "prob": 0.55,
            "tp": target,
            "pbr": round(target / bps_12mf, 3),
            "thesis": "3Q부터 고로 스프레드 회복, 3~4Q 주주환원 윤곽, PBR 0.28x 재평가",
        },
        {
            "id": "bull",
            "name": "강세",
            "prob": 0.25,
            "tp": 50000,
            "pbr": 0.33,
            "thesis": "밸류업+자사주, 3Q 서프라이즈, AIDC·팹 물량 가시화. 하나 TP와 수렴",
        },
    ]
    expected = sum(s["tp"] * s["prob"] for s in scenarios)

    q_path = {
        "labels": ["1Q26", "2Q26", "3Q26E", "4Q26E"],
        "actual_or_blend": [15.7, 57.7, round(blend_q3, 1), round(blend_q4, 1)],
        "brokers": {
            b["name"]: [None, 57.7, b["q3_op"], b["q4_op"]] for b in brokers
        },
    }

    return {
        "meta": {
            **meta,
            "market_cap_latest_bn": round(price_latest * shares / 1e8, 0),
            "pbr_latest_12mf": round(price_latest / bps_12mf, 3),
            "pbr_report_12mf": round(price_report / bps_12mf, 3),
            "pbr_latest_2025": round(price_latest / meta["bps_2025a"], 3),
        },
        "blend": {
            "q3_op": round(blend_q3, 1),
            "q4_op": round(blend_q4, 1),
            "fy26_op": round(blend_2026_op, 1),
            "fy26_op_from_quarters": round(15.7 + 57.7 + blend_q3 + blend_q4, 1),
            "fy27_op": round(blend_2027_op, 1),
            "fy26_np": round(blend_2026_np, 1),
            "fy27_np": round(blend_2027_np, 1),
            "fy26_eps": round(per_share(blend_2026_np, shares)),
            "fy27_eps": round(per_share(blend_2027_np, shares)),
            "fy26_bps": round(blend_2026_bps),
            "fy27_bps": round(blend_2027_bps),
            "bps_12mf": round(bps_12mf),
            "fy26_ebitda": blend_2026_ebitda,
            "fy26_nd": blend_2026_nd,
            "fy26_op_street": sorted(op_2026),
            "fy27_op_street": sorted(op_2027),
        },
        "methods": methods,
        "target": {
            "tp": target,
            "raw_weighted": round(weighted_tp),
            "expected_value": round(expected),
            "upside_vs_latest": round((target / price_latest - 1) * 100, 1),
            "upside_vs_report": round((target / price_report - 1) * 100, 1),
            "rating": "BUY",
            "target_pbr": round(target / bps_12mf, 3),
            "div_yield": round(meta["dps_2026e"] / price_latest * 100, 2),
        },
        "scenarios": scenarios,
        "q_path": q_path,
        "brokers": brokers,
        "actual_2q26": raw["actual_2q26"],
        "consensus_2q26": raw["consensus_2q26"],
    }


if __name__ == "__main__":
    result = compute(load())
    out = ROOT / "output" / "valuation.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    t = result["target"]
    print(f"TP {t['tp']:,}  BUY  +{t['upside_vs_latest']}% vs {result['meta']['price_latest']:,}")
    print(f"12mf BPS {result['blend']['bps_12mf']:,}  target PBR {t['target_pbr']}")
    for m in result["methods"]:
        print(f"  {m['name']:16} {m['mid']:6,}  ({m['low']:,}–{m['high']:,})  w={m['weight']}")
