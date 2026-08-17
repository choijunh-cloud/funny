import math
import unittest

from clinic_stress_model import (
    Assumptions,
    annual_financials,
    break_even_summary,
    monthly_revenue_from_capacity,
    payoff_years,
    patients_needed,
    solve_monthly_revenue_for_annual_cash,
)


class ClinicStressModelTests(unittest.TestCase):
    def setUp(self) -> None:
        self.a = Assumptions()

    def test_capacity_revenue(self) -> None:
        # 10 doctors × 28 days × 25 patients × KRW150,000 = KRW1.05bn.
        self.assertAlmostEqual(monthly_revenue_from_capacity(self.a), 10.5)

    def test_cash_waterfall_at_capacity(self) -> None:
        result = annual_financials(10.5, self.a)
        self.assertAlmostEqual(result["annual_revenue"], 126.0)
        self.assertAlmostEqual(result["owner_draw_pre_tax"], 12.6)
        self.assertAlmostEqual(result["ebit_before_corporate_tax"], 5.6)
        self.assertAlmostEqual(result["corporate_tax"], 0.9504)
        self.assertAlmostEqual(result["cash_available_for_principal"], 4.6496)
        self.assertAlmostEqual(result["per_owner_monthly_take_home"], 0.3255)

    def test_break_even_thresholds_include_owner_draw_and_corporate_tax(self) -> None:
        thresholds = break_even_summary(self.a)
        self.assertAlmostEqual(thresholds["operating_ebit_break_even_monthly_revenue"], 70 / 0.6 / 12)
        seven_year_sales = thresholds["7_year_principal_repayment_monthly_revenue"]
        cash = annual_financials(seven_year_sales, self.a)["cash_available_for_principal"]
        self.assertAlmostEqual(cash, 90 / 7)
        self.assertAlmostEqual(payoff_years(seven_year_sales, self.a), 7)

    def test_patient_backsolve(self) -> None:
        needed = patients_needed(10.5, self.a)
        self.assertAlmostEqual(needed["patients_per_day"], 250)
        self.assertAlmostEqual(needed["patients_per_doctor_per_day"], 25)

    def test_no_payoff_when_post_tax_cash_is_negative(self) -> None:
        self.assertTrue(math.isinf(payoff_years(8.0, self.a)))

    def test_solver_rejects_negative_target(self) -> None:
        with self.assertRaises(ValueError):
            solve_monthly_revenue_for_annual_cash(-1, self.a)


if __name__ == "__main__":
    unittest.main()
