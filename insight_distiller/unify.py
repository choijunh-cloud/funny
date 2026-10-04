"""Fold quick comments, the second pass, and the five talks into one note.

A point that shows up in more than one source is kept once, with the sources joined.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from insight_distiller.distill import Bullet, Section
from insight_distiller.parse import near_duplicate

# Specific facts only. Broad words like PER or 하이닉스 would glue unrelated lines.
ANCHORS = (
    "1.95%",
    "5.2~5.1",
    "28만 5,000",
    "10월 15일",
    "고점 대비 약 13%",
    "13%까지",
    "불타",
    "장비 사이클은 5년",
    "5년짜리",
    "12만 원",
    "16.8배",
    "약 9배",
    "아홉배",
    "4만 대",
    "담합",
    "2.4GW",
    "7대 3",
    "4,400만",
    "25조",
    "위클리",
    "1,500원",
    "400만 원",
    "장단기",
    "퀄리티",
    "15% 이상",
    "프리캐시",
    "5.5%",
    "박스이고",
    "박스권",
    "수급의 파괴력",
    "통신 투자",
    "커버드콜",
    "11월 3일",
    "1480원",
    "DustPhotonics",
    "HVLP4",
    "A100",
    "코스닥 비중",
    "Bad Jobs",
    "저보스",
    "11.2배",
    "예비율",
    "65%",
    "ZeroFlap",
    "PhotonLink",
    "3개월 평균",
    "근원 PCE",
    "직접·간접",
    "유럽은",
    "군사용",
    "보안 사고",
    "인수자",
    "단가는 주춤",
    "물량 사이클",
    "기울기",
    "넘어가는 쪽",
    "원자 폭탄",
    "핵과 우주",
    "본전",
    "고점 매도",
    "성장주가 버는",
    "민감도는 과거",
    "민감도는 많이",
    "패시브 매도",
    "급락하지 않은",
    "증착",
    "유리기판",
    "한미반도체",
    "고압수소",
    "장부 밖",
    "외국인의 코스피",
    "패시브 매도는 계속",
    "수주잔고",
    "영업이익률은 FY26",
    "점유율은 86%",
    "합산 점유율",
    "할인율 밴드",
    "-20~-50%",
    "ADR 프리미엄",
    "컨센서스 환율",
    "베라 루빈",
    "목표주가는 $350",
    "목표주가 $350",
    "매출 성장률 가이던스",
    "수혜 사슬",
    "투기등급",
    "임대료를 못",
    "의무공개매수",
    "솔리다임",
    "선행지수는",
    "동행지수",
    "높은 배수에 사서",
    "수출 금액은 강한",
    "화장품은 수출",
    "화장품은 전체",
    "토큰 가격",
    "추론 사용",
    "피지컬 주가",
    "배당·커버드콜",
    "나눠 판다",
    "잘게 나눈다",
    "영업이익률 82%",
    "61%에서 63%",
    "약 18% 오른다",
    "40GW",
    "120GW",
    "아시아 50개",
    "3.5%",
    "33달러",
    "450만 개",
    "430만 개",
    "110조",
    "70조",
    "HBM4",
    "120%",
    "신흥국부터",
    "주주환원 때",
    "20~30%",
    "소재는 부족",
    "소비 신용",
    "출하의 약 97%",
    "500위안",
    "데이터 주권",
    "텔레오퍼레이션",
    "리베로",
    "띵커",
    "나비 AI",
    "4,500만",
    "세 배",
    "49bp",
    "260%",
    "ROE",
    "8,000억 달러",
    "가계 소비",
    "26건",
    "2.5배",
    "특별 배당",
    "국산화",
    "100에서 나이",
    "한국 원전",
    "기판과 MLCC",
    "약 4배",
    "130%",
    "30~40%",
    "7,200",
    "코스닥 888",
    "66%",
    "알래스카 LNG",
    "10월 9일",
    "두산에너빌리티",
    "하나오션",
    "블루아울",
    "물 먹는 하마",
    "120조",
    "명목 GDP",
    "필수 투입재",
    "내년 2분기",
    "SLR",
    "기간 프리미엄",
    "175만",
    "현금이 가는",
    "동아시아",
    "파란 불",
    "영원한 해자",
    "커스텀 HBM",
    "YMTC",
    "다시는 내려오지",
    "내년 1분기 3.1%",
    "디젤",
    "위험 선호",
    "고물가 국면",
    "ISM 제조업",
    "6개월과 1년 승률",
    "같이 오버웨이트",
    "카메라 모듈 마진",
    "시장 약 27조",
    "3배에서 5배",
    "6조 8,000억",
    "48~56주",
    "200만 원 초중반",
    "무라타",
    "86.25",
    "약 3%밖에",
    "101조~108조",
    "토큰 수요",
    "약 300억 달러",
    "베트남을 포함한 아세안",
    "4,500억 달러",
    "희토류",
    "가격 통제권",
    "70에서 50",
)

RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("macro", ("SOX", "+30bp", "Bad Jobs", "저보스", "근원 PCE", "3개월 평균", "5.2~5.1", "장단기", "급락하지 않은", "약 9배", "아홉배", "49bp", "66%", "알래스카", "SLR", "가계 소비", "130%", "내부 수익률", "기간 프리미엄", "다시는 내려오지", "디젤", "위험 선호", "고물가", "ISM 제조업", "6개월과 1년 승률", "약 300억 달러", "아세안", "희토류", "가격 통제권")),
    ("supply", ("4,400만", "25조", "위클리", "1,500원", "패시브", "1.95%", "28만 5,000", "10월 15일", "13%", "불타", "자사주", "본전", "외국인의 코스피", "신흥국부터", "7,200", "120조")),
    ("power", ("2.4GW", "주피터", "예비율", "154kV", "산일", "블룸", "임대료", "투기등급", "장부 밖", "11월 3일", "중간선거", "한국 원전", "두산에너빌리티")),
    ("robot", ("휴머노이드", "감속기", "유니트리", "텔레오", "액추에이터", "나비", "리베로", "띵커")),
    ("peak", ("400만 원", "15% 이상", "프리캐시", "5.5%", "수급의 파괴력", "통신 투자", "커버드콜", "기울기", "박스", "고퍼", "원자", "피지컬", "화장품", "토큰", "퀄리티", "단가", "높은 배수", "PER이 낮은", "군사", "4만 대", "담합", "보안 사고", "성장주가 버는", "주식 랠리", "인수자", "솔리다임", "의무공개매수", "40GW", "네오클라우드", "3.5%", "TPU", "소비 신용", "10월 9일", "하나오션", "명목 GDP", "동아시아", "파란 불")),
    ("substrate", ("원익", "HPSP", "리노", "유리기판", "필옵", "증착", "16.8", "인텍", "주성", "PSK", "솔브레인", "장비 사이클", "ETF", "소부장", "MLCC", "20~30%", "삼성전기", "무라타")),
    ("optical", ("1.6T", "800G", "3.2T", "Dust", "BOM", "HVLP", "코히런트", "크레도", "광통신", "광모듈", "레이저", "CCL")),
    ("hdd", ("시게이트", "도시바", "WDC", "HDD", "Toshiba", "웨스턴")),
    ("portfolio", ("기본포트", "7대 3", "코스닥 비중", "2차전지", "분할로", "약 9배", "아홉배", "ROE", "100에서 나이", "코스닥 888", "현금이 가는", "국부 펀드", "국부펀드")),
    ("risk", ("Burry", "A100", "잔존", "42bn", "$42", "수명 가정", "CoreWeave", "블루아울")),
    ("memory", ("하이닉스", "삼성전자", "마이크론", "ADR", "샌디스크", "할인율", "환율", "63%", "PC D램", "HBM4", "110조", "260%", "세 배", "26건", "2.5배", "특별 배당", "30~40%", "필수 투입재", "내년 2분기", "175만", "토큰 수요", "86.25")),
    ("macro", ("고용", "PCE", "10년물", "골드만", "유가", "이란", "임금", "유럽은")),
)

TITLES = {
    "macro": "매크로 · 금리",
    "memory": "메모리",
    "supply": "수급과 가격대",
    "hdd": "HDD",
    "optical": "광통신",
    "substrate": "기판 · 소부장",
    "power": "전력과 데이터센터",
    "robot": "로봇 · 피지컬",
    "peak": "피크아웃 · 산업과 주가",
    "risk": "AI CapEx 리스크",
    "portfolio": "포트폴리오",
}

ORDER = list(TITLES)

LABELS = {
    "lee": "이선엽",
    "yeolmae": "김열매",
    "jiwon": "이지원",
    "yun": "윤지호",
    "hyojin": "김효진",
    "nokun": "노근창",
    "park": "박수현",
    "kcg": "목대균·이경규",
    "rts": "RTS",
    "shin": "신중호",
    "gravity": "전략 이사",
    "semco": "김장렬",
    "jungho": "박정호",
    "deep": "녹취",
    "quick": "퀵코멘트",
    "extract": "퀵코멘트",
    "transcript": "녹취",
    "unified": "합본",
}


@dataclass
class _Item:
    text: str
    sources: set[str] = field(default_factory=set)
    theme: str = "macro"


def _theme(text: str, fallback: str | None) -> str:
    for key, needles in RULES:
        if any(needle in text for needle in needles):
            return key
    return fallback or "macro"


def _anchors(text: str) -> set[str]:
    return {anchor for anchor in ANCHORS if anchor in text}


def _label(sources: set[str]) -> str:
    names = []
    for key in ("quick", "extract", "lee", "yeolmae", "jiwon", "yun", "hyojin", "nokun", "park", "kcg", "rts", "shin", "gravity", "semco", "jungho", "deep", "transcript"):
        if key in sources:
            label = LABELS[key]
            if label not in names:
                names.append(label)
    return " · ".join(names) or "원문"


def _absorb(report) -> list[_Item]:
    found: list[_Item] = []

    def add(text: str, source: str, fallback: str | None) -> None:
        text = " ".join(text.split())
        if len(text) < 20:
            return
        keys = _anchors(text)
        for prev in found:
            shared = keys & _anchors(prev.text)
            if shared or near_duplicate(prev.text, text, threshold=0.72):
                if len(text) > len(prev.text):
                    prev.text = text
                    prev.theme = _theme(text, prev.theme)
                prev.sources.add(source)
                return
        found.append(_Item(text, {source}, _theme(text, fallback)))

    for section in report.sections:
        for bullet in section.bullets:
            add(bullet.text, "quick" if bullet.time or bullet.source == "quick" else bullet.source, section.key)
    for show in report.dialogs:
        for text in show.items:
            add(text, show.key, None)
    for block in report.deep:
        for text in block.items:
            add(text, "deep", block.key)
    return found


def _lead(report, key: str) -> str:
    old = {section.key: section for section in report.sections}
    if key == "substrate" and "substrate" in old:
        return old["substrate"].lead
    if key == "power":
        base = old["power"].lead if "power" in old else ""
        return base
    if key in old:
        return old[key].lead
    if key == "supply":
        return "가격대는 이선엽 방송, 수급은 이지원 인터뷰, 현금 비중은 김열매 대담에서 가져왔다."
    if key == "peak":
        return "싼 배수와 긴 산업 스토리를 한 질문에 모았다. 2028년에도 성장이 이어지는가, 그리고 그 성장이 주가에 남는가다."
    if key == "robot":
        return "중국 휴머노이드는 출하 경쟁보다 현장 데이터가 병목이다. 하드웨어 해자는 뇌가 똑똑해지면 얇아진다."
    return ""


def _table(report, key: str) -> list[dict]:
    for section in report.sections:
        if section.key == key and section.table:
            return section.table
    return []


def unify(report) -> list[Section]:
    grouped: dict[str, list[_Item]] = {key: [] for key in ORDER}
    for item in _absorb(report):
        grouped.setdefault(item.theme, []).append(item)

    sections: list[Section] = []
    for key in ORDER:
        items = grouped.get(key) or []
        items.sort(key=lambda item: (len(_anchors(item.text)), len(item.sources), len(item.text)), reverse=True)
        lead = _lead(report, key)
        bullets: list[Bullet] = []
        covered: set[str] = _anchors(lead)
        for item in items:
            keys = _anchors(item.text)
            if not keys or not (keys - covered):
                continue
            if lead and near_duplicate(lead, item.text, threshold=0.62):
                covered |= keys
                continue
            bullets.append(Bullet(item.text, len(item.sources), "unified", _label(item.sources)))
            covered |= keys
        for item in items:
            if _anchors(item.text) or (lead and near_duplicate(lead, item.text, threshold=0.62)):
                continue
            if any(near_duplicate(item.text, bullet.text, threshold=0.72) for bullet in bullets):
                continue
            bullets.append(Bullet(item.text, len(item.sources), "unified", _label(item.sources)))
            if len(bullets) >= 12:
                break
        table = _table(report, key)
        if not lead and not bullets and not table:
            continue
        sections.append(Section(key, TITLES[key], lead, bullets, table))
    return sections


def prune_checklist(items: list[str], sections: list[Section]) -> list[str]:
    blob = "\n".join(bullet.text for section in sections for bullet in section.bullets)
    blob += "\n" + "\n".join(section.lead for section in sections)
    kept: list[str] = []
    for item in items:
        keys = _anchors(item)
        if keys and any(key in blob for key in keys):
            continue
        if any(near_duplicate(item, prev, threshold=0.7) for prev in kept):
            continue
        if any(near_duplicate(item, bullet.text, threshold=0.7) for section in sections for bullet in section.bullets):
            continue
        kept.append(item)
        if len(kept) >= 6:
            break
    return kept
