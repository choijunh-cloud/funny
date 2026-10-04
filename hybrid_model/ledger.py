"""원장 1~7권에서 10/2까지 채점이 끝난 콜.

건수는 대시보드 막대와 같다. 1층·반증가능성은 종합 점수가 공개된 12명만 적었다.
박병창의 반증가능성 5는 문장으로만 있어서 종합 입력에는 넣지 않았다.
"""

from __future__ import annotations

from dataclasses import dataclass

from hybrid_model.scoring import MAIN_MIN_N, composite, hit_rate


@dataclass(frozen=True)
class Panel:
    name: str
    affiliation: str
    axis: str
    hits: int
    partials: int
    misses: int
    layer1: int | None = None
    falsifiability: int | None = None
    signature: str = ""
    frame: str = ""
    now_cast: str = ""
    falsify: str = ""

    @property
    def n(self) -> int:
        return self.hits + self.partials + self.misses

    @property
    def main(self) -> bool:
        return self.n >= MAIN_MIN_N


def _panel(
    name: str,
    affiliation: str,
    axis: str,
    hits: int,
    partials: int,
    misses: int,
    **kwargs: object,
) -> Panel:
    return Panel(name, affiliation, axis, hits, partials, misses, **kwargs)  # type: ignore[arg-type]


PANELS: tuple[Panel, ...] = (
    _panel("이영훈", "iM증권", "flow", 7, 1, 2, layer1=4, falsifiability=3,
           signature="수급 1층 관찰 최상급 · 순환매 요일 일지",
           frame="자사주 마중물 · 순환매 요일 일지 · 예탁금 이탈",
           now_cast="마중물 10/15 소진. 거래대금 25.9조(5월 대비 −60%)라 순환매 체력이 약하다.",
           falsify="거래대금 30조 회복"),
    _panel("이진호", "소장·차티스트", "level", 4, 1, 1, layer1=5, falsifiability=4,
           signature="수치 정밀 · 7,200 주봉 시한",
           frame="7,200 주봉 종가가 유일한 돌파 판정선",
           now_cast="7,004는 상단 존 바로 아래. 7,200 주봉이 판정선.",
           falsify="7,200 주봉 종가 안착"),
    _panel("황유현", "신한투자증권", "flow", 4, 2, 1, layer1=4, falsifiability=4,
           signature="수급 마이크로 정밀 · 되돌림 레벨",
           frame="50% 되돌림 7,324 · 하닉 200~214만 후 10월 중하순 전환",
           now_cast="하닉 184만(고점 대비 −10%)은 전환 국면. 10월 중하순 외인 복귀가 전략을 가른다.",
           falsify="하닉 200만 재돌파 · 외인 순매수"),
    _panel("박근형", "IBK투자증권", "macro", 7, 1, 3,
           signature="뉴스 소화 최상 · 결론 정확·라벨 오류형",
           frame="2회 인상 · 매물대 7,500~8,500 · 자사주 종료 우려",
           now_cast="12월 인상은 가격에 반영. 삼성 3Q 130~140조는 10/8에 채점하고, 110조대면 기각.",
           falsify="삼성 3Q 120조 이상"),
    _panel("이영수", "아신(HSL)", "semi", 4, 0, 2, layer1=5, falsifiability=3,
           signature="엔비디아·공급망 1층 상급 · P→Q 프레임",
           frame="P→Q · 하닉6:삼전4 · 연말~상반기 전고점 트라이",
           now_cast="마이크론 FQ1 $61.5B가 P→Q를 지지. 전고점은 B 시나리오 12월 밴드 밖.",
           falsify="4Q 서버 DRAM 계약가 QoQ 감속"),
    _panel("김장열", "유니스토리자산운용", "semi", 9, 1, 5,
           signature="메커니즘 설명 최고 · 수치 상단 편향 · 시점 오류",
           frame="28년까지 부족 · 피크아웃은 방향만 담는다",
           now_cast="9월 반도체 수출 $603억이 부족을 지지. 그가 말한 레벨은 상단으로 치우쳐 있다.",
           falsify="DRAMeXchange 4Q 고정가 QoQ 하락"),
    _panel("김민수", "", "flow", 5, 0, 3, signature="유동성 흡수 · 앤트로픽 IPO"),
    _panel("박명석", "", "macro", 5, 0, 3, signature="결론 정확 · 기전 오류형"),
    _panel("박병창", "MP파트너스", "level", 5, 1, 3,
           signature="규칙이 숫자 — 종가만으로 판정 가능",
           frame="7,100~7,500 분할매도 / 6,000~6,100 이탈 매도",
           now_cast="7,004는 상단 존 직전. 추격 금지, 상단 진입 시 분할매도.",
           falsify="7,200 주봉 종가 안착"),
    _panel("이은택", "", "frame", 3, 0, 3,
           signature="버블 붕괴 2조건 AND · 바닥 W형",
           frame="조건① 10Y 5.0~5.3 돌파 · 조건② 노웨이백",
           now_cast="조건①은 10Y 5.28에서 켜졌다. 조건②는 10/14 CPI와 10/28 FOMC.",
           falsify="9월 근원 CPI MoM 0.2 이하"),
    _panel("박세익", "", "frame", 3, 1, 4, signature="금리 임계 4.5%는 폐기, 1987 템플릿은 유효"),
    _panel("문홍철", "", "macro", 2, 2, 3, signature="4Q 금리 하락 콜은 기각"),
    _panel("이선엽", "", "semi", 2, 1, 5, signature="구두 수치는 버리고 덱만 취함"),
    _panel("문남중", "", "macro", 2, 1, 6, signature="연준 경로 5연속 기각 · 국내 사이클 타이밍만 잔존"),
    _panel("강건우", "더프레미어", "macro", 3, 1, 0, layer1=3, falsifiability=4,
           signature="PBR=할인율 · 4.7 알람벨 / 5.0 사이렌",
           frame="인상은 불확실성 해소 · 5.0 사이렌",
           now_cast="사이렌은 울렸으나 코스피는 7,000. 인상=해소는 B의 재료.",
           falsify="10Y 5.0% 하회"),
    _panel("박현상", "주머니투자자문", "level", 3, 1, 0, layer1=3, falsifiability=4,
           signature="레벨·수급 실전형",
           frame="7,500 박스 상단 · 자사주 종료 후 외인 복귀 전례",
           now_cast="전저점 6,300~6,400이 진행중. 외인 복귀는 공백론의 반증.",
           falsify="자사주 종료 후 외인 주간 순매수"),
    _panel("윤지호", "진행자·전략가", "flow", 3, 1, 0, layer1=4, falsifiability=3,
           signature="자사주 소진 자체 계산 유일 · 이익의 질",
           frame="하닉 자사주 소진 계산",
           now_cast="9/30 잔여 27% 서술과 그의 소진 계산이 맞닿아 있다. 10월 중순이 공백의 시작.",
           falsify="소진 이후에도 기타법인 매수가 이어짐"),
    _panel("김광석", "김광석TV", "macro", 3, 0, 1, layer1=4, falsifiability=3,
           signature="종합 점수에는 올라오나 잭슨홀 매파 콜은 기각"),
    _panel("박사주", "", "semi", 3, 0, 1, signature="반증 불가 명제는 제외 · 팩트 발굴만 채택"),
    _panel("김학균", "신영증권", "frame", 1, 1, 0, layer1=5, falsifiability=2,
           signature="환원=바닥 장치, 랠리 동력 아님",
           frame="주주환원은 바닥 장치이고 랠리의 동력이 아니다",
           now_cast="자사주가 걷히면 바닥은 실적과 외인이 대신해야 한다. 판정은 10/8과 10월 말.",
           falsify="자사주 종료 후 6,838 지지"),
    _panel("홍춘욱", "프리즘투자자문", "macro", 3, 1, 1, layer1=4, falsifiability=3,
           signature="금리 방향 유일 적중 · 매크로 1R 승자",
           frame="사상 최고가에서 인하는 없다 · 9,300은 요원",
           now_cast="10월 인상 확률은 낮아졌으나 12월 인상이 남아 인하 없음이 유지된다.",
           falsify="12월 인하 확률 등장"),
    _panel("한지영", "", "macro", 2, 1, 1, signature="레벨보다 속도"),
    _panel("이건규", "", "semi", 1, 3, 0, signature="FOMC 방향은 부분 적중"),
    _panel("알상무", "채권·FX 실무", "macro", 2, 2, 1, layer1=5, falsifiability=4,
           signature="자기 시장 1층 최상 · 연준 프레임 승자",
           frame="최종금리 3.5+ · 10월 조심 · 11~12월이 낫다",
           now_cast="3.75~4.00에 도달. 10월 조심 구간이고 저점 6,400~6,200은 C의 하단.",
           falsify="10월 중 7,200 돌파"),
    _panel("Quick 코멘트", "피드 채널", "flow", 2, 0, 2, layer1=5, falsifiability=4,
           signature="1층 사실 정확도가 종합 점수를 끌어올림"),
    _panel("이건희", "", "frame", 1, 1, 1, signature="5% 뉴노멀"),
    _panel("김중손", "", "macro", 2, 0, 3),
    _panel("김대호", "", "macro", 2, 0, 3, signature="결론 정확 · 기전 오류형"),
    _panel("빈센트", "", "semi", 0, 0, 2, signature="FIMA·9대2 기각 · DCA 규율만 잔존"),
)

OPEN_CALLS = 23
LEDGER_SPAN = "2026-08-06~2026-09-29"

AXIS_LABEL = {
    "macro": "매크로·금리",
    "flow": "수급",
    "level": "레벨·차트",
    "semi": "반도체 펀더멘털",
    "frame": "구조·리스크 프레임",
}


@dataclass(frozen=True)
class AxisNote:
    axis: str
    winners: tuple[str, ...]
    now: str
    falsify: str


AXES: tuple[AxisNote, ...] = (
    AxisNote(
        "macro",
        ("홍춘욱", "알상무", "강건우", "박근형"),
        "인하는 없고 9월 인상은 맞았다. 12월 인상 1회가 가격에 들어 있고 10Y는 5%대에 붙어 있다.",
        "10Y 5.0% 하회와 12월 인상 확률 50% 아래가 같이 나오면 프레임이 약해진다.",
    ),
    AxisNote(
        "flow",
        ("이영훈", "황유현", "윤지호", "김민수", "박현상"),
        "자사주가 외인·개인 매도를 흡수했다. 삼성 잔여 5%·하이닉스 잔여가 10월 중순에 걷히면 공백이 시작된다.",
        "자사주 종료 후 외인 주간 순매수로 바뀌면 공백론은 기각이다.",
    ),
    AxisNote(
        "level",
        ("박병창", "황유현", "박현상", "이진호"),
        "7,100~7,500은 세 번 거부됐다. 7,004는 그 바로 아래이고 판정선은 7,200 주봉이다.",
        "7,200 주봉 종가 안착이면 상단 규칙이 무효다.",
    ),
    AxisNote(
        "semi",
        ("김장열", "이영수", "박근형"),
        "삼전 28~29만과 하닉6:삼전4는 맞았다. 마이크론은 가이던스 상회 뒤 −3%라 호재 소진의 모양이다.",
        "4Q 계약가가 QoQ로 감속하면 피크아웃 프레임이 반증된다.",
    ),
    AxisNote(
        "frame",
        ("이은택", "김학균"),
        "조건①은 켜졌다. 환원은 바닥 장치였고, 그 장치가 10월 중순에 사라진다. 조건②는 10/14 CPI.",
        "9월 근원 CPI가 둔화하고 12월 인상 확률이 급락하면 2조건이 완성되지 않아 C를 줄인다.",
    ),
)


@dataclass(frozen=True)
class Discarded:
    name: str
    title: str
    reason: str


DISCARDED: tuple[Discarded, ...] = (
    Discarded("문남중", "연준 경로 콜", "잭슨홀·9월 동결·4Q 완화·2회 인하·고용 부호가 연속으로 기각. 국내 사이클 타이밍만 남긴다."),
    Discarded("박세익", "금리 임계 4.5%", "10Y 5.28에도 코스피는 7,000. 레벨론은 폐기하고 1987 템플릿과 점도표 분포만 남긴다."),
    Discarded("빈센트", "FIMA · 9대2", "잔액은 0, 표결은 12:0. DCA 규율만 취한다."),
    Discarded("이선엽", "구두 수치", "덱에 없는 문장은 버린다."),
    Discarded("김대호·박명석", "기전 설명", "결론은 맞고 기전은 틀렸다. 뉴스 소화만 쓰고 이유는 다시 조달한다."),
    Discarded("박사주", "반증 불가 명제", "반도체는 포기할 때 오른다는 문장은 채점에서 뺀다. 팩트 발굴만 남긴다."),
)


def validate_ledger(panels: tuple[Panel, ...] = PANELS) -> None:
    names = [panel.name for panel in panels]
    if len(names) != len(set(names)):
        raise ValueError("패널 이름이 겹친다")
    if len(panels) != 29:
        raise ValueError(f"패널은 29명이어야 한다: {len(panels)}")
    hits = partials = misses = 0
    for panel in panels:
        if panel.axis not in AXIS_LABEL:
            raise ValueError(panel.name)
        if min(panel.hits, panel.partials, panel.misses) < 0 or panel.n == 0:
            raise ValueError(panel.name)
        rate = hit_rate(panel.hits, panel.partials, panel.misses)
        composite(rate, panel.n, panel.layer1, panel.falsifiability)
        hits += panel.hits
        partials += panel.partials
        misses += panel.misses
    if (hits, partials, misses) != (93, 24, 60):
        raise ValueError(f"채점 합계가 93/24/60이 아니다: {hits, partials, misses}")
    if hits + partials + misses != 177:
        raise ValueError("채점 완료 콜이 177이 아니다")
