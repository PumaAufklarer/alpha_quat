"""Trading cost models."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from alpha_quat.core import Currency, Price


class CostModel(ABC):
    """Abstract base class for cost models."""

    @abstractmethod
    def calculate_commission(self, value: float, is_buy: bool) -> Currency:
        """Calculate commission for a trade."""
        pass


@dataclass
class AShareCostModel(CostModel):
    """A-share trading cost model.

    Includes:
    - Commission: ~0.03% (minimum 5 yuan)
    - Stamp tax: 0.1% (sell only)
    - Transfer fee: 0.001% (both sides)
    """

    commission_rate: float = 0.0003  # 0.03%
    commission_min: float = 5.0
    stamp_tax_rate: float = 0.001  # 0.1%, sell only
    transfer_fee_rate: float = 0.00001  # 0.001%

    def calculate_commission(self, value: float, is_buy: bool) -> Currency:
        """Calculate total commission for A-share trade."""
        commission = value * self.commission_rate
        commission = max(commission, self.commission_min)
        transfer_fee = value * self.transfer_fee_rate
        if not is_buy:
            stamp_tax = value * self.stamp_tax_rate
        else:
            stamp_tax = 0.0
        total = commission + transfer_fee + stamp_tax
        return Currency(total)


class SlippageModel(ABC):
    """Abstract base class for slippage models."""

    @abstractmethod
    def calculate_slippage(self, price: float, quantity: int, is_buy: bool) -> Price:
        """Calculate slippage amount per share."""
        pass


@dataclass
class FixedSlippageModel(SlippageModel):
    """Fixed amount slippage model."""

    fixed_amount: float = 0.01

    def calculate_slippage(self, price: float, quantity: int, is_buy: bool) -> Price:
        return Price(self.fixed_amount)


@dataclass
class PercentageSlippageModel(SlippageModel):
    """Percentage of price slippage model."""

    percentage: float = 0.001  # 0.1%

    def calculate_slippage(self, price: float, quantity: int, is_buy: bool) -> Price:
        return Price(price * self.percentage)
