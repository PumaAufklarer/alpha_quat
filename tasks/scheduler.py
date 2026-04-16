"""Task scheduler for sequential execution."""

import logging
from typing import Any

from .base import Task

logger = logging.getLogger(__name__)


class Scheduler:
    """
    Simple sequential task scheduler.
    """

    def __init__(self, stop_on_error: bool = True):
        """
        Initialize scheduler.

        Args:
            stop_on_error: If True, stop execution when a task fails
        """
        self.tasks: list[Task] = []
        self.stop_on_error = stop_on_error
        self.results: list[Any] = []

    def add_task(self, task: Task) -> "Scheduler":
        """
        Add a task to the scheduler.

        Args:
            task: Task to add

        Returns:
            Self for chaining
        """
        self.tasks.append(task)
        return self

    def add_tasks(self, tasks: list[Task]) -> "Scheduler":
        """
        Add multiple tasks to the scheduler.

        Args:
            tasks: List of tasks to add

        Returns:
            Self for chaining
        """
        self.tasks.extend(tasks)
        return self

    def run(self) -> list[Any]:
        """
        Run all tasks sequentially.

        Returns:
            List of task results
        """
        logger.info(f"Starting scheduler with {len(self.tasks)} tasks")
        self.results = []

        for i, task in enumerate(self.tasks, 1):
            logger.info(f"Executing task {i}/{len(self.tasks)}: {task.name}")
            try:
                result = task()
                self.results.append(result)
            except Exception:
                logger.error(f"Task {i}/{len(self.tasks)} failed: {task.name}")
                self.results.append(None)
                if self.stop_on_error:
                    logger.error("Stopping scheduler due to task failure")
                    raise

        logger.info("Scheduler completed all tasks")
        return self.results

    def clear(self) -> None:
        """Clear all tasks and results."""
        self.tasks = []
        self.results = []
