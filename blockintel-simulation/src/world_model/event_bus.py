"""BlockIntel World Model — asynchronous event bus.

A lightweight publish-subscribe event bus used for communication between
the World Model layer and the Intelligence layer.  Supports both sync
and async handlers.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

# Type alias for event handlers — can be sync or async callables.
EventHandler = Callable[..., Any | Coroutine[Any, Any, Any]]


@dataclass
class Event:
    """Immutable event envelope."""

    event_type: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus:
    """Simple async-capable pub/sub event bus.

    Usage::

        bus = EventBus()
        bus.subscribe("signal.new", my_handler)
        await bus.publish("signal.new", {"merchant_id": "m-42"})

    Both sync and async handlers are accepted.  Sync handlers are
    executed in the current event-loop thread; async handlers are
    awaited concurrently via ``asyncio.gather``.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
        self._history: dict[str, list[Event]] = defaultdict(list)
        self._max_history: int = 1000  # per event type

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Register *handler* to be called whenever *event_type* is published."""
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)
            logger.debug("Subscribed %s to '%s'", handler.__name__, event_type)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        """Remove a previously registered handler."""
        try:
            self._subscribers[event_type].remove(handler)
        except ValueError:
            pass

    async def publish(self, event_type: str, data: dict[str, Any]) -> list[Any]:
        """Publish an event and invoke all subscribed handlers.

        Returns a list of handler results (useful for testing / debugging).
        """
        event = Event(event_type=event_type, data=data)
        self._record(event)

        handlers = self._subscribers.get(event_type, [])
        if not handlers:
            logger.debug("No subscribers for '%s'", event_type)
            return []

        tasks: list[Any] = []
        sync_results: list[Any] = []

        for handler in handlers:
            try:
                if inspect.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    sync_results.append(handler(event))
            except Exception:
                logger.exception("Handler %s failed for '%s'", handler.__name__, event_type)

        async_results: list[Any] = []
        if tasks:
            async_results = list(await asyncio.gather(*tasks, return_exceptions=True))
            for r in async_results:
                if isinstance(r, BaseException):
                    logger.error("Async handler error: %s", r)

        return sync_results + async_results

    def get_history(self, event_type: str | None = None) -> list[Event]:
        """Return recorded events, optionally filtered by type."""
        if event_type is not None:
            return list(self._history.get(event_type, []))
        # Merge all types, sorted chronologically.
        all_events: list[Event] = []
        for events in self._history.values():
            all_events.extend(events)
        all_events.sort(key=lambda e: e.timestamp)
        return all_events

    def clear_history(self, event_type: str | None = None) -> None:
        """Clear recorded event history."""
        if event_type is not None:
            self._history.pop(event_type, None)
        else:
            self._history.clear()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _record(self, event: Event) -> None:
        history = self._history[event.event_type]
        history.append(event)
        if len(history) > self._max_history:
            self._history[event.event_type] = history[-self._max_history:]
