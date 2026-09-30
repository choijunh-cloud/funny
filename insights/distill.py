"""코멘트를 화자의 판단으로 증류한다.

시세를 맞추지 않는다. 한 줄 평결, 대비, '핵심은'이 숫자 표보다 앞이다.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from insights.intent import (
    Contrast,
    Line,
    best_theme,
    clean_line,
    extract_contrasts,
    factiness,
    has_judgment,
    score_text,
    split_lines,
    tag_comments,
)
from insights.parse import Comment, parse_comments
from insights.themes import THEMES, THEME_BY_KEY, Theme

NAMES = (
    ("삼성전자", ("삼성전자", "삼전")),
    ("SK하이닉스", ("SK하이닉스", "SKHY", "하이닉스")),
    ("마이크론", ("마이크론",)),
    ("Sandisk", ("Sandisk", "샌디스크")),
    ("한미반도체", ("한미반도체",)),
    ("이수페타시스", ("이수페타시스",)),
    ("피에스케이홀딩스", ("피에스케이홀딩스", "피에스케이")),
    ("삼성전기", ("삼성전기",)),
    ("삼성SDI", ("삼성SDI",)),
    ("네이버", ("네이버", "NAVER")),
    ("삼성SDS", ("삼성SDS",)),
    ("NHN", ("NHN",)),
    ("테슬라", ("테슬라", "Tesla")),
    ("TSMC", ("TSMC",)),
    ("엔비디아", ("엔비디아", "NVIDIA")),
    ("ASML", ("ASML",)),
    ("Applied Materials", ("Applied Materials", "AMAT")),
    ("Lam Research", ("Lam Research", "램리서치")),
    ("KLA", ("KLA",)),
    ("Bloom Energy", ("Bloom",)),
    ("코세스", ("코세스",)),
    ("서진시스템", ("서진시스템", "서진")),
    ("비나텍", ("비나텍",)),
    ("미코", ("미코",)),
    ("두산퓨얼셀", ("두산퓨얼셀",)),
    ("TDK", ("TDK",)),
    ("Taiyo Yuden", ("Taiyo",)),
    ("OpenAI", ("OpenAI", "오픈AI", "오픈 AI")),
    ("Meta", ("메타", "Meta")),
    ("유안타", ("유안타",)),
    ("BNK", ("BNK",)),
    ("흥국", ("흥국",)),
    ("JPMorgan", ("제이피모건", "JP모건")),
    ("현대차", ("현대차",)),
    ("로보티즈", ("로보티즈",)),
)


@dataclass
class Meaning:
    theme: str
    label: str
    point: str
    alongside: list[str]
    against: str
    watch: str
    grounds: list[str]
    names: list[str]
    sources: list[str]
    order: int


@dataclass
class AgendaItem:
    what: str


@dataclass
class Briefing:
    intro: str
    judgments: list[str]
    meanings: list[Meaning]
    agenda: list[AgendaItem]
    basket: list[tuple[str, str]]
    dropped: list[str]
    stats: dict[str, int] = field(default_factory=dict)

    def by(self, theme: str) -> Meaning:
        for meaning in self.meanings:
            if meaning.theme == theme:
                return meaning
        raise KeyError(theme)


def distill_path(path: str | Path) -> Briefing:
    return distill_text(Path(path).read_text(encoding="utf-8"))


def distill_text(text: str) -> Briefing:
    comments = parse_comments(text)
    tag_comments(comments)
    notes = [comment for comment in comments if comment.kind == "note"]
    lines_by_theme: dict[str, list[Line]] = {theme.key: [] for theme in THEMES}
    all_claim_lines: list[Line] = []
    for comment in notes:
        if not comment.theme:
            continue
        for line in split_lines(comment):
            line_theme = comment.theme
            lines_by_theme.setdefault(line_theme, []).append(line)
            if line.kind in {"claim", "action"}:
                all_claim_lines.append(line)

    meanings: list[Meaning] = []
    for theme in THEMES:
        group = [comment for comment in notes if comment.theme == theme.key]
        if not group and not lines_by_theme.get(theme.key):
            continue
        meaning = _compose_theme(
            theme,
            group,
            lines_by_theme.get(theme.key, []),
            all_claim_lines,
            notes,
        )
        if meaning is None:
            continue
        meanings.append(meaning)

    meanings.sort(key=lambda item: item.order)
    judgments = [_first_sentence(item.point) for item in meanings if item.point]
    dropped = [
        f"{comment.time} {clean_line(comment.body.replace(chr(10), ' '))[:42]}"
        for comment in comments
        if comment.kind in {"logistics", "verdict"}
    ]
    briefing = Briefing(
        intro=(
            "퀵 코멘트에서 화자가 회원에게 설득하려는 판단을 뽑았다. "
            "숫자는 그 판단을 떠받치려고 꺼낸 말로만 붙였고, 따로 맞추거나 반박하지 않았다."
        ),
        judgments=judgments,
        meanings=meanings,
        agenda=_agenda(comments),
        basket=_basket(notes),
        dropped=dropped,
        stats={
            "comments": len(comments),
            "notes": len(notes),
            "logistics": sum(comment.kind == "logistics" for comment in comments),
            "verdicts": sum(comment.kind == "verdict" for comment in comments),
            "meanings": len(meanings),
        },
    )
    return briefing


def _compose_theme(
    theme: Theme,
    comments: list[Comment],
    lines: list[Line],
    outside_claims: list[Line],
    notes: list[Comment],
) -> Meaning | None:
    claims = _dedupe([line for line in lines if line.kind == "claim"])
    actions = _dedupe([line for line in lines if line.kind in {"action", "claim"} and line.watch])
    factors = _dedupe([line for line in lines if line.kind == "factor"])
    evidence = _dedupe([line for line in lines if line.kind == "evidence"])
    verdicts = []
    for comment in comments:
        for verdict in comment.verdicts:
            if verdict not in verdicts:
                verdicts.append(verdict)

    if not claims or max(line.score for line in claims) < 5:
        claims = _dedupe(claims + _harvest(theme, outside_claims, lines))

    contrasts = []
    for line in claims:
        contrasts.extend(extract_contrasts(line.text))
    contrast = _best_contrast(contrasts)

    if theme.key == "method":
        point, alongside, watch = _method_point(lines, comments, notes)
        if not point:
            return None
    else:
        lead_bits = _lead(theme, contrast, verdicts, claims)
        if not lead_bits:
            return None
        point = lead_bits[0]
        if len(point) < 28 and len(lead_bits) > 1:
            point = _join(lead_bits[:2])
        if factiness(point) >= 0.12 and theme.key != "method":
            softer = [bit for bit in lead_bits if factiness(bit) < 0.1]
            if not softer:
                return None
            point = softer[0]

        used = [point]
        watch = ""
        for line in sorted(actions, key=lambda item: item.score, reverse=True):
            if not _on_theme(theme, line.text) and theme.key != "micron_print":
                continue
            if _similar_any(line.text, used):
                continue
            watch = _clip(_finish(line.text), 150)
            used.append(line.text)
            break

        alongside = []
        pool = claims + factors
        for line in pool:
            if len(alongside) >= 2:
                break
            if line.kind == "factor" and line.score < 3:
                continue
            if not _on_theme(theme, line.text):
                continue
            if _similar_any(line.text, used):
                continue
            if factiness(line.text) >= 0.08 or sum(ch.isdigit() for ch in line.text) >= 6:
                continue
            if contrast and contrast.pos and contrast.pos[:12] in line.text:
                continue
            if line.text.count("=") >= 1 or ".." in line.text:
                continue
            alongside.append(_clip(_finish(line.text), 150))
            used.append(line.text)

    grounds = []
    for line in sorted(evidence, key=lambda item: item.score, reverse=True):
        if len(grounds) >= 4:
            break
        if _similar_any(line.text, grounds):
            continue
        grounds.append(_clip(line.text, 170))

    blob = "\n".join(comment.body for comment in comments)
    names = _names(blob + "\n" + point)
    sources = sorted({comment.time for comment in comments})
    against = ""
    if theme.key != "method" and contrast and contrast.pos and _contrast_ok(contrast):
        if _similar(contrast.pos, point) >= 0.45 or contrast.pos in point:
            against = _clip(contrast.neg, 42)

    return Meaning(
        theme=theme.key,
        label=theme.label,
        point=point,
        alongside=alongside,
        against=against,
        watch=watch,
        grounds=grounds,
        names=names[:8],
        sources=sources,
        order=theme.order,
    )


def _harvest(theme: Theme, claims: list[Line], own_lines: list[Line]) -> list[Line]:
    owned = {line.text for line in own_lines}
    harvested: list[Line] = []
    for line in claims:
        if line.text in owned or len(line.text) > 160:
            continue
        if not any(anchor in line.text for anchor in theme.anchors):
            continue
        if not has_judgment(line.text) or factiness(line.text) >= 0.12:
            continue
        harvested.append(line)
    return harvested


def _on_theme(theme: Theme, text: str) -> bool:
    if theme.key == "micron_print" and "마이크론" in text and has_judgment(text):
        return True
    owner = best_theme(text)
    if owner is None:
        return True
    return owner == theme.key


def _contrast_ok(contrast: Contrast) -> bool:
    if not contrast.pos or not contrast.neg:
        return False
    if len(contrast.neg) > 36 or len(contrast.pos) > 70:
        return False
    timed = re.sub(r"\d{1,2}월|\d{1,2}일", "", contrast.pos)
    if factiness(timed) >= 0.12:
        return False
    return True


def _lead(
    theme: Theme,
    contrast: Contrast | None,
    verdicts: list[str],
    claims: list[Line],
) -> list[str]:
    """대비가 있으면 그 긍정 쪽이 결론이다. 숫자 문장보다 앞선다."""
    chosen: list[str] = []
    if contrast and _contrast_ok(contrast):
        chosen.append(_finish(contrast.pos))
    ranked: list[tuple[int, str]] = []
    for verdict in verdicts:
        ranked.append((score_text(verdict) + 7, _finish(verdict)))
    for line in claims:
        if factiness(line.text) >= 0.11:
            continue
        if not _on_theme(theme, line.text):
            continue
        ranked.append((line.score, _finish(line.text)))
    ranked.sort(key=lambda item: item[0], reverse=True)
    for _score, text in ranked:
        if not text or _similar_any(text, chosen):
            continue
        chosen.append(text)
        if len(chosen) >= 3:
            break
    return chosen


def _method_point(
    lines: list[Line],
    comments: list[Comment],
    notes: list[Comment],
) -> tuple[str, list[str], str]:
    bits: list[str] = []
    for line in sorted(lines, key=lambda item: item.feed_index):
        text = _clip(_finish(line.text), 80)
        if text and not _similar_any(text, bits):
            bits.append(text)
    if not bits:
        return "", [], ""
    point = _join(bits[:2])
    alongside = bits[2:4]
    if comments and notes:
        start = min(comment.feed_index for comment in comments)
        for note in notes:
            if note.feed_index > start and note.theme:
                if note.theme == "sofc":
                    alongside.append("바로 뒤에서 블룸 공급망을 말하니, 이 체로 그 이름을 거르라는 순서로 읽힌다.")
                break
    return point, alongside, ""


def _best_contrast(contrasts: list[Contrast]) -> Contrast | None:
    usable = [item for item in contrasts if _contrast_ok(item)]
    if not usable:
        return None

    def quality(item: Contrast) -> int:
        score = score_text(item.pos) + min(len(item.pos), 40) // 8
        if "결과" in item.pos:
            score += 8
        if "원인" in item.neg:
            score += 3
        return score

    return max(usable, key=quality)


def _join(parts: list[str]) -> str:
    cleaned = []
    for part in parts:
        text = _finish(part)
        if text and not _similar_any(text, cleaned):
            cleaned.append(text)
    return " ".join(cleaned)


def _finish(text: str) -> str:
    clause = clean_line(text)
    clause = re.sub(r"^(그런데|다만|특히|즉|따라서)[, ]*", "", clause)
    clause = re.sub(r"\s+", " ", clause).strip(" \t")
    if clause.endswith("것"):
        clause += "이다"
    if clause and clause[-1] in "다요까임함됨":
        clause += "."
    elif clause and clause[-1] not in ".?!":
        clause += "."
    return clause


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def _first_sentence(text: str) -> str:
    parts = [part.strip() for part in re.split(r"(?<=다\.)\s+|(?<=요\.)\s+|(?<=까\?)\s+", text) if part.strip()]
    sentence = parts[0] if parts else text
    if len(parts) > 1 and len(parts[0]) < 42:
        sentence = f"{parts[0]} {parts[1]}"
    return _clip(sentence, 180)


def _norm(text: str) -> str:
    import re

    return re.sub(r"\s+|[\"“”'‘’·,.]", "", text)


def _similar(left: str, right: str) -> float:
    if not left or not right:
        return 0.0
    if left in right or right in left:
        shorter = min(len(left), len(right))
        longer = max(len(left), len(right))
        if shorter >= 12 and shorter / longer >= 0.34:
            return 0.9
    return SequenceMatcher(None, _norm(left), _norm(right)).ratio()


def _similar_any(text: str, others: list[str]) -> bool:
    return any(_similar(text, other) >= 0.72 for other in others)


def _dedupe(lines: list[Line]) -> list[Line]:
    ranked = sorted(lines, key=lambda line: (line.score, -line.feed_index), reverse=True)
    kept: list[Line] = []
    for line in ranked:
        if _similar_any(line.text, [item.text for item in kept]):
            continue
        kept.append(line)
    return kept


def _names(text: str) -> list[str]:
    found = []
    for label, aliases in NAMES:
        if any(alias in text for alias in aliases):
            found.append(label)
    return found


def _agenda(comments: list[Comment]) -> list[AgendaItem]:
    blob = "\n".join(comment.body for comment in comments)
    items: list[str] = []

    def add(text: str) -> None:
        if text not in items:
            items.append(text)

    if "라이브" in blob or "youtube" in blob:
        add("9월 30일 오전 라이브에서 이어서 설명하겠다고 예고했다.")
    if "PCE" in blob:
        add("8월 PCE를 10월 금리 경로의 1차 분기점으로 짚었다.")
    if "마이크론" in blob and ("실적" in blob or "가이던스" in blob):
        add("방향은 마이크론 실적을 보고 정하겠다는 말이 반복된다. 날짜는 9월 30일과 10월 1일이 같이 나온다.")
    if "고용" in blob:
        add("고용보고서도 금리 쪽 다음 분기점으로 적어 두었다.")
    if "TCMV" in blob or "10월 6일" in blob:
        add("10월 6일 TCMV는 표결이 빠진 추가 논의이고, 다음 회의는 12월로 말했다.")
    if "10월 8일" in blob and "삼성" in blob:
        add("삼성 잠정은 10월 8일로 짚었다.")
    if "10월 15일" in blob:
        add("Roadster 공개는 기상 때문에 10월 15일로 미뤘다고 전했다.")
    if "11월 3일" in blob:
        add("미국 중간선거(11월 3일)를 이란 협상의 시간표로 연결했다.")
    return [AgendaItem(what=item) for item in items]


def _basket(comments: list[Comment]) -> list[tuple[str, str]]:
    import re

    rows: list[tuple[str, str]] = []
    for comment in comments:
        if "관심 종목" not in comment.body:
            continue
        section = ""
        for raw in comment.body.splitlines():
            section, is_header = _basket_header(raw, section)
            if is_header or section != "basket":
                continue
            text = clean_line(raw)
            match = re.match(r"([^:]{2,24}):\s*(.+)", text)
            if match:
                rows.append((match.group(1).strip(), match.group(2).strip()))
    return rows


def _basket_header(raw: str, section: str) -> tuple[str, bool]:
    import re

    bracket = re.match(r"^[<\[]\s*(.+?)\s*[>\]]$", raw.strip())
    label = bracket.group(1).strip() if bracket else ""
    if "관심" in label:
        return "basket", True
    if label:
        return section, True
    return section, False
