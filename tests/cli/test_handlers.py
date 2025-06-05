"""
Unit tests for CLI handler logic.

This module verifies:
- `handle_result` behavior across text and JSON formats
- Conditional logging based on verbosity
- DEV vs. UAT/PROD simulation handling in `process_query_or_simulate`
- Output correctness, log capture, and simulated error handling
"""

from __future__ import annotations

import json
from argparse import Namespace
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest

from myproject.cli.handlers import handle_result, process_query_or_simulate
from myproject.types import FakeSettingsModule

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture

__all__ = [
    "test_handle_result_force_stdout_true",
    "test_handle_result_json_output",
    "test_handle_result_logs_if_not_verbose",
    "test_handle_result_text_output",
    "test_process_query_or_simulate_dev",
    "test_process_query_or_simulate_dev_error",
    "test_process_query_or_simulate_real",
]

# ---------------------------------------------------------------------
# Tests for handle_result()
# ---------------------------------------------------------------------


@pytest.mark.parametrize("env", ["DEV", "UAT", "PROD"])
def test_handle_result_text_output(env: str, capsys: CaptureFixture[str]) -> None:
    """Ensure handle_result prints rich text output with environment context."""
    args = Namespace(query="demo", format="text", verbose=True, debug=False, color="always")
    sett = FakeSettingsModule(env)
    handle_result("Processed: demo", args, sett, use_color=False)

    out, _ = capsys.readouterr()
    assert "[RESULT]" in out
    assert "Input query" in out
    assert "Processed: demo" in out
    assert env in out


def test_handle_result_json_output(capsys: CaptureFixture[str]) -> None:
    """Verify JSON output from handle_result when format is 'json'."""
    args = Namespace(query="demo", format="json", verbose=False, debug=False, color="never")
    sett = FakeSettingsModule("UAT")
    handle_result("Processed: demo", args, sett, use_color=False)

    out, _ = capsys.readouterr()
    data = json.loads(out)
    assert data["environment"] == "UAT"
    assert data["input"] == "demo"
    assert data["output"] == "Processed: demo"


def test_handle_result_logs_if_not_verbose() -> None:
    """When verbose is False, handle_result should log instead of printing."""
    args = Namespace(query="silent", format="text", verbose=False, debug=False, color="never")
    sett = FakeSettingsModule("PROD")
    with patch("myproject.cli.handlers.logging.getLogger") as mock_logger:
        handle_result("Processed: silent", args, sett, use_color=False)
        assert mock_logger.return_value.warning.called


def test_handle_result_force_stdout_true(capsys: CaptureFixture[str]) -> None:
    """Ensure handle_result still writes to stdout when verbose is True."""
    args = Namespace(query="test", format="text", verbose=True, debug=False, color="always")
    sett = FakeSettingsModule("DEV")
    handle_result("Processed: test", args, sett, use_color=True)

    out, _ = capsys.readouterr()
    assert "Processed: test" in out
    assert "DEV environment" in out


# ---------------------------------------------------------------------
# Tests for process_query_or_simulate()
# ---------------------------------------------------------------------


def test_process_query_or_simulate_dev(capsys: CaptureFixture[str]) -> None:
    """In DEV mode, simulate processing and ensure expected output and side effects."""
    args = Namespace(
        query="test simulation",
        format="text",
        verbose=True,
        debug=False,
        color="never",
    )
    sett = FakeSettingsModule("DEV")
    result = process_query_or_simulate(args, sett)

    out, _ = capsys.readouterr()
    assert "Simulating logic in DEV mode" in out
    assert "Processed (DEV MOCK)" in result


@pytest.mark.parametrize("env", ["UAT", "PROD"])
def test_process_query_or_simulate_real(env: str) -> None:
    """In UAT/PROD mode, real query processing should return input directly."""
    args = Namespace(query="real run", format="text", verbose=False, debug=False, color="never")
    sett = FakeSettingsModule(env)
    result = process_query_or_simulate(args, sett)

    expected = args.query if env in {"UAT", "PROD"} else f"Processed query: {args.query}"
    assert result == expected


def test_process_query_or_simulate_dev_error(capsys: CaptureFixture[str]) -> None:
    """Simulate an error in DEV mode to hit _simulate_error and exception handler."""
    args = Namespace(
        query="fail",  # triggers _simulate_error()
        format="text",
        verbose=True,
        debug=False,
        color="never",
    )
    sett = FakeSettingsModule("DEV")

    with pytest.raises(ValueError, match="Simulated runtime failure") as excinfo:
        process_query_or_simulate(args, sett)

    out, _ = capsys.readouterr()
    assert "simulating logic in dev mode" in out.lower()
    assert "simulated runtime failure" in str(excinfo.value).lower()
