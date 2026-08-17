import math
import random
import unittest

from clinic_model import (
    BILLION,
    Assumptions,
    Triangular,
    korean_income_tax,
    run_trial,
)


class FixedTriangular(Triangular):
    def __init__(self, value):
        super().__init__(value, value, value)

    def draw(self, rng):
        return self.low

    def inverse(self, probability):
        return self.low


class ClinicModelTest(unittest.TestCase):
    def test_income_tax_is_progressive(self):
        self.assertAlmostEqual(korean_income_tax(14_000_000), 924_000)
        self.assertGreater(korean_income_tax(600_000_000), 200_000_000)
        self.assertLess(korean_income_tax(600_000_000), 250_000_000)

    def test_bep_does_not_double_count_payroll(self):
        assumptions = Assumptions(
            total_physicians=FixedTriangular(2),
            nonphysician_staff=0,
            patients_per_doctor_day=FixedTriangular(25),
            realized_revenue_per_visit=FixedTriangular(150_000),
            annual_rent_and_management=FixedTriangular(3 * BILLION),
            annual_other_fixed_cost=FixedTriangular(3 * BILLION),
            variable_cost_rate=FixedTriangular(0.30),
        )
        trial = run_trial(random.Random(1), assumptions)
        # Contribution after 10% owners' share and 30% variable cost is 60%.
        expected_monthly_bep = 6 * BILLION / 0.60 / 12
        self.assertAlmostEqual(
            trial.operating_bep_monthly_revenue,
            expected_monthly_bep,
            delta=1,
        )

    def test_nonpositive_cashflow_never_repays(self):
        assumptions = Assumptions(
            total_physicians=FixedTriangular(2),
            nonphysician_staff=0,
            patients_per_doctor_day=FixedTriangular(1),
            realized_revenue_per_visit=FixedTriangular(1),
            annual_rent_and_management=FixedTriangular(BILLION),
            annual_other_fixed_cost=FixedTriangular(BILLION),
            variable_cost_rate=FixedTriangular(0.30),
        )
        trial = run_trial(random.Random(1), assumptions)
        self.assertTrue(math.isinf(trial.years_to_repay))


if __name__ == "__main__":
    unittest.main()
