"""HTML 해석 편에서 화자의 말·의미·보라는 것만 뽑는다.

그림 속 숫자와 부록의 실측은 주장으로 올리지 않는다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


@dataclass
class Block:
    kind: str  # say, mean, look, lede, quote
    text: str
    section: str


@dataclass
class Voice:
    name: str
    role: str
    line: str
    prescription: str


@dataclass
class Essay:
    title: str
    subtitle: str
    eyebrow: str
    blocks: list[Block] = field(default_factory=list)
    voices: list[Voice] = field(default_factory=list)
    morals: list[str] = field(default_factory=list)


def _classes(attrs: list[tuple[str, str | None]]) -> set[str]:
    for key, value in attrs:
        if key == "class" and value:
            return set(value.split())
    return set()


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(말하는 바|의미|보라는 것)\s*[·—\-]\s*", "", text)
    text = re.sub(r"\s*해석\s*$", "", text)
    return text.strip(" ·—-")


class EssayParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.essay = Essay(title="", subtitle="", eyebrow="")
        self._skip = 0
        self._stack: list[tuple[str, str]] = []
        self._buf: list[str] = []
        self._section = ""
        self._skip_section = False
        self._div_depth = 0
        self._spk_depth: int | None = None
        self._card_depth: int | None = None
        self._voice_name = ""
        self._voice_line = ""
        self._voice_rx = ""
        self._ignore_data = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"svg", "style", "script"}:
            self._skip += 1
            return
        if self._skip:
            return
        if tag == "div":
            self._div_depth += 1
            classes = _classes(attrs)
            if "spk" in classes:
                self._spk_depth = self._div_depth
            if "card" in classes and self._spk_depth is not None:
                self._card_depth = self._div_depth
                self._voice_name = ""
                self._voice_line = ""
                self._voice_rx = ""
        if tag == "section":
            sid = dict(attrs).get("id") or ""
            self._skip_section = sid == "sx"
        classes = _classes(attrs)
        if tag == "span" and "snum" in classes:
            self._ignore_data += 1
        if tag == "span" and "sub" in classes and self._stack and self._stack[-1][1] == "h3":
            self._buf.append(" · ")
        kind = _open_kind(tag, classes, self._stack, self._card_depth is not None)
        if kind:
            self._stack.append((tag, kind))
            if len(self._stack) == 1:
                self._buf = []

    def handle_endtag(self, tag: str) -> None:
        if tag in {"svg", "style", "script"} and self._skip:
            self._skip -= 1
            return
        if self._skip:
            return
        if self._stack and self._stack[-1][0] == tag:
            _open, kind = self._stack.pop()
            text = _clean("".join(self._buf)) if not self._stack else ""
            if not self._stack:
                self._take(kind, text)
                self._buf = []
        if tag == "div":
            if self._card_depth == self._div_depth:
                self._flush_voice()
                self._card_depth = None
            if self._spk_depth == self._div_depth:
                self._spk_depth = None
            self._div_depth = max(0, self._div_depth - 1)
        if tag == "span" and self._ignore_data:
            self._ignore_data -= 1
        if tag == "section":
            self._skip_section = False

    def handle_data(self, data: str) -> None:
        if self._skip or self._ignore_data or not self._stack:
            return
        if self._skip_section and self._stack[-1][1] != "h2":
            return
        self._buf.append(data)

    def _take(self, kind: str, text: str) -> None:
        if not text:
            return
        if kind == "h1":
            self.essay.title = text
            return
        if kind == "eyebrow":
            self.essay.eyebrow = text
            return
        if kind == "sub" and not self.essay.subtitle:
            self.essay.subtitle = text
            return
        if kind == "h2":
            self._section = re.sub(r"^\d+\s*", "", text).lstrip()
            self._skip_section = _skip_heading(self._section)
            return
        if kind == "h3" and self._card_depth is not None:
            self._voice_name = text
            return
        if kind == "pline" and self._card_depth is not None:
            self._voice_line = text
            return
        if kind == "cap" and self._card_depth is not None and "처방" in text:
            self._voice_rx = re.sub(r"^처방\s*[·—\-]\s*", "", text)
            return
        if self._skip_section:
            return
        if kind == "moral":
            self.essay.morals.append(text)
            return
        if kind in {"say", "mean", "look", "lede", "quote"} and self._section:
            self.essay.blocks.append(Block(kind=kind, text=text, section=self._section))

    def _flush_voice(self) -> None:
        if not self._voice_name or not self._voice_line:
            return
        self.essay.voices.append(
            Voice(
                name=self._voice_name.strip(),
                role="",
                line=self._voice_line.strip(),
                prescription=self._voice_rx.strip(),
            )
        )
        self._voice_name = ""
        self._voice_line = ""
        self._voice_rx = ""


def _open_kind(tag: str, classes: set[str], stack: list[tuple[str, str]], in_card: bool) -> str | None:
    if tag == "h1":
        return "h1"
    if tag == "h2":
        return "h2"
    if tag == "h3" and in_card:
        return "h3"
    if tag == "p" and in_card and "q" not in classes and not stack:
        return "pline"
    if any(item[1] == "h3" for item in stack):
        return None
    for name in ("moral", "lede", "say", "mean", "look", "quote", "eyebrow", "sub", "q", "cap"):
        if name in classes:
            if name == "q" and in_card:
                return "pline"
            if name == "cap":
                return "cap"
            return name
    return None


def _skip_heading(title: str) -> bool:
    return any(word in title for word in ("부록", "실측", "전사"))


def parse_essay(html: str) -> Essay:
    parser = EssayParser()
    parser.feed(html)
    parser.close()
    return parser.essay


def parse_essay_path(path: str | Path) -> Essay:
    return parse_essay(Path(path).read_text(encoding="utf-8"))
