#!/usr/bin/env python3
"""Must-keep facts from the Hana 7/14 note and Aug updates."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "reports" / "2026-08-28-alteogen-alt-b4.html",
    ROOT / "lectures" / "8월 28일 알테오젠 ALT-B4 분석.md",
]

NEEDLES = [
    "WO2026/142299",
    "WO2026/142300",
    "Enhanze",
    "ALT-B4",
    "165",
    "120",
    "37.5",
    "463",
    "365",
    "Intas",
    "Sandoz",
    "berahyaluronidase",
    "대표청구항",
    "580,000",
    "279,500",
    "320,000",
]


def main() -> None:
    missing = []
    for path in FILES:
        text = path.read_text(encoding="utf-8")
        for n in NEEDLES:
            if n not in text:
                missing.append(f"{path.name}: {n}")
    if missing:
        raise SystemExit("missing facts:\n" + "\n".join(missing))
    print(f"ok · {len(NEEDLES)} needles in {len(FILES)} files")


if __name__ == "__main__":
    main()
