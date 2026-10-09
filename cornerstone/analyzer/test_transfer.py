from django.test import SimpleTestCase

from analyzer.transfer import (
    acquisition_costs,
    estimated_bond_and_legal_costs,
    transfer_duty,
)


class TransferDutyTests(SimpleTestCase):
    def test_below_threshold_is_zero(self):
        self.assertEqual(transfer_duty(1_000_000), 0.0)

    def test_at_threshold_is_zero(self):
        self.assertEqual(transfer_duty(1_210_000), 0.0)

    def test_known_sars_values(self):
        # Verified against the SARS sliding scale (1 April 2025 table)
        cases = {
            1_500_000: 8_700,
            2_000_000: 33_786,
            2_500_000: 67_200,
            5_000_000: 327_356,
            15_000_000: 1_461_156,
        }
        for price, expected in cases.items():
            self.assertAlmostEqual(transfer_duty(price), expected, delta=1)


class AcquisitionCostTests(SimpleTestCase):
    def test_bond_and_legal_scales_with_price_and_loan(self):
        # 2,000,000 * 1.3% + 1,800,000 * 0.8% = 26,000 + 14,400
        cost = estimated_bond_and_legal_costs(2_000_000, 1_800_000)
        self.assertAlmostEqual(cost, 40_400, delta=1)

    def test_acquisition_costs_include_transfer_duty(self):
        price, loan = 2_000_000, 1_800_000
        total = acquisition_costs(price, loan)
        self.assertGreater(total, transfer_duty(price))
        self.assertAlmostEqual(
            total,
            transfer_duty(price) + estimated_bond_and_legal_costs(price, loan),
            delta=0.01,
        )