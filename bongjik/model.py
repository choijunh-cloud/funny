# -*- coding: utf-8 -*-
"""
봉직 통합 모델 v3 — 응급의학과 공고 평가
========================================
12곳 주관 레이더부터 72프로필 실측 마스터·8월 홀드아웃까지를
한 파이프라인으로 묶는다.

  공고 → 위생 → 거부 → 스크리닝/확정 게이트 → 시장점수(프레임 A/B)
       → 정성 S1–S6 → 개인점수(옥수동) → 잔차·목표밴드 → 카드

사용:
  python3 -m bongjik.model --report
  python3 -m bongjik.model --targets
  python3 -m bongjik.model --posting
  python3 -m bongjik.model --holdout
  python3 -m bongjik.model --stats
  python3 -m bongjik.model --estimate --zone 서울 --backup 강 --pp 2000 --hours 120
"""
from __future__ import annotations

import json
import math
import random
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
JSON_POOL = DATA / "master_pool.json"
OVERLAYS = DATA / "overlays.json"
POSTINGS = DATA / "postings.json"
LINEAGE = DATA / "lineage.json"
MASTER_XLSX = DATA / "응급의학과_봉직공고_최종마스터.xlsx"

ANCHOR_ADMIT = 0.354
WON_PER_ADMIT = 3
CUT_UNIT = 13.3
CUT_SCREEN = 11.1
CUT_CONFIRM = 13.1
CUT_BAND = (13.1, 13.3)
SAFE_SCREEN = 6.3
SAFE_FLOOR = 5.5
SAFE_COLLAPSE = 4.0
WLB_SIGNAL = 5.4
L3_SAFE, L3_WLB = 5.5, 5.4
HOURS_HARD = 130
HOURS_RED = 168
PPH_RED = 2.0
VOL_CUT = 15000
VOL_TRAP = 8000
TIER_RULE = [(1, "S"), (9, "A"), (12, "B"), (20, "C")]
EXPECTED_POOL = (70, 80)

# v5.1 시트16 가중 — 프레임 B
V51_W = dict(safe=0.31, effload=0.20, pay_v51=0.13, sys=0.13, wlb=0.12, acu_val=0.11)

_norm = lambda s: re.sub(r"[\s\-–—·]", "", str(s))

OVERRIDES = {
    "나사렛국제(현직)": dict(cash2=2800, incen=291, incen_src="실측"),
    "진주경상대": dict(cash2=3367, incen=None, incen_src="실측포함"),
    "김포우리병원": dict(cash2=2900, incen=None, incen_src="실측포함"),
    "인천현대유비스": dict(cash2=2450, incen=None, incen_src="실측포함"),
    "오산한국병원": dict(cash2=2398, incen=None, incen_src="실측포함"),
    "안양샘병원": dict(cash2=2073, incen=None, incen_src="실측포함"),
    "수원의료원": dict(cash2=2184, incen=None, incen_src="실측포함"),
    "국립소방병원": dict(cash2=2600, incen=None, incen_src="실측포함"),
    "안동병원": dict(cash2=2135, incen=None, incen_src="실측포함"),
}
OVERRIDES_NORM = {_norm(k): v for k, v in OVERRIDES.items()}

PROFILES = {
    "P1_균등": dict(safe=0.20, wlb=0.20, effload=0.20, sys=0.20, pay2=0.20),
    "P2_QOL": dict(safe=0.30, wlb=0.25, effload=0.25, sys=0.10, pay2=0.10),
    "P3_균형": dict(safe=0.25, wlb=0.25, effload=0.20, sys=0.10, pay2=0.20),
    "P4_현금": dict(safe=0.25, wlb=0.20, effload=0.15, sys=0.10, pay2=0.30),
}
PROFILES_NOPAY = {
    "N1": dict(safe=0.25, wlb=0.25, effload=0.25, sys=0.25),
    "N2": dict(safe=0.35, wlb=0.30, effload=0.25, sys=0.10),
    "N3": dict(safe=0.30, wlb=0.30, effload=0.25, sys=0.15),
}

ZONE_COMMUTE = {"서울": 2, "수도권": 0, "광역시": -1, "강원": -3, "제주": -5, "지방": -5}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_overlays(path=None):
    return load_json(path or OVERLAYS)


def load_postings(path=None):
    return load_json(path or POSTINGS)


def load_lineage(path=None):
    return load_json(path or LINEAGE)


def load_pool(path=None):
    if path:
        p = Path(path)
        if p.suffix.lower() == ".json":
            raw = load_json(p)
            return [dict(d) for d in raw["pool"]], raw.get("meta", {})
        return _load_xlsx(p)
    if JSON_POOL.exists():
        raw = load_json(JSON_POOL)
        return [dict(d) for d in raw["pool"]], raw.get("meta", {})
    if MASTER_XLSX.exists():
        return _load_xlsx(MASTER_XLSX)
    raise FileNotFoundError("master_pool.json 또는 마스터 엑셀이 필요합니다")


def _load_xlsx(path):
    from bongjik.extract import _load_xlsx as _ex
    return _ex(path)


# ── 위생 ─────────────────────────────────────────────
def apply_corrections(pool, path=None):
    """시트5·v4.8·시트38·8월 실측 정정을 인센 계산 전에 덮어쓴다."""
    p = Path(path) if path else DATA / "corrections.json"
    if not p.exists():
        return pool
    cash = load_json(p).get("cash", {})
    for d in pool:
        patch = cash.get(d["h"])
        if not patch:
            continue
        for k, v in patch.items():
            if k == "note":
                d["corr_note"] = v
            else:
                d[k] = v
        if patch.get("cash2") is not None:
            d["cash"] = patch["cash2"]
    return pool


def apply_hygiene(pool, ov):
    exclude = set(ov.get("exclude_from_rank", []))
    provisional = set(ov.get("provisional_volume", []))
    for d in pool:
        d["rankable"] = d["h"] not in exclude
        if d["h"] in provisional:
            d["tot"] = None
            d["pp"] = None
            d["volume_note"] = "잠정·미확정"
        d["scenario"] = False
    for members in ov.get("scenario_groups", {}).values():
        for name in members:
            for d in pool:
                if d["h"] == name:
                    d["scenario"] = True
    return pool


def infer_incen_included(d):
    """시트1 통장이 인센포함 열에 붙어 있으면 모델 입원인센을 재가산하지 않는다."""
    cash, base, inc = d.get("cash"), d.get("net_base_eok"), d.get("net_inc_eok")
    if cash is None or inc is None or base is None:
        return False
    inc_m = inc * 10000 / 12
    base_m = base * 10000 / 12
    if abs(inc_m - base_m) < 30:
        return False
    return abs(cash - inc_m) + 20 < abs(cash - base_m)


def apply_incentive(pool):
    for d in pool:
        ov = OVERRIDES_NORM.get(_norm(d["h"]), {})
        d.update({k: v for k, v in ov.items() if v is not None or k == "incen"})
        d.setdefault("incen_src", "모델추정")
        if not d.get("pp") or d["pp"] <= 0:
            d["mpat"] = None
            d.setdefault("incen", None)
            if "cash2" not in d:
                d["cash2"] = d.get("cash")
            d["pp2"] = None
            d["incomplete"] = True
            continue
        d["incomplete"] = False
        d["mpat"] = d["pp"] / 12
        if d.get("incen_src") in ("실측", "실측포함") and "cash2" in d:
            if d.get("incen") is None:
                d["incen"] = 0
            d["pp2"] = d["cash2"] / d["mpat"]
            continue
        if infer_incen_included(d) and "cash2" not in d:
            d["incen"] = 0
            d["incen_src"] = "시트인센포함"
            d["cash2"] = d["cash"]
            d["pp2"] = d["cash2"] / d["mpat"]
            continue
        if "incen" not in d or (d["incen"] is None and "cash2" not in d):
            acu = d.get("acu") or 1.0
            d["incen"] = d["mpat"] * ANCHOR_ADMIT * acu * WON_PER_ADMIT
        if "cash2" not in d:
            d["cash2"] = (d.get("cash") or 0) + (d.get("incen") or 0)
        d["pp2"] = d["cash2"] / d["mpat"]
    return pool


def spendable_cash(d, ov):
    rtype = ov.get("retirement", {}).get(d["h"], "unknown")
    cash = d.get("cash2") or d.get("cash") or 0
    d["retire_type"] = rtype
    d["cash_spendable"] = cash * 12 / 13 if rtype == "dc_in_net" else cash
    return d


def compute_axes(pool, lo=None, hi=None):
    vals = [d["cash2"] for d in pool if d.get("cash2") is not None]
    lo = min(vals) if lo is None else lo
    hi = max(vals) if hi is None else hi
    span = hi - lo
    for d in pool:
        if d.get("cash2") is None:
            d["pay2_raw"] = d["pay2"] = None
            d["f5"] = None
            continue
        d["pay2_raw"] = 5.0 if span <= 0 else (d["cash2"] - lo) / span * 10
        d["pay2"] = max(0.0, min(10.0, d["pay2_raw"]))
        need = ("safe", "pay2", "sys", "wlb", "effload")
        if all(d.get(k) is not None for k in need):
            d["f5"] = d["safe"] + d["pay2"] + d["sys"] + d["wlb"] + d["effload"]
        else:
            d["f5"] = None
        if all(d.get(k) is not None for k in V51_W):
            d["v51"] = sum(d[k] * w for k, w in V51_W.items()) * 10
        else:
            d["v51"] = None
    return lo, hi


def _rank_by(pool, key):
    ranked = sorted(pool, key=lambda x: (-key(x), x["h"]))
    return {id(d): i + 1 for i, d in enumerate(ranked)}


def composite(pool, profiles=PROFILES, prefix=""):
    usable = [
        d for d in pool
        if d.get("rankable") and d.get("pay2") is not None
        and all(d.get(k) is not None for k in ("safe", "wlb", "effload", "sys"))
    ]
    for n, w in profiles.items():
        for d in usable:
            d[prefix + n] = sum(d[k] * wt for k, wt in w.items()) * 10
    rks = {n: _rank_by(usable, lambda x, n=n: x[prefix + n]) for n in profiles}
    for d in usable:
        d[prefix + "ranks"] = [rks[n][id(d)] for n in profiles]
        d[prefix + "meanrank"] = sum(d[prefix + "ranks"]) / len(profiles)
        d[prefix + "score"] = sum(d[prefix + n] for n in profiles) / len(profiles)
    fin = sorted(usable, key=lambda d: (d[prefix + "meanrank"], -d[prefix + "score"], d["h"]))
    for i, d in enumerate(fin, 1):
        d[prefix + "comp_rank"] = i
        d[prefix + "tier"] = next((t for lim, t in TIER_RULE if i <= lim), "-")
    for d in pool:
        if prefix + "comp_rank" not in d:
            d[prefix + "comp_rank"] = None
            d[prefix + "tier"] = None
            d[prefix + "score"] = None
    return fin


def rank_frame_b(pool):
    usable = [d for d in pool if d.get("rankable") and d.get("v51") is not None]
    fin = sorted(usable, key=lambda d: (-d["v51"], d["h"]))
    for i, d in enumerate(fin, 1):
        d["v51_rank"] = i
    for d in pool:
        d.setdefault("v51_rank", None)
    return fin


def zone_group(zone):
    if zone in ("서울", "수도권", "광역시"):
        return zone
    return "지방+"


def backup_group(backup):
    if backup in ("최강", "강"):
        return "강+"
    if backup == "중":
        return "중"
    return "약"


def volume_status(d, ov):
    rescue = ov.get("volume_rescue", {}).get(d["h"]) or d.get("volume_rescue")
    tot = d.get("tot")
    if tot is None:
        return ("rescued", rescue or "연환자미확정") if rescue else ("unknown", "연환자 결측")
    if tot >= VOL_CUT:
        return "ok", None
    if rescue and "경계" in str(rescue):
        return "fail", rescue
    if rescue:
        return "rescued", rescue
    if tot < VOL_TRAP and (d.get("backup") == "약" or (d.get("safe") or 0) < SAFE_FLOOR):
        return "trap", "한산+약백업"
    return "fail", f"연환자 {tot:.0f}<{VOL_CUT}"


def gates(d, ov):
    pp2, safe, hrs = d.get("pp2"), d.get("safe"), d.get("hrs")
    pph = d.get("pph")
    g = {
        "단가스크리닝": pp2 is not None and pp2 >= CUT_SCREEN,
        "단가확정": pp2 is not None and pp2 >= CUT_CONFIRM,
        "단가13.3": pp2 is not None and pp2 >= CUT_UNIT,
        "안전스크리닝": safe is not None and safe >= SAFE_SCREEN,
        "안전플로어": safe is not None and safe >= SAFE_FLOOR,
        "워라밸신호": (d.get("wlb") or 0) >= WLB_SIGNAL,
        "월시간": hrs is not None and hrs <= HOURS_HARD,
        "시간당": pph is not None and pph <= PPH_RED,
    }
    g["스크리닝"] = g["안전스크리닝"] and g["단가스크리닝"]
    g["확정"] = g["안전플로어"] and g["단가확정"]
    vol, vol_why = volume_status(d, ov)
    g["연환자"] = vol in ("ok", "rescued")
    g["무결점"] = g["확정"] and g["연환자"]
    d["vol_status"] = vol
    d["vol_why"] = vol_why
    return g


def veto_reason(d, ov):
    if d["h"] in ov.get("avoid", []):
        return "회피리스트"
    if d.get("legal") == "D":
        return "법적D"
    if d.get("hrs") is not None and d["hrs"] >= HOURS_RED:
        return "월168h+"
    if d.get("safe") is not None and d["safe"] < SAFE_COLLAPSE:
        return "안전붕괴"
    tot = d.get("tot")
    if tot is not None and tot < VOL_TRAP and d.get("backup") == "약":
        return "한산약백업"
    if d.get("er") and "ER기능 미미" in str(d["er"]):
        return "ER범주외"
    return None


def verdict(d, ov):
    """숫자 게이트 + 정정 후 평판. 확정인데 연환자 미달은 스크리닝으로 올리지 않는다."""
    why = veto_reason(d, ov)
    g = d.get("g") or gates(d, ov)
    if why:
        return "AVOID", why
    if g["무결점"]:
        v, w = "PASS_CONFIRM", "확정+연환자"
    elif g["확정"] and not g["연환자"]:
        v, w = "HOLD", d.get("vol_why") or "연환자미달"
    elif g["스크리닝"]:
        v, w = "PASS_SCREEN", "스크리닝"
    else:
        v, w = "HOLD", "게이트미달"
    rep = ov.get("reputation", {}).get(d["h"], {})
    if v != "AVOID" and rep.get("flag") == "평판리스크":
        return "REVIEW", "평판리스크·현직자통화필수"
    return v, w


def qualitative(d, ov):
    sig = ov.get("signals", {}).get(d["h"], {})
    keys = ["S1", "S2", "S3", "S4", "S5", "S6"]
    hits = sum(1 for k in keys if sig.get(k))
    bonus = min(2.8, hits * 0.4)
    market = sig.get("market")
    if market in ("즉시마감", "조건상향"):
        bonus = min(2.8, bonus + 0.6)
    elif market == "출장형":
        bonus = min(2.8, bonus + 0.3)
    elif market == "재공고":
        bonus -= 0.3
    d["sig"] = sig
    d["sig_hits"] = hits
    d["sig_bonus"] = bonus
    d["market_sig"] = market
    d["fly_in"] = d["h"] in set(ov.get("fly_in", [])) or market == "출장형"
    return bonus


def commute_score(d, ov):
    table = ov.get("commute_oksoo", {})
    if d["h"] in table:
        return table[d["h"]]
    return ZONE_COMMUTE.get(d.get("zone"), -2)


def personalize(d, ov):
    qual = qualitative(d, ov)
    comm = commute_score(d, ov)
    rep = ov.get("reputation", {}).get(d["h"], {})
    pen = rep.get("penalty", 0)
    market = d.get("score")
    d["commute"] = comm
    d["rep_flag"] = rep.get("flag")
    d["rep_note"] = rep.get("note")
    d["personal"] = None if market is None else market + comm * 1.8 + qual * 1.2 + pen * 1.5
    return d


def expected_pp2(pool, d):
    zg, bg = zone_group(d.get("zone")), backup_group(d.get("backup"))
    comps = [
        x["pp2"] for x in pool
        if x.get("rankable") and x.get("pp2") is not None
        and zone_group(x.get("zone")) == zg
        and backup_group(x.get("backup")) == bg
        and x["h"] != d.get("h")
    ]
    if len(comps) < 3:
        comps = [
            x["pp2"] for x in pool
            if x.get("rankable") and x.get("pp2") is not None
            and zone_group(x.get("zone")) == zg
            and x["h"] != d.get("h")
        ]
    if not comps:
        return None, []
    return statistics.median(comps), comps


def attach_residual(pool):
    for d in pool:
        exp, comps = expected_pp2(pool, d)
        d["pp2_exp"] = exp
        d["n_comps"] = len(comps)
        if exp is None or d.get("pp2") is None:
            d["pp2_resid"] = d["cash_resid"] = None
            continue
        d["pp2_resid"] = d["pp2"] - exp
        d["cash_resid"] = d["pp2_resid"] * (d["mpat"] or 0)
    return pool


def prepare(pool=None, overlays=None):
    ov = overlays if overlays is not None else load_overlays()
    if pool is None:
        pool, _ = load_pool()
    else:
        pool = [dict(d) for d in pool]
    apply_hygiene(pool, ov)
    apply_corrections(pool)
    apply_incentive(pool)
    for d in pool:
        spendable_cash(d, ov)
    compute_axes(pool)
    fin = composite(pool)
    rank_frame_b(pool)
    for d in pool:
        d["g"] = gates(d, ov)
        d["verdict"], d["verdict_why"] = verdict(d, ov)
        personalize(d, ov)
    attach_residual(pool)
    pers = sorted(
        [d for d in pool if d.get("personal") is not None],
        key=lambda x: (-x["personal"], x["h"]),
    )
    for i, d in enumerate(pers, 1):
        d["personal_rank"] = i
    return pool, fin, ov


def _quantile(xs, q):
    if not xs:
        return None
    xs = sorted(xs)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * q
    lo, hi = int(math.floor(pos)), int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - pos) + xs[hi] * (pos - lo)


def _band(rows, keys=("cash2", "pp2", "hrs", "safe", "wlb", "tot")):
    out = {"n": len(rows)}
    for k in keys:
        xs = [d[k] for d in rows if d.get(k) is not None]
        out[k] = None if not xs else {
            "p25": round(_quantile(xs, 0.25), 2),
            "p50": round(_quantile(xs, 0.50), 2),
            "p75": round(_quantile(xs, 0.75), 2),
        }
    return out


def _career(d):
    er = str(d.get("er") or "")
    return any(s in er for s in ("권역", "상종", "외상"))


def target_bands(pool):
    confirm = [d for d in pool if d.get("g", {}).get("무결점") and d.get("rankable")]
    seoul = [d for d in confirm if d.get("zone") in ("서울", "수도권")]
    cash = sorted(
        [d for d in pool if d.get("rankable") and d.get("cash2")],
        key=lambda x: -x["cash2"],
    )[: max(8, len(pool) // 8)]
    wlb = [
        d for d in pool if d.get("rankable")
        and d.get("hrs") is not None and d["hrs"] <= 122
        and (d.get("wlb") or 0) >= WLB_SIGNAL
    ]
    career = [d for d in confirm if _career(d)]
    light = [
        d for d in pool if d.get("rankable")
        and (d.get("acu") or 9) <= 1.0
        and (d.get("safe") or 0) >= SAFE_FLOOR
        and d.get("vol_status") != "trap"
    ]
    fly = [
        d for d in pool if d.get("rankable")
        and (
            d.get("fly_in")
            or (
                d.get("hrs") is not None and d["hrs"] <= 120
                and ((d.get("wlb") or 0) >= 6.0 or (d.get("sig_hits") or 0) >= 2)
            )
        )
    ]
    return {
        "확정통과": _band(confirm),
        "서울균형": _band(seoul),
        "현금": _band(cash),
        "워라밸": _band(wlb),
        "커리어": _band(career),
        "라이트세이프": _band(light),
        "출장형": _band(fly),
    }


def estimate_offer(zone="서울", backup="강", pp=2000, hours=120, acuity=1.0, pool=None):
    if pool is None:
        pool, _, _ = prepare()
    mpat = pp / 12
    dummy = dict(h="__est__", zone=zone, backup=backup, pp2=None)
    exp, comps = expected_pp2(pool, dummy)
    fair_pp2 = exp if exp is not None else CUT_UNIT
    return {
        "입력": dict(zone=zone, backup=backup, pp=pp, hours=hours, acuity=acuity),
        "월환자": round(mpat, 1),
        "스크리닝_단가": CUT_SCREEN,
        "확정_단가": CUT_CONFIRM,
        "설명컷_단가": CUT_UNIT,
        "시장중앙_단가": None if exp is None else round(exp, 2),
        "n_comps": len(comps),
        "목표통장_스크리닝": round(CUT_SCREEN * mpat),
        "목표통장_확정": round(CUT_CONFIRM * mpat),
        "목표통장_설명컷": round(CUT_UNIT * mpat),
        "목표통장_시장중앙": None if exp is None else round(fair_pp2 * mpat),
        "월시간_그린": "≤122",
        "월시간_하드": f"≤{HOURS_HARD}",
        "안전_스크리닝": SAFE_SCREEN,
        "안전_플로어": SAFE_FLOOR,
        "시간당_레드": PPH_RED,
        "시간당_추정": round(pp / 12 / hours * acuity, 2) if hours else None,
        "메모": "단가 13.3은 설명적 컷. 목표 통장은 확정 단가×월환자를 기본으로 보고, 시장 중앙을 옆에 둔다.",
    }


def _interp_effload(pool, effhr):
    pts = sorted(
        (d["effhr"], d["effload"]) for d in pool
        if d.get("effhr") is not None and d.get("effload") is not None
    )
    if not pts:
        raise ValueError("보간용 effhr 없음")
    if effhr <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= effhr <= x1:
            return y0 if x1 == x0 else y0 + (effhr - x0) * (y1 - y0) / (x1 - x0)
    return pts[-1][1]


def make_candidate(pool, name, annual, em, hours, cash_actual, acu, safe, sysx, wlb,
                   incen_included=True, backup=None, zone=None, legal="B",
                   volume_rescue=None):
    if em <= 0 or hours <= 0 or annual <= 0:
        raise ValueError(f"{name}: annual/em/hours 양수")
    pp = annual / em
    d = dict(
        h=name, pp=pp, tot=annual, hrs=hours, acu=acu, safe=safe, sys=sysx, wlb=wlb,
        cash=cash_actual, backup=backup, zone=zone, legal=legal, rankable=True,
        er="신규공고", em=em, volume_rescue=volume_rescue,
    )
    d["mpat"] = pp / 12
    d["pph"] = pp / 12 / hours
    d["effhr"] = d["pph"] * acu
    d["effload"] = _interp_effload(pool, d["effhr"])
    d["incen"] = 0 if incen_included else d["mpat"] * ANCHOR_ADMIT * acu * WON_PER_ADMIT
    d["incen_src"] = "실측포함" if incen_included else "모델추정"
    d["cash2"] = cash_actual + d["incen"]
    d["pp2"] = d["cash2"] / d["mpat"]
    d["incomplete"] = False
    return d


def evaluate_postings(pool_master, specs, ov):
    base = [dict(d) for d in pool_master if d.get("rankable") and d.get("cash2") is not None]
    lo, hi = compute_axes(base)
    master_fin = composite(base)
    master_scores = sorted((d["score"] for d in master_fin if d.get("score") is not None), reverse=True)
    cands = [make_candidate(base, **s) for s in specs]
    allp = base + cands
    compute_axes(allp, lo=lo, hi=hi)
    composite(allp)
    rank_frame_b(allp)
    cards = []
    for d in cands:
        spendable_cash(d, ov)
        d["g"] = gates(d, ov)
        d["verdict"], d["verdict_why"] = verdict(d, ov)
        personalize(d, ov)
        exp, comps = expected_pp2(base, d)
        d["pp2_exp"] = exp
        d["n_comps"] = len(comps)
        d["pp2_resid"] = None if exp is None else d["pp2"] - exp
        d["cash_resid"] = None if d["pp2_resid"] is None else d["pp2_resid"] * d["mpat"]
        r_vs_m = 1 + sum(1 for s in master_scores if s > (d.get("score") or -1e9))
        d["rank_vs_master"] = r_vs_m
        d["pct_vs_master"] = round((1 - r_vs_m / (len(master_scores) + 1)) * 100)
        cards.append(d)
    return cards


# ── 통계 컷 (v1.2, 설명적) ───────────────────────────
_LG = [0.0, 0.0]


def _lg(n):
    while len(_LG) <= n:
        _LG.append(_LG[-1] + math.log(len(_LG)))
    return _LG[n]


def _lc(n, k):
    return -1e18 if (k < 0 or k > n) else _lg(n) - _lg(k) - _lg(n - k)


def fisher_sf(tp, N, K, n):
    tot = _lc(N, n)
    return min(1.0, sum(
        math.exp(_lc(K, x) + _lc(N - K, n - x) - tot)
        for x in range(tp, min(K, n) + 1)
    ))


def maxstat(values, labels):
    N, K = len(values), sum(labels)
    vals = sorted(set(values))
    out = []
    for i in range(len(vals) - 1):
        t = (vals[i] + vals[i + 1]) / 2
        idx = [j for j in range(N) if values[j] >= t]
        if not idx or len(idx) == N:
            continue
        out.append((t, fisher_sf(sum(labels[j] for j in idx), N, K, len(idx)),
                    len(idx), sum(labels[j] for j in idx)))
    return out


def stat_cut(pool, label_set, boot=0):
    rows = [d for d in pool if d.get("pp2") is not None and d.get("rankable")]
    vals = [d["pp2"] for d in rows]
    labs = [1 if d["h"] in label_set else 0 for d in rows]
    curve = maxstat(vals, labs)
    if not curve:
        return dict(best_cut=None, p_raw=1.0, p_bonf=1.0, zone=None, M=0)
    M = len(curve)
    best = min(curve, key=lambda r: r[1])
    sig = [r[0] for r in curve if r[1] * M < 0.05]
    res = dict(
        best_cut=best[0], p_raw=best[1], p_bonf=min(1, best[1] * M),
        zone=(round(min(sig), 2), round(max(sig), 2)) if sig else None, M=M,
    )
    if boot:
        random.seed(7)
        cuts = []
        N = len(vals)
        for _ in range(boot):
            idx = [random.randrange(N) for _ in range(N)]
            c = maxstat([vals[i] for i in idx], [labs[i] for i in idx])
            if c:
                cuts.append(min(c, key=lambda r: r[1])[0])
        cuts.sort()
        if cuts:
            res["boot_ci"] = (cuts[int(0.025 * len(cuts))], cuts[int(0.975 * len(cuts))])
            res["boot_med"] = cuts[len(cuts) // 2]
    return res


def make_labels(pool):
    fin1 = [d for d in pool if d.get("comp_rank") is not None]
    fin1 = sorted(fin1, key=lambda d: d["comp_rank"])
    composite(pool, PROFILES_NOPAY, prefix="np_")
    fin2 = sorted(
        [d for d in pool if d.get("np_comp_rank") is not None],
        key=lambda d: d["np_comp_rank"],
    )
    return {
        "L1_종합TOP20(페이포함)": set(d["h"] for d in fin1[:20]),
        "L2_페이제거TOP20": set(d["h"] for d in fin2[:20]),
        "L3_QOL게이트(사전정의)": set(
            d["h"] for d in pool
            if d.get("rankable") and (d.get("safe") or 0) >= L3_SAFE and (d.get("wlb") or 0) >= L3_WLB
        ),
    }


# ── 출력 ─────────────────────────────────────────────
def _incen_str(d):
    src = d.get("incen_src")
    if src == "실측":
        return f"{d.get('incen') or 0:.0f} ★실측"
    if src in ("실측포함", "시트인센포함"):
        return "포함(내역미상)" if src == "실측포함" else "시트포함"
    if d.get("incen") is None:
        return "-"
    return f"{d['incen']:.0f} (모델)"


def print_report(pool, fin, ov):
    rankable = [d for d in pool if d.get("rankable")]
    print("═" * 64)
    print(f"봉직 통합 모델 v3 — 풀 {len(pool)} · 랭킹대상 {len(rankable)} · 시장순위 {len(fin)}")
    print("프레임 A = 4프로필 평균(통근 없음) · 프레임 B = v5.1 가중 · 개인 = A + 옥수동")
    print("═" * 64)

    print("\n[판정 분포]")
    for lab in ("PASS_CONFIRM", "REVIEW", "PASS_SCREEN", "HOLD", "AVOID"):
        names = [d["h"] for d in pool if d.get("verdict") == lab and d.get("rankable")]
        print(f"  {lab:14s} {len(names):2d}  {', '.join(names[:8])}{'…' if len(names) > 8 else ''}")

    print("\n[프레임 A 시장 TOP12]  (4프로필 · 통근 제외)")
    for d in fin[:12]:
        print(
            f"  {d['comp_rank']:2}. [{d['tier']}] {d['h']:22s} {d['score']:5.1f}  "
            f"단가 {d['pp2']:5.1f}  안전 {d['safe']:4.1f}  {d['verdict']}"
        )

    fb = sorted([d for d in pool if d.get("v51_rank")], key=lambda x: x["v51_rank"])
    print("\n[프레임 B v5.1 TOP8]  (시트16 가중 · 구 페이축)")
    for d in fb[:8]:
        print(f"  {d['v51_rank']:2}. {d['h']:22s} {d['v51']:5.1f}")

    a1, b1 = fin[0]["h"] if fin else None, fb[0]["h"] if fb else None
    print(f"\n[1위 프레임] A={a1}  /  B={b1}  →  {'일치' if a1 == b1 else '불일치 — 1위 교체를 확정처럼 쓰지 말 것'}")

    pers = sorted([d for d in pool if d.get("personal") is not None], key=lambda x: x["personal_rank"])
    print("\n[옥수동 개인 TOP10]")
    for d in pers[:10]:
        print(
            f"  {d['personal_rank']:2}. {d['h']:22s} {d['personal']:5.1f}  "
            f"통근 {d['commute']:+d}  정성 {d['sig_hits']}  {d.get('rep_flag') or ''}"
        )

    naz = next(d for d in pool if "나사렛" in d["h"])
    print("\n[현직 나사렛]")
    print(
        f"  시장A {naz.get('comp_rank')}위 · 시장B {naz.get('v51_rank')}위 · "
        f"개인 {naz.get('personal_rank')}위 · 통장 {naz['cash2']:.0f} · "
        f"단가 {naz['pp2']:.1f} · {naz['verdict']} · 인센 {_incen_str(naz)}"
    )

    nmc = next((d for d in pool if d["h"] == "국립중앙의료원"), None)
    if nmc:
        samsung = next(d for d in pool if "강북삼성" in d["h"])
        print("\n[NMC vs 강북삼성 — 같은 값대 대조]")
        print(
            f"  NMC     통장 {nmc['cash2']:.0f} 단가 {nmc['pp2']:.1f} 안전 {nmc['safe']:.1f}  "
            f"통근 {nmc['commute']:+d}  {nmc['verdict']}"
        )
        print(
            f"  강북삼성 통장 {samsung['cash2']:.0f} 단가 {samsung['pp2']:.1f} 안전 {samsung['safe']:.1f}  "
            f"통근 {samsung['commute']:+d}  {samsung['verdict']}"
        )

    print("\n[시장가 잔차 TOP/BOTTOM]")
    resid = [d for d in rankable if d.get("cash_resid") is not None and d.get("verdict") != "AVOID"]
    resid.sort(key=lambda x: -x["cash_resid"])
    print("  후한 쪽:")
    for d in resid[:5]:
        print(f"    {d['h']:22s} 단가 {d['pp2']:5.1f} vs {d['pp2_exp']:4.1f}  통장잔차 {d['cash_resid']:+.0f}")
    print("  싼 쪽:")
    for d in resid[-5:]:
        print(f"    {d['h']:22s} 단가 {d['pp2']:5.1f} vs {d['pp2_exp']:4.1f}  통장잔차 {d['cash_resid']:+.0f}")


def print_targets(pool):
    bands = target_bands(pool)
    print("\n[프로파일별 목표 조건 — 확정/필터 집합의 p25–p75]")
    print("  신규 공고는 중앙값과의 갭으로 읽는다. 밴드 밖 = 자동탈락이 아니라 협상 항목.")
    for name, b in bands.items():
        print(f"\n  ▸ {name}  n={b['n']}")
        if not b["n"]:
            continue
        for k, label in (("cash2", "통장"), ("pp2", "단가"), ("hrs", "월h"),
                         ("safe", "안전"), ("wlb", "워라밸"), ("tot", "연환자")):
            sl = b.get(k)
            if not sl:
                continue
            print(f"      {label:6s}  {sl['p25']}  /  {sl['p50']}  /  {sl['p75']}")


def print_postings(pool, ov):
    specs = load_postings()["evaluate"]
    print("\n[신규 공고 카드 — 고정 스케일]")
    for d in evaluate_postings(pool, specs, ov):
        resid = "" if d.get("cash_resid") is None else f"잔차 {d['cash_resid']:+.0f}만"
        print(
            f"  ▸ {d['h']:22s} {d['verdict']:13s} 통장 {d['cash2']:.0f} 단가 {d['pp2']:.1f}  "
            f"시장 {d['rank_vs_master']}위(상위 {100 - d['pct_vs_master']}%)  {resid}"
        )
        print(
            f"      게이트 확정={d['g']['확정']} 스크리닝={d['g']['스크리닝']} "
            f"연환자={d['g']['연환자']} 월h={d['g']['월시간']} · {d['verdict_why']}"
        )


def _holdout_hit(key, cards, pool):
    stem = key.split("(")[0]
    for n, d in cards.items():
        if stem[:4] in n or n.split("(")[0][:4] in key:
            return d, "카드"
    for d in pool:
        if stem and stem in d["h"]:
            return d, "풀"
    return None, None


def print_holdout(pool, ov):
    rec = load_postings()["recorded"]
    print("\n[8월 홀드아웃 — 시트 판정 vs 모델]")
    cards = {d["h"]: d for d in evaluate_postings(pool, load_postings()["evaluate"], ov)}
    for r in rec:
        key = r["name"]
        hit, src = _holdout_hit(key, cards, pool)
        model_v = f"{hit['verdict']}({src})" if hit else "(미평가)"
        ok = (
            r["verdict_sheet"] == "CLOSED"
            or (hit and hit["verdict"] == r["verdict_sheet"])
            or (r["verdict_sheet"] == "HOLD" and hit and hit["verdict"] in ("HOLD", "PASS_SCREEN"))
        )
        mark = "✓" if ok else "·"
        print(f"  {mark} {key:22s} 시트 {r['verdict_sheet']:12s} 모델 {model_v:16s}  {r['note'][:44]}")


def print_stats(pool, boot=0):
    labels = make_labels(pool)
    print("\n[통계 컷 — 라벨 3종 · 설명적 기준선 (예측 임계값 아님)]")
    for lname, lset in labels.items():
        st = stat_cut(pool, lset, boot=boot)
        cut = "없음" if st["best_cut"] is None else f"{st['best_cut']:.2f}"
        line = (
            f"  {lname:24s} n+={len(lset):2d} → 컷 {cut} · "
            f"raw {st['p_raw']:.1e} · Bonf {st['p_bonf']:.3f} · 구간 {st['zone']}"
        )
        if "boot_ci" in st:
            line += f" · CI [{st['boot_ci'][0]:.2f}, {st['boot_ci'][1]:.2f}]"
        print(line)
    print("  해석: 컷이 13.1–13.3에 모이면 강건. L2/L3 Bonferroni는 경계 공고가 늘면 약해진다.")


def print_lineage():
    lin = load_lineage()
    print("\n[모델 계보]")
    for g in lin["generations"]:
        print(f"  · {g['id']:8s} n={g['n']!s:12s}  {g['score']}")
        print(f"      유지: {g['kept']}")
        print(f"      한계: {g['broke']}")
    print("\n[학습 한 줄]")
    for lesson in lin["lessons"]:
        print(f"  — {lesson}")


def print_estimate(args, pool):
    est = estimate_offer(
        zone=args.get("zone", "서울"),
        backup=args.get("backup", "강"),
        pp=float(args.get("pp", 2000)),
        hours=float(args.get("hours", 120)),
        acuity=float(args.get("acuity", 1.0)),
        pool=pool,
    )
    print("\n[조건 역산 — 이 스펙에서 「좋은 공고」의 통장]")
    for k, v in est.items():
        print(f"  {k:22s} {v}")


def _parse_kv(argv):
    out, flags = {}, set()
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith("--") and i + 1 < len(argv) and not argv[i + 1].startswith("--"):
            key = a[2:]
            if key in ("zone", "backup", "pp", "hours", "acuity"):
                out[key] = argv[i + 1]
                i += 2
                continue
        if a.startswith("--"):
            flags.add(a)
        i += 1
    return flags, out


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    flags, kv = _parse_kv(argv)
    if not flags:
        flags = {"--verdict"}
    pool, fin, ov = prepare()
    if "--verdict" in flags:
        from bongjik.verdict import print_board, print_card
        cards = print_board(pool=pool, ov=ov)
        print("\n[핵심 카드]")
        for n in ("나사렛", "경희의료원", "진주", "을지(12", "국립중앙", "여수전남", "강북삼성"):
            print_card(n, cards)
    if "--lineage" in flags:
        print_lineage()
    if "--report" in flags:
        print_report(pool, fin, ov)
    if "--targets" in flags:
        print_targets(pool)
    if "--posting" in flags:
        print_postings(pool, ov)
    if "--holdout" in flags:
        print_holdout(pool, ov)
    if "--stats" in flags:
        print_stats(pool, boot=800 if "--boot" in flags else 0)
    if "--estimate" in flags:
        print_estimate(kv, pool)
    return 0


if __name__ == "__main__":
    sys.exit(main())
