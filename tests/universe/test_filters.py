"""Tests for Filter class."""

import pandas as pd

from alpha_quat.universe.conditions import ValueCondition
from alpha_quat.universe.filters import Filter


def test_filter_apply_and():
    """Test Filter applying multiple conditions with AND logic."""
    data = pd.DataFrame(
        {
            "ts_code": ["001", "002", "003", "004"],
            "value1": [5, 10, 15, 20],
            "value2": [100, 200, 300, 400],
        }
    )

    filter = Filter(
        [
            ValueCondition("value1", ">", 8),
            ValueCondition("value2", "<", 350),
        ]
    )

    result = filter.apply(data)
    assert len(result) == 2
    assert list(result["ts_code"]) == ["002", "003"]


def test_filter_get_mask():
    """Test Filter get_mask method."""
    data = pd.DataFrame(
        {
            "ts_code": ["001", "002", "003"],
            "value": [5, 10, 15],
        }
    )

    filter = Filter([ValueCondition("value", ">=", 10)])
    mask = filter.get_mask(data)
    assert list(mask) == [False, True, True]
