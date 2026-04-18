"""Fetch stock monthly data task."""

import logging

from alpha_quat.data_sources.stock import StockDataSource
from alpha_quat.tasks import Task, TaskContext, register_task

logger = logging.getLogger(__name__)


@register_task("fetch_stock_monthly")
class FetchStockMonthlyTask(Task):
    """Task to fetch stock monthly data."""

    def run(self, context: TaskContext) -> dict:
        """
        Execute the task.

        Args:
            context: Task context containing upstream data and configuration

        Returns:
            Task result dictionary with data, count, and is_cached
        """
        ds = StockDataSource()
        ts_code = context.config.get("ts_code", "")
        start_date = context.config.get("start_date", "")
        end_date = context.config.get("end_date", "")
        adj = context.config.get("adj", None)
        force_refresh = context.config.get("force_refresh", False)

        logger.info(f"Fetching stock monthly data: ts_code={ts_code}")

        df, is_cached = ds.get_monthly(
            ts_code=ts_code,
            start_date=start_date,
            end_date=end_date,
            adj=adj,
            force_refresh=force_refresh,
        )

        if is_cached:
            logger.info(f"Fetched {len(df)} records from cache")
        else:
            logger.info(f"Fetched {len(df)} records from API")

        return {
            "data": df,
            "count": len(df),
            "is_cached": is_cached,
        }
