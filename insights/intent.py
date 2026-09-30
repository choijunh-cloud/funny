"""문장을 주장·행동·근거로 가른다.

숫자 밀도는 감점이다. 화자가 결론을 말하는 문장이 위로 올라온다.
연도와 분기는 시세가 아니라 시점이라 밀도에서 뺀다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from insights.parse import Comment
from insights.themes import THEMES, Theme

YEAR_OR_QUARTER = re.compile(r"20\d{2}|[1-4]Q")
DISCLAIMER_MARKERS = (
    "매수와 매도의 추천이 아닙니다",
    "투자에 따른 판단은 각자의 몫",
    "법적 자료로 활용할 수 없습니다",
)
LOGISTICS_MARKERS = (
    "SKIP",
    "라이브로 설명",
    "관심있는 분만",
    "자세한 풀이",
    "워드파일",
    "매일 업데이트",
    "이 다음은",
    "좀더 설명부분",
    "다음은 좀더",
)
AGENDA_MARKERS = ("youtube.com", "http://", "https://", "라이브 링크")
SECTION_HEADERS = {
    "결론": "core",
    "헤드라인": "core",
    "핵심 메시지": "core",
    "핵심 포인트": "core",
    "핵심 포인트 4가지": "core",
    "마무리 코멘트": "close",
    "마감 생각": "close",
    "시장 해석": "core",
    "긍정적 요인": "factor",
    "부정적 요인": "factor",
    "관심 종목": "basket",
    "주요 이슈": "factor",
    "시장 이슈": "factor",
}
CLAIM_MARKERS = (
    ("핵심은", 8),
    ("핵심", 4),
    ("결국", 5),
    ("아니라", 5),
    ("아니다", 4),
    ("보다는", 5),
    ("부정적이지 않다", 7),
    ("결과물", 4),
    ("동감", 4),
    ("동의", 3),
    ("타당", 3),
    ("관건", 3),
    ("눈높이", 3),
    ("봅니다", 2),
    ("봐야", 2),
    ("변수", 2),
    ("직결", 3),
    ("포인트", 2),
    ("무게", 2),
    ("신뢰", 2),
    ("방향", 2),
    ("유효", 2),
    ("주목", 2),
    ("유리", 3),
    ("지속", 2),
    ("서두를 필요", 5),
    ("이번 발표", 6),
    ("더 싸게", 5),
    ("반론", 5),
)
JUDGMENT = (
    "핵심",
    "관건",
    "방향",
    "신뢰",
    "눈높이",
    "쉬어",
    "타당",
    "동감",
    "동의",
    "아니라",
    "아니다",
    "봐야",
    "봅니다",
    "무게",
    "직결",
    "포인트",
    "유보",
    "결과",
)
WATCH_MARKERS = ("변수", "체크", "관건", "봐야", "주목", "눈높이", "전까지", "확인")
CONTRAST_PATTERNS = (
    re.compile(
        r"[\"“'](?P<neg>[^\"”']{2,40})[\"”']\s*가\s*아니라\s*[\"“'](?P<pos>[^\"”']{2,80})"
    ),
    re.compile(r"(?P<neg>.{4,24})보다는\s*(?P<pos>.{4,60}?)(?:[\.?!]|$)"),
    re.compile(r"(?P<neg>.{4,36})가\s*아니다\s*[→\-–>]+\s*(?P<pos>.{4,42})"),
    re.compile(r"[\"“'](?P<neg>[^\"”']{2,48})[\"”']\s*(?:이|가)\s*아니다"),
)


@dataclass(frozen=True)
class Contrast:
    neg: str
    pos: str


@dataclass
class Line:
    text: str
    kind: str  # claim, action, evidence, factor, basket, noise
    score: int
    section: str
    time: str
    feed_index: int
    watch: bool = False


def factiness(text: str) -> float:
    """숫자 나열에 가까운 정도. 연도·분기는 빼 시점 표현을 벌하지 않는다."""
    stripped = YEAR_OR_QUARTER.sub("", text)
    stripped = re.sub(r"\s+", "", stripped)
    if not stripped:
        return 0.0
    digits = sum(character.isdigit() for character in stripped)
    return digits / len(stripped)


def clean_line(text: str) -> str:
    line = text.strip()
    line = re.sub(r"^[→⇒>\-]+\s*", "", line)
    line = re.sub(r"^[\-\*•●▪▸►]\s*", "", line)
    line = re.sub(r"^[①②③④⑤⑥⑦⑧⑨⑩]\s*", "", line)
    line = re.sub(r"^\d+[\.\)]\s*", "", line)
    line = line.replace("**", "")
    line = line.replace("_", "")
    line = re.sub(r"\s+", " ", line)
    return line.strip()


def _is_logistics(body: str) -> bool:
    compact = body.strip()
    if len(compact) > 180 and "http" not in compact:
        return False
    return any(marker in compact for marker in LOGISTICS_MARKERS)


def _is_agenda(body: str) -> bool:
    compact = body.strip()
    if "http" in compact or "youtube" in compact:
        return True
    return any(marker in compact for marker in AGENDA_MARKERS) and len(compact) < 220


def _is_verdict(body: str) -> bool:
    """본문 전체가 한 줄 평결일 때만. 긴 논지는 그 자체로 코멘트다."""
    compact = re.sub(r"\s+", " ", body.strip())
    if "\n" in body.strip():
        return False
    if len(compact) > 42 or len(compact) < 8:
        return False
    if _is_logistics(compact) or _is_agenda(compact):
        return False
    if factiness(compact) >= 0.08:
        return False
    return True


def _strip_disclaimer(body: str) -> str:
    cut = len(body)
    for marker in DISCLAIMER_MARKERS:
        found = body.find(marker)
        if found != -1:
            cut = min(cut, found)
    return body[:cut].strip()


def _header_section(raw: str, section: str) -> tuple[str, bool]:
    stripped = raw.strip()
    bracket = re.match(r"^[<\[]\s*(.+?)\s*[>\]]$", stripped)
    label_source = bracket.group(1).strip() if bracket else stripped
    label = re.sub(r"^[^\w가-힣A-Za-z]+", "", label_source).strip(" :")
    label = label.split(":")[0].strip()
    if label.startswith("장 시작 전") and len(stripped) < 24:
        return "open", True
    if label in SECTION_HEADERS and len(stripped) < 28:
        return SECTION_HEADERS[label], True
    if label in SECTION_HEADERS:
        return SECTION_HEADERS[label], False
    if "헤드라인" in stripped[:16]:
        return "core", False
    return section, False


def score_text(text: str, section: str = "") -> int:
    score = 0
    for marker, points in CLAIM_MARKERS:
        if marker in text:
            score += points
    if section == "core":
        score += 2
    if section == "close":
        score += 3
    if section == "open":
        score += 1
    density = factiness(text)
    if density >= 0.14:
        score -= 6
    elif density >= 0.08:
        score -= 2
    if len(text) < 16:
        score -= 2
    elif 24 <= len(text) <= 140:
        score += 2
    elif len(text) > 180:
        score -= 5
    if "우려" in text and "반론" not in text:
        score -= 4
    return score


def classify_line(text: str, section: str) -> str:
    if not text or len(text) < 8:
        return "noise"
    if section == "basket":
        return "basket"
    if text.startswith("<") or re.fullmatch(r"[<\[][^>\]]+[>\]]", text):
        return "noise"
    density = factiness(text)
    contrast = any(pattern.search(text) for pattern in CONTRAST_PATTERNS)
    claim_score = score_text(text, section)
    if density >= 0.14 and not contrast and "핵심" not in text:
        return "evidence"
    if section == "factor" and density < 0.12 and claim_score < 6:
        return "factor"
    if any(marker in text for marker in WATCH_MARKERS) and "핵심은" not in text and claim_score < 8:
        return "action"
    if claim_score >= 3 or contrast or section in {"core", "close"}:
        return "claim"
    if density >= 0.07:
        return "evidence"
    if len(text) >= 36:
        return "claim"
    return "noise"


def extract_contrasts(text: str) -> list[Contrast]:
    found: list[Contrast] = []
    for pattern in CONTRAST_PATTERNS:
        for match in pattern.finditer(text):
            neg = _tidy_clause(match.group("neg") if "neg" in match.groupdict() else "")
            pos = ""
            if "pos" in match.groupdict() and match.group("pos"):
                pos = _tidy_clause(match.group("pos"))
            else:
                rest = text[match.end() :]
                arrow = re.search(r"[→>\-–]+\s*(.{4,60})", rest)
                if arrow:
                    pos = _tidy_clause(arrow.group(1))
            if neg:
                found.append(Contrast(neg=neg, pos=pos))
    return found


def _tidy_clause(text: str) -> str:
    clause = text.strip(" \"'“”‘’.,·")
    clause = re.sub(r"\s+", " ", clause)
    clause = re.sub(r"\s*(이\s*)?핵심$", "", clause).strip()
    clause = re.sub(r"이라기$", "", clause).strip()
    clause = re.sub(r"^(그런데|다만|특히|즉|따라서)\s*", "", clause)
    return clause.strip()


def theme_score(text: str, theme: Theme) -> int:
    return sum(1 for key in theme.keys if key in text)


def best_theme(text: str) -> str | None:
    ranked = sorted(
        ((theme_score(text, theme), theme.weight, theme.key) for theme in THEMES),
        reverse=True,
    )
    score, _weight, key = ranked[0]
    if score <= 0:
        return None
    return key


def explode_sentences(raw: str) -> list[str]:
    """마침표 뒤 새 문장만 자른다. 5.27처럼 숫자 안의 점은 건드리지 않는다."""
    parts = re.split(r"(?<=[\.!?])\s+(?=[가-힣A-Za-z0-9“\"‘\(])", raw.strip())
    sentences: list[str] = []
    for part in parts:
        sentences.extend(re.split(r"\s+[—–]\s+", part))
    return [sentence.strip() for sentence in sentences if sentence.strip()]


def _emit(sentence: str, section: str, lines: list[Line], comment: Comment) -> None:
    text = clean_line(sentence)
    if len(text) < 8:
        return
    kind = classify_line(text, section)
    if comment.theme == "method" and len(text) >= 8:
        kind = "claim"
    if kind == "noise":
        return
    lines.append(
        Line(
            text=text,
            kind=kind,
            score=score_text(text, section),
            section=section,
            time=comment.time,
            feed_index=comment.feed_index,
            watch=any(marker in text for marker in WATCH_MARKERS),
        )
    )


def split_lines(comment: Comment) -> list[Line]:
    """줄바꿈으로 끊긴 문장은 잇고, 마침표 뒤에서만 문장을 나눈다."""
    section = ""
    lines: list[Line] = []
    pending: list[str] = []
    body = _strip_disclaimer(comment.body)

    def flush() -> None:
        if not pending:
            return
        paragraph = " ".join(pending)
        pending.clear()
        for sentence in explode_sentences(paragraph):
            _emit(sentence, section, lines, comment)

    for raw_line in body.splitlines():
        raw = raw_line.strip()
        if not raw:
            flush()
            continue
        if len(raw) < 8 and not pending:
            continue
        new_section, is_header = _header_section(raw, section)
        if is_header:
            flush()
            section = new_section
            continue
        section = new_section
        if re.match(r"^(?:[\-\*•●]|[①②③④⑤⑥⑦⑧⑨⑩]|\d+[\.\)])\s*", raw):
            flush()
            for sentence in explode_sentences(raw):
                _emit(sentence, section, lines, comment)
            continue
        pending.append(raw)
        if re.search(r"[\.!?]\s*$", raw):
            flush()
    flush()
    return lines


def tag_comments(comments: list[Comment]) -> None:
    """물류·한줄 평결·테마를 코멘트에 붙인다. 평결은 바로 아래 본문에 연결한다."""
    for comment in comments:
        if _is_agenda(comment.body):
            comment.kind = "agenda"
        elif _is_logistics(comment.body):
            comment.kind = "logistics"
        elif _is_verdict(comment.body):
            comment.kind = "verdict"
        else:
            comment.kind = "note"
            comment.theme = best_theme(comment.body)

    for index, comment in enumerate(comments):
        if comment.kind != "verdict":
            continue
        verdict = clean_line(comment.body.replace("\n", " "))
        previous = _previous_note(comments, index)
        target = _next_note(comments, index)
        want = best_theme(verdict)
        chosen: list[Comment] = []
        if previous and want and previous.theme == want:
            chosen.append(previous)
        elif target and (want is None or target.theme == want):
            chosen.append(target)
            if previous and previous.theme and previous.theme == target.theme:
                chosen.append(previous)
        elif previous and want is None:
            chosen.append(previous)
        for host in chosen:
            if verdict not in host.verdicts:
                host.verdicts.append(verdict)


def _next_note(comments: list[Comment], index: int) -> Comment | None:
    for comment in comments[index + 1 :]:
        if comment.kind == "note":
            return comment
    return None


def _previous_note(comments: list[Comment], index: int) -> Comment | None:
    for comment in reversed(comments[:index]):
        if comment.kind == "note":
            return comment
    return None


def has_judgment(text: str) -> bool:
    return any(marker in text for marker in JUDGMENT)
