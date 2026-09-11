#!/usr/bin/env python3
"""Gates for the 352/80/24 domain set + evidence cards."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "sft"))

import retrieve  # noqa: E402
import tools  # noqa: E402
import verify_sft  # noqa: E402

EXPECTED = {"train": 352, "validation": 80, "eval": 24}


def load(path: Path) -> list[dict]:
    rows = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        rec = json.loads(line)
        rec["_src"] = f"{path.name}:{i}"
        rows.append(rec)
    return rows


def check_calc(rec: dict) -> None:
    net = rec["meta"]["net"]
    payload = {
        "neurons": net["neurons"],
        "edges": net["edges"],
        "x": net["x"],
        "V": [0.0] * len(net["neurons"]),
        "tau": 10.0,
        "dt": 1.0,
    }
    out = tools.current_and_lif(payload)
    text = rec["messages"][2]["content"]
    I_txt = verify_sft.parse_answer_vec(text)
    if not np.allclose(I_txt, np.asarray(out["I"], float), atol=1e-6):
        raise AssertionError(f"I mismatch {I_txt} vs {out['I']}")
    m = re.search(r"ANSWER_DV:\s*\[([^\]]+)\]", text)
    if not m:
        raise AssertionError("missing ANSWER_DV")
    dV = np.fromstring(m.group(1), sep=",")
    if not np.allclose(dV, np.asarray(out["dV"], float), atol=1e-6):
        raise AssertionError("dV mismatch")


def verify(data_dir: Path) -> dict:
    errors = []
    searcher = retrieve.ConnectomeSearch()
    if len(searcher.cards) != 12:
        errors.append("need 12 evidence cards")

    counts = {}
    tasks = Counter()
    for split, n_exp in EXPECTED.items():
        name = "train.jsonl" if split == "train" else f"{split}.jsonl"
        rows = load(data_dir / name)
        counts[split] = len(rows)
        if len(rows) != n_exp:
            errors.append(f"{split} {len(rows)} != {n_exp}")
        for rec in rows:
            try:
                verify_sft.check_schema(rec)
                text = verify_sft.assistant_text(rec)
                if verify_sft.asserts_glu_plus(text):
                    raise AssertionError("glu +1 assertion")
                for tok in rec["meta"].get("must_contain") or []:
                    if tok not in text:
                        raise AssertionError(f"missing {tok!r}")
                tasks[rec["meta"]["task"]] += 1
                if rec["meta"]["task"] == "calculation":
                    check_calc(rec)
                if rec["meta"]["task"] == "evidence" and rec["meta"].get("card_id"):
                    if not searcher.card(rec["meta"]["card_id"]):
                        raise AssertionError("missing card")
            except AssertionError as exc:
                errors.append(f"{rec.get('_src')}: {exc}")

    return {"counts": counts, "tasks": dict(tasks), "errors": errors, "ok": not errors}


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", type=Path, default=HERE / "data")
    args = p.parse_args(argv)
    report = verify(args.data_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if not report["ok"]:
        print("FAILED", file=sys.stderr)
        for e in report["errors"][:25]:
            print(" -", e, file=sys.stderr)
        return 1
    print("OK domain set + 12 cards + calc recompute + glu gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
