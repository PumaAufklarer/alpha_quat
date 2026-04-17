"""Tests for core types."""

from datetime import datetime
from alpha_quat.core.types import Currency, Quantity, Price, Timestamp


def test_currency_type():
    """Test currency type operations."""
    c1 = Currency(100.5)
    c2 = Currency(200.25)
    assert c1 + c2 == Currency(300.75)
    assert c2 - c1 == Currency(99.75)
    assert c1 * 2 == Currency(201.0)


def test_quantity_type():
    """Test quantity type operations."""
    q1 = Quantity(100)
    q2 = Quantity(50)
    assert q1 + q2 == Quantity(150)
    assert q1 - q2 == Quantity(50)


def test_price_type():
    """Test price type operations."""
    p1 = Price(10.5)
    p2 = Price(20.0)
    assert p1 < p2 is True
    assert float(p1) == 10.5


def test_timestamp_type():
    """Test timestamp type."""
    dt = datetime(2024, 1, 1)
    ts = Timestamp(dt)
    assert ts.as_datetime() == dt
