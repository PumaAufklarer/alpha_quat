"""Base classes for tasks."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class TaskContext:
    """Context for passing data between tasks."""

    data: dict[str, Any]
    config: dict[str, Any]


class Task(ABC):
    """Abstract base class for tasks."""

    name: str

    @abstractmethod
    def run(self, context: TaskContext) -> dict[str, Any]:
        """
        Execute the task.

        Args:
            context: Task context containing upstream data and configuration

        Returns:
            Task result, will be stored in context for downstream tasks
        """
        pass
