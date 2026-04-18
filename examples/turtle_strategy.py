"""
Turtle Trading Strategy implementation using new framework.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from alpha_quat.core import SignalDirection
from alpha_quat.features import ATR, DonchianChannels, FeaturePipeline
from alpha_quat.strategy.generator import SignalGenerator
from alpha_quat.strategy.signals import Signal


class TurtleStrategy(SignalGenerator):
    """
    海龟交易策略 - 新框架版本

    使用 SignalGenerator 接口生成交易信号。

    入场规则:
    - 做多: 价格突破入场周期唐奇安上轨
    - 做空: 价格突破入场周期唐奇安下轨

    出场规则:
    - 做多: 价格跌破出场周期唐奇安下轨
    - 做空: 价格突破出场周期唐奇安上轨
    """

    def __init__(
        self,
        entry_period: int = 20,
        exit_period: int = 10,
        position_size: int = 100,
        use_atr: bool = False,
    ):
        """
        初始化海龟策略

        Args:
            entry_period: 入场突破周期 (默认: 20)
            exit_period: 出场突破周期 (默认: 10)
            position_size: 每次交易的股数 (默认: 100)
            use_atr: 是否使用 ATR 进行仓位管理 (默认: False)
        """
        self.entry_period = entry_period
        self.exit_period = exit_period
        self.position_size = position_size
        self.use_atr = use_atr
        self._portfolio_state: dict[str, int] = {}

    def initialize(self) -> None:
        """初始化策略状态"""
        self._portfolio_state = {}

    def generate(self, data: dict[str, Any]) -> list[Signal]:
        """
        生成交易信号

        Args:
            data: 包含市场数据和特征的字典

        Returns:
            交易信号列表
        """
        signals: list[Signal] = []

        ts_code = data.get("ts_code")
        if not ts_code:
            return signals

        close = data.get("close")
        if not close or pd.isna(close):
            return signals

        # 获取唐奇安通道
        entry_upper = data.get(f"donchian_{self.entry_period}_upper")
        entry_lower = data.get(f"donchian_{self.entry_period}_lower")
        exit_upper = data.get(f"donchian_{self.exit_period}_upper")
        exit_lower = data.get(f"donchian_{self.exit_period}_lower")

        # 检查必需特征是否存在
        if any(v is None or pd.isna(v) for v in [entry_upper, entry_lower, exit_upper, exit_lower]):
            return signals

        # 获取当前持仓状态
        current_position = self._portfolio_state.get(ts_code, 0)
        has_long = current_position > 0
        has_short = current_position < 0

        # 交易逻辑
        if not has_long and not has_short:
            # 无持仓，寻找入场机会
            if close > entry_upper:
                # 突破上轨，做多
                signals.append(
                    Signal(
                        ts_code=ts_code,
                        direction=SignalDirection.LONG,
                    )
                )
                # 更新内部状态
                self._portfolio_state[ts_code] = self.position_size
            elif close < entry_lower:
                # 突破下轨，做空
                signals.append(
                    Signal(
                        ts_code=ts_code,
                        direction=SignalDirection.SHORT,
                    )
                )
                # 更新内部状态
                self._portfolio_state[ts_code] = -self.position_size
        elif has_long:
            # 持有多头，寻找出场机会
            if close < exit_lower:
                # 平多
                signals.append(
                    Signal(
                        ts_code=ts_code,
                        direction=SignalDirection.EXIT_LONG,
                    )
                )
                # 更新内部状态
                self._portfolio_state[ts_code] = 0
        elif has_short:
            # 持有空头，寻找出场机会
            if close > exit_upper:
                # 平空
                signals.append(
                    Signal(
                        ts_code=ts_code,
                        direction=SignalDirection.EXIT_SHORT,
                    )
                )
                # 更新内部状态
                self._portfolio_state[ts_code] = 0

        return signals

    def finalize(self) -> None:
        """清理策略状态"""
        self._portfolio_state = {}


def prepare_single_stock_data(
    df: pd.DataFrame,
    ts_code: str,
    entry_period: int = 20,
    exit_period: int = 10,
) -> pd.DataFrame:
    """
    准备单股票回测数据，预计算特征

    Args:
        df: 完整的日线 DataFrame
        ts_code: 股票代码
        entry_period: 入场突破周期
        exit_period: 出场突破周期

    Returns:
        过滤并排序后的 DataFrame，包含计算好的特征
    """
    stock_df = df[df["ts_code"] == ts_code].copy()
    if "trade_date" in stock_df.columns:
        stock_df["trade_date"] = pd.to_datetime(stock_df["trade_date"], format="%Y%m%d")
        stock_df = stock_df.sort_values("trade_date").reset_index(drop=True)

    # 使用新的特征管道计算特征
    pipeline = FeaturePipeline(
        [
            DonchianChannels(period=entry_period),
            DonchianChannels(period=exit_period),
            ATR(period=14),
        ]
    )

    stock_df = pipeline.calculate(stock_df)
    return stock_df
