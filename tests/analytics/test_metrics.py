"""Tests for performance metrics."""

import pandas as pd

from alpha_quat.analytics.metrics import (
    calculate_calmar_ratio,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_volatility,
)


def test_calculate_volatility():
    """Test volatility calculation."""
    returns = pd.Series([0.01, -0.02, 0.015, -0.005, 0.01])
    vol = calculate_volatility(returns, periods_per_year=252)
    assert vol > 0


def test_calculate_sharpe_ratio():
    """Test Sharpe ratio calculation."""
    returns = pd.Series([0.01, 0.005, 0.015, 0.008, 0.012])
    sharpe = calculate_sharpe_ratio(returns, risk_free_rate=0.0, periods_per_year=252)
    assert sharpe > 0


def test_calculate_sortino_ratio():
    """Test Sortino ratio calculation."""
    returns = pd.Series([0.01, -0.005, 0.015, -0.002, 0.01])
    sortino = calculate_sortino_ratio(returns, risk_free_rate=0.0, periods_per_year=252)
    assert sortino > 0


def test_calculate_calmar_ratio():
    """Test Calmar ratio calculation."""
    equity = pd.Series([100.0, 110.0, 105.0, 115.0, 95.0, 105.0])
    calmar = calculate_calmar_ratio(equity, periods_per_year=252)
    assert calmar is not None
