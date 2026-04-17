"""Tests for timeline module."""

from datetime import datetime

from alpha_quat.backtest.timeline import Timeline, TimelineEvent


def test_timeline_creation():
    """Test creating a timeline."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 5)
    timeline = Timeline(start_date=start_date, end_date=end_date)

    assert timeline.start_date == start_date
    assert timeline.end_date == end_date
    assert timeline.current_datetime is None


def test_timeline_events():
    """Test timeline event generation."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 3)
    timeline = Timeline(start_date=start_date, end_date=end_date)

    events = list(timeline.generate_events())

    # Each day should have: MARKET_CLOSE, DECISION_POINT, ORDER_PLACEMENT, MARKET_OPEN (next day)
    # For 2 days (1-1 to 1-3), we should have events for 1-1, 1-2
    assert len(events) > 0


def test_timeline_event_order():
    """Test that timeline events are in correct order."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 2)
    timeline = Timeline(start_date=start_date, end_date=end_date)

    events = list(timeline.generate_events())

    # First event should be MARKET_CLOSE
    assert events[0].event_type == TimelineEvent.MARKET_CLOSE


def test_timeline_iteration():
    """Test timeline iteration."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 5)
    timeline = Timeline(start_date=start_date, end_date=end_date)

    event_count = 0
    for event in timeline:
        event_count += 1
        assert timeline.current_datetime is not None

    assert event_count > 0
