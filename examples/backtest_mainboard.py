#!/usr/bin/env python3
"""
Backtest turtle strategy on main board stocks.
"""

import argparse
import logging

import pandas as pd

from backtest import BacktestEngine, DataFeed, Portfolio
from data_fetcher import DataSource
from examples import TurtleStrategy
from examples.turtle_strategy import prepare_single_stock_data

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SingleStockDataFeed(DataFeed):
    """Data feed for single stock with proper datetime handling."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        if "trade_date" in self.df.columns:
            self.df["trade_date"] = pd.to_datetime(self.df["trade_date"], format="%Y%m%d")
        self.df = self.df.sort_values("trade_date").reset_index(drop=True)
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


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Backtest turtle strategy on main board stocks")
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of stocks for testing"
    )
    parser.add_argument(
        "--days", type=int, default=5000, help="Number of days to backtest (default: 500)"
    )
    parser.add_argument(
        "--entry-period", type=int, default=20, help="Entry breakout period (default: 20)"
    )
    parser.add_argument(
        "--exit-period", type=int, default=10, help="Exit breakout period (default: 10)"
    )
    parser.add_argument(
        "--include-st", action="store_true", help="Include ST stocks (default: exclude ST stocks)"
    )
    parser.add_argument(
        "--use-atr", action="store_true", help="Use ATR for position sizing (default: False)"
    )
    return parser.parse_args()


def backtest_single_stock(
    ds: DataSource,
    ts_code: str,
    name: str,
    days: int,
    entry_period: int,
    exit_period: int,
    use_atr: bool,
) -> dict:
    """Backtest single stock and return results."""
    # Fetch daily OHLC data
    daily_df, _ = ds.get_daily(ts_code=ts_code)

    if daily_df.empty:
        return None

    # Prepare data with pre-computed features
    stock_df = prepare_single_stock_data(
        daily_df,
        ts_code,
        entry_period=entry_period,
        exit_period=exit_period,
    )
    stock_df = stock_df.tail(days).reset_index(drop=True)

    min_required = max(entry_period, exit_period) + 1
    if len(stock_df) < min_required:
        return None

    # Create data feed
    data_feed = SingleStockDataFeed(stock_df)

    # Create portfolio and strategy
    initial_cash = 100000.0
    portfolio = Portfolio(initial_cash=initial_cash)
    strategy = TurtleStrategy(
        entry_period=entry_period,
        exit_period=exit_period,
        position_size=100,
        use_atr=use_atr,
    )

    # Run backtest
    engine = BacktestEngine(data=data_feed, strategy=strategy, portfolio=portfolio)
    result = engine.run()

    return {
        "ts_code": ts_code,
        "name": name,
        "initial_equity": initial_cash,
        "final_equity": result.portfolio.total_equity,
        "total_return": result.metrics.total_return,
        "annual_return": result.metrics.annual_return,
        "volatility": result.metrics.volatility,
        "sharpe_ratio": result.metrics.sharpe_ratio,
        "max_drawdown": result.metrics.max_drawdown,
        "total_trades": len(result.trades),
    }


def main():
    """Run backtest on main board stocks."""
    args = parse_args()

    logger.info("=" * 60)
    logger.info("Turtle Strategy Backtest (with Feature Engineering) - Main Board")
    logger.info("=" * 60)
    logger.info(f"Configuration:")
    logger.info(f"  Entry period: {args.entry_period}")
    logger.info(f"  Exit period: {args.exit_period}")
    logger.info(f"  Use ATR sizing: {args.use_atr}")

    # Initialize data source
    logger.info("Initializing data source...")
    ds = DataSource()

    # Get stock list (main board only)
    logger.info("Fetching main board stock list...")
    stock_list, _ = ds.get_stock_list(list_status="L")
    stocks_to_test = stock_list[stock_list["market"] == "主板"].copy()
    logger.info(f"Found {len(stocks_to_test)} main board stocks")

    # Filter out ST stocks by default
    if not args.include_st and "name" in stocks_to_test.columns:
        st_mask = stocks_to_test["name"].str.startswith(("ST", "*ST"))
        stocks_to_test = stocks_to_test[~st_mask].copy()
        logger.info(f"Filtered out ST stocks, remaining: {len(stocks_to_test)}")

    # Limit stocks for testing (after ST filter)
    if args.limit is not None:
        stocks_to_test = stocks_to_test.head(args.limit)
        logger.info(f"Limited to {len(stocks_to_test)} stocks for testing")

    # Run backtests
    results: list[dict] = []
    for i, (_, row) in enumerate(stocks_to_test.iterrows(), 1):
        ts_code = row["ts_code"]
        name = row["name"]
        logger.info(f"[{i}/{len(stocks_to_test)}] Backtesting {name} ({ts_code})...")

        try:
            result = backtest_single_stock(
                ds,
                ts_code,
                name,
                days=args.days,
                entry_period=args.entry_period,
                exit_period=args.exit_period,
                use_atr=args.use_atr,
            )
            if result:
                results.append(result)
        except Exception as e:
            logger.error(f"Failed to backtest {ts_code}: {e}")

    # Output summary
    logger.info("=" * 60)
    logger.info("Backtest Summary")
    logger.info("=" * 60)
    logger.info(f"Total stocks tested: {len(stocks_to_test)}")
    logger.info(f"Successful backtests: {len(results)}")

    if results:
        results_df = pd.DataFrame(results)
        logger.info("\nAverage results:")
        logger.info(f"  Average total return: {results_df['total_return'].mean():.2%}")
        logger.info(f"  Average annual return: {results_df['annual_return'].mean():.2%}")
        logger.info(f"  Average Sharpe ratio: {results_df['sharpe_ratio'].mean():.2f}")
        logger.info(f"  Average max drawdown: {results_df['max_drawdown'].mean():.2%}")
        logger.info(f"  Average trades: {results_df['total_trades'].mean():.1f}")

        logger.info("\nTop 5 performers:")
        top5 = results_df.nlargest(5, "total_return")
        for _, row in top5.iterrows():
            logger.info(f"  {row['name']} ({row['ts_code']}): {row['total_return']:.2%}")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
