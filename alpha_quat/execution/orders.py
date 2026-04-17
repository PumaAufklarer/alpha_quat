"""Order and execution management."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from alpha_quat.core import Currency, Price, Quantity


class OrderType(Enum):
    """Order type enum."""

    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    TRAILING_STOP = "trailing_stop"


class OrderStatus(Enum):
    """Order status enum."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(Enum):
    """Time in force enum."""

    DAY = "day"
    GTC = "gtc"
    FOK = "fok"
    IOC = "ioc"


@dataclass
class Order:
    """Order class."""

    order_id: str
    ts_code: str
    quantity: Quantity
    order_type: OrderType
    limit_price: Price | None = None
    stop_price: Price | None = None
    trailing_amount: Price | None = None
    trailing_percent: float | None = None
    time_in_force: TimeInForce = TimeInForce.DAY
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Quantity = Quantity(0)
    filled_price: Price | None = None
    created_at: datetime | None = None
    filled_at: datetime | None = None
    metadata: dict = field(default_factory=dict)

    @property
    def is_buy(self) -> bool:
        """Check if this is a buy order."""
        return self.quantity > 0

    @property
    def is_sell(self) -> bool:
        """Check if this is a sell order."""
        return self.quantity < 0

    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.status == OrderStatus.FILLED and self.filled_quantity == abs(self.quantity)

    @property
    def remaining_quantity(self) -> Quantity:
        """Get remaining quantity to fill."""
        return Quantity(abs(self.quantity) - self.filled_quantity)


@dataclass
class Trade:
    """Trade record class."""

    trade_id: str
    order_id: str
    ts_code: str
    quantity: Quantity
    price: Price
    traded_at: datetime
    commission: Currency = Currency(0.0)
    slippage: Price = Price(0.0)
    metadata: dict = field(default_factory=dict)

    @property
    def value(self) -> Currency:
        """Calculate total trade value (price * quantity)."""
        return Currency(float(self.price) * abs(self.quantity))

    @property
    def total_cost(self) -> Currency:
        """Calculate total cost including commission."""
        return Currency(self.value + self.commission)
