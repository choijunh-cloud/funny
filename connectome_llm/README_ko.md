# 커넥톰 대화 봇 — 검색 + 계산 도구 + 전문 문답 학습

권장 진입점은 저장소 루트의 단일 파일입니다. 다른 Python/지식/템플릿 파일 없이 표준 라이브러리만으로 데이터를 만들고 검증합니다.

```
python connectome_llm_all_in_one.py build
python connectome_llm_all_in_one.py verify
python connectome_llm_all_in_one.py prepare --question "Glu는 항상 억제성인가요?"
```

기본 자료는 합성/문헌 기반 학습 352, 검증 80, 별도 평가 24입니다.
NT 극성은 모델 가정과 실험 사실을 구분하며, Glu=+1을 일괄 금지하지 않습니다.
이 파일만으로 MaleCNS Feather나 사전학습 LLM 성능이 검증됐다는 뜻은 아닙니다.

아래 `connectome_llm/` 패키지는 같은 주제를 여러 파일로 나눈 이전 구성입니다.

대화형 봇에는 근거 검색, 계산 도구, 전문 문답 학습을 함께 쓰는 구성이 맞다.
파일·버전 정보는 검색으로 제공하고, 설명과 코드 검토 방식은 미세조정한다.
부호화된 입력과 막전위 변화는 도구로 확인한다. 실제 데이터나 실행 결과가 없으면 수치를 만들지 않는다.

검색 기반 생성의 배경은 Lewis et al., 2020, [arXiv:2005.11401](https://arxiv.org/abs/2005.11401).

## 학습의 중심

* 개념 설명: NT 극성, 수용체 의존성, 모델 가정을 구분하기
* 코드 검토: 행렬 방향, 결측·동률, 중복 에지, LIF 구현 오류 찾기
* 계산: 부호화된 입력과 막전위 변화를 도구로 확인하기
* 근거 판단: 실제 데이터나 실행 결과가 없으면 수치를 만들어내지 않기

## 패키지

| 경로 | 내용 |
| --- | --- |
| `cards/evidence_cards.json` | 근거 카드 12개 (파일·버전·이 저장소 실측) |
| `data/train.jsonl` | 학습 352 |
| `data/validation.jsonl` | 검증 80 |
| `data/eval.jsonl` | 별도 평가 24 |
| `retrieve.py` | 다른 봇에 붙일 검색 인터페이스 |
| `tools.py` | `W.T@x`, 중복 에지 합, LIF 한 스텝 |
| `train_lora.py` | LoRA 학습·저장·복원 |
| `infer.py` | 검색+도구 응답 |
| `evaluate.py` | 같은 24문항으로 검색만 vs 학습 타깃 비교 |

학습 문장은 `sft/knowledge.py` + `domain_facts.py` 원장과 카드·도구 결과만 사용한다.

## 검색을 다른 봇에 붙이기

```python
from retrieve import ConnectomeSearch, search

hits = search("Male CNS feather 파일 이름", k=3)
ctx = ConnectomeSearch().as_context("원본 에지 수", k=2)
```

## 로컬 LLM LoRA

압축을 푼 폴더에서, 준비한 로컬 LLM 경로를 지정한다.

```
python train_lora.py \
  --model "/path/to/your/local-chat-model" \
  --train data/train.jsonl \
  --validation data/validation.jsonl \
  --output-dir runs/domain_lora \
  --max-length 4096
```

`transformers` / `peft` / `torch` 가 있을 때 위 경로가 동작한다.
데이터 분리, 계산 정답, 학습 마스킹(프롬프트 `labels=-100`), LoRA 업데이트·저장·복원은
`--model tiny` 인프라 경로로 검증했다.

```
python train_lora.py --model tiny --train data/train.jsonl \
  --validation data/validation.jsonl --output-dir runs/domain_lora
python evaluate.py
```

실제 사용할 LLM의 미세조정과 성능 향상 측정은 아직 수행하지 않았다.
먼저 기존 봇에 검색을 붙인 결과와 미세조정 타깃을 같은 평가 문항으로 비교하도록 구성했다
(`evaluate.py`의 `retrieve_only` vs `gold_sft_style`, `lora_generation=not_run`).

## 재현

```
python build_domain.py
python verify_domain.py
python infer.py --query "weight>=5 후 에지 수는?"
```

원본 Feather가 생기면 `sft/build_sft.py`의 `make_net()` 자리에 실데이터 서브그래프를 넣는 것이 계산 과제의 다음 개선이다.
카드 `card.stats` / `card.hubs` 수치는 `scripts/analyze_male_cns_connectome.py` 실행 결과이다.
