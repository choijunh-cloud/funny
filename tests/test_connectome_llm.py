"""Domain package: cards, retrieval, tools, splits, LoRA infra."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "connectome_llm"))
sys.path.insert(0, str(ROOT / "sft"))

import infer  # noqa: E402
import retrieve  # noqa: E402
import tools  # noqa: E402
import train_lora  # noqa: E402
import verify_domain  # noqa: E402
import verify_sft  # noqa: E402


def test_twelve_cards_and_search_files():
    s = retrieve.ConnectomeSearch()
    assert len(s.cards) == 12
    hits = s.search("connectome-weights-male-cns feather 파일", k=3)
    assert hits and hits[0].id == "card.files"


def test_tool_refuses_without_net():
    try:
        tools.current_WTx({})
    except tools.ToolError as exc:
        assert "거부" in str(exc)
    else:
        raise AssertionError("should refuse")


def test_tool_dedupes_and_matches_independent_WTx():
    payload = {
        "neurons": ["A", "B"],
        "edges": [("A", "B", 3, "glutamate"), ("A", "B", 4, "glutamate")],
        "x": [1, 0],
    }
    out = tools.current_WTx(payload)
    assert out["rows"][0]["signed_weight"] == -7
    # I_B = W[A,B] * x_A = -7
    assert out["I"] == [-0.0, -7.0] or np.allclose(out["I"], [0, -7])


def test_glu_plus_gate_still_on():
    assert verify_sft.asserts_glu_plus("초파리 글루타메이트는 +1이다.")


def test_mask_labels_ignore_prompt():
    ids, labels = train_lora.mask_labels([1, 2, 3], [4, 5], max_length=8)
    assert labels[:3] == [train_lora.IGNORE] * 3
    assert labels[3:5] == [4, 5]
    assert labels[5:] == [train_lora.IGNORE] * 3
    assert len(ids) == 8


def test_domain_jsonl_if_present():
    data = ROOT / "connectome_llm" / "data"
    if not (data / "train.jsonl").exists():
        return
    report = verify_domain.verify(data)
    assert report["ok"], report["errors"][:6]
    assert report["counts"] == {"train": 352, "validation": 80, "eval": 24}


def test_retrieve_only_does_not_invent_when_empty():
    out = infer.answer("행성 X의 시냅스 수는 몇 개인가?")
    assert "만들지" in out["text"] or "수치를 만들지" in out["text"]
