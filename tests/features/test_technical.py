"""Tests for technical indicators."""

import pandas as pd

from alpha_quat.features.technical import ATR, DonchianChannels


def test_donchian_channels():
    """Test Donchian Channels calculation."""
    data = pd.DataFrame(
        {
            "high": [10, 12, 11, 14, 13, 15],
            "low": [8, 9, 7, 10, 9, 11],
            "close": [9, 11, 10, 12, 11, 13],
        }
    )

    donchian = DonchianChannels(period=3)
    assert donchian.name == "donchian_3"

    result = donchian.calculate(data)
    assert "donchian_3_upper" in result.columns
    assert "donchian_3_lower" in result.columns

    # 第3个位置(index=2)开始有值
    assert pd.isna(result["donchian_3_upper"].iloc[0])
    assert pd.isna(result["donchian_3_upper"].iloc[1])
    # index=2: high[0-2] = 10,12,11 -> max=12
    assert result["donchian_3_upper"].iloc[2] == 12
    # index=3: high[1-3] = 12,11,14 -> max=14
    assert result["donchian_3_upper"].iloc[3] == 14


def test_atr():
    """Test ATR calculation."""
    data = pd.DataFrame(
        {
            "high": [10, 12, 11, 14, 13, 15],
            "low": [8, 9, 7, 10, 9, 11],
            "close": [9, 11, 10, 12, 11, 13],
        }
    )

    atr = ATR(period=3)
    assert atr.name == "atr_3"

    result = atr.calculate(data)
    assert "atr_3" in result.columns

    # 检查 TR 计算逻辑（ATR 是 TR 的移动平均）
    # 滚动窗口 period=3，index 0-2 用于计算第一个值（index 2）
    assert pd.isna(result["atr_3"].iloc[0])
    assert pd.isna(result["atr_3"].iloc[1])
    assert not pd.isna(result["atr_3"].iloc[2])
    assert not pd.isna(result["atr_3"].iloc[3])
