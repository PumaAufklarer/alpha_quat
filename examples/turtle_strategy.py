"""
Turtle Trading Strategy implementation.
"""

from collections import deque

import pandas as pd

from backtest import OrderType, Strategy


class TurtleStrategy(Strategy):
    """
    Turtle Trading Strategy.

    Entry rules:
    - Long: Price breaks above 20-day high
    - Short: Price breaks below 20-day low

    Exit rules:
    - Long: Price breaks below 10-day low
    - Short: Price breaks above 10-day high
    """

    def __init__(self, entry_period: int = 20, exit_period: int = 10, position_size: int = 100):
        """
        Initialize turtle strategy.

        Args:
            entry_period: Period for entry breakout (default: 20)
            exit_period: Period for exit breakout (default: 10)
            position_size: Number of shares per trade (default: 100)
        """
        super().__init__()
        self.entry_period = entry_period
        self.exit_period = exit_period
        self.position_size = position_size

        # Store price history for each stock
        self.price_history: dict[str, deque] = {}
        self.in_position: dict[str, bool] = {}

    def on_bar(self, bar: dict) -> None:
        """
        Called on each new bar of data.

        Args:
            bar: Current bar data as dictionary
        """
        ts_code = bar.get("ts_code")
        if not ts_code:
            return

        close = bar.get("close")
        high = bar.get("high", close)
        low = bar.get("low", close)

        if not close:
            return

        # Initialize price history for this stock
        if ts_code not in self.price_history:
            self.price_history[ts_code] = deque(maxlen=max(self.entry_period, self.exit_period) + 1)
            self.in_position[ts_code] = False

        history = self.price_history[ts_code]

        # First calculate breakout levels using history WITHOUT current bar
        if len(history) >= self.entry_period:
            # Calculate breakout levels from existing history
            highs = [h["high"] for h in history]
            lows = [h["low"] for h in history]

            entry_high = max(highs[-self.entry_period :])
            entry_low = min(lows[-self.entry_period :])
            exit_low = min(lows[-self.exit_period :])
            exit_high = max(highs[-self.exit_period :])

            # Get current position
            position = self.portfolio.get_position(ts_code)
            has_long = position.quantity > 0
            has_short = position.quantity < 0

            # Trading logic - use current bar's close to decide
            if not has_long and not has_short:
                # No position, look for entry
                if close > entry_high:
                    # Breakout above entry high, go long
                    self.buy(ts_code, self.position_size, OrderType.MARKET)
                elif close < entry_low:
                    # Breakout below entry low, go short
                    self.sell(ts_code, self.position_size, OrderType.MARKET)
            elif has_long:
                # Long position, look for exit
                if close < exit_low:
                    # Exit long
                    self.sell(ts_code, position.quantity, OrderType.MARKET)
            elif has_short:
                # Short position, look for exit
                if close > exit_high:
                    # Exit short
                    self.buy(ts_code, abs(position.quantity), OrderType.MARKET)

        # Now add current bar to history for next time
        history.append({"high": high, "low": low, "close": close})


def prepare_single_stock_data(df: pd.DataFrame, ts_code: str) -> pd.DataFrame:
    """
    Prepare data for single stock backtesting.

    Args:
        df: Full daily DataFrame
        ts_code: Stock code to filter

    Returns:
        Filtered DataFrame sorted by date ascending
    """
    stock_df = df[df["ts_code"] == ts_code].copy()
    if "trade_date" in stock_df.columns:
        stock_df["trade_date"] = pd.to_datetime(stock_df["trade_date"], format="%Y%m%d")
        stock_df = stock_df.sort_values("trade_date").reset_index(drop=True)
    return stock_df
