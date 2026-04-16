"""
Feature engineering module for quantitative trading.
"""

from .base import FeatureBase
from .basic import LogReturns, Returns, Volatility
from .pipeline import FeaturePipeline
from .technical import ATR, EMA, MACD, RSI, SMA, BollingerBands

__all__ = [
    "FeatureBase",
    "Returns",
    "LogReturns",
    "Volatility",
    "SMA",
    "EMA",
    "RSI",
    "MACD",
    "BollingerBands",
    "ATR",
    "FeaturePipeline",
]
