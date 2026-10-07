#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("/workspace/scripts")))
import oct7_distill as D


def test_final_brief_pillars():
    text = Path("/workspace/output/oct7/최종본.md").read_text(encoding="utf-8")
    for needle in ("기둥 지도", "4.0x", "기억", "1200", "입찰"):
        assert needle in text
    assert len(text) > 4000


def test_entry_writes():
    D.main()
    out = Path("/workspace/output/oct7")
    assert (out / "투자인사이트.md").is_file()
    assert (out / "youtube_insights.md").is_file()
    assert (out / "model.json").is_file()
    text = (out / "투자인사이트.md").read_text(encoding="utf-8")
    assert "유튜브/방송" in text
    assert "정밀 모델" in text
    assert len(text) > 6000


if __name__ == "__main__":
    test_entry_writes()
    print("ok")
