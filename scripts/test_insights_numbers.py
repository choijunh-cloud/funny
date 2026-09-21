#!/usr/bin/env python3
"""인사이트 숫자의 산술·불변식을 고정한다."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("/workspace")
sys.path.insert(0, str(ROOT / "scripts"))

import insights_data as D  # noqa: E402


def test_sirens() -> None:
    assert D.siren_10y_fired() is False
    assert D.siren_oil_fired() is False
    assert D.FRI_WTI < D.OIL_SIREN
    assert D.TENY_WORKING_LO < D.TENY_SIREN <= D.TENY_WORKING_HI


def test_nvda_ocf_ni() -> None:
    assert abs(D.nvda_ocf_ni() - D.NVDA_OCF_NI) < 0.15
    assert abs(D.NVDA_OCF / D.NVDA_NI * 100 - 40.3) < 0.15


def test_dc_gap() -> None:
    assert abs(D.dc_gap() - D.DC_GAP) < 0.15
    assert abs(D.DC_2030_DEMAND - D.DC_2030_GRID - D.DC_GAP) < 0.15


def test_kospi_draw() -> None:
    got = D.kospi_drawdown_from_peak()
    assert -30 < got < -20
    assert D.BOX_LO < D.KOSPI_SEP18 < D.BOX_HI


def test_mix_and_book() -> None:
    assert sum(v for _, v in D.SK_ECO_SALES_MIX) == 100
    assert sum(v for _, v in D.BOOK_C) == 100
    assert D.H2_EQUITY + D.H2_CASH == 100
    assert len(D.H2_TOP10) == 10
    assert len(D.THESES) == 8
    assert len(D.CORPUS) == 21


def test_frames_untouched() -> None:
    assert D.TENY_FRAME == 5.00
    assert D.THIRTY_Y_FRAME == 6.0
    assert D.TIPS_FRAME == 3.0
    assert D.OIL_SIREN == 120.0


def test_unlocked_not_used_as_spot() -> None:
    assert D.UNLOCKED["ib_hynix_310"] == 310
    assert D.UNLOCKED["guest_hynix_200"] == 200
    assert D.HYNIX_SEP18 != D.UNLOCKED["guest_hynix_200"] * 10_000


def test_charts_exist() -> None:
    folder = ROOT / "lectures" / "assets" / "insights"
    names = [
        "01_corpus.png", "02_themes.png", "03_frames.png", "04_siren.png",
        "05_and_gate.png", "06_kospi_box.png", "07_memory_per.png", "08_fair_band.png",
        "09_hbm.png", "10_token.png", "11_nvidia.png", "12_capex.png",
        "13_equipment.png", "14_sk.png", "15_atlas.png", "16_h2.png",
        "17_bookc.png", "18_power.png", "19_flows.png", "20_export.png",
        "21_leads.png", "22_calendar.png", "23_lock.png", "24_evolve.png",
        "25_darkgpu.png", "26_opm.png",
    ]
    missing = [n for n in names if not (folder / n).exists() or (folder / n).stat().st_size < 2000]
    assert not missing, missing


def main() -> None:
    tests = [
        test_sirens,
        test_nvda_ocf_ni,
        test_dc_gap,
        test_kospi_draw,
        test_mix_and_book,
        test_frames_untouched,
        test_unlocked_not_used_as_spot,
        test_charts_exist,
    ]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"{len(tests)} passed")


if __name__ == "__main__":
    main()
