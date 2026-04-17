"""Tests for event definitions."""

from datetime import datetime

from alpha_quat.core.events import (
    DecisionPointEvent,
    Event,
    EventType,
    MarketCloseEvent,
    MarketOpenEvent,
    OrderPlacementEvent,
)


def test_event_base():
    """Test base event class."""
    dt = datetime(2024, 1, 1)
    event = Event(event_type=EventType.MARKET_CLOSE, timestamp=dt)
    assert event.event_type == EventType.MARKET_CLOSE
    assert event.timestamp == dt


def test_market_close_event():
    """Test MarketCloseEvent."""
    dt = datetime(2024, 1, 1)
    event = MarketCloseEvent(timestamp=dt)
    assert event.event_type == EventType.MARKET_CLOSE


def test_decision_point_event():
    """Test DecisionPointEvent."""
    dt = datetime(2024, 1, 1)
    event = DecisionPointEvent(timestamp=dt)
    assert event.event_type == EventType.DECISION_POINT


def test_order_placement_event():
    """Test OrderPlacementEvent."""
    dt = datetime(2024, 1, 1)
    event = OrderPlacementEvent(timestamp=dt)
    assert event.event_type == EventType.ORDER_PLACEMENT


def test_market_open_event():
    """Test MarketOpenEvent."""
    dt = datetime(2024, 1, 1)
    event = MarketOpenEvent(timestamp=dt)
    assert event.event_type == EventType.MARKET_OPEN
