from tonz_model.tax import couple_takehome, income_tax, self_employed_burden


def test_income_tax_example_70m():
    # 7,000만 × 24% − 576만 = 1,104만
    assert abs(income_tax(70_000_000) - 11_040_000) < 1


def test_high_income_effective_above_shortcut():
    # 월매출 10억 → 1인 세전 연 6억. 실효세가 38%보다 높아야 함
    t = couple_takehome(12_000_000_000, 0.10)
    assert t["effective_rate"] > 0.42
    assert t["each_net_monthly"] < t["shortcut_3_1pct_one_monthly"]


def test_low_income_close_to_shortcut():
    # 월 4억 → 1인 세전 연 2.4억, 38% 구간
    t = couple_takehome(4.8 * 100_000_000 * 12, 0.10)
    assert 0.36 < t["effective_rate"] < 0.50
    assert t["couple_net_monthly"] == t["each_net_monthly"] * 2


def test_zero():
    r = self_employed_burden(0)
    assert r.net_monthly == 0
