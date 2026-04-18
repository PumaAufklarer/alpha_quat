"""Index data source with daily/weekly/monthly support."""

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd

from .base import OHLCDataSource, TushareFetcher, merge_and_fetch_ts_data

logger = logging.getLogger(__name__)


class IndexDataSource(OHLCDataSource):
    """Data source for index data."""

    def __init__(self, config_path: str | None = None, data_dir: Path | None = None):
        """
        Initialize IndexDataSource.

        Args:
            config_path: Path to config.json file
            data_dir: Directory to store cached data
        """
        self.fetcher = TushareFetcher(config_path)
        self.pro = self.fetcher.get_pro_api()
        self.data_dir = data_dir

    def get_daily(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        adj: str | None = None,
        force_refresh: bool = False,
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get index daily OHLC data.

        Args:
            ts_code: Index code (e.g., 000001.SH for Shanghai Composite)
            trade_date: Trade date (YYYYMMDD)
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            adj: Not used for index data, present for interface compatibility
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        if ts_code:
            data_name = f"{ts_code}"
        else:
            data_name = "all"

        def fetch():
            return self.pro.index_daily(
                ts_code=ts_code,
                trade_date=trade_date,
                start_date=start_date,
                end_date=end_date,
            )

        return merge_and_fetch_ts_data(
            data_name,
            fetch,
            date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir,
            force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="index/daily",
        )

    def get_weekly(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        adj: str | None = None,
        force_refresh: bool = False,
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get index weekly OHLC data.

        Args:
            Same as get_daily()

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        if ts_code:
            data_name = f"{ts_code}"
        else:
            data_name = "all"

        def fetch():
            return self.pro.index_weekly(
                ts_code=ts_code,
                trade_date=trade_date,
                start_date=start_date,
                end_date=end_date,
            )

        return merge_and_fetch_ts_data(
            data_name,
            fetch,
            date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir,
            force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="index/weekly",
        )

    def get_monthly(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        adj: str | None = None,
        force_refresh: bool = False,
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get index monthly OHLC data.

        Args:
            Same as get_daily()

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        if ts_code:
            data_name = f"{ts_code}"
        else:
            data_name = "all"

        def fetch():
            return self.pro.index_monthly(
                ts_code=ts_code,
                trade_date=trade_date,
                start_date=start_date,
                end_date=end_date,
            )

        return merge_and_fetch_ts_data(
            data_name,
            fetch,
            date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir,
            force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="index/monthly",
        )
