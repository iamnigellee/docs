"""BlockIntel World Model — data model definitions.

Canonical data structures shared by the Company World Model and the
Customer World Model.  Every struct is a frozen dataclass so it can be
safely passed across async boundaries without defensive copies.
"""

from __future__ import annotations

import random
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Organisation role enum
# ---------------------------------------------------------------------------

class OrganizationRole(Enum):
    """Flat-organisation roles inspired by Block's player-coach model."""

    IC = "Individual Contributor"
    DRI = "Directly Responsible Individual"
    PLAYER_COACH = "Player Coach"

    @property
    def description(self) -> str:
        _desc: dict[str, str] = {
            "IC": (
                "Executes hands-on work; empowered to make local decisions "
                "using context from the Company World Model."
            ),
            "DRI": (
                "Owns a specific outcome end-to-end; the single accountable "
                "person for cross-functional delivery."
            ),
            "PLAYER_COACH": (
                "Contributes individually while also unblocking others; "
                "replaces traditional middle-management oversight."
            ),
        }
        return _desc[self.name]


# ---------------------------------------------------------------------------
# Company-side data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Decision:
    """A recorded organisational decision."""

    id: str
    title: str
    context: str
    outcome: str
    timestamp: datetime
    participants: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class BuildStatus:
    """Current build / project progress."""

    project: str
    progress_pct: float
    blockers: list[str] = field(default_factory=list)
    version: str = "0.0.1"


@dataclass(frozen=True)
class ResourceAllocation:
    """Resource allocation snapshot for a team."""

    team: str
    budget: float
    headcount: int
    priority: int  # 1 = highest


# ---------------------------------------------------------------------------
# Customer-side data models
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Transaction:
    """A single buyer-seller transaction (dual-sided)."""

    id: str
    buyer_id: str
    seller_id: str
    amount: float
    category: str
    timestamp: datetime
    location: str = ""


@dataclass(frozen=True)
class MerchantProfile:
    """Aggregate merchant profile built from Square-side data."""

    id: str
    name: str
    industry: str
    monthly_revenue: float
    employee_count: int
    location: str
    risk_score: float = 0.0  # 0.0 (safe) – 1.0 (high risk)


@dataclass(frozen=True)
class ConsumerProfile:
    """Aggregate consumer profile built from Cash App-side data."""

    id: str
    spending_pattern: dict[str, float] = field(default_factory=dict)
    income_cycle: str = "monthly"  # monthly | biweekly | irregular
    savings_rate: float = 0.0


@dataclass(frozen=True)
class Signal:
    """An extracted honest signal ready for the intelligence layer."""

    type: str  # e.g. "cashflow_warning", "growth_opportunity"
    source: str  # e.g. "transaction_analysis", "merchant_trend"
    confidence: float  # 0.0 – 1.0
    timestamp: datetime
    merchant_id: str = ""
    details: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Simulated data generators
# ---------------------------------------------------------------------------

_INDUSTRIES = [
    "food_and_beverage", "retail", "professional_services",
    "health_and_beauty", "construction", "logistics",
]
_CATEGORIES = [
    "groceries", "electronics", "dining", "entertainment",
    "utilities", "transport", "health", "education",
]
_LOCATIONS = [
    "San Francisco, CA", "New York, NY", "Austin, TX",
    "Chicago, IL", "Miami, FL", "Seattle, WA", "Denver, CO",
]
_PROJECT_NAMES = [
    "payment-gateway-v3", "risk-engine-rewrite", "onboarding-flow",
    "merchant-dashboard", "cash-app-savings", "compliance-audit",
]


def _ts(days_ago_max: int = 90) -> datetime:
    """Return a random recent UTC timestamp."""
    return datetime.now(timezone.utc) - timedelta(
        days=random.randint(0, days_ago_max),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )


def generate_decisions(n: int = 5) -> list[Decision]:
    """Generate *n* plausible organisational decisions."""
    titles = [
        "Migrate to event-driven architecture",
        "Adopt BNPL for mid-market merchants",
        "Deprecate legacy POS integration",
        "Launch Cash App savings goals",
        "Hire 10 ML engineers for risk team",
        "Open Latin America payments corridor",
        "Switch CI to Bazel monorepo build",
        "Implement real-time fraud scoring",
    ]
    return [
        Decision(
            id=str(uuid.uuid4()),
            title=random.choice(titles),
            context=f"Discussed in cross-functional review on {_ts().date()}",
            outcome=random.choice(["approved", "deferred", "in_progress"]),
            timestamp=_ts(),
            participants=[f"emp-{random.randint(100, 999)}" for _ in range(random.randint(2, 6))],
        )
        for _ in range(n)
    ]


def generate_build_statuses(n: int = 4) -> list[BuildStatus]:
    """Generate *n* build status snapshots."""
    blockers_pool = [
        "waiting on API spec from partner",
        "CI flaky test: test_payment_timeout",
        "security review pending",
        "dependency bump blocked by CVE-2026-1234",
        "",
    ]
    return [
        BuildStatus(
            project=random.choice(_PROJECT_NAMES),
            progress_pct=round(random.uniform(5, 100), 1),
            blockers=[b for b in random.sample(blockers_pool, k=random.randint(0, 2)) if b],
            version=f"{random.randint(0,3)}.{random.randint(0,9)}.{random.randint(0,20)}",
        )
        for _ in range(n)
    ]


def generate_resource_allocations(n: int = 3) -> list[ResourceAllocation]:
    teams = ["payments", "risk", "growth", "platform", "ml-infra", "compliance"]
    return [
        ResourceAllocation(
            team=random.choice(teams),
            budget=round(random.uniform(100_000, 5_000_000), 2),
            headcount=random.randint(3, 40),
            priority=random.randint(1, 5),
        )
        for _ in range(n)
    ]


def generate_transactions(n: int = 20) -> list[Transaction]:
    """Generate *n* dual-sided transactions."""
    return [
        Transaction(
            id=str(uuid.uuid4()),
            buyer_id=f"consumer-{random.randint(1000, 9999)}",
            seller_id=f"merchant-{random.randint(100, 999)}",
            amount=round(random.uniform(1.50, 2500.00), 2),
            category=random.choice(_CATEGORIES),
            timestamp=_ts(days_ago_max=30),
            location=random.choice(_LOCATIONS),
        )
        for _ in range(n)
    ]


def generate_merchant_profiles(n: int = 5) -> list[MerchantProfile]:
    names = [
        "Corner Brew Coffee", "QuickFix Auto", "Bloom Florist",
        "UrbanBite Kitchen", "CodeCraft Consulting", "FreshMart Groceries",
        "Peak Fitness Studio", "Noodle House Express",
    ]
    return [
        MerchantProfile(
            id=f"merchant-{random.randint(100, 999)}",
            name=random.choice(names),
            industry=random.choice(_INDUSTRIES),
            monthly_revenue=round(random.uniform(8_000, 500_000), 2),
            employee_count=random.randint(1, 120),
            location=random.choice(_LOCATIONS),
            risk_score=round(random.uniform(0, 1), 3),
        )
        for _ in range(n)
    ]


def generate_consumer_profiles(n: int = 5) -> list[ConsumerProfile]:
    return [
        ConsumerProfile(
            id=f"consumer-{random.randint(1000, 9999)}",
            spending_pattern={
                cat: round(random.uniform(20, 800), 2)
                for cat in random.sample(_CATEGORIES, k=random.randint(2, 5))
            },
            income_cycle=random.choice(["monthly", "biweekly", "irregular"]),
            savings_rate=round(random.uniform(0, 0.35), 3),
        )
        for _ in range(n)
    ]


def generate_signals(n: int = 6) -> list[Signal]:
    signal_types = [
        "cashflow_warning", "growth_opportunity", "churn_risk",
        "seasonal_spike", "fraud_suspicion", "cross_sell_ready",
    ]
    return [
        Signal(
            type=random.choice(signal_types),
            source=random.choice(["transaction_analysis", "merchant_trend", "consumer_behaviour"]),
            confidence=round(random.uniform(0.4, 0.99), 3),
            timestamp=_ts(days_ago_max=7),
            merchant_id=f"merchant-{random.randint(100, 999)}",
            details={"summary": "Auto-generated simulation signal"},
        )
        for _ in range(n)
    ]
