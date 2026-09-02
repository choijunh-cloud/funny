#!/usr/bin/env python3
"""생성 파일에 원문 3개 PDF의 핵심 문장이 들어갔는지 확인."""

from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

LECTURES = Path("/workspace/lectures")
DOCX = LECTURES / "9월 2일 모닝미팅 정리.docx"
HTML = LECTURES / "9월 2일 모닝미팅 정리.html"
MD = LECTURES / "9월 2일 모닝미팅 정리.md"

NEEDLES = [
    "유가",
    "68.2%",
    "Low Hire",
    "Fear",
    "25.8조",
    "11.84조",
    "609억",
    "1.82조",
    "10억",
    "삼성전기",
    "Dell",
    "9/4",
]


def docx_text(path: Path) -> str:
    with ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    return "".join(t.text or "" for t in root.findall(".//w:t", ns))


def test_outputs_exist_and_cover():
    assert DOCX.exists() and DOCX.stat().st_size > 10_000
    assert HTML.exists() and HTML.stat().st_size > 5_000
    assert MD.exists()
    body = docx_text(DOCX) + HTML.read_text(encoding="utf-8") + MD.read_text(encoding="utf-8")
    missing = [n for n in NEEDLES if n not in body]
    assert not missing, f"missing: {missing}"


if __name__ == "__main__":
    test_outputs_exist_and_cover()
    print("test_sep02_brief_coverage: ok")
