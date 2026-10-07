#!/usr/bin/env python3
"""10/7 PDF+paste → 투자 인사이트 증류 (핵심만)."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path("/workspace")
SRC = ROOT / "sources" / "oct7"
OUT = ROOT / "output" / "oct7"


@dataclass
class Claim:
    theme: str
    claim: str
    support: list[str] = field(default_factory=list)
    quality: str = "core"  # core | support | discard
    why: str = ""


def _read_extracted() -> dict[str, str]:
    texts: dict[str, str] = {}
    for p in sorted((SRC / "extracted").glob("*.txt")):
        texts[p.stem] = p.read_text(encoding="utf-8", errors="replace")
    paste = SRC / "paste_copy-2.txt"
    if paste.exists():
        texts["paste"] = paste.read_text(encoding="utf-8", errors="replace")
    return texts


def _has(blob: str, *needles: str) -> bool:
    return all(n in blob for n in needles)


def extract_claims(docs: dict[str, str]) -> list[Claim]:
    china = next((v for k, v in docs.items() if "AI" in k and "CoWoS" not in k and "CPU" not in k), "")
    # filenames are mangled; use content markers
    by_mark: dict[str, str] = {}
    for name, text in docs.items():
        if "토큰당 가격" in text or "중국 AI가 정말" in text:
            by_mark["china"] = text
        if "Muse Secure VM" in text or "MUSE에서 메모리는" in text or "8GB 할당" in text:
            by_mark["muse"] = text
        if "Sandisk" in text and "PER" in text:
            by_mark["val"] = text
        if "서버 CPU TAM" in text or "$300B" in text or "3000억달러" in text:
            by_mark["cpu"] = text
        if "피에스케이" in text or "EMIB" in text:
            by_mark["psk"] = text
        if "중간선거" in text or "affordability" in text:
            by_mark["midterm"] = text
        if name == "paste":
            by_mark["paste"] = text

    claims: list[Claim] = []

    # 1 China AI
    if "china" in by_mark:
        t = by_mark["china"]
        claims.append(
            Claim(
                "AI 경제성",
                "토큰 단가가 아니라 작업 완료 총비용(TCO)으로 봐야 한다.",
                ["중국 AI ‘저가’는 토큰 가격 기준", "작업 완료 비용에서는 미국 AI가 더 저렴할 수 있음"],
                "core",
                "단위 비교 프레임이 잘못되면 CapEx 판단이 틀어진다.",
            )
        )
        if "비약" in t:
            claims.append(
                Claim(
                    "AI CapEx",
                    "단위비용 하락 → AI CapEx 과도 는 비약.",
                    ["Agentic AI 사용량 폭증이 비용 하락을 상쇄할 수 있음", "사용량↑ ≠ 기업비용·CapEx 폭증"],
                    "core",
                    "약세 논리의 핵심 오류.",
                )
            )

    # 2 Muse
    if "muse" in by_mark:
        claims.append(
            Claim(
                "Agent 메모리",
                "Muse DRAM 수요는 8GB×N이 아니라 실제 평균 사용량×동시 활성 N.",
                ["할당 ~8GB / 관측 사용 ~3GB", "CPU는 oversubscribe 용이, DRAM은 working state 유지로 공유 어려움"],
                "core",
                "과대 추정과 과소 추정을 동시에 피한다.",
            )
        )
        claims.append(
            Claim(
                "Agent 메모리",
                "고도화 경로(3→8→16GB+)가 DRAM 업사이드 옵션.",
                ["현재 8GB/~3GB → 고도화 16GB/6~10GB → 복잡 Agent 32GB+/10~20GB+", "백그라운드 상시 작업 → SSD/NAND도 동반"],
                "core",
                "현재 실측과 미래 옵션을 분리.",
            )
        )

    # 3 Valuation
    if "val" in by_mark:
        t = by_mark["val"]
        nums = []
        if "7.2배" in t:
            nums.append("Sandisk FY27 PER 7.2x")
        if "6.3배" in t or "5.8배" in t:
            nums.append("Micron FY27 6.3x / CY27 5.8x")
        if "4.0배" in t:
            nums.append("SKH·삼성 본주 27Y PER 4.0x")
        claims.append(
            Claim(
                "메모리 밸류",
                "10/6 종가 기준 메모리 PER은 한 자리수(대략 4~7배).",
                nums or ["한 자리수 PER"],
                "core",
                "절대 레벨이 아직 ‘비싸다’ 구간이 아님.",
            )
        )
        if "−31%" in t or "-31%" in t or "할인율" in t:
            claims.append(
                Claim(
                    "메모리 밸류",
                    "삼전닉스 vs Micron 할인 ~31%(환율 조정 여지), 과거 −20~−50% 중간.",
                    ["ADR 프리미엄 37% → 30%/20%면 본주 202만/219만", "원화 강세 5~10% ≈ 주식 6~12% 하방"],
                    "support",
                    "할인·환율·ADR을 같이 봐야 함.",
                )
            )

    # 4 CPU
    if "cpu" in by_mark or "paste" in by_mark:
        claims.append(
            Claim(
                "CPU/Agentic",
                "Agentic AI는 GPU만이 아니라 CPU·DRAM·NAND로 AI CapEx 수혜를 확산.",
                ["Chatbot=질문→답변 / Agent=지속 orchestration·tool call", "AMD: CPU:GPU 1:4~8 → 1:1 가능"],
                "core",
                "투자 맵을 GPU 단일에서 인프라 체인으로 확장.",
            )
        )
        claims.append(
            Claim(
                "CPU/Agentic",
                "2030 서버 CPU TAM: 씨티 $300B(공격적) vs 미즈호 $209B — 방향 공유, 절대값 이견.",
                ["씨티 5월 $131.5B → 10월 $300B", "미즈호 Agentic CPU 비중 4%→30%, DRAM/NAND 비트 22~30%"],
                "core",
                "숫자를 믿기보다 확산 방향에 베팅 포인트를 둔다.",
            )
        )

    # 5 PSK
    if "psk" in by_mark:
        claims.append(
            Claim(
                "후공정",
                "PSK는 CoWoS/HBM/OSAT와 Intel EMIB의 교집합 — EMIB가 레벨업 옵션.",
                ["CoWoS/HBM=Reflow, OSAT=Descum, EMIB=둘 다", "한화 TP 27만, 이익전망이 TP 정당화 열쇠"],
                "core",
                "AI 패키징 CAPEX 확대의 직접 수혜 축.",
            )
        )

    # 6 Midterm
    if "midterm" in by_mark:
        claims.append(
            Claim(
                "정책/전력",
                "중간선거 에너지 본질은 반-DC가 아니라 전력 공급·affordability.",
                ["공화: 원전·가스·ESS / 민주: 신재생·원전+비용완화", "IRA 전면복원보다 보조금·세액공제 일부 수정 가능성"],
                "core",
                "전력 밸류체인 모멘텀은 선거 이후에도 이어질 가능성.",
            )
        )

    # Paste addons — only if they change the thesis
    paste = by_mark.get("paste", "")
    if "파업 승인" in paste or "파업승인" in paste:
        claims.append(
            Claim(
                "수급 이벤트",
                "Micron 대만 노조는 파업 ‘승인’ 단계 — 돌입·일정 확정 전 과잉 해석 주의.",
                ["99% 찬성, 이익 15% 분기 성과급 요구", "승인→일정→중단 3단계"],
                "support",
                "공급 타이트닝 옵션이지만 아직 실물이 아님.",
            )
        )
    if "3,000" in paste or "$3,000" in paste:
        claims.append(
            Claim(
                "밸류 앵커",
                "MU TP $3,000(19x)는 컨센($1,572)과 배수 괴리 — Approach는 컨센−20~30%($1,200~$1,371).",
                ["이익 추정보다 PER 가정이 차이", "안전마진 프레임"],
                "support",
                "공격적 TP를 앵커로 쓰지 말 것.",
            )
        )
    if "핀란드" in paste and "Constellation" in paste:
        claims.append(
            Claim(
                "전력/DC",
                "Google 핀란드 공사 중단은 수요 부족이 아니라 환경 인허가 — 미국은 3.59GW 전력 계약으로 반대 방향.",
                ["Muhos·Kajaani 일시 중단", "Constellation 원전 uprate 포함"],
                "support",
                "헤드라인을 CapEx 피크로 읽지 말 것.",
            )
        )

    return claims


def distill(claims: list[Claim]) -> dict:
    core = [c for c in claims if c.quality == "core"]
    support = [c for c in claims if c.quality == "support"]

    # One-line thesis from first-order cores
    thesis = (
        "Agentic AI는 ‘토큰 싸짐=CapEx 끝’이 아니라 CPU·메모리·후공정·전력으로 수요를 넓힌다. "
        "메모리 밸류는 아직 한 자리수 PER이고, 숫자의 절대값($300B 등)보다 확산 방향이 핵심이다."
    )

    # Scoreboard: theme → punch
    by_theme: dict[str, list[Claim]] = {}
    for c in core + support:
        by_theme.setdefault(c.theme, []).append(c)

    do_not = [
        "토큰 단가↓를 CapEx 피크로 연결하지 말 것",
        "Agent DRAM을 8GB×사용자수로 단순 곱하지 말 것",
        "씨티 $300B를 컨센서스처럼 쓰지 말 것 (방향만)",
        "Micron 파업승인을 생산차질로 바로 읽지 말 것",
        "Google 핀란드 중단을 AI 수요 둔화로 읽지 말 것",
        "MU TP $3,000(19x)를 밸류 앵커로 쓰지 말 것",
    ]

    checklist = [
        "TCO 프레임 유지하는가",
        "Agent 실제 DRAM(현재~3GB) vs 고도화 옵션 분리했는가",
        "메모리 PER·할인·환율을 같이 봤는가",
        "GPU→CPU→DRAM/NAND→후공정 체인으로 포트 질문을 던지는가",
        "전력/정책은 공급·affordability 프레임인가",
    ]

    return {
        "date": "2026-10-07",
        "thesis": thesis,
        "core": [asdict(c) for c in core],
        "support": [asdict(c) for c in support],
        "themes": {k: [asdict(x) for x in v] for k, v in by_theme.items()},
        "do_not": do_not,
        "checklist": checklist,
        "counts": {"core": len(core), "support": len(support), "docs": len(_read_extracted())},
    }


def render_md(data: dict) -> str:
    lines = [
        "# 10/7 투자 인사이트 증류",
        "",
        f"자료 {data['counts']['docs']}개 → 핵심 {data['counts']['core']} · 보강 {data['counts']['support']}. 매수·매도 권유 아님.",
        "",
        "## 한 줄",
        "",
        data["thesis"],
        "",
        "## 핵심 (Core)",
        "",
    ]
    for i, c in enumerate(data["core"], 1):
        lines.append(f"### {i}. [{c['theme']}] {c['claim']}")
        lines.append("")
        for s in c["support"]:
            lines.append(f"- {s}")
        if c["why"]:
            lines.append(f"- *왜:* {c['why']}")
        lines.append("")

    lines += ["## 보강 (Support)", ""]
    for c in data["support"]:
        lines.append(f"- **{c['theme']}** — {c['claim']}")
        if c["support"]:
            lines.append(f"  - " + " · ".join(c["support"][:3]))
    lines += ["", "## 하지 말 것", ""]
    for d in data["do_not"]:
        lines.append(f"- {d}")
    lines += ["", "## 체크", ""]
    for d in data["checklist"]:
        lines.append(f"- [ ] {d}")
    lines.append("")
    return "\n".join(lines)


def render_chat(data: dict) -> str:
    """채팅에 바로 붙일 짧은 버전."""
    bullets = []
    for c in data["core"]:
        bullets.append(f"**{c['theme']}** — {c['claim']}")
    support = " · ".join(f"{c['theme']}: {c['claim']}" for c in data["support"][:4])
    dont = "\n".join(f"- {d}" for d in data["do_not"][:5])
    return f"""## 한 줄
{data['thesis']}

## 핵심 {data['counts']['core']}
""" + "\n".join(f"{i}. {b}" for i, b in enumerate(bullets, 1)) + f"""

## 보강
{support}

## 하지 말 것
{dont}
"""


def main() -> None:
    docs = _read_extracted()
    if not docs:
        raise SystemExit("sources/oct7/extracted 없음")
    claims = extract_claims(docs)
    data = distill(claims)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "insights.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "투자인사이트.md").write_text(render_md(data), encoding="utf-8")
    chat = render_chat(data)
    (OUT / "chat_summary.md").write_text(chat, encoding="utf-8")
    print(chat)
    print(f"\n[wrote] {OUT / '투자인사이트.md'} | core={data['counts']['core']} support={data['counts']['support']}")


if __name__ == "__main__":
    main()
