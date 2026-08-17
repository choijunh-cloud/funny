import numpy as np

from tonz_model import tax


def test_bracket_boundaries_are_continuous():
    for upper, _, _ in tax.BRACKETS[:-1]:
        below = tax.income_tax(upper - 0.01)
        above = tax.income_tax(upper + 0.01)
        assert abs(above - below) < 1.0  # 누진공제가 맞으면 경계에서 연속


def test_known_bracket_value():
    # 과세표준 3억 -> 3억*38% - 1,994만 = 9,406만
    assert abs(tax.income_tax(30_000.0) - 9_406.0) < 1e-6


def test_net_income_monotone_and_bounded():
    grosses = np.array([1_000.0, 5_000.0, 20_000.0, 60_000.0, 120_000.0])
    nets = tax.net_income(grosses)
    assert np.all(np.diff(nets) > 0)
    assert np.all(nets < grosses)
    assert np.all(nets > 0)


def test_effective_rate_rises_with_income():
    rates = [tax.effective_rate(g) for g in (5_000, 20_000, 60_000, 120_000)]
    assert rates == sorted(rates)
    # 고소득 구간 실효부담률은 45~55% 사이여야 한다 (지방세·4대보험 포함)
    assert 0.45 < rates[-1] < 0.56


def test_social_insurance_capped():
    huge = tax.social_insurance(1_000_000.0)
    # 상한이 있으므로 소득의 10%를 넘지 않는다
    assert huge < 100_000.0
