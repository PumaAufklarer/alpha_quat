"""
Test script for Turtle Strategy with sample data.
"""

import numpy as np
import pandas as pd
from backtest import BacktestEngine, Portfolio

from examples import TurtleStrategy
from examples.turtle_strategy import prepare_single_stock_data


def generate_sample_data(days: int = 200) -> pd.DataFrame:
    """Generate sample OHLC data with a clear trend."""
    np.random.seed(42)

    dates = pd.date_range(start="2024-01-01", periods=days, freq="D")
    ts_code = "000001.SZ"

    # Generate an uptrend with some pullbacks
    t = np.arange(days)
    # Base trend + seasonality + noise
    base_price = 100 + 0.3 * t + 5 * np.sin(t / 10) + np.random.normal(0, 1.5, days)

    # Generate OHLC
    high = base_price * (1 + np.random.uniform(0, 0.015, days))
    low = base_price * (1 - np.random.uniform(0, 0.015, days))
    open_ = np.roll(base_price, 1)
    open_[0] = base_price[0] * 0.998
    close = base_price

    df = pd.DataFrame(
        {
            "ts_code": ts_code,
            "trade_date": dates,
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
        }
    )
    return df


class SimpleDataFeed:
    """Simple data feed for testing."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self._current_index = 0
        self._current_datetime = None

    def __iter__(self):
        for self._current_index in range(len(self.df)):
            row = self.df.iloc[self._current_index]
            self._current_datetime = row["trade_date"]
            yield row.to_dict()

    def reset(self):
        self._current_index = 0
        self._current_datetime = None

    @property
    def current_datetime(self):
        return self._current_datetime


def main():
    """Run test for Turtle Strategy."""
    print("=== Testing Turtle Strategy ===\n")

    # Generate sample data
    print("1. Generating sample data...")
    raw_df = generate_sample_data(days=200)
    print(f"   Raw data shape: {raw_df.shape}")

    # Prepare data with features
    print("\n2. Preparing data with features...")
    df = prepare_single_stock_data(
        raw_df,
        ts_code="000001.SZ",
        entry_period=20,
        exit_period=10,
    )
    print(f"   Data with features shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")

    # Create data feed
    print("\n3. Creating data feed...")
    data_feed = SimpleDataFeed(df)

    # Create portfolio and strategy
    print("\n4. Creating portfolio and strategy...")
    initial_cash = 100000.0
    portfolio = Portfolio(initial_cash=initial_cash)
    strategy = TurtleStrategy(
        entry_period=20,
        exit_period=10,
        position_size=100,
        use_atr=False,
    )

    # Run backtest
    print("\n5. Running backtest...")
    engine = BacktestEngine(data=data_feed, strategy=strategy, portfolio=portfolio)
    result = engine.run()

    # Print results
    print("\n=== Backtest Results ===")
    print(f"Initial equity: ¥{initial_cash:,.2f}")
    print(f"Final equity: ¥{result.portfolio.total_equity:,.2f}")
    print(f"Total return: {result.metrics.total_return:.2%}")
    print(f"Annual return: {result.metrics.annual_return:.2%}")
    print(f"Volatility: {result.metrics.volatility:.2%}")
    print(f"Sharpe ratio: {result.metrics.sharpe_ratio:.2f}")
    print(f"Max drawdown: {result.metrics.max_drawdown:.2%}")
    print(f"Total trades: {len(result.trades)}")

    if result.trades:
        print("\n=== Trade List ===")
        for i, trade in enumerate(result.trades, 1):
            side = "BUY" if trade.quantity > 0 else "SELL"
            print(
                f"  {i}. {side} {abs(trade.quantity)} shares "
                f"@ ¥{trade.price:.2f} on {trade.traded_at.date()}"
            )

    print("\n=== Test complete ===")


if __name__ == "__main__":
    main()
