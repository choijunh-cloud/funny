"""Connectome LIF SFT — single knowledge ledger.

Every teachable sentence in the dataset is assembled from this file.
Facts are tagged ``prov="context"`` (sign table + pipeline code) or
``prov="inferred"`` (four judgements not stated in that source material).

``build_sft.py --include-inferred`` is required to emit the four inferred
facts. Without the flag the generator only uses ``context`` rows.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal

Prov = Literal["context", "inferred"]


@dataclass(frozen=True)
class Fact:
    id: str
    prov: Prov
    tags: tuple[str, ...]
    ko: str
    en: str


# ---------------------------------------------------------------------------
# Insect CNS signed-weight table (modeling convention: Shiu / FlyWire LIF)
# W[i, j] = signed synapse count from i → j
# I = W.T @ x
# ---------------------------------------------------------------------------

INSECT_SIGN: dict[str, int] = {
    "acetylcholine": 1,
    "glutamate": -1,
    "gaba": -1,
    "serotonin": 1,
    "dopamine": 1,
    "octopamine": 1,
    "histamine": -1,
}

NT_ALIASES: dict[str, str] = {
    "acetylcholine": "acetylcholine",
    "ach": "acetylcholine",
    "acha": "acetylcholine",
    "아세틸콜린": "acetylcholine",
    "glutamate": "glutamate",
    "glu": "glutamate",
    "glut": "glutamate",
    "글루타메이트": "glutamate",
    "gaba": "gaba",
    "가바": "gaba",
    "serotonin": "serotonin",
    "5-ht": "serotonin",
    "5ht": "serotonin",
    "세로토닌": "serotonin",
    "dopamine": "dopamine",
    "da": "dopamine",
    "도파민": "dopamine",
    "octopamine": "octopamine",
    "oa": "octopamine",
    "옥토파민": "octopamine",
    "histamine": "histamine",
    "ha": "histamine",
    "히스타민": "histamine",
}

# Vertebrate *sign* column (textbook polarity). Receptor subtype prose is inferred.
VERTEBRATE_SIGN: dict[str, str] = {
    "acetylcholine": "+1 at NMJ (nicotinic); mixed muscarinic in CNS",
    "glutamate": "+1 (AMPA/NMDA excitatory)",
    "gaba": "-1 (GABA_A/B inhibitory)",
    "serotonin": "mixed / neuromodulatory",
    "dopamine": "mixed / neuromodulatory (D1/D2)",
    "octopamine": "absent (norepinephrine is the analogue)",
    "histamine": "mostly neuromodulatory (no HisCl default)",
}


PIPELINE_STEPS: tuple[str, ...] = (
    "① 에지 로드: bodyId_pre, bodyId_post, weight",
    "② pre 뉴런에 NT 조인 (데일: 출력 NT는 pre의 속성)",
    "③ NT → insect sign 매핑",
    "④ signed_weight = weight * sign  (한 뉴런의 모든 출력에 같은 부호)",
    "⑤ 필터: weight >= 5 AND sign.notna()  (OR 아님, |signed_weight| 아님)",
    "⑥ 행렬 W[i,j] = i→j signed_weight (행=pre, 열=post)",
    "⑦ 입력 전류 I = W.T @ x",
)


REFERENCE_CODE = '''
def signed_edgelist(edges, nt_of_pre, sign=INSECT_SIGN, min_weight=5):
    """Join NT on *pre*, apply Dale's one-sign-per-neuron rule, filter."""
    rows = []
    for pre, post, weight in edges:
        nt = nt_of_pre.get(pre)
        if nt is None or nt not in sign:
            continue
        if weight < min_weight:  # synapse count, not |signed_weight|
            continue
        rows.append((pre, post, weight, nt, weight * sign[nt]))
    return rows


def current_WTx(neurons, signed_rows, x):
    """W[i,j] = i→j signed weight; I = W.T @ x."""
    idx = {n: i for i, n in enumerate(neurons)}
    n = len(neurons)
    W = np.zeros((n, n))
    for pre, post, _w, _nt, sw in signed_rows:
        W[idx[pre], idx[post]] = sw
    return W, W.T @ np.asarray(x, dtype=float)
'''.strip()


FACTS: tuple[Fact, ...] = (
    Fact(
        "sys.role",
        "context",
        ("system",),
        "너는 초파리/곤충 CNS 커넥톰의 부호 가중 그래프와 LIF 입력 전류를 푸는 조교다. "
        "곤충 CNS에서 글루타메이트는 -1(억제, GluCl)이며 +1이라고 단언하지 않는다. "
        "아세틸콜린이 주된 흥분성(+1) 전달물질이다. "
        "데일의 원리로 NT는 시냅스 전(pre) 뉴런에 조인하고, 그 뉴런의 모든 출력에 같은 부호를 곱한다. "
        "W[i,j]는 i→j 부호 가중치이고 전류는 I = W.T @ x 이다. "
        "시냅스 수 필터는 weight >= 5 이며 |signed_weight|나 OR 결합이 아니다.",
        "You are a teaching assistant for insect/Drosophila CNS signed-weight graphs and LIF current. "
        "In the insect CNS glutamate is -1 (inhibitory, GluCl); do not assert it is +1. "
        "Acetylcholine is the primary excitatory (+1) transmitter. "
        "By Dale's principle, join NT on the presynaptic neuron and apply that sign to every outgoing edge. "
        "W[i,j] is the i→j signed weight and current is I = W.T @ x. "
        "The synapse-count filter is weight >= 5, not |signed_weight| and not an OR-combination.",
    ),
    Fact(
        "sign.ach",
        "context",
        ("sign", "lookup", "insect"),
        "곤충 CNS에서 아세틸콜린(acetylcholine, ACh)의 모델링 부호는 +1(흥분)이다. 초파리 뇌에서 주된 흥분성 전달물질이다.",
        "In the insect CNS the modeling sign of acetylcholine (ACh) is +1 (excitatory). It is the primary excitatory transmitter in the fly brain.",
    ),
    Fact(
        "sign.glu",
        "context",
        ("sign", "lookup", "insect", "glu"),
        "곤충 CNS에서 글루타메이트(glutamate, Glu)의 모델링 부호는 -1(억제)이다. 중심 시냅스에서는 GluCl(글루타메이트 개폐 염소 채널)을 통해 억제로 취급한다. 척추동물의 +1(흥분)과 반대이므로 +1로 단언하면 안 된다.",
        "In the insect CNS the modeling sign of glutamate (Glu) is -1 (inhibitory). Central synapses are treated as inhibitory via GluCl. This is the opposite of vertebrate +1; do not assert glutamate is +1.",
    ),
    Fact(
        "sign.gaba",
        "context",
        ("sign", "lookup", "insect"),
        "곤충 CNS에서 GABA의 모델링 부호는 -1(억제)이다.",
        "In the insect CNS the modeling sign of GABA is -1 (inhibitory).",
    ),
    Fact(
        "sign.ser",
        "context",
        ("sign", "lookup", "insect"),
        "곤충 CNS 부호표에서 세로토닌(serotonin, 5-HT)의 모델링 부호는 +1이다 (FlyWire LIF 관례: 모노아민을 흥분 범주로 둔다).",
        "In the insect CNS sign table serotonin (5-HT) is modeled as +1 (FlyWire LIF convention: monoamines in the excitatory bin).",
    ),
    Fact(
        "sign.da",
        "context",
        ("sign", "lookup", "insect"),
        "곤충 CNS 부호표에서 도파민(dopamine, DA)의 모델링 부호는 +1이다.",
        "In the insect CNS sign table dopamine (DA) is modeled as +1.",
    ),
    Fact(
        "sign.oa",
        "context",
        ("sign", "lookup", "insect"),
        "곤충 CNS 부호표에서 옥토파민(octopamine, OA)의 모델링 부호는 +1이다. 척추동물의 노르에피네프린에 대응하는 곤충 모노아민이다.",
        "In the insect CNS sign table octopamine (OA) is modeled as +1. It is the insect analogue of vertebrate norepinephrine.",
    ),
    Fact(
        "sign.ha",
        "context",
        ("sign", "lookup", "insect"),
        "곤충 CNS에서 히스타민(histamine, HA)의 모델링 부호는 -1이다. 광수용 경로의 HisCl이 억제성이다.",
        "In the insect CNS histamine (HA) is modeled as -1. Photoreceptor HisCl channels are inhibitory.",
    ),
    Fact(
        "vert.ach",
        "context",
        ("sign", "lookup", "vertebrate", "contrast"),
        "척추동물 참고 컬럼에서 아세틸콜린은 신경근 접합(니코틴)에서 +1(흥분)이고, CNS 무스카린 수용체는 혼합이다.",
        "In the vertebrate reference column acetylcholine is +1 at the neuromuscular junction (nicotinic); muscarinic CNS actions are mixed.",
    ),
    Fact(
        "vert.glu",
        "context",
        ("sign", "lookup", "vertebrate", "contrast", "glu"),
        "척추동물 참고 컬럼에서 글루타메이트는 +1(흥분, AMPA/NMDA)이다. 이 +1은 척추동물 컬럼의 값이며 곤충 CNS 부호가 아니다.",
        "In the vertebrate reference column glutamate is +1 (excitatory, AMPA/NMDA). That +1 belongs to the vertebrate column, not the insect CNS sign.",
    ),
    Fact(
        "vert.gaba",
        "context",
        ("sign", "lookup", "vertebrate", "contrast"),
        "척추동물 참고 컬럼에서 GABA는 -1(억제)로 곤충과 같다.",
        "In the vertebrate reference column GABA is -1 (inhibitory), same polarity as in insects.",
    ),
    Fact(
        "vert.oa",
        "context",
        ("sign", "lookup", "vertebrate", "contrast"),
        "척추동물에는 옥토파민이 없고 노르에피네프린이 대응 모노아민이다.",
        "Vertebrates lack octopamine; norepinephrine is the corresponding monoamine.",
    ),
    Fact(
        "vert.ha",
        "context",
        ("sign", "lookup", "vertebrate", "contrast"),
        "척추동물 참고 컬럼에서 히스타민 부호는 기본 억제(HisCl)가 아니라 주로 변조로 적는다.",
        "In the vertebrate reference column histamine is listed as mostly neuromodulatory, not as a default HisCl inhibition.",
    ),
    Fact(
        "pipe.steps",
        "context",
        ("pipeline", "concept"),
        "부호 가중 파이프라인은 일곱 단계다. "
        + " / ".join(PIPELINE_STEPS),
        "The signed-weight pipeline has seven steps: "
        "(1) load edges bodyId_pre, bodyId_post, weight; "
        "(2) join NT on the pre neuron; "
        "(3) map NT to insect sign; "
        "(4) signed_weight = weight * sign; "
        "(5) filter weight >= 5 AND sign.notna(); "
        "(6) W[i,j] = i→j signed weight; "
        "(7) I = W.T @ x.",
    ),
    Fact(
        "pipe.join_pre",
        "context",
        ("pipeline", "debug", "dale", "concept"),
        "NT 테이블은 bodyId_pre(시냅스 전 뉴런)에 조인한다. post에 조인하면 받는 쪽의 전달물질을 보내는 쪽 부호로 쓰게 되어 부호가 뒤집힌다.",
        "Join the NT table on bodyId_pre (the presynaptic neuron). Joining on post assigns the receiver's transmitter to the sender's sign and flips polarity.",
    ),
    Fact(
        "pipe.signed",
        "context",
        ("pipeline", "concept"),
        "signed_weight = weight * sign 이다. weight는 시냅스 개수(항상 양수)이고 sign만 +1 또는 -1이다.",
        "signed_weight = weight * sign. weight is a synapse count (always positive); only sign is +1 or -1.",
    ),
    Fact(
        "pipe.filter",
        "context",
        ("pipeline", "debug", "concept"),
        "필터는 시냅스 수 weight >= 5 와 부호 존재(sign.notna())를 AND 로 결합한다. "
        "OR로 묶으면 약한 연결이나 NT 없는 에지가 남는다. "
        "|signed_weight| >= 5 로 바꾸면 결과는 같아 보여도, signed_weight >= 5 로 쓰면 억제(-) 에지가 전부 탈락한다.",
        "Filter with synapse count weight >= 5 AND sign.notna(). "
        "OR keeps weak or unsigned edges. "
        "|signed_weight| >= 5 looks similar, but signed_weight >= 5 drops every inhibitory edge.",
    ),
    Fact(
        "pipe.WTx",
        "context",
        ("pipeline", "debug", "concept", "numeric"),
        "W[i,j]를 i→j 부호 가중치로 두면 각 뉴런이 받는 전류는 I = W.T @ x 이다. "
        "전치를 빼면 I = W @ x 가 되어 전류가 나가는 쪽 축으로 계산된다.",
        "If W[i,j] is the i→j signed weight, the current each neuron receives is I = W.T @ x. "
        "Dropping the transpose computes W @ x and puts current on the outgoing axis.",
    ),
    Fact(
        "pipe.inner",
        "context",
        ("pipeline", "debug", "concept"),
        "NT를 inner join 하면 전달물질이 없는 pre 뉴런의 에지가 삭제된다. "
        "left join 후 sign.notna()로 걸러야 누락을 셀 수 있다. unknown NT를 +1로 채우면 안 된다.",
        "An inner join on NT deletes edges whose pre neuron has no transmitter. "
        "Left-join then filter sign.notna() so the drop is visible. Do not fill unknown NT with +1.",
    ),
    Fact(
        "pipe.columns",
        "context",
        ("pipeline", "concept"),
        "Male CNS v1.0 Feather 가중치 컬럼은 body_pre, body_post, weight 이고, "
        "신경전달물질 테이블은 body / consensus_nt 이다. "
        "요청 코드의 bodyId_pre / bodyId_post 로 바꿔 조인한다.",
        "Male CNS v1.0 Feather weight columns are body_pre, body_post, weight, "
        "and the transmitter table uses body / consensus_nt. "
        "Rename to bodyId_pre / bodyId_post before joining.",
    ),
    Fact(
        "pipe.min_w",
        "context",
        ("pipeline", "concept"),
        "노이즈 제거 임계값은 시냅스 수 5개다 (weight >= 5). 원본 Feather는 1.5억 에지 중 약 62%가 weight=1 이다.",
        "The noise threshold is 5 synapses (weight >= 5). About 62% of the raw Feather edges have weight=1.",
    ),
    Fact(
        "pipe.mode",
        "context",
        ("pipeline", "concept", "pandas"),
        "뉴런 단위 NT는 시냅스별 예측의 다수결로 고른다. pandas에서는 그룹마다 Series.mode()를 쓴다.",
        "Per-neuron NT is the majority vote of synapse-level predictions. In pandas that is Series.mode() per group.",
    ),
    Fact(
        "dale.one_nt",
        "context",
        ("dale", "concept"),
        "데일의 원리(근사): 한 뉴런은 하나의 빠른 전달물질을 모든 출력 시냅스에 쓴다. "
        "그래서 부호는 에지가 아니라 pre 뉴런의 속성이다.",
        "Dale's principle (approximation): a neuron uses one fast transmitter at every outgoing synapse. "
        "Sign is therefore a property of the pre neuron, not of each edge independently.",
    ),
    Fact(
        "debug.glu_plus",
        "context",
        ("debug", "glu"),
        "가장 위험한 버그는 곤충 글루타메이트를 +1로 단언하는 것이다. "
        "정답 부호는 -1 이고, 척추동물 컬럼의 +1과 섞으면 회로 극성이 붕괴한다.",
        "The most dangerous bug is asserting insect glutamate is +1. "
        "The correct insect sign is -1; mixing it with the vertebrate +1 collapses circuit polarity.",
    ),
    Fact(
        "code.lif",
        "context",
        ("codegen", "pipeline"),
        "기준 구현은 pre 조인, weight>=5 AND sign.notna() 필터, signed_weight=weight*sign, "
        "W[i,j]=i→j, I=W.T@x 이다. 글루타메이트 항목은 INSECT_SIGN['glutamate'] == -1 이어야 한다.",
        "The reference implementation joins NT on pre, filters weight>=5 AND sign.notna(), "
        "sets signed_weight=weight*sign, builds W[i,j]=i→j, and returns I=W.T@x. "
        "INSECT_SIGN['glutamate'] must be -1.",
    ),
    # ---- inferred (exactly four) ----
    Fact(
        "inf.mode_tie",
        "inferred",
        ("pandas", "debug"),
        "pandas Series.mode()는 동률인 최빈값을 모두 돌려주고, mode()[0]은 그 중 정렬 첫 값이다. "
        "문자열 NT에서는 알파벳순 편향이 생긴다 (예: gaba 와 glutamate 가 동률이면 gaba).",
        "pandas Series.mode() returns every tied mode, and mode()[0] is the first in sorted order. "
        "For string NT names that is an alphabetical bias (e.g. gaba beats glutamate on a tie).",
    ),
    Fact(
        "inf.mode_nan",
        "inferred",
        ("pandas", "debug"),
        "그룹의 값이 전부 NaN 이면 mode()는 빈 Series를 돌려서 mode()[0]이 IndexError 를 낸다. "
        "조인 전에 빈 그룹을 가드해야 한다.",
        "If every value in a group is NaN, mode() is an empty Series and mode()[0] raises IndexError. "
        "Guard empty groups before taking [0].",
    ),
    Fact(
        "inf.dale_stages",
        "inferred",
        ("dale", "concept"),
        "일곱 단계 파이프라인에서 데일의 원리가 직접 대응하는 단계는 ②(pre에 NT 조인)와 "
        "④(그 부호를 해당 뉴런의 모든 출력 가중치에 곱함)이다.",
        "In the seven-step pipeline Dale's principle maps onto step ② (join NT on pre) and "
        "step ④ (multiply that sign onto every outgoing weight of the neuron).",
    ),
    Fact(
        "inf.vert_receptors",
        "inferred",
        ("vertebrate", "contrast"),
        "척추동물 참고 컬럼의 세부 수용체: 세로토닌의 이온성 흥분은 5-HT₃, "
        "히스타민은 H1~H4 대사성 수용체로 적는다. 부호 칸 자체(혼합/변조)는 문맥 그대로다.",
        "Vertebrate reference-column receptor detail: ionotropic excitatory serotonin is 5-HT3; "
        "histamine is written as H1–H4 metabotropic receptors. The sign cells themselves stay mixed/modulatory.",
    ),
)


SYSTEM_PROMPT_KO = next(f.ko for f in FACTS if f.id == "sys.role")
SYSTEM_PROMPT_EN = next(f.en for f in FACTS if f.id == "sys.role")


def facts(*, include_inferred: bool) -> tuple[Fact, ...]:
    if include_inferred:
        return FACTS
    return tuple(f for f in FACTS if f.prov == "context")


def fact_map(*, include_inferred: bool) -> dict[str, Fact]:
    return {f.id: f for f in facts(include_inferred=include_inferred)}


def facts_with_tag(tag: str, *, include_inferred: bool) -> tuple[Fact, ...]:
    return tuple(f for f in facts(include_inferred=include_inferred) if tag in f.tags)


def canonical_nt(name: str) -> str:
    key = name.strip().lower()
    if key not in NT_ALIASES:
        raise KeyError(f"unknown NT alias: {name}")
    return NT_ALIASES[key]


def insect_sign(name: str) -> int:
    return INSECT_SIGN[canonical_nt(name)]


def inferred_ids() -> tuple[str, ...]:
    return tuple(f.id for f in FACTS if f.prov == "inferred")


def all_fact_ids(ids: Iterable[str], *, include_inferred: bool) -> bool:
    allowed = set(fact_map(include_inferred=include_inferred))
    return all(i in allowed for i in ids)
