"""Stock data source with daily/weekly/monthly support."""

import logging
from pathlib import Path
from typing import Tuple

import pandas as pd
import tushare as ts

from .base import OHLCDataSource, TushareFetcher, get_or_fetch_data, merge_and_fetch_ts_data

logger = logging.getLogger(__name__)


class StockDataSource(OHLCDataSource):
    """Data source for stock data."""

    def __init__(self, config_path: str | None = None, data_dir: Path | None = None):
        """
        Initialize StockDataSource.

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
        Get stock daily OHLC data.

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
        adj_suffix = f"_{adj}" if adj else ""
        if ts_code:
            data_name = f"{ts_code}{adj_suffix}"
        else:
            data_name = f"all{adj_suffix}"

        def fetch():
            if adj:
                return self._fetch_adjusted_daily(ts_code, adj, start_date, end_date)
            else:
                return self._fetch_unadjusted_daily(ts_code, trade_date, start_date, end_date)

        return merge_and_fetch_ts_data(
            data_name,
            fetch,
            date_cols=["ts_code", "trade_date"],
            data_dir=self.data_dir,
            force_refresh=force_refresh,
            unique_key=["ts_code", "trade_date"],
            sub_dir="stock/daily",
        )

    def _fetch_adjusted_daily(
        self,
        ts_code: str,
        adj: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Fetch adjusted daily data using pro_bar."""
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

            if "trade_date" in df.columns:
                if pd.api.types.is_datetime64_any_dtype(df["trade_date"]):
                    df["trade_date"] = df["trade_date"].dt.strftime("%Y%m%d")

            all_dfs.append(df)

            if len(df) < max_rows_per_request:
                break

            if not start_date:
                if "trade_date" in df.columns:
                    df_sorted = df.sort_values("trade_date", ascending=True)
                    earliest_date = df_sorted.iloc[0]["trade_date"]
                    if current_end_date == earliest_date:
                        break
                    current_end_date = earliest_date
                else:
                    break
            else:
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
            if "trade_date" in result.columns:
                result = result.drop_duplicates(subset=["trade_date"], keep="last")
                result = result.sort_values("trade_date", ascending=False).reset_index(
                    drop=True
                )
            return result
        return pd.DataFrame()

    def _fetch_unadjusted_daily(
        self,
        ts_code: str,
        trade_date: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """Fetch unadjusted daily data."""
        return self.pro.daily(
            ts_code=ts_code,
            trade_date=trade_date,
            start_date=start_date,
            end_date=end_date,
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
        Get stock weekly OHLC data.

        Args:
            Same as get_daily()

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        adj_suffix = f"_{adj}" if adj else ""
        if ts_code:
            data_name = f"{ts_code}{adj_suffix}"
        else:
            data_name = f"all{adj_suffix}"

        def fetch():
            return self.pro.weekly(
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
            sub_dir="stock/weekly",
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
        Get stock monthly OHLC data.

        Args:
            Same as get_daily()

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        adj_suffix = f"_{adj}" if adj else ""
        if ts_code:
            data_name = f"{ts_code}{adj_suffix}"
        else:
            data_name = f"all{adj_suffix}"

        def fetch():
            return self.pro.monthly(
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
            sub_dir="stock/monthly",
        )

    def get_daily_basic(
        self,
        ts_code: str = "",
        trade_date: str = "",
        start_date: str = "",
        end_date: str = "",
        force_refresh: bool = False,
    ) -> Tuple[pd.DataFrame, bool]:
        """
        Get stock daily basic indicators (PE, PB, etc.).

        Args:
            ts_code: Stock code
            trade_date: Trade date (YYYYMMDD)
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        if ts_code:
            data_name = f"{ts_code}"
        else:
            data_name = "all"

        def fetch():
            return self.pro.daily_basic(
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
            sub_dir="stock/daily_basic",
        )
