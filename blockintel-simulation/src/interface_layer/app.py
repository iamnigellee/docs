"""FastAPI application — BlockIntel Interface Layer.

Serves API endpoints that expose dashboard data, capability health,
merchant signals, solution composition, world-model state, and
organizational role information.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from .models import (
    CapabilityHealth,
    CapabilityStatus,
    CompanyWorldState,
    ComposeRequest,
    CustomerProfile,
    DashboardResponse,
    MerchantOverview,
    OrganizationRole,
    RoleType,
    SignalReport,
    SignalSeverity,
    SignalSummary,
    SolutionProposal,
    SolutionStatus,
)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="BlockIntel",
    description="Intelligent Business Platform — Interface Layer",
    version="0.1.0",
)

# ---------------------------------------------------------------------------
# Mock data helpers
# ---------------------------------------------------------------------------

_NOW = datetime.utcnow()


def _mock_capabilities() -> list[CapabilityStatus]:
    return [
        CapabilityStatus(
            name="Payment Processing",
            health=CapabilityHealth.HEALTHY,
            latency_ms=45.2,
            throughput_rps=12500,
            error_rate=0.001,
            last_checked=_NOW,
        ),
        CapabilityStatus(
            name="Lending",
            health=CapabilityHealth.HEALTHY,
            latency_ms=120.8,
            throughput_rps=3200,
            error_rate=0.003,
            last_checked=_NOW,
        ),
        CapabilityStatus(
            name="Card Issuing",
            health=CapabilityHealth.DEGRADED,
            latency_ms=230.5,
            throughput_rps=1800,
            error_rate=0.015,
            last_checked=_NOW,
        ),
        CapabilityStatus(
            name="BNPL (Buy Now Pay Later)",
            health=CapabilityHealth.HEALTHY,
            latency_ms=98.1,
            throughput_rps=4100,
            error_rate=0.002,
            last_checked=_NOW,
        ),
        CapabilityStatus(
            name="Fraud Detection",
            health=CapabilityHealth.HEALTHY,
            latency_ms=15.3,
            throughput_rps=25000,
            error_rate=0.0005,
            last_checked=_NOW,
        ),
        CapabilityStatus(
            name="Invoicing",
            health=CapabilityHealth.DOWN,
            latency_ms=0,
            throughput_rps=0,
            error_rate=1.0,
            last_checked=_NOW - timedelta(minutes=12),
        ),
    ]


def _mock_signals(merchant_id: str = "M-1001") -> list[SignalReport]:
    return [
        SignalReport(
            signal_id="SIG-001",
            merchant_id=merchant_id,
            merchant_name="Sunrise Coffee",
            signal_type="cash_flow_anomaly",
            severity=SignalSeverity.HIGH,
            description="30-day rolling cash flow dropped 38% — potential seasonal dip or churn risk.",
            detected_at=_NOW - timedelta(hours=2),
            metadata={"drop_pct": 38, "baseline_avg": 42000},
        ),
        SignalReport(
            signal_id="SIG-002",
            merchant_id=merchant_id,
            merchant_name="Sunrise Coffee",
            signal_type="growth_spike",
            severity=SignalSeverity.MEDIUM,
            description="Online order volume up 120% week-over-week.",
            detected_at=_NOW - timedelta(hours=5),
            metadata={"wow_growth": 1.2},
        ),
        SignalReport(
            signal_id="SIG-003",
            merchant_id=merchant_id,
            merchant_name="Sunrise Coffee",
            signal_type="compliance_flag",
            severity=SignalSeverity.CRITICAL,
            description="KYC document expired — action required within 7 days.",
            detected_at=_NOW - timedelta(hours=1),
        ),
    ]


def _mock_solutions() -> list[SolutionProposal]:
    return [
        SolutionProposal(
            proposal_id="SOL-001",
            merchant_id="M-1001",
            merchant_name="Sunrise Coffee",
            title="Cash Flow Stabilisation Package",
            description="Combine short-term lending with flexible BNPL to bridge seasonal revenue gap.",
            capabilities_used=["Lending", "BNPL (Buy Now Pay Later)"],
            estimated_impact="Projected +$8,500/mo stabilisation",
            confidence=0.87,
            status=SolutionStatus.PROPOSED,
            created_at=_NOW - timedelta(hours=1),
        ),
        SolutionProposal(
            proposal_id="SOL-002",
            merchant_id="M-1002",
            merchant_name="Urban Threads Boutique",
            title="Growth Acceleration Bundle",
            description="Enable card issuing + advanced payment processing to capture omnichannel growth.",
            capabilities_used=["Card Issuing", "Payment Processing"],
            estimated_impact="Projected +22% transaction volume",
            confidence=0.74,
            status=SolutionStatus.APPROVED,
            created_at=_NOW - timedelta(hours=6),
        ),
        SolutionProposal(
            proposal_id="SOL-003",
            merchant_id="M-1003",
            merchant_name="FreshBite Delivery",
            title="Fraud Shield Pro",
            description="Deploy enhanced fraud detection with real-time scoring for high-volume delivery orders.",
            capabilities_used=["Fraud Detection", "Payment Processing"],
            estimated_impact="Estimated $12,000/mo fraud savings",
            confidence=0.92,
            status=SolutionStatus.DEPLOYED,
            created_at=_NOW - timedelta(days=2),
        ),
    ]


def _mock_roles() -> list[OrganizationRole]:
    return [
        OrganizationRole(
            role_type=RoleType.IC,
            title="Individual Contributor",
            description="Autonomous specialist who owns a capability end-to-end without managerial overhead.",
            responsibilities=[
                "Own capability design, implementation, and SLA",
                "Collaborate directly with peers across layers",
                "Ship incremental improvements continuously",
                "Maintain technical documentation",
            ],
            current_holders=142,
        ),
        OrganizationRole(
            role_type=RoleType.DRI,
            title="Directly Responsible Individual",
            description="Single point of accountability for a cross-cutting initiative or decision.",
            responsibilities=[
                "Drive decisions without consensus-seeking paralysis",
                "Coordinate across capability boundaries",
                "Report outcomes, not activity",
                "Escalate only true blockers",
            ],
            current_holders=28,
        ),
        OrganizationRole(
            role_type=RoleType.PLAYER_COACH,
            title="Player Coach",
            description="Hands-on leader who writes code AND mentors — replacing traditional middle management.",
            responsibilities=[
                "Contribute production code alongside the team",
                "Mentor ICs through pairing and code review",
                "Remove organizational friction",
                "Translate company strategy into capability roadmaps",
            ],
            current_holders=15,
        ),
    ]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/dashboard", response_model=DashboardResponse)
async def get_dashboard() -> DashboardResponse:
    """Return aggregated dashboard data: merchants, signals, solutions, capabilities, roles."""
    return DashboardResponse(
        merchant_overview=MerchantOverview(
            total=1284,
            active=1130,
            at_risk=47,
            high_growth=203,
        ),
        signal_summary=SignalSummary(
            total=312,
            critical=8,
            high=34,
            medium=127,
            low=143,
        ),
        recommended_solutions=_mock_solutions(),
        capability_statuses=_mock_capabilities(),
        organization_roles=_mock_roles(),
        generated_at=_NOW,
    )


@app.get("/api/capabilities", response_model=List[CapabilityStatus])
async def get_capabilities() -> list[CapabilityStatus]:
    """List every registered capability with its current health status."""
    return _mock_capabilities()


@app.get("/api/signals/{merchant_id}", response_model=List[SignalReport])
async def get_signals(merchant_id: str) -> list[SignalReport]:
    """Return detected signals for a given merchant."""
    signals = _mock_signals(merchant_id)
    if not signals:
        raise HTTPException(status_code=404, detail=f"No signals found for merchant {merchant_id}")
    return signals


@app.post("/api/solutions/compose", response_model=SolutionProposal)
async def compose_solution(req: ComposeRequest) -> SolutionProposal:
    """Trigger the intelligence layer to compose a new solution for the merchant."""
    return SolutionProposal(
        proposal_id=f"SOL-{uuid4().hex[:6].upper()}",
        merchant_id=req.merchant_id,
        merchant_name="Dynamic Merchant",
        title="AI-Composed Solution",
        description=(
            f"Automatically composed solution using capabilities: "
            f"{', '.join(req.preferred_capabilities) or 'auto-selected'}."
        ),
        capabilities_used=req.preferred_capabilities or ["Payment Processing", "Lending"],
        estimated_impact="Pending detailed analysis",
        confidence=0.65,
        status=SolutionStatus.PROPOSED,
    )


@app.get("/api/world-model/company", response_model=CompanyWorldState)
async def get_company_world_state() -> CompanyWorldState:
    """Return the current company-level world model snapshot."""
    caps = _mock_capabilities()
    return CompanyWorldState(
        total_merchants=1284,
        active_merchants=1130,
        total_revenue_30d=4_870_000.0,
        capability_count=len(caps),
        capabilities_healthy=sum(1 for c in caps if c.health == CapabilityHealth.HEALTHY),
        pending_signals=312,
        active_solutions=3,
        last_updated=_NOW,
    )


@app.get("/api/world-model/customer/{merchant_id}", response_model=CustomerProfile)
async def get_customer_profile(merchant_id: str) -> CustomerProfile:
    """Return the world-model profile for a single merchant."""
    signals = _mock_signals(merchant_id)
    solutions = [s for s in _mock_solutions() if s.merchant_id == merchant_id]
    return CustomerProfile(
        merchant_id=merchant_id,
        merchant_name="Sunrise Coffee",
        industry="Food & Beverage",
        monthly_volume=142_000.0,
        active_capabilities=["Payment Processing", "Lending", "BNPL (Buy Now Pay Later)"],
        risk_score=0.34,
        growth_score=0.72,
        signals=signals,
        recommended_solutions=solutions,
        last_updated=_NOW,
    )


@app.get("/api/organization/roles", response_model=List[OrganizationRole])
async def get_organization_roles() -> list[OrganizationRole]:
    """Return the three organizational role archetypes and their counts."""
    return _mock_roles()


# ---------------------------------------------------------------------------
# Dashboard HTML
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard() -> HTMLResponse:
    """Serve the single-page HTML dashboard."""
    html_path = Path(__file__).parent / "dashboard.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))
