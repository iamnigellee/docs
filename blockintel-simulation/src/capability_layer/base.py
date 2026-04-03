"""Abstract base class for all BlockIntel capabilities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


@dataclass
class HealthReport:
    """Health check result for a capability."""

    status: HealthStatus
    latency_ms: float
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Standardised result returned by every capability execution."""

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    latency_ms: float = 0.0


class Capability(ABC):
    """Abstract base defining the SLA contract every capability must honour."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable capability name."""
        ...

    @property
    @abstractmethod
    def sla_response_time_ms(self) -> float:
        """Maximum response time (ms) promised by this capability's SLA."""
        ...

    @property
    def tags(self) -> list[str]:
        """Tags used for discovery in the registry (override to customise)."""
        return []

    @abstractmethod
    def execute(self, request: dict[str, Any]) -> ExecutionResult:
        """Run the core business logic for this capability."""
        ...

    @abstractmethod
    def health_check(self) -> HealthReport:
        """Return the current operational health of this capability."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name!r}>"
