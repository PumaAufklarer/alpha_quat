"""Drawdown calculations for performance analysis."""

from __future__ import annotations

import pandas as pd


def calculate_drawdowns(equity: pd.Series) -> tuple[pd.Series, pd.Series]:
    """
    Calculate drawdown series and peak series from equity.

    Args:
        equity: Series of equity values

    Returns:
        Tuple of (drawdown_series, peak_series)
    """
    peaks = equity.cummax()
    drawdowns = (peaks - equity) / peaks
    return drawdowns, peaks


def calculate_max_drawdown(equity: pd.Series) -> float:
    """
    Calculate maximum drawdown from equity series.

    Args:
        equity: Series of equity values

    Returns:
        Maximum drawdown as a decimal (e.g., 0.25 for 25%)
    """
    drawdowns, _ = calculate_drawdowns(equity)
    return float(drawdowns.max())


def calculate_average_drawdown(equity: pd.Series) -> float:
    """
    Calculate average drawdown (only non-zero drawdown periods).

    Args:
        equity: Series of equity values

    Returns:
        Average drawdown as a decimal
    """
    drawdowns, _ = calculate_drawdowns(equity)
    non_zero_drawdowns = drawdowns[drawdowns > 0]
    if len(non_zero_drawdowns) == 0:
        return 0.0
    return float(non_zero_drawdowns.mean())


def calculate_drawdown_duration(equity: pd.Series) -> int:
    """
    Calculate the maximum drawdown duration in periods.

    Args:
        equity: Series of equity values

    Returns:
        Maximum drawdown duration in number of periods
    """
    _, peaks = calculate_drawdowns(equity)

    max_duration = 0
    current_duration = 0
    last_peak_idx = 0

    for i in range(1, len(equity)):
        if peaks.iloc[i] > peaks.iloc[i - 1]:
            # New peak
            current_duration = 0
            last_peak_idx = i
        else:
            # Still in drawdown
            current_duration = i - last_peak_idx
            max_duration = max(max_duration, current_duration)

    return max_duration
