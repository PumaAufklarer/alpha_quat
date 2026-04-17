"""Backtest engine - core backtesting logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd

from alpha_quat.backtest.result import BacktestResult
from alpha_quat.backtest.timeline import Timeline
from alpha_quat.core import Currency
from alpha_quat.data.feed import DataFeed
from alpha_quat.execution.orders import Trade
from alpha_quat.portfolio.portfolio import Portfolio
from alpha_quat.strategy.generator import SignalGenerator


@dataclass
class BacktestEngine:
    """
    Main backtest engine.

    Orchestrates the entire backtest process:
    - Data feed iteration
    - Strategy signal generation
    - Order execution
    - Portfolio management
    - Result collection
    """

    data_feed: DataFeed
    strategy: SignalGenerator
    initial_capital: float
    portfolio: Portfolio = field(init=False)
    timeline: Timeline | None = field(init=False, default=None)
    _equity_history: list[tuple[datetime, float]] = field(init=False, default_factory=list)
    _trades: list[Trade] = field(init=False, default_factory=list)

    def __post_init__(self):
        """Initialize portfolio and timeline."""
        self.portfolio = Portfolio(initial_cash=Currency(self.initial_capital))
        self._equity_history = []
        self._trades = []

    def run(self) -> BacktestResult:
        """
        Run the backtest.

        Returns:
            BacktestResult containing results of the backtest
        """
        # Reset data feed
        self.data_feed.reset()
        self._equity_history = []
        self._trades = []
        self.portfolio = Portfolio(initial_cash=Currency(self.initial_capital))

        # Initialize strategy
        self.strategy.initialize()

        # Get data timestamps to create timeline
        data_points = list(self.data_feed)
        if not data_points:
            raise ValueError("No data in data feed")

        start_date = (
            data_points[0].get("datetime") if "datetime" in data_points[0] else datetime.now()
        )
        end_date = (
            data_points[-1].get("datetime") if "datetime" in data_points[-1] else datetime.now()
        )

        # Record initial equity
        if isinstance(start_date, datetime):
            self._equity_history.append((start_date, float(self.portfolio.total_equity)))

        # Simple backtest loop - process each data point
        for data_point in data_points:
            current_dt = data_point.get("datetime")
            if current_dt is None:
                continue

            # Update portfolio prices based on market data
            self._update_portfolio_prices(data_point)

            # Record equity
            self._equity_history.append((current_dt, float(self.portfolio.total_equity)))

            # Generate signals
            signals = self.strategy.generate(data_point)

            # Simple execution: convert signals to trades (placeholder)
            # In a real implementation, this would go through order management
            self._execute_signals(signals, data_point, current_dt)

        # Finalize strategy
        self.strategy.finalize()

        # Create result
        return self._create_result(start_date, end_date)

    def _update_portfolio_prices(self, data_point: dict[str, Any]) -> None:
        """Update portfolio prices based on market data."""
        if "assets" in data_point:
            for ts_code, asset_data in data_point["assets"].items():
                if ts_code in self.portfolio.positions:
                    close_price = asset_data.get("close")
                    if close_price is not None:
                        position = self.portfolio.positions[ts_code]
                        position.current_price = close_price

    def _execute_signals(
        self,
        signals: list,
        data_point: dict[str, Any],
        timestamp: datetime,
    ) -> None:
        """
        Execute signals (placeholder implementation).

        In a full implementation, this would:
        - Convert signals to orders
        - Check risk limits
        - Route to order manager
        - Match at next market open
        """
        # This is a simplified placeholder
        pass

    def _create_result(self, start_date: datetime, end_date: datetime) -> BacktestResult:
        """Create backtest result from collected data."""
        # Create equity curve
        if self._equity_history:
            dates = [d for d, _ in self._equity_history]
            values = [v for _, v in self._equity_history]
            equity_curve = pd.Series(values, index=dates)
        else:
            equity_curve = pd.Series([self.initial_capital], index=[start_date])

        final_capital = float(self.portfolio.total_equity)

        return BacktestResult(
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            equity_curve=equity_curve,
            trades=self._trades,
        )
