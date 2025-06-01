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


@pytest.mark.parametrize("env", ["DEV", "UAT", "PROD"])
def test_handle_result_text_output(env: str, capsys: CaptureFixture[str]) -> None:
    args = Namespace(query="demo", format="text", verbose=True, debug=False, color="always")
    sett = FakeSettingsModule(env)
    handle_result("Processed: demo", args, sett, use_color=False)

    out, _ = capsys.readouterr()
    assert "[RESULT]" in out
    assert "Input query" in out
    assert "Processed: demo" in out
    assert env in out


def test_handle_result_json_output(capsys: CaptureFixture[str]) -> None:
    args = Namespace(query="demo", format="json", verbose=False, debug=False, color="never")
    sett = FakeSettingsModule("UAT")
    handle_result("Processed: demo", args, sett, use_color=False)

    out, _ = capsys.readouterr()
    data = json.loads(out)
    assert data["environment"] == "UAT"
    assert data["input"] == "demo"
    assert data["output"] == "Processed: demo"


def test_handle_result_logs_if_not_verbose() -> None:
    args = Namespace(query="silent", format="text", verbose=False, debug=False, color="never")
    sett = FakeSettingsModule("PROD")
    with patch("myproject.cli.handlers.logging.getLogger") as mock_logger:
        handle_result("Processed: silent", args, sett, use_color=False)
        assert mock_logger.return_value.warning.called


def test_handle_result_force_stdout_true(capsys: CaptureFixture[str]) -> None:
    args = Namespace(query="test", format="text", verbose=True, debug=False, color="always")
    sett = FakeSettingsModule("DEV")
    handle_result("Processed: test", args, sett, use_color=True)
    out, _ = capsys.readouterr()
    assert "Processed: test" in out
    assert "DEV environment" in out


def test_process_query_or_simulate_dev(capsys: CaptureFixture[str]) -> None:
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
    args = Namespace(query="real run", format="text", verbose=False, debug=False, color="never")
    sett = FakeSettingsModule(env)
    result = process_query_or_simulate(args, sett)
    assert result == "Processed query: real run"
