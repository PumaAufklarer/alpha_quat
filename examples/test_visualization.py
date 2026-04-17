"""
Test script for backtest visualization.

This script runs a turtle strategy backtest and generates visualization plots.
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from backtest import BacktestEngine, BacktestPlotter, PandasDataFeed, Portfolio
from examples import TurtleStrategy
from examples.turtle_strategy import prepare_single_stock_data


def generate_sample_data(
    days: int = 250,
    ts_code: str = "000001.SZ",
    start_date: str = "2024-01-01",
) -> pd.DataFrame:
    """Generate sample OHLC data with a clear trend."""
    np.random.seed(42)

    dates = pd.date_range(start=start_date, periods=days, freq="D")

    # Generate an uptrend with some pullbacks
    t = np.arange(days)
    # Base trend + seasonality + noise
    base_price = 100 + 0.2 * t + 8 * np.sin(t / 15) + np.random.normal(0, 2, days)

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
    return df


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Backtest visualization test")
    parser.add_argument(
        "--ts-code",
        type=str,
        default="000001.SZ",
        help="Stock code (default: 000001.SZ)",
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
        default=100000.0,
        help="Initial cash for backtest (default: 100000.0)",
    )
    parser.add_argument(
        "--entry-period",
        type=int,
        default=20,
        help="Entry period for turtle strategy (default: 20)",
    )
    parser.add_argument(
        "--exit-period",
        type=int,
        default=10,
        help="Exit period for turtle strategy (default: 10)",
    )
    parser.add_argument(
        "--position-size",
        type=int,
        default=100,
        help="Position size per trade (default: 100)",
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
    """Run test for visualization."""
    args = parse_args()

    print("=== Testing Backtest Visualization ===\n")
    print("Parameters:")
    print(f"  ts_code: {args.ts_code}")
    print(f"  days: {args.days}")
    print(f"  start_date: {args.start_date}")
    print(f"  initial_cash: ¥{args.initial_cash:,.0f}")
    print(f"  entry_period: {args.entry_period}")
    print(f"  exit_period: {args.exit_period}")
    print(f"  position_size: {args.position_size}")

    # Create output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = Path(__file__).parent.parent / "output" / "plots"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\nOutput directory: {output_dir}")

    # Generate sample data
    print("\n1. Generating sample data...")
    raw_df = generate_sample_data(
        days=args.days,
        ts_code=args.ts_code,
        start_date=args.start_date,
    )
    print(f"   Raw data shape: {raw_df.shape}")

    # Prepare data with features
    print("\n2. Preparing data with features...")
    df = prepare_single_stock_data(
        raw_df,
        ts_code=args.ts_code,
        entry_period=args.entry_period,
        exit_period=args.exit_period,
    )
    print(f"   Data with features shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")

    # Create data feed
    print("\n3. Creating data feed...")
    data_feed = PandasDataFeed(df, datetime_col="trade_date")

    # Create portfolio and strategy
    print("\n4. Creating portfolio and strategy...")
    portfolio = Portfolio(initial_cash=args.initial_cash)
    strategy = TurtleStrategy(
        entry_period=args.entry_period,
        exit_period=args.exit_period,
        position_size=args.position_size,
        use_atr=False,
    )

    # Run backtest
    print("\n5. Running backtest...")
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

    # Create plotter
    print("\n6. Creating visualizations...")
    plotter = BacktestPlotter(result, price_data=df)

    # Save all plots
    print("\n7. Saving plots...")
    plot_paths = plotter.save_all_plots(output_dir, dpi=args.dpi)

    print("\n=== Plots saved ===")
    for name, path in plot_paths.items():
        print(f"  {name}: {path}")

    print("\n=== Test complete ===")


if __name__ == "__main__":
    main()
