"""Analytics layer."""

from .drawdown import (
    calculate_average_drawdown,
    calculate_drawdown_duration,
    calculate_drawdowns,
    calculate_max_drawdown,
)
from .metrics import (
    calculate_calmar_ratio,
    calculate_profit_factor,
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_volatility,
    calculate_win_rate,
)
from .returns import (
    calculate_annualized_return,
    calculate_cumulative_returns,
    calculate_returns,
)

__all__ = [
    # Returns
    "calculate_returns",
    "calculate_cumulative_returns",
    "calculate_annualized_return",
    # Drawdown
    "calculate_drawdowns",
    "calculate_max_drawdown",
    "calculate_average_drawdown",
    "calculate_drawdown_duration",
    # Metrics
    "calculate_volatility",
    "calculate_sharpe_ratio",
    "calculate_sortino_ratio",
    "calculate_calmar_ratio",
    "calculate_win_rate",
    "calculate_profit_factor",
]
