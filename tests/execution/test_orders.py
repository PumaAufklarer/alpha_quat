"""Tests for order definitions."""

from datetime import datetime
from alpha_quat.execution.orders import (
    OrderType,
    OrderStatus,
    TimeInForce,
    Order,
)


def test_order_creation():
    """Test creating an order."""
    dt = datetime(2024, 1, 1)
    order = Order(
        order_id="ORD001",
        ts_code="000001.SZ",
        quantity=100,
        order_type=OrderType.LIMIT,
        limit_price=10.5,
        created_at=dt,
    )
    assert order.order_id == "ORD001"
    assert order.ts_code == "000001.SZ"
    assert order.quantity == 100
    assert order.order_type == OrderType.LIMIT
    assert order.limit_price == 10.5


def test_order_filled():
    """Test order filled property."""
    order = Order(
        order_id="ORD001",
        ts_code="000001.SZ",
        quantity=100,
        order_type=OrderType.MARKET,
    )
    assert order.is_filled is False
    order.status = OrderStatus.FILLED
    order.filled_quantity = 100
    assert order.is_filled is True


def test_order_direction():
    """Test order direction properties."""
    buy_order = Order(
        order_id="ORD001",
        ts_code="000001.SZ",
        quantity=100,
        order_type=OrderType.MARKET,
    )
    assert buy_order.is_buy is True
    assert buy_order.is_sell is False

    sell_order = Order(
        order_id="ORD002",
        ts_code="000001.SZ",
        quantity=-100,
        order_type=OrderType.MARKET,
    )
    assert sell_order.is_buy is False
    assert sell_order.is_sell is True
