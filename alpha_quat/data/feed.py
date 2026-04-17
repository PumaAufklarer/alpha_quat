"""Data feed implementations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from datetime import datetime
from typing import Any

import pandas as pd


class DataFeed(ABC):
    """Abstract base class for data feeds."""

    @abstractmethod
    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate over data bars."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the data feed to the beginning."""
        pass

    @property
    @abstractmethod
    def current_datetime(self) -> datetime | None:
        """Get the current datetime of the data feed."""
        pass


class PandasDataFeed(DataFeed):
    """Data feed using pandas DataFrame."""

    def __init__(self, df: pd.DataFrame, datetime_col: str = "trade_date"):
        """
        Initialize pandas data feed.

        Args:
            df: DataFrame containing the data
            datetime_col: Column name for datetime
        """
        self.df = df.copy()
        self.datetime_col = datetime_col
        self._current_index = 0
        self._current_datetime: datetime | None = None

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """Iterate over data bars."""
        for self._current_index in range(len(self.df)):
            row = self.df.iloc[self._current_index]
            dt_val = row[self.datetime_col]
            if hasattr(dt_val, "to_pydatetime"):
                self._current_datetime = dt_val.to_pydatetime()
            else:
                self._current_datetime = pd.to_datetime(dt_val).to_pydatetime()
            yield row.to_dict()

    def reset(self) -> None:
        """Reset the data feed to the beginning."""
        self._current_index = 0
        self._current_datetime = None

    @property
    def current_datetime(self) -> datetime | None:
        """Get the current datetime of the data feed."""
        return self._current_datetime


class MultiAssetDataFeed(DataFeed):
    """
    Data feed for multiple assets.

    Groups data by datetime, yields all assets for each datetime.
    Each iteration returns a dict with:
    - datetime: current datetime
    - assets: dict of {ts_code: asset_data_dict}
    """

    def __init__(
        self,
        df: pd.DataFrame,
        datetime_col: str = "trade_date",
        ts_code_col: str = "ts_code",
    ):
        """
        Initialize multi-asset data feed.

        Args:
            df: DataFrame containing the data (must have datetime and ts_code columns)
            datetime_col: Column name for datetime
            ts_code_col: Column name for asset code
        """
        self.df = df.copy()
        self.datetime_col = datetime_col
        self.ts_code_col = ts_code_col
        self.df = self.df.sort_values(datetime_col).reset_index(drop=True)
        self._grouped = list(self.df.groupby(datetime_col))
        self._group_index = 0
        self._current_datetime: datetime | None = None

    def __iter__(self) -> Iterator[dict[str, Any]]:
        """
        Iterate over data, grouped by datetime.

        Yields:
            Dict with 'datetime' and 'assets' (dict of {ts_code: asset_data})
        """
        for self._group_index in range(len(self._grouped)):
            dt, group = self._grouped[self._group_index]
            if hasattr(dt, "to_pydatetime"):
                self._current_datetime = dt.to_pydatetime()
            else:
                self._current_datetime = pd.to_datetime(dt).to_pydatetime()
            assets = {}
            for _, row in group.iterrows():
                ts_code = row[self.ts_code_col]
                assets[ts_code] = row.to_dict()
            yield {"datetime": self._current_datetime, "assets": assets}

    def reset(self) -> None:
        """Reset the data feed to the beginning."""
        self._group_index = 0
        self._current_datetime = None

    @property
    def current_datetime(self) -> datetime | None:
        """Get the current datetime of the data feed."""
        return self._current_datetime
