"""Portfolio management."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from alpha_quat.core import Currency
from alpha_quat.execution import Trade

from .position import Position


@dataclass
class Portfolio:
    """Portfolio class managing cash and positions."""

    initial_cash: Currency
    current_cash: Currency = field(init=False)
    positions: dict[str, Position] = field(default_factory=dict)
    trades: list[Trade] = field(default_factory=list)
    equity_history: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self.current_cash = Currency(self.initial_cash)

    @property
    def total_equity(self) -> Currency:
        """Calculate total portfolio equity (cash + market value)."""
        market_value = sum(p.market_value for p in self.positions.values() if not p.is_flat)
        return Currency(self.current_cash + market_value)

    def update_price(self, ts_code: str, price: float) -> None:
        """Update current price for a position."""
        if ts_code in self.positions:
            from alpha_quat.core import Price

            self.positions[ts_code].current_price = Price(price)

    def update_all_prices(self, price_map: dict[str, float]) -> None:
        """Update prices for multiple assets."""
        for ts_code, price in price_map.items():
            self.update_price(ts_code, price)

    def get_position(self, ts_code: str) -> Position:
        """Get or create position for an asset."""
        if ts_code not in self.positions:
            from alpha_quat.core import Price, Quantity

            self.positions[ts_code] = Position(
                ts_code=ts_code,
                quantity=Quantity(0),
                avg_cost=Price(0.0),
                current_price=Price(0.0),
            )
        return self.positions[ts_code]

    def add_trade(self, trade: Trade) -> None:
        """Record a trade and update position."""
        self.trades.append(trade)
        position = self.get_position(trade.ts_code)
        qty_change = int(trade.quantity)
        abs_qty = abs(qty_change)

        if qty_change > 0:
            # Buy
            total_cost = (
                float(position.avg_cost) * abs(int(position.quantity))
                + float(trade.price) * abs_qty
            )
            new_qty = int(position.quantity) + qty_change
            from alpha_quat.core import Price, Quantity

            position.quantity = Quantity(new_qty)
            position.avg_cost = Price(total_cost / new_qty) if new_qty != 0 else Price(0.0)
            self.current_cash = Currency(float(self.current_cash) - float(trade.price) * abs_qty)
        else:
            # Sell - calculate realized P&L
            sell_qty = abs(qty_change)
            realized_pnl = (float(trade.price) - float(position.avg_cost)) * sell_qty
            position.realized_pnl = Currency(float(position.realized_pnl) + realized_pnl)
            from alpha_quat.core import Quantity

            position.quantity = Quantity(int(position.quantity) + qty_change)
            self.current_cash = Currency(float(self.current_cash) + float(trade.price) * sell_qty)

    def record_equity(self, dt: datetime) -> None:
        """Record equity at a specific datetime."""
        self.equity_history.append(
            {
                "datetime": dt,
                "cash": float(self.current_cash),
                "equity": float(self.total_equity),
            }
        )
