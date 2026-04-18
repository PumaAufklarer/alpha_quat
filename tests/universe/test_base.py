"""Tests for universe base classes."""

import pandas as pd

from alpha_quat.universe.base import Condition, Universe


class SimpleCondition(Condition):
    """Test condition implementation."""

    def __init__(self, threshold: float = 10.0):
        self.threshold = threshold

    @property
    def name(self) -> str:
        return f"simple_{self.threshold}"

    def apply(self, data: pd.DataFrame) -> pd.Series:
        return data["close"] > self.threshold


def test_condition_base():
    """Test Condition base class interface."""
    cond = SimpleCondition(threshold=10.0)
    assert cond.name == "simple_10.0"

    data = pd.DataFrame({"close": [5, 10, 15, 20]})
    mask = cond.apply(data)
    assert list(mask) == [False, False, True, True]


def test_universe_initialization():
    """Test Universe initialization."""
    stock_list = pd.DataFrame(
        {
            "ts_code": ["000001.SZ", "000002.SZ"],
            "name": ["平安银行", "万科A"],
            "list_date": ["19910403", "19910129"],
        }
    )
    daily_basic = pd.DataFrame(
        {
            "ts_code": ["000001.SZ", "000001.SZ", "000002.SZ", "000002.SZ"],
            "trade_date": ["20240101", "20240102", "20240101", "20240102"],
            "close": [10.0, 10.5, 20.0, 20.5],
            "total_mv": [1000.0, 1050.0, 2000.0, 2050.0],
        }
    )

    universe = Universe(stock_list=stock_list, daily_basic=daily_basic)
    assert len(universe.get_stocks()) == 2
    assert set(universe.get_stocks()) == {"000001.SZ", "000002.SZ"}
