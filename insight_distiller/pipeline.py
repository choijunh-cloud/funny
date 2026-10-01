"""수집, 추출, 학습, 증류를 한 번에 실행한다."""

from __future__ import annotations

import json
from pathlib import Path

from insight_distiller.distill import render
from insight_distiller.extract import extract
from insight_distiller.ingest import ingest_dir
from insight_distiller.learn import learn
from insight_distiller.models import Knowledge


def run(inputs: Path, out: Path, ocr: bool = True) -> Knowledge:
    chunks = ingest_dir(inputs, ocr=ocr)
    if not chunks:
        raise SystemExit(f"읽을 문서가 없습니다: {inputs}")
    facts = extract(chunks)
    knowledge = learn(chunks, facts)
    report = render(knowledge)
    out.mkdir(parents=True, exist_ok=True)
    (out / "투자인사이트.md").write_text(report, encoding="utf-8")
    (out / "knowledge.json").write_text(
        json.dumps(_payload(knowledge), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return knowledge


def _payload(knowledge: Knowledge) -> dict:
    return {
        "documents": knowledge.documents,
        "themes": knowledge.themes,
        "associations": knowledge.associations,
        "equipment": knowledge.equipment,
        "facts": [
            {
                "key": fact.key,
                "display": fact.display,
                "source": fact.source,
                "locator": fact.locator,
                "quality": fact.quality,
                "support": fact.support,
                "mentions": fact.mentions,
                "snippet": fact.snippet,
            }
            for fact in knowledge.facts
        ],
    }
