"""python -m insights DATA -o OUT"""

from __future__ import annotations

import argparse
from pathlib import Path

from insights.distill import distill_path
from insights.render import write_outputs, write_unified
from insights.transcript import distill_transcript_path, write_study
from insights.unify import unify

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "raw" / "2026-09-29_quick_comments.txt"
DEFAULT_TITLE = "9월 29일 퀵 코멘트, 화자가 말한 뜻"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="퀵 코멘트에서 화자의 판단을 증류한다.")
    parser.add_argument("source", nargs="?", default=str(DEFAULT_INPUT), help="Quick 코멘트 원문")
    parser.add_argument("-o", "--out", default="out/insights", help="md, json, docx를 쓸 폴더")
    parser.add_argument("--title", default=DEFAULT_TITLE)
    parser.add_argument("--html", action="append", default=[], help="해석 HTML. 있으면 퀵 코멘트와 한 편으로 합친다")
    parser.add_argument("--transcript", help="방송 전사. 오늘의 논리를 증류한다")
    parser.add_argument("--print", action="store_true", dest="show", help="판단 문장만 stdout에 찍는다")
    args = parser.parse_args(argv)
    if args.transcript:
        study = distill_transcript_path(args.transcript)
        paths = write_study(study, Path(args.out))
        if args.show:
            for piece in study.pieces:
                print(f"[{piece.label}] {piece.point}")
            return
        print(f"sentences={study.stats.get('sentences')} pieces={study.stats.get('pieces')}")
        for label, path in paths.items():
            print(f"{label}: {path}")
        return
    if args.html:
        doc = unify(args.source, args.html)
        paths = write_unified(doc, Path(args.out))
        if args.show:
            for piece in doc.pieces:
                from insights.unify import piece_point

                print(f"[{piece.label}] {piece_point(piece)}")
            return
        print(
            f"essays={doc.stats.get('essays')} blocks={doc.stats.get('blocks')} "
            f"pieces={doc.stats.get('pieces')}"
        )
        for label, path in paths.items():
            print(f"{label}: {path}")
        return
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
