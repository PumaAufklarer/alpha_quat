"""Signal generator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from alpha_quat.strategy.signals import Signal


class SignalGenerator(ABC):
    """Abstract base class for signal generators."""

    @abstractmethod
    def generate(self, data: dict[str, Any]) -> list[Signal]:
        """
        Generate trading signals based on input data.

        Args:
            data: Dictionary containing market data and context

        Returns:
            List of Signal objects
        """
        pass

    def initialize(self) -> None:
        """
        Initialize the signal generator.

        Called once before the start of a backtest or live trading session.
        """
        pass

    def finalize(self) -> None:
        """
        Finalize the signal generator.

        Called once at the end of a backtest or live trading session.
        """
        pass
