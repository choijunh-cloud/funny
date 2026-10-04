"""Pick one core line per fact from the already distilled note.

A line is kept only when its anchor is found in a bullet. Nothing is written
that the distillation did not already extract from the source.
"""

from __future__ import annotations

from insight_distiller.distill import Bullet, Report

# Order is the reading order. Each anchor must be specific enough to hit one claim.
GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "판단",
        (
            "다시는 내려오지",
            "내년 1분기 3.1%",
            "ISM 제조업",
            "고물가 국면",
            "디젤",
        ),
    ),
    (
        "메모리",
        (
            "110조",
            "120%",
            "세 배",
            "약 3%밖에",
            "101조~108조",
            "필수 투입재",
        ),
    ),
    (
        "수급",
        (
            "신흥국부터",
            "175만",
            "7,200",
            "10월 15일",
        ),
    ),
    (
        "다음 돈",
        (
            "현금이 가는",
            "20~30%",
            "200만 원 초중반",
            "시장 약 27조",
            "한국 원전",
            "약 4배",
        ),
    ),
    (
        "자금과 사이클",
        (
            "4,500억 달러",
            "40GW",
            "450만 개",
            "희토류",
        ),
    ),
)


def _bullets(report: Report) -> list[Bullet]:
    return [bullet for section in report.sections for bullet in section.bullets]


def _find(bullets: list[Bullet], anchor: str) -> Bullet | None:
    hits = [bullet for bullet in bullets if anchor in bullet.text]
    if not hits:
        return None
    hits.sort(key=lambda bullet: (anchor in (bullet.time or ""), len(bullet.text)))
    return hits[0]


def core_brief(report: Report) -> list[tuple[str, list[Bullet]]]:
    """Return (group, bullets) for anchors that the note actually contains."""
    pool = _bullets(report)
    seen: set[str] = set()
    grouped: list[tuple[str, list[Bullet]]] = []
    for title, anchors in GROUPS:
        chosen: list[Bullet] = []
        for anchor in anchors:
            bullet = _find(pool, anchor)
            if bullet is None or bullet.text in seen:
                continue
            seen.add(bullet.text)
            chosen.append(bullet)
        if chosen:
            grouped.append((title, chosen))
    return grouped


def missing_anchors(report: Report) -> list[str]:
    pool = _bullets(report)
    missing: list[str] = []
    for _, anchors in GROUPS:
        for anchor in anchors:
            if _find(pool, anchor) is None:
                missing.append(anchor)
    return missing


def valuation_line(report: Report) -> str:
    for section in report.sections:
        if section.key != "memory" or not section.table:
            continue
        bits = []
        for row in section.table:
            name = row.get("name", "")
            price = row.get("price", "")
            later = row.get("y27", "")
            if name and price and later:
                bits.append(f"{name} {price} · {later}")
        if bits:
            return "현재 가격 기준 " + " / ".join(bits)
    return ""
