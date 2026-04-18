"""Base classes for stock universe selection."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from .filters import Filter


class Condition(ABC):
    """Base class for filter conditions."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of this condition."""
        pass

    @abstractmethod
    def apply(self, data: pd.DataFrame) -> pd.Series:
        """
        Apply condition to data.

        Args:
            data: Input DataFrame (should contain required fields)

        Returns:
            Boolean Series where True indicates the condition is satisfied
        """
        pass


@dataclass
class Universe:
    """Stock universe container."""

    stock_list: pd.DataFrame  # From get_stock_list()
    daily_basic: pd.DataFrame  # From get_daily_basic()

    def filter(self, filter_obj: Filter) -> Universe:
        """
        Apply filter and return new Universe.

        Args:
            filter_obj: Filter to apply

        Returns:
            New Universe containing only filtered stocks
        """

        # Get combined data
        combined_data = self.get_stock_data()

        # Apply filter to get mask
        mask = filter_obj.get_mask(combined_data)

        # Get filtered stock codes
        filtered_stocks = combined_data[mask]["ts_code"].unique()

        # Create new universe
        filtered_stock_list = self.stock_list[
            self.stock_list["ts_code"].isin(filtered_stocks)
        ].copy()
        filtered_daily_basic = self.daily_basic[
            self.daily_basic["ts_code"].isin(filtered_stocks)
        ].copy()

        return Universe(
            stock_list=filtered_stock_list,
            daily_basic=filtered_daily_basic,
        )

    def get_stocks(self) -> list[str]:
        """Get list of stock codes in this universe."""
        return list(self.stock_list["ts_code"].unique())

    def get_stock_data(self) -> pd.DataFrame:
        """Get combined stock data (stock_list + daily_basic)."""
        # Merge on ts_code
        if "ts_code" in self.stock_list.columns and "ts_code" in self.daily_basic.columns:
            # Get latest daily_basic record per stock for filtering
            latest_daily = (
                self.daily_basic.sort_values("trade_date", ascending=False)
                .groupby("ts_code")
                .first()
                .reset_index()
            )
            return pd.merge(
                self.stock_list,
                latest_daily,
                on="ts_code",
                how="inner",
            )
        return self.daily_basic.copy()
