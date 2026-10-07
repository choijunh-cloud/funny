#!/usr/bin/env python3
"""10/7 정량 모델: Muse DRAM · CPU TAM · 메모리 밸류 · CapEx 역설 · Muse→NV bridge."""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

OUT = Path("/workspace/output/oct7")


# ── helpers ──────────────────────────────────────────────────────────────


def cagr(start: float, end: float, years: float) -> float:
    if start <= 0 or years <= 0:
        return float("nan")
    return (end / start) ** (1 / years) - 1


def grow(start: float, rate: float, years: float) -> float:
    return start * ((1 + rate) ** years)


def pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def usd_b(x: float) -> str:
    return f"${x:.1f}B"


def krw_man(x: float) -> str:
    return f"{x:,.0f}만"


# ── 1) Muse DRAM demand model ────────────────────────────────────────────


@dataclass
class MuseScenario:
    name: str
    dau_m: float  # million DAU
    active_ratio: float  # concurrent fraction of DAU with live VM
    alloc_gb: float
    used_gb: float
    # physical_gb = concurrent * used_gb / sharing; sharing~1 for DRAM
    sharing: float


def muse_physical_eb(s: MuseScenario) -> dict:
    """Return physical DRAM demand in EB (exabytes) and TB."""
    concurrent = s.dau_m * 1e6 * s.active_ratio
    logical_alloc_tb = concurrent * s.alloc_gb / 1e3  # GB→TB? 1e6 concurrent * GB / 1e6 = TB... 
    # concurrent * GB = total GB; /1e6 = PB? Let's be careful:
    # 1 EB = 1e9 GB, 1 PB = 1e6 GB, 1 TB = 1e3 GB
    total_alloc_gb = concurrent * s.alloc_gb
    total_used_gb = concurrent * s.used_gb
    physical_gb = total_used_gb / max(s.sharing, 1e-9)
    return {
        "name": s.name,
        "dau_m": s.dau_m,
        "active_ratio": s.active_ratio,
        "concurrent_m": concurrent / 1e6,
        "alloc_gb": s.alloc_gb,
        "used_gb": s.used_gb,
        "sharing": s.sharing,
        "logical_alloc_EB": total_alloc_gb / 1e9,
        "used_EB": total_used_gb / 1e9,
        "physical_EB": physical_gb / 1e9,
        "physical_PB": physical_gb / 1e6,
        "naive_8gb_EB": (concurrent * 8) / 1e9,
        "naive_overstate_vs_physical": (concurrent * 8) / max(physical_gb, 1e-9),
    }


def build_muse_grid() -> list[dict]:
    """Scenario grid: adoption × intensity."""
    rows = []
    # DAU paths (million): early / scale / Muse-citi-1억
    for dau, dau_label in ((10, "1천만"), (50, "5천만"), (100, "1억")):
        for active, act_label in ((0.05, "활성5%"), (0.15, "활성15%"), (0.30, "활성30%")):
            for intensity in (
                MuseScenario("현재실측", dau, active, 8, 3, 1.1),
                MuseScenario("고도화", dau, active, 16, 8, 1.05),
                MuseScenario("복잡Agent", dau, active, 32, 15, 1.0),
            ):
                r = muse_physical_eb(intensity)
                r["dau_label"] = dau_label
                r["act_label"] = act_label
                r["key"] = f"{dau_label}|{act_label}|{intensity.name}"
                rows.append(r)
    return rows


def muse_insights(rows: list[dict]) -> dict:
    # Anchor: Citi Muse 1억 DAU, mid activity 15%, current vs complex
    def pick(dau_m, active, name):
        for r in rows:
            if r["dau_m"] == dau_m and abs(r["active_ratio"] - active) < 1e-9 and r["name"] == name:
                return r
        raise KeyError

    base = pick(100, 0.15, "현재실측")
    bull = pick(100, 0.30, "복잡Agent")
    bear = pick(100, 0.05, "현재실측")
    mid = pick(100, 0.15, "고도화")
    return {
        "formula": "Physical DRAM ≈ DAU × active_ratio × used_GB / sharing",
        "not_formula": "≠ DAU × 8GB (논리적 할당 과대)",
        "anchor_1e8_dau": {
            "bear_active5_current": bear,
            "base_active15_current": base,
            "mid_active15_upgrade": mid,
            "bull_active30_complex": bull,
        },
        "overstate": {
            "at_base": base["naive_overstate_vs_physical"],
            "note": "1억 DAU·활성15%·현재실측에서 8GB×N은 물리 수요를 약 N배 과대",
        },
        "implication": (
            "현재는 used≈3GB·sharing>1로 물리 수요가 작아 보일 수 있으나, "
            "활성률↑와 used_GB↑가 동시에 오면 비선형으로 커진다. "
            "CPU oversubscribe와 달리 DRAM sharing≈1에 수렴하는 것이 비대칭 포인트."
        ),
    }


# ── 2) CPU TAM scenario model ────────────────────────────────────────────


@dataclass
class TamPath:
    name: str
    y2025: float
    y2030: float
    agentic_share_2030: float | None = None
    agentic_usd_2030: float | None = None
    note: str = ""


def build_cpu_tam() -> dict:
    paths = [
        TamPath("Citi May", 29.3, 131.5, 0.45, 59.4, "Agentic CAGR 185% (5월 모델)"),
        TamPath("Citi Oct", 29.0, 300.0, None, None, "Muse/Agentic 반영 상향; Agentic $는 미제시"),
        TamPath("Mizuho", 25.9, 209.0, 0.30, 80.0, "DRAM/NAND 비트 22~30%도 Agent"),
    ]
    table = []
    for p in paths:
        years = 5.0
        g = cagr(p.y2025, p.y2030, years)
        y2026 = grow(p.y2025, g, 1)
        y2027 = grow(p.y2025, g, 2)
        y2028 = grow(p.y2025, g, 3)
        table.append(
            {
                "name": p.name,
                "y2025": p.y2025,
                "y2026_implied": round(y2026, 1),
                "y2027_implied": round(y2027, 1),
                "y2028_implied": round(y2028, 1),
                "y2030": p.y2030,
                "cagr": g,
                "cagr_pct": pct(g),
                "multiple_5y": p.y2030 / p.y2025,
                "agentic_share_2030": p.agentic_share_2030,
                "agentic_usd_2030": p.agentic_usd_2030,
                "note": p.note,
            }
        )

    # Bridge: what agentic layer must do for Citi Oct vs May
    citi_may = next(x for x in table if x["name"] == "Citi May")
    citi_oct = next(x for x in table if x["name"] == "Citi Oct")
    delta_2030 = citi_oct["y2030"] - citi_may["y2030"]  # 168.5
    # If traditional layer stays at May path, agentic must fill delta + may agentic
    may_agentic = 59.4
    implied_agentic_oct = may_agentic + delta_2030  # if non-agentic fixed
    implied_share_oct = implied_agentic_oct / 300.0

    # CPU:GPU ratio shift impact (illustrative)
    # Old: 1 CPU : 6 GPU → New: 1:1 means ~6x CPU sockets per same GPU fleet
    ratio_old = 6.0
    ratio_new = 1.0
    cpu_intensity_uplift = ratio_old / ratio_new

    return {
        "paths": table,
        "bridge_oct_vs_may": {
            "delta_2030_B": delta_2030,
            "if_non_agentic_fixed_at_may": {
                "implied_agentic_2030_B": round(implied_agentic_oct, 1),
                "implied_agentic_share": round(implied_share_oct, 3),
                "note": "May non-agentic≈$72.1B 고정 가정 시 Oct $300B를 맞추려면 Agentic≈$228B(약 76%) 필요 — 매우 공격적",
            },
        },
        "cpu_gpu_ratio": {
            "chatbot_cpu_per_gpu": 1 / ratio_old,
            "agent_cpu_per_gpu": 1 / ratio_new,
            "cpu_socket_uplift_same_gpu_fleet": cpu_intensity_uplift,
            "note": "동일 GPU 규모에서 CPU 소켓 수요 최대 ~6배. 실제는 mix·utilization으로 할인.",
        },
        "muse_nv_bridge": {
            "dau": 100_000_000,
            "gpu_units": (200_000, 390_000),
            "nvl72_racks": (2800, 5500),
            "nv_one_time_B": (7.0, 19.0),
            "per_1m_dau_nv_M": (70, 190),  # $M
            "note": "씨티의 Muse 1억 DAU → NV 일회성 $70~190억. CPU TAM 상향의 ‘수요 증거’ 브리지이지 CPU 매출 직접치 아님.",
        },
        "judgment": (
            "세 경로는 모두 2025~$26–29B에서 출발해 2030년 4.5~10배. "
            "투자 결정은 ‘$300B 여부’가 아니라 (1) CPU intensity uplift가 지속되는지 "
            "(2) Agentic이 DRAM/NAND 비트 20%+를 가져가는지 (미즈호)다."
        ),
    }


# ── 3) Memory valuation model ────────────────────────────────────────────


@dataclass
class Name:
    ticker: str
    price: float  # USD or KRW만원 depending on unit
    unit: str
    eps_26: float | None
    eps_27: float | None
    per_26: float | None
    per_27: float | None
    note: str = ""


def build_valuation() -> dict:
    fx = 1340.0
    names = [
        Name("Sandisk", 1660.46, "USD", None, 230.0, None, 7.2),
        Name("Micron FY27", 1045.56, "USD", None, 165.0, None, 6.3, "FY27=26/9~27/8"),
        Name("Micron CY27", 1045.56, "USD", None, 180.0, None, 5.8, "컨센"),
        Name("SKH ADR", 182.56, "USD", None, None, 7.0, 5.5, "244.6만원@1340"),
        Name("SKH 본주", 178.4, "KRW만", 349.0, 444.0, 5.1, 4.0, "EPS 천원"),
        Name("삼성전자", 27.3, "KRW만", 47.9, 67.9, 5.7, 4.0, "EPS 천원"),
    ]

    mu_cy27_per = 5.8
    rows = []
    for n in names:
        discount_to_mu = None
        if n.per_27 is not None and n.unit == "KRW만":
            discount_to_mu = n.per_27 / mu_cy27_per - 1
        elif n.ticker == "SKH ADR" and n.per_27:
            discount_to_mu = n.per_27 / mu_cy27_per - 1
        rows.append(
            {
                "ticker": n.ticker,
                "price": n.price,
                "unit": n.unit,
                "eps_26": n.eps_26,
                "eps_27": n.eps_27,
                "per_26": n.per_26,
                "per_27": n.per_27,
                "discount_to_mu_cy27": discount_to_mu,
                "note": n.note,
            }
        )

    # ADR premium reverse — 원문이 182.56×1340=244.6만원으로 표기 (주당 환산 관행)
    adr_krw = 244.6
    local = 178.4
    premium = adr_krw / local - 1
    implied = {p: adr_krw / (1 + p) for p in (0.37, 0.30, 0.20, 0.10, 0.0)}

    # FX sensitivity on KR names: 1480 → 1370 ≈ -7.4% on USD-linked EPS if full pass-through
    fx_hi, fx_lo = 1480.0, 1370.0
    fx_shock = fx_lo / fx_hi - 1  # -7.43%
    # Source says 원화강세 5~10% => 주식 6~12% — use elasticities 1.2x
    fx_to_equity = {0.05: -0.06, 0.10: -0.12}

    # Conservative ceiling: 26Y earnings, 0 growth to 28, PER 4~8 band
    skh_26_eps = 349.0  # 천원 → 주가 만원 = PER * EPS(천원)/10? 
    # price(만원) = PER * EPS(천원) / 10? 178.4 = 5.1 * 349 / 10 → 5.1*34.9=177.99 ✓
    # so price_man = PER * eps_k / 10
    def price_from_per(eps_k: float, per: float) -> float:
        return per * eps_k / 10.0

    skh_band = {per: price_from_per(349.0, per) for per in (4, 5, 6, 7, 8)}
    sec_band = {per: price_from_per(47.9, per) for per in (4, 5, 6, 7, 8)}
    # Source conservative 209~244만 / 28.7~33.5만 at ~7x on 26Y
    # 7*349/10=244.3, 6*349/10=209.4 — matches 209~244
    # 7*47.9/10=33.53, 6*47.9/10=28.74 — matches

    # 27Y fair if re-rate toward MU CY27 5.8x (still discount scenarios)
    skh_27_targets = {
        "at_mu_parity_5.8x": price_from_per(444.0, 5.8),
        "at_15pct_discount": price_from_per(444.0, 5.8 * 0.85),
        "at_31pct_discount": price_from_per(444.0, 5.8 * 0.69),
        "at_current_4.0x": price_from_per(444.0, 4.0),
    }
    sec_27_targets = {
        "at_mu_parity_5.8x": price_from_per(67.9, 5.8),
        "at_15pct_discount": price_from_per(67.9, 5.8 * 0.85),
        "at_31pct_discount": price_from_per(67.9, 5.8 * 0.69),
        "at_current_4.0x": price_from_per(67.9, 4.0),
    }

    # MU street TP debate
    mu_price = 1045.56
    mu_tp_davidson = 3000.0
    mu_tp_cons_avg = 1572.0  # 9 brokers post-print; with 3000 → 1714
    mu_tp_cons_ex = 1714.0
    mu_fy27_eps = 165.0
    mu_cy27_eps = 180.0

    def implied_per(tp, eps):
        return tp / eps

    approach_low = mu_tp_cons_avg * 0.70
    approach_high = mu_tp_cons_avg * 0.80
    approach_alt_low = 1714 * 0.70
    approach_alt_high = 1714 * 0.80

    return {
        "asof": "2026-10-06 close",
        "fx_spot": fx,
        "names": rows,
        "adr": {
            "adr_usd": 182.56,
            "adr_krw_man": round(adr_krw, 1),
            "local_man": local,
            "premium": premium,
            "implied_local_by_premium": {f"{int(p*100)}%": round(v, 1) for p, v in implied.items()},
        },
        "fx_sensitivity": {
            "broker_fx_1480_to_1370": fx_shock,
            "broker_eps_haircut_approx": "~10% 컨센 하향 여지 (원문)",
            "equity_beta_to_krw": fx_to_equity,
        },
        "conservative_26y_no_growth": {
            "skh_man": {str(k): round(v, 1) for k, v in skh_band.items()},
            "sec_man": {str(k): round(v, 1) for k, v in sec_band.items()},
            "source_band": {"skh": "209~244만@6~7x", "sec": "28.7~33.5만@6~7x"},
        },
        "reevaluation_27y": {
            "skh": {k: round(v, 1) for k, v in skh_27_targets.items()},
            "sec": {k: round(v, 1) for k, v in sec_27_targets.items()},
            "upside_skh_from_178": {
                k: round(v / 178.4 - 1, 3) for k, v in skh_27_targets.items()
            },
            "upside_sec_from_273": {
                k: round(v / 27.3 - 1, 3) for k, v in sec_27_targets.items()
            },
        },
        "mu_tp_debate": {
            "spot": mu_price,
            "davidson_tp": mu_tp_davidson,
            "davidson_upside": mu_tp_davidson / mu_price - 1,
            "davidson_per_on_fy27_165": implied_per(mu_tp_davidson, mu_fy27_eps),
            "davidson_per_on_cy27_180": implied_per(mu_tp_davidson, mu_cy27_eps),
            "cons_avg_9": mu_tp_cons_avg,
            "cons_avg_incl_3000": mu_tp_cons_ex,
            "cons_implied_per_cy27": implied_per(mu_tp_cons_avg, mu_cy27_eps),
            "approach_on_1572_20_30pct": (round(approach_low), round(approach_high)),
            "approach_on_1714_20_30pct": (round(approach_alt_low), round(approach_alt_high)),
            "judgment": (
                f"Davidson {implied_per(mu_tp_davidson, mu_fy27_eps):.1f}x(FY27 EPS165)≈원문~19x. "
                f"컨센 TP ${mu_tp_cons_avg:.0f}는 CY27 EPS180 기준 ~{implied_per(mu_tp_cons_avg, mu_cy27_eps):.1f}x. "
                "이익보다 배수가 싸움. Approach 앵커는 1200~1371."
            ),
        },
        "op_eps_27": {
            "skh": {"op_26": 265, "op_27": 392, "eps_26_k": 349, "eps_27_k": 444, "op_yoy": 392 / 265 - 1, "eps_yoy": 444 / 349 - 1},
            "sec": {"op_26": 388, "op_27": 555, "eps_26_k": 47.9, "eps_27_k": 67.9, "op_yoy": 555 / 388 - 1, "eps_yoy": 67.9 / 47.9 - 1},
        },
    }


# ── 4) CapEx paradox (cost ↓ × usage ↑) ───────────────────────────────────


def build_capex_paradox() -> dict:
    """Net enterprise AI spend = tasks × cost_per_task.
    Also infra demand ∝ tokens/compute, not $ spend."""
    scenarios = []
    for name, cost_chg, task_chg in (
        ("Bear_efficiency", -0.50, 1.5),   # cost half, tasks +50%
        ("Base", -0.40, 3.0),
        ("Bull_agentic", -0.50, 8.0),
        ("Super_agent", -0.60, 20.0),
    ):
        net_spend = (1 + cost_chg) * task_chg  # relative to t0=1
        # compute/tokens roughly track tasks more than $ if price falls
        compute_proxy = task_chg
        scenarios.append(
            {
                "name": name,
                "cost_per_task_chg": cost_chg,
                "tasks_chg_multiple": task_chg,
                "enterprise_ai_spend_multiple": round(net_spend, 2),
                "infra_compute_proxy_multiple": round(compute_proxy, 2),
                "divergence_infra_vs_spend": round(compute_proxy / net_spend, 2),
            }
        )
    return {
        "identity": "Spend ∝ tasks × cost_per_task; Infra ∝ tasks × compute_per_task",
        "verdicts_from_source": {
            "경제성분석": "타당",
            "중국AI_가격만큼_안쌈": "타당",
            "미국AI_전반_더쌈": "부분타당",
            "기업지출_비폭증": "부분타당",
            "그러므로_CapEx_과도": "비약",
        },
        "scenarios": scenarios,
        "judgment": (
            "기업 $지출이 플랫/감소해도 infra compute는 tasks와 함께 증가 가능. "
            "‘지출 안 늘어남’을 CapEx 피크로 번역하는 것이 비약인 이유."
        ),
    }


# ── 5) PSK optionality score ─────────────────────────────────────────────


def build_psk() -> dict:
    return {
        "tp_hanwha_man": 27.0,
        "stance": "이익 컨센 상회가 TP 상향을 정당화. 수치 뒷받침 시 차익 서둘지 않음.",
        "stack": {
            "CoWoS_HBM": {"tool": "Reflow", "status": "기존 성장"},
            "OSAT": {"tool": "Descum", "status": "기존 성장"},
            "EMIB": {"tool": "Reflow+Descum", "status": "레벨업 옵션", "why": "Intel CAPA(NM·Penang) + CoWoS 대안"},
        },
        "positioning": {
            "existing": "눌림목 분할; 안전마진~30%면 가산",
            "risk": "손절 칼같이 (분할매수 전제)",
        },
        "model_note": (
            "정량 EPS/매출 컨센이 PDF에 없어 배수 모델 불가. "
            "질적 옵션 가치 = P(EMIB양산)×(Reflow+Descum 동시 침투). "
            "확인 지표: Intel EMIB CAPA 가이던스, PSK EMIB 매출 믹스 공시."
        ),
    }


# ── 6) Midterm policy tree ───────────────────────────────────────────────


def build_midterm() -> dict:
    return {
        "false_frame": "친환경 vs 화석연료 / 반-데이터센터",
        "true_frame": "전력 수급 안정 + affordability",
        "branches": [
            {
                "branch": "R_senate_hold",
                "policy": "원전·가스·ESS·가스망 확대 지속",
                "ira": "현행 축소 기조 유지 가능",
                "ai_power": "공급 확대 = DC 친화",
            },
            {
                "branch": "D_house_or_better",
                "policy": "신재생·원전 + 비용완화",
                "ira": "전면복원 < 보조금·세액공제 일부 연장/수정",
                "ai_power": "반-DC 아님; 가격 안정이 제약",
            },
        ],
        "investable": "원전·가스터빈·ESS·신재생·송배전 — 선거 결과와 무관하게 AI 전력수요 대응 투자는 지속 가능성 높음",
    }


# ── assemble ─────────────────────────────────────────────────────────────


def run_model() -> dict:
    muse_rows = build_muse_grid()
    muse = muse_insights(muse_rows)
    cpu = build_cpu_tam()
    val = build_valuation()
    capex = build_capex_paradox()
    psk = build_psk()
    mid = build_midterm()

    # Cross-model scoreboard
    scoreboard = {
        "memory_cheap_vs_history": {
            "signal": "본주 27Y PER 4.0x vs 과거 사이클 4~8x 하단",
            "strength": "high",
        },
        "agentic_diffusion": {
            "signal": "CPU TAM 상향 + Muse DRAM 비대칭 + Mizuho bit share 22~30%",
            "strength": "high",
        },
        "capex_not_peaking_from_token_price": {
            "signal": "Spend/Infra divergence in agentic scenarios",
            "strength": "high",
        },
        "cpu_300b_as_point_estimate": {
            "signal": "Oct vs May bridge implies ~76% agentic share if non-agentic fixed — fragile",
            "strength": "low_as_number_high_as_direction",
        },
        "psk_emib": {
            "signal": "Qualitative call option; needs CAPA/mix confirmation",
            "strength": "medium",
        },
        "midterm_anti_dc": {
            "signal": "Falsified frame in source; power supply is the constant",
            "strength": "high_as_frame",
        },
    }

    thesis = (
        f"프레임: TCO·Agent 확산. "
        f"CPU 2030은 {usd_b(131.5)}→{usd_b(209)}~{usd_b(300)} 밴드. "
        f"Muse 1억 DAU·활성15%에서 8GB×N은 물리 DRAM을 약 {muse['overstate']['at_base']:.1f}배 과대. "
        f"삼전닉스 27Y PER 4.0x; MU 패리티(5.8x) 시 하이닉스≈{val['reevaluation_27y']['skh']['at_mu_parity_5.8x']:.0f}만 "
        f"(현재 대비 {val['reevaluation_27y']['upside_skh_from_178']['at_mu_parity_5.8x']*100:.0f}%). "
        f"기업 AI $지출 정체≠인프라 피크."
    )

    return {
        "date": "2026-10-07",
        "thesis": thesis,
        "muse": {"insights": muse, "grid_n": len(muse_rows), "grid": muse_rows},
        "cpu": cpu,
        "valuation": val,
        "capex": capex,
        "psk": psk,
        "midterm": mid,
        "scoreboard": scoreboard,
    }


def render_precise_md(m: dict) -> str:
    muse = m["muse"]["insights"]
    base = muse["anchor_1e8_dau"]["base_active15_current"]
    mid = muse["anchor_1e8_dau"]["mid_active15_upgrade"]
    bull = muse["anchor_1e8_dau"]["bull_active30_complex"]
    bear = muse["anchor_1e8_dau"]["bear_active5_current"]
    cpu = m["cpu"]
    val = m["valuation"]
    capex = m["capex"]

    lines = [
        "# 10/7 투자 인사이트 — 정밀 모델 증류",
        "",
        "매수·매도 권유 아님. 원문 PDF 6 + paste 숫자만으로 닫힌 식.",
        "",
        "## 0. 한 줄",
        "",
        m["thesis"],
        "",
        "## 1. CapEx 역설 (Spend ≠ Infra)",
        "",
        f"- 항등식: `{capex['identity']}`",
        f"- 판정: CapEx 과도 = **{capex['verdicts_from_source']['그러므로_CapEx_과도']}**",
        "",
        "| 시나리오 | 비용/task | task 배수 | 기업$지출 | 인프라compute | 괴리(infra/spend) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for s in capex["scenarios"]:
        lines.append(
            f"| {s['name']} | {s['cost_per_task_chg']:+.0%} | {s['tasks_chg_multiple']:.1f}x | "
            f"{s['enterprise_ai_spend_multiple']:.2f}x | {s['infra_compute_proxy_multiple']:.1f}x | {s['divergence_infra_vs_spend']:.2f}x |"
        )
    lines += ["", f"→ {capex['judgment']}", "", "## 2. Muse DRAM 수요 모델", "", f"- 식: `{muse['formula']}`", f"- 금지: `{muse['not_formula']}`", "",
              "| 시나리오 (DAU 1억) | 활성 | used GB | Physical PB | 8GB×N 과대배수 |",
              "|---|---:|---:|---:|---:|"]
    for label, r in (
        ("Bear", bear),
        ("Base", base),
        ("Upgrade", mid),
        ("Bull", bull),
    ):
        lines.append(
            f"| {label}·{r['name']} | {r['active_ratio']:.0%} | {r['used_gb']:.0f} | "
            f"{r['physical_PB']:.1f} | {r['naive_overstate_vs_physical']:.2f}x |"
        )
    lines += ["", f"→ {muse['implication']}", "", "## 3. 서버 CPU TAM 경로", "",
              "| 하우스 | 2025 | 2026E* | 2028E* | 2030 | CAGR | 5년배수 | Agentic |",
              "|---|---:|---:|---:|---:|---:|---:|---|"]
    for p in cpu["paths"]:
        ag = ""
        if p["agentic_usd_2030"]:
            ag = f"${p['agentic_usd_2030']:.0f}B ({p['agentic_share_2030']:.0%})"
        elif p["name"] == "Citi Oct":
            ag = "미제시"
        lines.append(
            f"| {p['name']} | {p['y2025']:.1f} | {p['y2026_implied']:.1f} | {p['y2028_implied']:.1f} | "
            f"{p['y2030']:.0f} | {p['cagr_pct']} | {p['multiple_5y']:.1f}x | {ag} |"
        )
    lines += [
        "",
        "- \\*2026/28은 각 경로 CAGR 기계 역산 (Citi가 2026을 직접 준 것 아님).",
        f"- Oct vs May Δ2030 = **${cpu['bridge_oct_vs_may']['delta_2030_B']:.1f}B**. "
        f"{cpu['bridge_oct_vs_may']['if_non_agentic_fixed_at_may']['note']}",
        f"- CPU:GPU 1:{int(1/cpu['cpu_gpu_ratio']['chatbot_cpu_per_gpu'])} → 1:1 이면 동일 GPU 대비 CPU 소켓 최대 "
        f"**{cpu['cpu_gpu_ratio']['cpu_socket_uplift_same_gpu_fleet']:.0f}x**.",
        (
            f"- Muse→NV 브리지: 1억 DAU → GPU "
            f"{cpu['muse_nv_bridge']['gpu_units'][0]:,}~{cpu['muse_nv_bridge']['gpu_units'][1]:,} · "
            f"NV 일회성 ${cpu['muse_nv_bridge']['nv_one_time_B'][0]:.0f}~{cpu['muse_nv_bridge']['nv_one_time_B'][1]:.0f}B "
            f"(CPU 매출 직접치 아님)."
        ),
        "",
        f"→ {cpu['judgment']}",
        "",
        "## 4. 메모리 밸류 · 재평가 맵",
        "",
        f"기준: {val['asof']}, FX {val['fx_spot']:.0f}원.",
        "",
        "| 종목 | 가격 | 27Y PER | vs MU CY27 |",
        "|---|---:|---:|---:|",
    ]
    for n in val["names"]:
        d = n["discount_to_mu_cy27"]
        d_s = f"{d:.0%}" if d is not None else "—"
        per = n["per_27"] if n["per_27"] is not None else "—"
        lines.append(f"| {n['ticker']} | {n['price']} {n['unit']} | {per} | {d_s} |")

    lines += [
        "",
        f"- ADR 프리미엄 **{val['adr']['premium']:.0%}** (ADR {val['adr']['adr_krw_man']}만 / 본주 {val['adr']['local_man']}만).",
        f"  프리미엄 축소 시 본주 함의: " + ", ".join(f"{k}→{v}만" for k, v in val["adr"]["implied_local_by_premium"].items() if k != "37%"),
        f"- FX: 1480→1370 ≈ {val['fx_sensitivity']['broker_fx_1480_to_1370']:.1%} EPS 압력; 원화+5~10% → 주식 {val['fx_sensitivity']['equity_beta_to_krw'][0.05]:.0%}~{val['fx_sensitivity']['equity_beta_to_krw'][0.10]:.0%}.",
        "",
        "### 26Y 이익 동결 + PER 4~8x (보수 천장)",
        "",
        f"- SKH: " + ", ".join(f"{k}x→{v}만" for k, v in val["conservative_26y_no_growth"]["skh_man"].items()),
        f"- 삼성: " + ", ".join(f"{k}x→{v}만" for k, v in val["conservative_26y_no_growth"]["sec_man"].items()),
        f"- 원문 밴드: {val['conservative_26y_no_growth']['source_band']}",
        "",
        "### 27Y 재평가 (EPS 성장 인정 시)",
        "",
        f"- SKH 현재 178.4만 → MU패리티 {val['reevaluation_27y']['skh']['at_mu_parity_5.8x']}만 "
        f"({val['reevaluation_27y']['upside_skh_from_178']['at_mu_parity_5.8x']:+.0%}), "
        f"15%할인 {val['reevaluation_27y']['skh']['at_15pct_discount']}만 "
        f"({val['reevaluation_27y']['upside_skh_from_178']['at_15pct_discount']:+.0%}), "
        f"현 할인31% 유지 {val['reevaluation_27y']['skh']['at_31pct_discount']}만 "
        f"({val['reevaluation_27y']['upside_skh_from_178']['at_31pct_discount']:+.0%}).",
        f"- 삼성 현재 27.3만 → 패리티 {val['reevaluation_27y']['sec']['at_mu_parity_5.8x']}만 "
        f"({val['reevaluation_27y']['upside_sec_from_273']['at_mu_parity_5.8x']:+.0%}) / "
        f"15%할인 {val['reevaluation_27y']['sec']['at_15pct_discount']}만 / "
        f"31%할인 {val['reevaluation_27y']['sec']['at_31pct_discount']}만.",
        f"- 27Y OP/EPS: SKH OP {val['op_eps_27']['skh']['op_yoy']:+.0%}, EPS {val['op_eps_27']['skh']['eps_yoy']:+.0%}; "
        f"삼성 OP {val['op_eps_27']['sec']['op_yoy']:+.0%}, EPS {val['op_eps_27']['sec']['eps_yoy']:+.0%}.",
        "",
        "### MU TP 논쟁",
        "",
        f"- Spot ${val['mu_tp_debate']['spot']:.0f} / Davidson ${val['mu_tp_debate']['davidson_tp']:.0f} "
        f"({val['mu_tp_debate']['davidson_upside']:+.0%}, FY27 EPS165 기준 **{val['mu_tp_debate']['davidson_per_on_fy27_165']:.1f}x**, "
        f"CY27 EPS180 기준 {val['mu_tp_debate']['davidson_per_on_cy27_180']:.1f}x).",
        f"- 컨센 평균 ${val['mu_tp_debate']['cons_avg_9']:.0f} (3000 포함 시 ${val['mu_tp_debate']['cons_avg_incl_3000']:.0f}).",
        f"- Approach(−20~30%): ${val['mu_tp_debate']['approach_on_1572_20_30pct'][0]}~{val['mu_tp_debate']['approach_on_1572_20_30pct'][1]} "
        f"또는 ${val['mu_tp_debate']['approach_on_1714_20_30pct'][0]}~{val['mu_tp_debate']['approach_on_1714_20_30pct'][1]}.",
        f"- {val['mu_tp_debate']['judgment']}",
        "",
        "## 5. PSK · 중간선거 (옵션/프레임)",
        "",
        f"- PSK: 한화 TP {m['psk']['tp_hanwha_man']:.0f}만. {m['psk']['model_note']}",
        f"- 중간선거: 거짓 프레임 `{m['midterm']['false_frame']}` → 참 프레임 `{m['midterm']['true_frame']}`.",
        f"- {m['midterm']['investable']}",
        "",
        "## 6. 스코어보드",
        "",
        "| 테제 | 강도 | 시그널 |",
        "|---|---|---|",
    ]
    for k, v in m["scoreboard"].items():
        lines.append(f"| {k} | {v['strength']} | {v['signal']} |")
    lines += [
        "",
        "## 7. 의사결정 규칙",
        "",
        "1. CapEx 논쟁은 **task×cost**와 **task×compute**를 분리해서 말할 것.",
        "2. Muse/Agent DRAM은 **활성률·used_GB·sharing** 세 레버 민감도로 말할 것.",
        "3. CPU는 **$300B 점추정 금지**, $131~300B 밴드 + CPU intensity uplift로 말할 것.",
        "4. 삼전닉스는 **4.0x 현 배수 vs 할인율 축소 시나리오**로 업사이드 구간을 말할 것.",
        "5. MU는 **19x 금지**, Approach 1200~1371을 상단 토론 앵커로.",
        "6. PSK는 EMIB 매출 믹스 확인 전 **질적 옵션**으로만.",
        "",
    ]
    return "\n".join(lines)


def render_chat(m: dict) -> str:
    """채팅용 — 표 포함 정밀 요약."""
    return render_precise_md(m)


def main():
    m = run_model()
    OUT.mkdir(parents=True, exist_ok=True)
    # grid is large — keep full in model.json, slim for insights
    slim = {k: v for k, v in m.items() if k != "muse"}
    slim["muse"] = {"insights": m["muse"]["insights"], "grid_n": m["muse"]["grid_n"]}
    (OUT / "model.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    md = render_precise_md(m)
    (OUT / "투자인사이트.md").write_text(md, encoding="utf-8")
    (OUT / "chat_summary.md").write_text(md, encoding="utf-8")
    print(md)
    print(f"\n[model] grid={m['muse']['grid_n']} paths={len(m['cpu']['paths'])} → {OUT}")


if __name__ == "__main__":
    main()
