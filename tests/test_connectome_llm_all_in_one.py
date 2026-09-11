"""Stdlib gates for the single-file connectome LLM tool.

Does not call or download a chat model. Does not treat Glu=+1 as globally forbidden.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "connectome_llm_all_in_one.py"
sys.path.insert(0, str(ROOT))

import connectome_llm_all_in_one as aio  # noqa: E402


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd or ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_embedded_counts_and_no_gold_in_index():
    assert len(aio.KNOWLEDGE_CARDS) == 12
    cases = aio.read_cases(None)
    assert len(cases) == 24
    assert sum(c["kind"] == "numeric" for c in cases) == 8
    assert sum(c["kind"] == "manual" for c in cases) == 16
    card_text = " ".join(c["text"] for c in aio.KNOWLEDGE_CARDS)
    for case in cases:
        assert case["prompt"] not in card_text


def test_glu_plus_one_is_not_blanket_banned():
    prompts = " ".join(p for _, p, _ in aio.CONCEPTS)
    answers = " ".join(a for _, _, a in aio.CONCEPTS)
    assert "글루타메이트를 전부 +1" in prompts
    assert "그 변경만으로 정확도가 좋아진다고 판단할 수 없습니다" in answers
    assert "Glu=-1은 수용체 정보를 생략한 기본 모델 가정" in answers


def test_signed_input_presynaptic_sign_and_mask():
    args = {
        "nodes": ["E", "I", "M", "R"],
        "edges": [
            {"pre": "E", "post": "R", "weight": 9},
            {"pre": "I", "post": "R", "weight": 4},
            {"pre": "M", "post": "R", "weight": 100},
        ],
        "spikes": {"E": 1, "I": 1, "M": 1},
        "signs": {"E": 1, "I": -1, "M": 0, "R": -1},
    }
    assert aio.signed_input(**args)["incoming"]["R"] == 5
    args["spikes"]["M"] = 0
    assert aio.signed_input(**args)["incoming"]["R"] == 5


def test_holdout_numeric_gold_matches_independent_math():
    cases = {c["id"]: c for c in aio.read_cases(None) if c["kind"] == "numeric"}
    assert cases["eval_num_01"]["expected_answer"]["input_current"] == [0, 6, -4]
    got = aio.signed_input(
        nodes=["A", "B", "C"],
        edges=[
            {"pre": "A", "post": "B", "weight": 6},
            {"pre": "B", "post": "C", "weight": 4},
            {"pre": "C", "post": "B", "weight": 2},
        ],
        spikes={"A": 1, "B": 1, "C": 0},
        signs={"A": 1, "B": -1, "C": -1},
    )
    assert [got["incoming"][n] for n in ["A", "B", "C"]] == [0, 6, -4]


def test_majority_and_lif_teaching_tools():
    assert aio.majority_vote([None, None])["nt"] == "unknown"
    assert aio.majority_vote(["ACh", "GABA"])["accepted"] is False
    assert aio.majority_vote(["ACh", "ACh", None])["accepted"] is True
    assert aio.lif_step(0.9, 2, gain=0.12)["spike"] == 1
    assert aio.lif_step(0.9, 100, refractory_left=1) == {
        "voltage": 0.0,
        "spike": 0,
        "refractory_left": 0,
    }


def test_prepare_does_not_call_a_model():
    prepared = aio.ConnectomeBot().prepare("Glu는 항상 억제성인가요?")
    assert prepared["model_called"] is False
    assert prepared["messages"][0]["role"] == "system"
    assert "nt_sign_receptors" in prepared["retrieved_ids"]


def test_build_verify_default_counts(tmp_path: Path):
    built = _run("build", "--output-dir", str(tmp_path / "sft_data"))
    assert built.returncode == 0, built.stderr
    manifest = json.loads((tmp_path / "sft_data" / "manifest.json").read_text())
    assert manifest["train_examples"] == 352
    assert manifest["validation_examples"] == 80
    assert manifest["model_trained"] is False
    exported = [
        json.loads(line)
        for line in (tmp_path / "sft_data" / "eval_prompts.jsonl").read_text().splitlines()
        if line.strip()
    ]
    assert len(exported) == 24
    assert all(not {"expected_answer", "rubric"} & row.keys() for row in exported)
    verified = _run("verify", "--data-dir", str(tmp_path / "sft_data"))
    assert verified.returncode == 0, verified.stderr
    report = json.loads(verified.stdout)
    assert report == {
        **report,
        "status": "passed",
        "train_examples": 352,
        "validation_examples": 80,
        "evaluation_cases": 24,
        "knowledge_cards": 12,
        "real_llm_performance_measured": False,
    }


def test_eval_scores_numeric_gold_and_holds_manual():
    cases = aio.read_cases(None)
    predictions = {
        case["id"]: (
            {"id": case["id"], "answer": case["expected_answer"]}
            if case["kind"] == "numeric"
            else {"id": case["id"], "response": "검토용 초안"}
        )
        for case in cases
    }
    report = aio.score(cases, predictions)
    assert report["numeric"]["correct"] == 8
    assert report["numeric"]["accuracy_all_numeric"] == 1.0
    assert report["conceptual"]["automated_accuracy"] is None
    assert report["conceptual"]["awaiting_human_review"] == 16
