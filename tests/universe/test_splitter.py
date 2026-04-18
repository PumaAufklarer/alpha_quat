"""Tests for TimeSplitter class."""

import pandas as pd

from alpha_quat.universe.splitter import TimeSplitter


def test_time_splitter_split():
    """Test TimeSplitter basic functionality."""
    data = pd.DataFrame({
        "ts_code": ["001", "001", "001", "001", "001"],
        "trade_date": ["20190101", "20190601", "20200101", "20210101", "20220101"],
        "close": [10, 11, 12, 13, 14],
    })

    splitter = TimeSplitter(date_column="trade_date")
    splits = splitter.split(
        data,
        train_end="20200101",
        val_end="20220101",
    )

    assert "train" in splits
    assert "val" in splits
    assert "test" in splits

    # Train: before 20200101 (exclusive)
    assert len(splits["train"]) == 2
    assert list(splits["train"]["trade_date"]) == ["20190101", "20190601"]

    # Val: 20200101 <= x < 20220101
    assert len(splits["val"]) == 2
    assert list(splits["val"]["trade_date"]) == ["20200101", "20210101"]

    # Test: >= 20220101
    assert len(splits["test"]) == 1
    assert list(splits["test"]["trade_date"]) == ["20220101"]


def test_time_splitter_no_val():
    """Test TimeSplitter when val_end is same as train_end (no val set)."""
    data = pd.DataFrame({
        "trade_date": ["20190101", "20200101", "20210101"],
    })

    splitter = TimeSplitter(date_column="trade_date")
    splits = splitter.split(
        data,
        train_end="20200101",
        val_end="20200101",  # Same as train_end = no val set
    )

    assert len(splits["train"]) == 1
    assert len(splits["val"]) == 0
    assert len(splits["test"]) == 2
