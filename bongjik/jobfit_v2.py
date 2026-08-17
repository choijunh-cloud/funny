# -*- coding: utf-8 -*-
"""
JobFit v2 — 응급의학과 봉직 구직 조건 추정
==========================================
시장 점수(통근 없음)와 개인 점수(옥수동 기본)를 분리하고,
게이트 → 잔차 → 목표밴드 → 판정카드 순으로 읽는다.

사용:
  python3 bongjik/jobfit_v2.py --report
  python3 bongjik/jobfit_v2.py --targets
  python3 bongjik/jobfit_v2.py --posting
  python3 bongjik/jobfit_v2.py --estimate --zone 서울 --backup 강 --pp 2000 --hours 120
"""
from __future__ import annotations

import json
import math
import re
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
JSON_POOL = DATA / "master_pool.json"
OVERLAYS = DATA / "overlays.json"
MASTER_XLSX = DATA / "응급의학과_봉직공고_최종마스터.xlsx"

ANCHOR_ADMIT = 0.354
WON_PER_ADMIT = 3
CUT_UNIT = 13.3
CUT_SCREEN = 11.1
CUT_CONFIRM = 13.1
SAFE_SCREEN = 6.3
SAFE_FLOOR = 5.5
WLB_SIGNAL = 5.4
HOURS_HARD = 130
HOURS_RED = 168
PPH_RED = 2.0
VOL_CUT = 15000
VOL_TRAP = 8000
TIER_RULE = [(1, "S"), (9, "A"), (12, "B"), (20, "C")]

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

POSTING_EXAMPLES = [
    dict(name="김포우리(복원)", annual=31500, em=11, hours=130, cash_actual=2652,
         acu=0.94, safe=6.7, sysx=5.2, wlb=5.3, incen_included=False,
         backup="강", zone="수도권"),
    dict(name="세란(신규)", annual=14800, em=5, hours=146, cash_actual=2675,
         acu=0.88, safe=4.4, sysx=3.2, wlb=4.3, incen_included=True,
         backup="중", zone="서울"),
    dict(name="오산한국(8인·갱신)", annual=20864, em=8, hours=122, cash_actual=2398,
         acu=1.0, safe=5.9, sysx=4.3, wlb=5.73, incen_included=True,
         backup="강", zone="수도권"),
]

ZONE_COMMUTE = {"서울": 2, "수도권": 0, "광역시": -1, "강원": -3, "제주": -5, "지방": -5}


def load_overlays(path=None):
    p = Path(path) if path else OVERLAYS
    return json.loads(p.read_text(encoding="utf-8"))


def load_pool(path=None):
    """JSON 스냅샷 우선. 없거나 --xlsx 이면 마스터 엑셀."""
    if path:
        p = Path(path)
        if p.suffix.lower() == ".json":
            raw = json.loads(p.read_text(encoding="utf-8"))
            return [dict(d) for d in raw["pool"]], raw.get("meta", {})
    if JSON_POOL.exists() and not (path and str(path).endswith(".xlsx")):
        raw = json.loads(JSON_POOL.read_text(encoding="utf-8"))
        return [dict(d) for d in raw["pool"]], raw.get("meta", {})
    return _load_xlsx(path or MASTER_XLSX)


def _load_xlsx(path):
    try:
        import openpyxl
    except ImportError:
        sys.exit("openpyxl 필요 또는 data/master_pool.json 사용")
    wb = openpyxl.load_workbook(path, data_only=True)
    # 최소 로더 — JSON이 정본. 엑셀은 폴백.
    from bongjik_model_v12 import load_master, SHEET_MAIN, SHEET_AXES  # type: ignore
    del SHEET_MAIN, SHEET_AXES
    pool, rep = load_master(path, report=True)
    wb.close()
    return pool, rep


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
        if "incen" not in d or (d["incen"] is None and "cash2" not in d):
            acu = d.get("acu") or 1.0
            d["incen"] = d["mpat"] * ANCHOR_ADMIT * acu * WON_PER_ADMIT
        if "cash2" not in d:
            d["cash2"] = (d.get("cash") or 0) + (d.get("incen") or 0)
        d["pp2"] = d["cash2"] / d["mpat"]
    return pool


def spendable_cash(d, ov):
    """DC 포함이면 가용 현금 = 액면 × 12/13."""
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
    return lo, hi


def _rank_by(pool, key):
    ranked = sorted(pool, key=lambda x: (-key(x), x["h"]))
    return {id(d): i + 1 for i, d in enumerate(ranked)}


def composite(pool, profiles=PROFILES, prefix=""):
    usable = [d for d in pool if d.get("rankable") and d.get("pay2") is not None
              and all(d.get(k) is not None for k in ("safe", "wlb", "effload", "sys"))]
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


def zone_group(zone):
    if zone == "서울":
        return "서울"
    if zone == "수도권":
        return "수도권"
    if zone == "광역시":
        return "광역시"
    return "지방+"


def backup_group(backup):
    if backup in ("최강", "강"):
        return "강+"
    if backup == "중":
        return "중"
    return "약"


def volume_status(d, ov):
    rescue = ov.get("volume_rescue", {}).get(d["h"])
    tot = d.get("tot")
    if tot is None:
        return ("rescued", rescue or "연환자미확정") if rescue else ("unknown", "연환자 결측")
    if tot >= VOL_CUT:
        return "ok", None
    if rescue:
        return "rescued", rescue
    if tot < VOL_TRAP and (d.get("backup") == "약" or (d.get("safe") or 0) < SAFE_FLOOR):
        return "trap", "한산+약백업"
    return "fail", f"연환자 {tot:.0f}<{VOL_CUT}"


def gates(d, ov):
    pp2 = d.get("pp2")
    safe = d.get("safe")
    hrs = d.get("hrs")
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
    tot = d.get("tot")
    if tot is not None and tot < VOL_TRAP and d.get("backup") == "약":
        return "한산약백업"
    if d.get("er") and "ER기능 미미" in str(d["er"]):
        return "ER범주외"
    return None


def verdict(d, ov):
    why = veto_reason(d, ov)
    g = d.get("g") or gates(d, ov)
    if why:
        return "AVOID", why
    if g["무결점"]:
        return "PASS_CONFIRM", "확정+연환자"
    if g["스크리닝"]:
        return "PASS_SCREEN", "스크리닝"
    return "HOLD", "게이트미달"


def qualitative(d, ov):
    sig = ov.get("signals", {}).get(d["h"], {})
    keys = ["S1", "S2", "S3", "S4", "S5"]
    hits = sum(1 for k in keys if sig.get(k))
    bonus = min(2.5, hits * 0.4)
    market = sig.get("market")
    if market in ("즉시마감", "조건상향"):
        bonus = min(2.5, bonus + 0.6)
    elif market == "재공고":
        bonus -= 0.3
    d["sig"] = sig
    d["sig_hits"] = hits
    d["sig_bonus"] = bonus
    d["market_sig"] = market
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
    comps = [x["pp2"] for x in pool
             if x.get("rankable") and x.get("pp2") is not None
             and zone_group(x.get("zone")) == zg
             and backup_group(x.get("backup")) == bg
             and x["h"] != d.get("h")]
    if len(comps) < 3:
        comps = [x["pp2"] for x in pool
                 if x.get("rankable") and x.get("pp2") is not None
                 and zone_group(x.get("zone")) == zg
                 and x["h"] != d.get("h")]
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
    apply_incentive(pool)
    for d in pool:
        spendable_cash(d, ov)
    compute_axes(pool)
    fin = composite(pool)
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
    cash = sorted([d for d in pool if d.get("rankable") and d.get("cash2")],
                  key=lambda x: -x["cash2"])[: max(8, len(pool) // 8)]
    wlb = [d for d in pool if d.get("rankable")
           and d.get("hrs") is not None and d["hrs"] <= 122
           and (d.get("wlb") or 0) >= WLB_SIGNAL]
    career = [d for d in confirm if _career(d)]
    light = [d for d in pool if d.get("rankable")
             and (d.get("acu") or 9) <= 1.0
             and (d.get("safe") or 0) >= SAFE_FLOOR
             and d.get("vol_status") != "trap"]
    fly = [d for d in pool if d.get("rankable")
           and d.get("hrs") is not None and d["hrs"] <= 120
           and ((d.get("wlb") or 0) >= 6.0 or (d.get("sig_hits") or 0) >= 2)]
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
    """공고 스펙만으로 목표 통장·단가·게이트를 역산."""
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
    pts = sorted((d["effhr"], d["effload"]) for d in pool
                 if d.get("effhr") is not None and d.get("effload") is not None)
    if not pts:
        raise ValueError("보간용 effhr 없음")
    if effhr <= pts[0][0]:
        return pts[0][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= effhr <= x1:
            return y0 if x1 == x0 else y0 + (effhr - x0) * (y1 - y0) / (x1 - x0)
    return pts[-1][1]


def make_candidate(pool, name, annual, em, hours, cash_actual, acu, safe, sysx, wlb,
                   incen_included=True, backup=None, zone=None):
    if em <= 0 or hours <= 0 or annual <= 0:
        raise ValueError(f"{name}: annual/em/hours 양수")
    pp = annual / em
    d = dict(h=name, pp=pp, tot=annual, hrs=hours, acu=acu, safe=safe, sys=sysx, wlb=wlb,
             cash=cash_actual, backup=backup, zone=zone, legal="B", rankable=True,
             er="신규공고", em=em)
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
        cards.append(d)
        d["rank_vs_master"] = r_vs_m
        d["pct_vs_master"] = round((1 - r_vs_m / (len(master_scores) + 1)) * 100)
    return cards


def _incen_str(d):
    src = d.get("incen_src")
    if src == "실측":
        return f"{d.get('incen') or 0:.0f} ★실측"
    if src == "실측포함":
        return "포함(내역미상)"
    if d.get("incen") is None:
        return "-"
    return f"{d['incen']:.0f} (모델)"


def _gap_vs_band(d, band):
    if not band or not band.get("pp2"):
        return None
    gaps = {}
    for k, label in (("pp2", "단가"), ("cash2", "통장"), ("hrs", "월시간"), ("safe", "안전")):
        b = band.get(k)
        if not b or d.get(k) is None:
            continue
        if k == "hrs":
            gaps[label] = round(b["p50"] - d[k], 1)
        else:
            gaps[label] = round(d[k] - b["p50"], 1)
    return gaps


def print_report(pool, fin, ov):
    rankable = [d for d in pool if d.get("rankable")]
    print("═" * 64)
    print(f"JobFit v2 — 풀 {len(pool)} · 랭킹대상 {len(rankable)} · 시장순위 {len(fin)}")
    print("시장 점수 = 4프로필 평균(통근 없음) · 개인 점수 = 시장 + 옥수동통근 + 정성 + 평판")
    print("═" * 64)

    print("\n[판정 분포]")
    for lab in ("PASS_CONFIRM", "PASS_SCREEN", "HOLD", "AVOID"):
        names = [d["h"] for d in pool if d.get("verdict") == lab and d.get("rankable")]
        print(f"  {lab:14s} {len(names):2d}  {', '.join(names[:8])}{'…' if len(names) > 8 else ''}")

    print("\n[시장 TOP12]  (통근 제외 · 프레임 A)")
    for d in fin[:12]:
        print(f"  {d['comp_rank']:2}. [{d['tier']}] {d['h']:22s} {d['score']:5.1f}  "
              f"단가 {d['pp2']:5.1f}  안전 {d['safe']:4.1f}  {d['verdict']}")

    pers = sorted([d for d in pool if d.get("personal") is not None],
                  key=lambda x: x["personal_rank"])
    print("\n[옥수동 개인 TOP10]")
    for d in pers[:10]:
        print(f"  {d['personal_rank']:2}. {d['h']:22s} {d['personal']:5.1f}  "
              f"통근 {d['commute']:+d}  정성 {d['sig_hits']}  {d.get('rep_flag') or ''}")

    print("\n[현직 나사렛]")
    naz = next(d for d in pool if "나사렛" in d["h"])
    print(f"  시장 {naz.get('comp_rank')}위 · 개인 {naz.get('personal_rank')}위 · "
          f"통장 {naz['cash2']:.0f} · 단가 {naz['pp2']:.1f} · {naz['verdict']}")

    print("\n[시장가 잔차 TOP/BOTTOM]")
    resid = [d for d in rankable if d.get("cash_resid") is not None and d.get("verdict") != "AVOID"]
    resid.sort(key=lambda x: -x["cash_resid"])
    print("  후한 쪽:")
    for d in resid[:5]:
        print(f"    {d['h']:22s} 단가 {d['pp2']:5.1f} vs {d['pp2_exp']:4.1f}  "
              f"통장잔차 {d['cash_resid']:+.0f}")
    print("  싼 쪽:")
    for d in resid[-5:]:
        print(f"    {d['h']:22s} 단가 {d['pp2']:5.1f} vs {d['pp2_exp']:4.1f}  "
              f"통장잔차 {d['cash_resid']:+.0f}")


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
    print("\n[신규 공고 카드 — 고정 스케일]")
    for d in evaluate_postings(pool, POSTING_EXAMPLES, ov):
        resid = "" if d.get("cash_resid") is None else f"잔차 {d['cash_resid']:+.0f}만"
        print(f"  ▸ {d['h']:18s} {d['verdict']:13s} 통장 {d['cash2']:.0f} 단가 {d['pp2']:.1f}  "
              f"시장 {d['rank_vs_master']}위(상위 {100 - d['pct_vs_master']}%)  {resid}")
        print(f"      게이트 확정={d['g']['확정']} 스크리닝={d['g']['스크리닝']} "
              f"연환자={d['g']['연환자']} 월h={d['g']['월시간']} · {d['verdict_why']}")


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
        flags = {"--report", "--targets"}
    pool, fin, ov = prepare()
    if "--report" in flags:
        print_report(pool, fin, ov)
    if "--targets" in flags:
        print_targets(pool)
    if "--posting" in flags:
        print_postings(pool, ov)
    if "--estimate" in flags:
        print_estimate(kv, pool)
    return 0


if __name__ == "__main__":
    sys.exit(main())
