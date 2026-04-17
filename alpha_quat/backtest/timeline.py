"""Timeline management for backtesting."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


class TimelineEvent(Enum):
    """Type of timeline event."""

    MARKET_CLOSE = "market_close"
    DECISION_POINT = "decision_point"
    ORDER_PLACEMENT = "order_placement"
    MARKET_OPEN = "market_open"


@dataclass
class TimelineItem:
    """Single item in the timeline."""

    event_type: TimelineEvent
    timestamp: datetime
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Timeline:
    """
    Timeline for backtesting.

    Manages the sequence of events for each trading day:
    - MARKET_CLOSE: Market closes, data becomes available
    - DECISION_POINT: Strategy makes decisions
    - ORDER_PLACEMENT: Orders are placed
    - MARKET_OPEN: Next market open, orders are executed
    """

    def __init__(
        self,
        start_date: datetime,
        end_date: datetime,
    ):
        """
        Initialize timeline.

        Args:
            start_date: Start date of the timeline
            end_date: End date of the timeline
        """
        self.start_date = start_date
        self.end_date = end_date
        self._current_index = -1
        self._events: list[TimelineItem] = []
        self._generate_events()

    def _generate_events(self) -> None:
        """Generate all timeline events."""
        self._events = []

        current_date = self.start_date
        while current_date <= self.end_date:
            # Skip weekends (optional, could be enhanced for market holidays)
            if current_date.weekday() < 5:  # 0-4 are Monday-Friday
                # Market close event for current day
                self._events.append(
                    TimelineItem(
                        event_type=TimelineEvent.MARKET_CLOSE,
                        timestamp=current_date,
                    )
                )

                # Decision point
                self._events.append(
                    TimelineItem(
                        event_type=TimelineEvent.DECISION_POINT,
                        timestamp=current_date,
                    )
                )

                # Order placement
                self._events.append(
                    TimelineItem(
                        event_type=TimelineEvent.ORDER_PLACEMENT,
                        timestamp=current_date,
                    )
                )

            current_date += timedelta(days=1)

        # Add final market open (though we might not have data for it)
        # This is for executing orders placed on the last decision point
        if self._events:
            last_date = self._events[-1].timestamp + timedelta(days=1)
            # Skip to next business day
            while last_date.weekday() >= 5:
                last_date += timedelta(days=1)
            self._events.append(
                TimelineItem(
                    event_type=TimelineEvent.MARKET_OPEN,
                    timestamp=last_date,
                )
            )

    def generate_events(self) -> Iterator[TimelineItem]:
        """
        Generate all timeline events.

        Yields:
            TimelineItem events in order
        """
        yield from self._events

    @property
    def current_datetime(self) -> datetime | None:
        """Get current datetime in the timeline."""
        if 0 <= self._current_index < len(self._events):
            return self._events[self._current_index].timestamp
        return None

    def reset(self) -> None:
        """Reset timeline to the beginning."""
        self._current_index = -1

    def __iter__(self) -> Iterator[TimelineItem]:
        """Iterate through timeline events."""
        for self._current_index in range(len(self._events)):
            yield self._events[self._current_index]

    def __len__(self) -> int:
        """Get number of events in timeline."""
        return len(self._events)
