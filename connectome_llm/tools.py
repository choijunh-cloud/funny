"""Calculation tools. Numbers come from a provided net or they are refused."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

SFT = Path(__file__).resolve().parents[1] / "sft"
sys.path.insert(0, str(SFT))
import knowledge as kn  # noqa: E402


class ToolError(ValueError):
    pass


def _require(payload: dict, *keys: str) -> None:
    missing = [k for k in keys if k not in payload or payload[k] in (None, [], {})]
    if missing:
        raise ToolError(
            "계산을 거부한다. 필요한 필드가 없다: "
            + ", ".join(missing)
            + ". 실제 미니넷이나 실행 결과가 없으면 수치를 만들지 않는다."
        )


def dedupe_edges(edges: list[tuple]) -> list[tuple]:
    """Sum synapse counts on duplicate (pre, post). NT must agree."""
    acc: dict[tuple[str, str], list] = {}
    for row in edges:
        pre, post, w, ntv = row[0], row[1], int(row[2]), row[3]
        key = (str(pre), str(post))
        if key not in acc:
            acc[key] = [pre, post, 0, ntv]
        elif acc[key][3] != ntv:
            raise ToolError(f"duplicate edge {key} has conflicting NT")
        acc[key][2] += w
    return [tuple(v) for v in acc.values()]


def signed_weights(payload: dict, min_weight: int = 5) -> dict[str, Any]:
    _require(payload, "edges")
    edges = dedupe_edges([tuple(e) for e in payload["edges"]])
    rows = []
    for pre, post, w, ntv in edges:
        if w < min_weight:
            continue
        sign = kn.INSECT_SIGN[ntv]
        rows.append(
            {
                "pre": pre,
                "post": post,
                "weight": int(w),
                "nt": ntv,
                "sign": int(sign),
                "signed_weight": int(w * sign),
            }
        )
    return {
        "rows": rows,
        "n_pos": sum(1 for r in rows if r["signed_weight"] > 0),
        "n_neg": sum(1 for r in rows if r["signed_weight"] < 0),
    }


def current_WTx(payload: dict, min_weight: int = 5) -> dict[str, Any]:
    _require(payload, "neurons", "edges", "x")
    names = [str(n) for n in payload["neurons"]]
    x = np.asarray(payload["x"], dtype=float)
    if x.shape != (len(names),):
        raise ToolError("x 길이가 뉴런 수와 다르다. 전류를 만들지 않는다.")
    signed = signed_weights(payload, min_weight=min_weight)
    idx = {n: i for i, n in enumerate(names)}
    W = np.zeros((len(names), len(names)), dtype=float)
    for r in signed["rows"]:
        W[idx[r["pre"]], idx[r["post"]]] = float(r["signed_weight"])
    I = W.T @ x
    return {
        "W": W.tolist(),
        "I": [float(v) for v in I],
        "n_pos": signed["n_pos"],
        "n_neg": signed["n_neg"],
        "rows": signed["rows"],
    }


def lif_step(
    V: list[float] | np.ndarray,
    I: list[float] | np.ndarray,
    *,
    tau: float,
    dt: float,
    V_rest: float = 0.0,
    V_th: float = 1.0,
    V_reset: float = 0.0,
) -> dict[str, Any]:
    """One leaky-integrate step. Parameters are model knobs, not fly data."""
    V0 = np.asarray(V, dtype=float)
    I0 = np.asarray(I, dtype=float)
    if V0.shape != I0.shape:
        raise ToolError("V와 I 길이가 다르다. ΔV를 만들지 않는다.")
    if tau <= 0 or dt <= 0:
        raise ToolError("tau와 dt는 양수여야 한다.")
    dV = (dt / tau) * (V_rest - V0 + I0)
    V1 = V0 + dV
    spiked = V1 >= V_th
    V1 = np.where(spiked, V_reset, V1)
    return {
        "V_next": [float(v) for v in V1],
        "dV": [float(v) for v in dV],
        "spiked": [bool(s) for s in spiked],
        "params": {"tau": tau, "dt": dt, "V_rest": V_rest, "V_th": V_th, "V_reset": V_reset},
        "note": "tau/dt/V_th는 모델 파라미터이며 초파리 실측이 아니다.",
    }


def current_and_lif(payload: dict) -> dict[str, Any]:
    cur = current_WTx(payload)
    V = payload.get("V") or [0.0] * len(payload["neurons"])
    step = lif_step(
        V,
        cur["I"],
        tau=float(payload.get("tau", 10.0)),
        dt=float(payload.get("dt", 1.0)),
        V_rest=float(payload.get("V_rest", 0.0)),
        V_th=float(payload.get("V_th", 1.0)),
        V_reset=float(payload.get("V_reset", 0.0)),
    )
    return {**cur, **step}
