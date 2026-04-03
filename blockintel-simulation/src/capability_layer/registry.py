"""Capability registry -- central catalogue for discovery and lookup."""

from __future__ import annotations

from .base import Capability, HealthReport


class CapabilityRegistry:
    """Register, discover and query available capabilities."""

    def __init__(self) -> None:
        self._capabilities: dict[str, Capability] = {}

    # -- mutation --------------------------------------------------------

    def register(self, capability: Capability) -> None:
        """Register a capability instance (keyed by its name)."""
        self._capabilities[capability.name] = capability

    def unregister(self, name: str) -> bool:
        """Remove a capability by name. Returns True if it existed."""
        return self._capabilities.pop(name, None) is not None

    # -- query -----------------------------------------------------------

    def get(self, name: str) -> Capability | None:
        """Retrieve a capability by its exact name."""
        return self._capabilities.get(name)

    def find_by_tag(self, tag: str) -> list[Capability]:
        """Return all capabilities whose tags contain *tag*."""
        return [
            cap for cap in self._capabilities.values() if tag in cap.tags
        ]

    def find_by_tags(self, tags: list[str], match_all: bool = False) -> list[Capability]:
        """Return capabilities matching any (or all) of the given tags."""
        result: list[Capability] = []
        for cap in self._capabilities.values():
            cap_tags = set(cap.tags)
            if match_all:
                if set(tags).issubset(cap_tags):
                    result.append(cap)
            else:
                if set(tags) & cap_tags:
                    result.append(cap)
        return result

    def list_all(self) -> list[Capability]:
        """Return every registered capability."""
        return list(self._capabilities.values())

    def list_names(self) -> list[str]:
        """Return the names of all registered capabilities."""
        return list(self._capabilities.keys())

    # -- health ----------------------------------------------------------

    def health_check_all(self) -> dict[str, HealthReport]:
        """Run health checks across all registered capabilities."""
        return {
            name: cap.health_check()
            for name, cap in self._capabilities.items()
        }

    # -- dunder ----------------------------------------------------------

    def __len__(self) -> int:
        return len(self._capabilities)

    def __contains__(self, name: str) -> bool:
        return name in self._capabilities

    def __repr__(self) -> str:
        names = ", ".join(self._capabilities.keys())
        return f"<CapabilityRegistry [{names}]>"
