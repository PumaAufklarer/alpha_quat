"""Bar data structures."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from alpha_quat.core import Price, Quantity


@dataclass
class Bar:
    """OHLCV Bar data."""

    ts_code: str
    timestamp: datetime
    open: Price
    high: Price
    low: Price
    close: Price
    volume: Quantity

    @property
    def typical_price(self) -> Price:
        """Calculate typical price: (high + low + close) / 3."""
        return Price((self.high + self.low + self.close) / 3)

    @property
    def median_price(self) -> Price:
        """Calculate median price: (high + low) / 2."""
        return Price((self.high + self.low) / 2)


@dataclass
class BarData:
    """Collection of Bar data."""

    bars: list[Bar]

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        ts_code_col: str = "ts_code",
        datetime_col: str = "trade_date",
        open_col: str = "open",
        high_col: str = "high",
        low_col: str = "low",
        close_col: str = "close",
        volume_col: str = "vol",
    ) -> BarData:
        """Create BarData from a pandas DataFrame."""
        bars = []
        for _, row in df.iterrows():
            ts_code = str(row[ts_code_col])
            dt_val = row[datetime_col]
            if hasattr(dt_val, "to_pydatetime"):
                timestamp = dt_val.to_pydatetime()
            else:
                timestamp = pd.to_datetime(dt_val).to_pydatetime()
            bar = Bar(
                ts_code=ts_code,
                timestamp=timestamp,
                open=Price(float(row[open_col])),
                high=Price(float(row[high_col])),
                low=Price(float(row[low_col])),
                close=Price(float(row[close_col])),
                volume=Quantity(int(row[volume_col]) if pd.notna(row[volume_col]) else 0),
            )
            bars.append(bar)
        return cls(bars=bars)

    def get_bars_for_asset(self, ts_code: str) -> list[Bar]:
        """Get all bars for a specific asset."""
        return [bar for bar in self.bars if bar.ts_code == ts_code]

    def get_unique_timestamps(self) -> list[datetime]:
        """Get all unique timestamps sorted."""
        timestamps = sorted({bar.timestamp for bar in self.bars})
        return timestamps

    def get_bars_at_timestamp(self, timestamp: datetime) -> dict[str, Bar]:
        """Get all bars at a specific timestamp, keyed by ts_code."""
        result = {}
        for bar in self.bars:
            if bar.timestamp == timestamp:
                result[bar.ts_code] = bar
        return result
