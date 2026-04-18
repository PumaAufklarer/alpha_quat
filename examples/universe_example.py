#!/usr/bin/env python3
"""
Example demonstrating universe selection and filtering.

Shows how to:
1. Fetch stock data
2. Create filter conditions
3. Apply filters to get a filtered universe
4. Split into train/validation/test sets
"""

from __future__ import annotations

import logging

import pandas as pd

from alpha_quat.universe import (
    Filter,
    IsSTCondition,
    ListingDateCondition,
    MarketCapCondition,
    TimeSplitter,
    Universe,
    ValueCondition,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_sample_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create sample data for demonstration (doesn't require DataSource)."""
    # Sample stock list
    stock_list = pd.DataFrame(
        {
            "ts_code": ["000001.SZ", "000002.SZ", "000004.SZ", "600000.SH", "600036.SH"],
            "name": ["平安银行", "万科A", "ST国华", "浦发银行", "招商银行"],
            "market": ["主板", "主板", "主板", "主板", "主板"],
            "list_date": ["19910403", "19910129", "20000101", "19991110", "20020409"],
        }
    )

    # Sample daily basic data
    trade_dates = ["20231201", "20231202", "20231203"]
    records = []
    for ts_code in stock_list["ts_code"]:
        for trade_date in trade_dates:
            records.append(
                {
                    "ts_code": ts_code,
                    "trade_date": trade_date,
                    "close": 10.0 + hash(ts_code) % 100,
                    "total_mv": 100.0 + hash(ts_code) % 900,
                    "pe": 10.0 + hash(ts_code) % 50,
                    "pb": 1.0 + hash(ts_code) % 10,
                }
            )
    daily_basic = pd.DataFrame(records)

    return stock_list, daily_basic


def main():
    """Run the example."""
    logger.info("=" * 60)
    logger.info("Stock Universe Selection Example")
    logger.info("=" * 60)

    # 1. Get data (using sample data for this example)
    logger.info("Creating sample data...")
    stock_list, daily_basic = create_sample_data()

    # To use real data (uncomment):
    # from alpha_quat.legacy.data_fetcher.sources import DataSource
    # ds = DataSource()
    # stock_list, _ = ds.get_stock_list(list_status="L")
    # daily_basic, _ = ds.get_daily_basic()

    # 2. Create universe
    logger.info("Creating universe...")
    universe = Universe(stock_list=stock_list, daily_basic=daily_basic)
    logger.info(f"Original universe: {len(universe.get_stocks())} stocks")

    # 3. Create filter conditions
    logger.info("Creating filter...")
    filter = Filter(
        [
            MarketCapCondition(min_mv=200, max_mv=800),  # Market cap 20-80B
            ListingDateCondition(min_days=365 * 5),  # Listed > 5 years
            IsSTCondition(exclude=True),  # Exclude ST stocks
            ValueCondition("pe", ">", 0),  # PE > 0 (profitable)
        ]
    )
    logger.info(f"Filter: {filter.name}")

    # 4. Apply filter
    logger.info("Applying filter...")
    filtered_universe = universe.filter(filter)
    logger.info(f"Filtered universe: {len(filtered_universe.get_stocks())} stocks")
    logger.info(f"Selected stocks: {filtered_universe.get_stocks()}")

    # 5. Split into train/val/test
    logger.info("Splitting into train/val/test...")
    splitter = TimeSplitter(date_column="trade_date")
    splits = splitter.split(
        filtered_universe.daily_basic,
        train_end="20231202",
        val_end="20231203",
    )
    logger.info(f"Train: {len(splits['train'])} records")
    logger.info(f"Val: {len(splits['val'])} records")
    logger.info(f"Test: {len(splits['test'])} records")

    logger.info("=" * 60)
    logger.info("Example complete!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
