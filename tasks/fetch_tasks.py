"""Data fetching tasks."""

import logging
from typing import Any

import pandas as pd

from data_fetcher import DataSource

from .base import Task

logger = logging.getLogger(__name__)


class FetchStockListTask(Task):
    """Task to fetch stock list."""

    def __init__(
        self,
        ds: DataSource,
        exchange: str = "",
        list_status: str = "L",
        force_refresh: bool = False,
    ):
        super().__init__("fetch_stock_list")
        self.ds = ds
        self.exchange = exchange
        self.list_status = list_status
        self.force_refresh = force_refresh

    def run(self) -> pd.DataFrame:
        df, is_cached = self.ds.get_stock_list(
            exchange=self.exchange, list_status=self.list_status, force_refresh=self.force_refresh
        )
        logger.info(f"Fetched {len(df)} stocks (cached: {is_cached})")
        return df


class FetchDailyBasicTask(Task):
    """Task to fetch daily basic data for a stock."""

    def __init__(
        self,
        ds: DataSource,
        ts_code: str,
        start_date: str = "",
        end_date: str = "",
        force_refresh: bool = False,
    ):
        super().__init__(f"fetch_daily_basic_{ts_code}")
        self.ds = ds
        self.ts_code = ts_code
        self.start_date = start_date
        self.end_date = end_date
        self.force_refresh = force_refresh

    def run(self) -> pd.DataFrame:
        df, is_cached = self.ds.get_daily_basic(
            ts_code=self.ts_code,
            start_date=self.start_date,
            end_date=self.end_date,
            force_refresh=self.force_refresh,
        )
        logger.info(f"Fetched {len(df)} records for {self.ts_code} (cached: {is_cached})")
        return df


class FetchAllTask(Task):
    """
    Task to fetch all data:
    1. Fetch stock list
    2. Fetch daily basic for each stock
    """

    def __init__(
        self,
        ds: DataSource,
        start_date: str = "",
        end_date: str = "",
        exchange: str = "",
        list_status: str = "L",
        force_refresh: bool = False,
        limit: int | None = None,
        markets: list[str] | None = None,
    ):
        super().__init__("fetch_all")
        self.ds = ds
        self.start_date = start_date
        self.end_date = end_date
        self.exchange = exchange
        self.list_status = list_status
        self.force_refresh = force_refresh
        self.limit = limit
        self.markets = markets

    def run(self) -> dict[str, Any]:
        results: dict[str, Any] = {}

        # Step 1: Fetch stock list
        logger.info("Step 1: Fetching stock list")
        stock_list_task = FetchStockListTask(
            self.ds,
            exchange=self.exchange,
            list_status=self.list_status,
            force_refresh=self.force_refresh,
        )
        stock_df = stock_list_task.run()
        results["stock_list"] = stock_df

        if stock_df.empty:
            logger.warning("No stocks found, skipping daily basic fetch")
            return results

        # Filter by markets if specified
        stocks_to_fetch = stock_df
        if self.markets is not None and len(self.markets) > 0:
            if "market" in stock_df.columns:
                stocks_to_fetch = stock_df[stock_df["market"].isin(self.markets)].copy()
                logger.info(f"Filtered to {len(stocks_to_fetch)} stocks in markets: {self.markets}")
            else:
                logger.warning("'market' column not found in stock list, skipping market filter")

        if stocks_to_fetch.empty:
            logger.warning("No stocks found after market filter, skipping daily basic fetch")
            return results

        # Limit if needed
        if self.limit is not None:
            stocks_to_fetch = stocks_to_fetch.head(self.limit)
            logger.info(f"Limited to {self.limit} stocks for testing")

        # Step 2: Fetch daily basic for each stock
        logger.info(f"Step 2: Fetching daily basic for {len(stocks_to_fetch)} stocks")
        daily_results = []

        for _, row in stocks_to_fetch.iterrows():
            ts_code = row["ts_code"]
            try:
                daily_task = FetchDailyBasicTask(
                    self.ds,
                    ts_code=ts_code,
                    start_date=self.start_date,
                    end_date=self.end_date,
                    force_refresh=self.force_refresh,
                )
                daily_df = daily_task.run()
                if not daily_df.empty:
                    daily_results.append(daily_df)
            except Exception as e:
                logger.error(f"Failed to fetch daily basic for {ts_code}: {e}")

        if daily_results:
            all_daily_df = pd.concat(daily_results, ignore_index=True)
            results["daily_basic"] = all_daily_df
            logger.info(f"Fetched total {len(all_daily_df)} daily basic records")
        else:
            results["daily_basic"] = pd.DataFrame()
            logger.warning("No daily basic data fetched")

        return results
