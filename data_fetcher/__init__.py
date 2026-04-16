"""Data fetcher module for ETF quantitative analysis."""

from .fetcher import TushareFetcher
from .sources import DataSource
from .tushare_api import TushareAPI
from .utils import (
    get_latest_parquet_path,
    get_or_fetch_data,
    is_data_up_to_date,
    load_parquet,
    merge_and_fetch_ts_data,
    save_parquet_with_metadata,
)

__all__ = [
    "TushareFetcher",
    "DataSource",
    "TushareAPI",
    "get_or_fetch_data",
    "merge_and_fetch_ts_data",
    "save_parquet_with_metadata",
    "load_parquet",
    "get_latest_parquet_path",
    "is_data_up_to_date",
]
