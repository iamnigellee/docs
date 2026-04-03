"""Pydantic data models for the BlockIntel Interface Layer API."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class CapabilityHealth(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class SignalSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RoleType(str, Enum):
    IC = "IC"
    DRI = "DRI"
    PLAYER_COACH = "Player Coach"


class SolutionStatus(str, Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Core Models
# ---------------------------------------------------------------------------

class CapabilityStatus(BaseModel):
    """Health and metadata for a single business capability."""

    name: str = Field(..., description="Capability name, e.g. 'Payment Processing'")
    health: CapabilityHealth = Field(default=CapabilityHealth.HEALTHY)
    latency_ms: float = Field(..., ge=0, description="P95 latency in milliseconds")
    throughput_rps: float = Field(..., ge=0, description="Requests per second")
    error_rate: float = Field(default=0.0, ge=0, le=1, description="Error rate 0-1")
    last_checked: datetime = Field(default_factory=datetime.utcnow)


class SignalReport(BaseModel):
    """A detected signal for a specific merchant."""

    signal_id: str
    merchant_id: str
    merchant_name: str
    signal_type: str = Field(..., description="E.g. 'cash_flow_anomaly', 'growth_spike'")
    severity: SignalSeverity
    description: str
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, object] = Field(default_factory=dict)


class SolutionProposal(BaseModel):
    """A composed solution proposed by the intelligence layer."""

    proposal_id: str
    merchant_id: str
    merchant_name: str
    title: str
    description: str
    capabilities_used: list[str] = Field(default_factory=list)
    estimated_impact: str
    confidence: float = Field(..., ge=0, le=1)
    status: SolutionStatus = Field(default=SolutionStatus.PROPOSED)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CompanyWorldState(BaseModel):
    """Snapshot of the company-level world model."""

    total_merchants: int
    active_merchants: int
    total_revenue_30d: float
    capability_count: int
    capabilities_healthy: int
    pending_signals: int
    active_solutions: int
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class CustomerProfile(BaseModel):
    """World-model representation of a single merchant / customer."""

    merchant_id: str
    merchant_name: str
    industry: str
    monthly_volume: float
    active_capabilities: list[str] = Field(default_factory=list)
    risk_score: float = Field(default=0.0, ge=0, le=1)
    growth_score: float = Field(default=0.0, ge=0, le=1)
    signals: list[SignalReport] = Field(default_factory=list)
    recommended_solutions: list[SolutionProposal] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.utcnow)


class OrganizationRole(BaseModel):
    """A role within Block's flat organizational model."""

    role_type: RoleType
    title: str
    description: str
    responsibilities: list[str] = Field(default_factory=list)
    current_holders: int = Field(default=0, ge=0)


# ---------------------------------------------------------------------------
# Composite / Response Models
# ---------------------------------------------------------------------------

class MerchantOverview(BaseModel):
    total: int
    active: int
    at_risk: int
    high_growth: int


class SignalSummary(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int


class DashboardResponse(BaseModel):
    """Top-level response for the dashboard endpoint."""

    merchant_overview: MerchantOverview
    signal_summary: SignalSummary
    recommended_solutions: list[SolutionProposal] = Field(default_factory=list)
    capability_statuses: list[CapabilityStatus] = Field(default_factory=list)
    organization_roles: list[OrganizationRole] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ComposeRequest(BaseModel):
    """Request body for the solution composition endpoint."""

    merchant_id: str
    signal_ids: list[str] = Field(default_factory=list)
    preferred_capabilities: list[str] = Field(default_factory=list)
    budget_limit: Optional[float] = None
