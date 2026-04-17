"""
Basic feature implementations.
"""

import pandas as pd

from .base import FeatureBase


class Returns(FeatureBase):
    """Calculate simple returns."""

    def __init__(self, price_col: str = "close", periods: int = 1):
        """
        Initialize Returns feature.

        Args:
            price_col: Column name for price data
            periods: Number of periods to calculate returns over
        """
        self.price_col = price_col
        self.periods = periods

    @property
    def name(self) -> str:
        """Get the name of this feature."""
        return f"returns_{self.periods}"

    @property
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        return [self.price_col]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate returns and add to DataFrame.

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        result_df = df.copy()
        result_df[self.name] = result_df[self.price_col].pct_change(periods=self.periods)
        return result_df


class LogReturns(FeatureBase):
    """Calculate log returns."""

    def __init__(self, price_col: str = "close", periods: int = 1):
        """
        Initialize LogReturns feature.

        Args:
            price_col: Column name for price data
            periods: Number of periods to calculate returns over
        """
        self.price_col = price_col
        self.periods = periods

    @property
    def name(self) -> str:
        """Get the name of this feature."""
        return f"log_returns_{self.periods}"

    @property
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        return [self.price_col]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate log returns and add to DataFrame.

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        import numpy as np

        result_df = df.copy()
        result_df[self.name] = np.log(
            result_df[self.price_col] / result_df[self.price_col].shift(self.periods)
        )
        return result_df


class Volatility(FeatureBase):
    """Calculate rolling volatility (standard deviation of returns)."""

    def __init__(
        self,
        price_col: str = "close",
        window: int = 20,
        periods: int = 1,
        annualize: bool = True,
        annual_factor: int = 252,
    ):
        """
        Initialize Volatility feature.

        Args:
            price_col: Column name for price data
            window: Rolling window size
            periods: Number of periods for returns calculation
            annualize: Whether to annualize volatility
            annual_factor: Number of trading days in a year for annualization
        """
        self.price_col = price_col
        self.window = window
        self.periods = periods
        self.annualize = annualize
        self.annual_factor = annual_factor

    @property
    def name(self) -> str:
        """Get the name of this feature."""
        return f"volatility_{self.window}"

    @property
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        return [self.price_col]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate volatility and add to DataFrame.

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        result_df = df.copy()

        # First calculate returns
        returns = result_df[self.price_col].pct_change(periods=self.periods)

        # Calculate rolling standard deviation
        vol = returns.rolling(window=self.window).std()

        # Annualize if requested
        if self.annualize:
            vol = vol * (self.annual_factor**0.5)

        result_df[self.name] = vol
        return result_df
