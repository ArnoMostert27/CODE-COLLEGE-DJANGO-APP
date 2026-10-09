from django.test import SimpleTestCase

from analyzer.engine import DealMetrics
from analyzer.scoring import score_deal


def metrics(**overrides):
    defaults = dict(
        loan_amount=900_000,
        monthly_bond=9_000,
        monthly_operating_expenses=2_000,
        effective_monthly_rent=11_000,
        monthly_cash_flow=0,
        annual_cash_flow=0,
        gross_yield=10,
        net_yield=8,
        cap_rate=8,
        cash_invested=100_000,
        cash_on_cash=6,
    )
    defaults.update(overrides)
    return DealMetrics(**defaults)


class ScoreDealTests(SimpleTestCase):
    def test_strong_deal_grades_a(self):
        result = score_deal(metrics(
            monthly_cash_flow=2_000,
            net_yield=10,
            cash_on_cash=12,
            gross_yield=11,
        ))
        self.assertEqual(result.score, 100)
        self.assertEqual(result.grade, "A")

    def test_poor_deal_grades_f(self):
        result = score_deal(metrics(
            monthly_cash_flow=-3_000,
            net_yield=4,
            cash_on_cash=-5,
            gross_yield=6,
        ))
        self.assertEqual(result.grade, "F")
        self.assertLess(result.score, 40)

    def test_positive_cash_flow_emits_good_signal(self):
        result = score_deal(metrics(monthly_cash_flow=1_500))
        self.assertTrue(any(s.level == "good" for s in result.signals))

    def test_negative_cash_flow_emits_bad_signal(self):
        result = score_deal(metrics(monthly_cash_flow=-3_000))
        self.assertTrue(any(s.level == "bad" for s in result.signals))

    def test_mid_deal_grades_c(self):
        # break-even (15) + net yield 7 (15) + cash-on-cash 6 (15) + gross 10 (20) = 65
        result = score_deal(metrics(
            monthly_cash_flow=-300,
            net_yield=7,
            cash_on_cash=6,
            gross_yield=10,
        ))
        self.assertEqual(result.score, 65)
        self.assertEqual(result.grade, "C")