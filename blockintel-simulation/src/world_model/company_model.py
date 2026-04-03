"""BlockIntel World Model — Company World Model.

Replaces traditional management information-routing with a continuously
updated organisational knowledge graph.  Every employee (IC, DRI, or
Player Coach) can query the model directly to obtain full context,
automatic alignment state, and blocker visibility — eliminating status
meetings and management bottlenecks.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .data_models import (
    BuildStatus,
    Decision,
    OrganizationRole,
    ResourceAllocation,
    generate_build_statuses,
    generate_decisions,
    generate_resource_allocations,
)
from .event_bus import EventBus

logger = logging.getLogger(__name__)


@dataclass
class EmployeeContext:
    """Personalised context snapshot delivered to a single employee."""

    employee_id: str
    role: OrganizationRole
    relevant_decisions: list[Decision]
    build_statuses: list[BuildStatus]
    resource_view: list[ResourceAllocation]
    active_blockers: list[str]
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AlignmentReport:
    """Result of an automatic alignment check across teams."""

    team_ids: list[str]
    shared_priorities: list[str]
    conflicts: list[str]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Blocker:
    """A detected organisational or technical blocker."""

    id: str
    project: str
    description: str
    severity: str  # "critical" | "high" | "medium" | "low"
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CompanyWorldModel:
    """Cognitive model of the entire organisation.

    Data sources
    ------------
    - **Decision records** — discussions, designs, plans
    - **Code & build status** — progress, blockers, versions
    - **Resources & performance** — allocation, effectiveness, priorities

    The model exposes three core management-replacement functions:

    1. ``provide_context`` — any employee gets full global context
    2. ``auto_align`` — cross-team alignment without status meetings
    3. ``detect_blockers`` — automatic blocker discovery & escalation
    """

    def __init__(self, event_bus: EventBus | None = None) -> None:
        self._decisions: list[Decision] = []
        self._build_statuses: list[BuildStatus] = []
        self._resources: list[ResourceAllocation] = []

        # employee_id → role mapping
        self._roles: dict[str, OrganizationRole] = {}

        self.event_bus: EventBus = event_bus or EventBus()

    # ------------------------------------------------------------------
    # Data ingestion
    # ------------------------------------------------------------------

    def ingest_decisions(self, decisions: list[Decision]) -> None:
        self._decisions.extend(decisions)
        logger.info("Ingested %d decisions (total: %d)", len(decisions), len(self._decisions))

    def ingest_build_statuses(self, statuses: list[BuildStatus]) -> None:
        self._build_statuses.extend(statuses)

    def ingest_resources(self, allocations: list[ResourceAllocation]) -> None:
        self._resources.extend(allocations)

    def register_employee(self, employee_id: str, role: OrganizationRole) -> None:
        self._roles[employee_id] = role

    # ------------------------------------------------------------------
    # Core management-replacement functions
    # ------------------------------------------------------------------

    def provide_context(self, employee_id: str) -> EmployeeContext:
        """Return a full context snapshot for *employee_id*.

        Replaces: weekly 1-on-1s, status emails, "what's going on?" Slack pings.
        """
        role = self._roles.get(employee_id, OrganizationRole.IC)

        # Filter decisions relevant to the employee (in a real system this
        # would use an embedding-based relevance model).
        relevant = [
            d for d in self._decisions
            if employee_id in d.participants or role == OrganizationRole.DRI
        ]
        # Fallback: if nothing matched, surface the most recent decisions.
        if not relevant:
            relevant = sorted(self._decisions, key=lambda d: d.timestamp, reverse=True)[:5]

        active_blockers = self._collect_blockers_flat()

        ctx = EmployeeContext(
            employee_id=employee_id,
            role=role,
            relevant_decisions=relevant,
            build_statuses=list(self._build_statuses),
            resource_view=list(self._resources),
            active_blockers=active_blockers,
        )
        logger.debug("Context for %s: %d decisions, %d blockers", employee_id, len(relevant), len(active_blockers))
        return ctx

    def auto_align(self, team_ids: list[str]) -> AlignmentReport:
        """Compute alignment state across *team_ids* — no meeting required.

        Identifies shared priorities and potential conflicts.
        """
        team_resources = [r for r in self._resources if r.team in team_ids]

        priority_map: dict[int, list[str]] = {}
        for r in team_resources:
            priority_map.setdefault(r.priority, []).append(r.team)

        shared = [
            f"Priority {p}: {', '.join(teams)}"
            for p, teams in sorted(priority_map.items())
            if len(teams) > 1
        ]

        # Detect budget conflicts (simplistic: two teams at P1 with large budgets).
        conflicts: list[str] = []
        p1_teams = [r for r in team_resources if r.priority == 1]
        if len(p1_teams) > 1:
            conflicts.append(
                f"Multiple teams at P1: {[r.team for r in p1_teams]} — may compete for shared resources"
            )

        report = AlignmentReport(
            team_ids=team_ids,
            shared_priorities=shared,
            conflicts=conflicts,
        )
        return report

    def detect_blockers(self) -> list[Blocker]:
        """Scan all data sources and surface blockers automatically.

        Replaces: stand-ups, escalation chains, "can you unblock me?" messages.
        """
        blockers: list[Blocker] = []
        now = datetime.now(timezone.utc)

        for idx, bs in enumerate(self._build_statuses):
            for desc in bs.blockers:
                severity = "critical" if bs.progress_pct < 30 else "high" if bs.progress_pct < 60 else "medium"
                blockers.append(
                    Blocker(
                        id=f"BLK-{idx:04d}",
                        project=bs.project,
                        description=desc,
                        severity=severity,
                        detected_at=now,
                    )
                )

        if blockers:
            logger.info("Detected %d blockers across %d projects", len(blockers), len({b.project for b in blockers}))
        return blockers

    # ------------------------------------------------------------------
    # Cross-model interface (consumed by CustomerWorldModel)
    # ------------------------------------------------------------------

    def get_resource_snapshot(self) -> list[ResourceAllocation]:
        """Public accessor used by the Customer World Model to understand
        internal capacity when composing solutions."""
        return list(self._resources)

    def get_active_projects(self) -> list[BuildStatus]:
        """Expose current build statuses to other layers."""
        return list(self._build_statuses)

    # ------------------------------------------------------------------
    # Simulation helpers
    # ------------------------------------------------------------------

    @classmethod
    def from_simulated_data(cls, event_bus: EventBus | None = None) -> CompanyWorldModel:
        """Bootstrap a model pre-loaded with realistic simulated data."""
        model = cls(event_bus=event_bus)
        model.ingest_decisions(generate_decisions(8))
        model.ingest_build_statuses(generate_build_statuses(6))
        model.ingest_resources(generate_resource_allocations(5))

        # Register a handful of simulated employees.
        for i in range(100, 106):
            role = [OrganizationRole.IC, OrganizationRole.DRI, OrganizationRole.PLAYER_COACH][i % 3]
            model.register_employee(f"emp-{i}", role)

        return model

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _collect_blockers_flat(self) -> list[str]:
        """Flatten all blockers from build statuses into a string list."""
        result: list[str] = []
        for bs in self._build_statuses:
            for b in bs.blockers:
                result.append(f"[{bs.project}] {b}")
        return result
