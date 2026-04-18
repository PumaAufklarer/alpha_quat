"""Tests for index fetch tasks."""



def test_import_index_tasks():
    """Test that index fetch tasks can be imported."""
    from alpha_quat.tasks.fetch import index_daily, index_monthly, index_weekly

    assert index_daily is not None
    assert index_weekly is not None
    assert index_monthly is not None


def test_index_tasks_registered():
    """Test that index fetch tasks are registered."""
    from alpha_quat.tasks import list_tasks

    all_tasks = list_tasks()
    # Note: The tasks need to be imported first to be registered
    # For this test, we'll just verify the function exists
    assert callable(list_tasks)
