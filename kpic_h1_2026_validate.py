"""Arithmetic checks for KPIC (대한유화) H1 2026 half-year report figures.

Numbers transcribed from the DART half-year report filed 2026-08-14
(제58기 반기보고서, period 2026-01-01 ~ 2026-06-30). Units: 백만원 unless noted.
"""

from __future__ import annotations

# --- Consolidated income (연결 포괄손익, 누적) ---
CONSOL_H1 = {
    "2026": {"rev": 1_803_361, "op": 69_686, "ni": 65_803, "eps": 7_512},
    "2025": {"rev": 1_588_406, "op": -14_471, "ni": 10_839, "eps": 715},
}

# Q2 2026 (3개월) 연결 영업이익
CONSOL_Q2_2026_OP = -3_877

# --- Consolidated balance sheet (연결 재무상태표) ---
CONSOL_BS = {
    "2026H1": {
        "cash": 302_682,
        "inventory": 391_999,
        "assets": 2_888_962,
        "liab": 758_176,
        "equity": 2_130_786,
        "current_assets": 1_010_259,
        "current_liab": 512_827,
    },
    "2025YE": {
        "cash": 151_455,
        "inventory": 227_503,
        "assets": 2_700_326,
        "liab": 618_856,
        "equity": 2_081_470,
        "current_assets": 763_616,
        "current_liab": 426_671,
    },
}

# --- Segment (연결조정 전 단순합) ---
SEGMENTS_H1_2026 = {
    "petro": {"rev": 1_440_143, "op": 14_813},
    "gas": {"rev": 25_213, "op": 3_108},
    "utility": {"rev": 366_014, "op": 50_833},
    "salt": {"rev": 28_998, "op": 3_576},
}

# Reported segment revenue / OP shares in the filing (percent)
SEG_REV_SHARE_REPORTED = {
    "petro": 77.3,
    "gas": 1.4,
    "utility": 19.7,
    "salt": 1.6,
}
SEG_OP_SHARE_REPORTED = {
    "petro": 20.5,
    "gas": 4.3,
    "utility": 70.3,
    "salt": 4.9,
}

# --- Parent (별도) ---
PARENT_H1_2026 = {"rev": 1_440_143, "op": 14_813, "ni": 34_117, "eps": 5_524}
PARENT_INVENTORY_LOSS_H1_2026 = 46_976

# Utilization (%)
UTILIZATION = {
    "onsan_h1_2026": 70.63,
    "ulsan_h1_2026": 62.51,
}


def pct_change(new: float, old: float) -> float:
    return (new / old - 1.0) * 100.0


def growth(new: float, old: float) -> float:
    return (new - old) / old * 100.0


def nearly(a: float, b: float, tol: float = 0.15) -> bool:
    return abs(a - b) <= tol


def validate_consol_yoy() -> tuple[list[str], list[str]]:
    rows: list[str] = []
    fails: list[str] = []
    a, b = CONSOL_H1["2026"], CONSOL_H1["2025"]
    rev_g = pct_change(a["rev"], b["rev"])
    rows.append(
        f"매출 H1'26 {a['rev']:,} vs H1'25 {b['rev']:,} => {rev_g:+.1f}%"
    )
    if not nearly(rev_g, 13.5, tol=0.2):
        fails.append(f"rev YoY expected ~+13.5%, got {rev_g:+.1f}%")

    rows.append(
        f"영업이익 H1'26 {a['op']:+,} vs H1'25 {b['op']:+,} (흑자 전환)"
    )
    if a["op"] <= 0 or b["op"] >= 0:
        fails.append("expected H1'26 OP > 0 and H1'25 OP < 0")

    eps_mult = a["eps"] / b["eps"]
    rows.append(
        f"EPS {a['eps']:,} vs {b['eps']:,} => {eps_mult:.1f}x"
    )
    if eps_mult < 8:
        fails.append(f"EPS multiple unexpectedly low: {eps_mult:.1f}x")
    return rows, fails


def validate_margins() -> tuple[list[str], list[str]]:
    rows: list[str] = []
    fails: list[str] = []
    a = CONSOL_H1["2026"]
    opm = a["op"] / a["rev"] * 100
    nim = a["ni"] / a["rev"] * 100
    rows.append(f"연결 OPM {opm:.2f}%")
    rows.append(f"연결 NIM {nim:.2f}%")
    if not nearly(opm, 3.86, tol=0.05):
        fails.append(f"OPM expected ~3.86%, got {opm:.2f}%")
    if not nearly(nim, 3.65, tol=0.05):
        fails.append(f"NIM expected ~3.65%, got {nim:.2f}%")
    return rows, fails


def validate_parent_thin_op() -> tuple[list[str], list[str]]:
    rows: list[str] = []
    fails: list[str] = []
    p = PARENT_H1_2026
    popm = p["op"] / p["rev"] * 100
    rows.append(
        f"별도 매출 {p['rev']:,} / OP {p['op']:,} / NI {p['ni']:,} / EPS {p['eps']:,}"
    )
    rows.append(f"별도(석유화학) OPM {popm:.2f}%")
    if not nearly(popm, 1.03, tol=0.05):
        fails.append(f"parent OPM expected ~1.03%, got {popm:.2f}%")
    if popm >= 3.0:
        fails.append("parent OPM not thin vs consol (~3.9%) as expected")
    return rows, fails


def validate_segment_mix() -> tuple[list[str], list[str]]:
    rows: list[str] = []
    fails: list[str] = []
    rev_sum = sum(v["rev"] for v in SEGMENTS_H1_2026.values())
    op_sum = sum(v["op"] for v in SEGMENTS_H1_2026.values())
    rows.append(f"부문 매출 단순합 {rev_sum:,} / 영업이익 단순합 {op_sum:,}")
    elim = CONSOL_H1["2026"]["op"] - op_sum
    rows.append(
        f"연결 OP {CONSOL_H1['2026']['op']:,} − 부문합 {op_sum:,} = 연결조정 {elim:+,}"
    )
    if elim >= 0:
        fails.append(f"expected consolidation elim negative, got {elim:+,}")

    for name, seg in SEGMENTS_H1_2026.items():
        rev_share = seg["rev"] / rev_sum * 100
        op_share = seg["op"] / op_sum * 100
        rows.append(
            f"{name}: rev share {rev_share:.1f}% (rpt {SEG_REV_SHARE_REPORTED[name]}%), "
            f"op share {op_share:.1f}% (rpt {SEG_OP_SHARE_REPORTED[name]}%)"
        )
        if not nearly(rev_share, SEG_REV_SHARE_REPORTED[name], tol=0.2):
            fails.append(
                f"{name} rev share {rev_share:.1f} vs reported {SEG_REV_SHARE_REPORTED[name]}"
            )
        if not nearly(op_share, SEG_OP_SHARE_REPORTED[name], tol=0.2):
            fails.append(
                f"{name} op share {op_share:.1f} vs reported {SEG_OP_SHARE_REPORTED[name]}"
            )

    util_op_share = SEGMENTS_H1_2026["utility"]["op"] / op_sum * 100
    rows.append(f"유틸리티 OP 비중 {util_op_share:.1f}% (핵심 드라이버)")
    if util_op_share < 60:
        fails.append("utility OP share unexpectedly below 60%")
    return rows, fails


def validate_balance_sheet() -> tuple[list[str], list[str]]:
    rows: list[str] = []
    fails: list[str] = []
    h1, ye = CONSOL_BS["2026H1"], CONSOL_BS["2025YE"]

    cash_g = growth(h1["cash"], ye["cash"])
    inv_g = growth(h1["inventory"], ye["inventory"])
    rows.append(f"현금 {h1['cash']:,} (YE'25 {ye['cash']:,}) => {cash_g:+.1f}%")
    rows.append(f"재고 {h1['inventory']:,} (YE'25 {ye['inventory']:,}) => {inv_g:+.1f}%")
    if not nearly(cash_g, 99.85, tol=0.5):
        fails.append(f"cash growth expected ~+99.9%, got {cash_g:+.1f}%")
    if not nearly(inv_g, 72.3, tol=0.5):
        fails.append(f"inventory growth expected ~+72.3%, got {inv_g:+.1f}%")

    da = h1["liab"] / h1["assets"] * 100
    cr = h1["current_assets"] / h1["current_liab"]
    rows.append(f"부채/자산 {da:.2f}%")
    rows.append(f"유동비율 {cr:.2f}x")
    if not nearly(da, 26.24, tol=0.1):
        fails.append(f"D/A expected ~26.24%, got {da:.2f}%")
    if not nearly(cr, 1.97, tol=0.02):
        fails.append(f"current ratio expected ~1.97, got {cr:.2f}")

    equity_check = h1["assets"] - h1["liab"]
    rows.append(
        f"자산−부채 {equity_check:,} vs 자본 {h1['equity']:,} "
        f"(diff {equity_check - h1['equity']:+,})"
    )
    if equity_check != h1["equity"]:
        fails.append("assets − liabilities != equity")
    return rows, fails


def validate_q2_residual() -> tuple[list[str], list[str]]:
    rows: list[str] = []
    fails: list[str] = []
    h1_op = CONSOL_H1["2026"]["op"]
    q2 = CONSOL_Q2_2026_OP
    implied_q1 = h1_op - q2
    rows.append(f"H1 OP {h1_op:+,} = implied Q1 {implied_q1:+,} + Q2 {q2:+,}")
    if q2 >= 0:
        fails.append("expected Q2 OP loss")
    if implied_q1 <= abs(q2):
        fails.append("Q1 OP not dominant vs |Q2| as expected from filing narrative")
    return rows, fails


def validate_inventory_loss() -> tuple[list[str], list[str]]:
    rows: list[str] = []
    fails: list[str] = []
    loss = PARENT_INVENTORY_LOSS_H1_2026
    rows.append(f"별도 재고평가손실 H1'26 {loss:,}")
    if loss < 40_000:
        fails.append("inventory valuation loss unexpectedly small vs report")
    parent_op = PARENT_H1_2026["op"]
    rows.append(
        f"별도 OP {parent_op:,} vs 재고평가손실 {loss:,} "
        f"(손실이 OP의 {loss / parent_op:.1f}배)"
    )
    return rows, fails


def validate_utilization() -> tuple[list[str], list[str]]:
    rows: list[str] = []
    fails: list[str] = []
    rows.append(f"온산 가동률 {UTILIZATION['onsan_h1_2026']:.2f}%")
    rows.append(f"울산 가동률 {UTILIZATION['ulsan_h1_2026']:.2f}%")
    if UTILIZATION["onsan_h1_2026"] >= 85:
        fails.append("onsan utilization not depressed vs FY pattern")
    if UTILIZATION["ulsan_h1_2026"] >= 70:
        fails.append("ulsan utilization unexpectedly high")
    return rows, fails


def main() -> int:
    sections = [
        ("Consol YoY (H1'26 vs H1'25)", validate_consol_yoy),
        ("Margins", validate_margins),
        ("Parent thin OP", validate_parent_thin_op),
        ("Segment mix", validate_segment_mix),
        ("Balance sheet", validate_balance_sheet),
        ("Q2 residual", validate_q2_residual),
        ("Inventory valuation loss", validate_inventory_loss),
        ("Utilization", validate_utilization),
    ]

    all_fails: list[str] = []
    for title, fn in sections:
        rows, fails = fn()
        print(f"=== {title} ===")
        print("\n".join(rows))
        if fails:
            print("FAIL:")
            print("\n".join(f"  - {f}" for f in fails))
            all_fails.extend(fails)
        print()

    if all_fails:
        print(f"RESULT: {len(all_fails)} check(s) failed")
        return 1
    print("RESULT: all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
