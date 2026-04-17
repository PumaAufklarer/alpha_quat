"""Tushare API wrapper with rate limit handling and pagination."""

import logging
import time
from collections.abc import Callable
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


class TushareAPI:
    """
    Wrapper for tushare API with rate limit handling and pagination.
    """

    def __init__(self, pro_api):
        """
        Initialize with tushare pro api instance.

        Args:
            pro_api: Tushare pro api instance
        """
        self.pro = pro_api
        self.min_interval = 0.1  # 最小请求间隔（秒）
        self.last_request_time = 0.0
        self.max_retries = 5
        self.base_sleep_time = 1.0

    def _wait_rate_limit(self):
        """Ensure minimum interval between requests."""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def _call_with_retry(self, func: Callable, **kwargs) -> Any:
        """
        Call API function with retry on rate limit.

        Args:
            func: API function to call
            **kwargs: Arguments for the function

        Returns:
            API result
        """
        retries = 0
        while retries < self.max_retries:
            try:
                self._wait_rate_limit()
                return func(**kwargs)
            except Exception as e:
                error_msg = str(e)
                if "最多访问" in error_msg.lower():
                    retries += 1
                    sleep_time = self.base_sleep_time * (2**retries)  # 指数退避
                    logger.warning(
                        f"Rate limit hit, retrying in {sleep_time:.1f}s "
                        f"(attempt {retries}/{self.max_retries})"
                    )
                    time.sleep(sleep_time)
                else:
                    # Not a rate limit error, re-raise
                    raise

        raise Exception(f"Max retries ({self.max_retries}) exceeded")

    def query(self, api_name: str, **kwargs) -> pd.DataFrame:
        """
        Query tushare API.

        Args:
            api_name: API name (e.g., 'daily_basic', 'index_daily')
            **kwargs: API parameters

        Returns:
            Result DataFrame
        """

        def api_call():
            return self.pro.query(api_name, **kwargs)

        return self._call_with_retry(api_call)

    def fetch_until_complete(
        self,
        api_name: str,
        ts_code: str,
        end_date: str = "",
        start_date: str = "",
        trade_date: str = "",
        date_column: str = "trade_date",
        max_rows_per_request: int = 6000,
    ) -> pd.DataFrame:
        """
        Fetch data with pagination until we get the latest data.

        Args:
            api_name: API name
            ts_code: Stock/asset code
            end_date: End date (YYYYMMDD)
            start_date: Start date (YYYYMMDD)
            trade_date: Specific trade date
            date_column: Column name for date
            max_rows_per_request: Max rows per request (tushare limit is 6000)

        Returns:
            Complete DataFrame
        """
        all_dfs = []
        current_end_date = end_date

        while True:
            logger.debug(f"Fetching {api_name} for {ts_code}, end_date={current_end_date}")

            kwargs = {
                "ts_code": ts_code,
                "start_date": start_date,
            }
            if current_end_date:
                kwargs["end_date"] = current_end_date
            if trade_date:
                kwargs["trade_date"] = trade_date

            df = self.query(api_name, **kwargs)

            if df.empty:
                break

            all_dfs.append(df)

            # Check if we've reached the start date or got less than max rows
            if len(df) < max_rows_per_request:
                break

            if not start_date:
                # If no start_date specified, check if we need to continue
                # Get the earliest date in this batch and continue fetching from there
                if date_column in df.columns:
                    df_sorted = df.sort_values(date_column, ascending=True)
                    earliest_date = df_sorted.iloc[0][date_column]
                    # Set end_date to one day before earliest_date to get older data
                    current_end_date = earliest_date
                    # To prevent infinite loop, if we get the same date twice, break
                    if current_end_date == end_date:
                        break
                    end_date = current_end_date
                else:
                    break
            else:
                # If we have a start_date, check if we've reached it
                if date_column in df.columns:
                    df_sorted = df.sort_values(date_column, ascending=True)
                    earliest_date = df_sorted.iloc[0][date_column]
                    if earliest_date <= start_date:
                        break
                    # Continue fetching older data
                    current_end_date = earliest_date
                else:
                    break

        if all_dfs:
            result = pd.concat(all_dfs, ignore_index=True)
            # Remove duplicates
            if date_column in result.columns:
                result = result.drop_duplicates(subset=[date_column], keep="last")
                result = result.sort_values(date_column, ascending=False).reset_index(drop=True)
            return result

        return pd.DataFrame()
