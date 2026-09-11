#!/usr/bin/env python3
"""Compare retrieve-only answers to gold eval items.

A generative LoRA eval is recorded as not_run until a real local model is trained.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
import sys

sys.path.insert(0, str(HERE))
import infer  # noqa: E402


def score_item(gold: dict, pred_text: str) -> dict:
    must = gold["meta"].get("must_contain") or []
    hits = [t in pred_text for t in must]
    return {
        "id": gold["meta"]["id"],
        "task": gold["meta"]["task"],
        "n_must": len(must),
        "n_hit": sum(hits),
        "ok": bool(must) and all(hits),
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--eval", type=Path, default=HERE / "data" / "eval.jsonl")
    p.add_argument("--out", type=Path, default=HERE / "runs" / "eval_compare.json")
    args = p.parse_args(argv)

    rows = [json.loads(l) for l in args.eval.read_text(encoding="utf-8").splitlines() if l.strip()]
    retrieve_scores = []
    gold_scores = []
    for rec in rows:
        q = rec["messages"][1]["content"]
        net = rec["meta"].get("net")
        pred = infer.answer(q, net=net)
        retrieve_scores.append(score_item(rec, pred["text"]))
        gold_scores.append(score_item(rec, rec["messages"][2]["content"]))

    def rate(xs):
        return sum(1 for x in xs if x["ok"]) / max(len(xs), 1)

    report = {
        "n_eval": len(rows),
        "retrieve_only_exact_must": rate(retrieve_scores),
        "gold_sft_style_exact_must": rate(gold_scores),
        "lora_generation": "not_run",
        "note": (
            "Same 24 eval items. retrieve_only uses evidence cards + tools. "
            "gold_sft_style is the fine-tune target text (not a trained LLM). "
            "Train a local model with train_lora.py to fill lora_generation."
        ),
        "retrieve_items": retrieve_scores,
        "gold_items": gold_scores,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in report if k not in {"retrieve_items", "gold_items"}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
