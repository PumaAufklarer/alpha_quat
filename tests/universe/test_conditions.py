"""Tests for condition implementations."""

import pandas as pd

from alpha_quat.universe.conditions import (
    IsSTCondition,
    ListingDateCondition,
    MarketCapCondition,
    RangeCondition,
    ValueCondition,
)


def test_value_condition():
    """Test ValueCondition with various operators."""
    data = pd.DataFrame({"value": [5, 10, 15, 20]})

    cond1 = ValueCondition("value", ">", 10)
    assert list(cond1.apply(data)) == [False, False, True, True]

    cond2 = ValueCondition("value", ">=", 10)
    assert list(cond2.apply(data)) == [False, True, True, True]

    cond3 = ValueCondition("value", "<", 15)
    assert list(cond3.apply(data)) == [True, True, False, False]

    cond4 = ValueCondition("value", "<=", 15)
    assert list(cond4.apply(data)) == [True, True, True, False]

    cond5 = ValueCondition("value", "==", 10)
    assert list(cond5.apply(data)) == [False, True, False, False]

    cond6 = ValueCondition("value", "!=", 10)
    assert list(cond6.apply(data)) == [True, False, True, True]


def test_range_condition():
    """Test RangeCondition."""
    data = pd.DataFrame({"value": [5, 10, 15, 20, 25]})

    cond = RangeCondition("value", 10, 20)
    assert list(cond.apply(data)) == [False, True, True, True, False]


def test_market_cap_condition():
    """Test MarketCapCondition."""
    data = pd.DataFrame(
        {
            "ts_code": ["001", "002", "003", "004"],
            "total_mv": [50, 100, 200, 500],
        }
    )

    # Min only
    cond1 = MarketCapCondition(min_mv=100)
    assert list(cond1.apply(data)) == [False, True, True, True]

    # Max only
    cond2 = MarketCapCondition(max_mv=200)
    assert list(cond2.apply(data)) == [True, True, True, False]

    # Both min and max
    cond3 = MarketCapCondition(min_mv=100, max_mv=200)
    assert list(cond3.apply(data)) == [False, True, True, False]


def test_listing_date_condition():
    """Test ListingDateCondition."""
    data = pd.DataFrame(
        {
            "ts_code": ["001", "002", "003"],
            "list_date": ["20200101", "20220101", "20230601"],
            "trade_date": ["20240101", "20240101", "20240101"],
        }
    )

    # With reference date
    cond = ListingDateCondition(min_days=365, reference_date="20240101")
    # 001: 4 years, 002: 2 years, 003: 7 months (<365 days)
    assert list(cond.apply(data)) == [True, True, False]


def test_is_st_condition():
    """Test IsSTCondition."""
    data = pd.DataFrame(
        {
            "ts_code": ["001", "002", "003", "004"],
            "name": ["平安银行", "ST平安", "万科A", "*ST万科"],
        }
    )

    # Exclude ST
    cond1 = IsSTCondition(exclude=True)
    assert list(cond1.apply(data)) == [True, False, True, False]

    # Include only ST
    cond2 = IsSTCondition(exclude=False)
    assert list(cond2.apply(data)) == [False, True, False, True]
