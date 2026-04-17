"""Backtest result container and analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd

from alpha_quat.analytics.drawdown import calculate_max_drawdown
from alpha_quat.analytics.metrics import (
    calculate_calmar_ratio,
    calculate_profit_factor,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_volatility,
    calculate_win_rate,
)
from alpha_quat.analytics.returns import (
    calculate_annualized_return,
    calculate_cumulative_returns,
    calculate_returns,
)
from alpha_quat.execution.orders import Trade


@dataclass
class BacktestResult:
    """
    Container for backtest results.

    Stores all data from a backtest run and provides methods for analysis.
    """

    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    equity_curve: pd.Series
    trades: list[Trade]
    metadata: dict[str, Any] = field(default_factory=dict)

    def calculate_metrics(
        self, risk_free_rate: float = 0.0, periods_per_year: int = 252
    ) -> dict[str, Any]:
        """
        Calculate comprehensive performance metrics.

        Args:
            risk_free_rate: Annual risk-free rate
            periods_per_year: Number of periods per year

        Returns:
            Dictionary of performance metrics
        """
        returns = calculate_returns(self.equity_curve)

        if len(returns) == 0:
            return {}

        cumulative_returns = calculate_cumulative_returns(returns)
        total_return = cumulative_returns.iloc[-1] if len(cumulative_returns) > 0 else 0.0

        num_periods = len(self.equity_curve)
        annualized_return = calculate_annualized_return(
            total_return,
            num_periods,
            periods_per_year,
        )

        volatility = calculate_volatility(returns, periods_per_year)
        sharpe_ratio = calculate_sharpe_ratio(returns, risk_free_rate, periods_per_year)
        sortino_ratio = calculate_sortino_ratio(returns, risk_free_rate, periods_per_year)
        max_drawdown = calculate_max_drawdown(self.equity_curve)
        calmar_ratio = calculate_calmar_ratio(self.equity_curve, periods_per_year)
        win_rate = calculate_win_rate(returns)
        profit_factor = calculate_profit_factor(returns)

        # Trade statistics
        total_trades = len(self.trades)
        winning_trades = (
            sum(
                1
                for t in self.trades
                if (t.price - (t.commission / abs(t.quantity)) if t.quantity != 0 else 0) > 0
            )
            if total_trades > 0
            else 0
        )
        trade_win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        return {
            # Return metrics
            "total_return": total_return,
            "annualized_return": annualized_return,
            # Risk metrics
            "volatility": volatility,
            "max_drawdown": max_drawdown,
            # Risk-adjusted metrics
            "sharpe_ratio": sharpe_ratio,
            "sortino_ratio": sortino_ratio,
            "calmar_ratio": calmar_ratio,
            # Return distribution
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            # Trade statistics
            "total_trades": total_trades,
            "trade_win_rate": trade_win_rate,
        }

    def summary(self, risk_free_rate: float = 0.0) -> dict[str, str]:
        """
        Get a human-readable summary of backtest results.

        Args:
            risk_free_rate: Annual risk-free rate for metrics

        Returns:
            Dictionary of formatted summary metrics
        """
        metrics = self.calculate_metrics(risk_free_rate)

        def format_pct(value: float | None) -> str:
            if value is None:
                return "N/A"
            return f"{value * 100:.2f}%"

        def format_num(value: float | None, decimals: int = 2) -> str:
            if value is None:
                return "N/A"
            return f"{value:.{decimals}f}"

        return {
            "Total Return": format_pct(metrics.get("total_return")),
            "Annualized Return": format_pct(metrics.get("annualized_return")),
            "Volatility": format_pct(metrics.get("volatility")),
            "Max Drawdown": format_pct(metrics.get("max_drawdown")),
            "Sharpe Ratio": format_num(metrics.get("sharpe_ratio")),
            "Sortino Ratio": format_num(metrics.get("sortino_ratio")),
            "Calmar Ratio": format_num(metrics.get("calmar_ratio")),
            "Win Rate": format_pct(metrics.get("win_rate")),
            "Profit Factor": format_num(metrics.get("profit_factor")),
            "Total Trades": str(metrics.get("total_trades", 0)),
            "Trade Win Rate": format_pct(metrics.get("trade_win_rate")),
        }
