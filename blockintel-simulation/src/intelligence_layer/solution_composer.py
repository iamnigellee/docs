"""Solution composer -- maps detected signals to capability combinations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..capability_layer.base import Capability
from .signal_detector import Signal, SignalType


@dataclass
class Solution:
    """A composed solution built from one or more capabilities."""

    solution_id: str
    signal: Signal
    capabilities: list[str]  # capability names
    parameters: dict[str, Any] = field(default_factory=dict)
    expected_impact: dict[str, Any] = field(default_factory=dict)
    description: str = ""


# Maps signal types to the capability names (and tags) that can address them.
_SIGNAL_CAPABILITY_MAP: dict[SignalType, list[str]] = {
    SignalType.CASH_FLOW_SHORTAGE: ["lending", "bnpl", "payment"],
    SignalType.GROWTH_OPPORTUNITY: ["lending", "card_issuing", "bnpl"],
    SignalType.SEASONAL_PATTERN: ["lending", "bnpl"],
}


class SolutionComposer:
    """Composes solutions by matching signals to available capabilities."""

    def __init__(self) -> None:
        self._counter: int = 0

    def _next_id(self) -> str:
        self._counter += 1
        return f"SOL-{self._counter:05d}"

    def compose(
        self,
        signal: Signal,
        available_capabilities: list[Capability],
    ) -> Solution | None:
        """Build a solution for the given *signal* using *available_capabilities*.

        Returns ``None`` if no suitable capability is available.
        """
        desired_names = _SIGNAL_CAPABILITY_MAP.get(signal.signal_type, [])
        available_map = {cap.name: cap for cap in available_capabilities}

        matched = [name for name in desired_names if name in available_map]
        if not matched:
            return None

        # Delegate to specialised composers
        composer_fn = {
            SignalType.CASH_FLOW_SHORTAGE: self._compose_cash_flow,
            SignalType.GROWTH_OPPORTUNITY: self._compose_growth,
            SignalType.SEASONAL_PATTERN: self._compose_seasonal,
        }.get(signal.signal_type, self._compose_generic)

        return composer_fn(signal, matched)

    # ------------------------------------------------------------------
    # Signal-specific composers
    # ------------------------------------------------------------------

    def _compose_cash_flow(self, signal: Signal, caps: list[str]) -> Solution:
        runway = signal.details.get("runway_months", 0)
        net = signal.details.get("net_monthly", 0)

        params: dict[str, Any] = {}
        description_parts: list[str] = []

        if "lending" in caps:
            bridge_amount = abs(net) * 3  # 3-month bridge
            params["lending"] = {
                "requested_amount": round(bridge_amount, 2),
                "purpose": "cash_flow_bridge",
            }
            description_parts.append(
                f"Short-term loan of ${bridge_amount:,.2f} to bridge cash-flow gap"
            )

        if "bnpl" in caps:
            params["bnpl"] = {"enable_for_customers": True}
            description_parts.append(
                "Enable BNPL for customers to accelerate merchant receivables"
            )

        if "payment" in caps:
            params["payment"] = {"enable_instant_deposit": True}
            description_parts.append("Activate instant deposits to speed up cash access")

        return Solution(
            solution_id=self._next_id(),
            signal=signal,
            capabilities=caps,
            parameters=params,
            expected_impact={
                "runway_improvement_months": round(max(3 - runway, 0), 1),
                "cash_flow_improvement_pct": 25,
            },
            description="; ".join(description_parts),
        )

    def _compose_growth(self, signal: Signal, caps: list[str]) -> Solution:
        score = signal.details.get("composite_score", 0)

        params: dict[str, Any] = {}
        description_parts: list[str] = []

        if "lending" in caps:
            expansion_fund = score * 500
            params["lending"] = {
                "requested_amount": round(expansion_fund, 2),
                "purpose": "business_expansion",
            }
            description_parts.append(
                f"Growth loan of ${expansion_fund:,.2f} based on momentum score"
            )

        if "card_issuing" in caps:
            params["card_issuing"] = {
                "card_type": "virtual",
                "spending_limit": round(score * 200, 2),
            }
            description_parts.append("Issue business card to manage expansion spending")

        if "bnpl" in caps:
            params["bnpl"] = {"enable_for_customers": True, "max_instalments": 6}
            description_parts.append(
                "Offer extended BNPL plans to boost average order value"
            )

        return Solution(
            solution_id=self._next_id(),
            signal=signal,
            capabilities=caps,
            parameters=params,
            expected_impact={
                "projected_revenue_lift_pct": round(score * 0.8, 1),
                "new_customer_conversion_pct": 15,
            },
            description="; ".join(description_parts),
        )

    def _compose_seasonal(self, signal: Signal, caps: list[str]) -> Solution:
        trough_months = signal.details.get("trough_months", [])
        avg_revenue = signal.details.get("average_revenue", 0)

        params: dict[str, Any] = {}
        description_parts: list[str] = []

        if "lending" in caps:
            buffer_amount = avg_revenue * 0.5
            params["lending"] = {
                "requested_amount": round(buffer_amount, 2),
                "purpose": "seasonal_buffer",
                "disburse_before_months": trough_months,
            }
            description_parts.append(
                f"Seasonal credit line of ${buffer_amount:,.2f} before low months"
            )

        if "bnpl" in caps:
            params["bnpl"] = {
                "boost_during_months": signal.details.get("peak_months", []),
                "max_instalments": 4,
            }
            description_parts.append("Amplify peak-season sales with BNPL promotions")

        return Solution(
            solution_id=self._next_id(),
            signal=signal,
            capabilities=caps,
            parameters=params,
            expected_impact={
                "trough_revenue_lift_pct": 20,
                "annual_revenue_smoothing_pct": 15,
            },
            description="; ".join(description_parts),
        )

    def _compose_generic(self, signal: Signal, caps: list[str]) -> Solution:
        return Solution(
            solution_id=self._next_id(),
            signal=signal,
            capabilities=caps,
            parameters={},
            expected_impact={},
            description="Generic solution composed from available capabilities",
        )
