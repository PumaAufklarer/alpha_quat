"""
Base class for features.
"""

from abc import ABC, abstractmethod

import pandas as pd


class FeatureBase(ABC):
    """Abstract base class for features."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of this feature."""
        pass

    @property
    @abstractmethod
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        pass

    @abstractmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate features and add to DataFrame.

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        pass
