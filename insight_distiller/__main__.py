"""python -m insight_distiller --inputs sources --out output"""

from __future__ import annotations

import argparse
from pathlib import Path

from insight_distiller.pipeline import run


def main() -> None:
    parser = argparse.ArgumentParser(description="반도체 자료를 읽어 투자 인사이트를 증류합니다.")
    parser.add_argument("--inputs", type=Path, default=Path("sources"))
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--no-ocr", action="store_true", help="PDF 텍스트층만 사용합니다.")
    args = parser.parse_args()
    knowledge = run(args.inputs, args.out, ocr=not args.no_ocr)
    chars = sum(row["chars"] for row in knowledge.documents)
    print(f"문서 {len(knowledge.documents)}개, 청크 {len(knowledge.chunks)}개, {chars:,}자")
    print(f"팩트 {len(knowledge.facts)}개, 테마 {len(knowledge.themes)}개")
    print(f"메모: {args.out / '투자인사이트.md'}")


if __name__ == "__main__":
    main()
