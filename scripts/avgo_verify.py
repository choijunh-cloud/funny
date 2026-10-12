#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent arithmetic check of avgo_valuation.py.

Recomputes WACC, scenario EPS, probability-weighted target, Gordon DCF and SOTP
from the inputs. Does not call the model's dcf()/build() for the headline figures.
Hypothesis tests (IDENT/CALIB/TEST) are reported, not treated as engine failures.
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import avgo_valuation as m

ART = Path("/opt/cursor/artifacts")
ART.mkdir(parents=True, exist_ok=True)
LOG = ART / "avgo_verification.log"


class Fail(Exception):
    pass


failures: list[str] = []


def check(name: str, cond: bool, detail: str) -> None:
    status = "PASS" if cond else "FAIL"
    line = f"[{status}] {name} — {detail}"
    print(line)
    if not cond:
        failures.append(line)


def close(a: float, b: float, tol: float = 1e-6) -> bool:
    return abs(a - b) <= tol


def hand_path(nonai0: float, sw0: float, nonai_g: float, sw_g: list[float], ai: list[float], opm: list[float]):
    nonai, sw = nonai0, sw0
    rows = []
    prev = m.FACT["fy25"]["rev"]
    for i, year in enumerate(m.YEARS):
        if i:
            nonai *= 1 + nonai_g
            sw *= 1 + sw_g[i - 1]
        rev = ai[i] + nonai + sw
        oi = rev * opm[i]
        sbc = m.SBC_PATH[i]
        nopat = (oi - sbc) * (1 - m.TAX)
        dnwc = m.NWC_RATE * (rev - prev)
        ufcf = nopat + m.DEP_PATH[i] - m.CAPEX_PATH[i] - dnwc
        ni = (oi - m.NET_INT[i]) * (1 - m.TAX)
        eps = ni / m.FACT["dil_shares"]
        rep = ufcf + sbc * (1 - m.TAX) - m.NET_INT[i] * (1 - m.TAX)
        rows.append(dict(year=year, rev=rev, ai=ai[i], nonai=nonai, sw=sw, oi=oi, sbc=sbc,
                         nopat=nopat, dnwc=dnwc, ufcf=ufcf, ni=ni, eps=eps, rep_fcf=rep, opm=opm[i]))
        prev = rev
    return rows


def hand_dcf(rows, r, g=0.03, tv_lag=0.5):
    stub = 0.06
    pv = 0.0
    details = []
    for i, row in enumerate(rows):
        if i == 0:
            cf, t = row["ufcf"] * stub, stub / 2
        else:
            cf, t = row["ufcf"], stub + (i - 1) + 0.5
        df = (1 + r) ** (-t)
        pv += cf * df
        details.append((cf, t, df))
    tN = details[-1][1] + tv_lag
    tv = rows[-1]["ufcf"] * (1 + g) / (r - g)
    pv_tv = tv * (1 + r) ** (-tN)
    ev = pv + pv_tv
    eq = ev - (m.FACT["debt_principal"] - m.FACT["cash"])
    return dict(ev=ev, pv=pv, pv_tv=pv_tv, tv_share=pv_tv / ev, equity=eq,
                value_ps=eq / m.FACT["dil_shares"], tN=tN, tv=tv)


def main() -> int:
    out = m.run_model()
    price = m.FACT["price"]
    shares = m.FACT["dil_shares"]

    # ── 입력 항등 ──
    fy26_rev = sum(m.FACT["fy26_q"]["rev"])
    fy26_ai = sum(m.FACT["fy26_q"]["ai"])
    fy26_sw = sum(m.FACT["fy26_q"]["sw"])
    check("FY26 매출 분기합", close(fy26_rev, 19.311 + 22.187 + 29.591 + 34.8), f"{fy26_rev:.3f}")
    check("FY26 AI 분기합", close(fy26_ai, 57.6), f"{fy26_ai:.1f}")
    check("FY26 소프트웨어 분기합", close(fy26_sw, 31.426, 1e-9), f"{fy26_sw:.3f}")
    check("FY26 매출 vs 컨센 0.5B", abs(fy26_rev - m.CONS["fy26_rev"]) < 0.5, f"{fy26_rev:.2f} vs {m.CONS['fy26_rev']}")
    q_fcf = m.FACT["fy26_q"]["fcf"]
    check("9M FCF = 8.010+10.262+13.665", close(sum(q_fcf[:3]), 31.937), f"{sum(q_fcf[:3]):.3f}")
    check("시나리오 확률 합", close(sum(s["p"] for s in m.SCEN.values()), 1.0), f"{sum(s['p'] for s in m.SCEN.values())}")
    check("공통팩터 가중", close(0.6 ** 2 + 0.8 ** 2, 1.0), "0.36+0.64")
    check("순부채 원금−현금", close(m.NET_DEBT, 61.079 - 23.975), f"{m.NET_DEBT:.3f}")

    # ── WACC, 모델 함수를 쓰지 않고 ──
    beta_blume = round(0.67 * 1.48 + 0.33, 2)
    check("Blume 베타", beta_blume == 1.32, f"{beta_blume}")
    coe_raw = 0.0524 + 1.48 * 0.0420
    coe_base = 0.0524 + beta_blume * 0.0420
    E = price * shares
    D = 61.079
    kd = 0.062 * (1 - 0.16)
    w_raw = coe_raw * E / (E + D) + kd * D / (E + D)
    w_base = coe_base * E / (E + D) + kd * D / (E + D)
    check("WACC raw", close(w_raw, out["wacc"]["raw"]["wacc"]), f"hand {w_raw:.6%} model {out['wacc']['raw']['wacc']:.6%}")
    check("WACC base", close(w_base, out["wacc"]["base"]["wacc"]), f"hand {w_base:.6%} model {out['wacc']['base']['wacc']:.6%}")
    check("CoE raw", close(coe_raw, 0.11456), f"{coe_raw:.5%}")

    # ── 시나리오 EPS·목표가, build()를 다시 구현 ──
    hand = {}
    for name, s in m.SCEN.items():
        rows = hand_path(16.8, 31.43, s["nonai_g"], s["sw_g"], s["ai"], s["opm"])
        tp = s["pe"] * rows[2]["eps"]
        hand[name] = dict(rows=rows, tp=tp, eps=rows[2]["eps"])
        model_rows = out["scenario_rows"][name]
        check(f"{name} FY28 EPS", close(rows[2]["eps"], out["scenarios"][name]["fy28_eps"]),
              f"hand ${rows[2]['eps']:.4f} model ${out['scenarios'][name]['fy28_eps']:.4f}")
        check(f"{name} 6개년 UFCF", all(close(a["ufcf"], b["ufcf"]) for a, b in zip(rows, model_rows)),
              f"FY26 UFCF hand {rows[0]['ufcf']:.4f}")
        check(f"{name} TP = P/E × EPS", close(tp, out["scenarios"][name]["tp"]), f"${tp:.2f}")

    exp_tp = sum(m.SCEN[k]["p"] * hand[k]["tp"] for k in m.SCEN)
    check("확률가중 12M 목표가", close(exp_tp, out["expected_tp"]), f"hand ${exp_tp:.4f} model ${out['expected_tp']:.4f}")
    coe_b = 0.0524 + 1.32 * 0.0420
    rolls = {k: out["scen_dcf"][k] * (1 + coe_b) - m.FACT["dps"] for k in m.SCEN}
    fair = out["reasonable"]
    check("정합 12개월 가치", all(close(rolls[k], fair["roll12m"][k]) for k in rolls),
          " ".join(f"{k} {rolls[k]:.1f}" for k in rolls))
    check("정합 배수 × EPS", all(close(rolls[k], fair["justified_pe"][k] * out["scenarios"][k]["fy28_eps"]) for k in rolls),
          " ".join(f"{k} {fair['justified_pe'][k]:.2f}x" for k in ("Tail", "Bear", "Base", "Bull")))
    model_pw = sum(m.SCEN[k]["p"] * rolls[k] for k in m.SCEN)
    anchored = sum((m.CONS["ms_bear"] if k == "Bear" else rolls[k]) * m.SCEN[k]["p"] for k in m.SCEN)
    p_shift = {k: m.SCEN[k]["p"] for k in m.SCEN}
    p_shift["Bear"] -= 0.10
    p_shift["Base"] += 0.10
    shifted = sum(p_shift[k] * rolls[k] for k in m.SCEN)
    midpoint = (anchored + shifted) / 2
    check("합리적인 목표 = 두 보정의 평균", close(midpoint, fair["target"]),
          f"A ${anchored:.2f}  B ${shifted:.2f}  평균 ${midpoint:.2f}")
    price_roll = price * (1 + coe_b) - m.FACT["dps"]
    check("주가의 CoE 롤", close(price_roll, fair["price_rolled_at_coe"]), f"${price_roll:.2f}")
    recent_px = [470.0, 575.0, 530.0, 460.0, 470.0]
    tape = out["tape"]
    check("세이브티커 최근 5곳 평균", close(sum(recent_px) / 5, tape["recent_mean"]), f"${tape['recent_mean']:.2f}")
    check("세이브티커 최근 5곳 중앙", close(470.0, tape["recent_median"]), f"${tape['recent_median']:.0f}")
    check("풋/콜 거래량 0.67", abs((40 / 60) - m.TAPE["options"]["pc_volume"]) < 0.01, f"{40/60:.3f}")
    check("10/9 차트 종가 = 모델 종가", close(m.TAPE["bar"]["close"], m.FACT["price"]), f"{m.TAPE['bar']['close']}")
    check("배당수익률 0.72%", abs((m.FACT["dps"] / m.TAPE["last"]) - m.TAPE["screen_q3"]["div_yield"]) < 0.0002,
          f"{m.FACT['dps'] / m.TAPE['last']:.3%}")
    check("목표와 애널리스트 최저의 간격", abs(tape["fundamental"] - tape["analyst_low"]) < 5,
          f"${tape['fundamental']:.2f} vs ${tape['analyst_low']:.0f}")
    check("옵션 핀은 목표를 바꾸지 않음", tape["target_change"] == 0.0, "0")
    check("확률 가중 합산 재검", close(exp_tp, sum(out["scenarios"][k]["p"] * out["scenarios"][k]["tp"] for k in out["scenarios"])),
          f"${exp_tp:.2f}")

    # Base FY28를 전개식으로 한 번 더
    nonai28 = 16.8 * 1.04 * 1.04
    sw28 = 31.43 * 1.07 * 1.06
    rev28 = 195 + nonai28 + sw28
    eps28 = ((rev28 * 0.65 - 1.8) * 0.84) / 4.94
    check("Base FY28 전개식", close(eps28, hand["Base"]["eps"]), f"${eps28:.4f} rev {rev28:.3f}")

    # 보고 FCF 대수: rep = OI*(1-t) + dep - capex - dnwc - interest*(1-t)
    b0 = hand["Base"]["rows"][0]
    rep_alg = b0["oi"] * (1 - m.TAX) + m.DEP_PATH[0] - m.CAPEX_PATH[0] - b0["dnwc"] - m.NET_INT[0] * (1 - m.TAX)
    check("FY26 보고 FCF 대수", close(rep_alg, b0["rep_fcf"]), f"{rep_alg:.4f}")

    # ── DCF 독립 구현 ──
    base_rows = hand["Base"]["rows"]
    d_hand = hand_dcf(base_rows, w_base, 0.03, tv_lag=0.5)
    d_model = out["dcf"]["base"]
    check("DCF tN = 5.06", close(d_hand["tN"], 5.06), f"{d_hand['tN']}")
    check("DCF base 주당", close(d_hand["value_ps"], d_model["value_ps"], 1e-6),
          f"hand ${d_hand['value_ps']:.4f} model ${d_model['value_ps']:.4f}")
    check("DCF TV 비중", close(d_hand["tv_share"], d_model["tv_share"], 1e-8), f"{d_hand['tv_share']:.4%}")
    check("EV = 명시 PV + TV PV", close(d_hand["ev"], d_hand["pv"] + d_hand["pv_tv"]), f"{d_hand['ev']:.4f}")
    check("주식가치 = EV − 순부채", close(d_hand["equity"], d_hand["ev"] - m.NET_DEBT), f"{d_hand['equity']:.4f}")
    d_time = hand_dcf(base_rows, w_base, 0.03, tv_lag=1.0)
    check("시점정합 DCF", close(d_time["value_ps"], out["timing_consistent_dcf"], 1e-6),
          f"hand ${d_time['value_ps']:.2f}")

    # ── SOTP ──
    fy28 = base_rows[2]
    seg_ai = fy28["ai"] * 0.58 * 20
    seg_non = fy28["nonai"] * 0.50 * 14
    seg_sw = fy28["sw"] * 0.77 * 15
    corp = -(fy28["sbc"] + 2.0) * 14
    sotp_eq = seg_ai + seg_non + seg_sw + corp - m.NET_DEBT
    sotp_ps = sotp_eq / shares
    check("SOTP FY28 주당", close(sotp_ps, out["sotp"]["fwd"]["value_ps"], 1e-6),
          f"hand ${sotp_ps:.2f} model ${out['sotp']['fwd']['value_ps']:.2f}")
    ubs = (31.2 * 17 + 60.4 * 30 - m.NET_DEBT) / shares
    check("UBS형 SOTP", close(ubs, out["sotp"]["ubs"]["ps"], 1e-6), f"${ubs:.2f}")

    # ── 몬테카를로 재현 ──
    mc_a = m.monte_carlo(n=20000, seed=42)
    mc_b = m.monte_carlo(n=20000, seed=42)
    check("MC v1 시드 재현", mc_a["p50"] == mc_b["p50"] == out["mc"]["p50"], f"p50 {mc_a['p50']:.4f}")
    mc2_a = m.monte_carlo_v2(n=20000, seed=42)
    check("MC v2 시드 재현", mc2_a["p50"] == out["mc2"]["p50"], f"p50 {mc2_a['p50']:.4f}")
    share_err = max(abs(mc2_a["scen_share"][k] - m.SCEN[k]["p"]) for k in m.SCEN)
    check("MC v2 시나리오 점유 ±1.5%p", share_err < 0.015, f"max abs {share_err:.3%}")
    # 분위는 정렬 표본의 정의와 일치
    check("MC v2 분위 순서", mc2_a["p5"] <= mc2_a["p25"] <= mc2_a["p50"] <= mc2_a["p75"] <= mc2_a["p95"],
          f"{mc2_a['p5']:.0f} / {mc2_a['p50']:.0f} / {mc2_a['p95']:.0f}")

    # ── 가격 내재 AI ──
    implied_eps = price / 16
    implied_ai = (implied_eps * shares / 0.84 + 1.8) / 0.65 - nonai28 - sw28
    check("16x 내재 EPS", close(implied_eps, out["implied"]["eps_at_16x"]), f"${implied_eps:.4f}")
    check("16x 내재 AI", close(implied_ai, out["implied"]["ai28_at_16x"], 1e-6), f"{implied_ai:.3f}B")

    # ── 분기 실측으로 FY26 영업이익을 다시 쌓는다 (모형 build와 독립) ──
    q_rev, q_opm = m.FACT["fy26_q"]["rev"], m.FACT["fy26_q"]["opm"]
    oi_9m = sum(r * o for r, o in zip(q_rev[:3], q_opm[:3]))
    oi_fy26 = oi_9m + q_rev[3] * q_opm[3]
    eps_fy26_hand = ((oi_fy26 - m.NET_INT[0]) * (1 - m.TAX)) / shares
    check("FY26 OI 분기합", close(oi_fy26, b0["oi"], 0.02), f"hand {oi_fy26:.3f} model {b0['oi']:.3f}")
    check("FY26 EPS vs 컨센 11.66 ±3%", abs(eps_fy26_hand / m.CONS["fy26_eps"] - 1) < 0.03,
          f"${eps_fy26_hand:.2f} vs {m.CONS['fy26_eps']}")

    # ── 대차 시점 공백 (8/2 순부채 vs 10/9 평가) ──
    # 9M 보고 FCF 31.937. 모형 FY26 보고 FCF에서 역산한 4분기, 그 중 10/9까지 67/90.
    q4_rep = b0["rep_fcf"] - 31.937
    earned = q4_rep * (67 / 90)
    dividend = 3.10  # 9/30 $0.65, 3분기 배당금 $3.103B와 같은 규모
    nd_oct9 = m.NET_DEBT + dividend - earned
    dcf_roll_ps = (d_hand["ev"] - nd_oct9) / shares
    spot_gap = dcf_roll_ps - d_hand["value_ps"]

    # 자사주 잔여 $10.1B를 현재가에 소각. 단위가 모두 십억이므로 10.1/주가 = 십억 주.
    shares_bb = shares - (10.1 / price)
    eps_bb = hand["Base"]["rows"][2]["ni"] / shares_bb
    tp_bb = sum(m.SCEN[k]["p"] * m.SCEN[k]["pe"] * (hand[k]["rows"][2]["ni"] / shares_bb) for k in m.SCEN)
    coe = 0.0524 + 1.32 * 0.0420
    pw_dcf_roll = sum(m.SCEN[k]["p"] * (out["scen_dcf"][k] * (1 + coe) - m.FACT["dps"]) for k in m.SCEN)
    bear_gap = out["scenarios"]["Bear"]["tp"] - m.CONS["ms_bear"]
    # Bear를 MS $300에 강제로 두면 기대 목표가가 얼마나 움직이는지 (테스트 실패의 민감도).
    tp_bear_anchored = exp_tp + m.SCEN["Bear"]["p"] * (m.CONS["ms_bear"] - out["scenarios"]["Bear"]["tp"])

    # 분기 가중 GM
    revs, gms = m.FACT["fy26_q"]["rev"], m.FACT["fy26_q"]["gm"]
    gm_w = sum(r * g for r, g in zip(revs, gms)) / sum(revs)
    opex_model = 105.89 * 0.752 - 105.89 * 0.669
    opex_actual_base = fy26_rev * gm_w - fy26_rev * 0.669

    lines = []
    lines.append("=== AVGO 12개월 목표가 ===")
    lines.append(f"기준일 2026-10-09  종가 ${price:.2f}")
    lines.append(f"합리적인 12개월 목표주가 ${out['reasonable']['target']:.2f}  ({out['reasonable']['target'] / price - 1:+.1%})")
    lines.append(f"  두 보정 ${out['reasonable']['bear_anchored_at_ms']:.2f} 와 ${out['reasonable']['bear_prob_shifted']:.2f}, 모델확률 DCF롤 ${out['reasonable']['model_prob_pw']:.2f}")
    lines.append(f"배수법 기대값 ${exp_tp:.2f} = 종가를 자본비용으로 굴린 ${out['reasonable']['price_rolled_at_coe']:.2f}")
    for k in ("Tail", "Bear", "Base", "Bull"):
        s = out["scenarios"][k]
        lines.append(f"  {k:5s} p={s['p']:.2f}  FY28 EPS ${s['fy28_eps']:.2f} × {s['pe']:.0f}x = ${s['tp']:.2f}  ({s['upside']:+.1%})  {s['label']}")
    lines.append(f"DCF 현재가치(β {beta_blume:.2f}, WACC {w_base:.2%}, g 3%) ${d_hand['value_ps']:.2f}  TV비중 {d_hand['tv_share']:.1%}")
    lines.append(f"DCF 시점정합(다음 해 +1.0년) ${d_time['value_ps']:.2f}")
    lines.append(f"DCF 12M 롤 base (×(1+CoE)−DPS) ${out['dcf']['roll12m']['base']:.2f}")
    lines.append(f"확률가중 DCF의 12M 롤 ${pw_dcf_roll:.2f}")
    lines.append(f"Bear를 MS $300에 고정하면 확률가중 목표가 ${tp_bear_anchored:.2f} (Bear 괴리 {bear_gap:+.2f} × p 0.25)")
    lines.append(f"8/2→10/9 현금 롤 후 DCF ${dcf_roll_ps:.2f}  (4Q 보고FCF {q4_rep:.2f}B 중 {earned:.2f}B 인식, 배당 {dividend:.2f}B, 주당 {spot_gap:+.2f})")
    lines.append(f"확률가중 DCF ${out['pw_dcf']:.2f}")
    lines.append(f"SOTP FY27 ${out['sotp']['now']['value_ps']:.2f} | FY28 ${sotp_ps:.2f} | UBS형 ${ubs:.2f}")
    lines.append(f"MC v2 p5/p50/p95 ${out['mc2']['p5']:.0f} / ${out['mc2']['p50']:.0f} / ${out['mc2']['p95']:.0f}  mean ${out['mc2']['mean']:.0f}")
    lines.append(f"자사주 10.1B 전량 소각 시 희석주 {shares_bb:.3f}B, 확률가중 목표가 ${tp_bb:.2f} (EPS base ${eps_bb:.2f})")
    lines.append(f"FY26 가중 GM {gm_w:.2%} vs 믹스검사가 쓴 75.2%. opex 플러그 {opex_model:.2f}B vs 분기가중 {opex_actual_base:.2f}B")
    lines.append("가설 테스트:")
    for t in out["tests"]:
        lines.append(f"  [{t['kind']}] {'PASS' if t['passed'] else 'FAIL'}  {t['name']} — {t['value']}")
    text = "\n".join(lines)
    print(text)
    LOG.write_text("\n".join([f"[{'FAIL' if failures else 'PASS'}] engine checks: {len(failures)} failed", *failures, "", text]) + "\n", encoding="utf-8")

    note = dict(
        engine_failures=failures,
        fy26_eps_hand=eps_fy26_hand,
        q4_rep_fcf=q4_rep,
        fcf_earned_aug3_to_oct9=earned,
        dividend_sep30=dividend,
        net_debt_oct9=nd_oct9,
        dcf_after_cash_roll=dcf_roll_ps,
        buyback_shares_b=shares - shares_bb,
        target_if_buyback_done=tp_bb,
        pw_dcf_roll_12m=pw_dcf_roll,
        target_if_bear_equals_ms=tp_bear_anchored,
        fy26_gm_weighted=gm_w,
        opex0_model=opex_model,
        opex0_from_quarters=opex_actual_base,
        hand_expected_tp=exp_tp,
        hand_dcf_base=d_hand["value_ps"],
        hand_dcf_timing=d_time["value_ps"],
    )
    payload = out
    payload["verification"] = note
    m.OUT_PATH.write_text(json.dumps(payload, indent=1, ensure_ascii=False, default=lambda o: float(o)), encoding="utf-8")
    print(f"engine failures: {len(failures)}")
    print(f"wrote {LOG}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
