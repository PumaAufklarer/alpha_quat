#!/usr/bin/env python3
"""
CLI for Alpha Quant Scripts - DAG Task Runner.

This module provides command-line interface for managing and executing workflows.
"""

import argparse
import logging
import sys
from pathlib import Path

from .runner import DAGRunner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Alpha Quant Scripts - DAG Task Runner")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    subparsers.add_parser("list", help="List available workflows")

    run_parser = subparsers.add_parser("run", help="Run a workflow")
    run_parser.add_argument("workflow", help="Workflow name or path")
    run_parser.add_argument("--config", "-c", action="append", help="Override config (key=value)")
    run_parser.add_argument("--workers", "-w", type=int, default=4, help="Max parallel workers")

    validate_parser = subparsers.add_parser("validate", help="Validate workflow config")
    validate_parser.add_argument("workflow", help="Workflow name or path")

    args = parser.parse_args()

    if args.command == "list":
        list_workflows()
    elif args.command == "run":
        run_workflow(args.workflow, args.config, args.workers)
    elif args.command == "validate":
        validate_workflow(args.workflow)
    else:
        parser.print_help()


def list_workflows():
    """List all available workflows."""
    configs_dir = Path("configs/workflows")
    if not configs_dir.exists():
        print("No workflows found")
        return

    print("Available workflows:")
    for yaml_file in sorted(configs_dir.glob("*.yaml")):
        print(f"  - {yaml_file.stem}")


def get_workflow_path(name_or_path: str) -> Path:
    """
    Get workflow config file path.

    Args:
        name_or_path: Workflow name or full path

    Returns:
        Path to workflow config file

    Raises:
        FileNotFoundError: If workflow not found
    """
    path = Path(name_or_path)
    if path.exists():
        return path

    configs_dir = Path("configs/workflows")
    path = configs_dir / f"{name_or_path}.yaml"
    if path.exists():
        return path

    raise FileNotFoundError(f"Workflow not found: {name_or_path}")


def run_workflow(workflow: str, config_overrides: list[str] | None, max_workers: int):
    """
    Run a workflow.

    Args:
        workflow: Workflow name or path
        config_overrides: List of config overrides in key=value format
        max_workers: Maximum number of parallel workers
    """
    config_path = get_workflow_path(workflow)
    runner = DAGRunner(max_workers=max_workers)
    workflow_config = runner.load_workflow(config_path)

    if config_overrides:
        for override in config_overrides:
            if "=" not in override:
                logger.warning(f"Invalid config override: {override}")
                continue
            key, value = override.split("=", 1)
            keys = key.split(".")
            current = workflow_config
            for k in keys[:-1]:
                current = current.setdefault(k, {})
            current[keys[-1]] = value

    logger.info(f"Running workflow: {workflow_config.get('name', workflow)}")
    runner.run(workflow_config)
    logger.info("Workflow completed successfully")


def validate_workflow(workflow: str):
    """
    Validate workflow configuration.

    Args:
        workflow: Workflow name or path
    """
    config_path = get_workflow_path(workflow)
    runner = DAGRunner()
    workflow_config = runner.load_workflow(config_path)

    try:
        runner.build_dag(workflow_config)
        print(f"✓ Workflow '{workflow}' is valid")
    except Exception as e:
        print(f"✗ Workflow '{workflow}' is invalid: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
