"""Search interface over the 12 evidence cards (+ optional ledger sentences).

Other bots can import ``ConnectomeSearch`` and call ``search`` / ``as_context``.
This is lexical retrieval (token overlap), not a neural index — file/version
answers should come from here, not from model memory.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
CARD_PATH = HERE / "cards" / "evidence_cards.json"

_TOKEN = re.compile(r"[A-Za-z0-9가-힣_\.\+\-≥≤]+")


def tokenize(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN.findall(text)]


@dataclass(frozen=True)
class Hit:
    id: str
    title: str
    score: float
    text_ko: str
    text_en: str
    source: str
    version: str
    numbers: dict


class ConnectomeSearch:
    def __init__(self, card_path: Path | None = None) -> None:
        path = card_path or CARD_PATH
        self.cards = json.loads(path.read_text(encoding="utf-8"))
        if len(self.cards) != 12:
            raise ValueError(f"expected 12 evidence cards, got {len(self.cards)}")
        self._docs = []
        for c in self.cards:
            blob = " ".join(
                [
                    c["id"],
                    c["title"],
                    c.get("text_ko", ""),
                    c.get("text_en", ""),
                    c.get("source", ""),
                    c.get("version", ""),
                    " ".join(map(str, (c.get("numbers") or {}).keys())),
                ]
            )
            self._docs.append((c, tokenize(blob)))

    def search(self, query: str, k: int = 4) -> list[Hit]:
        q = tokenize(query)
        if not q:
            return []
        qset = set(q)
        scored: list[Hit] = []
        for card, toks in self._docs:
            tf = {}
            for t in toks:
                tf[t] = tf.get(t, 0) + 1
            overlap = sum(tf.get(t, 0) for t in qset)
            if overlap <= 0:
                continue
            scored.append(
                Hit(
                    id=card["id"],
                    title=card["title"],
                    score=float(overlap),
                    text_ko=card["text_ko"],
                    text_en=card["text_en"],
                    source=card["source"],
                    version=card["version"],
                    numbers=card.get("numbers") or {},
                )
            )
        scored.sort(key=lambda h: (-h.score, h.id))
        return scored[:k]

    def as_context(self, query: str, k: int = 4, lang: str = "ko") -> str:
        hits = self.search(query, k=k)
        if not hits:
            return "검색 결과 없음. 수치를 만들지 말 것."
        blocks = []
        for h in hits:
            body = h.text_ko if lang == "ko" else h.text_en
            blocks.append(f"[{h.id} | {h.version}] {h.title}\n{body}\n(source: {h.source})")
        return "\n\n".join(blocks)

    def card(self, card_id: str) -> dict | None:
        for c in self.cards:
            if c["id"] == card_id:
                return c
        return None


def search(query: str, k: int = 4) -> list[dict]:
    """Stable import surface for other bots."""
    hits = ConnectomeSearch().search(query, k=k)
    return [
        {
            "id": h.id,
            "title": h.title,
            "score": h.score,
            "text_ko": h.text_ko,
            "text_en": h.text_en,
            "source": h.source,
            "version": h.version,
            "numbers": h.numbers,
        }
        for h in hits
    ]
