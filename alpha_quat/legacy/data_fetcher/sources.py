"""Common data sources wrapped with caching."""

import logging
from pathlib import Path

import pandas as pd
import tushare as ts

from .fetcher import TushareFetcher
from .utils import get_or_fetch_data, merge_and_fetch_ts_data

logger = logging.getLogger(__name__)


class DataSource:
    """
    Data source class providing cached access to common tushare APIs.
    """

    def __init__(self, config_path: str | None = None, data_dir: Path | None = None):
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
        self, exchange: str = "", list_status: str = "L", force_refresh: bool = False
    ) -> tuple[pd.DataFrame, bool]:
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

        return get_or_fetch_data(
            data_name, fetch, self.data_dir, force_refresh, sub_dir="stock_list"
        )

    def get_trade_calendar(
        self,
        start_date: str = "",
        end_date: str = "",
        exchange: str = "SSE",
        force_refresh: bool = False,
    ) -> tuple[pd.DataFrame, bool]:
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
            data_name,
            fetch,
            date_cols="cal_date",
            data_dir=self.data_dir,
            force_refresh=force_refresh,
            sub_dir="trade_cal",
        )

    def get_daily_basic(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        force_refresh: bool = False,
    ) -> tuple[pd.DataFrame, bool]:
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
                    trade_date=trade_date,
                )
            else:
                return self.pro.daily_basic(
                    ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date
                )

        return merge_and_fetch_ts_data(
            data_name,
            fetch,
            date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir,
            force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="daily_basic",
        )

    def get_daily(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        adj: str | None = None,
        force_refresh: bool = False,
    ) -> tuple[pd.DataFrame, bool]:
        """
        Get daily OHLC data (time-series data, merged).

        Args:
            ts_code: Stock code
            trade_date: Trade date (YYYYMMDD)
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            adj: Adjustment type: None (unadjusted), 'qfq' (前复权), 'hfq' (后复权)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        # Include adj in data_name for caching different adjusted data
        adj_suffix = f"_{adj}" if adj else ""
        if ts_code:
            data_name = f"daily_{ts_code}{adj_suffix}"
        else:
            data_name = f"daily_all{adj_suffix}"

        def fetch():
            if adj:
                # Use pro_bar for adjusted data with pagination
                all_dfs = []
                current_end_date = end_date
                max_rows_per_request = 6000

                while True:
                    logger.debug(f"Fetching {adj} daily for {ts_code}, end_date={current_end_date}")

                    df = ts.pro_bar(
                        ts_code=ts_code,
                        adj=adj,
                        start_date=start_date,
                        end_date=current_end_date,
                        api=self.pro,
                    )

                    if df is None or df.empty:
                        break

                    # Convert trade_date to string if it's datetime
                    if "trade_date" in df.columns:
                        if pd.api.types.is_datetime64_any_dtype(df["trade_date"]):
                            df["trade_date"] = df["trade_date"].dt.strftime("%Y%m%d")

                    all_dfs.append(df)

                    # Check if we've reached the start date or got less than max rows
                    if len(df) < max_rows_per_request:
                        break

                    if not start_date:
                        # If no start_date specified, continue fetching older data
                        if "trade_date" in df.columns:
                            df_sorted = df.sort_values("trade_date", ascending=True)
                            earliest_date = df_sorted.iloc[0]["trade_date"]
                            # Set end_date to earliest_date to get older data
                            if current_end_date == earliest_date:
                                break  # Prevent infinite loop
                            current_end_date = earliest_date
                        else:
                            break
                    else:
                        # If we have a start_date, check if we've reached it
                        if "trade_date" in df.columns:
                            df_sorted = df.sort_values("trade_date", ascending=True)
                            earliest_date = df_sorted.iloc[0]["trade_date"]
                            if earliest_date <= start_date:
                                break
                            current_end_date = earliest_date
                        else:
                            break

                if all_dfs:
                    result = pd.concat(all_dfs, ignore_index=True)
                    # Remove duplicates
                    if "trade_date" in result.columns:
                        result = result.drop_duplicates(subset=["trade_date"], keep="last")
                        # Sort in descending order to match tushare's default
                        result = result.sort_values("trade_date", ascending=False).reset_index(
                            drop=True
                        )
                    return result
                return pd.DataFrame()
            else:
                # Use original daily API for unadjusted data
                if ts_code:
                    return self.api.fetch_until_complete(
                        "daily",
                        ts_code=ts_code,
                        start_date=start_date,
                        end_date=end_date,
                        trade_date=trade_date,
                    )
                else:
                    return self.pro.daily(
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
            sub_dir="daily",
        )

    def get_index_daily(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        force_refresh: bool = False,
    ) -> tuple[pd.DataFrame, bool]:
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
                    trade_date=trade_date,
                )
            else:
                return self.pro.index_daily(
                    ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date
                )

        return merge_and_fetch_ts_data(
            data_name,
            fetch,
            date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir,
            force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="index_daily",
        )

    def get_fund_list(
        self, market: str = "E", status: str = "L", force_refresh: bool = False
    ) -> tuple[pd.DataFrame, bool]:
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
        force_refresh: bool = False,
    ) -> tuple[pd.DataFrame, bool]:
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
                    trade_date=trade_date,
                )
            else:
                return self.pro.fund_daily(
                    ts_code=ts_code, trade_date=trade_date, start_date=start_date, end_date=end_date
                )

        return merge_and_fetch_ts_data(
            data_name,
            fetch,
            date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir,
            force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="fund",
        )

    def get_fund_nav(
        self, ts_code: str = "", end_date: str = "", market: str = "E", force_refresh: bool = False
    ) -> tuple[pd.DataFrame, bool]:
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
            data_name,
            fetch,
            date_cols=["ts_code", "end_date"],
            data_dir=self.data_dir,
            force_refresh=force_refresh,
            unique_key=["ts_code", "end_date"],
            sub_dir="fund",
        )
