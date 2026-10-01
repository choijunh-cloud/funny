"""추출된 근거로 테마 가중치와 기업-주제 연결을 만든다."""

from __future__ import annotations

import re

from insight_distiller.ingest import document_stats
from insight_distiller.models import Chunk, Fact, Knowledge

THEMES: dict[str, tuple[str, ...]] = {
    "메모리 가격": ("ASP", "판가", "가격 상승", "DRAM", "NAND", "eSSD"),
    "HBM": ("HBM", "HBM4", "베이스 다이", "본더", "HBM4E"),
    "공급 계약": ("SCA", "장기공급", "RPO", "약정", "테이크오어페이"),
    "공급 부족": ("공급부족", "공급 부족", "수급", "숏티지"),
    "수익성": ("영업이익", "GPM", "마진", "EPS", "OPM"),
    "투자와 소부장": ("Capex", "증설", "클린룸", "수주", "소부장", "증착"),
    "주주환원": ("자사주", "배당", "주주환원", "소각"),
    "환율": ("환율", "원/달러", "원달러", "1350", "1400"),
    "매크로": ("PCE", "금리", "국채", "Higher for longer"),
    "국산화": ("국산화", "펠리클", "블랭크", "EUV"),
}

ANCHORS = (
    "삼성전자",
    "SK하이닉스",
    "마이크론",
    "Micron",
    "SFA",
    "원익IPS",
    "HPSP",
    "한미반도체",
    "리노공업",
    "테스",
    "솔브레인",
    "에프에스티",
    "엔비디아",
    "NVIDIA",
)


def learn(chunks: list[Chunk], facts: list[Fact]) -> Knowledge:
    _relabel_asp(facts)
    themes = _theme_weights(chunks)
    return Knowledge(
        documents=document_stats(chunks),
        chunks=chunks,
        facts=facts,
        themes=themes,
        associations=_associations(chunks, themes),
        equipment=_equipment(chunks),
        comments=_comments(chunks),
    )


def _mentioned(company: str, text: str) -> bool:
    if company == "테스":
        return re.search(r"테스(?!트)", text) is not None
    return company in text


def _relabel_asp(facts: list[Fact]) -> None:
    brokers_by_date: dict[str, list[str]] = {}
    for fact in facts:
        if fact.key != "sec_broker_op":
            continue
        match = re.match(r"(\S+) \((\d{1,2}/\d{1,2})\)", fact.display)
        if match and match.group(1) != "미식별":
            brokers_by_date.setdefault(match.group(2), []).append(match.group(1))
    cursors: dict[tuple[str, str], int] = {}
    for fact in facts:
        if fact.key != "sec_asp_row" or "미식별" not in fact.display:
            continue
        match = re.match(r"(DRAM|NAND) 미식별 \((\d{1,2}/\d{1,2})\)", fact.display)
        if not match:
            continue
        names = brokers_by_date.get(match.group(2), [])
        cursor = cursors.get((match.group(1), match.group(2)), 0)
        if cursor >= len(names):
            continue
        fact.display = fact.display.replace("미식별", names[cursor], 1)
        cursors[(match.group(1), match.group(2))] = cursor + 1


def _theme_weights(chunks: list[Chunk]) -> list[dict]:
    rows = []
    for name, terms in THEMES.items():
        hits = 0
        weighted = 0.0
        sources: set[str] = set()
        for chunk in chunks:
            found = [term for term in terms if term in chunk.text]
            if not found:
                continue
            scale = 0.3 if chunk.kind == "transcript" else 1.0
            hits += 1
            weighted += chunk.quality * scale * len(found)
            sources.add(chunk.source)
        rows.append(
            {
                "theme": name,
                "chunks": hits,
                "weight": round(weighted, 2),
                "sources": len(sources),
            }
        )
    rows.sort(key=lambda row: row["weight"], reverse=True)
    return rows


def _associations(chunks: list[Chunk], themes: list[dict]) -> list[dict]:
    theme_terms = {row["theme"]: THEMES[row["theme"]] for row in themes}
    linked = []
    for company in ANCHORS:
        scores = []
        company_chunks = [chunk for chunk in chunks if _mentioned(company, chunk.text) and chunk.kind != "transcript"]
        if not company_chunks:
            company_chunks = [chunk for chunk in chunks if _mentioned(company, chunk.text)]
        if not company_chunks:
            continue
        for theme, terms in theme_terms.items():
            both = sum(1 for chunk in company_chunks if any(term in chunk.text for term in terms))
            if both:
                scores.append((theme, both))
        scores.sort(key=lambda item: item[1], reverse=True)
        if scores:
            linked.append(
                {
                    "company": company,
                    "mentions": len(company_chunks),
                    "themes": [{"theme": name, "chunks": count} for name, count in scores[:3]],
                }
            )
    linked.sort(key=lambda row: row["mentions"], reverse=True)
    return linked


def _equipment(chunks: list[Chunk]) -> dict:
    sections = []
    summary: list[str] = []
    for chunk in chunks:
        if chunk.kind != "pptx":
            continue
        lines = [line.strip() for line in chunk.text.splitlines() if line.strip()]
        if not lines:
            continue
        title, body = lines[0], lines[1:]
        if "투자 관점" in title:
            summary = body
            continue
        if not body:
            continue
        companies = []
        notes = []
        for line in body:
            match = re.match(r"^([^:：*]{2,24})\s*[:：]\s*(.+)$", line)
            if match:
                role = match.group(2).strip().replace("생사 기업", "생산 기업")
                companies.append({"name": match.group(1).strip(), "role": role})
            else:
                notes.append(line)
        sections.append(
            {
                "title": title,
                "locator": chunk.locator,
                "companies": companies,
                "notes": notes,
            }
        )
    return {"sections": sections, "summary": summary}


def _comments(chunks: list[Chunk]) -> list[dict]:
    rows = []
    for chunk in chunks:
        if chunk.kind != "txt":
            continue
        text = re.sub(r"\s+", " ", chunk.text).strip()
        themes = [name for name, terms in THEMES.items() if any(term in chunk.text for term in terms)]
        rows.append(
            {
                "locator": chunk.locator,
                "chars": chunk.chars,
                "themes": themes,
                "preview": text[:180],
            }
        )
    return rows
