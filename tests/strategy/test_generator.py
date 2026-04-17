"""Tests for signal generators."""

from datetime import datetime

from alpha_quat.data.bars import Bar, BarData
from alpha_quat.strategy.generator import SignalGenerator
from alpha_quat.strategy.signals import Signal, SignalDirection


class TestSignalGenerator(SignalGenerator):
    """Test signal generator implementation."""

    def generate(self, data: dict) -> list[Signal]:
        """Generate test signals."""
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


def test_signal_generator_interface():
    """Test signal generator interface."""
    generator = TestSignalGenerator()
    data = {
        "assets": {
            "000001.SZ": {"close": 10.0},
            "000002.SZ": {"close": 20.0},
        }
    }
    signals = generator.generate(data)
    assert len(signals) == 2
    assert signals[0].ts_code == "000001.SZ"
    assert signals[1].ts_code == "000002.SZ"


def test_signal_generator_with_bar_data():
    """Test signal generator with BarData."""

    class BarBasedGenerator(SignalGenerator):
        def generate(self, data: dict) -> list[Signal]:
            signals = []
            if "bar_data" in data:
                bar_data = data["bar_data"]
                for bar in bar_data.bars:
                    if bar.close > bar.open:
                        signals.append(
                            Signal(
                                ts_code=bar.ts_code,
                                direction=SignalDirection.LONG,
                            )
                        )
            return signals

    dt = datetime(2024, 1, 1)
    bars = [
        Bar(
            ts_code="000001.SZ",
            timestamp=dt,
            open=10.0,
            high=11.0,
            low=9.5,
            close=10.5,
            volume=1000000,
        )
    ]
    bar_data = BarData(bars=bars)

    generator = BarBasedGenerator()
    signals = generator.generate({"bar_data": bar_data})
    assert len(signals) == 1
    assert signals[0].ts_code == "000001.SZ"
