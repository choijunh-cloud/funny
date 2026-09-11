#!/usr/bin/env python3
"""LoRA train entry.

Real local chat models (transformers+peft) use --model /path/to/model.
Infrastructure checks (split, masking, LoRA update/save/restore) run on
a tiny numpy backend when the heavy stack or a base checkpoint is absent.

Example:
  python train_lora.py \\
    --model "/path/to/your/local-chat-model" \\
    --train data/train.jsonl \\
    --validation data/validation.jsonl \\
    --output-dir runs/domain_lora \\
    --max-length 4096
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent

IGNORE = -100


def load_jsonl(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def chat_to_text(messages: list[dict]) -> tuple[str, str]:
    """Prompt (system+user) vs assistant — labels mask the prompt."""
    prompt = ""
    answer = ""
    for m in messages:
        role, content = m["role"], m["content"]
        if role == "assistant":
            answer += content
        else:
            prompt += f"<|{role}|>\n{content}\n"
    prompt += "<|assistant|>\n"
    return prompt, answer


def mask_labels(prompt_ids: list[int], answer_ids: list[int], max_length: int) -> tuple[list[int], list[int]]:
    """Keep the answer tail. Prompt is left-truncated so labels are not all IGNORE."""
    ans_budget = max(8, min(len(answer_ids) or 8, max_length // 2))
    ans = list(answer_ids[:ans_budget]) or [1]
    prompt_budget = max_length - len(ans)
    prompt = list(prompt_ids[-prompt_budget:]) if prompt_budget else []
    ids = prompt + ans
    labels = [IGNORE] * len(prompt) + ans
    if len(ids) < max_length:
        pad = max_length - len(ids)
        ids = ids + [0] * pad
        labels = labels + [IGNORE] * pad
    return ids, labels


class HashTok:
    def __init__(self, vocab: int = 256) -> None:
        self.vocab = vocab

    def encode(self, text: str) -> list[int]:
        if not text:
            return []
        out = []
        for i in range(0, len(text), 3):
            chunk = text[i : i + 3]
            out.append(1 + (hash(chunk) % (self.vocab - 2)))
        return out


class LoRALinear:
    def __init__(self, inn: int, out: int, r: int, alpha: float, rng: np.random.Generator) -> None:
        self.W = rng.normal(scale=0.05, size=(out, inn))
        self.A = rng.normal(scale=0.05, size=(r, inn))
        self.B = np.zeros((out, r))
        self.r = r
        self.alpha = alpha

    def forward(self, x: np.ndarray) -> np.ndarray:
        return x @ self.W.T + (self.alpha / self.r) * (x @ self.A.T @ self.B.T)

    def step(self, x: np.ndarray, dY: np.ndarray, lr: float) -> None:
        scale = self.alpha / self.r
        # dY: (B, out), x: (B, inn)
        dB = scale * (dY.T @ (x @ self.A.T))
        dA = scale * ((self.B.T @ dY.T) @ x)
        self.B -= lr * dB / max(len(x), 1)
        self.A -= lr * dA / max(len(x), 1)

    def state(self) -> dict:
        return {"A": self.A.tolist(), "B": self.B.tolist(), "W": self.W.tolist(), "r": self.r, "alpha": self.alpha}

    def load(self, blob: dict) -> None:
        self.A = np.asarray(blob["A"], float)
        self.B = np.asarray(blob["B"], float)
        self.W = np.asarray(blob["W"], float)
        self.r = int(blob["r"])
        self.alpha = float(blob["alpha"])


def _one_hot(ids: np.ndarray, vocab: int) -> np.ndarray:
    b, t = ids.shape
    oh = np.zeros((b, t, vocab), dtype=float)
    flat = ids.reshape(-1)
    oh.reshape(-1, vocab)[np.arange(flat.size), flat] = 1.0
    return oh


def numpy_train(train_path: Path, val_path: Path, out_dir: Path, max_length: int, steps: int = 40) -> dict:
    tok = HashTok()
    rng = np.random.default_rng(0)
    layer = LoRALinear(tok.vocab, tok.vocab, r=4, alpha=8.0, rng=rng)
    rows = load_jsonl(train_path)
    val_rows = load_jsonl(val_path)

    def batch(recs, n=8):
        xs, ys = [], []
        for rec in recs[:n]:
            p, a = chat_to_text(rec["messages"])
            ids, labels = mask_labels(tok.encode(p), tok.encode(a), min(max_length, 96))
            xs.append(ids)
            ys.append(labels)
        return np.asarray(xs), np.asarray(ys)

    def loss_and_step(x, y, train=True):
        # mean-pool one-hot prompt+answer, predict next-token bag on unmasked labels
        oh = _one_hot(x, tok.vocab).mean(axis=1)  # (B, V)
        logits = layer.forward(oh)
        # target: bag of unmasked tokens
        tgt = np.zeros_like(logits)
        for i, row in enumerate(y):
            keep = row[row != IGNORE]
            if len(keep) == 0:
                continue
            for t in keep:
                tgt[i, int(t)] += 1
            tgt[i] /= max(len(keep), 1)
        # softmax CE
        z = logits - logits.max(axis=1, keepdims=True)
        exp = np.exp(z)
        p = exp / exp.sum(axis=1, keepdims=True)
        loss = float(-(tgt * np.log(p + 1e-9)).sum() / len(x))
        if train:
            dlogits = (p - tgt) / len(x)
            layer.step(oh, dlogits, lr=0.15)
        return loss

    x0, y0 = batch(rows, 8)
    assert (y0[0, :10] == IGNORE).any(), "prompt tokens must be masked"
    start = loss_and_step(x0, y0, train=False)
    for _ in range(steps):
        loss_and_step(*batch(rows, 8), train=True)
    end = loss_and_step(x0, y0, train=False)
    xv, yv = batch(val_rows, 8)
    val_loss = loss_and_step(xv, yv, train=False)

    out_dir.mkdir(parents=True, exist_ok=True)
    adapter = out_dir / "adapter_numpy.json"
    adapter.write_text(json.dumps(layer.state()), encoding="utf-8")
    restored = LoRALinear(tok.vocab, tok.vocab, r=4, alpha=8.0, rng=np.random.default_rng(99))
    restored.load(json.loads(adapter.read_text()))
    a1 = layer.forward(np.eye(tok.vocab)[:3])
    a2 = restored.forward(np.eye(tok.vocab)[:3])
    if not np.allclose(a1, a2):
        raise RuntimeError("LoRA restore mismatch")

    report = {
        "backend": "numpy_tiny",
        "n_train": len(rows),
        "n_validation": len(val_rows),
        "max_length": max_length,
        "loss_start": start,
        "loss_end": end,
        "val_loss": val_loss,
        "loss_dropped": end < start,
        "masking_ok": True,
        "restore_ok": True,
        "adapter": str(adapter),
        "note": "Infrastructure check on a tiny LoRA. Production LLM fine-tune was not run.",
    }
    (out_dir / "train_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not report["loss_dropped"]:
        raise SystemExit("LoRA loss did not drop")
    return report


def peft_train(model_path: str, train_path: Path, val_path: Path, out_dir: Path, max_length: int) -> None:
    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
    except ImportError as exc:
        raise SystemExit(
            "transformers / peft / torch 가 없습니다. "
            "인프라 검증은 `--model tiny` 로 하고, 실제 로컬 LLM은 의존성을 설치한 뒤 다시 실행하세요."
        ) from exc

    tok = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True)
    model = get_peft_model(
        model,
        LoraConfig(r=8, lora_alpha=16, lora_dropout=0.05, bias="none", task_type="CAUSAL_LM"),
    )

    def encode_row(rec):
        prompt, answer = chat_to_text(rec["messages"])
        p = tok(prompt, add_special_tokens=False)["input_ids"]
        a = tok(answer, add_special_tokens=False)["input_ids"]
        ids, labels = mask_labels(p, a, max_length)
        return {"input_ids": ids, "labels": labels, "attention_mask": [1 if i != 0 else 0 for i in ids]}

    train_ds = Dataset.from_list([encode_row(r) for r in load_jsonl(train_path)])
    val_ds = Dataset.from_list([encode_row(r) for r in load_jsonl(val_path)])
    args = TrainingArguments(
        output_dir=str(out_dir),
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        num_train_epochs=1,
        logging_steps=10,
        eval_strategy="epoch",
        save_strategy="epoch",
        report_to=[],
    )
    trainer = Trainer(model=model, args=args, train_dataset=train_ds, eval_dataset=val_ds)
    trainer.train()
    model.save_pretrained(out_dir)
    tok.save_pretrained(out_dir)
    print(f"saved peft adapter → {out_dir}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True, help="local chat model path, or 'tiny' for the infra check")
    p.add_argument("--train", type=Path, default=HERE / "data" / "train.jsonl")
    p.add_argument("--validation", type=Path, default=HERE / "data" / "validation.jsonl")
    p.add_argument("--output-dir", type=Path, default=HERE / "runs" / "domain_lora")
    p.add_argument("--max-length", type=int, default=4096)
    args = p.parse_args(argv)

    n_tr = len(load_jsonl(args.train))
    n_va = len(load_jsonl(args.validation))
    print(f"split train={n_tr} validation={n_va}")
    if args.model in {"tiny", "numpy", "infra"}:
        numpy_train(args.train, args.validation, args.output_dir, args.max_length)
        return 0
    peft_train(args.model, args.train, args.validation, args.output_dir, args.max_length)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
