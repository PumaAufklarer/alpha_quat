"""
Test script for multi-asset backtesting.

This script demonstrates how to backtest a strategy on a basket of stocks.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import (
    BacktestEngine,
    BacktestPlotter,
    MultiAssetDataFeed,
    Portfolio,
    Strategy,
)
from backtest.order import OrderType


def generate_multi_asset_sample_data(
    num_stocks: int = 3,
    days: int = 250,
    start_date: str = "2024-01-01",
) -> pd.DataFrame:
    """Generate sample OHLC data for multiple stocks."""
    np.random.seed(42)

    dates = pd.date_range(start=start_date, periods=days, freq="D")

    # Generate stock codes
    stock_codes = [f"{600000 + i:06d}.SH" for i in range(num_stocks)]

    all_data = []

    for ts_code in stock_codes:
        # Generate slightly different trends for each stock
        t = np.arange(days)
        base_trend = 100 + 0.15 * t + np.random.normal(0, 0.5, days) * t * 0.01
        seasonality = 5 * np.sin(t / (15 + np.random.randint(0, 10)))
        noise = np.random.normal(0, 2, days)
        base_price = base_trend + seasonality + noise

        # Generate OHLC
        high = base_price * (1 + np.random.uniform(0, 0.02, days))
        low = base_price * (1 - np.random.uniform(0, 0.02, days))
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
        all_data.append(df)

    # Combine all stocks and sort by date
    result = pd.concat(all_data, ignore_index=True)
    result = result.sort_values(["trade_date", "ts_code"]).reset_index(drop=True)
    return result


class SimpleMomentumStrategy(Strategy):
    """
    Simple multi-asset momentum strategy.

    Buy the stock with the highest momentum, hold for N days, then rebalance.
    """

    def __init__(self, hold_period: int = 20, position_size: int = 100):
        """
        Initialize momentum strategy.

        Args:
            hold_period: Days to hold each position
            position_size: Number of shares per trade
        """
        super().__init__()
        self.hold_period = hold_period
        self.position_size = position_size
        self.day_counter = 0
        self.current_holding: str | None = None

    def on_bar(self, bar: dict) -> None:
        """
        Called on each new bar of data.

        For multi-asset data, bar contains:
        - datetime: current datetime
        - assets: dict of {ts_code: asset_data}
        """
        # Check if this is multi-asset bar
        if "assets" not in bar:
            return

        assets = bar["assets"]
        self.day_counter += 1

        # Rebalance every hold_period days
        if self.day_counter % self.hold_period == 0 or self.day_counter == 1:
            self._rebalance(assets)

    def _rebalance(self, assets: dict) -> None:
        """Rebalance portfolio: pick stock with highest momentum."""
        # Sell current holding if any
        if self.current_holding and self.current_holding in assets:
            position = self.portfolio.get_position(self.current_holding)
            if position.quantity > 0:
                self.sell(self.current_holding, position.quantity, OrderType.MARKET)
                self.current_holding = None

        # Calculate momentum for each stock (simplified: just current price)
        best_ts_code = None
        highest_price = 0

        for ts_code, asset_data in assets.items():
            close = asset_data.get("close", 0)
            if close > highest_price:
                highest_price = close
                best_ts_code = ts_code

        # Buy the stock with highest price
        if best_ts_code and highest_price > 0:
            self.buy(best_ts_code, self.position_size, OrderType.MARKET)
            self.current_holding = best_ts_code


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Multi-asset backtest test")
    parser.add_argument(
        "--num-stocks",
        type=int,
        default=5,
        help="Number of stocks in the basket (default: 5)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=300,
        help="Number of days for sample data (default: 300)",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default="2024-01-01",
        help="Start date for sample data (default: 2024-01-01)",
    )
    parser.add_argument(
        "--initial-cash",
        type=float,
        default=500000.0,
        help="Initial cash for backtest (default: 500000.0)",
    )
    parser.add_argument(
        "--hold-period",
        type=int,
        default=15,
        help="Hold period in days for momentum strategy (default: 15)",
    )
    parser.add_argument(
        "--position-size",
        type=int,
        default=200,
        help="Position size per trade (default: 200)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for plots (default: output/plots)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        help="DPI for saved plots (default: 150)",
    )
    return parser.parse_args()


def main():
    """Run multi-asset backtest test."""
    args = parse_args()

    print("=== Testing Multi-Asset Backtest ===\n")
    print("Parameters:")
    print(f"  num_stocks: {args.num_stocks}")
    print(f"  days: {args.days}")
    print(f"  start_date: {args.start_date}")
    print(f"  initial_cash: ¥{args.initial_cash:,.0f}")
    print(f"  hold_period: {args.hold_period} days")
    print(f"  position_size: {args.position_size} shares")

    # Create output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).parent.parent / "output" / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    # Generate sample data
    print("\n1. Generating multi-asset sample data...")
    raw_df = generate_multi_asset_sample_data(
        num_stocks=args.num_stocks,
        days=args.days,
        start_date=args.start_date,
    )
    print(f"   Raw data shape: {raw_df.shape}")
    print(f"   Stocks in basket: {raw_df['ts_code'].unique()}")

    # Create multi-asset data feed
    print("\n2. Creating multi-asset data feed...")
    data_feed = MultiAssetDataFeed(raw_df, datetime_col="trade_date", ts_code_col="ts_code")

    # Create portfolio and strategy
    print("\n3. Creating portfolio and strategy...")
    portfolio = Portfolio(initial_cash=args.initial_cash)
    strategy = SimpleMomentumStrategy(
        hold_period=args.hold_period,
        position_size=args.position_size,
    )

    # Run backtest
    print("\n4. Running backtest...")
    engine = BacktestEngine(data=data_feed, strategy=strategy, portfolio=portfolio)
    result = engine.run()

    # Print results
    print("\n=== Backtest Results ===")
    print(f"Initial equity: ¥{args.initial_cash:,.2f}")
    print(f"Final equity: ¥{result.portfolio.total_equity:,.2f}")
    print(f"Total return: {result.metrics.total_return:.2%}")
    print(f"Annual return: {result.metrics.annual_return:.2%}")
    print(f"Volatility: {result.metrics.volatility:.2%}")
    print(f"Sharpe ratio: {result.metrics.sharpe_ratio:.2f}")
    print(f"Max drawdown: {result.metrics.max_drawdown:.2%}")
    print(f"Total trades: {len(result.trades)}")

    # For visualization, test all multi-asset plots
    print("\n5. Creating multi-asset visualizations...")
    plotter = BacktestPlotter(result, price_data=raw_df)

    # Save all plots using save_all_plots
    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
    test_output_dir = output_dir / f"multi_asset_test_{timestamp}"
    paths = plotter.save_all_plots(test_output_dir, dpi=args.dpi)

    print(f"   Saved all plots to: {test_output_dir}")
    for name, path in paths.items():
        print(f"   - {name}: {path.name}")

    print("\n=== Test complete ===")


if __name__ == "__main__":
    main()
