#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path("/workspace/scripts")))
import oct7_youtube as Y
import oct7_distill as D


def test_split_six_episodes():
    text = Y.SRC.read_text(encoding="utf-8", errors="replace")
    meta = Y.split_episodes(text)
    assert len(meta["episodes"]) == 6
    assert meta["yt_chars"] > 100_000
    assert "ep6_plusclick" in meta["episodes"]
    assert meta["episodes"]["ep6_plusclick"]["chars"] > 5_000


def test_plusclick_claims():
    r = Y.run()
    themes = {c["theme"] for c in r["meta"]["claims"] if c["episode"] == "ep6_plusclick"}
    for need in ("기억과정신", "수출", "삼성실적", "체크포인트", "현대차"):
        assert need in themes, themes
    assert len(r["meta"]["claims"]) >= 30


def test_integrated_contains_youtube():
    D.main()
    text = Path("/workspace/output/oct7/투자인사이트.md").read_text(encoding="utf-8")
    assert "유튜브/방송" in text
    assert "기억과 정신" in text or "기억과정신" in text
    assert "1,200억" in text or "1200억" in text
    assert "의사결정 규칙" in text
    assert len(text) > 6000


if __name__ == "__main__":
    test_split_six_episodes()
    test_plusclick_claims()
    test_integrated_contains_youtube()
    print("ok")
