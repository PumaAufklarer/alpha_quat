"""Return calculations for performance analysis."""

from __future__ import annotations

import pandas as pd


def calculate_returns(equity: pd.Series) -> pd.Series:
    """
    Calculate simple returns from equity series.

    Args:
        equity: Series of equity values

    Returns:
        Series of simple returns (same index as equity, minus first element)
    """
    returns = equity.pct_change().dropna()
    return returns


def calculate_cumulative_returns(returns: pd.Series) -> pd.Series:
    """
    Calculate cumulative returns from simple returns.

    Args:
        returns: Series of simple returns

    Returns:
        Series of cumulative returns
    """
    cumulative = (1 + returns).cumprod() - 1
    return cumulative


def calculate_annualized_return(
    cumulative_return: float,
    num_periods: int,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate annualized return.

    Args:
        cumulative_return: Total cumulative return (e.g., 0.25 for 25%)
        num_periods: Number of periods in the data
        periods_per_year: Number of periods per year (default: 252 for daily)

    Returns:
        Annualized return
    """
    if num_periods == 0:
        return 0.0
    years = num_periods / periods_per_year
    if years <= 0:
        return 0.0
    annualized = (1 + cumulative_return) ** (1 / years) - 1
    return annualized
