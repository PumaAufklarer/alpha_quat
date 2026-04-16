"""Common data sources wrapped with caching."""
from pathlib import Path
from typing import Optional, Tuple

import pandas as pd

from .fetcher import TushareFetcher
from .utils import get_or_fetch_data, merge_and_fetch_ts_data


class DataSource:
    """
    Data source class providing cached access to common tushare APIs.
    """

    def __init__(self, config_path: Optional[str] = None, data_dir: Optional[Path] = None):
        """
        Initialize DataSource.

        Args:
            config_path: Path to config.json file
            data_dir: Directory to store cached data
        """
        self.fetcher = TushareFetcher(config_path)
        self.pro = self.fetcher.get_pro_api()
        self.api = self.fetcher.get_api_wrapper()
        self.data_dir = data_dir

    def get_stock_list(
        self,
        exchange: str = "",
        list_status: str = "L",
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get stock basic information (static data).

        Args:
            exchange: Exchange code (SSE/SZSE/BSE, empty for all)
            list_status: List status (L: listed, D: delisted, P: suspended)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        exchange_suffix = f"_{exchange}" if exchange else ""
        data_name = f"stock_list{exchange_suffix}_{list_status}"

        def fetch():
            return self.pro.stock_basic(exchange=exchange, list_status=list_status)

        return get_or_fetch_data(data_name, fetch, self.data_dir, force_refresh, sub_dir="stock_list")

    def get_trade_calendar(
        self,
        start_date: str = "",
        end_date: str = "",
        exchange: str = "SSE",
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get trade calendar (time-series data, merged).

        Args:
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            exchange: Exchange code (SSE/SZSE)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        data_name = f"trade_cal_{exchange}"

        def fetch():
            return self.pro.trade_cal(exchange=exchange, start_date=start_date, end_date=end_date)

        return merge_and_fetch_ts_data(
            data_name, fetch, date_cols="cal_date",
            data_dir=self.data_dir, force_refresh=force_refresh,
            sub_dir="trade_cal"
        )

    def get_daily_basic(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get daily basic indicators (time-series data, merged).

        Args:
            ts_code: Stock code
            trade_date: Trade date (YYYYMMDD)
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        # Use ts_code in data_name for per-stock cache
        if ts_code:
            data_name = f"daily_basic_{ts_code}"
        else:
            data_name = "daily_basic_all"

        def fetch():
            if ts_code:
                # Use wrapper for single stock with pagination
                return self.api.fetch_until_complete(
                    "daily_basic",
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date,
                    trade_date=trade_date
                )
            else:
                return self.pro.daily_basic(
                    ts_code=ts_code,
                    trade_date=trade_date,
                    start_date=start_date,
                    end_date=end_date
                )

        return merge_and_fetch_ts_data(
            data_name, fetch, date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir, force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="daily_basic"
        )

    def get_index_daily(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get index daily data (time-series data, merged).

        Args:
            ts_code: Index code (e.g., 000001.SH for Shanghai Composite)
            trade_date: Trade date (YYYYMMDD)
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        if ts_code:
            data_name = f"index_daily_{ts_code}"
        else:
            data_name = "index_daily_all"

        def fetch():
            if ts_code:
                return self.api.fetch_until_complete(
                    "index_daily",
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date,
                    trade_date=trade_date
                )
            else:
                return self.pro.index_daily(
                    ts_code=ts_code,
                    trade_date=trade_date,
                    start_date=start_date,
                    end_date=end_date
                )

        return merge_and_fetch_ts_data(
            data_name, fetch, date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir, force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="index_daily"
        )

    def get_fund_list(
        self,
        market: str = "E",
        status: str = "L",
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get fund list (static data).

        Args:
            market: Market type (E: Exchange, O: OTC)
            status: Status (L: Listed, D: Delisted)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        data_name = f"fund_list_{market}_{status}"

        def fetch():
            return self.pro.fund_basic(market=market, status=status)

        return get_or_fetch_data(data_name, fetch, self.data_dir, force_refresh, sub_dir="fund")

    def get_fund_daily(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get fund daily data (time-series data, merged).

        Args:
            ts_code: Fund code
            trade_date: Trade date (YYYYMMDD)
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        if ts_code:
            data_name = f"fund_daily_{ts_code}"
        else:
            data_name = "fund_daily_all"

        def fetch():
            if ts_code:
                return self.api.fetch_until_complete(
                    "fund_daily",
                    ts_code=ts_code,
                    start_date=start_date,
                    end_date=end_date,
                    trade_date=trade_date
                )
            else:
                return self.pro.fund_daily(
                    ts_code=ts_code,
                    trade_date=trade_date,
                    start_date=start_date,
                    end_date=end_date
                )

        return merge_and_fetch_ts_data(
            data_name, fetch, date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir, force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="fund"
        )

    def get_fund_nav(
        self,
        ts_code: str = "",
        end_date: str = "",
        market: str = "E",
        force_refresh: bool = False
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get fund NAV data (time-series data, merged).

        Args:
            ts_code: Fund code
            end_date: End date (YYYYMMDD)
            market: Market type (E: Exchange, O: OTC)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        data_name = f"fund_nav_{ts_code}_{market}"

        def fetch():
            return self.pro.fund_nav(ts_code=ts_code, end_date=end_date, market=market)

        return merge_and_fetch_ts_data(
            data_name, fetch, date_cols=["ts_code", "end_date"],
            data_dir=self.data_dir, force_refresh=force_refresh,
            unique_key=["ts_code", "end_date"],
            sub_dir="fund"
        )
