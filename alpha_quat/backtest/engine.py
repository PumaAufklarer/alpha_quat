"""Backtest engine - core backtesting logic."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pandas as pd

from alpha_quat.backtest.result import BacktestResult
from alpha_quat.backtest.timeline import Timeline
from alpha_quat.core import Currency, Price, Quantity, SignalDirection
from alpha_quat.data.feed import DataFeed
from alpha_quat.execution.orders import Trade
from alpha_quat.portfolio.portfolio import Portfolio
from alpha_quat.strategy.generator import SignalGenerator
from alpha_quat.strategy.signals import Signal


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
    default_position_size: int = 100
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

            # Simple execution: convert signals to trades
            self._execute_signals(signals, data_point, current_dt)

        # Finalize strategy
        self.strategy.finalize()

        # Create result
        return self._create_result(start_date, end_date)

    def _update_portfolio_prices(self, data_point: dict[str, Any]) -> None:
        """Update portfolio prices based on market data."""
        # 处理多资产格式（包含 "assets" 键）
        if "assets" in data_point:
            for ts_code, asset_data in data_point["assets"].items():
                close_price = asset_data.get("close")
                if close_price is not None:
                    self.portfolio.update_price(ts_code, float(close_price))
        # 处理单资产格式（直接包含 "ts_code" 和 "close"）
        else:
            ts_code = data_point.get("ts_code")
            close_price = data_point.get("close")
            if ts_code and close_price is not None:
                self.portfolio.update_price(ts_code, float(close_price))

    def _execute_signals(
        self,
        signals: list[Signal],
        data_point: dict[str, Any],
        timestamp: datetime,
    ) -> None:
        """
        Execute signals by creating trades and updating portfolio.

        Simple implementation:
        - Immediately execute signals at current close price
        - No slippage or transaction costs for simplicity
        """
        # 获取当前价格
        close_price = None
        ts_code = None

        if "assets" in data_point:
            # 多资产格式 - 为每个信号找对应资产
            for signal in signals:
                asset_data = data_point["assets"].get(signal.ts_code, {})
                close_price = asset_data.get("close")
                if close_price is not None:
                    self._execute_single_signal(signal, Price(close_price), timestamp)
        else:
            # 单资产格式
            ts_code = data_point.get("ts_code")
            close_price = data_point.get("close")
            if ts_code and close_price is not None:
                for signal in signals:
                    if signal.ts_code == ts_code:
                        self._execute_single_signal(signal, Price(close_price), timestamp)

    def _execute_single_signal(
        self,
        signal: Signal,
        price: Price,
        timestamp: datetime,
    ) -> None:
        """Execute a single signal and create a trade."""
        position = self.portfolio.get_position(signal.ts_code)
        current_qty = int(position.quantity)

        # 确定交易数量
        trade_qty = 0

        if signal.direction == SignalDirection.LONG:
            # 做多 - 默认使用 default_position_size
            trade_qty = self.default_position_size
        elif signal.direction == SignalDirection.SHORT:
            # 做空 - 默认使用 default_position_size
            trade_qty = -self.default_position_size
        elif signal.direction == SignalDirection.EXIT_LONG:
            # 平多 - 平掉当前多头
            if current_qty > 0:
                trade_qty = -current_qty
        elif signal.direction == SignalDirection.EXIT_SHORT:
            # 平空 - 平掉当前空头
            if current_qty < 0:
                trade_qty = -current_qty
        elif signal.direction == SignalDirection.FLAT:
            # 全平 - 平掉所有持仓
            if current_qty != 0:
                trade_qty = -current_qty

        if trade_qty == 0:
            return

        # 检查是否有足够现金（买入时）
        if trade_qty > 0:
            cost = float(price) * abs(trade_qty)
            if float(self.portfolio.current_cash) < cost:
                return  # 现金不足，跳过

        # 创建交易
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            order_id=str(uuid.uuid4()),
            ts_code=signal.ts_code,
            quantity=Quantity(trade_qty),
            price=price,
            traded_at=timestamp,
            commission=Currency(0.0),
            slippage=Price(0.0),
        )

        # 更新投资组合
        self.portfolio.add_trade(trade)
        self._trades.append(trade)

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
