"""Markdown rendering of a distilled report."""

from __future__ import annotations

from insight_distiller.brief import core_brief, valuation_line
from insight_distiller.distill import Report


def _tag(bullet) -> str:
    if bullet.time:
        return bullet.time
    if bullet.source == "transcript":
        return "녹취"
    if bullet.source == "extract":
        return "추출"
    return "코멘트"


def _table(rows: list[dict]) -> str:
    if not rows:
        return ""
    lines = [
        "| 종목 | 가격 | 앞 구간 | 뒤 구간 |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {name} | {price} | {y26} | {y27} |".format(
                name=row.get("name", ""),
                price=row.get("price", ""),
                y26=row.get("y26", "") or "—",
                y27=row.get("y27", "") or "—",
            )
        )
    return "\n".join(lines)


def render_markdown(report: Report) -> str:
    stats = report.stats
    parts = [
        "# 투자 인사이트 증류",
        "",
        report.headline or "원문에서 한 줄 프레임을 찾지 못했다.",
        "",
        (
            f"퀵코멘트 {stats['quick_kept']}개와 방송 대담 {len(report.dialogs)}편을 한 노트로 합쳤다. "
            f"같은 논지는 한 번만 남기고 출처를 붙였다. 문장 {stats.get('unified_bullets', 0)}개. "
            "숫자는 원문 표기다."
        ),
        "",
    ]
    if report.sources:
        parts.append("원문에 등장한 출처 표기: " + ", ".join(report.sources) + ".")
        parts.append("")

    brief = core_brief(report)
    if brief:
        parts.append("## 핵심")
        parts.append("")
        parts.append("아래 문장은 증류 노트에 이미 있는 문장만 다시 골랐다.")
        parts.append("")
        value = valuation_line(report)
        if value:
            parts.append(value)
            parts.append("")
        for title, bullets in brief:
            parts.append(f"### {title}")
            parts.append("")
            for bullet in bullets:
                who = bullet.time or _tag(bullet)
                parts.append(f"- {who} · {bullet.text}")
            parts.append("")

    for section in report.sections:
        parts.append(f"## {section.title}")
        parts.append("")
        if section.lead:
            parts.append(section.lead)
            parts.append("")
        table = _table(section.table)
        if table:
            parts.append(table)
            parts.append("")
        for bullet in section.bullets:
            parts.append(f"- {_tag(bullet)} · {bullet.text}")
        parts.append("")

    if report.checklist:
        parts.append("## 확인할 조건")
        parts.append("")
        for item in report.checklist:
            parts.append(f"- {item}")
        parts.append("")

    parts.append("---")
    parts.append("")
    parts.append("원문 코멘트를 코드로 추출·증류한 결과이며, 매수·매도 권유가 아니다.")
    parts.append("")
    return "\n".join(parts)
