from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable


@dataclass(frozen=True)
class Event:
    kind: str
    timestamp: float
    payload: dict[str, Any] = field(default_factory=dict)


class EventStream:
    def __init__(self, events: Iterable[Event] | None = None) -> None:
        self._events = list(events or [])

    @property
    def events(self) -> list[Event]:
        return list(self._events)

    def append(self, event: Event) -> None:
        self._events.append(event)

    def extend(self, events: Iterable[Event]) -> None:
        self._events.extend(events)

    def __iter__(self):
        return iter(self._events)


class ReplaySession:
    """Synchronous event-order replay for CAN/UDS/signal streams."""

    def __init__(self, stream: EventStream | Iterable[Event]) -> None:
        if isinstance(stream, EventStream):
            self.stream = stream
        else:
            self.stream = EventStream(stream)

    def ordered_events(self) -> list[Event]:
        return sorted(self.stream.events, key=lambda event: event.timestamp)

    def next(self) -> Event | None:
        ordered = self.ordered_events()
        return ordered[0] if ordered else None
