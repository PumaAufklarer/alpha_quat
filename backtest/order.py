"""
Order and execution management.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderType(Enum):
    """Order type enum."""

    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(Enum):
    """Order status enum."""

    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Order class."""

    ts_code: str
    quantity: int
    order_type: OrderType
    limit_price: float | None = None
    status: OrderStatus = OrderStatus.PENDING
    filled_price: float | None = None
    filled_quantity: int = 0
    created_at: datetime | None = None
    filled_at: datetime | None = None

    @property
    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.status == OrderStatus.FILLED and self.filled_quantity == self.quantity


@dataclass
class Trade:
    """Trade record class."""

    ts_code: str
    quantity: int
    price: float
    traded_at: datetime
    order_id: str | None = None
