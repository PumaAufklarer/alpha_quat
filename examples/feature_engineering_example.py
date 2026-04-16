"""
Example script demonstrating the feature engineering module.
"""

import numpy as np
import pandas as pd

from features import (
    ATR,
    EMA,
    MACD,
    RSI,
    SMA,
    BollingerBands,
    FeaturePipeline,
    LogReturns,
    Returns,
    Volatility,
)


def generate_sample_data(days: int = 100) -> pd.DataFrame:
    """Generate sample OHLC data for testing."""
    np.random.seed(42)

    # Generate price data with some trend and volatility
    dates = pd.date_range(start="2024-01-01", periods=days, freq="D")
    base_price = 100.0

    # Generate random walk with drift
    returns = np.random.normal(0.001, 0.02, days)
    prices = base_price * (1 + returns).cumprod()

    # Generate OHLC
    high = prices * (1 + np.random.uniform(0, 0.01, days))
    low = prices * (1 - np.random.uniform(0, 0.01, days))
    open_ = np.roll(prices, 1)
    open_[0] = prices[0] * 0.995
    close = prices

    df = pd.DataFrame({"open": open_, "high": high, "low": low, "close": close}, index=dates)
    return df


def main():
    """Run feature engineering example."""
    print("=== Feature Engineering Module Example ===\n")

    # Generate sample data
    print("1. Generating sample OHLC data...")
    df = generate_sample_data(days=200)
    print(f"   Data shape: {df.shape}")
    print(f"   Date range: {df.index[0]} to {df.index[-1]}")
    print()

    # Create feature pipeline
    print("2. Creating feature pipeline...")
    pipeline = FeaturePipeline(
        [
            Returns(periods=1),
            Returns(periods=5),
            LogReturns(periods=1),
            Volatility(window=20),
            SMA(period=10),
            SMA(period=20),
            SMA(period=60),
            EMA(period=12),
            EMA(period=26),
            RSI(period=14),
            MACD(),
            BollingerBands(period=20, std_dev=2.0),
            ATR(period=14),
        ]
    )
    print(f"   Pipeline: {pipeline}")
    print(f"   Required inputs: {pipeline.required_inputs}")
    print()

    # Calculate features
    print("3. Calculating features...")
    df_with_features = pipeline.calculate(df)
    print(f"   Result shape: {df_with_features.shape}")
    print()

    # Show feature columns
    print("4. Feature columns added:")
    feature_cols = [col for col in df_with_features.columns if col not in df.columns]
    for col in feature_cols:
        print(f"   - {col}")
    print()

    # Show sample of the data
    print("5. Sample data (last 5 rows):")
    print(df_with_features.tail())
    print()

    print("=== Example complete ===")


if __name__ == "__main__":
    main()
