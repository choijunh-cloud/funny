#!/usr/bin/env python3
"""10/2 자료(PDF 5 + 퀵코멘트 + 방송 전사)를 구조화하고 차트를 만든다.

숫자는 원문에 실제로 있는 문자열만 사실로 인정한다. 해석은 별도 필드로 둔다.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "sources" / "oct2"
OUT_DIR = ROOT / "output" / "oct2"
CHART_DIR = OUT_DIR / "charts"

PDFS = {
    "muse": "01_muse_airbnb.pdf",
    "bonds_fx_japan": "02_bonds_fx_japan.pdf",
    "pce": "03_august_pce.pdf",
    "oct1_us": "04_oct1_us_session.pdf",
    "avgo": "05_broadcom_anthropic.pdf",
}

# 브리프가 인용하는 앵커. 원문에서 사라지면 테스트가 실패한다.
FACT_NEEDLES: dict[str, str] = {
    "pce_july_old": "3.344%",
    "pce_july_rev": "2.983%",
    "pce_aug": "3.008%",
    "pce_3m": "2.05%",
    "pce_6m": "2.74%",
    "ust_spike": "5.34%",
    "cohr_move": "+10.9%",
    "crdo_move": "+7.9%",
    "cohr_pt": "$350",
    "crdo_sales": "$479M",
    "avgo_42": "$42bn",
    "sanil_cagr_sales": "32.5%",
    "sanil_cagr_op": "38.5%",
    "sanil_per": "PER 16배",
    "ls_per": "31배",
    "intek_tp": "9.5만원",
    "intek_eps": "4,904원",
    "semco_uplift": "+64%",
    "margin_tight": "20~30%",
    "margin_wide": "50~60%",
    "kospi_close": "6,971pt",
    "kosdaq_move": "+4.48%",
    "semi_export": "603억 달러",
    "semi_yoy": "+262.8%",
    "mu_gm": "87%",
    "mu_gm_next": "86.2%",
    "mu_rpo": "1,500억 달러",
    "mu_capex_26": "270억 달러",
    "mu_capex_27h1": "250억 달러",
    "foreign_buy": "3,500억",
    "pension_buy": "233억",
    "hold_odds": "74%",
    "ism_prices": "77.9",
    "acn_bookings": "22.2",
    "acn_fcf": "11.6",
    "acn_return": "11.5",
    "aws_gpu": "15%",
    "ls_hvdc": "345kV",
    "doosan_omon": "8,400억",
    "doosan_ytd": "3조 8",
    "samsung_box": "24만 5,000원",
    "googl_50w": "331달러",
    "france_cut": "540억 유로",
    "buyback_ust": "60억 달러",
    "hana_op": "520조",
    "fx_1350": "1350",
    "shinko_fy": "FY2028",
    "unimicron_2030": "2030년",
    "abnb_multiple": "30배",
    "bkng_multiple": "10~11배",
}

THEMES: list[tuple[str, str, list[str]]] = [
    ("rates", "금리·연준", ["10년물", "국채", "연준", "PCE", "기준금", "금리인상", "금리 인상"]),
    ("memory", "메모리", ["마이크론", "하이닉스", "HBM", "쇼티지", "소티지", "공급 부족", "삼성전자"]),
    ("equipment", "장비·증설", ["반도체 장비", "케팩스", "증설", "클린룸", "어플라이드", "램리서치", "KLA"]),
    ("optical", "광연결", ["광통신", "광트랜", "코히", "크레도", "루멘텀", "AEC", "SerDes", "PhotonLink"]),
    ("packaging", "기판·패키징", ["기판", "FC-BGA", "삼성전기", "심텍", "ABF", "패키징", "인텍플러스"]),
    ("power", "전력·냉각", ["변압기", "변합기", "산일", "칠러", "일렉트릭", "345kV", "냉각"]),
    ("oil", "유가·정유", ["유가", "WTI", "정유", "정제", "브렌트", "석유 제품", "브랜드유"]),
    ("fx", "원화·환율", ["환율", "원달러", "원화", "1350", "1400"]),
    ("circular", "순환투자·GPU수명", ["브로드컴", "Burry", "버리", "감가상각", "잔존가치", "잔존"]),
    ("platform", "에이전트·통행세", ["에어비앤비", "뮤즈", "Muse", "통행세", "부킹"]),
    ("japan_reform", "일본 기업개혁", ["ROIC", "주주환원", "행동주의", "정책보유"]),
    ("japan_macro", "일본 매크로", ["엔화", "관광", "도시락", "3.12", "3.1%"]),
    ("flow", "국내 수급", ["코스닥", "외국인", "연기금", "거래대금"]),
    ("geo", "이란·선거", ["이란", "항공모", "중간 선거", "중간선거", "호르무즈"]),
    ("consumer", "소비 브랜드", ["나이키", "넷플릭스", "화장품"]),
    ("governance", "주주환원", ["자사주", "주주 환원", "주주환원", "주주 언원", "주전원"]),
    ("credit", "회사채·TLT", ["TLT", "회사채", "채권 발행", "하이일드", "하일드"]),
]

ENTITIES: dict[str, list[str]] = {
    "삼성전자": ["삼성전자", "삼성자"],
    "SK하이닉스": ["하이닉스", "하이니스"],
    "마이크론": ["마이크론"],
    "엔비디아": ["엔비디아", "엔피디"],
    "브로드컴": ["브로드컴"],
    "코히런트": ["코히런트", "코히어", "코이어"],
    "크레도": ["크레도", "크리도"],
    "삼성전기": ["삼성전기"],
    "산일전기": ["산일전기", "산일 전기"],
    "인텍플러스": ["인텍플러스"],
    "앤트로픽": ["앤트로픽", "엔트로픽", "엔스로", "앤픽", "엔픽"],
    "나이키": ["나이키"],
    "엑센추어": ["엑센추어", "엑센츄어", "엑센초"],
    "두산에너빌리티": ["두산 에너", "두산에너"],
    "LS일렉트릭": ["LS 일렉", "LS일렉", "일렉트릭"],
    "SK이노베이션": ["이노베이션"],
    "에어비앤비": ["에어비앤비", "Airbnb"],
    "구글": ["구글"],
    "오픈AI": ["오픈 AI", "오픈AI", "오픈에이"],
}

CHAPTERS: list[tuple[str, str, str]] = [
    ("open_macro", "이제 그 쇼티지가", "오프닝 — 장비·수출·유가, 금리가 유가와 반대로 움직임"),
    ("fed_speakers", "필립 제퍼슨", "연준 인사(제퍼슨·쿡·카시카리)와 고용·ISM 첫 정리"),
    ("qa_housing", "미국 집값은 내리고", "질의 — 미국 주택 락인, 한국 부동산·자영업, 코리안 디스카운트"),
    ("park", "박병창", "박병창 — 10/1 수급, 코스닥 양봉, 앤트로픽 IPO 지연, 수출"),
    ("kwon", "권순우", "권순우 — 정유 수출금지, 품목별 수출, LG 칠러, LS·두산, 서울 집값"),
    ("lee", "AFW", "이선엽 — 마이크론 세 조건, 신뢰, 5% 금리의 의미, 10월 정치"),
    ("wallst", "ISM 제조업 가격", "월가 브리핑 — ISM 물가, 광규제, 마이크론 디테일, 나이키·엑센추어"),
    ("dave", "데이바입니다", "데이바 — 회사채 물량, TLT, 비중, 주주환원, 반도체 박스"),
]


@dataclass
class ThemeScore:
    theme_id: str
    label: str
    pdf: int
    comments: int
    speech: int
    pdf_per_10k: float
    comments_per_10k: float
    speech_per_10k: float


@dataclass
class Chapter:
    chapter_id: str
    title: str
    start: int
    end: int
    chars: int


def _pdf_text(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


def _count_hits(text: str, keywords: list[str]) -> int:
    return sum(text.count(k) for k in keywords)


def _per_10k(hits: int, n_chars: int) -> float:
    if n_chars <= 0:
        return 0.0
    return round(hits * 10000 / n_chars, 2)


def load_corpus(source_dir: Path = SOURCE_DIR) -> dict[str, str]:
    pdfs = {key: _pdf_text(source_dir / name) for key, name in PDFS.items()}
    raw = (source_dir / "paste_copy.txt").read_text(encoding="utf-8")
    lines = raw.splitlines()
    speech_at = next(i for i, line in enumerate(lines) if re.match(r"^\d+분", line.strip()))
    comments = "\n".join(lines[: speech_at - 1])
    speech_lines = []
    for line in lines[speech_at - 1 :]:
        s = line.strip()
        if re.match(r"^\d+:\d{2}$", s) or re.match(r"^\d+분", s):
            continue
        speech_lines.append(s)
    speech = "\n".join(speech_lines)
    cut = speech.find("보고서 형식")
    if cut > 0:
        speech = speech[:cut]
    pdf_all = "\n".join(pdfs.values())
    return {
        "pdfs": pdfs,
        "pdf_all": pdf_all,
        "comments": comments,
        "speech": speech,
        "all": "\n".join([pdf_all, comments, speech]),
    }


def parse_comments(comments: str) -> list[dict]:
    parts = re.split(r"\nQuick 코멘트\n", comments)
    blocks = []
    for i, part in enumerate(parts[1:], start=1):
        stamp = ""
        head = parts[i - 1]
        m = re.findall(r"(\d{2}:\d{2})", head)
        if m:
            stamp = m[-1]
        body = part.strip()
        nxt = re.search(r"\n\d{2}:\d{2}\s*$", body)
        if nxt:
            body = body[: nxt.start()].strip()
        blocks.append({"n": i, "time": stamp, "chars": len(body), "text": body})
    return blocks


def score_themes(corpus: dict[str, str]) -> list[ThemeScore]:
    pdf, comments, speech = corpus["pdf_all"], corpus["comments"], corpus["speech"]
    scored = []
    for theme_id, label, kws in THEMES:
        hp, hc, hs = _count_hits(pdf, kws), _count_hits(comments, kws), _count_hits(speech, kws)
        scored.append(
            ThemeScore(
                theme_id,
                label,
                hp,
                hc,
                hs,
                _per_10k(hp, len(pdf)),
                _per_10k(hc, len(comments)),
                _per_10k(hs, len(speech)),
            )
        )
    return scored


def entity_counts(corpus: dict[str, str]) -> list[dict]:
    rows = []
    for name, aliases in ENTITIES.items():
        rows.append(
            {
                "name": name,
                "pdf": _count_hits(corpus["pdf_all"], aliases),
                "comments": _count_hits(corpus["comments"], aliases),
                "speech": _count_hits(corpus["speech"], aliases),
            }
        )
    for row in rows:
        row["total"] = row["pdf"] + row["comments"] + row["speech"]
    rows.sort(key=lambda r: r["total"], reverse=True)
    return rows


def chapter_spans(speech: str) -> list[Chapter]:
    found = []
    for chapter_id, anchor, title in CHAPTERS:
        at = speech.find(anchor)
        if at < 0:
            raise ValueError(f"chapter anchor missing: {anchor}")
        found.append((at, chapter_id, title))
    found.sort()
    chapters = []
    for i, (start, chapter_id, title) in enumerate(found):
        end = found[i + 1][0] if i + 1 < len(found) else len(speech)
        chapters.append(Chapter(chapter_id, title, start, end, end - start))
    return chapters


def check_facts(corpus: dict[str, str]) -> list[dict]:
    text = corpus["all"]
    rows = []
    for fact_id, needle in FACT_NEEDLES.items():
        rows.append({"id": fact_id, "needle": needle, "found": needle in text})
    return rows


def find_tensions(corpus: dict[str, str]) -> list[dict]:
    """같은 재료를 두고 원문 안에 공존하는 긴장. 해석이지 새 사실이 아니다."""
    comments, speech, pdfs = corpus["comments"], corpus["speech"], corpus["pdfs"]
    tensions = []

    if "50~60%" in comments and "20~30%" in comments:
        tensions.append(
            {
                "id": "semco_cushion",
                "topic": "삼성전기 안전마진",
                "what": "같은 논리(이익 +64%, 외국인, 급등 부담)인데 보유 안전마진이 50~60%에서 20~30%로 좁아졌다.",
                "read": "나중 코멘트가 허용 낙폭을 줄였다. 신규는 처음부터 눌림·분할이다.",
            }
        )
    if "종료될 가능성" in comments and "인상 사이클 종료" in comments:
        tensions.append(
            {
                "id": "hike_cycle",
                "topic": "인상 사이클 종료 여부",
                "what": "골드만은 10월 인상 철회에 더해 사이클 종료 가능성까지 말했다. 하우스 코멘트는 PCE가 그 신호는 아니라고 선을 그었다.",
                "read": "10월 동결(단기)과 사이클 종료(레짐)를 한 문장으로 묶지 않는다.",
            }
        )
    if "금리 인하가 될 수 있다" in speech and "현실성이 그렇게 높다라고 생각하지는 않습니다" in speech:
        tensions.append(
            {
                "id": "citi_cut",
                "topic": "다음 액션이 인하인가",
                "what": "시티는 9월 인상 이후 추가 인상 없이 동결을 거쳐 인하가 먼저 올 수 있다고 봤다. 브리핑은 그 현실성을 높게 보지 않았다.",
                "read": "시장이 세 번 인상을 가격에 넣었던 부담이 걷히는 것과, 인하 사이클 시작은 다른 문장이다.",
            }
        )
    if "5.252%" in comments and "5.24" in speech:
        tensions.append(
            {
                "id": "ust_close",
                "topic": "미 10년물 마감",
                "what": "장전 메모는 5.252%, 이후 전사는 5.24 마감과 장중 고점 5.34를 같이 말한다.",
                "read": "레벨의 소수점보다 장중 고점 5.34 이후 되밀렸다는 모양이 공통분모다.",
            }
        )
    if "103달러" in speech and "100달러" in speech:
        tensions.append(
            {
                "id": "brent_print",
                "topic": "브렌트 레벨",
                "what": "한 구간은 브렌트 103달러, 다른 구간은 다시 100달러를 넘었다(+4% 안팎)고 말한다.",
                "read": "공통은 WTI 90달러 초중반, 브렌트 100달러 위, 중국 석유제품 수출 중단이다. 틱은 전사마다 다르다.",
            }
        )
    if "1350" in pdfs["bonds_fx_japan"] and "1400" in pdfs["bonds_fx_japan"]:
        tensions.append(
            {
                "id": "krw_2027",
                "topic": "2027년 원/달러",
                "what": "하나증권이 삼성 2027년 이익을 깎은 이유는 환율 가정을 1400원대 중반에서 1350원으로 낮춘 것이다. 화자는 1350 안착·1300 이하 강세보다 1400원대 재약세에 무게를 둔다.",
                "read": "반도체 적정주가 논의와 환율 가정을 분리한다. 이익 모델의 환율이 강세면 화자의 매크로와 어긋난다.",
            }
        )
    if "MUSE" in comments and "에어비앤비" in pdfs["muse"]:
        tensions.append(
            {
                "id": "muse_two_sided",
                "topic": "뮤즈의 두 얼굴",
                "what": "마감 코멘트는 메타 뮤즈를 AI 캡엑스와 에이전트 기대로 긍정 요인에 올렸다. 같은 뮤즈를 다룬 PDF는 에어비앤비·검색 광고의 통행세가 빠져나가는 사례로 읽는다.",
                "read": "에이전트는 인프라 투자에는 수요이고, 트래픽 수수료 사업에는 대체재다.",
            }
        )
    return tensions


def portfolio_books() -> dict:
    """코멘트에 적힌 범위만 사용. 소부장은 AI 안의 20이다.

    AI 50 = 삼전닉스 30 + 소부장 20, AI 60 = 삼전닉스 40 + 소부장 20.
    하단 북은 합이 90이라 잔여 10은 원문이 배분하지 않은 완충으로 남긴다.
    """
    low = {
        "삼전닉스": 30,
        "소부장": 20,
        "2차전지": 10,
        "건설/조선": 10,
        "현금": 20,
        "원문 미배분": 10,
    }
    high = {
        "삼전닉스": 40,
        "소부장": 20,
        "2차전지": 10,
        "건설/조선": 10,
        "현금": 20,
        "원문 미배분": 0,
    }
    assert sum(low.values()) == 100
    assert sum(high.values()) == 100
    assert low["삼전닉스"] + low["소부장"] == 50
    assert high["삼전닉스"] + high["소부장"] == 60
    return {"experienced_ai50": low, "experienced_ai60": high}


def _font():
    from matplotlib import font_manager

    path = "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc"
    font_manager.fontManager.addfont(path)
    return font_manager.FontProperties(fname=path)


def render_charts(themes: list[ThemeScore], chapters: list[Chapter], out_dir: Path = CHART_DIR) -> dict[str, str]:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch

    out_dir.mkdir(parents=True, exist_ok=True)
    fp = _font()
    plt.rcParams["axes.unicode_minus"] = False
    navy, gold, blue, green, red, ink, grid = (
        "#0F2043",
        "#B8943A",
        "#1E407C",
        "#166534",
        "#991B1B",
        "#1A1A1A",
        "#E6EAF0",
    )

    def style_ax(ax, title):
        ax.set_title(title, fontproperties=fp, color=navy, loc="left", pad=10, fontsize=13)
        ax.tick_params(colors=ink, labelsize=8)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_fontproperties(fp)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color("#D5DCE6")
        ax.spines["bottom"].set_color("#D5DCE6")
        ax.grid(axis="x", color=grid, zorder=0)
        ax.set_axisbelow(True)

    paths: dict[str, str] = {}

    # 1. theme density
    fig, ax = plt.subplots(figsize=(10.2, 6.4), dpi=140)
    ordered = sorted(
        themes,
        key=lambda t: t.speech_per_10k + t.comments_per_10k + t.pdf_per_10k,
        reverse=True,
    )
    labels = [t.label for t in ordered][::-1]
    y = list(range(len(ordered)))
    speech_vals = [t.speech_per_10k for t in ordered][::-1]
    comment_vals = [t.comments_per_10k for t in ordered][::-1]
    pdf_vals = [t.pdf_per_10k for t in ordered][::-1]
    h = 0.26
    ax.barh([i + h for i in y], speech_vals, color=blue, height=h, label="방송 전사", zorder=2)
    ax.barh(y, comment_vals, color=gold, height=h, label="퀵코멘트", zorder=2)
    ax.barh([i - h for i in y], pdf_vals, color="#9A3412", height=h, label="PDF", zorder=2)
    ax.set_yticks(y, labels)
    ax.set_xlabel("1만 자당 키워드 적중", fontproperties=fp, color=ink)
    style_ax(ax, "주제가 어디에 몰려 있나")
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=grid)
    leg = ax.legend(prop=fp, frameon=False, loc="lower right")
    for t in leg.get_texts():
        t.set_color(ink)
    fig.tight_layout()
    p = out_dir / "theme_density.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["theme_density"] = str(p)

    # 2. yield move
    fig, ax = plt.subplots(figsize=(10.2, 4.6), dpi=140)
    tenors = ["1년", "2년", "5년", "10년", "30년"]
    start = [4.54, 4.89, 5.08, 5.29, 5.63]
    end = [4.43, 4.791, 5.00, 5.24, 5.61]
    x = range(len(tenors))
    w = 0.36
    ax.bar([i - w / 2 for i in x], start, width=w, color="#C5CEDA", label="되밀리기 전", zorder=2)
    ax.bar([i + w / 2 for i in x], end, width=w, color=navy, label="되밀린 뒤", zorder=2)
    for i, (a, b) in enumerate(zip(start, end)):
        bp = round((b - a) * 100)
        ax.text(i, max(a, b) + 0.08, f"{bp}bp", ha="center", va="bottom", fontsize=9, color=green, fontproperties=fp)
    ax.set_xticks(list(x), tenors)
    ax.set_ylim(4.0, 6.15)
    ax.set_ylabel("%", fontproperties=fp)
    style_ax(ax, "미국 국채, 만기별로 단기물이 더 빠졌다")
    ax.legend(prop=fp, frameon=False, loc="upper left")
    fig.tight_layout()
    p = out_dir / "ust_move.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["ust_move"] = str(p)

    # 3. scoreboard
    fig, ax = plt.subplots(figsize=(10.2, 4.8), dpi=140)
    names = ["KOSPI", "KOSDAQ", "S&P", "나스닥", "SOX", "MU", "SKHY\nADR", "NVDA", "AVGO", "COHR", "LITE", "CRDO"]
    vals = [1.95, 4.48, 0.20, 0.04, 1.59, 3.03, 5.08, 1.14, -2.13, 10.90, 7.67, 7.9]
    colors = [green if v >= 0 else red for v in vals]
    ax.bar(names, vals, color=colors, zorder=2)
    ax.axhline(0, color="#D5DCE6", lw=1)
    ax.set_ylabel("%", fontproperties=fp)
    for i, v in enumerate(vals):
        ax.text(i, v + (0.25 if v >= 0 else -0.45), f"{v:+.2f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=7.5, color=ink, fontproperties=fp)
    style_ax(ax, "10/1 국내 마감과 직전 미국장, 같은 날의 수익률")
    ax.set_ylim(-4, 13)
    fig.tight_layout()
    p = out_dir / "scoreboard.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["scoreboard"] = str(p)

    # 4. portfolio
    fig, ax = plt.subplots(figsize=(10.2, 3.6), dpi=140)
    books = portfolio_books()
    keys = list(books["experienced_ai60"].keys())
    palette = {
        "삼전닉스": navy,
        "소부장": blue,
        "2차전지": "#3D6B4F",
        "건설/조선": gold,
        "현금": "#C5CEDA",
        "원문 미배분": "#F4E4C4",
    }
    left_low = 0
    left_high = 0
    for key in keys:
        ax.barh(1, books["experienced_ai50"][key], left=left_low, color=palette[key], height=0.55, zorder=2)
        ax.barh(0, books["experienced_ai60"][key], left=left_high, color=palette[key], height=0.55, zorder=2)
        if books["experienced_ai50"][key] >= 8:
            ax.text(left_low + books["experienced_ai50"][key] / 2, 1, f"{key}\n{books['experienced_ai50'][key]}", ha="center", va="center", fontsize=7.5, color="white" if key in {"삼전닉스", "소부장", "2차전지"} else ink, fontproperties=fp)
        if books["experienced_ai60"][key] >= 8:
            ax.text(left_high + books["experienced_ai60"][key] / 2, 0, f"{key}\n{books['experienced_ai60'][key]}", ha="center", va="center", fontsize=7.5, color="white" if key in {"삼전닉스", "소부장", "2차전지"} else ink, fontproperties=fp)
        left_low += books["experienced_ai50"][key]
        left_high += books["experienced_ai60"][key]
    ax.set_yticks([1, 0], ["AI 50 북", "AI 60 북"])
    ax.set_xlabel("비중 %", fontproperties=fp)
    ax.set_xlim(0, 100)
    style_ax(ax, "경력자 기본북 — AI 범위의 양 끝만 원문에 있다")
    fig.tight_layout()
    p = out_dir / "portfolio.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["portfolio"] = str(p)

    # 5. PCE path
    fig, ax = plt.subplots(figsize=(10.2, 4.2), dpi=140)
    labels = ["7월 발표", "7월 개정", "8월"]
    vals = [3.344, 2.983, 3.008]
    cols = ["#C5CEDA", blue, navy]
    ax.plot(labels, vals, color=gold, lw=2, zorder=2)
    ax.scatter(labels, vals, s=80, color=cols, zorder=3)
    for lab, v in zip(labels, vals):
        ax.text(lab, v + 0.04, f"{v:.3f}%", ha="center", fontproperties=fp, color=ink, fontsize=10)
    ax.annotate(
        "헤드라인의 '3.34→3.0'은\n이 개정 구간이다",
        xy=(0.5, 3.16),
        xytext=(0.15, 3.22),
        fontproperties=fp,
        fontsize=9,
        color=red,
        arrowprops=dict(arrowstyle="->", color=red),
    )
    ax.set_ylim(2.85, 3.5)
    ax.set_ylabel("Core PCE YoY %", fontproperties=fp)
    style_ax(ax, "8월 코어 PCE 3.0%의 실체")
    fig.tight_layout()
    p = out_dir / "pce_path.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["pce_path"] = str(p)

    # 6. scenario map
    fig, ax = plt.subplots(figsize=(10.2, 5.6), dpi=140)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")
    ax.set_title("금리가 고점인 이유에 따라 자산이 갈린다", fontproperties=fp, color=navy, loc="left", fontsize=13)
    boxes = [
        (0.4, 5.2, 4.5, 4.2, "#E8F5E9", green, "경기 견조 + 금리 상승 멈춤", "골디락스\n주식이 채권보다 낫다\n할인율 안정 + EPS"),
        (5.1, 5.2, 4.5, 4.2, "#E8F1FB", blue, "경기 침체 + 금리 고점", "채권의 논리\n가격 하락이 끝나고\n금리 하락 시 자본차익"),
        (0.4, 0.4, 4.5, 4.4, "#FFF8E7", "#7A5C12", "경기 견조 + 금리가 다시 오른다", "케이스 2\n주식 하락이 크진 않아도\n상승 한계가 보인다"),
        (5.1, 0.4, 4.5, 4.4, "#FDECEA", red, "인플레가 소비·성장을 꺾는다", "주식 논리의 붕괴 조건\n아직 그 시그널은 없다\n유가 $100+는 꼬리"),
    ]
    for x, y, w, h, fill, edge, head, body in boxes:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.15", facecolor=fill, edgecolor=edge, lw=1.4))
        ax.text(x + 0.25, y + h - 0.45, head, fontproperties=fp, fontsize=9, color=edge, fontweight="bold", va="top")
        ax.text(x + 0.25, y + h - 1.15, body, fontproperties=fp, fontsize=9, color=ink, va="top")
    fig.tight_layout()
    p = out_dir / "scenario_map.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["scenario_map"] = str(p)

    # 7. chapter weight
    fig, ax = plt.subplots(figsize=(10.2, 4.2), dpi=140)
    labels = [c.title.split("—")[0].strip() for c in chapters]
    vals = [round(c.chars / 1000, 1) for c in chapters]
    ax.barh(labels[::-1], vals[::-1], color=navy, zorder=2)
    ax.set_xlabel("분량 (천 자)", fontproperties=fp)
    style_ax(ax, "방송 41분, 화자 구간별 분량")
    fig.tight_layout()
    p = out_dir / "chapters.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["chapters"] = str(p)

    # 8. capex stack timeline (qualitative positions)
    fig, ax = plt.subplots(figsize=(10.2, 3.8), dpi=140)
    stages = [
        (2026, "메모리 쇼티지\n이미 내년 물량 매진"),
        (2027, "HBM 재계약\n장비 캐파 배증"),
        (2028, "수급이 2026보다 타이트\n신코 양산, 산일 154kV"),
        (2030, "유니마이크론 캐파\n기판 선행 투자"),
        (2031, "일부 LTA 만기"),
    ]
    xs = [s[0] for s in stages]
    ax.hlines(0, 2025.7, 2031.4, color=gold, lw=3, zorder=1)
    ax.scatter(xs, [0] * len(xs), s=90, color=navy, zorder=2)
    for i, (year, text) in enumerate(stages):
        dy = 0.18 if i % 2 == 0 else -0.38
        va = "bottom" if dy > 0 else "top"
        ax.text(year, dy, f"{year}\n{text}", ha="center", va=va, fontproperties=fp, fontsize=8, color=ink)
    ax.set_ylim(-0.85, 0.7)
    ax.axis("off")
    ax.set_title("AI 공급망이 말해 준 시간축", fontproperties=fp, color=navy, loc="left", fontsize=13)
    fig.tight_layout()
    p = out_dir / "capex_timeline.png"
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close()
    paths["capex_timeline"] = str(p)

    return paths


def analyze(source_dir: Path = SOURCE_DIR, out_dir: Path = OUT_DIR) -> dict:
    corpus = load_corpus(source_dir)
    themes = score_themes(corpus)
    chapters = chapter_spans(corpus["speech"])
    facts = check_facts(corpus)
    missing = [f["id"] for f in facts if not f["found"]]
    if missing:
        raise SystemExit(f"fact needles missing from corpus: {missing}")
    tensions = find_tensions(corpus)
    entities = entity_counts(corpus)
    comments = parse_comments(corpus["comments"])
    charts = render_charts(themes, chapters, out_dir / "charts")
    books = portfolio_books()

    top_speech = sorted(themes, key=lambda t: t.speech_per_10k, reverse=True)[:4]
    top_comments = sorted(themes, key=lambda t: t.comments_per_10k, reverse=True)[:4]
    top_pdf = sorted(themes, key=lambda t: t.pdf_per_10k, reverse=True)[:4]

    payload = {
        "counts": {
            "pdf_chars": len(corpus["pdf_all"]),
            "comment_chars": len(corpus["comments"]),
            "speech_chars": len(corpus["speech"]),
            "comment_blocks": len(comments),
            "chapters": len(chapters),
            "facts": len(facts),
            "facts_found": sum(1 for f in facts if f["found"]),
            "tensions": len(tensions),
        },
        "density_leaders": {
            "speech": [t.label for t in top_speech],
            "comments": [t.label for t in top_comments],
            "pdf": [t.label for t in top_pdf],
        },
        "themes": [asdict(t) for t in themes],
        "chapters": [asdict(c) for c in chapters],
        "entities": entities,
        "facts": facts,
        "tensions": tensions,
        "portfolio": books,
        "charts": charts,
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "analysis.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return payload


def main() -> None:
    payload = analyze()
    c = payload["counts"]
    print(
        f"comments={c['comment_blocks']} speech_chars={c['speech_chars']} "
        f"facts={c['facts_found']}/{c['facts']} tensions={c['tensions']}"
    )
    print("speech density:", " · ".join(payload["density_leaders"]["speech"]))
    print("comment density:", " · ".join(payload["density_leaders"]["comments"]))
    print("pdf density:", " · ".join(payload["density_leaders"]["pdf"]))
    print("wrote", OUT_DIR / "analysis.json")


if __name__ == "__main__":
    main()
