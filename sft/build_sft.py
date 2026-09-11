#!/usr/bin/env python3
"""Build chat-JSONL SFT samples from knowledge.py only.

Every assistant sentence is assembled from ledger facts plus numbers that
``make_net()`` / numpy produce. No other textbook claims are introduced.

Usage:
  python sft/build_sft.py --include-inferred
  python sft/build_sft.py --include-inferred --strip-meta --out-dir sft/data/openai
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import knowledge as kn  # noqa: E402

SEED = 20260911
TRAIN_N = 246
VAL_N = 28
TOTAL = TRAIN_N + VAL_N  # 274

# task → total / val  (train = total - val)
QUOTAS = {
    "numeric": (150, 15),
    "lookup": (62, 6),
    "concept": (28, 3),
    "debug": (14, 2),
    "codegen": (9, 1),
    "contrast": (11, 1),
}

NT_CHOICES = (
    "acetylcholine",
    "glutamate",
    "gaba",
    "octopamine",
    "dopamine",
    "serotonin",
)
# Fly-like mix used only to *sample* toy nets (assumption, not a taught fact).
NT_P = np.array([0.50, 0.24, 0.16, 0.04, 0.03, 0.03])


def fmt_vec(v) -> str:
    return "[" + ", ".join(f"{float(x):.4g}" for x in np.asarray(v, dtype=float)) + "]"


def make_net(rng: np.random.Generator, n: int | None = None) -> dict:
    """Synthetic 3–6 neuron directed graph. Replace with a Feather subgraph later."""
    n = int(n or rng.integers(3, 7))
    names = [f"N{i}" for i in range(n)]
    nt = {names[i]: str(rng.choice(NT_CHOICES, p=NT_P)) for i in range(n)}
    # Guarantee at least one glutamate source so the -1 rule is exercised often.
    if rng.random() < 0.72:
        nt[names[int(rng.integers(0, n))]] = "glutamate"

    edges: list[tuple[str, str, int, str]] = []
    for i, pre in enumerate(names):
        for j, post in enumerate(names):
            if i == j:
                continue
            if rng.random() < (0.42 + 0.04 * n):
                w = int(rng.integers(1, 17))
                edges.append((pre, post, w, nt[pre]))
    if len(edges) < n:
        for k in range(n):
            pre, post = names[k], names[(k + 1) % n]
            edges.append((pre, post, int(rng.integers(5, 14)), nt[pre]))
    # unique undirected? keep last of duplicate directed pairs
    uniq = {}
    for pre, post, w, ntv in edges:
        uniq[(pre, post)] = (pre, post, w, ntv)
    edges = list(uniq.values())
    x = [int(v) for v in rng.integers(0, 3, size=n)]
    if sum(x) == 0:
        x[0] = 1
    return {"neurons": names, "nt": nt, "edges": edges, "x": x}


def signed_rows(net: dict, min_weight: int = 5) -> list[tuple]:
    rows = []
    for pre, post, w, ntv in net["edges"]:
        if w < min_weight:
            continue
        sw = int(w * kn.INSECT_SIGN[ntv])
        rows.append((pre, post, int(w), ntv, sw))
    return rows


def dense_WTx(net: dict, rows: list[tuple]) -> tuple[np.ndarray, np.ndarray]:
    names = net["neurons"]
    idx = {n: i for i, n in enumerate(names)}
    n = len(names)
    W = np.zeros((n, n), dtype=float)
    for pre, post, _w, _nt, sw in rows:
        W[idx[pre], idx[post]] = float(sw)
    I = W.T @ np.asarray(net["x"], dtype=float)
    return W, I


def edge_table(net: dict) -> str:
    lines = ["pre post weight NT", "--- ---- ------ --"]
    for pre, post, w, ntv in net["edges"]:
        lines.append(f"{pre} {post} {w} {ntv}")
    return "\n".join(lines)


def signed_table(rows: list[tuple]) -> str:
    if not rows:
        return "(no edges survive weight >= 5)"
    lines = ["pre post weight NT sign signed_weight", "--- ---- ------ -- ---- -------------"]
    for pre, post, w, ntv, sw in rows:
        sign = kn.INSECT_SIGN[ntv]
        lines.append(f"{pre} {post} {w} {ntv} {sign:+d} {sw:+d}")
    return "\n".join(lines)


def sample(
    *,
    sid: str,
    task: str,
    split: str,
    lang: str,
    user: str,
    assistant: str,
    fact_ids: list[str],
    must_contain: list[str],
    net: dict | None = None,
    numeric_kind: str | None = None,
) -> dict:
    sys_p = kn.SYSTEM_PROMPT_EN if lang == "en" else kn.SYSTEM_PROMPT_KO
    rec = {
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
            "must_contain": must_contain,
            "numeric_kind": numeric_kind,
            "net": net,
        },
    }
    return rec


def build_numeric(rng: np.random.Generator, sid: str, split: str, lang: str) -> dict:
    net = make_net(rng)
    rows = signed_rows(net)
    _W, I = dense_WTx(net, rows)
    n_pos = sum(1 for r in rows if r[4] > 0)
    n_neg = sum(1 for r in rows if r[4] < 0)
    kind = str(rng.choice(["signed", "counts", "current", "all"]))

    f_sign = kn.fact_map(include_inferred=True)
    glu_line = f_sign["sign.glu"].en if lang == "en" else f_sign["sign.glu"].ko
    wtx_line = f_sign["pipe.WTx"].en if lang == "en" else f_sign["pipe.WTx"].ko
    sw_line = f_sign["pipe.signed"].en if lang == "en" else f_sign["pipe.signed"].ko
    flt_line = f_sign["pipe.filter"].en if lang == "en" else f_sign["pipe.filter"].ko

    names = ", ".join(net["neurons"])
    x_s = fmt_vec(net["x"])
    nt_s = ", ".join(f"{k}={v}" for k, v in net["nt"].items())

    if lang == "en":
        user = (
            f"Mini network neurons [{names}]. Presynaptic NT: {nt_s}.\n"
            f"Edgelist (pre post weight NT):\n{edge_table(net)}\n\n"
            f"Firing vector x in neuron order: {x_s}\n"
            "Convention: insect CNS signs, Dale join on pre, filter weight>=5, "
            "W[i,j]=i→j signed weight, I = W.T @ x.\n"
        )
        if kind == "signed":
            user += "Write the surviving signed_weight table."
        elif kind == "counts":
            user += "After the filter, how many + and − edges remain?"
        elif kind == "current":
            user += "Compute I = W.T @ x step by step."
        else:
            user += "Give the signed_weight table, ± counts, and I = W.T @ x."
    else:
        user = (
            f"미니 네트워크 뉴런 [{names}]. pre NT: {nt_s}.\n"
            f"에지 (pre post weight NT):\n{edge_table(net)}\n\n"
            f"발화 벡터 x (뉴런 순서): {x_s}\n"
            "규약: 곤충 CNS 부호, 데일(pre 조인), weight>=5 필터, "
            "W[i,j]=i→j 부호 가중, I = W.T @ x.\n"
        )
        if kind == "signed":
            user += "살아남은 signed_weight 표를 쓰라."
        elif kind == "counts":
            user += "필터 후 + 에지와 − 에지 개수를 구하라."
        elif kind == "current":
            user += "I = W.T @ x 를 단계별로 계산하라."
        else:
            user += "signed_weight 표, ±개수, I = W.T @ x 를 모두 구하라."

    steps = []
    names_l = net["neurons"]
    idx = {n: i for i, n in enumerate(names_l)}
    x = np.asarray(net["x"], dtype=float)
    for j, post in enumerate(names_l):
        parts = []
        acc = 0.0
        for pre, _post, _w, ntv, sw in rows:
            if _post != post:
                continue
            xi = x[idx[pre]]
            parts.append(f"{sw:+g}*{xi:g}({pre})")
            acc += sw * xi
        if parts:
            steps.append(f"  I[{post}] = " + " + ".join(parts) + f" = {acc:g}")
        else:
            steps.append(f"  I[{post}] = 0")

    if lang == "en":
        assistant = (
            f"{glu_line}\n{sw_line}\n{flt_line}\n{wtx_line}\n\n"
            f"signed_weight table (weight>=5):\n{signed_table(rows)}\n\n"
            f"+ edges: {n_pos}\n- edges: {n_neg}\n\n"
            "Current I = W.T @ x:\n"
            + "\n".join(steps)
            + f"\n\nANSWER_I: {fmt_vec(I)}\nANSWER_POS: {n_pos}\nANSWER_NEG: {n_neg}"
        )
    else:
        assistant = (
            f"{glu_line}\n{sw_line}\n{flt_line}\n{wtx_line}\n\n"
            f"signed_weight 표 (weight>=5):\n{signed_table(rows)}\n\n"
            f"+ 에지: {n_pos}\n- 에지: {n_neg}\n\n"
            "전류 I = W.T @ x:\n"
            + "\n".join(steps)
            + f"\n\nANSWER_I: {fmt_vec(I)}\nANSWER_POS: {n_pos}\nANSWER_NEG: {n_neg}"
        )

    must = ["ANSWER_I:", fmt_vec(I), "glutamate"]
    # glutamate word may be absent if no glu in this net
    if not any(r[3] == "glutamate" for r in net["edges"]):
        must = ["ANSWER_I:", fmt_vec(I)]
    return sample(
        sid=sid,
        task="numeric",
        split=split,
        lang=lang,
        user=user,
        assistant=assistant,
        fact_ids=["sign.glu", "pipe.signed", "pipe.filter", "pipe.WTx"],
        must_contain=must,
        net=net,
        numeric_kind=kind,
    )


def build_lookup(rng: np.random.Generator, sid: str, split: str, include_inferred: bool) -> dict:
    fmap = kn.fact_map(include_inferred=include_inferred)
    pool = [f for f in fmap.values() if "lookup" in f.tags]
    fact = pool[int(rng.integers(0, len(pool)))]
    lang = "en" if rng.random() < 0.35 else "ko"
    if lang == "en":
        user = f"What is the modeling sign / reference note for {fact.id.split('.', 1)[-1]}? Quote the ledger."
        assistant = fact.en
        must = [fact.en.split(".")[0]]
    else:
        user = f"{fact.id} 항목의 모델링 부호 또는 참고 서술을 원장 문장으로 답하라."
        assistant = fact.ko
        must = [fact.ko[:18]]
    # tighten must_contain to a stable token
    if "glu" in fact.tags and "vertebrate" not in fact.tags:
        must = ["-1"]
    elif fact.id == "sign.ach":
        must = ["+1"]
    elif fact.id == "sign.gaba":
        must = ["-1"]
    return sample(
        sid=sid,
        task="lookup",
        split=split,
        lang=lang,
        user=user,
        assistant=assistant,
        fact_ids=[fact.id],
        must_contain=must,
    )


def build_concept(rng: np.random.Generator, sid: str, split: str, include_inferred: bool) -> dict:
    fmap = kn.fact_map(include_inferred=include_inferred)
    pool = [f for f in fmap.values() if "concept" in f.tags]
    fact = pool[int(rng.integers(0, len(pool)))]
    lang = "en" if rng.random() < 0.25 else "ko"
    if lang == "en":
        user = f"Explain this connectome-LIF idea in one short paragraph: {fact.id}."
        assistant = fact.en
    else:
        user = f"다음 개념을 한 단락으로 설명하라: {fact.id}."
        assistant = fact.ko
    token = "-1" if "glu" in fact.tags else fact.id.split(".")[-1]
    # safer must: a distinctive 6+ char snippet
    snippet = (fact.en if lang == "en" else fact.ko)
    must = [snippet[0:24].strip()]
    if fact.id == "pipe.WTx":
        must = ["W.T"]
    elif fact.id == "dale.one_nt":
        must = ["pre"]
    elif fact.id == "inf.dale_stages":
        must = ["②"]
    return sample(
        sid=sid,
        task="concept",
        split=split,
        lang=lang,
        user=user,
        assistant=assistant,
        fact_ids=[fact.id],
        must_contain=must,
    )


DEBUG_CASES = (
    ("post_join", ["pipe.join_pre", "dale.one_nt"], "debug"),
    ("no_transpose", ["pipe.WTx"], "debug"),
    ("glu_plus", ["debug.glu_plus", "sign.glu"], "debug"),
    ("inner_join", ["pipe.inner"], "debug"),
    ("or_filter", ["pipe.filter"], "debug"),
    ("abs_filter", ["pipe.filter"], "debug"),
    ("signed_ge5", ["pipe.filter", "sign.glu"], "debug"),
    ("fill_unknown_plus", ["pipe.inner", "debug.glu_plus"], "debug"),
    ("mode_tie", ["inf.mode_tie", "pipe.mode"], "debug"),
    ("mode_nan", ["inf.mode_nan", "pipe.mode"], "debug"),
    ("join_type_not_id", ["pipe.join_pre", "pipe.columns"], "debug"),
    ("wx_not_wtx", ["pipe.WTx"], "debug"),
    ("drop_negative_sign", ["pipe.filter", "pipe.signed"], "debug"),
    ("sum_unsigned", ["pipe.signed", "pipe.WTx"], "debug"),
)


def build_debug(sid: str, split: str, case: tuple, include_inferred: bool) -> dict:
    key, fact_ids, _ = case
    usable = [i for i in fact_ids if i in kn.fact_map(include_inferred=include_inferred)]
    if not usable:
        usable = ["pipe.join_pre"]
        key = "post_join"
    fmap = kn.fact_map(include_inferred=include_inferred)
    body = "\n".join(fmap[i].ko for i in usable)

    prompts = {
        "post_join": (
            "버그: NT를 bodyId_post 에 merge 했다. 무엇이 틀렸고 어디를 고치나?",
            body,
            ["pre"],
        ),
        "no_transpose": (
            "버그: 전류를 W @ x 로 계산했다. 규약 W[i,j]=i→j 에서 올바른 식은?",
            body,
            ["W.T"],
        ),
        "glu_plus": (
            "버그: INSECT_SIGN['glutamate'] = +1 로 두었다. 왜 위험한가?",
            body,
            ["-1"],
        ),
        "inner_join": (
            "버그: NT를 how='inner' 로 조인해 행이 사라졌다. 올바른 조인은?",
            body,
            ["left"],
        ),
        "or_filter": (
            "버그: (weight>=5) | sign.notna() 로 필터했다. 무엇이 남게 되나?",
            body,
            ["AND"],
        ),
        "abs_filter": (
            "버그: 필터를 abs(signed_weight) >= 5 로 썼다. 의도와 다른 점은?",
            body,
            ["weight"],
        ),
        "signed_ge5": (
            "버그: signed_weight >= 5 로 필터해 음수 에지가 전부 사라졌다. 원인은?",
            body,
            ["억제"] if "억제" in body else ["-1"],
        ),
        "fill_unknown_plus": (
            "버그: NT가 없는 pre 의 sign 을 +1 로 fillna 했다. 왜 안 되나?",
            body,
            ["+1"],
        ),
        "mode_tie": (
            "한 뉴런에서 gaba 와 glutamate 예측이 동률이다. mode()[0] 은 무엇을 고르나?",
            body,
            ["gaba"],
        ),
        "mode_nan": (
            "그룹이 전부 NaN 인데 nt = g.mode()[0] 을 호출했다. 무슨 예외가 나나?",
            body,
            ["IndexError"],
        ),
        "join_type_not_id": (
            "버그: NT를 cell type 이름으로 조인하고 bodyId 를 무시했다. 문제는?",
            body,
            ["bodyId_pre"],
        ),
        "wx_not_wtx": (
            "W 를 (pre×post)로 쌓고도 I = W @ x 를 썼다. 고쳐라.",
            body,
            ["W.T"],
        ),
        "drop_negative_sign": (
            "필터 조건이 signed_weight > 0 이다. 글루타메이트 에지는?",
            body,
            ["-1"],
        ),
        "sum_unsigned": (
            "전류를 부호 없이 weight 합으로 계산했다. 빠진 단계는?",
            body,
            ["signed_weight"],
        ),
    }
    user, assistant, must = prompts[key]
    return sample(
        sid=sid,
        task="debug",
        split=split,
        lang="ko",
        user=user,
        assistant=assistant,
        fact_ids=usable,
        must_contain=must,
    )


CODEGEN_SPECS = (
    (
        "write pandas that joins consensus_nt onto the weight table. name the join key.",
        ["pipe.join_pre", "pipe.columns", "code.lif"],
        ["bodyId_pre"],
        "ko",
    ),
    (
        "write the INSECT_SIGN dict. glutamate must be -1.",
        ["sign.glu", "sign.ach", "code.lif"],
        ["'glutamate': -1", "'acetylcholine': 1"],
        "en",
    ),
    (
        "weight>=5 와 sign.notna() 를 AND 로 필터하는 한 줄을 쓰라.",
        ["pipe.filter", "code.lif"],
        ["weight"],
        "ko",
    ),
    (
        "signed_weight 컬럼을 만드는 한 줄.",
        ["pipe.signed", "code.lif"],
        ["sign"],
        "ko",
    ),
    (
        "numpy 로 W 를 만들고 I = W.T @ x 를 반환하는 함수를 스케치하라.",
        ["pipe.WTx", "code.lif"],
        ["W.T"],
        "ko",
    ),
    (
        "left join 후 unknown NT 를 세는 코드를 쓰라. fillna(+1) 금지.",
        ["pipe.inner", "code.lif"],
        ["left"],
        "ko",
    ),
    (
        "Rename body_pre/body_post to bodyId_* then merge NT on pre.",
        ["pipe.columns", "pipe.join_pre"],
        ["body_pre"],
        "en",
    ),
    (
        "mode()[0] 호출 전에 빈 그룹을 가드하는 코드를 쓰라.",
        ["inf.mode_nan", "pipe.mode"],
        ["mode"],
        "ko",
    ),
    (
        "Write a one-liner that maps NT → insect sign and never maps glutamate to +1.",
        ["sign.glu", "code.lif"],
        ["-1"],
        "en",
    ),
)


def build_codegen(sid: str, split: str, spec: tuple, include_inferred: bool) -> dict:
    user, fact_ids, extra_must, lang = spec
    usable = [i for i in fact_ids if i in kn.fact_map(include_inferred=include_inferred)]
    if not usable:
        usable = ["code.lif"]
    fmap = kn.fact_map(include_inferred=include_inferred)
    text = "\n".join((fmap[i].en if lang == "en" else fmap[i].ko) for i in usable)
    snippets = {
        "bodyId_pre": (
            "edges.merge(nt.rename(columns={'body':'bodyId_pre','consensus_nt':'nt'}), "
            "on='bodyId_pre', how='left')"
        ),
        "'glutamate': -1": (
            "INSECT_SIGN = {'acetylcholine': 1, 'glutamate': -1, 'gaba': -1, "
            "'serotonin': 1, 'dopamine': 1, 'octopamine': 1, 'histamine': -1}"
        ),
        "weight": "df = df[(df['weight'] >= 5) & df['sign'].notna()]",
        "sign": "df['signed_weight'] = df['weight'] * df['sign']",
        "W.T": (
            "W[idx[pre], idx[post]] = signed_weight\nI = W.T @ x  # not W @ x"
        ),
        "left": (
            "df = edges.merge(nt, on='bodyId_pre', how='left')\n"
            "n_unknown = int(df['nt'].isna().sum())  # do not fillna(1)"
        ),
        "body_pre": (
            "df = df.rename(columns={'body_pre':'bodyId_pre','body_post':'bodyId_post'})"
        ),
        "mode": (
            "m = g.mode()\nnt = m.iloc[0] if len(m) else None  # avoid mode()[0] IndexError"
        ),
        "-1": "sign = {'glutamate': -1}.get(nt)  # never +1 for insect glutamate",
    }
    code = snippets.get(extra_must[0], "")
    assistant = text + "\n\n```python\n" + code + "\n```"
    return sample(
        sid=sid,
        task="codegen",
        split=split,
        lang=lang,
        user=user,
        assistant=assistant,
        fact_ids=usable,
        must_contain=extra_must,
    )


def build_contrast(rng: np.random.Generator, sid: str, split: str, include_inferred: bool) -> dict:
    fmap = kn.fact_map(include_inferred=include_inferred)
    ids = [i for i in ("sign.glu", "vert.glu", "sign.ach", "vert.ach", "sign.oa", "vert.oa", "sign.ha", "vert.ha") if i in fmap]
    pick = [ids[int(rng.integers(0, len(ids)))] for _ in range(2)]
    # always include glu pair if available — that is the point of the set
    if "sign.glu" in fmap and "vert.glu" in fmap and rng.random() < 0.7:
        pick = ["sign.glu", "vert.glu"]
    extra = []
    if include_inferred and rng.random() < 0.45 and "inf.vert_receptors" in fmap:
        extra = ["inf.vert_receptors"]
    fact_ids = list(dict.fromkeys(pick + extra))
    lang = "en" if rng.random() < 0.4 else "ko"
    texts = [(fmap[i].en if lang == "en" else fmap[i].ko) for i in fact_ids]
    assistant = "\n".join(texts)
    if lang == "en":
        user = "Contrast the insect CNS modeling sign with the vertebrate reference column for the relevant transmitters. Keep the two columns distinct."
    else:
        user = "해당 전달물질에 대해 곤충 CNS 모델링 부호와 척추동물 참고 컬럼을 구분해 대조하라. 두 컬럼을 섞지 마라."
    must = ["-1", "+1"] if "sign.glu" in fact_ids else [texts[0][:12]]
    return sample(
        sid=sid,
        task="contrast",
        split=split,
        lang=lang,
        user=user,
        assistant=assistant,
        fact_ids=fact_ids,
        must_contain=must,
    )


def assign_splits(task: str, k: int) -> list[str]:
    _total, n_val = QUOTAS[task]
    return ["val"] * n_val + ["train"] * (k - n_val)


def generate(include_inferred: bool) -> list[dict]:
    rng = np.random.default_rng(SEED)
    items: list[dict] = []
    n = 0

    splits = assign_splits("numeric", QUOTAS["numeric"][0])
    rng.shuffle(splits)
    for split in splits:
        lang = "en" if rng.random() < 0.12 else "ko"
        items.append(build_numeric(rng, f"num-{n:03d}", split, lang))
        n += 1

    splits = assign_splits("lookup", QUOTAS["lookup"][0])
    rng.shuffle(splits)
    for split in splits:
        items.append(build_lookup(rng, f"lkp-{n:03d}", split, include_inferred))
        n += 1

    splits = assign_splits("concept", QUOTAS["concept"][0])
    rng.shuffle(splits)
    for split in splits:
        items.append(build_concept(rng, f"con-{n:03d}", split, include_inferred))
        n += 1

    debug_cases = list(DEBUG_CASES)
    if not include_inferred:
        debug_cases = [c for c in debug_cases if not any(i.startswith("inf.") for i in c[1])]
        # pad with context-only repeats to keep 14
        while len(debug_cases) < QUOTAS["debug"][0]:
            debug_cases.append(debug_cases[len(debug_cases) % max(len(debug_cases), 1)])
    debug_cases = debug_cases[: QUOTAS["debug"][0]]
    splits = assign_splits("debug", len(debug_cases))
    for split, case in zip(splits, debug_cases):
        items.append(build_debug(f"dbg-{n:03d}", split, case, include_inferred))
        n += 1

    specs = list(CODEGEN_SPECS)
    if not include_inferred:
        specs = [s for s in specs if not any(i.startswith("inf.") for i in s[1])]
        while len(specs) < QUOTAS["codegen"][0]:
            specs.append(specs[len(specs) % max(len(specs), 1)])
    specs = specs[: QUOTAS["codegen"][0]]
    splits = assign_splits("codegen", len(specs))
    for split, spec in zip(splits, specs):
        items.append(build_codegen(f"gen-{n:03d}", split, spec, include_inferred))
        n += 1

    splits = assign_splits("contrast", QUOTAS["contrast"][0])
    rng.shuffle(splits)
    for split in splits:
        items.append(build_contrast(rng, f"cst-{n:03d}", split, include_inferred))
        n += 1

    if len(items) != TOTAL and include_inferred:
        raise RuntimeError(f"expected {TOTAL} samples, got {len(items)}")
    return items


def strip_meta(rec: dict) -> dict:
    return {"messages": rec["messages"]}


def write_jsonl(path: Path, rows: list[dict], *, strip: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for rec in rows:
            payload = strip_meta(rec) if strip else rec
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--include-inferred", action="store_true",
                   help="emit the four inferred ledger rows")
    p.add_argument("--strip-meta", action="store_true",
                   help="OpenAI-style messages-only JSONL")
    p.add_argument("--out-dir", type=Path, default=ROOT / "data")
    args = p.parse_args(argv)

    items = generate(include_inferred=args.include_inferred)
    train = [r for r in items if r["meta"]["split"] == "train"]
    val = [r for r in items if r["meta"]["split"] == "val"]
    write_jsonl(args.out_dir / "train.jsonl", train, strip=args.strip_meta)
    write_jsonl(args.out_dir / "val.jsonl", val, strip=args.strip_meta)
    print(
        f"wrote {len(train)} train / {len(val)} val "
        f"(inferred={args.include_inferred}, strip_meta={args.strip_meta}) "
        f"→ {args.out_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
