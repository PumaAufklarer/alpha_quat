"""Utility functions for data storage and caching."""
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

import pandas as pd


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as filename.

    Args:
        name: String to sanitize

    Returns:
        Sanitized string
    """
    # Replace invalid characters with underscore
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    # Replace spaces with underscore
    name = name.replace(' ', '_')
    return name


def get_latest_parquet_path(data_dir: Path, data_name: str, sub_dir: Optional[str] = None) -> Optional[Path]:
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
    sanitized_name = sanitize_filename(data_name)
    pattern = f"{sanitized_name}_*.parquet"
    files = list(data_dir.glob(pattern))

    if not files:
        return None

    # Sort by modification time, newest first
    files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    return files[0]


def is_data_up_to_date(file_path: Path, check_date: Optional[datetime] = None) -> bool:
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
    timestamp: Optional[datetime] = None,
    sub_dir: Optional[str] = None
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
    data_dir: Optional[Path] = None,
    force_refresh: bool = False,
    sub_dir: Optional[str] = None
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
        Tuple of (DataFrame, is_cached: bool)
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent / "data"

    latest_file = get_latest_parquet_path(data_dir, data_name, sub_dir=sub_dir)

    if not force_refresh and latest_file is not None and is_data_up_to_date(latest_file):
        # Use cached data
        return load_parquet(latest_file), True

    # Fetch fresh data
    df = fetch_func()
    save_parquet_with_metadata(df, data_dir, data_name, sub_dir=sub_dir)
    return df, False


def merge_and_fetch_ts_data(
    data_name: str,
    fetch_func: Callable[[], pd.DataFrame],
    date_cols: list[str] | str = "trade_date",
    data_dir: Optional[Path] = None,
    force_refresh: bool = False,
    unique_key: Optional[list[str] | str] = None,
    sub_dir: Optional[str] = None
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
        Tuple of (merged DataFrame, is_partially_cached: bool)
    """
    if data_dir is None:
        data_dir = Path(__file__).parent.parent / "data"

    latest_file = get_latest_parquet_path(data_dir, data_name, sub_dir=sub_dir)
    existing_df = None
    is_partially_cached = False

    if not force_refresh and latest_file is not None:
        existing_df = load_parquet(latest_file)
        is_partially_cached = True

        # Check if today already updated
        if is_data_up_to_date(latest_file):
            return existing_df, True

    # Fetch fresh data
    new_df = fetch_func()

    if new_df.empty:
        return existing_df if existing_df is not None else pd.DataFrame(), is_partially_cached

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
    else:
        merged_df = new_df

    # Save merged data
    save_parquet_with_metadata(merged_df, data_dir, data_name, sub_dir=sub_dir)
    return merged_df, is_partially_cached
