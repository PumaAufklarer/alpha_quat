#!/usr/bin/env python3
"""
Backtest turtle strategy on main board stocks using new framework.
"""

from __future__ import annotations

import argparse
import logging

import pandas as pd
from data_fetcher import DataSource

from alpha_quat.backtest.engine import BacktestEngine
from alpha_quat.data.feed import PandasDataFeed
from examples.turtle_strategy import TurtleStrategy, prepare_single_stock_data

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Backtest turtle strategy on main board stocks")
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of stocks for testing"
    )
    parser.add_argument(
        "--days", type=int, default=500, help="Number of days to backtest (default: 500)"
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
    parser.add_argument(
        "--adj",
        type=str,
        default="qfq",
        choices=[None, "qfq", "hfq"],
        help="Price adjustment type: None (unadjusted), qfq (前复权, default), hfq (后复权)",
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
    adj: str | None,
) -> dict | None:
    """
    回测单只股票并返回结果

    注意: 新框架的 BacktestEngine 的 _execute_signals 目前是占位实现，
    此函数展示了如何集成新框架，实际交易执行逻辑需要进一步完善。
    """
    # 获取日线 OHLC 数据
    daily_df, _ = ds.get_daily(ts_code=ts_code, adj=adj)

    if daily_df.empty:
        return None

    # 准备数据，预计算特征
    stock_df = prepare_single_stock_data(
        daily_df,
        ts_code,
        entry_period=entry_period,
        exit_period=exit_period,
    )
    stock_df = stock_df.tail(days).reset_index(drop=True)

    # 检查数据量是否足够
    min_required = max(entry_period, exit_period) + 1
    if len(stock_df) < min_required:
        return None

    # 确保有 datetime 列
    if "trade_date" in stock_df.columns and "datetime" not in stock_df.columns:
        stock_df["datetime"] = stock_df["trade_date"]

    # 创建数据馈送
    data_feed = PandasDataFeed(stock_df, datetime_col="datetime")

    # 创建策略
    strategy = TurtleStrategy(
        entry_period=entry_period,
        exit_period=exit_period,
        position_size=100,
        use_atr=use_atr,
    )

    # 创建回测引擎
    initial_capital = 100000.0
    engine = BacktestEngine(
        data_feed=data_feed,
        strategy=strategy,
        initial_capital=initial_capital,
    )

    # 运行回测
    logger.info(f"Running backtest for {name} ({ts_code})...")
    result = engine.run()

    # 计算简单的收益率指标
    total_return = (result.final_capital - initial_capital) / initial_capital

    return {
        "ts_code": ts_code,
        "name": name,
        "initial_equity": initial_capital,
        "final_equity": result.final_capital,
        "total_return": total_return,
        # 注意: 新框架的 analytics 模块可以用来计算更丰富的指标
    }


def main():
    """Run backtest on main board stocks."""
    args = parse_args()

    logger.info("=" * 60)
    logger.info("Turtle Strategy Backtest (New Framework) - Main Board")
    logger.info("=" * 60)
    logger.info("Configuration:")
    logger.info(f"  Entry period: {args.entry_period}")
    logger.info(f"  Exit period: {args.exit_period}")
    logger.info(f"  Use ATR sizing: {args.use_atr}")
    logger.info(f"  Price adjustment: {args.adj or 'None (unadjusted)'}")
    logger.info("=" * 60)
    logger.info("NOTE: New framework backtest engine is a work in progress.")
    logger.info("      Signal execution logic is currently a placeholder.")
    logger.info("=" * 60)

    # 初始化数据源
    logger.info("Initializing data source...")
    ds = DataSource()

    # 获取股票列表（仅主板）
    logger.info("Fetching main board stock list...")
    stock_list, _ = ds.get_stock_list(list_status="L")
    stocks_to_test = stock_list[stock_list["market"] == "主板"].copy()
    logger.info(f"Found {len(stocks_to_test)} main board stocks")

    # 默认过滤 ST 股票
    if not args.include_st and "name" in stocks_to_test.columns:
        st_mask = stocks_to_test["name"].str.startswith(("ST", "*ST"))
        stocks_to_test = stocks_to_test[~st_mask].copy()
        logger.info(f"Filtered out ST stocks, remaining: {len(stocks_to_test)}")

    # 限制测试股票数量
    if args.limit is not None:
        stocks_to_test = stocks_to_test.head(args.limit)
        logger.info(f"Limited to {len(stocks_to_test)} stocks for testing")

    # 运行回测
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
                adj=args.adj,
            )
            if result:
                results.append(result)
        except Exception as e:
            logger.error(f"Failed to backtest {ts_code}: {e}")

    # 输出汇总
    logger.info("=" * 60)
    logger.info("Backtest Summary")
    logger.info("=" * 60)
    logger.info(f"Total stocks tested: {len(stocks_to_test)}")
    logger.info(f"Successful backtests: {len(results)}")

    if results:
        results_df = pd.DataFrame(results)
        logger.info("\nAverage results:")
        logger.info(f"  Average total return: {results_df['total_return'].mean():.2%}")
        logger.info(f"  Average final equity: {results_df['final_equity'].mean():.2f}")

        logger.info("\nTop 5 performers:")
        top5 = results_df.nlargest(5, "total_return")
        for _, row in top5.iterrows():
            logger.info(f"  {row['name']} ({row['ts_code']}): {row['total_return']:.2%}")

    logger.info("=" * 60)


if __name__ == "__main__":
    main()
