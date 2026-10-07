#!/usr/bin/env python3
"""10/7 통합 증류: 정량 모델 + 유튜브 스크립트 + PDF Quick코멘트."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import oct7_model as model
import oct7_youtube as yt

OUT = Path("/workspace/output/oct7")


def render_integrated(m: dict, yt_md: str, yt_payload: dict) -> str:
    """정밀 모델 + 유튜브를 한 문서로."""
    base = model.render_precise_md(m)
    # Insert YouTube block before decision rules (section 7)
    marker = "## 7. 의사결정 규칙"
    yt_section = [
        "## 7. 유튜브/방송 스크립트 (빠졌던 레이어)",
        "",
        f"에피소드 {len(yt_payload['episodes'])}개 · 클레임 {len(yt_payload['claims'])}개 · 방송본문 ≈ {yt_payload['yt_chars']:,}자.",
        "",
        "### 7-A. 플러스클릭 「기억과 정신」 (핵심 추가분)",
        "",
    ]
    # Pull plusclick claims
    pc = [c for c in yt_payload["claims"] if c["episode"] == "ep6_plusclick"]
    for c in pc:
        yt_section.append(f"- **{c['theme']}** — {c['claim']}")
    yt_section += [
        "",
        "### 7-B. 장중/인터뷰가 숫자로 보탠 것",
        "",
        "| 항목 | 방송 숫자/주장 | 모델과의 연결 |",
        "|---|---|---|",
        "| 삼성 잠정 OP | ~105조 (101~117), ‘적게 봐도 100조’ | 실적 촉매 vs 수급이 선반영 |",
        "| 마이크론 GPM | 87% (85% 실망선 상회) | Bull 사이클·증설 가속 |",
        "| 9월 수출/흑자 | $1,200억 / $499억 | 금리 감내·세수 논거 |",
        "| 연못 고래 | 삼성~500조 + 닉스~300조 OP 서사 | GDP 대비 양극화 |",
        "| 외국인 | YTD −220조 | 할인율/수급 레이어 |",
        "| 피어할인 | 삼전닉스 ~−30% | 모델 −31%와 정합 |",
        "| SKH ADR | 전일 ≈−6%, 지지 후보 $165 | 밸류와 별개 테이프 |",
        "| 미 10년 | ≈5.27% ‘안정’ vs 메모리↓ | CapEx/금리 괴리 |",
        "| 전력 | 구글 원전 20년·3.6GW | 중간선거 전력 프레임 보강 |",
        "| 체크 | 10·20년물 입찰 > 잠정 숫자 | 의사결정 캘린더 |",
        "| 현대차 | 전선 미확정, 70만 매도 언급 | AI 바스켓과 분리 |",
        "| 오너루프 | 저커버그 글라스·에이전트 지속 | Muse/Agent 수요 질적 보강 |",
        "",
        "### 7-C. 에피소드 한 줄",
        "",
    ]
    for eid, ep in yt_payload["episodes"].items():
        yt_section.append(f"- `{eid}` {ep['title']} ({ep['chars']:,}자)")
    yt_section += [
        "",
        "> 상세 클레임 전체: `output/oct7/youtube_insights.md`",
        "",
        "## 8. 의사결정 규칙 (모델 + 방송 통합)",
        "",
        "1. CapEx: task×cost vs task×compute 분리 + **오너 CEO 루프가 꺼지지 않음**.",
        "2. Muse/Agent: 활성·used·sharing 민감도 + 메타 글라스/에이전트 디바이스 서사.",
        "3. CPU: $131~300B 밴드 (점추정 금지).",
        "4. 삼전닉스: 4.0x vs 할인 축소 + **수급(외인·프로그램)이 할인 유지 원인**.",
        "5. MU: Approach $1200~1371 / 방송 GPM 87%는 사이클 보강.",
        "6. 이번 주 캘린더: **미 장기물 입찰·하이퍼스케일러 회사채 > 삼성 잠정 서프라이즈**.",
        "7. 현대차·블루웨이브는 AI 코어와 분리. 추격 금지.",
        "8. PSK/EMIB·전력(원전 PPA)은 확산 체인 옵션.",
        "",
    ]
    if marker in base:
        head, _ = base.split(marker, 1)
        # drop old section 7 from base after split — we replace it
        return head.rstrip() + "\n\n" + "\n".join(yt_section)
    return base + "\n\n" + "\n".join(yt_section)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Persist quantitative model artifacts (model.json etc.)
    m = model.run_model()
    (OUT / "model.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    yt_result = yt.run()
    integrated = render_integrated(m, yt_result["md"], yt_result["meta"])
    (OUT / "투자인사이트.md").write_text(integrated, encoding="utf-8")
    (OUT / "chat_summary.md").write_text(integrated, encoding="utf-8")
    (OUT / "integrated_meta.json").write_text(
        json.dumps(
            {
                "model_thesis": m["thesis"],
                "yt_episodes": list(yt_result["meta"]["episodes"].keys()),
                "yt_claims": len(yt_result["meta"]["claims"]),
                "yt_chars": yt_result["meta"]["yt_chars"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(integrated)
    print(
        f"\n[integrated] model + yt_claims={len(yt_result['meta']['claims'])} "
        f"yt_chars={yt_result['meta']['yt_chars']:,} → {OUT / '투자인사이트.md'}"
    )


if __name__ == "__main__":
    main()
