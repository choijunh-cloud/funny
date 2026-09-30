"""타임스탬프 + Quick 코멘트 묶음을 메시지 단위로 자른다."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


HEADER = re.compile(
    r"(?m)^(?P<prefix>.*?)(?P<time>\d{1,2}:\d{2})[ \t]*\nQuick 코멘트[ \t]*\n"
)


@dataclass
class Comment:
    time: str
    body: str
    feed_index: int
    kind: str = "note"  # note, verdict, logistics, agenda
    theme: str | None = None
    verdicts: list[str] = field(default_factory=list)


def _pad_time(value: str) -> str:
    hour, minute = value.split(":")
    return f"{int(hour):02d}:{minute}"


def parse_comments(text: str) -> list[Comment]:
    """헤더 시각이 앞 문장 끝에 붙어 있어도 메시지를 나눈다.

    붙임 예: ``...높습니다. 07:47\\nQuick 코멘트``
    시각 앞의 문장은 이전 코멘트의 끝이다.
    """
    raw = text.replace("\r\n", "\n").strip()
    if not raw:
        return []
    raw = raw + "\n"
    matches = list(HEADER.finditer(raw))
    comments: list[Comment] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(raw)
        body = raw[match.end() : end].strip()
        if index + 1 < len(matches):
            prefix = matches[index + 1].group("prefix").strip()
            if prefix:
                body = f"{body}\n{prefix}".strip()
        comments.append(
            Comment(time=_pad_time(match.group("time")), body=body, feed_index=index)
        )
    return comments
