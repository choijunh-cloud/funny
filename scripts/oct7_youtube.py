#!/usr/bin/env python3
"""paste_copy-2.txt → 유튜브/방송 에피소드 분할 + 투자 클레임 추출."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

SRC = Path("/workspace/sources/oct7/paste_copy-2.txt")
OUT = Path("/workspace/output/oct7")

EPISODES = [
    ("ep1_rate_strategy", "잘 잘 들리시죠?", "금리·수급 전략 라이브"),
    ("ep2_interview", "대표님 이번 주가 이제 월요일이 휴일이었어요", "인터뷰·삼전/하이닉스·MLCC"),
    ("ep3_monitor_open", "10월 7일 장 시작전 방송", "10/7 장전 모니터"),
    ("ep4_memory_lee", "오늘 메모리 주가 급락이 나와서", "메모리 급락 코멘트"),
    ("ep5_kospi_flow", "오늘 코스피 시장 코스닥 시장 약세 출발", "수급·프로그램·현대차"),
    ("ep6_plusclick", "플러스 클리의 호스트를 맡은 슈카", "플러스클릭·기억과정신"),
]


@dataclass
class YTClaim:
    episode: str
    theme: str
    claim: str
    evidence: list[str] = field(default_factory=list)
    weight: str = "high"  # high | medium | color


def strip_timestamps(chunk: str) -> str:
    lines = []
    for line in chunk.splitlines():
        s = line.strip()
        if not s:
            continue
        if re.fullmatch(r"\d{1,2}:\d{2}", s):
            continue
        if re.fullmatch(r"\d{1,2}:\d{2}:\d{2}", s):
            continue
        if re.fullmatch(r"\d+시간\s*\d+분\s*\d+초", s):
            continue
        if re.fullmatch(r"\d+분\s*\d+초", s) or re.fullmatch(r"\d+초", s):
            continue
        lines.append(s)
    return "\n".join(lines)


def split_episodes(text: str) -> dict[str, dict]:
    # Transcript starts near first spoken line after QC
    start = text.find("잘 잘 들리시죠?")
    if start < 0:
        start = text.find("1분 1초")
    yt = text[start:] if start >= 0 else text
    found: list[tuple[int, str, str, str]] = []
    for eid, marker, title in EPISODES:
        i = yt.find(marker)
        if i >= 0:
            found.append((i, eid, marker, title))
    found.sort()
    out: dict[str, dict] = {}
    for n, (i, eid, marker, title) in enumerate(found):
        j = found[n + 1][0] if n + 1 < len(found) else len(yt)
        plain = strip_timestamps(yt[i:j])
        out[eid] = {
            "id": eid,
            "title": title,
            "marker": marker,
            "chars": len(plain),
            "plain": plain,
        }
    return {
        "qc_chars": start if start >= 0 else 0,
        "yt_chars": len(yt),
        "episodes": out,
    }


def extract_claims(eps: dict[str, dict]) -> list[YTClaim]:
    c: list[YTClaim] = []
    p = {k: v["plain"] for k, v in eps.items()}

    # ── ep1 ──
    if "ep1_rate_strategy" in p:
        c += [
            YTClaim("ep1_rate_strategy", "금리", "미 10년 5%는 ‘시장 끝’ 레벨이 아니다(일관 메시지).", ["5% 공포 프레임 반박", "좋은 방향의 금리 하락 가능"], "high"),
            YTClaim("ep1_rate_strategy", "금리", "헤지펀드 미 국채 10년 공매도 잔고 약 204만 계약 — 숏커버 시 금리 하방 촉매.", ["204만 계약"], "high"),
            YTClaim("ep1_rate_strategy", "메모리", "메모리 쇼티지 서사: 삼성 쪽 28년까지, 씨티는 2031년까지 언급.", ["28년", "2031"], "high"),
            YTClaim("ep1_rate_strategy", "삼전 레벨", "삼성 단기 테스트 구간 약 26만 원대 시각.", ["26만"], "medium"),
            YTClaim("ep1_rate_strategy", "전력", "미국 전력 소비 사상 최고 국면 — 원전 부족 규모를 GW·기수로 언급(약 57GW/40기 맥락).", ["57기가", "원전"], "medium"),
            YTClaim("ep1_rate_strategy", "수급", "한국 거래대금 빈약 + 반도체 ETF 레버리지 잔여 효과.", ["거래가 없어요", "레버리지"], "medium"),
        ]

    # ── ep2 ──
    if "ep2_interview" in p:
        c += [
            YTClaim("ep2_interview", "수급", "외국인 연초 대비 약 220조 순매도 — 그래도 위로 갈 확률 70%+ 시각.", ["220조", "70%"], "high"),
            YTClaim("ep2_interview", "금리×AI", "하이퍼스케일러 조달(예: 오라클 15%) vs AWS 마진(~40%) — 금리 공포를 과대평가하지 말 것.", ["15%", "40%"], "high"),
            YTClaim("ep2_interview", "밸류", "삼전·하이닉스 글로벌 피어 대비 약 30% 디스카운트.", ["30%"], "high"),
            YTClaim("ep2_interview", "하이닉스", "약세 요인 후보: HBM4 노이즈 + 솔리다임 중복상장 가능성 — 본질 훼손인지 구분.", ["HBM4", "솔리다"], "high"),
            YTClaim("ep2_interview", "HBM 점유", "삼성 HBM4 회복 시 하이닉스 점유율 하락은 자연 시나리오(제로섬 우려).", ["HBM4", "점유율"], "medium"),
            YTClaim("ep2_interview", "전력", "구글–원전 20년 계약, 신규/업레이트 물량 2028 공급 프레임.", ["20년", "2028"], "high"),
            YTClaim("ep2_interview", "소부장", "삼성전기 MLCC 장기공급 공시(데이터센터향) + 세종 기판 투자/한미 장비.", ["MLCC", "기판", "데이터 센터"], "high"),
            YTClaim("ep2_interview", "밸류 타이밍", "엔비디아·TSMC처럼 삼전닉스도 27년에 밸류에이션 복귀·신고가 견인 역할 가능(펀더멘탈 뷰).", ["27년", "밸루에이션"], "high"),
            YTClaim("ep2_interview", "환율", "환율 변동 속도↑ — 1320원대 하단 언급 등, 정보유통·프로그램 매매 민감.", ["1320"], "medium"),
        ]

    # ── ep3 ──
    if "ep3_monitor_open" in p:
        c += [
            YTClaim("ep3_monitor_open", "테이프", "SKH ADR 전일 약 −6%, DRAM 관련 ETF 약 −3% → 국내 갭 하락 전제.", ["6%", "3%"], "high"),
            YTClaim("ep3_monitor_open", "전력", "구글–Constellation형 원전 PPA 20년·업레이트(신규 건설 10년+ vs 개조).", ["20년", "업레이트" if "업레이트" in p["ep3_monitor_open"] or "고쳐" in p["ep3_monitor_open"] else "원전"], "high"),
            YTClaim("ep3_monitor_open", "기대", "당일 SKH −2~3%, 삼성 −1~2% 내외 시나리오 제시(방송 가정치).", ["2, 3%", "1, 2%"], "medium"),
        ]

    # ── ep4 ──
    if "ep4_memory_lee" in p:
        c += [
            YTClaim("ep4_memory_lee", "매크로", "미 10년물 약 5.274%로 ‘안정’ 해석 vs 메모리 주가 괴리.", ["5.274"], "high"),
            YTClaim("ep4_memory_lee", "테이프", "EWY 약 −2.64%, SKH ADR 약 −6.4% — 지수↑·메모리↓ 짜증 장세.", ["2.64", "6.39"], "medium"),
            YTClaim("ep4_memory_lee", "전력", "3.6GW ≈ 원전 약 3기 규모로 체감.", ["3.6GW"], "medium"),
        ]

    # ── ep5 ──
    if "ep5_kospi_flow" in p:
        c += [
            YTClaim("ep5_kospi_flow", "실적", "삼성 ‘분기 영업이익 100조 시대’ 서사 — 잠정 전날 수급이 더 중요할 수 있음.", ["100조"], "high"),
            YTClaim("ep5_kospi_flow", "수급", "비차익·바스켓 매도 강화(수조 단위) — 합성/네이키드 매도 에너지.", ["3조", "비차익"], "high"),
            YTClaim("ep5_kospi_flow", "레벨", "삼성 27만 이탈 주시, 하이닉스 170만 테스트 언급.", ["27만", "170만"], "high"),
            YTClaim("ep5_kospi_flow", "테마", "블루웨이브/2차전지·재생 급등은 ‘올려놓고 파는’ 냄새 — 추격 금지.", ["블루웨이브", "2차전지"], "high"),
            YTClaim("ep5_kospi_flow", "현대차", "10/25~월말 결판 구간 시각. 고점(70만 언급) 매도 후 관망.", ["70만", "10월"], "high"),
            YTClaim("ep5_kospi_flow", "ADR", "SKH ADR 지지 후보 약 $165 언급.", ["165"], "medium"),
            YTClaim("ep5_kospi_flow", "원전/건설", "한국형 원전(APR1400) 레퍼런스·현대건설/삼성물산 시공 스토리.", ["APR", "현대 건설"], "medium"),
        ]

    # ── ep6 Plus Click ──
    if "ep6_plusclick" in p:
        t = p["ep6_plusclick"]
        c += [
            YTClaim(
                "ep6_plusclick",
                "기억과정신",
                "AI CapEx는 해킹/규제 이슈로 멈추지 않는다 — 오너 CEO(저커버그·머스크·베조스·세르게이 등)의 ‘기업가 정신’이 무한루프 투자를 지속.",
                ["기업가 정신", "메타", "오너"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "메타/에이전트",
                "메타: 메타버스 오판 인정→AI 피벗. 스마트글라스(~점유 80%)로 에이전트 밀착 디바이스·구독 락인.",
                ["스마트 글라스", "80%", "에이전트"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "오너 vs 월급CEO",
                "월급 CEO(애플·MS식)는 40년 만기 빅배팅 어려움 → AI 판은 오너 리그.",
                ["월급", "40년"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "금리×주식",
                "하이퍼스케일러가 돈을 가져가 금리↑인데 주식·채권이 안 깨짐 — ‘누가 먼저 무너지나’ 국면.",
                ["금리", "안 빠져"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "버블 프레임",
                "IT버블 비유는 ‘끝’이 아니라 ‘시작/아직 많이 남음’(과거 금리 7%대) 쪽 내러티브가 시장에 있음.",
                ["7%", "IT 버블"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "유동성",
                "국채 입찰 주저 — 메타/MS 회사채(7~8%)·앤트로픽 상장(11월)로 자금 이연.",
                ["7, 8%", "엔트로픽", "입찰"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "요금/락인",
                "닷컴과 달리 AI는 유료가 기본. OpenAI 고가 요금제($500) — 락인 후 가격 전가 여지.",
                ["500불", "유료"],
                "medium",
            ),
            YTClaim(
                "ep6_plusclick",
                "삼성실적",
                "10/8 잠정: 컨센 밴드 대략 101~117조, 무게중심 ~105조. ‘적게 봐도 100조’.",
                ["105조", "100조", "10월 8일"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "마이크론",
                "GPM 87%(85% 이하면 실망 기준을 상회). 내년·내후년 수요↑, 물량 70%+ 계약, 증설 가속.",
                ["87%", "70%"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "수출",
                "9월 수출 약 $1,200억 / 무역흑자 약 $499억 — ‘한 달 70조’급 유입 체감 → 금리↑도 감내 논거.",
                ["1,200억", "499억"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "연못고래",
                "삼성 OP ~500조 + 하이닉스 ~300조 전망이 겹치면 GDP(~2,700조) 대비 ‘연못에 고래 두 마리’ → AI/비AI 양극화 심화.",
                ["500조", "300조", "2,700조"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "체크포인트",
                "이번 주 핵심은 삼성 잠정보다 미 장기물(10·20년) 입찰 + 하이퍼스케일러 회사채 뉴스.",
                ["10년물", "20년물", "채권 발행"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "현대차",
                "AI와 달리 자동차는 전선 미확정(중국 EV 다수·독일차·도요타). 수출 2위 자리도 흔들림. 불확실성↑.",
                ["전선", "테슬라", "모델 Y"],
                "high",
            ),
            YTClaim(
                "ep6_plusclick",
                "포지션톤",
                "박정호=기억과정신 강세 / 알상무=강세+금리(채권) 숏 — ‘금리↑·주식↑ 동행’ 시나리오.",
                ["강세론자", "채권 숏"],
                "medium",
            ),
        ]

    # only keep claims whose evidence tokens mostly appear (soft filter)
    kept = []
    for cl in c:
        blob = p.get(cl.episode, "")
        hits = sum(1 for e in cl.evidence if e.replace(",", "") in blob.replace(",", "") or e in blob)
        if hits >= max(1, len(cl.evidence) // 2) or cl.weight == "high":
            kept.append(cl)
    return kept


def render_youtube_md(meta: dict, claims: list[YTClaim]) -> str:
    lines = [
        "# 유튜브/방송 스크립트 증류 (paste)",
        "",
        f"Quick코멘트 앞단 ≈ {meta['qc_chars']:,}자 · 방송 본문 ≈ {meta['yt_chars']:,}자 · 에피소드 {len(meta['episodes'])}개 · 클레임 {len(claims)}개.",
        "",
        "## 에피소드 맵",
        "",
        "| ID | 제목 | 분량(자) |",
        "|---|---|---:|",
    ]
    for eid, ep in meta["episodes"].items():
        lines.append(f"| `{eid}` | {ep['title']} | {ep['chars']:,} |")

    lines += ["", "## 에피소드별 핵심", ""]
    by_ep: dict[str, list[YTClaim]] = {}
    for cl in claims:
        by_ep.setdefault(cl.episode, []).append(cl)

    titles = {k: v["title"] for k, v in meta["episodes"].items()}
    for eid in meta["episodes"]:
        lines.append(f"### {titles[eid]} (`{eid}`)")
        lines.append("")
        for cl in by_ep.get(eid, []):
            ev = ", ".join(cl.evidence[:4])
            lines.append(f"- **[{cl.theme}]** {cl.claim}")
            if ev:
                lines.append(f"  - 근거키: {ev}")
        lines.append("")

    lines += [
        "## 방송이 PDF 모델에 더하는 것",
        "",
        "1. **금리 5% 공포 ≠ 사이클 종료** — 숏커버·입찰·회사채 대체가 변수.",
        "2. **오너 CEO 루프** — 해킹/규제로는 CapEx가 안 꺾인다는 질적 보강(정량 CapEx 역설과 정합).",
        "3. **삼전 100조·수출 $1,200억** — 실적/실물 숫자로 ‘금리 감내’ 논거.",
        "4. **수급** — 외국인 220조, 프로그램/바스켓 매도가 밸류 할인의 단기 원인.",
        "5. **현대차** — AI와 다른 불확실성(전선 미확정). 포트에서 AI와 분리.",
        "6. **체크** — 잠정보다 **미 장기물 입찰 + 하이퍼스케일러 채권**.",
        "",
    ]
    return "\n".join(lines)


def run() -> dict:
    text = SRC.read_text(encoding="utf-8", errors="replace")
    meta = split_episodes(text)
    # drop plain from saved json (too large) — keep on disk per episode
    OUT.mkdir(parents=True, exist_ok=True)
    yt_dir = OUT / "youtube"
    yt_dir.mkdir(exist_ok=True)
    slim_eps = {}
    for eid, ep in meta["episodes"].items():
        (yt_dir / f"{eid}.txt").write_text(ep["plain"], encoding="utf-8")
        slim_eps[eid] = {k: v for k, v in ep.items() if k != "plain"}
    claims = extract_claims(meta["episodes"])
    payload = {
        "qc_chars": meta["qc_chars"],
        "yt_chars": meta["yt_chars"],
        "episodes": slim_eps,
        "claims": [asdict(c) for c in claims],
    }
    (OUT / "youtube_insights.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md = render_youtube_md({"qc_chars": meta["qc_chars"], "yt_chars": meta["yt_chars"], "episodes": slim_eps}, claims)
    (OUT / "youtube_insights.md").write_text(md, encoding="utf-8")
    return {"meta": payload, "claims": claims, "md": md}


if __name__ == "__main__":
    r = run()
    print(r["md"])
    print(f"[yt] episodes={len(r['meta']['episodes'])} claims={len(r['claims'])}")
