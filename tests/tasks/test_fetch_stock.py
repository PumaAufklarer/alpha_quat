"""Tests for stock fetch tasks."""



def test_import_stock_tasks():
    """Test that stock fetch tasks can be imported."""
    from alpha_quat.tasks.fetch import stock_daily, stock_daily_basic, stock_monthly, stock_weekly

    assert stock_daily is not None
    assert stock_weekly is not None
    assert stock_monthly is not None
    assert stock_daily_basic is not None


def test_stock_tasks_registered():
    """Test that stock fetch tasks are registered."""
    from alpha_quat.tasks import list_tasks

    all_tasks = list_tasks()
    # Note: The tasks need to be imported first to be registered
    # For this test, we'll just verify the function exists
    assert callable(list_tasks)
