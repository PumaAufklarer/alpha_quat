"""Tests for index data source module."""

import pytest


def test_import_index_module():
    """Test that index module can be imported."""
    from alpha_quat.data_sources import index

    assert index is not None
    assert hasattr(index, "IndexDataSource")


def test_index_data_source_inheritance():
    """Test that IndexDataSource inherits from OHLCDataSource."""
    from alpha_quat.data_sources.base import OHLCDataSource
    from alpha_quat.data_sources.index import IndexDataSource

    assert issubclass(IndexDataSource, OHLCDataSource)
