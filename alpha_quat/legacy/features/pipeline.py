"""
Feature pipeline for combining multiple features.
"""

import pandas as pd

from .base import FeatureBase


class FeaturePipeline:
    """
    Pipeline for applying multiple feature calculations in sequence.
    """

    def __init__(self, features: list[FeatureBase] | None = None):
        """
        Initialize FeaturePipeline.

        Args:
            features: List of features to include in the pipeline
        """
        self.features: list[FeatureBase] = features or []

    def add_feature(self, feature: FeatureBase) -> "FeaturePipeline":
        """
        Add a feature to the pipeline.

        Args:
            feature: Feature to add

        Returns:
            Self for method chaining
        """
        self.features.append(feature)
        return self

    @property
    def required_inputs(self) -> set[str]:
        """
        Get all required input columns across all features.

        Returns:
            Set of required input column names
        """
        inputs: set[str] = set()
        for feature in self.features:
            inputs.update(feature.inputs)
        return inputs

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all features in the pipeline.

        Features are applied in sequence, so later features can use
        columns created by earlier features.

        Args:
            df: Input DataFrame with required columns

        Returns:
            DataFrame with all feature columns added
        """
        result_df = df.copy()

        for feature in self.features:
            result_df = feature.calculate(result_df)

        return result_df

    def __repr__(self) -> str:
        """Get string representation of the pipeline."""
        feature_names = [f.name for f in self.features]
        return f"FeaturePipeline(features={feature_names})"
