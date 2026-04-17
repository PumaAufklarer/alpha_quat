"""
Base strategy class for backtesting.
"""

from abc import ABC, abstractmethod

from .data import DataFeed
from .order import Order, OrderType
from .portfolio import Portfolio


class Strategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self):
        self.data: DataFeed | None = None
        self.portfolio: Portfolio | None = None
        self._pending_orders: list[Order] = []

    def initialize(self, data: DataFeed, portfolio: Portfolio) -> None:
        """
        Initialize strategy with data feed and portfolio.

        Args:
            data: Data feed instance
            portfolio: Portfolio instance
        """
        self.data = data
        self.portfolio = portfolio

    @abstractmethod
    def on_bar(self, bar: dict) -> None:
        """
        Called on each new bar of data.

        Args:
            bar: Current bar data as dictionary
        """
        pass

    def on_order_filled(self, order: Order) -> None:
        """
        Called when an order is filled.

        Args:
            order: The filled order
        """
        pass

    def buy(
        self,
        ts_code: str,
        quantity: int,
        order_type: OrderType = OrderType.MARKET,
        limit_price: float | None = None,
    ) -> Order:
        """
        Place a buy order.

        Args:
            ts_code: Asset code
            quantity: Quantity to buy
            order_type: Order type (MARKET or LIMIT)
            limit_price: Limit price for LIMIT orders

        Returns:
            Order instance
        """
        order = Order(
            ts_code=ts_code, quantity=quantity, order_type=order_type, limit_price=limit_price
        )
        self._pending_orders.append(order)
        return order

    def sell(
        self,
        ts_code: str,
        quantity: int,
        order_type: OrderType = OrderType.MARKET,
        limit_price: float | None = None,
    ) -> Order:
        """
        Place a sell order.

        Args:
            ts_code: Asset code
            quantity: Quantity to sell
            order_type: Order type (MARKET or LIMIT)
            limit_price: Limit price for LIMIT orders

        Returns:
            Order instance
        """
        order = Order(
            ts_code=ts_code, quantity=-quantity, order_type=order_type, limit_price=limit_price
        )
        self._pending_orders.append(order)
        return order

    def get_pending_orders(self) -> list[Order]:
        """Get all pending orders and clear the list."""
        orders = self._pending_orders.copy()
        self._pending_orders.clear()
        return orders
