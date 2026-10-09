from django.test import SimpleTestCase

from analyzer.engine import (
    DealInputs,
    analyse,
    effective_monthly_rent,
    management_fee,
    monthly_bond_repayment,
    monthly_operating_expenses,
)


def base_inputs(**overrides):
    defaults = dict(
        purchase_price=1_000_000,
        deposit=100_000,
        interest_rate=12,
        loan_term_years=20,
        monthly_rent=10_000,
        vacancy_rate=0,
        monthly_levies=1_000,
        monthly_rates=500,
        monthly_insurance=300,
        monthly_maintenance=200,
        management_fee_percent=10,
    )
    defaults.update(overrides)
    return DealInputs(**defaults)


class BondRepaymentTests(SimpleTestCase):
    def test_standard_amortising_payment(self):
        # R900k at 12% over 20 years ≈ R9,909.79/month
        payment = monthly_bond_repayment(900_000, 12, 20)
        self.assertAlmostEqual(payment, 9909.79, delta=1)

    def test_zero_interest_is_principal_over_months(self):
        self.assertAlmostEqual(monthly_bond_repayment(240_000, 0, 20), 1000.0, places=2)

    def test_zero_term_returns_zero(self):
        self.assertEqual(monthly_bond_repayment(500_000, 11, 0), 0.0)


class ComponentTests(SimpleTestCase):
    def test_management_fee_is_percent_of_rent(self):
        self.assertAlmostEqual(management_fee(base_inputs()), 1000.0, places=2)

    def test_operating_expenses_sum(self):
        self.assertAlmostEqual(monthly_operating_expenses(base_inputs()), 3000.0, places=2)

    def test_vacancy_reduces_rent(self):
        self.assertAlmostEqual(
            effective_monthly_rent(base_inputs(vacancy_rate=10)), 9000.0, places=2
        )


class AnalyseTests(SimpleTestCase):
    def test_loan_amount(self):
        self.assertEqual(base_inputs().loan_amount, 900_000)

    def test_gross_yield(self):
        self.assertAlmostEqual(analyse(base_inputs()).gross_yield, 12.0, places=2)

    def test_net_yield_and_cap_rate_match(self):
        m = analyse(base_inputs())
        self.assertAlmostEqual(m.net_yield, 8.4, places=2)
        self.assertAlmostEqual(m.cap_rate, 8.4, places=2)

    def test_negative_cash_flow_when_bond_exceeds_income(self):
        m = analyse(base_inputs())
        self.assertLess(m.monthly_cash_flow, 0)
        self.assertAlmostEqual(m.monthly_cash_flow, -2909.79, delta=1)

    def test_cash_invested_includes_acquisition_costs(self):
        m = analyse(base_inputs())
        # deposit 100,000 + legal/registration 20,200 (no transfer duty below R1.21m)
        self.assertAlmostEqual(m.cash_invested, 120_200, delta=1)

    def test_cash_on_cash_uses_total_cash_invested(self):
        m = analyse(base_inputs())
        self.assertAlmostEqual(
            m.cash_on_cash, m.annual_cash_flow / m.cash_invested * 100, places=4
        )