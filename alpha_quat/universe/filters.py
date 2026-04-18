"""Filter for composing multiple conditions."""

from __future__ import annotations

import pandas as pd

from .base import Condition


class Filter:
    """Composes multiple conditions with AND logic."""

    def __init__(self, conditions: list[Condition]):
        """
        Args:
            conditions: List of conditions to apply (all must be satisfied)
        """
        self.conditions = conditions

    def apply(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all conditions with AND logic.

        Args:
            data: Input DataFrame

        Returns:
            Filtered DataFrame containing only rows that satisfy all conditions
        """
        mask = self.get_mask(data)
        return data[mask].copy()

    def get_mask(self, data: pd.DataFrame) -> pd.Series:
        """Get boolean mask without filtering data."""
        if not self.conditions:
            return pd.Series([True] * len(data), index=data.index)

        # Start with all True
        mask = pd.Series([True] * len(data), index=data.index)

        # AND all conditions
        for condition in self.conditions:
            cond_mask = condition.apply(data)
            mask = mask & cond_mask

        return mask

    @property
    def name(self) -> str:
        """Get combined name of all conditions."""
        return " & ".join(cond.name for cond in self.conditions)
