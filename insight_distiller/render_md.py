"""Markdown rendering of a distilled report."""

from __future__ import annotations

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
            f"퀵코멘트 {stats['quick_raw']}개 중 중복 {stats['quick_dropped']}개를 빼고 "
            f"{stats['quick_kept']}개를 남겼다. 녹취 블록 {stats['transcript_blocks']}개, "
            f"챕터 {stats['chapters']}개. 파일은 최신 코멘트가 위이며, 같은 문장의 수정본은 위쪽을 채택한다. "
            "숫자는 원문 표기다."
        ),
        "",
    ]
    if report.sources:
        parts.append("원문에 등장한 출처 표기: " + ", ".join(report.sources) + ".")
        parts.append("")
    if report.chapters:
        parts.append("## 녹취 챕터")
        parts.append("")
        for chapter in report.chapters:
            parts.append(f"- {chapter}")
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

    if report.deep:
        parts.append("## 2차 분석 · 녹취에서 보강한 내용")
        parts.append("")
        parts.append(
            f"퀵코멘트 표에 없던 녹취·맥락 {report.stats.get('deep_items', 0)}개다. "
            "문장은 원문 앵커가 있을 때만 남긴다."
        )
        parts.append("")
        for section in report.deep:
            parts.append(f"### {section.title}")
            parts.append("")
            for item in section.items:
                parts.append(f"- {item}")
            parts.append("")

    if report.checklist:
        parts.append("## 확인할 조건")
        parts.append("")
        for item in report.checklist:
            parts.append(f"- {item}")
        parts.append("")

    if report.watchlist:
        parts.append("## 녹취 언급 빈도")
        parts.append("")
        parts.append("방송 녹취에서 반복된 이름이다. 언급 횟수이며 매수 순위가 아니다.")
        parts.append("")
        parts.append("| 이름 | 언급 |")
        parts.append("|---|---|")
        for name, count in report.watchlist:
            parts.append(f"| {name} | {count} |")
        parts.append("")

    parts.append("---")
    parts.append("")
    parts.append("원문 코멘트를 코드로 추출·증류한 결과이며, 매수·매도 권유가 아니다.")
    parts.append("")
    return "\n".join(parts)
