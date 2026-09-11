"""Extra ledger rows for the interactive-bot curriculum.

Imported together with sft/knowledge.py. New sentences stay here so the
original 274-sample ledger remains unchanged.
"""

from __future__ import annotations

import sys
from pathlib import Path

SFT = Path(__file__).resolve().parents[1] / "sft"
sys.path.insert(0, str(SFT))

from knowledge import FACTS as BASE_FACTS  # noqa: E402
from knowledge import Fact  # noqa: E402

DOMAIN_FACTS: tuple[Fact, ...] = (
    Fact(
        "bot.roles",
        "context",
        ("system", "rag"),
        "대화형 봇은 근거 검색 + 계산 도구 + 전문 문답 학습을 함께 쓴다. "
        "파일·버전·실행 수치는 검색으로 제공하고, 설명과 코드 검토 방식은 미세조정한다. "
        "실제 데이터나 도구 실행 결과가 없으면 수치를 만들지 않는다.",
        "The interactive bot combines retrieval, calculation tools, and specialist SFT. "
        "File/version/run figures come from search; explanation and code review from fine-tuning. "
        "Do not invent a number without data or a tool result.",
    ),
    Fact(
        "concept.receptor",
        "context",
        ("concept",),
        "같은 전달물질도 수용체에 따라 극성이 달라질 수 있다. "
        "이 모델은 뉴런당 부호 하나를 가정하므로, 수용체 의존성과 모델 가정을 구분해 설명해야 한다. "
        "곤충 중심 글루타메이트의 -1은 GluCl 가정이다.",
        "The same transmitter can flip polarity with the receptor. "
        "This model assumes one sign per neuron, so receptor dependence and the model assumption must be named separately. "
        "Insect central glutamate at -1 is a GluCl assumption.",
    ),
    Fact(
        "concept.assume",
        "context",
        ("concept",),
        "모델 가정: 데일(출력 NT 하나), 글루타메이트 억제, 모노아민 +1 빈, W[i,j]=i→j, I=W.T@x. "
        "가정은 실측 부호가 아니다.",
        "Model assumptions: Dale (one outgoing NT), inhibitory glutamate, monoamines in the +1 bin, W[i,j]=i→j, I=W.T@x. "
        "Assumptions are not measured per-synapse signs.",
    ),
    Fact(
        "code.dup_edge",
        "context",
        ("code_review",),
        "같은 (pre, post)가 두 행이면 시냅스 수를 합친 뒤 부호를 곱한다. "
        "행을 따로 W에 넣으면 마지막 값만 남거나 이중 계산이 된다.",
        "Duplicate (pre, post) rows must be summed on synapse count before signing. "
        "Writing them separately into W keeps only the last value or double-counts.",
    ),
    Fact(
        "code.lif_bugs",
        "context",
        ("code_review", "lif"),
        "LIF 구현 오류: 누수 없이 V+=I, 발화 후 리셋 없음, I=W@x, 글루타메이트 +1, "
        "unknown NT를 +1로 채움. 한 스텝은 V += (dt/tau)*(V_rest - V + I) 이다.",
        "LIF bugs: V+=I with no leak, no reset after spike, I=W@x, glutamate +1, "
        "filling unknown NT with +1. One step is V += (dt/tau)*(V_rest - V + I).",
    ),
    Fact(
        "calc.tool_only",
        "context",
        ("calculation", "evidence"),
        "부호화 입력 전류와 막전위 변화는 계산 도구로 확인한다. "
        "미니넷이나 실행 로그가 없으면 I나 ΔV 숫자를 쓰지 않고 거절한다.",
        "Encoded current and membrane change are checked with the calculation tool. "
        "Without a mini-net or a run log, refuse to write I or ΔV numbers.",
    ),
    Fact(
        "evidence.refuse",
        "context",
        ("evidence",),
        "근거 카드나 도구 결과가 없는 수치는 만들지 않는다. "
        "모르면 카드 id를 요청하거나 검색을 다시 한다.",
        "Do not invent a number that is not on an evidence card or a tool result. "
        "If unknown, ask for a card id or search again.",
    ),
)


def all_facts(*, include_inferred: bool) -> tuple[Fact, ...]:
    rows = BASE_FACTS + DOMAIN_FACTS
    if include_inferred:
        return rows
    return tuple(f for f in rows if f.prov == "context")


SYSTEM_KO = (
    "너는 곤충 CNS 커넥톰 조교다. "
    "파일·버전·실행 수치는 근거 카드를 검색해 인용하고, "
    "전류와 막전위는 계산 도구로만 구한다. "
    "곤충 글루타메이트는 -1(GluCl 가정)이며 +1로 단언하지 않는다. "
    "I = W.T @ x, NT는 pre에 조인한다. "
    "카드나 실행이 없으면 수치를 만들지 않는다."
)

SYSTEM_EN = (
    "You are an insect CNS connectome assistant. "
    "Cite file/version/run figures from retrieved evidence cards. "
    "Compute current and voltage only with tools. "
    "Insect glutamate is -1 (GluCl assumption); do not assert +1. "
    "I = W.T @ x; join NT on pre. "
    "Do not invent numbers without a card or a run."
)
