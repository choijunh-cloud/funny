"""파이프라인이 주고받는 자료 구조."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Chunk:
    source: str
    kind: str
    locator: str
    text: str
    quality: float

    @property
    def chars(self) -> int:
        return len(self.text)


@dataclass
class Fact:
    key: str
    display: str
    snippet: str
    source: str
    locator: str
    quality: float
    kind: str
    support: int = 1
    mentions: int = 1


@dataclass
class Knowledge:
    documents: list[dict]
    chunks: list[Chunk]
    facts: list[Fact]
    themes: list[dict]
    associations: list[dict]
    equipment: dict
    comments: list[dict] = field(default_factory=list)

    def get(self, key: str) -> Fact | None:
        hits = [fact for fact in self.facts if fact.key == key]
        if not hits:
            return None
        hits.sort(key=lambda fact: (fact.support, fact.mentions, fact.quality), reverse=True)
        return hits[0]

    def has(self, key: str) -> bool:
        return self.get(key) is not None

    def display(self, key: str, default: str = "") -> str:
        fact = self.get(key)
        return fact.display if fact else default

    def rows(self, key: str) -> list[Fact]:
        return [fact for fact in self.facts if fact.key == key]
