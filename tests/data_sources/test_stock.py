"""Tests for stock data source module."""



def test_import_stock_module():
    """Test that stock module can be imported."""
    from alpha_quat.data_sources import stock

    assert stock is not None
    assert hasattr(stock, "StockDataSource")


def test_stock_data_source_inheritance():
    """Test that StockDataSource inherits from OHLCDataSource."""
    from alpha_quat.data_sources.base import OHLCDataSource
    from alpha_quat.data_sources.stock import StockDataSource

    assert issubclass(StockDataSource, OHLCDataSource)
