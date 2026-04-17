#!/usr/bin/env python3
"""
Daily run script for ETF quantitative analysis.

This script executes all daily tasks in sequence:
1. Fetch stock list
2. Fetch daily basic data for all stocks
3. (TODO) Run quantitative analysis
4. (TODO) Send email report
"""

import argparse
import logging
from datetime import datetime

from data_fetcher import DataSource
from tasks import FetchAllTask, Scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Daily run script for ETF quant")
    parser.add_argument(
        "--start-date",
        type=str,
        default="",
        help="Start date (YYYYMMDD), default: empty (tushare default)",
    )
    parser.add_argument(
        "--end-date", type=str, default="", help="End date (YYYYMMDD), default: empty (today)"
    )
    parser.add_argument(
        "--exchange", type=str, default="", help="Exchange code (SSE/SZSE/BSE), default: all"
    )
    parser.add_argument(
        "--list-status",
        type=str,
        default="L",
        help="List status (L: listed, D: delisted, P: suspended), default: L",
    )
    parser.add_argument(
        "--force-refresh", action="store_true", help="Force refresh data even if cached"
    )
    parser.add_argument(
        "--limit", type=int, default=None, help="Limit number of stocks for testing"
    )
    parser.add_argument(
        "--no-stop-on-error", action="store_true", help="Continue execution even if a task fails"
    )
    parser.add_argument(
        "--markets",
        type=str,
        nargs="*",
        default=["主板"],
        help="Market segments to fetch (e.g., '主板' '科创板' '创业板' '北交所'), default: '主板'",
    )
    parser.add_argument(
        "--adj",
        type=str,
        default="qfq",
        choices=[None, "qfq", "hfq"],
        help="Price adjustment type for daily OHLC: None (unadjusted), qfq (前复权, default), hfq (后复权)",
    )
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()

    logger.info("=" * 60)
    logger.info("ETF Quant Daily Run")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    # Initialize data source
    logger.info("Initializing data source...")
    ds = DataSource()

    # Create scheduler
    stop_on_error = not args.no_stop_on_error
    scheduler = Scheduler(stop_on_error=stop_on_error)

    # Add FetchAllTask
    logger.info("Adding FetchAllTask to scheduler...")
    fetch_task = FetchAllTask(
        ds,
        start_date=args.start_date,
        end_date=args.end_date,
        exchange=args.exchange,
        list_status=args.list_status,
        force_refresh=args.force_refresh,
        limit=args.limit,
        markets=args.markets,
        adj=args.adj,
    )
    scheduler.add_task(fetch_task)

    # TODO: Add quantitative analysis task here
    # TODO: Add email report task here

    # Run all tasks
    logger.info("Starting scheduler...")
    try:
        results = scheduler.run()

        # Log summary
        logger.info("=" * 60)
        logger.info("Run Summary")
        logger.info("=" * 60)

        if results:
            fetch_result = results[0]
            if fetch_result:
                stock_list = fetch_result.get("stock_list")
                daily_basic = fetch_result.get("daily_basic")
                daily = fetch_result.get("daily")
                if stock_list is not None:
                    logger.info(f"Stocks fetched: {len(stock_list)}")
                if daily_basic is not None:
                    logger.info(f"Daily basic records fetched: {len(daily_basic)}")
                if daily is not None:
                    logger.info(f"Daily OHLC records fetched: {len(daily)}")

        logger.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Run failed: {e}")
        raise


if __name__ == "__main__":
    main()
