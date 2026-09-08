#!/usr/bin/env python3
"""숫자 정합 + 리포트 커버리지."""

from __future__ import annotations

from pathlib import Path

import sep08_data as D

ROOT = Path("/workspace")
HTML = ROOT / "reports" / "2026-09-08-quick-comment-brief.html"
MD = ROOT / "lectures" / "9월 8일 Quick 코멘트 분석.md"
CHARTS = ROOT / "reports" / "charts"

NEEDLES = [
    "154.73",
    "59.5",
    "34%",
    "75.2",
    "3.7",
    "1.24",
    "스트라드비전",
    "키옥시아",
    "73",
    "RL5",
    "12.5",
    "엔시날",
    "9/10",
    "4.2",
    "Hartnett",
    "240.7",
    "PSK",
    "로보티즈",
    "DeepSeek",
    "Azure",
]


def test_data():
    D.assert_all()
    assert D.DRAM_VENDORS_2Q26[0][1] == 60.981
    assert D.HYNIX_ETF_SELL_T[0] == 1.24
    assert D.ENCINAL_USD_B == 22.3


def test_outputs():
    assert HTML.exists() and HTML.stat().st_size > 8_000
    assert MD.exists() and MD.stat().st_size > 2_000
    body = HTML.read_text(encoding="utf-8") + MD.read_text(encoding="utf-8")
    missing = [n for n in NEEDLES if n not in body]
    assert not missing, f"missing: {missing}"


def test_charts():
    expected = [
        "01_dram_2q26.png",
        "02_iphone_bom.png",
        "03_buyback_headroom.png",
        "04_etf_rebal.png",
        "05_astra_paradox.png",
        "06_memory_per.png",
        "07_physical_ai_chain.png",
        "08_us_dc.png",
    ]
    missing = [n for n in expected if not (CHARTS / n).exists()]
    assert not missing, f"missing charts: {missing}"
    for n in expected:
        assert (CHARTS / n).stat().st_size > 8_000, n


def test_fact_labels():
    html = HTML.read_text(encoding="utf-8")
    assert "미확인" in html or "추정" in html
    assert "TrendForce" in html
    assert "매수·매도 권유가 아닙니다" in html


if __name__ == "__main__":
    test_data()
    test_outputs()
    test_charts()
    test_fact_labels()
    print("test_sep08_brief: ok")
