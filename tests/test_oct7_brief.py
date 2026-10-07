#!/usr/bin/env python3
"""Oct 7 brief smoke tests."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("/workspace")
sys.path.insert(0, str(ROOT / "scripts"))

import oct7_data as D  # noqa: E402
import generate_oct7_brief as brief  # noqa: E402


def test_data_invariants():
    assert D.CPU["citi"]["oct"].startswith("2030")
    assert any("300" in row[1] for row in D.CPU["compare"])
    assert any(r[0] == "Micron" for r in D.MEMORY_VAL["rows"])
    assert len(D.CHINA_AI["verdicts"]) == 5
    assert D.CHINA_AI["verdicts"][-1][2] == "bad"
    assert D.PSK["tp"].startswith("한화")
    assert "전력" in D.MIDTERM["title"]
    assert len(D.MUSE["ram_path"]) == 3


def test_html_contains_key_sections():
    html = brief.build_html()
    for needle in [
        "MUSE",
        "$300B",
        "피에스케이",
        "중간선거",
        "Sandisk",
        "토큰당 가격",
        "id=\"cpu\"",
        "01_cpu_tam.png",
    ]:
        assert needle in html, needle


def test_md_oneline():
    md = brief.build_md()
    assert D.ONELINE in md
    assert "체크리스트" in md


def test_artifacts_exist_after_main(tmp_path=None):
    brief.main()
    assert (ROOT / "lectures" / brief.HTML_NAME).is_file()
    assert (ROOT / "lectures" / brief.MD_NAME).is_file()
    assert brief.REPORT_HTML.is_file()
    html = brief.REPORT_HTML.read_text(encoding="utf-8")
    assert "charts/" in html
    assert "../reports/charts/" not in html


if __name__ == "__main__":
    test_data_invariants()
    test_html_contains_key_sections()
    test_md_oneline()
    test_artifacts_exist_after_main()
    print("ok")
