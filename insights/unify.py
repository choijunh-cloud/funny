"""퀵 코멘트 증류와 HTML 해석 편을 한 편의 판단으로 합친다.

같은 말을 한 번만 남긴다. 부록의 실측은 넣지 않는다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from insights.distill import distill_path
from insights.html_essay import Block, Essay, Voice, parse_essay_path

THEMES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("rates", "금리", ("금리", "부식", "윌리엄스", "결과물", "서두르")),
    ("flow", "수급과 박스", ("외국인", "자사주", "박스", "순환", "거래대금", "종목 수", "눈치")),
    ("memory", "메모리와 마이크론", ("마이크론", "괴리", "위스퍼", "본주", "PER", "가이던스")),
    ("samsung", "삼성, 2028", ("2028", "초호황", "BNK", "유안타", "목표주가")),
    ("ai", "AI 수요와 병목", ("에이전트", "토큰", "ABF", "8단", "소버린", "앤트로픽", "핵", "기판", "솔")),
    ("power", "전력·소부장·전지", ("SOFC", "ESS", "소부장", "2차전지", "전력", "Bloom", "블룸")),
    ("tesla", "테슬라", ("FSD", "TCMV", "Roadster", "출시 기대", "테슬라")),
    ("commodity", "유가와 금", ("유가", "금 ", "150불", "WTI")),
    ("split", "어디서 갈리나", ("대립", "매트릭스", "합의")),
    ("watch", "보라는 것과 처방", ("보라는 것", "체크", "채점", "캘린더", "처방")),
)

QUICK_MAP = {
    "macro_rates": "rates",
    "market_tape": "flow",
    "memory_valuation": "memory",
    "micron_print": "memory",
    "samsung_dispersion": "samsung",
    "hbm": "ai",
    "ai_supply": "ai",
    "parts_alliance": "ai",
    "ai_demand": "ai",
    "equipment": "ai",
    "sofc": "power",
    "sdi": "power",
    "method": "flow",
    "tesla_fsd": "tesla",
    "tesla_roadster": "tesla",
}


@dataclass
class Piece:
    theme: str
    label: str
    says: list[str]
    readings: list[str]
    watches: list[str]
    quick: list[str]
    order: int


@dataclass
class Unified:
    title: str
    intro: str
    morals: list[str]
    pieces: list[Piece]
    voices: list[Voice]
    sources: list[str]
    stats: dict[str, int] = field(default_factory=dict)


def _section_theme(title: str) -> str | None:
    rules = (
        ("rates", ("금리",)),
        ("foreign_flow", ("외국인", "박스", "수급", "시황", "순환")),
        ("memory", ("메모리", "마이크론")),
        ("samsung", ("삼성", "2028", "TP")),
        ("ai", ("AI", "공급망", "수요")),
        ("power", ("2차전지", "소부장", "전력")),
        ("tesla", ("테슬라",)),
        ("commodity", ("유가", "금")),
        ("watch", ("보라는", "처방", "캘린더", "채점")),
        ("close", ("비유",)),
        ("split", ("대립", "매트릭스")),
        ("overview", ("한눈에",)),
    )
    for key, words in rules:
        if any(word in title for word in words):
            if key == "foreign_flow":
                return "flow"
            if key in {"close", "overview"}:
                return None
            return key
    return None


def _similar(left: str, right: str) -> bool:
    if not left or not right:
        return False
    if left in right or right in left:
        shorter = min(len(left), len(right))
        longer = max(len(left), len(right))
        if shorter >= 18 and shorter / longer >= 0.55:
            return True
    return SequenceMatcher(None, re.sub(r"\s+", "", left), re.sub(r"\s+", "", right)).ratio() >= 0.72


def _add(bucket: list[str], text: str, limit: int | None = None) -> None:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) < 12 or any(_similar(text, old) for old in bucket):
        return
    if limit is not None and len(bucket) >= limit:
        return
    bucket.append(text)


def _keep(lines: list[str], limit: int) -> list[str]:
    def score(text: str) -> int:
        value = 0
        for word, points in (
            ("핵심", 4),
            ("아니라", 5),
            ("아니다", 4),
            ("결과", 5),
            ("부식", 5),
            ("위스퍼", 3),
            ("괴리", 4),
            ("2028", 3),
            ("더 싸게", 6),
            ("더 오래", 3),
        ):
            if word in text:
                value += points
        if len(text) > 180:
            value -= 2
        return value

    kept: list[str] = []
    for text in sorted(lines, key=score, reverse=True):
        if any(_similar(text, old) for old in kept):
            continue
        kept.append(text)
        if len(kept) >= limit:
            break
    return kept


def unify(quick_path: str | Path, html_paths: list[str | Path]) -> Unified:
    briefing = distill_path(quick_path)
    essays = [parse_essay_path(path) for path in html_paths]
    grouped: dict[str, dict[str, list[str]]] = {
        key: {"say": [], "mean": [], "look": [], "quick": [], "lede": []}
        for key, _label, _words in THEMES
    }
    morals: list[str] = []
    voices: list[Voice] = []
    sources: list[str] = []
    for essay in essays:
        sources.append(essay.title)
        morals.extend(essay.morals)
        voices.extend(essay.voices)
        for block in essay.blocks:
            theme = _section_theme(block.section) or _line_theme(block.text)
            if theme is None or theme not in grouped:
                continue
            if block.kind == "say":
                _add(grouped[theme]["say"], block.text)
            elif block.kind == "mean":
                _add(grouped[theme]["mean"], block.text)
            elif block.kind == "look":
                _add(grouped[theme]["look"], block.text)
            elif block.kind == "lede" and any(
                word in block.text for word in ("아니라", "아니다", "핵심", "결과", "부식", "더 싸게")
            ):
                _add(grouped[theme]["say"], _first(block.text))

    for meaning in briefing.meanings:
        theme = QUICK_MAP.get(meaning.theme)
        if theme is None:
            continue
        _add(grouped[theme]["quick"], meaning.point, 2)
        if meaning.watch:
            _add(grouped[theme]["look"], meaning.watch)

    pieces: list[Piece] = []
    for index, (key, label, _words) in enumerate(THEMES):
        bag = grouped[key]
        says = _keep(bag["say"], 3)
        readings = _keep(bag["mean"], 2)
        watches = _keep(bag["look"], 2)
        quick = _keep(bag["quick"], 2)
        if not any((says, readings, watches, quick)):
            continue
        pieces.append(
            Piece(
                theme=key,
                label=label,
                says=says,
                readings=readings,
                watches=watches,
                quick=quick,
                order=index,
            )
        )

    intro = (
        "퀵 코멘트, 「서두르지 않는 브레이크」, 「부식제의 시간」을 한 편으로 읽었다. "
        "화자가 말하려는 바를 앞에 두고, 숫자는 그 말을 받치는 재료로만 두었다."
    )
    return Unified(
        title="녹슬지 않는 것, 서두르지 않는 브레이크",
        intro=intro,
        morals=morals,
        pieces=pieces,
        voices=_dedupe_voices(voices),
        sources=sources,
        stats={
            "essays": len(essays),
            "blocks": sum(len(essay.blocks) for essay in essays),
            "voices": len(voices),
            "pieces": len(pieces),
            "quick_meanings": len(briefing.meanings),
        },
    )


def _line_theme(text: str) -> str | None:
    for key, _label, words in THEMES:
        if any(word in text for word in words):
            return key
    return None


def _first(text: str) -> str:
    parts = re.split(r"(?<=다\.)\s+|(?<=요\.)\s+", text)
    return parts[0].strip() if parts else text


def _dedupe_voices(voices: list[Voice]) -> list[Voice]:
    kept: list[Voice] = []
    for voice in voices:
        if any(voice.name == old.name and _similar(voice.line, old.line) for old in kept):
            continue
        kept.append(voice)
    return kept


def piece_point(piece: Piece) -> str:
    if piece.says:
        return piece.says[0]
    if piece.watches:
        return piece.watches[0]
    if piece.quick:
        return piece.quick[0]
    if piece.readings:
        return piece.readings[0]
    return ""
