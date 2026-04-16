"""
Data feed for backtesting.
"""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from datetime import datetime

import pandas as pd


class DataFeed(ABC):
    """Abstract base class for data feeds."""

    @abstractmethod
    def __iter__(self) -> Iterator[dict]:
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

    def __iter__(self) -> Iterator[dict]:
        """Iterate over data bars."""
        for self._current_index in range(len(self.df)):
            row = self.df.iloc[self._current_index]
            self._current_datetime = row[self.datetime_col]
            yield row.to_dict()

    def reset(self) -> None:
        """Reset the data feed to the beginning."""
        self._current_index = 0
        self._current_datetime = None

    @property
    def current_datetime(self) -> datetime | None:
        """Get the current datetime of the data feed."""
        return self._current_datetime
