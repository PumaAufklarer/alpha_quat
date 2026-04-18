"""Feature base classes for feature engineering."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class Feature(ABC):
    """
    特征基类

    所有技术指标特征都应该继承此类并实现 calculate 方法。
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """
        特征名称

        Returns:
            特征的唯一标识符名称
        """
        pass

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        计算特征

        Args:
            data: 输入数据 DataFrame

        Returns:
            包含计算结果的 DataFrame，可能包含多列
        """
        pass


class FeaturePipeline:
    """
    特征管道

    组合多个特征，按顺序批量计算。
    """

    def __init__(self, features: list[Feature]):
        """
        初始化特征管道

        Args:
            features: 特征对象列表
        """
        self.features = features

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        按顺序计算所有特征

        Args:
            data: 输入数据 DataFrame

        Returns:
            包含所有特征的 DataFrame
        """
        result = data.copy()
        for feature in self.features:
            result = feature.calculate(result)
        return result
