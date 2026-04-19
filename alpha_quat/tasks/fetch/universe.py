"""Universe filtering task."""

import logging

from alpha_quat.tasks.base import Task, TaskContext
from alpha_quat.tasks.registry import register_task
from alpha_quat.universe import (
    EqualityCondition,
    Filter,
    IsSTCondition,
    MarketCapCondition,
    RangeCondition,
    Universe,
    ValueCondition,
)

logger = logging.getLogger(__name__)


@register_task("filter_universe")
class FilterUniverseTask(Task):
    """Task to filter stock universe using conditions."""

    def run(self, context: TaskContext) -> dict:
        """
        Execute the task.

        Args:
            context: Task context

        Returns:
            Dictionary with universe, stock_list, and count
        """
        stock_list = None
        for upstream_data in context.data.values():
            if "stock_list" in upstream_data:
                stock_list = upstream_data["stock_list"]
                break

        if stock_list is None:
            raise ValueError("No stock_list found in upstream data")

        logger.info(f"Building universe from {len(stock_list)} stocks")

        conditions = []
        for cond_config in context.config.get("conditions", []):
            cond_type = cond_config["type"]
            value = cond_config.get("value")
            field = cond_config.get("field")
            min_val = cond_config.get("min")
            max_val = cond_config.get("max")
            operator = cond_config.get("operator", "==")

            if cond_type == "market":
                conditions.append(EqualityCondition("market", value))
            elif cond_type == "list_status":
                conditions.append(EqualityCondition("list_status", value))
            elif cond_type == "not_st":
                conditions.append(IsSTCondition(exclude=True))
            elif cond_type == "is_st":
                conditions.append(IsSTCondition(exclude=False))
            elif cond_type == "market_cap":
                conditions.append(MarketCapCondition(min_val, max_val))
            elif cond_type == "range":
                conditions.append(RangeCondition(field, min_val, max_val))
            elif cond_type == "value":
                conditions.append(ValueCondition(field, operator, value))

        universe = Universe(stock_list)
        if conditions:
            universe = universe.filter(Filter(conditions))
            logger.info(f"Filtered to {len(universe)} stocks")

        return {
            "universe": universe,
            "stock_list": universe.stocks,
            "count": len(universe),
        }
