"""Score, classify, and compress commentary into a theme report."""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from difflib import SequenceMatcher

from insight_distiller.deep import DeepSection, deep_sections, extra_conditions, supplements
from insight_distiller.dialogs import Dialogue, dialogues
from insight_distiller.extract import Facts, extract_facts
from insight_distiller.parse import Block, dedupe_quick, normalize

THEMES: list[tuple[str, str, list[tuple[str, int]]]] = [
    (
        "portfolio",
        "포트폴리오",
        [
            ("기본포트", 5),
            ("AI쪽", 5),
            ("2차전지", 4),
            ("건설/조선", 4),
            ("분할로만", 4),
            ("안전마진", 3),
        ],
    ),
    (
        "power",
        "전력",
        [("산일전기", 5), ("변압기", 4), ("154kV", 4), ("Bloom", 3)],
    ),
    (
        "hdd",
        "HDD",
        [
            ("HDD", 4),
            ("Seagate", 4),
            ("Western Digital", 4),
            ("Toshiba", 4),
            ("도시바", 4),
            ("시게이트", 4),
            ("WDC", 3),
            ("STX", 3),
        ],
    ),
    (
        "optical",
        "광통신",
        [
            ("광통신", 4),
            ("광모듈", 4),
            ("CRDO", 4),
            ("크레도", 4),
            ("코히런트", 4),
            ("루멘텀", 4),
            ("CCL", 4),
            ("1.6T", 3),
            ("3.2T", 3),
            ("800G", 3),
            ("CPO", 2),
            ("두산", 2),
        ],
    ),
    (
        "substrate",
        "기판 · 패키징 · 소부장",
        [
            ("인텍플러스", 4),
            ("FC-BGA", 4),
            ("삼성전기", 4),
            ("기판", 3),
            ("패키징", 3),
            ("심텍", 3),
            ("Unimicron", 3),
            ("Shinko", 3),
            ("ABF", 3),
            ("소부장", 2),
            ("2028", 2),
            ("2030", 2),
        ],
    ),
    (
        "risk",
        "AI CapEx 리스크",
        [
            ("Burry", 5),
            ("잔존가치", 4),
            ("감가상각", 4),
            ("Anthropic", 4),
            ("프리캐시", 4),
            ("피크아웃", 4),
            ("Broadcom", 3),
            ("오라클", 3),
            ("순환투자", 3),
            ("순환구조", 3),
        ],
    ),
    (
        "memory",
        "메모리",
        [
            ("SK하이닉스", 4),
            ("삼전닉스", 4),
            ("마이크론", 4),
            ("Sandisk", 4),
            ("샌디스크", 4),
            ("삼성전자", 3),
            ("ADR", 3),
            ("HBM", 2),
            ("메모리", 2),
            ("원화", 3),
            ("환율", 2),
        ],
    ),
    (
        "macro",
        "매크로 · 금리",
        [
            ("비농업", 4),
            ("PCE", 4),
            ("10년물", 4),
            ("고용", 3),
            ("임금", 3),
            ("Fed", 3),
            ("연준", 3),
            ("SOX", 2),
            ("금리", 2),
            ("국채", 3),
            ("레버리지", 3),
            ("유가", 2),
            ("디스인플", 3),
        ],
    ),
]

THEME_ORDER = [key for key, _, _ in THEMES]

BAD = (
    "skip",
    "워드파일",
    "게시판",
    "감사합니다",
    "질문 주시면",
    "칩썰",
    "구독",
    "잘 들리",
    "콧방귀",
    "목을 가다듬",
    "코멘트드리겠습니다",
    "모시고",
    "애널리스트",
    "참고 하",
    "설명 드렸",
)
DISPLAY_ORDER = [
    "macro",
    "memory",
    "hdd",
    "optical",
    "substrate",
    "power",
    "risk",
    "portfolio",
]
MARKERS = ("핵심", "즉,", "즉 ", "본질", "따라서", "시사", "프레임", "포인트", "왜냐하면", "구조")
LEAD_HINT = {
    "memory": ("할인", "원화", "보수", "PER ~", "사이클"),
    "hdd": ("2028", "멀티플", "공급", "밸류", "재평가"),
    "optical": ("1.6T", "800G", "3.2T", "규제", "TAM", "Copper"),
    "substrate": ("피크아웃", "밸류체인", "가시성"),
    "power": ("154", "CAGR", "PER", "데이터센터"),
    "macro": ("인상", "동결", "유가", "인플", "싸움", "프레임"),
    "risk": ("수명", "순환", "잔존", "버블", "CapEx"),
    "portfolio": ("분할", "현금", "유가", "코스닥"),
}

WATCH = {
    "원익IPS": ("원익IPS", "원익 아이피스", "원익이스", "원이스"),
    "HPSP": ("HPSP",),
    "한미반도체": ("한미반도체", "한미 반도체"),
    "리노공업": ("리노공업", "리노랑", "리노 "),
    "삼성전기": ("삼성전기",),
    "심텍": ("심텍", "심택"),
    "대덕전자": ("TLB", "대덕"),
    "솔브레인": ("솔브레인", "솔브레이"),
    "필옵틱스": ("필옵틱스", "필업스"),
    "SFA": ("SFA",),
    "유진테크": ("유진테크", "유진 테크"),
    "주성엔지니어링": ("주성 엔지니어링", "주성엔지니어링", "주성은"),
    "PSK": ("PSK", "피에스케이"),
    "ISC": ("ISC",),
    "산일전기": ("산일전기",),
    "인텍플러스": ("인텍플러스",),
}

SOURCE_TAGS = (
    "이선엽",
    "삼프로",
    "윤지호",
    "이지원",
    "메리츠",
    "골드만",
    "Bernstein",
    "BofA",
    "Barron",
)


@dataclass
class Bullet:
    text: str
    score: int
    source: str
    time: str | None = None


@dataclass
class Section:
    key: str
    title: str
    lead: str
    bullets: list[Bullet] = field(default_factory=list)
    table: list[dict] = field(default_factory=list)


@dataclass
class Report:
    headline: str
    sections: list[Section]
    facts: Facts
    checklist: list[str]
    watchlist: list[tuple[str, int]]
    chapters: list[str]
    sources: list[str]
    stats: dict
    deep: list[DeepSection] = field(default_factory=list)
    dialogs: list[Dialogue] = field(default_factory=list)


def _clean(line: str) -> str:
    line = line.replace("**", "").replace("\u00a0", " ").strip()
    line = re.sub(r"\s+\d{1,2}:\d{2}\s*$", "", line)
    line = re.sub(r"\s+", " ", line)
    return line.strip(" -")


def _explode(line: str) -> list[str]:
    if len(line) < 110:
        return [line]
    parts = re.split(r"(?<=다\.)\s+|(?<=요\.)\s+|(?<=니다\.)\s+|(?<=까\.)\s+", line)
    parts = [_clean(p) for p in parts if _clean(p)]
    return parts or [line]


def statements_from_quick(text: str) -> list[str]:
    raw = [_clean(x) for x in text.splitlines()]
    raw = [x for x in raw if x and not re.fullmatch(r"\d{1,2}:\d{2}", x)]
    merged: list[str] = []
    i = 0
    while i < len(raw):
        cur = raw[i]
        chain = cur.count("→") >= 2 and len(cur) < 80
        if chain and merged and len(merged[-1]) < 90:
            nxt = raw[i + 1] if i + 1 < len(raw) and len(raw[i + 1]) < 120 else ""
            prev = merged.pop()
            merged.append(" ".join(x for x in (prev, cur, nxt) if x))
            i += 2 if nxt else 1
            continue
        merged.append(cur)
        i += 1
    out: list[str] = []
    for line in merged:
        out.extend(_explode(line))
    cleaned = []
    for sentence in out:
        sentence = re.sub(r"^(?:[①-⑳]|[0-9]+[.)]|•|→)+\s*", "", sentence).strip()
        if len(sentence) >= 18:
            cleaned.append(sentence)
    return cleaned


def transcript_statements(text: str) -> list[str]:
    lines: list[str] = []
    for raw in text.splitlines():
        s = _clean(raw)
        if not s or re.fullmatch(r"(?:\d+분(?: \d+초)?|\d+초|\d{1,2}:\d{2})", s):
            continue
        if s.startswith("챕터") or len(s) <= 3:
            continue
        lines.append(s)
    buf = ""
    out: list[str] = []
    for s in lines:
        buf = f"{buf} {s}".strip()
        if len(buf) >= 80 and (buf.endswith(("다", "요", "까", "죠", ".", "다.", "요.")) or len(buf) >= 150):
            out.append(buf)
            buf = ""
    if len(buf) >= 80:
        out.append(buf)
    return out


def score_statement(text: str, kind: str) -> int:
    if any(bad in text for bad in BAD):
        return -100
    if len(text) < 22:
        return -8
    score = 6 if kind == "quick" else 1
    score += 3 * sum(1 for marker in MARKERS if marker in text)
    if re.search(r"\d", text):
        score += 2
    if "→" in text:
        score += 2
    n = len(text)
    if 40 <= n <= 220:
        score += 3
    elif 220 < n <= 320:
        score += 1
    elif n > 420:
        score -= 4
    filler = len(re.findall(r"그죠|예\.|음\.|아 |네\.", text))
    score -= filler * 2
    if text.count("예") >= 3:
        score -= 4
    if "기본 정보" in text or text.startswith("SerDes") or "Serializer" in text:
        score -= 5
    if text.startswith("<") or text.startswith("*("):
        score -= 6
    if re.search(r"조/\s*[\d.]+K", text):
        score -= 6
    if re.search(r"\d{1,2}:\d{2}", text) or "두서없이" in text or "해 놨" in text:
        score -= 8
    return score


def classify(text: str) -> str | None:
    best_key = None
    best = 0
    for key, _title, weights in THEMES:
        total = sum(weight for token, weight in weights if token in text)
        if total > best:
            best = total
            best_key = key
    if best < 3:
        return None
    return best_key


def _similar(a: str, b: str) -> bool:
    na, nb = normalize(a), normalize(b)
    if not na or not nb:
        return False
    if na == nb or na in nb or nb in na:
        return True
    if abs(len(na) - len(nb)) / max(len(na), len(nb)) > 0.4:
        return False
    return SequenceMatcher(None, na[:400], nb[:400]).ratio() >= 0.78


def _pick(items: list[Bullet], limit: int = 5) -> list[Bullet]:
    ranked = sorted(items, key=lambda b: (b.score, -len(b.text)), reverse=True)
    kept: list[Bullet] = []
    for bullet in ranked:
        if bullet.score < 6:
            continue
        if any(_similar(bullet.text, k.text) for k in kept):
            continue
        kept.append(bullet)
        if len(kept) >= limit:
            break
    if len(kept) < 3:
        for bullet in ranked:
            if bullet in kept or bullet.score < 4:
                continue
            if any(_similar(bullet.text, k.text) for k in kept):
                continue
            kept.append(bullet)
            if len(kept) >= limit:
                break
    return kept


def _clip(text: str, limit: int = 280) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    parts = re.split(r"(?<=다\.)\s+|(?<=요\.)\s+", text)
    if parts and len(parts[0]) >= 40:
        return parts[0] if len(parts[0]) <= limit else parts[0][: limit - 1] + "…"
    return text[: limit - 1] + "…"


def _pop_match(bullets: list[Bullet], hints: tuple[str, ...], max_len: int = 180) -> Bullet | None:
    for i, bullet in enumerate(bullets):
        if any(hint in bullet.text for hint in hints) and len(bullet.text) <= max_len:
            return bullets.pop(i)
    for i, bullet in enumerate(bullets):
        if any(hint in bullet.text for hint in hints):
            chosen = bullets.pop(i)
            chosen.text = _clip(chosen.text, max_len)
            return chosen
    return None


def _num(facts: Facts, *keys: str) -> bool:
    return all(facts.scalars.get(k) for k in keys)


def _lead(key: str, facts: Facts, bullets: list[Bullet]) -> str:
    s = facts.scalars
    parts: list[str] = []
    if key == "memory" and _num(facts, "hynix_price", "samsung_price"):
        parts.append(
            f"SK하이닉스 {s['hynix_price']}만 원은 26년 PER {s.get('hynix_per_26')}배, 27년 PER {s.get('hynix_per_27')}배다. "
            f"삼성전자 {s['samsung_price']}만 원은 26년 PER {s.get('samsung_per_26')}배, 27년 PER {s.get('samsung_per_27')}배다."
        )
        if s.get("yoy_op"):
            parts.append(
                f"원문 기준 27년 영업이익은 YoY +{s['yoy_op']}% 이상이고, EPS는 하이닉스 +{s.get('yoy_hynix_eps')}%, 삼성전자 +{s.get('yoy_samsung_eps')}%다."
            )
        if s.get("hynix_floor"):
            parts.append(
                f"27년 성장이 없다는 가정에 26년 PER 약 {s.get('floor_per')}배를 적용하면 "
                f"하이닉스 {s['hynix_floor']}만 원, 삼성전자 {s.get('samsung_floor')}이다."
            )
        if s.get("fx_move"):
            parts.append(
                f"원화 {s['fx_move']} 강세는 삼전·닉스 주가에 {s.get('fx_price_hit')} 하락 요인으로 적혀 있다."
            )
    elif key == "hdd" and s.get("stx_per") and s.get("wdc_per"):
        parts.append(
            f"시게이트는 FY27 EPS {s.get('stx_eps')}달러에 PER {s['stx_per']}배, "
            f"웨스턴디지털은 FY27 EPS {s.get('wdc_eps')}달러에 PER {s['wdc_per']}배다."
        )
        if s.get("toshiba_capex"):
            parts.append(f"도시바 증설 규모는 약 {s['toshiba_capex']}억 달러다.")
        if s.get("share_wdc"):
            parts.append(
                f"용량 점유율은 웨스턴디지털 {s['share_wdc']}%, 시게이트 {s['share_stx']}%, 도시바 {s['share_toshiba']}%다."
            )
        if s.get("hdd_impact"):
            parts.append("가격에 반영되는 시점은 2028년 이후로 적혀 있다.")
    elif key == "optical" and s.get("cohr_d"):
        parts.append(
            f"코히런트는 주간 +{s['cohr_w']}% · 전일 +{s['cohr_d']}%, "
            f"루멘텀은 +{s['lite_w']}% · 전일 +{s['lite_d']}%, "
            f"크레도는 3거래일 +{s['crdo_1']}% · +{s['crdo_2']}% · +{s['crdo_3']}%다."
        )
        if s.get("crdo_rev"):
            parts.append(
                f"크레도 FY2027 1분기 매출은 ${s['crdo_rev']}M, 전년 대비 +{s.get('crdo_yoy')}%다."
            )
        if s.get("ccl_3q"):
            parts.append(
                f"두산 광모듈용 CCL은 1분기 {s['ccl_1q']}억, 2분기 {s['ccl_2q']}억, 3분기 {s['ccl_3q']}억(+{s['ccl_qoq']}% QoQ)이다."
            )
    elif key == "substrate" and s.get("semco_revision"):
        parts.append(f"삼성전기 이익 전망은 기존 컨센서스 대비 +{s['semco_revision']}%로 적혀 있다.")
        if s.get("semco_margin"):
            parts.append(f"보유 안전마진은 파일에서 먼저 나온 {s['semco_margin']}를 채택한다.")
        if s.get("intech_tp"):
            parts.append(
                f"인텍플러스 목표주가는 {s['intech_tp']}만 원, 2027년 영업이익 +{s.get('intech_op_27')}%다."
            )
        if s.get("shinko") or s.get("unimicron"):
            parts.append(
                "선행 증설 시계는 "
                + ", ".join(
                    p
                    for p in (
                        f"신코 {s['shinko']} 생산" if s.get("shinko") else "",
                        f"유니마이크론 {s['unimicron']} 캐파" if s.get("unimicron") else "",
                    )
                    if p
                )
                + "이다."
            )
    elif key == "power" and s.get("sanil_sales_cagr"):
        parts.append(
            f"산일전기 FY26~28 매출 CAGR {s['sanil_sales_cagr']}%, 영업이익 CAGR {s['sanil_op_cagr']}%, "
            f"FY28 PER {s.get('sanil_per')}배(LS일렉트릭 약 {s.get('ls_per')}배)다."
        )
    elif key == "macro" and s.get("jobs_actual"):
        parts.append(
            f"9월 고용은 {s['jobs_actual']}만 명으로 컨센서스 {s.get('jobs_cons')}만 명을 밑돌았다."
        )
        if s.get("wage"):
            parts.append(f"시간당 임금 상승률은 연초 {s.get('wage_start')}%에서 {s['wage']}%다.")
        if s.get("ust10"):
            parts.append(f"10년물은 {s['ust10']}%까지 재상승한 기록이 있다.")
        if s.get("gs_october"):
            parts.append("골드만삭스는 10월 추가 인상 전망을 철회했다.")
    elif key == "risk" and s.get("gpu_life"):
        parts.append(f"GPU 경제적 수명 가정은 {s['gpu_life']}이다.")
        if s.get("avgo_financing"):
            parts.append(f"브로드컴-앤트로픽 금융은 원문 표기 ${s['avgo_financing']}bn이다.")
    elif key == "portfolio" and s.get("port_ai"):
        parts.append(
            f"경력자 포트는 AI {s['port_ai']}(삼전·닉스 {s.get('port_memory')}, 소부장 {s.get('port_materials')}), "
            f"2차전지 {s.get('port_battery')}, 건설·조선 {s.get('port_infra')}, 현금 {s.get('port_cash')}다."
        )
        if s.get("port_cash_light"):
            parts.append(f"매매 시간이 적으면 현금 {s['port_cash_light']}다.")

    hint = _pop_match(bullets, LEAD_HINT.get(key, ()))
    if hint:
        parts.append(_clip(hint.text))
    return " ".join(p for p in parts if p).strip()


def _headline(bullets: list[Bullet]) -> str:
    pool = [b for b in bullets if "싸움" in b.text or "Bad Jobs" in b.text or "프레임" in b.text]
    if not pool:
        return ""
    best = max(pool, key=lambda b: (1 if "싸움" in b.text else 0, b.score))
    text = re.sub(r"^따라서:\s*", "", best.text)
    return _clip(text, 240)


def _checklist(bullets: list[Bullet], used: list[str]) -> list[str]:
    hints = ("분할", "눌릴", "제약", "연휴", "베스트", "안전마진", "5% 이하", "확인되면", "장기화")
    ranked = sorted(
        [b for b in bullets if b.score >= 6 and any(h in b.text for h in hints) and len(b.text) <= 180],
        key=lambda b: b.score,
        reverse=True,
    )
    kept: list[str] = []
    for bullet in ranked:
        text = _clip(bullet.text, 180)
        if any(_similar(text, prev) for prev in kept + used):
            continue
        kept.append(text)
        if len(kept) >= 6:
            break
    return kept


def _watchlist(transcripts: list[Block]) -> list[tuple[str, int]]:
    blob = "\n".join(b.prep() for b in transcripts)
    counts = []
    for name, aliases in WATCH.items():
        count = sum(blob.count(alias) for alias in aliases)
        if count >= 3:
            counts.append((name, count))
    counts.sort(key=lambda item: item[1], reverse=True)
    return counts[:12]


def _sources(text: str) -> list[str]:
    return [tag for tag in SOURCE_TAGS if tag in text]


def build_report(blocks: list[Block]) -> Report:
    quick = [b for b in blocks if b.kind == "quick"]
    deduped, dropped = dedupe_quick(quick)
    corpus = "\n".join(b.prep() for b in deduped)
    facts = extract_facts(corpus)
    full_text = "\n".join(b.prep() for b in blocks)

    pool: list[Bullet] = []
    for block in deduped:
        for sentence in statements_from_quick(block.prep()):
            pool.append(
                Bullet(sentence, score_statement(sentence, "quick"), "quick", block.time)
            )
    transcripts = [b for b in blocks if b.kind == "transcript"]
    for block in transcripts:
        for sentence in transcript_statements(block.prep()):
            scored = score_statement(sentence, "transcript")
            if scored >= 8:
                pool.append(Bullet(sentence, scored, "transcript", None))

    headline = _headline(pool)
    if headline:
        pool = [b for b in pool if not _similar(b.text, headline)]

    grouped: dict[str, list[Bullet]] = defaultdict(list)
    for bullet in pool:
        theme = classify(bullet.text)
        if theme:
            grouped[theme].append(bullet)

    titles = {key: title for key, title, _ in THEMES}
    built: dict[str, Section] = {}
    used: list[str] = [headline] if headline else []
    for key in THEME_ORDER:
        bullets = _pick(grouped.get(key, []))
        table = [row for row in facts.companies if row.get("group") == key]
        lead = _lead(key, facts, bullets)
        bullets = [b for b in bullets if not _similar(b.text, lead)][:5]
        if not lead and not bullets and not table:
            continue
        built[key] = Section(key, titles[key], lead, bullets, table)
        used.append(lead)
        used.extend(b.text for b in bullets)

    for key, lines in supplements(full_text, facts).items():
        section = built.get(key)
        if section is None:
            continue
        for line in lines:
            if any(_similar(line, prev) for prev in [section.lead, *[b.text for b in section.bullets]]):
                continue
            section.bullets.append(Bullet(line, 0, "extract", None))
        section.bullets = section.bullets[:12]

    raw_sections = [built[key] for key in DISPLAY_ORDER if key in built]
    talks = dialogues(full_text)
    deep = deep_sections(full_text)
    checklist = _checklist(pool, used)
    for line in extra_conditions(full_text):
        if any(_similar(line, prev) for prev in checklist):
            continue
        checklist.append(line)

    report = Report(
        headline=headline,
        sections=raw_sections,
        facts=facts,
        checklist=checklist,
        watchlist=_watchlist(transcripts),
        chapters=[b.text for b in blocks if b.kind == "chapter"],
        sources=_sources(full_text),
        stats={
            "quick_raw": len(quick),
            "quick_kept": len(deduped),
            "quick_dropped": dropped,
            "transcript_blocks": len(transcripts),
            "chapters": sum(1 for b in blocks if b.kind == "chapter"),
            "statements_scored": len(pool) + (1 if headline else 0),
            "deep_items": sum(len(section.items) for section in deep),
            "dialog_items": sum(len(show.items) for show in talks),
        },
        deep=deep,
        dialogs=talks,
    )
    from insight_distiller.unify import prune_checklist, unify

    report.sections = unify(report)
    report.checklist = prune_checklist(report.checklist, report.sections)
    report.stats["unified_bullets"] = sum(len(section.bullets) for section in report.sections)
    return report
