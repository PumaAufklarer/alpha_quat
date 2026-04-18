"""Task registry for registering and retrieving tasks."""

from typing import Dict, Type

from .base import Task

_task_registry: Dict[str, Type[Task]] = {}


def register_task(name: str):
    """
    Decorator to register a task class.

    Args:
        name: Unique name for the task

    Returns:
        Decorator function
    """

    def decorator(task_cls: Type[Task]) -> Type[Task]:
        task_cls.name = name
        _task_registry[name] = task_cls
        return task_cls

    return decorator


def get_task(name: str) -> Type[Task]:
    """
    Get a registered task class by name.

    Args:
        name: Task name

    Returns:
        Task class

    Raises:
        KeyError: If task not found
    """
    return _task_registry[name]


def list_tasks() -> list[str]:
    """List all registered task names."""
    return list(_task_registry.keys())
