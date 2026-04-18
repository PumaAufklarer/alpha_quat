"""Tests for DAG runner."""

import pytest

from alpha_quat.tasks import Task, TaskContext, register_task


@register_task("test_task_1")
class TestTask1(Task):
    def run(self, context: TaskContext) -> dict:
        return {"value": 1}


@register_task("test_task_2")
class TestTask2(Task):
    def run(self, context: TaskContext) -> dict:
        return {"value": 2}


@register_task("test_task_sum")
class TestTaskSum(Task):
    def run(self, context: TaskContext) -> dict:
        total = 0
        for task_data in context.data.values():
            total += task_data.get("value", 0)
        return {"sum": total}


def test_import_runner():
    """Test that runner module can be imported."""
    from scripts import runner

    assert runner is not None
    assert hasattr(runner, "DAGRunner")


def test_dag_runner_init():
    """Test DAGRunner initialization."""
    from scripts.runner import DAGRunner

    runner = DAGRunner(max_workers=2)
    assert runner.max_workers == 2


def test_build_dag_simple():
    """Test building a simple DAG."""
    from scripts.runner import DAGRunner

    runner = DAGRunner()
    workflow_config = {
        "tasks": [
            {"name": "task1", "task": "test_task_1"},
            {"name": "task2", "task": "test_task_2", "depends_on": ["task1"]},
        ]
    }

    graph = runner.build_dag(workflow_config)
    assert graph.has_node("task1")
    assert graph.has_node("task2")
    assert graph.has_edge("task1", "task2")


def test_build_dag_cycle_raises():
    """Test that cyclic DAG raises error."""
    from scripts.runner import DAGRunner

    runner = DAGRunner()
    workflow_config = {
        "tasks": [
            {"name": "task1", "task": "test_task_1", "depends_on": ["task2"]},
            {"name": "task2", "task": "test_task_2", "depends_on": ["task1"]},
        ]
    }

    with pytest.raises(ValueError, match="contains cycles"):
        runner.build_dag(workflow_config)
