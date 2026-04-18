"""Tests for task implementations."""


def test_import_base():
    """Test that base task module can be imported."""
    from alpha_quat.tasks import Task, TaskContext, register_task

    assert Task is not None
    assert TaskContext is not None
    assert register_task is not None


def test_simple_task():
    """Test a simple registered task."""
    from alpha_quat.tasks import Task, TaskContext, get_task, list_tasks, register_task

    @register_task("test_simple")
    class SimpleTask(Task):
        def run(self, context: TaskContext) -> dict:
            return {"result": "ok"}

    assert "test_simple" in list_tasks()
    task_cls = get_task("test_simple")
    task = task_cls()
    context = TaskContext(data={}, config={})
    result = task.run(context)
    assert result["result"] == "ok"
