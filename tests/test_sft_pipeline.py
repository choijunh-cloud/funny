"""SFT ledger / verifier gates."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "sft"))

import build_sft  # noqa: E402
import knowledge as kn  # noqa: E402
import verify_sft  # noqa: E402


def test_exactly_four_inferred_facts():
    inferred = kn.inferred_ids()
    assert inferred == (
        "inf.mode_tie",
        "inf.mode_nan",
        "inf.dale_stages",
        "inf.vert_receptors",
    )


def test_glutamate_is_minus_one():
    assert kn.INSECT_SIGN["glutamate"] == -1
    assert kn.insect_sign("Glu") == -1
    assert kn.insect_sign("아세틸콜린") == 1


def test_context_only_excludes_inferred():
    ids = set(kn.fact_map(include_inferred=False))
    assert "sign.glu" in ids
    assert "inf.mode_tie" not in ids


def test_glu_plus_gate_catches_assertion_and_allows_contrast():
    assert verify_sft.asserts_glu_plus("곤충에서 글루타메이트는 +1이다.")
    assert verify_sft.asserts_glu_plus("INSECT_SIGN['glutamate'] = 1")
    assert not verify_sft.asserts_glu_plus(
        "곤충 CNS에서 글루타메이트는 -1이다. +1로 단언하면 안 된다."
    )
    assert not verify_sft.asserts_glu_plus(
        "척추동물 참고 컬럼에서 글루타메이트는 +1(흥분, AMPA/NMDA)이다."
    )


def test_recompute_matches_builder_helper():
    rng = np.random.default_rng(0)
    net = build_sft.make_net(rng, n=4)
    rows = build_sft.signed_rows(net)
    _W, I = build_sft.dense_WTx(net, rows)
    I2, pos, neg = verify_sft.recompute(net)
    assert np.allclose(I, I2)
    assert pos + neg == len(rows)


def test_generated_dataset_passes_verifier(tmp_path: Path):
    items = build_sft.generate(include_inferred=True)
    assert len(items) == 274
    train = [r for r in items if r["meta"]["split"] == "train"]
    val = [r for r in items if r["meta"]["split"] == "val"]
    build_sft.write_jsonl(tmp_path / "train.jsonl", train, strip=False)
    build_sft.write_jsonl(tmp_path / "val.jsonl", val, strip=False)
    loaded_train = verify_sft.load_jsonl(tmp_path / "train.jsonl")
    loaded_val = verify_sft.load_jsonl(tmp_path / "val.jsonl")
    report = verify_sft.verify(
        loaded_train, loaded_val, include_inferred=True, strip_meta=False
    )
    assert report["ok"], report["errors"][:8]
    assert report["tasks"]["numeric"] == 150


def test_strip_meta_is_messages_only():
    items = build_sft.generate(include_inferred=True)
    stripped = build_sft.strip_meta(items[0])
    assert set(stripped) == {"messages"}
    assert json.loads(json.dumps(stripped))["messages"][0]["role"] == "system"
