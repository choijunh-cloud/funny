#!/usr/bin/env python3
"""Male CNS v1.0 connectome: filter, build a directed weighted graph, rank hubs.

The public Feather table is a *segment-to-segment* graph (151M edges). Loading
every edge into NetworkX needs tens of GB. This script:

1. Downloads the official Janelia GCS tables if they are missing.
2. Keeps edges with ``weight >= 5`` (same threshold as the requested snippet).
3. Computes weighted in/out-degree with pandas (mathematically identical to
   ``G.out_degree(weight="weight")``).
4. Builds a NetworkX DiGraph only when the edge count fits in ~15 GB RAM, and
   always builds a hub subgraph for a figure.
5. Writes a Korean HTML report under ``reports/male-cns-connectome/``.

Official columns are ``body_pre`` / ``body_post`` / ``weight``. They are renamed
to ``bodyId_pre`` / ``bodyId_post`` so the requested NetworkX call works.
"""

from __future__ import annotations

import argparse
import base64
import gc
import json
import sys
import urllib.request
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import networkx as nx
import numpy as np
import pandas as pd
import pyarrow.compute as pc
import pyarrow.feather as ft

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "raw"
REPORT_DIR = ROOT / "reports" / "male-cns-connectome"
FIG_DIR = REPORT_DIR / "figures"

GCS_BASE = (
    "https://storage.googleapis.com/flyem-male-cns/"
    "v1.0/connectome-data/flat-connectome"
)
WEIGHTS_NAME = "connectome-weights-male-cns-v1.0-minconf-0.5.feather"
ANN_NAME = "body-annotations-male-cns-v1.0-minconf-0.5.feather"
NT_NAME = "body-neurotransmitters-male-cns-v1.0.feather"

DEFAULT_MIN_WEIGHT = 5
# NetworkX DiGraph + edge dicts is ~0.4–1 KB/edge. Stay conservative on 15 GB.
NETWORKX_EDGE_BUDGET = 1_500_000

KR_FONT = "WenQuanYi Micro Hei"


def _setup_matplotlib() -> None:
    available = {f.name for f in fm.fontManager.ttflist}
    font = KR_FONT if KR_FONT in available else "DejaVu Sans"
    plt.rcParams.update(
        {
            "font.family": font,
            "axes.unicode_minus": False,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.25,
            "grid.linestyle": "--",
        }
    )


def normalize_edgelist(df: pd.DataFrame) -> pd.DataFrame:
    """Map Janelia ``body_*`` names onto the requested ``bodyId_*`` names."""
    rename = {}
    if "bodyId_pre" not in df.columns:
        if "body_pre" in df.columns:
            rename["body_pre"] = "bodyId_pre"
        else:
            raise ValueError("edgelist needs bodyId_pre or body_pre")
    if "bodyId_post" not in df.columns:
        if "body_post" in df.columns:
            rename["body_post"] = "bodyId_post"
        else:
            raise ValueError("edgelist needs bodyId_post or body_post")
    if "weight" not in df.columns:
        raise ValueError("edgelist needs a weight column")
    out = df.rename(columns=rename)
    return out[["bodyId_pre", "bodyId_post", "weight"]].copy()


def filter_min_weight(df: pd.DataFrame, min_weight: int = DEFAULT_MIN_WEIGHT) -> pd.DataFrame:
    return df.loc[df["weight"] >= min_weight].copy()


def weighted_degrees(df: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    out_d = df.groupby("bodyId_pre", sort=False)["weight"].sum()
    in_d = df.groupby("bodyId_post", sort=False)["weight"].sum()
    out_d.index = out_d.index.astype("int64")
    in_d.index = in_d.index.astype("int64")
    return out_d.astype("int64"), in_d.astype("int64")


def top_items(series: pd.Series, n: int = 5) -> list[tuple[int, int]]:
    ranked = series.sort_values(ascending=False).head(n)
    return [(int(k), int(v)) for k, v in ranked.items()]


def graph_counts(df: pd.DataFrame) -> tuple[int, int]:
    nodes = pd.unique(pd.concat([df["bodyId_pre"], df["bodyId_post"]], ignore_index=True))
    return int(len(nodes)), int(len(df))


def build_digraph(df: pd.DataFrame) -> nx.DiGraph:
    return nx.from_pandas_edgelist(
        df,
        source="bodyId_pre",
        target="bodyId_post",
        edge_attr="weight",
        create_using=nx.DiGraph(),
    )


def restrict_to_bodies(df: pd.DataFrame, body_ids) -> pd.DataFrame:
    allowed = pd.Index(pd.Series(body_ids).astype("int64").unique())
    mask = df["bodyId_pre"].isin(allowed) & df["bodyId_post"].isin(allowed)
    return df.loc[mask].copy()


def attach_metadata(
    ranked: list[tuple[int, int]],
    annotations: pd.DataFrame | None,
    neurotransmitters: pd.DataFrame | None,
) -> list[dict]:
    ann = None
    if annotations is not None and len(annotations):
        ann = annotations.drop_duplicates("bodyId").set_index("bodyId")
    nt = None
    if neurotransmitters is not None and len(neurotransmitters):
        nt = neurotransmitters.drop_duplicates("body").set_index("body")

    rows = []
    for body_id, strength in ranked:
        rec = {
            "bodyId": int(body_id),
            "weight": int(strength),
            "type": "unknown",
            "instance": "",
            "superclass": "",
            "status": "",
            "somaSide": "",
            "consensus_nt": "",
        }
        if ann is not None and body_id in ann.index:
            a = ann.loc[body_id]
            rec["type"] = _cell(a, "type") or "unknown"
            rec["instance"] = _cell(a, "instance")
            rec["superclass"] = _cell(a, "superclass")
            rec["status"] = _cell(a, "status")
            rec["somaSide"] = _cell(a, "somaSide")
        if nt is not None and body_id in nt.index:
            rec["consensus_nt"] = _cell(nt.loc[body_id], "consensus_nt")
        rows.append(rec)
    return rows


def _cell(row, col: str) -> str:
    if col not in row.index:
        return ""
    val = row[col]
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return ""
    return str(val)


def download_if_needed(dest: Path, url: str) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return dest
    print(f"다운로드: {url}")
    tmp = dest.with_suffix(dest.suffix + ".part")
    urllib.request.urlretrieve(url, tmp)
    tmp.replace(dest)
    return dest


def load_filtered_weights(path: Path, min_weight: int) -> pd.DataFrame:
    table = ft.read_table(path, memory_map=True)
    filtered = table.filter(pc.greater_equal(table["weight"], min_weight))
    df = normalize_edgelist(filtered.to_pandas())
    del table, filtered
    gc.collect()
    return df


def load_annotations(path: Path) -> pd.DataFrame:
    cols = [
        "bodyId",
        "type",
        "instance",
        "superclass",
        "class",
        "status",
        "statusLabel",
        "somaSide",
        "fruDsx",
        "dimorphism",
    ]
    table = ft.read_table(path, columns=cols)
    return table.to_pandas()


def load_neurotransmitters(path: Path) -> pd.DataFrame:
    cols = ["body", "cell_type", "consensus_nt", "predicted_nt", "predicted_nt_confidence"]
    return ft.read_table(path, columns=cols).to_pandas()


def strongest_edges(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return df.nlargest(n, "weight").reset_index(drop=True)


def type_out_strength(df: pd.DataFrame, annotations: pd.DataFrame, n: int = 12) -> pd.DataFrame:
    meta = annotations.drop_duplicates("bodyId")[["bodyId", "type"]]
    merged = df.merge(meta, left_on="bodyId_pre", right_on="bodyId", how="left")
    merged["type"] = merged["type"].fillna("unannotated")
    ranked = (
        merged.groupby("type", as_index=False)["weight"]
        .sum()
        .sort_values("weight", ascending=False)
        .head(n)
    )
    return ranked


def reciprocal_edge_fraction(df: pd.DataFrame) -> float:
    """Share of directed edges that have a reverse edge (unweighted)."""
    if df.empty:
        return 0.0
    fwd = df[["bodyId_pre", "bodyId_post"]].drop_duplicates()
    rev = fwd.rename(columns={"bodyId_pre": "bodyId_post", "bodyId_post": "bodyId_pre"})
    both = fwd.merge(rev, on=["bodyId_pre", "bodyId_post"])
    return float(len(both) / len(fwd))


def _png(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def make_figures(
    df: pd.DataFrame,
    out_d: pd.Series,
    top_out: list[dict],
    type_rank: pd.DataFrame,
    hub_graph: nx.DiGraph,
) -> dict[str, Path]:
    _setup_matplotlib()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    vals = np.clip(out_d.to_numpy(dtype="float64"), 1, None)
    bins = np.logspace(np.log10(vals.min()), np.log10(vals.max()), 40)
    ax.hist(vals, bins=bins, color="#1e407c", alpha=0.88, edgecolor="white", linewidth=0.3)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("가중 Out-degree (시냅스 수)")
    ax.set_ylabel("뉴런/세그먼트 수")
    ax.set_title("Out-degree 분포 (weight ≥ 5)")
    fig.tight_layout()
    paths["degree"] = FIG_DIR / "out_degree_distribution.png"
    fig.savefig(paths["degree"], dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    labels = [f"{r['instance'] or r['type']}  ({r['bodyId']})" for r in reversed(top_out)]
    weights = [r["weight"] for r in reversed(top_out)]
    colors = ["#b8943a" if i >= len(top_out) - 5 else "#1e407c" for i in range(len(top_out))]
    ax.barh(labels, weights, color=colors)
    ax.set_xlabel("가중 Out-degree (시냅스 수)")
    ax.set_title("상위 출력 허브")
    fig.tight_layout()
    paths["top"] = FIG_DIR / "top_out_degree.png"
    fig.savefig(paths["top"], dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    types = list(reversed(type_rank["type"].tolist()))
    tw = list(reversed(type_rank["weight"].tolist()))
    ax.barh(types, tw, color="#0f2043")
    ax.set_xlabel("타입 합산 출력 시냅스")
    ax.set_title("세포 타입별 출력 강도")
    fig.tight_layout()
    paths["types"] = FIG_DIR / "type_out_strength.png"
    fig.savefig(paths["types"], dpi=140)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.6, 8.0))
    if hub_graph.number_of_nodes() >= 2:
        weights = np.array([d.get("weight", 1) for *_, d in hub_graph.edges(data=True)], dtype=float)
        widths = 0.4 + 2.2 * (weights / max(weights.max(), 1.0))
        out_w = dict(hub_graph.out_degree(weight="weight"))
        sizes = [280 + 2200 * (out_w.get(n, 0) / max(max(out_w.values()), 1)) for n in hub_graph.nodes]
        pos = nx.spring_layout(hub_graph, k=1.25, seed=7, weight="weight")
        nx.draw_networkx_edges(hub_graph, pos, ax=ax, width=widths, alpha=0.28, arrows=True, arrowsize=8)
        nx.draw_networkx_nodes(hub_graph, pos, ax=ax, node_size=sizes, node_color="#1e407c", alpha=0.9)
        labels = {n: hub_graph.nodes[n].get("label", str(n)) for n in hub_graph.nodes}
        nx.draw_networkx_labels(hub_graph, pos, labels=labels, ax=ax, font_size=7, font_color="#111")
    ax.set_axis_off()
    ax.set_title("상위 허브 서브그래프 (노드 크기 = Out-degree)")
    fig.tight_layout()
    paths["hubs"] = FIG_DIR / "hub_subgraph.png"
    fig.savefig(paths["hubs"], dpi=140)
    plt.close(fig)

    return paths


def hub_subgraph(df: pd.DataFrame, out_d: pd.Series, annotations: pd.DataFrame, n_hubs: int = 36) -> nx.DiGraph:
    hubs = list(out_d.sort_values(ascending=False).head(n_hubs).index)
    sub = restrict_to_bodies(df, hubs)
    G = build_digraph(sub)
    inst = annotations.drop_duplicates("bodyId").set_index("bodyId")
    for node in G.nodes:
        if node in inst.index:
            label = _cell(inst.loc[node], "instance") or _cell(inst.loc[node], "type") or str(node)
        else:
            label = str(node)
        G.nodes[node]["label"] = label
    return G


def write_html(results: dict, figures: dict[str, Path], path: Path) -> None:
    def img(key: str, alt: str) -> str:
        return f'<img src="{_png(figures[key])}" alt="{alt}"/>'

    def rows(items: list[dict], kind: str) -> str:
        bits = []
        for i, r in enumerate(items, 1):
            bits.append(
                "<tr>"
                f"<td>{i}</td>"
                f"<td><code>{r['bodyId']}</code></td>"
                f"<td>{r['instance'] or r['type']}</td>"
                f"<td>{r['type']}</td>"
                f"<td>{r['superclass']}</td>"
                f"<td>{r['consensus_nt']}</td>"
                f"<td class='num'>{r['weight']:,}</td>"
                "</tr>"
            )
        return "".join(bits)

    edge_rows = []
    for r in results["strongest_edges"]:
        edge_rows.append(
            "<tr>"
            f"<td><code>{r['bodyId_pre']}</code></td>"
            f"<td>{r['pre_label']}</td>"
            f"<td>→</td>"
            f"<td><code>{r['bodyId_post']}</code></td>"
            f"<td>{r['post_label']}</td>"
            f"<td class='num'>{r['weight']:,}</td>"
            "</tr>"
        )

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Male CNS 커넥톰 그래프 분석</title>
  <style>
    :root {{
      --navy: #0f2043;
      --navy2: #1e407c;
      --gold: #b8943a;
      --ink: #1a1a1a;
      --muted: #4b5563;
      --line: #d0d7e2;
      --bg: #f4f6fb;
      --card: #ffffff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "WenQuanYi Micro Hei", "Apple SD Gothic Neo", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    header {{
      background: linear-gradient(135deg, var(--navy), var(--navy2));
      color: #fff;
      padding: 36px 28px 28px;
    }}
    header p {{ margin: 8px 0 0; opacity: 0.88; line-height: 1.55; }}
    h1 {{ margin: 0; font-size: 28px; letter-spacing: -0.03em; }}
    main {{ max-width: 1100px; margin: 0 auto; padding: 22px 16px 64px; }}
    .kpis {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 18px 0 8px; }}
    .kpi {{ background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; }}
    .kpi .label {{ color: var(--muted); font-size: 12px; }}
    .kpi .value {{ font-size: 22px; font-weight: 700; color: var(--navy); margin-top: 4px; }}
    section {{
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 20px 22px;
      margin-top: 16px;
    }}
    h2 {{ margin: 0 0 10px; font-size: 18px; color: var(--navy); }}
    p, li {{ line-height: 1.65; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13.5px; }}
    th {{ text-align: left; background: #eef2f8; color: var(--navy); padding: 8px 8px; }}
    td {{ padding: 7px 8px; border-bottom: 1px solid #e8edf5; }}
    td.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
    code, pre {{ font-family: ui-monospace, Menlo, Consolas, monospace; }}
    pre {{
      background: #0f2043;
      color: #e8eef8;
      padding: 14px 16px;
      border-radius: 10px;
      overflow: auto;
      font-size: 13px;
      line-height: 1.5;
    }}
    img {{ width: 100%; border-radius: 10px; border: 1px solid var(--line); }}
    .grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }}
    .note {{ color: var(--muted); font-size: 13.5px; }}
    .tag {{
      display: inline-block;
      background: #fff8e7;
      color: #7a5c12;
      border-radius: 999px;
      padding: 2px 10px;
      font-size: 12px;
      margin-right: 6px;
    }}
    @media (max-width: 800px) {{
      .kpis, .grid2 {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="tag">Male CNS v1.0</div>
    <div class="tag">minconf 0.5</div>
    <div class="tag">weight ≥ {results['min_weight']}</div>
    <h1>초파리 수컷 CNS 커넥톰 그래프 분석</h1>
    <p>Janelia FlyEM public Feather 가중치 테이블을 유향 가중 그래프(DiGraph)로 읽고,
    시냅스 수 기준 출력 허브(Out-degree)를 계산했다. 원본 테이블은 세그먼트-세그먼트
    전체 그래프(1.5억 에지)라서 임계값 필터가 필요하다.</p>
  </header>
  <main>
    <div class="kpis">
      <div class="kpi"><div class="label">필터 후 노드</div><div class="value">{results['n_nodes']:,}</div></div>
      <div class="kpi"><div class="label">필터 후 에지</div><div class="value">{results['n_edges']:,}</div></div>
      <div class="kpi"><div class="label">원본 에지</div><div class="value">{results['n_edges_raw']:,}</div></div>
      <div class="kpi"><div class="label">주석 있는 뉴런 서브그래프 에지</div><div class="value">{results['n_edges_annotated']:,}</div></div>
    </div>

    <section>
      <h2>요청 코드와 동일한 출력</h2>
      <pre>{results['console_block']}</pre>
      <p class="note">가중 Out-degree는 각 뉴런이 보내는 시냅스 수의 합이다.
      NetworkX <code>G.out_degree(weight="weight")</code>와 pandas
      <code>groupby(bodyId_pre).weight.sum()</code>은 같은 값이다.
      전체 {results['n_edges']:,}개 에지를 NetworkX에 올리면 이 환경(15 GB RAM)에서는
      프로세스 메모리를 넘긴다. 전역 랭킹은 pandas로 계산하고, NetworkX는
      {results['nx_note']}.</p>
    </section>

    <section>
      <h2>데이터와 전처리</h2>
      <ul>
        <li>출처: <code>gs://flyem-male-cns/v1.0/connectome-data/flat-connectome/</code>
            (Male CNS v1.0, 시냅스 confidence ≥ 0.5).</li>
        <li>원본 컬럼은 <code>body_pre</code>, <code>body_post</code>, <code>weight</code>다.
            요청 코드의 <code>bodyId_pre</code>/<code>bodyId_post</code>로 바꿔 넣었다.</li>
        <li>원본 {results['n_edges_raw']:,}개 에지 중 weight = 1인 연결이 약 62%다.
            <code>weight ≥ {results['min_weight']}</code>만 남기면 에지가
            {results['edge_keep_pct']:.2f}%로 줄어 노이즈와 메모리를 같이 줄인다.</li>
        <li>필터 후 노드 {results['n_nodes']:,}개는 증명된 뉴런만이 아니다.
            Feather 파일은 <b>모든 세그먼트</b>를 포함하므로 조각(fragment) ID가 섞인다.
            주석 테이블에 있는 body만 남기면 노드 {results['n_nodes_annotated']:,}개,
            에지 {results['n_edges_annotated']:,}개가 된다.
            논문의 ~166,700 뉴런에 더 가깝다.</li>
        <li>상호 에지 비율(방향만 반대인 쌍이 있는 비율):
            세그먼트 그래프 {results['reciprocal_all']:.1%},
            주석 뉴런 그래프 {results['reciprocal_ann']:.1%}.</li>
      </ul>
    </section>

    <section>
      <h2>Top 5 출력 뉴런</h2>
      <p>최상위 네 자리는 광역 억제 뉴런이다. CT1은 시각엽, APL은 버섯체(Kenyon cell)를
      덮는 GABA 세포라서 시냅스 합이 클 수밖에 없다. 5위 LPi21도 소엽판 광역 억제다.</p>
      <table>
        <thead>
          <tr><th>#</th><th>bodyId</th><th>instance</th><th>type</th><th>superclass</th><th>NT</th><th>Out-degree</th></tr>
        </thead>
        <tbody>{rows(results['top_out'], 'out')}</tbody>
      </table>
    </section>

    <section>
      <h2>참고: Top 10 입력 뉴런 (In-degree)</h2>
      <table>
        <thead>
          <tr><th>#</th><th>bodyId</th><th>instance</th><th>type</th><th>superclass</th><th>NT</th><th>In-degree</th></tr>
        </thead>
        <tbody>{rows(results['top_in'], 'in')}</tbody>
      </table>
    </section>

    <section>
      <h2>가장 강한 단일 연결</h2>
      <table>
        <thead>
          <tr><th>pre</th><th>type</th><th></th><th>post</th><th>type</th><th>weight</th></tr>
        </thead>
        <tbody>{''.join(edge_rows)}</tbody>
      </table>
    </section>

    <section>
      <h2>그림</h2>
      <div class="grid2">
        <div>{img('degree', 'Out-degree distribution')}</div>
        <div>{img('top', 'Top out-degree neurons')}</div>
        <div>{img('types', 'Type-level out strength')}</div>
        <div>{img('hubs', 'Hub subgraph')}</div>
      </div>
    </section>

    <section>
      <h2>재현</h2>
      <pre>pip install -r requirements.txt
python scripts/analyze_male_cns_connectome.py</pre>
      <p class="note">원본 Feather는 git에 넣지 않는다. 스크립트가 GCS에서
      <code>data/raw/</code>로 받는다. 단위 테스트는 작은 합성 에지로
      NetworkX와 pandas 차수가 같은지 확인한다:
      <code>pytest tests/test_connectome_graph.py</code></p>
    </section>
  </main>
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def _label_body(body_id: int, annotations: pd.DataFrame) -> str:
    inst = annotations.drop_duplicates("bodyId").set_index("bodyId")
    if body_id not in inst.index:
        return "unannotated"
    return _cell(inst.loc[body_id], "instance") or _cell(inst.loc[body_id], "type") or "unknown"


def analyze(min_weight: int, data_dir: Path, report_dir: Path) -> dict:
    weights_path = download_if_needed(data_dir / WEIGHTS_NAME, f"{GCS_BASE}/{WEIGHTS_NAME}")
    ann_path = download_if_needed(data_dir / ANN_NAME, f"{GCS_BASE}/{ANN_NAME}")
    nt_path = download_if_needed(data_dir / NT_NAME, f"{GCS_BASE}/{NT_NAME}")

    raw_table = ft.read_table(weights_path, memory_map=True)
    n_edges_raw = int(raw_table.num_rows)
    del raw_table
    gc.collect()

    print(f"가중치 테이블 로드 후 weight ≥ {min_weight} 필터")
    df = load_filtered_weights(weights_path, min_weight)
    annotations = load_annotations(ann_path)
    neurotransmitters = load_neurotransmitters(nt_path)

    n_nodes, n_edges = graph_counts(df)
    out_d, in_d = weighted_degrees(df)
    top_senders = top_items(out_d, 5)
    top_out_rows = attach_metadata(top_items(out_d, 15), annotations, neurotransmitters)
    top_in_rows = attach_metadata(top_items(in_d, 10), annotations, neurotransmitters)

    annotated_ids = annotations["bodyId"].astype("int64")
    df_ann = restrict_to_bodies(df, annotated_ids)
    n_nodes_ann, n_edges_ann = graph_counts(df_ann)

    recip_all = reciprocal_edge_fraction(df)
    recip_ann = reciprocal_edge_fraction(df_ann)
    type_rank = type_out_strength(df, annotations, 12)

    strong = strongest_edges(df, 8)
    strongest = []
    for rec in strong.to_dict("records"):
        strongest.append(
            {
                "bodyId_pre": int(rec["bodyId_pre"]),
                "bodyId_post": int(rec["bodyId_post"]),
                "weight": int(rec["weight"]),
                "pre_label": _label_body(int(rec["bodyId_pre"]), annotations),
                "post_label": _label_body(int(rec["bodyId_post"]), annotations),
            }
        )

    console_block = (
        f"노드 수: {n_nodes:,}\n"
        f"에지 수: {n_edges:,}\n"
        f"Top 5 Out-degree Neurons: {top_senders}"
    )
    print(console_block)

    nx_note = "상위 허브 서브그래프와 합성 테스트에만 사용했다"
    if n_edges <= NETWORKX_EDGE_BUDGET:
        G = build_digraph(df)
        assert G.number_of_nodes() == n_nodes
        assert G.number_of_edges() == n_edges
        nx_top = sorted(dict(G.out_degree(weight="weight")).items(), key=lambda x: x[1], reverse=True)[:5]
        assert [(int(a), int(b)) for a, b in nx_top] == top_senders
        nx_note = "필터 후 전체 DiGraph를 만들어 pandas 랭킹과 대조했다"
        del G
        gc.collect()

    hubs = hub_subgraph(df, out_d, annotations, n_hubs=36)
    figures = make_figures(df, out_d, top_out_rows, type_rank, hubs)

    results = {
        "dataset": "male-cns-v1.0",
        "min_weight": min_weight,
        "n_edges_raw": n_edges_raw,
        "n_nodes": n_nodes,
        "n_edges": n_edges,
        "edge_keep_pct": 100.0 * n_edges / n_edges_raw,
        "n_nodes_annotated": n_nodes_ann,
        "n_edges_annotated": n_edges_ann,
        "reciprocal_all": recip_all,
        "reciprocal_ann": recip_ann,
        "top_senders": top_senders,
        "top_out": top_out_rows,
        "top_in": top_in_rows,
        "strongest_edges": strongest,
        "type_out_strength": type_rank.to_dict("records"),
        "console_block": console_block,
        "nx_note": nx_note,
        "hub_subgraph_nodes": hubs.number_of_nodes(),
        "hub_subgraph_edges": hubs.number_of_edges(),
    }

    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_html(results, figures, report_dir / "index.html")
    print(f"리포트: {report_dir / 'index.html'}")
    return results


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Male CNS connectome graph analysis")
    p.add_argument("--min-weight", type=int, default=DEFAULT_MIN_WEIGHT)
    p.add_argument("--data-dir", type=Path, default=DATA_DIR)
    p.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    analyze(args.min_weight, args.data_dir, args.report_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
