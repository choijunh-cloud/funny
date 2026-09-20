#!/usr/bin/env python3
"""일요일 다이제스트 숫자·잠금 규칙 회귀."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("/workspace")
sys.path.insert(0, str(ROOT / "scripts"))

from sep20_data import (  # noqa: E402
    DO_NOT_LOCK,
    FRI_DOW_PCT,
    FRI_NASDAQ_PCT,
    FRI_SOX_PCT,
    FRI_SPX_PCT,
    FRI_WTI,
    MAIN,
    OIL_SIREN,
    SAT_PM_MAIN,
    TENY_SIREN,
    THU_SOX_PCT,
    UNLOCKED,
    siren_10y_fired,
    siren_oil_fired,
)


def test_friday_tape() -> None:
    assert FRI_NASDAQ_PCT == 0.40
    assert FRI_SPX_PCT == 0.17
    assert FRI_DOW_PCT == -0.18
    assert FRI_SOX_PCT == 2.78
    assert FRI_WTI == 100.30
    assert THU_SOX_PCT == 3.1
    assert FRI_SOX_PCT != THU_SOX_PCT


def test_sirens_off() -> None:
    assert siren_10y_fired() is False
    assert siren_oil_fired() is False
    assert FRI_WTI < OIL_SIREN
    assert TENY_SIREN == 5.00


def test_unlocked_not_treated_as_settle() -> None:
    assert UNLOCKED["ib_hynix_310"] == 310
    assert UNLOCKED["guest_hynix_200"] == 200
    assert UNLOCKED["cts_samsung_op"] == 500
    assert UNLOCKED["samsung_op_370"] == 370
    assert "10Y 5% 안착" in DO_NOT_LOCK
    assert "oil 120" in DO_NOT_LOCK


def test_main_count_and_sat_pm_ids() -> None:
    assert len(MAIN) == 8
    ids = {m["yt"] for m in MAIN}
    sat_ids = {vid for _, vid, _ in SAT_PM_MAIN}
    assert ids.isdisjoint(sat_ids)
    forbidden = {
        "xG6588IXZJI",
        "H6-OAvaZ-Pc",
        "Dm2-8f-Itwc",
        "ESX02IP_ZxQ",
        "93iH1jbSiPw",
        "5nzxKYJ8E_A",
    }
    assert forbidden == sat_ids
    assert forbidden.isdisjoint(ids)


def test_html_guards() -> None:
    path = ROOT / "lectures" / "9월 20일 일요일 오전 다이제스트 한장.html"
    text = path.read_text(encoding="utf-8")
    assert "사이렌" in text
    assert "미발화" in text
    assert "4.95–5.01" in text or "4.95-5.01" in text
    assert "$100.30" in text
    assert "Ohio" in text
    assert "결정된 사항 없음" in text
    assert "2030" in text  # HD 4GW is a 2030 target
    assert "성상현 부부장" in text
    assert "오늘 MAIN 8에 없다" in text
    assert "xG6588IXZJI" in text
    assert "박병창" in text and "문홍철" in text and "김영익" in text
    # do not present IB targets as room consensus
    assert "목표가≠합의" in text or "합의 가격" in text
    assert "잠그지 않는다" in text
    # clock separation
    assert "목 9/17" in text
    assert "금 9/18" in text
    assert "휴장" in text
    # no A/B box metaphor
    assert "A/B" not in text or "A/B·상자 비유 없음" in text


def test_html_does_not_lock_sirens() -> None:
    path = ROOT / "lectures" / "9월 20일 일요일 오전 다이제스트 한장.html"
    text = path.read_text(encoding="utf-8")
    assert "10Y 5% 안착 · oil 120" in text or "10Y 5% 안착" in text
    assert "사이렌 OFF" in text or "미발화" in text
    # must not say oil 120 has fired
    assert "oil 120 발화" not in text
    assert "안착 확정" not in text


def test_docx_exists() -> None:
    path = ROOT / "lectures" / "9월 20일 일요일 오전 다이제스트.docx"
    assert path.exists() and path.stat().st_size > 20_000


def test_charts_exist() -> None:
    names = [
        "01_clock.png",
        "02_tape.png",
        "03_siren.png",
        "04_ai_panel.png",
        "05_rate_camp.png",
        "06_intel_chain.png",
        "07_sox_thu.png",
        "08_shipyard.png",
        "09_cxl.png",
        "10_calendar.png",
        "11_matrix.png",
        "12_flows.png",
    ]
    folder = ROOT / "lectures" / "assets" / "sep20"
    for name in names:
        p = folder / name
        assert p.exists() and p.stat().st_size > 5_000, name


def main() -> None:
    tests = [
        test_friday_tape,
        test_sirens_off,
        test_unlocked_not_treated_as_settle,
        test_main_count_and_sat_pm_ids,
        test_html_guards,
        test_html_does_not_lock_sirens,
        test_docx_exists,
        test_charts_exist,
    ]
    failed = 0
    for fn in tests:
        try:
            fn()
            print(f"ok  {fn.__name__}")
        except Exception as exc:
            failed += 1
            print(f"FAIL {fn.__name__}: {exc}")
    if failed:
        raise SystemExit(failed)


if __name__ == "__main__":
    main()
