"""Tests for returns calculations."""

import numpy as np
import pandas as pd

from alpha_quat.analytics.returns import (
    calculate_annualized_return,
    calculate_cumulative_returns,
    calculate_returns,
)


def test_calculate_returns():
    """Test simple returns calculation."""
    equity = pd.Series([100.0, 110.0, 105.0, 115.5])
    returns = calculate_returns(equity)
    assert len(returns) == 3
    assert np.isclose(returns.iloc[0], 0.10)  # (110-100)/100
    assert np.isclose(returns.iloc[1], -0.0454545)  # (105-110)/110
    assert np.isclose(returns.iloc[2], 0.10)  # (115.5-105)/105


def test_calculate_cumulative_returns():
    """Test cumulative returns calculation."""
    returns = pd.Series([0.10, -0.05, 0.20])
    cum_returns = calculate_cumulative_returns(returns)
    assert len(cum_returns) == 3
    assert np.isclose(cum_returns.iloc[0], 0.10)
    assert np.isclose(cum_returns.iloc[1], 0.045)  # (1.1 * 0.95) - 1
    assert np.isclose(cum_returns.iloc[2], 0.254)  # (1.1 * 0.95 * 1.2) - 1


def test_calculate_annualized_return():
    """Test annualized return calculation."""
    cum_return = 0.254  # 25.4% total return
    periods = 365  # 1 year
    annualized = calculate_annualized_return(cum_return, periods, periods_per_year=365)
    assert np.isclose(annualized, 0.254)

    # 25.4% over 2 years
    annualized = calculate_annualized_return(0.254, 730, periods_per_year=365)
    assert np.isclose(annualized, 0.1198, rtol=1e-3)
