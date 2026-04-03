"""BlockIntel World Model -- Customer World Model.

Models the financial reality of every customer, merchant, and market.
Combines Cash App consumer behaviour with Square merchant operations
to form a dual-sided economic graph.  Extracts "honest signals" from
transaction data -- spending behaviour does not lie -- and builds
compounding value that deepens with every interaction.

Data sources
------------
- **Consumer behaviour** (Cash App side): spending patterns, income cycles, savings habits
- **Merchant operations** (Square side): revenue trends, inventory turnover, employee costs
- **Dual-sided transactions**: buyer + seller visible simultaneously, forming a complete
  economic graph

Output examples
---------------
- Merchant cash-flow early-warning before a shortfall hits
- Post-relocation account reconfiguration for a consumer who moved cities
- Timely lending / cash-advance offers surfaced at the right moment
"""

from __future__ import annotations

import logging
import math
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from .data_models import (
    ConsumerProfile,
    MerchantProfile,
    Signal,
    Transaction,
    generate_consumer_profiles,
    generate_merchant_profiles,
    generate_signals,
    generate_transactions,
)
from .event_bus import EventBus

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helper result types
# ---------------------------------------------------------------------------

@dataclass
class HonestSignalReport:
    """Bundle of honest signals extracted from raw transactions."""

    merchant_id: str | None
    signals: list[Signal]
    transaction_count: int
    analysis_window_days: int
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CompoundValueScore:
    """Quantifies the compounding value a merchant derives from the platform."""

    merchant_id: str
    tenure_months: float
    data_depth_score: float       # 0-1: how rich the behavioural data is
    product_penetration: float    # 0-1: fraction of platform products adopted
    switching_cost_index: float   # 0-1: estimated difficulty of leaving
    composite_score: float        # weighted aggregate
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CausalPrediction:
    """A forward-looking causal prediction about a merchant's trajectory."""

    merchant_id: str
    prediction_type: str   # e.g. "cashflow_shortfall", "growth_inflection"
    probability: float     # 0-1
    time_horizon_days: int
    recommended_action: str
    supporting_signals: list[Signal] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Customer World Model
# ---------------------------------------------------------------------------

class CustomerWorldModel:
    """Dual-sided economic model spanning consumers and merchants.

    Core capabilities
    -----------------
    1. ``extract_honest_signals`` -- behavioural signals that cannot be faked
    2. ``compute_compound_value`` -- the deeper the usage, the harder to replicate
    3. ``predict_causality``      -- move from description to prediction
    """

    def __init__(
        self,
        event_bus: EventBus | None = None,
        company_model: Any | None = None,
    ) -> None:
        self._merchants: dict[str, MerchantProfile] = {}
        self._consumers: dict[str, ConsumerProfile] = {}
        self._transactions: list[Transaction] = []

        # Optional back-link to the Company World Model so we can query
        # internal capacity / active projects when composing solutions.
        self._company_model = company_model

        self.event_bus: EventBus = event_bus or EventBus()

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def ingest_merchants(self, profiles: list[MerchantProfile]) -> None:
        for p in profiles:
            self._merchants[p.id] = p
        logger.info("Ingested %d merchant profiles (total: %d)", len(profiles), len(self._merchants))

    def ingest_consumers(self, profiles: list[ConsumerProfile]) -> None:
        for p in profiles:
            self._consumers[p.id] = p
        logger.info("Ingested %d consumer profiles (total: %d)", len(profiles), len(self._consumers))

    def ingest_transactions(self, txns: list[Transaction]) -> None:
        self._transactions.extend(txns)
        logger.info("Ingested %d transactions (total: %d)", len(txns), len(self._transactions))

    # ------------------------------------------------------------------
    # 1. Honest signal extraction
    # ------------------------------------------------------------------

    def extract_honest_signals(
        self,
        transactions: list[Transaction] | None = None,
        window_days: int = 30,
    ) -> list[HonestSignalReport]:
        """Derive honest signals from transaction data.

        "Honest" because spending behaviour cannot be fabricated -- it is
        a direct reflection of economic reality.

        Analyses performed per merchant:
        - Revenue trend (growing / declining / volatile)
        - Average ticket size anomalies
        - Transaction frequency shifts
        - Category concentration risk
        """
        txns = transactions if transactions is not None else self._transactions
        if not txns:
            return []

        cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
        recent = [t for t in txns if t.timestamp.replace(tzinfo=timezone.utc) >= cutoff]

        # Group by seller (merchant)
        by_merchant: dict[str, list[Transaction]] = defaultdict(list)
        for t in recent:
            by_merchant[t.seller_id].append(t)

        reports: list[HonestSignalReport] = []

        for merchant_id, mtxns in by_merchant.items():
            signals: list[Signal] = []
            amounts = [t.amount for t in mtxns]
            now = datetime.now(timezone.utc)

            # --- Revenue trend ---
            if len(amounts) >= 3:
                first_half = amounts[: len(amounts) // 2]
                second_half = amounts[len(amounts) // 2 :]
                avg_first = statistics.mean(first_half)
                avg_second = statistics.mean(second_half)
                if avg_first > 0:
                    change_pct = (avg_second - avg_first) / avg_first
                    if change_pct < -0.20:
                        signals.append(Signal(
                            type="cashflow_warning",
                            source="transaction_analysis",
                            confidence=min(0.95, 0.6 + abs(change_pct)),
                            timestamp=now,
                            merchant_id=merchant_id,
                            details={
                                "change_pct": round(change_pct, 3),
                                "summary": f"Revenue declined ~{abs(change_pct)*100:.0f}% within window",
                            },
                        ))
                    elif change_pct > 0.25:
                        signals.append(Signal(
                            type="growth_opportunity",
                            source="transaction_analysis",
                            confidence=min(0.95, 0.5 + change_pct),
                            timestamp=now,
                            merchant_id=merchant_id,
                            details={
                                "change_pct": round(change_pct, 3),
                                "summary": f"Revenue grew ~{change_pct*100:.0f}% within window",
                            },
                        ))

            # --- Ticket-size anomaly ---
            if len(amounts) >= 5:
                mean_amt = statistics.mean(amounts)
                stdev_amt = statistics.stdev(amounts)
                if stdev_amt > 0:
                    latest_avg = statistics.mean(amounts[-3:])
                    z_score = (latest_avg - mean_amt) / stdev_amt
                    if abs(z_score) > 1.8:
                        signals.append(Signal(
                            type="ticket_anomaly",
                            source="transaction_analysis",
                            confidence=round(min(0.95, 0.5 + abs(z_score) * 0.15), 3),
                            timestamp=now,
                            merchant_id=merchant_id,
                            details={
                                "z_score": round(z_score, 2),
                                "summary": f"Average ticket size deviates {z_score:.1f} sigma from mean",
                            },
                        ))

            # --- Category concentration risk ---
            categories = [t.category for t in mtxns]
            if categories:
                top_cat_ratio = max(categories.count(c) for c in set(categories)) / len(categories)
                if top_cat_ratio > 0.80:
                    signals.append(Signal(
                        type="concentration_risk",
                        source="transaction_analysis",
                        confidence=round(top_cat_ratio, 3),
                        timestamp=now,
                        merchant_id=merchant_id,
                        details={"top_category_ratio": round(top_cat_ratio, 3)},
                    ))

            reports.append(HonestSignalReport(
                merchant_id=merchant_id,
                signals=signals,
                transaction_count=len(mtxns),
                analysis_window_days=window_days,
            ))

        return reports

    # ------------------------------------------------------------------
    # 2. Compound value computation
    # ------------------------------------------------------------------

    def compute_compound_value(self, merchant_id: str) -> CompoundValueScore:
        """Quantify the compounding value that a merchant accumulates.

        The longer and deeper a merchant uses the platform, the more
        valuable the data becomes -- and the harder it is for a
        competitor to replicate.
        """
        merchant = self._merchants.get(merchant_id)
        txns = [t for t in self._transactions if t.seller_id == merchant_id]

        # Tenure (simulated: based on earliest transaction)
        if txns:
            earliest = min(t.timestamp for t in txns)
            tenure_days = (datetime.now(timezone.utc) - earliest.replace(tzinfo=timezone.utc)).days
        else:
            tenure_days = 0
        tenure_months = tenure_days / 30.0

        # Data depth: more transactions + more categories = richer signal
        unique_categories = len({t.category for t in txns})
        data_depth = min(1.0, (len(txns) / 100.0) * 0.5 + (unique_categories / 8.0) * 0.5)

        # Product penetration (simulated heuristic)
        product_signals = 0
        if txns:
            product_signals += 1  # uses payments
        if merchant and merchant.employee_count > 5:
            product_signals += 1  # likely uses payroll
        if merchant and merchant.monthly_revenue > 50_000:
            product_signals += 1  # likely uses lending / cash advance
        product_penetration = min(1.0, product_signals / 4.0)

        # Switching cost (logarithmic growth with tenure and depth)
        switching_cost = min(1.0, 0.2 * math.log1p(tenure_months) + 0.3 * data_depth + 0.2 * product_penetration)

        # Composite (weighted)
        composite = round(
            0.25 * min(1.0, tenure_months / 24)
            + 0.30 * data_depth
            + 0.20 * product_penetration
            + 0.25 * switching_cost,
            4,
        )

        return CompoundValueScore(
            merchant_id=merchant_id,
            tenure_months=round(tenure_months, 1),
            data_depth_score=round(data_depth, 4),
            product_penetration=round(product_penetration, 4),
            switching_cost_index=round(switching_cost, 4),
            composite_score=composite,
        )

    # ------------------------------------------------------------------
    # 3. Causal prediction
    # ------------------------------------------------------------------

    def predict_causality(self, merchant_data: MerchantProfile | None = None, merchant_id: str | None = None) -> list[CausalPrediction]:
        """Move from *describing* to *predicting*.

        Uses merchant profile + transaction history + honest signals to
        generate forward-looking causal predictions.
        """
        mid = merchant_id or (merchant_data.id if merchant_data else None)
        if mid is None:
            return []

        merchant = merchant_data or self._merchants.get(mid)
        if merchant is None:
            return []

        predictions: list[CausalPrediction] = []
        txns = [t for t in self._transactions if t.seller_id == mid]
        amounts = [t.amount for t in txns]

        # --- Cash-flow shortfall prediction ---
        if amounts:
            recent_avg = statistics.mean(amounts[-max(1, len(amounts) // 4) :])
            overall_avg = statistics.mean(amounts)
            if overall_avg > 0 and recent_avg < overall_avg * 0.70:
                shortfall_prob = min(0.95, 0.5 + (1 - recent_avg / overall_avg))
                predictions.append(CausalPrediction(
                    merchant_id=mid,
                    prediction_type="cashflow_shortfall",
                    probability=round(shortfall_prob, 3),
                    time_horizon_days=30,
                    recommended_action=(
                        "Proactively offer short-term cash advance or "
                        "flexible payment schedule to bridge shortfall."
                    ),
                ))

        # --- Growth inflection prediction ---
        if len(amounts) >= 6:
            recent_avg = statistics.mean(amounts[-3:])
            older_avg = statistics.mean(amounts[:-3])
            if older_avg > 0 and recent_avg > older_avg * 1.40:
                growth_prob = min(0.90, 0.4 + (recent_avg / older_avg - 1) * 0.5)
                predictions.append(CausalPrediction(
                    merchant_id=mid,
                    prediction_type="growth_inflection",
                    probability=round(growth_prob, 3),
                    time_horizon_days=60,
                    recommended_action=(
                        "Surface expansion tools: additional POS hardware, "
                        "staff scheduling upgrade, or working-capital line."
                    ),
                ))

        # --- High-risk churn prediction ---
        if merchant and merchant.risk_score > 0.7:
            predictions.append(CausalPrediction(
                merchant_id=mid,
                prediction_type="churn_risk",
                probability=round(merchant.risk_score * 0.85, 3),
                time_horizon_days=90,
                recommended_action=(
                    "Trigger retention workflow: dedicated account review, "
                    "fee-waiver evaluation, success-manager outreach."
                ),
            ))

        # --- Seasonal dip (simple month-over-month) ---
        if txns and len(txns) >= 10:
            by_month: dict[int, list[float]] = defaultdict(list)
            for t in txns:
                by_month[t.timestamp.month].append(t.amount)
            current_month = datetime.now(timezone.utc).month
            current_avg = statistics.mean(by_month.get(current_month, [0.0]) or [0.0])
            all_avg = statistics.mean(amounts)
            if all_avg > 0 and current_avg < all_avg * 0.65:
                predictions.append(CausalPrediction(
                    merchant_id=mid,
                    prediction_type="seasonal_dip",
                    probability=round(min(0.85, 0.5 + (1 - current_avg / all_avg) * 0.5), 3),
                    time_horizon_days=45,
                    recommended_action=(
                        "Suggest seasonal marketing campaign or temporary "
                        "pricing adjustments to offset expected dip."
                    ),
                ))

        return predictions

    # ------------------------------------------------------------------
    # Cross-model interface (interacts with CompanyWorldModel)
    # ------------------------------------------------------------------

    def link_company_model(self, company_model: Any) -> None:
        """Establish a live link to the CompanyWorldModel.

        This allows the customer model to query internal resource
        availability when composing merchant solutions.
        """
        self._company_model = company_model

    def get_merchant_signals_for_company(self, severity_threshold: float = 0.6) -> list[Signal]:
        """Return high-confidence merchant signals that the company model
        should be aware of (e.g. for resource-allocation decisions)."""
        reports = self.extract_honest_signals()
        high_priority: list[Signal] = []
        for r in reports:
            for s in r.signals:
                if s.confidence >= severity_threshold:
                    high_priority.append(s)
        return high_priority

    def get_market_summary(self) -> dict[str, Any]:
        """Aggregate market-level statistics for cross-model consumption."""
        if not self._transactions:
            return {"total_transactions": 0}

        amounts = [t.amount for t in self._transactions]
        categories: dict[str, float] = defaultdict(float)
        for t in self._transactions:
            categories[t.category] += t.amount

        return {
            "total_transactions": len(self._transactions),
            "total_volume": round(sum(amounts), 2),
            "avg_ticket": round(statistics.mean(amounts), 2),
            "merchant_count": len(self._merchants),
            "consumer_count": len(self._consumers),
            "top_categories": dict(
                sorted(categories.items(), key=lambda kv: kv[1], reverse=True)[:5]
            ),
        }

    # ------------------------------------------------------------------
    # Event publishing helpers
    # ------------------------------------------------------------------

    async def publish_signals(self, signals: list[Signal]) -> None:
        """Push extracted signals onto the event bus for the intelligence layer."""
        for sig in signals:
            await self.event_bus.publish("signal.new", {
                "type": sig.type,
                "merchant_id": sig.merchant_id,
                "confidence": sig.confidence,
                "details": sig.details,
            })

    async def publish_prediction(self, prediction: CausalPrediction) -> None:
        """Push a causal prediction onto the event bus."""
        await self.event_bus.publish("prediction.new", {
            "merchant_id": prediction.merchant_id,
            "prediction_type": prediction.prediction_type,
            "probability": prediction.probability,
            "recommended_action": prediction.recommended_action,
        })

    # ------------------------------------------------------------------
    # Simulation helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_simulated_data(cls, event_bus: EventBus | None = None) -> CustomerWorldModel:
        """Bootstrap a model pre-loaded with realistic simulated data."""
        model = cls(event_bus=event_bus)
        model.ingest_merchants(generate_merchant_profiles(8))
        model.ingest_consumers(generate_consumer_profiles(15))
        model.ingest_transactions(generate_transactions(50))
        return model
