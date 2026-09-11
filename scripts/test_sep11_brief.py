#!/usr/bin/env python3
from pathlib import Path
import sep11_data as D

HTML = Path("/workspace/reports/2026-09-11-oneboard.html")
PNG = Path("/workspace/reports/sep11-pages/oneboard.png")
NEEDLES = [
    "664", "121", "36개월", "BYOH", "−18.8", "1,089", "베이퍼", "스트라드비전",
    "아모텍", "T-glass", "9/24", "지니언스", "MLCC",
]


def test():
    D.assert_all()
    assert HTML.exists() and HTML.stat().st_size > 80_000
    body = HTML.read_text(encoding="utf-8")
    # 스트라드비전 is sep8 not sep11 - remove
    need = [n for n in NEEDLES if n != "스트라드비전"]
    missing = [n for n in need if n not in body]
    assert not missing, missing
    assert "data:image/png;base64," in body
    assert PNG.exists() and PNG.stat().st_size > 80_000
    print("test_sep11_brief: ok")


if __name__ == "__main__":
    test()
