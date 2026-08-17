#!/usr/bin/env python3
"""핵심 식 정합성 테스트."""

from tones_model.engine import ClinicEngine
from tones_model.params import ModelParams
from tones_model.physical import monthly_from_physical, theoretical_ppd
from tones_model.tax_kr import assess_person, couple_from_monthly_revenue_eok, income_tax


def test_variable_rate():
    p = ModelParams()
    assert abs(p.variable_rate - 0.30) < 1e-9
    assert abs(p.mso_net_rate - 0.60) < 1e-9


def test_bep_formula():
    e = ClinicEngine()
    assert abs(e.operating_bep() - 70 / 0.6 / 12) < 1e-9
    assert abs(e.required_monthly(7) - (90 / 7 + 70) / 0.6 / 12) < 1e-9
    assert abs(e.required_monthly(6) - (90 / 6 + 70) / 0.6 / 12) < 1e-9


def test_verified_takehome():
    tax = couple_from_monthly_revenue_eok(10.0)
    assert tax["검증식_1인월_만"] == 3100
    assert tax["검증식_부부월_만"] == 6200
    # 정밀 실수령은 건보 때문에 검증식보다 낮아야 함
    assert tax["1인_실수령월_만"] < tax["검증식_1인월_만"]
    assert abs(tax["부부_실수령월_만"] - tax["1인_실수령월_만"] * 2) <= 1


def test_income_tax_bracket():
    # 과세표준 1억: 35% - 1,544만 = 1,956만
    assert income_tax(100_000_000) == int(100_000_000 * 0.35 - 15_440_000)
    r = assess_person(480_000_000)
    assert 0.35 < r.effective_income_tax_rate < 0.45
    assert r.net_takehome < r.net_after_income_tax < r.gross_annual


def test_physical_identity():
    p = ModelParams()
    m = monthly_from_physical(25, 14.5, 11, 28)
    assert abs(m - 25 * 14.5 * 11 * 28 / 10_000) < 1e-9
    cap = theoretical_ppd(p)
    assert cap["의사1인_실용_이용률반영"] > 20


def test_staff_count():
    p = ModelParams()
    assert sum(r.headcount for r in p.staff_roles) == 50
    assert 64 < p.built_fixed_eok() < 80


def test_zero_rate_does_not_inflate_debt():
    e = ClinicEngine()
    # 월 6억은 적자. 무이자면 10년 뒤에도 원금 90
    out = e.interest_total_paid(6.0, 0.0, years=10)
    assert out["잔액"] == 90.0
    assert out["완제년"] is None


def test_interest_grows_if_cant_pay():
    e = ClinicEngine()
    out = e.interest_total_paid(6.0, 0.06, years=10)
    assert out["잔액"] > 90.0


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for fn in tests:
        fn()
        print("ok", fn.__name__)
    print(f"{len(tests)} tests passed")
