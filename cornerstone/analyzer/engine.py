"""Pure-Python financial engine for property investment analysis.

Decoupled from Django models so every function can be unit-tested in isolation.
Money values are in rands; rates are annual percentages unless noted otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass

from .transfer import acquisition_costs, transfer_duty


@dataclass
class DealInputs:
    purchase_price: float
    deposit: float
    interest_rate: float            # annual %, e.g. 11.75
    loan_term_years: int
    monthly_rent: float
    vacancy_rate: float             # %
    monthly_levies: float = 0.0
    monthly_rates: float = 0.0
    monthly_insurance: float = 0.0
    monthly_maintenance: float = 0.0
    management_fee_percent: float = 0.0    # % of monthly rent
    annual_rent_growth: float = 0.0        # %
    annual_appreciation: float = 0.0       # %
    holding_period_years: int = 5

    @classmethod
    def from_deal(cls, deal) -> "DealInputs":
        """Build inputs from a Deal instance, converting Decimals to float."""
        return cls(
            purchase_price=float(deal.purchase_price),
            deposit=float(deal.deposit),
            interest_rate=float(deal.interest_rate),
            loan_term_years=deal.loan_term_years,
            monthly_rent=float(deal.monthly_rent),
            vacancy_rate=float(deal.vacancy_rate),
            monthly_levies=float(deal.monthly_levies),
            monthly_rates=float(deal.monthly_rates),
            monthly_insurance=float(deal.monthly_insurance),
            monthly_maintenance=float(deal.monthly_maintenance),
            management_fee_percent=float(deal.management_fee_percent),
            annual_rent_growth=float(deal.annual_rent_growth),
            annual_appreciation=float(deal.annual_appreciation),
            holding_period_years=deal.holding_period_years,
        )

    @property
    def loan_amount(self) -> float:
        return self.purchase_price - self.deposit


def monthly_bond_repayment(principal: float, annual_rate: float, years: int) -> float:
    """Standard amortising loan payment. Handles a 0% rate gracefully."""
    n = years * 12
    if n == 0:
        return 0.0
    monthly_rate = (annual_rate / 100) / 12
    if monthly_rate == 0:
        return principal / n
    factor = (1 + monthly_rate) ** n
    return principal * monthly_rate * factor / (factor - 1)


def management_fee(inputs: DealInputs) -> float:
    return inputs.monthly_rent * (inputs.management_fee_percent / 100)


def monthly_operating_expenses(inputs: DealInputs) -> float:
    """Recurring monthly costs, excluding the bond repayment."""
    return (
        inputs.monthly_levies
        + inputs.monthly_rates
        + inputs.monthly_insurance
        + inputs.monthly_maintenance
        + management_fee(inputs)
    )


def effective_monthly_rent(inputs: DealInputs) -> float:
    """Rent adjusted for expected vacancy."""
    return inputs.monthly_rent * (1 - inputs.vacancy_rate / 100)


@dataclass
class DealMetrics:
    loan_amount: float
    monthly_bond: float
    monthly_operating_expenses: float
    effective_monthly_rent: float
    monthly_cash_flow: float
    annual_cash_flow: float
    gross_yield: float
    net_yield: float
    cap_rate: float
    cash_invested: float
    cash_on_cash: float
    transfer_duty: float = 0.0
    acquisition_costs: float = 0.0


def analyse(inputs: DealInputs) -> DealMetrics:
    """Compute the core single-year investment metrics for a deal."""
    bond = monthly_bond_repayment(
        inputs.loan_amount, inputs.interest_rate, inputs.loan_term_years
    )
    opex = monthly_operating_expenses(inputs)
    eff_rent = effective_monthly_rent(inputs)

    monthly_cf = eff_rent - opex - bond
    annual_cf = monthly_cf * 12
    annual_noi = (eff_rent - opex) * 12   # net operating income excludes financing

    price = inputs.purchase_price
    gross_yield = (inputs.monthly_rent * 12) / price * 100 if price else 0.0
    net_yield = annual_noi / price * 100 if price else 0.0
    cap_rate = net_yield   # cap rate is NOI / price — same basis here

    duty = transfer_duty(price)
    acq = acquisition_costs(price, inputs.loan_amount)
    cash_invested = inputs.deposit + acq
    cash_on_cash = annual_cf / cash_invested * 100 if cash_invested else 0.0

    return DealMetrics(
        loan_amount=inputs.loan_amount,
        monthly_bond=bond,
        monthly_operating_expenses=opex,
        effective_monthly_rent=eff_rent,
        monthly_cash_flow=monthly_cf,
        annual_cash_flow=annual_cf,
        gross_yield=gross_yield,
        net_yield=net_yield,
        cap_rate=cap_rate,
        cash_invested=cash_invested,
        cash_on_cash=cash_on_cash,
        transfer_duty=duty,
        acquisition_costs=acq,
    )