#!/usr/bin/env python3
"""Build domain chat JSONL: train 352 / validation 80 / eval 24."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sft"))

import build_sft as sft  # noqa: E402
import domain_facts as df  # noqa: E402
import knowledge as kn  # noqa: E402
import retrieve  # noqa: E402
import tools  # noqa: E402

SEED = 20260911
QUOTAS = {
    "train": {"concept": 110, "code_review": 90, "calculation": 100, "evidence": 52},
    "validation": {"concept": 25, "code_review": 20, "calculation": 22, "evidence": 13},
    "eval": {"concept": 6, "code_review": 6, "calculation": 6, "evidence": 6},
}


def _rec(sid, task, split, lang, user, assistant, fact_ids, must, **meta):
    sys_p = df.SYSTEM_EN if lang == "en" else df.SYSTEM_KO
    return {
        "messages": [
            {"role": "system", "content": sys_p},
            {"role": "user", "content": user},
            {"role": "assistant", "content": assistant},
        ],
        "meta": {
            "id": sid,
            "task": task,
            "split": split,
            "lang": lang,
            "fact_ids": fact_ids,
            "must_contain": must,
            **meta,
        },
    }


def _fact(fid: str, lang: str) -> str:
    fmap = {f.id: f for f in df.all_facts(include_inferred=True)}
    f = fmap[fid]
    return f.en if lang == "en" else f.ko


CONCEPT_IDS = [
    "sign.glu",
    "sign.ach",
    "concept.receptor",
    "concept.assume",
    "dale.one_nt",
    "pipe.WTx",
    "pipe.filter",
    "vert.glu",
    "card.glu_assumption",
]


def build_concept(rng, sid, split, lang, heldout=False) -> dict:
    fid = CONCEPT_IDS[int(rng.integers(0, len(CONCEPT_IDS)))]
    if fid == "card.glu_assumption":
        text = retrieve.ConnectomeSearch().card("card.glu_assumption")["text_en" if lang == "en" else "text_ko"]
        facts = ["concept.assume"]
        must = ["가정"] if lang == "ko" else ["assumption"]
    else:
        text = _fact(fid, lang)
        facts = [fid]
        must = ["-1"] if fid == "sign.glu" else [text[:16].strip()]
        if fid == "pipe.WTx":
            must = ["W.T"]
        if fid == "concept.receptor":
            must = ["GluCl"] if "GluCl" in text else ["수용체"]
    if lang == "en":
        user = (
            "Distinguish NT polarity, receptor dependence, and model assumptions. "
            f"Focus: {fid}."
            + (" Phrase it differently from the textbook title." if heldout else "")
        )
    else:
        user = (
            "NT 극성, 수용체 의존성, 모델 가정을 구분해 설명하라. "
            f"초점: {fid}."
            + (" 교과서 제목을 그대로 베끼지 말 것." if heldout else "")
        )
    extra = _fact("concept.assume", lang)
    assistant = text + "\n" + extra
    return _rec(sid, "concept", split, lang, user, assistant, facts + ["concept.assume"], must)


CODE_CASES = [
    ("post", "NT를 bodyId_post에 merge", ["pipe.join_pre"], ["pre"]),
    ("W", "I = W @ x  (W는 pre×post)", ["pipe.WTx"], ["W.T"]),
    ("glu", "INSECT_SIGN['glutamate']=+1", ["debug.glu_plus", "sign.glu"], ["-1"]),
    ("dup", "같은 (A,B) 두 행을 W에 차례로 대입", ["code.dup_edge"], ["합"]),
    ("mode", "g.mode()[0] on all-NaN", ["inf.mode_nan"], ["IndexError"]),
    ("tie", "gaba/glutamate 동률 mode()[0]", ["inf.mode_tie"], ["gaba"]),
    ("lif", "V += I  (누수 없음) 후 리셋 없음", ["code.lif_bugs"], ["dt/tau"]),
    ("fill", "unknown NT fillna(+1)", ["pipe.inner"], ["left"]),
    ("or", "(weight>=5) | sign.notna()", ["pipe.filter"], ["AND"]),
    ("ge", "signed_weight >= 5", ["pipe.filter"], ["억제"] ),
]


def build_code(rng, sid, split, lang, heldout=False) -> dict:
    key, bug, fids, must = CODE_CASES[int(rng.integers(0, len(CODE_CASES)))]
    usable = [i for i in fids if i in {f.id for f in df.all_facts(include_inferred=True)}]
    texts = [_fact(i, "ko") for i in usable]
    if key == "dup":
        texts.append(_fact("code.dup_edge", "ko"))
        must = ["합"]
    if key == "lif":
        texts.append(_fact("code.lif_bugs", "ko"))
    user = f"코드 검토. 버그: {bug}. 행렬 방향, 결측·동률, 중복 에지, LIF 오류 중 어디에 해당하나?"
    if heldout:
        user += " 한 문장으로 수정 포인트를 말하라."
    if lang == "en":
        user = f"Code review. Bug: {bug}. Name the fix (matrix direction, missing/tie, duplicate edge, or LIF)."
    assistant = "\n".join(texts)
    if key == "ge":
        must = ["-1"] if "억제" not in assistant else ["억제"]
    return _rec(sid, "code_review", split, lang, user, assistant, usable, must)


def build_calc(rng, sid, split, lang, heldout=False) -> dict:
    net = sft.make_net(rng)
    payload = {"neurons": net["neurons"], "edges": net["edges"], "x": net["x"], "V": [0.0] * len(net["neurons"]), "tau": 10.0, "dt": 1.0}
    out = tools.current_and_lif(payload)
    I = sft.fmt_vec(out["I"])
    dV = sft.fmt_vec(out["dV"])
    table = sft.edge_table(net)
    if lang == "en":
        user = (
            f"Compute encoded current I=W.T@x and one LIF step (tau=10, dt=1, V=0).\n"
            f"neurons={net['neurons']} x={net['x']}\n{table}\n"
            "Use the calculation tool. Do not guess."
        )
        assistant = (
            f"{_fact('calc.tool_only', 'en')}\n{_fact('pipe.WTx', 'en')}\n"
            f"tool I = {I}\ntool dV = {dV}\n"
            f"ANSWER_I: {I}\nANSWER_DV: {dV}\n"
            f"{retrieve.ConnectomeSearch().card('card.lif')['text_en']}"
        )
    else:
        user = (
            f"부호화 전류 I=W.T@x 와 LIF 한 스텝(tau=10, dt=1, V=0)을 도구로 확인하라.\n"
            f"뉴런={net['neurons']} x={net['x']}\n{table}\n"
            "추측하지 말 것."
        )
        assistant = (
            f"{_fact('calc.tool_only', 'ko')}\n{_fact('pipe.WTx', 'ko')}\n"
            f"도구 I = {I}\n도구 dV = {dV}\n"
            f"ANSWER_I: {I}\nANSWER_DV: {dV}\n"
            f"{retrieve.ConnectomeSearch().card('card.lif')['text_ko']}"
        )
    if heldout:
        user += "\n평가용: 중간 풀이 없이 ANSWER 줄을 포함하라."
    return _rec(
        sid,
        "calculation",
        split,
        lang,
        user,
        assistant,
        ["calc.tool_only", "pipe.WTx"],
        ["ANSWER_I:", I],
        net=net,
        tool=out,
    )


EVIDENCE_Q = [
    ("stats", "Male CNS v1.0에서 weight 필터 전 원본 에지 수는?", "card.stats", "151856684"),
    ("hubs", "weight>=5 기준 가중 Out-degree 1위 bodyId와 값은?", "card.hubs", "140969"),
    ("files", "공식 가중치 Feather 파일 이름은?", "card.files", "connectome-weights-male-cns-v1.0-minconf-0.5.feather"),
    ("traced", "Traced 서브그래프 노드 수는?", "card.stats", "163903"),
    ("policy", "실행 없이 에지 수를 대략 1.6억이라고 해도 되나?", "card.rag_policy", "만들지"),
    ("glu", "곤충 글루타메이트 -1은 시냅스마다 실측한 부호인가?", "card.glu_assumption", "가정"),
]


def build_evidence(rng, sid, split, lang, heldout=False) -> dict:
    key, q, card_id, must = EVIDENCE_Q[int(rng.integers(0, len(EVIDENCE_Q)))]
    searcher = retrieve.ConnectomeSearch()
    card = searcher.card(card_id)
    ctx = searcher.as_context(q, k=3, lang="ko")
    if key == "policy":
        assistant = (
            f"거절. {card['text_ko']}\n검색:\n{ctx}\n"
            + _fact("evidence.refuse", "ko")
        )
        user = q + " 카드에 없는 근사값을 만들어도 되는지 답하라."
    else:
        user = q + " 근거 카드를 검색해 인용하고, 카드에 없으면 수치를 만들지 마라."
        assistant = f"[{card_id}] {card['text_ko']}\n(source: {card['source']}, version: {card['version']})"
    if lang == "en":
        user = q + " Retrieve a card; do not invent a number."
        assistant = f"[{card_id}] {card['text_en']}"
        if key == "policy":
            assistant = card["text_en"] + "\n" + _fact("evidence.refuse", "en")
            must = "invent"
        elif must.isdigit():
            pass  # numbers are in both card languages
        elif key == "glu":
            must = "assumption"
    if heldout:
        user += " (eval)"
    return _rec(sid, "evidence", split, lang, user, assistant, ["evidence.refuse", "bot.roles"], [must], card_id=card_id)


def generate(split: str) -> list[dict]:
    rng = np.random.default_rng(SEED + {"train": 1, "validation": 2, "eval": 3}[split])
    heldout = split == "eval"
    items = []
    n = 0
    for task, count in QUOTAS[split].items():
        for _ in range(count):
            lang = "en" if rng.random() < (0.22 if task != "evidence" else 0.15) else "ko"
            sid = f"{split[:3]}-{task[:3]}-{n:04d}"
            if task == "concept":
                items.append(build_concept(rng, sid, split, lang, heldout))
            elif task == "code_review":
                items.append(build_code(rng, sid, split, lang, heldout))
            elif task == "calculation":
                items.append(build_calc(rng, sid, split, lang, heldout))
            else:
                items.append(build_evidence(rng, sid, split, lang, heldout))
            n += 1
    return items


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in rows:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out-dir", type=Path, default=HERE / "data")
    args = p.parse_args(argv)
    mapping = {
        "train": "train.jsonl",
        "validation": "validation.jsonl",
        "eval": "eval.jsonl",
    }
    for split, name in mapping.items():
        rows = generate(split)
        write_jsonl(args.out_dir / name, rows)
        print(f"{split}: {len(rows)} → {args.out_dir / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
