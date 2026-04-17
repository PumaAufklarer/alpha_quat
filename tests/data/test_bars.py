"""Tests for Bar data structures."""

from datetime import datetime

import pandas as pd

from alpha_quat.core.types import Price
from alpha_quat.data.bars import Bar, BarData


def test_bar_creation():
    """Test creating a Bar."""
    dt = datetime(2024, 1, 1)
    bar = Bar(
        ts_code="000001.SZ",
        timestamp=dt,
        open=10.0,
        high=11.0,
        low=9.5,
        close=10.5,
        volume=1000000,
    )
    assert bar.ts_code == "000001.SZ"
    assert bar.close == 10.5
    assert bar.typical_price == Price((11.0 + 9.5 + 10.5) / 3)


def test_bar_data_creation():
    """Test creating BarData from DataFrame."""
    data = {
        "ts_code": ["000001.SZ", "000001.SZ"],
        "trade_date": [pd.Timestamp("2024-01-01"), pd.Timestamp("2024-01-02")],
        "open": [10.0, 10.5],
        "high": [11.0, 11.5],
        "low": [9.5, 10.0],
        "close": [10.5, 11.0],
        "vol": [1000000, 1200000],
    }
    df = pd.DataFrame(data)
    bar_data = BarData.from_dataframe(df, ts_code_col="ts_code", datetime_col="trade_date")
    assert len(bar_data.bars) == 2
    assert bar_data.bars[0].close == 10.5
