"""DAG task runner for executing workflows."""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import networkx as nx
import yaml

from alpha_quat.tasks import TaskContext, get_task

logger = logging.getLogger(__name__)


class DAGRunner:
    """DAG-based workflow executor."""

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def load_workflow(self, config_path: str | Path) -> dict:
        """
        Load workflow configuration from YAML file.

        Args:
            config_path: Path to YAML configuration file

        Returns:
            Workflow configuration dictionary
        """
        path = Path(config_path)
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    def build_dag(self, workflow_config: dict) -> nx.DiGraph:
        """
        Build DAG from workflow configuration.

        Args:
            workflow_config: Workflow configuration dictionary

        Returns:
            NetworkX DiGraph representing the workflow

        Raises:
            ValueError: If workflow contains cycles
        """
        graph = nx.DiGraph()

        for task_config in workflow_config["tasks"]:
            task_name = task_config["name"]
            graph.add_node(task_name, config=task_config)

            for dep in task_config.get("depends_on", []):
                graph.add_edge(dep, task_name)

        if not nx.is_directed_acyclic_graph(graph):
            raise ValueError("Workflow contains cycles")

        return graph

    def run(self, workflow_config: dict) -> TaskContext:
        """
        Execute the workflow.

        Args:
            workflow_config: Workflow configuration dictionary

        Returns:
            Final task context with all results
        """
        graph = self.build_dag(workflow_config)

        context = TaskContext(
            data={},
            config=workflow_config.get("config", {}),
        )

        logger.info(f"Starting workflow: {workflow_config.get('name', 'unnamed')}")

        for generation in nx.topological_generations(graph):
            logger.info(f"Processing generation with {len(generation)} tasks")

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_task = {}

                for task_name in generation:
                    task_config = graph.nodes[task_name]["config"]
                    task_cls = get_task(task_config["task"])
                    task = task_cls()

                    future = executor.submit(
                        self._run_single_task,
                        task,
                        task_name,
                        task_config.get("params", {}),
                        context,
                    )
                    future_to_task[future] = task_name

                for future in as_completed(future_to_task):
                    task_name = future_to_task[future]
                    try:
                        result = future.result()
                        context.data[task_name] = result
                        logger.info(f"Completed task: {task_name}")
                    except Exception as e:
                        logger.error(f"Task failed: {task_name}")
                        raise RuntimeError(f"Task {task_name} failed") from e

        logger.info("Workflow completed successfully")
        return context

    def _run_single_task(self, task, task_name: str, params: dict, context: TaskContext) -> dict:
        """Run a single task with its own context."""
        task_context = TaskContext(
            data=context.data.copy(),
            config={**context.config, **params},
        )
        return task.run(task_context)
