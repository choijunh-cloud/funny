"""Synthetic-graph checks for the Male CNS connectome helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import analyze_male_cns_connectome as m  # noqa: E402


def _edges() -> pd.DataFrame:
    # A --5--> B --10--> C
    # A --1--> C          (dropped at min_weight=5)
    # B --7--> A          (reciprocal with A->B)
    return pd.DataFrame(
        {
            "body_pre": [1, 1, 2, 2],
            "body_post": [2, 3, 3, 1],
            "weight": [5, 1, 10, 7],
        }
    )


def test_normalize_renames_janelia_columns():
    df = m.normalize_edgelist(_edges())
    assert list(df.columns) == ["bodyId_pre", "bodyId_post", "weight"]
    assert df.loc[0, "bodyId_pre"] == 1


def test_filter_drops_subthreshold_edges():
    df = m.filter_min_weight(m.normalize_edgelist(_edges()), min_weight=5)
    assert len(df) == 3
    assert int(df["weight"].min()) == 5


def test_weighted_degrees_match_networkx():
    df = m.filter_min_weight(m.normalize_edgelist(_edges()), min_weight=5)
    out_d, in_d = m.weighted_degrees(df)
    G = m.build_digraph(df)

    assert G.number_of_nodes() == 3
    assert G.number_of_edges() == 3
    nx_out = {int(k): int(v) for k, v in dict(G.out_degree(weight="weight")).items()}
    nx_in = {int(k): int(v) for k, v in dict(G.in_degree(weight="weight")).items()}
    assert nx_out == {int(k): int(v) for k, v in out_d.items()}
    assert nx_in == {int(k): int(v) for k, v in in_d.items()}


def test_top_senders_order():
    df = m.filter_min_weight(m.normalize_edgelist(_edges()), min_weight=5)
    out_d, _ = m.weighted_degrees(df)
    top = m.top_items(out_d, 2)
    assert top[0] == (2, 17)  # 10 + 7
    assert top[1] == (1, 5)


def test_graph_counts_unique_nodes():
    df = m.filter_min_weight(m.normalize_edgelist(_edges()), min_weight=5)
    n_nodes, n_edges = m.graph_counts(df)
    assert n_nodes == 3
    assert n_edges == 3


def test_restrict_to_bodies_keeps_internal_edges_only():
    df = m.filter_min_weight(m.normalize_edgelist(_edges()), min_weight=5)
    # Drop neuron 3: only the A<->B edges remain
    sub = m.restrict_to_bodies(df, [1, 2])
    assert set(map(tuple, sub[["bodyId_pre", "bodyId_post"]].to_numpy())) == {(1, 2), (2, 1)}


def test_attach_metadata_fills_unknown():
    meta = pd.DataFrame(
        {
            "bodyId": [1],
            "type": ["CT1"],
            "instance": ["CT1_L"],
            "superclass": ["ol_intrinsic"],
            "status": ["Traced"],
            "somaSide": ["L"],
        }
    )
    nt = pd.DataFrame({"body": [1], "consensus_nt": ["gaba"]})
    rows = m.attach_metadata([(1, 100), (99, 4)], meta, nt)
    assert rows[0]["type"] == "CT1"
    assert rows[0]["consensus_nt"] == "gaba"
    assert rows[1]["type"] == "unknown"
    assert rows[1]["bodyId"] == 99


def test_normalize_accepts_already_renamed_columns():
    df = pd.DataFrame(
        {"bodyId_pre": [1], "bodyId_post": [2], "weight": [8]}
    )
    out = m.normalize_edgelist(df)
    assert list(out.columns) == ["bodyId_pre", "bodyId_post", "weight"]
    assert int(out.loc[0, "weight"]) == 8


def test_hub_subgraph_marks_top_senders():
    df = m.filter_min_weight(m.normalize_edgelist(_edges()), min_weight=5)
    out_d, _ = m.weighted_degrees(df)
    meta = pd.DataFrame(
        {"bodyId": [1, 2, 3], "type": ["A", "B", "C"], "instance": ["A", "B", "C"]}
    )
    G = m.hub_subgraph(df, out_d, meta, n_hubs=1, partners_per_hub=2)
    hubs = [n for n in G if G.nodes[n].get("is_hub")]
    assert hubs == [2]


def test_missing_weight_column_raises():
    with pytest.raises(ValueError, match="weight"):
        m.normalize_edgelist(pd.DataFrame({"body_pre": [1], "body_post": [2]}))
