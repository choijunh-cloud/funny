#!/usr/bin/env python3
"""Fail if distinctive 8/28 broadcast phrases are missing from the briefing."""

from __future__ import annotations

from pathlib import Path

HTML = Path("/workspace/reports/2026-08-28-broadcast-brief.html")

MUST = [
    "3.50",
    "1,280원",
    "6,400",
    "6,200",
    "3.25",
    "5.31%",
    "40조 달러",
    "3.7%",
    "블랙먼데이",
    "할로윈",
    "본전되면",
    "250만",
    "25만",
    "30만",
    "88조",
    "790만",
    "370만",
    "−5만",
    "11.4만",
    "3.8",
    "3.75",
    "2034",
    "1,400원",
    "1,600억$",
    "4nm",
    "2nm",
    "Nebius",
    "LPX",
    "HBM4",
    "하나마이크론",
    "테스나",
    "닉스 6",
    "삼전 4",
    "2.6조",
    "7,000",
    "7,400",
    "8,500",
    "60조",
    "2,760억$",
    "1,190억$",
    "138",
    "68%",
    "PolyPeptide",
    "3조",
    "59.4%",
    "Kevin Warsh",
    "Scott Bessent",
    "CXMT",
    "YMTC",
    "삼각",
    "20%",
    "150엔",
    "140엔",
    "알상무",
    "박세익",
    "문남중",
    "이영수",
    "박근형",
    "김장현",
    "이진호",
    "+70%",
    "공급천장",
    "비CSP",
    "캔슬림",
    "눈폭풍",
    "압구정",
    "페드워치",
    "전약후강",
    "매수·매도 권유",
]


def main() -> None:
    text = HTML.read_text(encoding="utf-8")
    missing = [p for p in MUST if p not in text]
    if missing:
        raise SystemExit("missing phrases:\n" + "\n".join(missing))
    print(f"ok · {len(MUST)} phrases in {HTML.name}")


if __name__ == "__main__":
    main()
