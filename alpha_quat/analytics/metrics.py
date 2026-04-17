"""Performance metrics calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd

from alpha_quat.analytics.drawdown import calculate_max_drawdown
from alpha_quat.analytics.returns import (
    calculate_annualized_return,
    calculate_cumulative_returns,
    calculate_returns,
)


def calculate_volatility(
    returns: pd.Series,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate annualized volatility.

    Args:
        returns: Series of simple returns
        periods_per_year: Number of periods per year

    Returns:
        Annualized volatility
    """
    if len(returns) < 2:
        return 0.0
    daily_vol = returns.std()
    annualized_vol = daily_vol * np.sqrt(periods_per_year)
    return float(annualized_vol)


def calculate_sharpe_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate annualized Sharpe ratio.

    Args:
        returns: Series of simple returns
        risk_free_rate: Annual risk-free rate (e.g., 0.02 for 2%)
        periods_per_year: Number of periods per year

    Returns:
        Sharpe ratio
    """
    if len(returns) < 2:
        return 0.0

    volatility = calculate_volatility(returns, periods_per_year)
    if volatility == 0:
        return 0.0

    mean_periodic_return = returns.mean()
    annualized_return = mean_periodic_return * periods_per_year
    excess_return = annualized_return - risk_free_rate

    sharpe = excess_return / volatility
    return float(sharpe)


def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.0,
    periods_per_year: int = 252,
) -> float:
    """
    Calculate annualized Sortino ratio (using only downside volatility).

    Args:
        returns: Series of simple returns
        risk_free_rate: Annual risk-free rate
        periods_per_year: Number of periods per year

    Returns:
        Sortino ratio
    """
    if len(returns) < 2:
        return 0.0

    mean_periodic_return = returns.mean()
    annualized_return = mean_periodic_return * periods_per_year
    excess_return = annualized_return - risk_free_rate

    # Calculate downside volatility (only negative returns)
    downside_returns = returns[returns < 0]
    if len(downside_returns) < 2:
        return 0.0

    downside_vol = downside_returns.std() * np.sqrt(periods_per_year)
    if downside_vol == 0:
        return 0.0

    sortino = excess_return / downside_vol
    return float(sortino)


def calculate_calmar_ratio(
    equity: pd.Series,
    periods_per_year: int = 252,
) -> float | None:
    """
    Calculate Calmar ratio (annualized return / max drawdown).

    Args:
        equity: Series of equity values
        periods_per_year: Number of periods per year

    Returns:
        Calmar ratio, or None if calculation fails
    """
    if len(equity) < 2:
        return None

    returns = calculate_returns(equity)
    cumulative_returns = calculate_cumulative_returns(returns)
    total_return = cumulative_returns.iloc[-1] if len(cumulative_returns) > 0 else 0.0

    annualized_return = calculate_annualized_return(
        total_return,
        len(equity),
        periods_per_year,
    )

    max_dd = calculate_max_drawdown(equity)
    if max_dd == 0:
        return None

    calmar = annualized_return / max_dd
    return float(calmar)


def calculate_win_rate(returns: pd.Series) -> float:
    """
    Calculate win rate (percentage of positive return periods).

    Args:
        returns: Series of simple returns

    Returns:
        Win rate as a decimal (e.g., 0.55 for 55%)
    """
    if len(returns) == 0:
        return 0.0
    wins = (returns > 0).sum()
    return float(wins / len(returns))


def calculate_profit_factor(returns: pd.Series) -> float:
    """
    Calculate profit factor (gross profits / gross losses).

    Args:
        returns: Series of simple returns

    Returns:
        Profit factor
    """
    if len(returns) == 0:
        return 0.0

    profits = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())

    if losses == 0:
        return float("inf") if profits > 0 else 0.0

    return float(profits / losses)
