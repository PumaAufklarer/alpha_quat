"""Tests for DataFeed implementations."""

import pandas as pd
from alpha_quat.data.feed import PandasDataFeed, MultiAssetDataFeed


def test_pandas_data_feed():
    """Test PandasDataFeed."""
    data = {
        "trade_date": [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")],
        "ts_code": ["000001.SZ", "000001.SZ"],
        "open": [10.0, 10.5],
        "high": [11.0, 11.5],
        "low": [9.5, 10.0],
        "close": [10.5, 11.0],
        "vol": [1000000, 1200000],
    }
    df = pd.DataFrame(data)
    feed = PandasDataFeed(df, datetime_col="trade_date")
    bars = list(feed)
    assert len(bars) == 2
    assert bars[0]["close"] == 10.5


def test_multi_asset_data_feed():
    """Test MultiAssetDataFeed."""
    data = {
        "trade_date": [
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-02"),
            pd.Timestamp("2024-01-02"),
        ],
        "ts_code": ["000001.SZ", "000002.SZ", "000001.SZ", "000002.SZ"],
        "open": [10.0, 20.0, 10.5, 20.5],
        "high": [11.0, 21.0, 11.5, 21.5],
        "low": [9.5, 19.5, 10.0, 20.0],
        "close": [10.5, 20.5, 11.0, 21.0],
        "vol": [1000000, 500000, 1200000, 600000],
    }
    df = pd.DataFrame(data)
    feed = MultiAssetDataFeed(df, datetime_col="trade_date", ts_code_col="ts_code")
    bars = list(feed)
    assert len(bars) == 2
    assert "datetime" in bars[0]
    assert "assets" in bars[0]
    assert "000001.SZ" in bars[0]["assets"]
    assert "000002.SZ" in bars[0]["assets"]
