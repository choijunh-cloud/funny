"""python -m insights DATA -o OUT"""

from __future__ import annotations

import argparse
from pathlib import Path

from insights.distill import distill_path
from insights.render import write_outputs

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "raw" / "2026-09-29_quick_comments.txt"
DEFAULT_TITLE = "9월 29일 퀵 코멘트, 화자가 말한 뜻"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="퀵 코멘트에서 화자의 판단을 증류한다.")
    parser.add_argument("source", nargs="?", default=str(DEFAULT_INPUT), help="Quick 코멘트 원문")
    parser.add_argument("-o", "--out", default="out/insights", help="md, json, docx를 쓸 폴더")
    parser.add_argument("--title", default=DEFAULT_TITLE)
    parser.add_argument("--print", action="store_true", dest="show", help="판단 문장만 stdout에 찍는다")
    args = parser.parse_args(argv)
    briefing = distill_path(args.source)
    paths = write_outputs(briefing, Path(args.out), args.title)
    if args.show:
        for meaning in briefing.meanings:
            print(f"[{meaning.label}] {meaning.point}")
            if meaning.against:
                print(f"  밀어냄: {meaning.against}")
            if meaning.watch:
                print(f"  그래서: {meaning.watch}")
            print()
    else:
        print(f"comments={briefing.stats.get('comments')} meanings={briefing.stats.get('meanings')}")
        for label, path in paths.items():
            print(f"{label}: {path}")


if __name__ == "__main__":
    main()
