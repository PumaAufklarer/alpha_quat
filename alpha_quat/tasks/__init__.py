"""Task module for defining and executing workflow tasks."""

from .base import Task, TaskContext

# Import all task modules to register them
from .fetch import (  # noqa: F401
    index_daily,
    index_monthly,
    index_weekly,
    stock_daily,
    stock_daily_basic,
    stock_list,
    stock_monthly,
    stock_weekly,
    universe,
)
from .registry import get_task, list_tasks, register_task

__all__ = [
    "Task",
    "TaskContext",
    "get_task",
    "list_tasks",
    "register_task",
]
