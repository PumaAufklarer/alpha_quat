"""Tests for backtest result module."""

from datetime import datetime

import pandas as pd

from alpha_quat.backtest.result import BacktestResult


def test_backtest_result_creation():
    """Test creating a backtest result."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)

    # Create equity curve
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    equity = pd.Series([100000 + i * 100 for i in range(len(dates))], index=dates)

    result = BacktestResult(
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000.0,
        final_capital=103000.0,
        equity_curve=equity,
        trades=[],
    )

    assert result.start_date == start_date
    assert result.end_date == end_date
    assert result.initial_capital == 100000.0
    assert result.final_capital == 103000.0


def test_backtest_result_metrics():
    """Test backtest result metrics calculation."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 10)

    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    equity = pd.Series(
        [100000, 101000, 100500, 102000, 101500, 103000, 102500, 104000, 103500, 105000],
        index=dates,
    )

    result = BacktestResult(
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000.0,
        final_capital=105000.0,
        equity_curve=equity,
        trades=[],
    )

    # Calculate metrics
    metrics = result.calculate_metrics()

    assert "total_return" in metrics
    assert "sharpe_ratio" in metrics
    assert "max_drawdown" in metrics


def test_backtest_result_summary():
    """Test backtest result summary."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 10)

    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    equity = pd.Series(
        [100000, 101000, 100500, 102000, 101500, 103000, 102500, 104000, 103500, 105000],
        index=dates,
    )

    result = BacktestResult(
        start_date=start_date,
        end_date=end_date,
        initial_capital=100000.0,
        final_capital=105000.0,
        equity_curve=equity,
        trades=[],
    )

    summary = result.summary()
    assert isinstance(summary, dict)
    assert "Total Return" in summary
