"""Split a mixed quick-comment / transcript paste into ordered blocks."""

from __future__ import annotations

import re
from dataclasses import dataclass

CLOCK = re.compile(r"\d{1,2}:\d{2}")
TRANSCRIPT_TS = re.compile(r"^(?:\d+분(?: \d+초)?|\d+초)$")
CHAPTER = re.compile(r"^챕터\s*\d+")


@dataclass
class Block:
    kind: str  # quick | transcript | chapter
    time: str | None
    text: str
    order: int

    def prep(self) -> str:
        return (
            self.text.replace("**", "")
            .replace("\u00a0", " ")
            .replace("\u200b", "")
            .replace("\r", "")
        )


def _lines(text: str) -> list[str]:
    return text.replace("\r\n", "\n").replace("\r", "\n").split("\n")


def parse(text: str) -> list[Block]:
    lines = _lines(text)
    n = len(lines)
    quick_at = [i for i, line in enumerate(lines) if line.strip().startswith("Quick 코멘트")]
    ranges: list[tuple[int, int, str | None, int]] = []
    covered: set[int] = set()

    for idx, q in enumerate(quick_at):
        clock_at = None
        j = q - 1
        while j >= 0 and not lines[j].strip():
            j -= 1
        if j >= 0 and CLOCK.fullmatch(lines[j].strip()):
            clock_at = j
        start = clock_at if clock_at is not None else q

        end = n
        for k in range(q + 1, n):
            stripped = lines[k].strip()
            if stripped.startswith("Quick 코멘트"):
                end = k
                p = k - 1
                while p > q and not lines[p].strip():
                    p -= 1
                if p > q and CLOCK.fullmatch(lines[p].strip()):
                    end = p
                break
            if TRANSCRIPT_TS.fullmatch(stripped) or CHAPTER.match(stripped):
                end = k
                break
        ranges.append((start, end, lines[clock_at].strip() if clock_at is not None else None, q))

    blocks: list[Block] = []
    for start, end, stamp, q in ranges:
        for k in range(start, end):
            covered.add(k)
        body = "\n".join(lines[q + 1 : end]).strip()
        blocks.append(Block("quick", stamp, body, start))

    idx = 0
    while idx < n:
        if idx in covered or not lines[idx].strip():
            idx += 1
            continue
        stripped = lines[idx].strip()
        if CHAPTER.match(stripped):
            blocks.append(Block("chapter", None, stripped, idx))
            idx += 1
            continue
        start = idx
        buf: list[str] = []
        while idx < n and idx not in covered:
            stripped = lines[idx].strip()
            if CHAPTER.match(stripped):
                text_block = "\n".join(buf).strip()
                if len(text_block) >= 40:
                    blocks.append(Block("transcript", None, text_block, start))
                blocks.append(Block("chapter", None, stripped, idx))
                buf = []
                start = idx + 1
                idx += 1
                continue
            if stripped:
                buf.append(lines[idx])
            idx += 1
        text_block = "\n".join(buf).strip()
        if len(text_block) >= 40:
            blocks.append(Block("transcript", None, text_block, start))

    blocks.sort(key=lambda b: b.order)
    return blocks


def normalize(text: str) -> str:
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"[“”\"'‘’·]", "", text)
    return text.lower()


def near_duplicate(a: str, b: str, threshold: float = 0.92) -> bool:
    from difflib import SequenceMatcher

    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return False
    if na == nb:
        return True
    shorter, longer = (na, nb) if len(na) <= len(nb) else (nb, na)
    if shorter in longer and len(shorter) / len(longer) > 0.86:
        return True
    if abs(len(na) - len(nb)) / max(len(na), len(nb)) > 0.28:
        return False
    return SequenceMatcher(None, na[:900], nb[:900]).ratio() >= threshold


def dedupe_quick(blocks: list[Block]) -> tuple[list[Block], int]:
    """Keep the earlier block (file order = later comment) when two overlap."""
    kept: list[Block] = []
    dropped = 0
    for block in blocks:
        if block.kind != "quick" or len(block.prep()) < 8:
            continue
        match = next((k for k in kept if near_duplicate(k.prep(), block.prep())), None)
        if match is None:
            kept.append(block)
            continue
        dropped += 1
        if len(block.prep()) > len(match.prep()) * 1.25:
            kept[kept.index(match)] = block
    return kept, dropped
