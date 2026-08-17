# -*- coding: utf-8 -*-
"""
판정 모델 — 정정사항 반영
========================
랭킹을 만들지 않는다. 공고 하나를 거부/보류/스크리닝/확정/재검토로만 나눈다.

정정 반영:
  · 적십자 3,125만 오산 → 본문 1,900/1,700
  · 을지 카톡 3.0+2.2 → 5.2억 단일·통장 2,530, 숫자는 통과해도 REVIEW
  · 나사렛 2,083 → 2,800 실측
  · 여수전남 2,626 → 2,770 / 포항세명 DC 2,430 / 남원 2,750 즉시마감
  · 확정인데 연환자 미달(한산·대학구조 경계)은 스크리닝이 아니라 HOLD
  · 안전 < 4.0 거부 (8월 동의)
  · 1위 교체는 이 모듈의 일이 아님
"""
from __future__ import annotations

import json
from pathlib import Path

from bongjik.model import (
    CUT_SCREEN,
    VOL_TRAP,
    gates,
    load_json,
    load_overlays,
    prepare,
    verdict as model_verdict,
)

ROOT = Path(__file__).resolve().parent
CORRECTIONS = ROOT / "data" / "corrections.json"

LABELS = ("AVOID", "HOLD", "REVIEW", "PASS_SCREEN", "PASS_CONFIRM")

NEXT_ACTION = {
    "AVOID": "시간 쓰지 않음",
    "HOLD": "프로파일이 맞을 때만 보관. 단가·백업·연환자 원인 확인",
    "REVIEW": "숫자는 통과. 현직자 2명 통화 전에는 확정 금지",
    "PASS_SCREEN": "후보. 컨택하되 확정 콤보·연환자를 먼저 확인",
    "PASS_CONFIRM": "컨택 1순위. 체크리스트 5문항만 확인",
}


def load_corrections(path=None):
    return load_json(path or CORRECTIONS)


def apply_corrections(pool, corr=None):
    """시트 정정·8월 실측을 인센 계산 전에 덮어쓴다."""
    corr = corr if corr is not None else load_corrections()
    cash = corr.get("cash", {})
    for d in pool:
        patch = cash.get(d["h"])
        if not patch:
            continue
        for k, v in patch.items():
            if k == "note":
                d["corr_note"] = v
                continue
            d[k] = v
        if patch.get("cash2") is not None and d.get("cash") is None:
            d["cash"] = patch["cash2"]
        if patch.get("cash2") is not None:
            d["cash"] = patch["cash2"]
    return pool


def finalize_verdict(d, ov, corr=None):
    if "g" not in d:
        d["g"] = gates(d, ov)
    return model_verdict(d, ov)


def judge(d, ov=None, corr=None):
    """병원 한 곳의 판정 카드."""
    ov = ov if ov is not None else load_overlays()
    corr = corr if corr is not None else load_corrections()
    if "g" not in d:
        d["g"] = gates(d, ov)
    v, why = finalize_verdict(d, ov, corr)
    g = d["g"]
    flags = []
    if d.get("corr_note"):
        flags.append("정정적용")
    if d.get("incomplete"):
        flags.append("연환자미확정")
    if d.get("scenario"):
        flags.append("시나리오행")
    if d.get("fly_in"):
        flags.append("출장형")
    if d.get("retire_type") == "dc_in_net":
        flags.append("DC포함(-8%)")
    if d.get("rep_flag"):
        flags.append(d["rep_flag"])
    if d.get("market_sig"):
        flags.append(d["market_sig"])
    if (d.get("pp2") or 0) >= 20 and (d.get("tot") or 0) < VOL_TRAP:
        flags.append("고단가함정주의")
    if (d.get("pp") or 0) >= 3200 and (d.get("pp2") or 0) < CUT_SCREEN:
        flags.append("고액그라인더")
    flags = list(dict.fromkeys(flags))
    card = {
        "h": d.get("h"),
        "verdict": v,
        "why": why,
        "next": NEXT_ACTION[v],
        "cash2": d.get("cash2"),
        "pp2": d.get("pp2"),
        "safe": d.get("safe"),
        "hrs": d.get("hrs"),
        "tot": d.get("tot"),
        "zone": d.get("zone"),
        "gates": {
            "스크리닝": g.get("스크리닝"),
            "확정": g.get("확정"),
            "연환자": g.get("연환자"),
            "월시간": g.get("월시간"),
            "워라밸": g.get("워라밸신호"),
        },
        "flags": flags,
        "questions": corr.get("contact_questions", []) if v in ("PASS_CONFIRM", "REVIEW", "PASS_SCREEN") else [],
    }
    return card


def judge_pool(pool=None, ov=None, corr=None):
    if pool is None or ov is None:
        pool, _, ov = prepare()
    corr = corr if corr is not None else load_corrections()
    cards = [judge(d, ov, corr) for d in pool if d.get("rankable")]
    order = {lab: i for i, lab in enumerate(LABELS)}
    cards.sort(key=lambda c: (order.get(c["verdict"], 9), -(c["pp2"] or 0), c["h"]))
    return cards


def _fmt(v, nd=1):
    if v is None:
        return "   -"
    if isinstance(v, float):
        return f"{v:5.{nd}f}"
    return f"{v:5}"


def print_board(cards=None, pool=None, ov=None):
    if cards is None:
        cards = judge_pool(pool, ov)
    print("═" * 72)
    print("판정 모델 — 정정사항 반영 (랭킹 없음 · 게이트만)")
    print("AVOID 거부 · HOLD 보관 · REVIEW 평판재검토 · SCREEN 후보 · CONFIRM 컨택1순위")
    print("═" * 72)

    counts = {lab: 0 for lab in LABELS}
    for c in cards:
        counts[c["verdict"]] = counts.get(c["verdict"], 0) + 1
    print(
        "  분포  "
        + "  ".join(f"{lab} {counts.get(lab, 0)}" for lab in LABELS)
        + f"  /  {len(cards)}곳"
    )

    for lab in ("PASS_CONFIRM", "REVIEW", "PASS_SCREEN", "HOLD", "AVOID"):
        rows = [c for c in cards if c["verdict"] == lab]
        if not rows:
            continue
        print(f"\n[{lab} × {len(rows)}]  {NEXT_ACTION[lab]}")
        print(f"  {'병원':22s} {'통장':>6} {'단가':>6} {'안전':>5} {'월h':>5}  이유")
        show = rows if lab != "HOLD" else rows[:12]
        for c in show:
            print(
                f"  {c['h']:22s} {_fmt(c['cash2'], 0)} {_fmt(c['pp2'])} "
                f"{_fmt(c['safe'])} {_fmt(c['hrs'], 0)}  {c['why']}"
            )
            if c["flags"] and lab != "HOLD":
                print(f"  {'':22s}  · {' · '.join(c['flags'])}")
        if lab == "HOLD" and len(rows) > 12:
            print(f"  … 외 {len(rows) - 12}곳")

    print("\n[컨택 1순위 체크리스트]")
    corr = load_corrections()
    for i, q in enumerate(corr.get("contact_questions", []), 1):
        print(f"  {i}. {q}")
    return cards


def print_card(name, cards=None):
    if cards is None:
        cards = judge_pool()
    hit = next((c for c in cards if c["h"] == name), None)
    if not hit:
        hit = next((c for c in cards if c["h"].startswith(name)), None)
    if not hit:
        hit = next((c for c in cards if name in c["h"]), None)
    if not hit:
        print(f"없음: {name}")
        return
    print(f"\n▸ {hit['h']}  [{hit['verdict']}]  {hit['why']}")
    print(f"  다음: {hit['next']}")
    print(
        f"  통장 {hit['cash2']}  단가 {None if hit['pp2'] is None else round(hit['pp2'], 1)}  "
        f"안전 {hit['safe']}  월h {hit['hrs']}  연환자 {hit['tot']}"
    )
    print("  게이트 " + " ".join(f"{k}={'✓' if v else '✗'}" for k, v in hit["gates"].items()))
    if hit["flags"]:
        print("  플래그 " + ", ".join(hit["flags"]))
    if hit["questions"]:
        print("  질문")
        for q in hit["questions"]:
            print(f"    · {q}")


def main(argv=None):
    import sys
    args = list(sys.argv[1:] if argv is None else argv)
    cards = print_board()
    names = [a for a in args if not a.startswith("--")]
    if not names:
        names = ["나사렛", "경희의료원", "진주", "을지(12", "국립중앙", "여수전남", "강북삼성"]
    print("\n[핵심 카드]")
    for n in names:
        print_card(n, cards)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
