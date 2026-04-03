"""Proactive pusher -- delivers the right solution at the right time."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .signal_detector import Signal, Urgency
from .solution_composer import Solution


class TargetInterface(Enum):
    DASHBOARD = "dashboard"
    MOBILE_PUSH = "mobile_push"
    EMAIL = "email"
    IN_APP_BANNER = "in_app_banner"
    SMS = "sms"


class TimingVerdict(Enum):
    PUSH_NOW = "push_now"
    SCHEDULE = "schedule"
    SUPPRESS = "suppress"


@dataclass
class TimingEvaluation:
    """Result of evaluating whether now is a good time to push."""

    verdict: TimingVerdict
    reason: str
    recommended_interfaces: list[TargetInterface] = field(default_factory=list)
    scheduled_at: datetime.datetime | None = None


@dataclass
class PushResult:
    """Outcome of a push attempt."""

    success: bool
    interface: TargetInterface
    solution_id: str
    delivered_at: datetime.datetime
    message: str = ""


class ProactivePusher:
    """Evaluates timing and pushes solutions to the appropriate interface."""

    # Business-hour window used for non-urgent pushes
    _BUSINESS_START: int = 9   # 09:00
    _BUSINESS_END: int = 18    # 18:00

    def __init__(self) -> None:
        self._push_log: list[PushResult] = []

    # -----------------------------------------------------------------
    # Timing evaluation
    # -----------------------------------------------------------------
    def evaluate_timing(
        self,
        signal: Signal,
        merchant: dict[str, Any],
    ) -> TimingEvaluation:
        """Decide whether, when, and how to push a solution.

        *merchant* may contain:
            merchant_id, timezone, preferred_channel, active_session
        """
        now = datetime.datetime.now(tz=datetime.timezone.utc)
        hour = now.hour
        has_active_session: bool = merchant.get("active_session", False)

        # Critical signals always push immediately
        if signal.urgency == Urgency.CRITICAL:
            interfaces = [TargetInterface.MOBILE_PUSH, TargetInterface.DASHBOARD]
            if has_active_session:
                interfaces.insert(0, TargetInterface.IN_APP_BANNER)
            return TimingEvaluation(
                verdict=TimingVerdict.PUSH_NOW,
                reason="Critical urgency -- immediate delivery required",
                recommended_interfaces=interfaces,
            )

        # High urgency: push now if within business hours, else schedule
        if signal.urgency == Urgency.HIGH:
            if self._BUSINESS_START <= hour < self._BUSINESS_END:
                interfaces = (
                    [TargetInterface.IN_APP_BANNER, TargetInterface.DASHBOARD]
                    if has_active_session
                    else [TargetInterface.MOBILE_PUSH, TargetInterface.EMAIL]
                )
                return TimingEvaluation(
                    verdict=TimingVerdict.PUSH_NOW,
                    reason="High urgency during business hours",
                    recommended_interfaces=interfaces,
                )
            next_morning = now.replace(
                hour=self._BUSINESS_START, minute=0, second=0, microsecond=0
            )
            if next_morning <= now:
                next_morning += datetime.timedelta(days=1)
            return TimingEvaluation(
                verdict=TimingVerdict.SCHEDULE,
                reason="High urgency but outside business hours -- scheduling",
                recommended_interfaces=[TargetInterface.MOBILE_PUSH],
                scheduled_at=next_morning,
            )

        # Medium / Low: only push during active session or schedule email
        if has_active_session:
            return TimingEvaluation(
                verdict=TimingVerdict.PUSH_NOW,
                reason="Merchant has an active session",
                recommended_interfaces=[TargetInterface.IN_APP_BANNER],
            )

        preferred = merchant.get("preferred_channel", "email")
        interface = (
            TargetInterface.SMS if preferred == "sms" else TargetInterface.EMAIL
        )
        next_morning = now.replace(
            hour=self._BUSINESS_START, minute=0, second=0, microsecond=0
        )
        if next_morning <= now:
            next_morning += datetime.timedelta(days=1)

        return TimingEvaluation(
            verdict=TimingVerdict.SCHEDULE,
            reason="Low/medium urgency with no active session -- scheduling",
            recommended_interfaces=[interface],
            scheduled_at=next_morning,
        )

    # -----------------------------------------------------------------
    # Push execution
    # -----------------------------------------------------------------
    def push(
        self,
        solution: Solution,
        target_interface: TargetInterface,
    ) -> PushResult:
        """Simulate delivering a solution to the given interface."""
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        # Simulate per-channel delivery
        messages = {
            TargetInterface.DASHBOARD: f"Solution {solution.solution_id} pinned to merchant dashboard",
            TargetInterface.MOBILE_PUSH: f"Push notification sent for {solution.solution_id}",
            TargetInterface.EMAIL: f"Email queued for {solution.solution_id}",
            TargetInterface.IN_APP_BANNER: f"In-app banner displayed for {solution.solution_id}",
            TargetInterface.SMS: f"SMS dispatched for {solution.solution_id}",
        }

        result = PushResult(
            success=True,
            interface=target_interface,
            solution_id=solution.solution_id,
            delivered_at=now,
            message=messages.get(target_interface, "Delivered"),
        )
        self._push_log.append(result)
        return result

    # -----------------------------------------------------------------
    # Log access
    # -----------------------------------------------------------------
    @property
    def push_history(self) -> list[PushResult]:
        """Return an immutable copy of the push log."""
        return list(self._push_log)
