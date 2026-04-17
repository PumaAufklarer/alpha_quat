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
            # Check if this is a multi-asset bar
            if "assets" in bar and "datetime" in bar:
                self._process_multi_asset_bar(bar)
            else:
                self._process_single_asset_bar(bar)

        # Calculate metrics
        metrics = Metrics.calculate(self.portfolio.equity_history)

        return BacktestResult(
            portfolio=self.portfolio, metrics=metrics, trades=self.portfolio.trades
        )

    def _process_single_asset_bar(self, bar: dict) -> None:
        """Process a single asset bar (legacy mode)."""
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
            self._execute_order_single_asset(order, bar)

        # Record equity
        if self.data.current_datetime:
            self.portfolio.record_equity(self.data.current_datetime)

    def _process_multi_asset_bar(self, bar: dict) -> None:
        """Process a multi-asset bar (new mode)."""
        datetime_val = bar["datetime"]
        assets = bar["assets"]

        # Update all position prices
        for ts_code, asset_data in assets.items():
            close = asset_data.get("close")
            if close is not None:
                self.portfolio.update_price(ts_code, close)

        # Call strategy on_bar for each asset, or pass the whole bar
        # Strategy can decide how to handle it
        self.strategy.on_bar(bar)

        # Get and execute pending orders
        pending_orders = self.strategy.get_pending_orders()
        for order in pending_orders:
            self._execute_order_multi_asset(order, assets)

        # Record equity (once per datetime)
        self.portfolio.record_equity(datetime_val)

    def _execute_order_single_asset(self, order: Order, bar: dict) -> None:
        """
        Execute an order against a single asset bar.

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

    def _execute_order_multi_asset(self, order: Order, assets: dict) -> None:
        """
        Execute an order against a multi-asset bar.

        Args:
            order: Order to execute
            assets: Dict of {ts_code: asset_data}
        """
        if order.order_type == OrderType.MARKET:
            asset_data = assets.get(order.ts_code)
            if asset_data is not None:
                fill_price = asset_data.get("close", 0)
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
