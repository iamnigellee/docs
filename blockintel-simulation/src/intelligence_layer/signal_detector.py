"""Signal detector -- analyses merchant world-model data to identify needs."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SignalType(Enum):
    CASH_FLOW_SHORTAGE = "cash_flow_shortage"
    GROWTH_OPPORTUNITY = "growth_opportunity"
    SEASONAL_PATTERN = "seasonal_pattern"


class Urgency(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Signal:
    """A detected business signal with context."""

    signal_type: SignalType
    urgency: Urgency
    merchant_id: str
    confidence: float  # 0.0 - 1.0
    details: dict[str, Any] = field(default_factory=dict)


class SignalDetector:
    """Analyses merchant data to detect actionable business signals."""

    # -----------------------------------------------------------------
    # Cash-flow shortage
    # -----------------------------------------------------------------
    def detect_cash_flow_shortage(self, merchant_data: dict[str, Any]) -> Signal | None:
        """Return a signal if the merchant shows signs of cash-flow pressure.

        Expected keys in *merchant_data*:
            merchant_id, monthly_revenue, monthly_expenses,
            cash_reserve, avg_payment_delay_days
        """
        merchant_id: str = merchant_data.get("merchant_id", "unknown")
        revenue: float = merchant_data.get("monthly_revenue", 0.0)
        expenses: float = merchant_data.get("monthly_expenses", 0.0)
        cash_reserve: float = merchant_data.get("cash_reserve", 0.0)
        delay_days: float = merchant_data.get("avg_payment_delay_days", 0.0)

        net = revenue - expenses
        runway_months = cash_reserve / expenses if expenses > 0 else float("inf")

        # Heuristic: negative cash-flow or < 2 months runway
        if net < 0 or runway_months < 2:
            confidence = min(1.0, 0.5 + (1.0 - runway_months / 2) * 0.3 + delay_days * 0.01)
            urgency = (
                Urgency.CRITICAL if runway_months < 1
                else Urgency.HIGH if runway_months < 2
                else Urgency.MEDIUM
            )
            return Signal(
                signal_type=SignalType.CASH_FLOW_SHORTAGE,
                urgency=urgency,
                merchant_id=merchant_id,
                confidence=round(min(confidence, 1.0), 3),
                details={
                    "net_monthly": round(net, 2),
                    "runway_months": round(runway_months, 2),
                    "avg_payment_delay_days": delay_days,
                },
            )
        return None

    # -----------------------------------------------------------------
    # Growth opportunity
    # -----------------------------------------------------------------
    def detect_growth_opportunity(self, merchant_data: dict[str, Any]) -> Signal | None:
        """Return a signal if the merchant exhibits strong growth indicators.

        Expected keys:
            merchant_id, monthly_revenue, revenue_growth_pct,
            customer_acquisition_rate, repeat_customer_pct
        """
        merchant_id: str = merchant_data.get("merchant_id", "unknown")
        growth_pct: float = merchant_data.get("revenue_growth_pct", 0.0)
        acq_rate: float = merchant_data.get("customer_acquisition_rate", 0.0)
        repeat_pct: float = merchant_data.get("repeat_customer_pct", 0.0)

        score = growth_pct * 0.4 + acq_rate * 0.3 + repeat_pct * 0.3

        if score >= 15:
            confidence = min(1.0, score / 50)
            urgency = Urgency.LOW if score < 25 else Urgency.MEDIUM
            return Signal(
                signal_type=SignalType.GROWTH_OPPORTUNITY,
                urgency=urgency,
                merchant_id=merchant_id,
                confidence=round(confidence, 3),
                details={
                    "composite_score": round(score, 2),
                    "revenue_growth_pct": growth_pct,
                    "customer_acquisition_rate": acq_rate,
                    "repeat_customer_pct": repeat_pct,
                },
            )
        return None

    # -----------------------------------------------------------------
    # Seasonal pattern
    # -----------------------------------------------------------------
    def detect_seasonal_pattern(
        self, transaction_history: list[dict[str, Any]]
    ) -> Signal | None:
        """Detect seasonal revenue patterns from transaction history.

        Each entry in *transaction_history* should have:
            month (1-12), revenue
        Returns a signal if a clear seasonal peak/trough is detected.
        """
        if len(transaction_history) < 6:
            return None

        revenues = [entry.get("revenue", 0.0) for entry in transaction_history]
        avg = sum(revenues) / len(revenues)
        if avg == 0:
            return None

        # Find months that deviate significantly from average
        peak_months: list[int] = []
        trough_months: list[int] = []
        for entry in transaction_history:
            ratio = entry["revenue"] / avg
            if ratio > 1.3:
                peak_months.append(entry["month"])
            elif ratio < 0.7:
                trough_months.append(entry["month"])

        if not peak_months and not trough_months:
            return None

        merchant_id = transaction_history[0].get("merchant_id", "unknown")
        variability = max(revenues) / min(revenues) if min(revenues) > 0 else float("inf")
        confidence = min(1.0, (variability - 1.0) / 3.0)

        return Signal(
            signal_type=SignalType.SEASONAL_PATTERN,
            urgency=Urgency.LOW,
            merchant_id=merchant_id,
            confidence=round(confidence, 3),
            details={
                "peak_months": peak_months,
                "trough_months": trough_months,
                "revenue_variability": round(variability, 2),
                "average_revenue": round(avg, 2),
            },
        )
