"""CLI: python -m insight_distiller data/paste_copy_2.txt"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from insight_distiller.distill import build_report
from insight_distiller.parse import parse
from insight_distiller.render_docx import render_docx
from insight_distiller.render_md import render_markdown

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "paste_copy_2.txt"
DEFAULT_MD = ROOT / "output" / "insights.md"
DEFAULT_JSON = ROOT / "output" / "insights.json"
DEFAULT_DOCX = ROOT / "lectures" / "투자인사이트 증류.docx"


def run(source: Path, md_path: Path, json_path: Path, docx_path: Path) -> dict:
    text = source.read_text(encoding="utf-8")
    report = build_report(parse(text))
    markdown = render_markdown(report)
    payload = {
        "headline": report.headline,
        "stats": report.stats,
        "sources": report.sources,
        "chapters": report.chapters,
        "facts": report.facts.public(),
        "sections": [
            {
                "key": section.key,
                "title": section.title,
                "lead": section.lead,
                "table": section.table,
                "bullets": [
                    {"time": bullet.time, "source": bullet.source, "score": bullet.score, "text": bullet.text}
                    for bullet in section.bullets
                ],
            }
            for section in report.sections
        ],
        "checklist": report.checklist,
        "watchlist": [{"name": name, "count": count} for name, count in report.watchlist],
    }
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(markdown, encoding="utf-8")
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    render_docx(report, docx_path)
    return report.stats


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="투자 코멘트를 추출해 증류 문서로 만든다.")
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--md", type=Path, default=DEFAULT_MD)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--docx", type=Path, default=DEFAULT_DOCX)
    args = parser.parse_args(argv)
    stats = run(args.source, args.md, args.json, args.docx)
    print(
        f"quick {stats['quick_raw']} -> {stats['quick_kept']} "
        f"(dropped {stats['quick_dropped']}), transcripts {stats['transcript_blocks']}"
    )
    print(args.md)
    print(args.json)
    print(args.docx)


if __name__ == "__main__":
    main()
