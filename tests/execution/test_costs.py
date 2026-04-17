"""Tests for cost models."""

from alpha_quat.execution.costs import (
    AShareCostModel,
    FixedSlippageModel,
    PercentageSlippageModel,
)


def test_a_share_cost_model():
    """Test A-share cost model."""
    model = AShareCostModel()
    # Buy order: only commission
    commission = model.calculate_commission(value=10000.0, is_buy=True)
    assert commission > 0
    # Sell order: commission + stamp tax (0.1%)
    commission_sell = model.calculate_commission(value=10000.0, is_buy=False)
    assert commission_sell > commission


def test_fixed_slippage_model():
    """Test fixed slippage model."""
    model = FixedSlippageModel(fixed_amount=0.01)
    slippage = model.calculate_slippage(price=10.0, quantity=100, is_buy=True)
    assert slippage == 0.01


def test_percentage_slippage_model():
    """Test percentage slippage model."""
    model = PercentageSlippageModel(percentage=0.001)  # 0.1%
    slippage = model.calculate_slippage(price=10.0, quantity=100, is_buy=True)
    assert slippage == 0.01  # 10.0 * 0.001
