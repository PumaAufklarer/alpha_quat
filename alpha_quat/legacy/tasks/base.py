"""Base task class."""

import logging
from abc import ABC, abstractmethod
from typing import Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Task(ABC):
    """Abstract base class for tasks."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def run(self) -> Any:
        """
        Execute the task.

        Returns:
            Task result
        """
        pass

    def __call__(self) -> Any:
        """Make task callable."""
        logger.info(f"Starting task: {self.name}")
        try:
            result = self.run()
            logger.info(f"Completed task: {self.name}")
            return result
        except Exception as e:
            logger.error(f"Task failed: {self.name}, error: {e}")
            raise
