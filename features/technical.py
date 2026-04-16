"""
Technical indicator feature implementations.
"""

import pandas as pd

from .base import FeatureBase


class SMA(FeatureBase):
    """Simple Moving Average."""

    def __init__(self, price_col: str = "close", period: int = 20):
        """
        Initialize SMA feature.

        Args:
            price_col: Column name for price data
            period: Moving average period
        """
        self.price_col = price_col
        self.period = period

    @property
    def name(self) -> str:
        """Get the name of this feature."""
        return f"sma_{self.period}"

    @property
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        return [self.price_col]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate SMA and add to DataFrame.

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        result_df = df.copy()
        result_df[self.name] = result_df[self.price_col].rolling(window=self.period).mean()
        return result_df


class EMA(FeatureBase):
    """Exponential Moving Average."""

    def __init__(self, price_col: str = "close", period: int = 20):
        """
        Initialize EMA feature.

        Args:
            price_col: Column name for price data
            period: Moving average period
        """
        self.price_col = price_col
        self.period = period

    @property
    def name(self) -> str:
        """Get the name of this feature."""
        return f"ema_{self.period}"

    @property
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        return [self.price_col]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate EMA and add to DataFrame.

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        result_df = df.copy()
        result_df[self.name] = result_df[self.price_col].ewm(span=self.period, adjust=False).mean()
        return result_df


class RSI(FeatureBase):
    """Relative Strength Index."""

    def __init__(self, price_col: str = "close", period: int = 14):
        """
        Initialize RSI feature.

        Args:
            price_col: Column name for price data
            period: RSI period
        """
        self.price_col = price_col
        self.period = period

    @property
    def name(self) -> str:
        """Get the name of this feature."""
        return f"rsi_{self.period}"

    @property
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        return [self.price_col]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI and add to DataFrame.

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        result_df = df.copy()

        # Calculate price changes
        delta = result_df[self.price_col].diff()

        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()

        # Calculate RS and RSI
        rs = gain / loss
        result_df[self.name] = 100 - (100 / (1 + rs))

        return result_df


class MACD(FeatureBase):
    """Moving Average Convergence Divergence."""

    def __init__(
        self,
        price_col: str = "close",
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
    ):
        """
        Initialize MACD feature.

        Args:
            price_col: Column name for price data
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line EMA period
        """
        self.price_col = price_col
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period

    @property
    def name(self) -> str:
        """Get the name of this feature."""
        return "macd"

    @property
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        return [self.price_col]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD and add to DataFrame.

        Adds three columns:
        - macd: MACD line (fast EMA - slow EMA)
        - macd_signal: Signal line (EMA of MACD)
        - macd_histogram: MACD histogram (MACD - signal)

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        result_df = df.copy()

        # Calculate EMAs
        ema_fast = result_df[self.price_col].ewm(span=self.fast_period, adjust=False).mean()
        ema_slow = result_df[self.price_col].ewm(span=self.slow_period, adjust=False).mean()

        # Calculate MACD line
        macd_line = ema_fast - ema_slow

        # Calculate signal line
        signal_line = macd_line.ewm(span=self.signal_period, adjust=False).mean()

        # Calculate histogram
        histogram = macd_line - signal_line

        # Add to DataFrame
        result_df[self.name] = macd_line
        result_df[f"{self.name}_signal"] = signal_line
        result_df[f"{self.name}_histogram"] = histogram

        return result_df


class BollingerBands(FeatureBase):
    """Bollinger Bands."""

    def __init__(self, price_col: str = "close", period: int = 20, std_dev: float = 2.0):
        """
        Initialize Bollinger Bands feature.

        Args:
            price_col: Column name for price data
            period: Moving average period
            std_dev: Number of standard deviations for bands
        """
        self.price_col = price_col
        self.period = period
        self.std_dev = std_dev

    @property
    def name(self) -> str:
        """Get the name of this feature."""
        return "bb"

    @property
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        return [self.price_col]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Bollinger Bands and add to DataFrame.

        Adds three columns:
        - bb_middle: Middle band (SMA)
        - bb_upper: Upper band (SMA + std_dev * std)
        - bb_lower: Lower band (SMA - std_dev * std)

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        result_df = df.copy()

        # Calculate middle band (SMA)
        middle = result_df[self.price_col].rolling(window=self.period).mean()

        # Calculate standard deviation
        std = result_df[self.price_col].rolling(window=self.period).std()

        # Calculate bands
        upper = middle + (std * self.std_dev)
        lower = middle - (std * self.std_dev)

        # Add to DataFrame
        result_df[f"{self.name}_middle"] = middle
        result_df[f"{self.name}_upper"] = upper
        result_df[f"{self.name}_lower"] = lower

        return result_df


class ATR(FeatureBase):
    """Average True Range."""

    def __init__(
        self,
        high_col: str = "high",
        low_col: str = "low",
        close_col: str = "close",
        period: int = 14,
    ):
        """
        Initialize ATR feature.

        Args:
            high_col: Column name for high prices
            low_col: Column name for low prices
            close_col: Column name for close prices
            period: ATR period
        """
        self.high_col = high_col
        self.low_col = low_col
        self.close_col = close_col
        self.period = period

    @property
    def name(self) -> str:
        """Get the name of this feature."""
        return f"atr_{self.period}"

    @property
    def inputs(self) -> list[str]:
        """Get the list of input column names required."""
        return [self.high_col, self.low_col, self.close_col]

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate ATR and add to DataFrame.

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with feature columns added
        """
        result_df = df.copy()

        # Calculate true range components
        high_low = result_df[self.high_col] - result_df[self.low_col]
        high_close_prev = abs(result_df[self.high_col] - result_df[self.close_col].shift(1))
        low_close_prev = abs(result_df[self.low_col] - result_df[self.close_col].shift(1))

        # Calculate true range
        tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)

        # Calculate ATR (using EMA)
        result_df[self.name] = tr.ewm(span=self.period, adjust=False).mean()

        return result_df
