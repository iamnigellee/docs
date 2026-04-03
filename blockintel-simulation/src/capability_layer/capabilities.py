"""Concrete capability implementations for BlockIntel."""

from __future__ import annotations

import random
import time
import uuid
from typing import Any

from .base import Capability, ExecutionResult, HealthReport, HealthStatus


# ---------------------------------------------------------------------------
# Payment
# ---------------------------------------------------------------------------

class PaymentCapability(Capability):
    """Processes payment requests and returns transaction results."""

    @property
    def name(self) -> str:
        return "payment"

    @property
    def sla_response_time_ms(self) -> float:
        return 200.0

    @property
    def tags(self) -> list[str]:
        return ["payment", "transaction", "core"]

    def execute(self, request: dict[str, Any]) -> ExecutionResult:
        start = time.monotonic()

        amount: float = request.get("amount", 0.0)
        currency: str = request.get("currency", "USD")
        merchant_id: str = request.get("merchant_id", "unknown")

        # Simulate processing delay
        time.sleep(random.uniform(0.01, 0.05))

        # Simulate a small failure rate
        if random.random() < 0.02:
            elapsed = (time.monotonic() - start) * 1000
            return ExecutionResult(
                success=False,
                error="payment_declined",
                latency_ms=elapsed,
            )

        transaction_id = uuid.uuid4().hex[:12]
        elapsed = (time.monotonic() - start) * 1000
        return ExecutionResult(
            success=True,
            data={
                "transaction_id": transaction_id,
                "amount": amount,
                "currency": currency,
                "merchant_id": merchant_id,
                "status": "completed",
            },
            latency_ms=elapsed,
        )

    def health_check(self) -> HealthReport:
        latency = random.uniform(5, 30)
        return HealthReport(
            status=HealthStatus.HEALTHY,
            latency_ms=latency,
            message="Payment gateway responding normally",
        )


# ---------------------------------------------------------------------------
# Lending
# ---------------------------------------------------------------------------

class LendingCapability(Capability):
    """Evaluates credit-worthiness and generates loan proposals."""

    @property
    def name(self) -> str:
        return "lending"

    @property
    def sla_response_time_ms(self) -> float:
        return 500.0

    @property
    def tags(self) -> list[str]:
        return ["lending", "credit", "financing"]

    def execute(self, request: dict[str, Any]) -> ExecutionResult:
        start = time.monotonic()

        merchant_id: str = request.get("merchant_id", "unknown")
        monthly_revenue: float = request.get("monthly_revenue", 0.0)
        requested_amount: float = request.get("requested_amount", 0.0)
        business_months: int = request.get("business_months", 0)

        time.sleep(random.uniform(0.02, 0.08))

        # Simple credit scoring simulation
        credit_score = min(100, int(
            (monthly_revenue / 1000) * 10
            + business_months * 2
        ))
        approved = credit_score >= 40 and requested_amount <= monthly_revenue * 6

        if not approved:
            elapsed = (time.monotonic() - start) * 1000
            return ExecutionResult(
                success=True,
                data={
                    "merchant_id": merchant_id,
                    "credit_score": credit_score,
                    "approved": False,
                    "reason": "insufficient_credit_score"
                    if credit_score < 40
                    else "amount_exceeds_limit",
                },
                latency_ms=elapsed,
            )

        # Generate a loan proposal
        interest_rate = max(3.5, 15.0 - credit_score * 0.1)
        term_months = 12 if requested_amount < monthly_revenue * 3 else 24

        elapsed = (time.monotonic() - start) * 1000
        return ExecutionResult(
            success=True,
            data={
                "merchant_id": merchant_id,
                "credit_score": credit_score,
                "approved": True,
                "loan_proposal": {
                    "amount": requested_amount,
                    "interest_rate_pct": round(interest_rate, 2),
                    "term_months": term_months,
                    "monthly_payment": round(
                        requested_amount
                        * (1 + interest_rate / 100)
                        / term_months,
                        2,
                    ),
                },
            },
            latency_ms=elapsed,
        )

    def health_check(self) -> HealthReport:
        latency = random.uniform(10, 60)
        return HealthReport(
            status=HealthStatus.HEALTHY,
            latency_ms=latency,
            message="Credit engine nominal",
        )


# ---------------------------------------------------------------------------
# Card Issuing
# ---------------------------------------------------------------------------

class CardIssuingCapability(Capability):
    """Issues virtual or physical cards for merchants."""

    @property
    def name(self) -> str:
        return "card_issuing"

    @property
    def sla_response_time_ms(self) -> float:
        return 300.0

    @property
    def tags(self) -> list[str]:
        return ["card", "issuing", "payment"]

    def execute(self, request: dict[str, Any]) -> ExecutionResult:
        start = time.monotonic()

        merchant_id: str = request.get("merchant_id", "unknown")
        card_type: str = request.get("card_type", "virtual")  # virtual | physical
        spending_limit: float = request.get("spending_limit", 5000.0)

        time.sleep(random.uniform(0.01, 0.04))

        card_number_suffix = f"{random.randint(1000, 9999)}"
        elapsed = (time.monotonic() - start) * 1000
        return ExecutionResult(
            success=True,
            data={
                "merchant_id": merchant_id,
                "card_id": uuid.uuid4().hex[:16],
                "card_type": card_type,
                "last_four": card_number_suffix,
                "spending_limit": spending_limit,
                "status": "active",
            },
            latency_ms=elapsed,
        )

    def health_check(self) -> HealthReport:
        latency = random.uniform(8, 40)
        return HealthReport(
            status=HealthStatus.HEALTHY,
            latency_ms=latency,
            message="Card issuing service operational",
        )


# ---------------------------------------------------------------------------
# Buy Now Pay Later (BNPL)
# ---------------------------------------------------------------------------

class BNPLCapability(Capability):
    """Provides Buy Now Pay Later instalment plans."""

    @property
    def name(self) -> str:
        return "bnpl"

    @property
    def sla_response_time_ms(self) -> float:
        return 250.0

    @property
    def tags(self) -> list[str]:
        return ["bnpl", "instalment", "financing", "payment"]

    def execute(self, request: dict[str, Any]) -> ExecutionResult:
        start = time.monotonic()

        order_amount: float = request.get("order_amount", 0.0)
        customer_id: str = request.get("customer_id", "unknown")
        instalments: int = request.get("instalments", 4)

        time.sleep(random.uniform(0.01, 0.04))

        if order_amount < 10 or order_amount > 10_000:
            elapsed = (time.monotonic() - start) * 1000
            return ExecutionResult(
                success=False,
                error="order_amount_out_of_range",
                latency_ms=elapsed,
            )

        per_instalment = round(order_amount / instalments, 2)
        elapsed = (time.monotonic() - start) * 1000
        return ExecutionResult(
            success=True,
            data={
                "plan_id": uuid.uuid4().hex[:12],
                "customer_id": customer_id,
                "order_amount": order_amount,
                "instalments": instalments,
                "per_instalment": per_instalment,
                "fee_pct": 0.0,
                "status": "active",
            },
            latency_ms=elapsed,
        )

    def health_check(self) -> HealthReport:
        latency = random.uniform(5, 25)
        return HealthReport(
            status=HealthStatus.HEALTHY,
            latency_ms=latency,
            message="BNPL engine ready",
        )
