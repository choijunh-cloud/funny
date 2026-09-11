#!/usr/bin/env python3
"""Quality gate for the connectome LIF SFT JSONL.

Recomputes I = W.T @ x from each numeric sample's mini-net with a dense
numpy matrix (does not trust ANSWER_* written by the generator). Rejects
assistant text that *asserts* insect glutamate is +1.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import knowledge as kn  # noqa: E402

EXPECTED_TASKS = {
    "numeric": 150,
    "lookup": 62,
    "concept": 28,
    "debug": 14,
    "codegen": 9,
    "contrast": 11,
}

# Positive assertion that insect glutamate is excitatory / +1.
# Vertebrate-column wording ("척추동물 ... +1") is allowed.
_GLU_ASSERT = re.compile(
    r"""
    (?:
        (?:곤충|초파리|insect|drosophila|fly) .{0,40}?
        (?:글루타메이트|glutamate)
        |
        (?:글루타메이트|glutamate) .{0,40}?
        (?:곤충|초파리|insect|drosophila)
    )
    .{0,48}?
    (?:
        (?<!-) \+1
        | 플러스\s*1
        | 흥분(?! 이 아니라)
        | excitatory
    )
    """,
    re.I | re.S | re.X,
)

_GLU_BARE_PLUS = re.compile(
    r"(?:INSECT_SIGN\s*\[?\s*['\"]glutamate['\"]\]?\s*=\s*\+?1"
    r"|['\"]glutamate['\"]\s*:\s*\+?1)",
    re.I,
)

_NEGATION = re.compile(
    r"(아니|아니라|아니고|안\s*된|안\s*된다|잘못된|오류|버그|위험|하지\s*마|금지|"
    r"단언하면\s*안|never|not|incorrect|wrong|do not|don't|must not|dangerous)",
    re.I,
)

_VERTEBRATE = re.compile(r"(척추|vertebrate|AMPA|NMDA)", re.I)


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            rec["_src"] = f"{path.name}:{line_no}"
            rows.append(rec)
    return rows


def assistant_text(rec: dict) -> str:
    msgs = rec["messages"]
    a = [m["content"] for m in msgs if m["role"] == "assistant"]
    if len(a) != 1:
        raise AssertionError(f"{rec.get('_src')}: need exactly one assistant turn")
    return a[0]


def asserts_glu_plus(text: str) -> bool:
    """True when the assistant claims insect glutamate is +1 / excitatory."""
    if _GLU_BARE_PLUS.search(text):
        # allow if the line is clearly forbidding that assignment
        window = text
        if _NEGATION.search(window) and "never" in window.lower() or "금지" in window or "아니" in window:
            # still fail the literal INSECT_SIGN['glutamate'] = 1 assignment
            if re.search(r"INSECT_SIGN\s*\[?\s*['\"]glutamate['\"]\]?\s*=\s*\+?1", text, re.I):
                return True
            if re.search(r"['\"]glutamate['\"]\s*:\s*\+?1", text):
                return True
        else:
            return True
    for m in _GLU_ASSERT.finditer(text):
        span = text[max(0, m.start() - 40) : m.end() + 40]
        if _VERTEBRATE.search(span):
            continue
        if _NEGATION.search(span):
            continue
        return True
    return False


def parse_answer_vec(text: str) -> np.ndarray:
    m = re.search(r"ANSWER_I:\s*\[([^\]]+)\]", text)
    if not m:
        raise AssertionError("numeric sample missing ANSWER_I")
    return np.fromstring(m.group(1), sep=",")


def parse_int_field(text: str, key: str) -> int:
    m = re.search(rf"{key}:\s*(-?\d+)", text)
    if not m:
        raise AssertionError(f"numeric sample missing {key}")
    return int(m.group(1))


def recompute(net: dict) -> tuple[np.ndarray, int, int]:
    names = net["neurons"]
    idx = {n: i for i, n in enumerate(names)}
    n = len(names)
    W = np.zeros((n, n), dtype=float)
    n_pos = n_neg = 0
    for pre, post, w, ntv in net["edges"]:
        if int(w) < 5:
            continue
        sw = float(int(w) * kn.INSECT_SIGN[ntv])
        W[idx[pre], idx[post]] = sw
        if sw > 0:
            n_pos += 1
        elif sw < 0:
            n_neg += 1
    I = W.T @ np.asarray(net["x"], dtype=float)
    return I, n_pos, n_neg


def check_schema(rec: dict) -> None:
    msgs = rec.get("messages")
    if not isinstance(msgs, list) or len(msgs) != 3:
        raise AssertionError(f"{rec.get('_src')}: messages must be [system, user, assistant]")
    roles = [m.get("role") for m in msgs]
    if roles != ["system", "user", "assistant"]:
        raise AssertionError(f"{rec.get('_src')}: roles {roles}")
    for m in msgs:
        if not str(m.get("content", "")).strip():
            raise AssertionError(f"{rec.get('_src')}: empty content")


def check_facts(rec: dict, include_inferred: bool) -> None:
    meta = rec.get("meta") or {}
    ids = meta.get("fact_ids") or []
    allowed = kn.fact_map(include_inferred=include_inferred)
    for fid in ids:
        if fid not in allowed:
            raise AssertionError(f"{rec.get('_src')}: fact {fid} not in ledger (inferred={include_inferred})")
        if not include_inferred and allowed[fid].prov == "inferred":
            raise AssertionError(f"{rec.get('_src')}: inferred fact leaked: {fid}")


def check_must_contain(rec: dict) -> None:
    meta = rec.get("meta") or {}
    text = assistant_text(rec)
    for token in meta.get("must_contain") or []:
        if token not in text:
            raise AssertionError(f"{rec.get('_src')} {meta.get('id')}: missing {token!r}")


def check_numeric(rec: dict) -> None:
    meta = rec.get("meta") or {}
    net = meta.get("net")
    if not net:
        raise AssertionError(f"{rec.get('_src')}: numeric without net")
    text = assistant_text(rec)
    I_hat, pos_hat, neg_hat = recompute(net)
    I_txt = parse_answer_vec(text)
    if I_txt.shape != I_hat.shape or not np.allclose(I_txt, I_hat, atol=1e-6, rtol=1e-6):
        raise AssertionError(
            f"{rec.get('_src')} {meta.get('id')}: I mismatch file={I_txt} recomputed={I_hat}"
        )
    if parse_int_field(text, "ANSWER_POS") != pos_hat:
        raise AssertionError(f"{rec.get('_src')}: POS mismatch")
    if parse_int_field(text, "ANSWER_NEG") != neg_hat:
        raise AssertionError(f"{rec.get('_src')}: NEG mismatch")


def verify(train: list[dict], val: list[dict], *, include_inferred: bool, strip_meta: bool) -> dict:
    rows = train + val
    errors: list[str] = []

    if include_inferred and not strip_meta:
        if len(train) != 246 or len(val) != 28:
            errors.append(f"split sizes {len(train)}/{len(val)} != 246/28")
        if len(rows) != 274:
            errors.append(f"total {len(rows)} != 274")

    ids = []
    tasks = Counter()
    for rec in rows:
        src = rec.get("_src")
        try:
            check_schema(rec)
            if asserts_glu_plus(assistant_text(rec)):
                raise AssertionError("assistant asserts insect glutamate is +1")
            if not strip_meta:
                check_facts(rec, include_inferred)
                check_must_contain(rec)
                meta = rec["meta"]
                ids.append(meta["id"])
                tasks[meta["task"]] += 1
                if meta["task"] == "numeric":
                    check_numeric(rec)
        except AssertionError as exc:
            errors.append(f"{src}: {exc}")

    if ids and len(ids) != len(set(ids)):
        errors.append("duplicate sample ids")

    if include_inferred and not strip_meta:
        for task, n in EXPECTED_TASKS.items():
            if tasks[task] != n:
                errors.append(f"task {task}: {tasks[task]} != {n}")
        n_ok = tasks["numeric"]
        if n_ok != 150:
            errors.append(f"numeric count {n_ok}")

    report = {
        "n_train": len(train),
        "n_val": len(val),
        "tasks": dict(tasks),
        "errors": errors,
        "ok": not errors,
    }
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, default=ROOT / "data")
    p.add_argument("--include-inferred", action="store_true")
    p.add_argument("--strip-meta", action="store_true")
    args = p.parse_args(argv)

    train = load_jsonl(args.data_dir / "train.jsonl")
    val = load_jsonl(args.data_dir / "val.jsonl")
    report = verify(
        train,
        val,
        include_inferred=args.include_inferred,
        strip_meta=args.strip_meta,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if report["errors"]:
        print(f"FAILED: {len(report['errors'])} errors", file=sys.stderr)
        for e in report["errors"][:20]:
            print(" -", e, file=sys.stderr)
        return 1
    n_num = report["tasks"].get("numeric", 0)
    print(f"OK  numeric recompute {n_num}/{n_num}  glu+1 gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
