from tonz_model.engine import DealParams, bep_table, physical_monthly_eok, required_revenue, surplus_annual


def test_verified_58_matches_locked_formula():
    p = DealParams(58.0, 0.30)
    b = bep_table(p)
    assert abs(b["operating"] - 58.0 / 0.60 / 12.0) < 1e-9
    assert abs(b["operating"] - 8.055555555555555) < 1e-9
    assert abs(b["y10"] - (90 / 10 + 58) / 0.60 / 12.0) < 1e-9
    assert abs(b["y7"] - (90 / 7 + 58) / 0.60 / 12.0) < 1e-9
    assert abs(b["y6"] - (90 / 6 + 58) / 0.60 / 12.0) < 1e-9
    assert 8.05 < b["operating"] < 8.06
    assert 9.30 < b["y10"] < 9.31
    assert 9.84 < b["y7"] < 9.85
    assert 10.13 < b["y6"] < 10.14


def test_staff50_68_bep():
    p = DealParams(68.0, 0.30)
    b = bep_table(p)
    assert abs(b["operating"] - 68 / 0.60 / 12) < 1e-9
    assert 9.44 < b["operating"] < 9.45
    assert 10.69 < b["y10"] < 10.70
    assert 11.23 < b["y7"] < 11.24


def test_surplus_identity():
    p = DealParams(68.0, 0.30)
    # 월 10억 = 연 120
    assert abs(surplus_annual(120, p) - (120 * 0.60 - 68)) < 1e-9


def test_interest_raises_hurdle():
    base = required_revenue(DealParams(68.0, 0.30, interest_rate=0.0), 7)
    with_i = required_revenue(DealParams(68.0, 0.30, interest_rate=0.06), 7)
    assert with_i > base + 5


def test_physical_capacity():
    # 11 * 25 * 28 * 150000 / 1e8 = 11.55
    assert abs(physical_monthly_eok(11, 25, 150_000, 28) - 11.55) < 1e-9
