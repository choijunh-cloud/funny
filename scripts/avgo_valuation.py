#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
avgo_valuation.py — Broadcom (AVGO) 12개월 선행 적정가치 원장
  DCF (UFCF, SBC=현금성 비용) / SOTP (3세그먼트 EV/EBIT) / 시나리오 확률가중 (FY28 EPS × 배수)
  / Monte Carlo (Mulberry32 seed=42, 공통팩터 w1²+w2²=1) / 터미널 충격 테스트 / IDENT·CALIB·TEST 분류

단위: 달러 십억(B), 주당은 달러. 회계연도 FY = 11월 첫째 일요일 마감 (FY26 = 2025-11-03 ~ 2026-11-01).
기준일: 2026-10-09 종가. 라벨 — [FACT] 공시/1차 사료  [CONS] 컨센 집계값(재조달 10/7~10/9)  [ASSUME] 본 모델 가정  [INF] 추론
실행: python3 avgo_valuation.py  → avgo_model_output.json 생성
"""
import json
import math
from copy import deepcopy
from pathlib import Path

OUT_PATH = Path(__file__).resolve().parent.parent / "avgo_model_output.json"

# ───────────────────────────────── 0. 확정 입력 ─────────────────────────────────
FACT = dict(
    price=361.54,            # 10/9 종가 (stockanalysis·Yahoo 일치)
    dil_shares=4.94,         # 4Q FY26 가이드 희석주 (non-GAAP), B
    cash=23.975, debt_principal=61.079,   # 10-Q 8/2/2026. 캐링 59.419
    buyback_remaining=10.1, dps=2.60,
    fy25=dict(rev=63.887, ai=20.0, nonai=16.858, sw=27.029, gm=78.6, opm=65.7, sbc=7.568,
              capex=0.623, fcf=26.914, eps=6.82, tax=0.14, dep=0.574),
    # FY26 = 3개 분기 실측 + 4Q 가이드 (IDENT)
    fy26_q=dict(rev=[19.311, 22.187, 29.591, 34.8], ai=[8.4, 10.8, 16.7, 21.7],
                sw=[6.796, 7.178, 8.752, 8.7], opm=[0.664, 0.673, 0.679, 0.66],
                gm=[0.770, 0.771, 0.750, 0.73], fcf=[8.010, 10.262, 13.665, None],
                sbc=[2.176, 2.092, 2.019, None], capex=[0.250, 0.231, 0.532, 1.4]),
    guide=dict(fy26_ai=58.0, fy27_ai=115.0, fy28_ai=230.0, fy28_eps_floor=30.0, tax=0.16,
               dollars_per_gw=(20, 30), rpo=179.2, rpo_12m_share=0.25),
    wacc_inputs=dict(rf=0.0524, erp=0.0420, beta_5y=1.48, kd_pre=0.062, tax=0.16),
)
CONS = dict(fy26_rev=105.97, fy26_eps=11.66, fy27_rev=173.93, fy27_eps=19.39, fy28_eps=27.39,
            tp_mean=527.2, tp_median=535.0, tp_high=715.0, tp_low=350.0,
            hold_tps=[350.0, 400.0],                        # DA Davidson Neutral, RBC Sector Perform
            ms_bull=640.0, ms_base=505.0, ms_bear=300.0,
            street_fy28_pe=(14, 18))                         # Piper 14x / Cantor 17x / Rosenblatt 18x

YEARS = ["FY26", "FY27", "FY28", "FY29", "FY30", "FY31"]

# ───────────────────────────────── 1. 시나리오 정의 ─────────────────────────────────
# AI 매출 경로 [ASSUME]: Bull=가이던스 그대로(115→230), Base=스트리트 FY28 EPS 27.4가 함의하는 ~195,
# Bear=고객 금융 지연으로 FY28 150, Tail=순환금융 붕괴(OpenAI/Anthropic 이연·취소)
SCEN = {
    "Tail": dict(p=0.10, ai=[57.6, 85, 105, 100, 100, 100], opm=[0.669, 0.62, 0.58, 0.57, 0.57, 0.57], pe=9.0,
                 nonai_g=-0.05, sw_g=[0.04, 0.03, 0.03, 0.03, 0.03], label="순환금융 붕괴"),
    "Bear": dict(p=0.25, ai=[57.6, 95, 150, 160, 165, 168], opm=[0.669, 0.64, 0.62, 0.61, 0.60, 0.60], pe=12.0,
                 nonai_g=0.02, sw_g=[0.06, 0.05, 0.04, 0.04, 0.04], label="금융 지연·Google 이탈"),
    "Base": dict(p=0.42, ai=[57.6, 118, 195, 225, 245, 258], opm=[0.669, 0.66, 0.65, 0.645, 0.64, 0.635], pe=16.0,
                 nonai_g=0.04, sw_g=[0.07, 0.06, 0.05, 0.04, 0.04], label="스트리트 할인 경로"),
    "Bull": dict(p=0.23, ai=[57.6, 125, 230, 275, 305, 325], opm=[0.669, 0.665, 0.66, 0.655, 0.65, 0.645], pe=19.0,
                 nonai_g=0.05, sw_g=[0.08, 0.07, 0.06, 0.05, 0.05], label="가이던스 달성"),
}
# 공통 [ASSUME]
SBC_PATH   = [8.4, 9.6, 11.0, 12.0, 12.6, 13.0]     # 인원·주가 연동, 매출보다 느리게
CAPEX_PATH = [2.41, 5.0, 6.5, 7.0, 7.0, 7.0]        # 4Q 가이드 1.4B/분기 + 싱가포르 기판 팹(FY27)
DEP_PATH   = [0.70, 1.0, 1.5, 2.0, 2.3, 2.5]
NWC_RATE   = 0.14                                   # ΔNWC = 14% × Δ매출  (CALIB: FY26 보고 FCF 47~49B)
TAX        = 0.16
NET_DEBT   = FACT["debt_principal"] - FACT["cash"]  # 원금 기준 37.1
NET_INT    = [2.6, 2.2, 1.8, 1.4, 1.0, 0.8]         # 순이자(세전) — 부채 상환 경로 [ASSUME]

def build(s):
    """시나리오 s에 대한 FY26~FY31 손익·현금흐름 테이블"""
    nonai = [16.8]; sw = [31.43]
    for i in range(1, 6):
        nonai.append(nonai[-1] * (1 + s["nonai_g"]))
        sw.append(sw[-1] * (1 + s["sw_g"][i - 1]))
    rows = []
    prev_rev = FACT["fy25"]["rev"]
    for i, y in enumerate(YEARS):
        rev = s["ai"][i] + nonai[i] + sw[i]
        oi = rev * s["opm"][i]
        sbc = SBC_PATH[i]
        ebit_econ = oi - sbc                               # SBC를 현금성 비용으로
        nopat = ebit_econ * (1 - TAX)
        dnwc = NWC_RATE * (rev - prev_rev)
        ufcf = nopat + DEP_PATH[i] - CAPEX_PATH[i] - dnwc
        ni = (oi - NET_INT[i]) * (1 - TAX)                 # non-GAAP 순이익 (SBC 제외 — 회사 정의)
        eps = ni / FACT["dil_shares"]
        rep_fcf = ufcf + sbc * (1 - TAX) - NET_INT[i] * (1 - TAX)   # 보고 FCF 근사(SBC 가산, 이자 차감)
        rows.append(dict(year=y, rev=rev, ai=s["ai"][i], nonai=nonai[i], sw=sw[i], opm=s["opm"][i], oi=oi,
                         sbc=sbc, nopat=nopat, dnwc=dnwc, capex=CAPEX_PATH[i], ufcf=ufcf, ni=ni, eps=eps,
                         rep_fcf=rep_fcf))
        prev_rev = rev
    return rows

# ───────────────────────────────── 2. WACC ─────────────────────────────────
def wacc(beta=None, rf=None, erp=None):
    w = FACT["wacc_inputs"]
    beta = w["beta_5y"] if beta is None else beta
    rf = w["rf"] if rf is None else rf
    erp = w["erp"] if erp is None else erp
    coe = rf + beta * erp
    E = FACT["price"] * FACT["dil_shares"]; D = FACT["debt_principal"]
    kd = w["kd_pre"] * (1 - w["tax"])
    return dict(coe=coe, kd_after=kd, wE=E / (E + D), wD=D / (E + D), wacc=coe * E / (E + D) + kd * D / (E + D),
                beta=beta, E=E, D=D)

W_RAW = wacc()                          # 베타 1.48 → CoE 11.46%
W_BASE = wacc(beta=round(0.67 * 1.48 + 0.33, 2))   # Blume 조정 베타 1.32 [ASSUME] — v1의 1.30은 임의 삭감이었음(적대적 검증 #4)
W_STREET = dict(wacc=0.090)             # [INF] 셀사이드 DCF 관행 9%대 (공개된 WACC 없음)

# ───────────────────────────────── 3. DCF ─────────────────────────────────
def dcf(rows, r, g=0.03, mid_year=True, exit_mult=None, tv_lag=0.5):
    """FY26 4Q 잔여(0.06년) + FY27~FY31 명시 + 터미널. 기준일 2026-10-09 ≈ FY26 종료 3주 전 → FY26 UFCF의 6%만 잔여.

    tv_lag: 마지막 명시 현금흐름 시점 대비 터미널 가치 시점의 추가 연수.
    명세 기본값 0.5는 '연말 터미널 − 중간연 현금흐름' 관행(tN = stub+5, FY31 CF는 그 0.5년 전).
    현금흐름이 중간 시점에 들어온다면 다음 해 현금흐름은 1.0년 뒤이므로 tv_lag=1.0이 시점 정합.
    """
    pv = 0.0; details = []
    stub = 0.06
    for i, row in enumerate(rows):
        if i == 0:
            cf = row["ufcf"] * stub; t = stub / 2
        else:
            cf = row["ufcf"]; t = stub + (i - 1) + (0.5 if mid_year else 1.0)
        df = (1 + r) ** (-t); pv += cf * df
        details.append(dict(year=row["year"], cf=cf, t=t, df=df, pv=cf * df))
    t_last = details[-1]["t"]
    tN = t_last + tv_lag
    fcf_T = rows[-1]["ufcf"]
    if exit_mult is None:
        tv = fcf_T * (1 + g) / (r - g)
    else:
        tv = fcf_T * exit_mult
    pv_tv = tv * (1 + r) ** (-tN)
    ev = pv + pv_tv
    eq = ev - NET_DEBT
    return dict(ev=ev, pv_explicit=pv, pv_tv=pv_tv, tv_share=pv_tv / ev if ev else float("nan"), equity=eq,
                value_ps=eq / FACT["dil_shares"], details=details, r=r, g=g, tN=tN, tv=tv)

def implied_r(rows, target_ps, g=0.03):
    lo, hi = 0.05, 0.20
    for _ in range(80):
        mid = (lo + hi) / 2
        if dcf(rows, mid, g)["value_ps"] > target_ps: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def implied_g(rows, r, target_ps):
    lo, hi = -0.02, r - 0.002
    for _ in range(80):
        mid = (lo + hi) / 2
        if dcf(rows, r, mid)["value_ps"] < target_ps: lo = mid
        else: hi = mid
    return (lo + hi) / 2

# ───────────────────────────────── 4. SOTP ─────────────────────────────────
SEG_MARGIN = dict(ai=0.58, nonai=0.50, sw=0.77)       # [ASSUME] 세그먼트 OI 마진(상각·SBC 제외). FY25 세그먼트: 반도체 57.6% / SW 76.8% [FACT]
SOTP_MULT_NOW = dict(ai=24.0, nonai=14.0, sw=15.0, corp=14.0)   # [ASSUME] FY27E EV/EBIT. NVDA fwd PE 19 / QCOM 19 / 성숙 인프라SW 15
SOTP_MULT_FWD = dict(ai=20.0, nonai=14.0, sw=15.0, corp=14.0)   # 12개월 뒤 FY28E 적용 — 성장 감속 반영

def sotp(rows, idx, mult):
    row = rows[idx]
    seg = dict(ai=row["ai"] * SEG_MARGIN["ai"], nonai=row["nonai"] * SEG_MARGIN["nonai"], sw=row["sw"] * SEG_MARGIN["sw"])
    corp = -(row["sbc"] + 2.0)                      # SBC + 미배분 본사비용 2.0B [ASSUME]
    ev_parts = {k: seg[k] * mult[k] for k in seg}
    ev_parts["corp"] = corp * mult["corp"]
    ev = sum(ev_parts.values())
    eq = ev - NET_DEBT
    return dict(year=row["year"], seg_oi=seg, corp=corp, ev_parts=ev_parts, ev=ev, equity=eq, value_ps=eq / FACT["dil_shares"])

# UBS형 EV/FCF SOTP 재현 (17x SW FCF 31.2 + 30x 반도체 FCF 60.4, CY27) [CONS]
UBS = dict(sw_fcf=31.2, semi_fcf=60.4, sw_m=17, semi_m=30)
ubs_ev = UBS["sw_fcf"] * UBS["sw_m"] + UBS["semi_fcf"] * UBS["semi_m"]
ubs_ps = (ubs_ev - NET_DEBT) / FACT["dil_shares"]

# ───────────────────────────────── 5. 시나리오 12M 목표가 ─────────────────────────────────
def scenario_targets():
    out = {}
    for k, s in SCEN.items():
        rows = build(s)
        fy28 = rows[2]
        tp = s["pe"] * fy28["eps"]
        out[k] = dict(p=s["p"], label=s["label"], rows=rows, fy28_eps=fy28["eps"], pe=s["pe"], tp=tp,
                      upside=tp / FACT["price"] - 1)
    return out

# ───────────────────────────────── 6. Monte Carlo (Mulberry32 seed=42) ─────────────────────────────────
def mulberry32(seed):
    a = seed & 0xFFFFFFFF
    def rnd():
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = a
        t = ((t ^ (t >> 15)) * (t | 1)) & 0xFFFFFFFF
        t ^= (t + (((t ^ (t >> 7)) * (t | 61)) & 0xFFFFFFFF)) & 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0
    return rnd

def box_muller(rnd):
    u1 = max(rnd(), 1e-12); u2 = rnd()
    return math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)

def monte_carlo(n=20000, seed=42):
    rnd = mulberry32(seed)
    w1, w2 = 0.6, 0.8                      # 공통팩터/개별충격, w1²+w2² = 1
    # 분포 [ASSUME]: FY28 AI 매출 lognormal(중앙 190, σ 0.22) / FY28 OPM N(0.645, 0.02) / FY28 배수 N(16.5, 2.5) 절단 9~24
    nonai28, sw28 = 16.8 * 1.04 ** 2, 31.43 * 1.07 * 1.06
    res = []
    for _ in range(n):
        zc = box_muller(rnd)
        z_ai = w1 * zc + w2 * box_muller(rnd)
        z_pe = w1 * zc + w2 * box_muller(rnd)
        z_m = box_muller(rnd)                              # 마진은 독립
        ai = 190 * math.exp(0.22 * z_ai - 0.5 * 0.22 ** 2 * 0)   # 중앙값 190 유지(보정항 0)
        opm = 0.645 + 0.02 * z_m
        pe = min(24.0, max(9.0, 16.5 + 2.5 * z_pe))
        rev = ai + nonai28 + sw28
        eps = (rev * opm - NET_INT[2]) * (1 - TAX) / FACT["dil_shares"]
        res.append(pe * eps)
    res.sort()
    q = lambda p: res[int(p * (n - 1))]
    mean = sum(res) / n
    p_up = sum(1 for v in res if v > FACT["price"]) / n
    hist_edges = list(range(100, 901, 25))
    hist = [0] * (len(hist_edges) - 1)
    for v in res:
        j = int((v - 100) // 25)
        if 0 <= j < len(hist): hist[j] += 1
    return dict(n=n, seed=seed, w=(w1, w2), mean=mean, p5=q(0.05), p25=q(0.25), p50=q(0.50), p75=q(0.75), p95=q(0.95),
                p_above_price=p_up, hist_edges=hist_edges, hist=hist)

# ───────────────────────────────── 6b. Monte Carlo v2 — 시나리오 혼합 (적대적 검증 #7 채택) ─────────────────────────────────
def monte_carlo_v2(n=20000, seed=42):
    """시나리오 질량(10/25/42/23)을 그대로 따르는 혼합분포. 시나리오 내부: AI lognormal(σ 0.12), OPM은 AI와 상관(0.6), P/E는 공통팩터와 상관.
       v1(단일 lognormal 190·σ 0.22)은 꼬리를 14배 과소평가(P(AI<105)=0.35% vs 시나리오 10%)했음."""
    rnd = mulberry32(seed)
    w1, w2 = 0.6, 0.8
    keys = list(SCEN.keys()); cum = []; acc = 0.0
    for k in keys:
        acc += SCEN[k]["p"]; cum.append(acc)
    if cum[-1] < 1.0 - 1e-9:
        raise RuntimeError(f"scenario probabilities sum to {cum[-1]}, not 1")
    nonai28, sw28 = 16.8 * 1.04 ** 2, 31.43 * 1.07 * 1.06
    res = []; by_scen = {k: [] for k in keys}
    for _ in range(n):
        u = rnd()
        k = keys[next(i for i, c in enumerate(cum) if u <= c + 1e-12)]
        s = SCEN[k]
        zc = box_muller(rnd)
        z_ai = w1 * zc + w2 * box_muller(rnd)
        z_pe = w1 * zc + w2 * box_muller(rnd)
        z_m = 0.6 * z_ai + 0.8 * box_muller(rnd)              # OPM ↔ AI 상관 0.6
        ai = s["ai"][2] * math.exp(0.12 * z_ai - 0.5 * 0.12 ** 2)   # 평균 보정 포함 → 평균 = 시나리오 값
        opm = s["opm"][2] + 0.02 * z_m
        pe = min(26.0, max(7.0, s["pe"] + 2.0 * z_pe))
        rev = ai + nonai28 + sw28
        eps = (rev * opm - NET_INT[2]) * (1 - TAX) / FACT["dil_shares"]
        v = pe * eps
        res.append(v); by_scen[k].append(v)
    res.sort()
    q = lambda p: res[int(p * (n - 1))]
    hist_edges = list(range(50, 901, 25))
    hist = [0] * (len(hist_edges) - 1)
    for v in res:
        j = int((v - 50) // 25)
        if 0 <= j < len(hist): hist[j] += 1
    return dict(n=n, seed=seed, w=(w1, w2), mean=sum(res) / n, p5=q(0.05), p25=q(0.25), p50=q(0.50), p75=q(0.75), p95=q(0.95),
                p_above_price=sum(1 for v in res if v > FACT["price"]) / n,
                p_below_300=sum(1 for v in res if v < 300) / n,
                hist_edges=hist_edges, hist=hist,
                scen_share={k: len(v) / n for k, v in by_scen.items()},
                scen_median={k: sorted(v)[len(v) // 2] for k, v in by_scen.items()})

# ───────────────────────────────── 6c. 믹스 기반 OPM 검사 (적대적 검증 #6 채택) ─────────────────────────────────
GM_SEG = dict(sw=0.93, nonai=0.67)       # [ASSUME] 4Q 가이드 GM 73%에서 역산한 AI GM ≈ 66% (SW 93 / non-AI 67 가정)
def opm_from_mix(row, ai_gm, opex0=None, opex_g=0.10, years_from_fy26=2):
    """OPM = (AI×GM_AI + SW×93% + nonAI×67% − opex) / rev.  opex FY26 = GM$ − OI$ = 79.6 − 70.8 ≈ 8.8B [FACT 파생], 연 +10% [ASSUME]"""
    if opex0 is None: opex0 = 105.89 * 0.752 - 105.89 * 0.669       # FY26 GM 75.2%(분기 가중) − OPM 66.9%
    opex = opex0 * (1 + opex_g) ** years_from_fy26
    gm_dollars = row["ai"] * ai_gm + row["sw"] * GM_SEG["sw"] + row["nonai"] * GM_SEG["nonai"]
    return (gm_dollars - opex) / row["rev"], gm_dollars / row["rev"]

# ───────────────────────────────── 6d. 소화(digestion) 사이클 DCF 케이스 (적대적 검증 #2 채택) ─────────────────────────────────
DIGEST = dict(p=None, ai=[57.6, 118, 195, 170, 156, 200], opm=[0.669, 0.66, 0.65, 0.62, 0.60, 0.62], pe=None,
              nonai_g=0.04, sw_g=[0.07, 0.06, 0.05, 0.04, 0.04], label="FY29~30 캐펙스 소화(−20%) 후 회복")

# ───────────────────────────────── 7. 테스트 (IDENT / CALIB / TEST) ─────────────────────────────────
def run_tests(S, base_rows, d_base):
    T = []
    fy26_rev = sum(FACT["fy26_q"]["rev"])
    T.append(dict(kind="IDENT", name="FY26 매출 = 3분기 실측 + 4Q 가이드", value=f"{fy26_rev:.2f}B vs 컨센 {CONS['fy26_rev']}",
                  passed=abs(fy26_rev - CONS["fy26_rev"]) < 0.5, note="정의상 항등식 — 점수화 안 함"))
    fy26_ai = sum(FACT["fy26_q"]["ai"])
    T.append(dict(kind="IDENT", name="FY26 AI = 분기합 57.6 ≈ 가이드 58", value=f"{fy26_ai:.1f}", passed=abs(fy26_ai - 58) < 1, note="반올림 차"))
    rep26 = base_rows[0]["rep_fcf"]
    T.append(dict(kind="CALIB", name="FY26 보고 FCF 근사 (ΔNWC 14% 보정)", value=f"{rep26:.1f}B (9M 실측 31.9 + 4Q 추정)",
                  passed=45 <= rep26 <= 50, note="NWC_RATE로 맞춘 값 — 점수화 안 함"))
    # TEST 1: Bull(가이던스 경로) FY28 EPS ≥ 30 재현 — 실패 가능 (OPM·이자·세율·주식수 가정이 틀리면 깨짐)
    bull_eps = S["Bull"]["fy28_eps"]
    T.append(dict(kind="TEST", name="가이던스 경로(AI 230·OPM 66)로 FY28 EPS > $30 재현", value=f"${bull_eps:.2f}",
                  passed=bull_eps >= 30.0, note="실패하면 회사 가이던스가 내 마진·세율 가정과 불일치"))
    # TEST 2: Base FY28 EPS vs 컨센 27.39 ±6%
    base_eps = S["Base"]["fy28_eps"]
    T.append(dict(kind="TEST", name="Base(AI 195) FY28 EPS가 컨센 27.39 ±6% 안", value=f"${base_eps:.2f} vs 27.39 ({base_eps/27.39-1:+.1%})",
                  passed=abs(base_eps / CONS["fy28_eps"] - 1) < 0.06, note="스트리트의 FY28 AI 할인폭 역산의 정합성"))
    # TEST 3: 터미널 충격 — OPM −29%p 시 TV($) 반응 및 TV 비중 이동
    shocked = deepcopy(SCEN["Base"]); shocked["opm"] = [m - 0.29 for m in shocked["opm"]]
    d_shock = dcf(build(shocked), d_base["r"], d_base["g"])
    tv_drop = 1 - d_shock["pv_tv"] / d_base["pv_tv"]
    T.append(dict(kind="TEST", name="터미널 충격 A: 전 연도 OPM −29%p → TV($) 하락률 / TV 비중 변화", value=f"TV −{tv_drop:.0%}, 비중 {d_base['tv_share']:.1%}→{d_shock['tv_share']:.1%}",
                  passed=tv_drop > 0.30, note="터미널이 영업 가정에 반응하는가 (상수면 DCF 무의미). 전 연도 균등 충격이면 비중은 거의 안 움직이는 게 정상"))
    # TEST 3b: 터미널 연도(FY31)만 OPM −29%p → TV 비중이 10%p 이상 이동해야 (8/12 규칙 원형)
    shocked_t = deepcopy(SCEN["Base"]); shocked_t["opm"] = shocked_t["opm"][:5] + [shocked_t["opm"][5] - 0.29]
    d_shock_t = dcf(build(shocked_t), d_base["r"], d_base["g"])
    share_move = d_base["tv_share"] - d_shock_t["tv_share"]
    T.append(dict(kind="TEST", name="터미널 충격 B: FY31(터미널 연도)만 OPM −29%p → TV 비중 ≥10%p 이동", value=f"비중 {d_base['tv_share']:.1%}→{d_shock_t['tv_share']:.1%} ({share_move:+.1%}p), 주당 ${d_base['value_ps']:.0f}→${d_shock_t['value_ps']:.0f}",
                  passed=share_move >= 0.10, note="2026-08-12 상설 규칙 원형 — 터미널 전환율이 마진에 반응"))
    # TEST 4: Hold 하우스 평균 ≈ 현재가 ±5%
    hold_avg = sum(CONS["hold_tps"]) / len(CONS["hold_tps"])
    T.append(dict(kind="TEST", name="Hold 하우스 평균 TP ≈ 현재가 ±5%", value=f"${hold_avg:.0f} vs ${FACT['price']}  ({hold_avg/FACT['price']-1:+.1%})",
                  passed=abs(hold_avg / FACT["price"] - 1) < 0.05, note="시장가가 어느 세계관인지 특정"))
    # TEST 5: Bear 시나리오 vs MS bear $300 ±10%
    T.append(dict(kind="TEST", name="Bear 목표가 vs Morgan Stanley bear $300 ±10%", value=f"${S['Bear']['tp']:.0f}",
                  passed=abs(S["Bear"]["tp"] / CONS["ms_bear"] - 1) < 0.10, note="외부 앵커 대조"))
    # TEST 6: 스트리트 평균 TP $527이 어느 (배수, EPS) 조합인지 — 컨센 FY28 EPS × 19.2x. 14~18x 밴드 밖이면 '평균은 어느 하우스의 값도 아님'
    implied_pe = CONS["tp_mean"] / CONS["fy28_eps"]
    T.append(dict(kind="TEST", name="컨센 평균 TP ÷ 컨센 FY28 EPS가 스트리트 배수 밴드(14~18x) 안", value=f"{implied_pe:.1f}x",
                  passed=14 <= implied_pe <= 18, note="실패 = 평균 TP는 EPS 상향(가이던스 신뢰)과 배수 확장이 섞인 값"))
    # TEST 7: 믹스 기반 OPM — AI GM 66%·opex +10%/yr로 Base FY28 OPM 65%가 ±2%p 안에서 재현되는가
    opm_mix, gm_mix = opm_from_mix(base_rows[2], ai_gm=0.66)
    T.append(dict(kind="TEST", name="믹스 역산 OPM(AI GM 66%·SW 93·non-AI 67·opex +10%/yr) vs Base FY28 OPM 65%", value=f"믹스 OPM {opm_mix:.1%} (GM {gm_mix:.1%}) vs 가정 {base_rows[2]['opm']:.1%}",
                  passed=abs(opm_mix - base_rows[2]["opm"]) < 0.02, note="실패하면 OPM 가정이 GM 희석과 모순 — AI GM이 60%면 61%로 추락(적대적 검증 #6)"))
    return T

def roll_12m(spot, coe=None):
    """현재 주식가치를 자본비용으로 1년 굴리고 배당을 뺀 12개월 가치."""
    coe = W_BASE["coe"] if coe is None else coe
    return spot * (1 + coe) - FACT["dps"]


def reasonable_target(S, scen_spot):
    """할인율과 정합하는 12개월 목표주가.

    시나리오 배수(Base 16x, Bull 19x)는 같은 현금흐름을 WACC 10.6%로 할인한
    가치가 허용하는 배수(약 13.7x, 14.7x)보다 높다. 12개월 가치는
    DCF 현재가치 × (1+CoE) − DPS 로 잡는다.

    모델 Bear의 12개월 가치는 Morgan Stanley bear $300보다 낮다. 아래 두 보정은
    그 불일치를 서로 다른 방식으로 고치고, 결과는 같은 자리로 모인다.
      A. Bear 결과만 $300으로 두고 모델 확률(10/25/42/23)을 유지
      B. 가혹한 Bear 확률을 25%에서 15%로 낮추고, 10%p를 Base로 이동
    목표주가는 A와 B의 평균이다.
    """
    roll = {k: roll_12m(scen_spot[k]) for k in S}
    justified = {k: roll[k] / S[k]["fy28_eps"] for k in S}
    model_pw = sum(S[k]["p"] * roll[k] for k in S)
    anchored = sum((CONS["ms_bear"] if k == "Bear" else roll[k]) * S[k]["p"] for k in S)
    shifted_p = {k: S[k]["p"] for k in S}
    shifted_p["Bear"] -= 0.10
    shifted_p["Base"] += 0.10
    shifted = sum(shifted_p[k] * roll[k] for k in S)
    midpoint = (anchored + shifted) / 2
    return dict(
        target=midpoint,
        model_prob_pw=model_pw,
        bear_anchored_at_ms=anchored,
        bear_prob_shifted=shifted,
        probabilities_shifted=shifted_p,
        roll12m=roll,
        justified_pe=justified,
        price_rolled_at_coe=roll_12m(FACT["price"]),
        ms_bear=CONS["ms_bear"],
    )


def run_model():
    S = scenario_targets()
    base_rows = S["Base"]["rows"]
    d_raw = dcf(base_rows, W_RAW["wacc"])
    d_base = dcf(base_rows, W_BASE["wacc"])
    d_street = dcf(base_rows, 0.09)
    d_street_g = dcf(base_rows, 0.09, 0.035)
    d_bull9 = dcf(S["Bull"]["rows"], 0.09, 0.035)
    d_exit = dcf(base_rows, W_BASE["wacc"], exit_mult=18.0)
    # 시점 정합: 중간연 현금흐름의 다음 해는 1.0년 뒤. 명세 기본(tv_lag=0.5)과의 차이만 별도 기록.
    d_timing = dcf(base_rows, W_BASE["wacc"], tv_lag=1.0)
    r_impl = implied_r(base_rows, FACT["price"])
    g_impl = implied_g(base_rows, W_BASE["wacc"], FACT["price"])

    # WACC × g 격자 (Base 경로)
    grid_r = [0.085, 0.09, 0.095, 0.10, 0.105, 0.11, 0.115]
    grid_g = [0.02, 0.025, 0.03, 0.035, 0.04]
    grid = [[round(dcf(base_rows, r, g)["value_ps"], 1) for g in grid_g] for r in grid_r]

    # 12M 롤포워드: DCF 가치 × (1+CoE) − DPS
    roll = lambda v, coe: v * (1 + coe) - FACT["dps"]

    sotp_now = sotp(base_rows, 1, SOTP_MULT_NOW)
    sotp_fwd = sotp(base_rows, 2, SOTP_MULT_FWD)

    ev_now = FACT["price"] * FACT["dil_shares"] + NET_DEBT
    exp_tp = sum(v["p"] * v["tp"] for v in S.values())
    mc = monte_carlo()

    # 가격에 내재된 것: 16x 배수 가정 시 FY28 EPS, 그 EPS가 함의하는 AI 매출
    implied_eps16 = FACT["price"] / 16.0
    nonai28, sw28 = base_rows[2]["nonai"], base_rows[2]["sw"]
    implied_ai16 = (implied_eps16 * FACT["dil_shares"] / (1 - TAX) + NET_INT[2]) / 0.65 - nonai28 - sw28

    # 괴리 분해. 베타는 코드가 쓰는 Blume 1.32 (v1의 1.30 라벨은 폐기).
    bridge = [
        (f"엄격 CAPM DCF (β {W_BASE['beta']:.2f} Blume·10Y 5.24%·g 3%)", d_base["value_ps"]),
        ("할인율만 9.0%로", d_street["value_ps"]),
        ("+ 터미널 g 3.5%", d_street_g["value_ps"]),
        ("+ AI 경로 Bull(가이던스 230)", d_bull9["value_ps"]),
        ("시나리오 확률가중 12M 목표가", exp_tp),
        ("셀사이드 평균 TP", CONS["tp_mean"]),
    ]

    # 확률가중 DCF (Base 단일값이 아니라 기대값) + 소화 사이클 케이스 + v1 배수(17/20/13/10, Tail 5%)와의 브리지
    pw_dcf = sum(v["p"] * dcf(v["rows"], W_BASE["wacc"])["value_ps"] for v in S.values())
    scen_dcf = {k: dcf(v["rows"], W_BASE["wacc"])["value_ps"] for k, v in S.items()}
    fair = reasonable_target(S, scen_dcf)
    d_digest = dcf(build(DIGEST), W_BASE["wacc"])
    d_digest9 = dcf(build(DIGEST), 0.09, 0.035)
    v1 = dict(Tail=(0.05, 10.0), Bear=(0.25, 13.0), Base=(0.45, 17.0), Bull=(0.25, 20.0))
    exp_tp_v1 = sum(v1[k][0] * v1[k][1] * S[k]["fy28_eps"] for k in S)
    dcf_pe = d_base["value_ps"] / S["Base"]["fy28_eps"]
    legacy_dcf_pe = 13.8
    exp_tp_dcfpe = sum(S[k]["p"] * (legacy_dcf_pe * S[k]["pe"] / 16.0) * S[k]["fy28_eps"] for k in S)
    exp_tp_dcfpe_live = sum(S[k]["p"] * (dcf_pe * S[k]["pe"] / 16.0) * S[k]["fy28_eps"] for k in S)
    mix_table = []
    for ai_gm in (0.70, 0.66, 0.62, 0.58, 0.55):
        o, g = opm_from_mix(base_rows[2], ai_gm)
        eps = (base_rows[2]["rev"] * o - NET_INT[2]) * (1 - TAX) / FACT["dil_shares"]
        mix_table.append(dict(ai_gm=ai_gm, gm=g, opm=o, eps=eps, tp16=16 * eps))
    mc2 = monte_carlo_v2()

    tests = run_tests(S, base_rows, d_base)
    out = dict(
        pw_dcf=pw_dcf, scen_dcf=scen_dcf, digest=dict(base=d_digest["value_ps"], street=d_digest9["value_ps"], tv_share=d_digest["tv_share"]),
        v1=dict(expected_tp=exp_tp_v1, mult=v1), expected_tp_dcfpe=exp_tp_dcfpe,
        dcf_implied_pe_base=dcf_pe, legacy_dcf_pe=legacy_dcf_pe, expected_tp_dcfpe_live=exp_tp_dcfpe_live,
        timing_consistent_dcf=d_timing["value_ps"], mix_table=mix_table, mc2=mc2,
        asof="2026-10-09", price=FACT["price"], net_debt=NET_DEBT, ev_now=ev_now, shares=FACT["dil_shares"],
        wacc=dict(raw=W_RAW, base=W_BASE, street=0.09),
        dcf=dict(raw=d_raw, base=d_base, street=d_street, street_g=d_street_g, bull9=d_bull9, exit18=d_exit,
                 timing=d_timing,
                 implied_wacc_at_price=r_impl, implied_g_at_price=g_impl,
                 grid=dict(r=grid_r, g=grid_g, v=grid),
                 roll12m=dict(base=roll(d_base["value_ps"], W_BASE["coe"]), street_g=roll(d_street_g["value_ps"], 0.095),
                              timing=roll(d_timing["value_ps"], W_BASE["coe"]))),
        sotp=dict(now=sotp_now, fwd=sotp_fwd, ubs=dict(ev=ubs_ev, ps=ubs_ps, **UBS), margins=SEG_MARGIN,
                  mult_now=SOTP_MULT_NOW, mult_fwd=SOTP_MULT_FWD),
        scenarios={k: {kk: vv for kk, vv in v.items() if kk != "rows"} for k, v in S.items()},
        scenario_rows={k: v["rows"] for k, v in S.items()},
        expected_tp=exp_tp, expected_upside=exp_tp / FACT["price"] - 1,
        reasonable=fair,
        mc=mc, implied=dict(eps_at_16x=implied_eps16, ai28_at_16x=implied_ai16),
        bridge=bridge, tests=tests, cons=CONS, fact=FACT,
    )
    return out

# ───────────────────────────────── 8. 실행 ─────────────────────────────────
if __name__ == "__main__":
    out = run_model()
    S_rows = out["scenario_rows"]
    d_raw, d_base = out["dcf"]["raw"], out["dcf"]["base"]
    d_street, d_street_g, d_bull9, d_exit = out["dcf"]["street"], out["dcf"]["street_g"], out["dcf"]["bull9"], out["dcf"]["exit18"]
    Wraw, Wbase = out["wacc"]["raw"], out["wacc"]["base"]
    exp_tp = out["expected_tp"]
    ev_now = out["ev_now"]
    mc, mc2 = out["mc"], out["mc2"]
    r_impl, g_impl = out["dcf"]["implied_wacc_at_price"], out["dcf"]["implied_g_at_price"]
    sotp_now, sotp_fwd, ubs_ps = out["sotp"]["now"], out["sotp"]["fwd"], out["sotp"]["ubs"]["ps"]
    implied_eps16, implied_ai16 = out["implied"]["eps_at_16x"], out["implied"]["ai28_at_16x"]
    pw_dcf, scen_dcf = out["pw_dcf"], out["scen_dcf"]
    d_digest_ps, d_digest9_ps = out["digest"]["base"], out["digest"]["street"]
    exp_tp_v1, exp_tp_dcfpe = out["v1"]["expected_tp"], out["expected_tp_dcfpe"]
    mix_table = out["mix_table"]
    base_rows = S_rows["Base"]
    tests = out["tests"]

    with OUT_PATH.open("w") as f:
        json.dump(out, f, indent=1, ensure_ascii=False, default=lambda o: float(o))

    # ── 콘솔 요약 ──
    print(f"기준일 {out['asof']}  주가 ${FACT['price']}  EV ${ev_now:,.0f}B  순부채 ${NET_DEBT:.1f}B  희석주 {FACT['dil_shares']}B")
    print(f"WACC  raw(β{Wraw['beta']:.2f}) {Wraw['wacc']:.2%} (CoE {Wraw['coe']:.2%}) | base(β{Wbase['beta']:.2f} Blume) {Wbase['wacc']:.2%} (CoE {Wbase['coe']:.2%}) | street 9.0%")
    for k, v in out["scenarios"].items():
        r28 = S_rows[k][2]
        r27 = S_rows[k][1]
        print(f"{k:5s} p={v['p']:.2f} FY27 rev {r27['rev']:.0f} / FY28 rev {r28['rev']:.0f} AI {r28['ai']:.0f} OPM {r28['opm']:.1%} EPS ${v['fy28_eps']:.2f} × {v['pe']}x = ${v['tp']:.0f} ({v['upside']:+.1%})")
    fair = out["reasonable"]
    print(f"확률가중 배수법 12M ${exp_tp:.0f} ({exp_tp/FACT['price']-1:+.1%}) | 주가를 CoE로 굴린 값 ${fair['price_rolled_at_coe']:.0f}")
    print(f"합리적인 12개월 목표주가 ${fair['target']:.0f}  (모델확률 DCF롤 ${fair['model_prob_pw']:.0f} | Bear=$300 고정 ${fair['bear_anchored_at_ms']:.0f} | Bear 15% ${fair['bear_prob_shifted']:.0f})")
    for k, pe in fair["justified_pe"].items():
        print(f"  정합배수 {k:5s} 12m ${fair['roll12m'][k]:.0f} = {pe:.1f}x FY28 EPS")
    print(f"DCF raw ${d_raw['value_ps']:.0f} | base ${d_base['value_ps']:.0f} (TV {d_base['tv_share']:.0%}) | 9%/3% ${d_street['value_ps']:.0f} | 9%/3.5% ${d_street_g['value_ps']:.0f} | Bull 9%/3.5% ${d_bull9['value_ps']:.0f} | exit 18x ${d_exit['value_ps']:.0f}")
    print(f"시점정합 DCF(tv_lag=1) ${out['timing_consistent_dcf']:.0f} | DCF가 함의하는 Base P/E {out['dcf_implied_pe_base']:.2f}x (레거시 상수 13.8x)")
    print(f"현재가 내재 WACC(g3%) {r_impl:.2%} | 내재 g(WACC {Wbase['wacc']:.1%}) {g_impl:.2%}")
    print(f"SOTP now(FY27E) ${sotp_now['value_ps']:.0f} | fwd(FY28E) ${sotp_fwd['value_ps']:.0f} | UBS형 ${ubs_ps:.0f}")
    print(f"MC n={mc['n']} seed={mc['seed']} w={mc['w']}: p5 {mc['p5']:.0f} p25 {mc['p25']:.0f} p50 {mc['p50']:.0f} p75 {mc['p75']:.0f} p95 {mc['p95']:.0f} mean {mc['mean']:.0f} P(>price) {mc['p_above_price']:.1%}")
    print(f"가격 내재(16x): FY28 EPS ${implied_eps16:.2f} → AI 매출 ${implied_ai16:.0f}B")
    print(f"확률가중 DCF ${pw_dcf:.0f}  시나리오별 DCF { {k: round(v) for k, v in scen_dcf.items()} }  소화 케이스 DCF ${d_digest_ps:.0f} (9%/3.5%: ${d_digest9_ps:.0f})")
    print(f"v1 배수(17/20/13/10·Tail5%) 기대 TP ${exp_tp_v1:.0f} → v2(16/19/12/9·Tail10%) ${exp_tp:.0f} → DCF 정합 배수(13.8x) ${exp_tp_dcfpe:.0f} → 실측 DCF배수 ${out['expected_tp_dcfpe_live']:.0f}")
    print("믹스 OPM 표:", [(m['ai_gm'], round(m['opm'], 3), round(m['eps'], 2), round(m['tp16'])) for m in mix_table])
    print(f"MC v2(혼합) p5 {mc2['p5']:.0f} p25 {mc2['p25']:.0f} p50 {mc2['p50']:.0f} p75 {mc2['p75']:.0f} p95 {mc2['p95']:.0f} mean {mc2['mean']:.0f} P(>price) {mc2['p_above_price']:.1%} P(<300) {mc2['p_below_300']:.1%} 시나리오 점유 {mc2['scen_share']}")
    print("Base rows:")
    for r in base_rows:
        print(f"  {r['year']} rev {r['rev']:.1f} ai {r['ai']:.0f} nonai {r['nonai']:.1f} sw {r['sw']:.1f} oi {r['oi']:.1f} sbc {r['sbc']:.1f} ufcf {r['ufcf']:.1f} repFCF {r['rep_fcf']:.1f} eps {r['eps']:.2f}")
    print("Tests:")
    for t in tests:
        print(f"  [{t['kind']}] {'PASS' if t['passed'] else 'FAIL'}  {t['name']} — {t['value']}")
    print(f"wrote {OUT_PATH}")
