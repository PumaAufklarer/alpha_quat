"""
Performance metrics calculation for backtesting.
"""
from dataclasses import dataclass
from typing import List, Dict

import pandas as pd
import numpy as np


@dataclass
class Metrics:
    """Performance metrics container."""
    total_return: float = 0.0
    annual_return: float = 0.0
    volatility: float = 0.0
    sharpe_ratio: float = 0.0
    max_drawdown: float = 0.0
    win_rate: float = 0.0
    total_trades: int = 0

    @classmethod
    def calculate(cls, equity_history: List[Dict], risk_free_rate: float = 0.03) -> "Metrics":
        """
        Calculate performance metrics from equity history.

        Args:
            equity_history: List of equity records with datetime and equity
            risk_free_rate: Annual risk-free rate for Sharpe ratio

        Returns:
            Metrics instance
        """
        if not equity_history or len(equity_history) < 2:
            return cls()

        df = pd.DataFrame(equity_history)
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")

        # Calculate returns
        df["return"] = df["equity"].pct_change().dropna()

        # Total return
        initial_equity = df["equity"].iloc[0]
        final_equity = df["equity"].iloc[-1]
        total_return = (final_equity / initial_equity) - 1

        # Annual return (assuming daily data)
        days = (df["datetime"].iloc[-1] - df["datetime"].iloc[0]).days
        annual_return = (1 + total_return) ** (365 / max(days, 1)) - 1 if days > 0 else 0

        # Volatility (annualized)
        volatility = df["return"].std() * np.sqrt(252) if len(df) > 1 else 0

        # Sharpe ratio
        excess_return = annual_return - risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility != 0 else 0

        # Max drawdown
        cumulative = (1 + df["return"].fillna(0)).cumprod()
        running_max = cumulative.cummax()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        return cls(
            total_return=total_return,
            annual_return=annual_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown
        )

    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            "total_return": self.total_return,
            "annual_return": self.annual_return,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "total_trades": self.total_trades
        }
