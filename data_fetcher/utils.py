"""Utility functions for data storage and caching."""

import logging
import re
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as filename.

    Args:
        name: String to sanitize

    Returns:
        Sanitized string
    """
    # Replace invalid characters with underscore
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    # Replace spaces with underscore
    name = name.replace(" ", "_")
    return name


def get_latest_parquet_path(
    data_dir: Path, data_name: str, sub_dir: str | None = None
) -> Path | None:
    """
    Get the latest parquet file path for given data name.

    Args:
        data_dir: Base directory to search in
        data_name: Name of the data
        sub_dir: Optional subdirectory to store data in

    Returns:
        Path to latest parquet file or None
    """
    if sub_dir:
        data_dir = data_dir / sub_dir

    if not data_dir.exists():
        return None

    sanitized_name = sanitize_filename(data_name)

    # More efficient: scan directory once and filter manually
    latest_file: Path | None = None
    latest_mtime = 0.0
    prefix = f"{sanitized_name}_"

    try:
        for file_path in data_dir.iterdir():
            if (
                file_path.is_file()
                and file_path.name.startswith(prefix)
                and file_path.suffix == ".parquet"
            ):
                mtime = file_path.stat().st_mtime
                if mtime > latest_mtime:
                    latest_mtime = mtime
                    latest_file = file_path
    except (FileNotFoundError, PermissionError):
        return None

    return latest_file


def is_data_up_to_date(file_path: Path, check_date: datetime | None = None) -> bool:
    """
    Check if data file is up to date for given date.

    Args:
        file_path: Path to parquet file
        check_date: Date to check against (defaults to today)

    Returns:
        True if data was updated on check_date
    """
    if check_date is None:
        check_date = datetime.now()

    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
    return file_mtime.date() == check_date.date()


def save_parquet_with_metadata(
    df: pd.DataFrame,
    data_dir: Path,
    data_name: str,
    timestamp: datetime | None = None,
    sub_dir: str | None = None,
) -> Path:
    """
    Save DataFrame to parquet file with timestamp in filename.

    Args:
        df: DataFrame to save
        data_dir: Base directory to save to
        data_name: Name of the data (for filename generation)
        timestamp: Timestamp to use (defaults to now)
        sub_dir: Optional subdirectory to store data in

    Returns:
        Path to saved file
    """
    if sub_dir:
        data_dir = data_dir / sub_dir
    data_dir.mkdir(parents=True, exist_ok=True)

    if timestamp is None:
        timestamp = datetime.now()

    sanitized_name = sanitize_filename(data_name)
    timestamp_str = timestamp.strftime("%Y%m%d")
    filename = f"{sanitized_name}_{timestamp_str}.parquet"
    file_path = data_dir / filename

    df.to_parquet(file_path, engine="pyarrow")
    return file_path


def load_parquet(file_path: Path) -> pd.DataFrame:
    """
    Load DataFrame from parquet file.

    Args:
        file_path: Path to parquet file

    Returns:
        Loaded DataFrame
    """
    return pd.read_parquet(file_path, engine="pyarrow")


def get_or_fetch_data(
    data_name: str,
    fetch_func: Callable[[], pd.DataFrame],
    data_dir: Path | None = None,
    force_refresh: bool = False,
    sub_dir: str | None = None,
) -> tuple[pd.DataFrame, bool]:
    """
    Get data from cache if up to date, otherwise fetch and save.

    Args:
        data_name: Unique name for the data
        fetch_func: Function to call to fetch fresh data
        data_dir: Directory to store cached data (defaults to ./data)
        force_refresh: If True, skip cache and always fetch
        sub_dir: Optional subdirectory to store data in

    Returns:
        Tuple of (DataFrame, is_fully_cached: bool)
        - is_fully_cached: True = data is fully cached (no API call)
                         False = API was called
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent / "data"

    latest_file = get_latest_parquet_path(data_dir, data_name, sub_dir=sub_dir)

    if not force_refresh and latest_file is not None and is_data_up_to_date(latest_file):
        # Use cached data
        logger.debug(f"[{data_name}] Already up-to-date, using cached data")
        return load_parquet(latest_file), True

    if force_refresh:
        logger.debug(f"[{data_name}] Force refresh enabled, fetching fresh data")
    elif latest_file is None:
        logger.debug(f"[{data_name}] No cache found, fetching fresh data")
    else:
        logger.debug(f"[{data_name}] Cache exists but not up-to-date, fetching fresh data")

    # Fetch fresh data
    df = fetch_func()
    save_parquet_with_metadata(df, data_dir, data_name, sub_dir=sub_dir)
    logger.debug(f"[{data_name}] Fetched {len(df)} records")
    return df, False


def merge_and_fetch_ts_data(
    data_name: str,
    fetch_func: Callable[[], pd.DataFrame],
    date_cols: list[str] | str = "trade_date",
    data_dir: Path | None = None,
    force_refresh: bool = False,
    unique_key: list[str] | str | None = None,
    sub_dir: str | None = None,
) -> tuple[pd.DataFrame, bool]:
    """
    Get time-series data, merge with existing cache if available.

    Args:
        data_name: Unique name for the data (should not include date ranges)
        fetch_func: Function to call to fetch fresh data
        date_cols: Column name(s) for date, used for deduplication
        data_dir: Directory to store cached data (defaults to ./data)
        force_refresh: If True, ignore cache and fetch all
        unique_key: Additional columns to use as unique key for deduplication
        sub_dir: Optional subdirectory to store data in

    Returns:
        Tuple of (merged DataFrame, is_fully_cached: bool)
        - is_fully_cached: True = data is fully cached (no API call)
                         False = API was called (either partial update or full fetch)
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent / "data"

    latest_file = get_latest_parquet_path(data_dir, data_name, sub_dir=sub_dir)
    existing_df = None

    if not force_refresh and latest_file is not None:
        existing_df = load_parquet(latest_file)

        # Check if today already updated
        if is_data_up_to_date(latest_file):
            logger.debug(f"[{data_name}] Already up-to-date, using cached data")
            return existing_df, True

        logger.debug(f"[{data_name}] Found existing cache, fetching updates...")

    # Fetch fresh data
    new_df = fetch_func()

    if new_df.empty:
        if existing_df is not None and not existing_df.empty:
            logger.debug(f"[{data_name}] No new data, using cached data only")
            return existing_df, False
        logger.debug(f"[{data_name}] No data found")
        return pd.DataFrame(), False

    # Merge with existing data
    if existing_df is not None and not existing_df.empty:
        # Combine and deduplicate
        if unique_key:
            # Use provided unique key
            key_cols = [unique_key] if isinstance(unique_key, str) else unique_key
            merged_df = pd.concat([existing_df, new_df], ignore_index=True)
            merged_df = merged_df.drop_duplicates(subset=key_cols, keep="last")
        else:
            # Use date column(s)
            date_cols_list = [date_cols] if isinstance(date_cols, str) else date_cols
            merged_df = pd.concat([existing_df, new_df], ignore_index=True)
            merged_df = merged_df.drop_duplicates(subset=date_cols_list, keep="last")

        new_rows = len(merged_df) - len(existing_df)
        logger.debug(
            f"[{data_name}] Merged cache + {len(new_df)} new records "
            f"({new_rows} new after dedup)"
        )
    else:
        merged_df = new_df
        logger.debug(f"[{data_name}] No existing cache, fetched {len(new_df)} records")

    # Sort by date ascending (oldest first)
    date_cols_list = [date_cols] if isinstance(date_cols, str) else date_cols
    if date_cols_list:
        merged_df = merged_df.sort_values(date_cols_list).reset_index(drop=True)

    # Save merged data
    save_parquet_with_metadata(merged_df, data_dir, data_name, sub_dir=sub_dir)
    return merged_df, False
