"""Tests for backtest engine."""

import pandas as pd

from alpha_quat.backtest.engine import BacktestEngine
from alpha_quat.data.feed import MultiAssetDataFeed
from alpha_quat.strategy.generator import SignalGenerator
from alpha_quat.strategy.signals import Signal, SignalDirection


class SimpleStrategy(SignalGenerator):
    """Simple test strategy that goes long on every asset."""

    def generate(self, data: dict) -> list[Signal]:
        """Generate long signals for all assets."""
        signals = []
        if "assets" in data:
            for ts_code in data["assets"]:
                signals.append(
                    Signal(
                        ts_code=ts_code,
                        direction=SignalDirection.LONG,
                        strength=1.0,
                    )
                )
        return signals


def test_backtest_engine_creation():
    """Test creating a backtest engine."""
    # Create sample data
    data = {
        "trade_date": [
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-02"),
        ],
        "ts_code": ["000001.SZ", "000001.SZ"],
        "open": [10.0, 10.5],
        "high": [11.0, 11.5],
        "low": [9.5, 10.0],
        "close": [10.5, 11.0],
        "vol": [1000000, 1200000],
    }
    df = pd.DataFrame(data)
    feed = MultiAssetDataFeed(df, datetime_col="trade_date", ts_code_col="ts_code")

    strategy = SimpleStrategy()

    engine = BacktestEngine(
        data_feed=feed,
        strategy=strategy,
        initial_capital=100000.0,
    )

    assert engine.initial_capital == 100000.0
    assert engine.strategy is strategy


def test_backtest_engine_run():
    """Test running a simple backtest."""
    # Create sample data
    data = {
        "trade_date": [
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-01"),
            pd.Timestamp("2024-01-02"),
            pd.Timestamp("2024-01-02"),
        ],
        "ts_code": ["000001.SZ", "000002.SZ", "000001.SZ", "000002.SZ"],
        "open": [10.0, 20.0, 10.5, 20.5],
        "high": [11.0, 21.0, 11.5, 21.5],
        "low": [9.5, 19.5, 10.0, 20.0],
        "close": [10.5, 20.5, 11.0, 21.0],
        "vol": [1000000, 500000, 1200000, 600000],
    }
    df = pd.DataFrame(data)
    feed = MultiAssetDataFeed(df, datetime_col="trade_date", ts_code_col="ts_code")

    strategy = SimpleStrategy()

    engine = BacktestEngine(
        data_feed=feed,
        strategy=strategy,
        initial_capital=100000.0,
    )

    result = engine.run()

    assert result is not None
    assert result.initial_capital == 100000.0
    assert len(result.equity_curve) > 0
