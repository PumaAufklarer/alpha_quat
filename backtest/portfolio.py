"""
Portfolio management for backtesting.
"""

from dataclasses import dataclass, field
from datetime import datetime

from .order import Trade


@dataclass
class Position:
    """Position in a single asset."""

    ts_code: str
    quantity: int = 0
    avg_cost: float = 0.0
    current_price: float = 0.0

    @property
    def is_long(self) -> bool:
        """Check if position is long."""
        return self.quantity > 0

    @property
    def is_short(self) -> bool:
        """Check if position is short."""
        return self.quantity < 0

    @property
    def market_value(self) -> float:
        """Calculate market value of position."""
        return abs(self.quantity) * self.current_price


@dataclass
class Portfolio:
    """Portfolio class managing cash and positions."""

    initial_cash: float
    current_cash: float = field(init=False)
    positions: dict[str, Position] = field(default_factory=dict)
    trades: list[Trade] = field(default_factory=list)
    equity_history: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self.current_cash = self.initial_cash

    @property
    def total_equity(self) -> float:
        """Calculate total portfolio equity (cash + market value)."""
        market_value = sum(p.market_value for p in self.positions.values() if p.quantity != 0)
        return self.current_cash + market_value

    def update_price(self, ts_code: str, price: float) -> None:
        """Update current price for a position."""
        if ts_code in self.positions:
            self.positions[ts_code].current_price = price

    def update_all_prices(self, price_map: dict[str, float]) -> None:
        """Update prices for multiple assets."""
        for ts_code, price in price_map.items():
            self.update_price(ts_code, price)

    def get_position(self, ts_code: str) -> Position:
        """Get or create position for an asset."""
        if ts_code not in self.positions:
            self.positions[ts_code] = Position(ts_code=ts_code)
        return self.positions[ts_code]

    def add_trade(self, trade: Trade) -> None:
        """Record a trade and update position."""
        self.trades.append(trade)
        position = self.get_position(trade.ts_code)

        if trade.quantity > 0:
            # Buy
            total_cost = position.avg_cost * position.quantity + trade.price * trade.quantity
            position.quantity += trade.quantity
            position.avg_cost = total_cost / position.quantity if position.quantity != 0 else 0
            self.current_cash -= trade.price * trade.quantity
        else:
            # Sell
            position.quantity += trade.quantity
            self.current_cash += trade.price * abs(trade.quantity)

    def record_equity(self, dt: datetime) -> None:
        """Record equity at a specific datetime."""
        self.equity_history.append(
            {"datetime": dt, "cash": self.current_cash, "equity": self.total_equity}
        )
