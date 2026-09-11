#!/usr/bin/env python3
"""Retrieve + tools (+ optional LoRA) answer loop for other bots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import retrieve  # noqa: E402
import tools  # noqa: E402


def answer(query: str, net: dict | None = None, lang: str = "ko") -> dict:
    hits = retrieve.ConnectomeSearch().search(query, k=4)
    ctx = retrieve.ConnectomeSearch().as_context(query, k=4, lang=lang)
    calc = None
    if net:
        try:
            calc = tools.current_and_lif(
                {
                    "neurons": net["neurons"],
                    "edges": net["edges"],
                    "x": net["x"],
                    "V": net.get("V") or [0.0] * len(net["neurons"]),
                    "tau": net.get("tau", 10.0),
                    "dt": net.get("dt", 1.0),
                }
            )
        except tools.ToolError as exc:
            calc = {"refused": str(exc)}
    wants_number = any(k in query.lower() for k in ("몇", "수", "count", "how many", "Δv", "전류", "i ="))
    strong = [h for h in hits if h.score >= 3]
    if wants_number and not calc and not any(h.numbers for h in strong):
        text = (
            "근거 카드나 실행/미니넷이 없어 수치를 만들지 않는다. "
            "파일·버전은 검색 결과를 보고, 전류는 에지 표를 도구에 넘기라."
        )
    elif calc and "I" in calc:
        text = ctx + f"\n\n도구 I={calc['I']} dV={calc['dV']}"
    else:
        text = ctx
    return {
        "text": text,
        "hits": [{"id": h.id, "score": h.score, "version": h.version} for h in hits],
        "calc": calc,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--query", required=True)
    p.add_argument("--net-json", type=Path, default=None)
    p.add_argument("--adapter", type=Path, default=None, help="unused unless a generative model is loaded")
    args = p.parse_args(argv)
    net = json.loads(args.net_json.read_text()) if args.net_json else None
    out = answer(args.query, net=net)
    print(json.dumps(out, ensure_ascii=False, indent=2))
    if args.adapter:
        print("note: adapter present but generation is retrieve+tools; load a local LLM to decode LoRA.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
