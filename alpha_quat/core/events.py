"""Event definitions for the trading system."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class EventType(Enum):
    """Event type enum."""

    MARKET_CLOSE = "market_close"
    DECISION_POINT = "decision_point"
    ORDER_PLACEMENT = "order_placement"
    MARKET_OPEN = "market_open"
    BAR_UPDATE = "bar_update"
    ORDER_FILLED = "order_filled"


@dataclass
class Event:
    """Base event class."""

    event_type: EventType
    timestamp: datetime
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MarketCloseEvent(Event):
    """Event emitted when market closes."""

    def __init__(self, timestamp: datetime, metadata: dict = None):
        super().__init__(
            event_type=EventType.MARKET_CLOSE,
            timestamp=timestamp,
            metadata=metadata,
        )


@dataclass
class DecisionPointEvent(Event):
    """Event emitted when it's time to make trading decisions."""

    def __init__(self, timestamp: datetime, metadata: dict = None):
        super().__init__(
            event_type=EventType.DECISION_POINT,
            timestamp=timestamp,
            metadata=metadata,
        )


@dataclass
class OrderPlacementEvent(Event):
    """Event emitted when orders should be placed."""

    def __init__(self, timestamp: datetime, metadata: dict = None):
        super().__init__(
            event_type=EventType.ORDER_PLACEMENT,
            timestamp=timestamp,
            metadata=metadata,
        )


@dataclass
class MarketOpenEvent(Event):
    """Event emitted when market opens."""

    def __init__(self, timestamp: datetime, metadata: dict = None):
        super().__init__(
            event_type=EventType.MARKET_OPEN,
            timestamp=timestamp,
            metadata=metadata,
        )
