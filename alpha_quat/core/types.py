"""Core type definitions for the trading system."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class Currency(float):
    """Currency value type."""

    def __new__(cls, value: float) -> Currency:
        return float.__new__(cls, round(value, 4))

    def __repr__(self) -> str:
        return f"Currency({float(self):.4f})"


class Quantity(int):
    """Quantity (shares/contracts) type."""

    def __repr__(self) -> str:
        return f"Quantity({int(self)})"


class Price(float):
    """Price value type."""

    def __new__(cls, value: float) -> Price:
        return float.__new__(cls, round(value, 4))

    def __repr__(self) -> str:
        return f"Price({float(self):.4f})"


@dataclass(frozen=True)
class Timestamp:
    """Timestamp wrapper."""

    value: datetime

    @classmethod
    def from_datetime(cls, dt: datetime) -> Timestamp:
        return cls(dt)

    def as_datetime(self) -> datetime:
        return self.value

    def __repr__(self) -> str:
        return f"Timestamp({self.value.isoformat()})"


class SignalDirection(Enum):
    """Signal direction enum."""

    LONG = "long"
    SHORT = "short"
    EXIT_LONG = "exit_long"
    EXIT_SHORT = "exit_short"
    FLAT = "flat"


class Urgency(Enum):
    """Order urgency enum."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
