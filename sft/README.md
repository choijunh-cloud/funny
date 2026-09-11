# Connectome LIF SFT (chat JSONL)

범용 chat JSONL (`system` / `user` / `assistant`) 274개 — train 246 / val 28.

```
knowledge.py   지식 원장 (교과서)
build_sft.py   그 교과서로만 문제를 내는 출제위원
verify_sft.py  답안을 자기 손으로 다시 푸는 채점관
data/          train.jsonl, val.jsonl
```

출제위원이 교과서 밖 문장을 못 내게 막아 둔 것이 환각 방지의 본체다.

## 설계

1. **학습 문장은 `knowledge.py`에서만 나온다.**  
   모든 팩트에 `prov="context"`(부호표·파이프라인 코드) 또는 `prov="inferred"`(원장 밖 판단 4건)가 있다.  
   `--include-inferred`를 빼면 문맥에 적힌 것만으로 데이터셋이 만들어진다.

2. **무게중심은 `numeric` 150개(55%).**  
   3–6개 뉴런 미니 네트워크 → signed_weight 표, 필터 후 ±개수, `I = Wᵀx`.  
   정답은 numpy로 산출하고, `verify_sft.py`가 밀집 행렬 `W.T @ x`로 **독립 재검산**한다.

3. **글루타메이트 +1 단언 금지.**  
   검증기에 곤충/초파리 문맥에서 글루타메이트를 +1·흥분으로 단언하는 문장 탐지 정규식이 있다.  
   척추동물 참고 컬럼의 +1(AMPA/NMDA)은 허용한다. 이 데이터셋이 봇에 심어야 할 가장 중요한 한 가지가 그 부호다.

### inferred 4건

문맥에 없던 판단이라 README에 명시한다. 맞다고 보지만 원문에는 없었다.

| id | 내용 |
| --- | --- |
| `inf.mode_tie` | pandas `mode()[0]` 동률 시 정렬 첫 값 → 문자열 NT는 알파벳순 편향 (`gaba` < `glutamate`) |
| `inf.mode_nan` | 전부 NaN 그룹에서 `mode()[0]` → `IndexError` |
| `inf.dale_stages` | 데일의 원리가 파이프라인 ②(pre 조인)·④(모든 출력에 같은 부호)에 대응 |
| `inf.vert_receptors` | 척추동물 참고 컬럼의 세부 서술(5-HT₃, H1–H4). 부호 칸 자체는 문맥 그대로 |

### 과제 구성 (274)

| task | n | 내용 |
| --- | --- | --- |
| numeric | 150 | 미니넷 signed_weight / ±개수 / Wᵀx |
| lookup | 62 | 부호 조회 (영어 포함) |
| concept | 28 | 데일, 필터, 전치, 컬럼명 |
| debug | 14 | post 조인·전치 누락·Glu +1·inner join·OR 필터·\|w\| 필터 등 |
| codegen | 9 | 파이프라인 한 단계 코드 |
| contrast | 11 | 곤충 vs 척추동물 컬럼 구분 |

## 규약 (context)

- 곤충 CNS: ACh +1, **Glu −1**, GABA −1, 5-HT/DA/OA +1, HA −1
- `W[i,j] = i→j` signed weight, 전류 `I = W.T @ x`
- NT는 `bodyId_pre`에 조인 (post 조인 금지)
- 필터는 `weight >= 5 AND sign.notna()` (OR 아님, `signed_weight >= 5` 아님)
- Male CNS Feather 컬럼: `body_pre`, `body_post`, `weight` / `consensus_nt`

`make_net()`의 NT 비율·시냅스 수 분포는 생성기 가정이다. 실데이터 Feather가 있으면 그 자리에 서브그래프를 넣는 것이 다음으로 가장 값진 개선이다 (`scripts/analyze_male_cns_connectome.py`가 `data/raw/`에 내려 둔다).

## 사용

```bash
pip install -r requirements.txt
python sft/build_sft.py --include-inferred
python sft/verify_sft.py --include-inferred
```

OpenAI 파인튜닝:

```bash
python sft/build_sft.py --include-inferred --strip-meta --out-dir sft/data/openai
```

`--strip-meta`는 `messages`만 남긴다. HF TRL은 `load_dataset("json", data_files=...)` 후 `messages` 필드가 chat template로 렌더링된다.

컨텍스트-only (inferred 4건 제외):

```bash
python sft/build_sft.py
python sft/verify_sft.py
```

대화형 봇(검색 + 계산 도구 + LoRA)은 `connectome_llm/README_ko.md` 를 본다.
