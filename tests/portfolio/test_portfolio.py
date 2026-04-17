"""Tests for Position and Portfolio."""

from alpha_quat.portfolio.portfolio import Portfolio
from alpha_quat.portfolio.position import Position


def test_position_creation():
    """Test creating a Position."""
    pos = Position(
        ts_code="000001.SZ",
        quantity=100,
        avg_cost=10.0,
        current_price=10.5,
    )
    assert pos.ts_code == "000001.SZ"
    assert pos.quantity == 100
    assert pos.is_long is True
    assert pos.market_value == 1050.0


def test_position_unrealized_pnl():
    """Test position unrealized P&L."""
    pos = Position(
        ts_code="000001.SZ",
        quantity=100,
        avg_cost=10.0,
        current_price=10.5,
    )
    assert pos.unrealized_pnl == 50.0


def test_portfolio_creation():
    """Test creating a Portfolio."""
    portfolio = Portfolio(initial_cash=100000.0)
    assert portfolio.initial_cash == 100000.0
    assert portfolio.current_cash == 100000.0
    assert portfolio.total_equity == 100000.0


def test_portfolio_get_or_create_position():
    """Test getting or creating a position."""
    portfolio = Portfolio(initial_cash=100000.0)
    pos = portfolio.get_position("000001.SZ")
    assert pos.ts_code == "000001.SZ"
    assert pos.quantity == 0
