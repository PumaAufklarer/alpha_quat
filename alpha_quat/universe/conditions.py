"""Concrete condition implementations."""

from __future__ import annotations

import pandas as pd

from .base import Condition


class ValueCondition(Condition):
    """Generic value comparison condition."""

    def __init__(self, field: str, operator: str, value: float | int | str):
        """
        Args:
            field: Field name to compare
            operator: Comparison operator (">", ">=", "<", "<=", "==", "!=")
            value: Value to compare against
        """
        self.field = field
        self.operator = operator
        self.value = value

    @property
    def name(self) -> str:
        return f"{self.field}_{self.operator}_{self.value}"

    def apply(self, data: pd.DataFrame) -> pd.Series:
        if self.operator == ">":
            return data[self.field] > self.value
        elif self.operator == ">=":
            return data[self.field] >= self.value
        elif self.operator == "<":
            return data[self.field] < self.value
        elif self.operator == "<=":
            return data[self.field] <= self.value
        elif self.operator == "==":
            return data[self.field] == self.value
        elif self.operator == "!=":
            return data[self.field] != self.value
        else:
            raise ValueError(f"Unknown operator: {self.operator}")


class RangeCondition(Condition):
    """Value range condition (inclusive)."""

    def __init__(self, field: str, min_val: float | int, max_val: float | int):
        self.field = field
        self.min_val = min_val
        self.max_val = max_val

    @property
    def name(self) -> str:
        return f"{self.field}_range_{self.min_val}_{self.max_val}"

    def apply(self, data: pd.DataFrame) -> pd.Series:
        return (data[self.field] >= self.min_val) & (data[self.field] <= self.max_val)


class MarketCapCondition(Condition):
    """Market capitalization filter (based on total_mv field)."""

    def __init__(self, min_mv: float | None = None, max_mv: float | None = None):
        """
        Args:
            min_mv: Minimum market cap (in 100 million yuan, optional)
            max_mv: Maximum market cap (in 100 million yuan, optional)
        """
        self.min_mv = min_mv
        self.max_mv = max_mv

    @property
    def name(self) -> str:
        parts = ["market_cap"]
        if self.min_mv is not None:
            parts.append(f">={self.min_mv}")
        if self.max_mv is not None:
            parts.append(f"<={self.max_mv}")
        return "_".join(parts)

    def apply(self, data: pd.DataFrame) -> pd.Series:
        mask = pd.Series([True] * len(data), index=data.index)
        if self.min_mv is not None:
            mask = mask & (data["total_mv"] >= self.min_mv)
        if self.max_mv is not None:
            mask = mask & (data["total_mv"] <= self.max_mv)
        return mask


class ListingDateCondition(Condition):
    """Listing date filter (minimum days since listing)."""

    def __init__(self, min_days: int, reference_date: str | None = None):
        """
        Args:
            min_days: Minimum days since listing
            reference_date: Reference date (YYYYMMDD), defaults to latest date in data
        """
        self.min_days = min_days
        self.reference_date = reference_date

    @property
    def name(self) -> str:
        return f"listing_days>={self.min_days}"

    def apply(self, data: pd.DataFrame) -> pd.Series:
        # Convert list_date to datetime
        if "list_date" not in data.columns:
            return pd.Series([True] * len(data), index=data.index)

        list_dates = pd.to_datetime(data["list_date"], format="%Y%m%d")

        # Determine reference date
        if self.reference_date is not None:
            ref_date = pd.to_datetime(self.reference_date, format="%Y%m%d")
        elif "trade_date" in data.columns:
            ref_date = pd.to_datetime(data["trade_date"], format="%Y%m%d").max()
        else:
            ref_date = pd.Timestamp.now()

        # Calculate days since listing
        days_since_listing = (ref_date - list_dates).dt.days

        return days_since_listing >= self.min_days


class IsSTCondition(Condition):
    """ST stock filter."""

    def __init__(self, exclude: bool = True):
        """
        Args:
            exclude: If True, exclude ST stocks; if False, include only ST stocks
        """
        self.exclude = exclude

    @property
    def name(self) -> str:
        return "exclude_ST" if self.exclude else "only_ST"

    def apply(self, data: pd.DataFrame) -> pd.Series:
        if "name" not in data.columns:
            return pd.Series([True] * len(data), index=data.index)

        # Check if name starts with ST or *ST
        is_st = data["name"].str.startswith(("ST", "*ST"), na=False)

        if self.exclude:
            return ~is_st
        else:
            return is_st
