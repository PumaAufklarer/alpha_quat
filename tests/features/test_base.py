"""Tests for feature base classes."""

import pandas as pd

from alpha_quat.features.base import Feature, FeaturePipeline


class SimpleFeature(Feature):
    """Test feature implementation."""

    def __init__(self, offset: int = 1):
        self.offset = offset

    @property
    def name(self) -> str:
        return f"simple_{self.offset}"

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        result = data.copy()
        result[self.name] = data["close"] + self.offset
        return result


def test_feature_base():
    """Test Feature base class interface."""
    feature = SimpleFeature(offset=1)
    assert feature.name == "simple_1"

    data = pd.DataFrame({"close": [10, 20, 30]})
    result = feature.calculate(data)
    assert "simple_1" in result.columns
    assert list(result["simple_1"]) == [11, 21, 31]


def test_feature_pipeline():
    """Test FeaturePipeline."""
    pipeline = FeaturePipeline(
        [
            SimpleFeature(offset=1),
            SimpleFeature(offset=2),
        ]
    )

    data = pd.DataFrame({"close": [10, 20, 30]})
    result = pipeline.calculate(data)
    assert "simple_1" in result.columns
    assert "simple_2" in result.columns
    assert list(result["simple_1"]) == [11, 21, 31]
    assert list(result["simple_2"]) == [12, 22, 32]
