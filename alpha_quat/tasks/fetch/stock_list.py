"""Stock list fetching task."""

import logging

from alpha_quat.legacy.data_fetcher.sources import DataSource
from alpha_quat.tasks import Task, TaskContext, register_task

logger = logging.getLogger(__name__)


@register_task("fetch_stock_list")
class FetchStockListTask(Task):
    """Task to fetch stock list."""

    def run(self, context: TaskContext) -> dict:
        """
        Execute the task.

        Args:
            context: Task context

        Returns:
            Dictionary with stock_list and count
        """
        ds = DataSource()
        exchange = context.config.get("exchange", "")
        list_status = context.config.get("list_status", "L")
        force_refresh = context.config.get("force_refresh", False)

        logger.info(f"Fetching stock list (exchange={exchange}, list_status={list_status})")

        df, is_cached = ds.get_stock_list(
            exchange=exchange,
            list_status=list_status,
            force_refresh=force_refresh,
        )

        if is_cached:
            logger.info(f"Fetched {len(df)} stocks from cache")
        else:
            logger.info(f"Fetched {len(df)} stocks from API")

        return {
            "stock_list": df,
            "count": len(df),
            "is_cached": is_cached,
        }
