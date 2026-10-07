#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("/workspace/scripts")))
import oct7_distill as D


def test_extract_has_core_themes():
    docs = D._read_extracted()
    claims = D.extract_claims(docs)
    themes = {c.theme for c in claims if c.quality == "core"}
    for need in ("AI CapEx", "Agent 메모리", "메모리 밸류", "CPU/Agentic", "후공정", "정책/전력"):
        assert need in themes or any(need.split("/")[0] in t for t in themes), themes


def test_render_chat_short():
    docs = D._read_extracted()
    data = D.distill(D.extract_claims(docs))
    chat = D.render_chat(data)
    assert "한 줄" in chat
    assert "하지 말 것" in chat
    assert len(chat) < 3500


if __name__ == "__main__":
    test_extract_has_core_themes()
    test_render_chat_short()
    print("ok")
