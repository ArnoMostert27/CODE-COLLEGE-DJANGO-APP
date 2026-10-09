"""South African transfer duty (SARS sliding scale) and acquisition-cost estimates.

Transfer-duty table effective 1 April 2025, confirmed unchanged for the 2026/27
year (National Treasury, Feb 2026 budget). SARS can revise this in any annual
budget — if the brackets change, update _TRANSFER_DUTY_BANDS below.
"""

from __future__ import annotations

# (upper_threshold, marginal_rate): the rate applies to the slice of the price
# between the previous threshold and this one. None = top band, no ceiling.
_TRANSFER_DUTY_BANDS = [
    (1_210_000, 0.00),
    (1_663_800, 0.03),
    (2_329_300, 0.06),
    (2_994_800, 0.08),
    (13_310_000, 0.11),
    (None, 0.13),
]


def transfer_duty(purchase_price: float) -> float:
    """SARS transfer duty, taxed progressively across the bands."""
    duty = 0.0
    lower = 0.0
    for upper, rate in _TRANSFER_DUTY_BANDS:
        if upper is None or purchase_price <= upper:
            duty += max(0.0, purchase_price - lower) * rate
            break
        duty += (upper - lower) * rate
        lower = upper
    return duty


def estimated_bond_and_legal_costs(purchase_price: float, loan_amount: float) -> float:
    """Rough benchmark for conveyancing + bond registration + Deeds Office fees.
    These scale with price/bond on the LSSA tariff; this is a simplified estimate.
    """
    conveyancing = purchase_price * 0.013
    bond_registration = loan_amount * 0.008
    return conveyancing + bond_registration


def acquisition_costs(purchase_price: float, loan_amount: float) -> float:
    """Total upfront cost on top of the deposit: transfer duty + legal/registration."""
    return transfer_duty(purchase_price) + estimated_bond_and_legal_costs(
        purchase_price, loan_amount
    )