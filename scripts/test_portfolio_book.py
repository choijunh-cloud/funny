#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import portfolio_book as B


def test_sums() -> None:
    assert abs(B.total_weight() - 100.0) < 1e-9, B.total_weight()
    assert abs(B.equity_weight() - B.EQUITY_PCT) < 1e-9
    assert abs(B.CASH_PCT + B.EQUITY_PCT - 100.0) < 1e-9


def test_book_c() -> None:
    got = B.book_c_weights()
    assert abs(sum(got.values()) - 100.0) < 1e-6
    assert set(got) == {n for n, _ in B.BOOK_C}
    assert abs(got["SEMI"] - 45.0) < 1e-6
    assert B.semi_cluster() == 22.0


def test_new_money() -> None:
    buys = B.buy_order()
    assert [h["ticker"] for h in buys] == ["071050", "035420", "012330", "015760"]
    assert abs(sum(h["weight"] for h in buys) - 21.0) < 1e-9


def test_no_chase() -> None:
    assert B.semi_cluster() < 30.0  # 9/3 코어 30에서 축소
    banned = {x[0] for x in B.EXCLUDE}
    have = {h["ticker"] for h in B.HOLDINGS}
    assert banned.isdisjoint(have)


def test_krw() -> None:
    assert B.krw(40.0) == 40_000_000
    assert B.krw(8.0) == 8_000_000
    assert sum(B.krw(h["weight"]) for h in B.HOLDINGS) == B.REF_KRW


def test_charts() -> None:
    folder = Path("/workspace/lectures/assets/portfolio")
    for n in ["01_alloc.png", "02_bookc.png", "03_names.png", "04_newmoney.png", "05_actions.png", "06_flow.png"]:
        p = folder / n
        assert p.exists() and p.stat().st_size > 2000, n


def main() -> None:
    for fn in [test_sums, test_book_c, test_new_money, test_no_chase, test_krw, test_charts]:
        fn()
        print("ok", fn.__name__)
    print("6 passed")


if __name__ == "__main__":
    main()
