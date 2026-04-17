"""Position management."""

from __future__ import annotations

from dataclasses import dataclass

from alpha_quat.core import Currency, Price, Quantity


@dataclass
class Position:
    """Position in a single asset."""

    ts_code: str
    quantity: Quantity
    avg_cost: Price
    current_price: Price
    realized_pnl: Currency = Currency(0.0)

    @property
    def is_long(self) -> bool:
        """Check if position is long."""
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        """Check if position is short."""
        return self.quantity < 0

    @property
    def is_flat(self) -> bool:
        """Check if position is flat (no position)."""
        return self.quantity == 0

    @property
    def market_value(self) -> Currency:
        """Calculate market value of position."""
        return Currency(float(abs(self.quantity)) * float(self.current_price))

    @property
    def cost_value(self) -> Currency:
        """Calculate cost value of position."""
        return Currency(float(abs(self.quantity)) * float(self.avg_cost))

    @property
    def unrealized_pnl(self) -> Currency:
        """Calculate unrealized P&L of position."""
        return Currency(self.market_value - self.cost_value)
