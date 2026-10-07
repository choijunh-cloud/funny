#!/usr/bin/env python3
"""Distill entry delegates to oct7_model."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("/workspace/scripts")))
import oct7_distill as D
import oct7_model as M


def test_entry_writes(tmp_path=None):
    D.main()
    out = Path("/workspace/output/oct7")
    assert (out / "투자인사이트.md").is_file()
    assert (out / "model.json").is_file()
    text = (out / "투자인사이트.md").read_text(encoding="utf-8")
    assert "정밀 모델" in text
    assert "의사결정 규칙" in text


def test_thesis_has_numbers():
    m = M.run_model()
    assert "4.0x" in m["thesis"] or "PER" in m["thesis"]
    assert "300" in m["thesis"] or "$" in m["thesis"]


if __name__ == "__main__":
    test_entry_writes()
    test_thesis_has_numbers()
    print("ok")
