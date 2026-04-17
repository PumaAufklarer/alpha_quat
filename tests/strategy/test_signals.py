"""Tests for strategy signals."""

from datetime import datetime

from alpha_quat.core import Price
from alpha_quat.strategy.signals import Signal, SignalDirection, Urgency


def test_signal_creation():
    """Test creating a signal."""
    dt = datetime(2024, 1, 1)
    signal = Signal(
        ts_code="000001.SZ",
        direction=SignalDirection.LONG,
        strength=1.0,
        urgency=Urgency.NORMAL,
        timestamp=dt,
    )
    assert signal.ts_code == "000001.SZ"
    assert signal.direction == SignalDirection.LONG
    assert signal.strength == 1.0
    assert signal.urgency == Urgency.NORMAL


def test_signal_with_limit_price():
    """Test signal with limit price."""
    signal = Signal(
        ts_code="000001.SZ",
        direction=SignalDirection.LONG,
        limit_price=Price(10.5),
    )
    assert signal.limit_price == Price(10.5)


def test_signal_direction_checks():
    """Test signal direction convenience properties."""
    long_signal = Signal(
        ts_code="000001.SZ",
        direction=SignalDirection.LONG,
    )
    assert long_signal.is_long is True
    assert long_signal.is_short is False
    assert long_signal.is_exit is False

    exit_signal = Signal(
        ts_code="000001.SZ",
        direction=SignalDirection.EXIT_LONG,
    )
    assert exit_signal.is_exit is True
    assert exit_signal.is_exit_long is True
