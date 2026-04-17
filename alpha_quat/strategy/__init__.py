"""Strategy layer."""

from .generator import SignalGenerator
from .signals import Signal

__all__ = [
    "Signal",
    "SignalGenerator",
]
