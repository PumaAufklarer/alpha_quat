"""Exception definitions for the trading system."""


class AlphaQuatError(Exception):
    """Base exception class for all Alpha Quant errors."""

    pass


class InsufficientFundsError(AlphaQuatError):
    """Raised when there are insufficient funds for an order."""

    def __init__(self, required: float, available: float):
        self.required = required
        self.available = available
        super().__init__(f"Insufficient funds: required {required:.2f}, available {available:.2f}")


class InsufficientPositionError(AlphaQuatError):
    """Raised when there are insufficient position shares for an order."""

    def __init__(self, ts_code: str, required: int, available: int):
        self.ts_code = ts_code
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient position for {ts_code}: required {required}, available {available}"
        )


class RiskLimitExceededError(AlphaQuatError):
    """Raised when a risk limit is exceeded."""

    def __init__(self, limit: str, value: float, max_value: float):
        self.limit = limit
        self.value = value
        self.max_value = max_value
        super().__init__(f"Risk limit exceeded: {limit} = {value:.4f}, max = {max_value:.4f}")


class InvalidOrderError(AlphaQuatError):
    """Raised when an order is invalid."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Invalid order: {reason}")


class DataError(AlphaQuatError):
    """Raised when there's an error with data."""

    pass
