"""Tests for drawdown calculations."""

import numpy as np
import pandas as pd

from alpha_quat.analytics.drawdown import (
    calculate_average_drawdown,
    calculate_drawdowns,
    calculate_max_drawdown,
)


def test_calculate_drawdowns():
    """Test drawdown series calculation."""
    equity = pd.Series([100.0, 110.0, 105.0, 115.5, 90.0, 100.0])
    drawdowns, peaks = calculate_drawdowns(equity)

    assert len(drawdowns) == len(equity)
    assert np.isclose(drawdowns.iloc[0], 0.0)  # Start at 0
    assert np.isclose(drawdowns.iloc[1], 0.0)  # New peak
    assert np.isclose(drawdowns.iloc[2], 0.0454545)  # (110-105)/110
    assert np.isclose(drawdowns.iloc[3], 0.0)  # New peak
    assert np.isclose(drawdowns.iloc[4], 0.220779)  # (115.5-90)/115.5


def test_calculate_max_drawdown():
    """Test max drawdown calculation."""
    equity = pd.Series([100.0, 110.0, 105.0, 115.5, 90.0, 100.0])
    max_dd = calculate_max_drawdown(equity)
    assert np.isclose(max_dd, 0.220779, rtol=1e-5)


def test_calculate_average_drawdown():
    """Test average drawdown calculation."""
    equity = pd.Series([100.0, 110.0, 105.0, 115.5, 90.0, 100.0])
    avg_dd = calculate_average_drawdown(equity)
    # Drawdowns are [0, 0, ~0.045, 0, ~0.22, ~0.134]
    # Average of non-zero drawdowns: (0.045 + 0.22 + 0.134)/3 ≈ 0.133
    assert avg_dd > 0
