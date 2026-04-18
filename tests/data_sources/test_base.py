"""Tests for data_sources base module."""

import pytest


def test_import_data_sources_module():
    """Test that data_sources module can be imported."""
    from alpha_quat.data_sources import base

    assert base is not None
    assert hasattr(base, "DataSourceBase")
    assert hasattr(base, "OHLCDataSource")
    assert hasattr(base, "CacheMetadata")
    assert hasattr(base, "get_or_fetch_data")
    assert hasattr(base, "merge_and_fetch_ts_data")


def test_cache_metadata():
    """Test CacheMetadata dataclass."""
    from alpha_quat.data_sources.base import CacheMetadata
    from datetime import datetime

    metadata = CacheMetadata(
        date_range_start="20200101",
        date_range_end="20241231",
        last_updated=datetime.now().timestamp(),
    )

    assert metadata.date_range_start == "20200101"
    assert metadata.date_range_end == "20241231"
    assert metadata.data_source == "tushare"
