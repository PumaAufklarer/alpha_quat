"""Tests for CLI module."""

import sys
from unittest.mock import patch


def test_import_cli():
    """Test that cli module can be imported."""
    from scripts import cli

    assert cli is not None
    assert hasattr(cli, "main")


def test_cli_help():
    """Test that CLI shows help."""
    from scripts.cli import main

    with patch.object(sys, "argv", ["cli", "--help"]):
        with patch("sys.exit") as mock_exit:
            main()
            mock_exit.assert_called_once()
