"""Base classes and cache utilities for data sources."""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Tuple

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import tushare as ts

logger = logging.getLogger(__name__)


@dataclass
class CacheMetadata:
    """Metadata for cached data files."""

    date_range_start: str | None
    date_range_end: str | None
    last_updated: float
    data_source: str = "tushare"


class DataSourceBase(ABC):
    """Base abstract class for all data sources."""

    pass


class OHLCDataSource(DataSourceBase):
    """Abstract base class for data sources with OHLC K-line data."""

    @abstractmethod
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
        Get daily OHLC data.

        Args:
            ts_code: Tushare asset code
            trade_date: Trade date (YYYYMMDD)
            start_date: Start date (YYYYMMDD)
            end_date: End date (YYYYMMDD)
            adj: Adjustment type: None (unadjusted), 'qfq' (前复权), 'hfq' (后复权)
            force_refresh: Skip cache if True

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        pass

    @abstractmethod
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
        Get weekly OHLC data.

        Args:
            Same as get_daily()

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        pass

    @abstractmethod
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
        Get monthly OHLC data.

        Args:
            Same as get_daily()

        Returns:
            Tuple of (DataFrame, is_cached)
        """
        pass


class TushareFetcher:
    """Helper class to initialize Tushare API."""

    def __init__(self, config_path: str | Path | None = None):
        """
        Initialize Tushare fetcher.

        Args:
            config_path: Path to config.json file
        """
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config.json"
        elif isinstance(config_path, str):
            config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")

        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)

        token = config.get("tushare", {}).get("token")
        if not token or token == "your_tushare_token_here":
            raise ValueError("Please set your tushare token in config.json")

        ts.set_token(token)
        self._pro = ts.pro_api()

    def get_pro_api(self):
        """Get Tushare pro API instance."""
        return self._pro


def _get_data_dir(data_dir: Path | None = None) -> Path:
    """Get data directory path."""
    if data_dir is None:
        data_dir = Path("data")
    return Path(data_dir)


def _get_cache_path(
    data_name: str,
    data_dir: Path | None = None,
    sub_dir: str | None = None,
) -> Path:
    """Get full path for cache file."""
    base_dir = _get_data_dir(data_dir)
    if sub_dir:
        cache_dir = base_dir / sub_dir
    else:
        cache_dir = base_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{data_name}.parquet"


def _read_parquet_with_metadata(path: Path) -> Tuple[pd.DataFrame, CacheMetadata | None]:
    """Read parquet file and extract metadata."""
    if not path.exists():
        return pd.DataFrame(), None

    table = pq.read_table(path)
    df = table.to_pandas()

    metadata = table.schema.metadata
    if metadata and b"cache_metadata" in metadata:
        metadata_dict = json.loads(metadata[b"cache_metadata"].decode("utf-8"))
        cache_meta = CacheMetadata(**metadata_dict)
    else:
        cache_meta = None

    return df, cache_meta


def _write_parquet_with_metadata(
    df: pd.DataFrame,
    path: Path,
    metadata: CacheMetadata,
):
    """Write DataFrame to parquet with metadata."""
    table = pa.Table.from_pandas(df)

    metadata_dict = asdict(metadata)
    existing_metadata = table.schema.metadata or {}
    existing_metadata[b"cache_metadata"] = json.dumps(metadata_dict).encode("utf-8")

    table = table.replace_schema_metadata(existing_metadata)
    pq.write_table(table, path)


def _extract_date_range(
    df: pd.DataFrame,
    date_cols: str | list[str],
) -> Tuple[str | None, str | None]:
    """Extract date range from DataFrame."""
    if df.empty:
        return None, None

    if isinstance(date_cols, str):
        date_col = date_cols
    else:
        date_col = date_cols[0] if date_cols else None

    if date_col and date_col in df.columns:
        dates = df[date_col].dropna().sort_values()
        if len(dates) > 0:
            return str(dates.iloc[0]), str(dates.iloc[-1])

    return None, None


def get_or_fetch_data(
    data_name: str,
    fetch_func: Callable[[], pd.DataFrame],
    data_dir: Path | None = None,
    force_refresh: bool = False,
    sub_dir: str | None = None,
) -> Tuple[pd.DataFrame, bool]:
    """
    Get static data from cache or fetch from API.

    Args:
        data_name: Name for cached data file
        fetch_func: Function to call to fetch data if not cached
        data_dir: Base directory for cached data
        force_refresh: Skip cache if True
        sub_dir: Subdirectory for cache file

    Returns:
        Tuple of (DataFrame, is_cached)
    """
    cache_path = _get_cache_path(data_name, data_dir, sub_dir)

    if not force_refresh and cache_path.exists():
        logger.debug(f"Loading cached data: {cache_path}")
        df, _ = _read_parquet_with_metadata(cache_path)
        if not df.empty:
            return df, True

    logger.debug(f"Fetching data: {data_name}")
    df = fetch_func()

    if not df.empty:
        date_start, date_end = _extract_date_range(
            df, "trade_date" if "trade_date" in df.columns else None
        )
        metadata = CacheMetadata(
            date_range_start=date_start,
            date_range_end=date_end,
            last_updated=datetime.now().timestamp(),
        )
        _write_parquet_with_metadata(df, cache_path, metadata)

    return df, False


def merge_and_fetch_ts_data(
    data_name: str,
    fetch_func: Callable[[], pd.DataFrame],
    date_cols: str | list[str],
    data_dir: Path | None = None,
    force_refresh: bool = False,
    unique_key: list[str] | None = None,
    sub_dir: str | None = None,
) -> Tuple[pd.DataFrame, bool]:
    """
    Get time-series data, merge with existing cache if available.

    Args:
        data_name: Name for cached data file
        fetch_func: Function to call to fetch new data
        date_cols: Date column(s) for sorting/merging
        data_dir: Base directory for cached data
        force_refresh: Skip cache if True
        unique_key: Columns to use for deduplication
        sub_dir: Subdirectory for cache file

    Returns:
        Tuple of (DataFrame, is_cached)
    """
    cache_path = _get_cache_path(data_name, data_dir, sub_dir)

    existing_df = pd.DataFrame()
    is_cached = False

    if not force_refresh and cache_path.exists():
        logger.debug(f"Loading cached data: {cache_path}")
        existing_df, _ = _read_parquet_with_metadata(cache_path)
        if not existing_df.empty:
            is_cached = True

    logger.debug(f"Fetching new data: {data_name}")
    new_df = fetch_func()

    if new_df.empty:
        if not existing_df.empty:
            return existing_df, True
        return pd.DataFrame(), False

    if existing_df.empty:
        merged_df = new_df
    else:
        merged_df = pd.concat([existing_df, new_df], ignore_index=True)
        if unique_key:
            merged_df = merged_df.drop_duplicates(subset=unique_key, keep="last")

    if isinstance(date_cols, str):
        date_cols = [date_cols]
    for date_col in date_cols:
        if date_col in merged_df.columns:
            merged_df = merged_df.sort_values(date_col, ascending=False).reset_index(drop=True)
            break

    date_start, date_end = _extract_date_range(merged_df, date_cols)
    metadata = CacheMetadata(
        date_range_start=date_start,
        date_range_end=date_end,
        last_updated=datetime.now().timestamp(),
    )
    _write_parquet_with_metadata(merged_df, cache_path, metadata)

    return merged_df, is_cached and not new_df.empty
