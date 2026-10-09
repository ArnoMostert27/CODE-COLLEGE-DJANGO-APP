"""Rules-based deal scoring — turns raw metrics into a grade and plain-English signals."""

from __future__ import annotations

from dataclasses import dataclass

from .engine import DealMetrics


@dataclass
class Signal:
    level: str          # "good", "warn", or "bad"
    message: str


@dataclass
class DealScore:
    score: int          # 0–100
    grade: str          # "A"–"F"
    signals: list[Signal]


def _grade_for(score: int) -> str:
    if score >= 85:
        return "A"
    if score >= 70:
        return "B"
    if score >= 55:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def score_deal(metrics: DealMetrics) -> DealScore:
    """Grade a deal A–F from its core metrics, with plain-English signals."""
    score = 0
    signals: list[Signal] = []

    # Cash flow (max 30)
    if metrics.monthly_cash_flow >= 0:
        score += 30
        signals.append(Signal(
            "good",
            f"Positive cash flow of R{metrics.monthly_cash_flow:,.0f} a month.",
        ))
    elif metrics.monthly_cash_flow >= -500:
        score += 15
        signals.append(Signal(
            "warn",
            f"Roughly break-even — you'd fund about R{abs(metrics.monthly_cash_flow):,.0f}/month.",
        ))
    else:
        signals.append(Signal(
            "bad",
            f"Negative cash flow — you fund R{abs(metrics.monthly_cash_flow):,.0f}/month out of pocket.",
        ))

    # Net yield (max 25)
    if metrics.net_yield >= 9:
        score += 25
        signals.append(Signal("good", f"Strong net yield of {metrics.net_yield:.1f}%."))
    elif metrics.net_yield >= 7:
        score += 15
    elif metrics.net_yield >= 5:
        score += 8
        signals.append(Signal("warn", f"Net yield of {metrics.net_yield:.1f}% is on the thin side."))
    else:
        signals.append(Signal("bad", f"Low net yield of {metrics.net_yield:.1f}% (below ~5%)."))

    # Cash-on-cash (max 25)
    if metrics.cash_on_cash >= 10:
        score += 25
        signals.append(Signal("good", f"Strong cash-on-cash return of {metrics.cash_on_cash:.1f}%."))
    elif metrics.cash_on_cash >= 5:
        score += 15
    elif metrics.cash_on_cash >= 0:
        score += 8
    else:
        signals.append(Signal("bad", f"Negative cash-on-cash return of {metrics.cash_on_cash:.1f}%."))

    # Gross yield (max 20)
    if metrics.gross_yield >= 10:
        score += 20
    elif metrics.gross_yield >= 8:
        score += 12
    else:
        score += 5

    return DealScore(score=score, grade=_grade_for(score), signals=signals)