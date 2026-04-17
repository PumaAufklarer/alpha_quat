"""Tests for exception definitions."""

from alpha_quat.core.exceptions import (
    AlphaQuatError,
    InsufficientFundsError,
    InsufficientPositionError,
    InvalidOrderError,
    RiskLimitExceededError,
)


def test_base_error():
    """Test base error class."""
    error = AlphaQuatError("Test error")
    assert str(error) == "Test error"
    assert isinstance(error, Exception)


def test_insufficient_funds_error():
    """Test InsufficientFundsError."""
    error = InsufficientFundsError(required=1000.0, available=500.0)
    assert "1000.0" in str(error)
    assert "500.0" in str(error)


def test_insufficient_position_error():
    """Test InsufficientPositionError."""
    error = InsufficientPositionError(ts_code="000001.SZ", required=100, available=50)
    assert "000001.SZ" in str(error)
    assert "100" in str(error)
    assert "50" in str(error)


def test_risk_limit_exceeded_error():
    """Test RiskLimitExceededError."""
    error = RiskLimitExceededError(limit="max_position", value=0.3, max_value=0.2)
    assert "max_position" in str(error)
    assert "0.3" in str(error)
    assert "0.2" in str(error)


def test_invalid_order_error():
    """Test InvalidOrderError."""
    error = InvalidOrderError(reason="Price cannot be negative")
    assert "Price cannot be negative" in str(error)
