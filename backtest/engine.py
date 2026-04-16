"""
Backtest engine core.
"""

from dataclasses import dataclass

from .data import DataFeed
from .metrics import Metrics
from .order import Order, OrderStatus, OrderType, Trade
from .portfolio import Portfolio
from .strategy import Strategy


@dataclass
class BacktestResult:
    """Result of a backtest run."""

    portfolio: Portfolio
    metrics: Metrics
    trades: list[Trade]


class BacktestEngine:
    """
    Main backtest engine.

    Orchestrates the backtest process:
    - Iterates over data feed
    - Calls strategy callbacks
    - Executes orders
    - Updates portfolio
    """

    def __init__(self, data: DataFeed, strategy: Strategy, portfolio: Portfolio):
        """
        Initialize backtest engine.

        Args:
            data: Data feed providing market data
            strategy: Trading strategy to test
            portfolio: Portfolio to use for trading
        """
        self.data = data
        self.strategy = strategy
        self.portfolio = portfolio
        self._order_id_counter = 0

    def run(self) -> BacktestResult:
        """
        Run the backtest.

        Returns:
            BacktestResult containing portfolio, metrics, and trades
        """
        # Reset
        self.data.reset()
        self.strategy.initialize(self.data, self.portfolio)

        # Main backtest loop
        for bar in self.data:
            # Update position prices
            ts_code = bar.get("ts_code")
            close = bar.get("close")
            if ts_code and close:
                self.portfolio.update_price(ts_code, close)

            # Call strategy on_bar
            self.strategy.on_bar(bar)

            # Get and execute pending orders
            pending_orders = self.strategy.get_pending_orders()
            for order in pending_orders:
                self._execute_order(order, bar)

            # Record equity
            if self.data.current_datetime:
                self.portfolio.record_equity(self.data.current_datetime)

        # Calculate metrics
        metrics = Metrics.calculate(self.portfolio.equity_history)

        return BacktestResult(
            portfolio=self.portfolio, metrics=metrics, trades=self.portfolio.trades
        )

    def _execute_order(self, order: Order, bar: dict) -> None:
        """
        Execute an order against the current bar.

        Args:
            order: Order to execute
            bar: Current market data bar
        """
        # Simple execution: assume market orders fill at close price
        if order.order_type == OrderType.MARKET:
            fill_price = bar.get("close", 0)
            if fill_price > 0:
                order.status = OrderStatus.FILLED
                order.filled_price = fill_price
                order.filled_quantity = order.quantity
                order.filled_at = self.data.current_datetime

                # Create trade
                trade = Trade(
                    ts_code=order.ts_code,
                    quantity=order.quantity,
                    price=fill_price,
                    traded_at=order.filled_at,
                    order_id=str(self._next_order_id()),
                )
                self.portfolio.add_trade(trade)
                self.strategy.on_order_filled(order)

    def _next_order_id(self) -> int:
        """Generate next order ID."""
        self._order_id_counter += 1
        return self._order_id_counter
