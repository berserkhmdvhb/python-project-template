from __future__ import annotations

import json
from argparse import Namespace
from typing import TYPE_CHECKING

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
