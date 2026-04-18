"""Technical indicators for feature engineering."""

from __future__ import annotations

import numpy as np
import pandas as pd

from alpha_quat.features.base import Feature


class DonchianChannels(Feature):
    """
    Donchian Channels（唐奇安通道）

    计算给定周期内的最高价和最低价通道。

    产生两列特征：
    - {name}_upper: 周期内最高价
    - {name}_lower: 周期内最低价
    """

    def __init__(self, period: int):
        """
        初始化唐奇安通道

        Args:
            period: 计算周期
        """
        self.period = period

    @property
    def name(self) -> str:
        return f"donchian_{self.period}"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算唐奇安通道

        Args:
            data: 输入数据 DataFrame，需要包含 'high' 和 'low' 列

        Returns:
            包含唐奇安通道上下轨的 DataFrame
        """
        result = data.copy()
        result[f"{self.name}_upper"] = data["high"].rolling(window=self.period).max()
        result[f"{self.name}_lower"] = data["low"].rolling(window=self.period).min()
        return result


class ATR(Feature):
    """
    ATR（Average True Range，平均真实波幅）

    计算市场波动率指标。
    """

    def __init__(self, period: int = 14):
        """
        初始化 ATR

        Args:
            period: 计算周期，默认 14
        """
        self.period = period

    @property
    def name(self) -> str:
        return f"atr_{self.period}"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算 ATR

        Args:
            data: 输入数据 DataFrame，需要包含 'high'、'low'、'close' 列

        Returns:
            包含 ATR 的 DataFrame
        """
        result = data.copy()

        # 计算真实波幅 (TR)
        high_low = data["high"] - data["low"]
        high_close = np.abs(data["high"] - data["close"].shift())
        low_close = np.abs(data["low"] - data["close"].shift())

        # 合并三个序列取最大值
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

        # 计算 ATR（TR 的简单移动平均）
        result[self.name] = tr.rolling(window=self.period).mean()
        return result
