"""Time-based dataset splitter."""

from __future__ import annotations

import pandas as pd


class TimeSplitter:
    """Splits data into train/validation/test sets by time."""

    def __init__(self, date_column: str = "trade_date"):
        """
        Args:
            date_column: Name of the date column
        """
        self.date_column = date_column

    def split(
        self,
        data: pd.DataFrame,
        train_end: str,
        val_end: str,
    ) -> dict[str, pd.DataFrame]:
        """
        Split data by time.

        Args:
            data: Input DataFrame
            train_end: End date for training set (YYYYMMDD, exclusive)
            val_end: End date for validation set (YYYYMMDD, exclusive)

        Returns:
            Dictionary with keys "train", "val", "test"
        """
        # Ensure date column is string for comparison
        dates = data[self.date_column].astype(str)

        # Train: < train_end
        train_mask = dates < train_end

        # Val: >= train_end and < val_end
        val_mask = (dates >= train_end) & (dates < val_end)

        # Test: >= val_end
        test_mask = dates >= val_end

        return {
            "train": data[train_mask].copy(),
            "val": data[val_mask].copy(),
            "test": data[test_mask].copy(),
        }
