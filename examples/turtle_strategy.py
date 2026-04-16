"""
Turtle Trading Strategy implementation using feature engineering module.
"""

import pandas as pd

from backtest import OrderType, Strategy
from features import ATR, DonchianChannels, FeaturePipeline


class TurtleStrategy(Strategy):
    """
    Turtle Trading Strategy using pre-computed features.

    Entry rules:
    - Long: Price breaks above entry-period Donchian upper band
    - Short: Price breaks below entry-period Donchian lower band

    Exit rules:
    - Long: Price breaks below exit-period Donchian lower band
    - Short: Price breaks above exit-period Donchian upper band
    """

    def __init__(
        self,
        entry_period: int = 20,
        exit_period: int = 10,
        position_size: int = 100,
        use_atr: bool = False,
    ):
        """
        Initialize turtle strategy.

        Args:
            entry_period: Period for entry breakout (default: 20)
            exit_period: Period for exit breakout (default: 10)
            position_size: Number of shares per trade (default: 100)
            use_atr: Whether to use ATR for position sizing (default: False)
        """
        super().__init__()
        self.entry_period = entry_period
        self.exit_period = exit_period
        self.position_size = position_size
        self.use_atr = use_atr

    @staticmethod
    def create_feature_pipeline(entry_period: int, exit_period: int) -> FeaturePipeline:
        """
        Create a feature pipeline for Turtle Strategy.

        Args:
            entry_period: Period for entry breakout
            exit_period: Period for exit breakout

        Returns:
            FeaturePipeline with required features
        """
        return FeaturePipeline(
            [
                DonchianChannels(period=entry_period),
                DonchianChannels(period=exit_period),
                ATR(period=14),
            ]
        )

    def on_bar(self, bar: dict) -> None:
        """
        Called on each new bar of data.

        Args:
            bar: Current bar data as dictionary with pre-computed features
        """
        ts_code = bar.get("ts_code")
        if not ts_code:
            return

        close = bar.get("close")
        if not close:
            return

        # Get pre-computed Donchian channels from bar
        entry_upper = bar.get(f"donchian_{self.entry_period}_upper")
        entry_lower = bar.get(f"donchian_{self.entry_period}_lower")
        exit_upper = bar.get(f"donchian_{self.exit_period}_upper")
        exit_lower = bar.get(f"donchian_{self.exit_period}_lower")

        # Skip if any required feature is missing
        if any(v is None or pd.isna(v) for v in [entry_upper, entry_lower, exit_upper, exit_lower]):
            return

        # Get current position
        position = self.portfolio.get_position(ts_code)
        has_long = position.quantity > 0
        has_short = position.quantity < 0

        # Calculate position size
        size = self.position_size
        if self.use_atr:
            atr = bar.get("atr_14")
            if atr is not None and not pd.isna(atr) and atr > 0:
                # Simple ATR-based sizing: 1% risk per trade
                # Position size = (1% of equity) / ATR
                risk_per_trade = self.portfolio.total_equity * 0.01
                size = int(risk_per_trade / atr)
                size = max(size, 10)  # Minimum 10 shares

        # Trading logic - use current bar's close and pre-computed features
        if not has_long and not has_short:
            # No position, look for entry
            if close > entry_upper:
                # Breakout above entry high, go long
                self.buy(ts_code, size, OrderType.MARKET)
            elif close < entry_lower:
                # Breakout below entry low, go short
                self.sell(ts_code, size, OrderType.MARKET)
        elif has_long:
            # Long position, look for exit
            if close < exit_lower:
                # Exit long
                self.sell(ts_code, position.quantity, OrderType.MARKET)
        elif has_short:
            # Short position, look for exit
            if close > exit_upper:
                # Exit short
                self.buy(ts_code, abs(position.quantity), OrderType.MARKET)


def prepare_single_stock_data(
    df: pd.DataFrame,
    ts_code: str,
    entry_period: int = 20,
    exit_period: int = 10,
) -> pd.DataFrame:
    """
    Prepare data for single stock backtesting with features pre-computed.

    Args:
        df: Full daily DataFrame
        ts_code: Stock code to filter
        entry_period: Period for entry breakout
        exit_period: Period for exit breakout

    Returns:
        Filtered DataFrame sorted by date ascending with features added
    """
    stock_df = df[df["ts_code"] == ts_code].copy()
    if "trade_date" in stock_df.columns:
        stock_df["trade_date"] = pd.to_datetime(stock_df["trade_date"], format="%Y%m%d")
        stock_df = stock_df.sort_values("trade_date").reset_index(drop=True)

    # Compute features using pipeline
    pipeline = TurtleStrategy.create_feature_pipeline(
        entry_period=entry_period,
        exit_period=exit_period,
    )
    stock_df = pipeline.calculate(stock_df)

    return stock_df
