import contextlib
import importlib
import json
import logging
import subprocess
import sys
from collections.abc import Callable
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.monkeypatch import MonkeyPatch

import myproject.constants as const
from myproject.cli import cli_main
from tests.utils import ArgcompleteStub


def test_help(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--help", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS
    assert "usage" in out.lower()


def test_version(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--version", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS
    assert any(char.isdigit() for char in out)


@pytest.mark.parametrize("query", ["hello", " world ", "TEST"])
def test_valid_query_json_default(run_cli: Callable[..., tuple[str, str, int]], query: str) -> None:
    out, err, code = run_cli("--query", query, env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS
    payload = json.loads(out)
    assert payload["input"] == query.strip()
    assert "output" in payload
    assert "environment" in payload


def test_valid_query_verbose_text(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli(
        "--query", "hello", "--verbose", "--format", "text", env={"MYPROJECT_ENV": "DEV"}
    )
    combined = (out + err).lower()
    assert code == const.EXIT_SUCCESS
    assert "query" in combined
    assert "hello" in combined
    assert any(k in combined for k in ("processed", "mock"))


def test_format_json_with_verbose_logging(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli(
        "--query", "hello", "--format", "json", "--verbose", env={"MYPROJECT_ENV": "UAT"}
    )
    assert code == const.EXIT_SUCCESS
    assert "[DEBUG]" not in out

    # Find JSON block
    json_start = out.find("{")
    json_end = out.rfind("}") + 1
    assert json_start != -1, "No JSON start found in output"
    assert json_end > json_start, "Invalid JSON range: end before start"

    json_block = out[json_start:json_end]
    payload = json.loads(json_block)

    # Extract surrounding logs
    before = out[:json_start]
    after = out[json_end:]

    assert "[INFO]" in before, "Expected [INFO] log before JSON"
    assert "[INFO]" in after, "Expected [INFO] log after JSON"

    # Validate JSON structure
    assert payload["input"] == "hello"
    assert "output" in payload


def test_empty_query_string_whitespace(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--query", " ", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_INVALID_USAGE
    assert "empty" in (out + err).lower()


def test_missing_query_argument(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli(env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_INVALID_USAGE
    combined = (out + err).lower()
    assert "--query is required" in combined or "error" in combined


def test_invalid_flag(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--not-a-real-option", env={"MYPROJECT_ENV": "DEV"})
    assert code in {const.EXIT_ARGPARSE_ERROR, const.EXIT_INVALID_USAGE}
    assert "usage" in (out + err).lower() or "error" in (out + err).lower()


def test_keyboard_interrupt(monkeypatch: MonkeyPatch) -> None:
    import myproject.cli.cli_main

    def raise_interrupt(*_: object, **__: object) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr("myproject.cli.handlers.process_query_or_simulate", raise_interrupt)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "example"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.cli_main.main()

    assert excinfo.value.code == const.EXIT_CANCELLED


def test_keyboard_interrupt_verbose(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import myproject.cli.cli_main

    def raise_interrupt(*_: object, **__: object) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr("myproject.cli.handlers.process_query_or_simulate", raise_interrupt)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "example", "--verbose"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.cli_main.main()

    assert excinfo.value.code == const.EXIT_CANCELLED

    captured = capsys.readouterr()
    assert "cancelled" in captured.err.lower()
    assert "[warning]" in captured.err.lower()


def test_keyboard_interrupt_hits_warning_line(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import myproject.cli.cli_main

    def raise_interrupt(*_: object, **__: object) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(
        sys, "argv", ["myproject", "--query", "test", "--verbose", "--color", "never"]
    )
    monkeypatch.setattr("myproject.cli.handlers.process_query_or_simulate", raise_interrupt)

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.cli_main.main()

    assert excinfo.value.code == const.EXIT_CANCELLED

    captured = capsys.readouterr()
    # Confirm the line we want is actually executed and printed
    assert "cancelled by user" in captured.err.lower()
    assert "warning" in captured.err.lower()


def test_internal_error(monkeypatch: MonkeyPatch) -> None:
    import myproject.cli.cli_main

    def raise_unexpected(*_: object, **__: object) -> str:
        msg = "Simulated crash"
        raise RuntimeError(msg)

    monkeypatch.setattr("myproject.cli.handlers.process_query_or_simulate", raise_unexpected)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "test"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.cli_main.main()

    assert excinfo.value.code == const.EXIT_ERROR


def test_dotenv_path_not_found(
    run_cli: Callable[..., tuple[str, str, int]], tmp_path: Path
) -> None:
    missing_env = tmp_path / "missing.env"
    out, err, code = run_cli(
        "--query", "hello", "--dotenv-path", str(missing_env), env={"MYPROJECT_ENV": "DEV"}
    )
    assert "dotenv path not found" in (out + err).lower()
    assert code == const.EXIT_SUCCESS


def test_debug_env_load_hidden_by_default(
    run_cli: Callable[..., tuple[str, str, int]], tmp_path: Path
) -> None:
    dummy_env = tmp_path / ".env"
    dummy_env.write_text("MYPROJECT_ENV=DEV\n")

    out, err, code = run_cli(
        "--query",
        "hello",
        "--dotenv-path",
        str(dummy_env),
        env={"MYPROJECT_DEBUG_ENV_LOAD": "1"},
    )
    assert "loaded environment variables" not in (out + err).lower()
    assert code == const.EXIT_SUCCESS


def test_debug_env_load_with_verbose(
    run_cli: Callable[..., tuple[str, str, int]], tmp_path: Path
) -> None:
    dummy_env = tmp_path / ".env"
    dummy_env.write_text("MYPROJECT_ENV=DEV\n")

    out, err, code = run_cli(
        "--query",
        "hello",
        "--dotenv-path",
        str(dummy_env),
        "--verbose",
        "--debug",  # Required to trigger dotenv diagnostics
        env={"MYPROJECT_DEBUG_ENV_LOAD": "1"},
    )

    combined = (out + err).lower()
    assert "loaded environment variables from" in combined
    assert code == const.EXIT_SUCCESS


def test_main_prints_help_and_exits_cleanly(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["myproject"])

    with pytest.raises(SystemExit) as excinfo:
        cli_main.main()

    assert excinfo.value.code == const.EXIT_INVALID_USAGE


def test_main_entry_point_via_module() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "myproject.cli.cli_main"],
        capture_output=True,
        text=True,
        env={"MYPROJECT_ENV": "DEV"},
        check=False,
    )

    assert result.returncode == const.EXIT_INVALID_USAGE
    assert "--query is required" in result.stderr.lower()


def test_debug_output(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    """Ensure --debug triggers diagnostic output."""
    stdout, stderr, code = run_cli("--debug", "--query", "alpha")

    assert code == 0
    assert "=== DEBUG DIAGNOSTICS ===" in stdout
    assert "Parsed args" in stdout
    assert "Environment" in stdout
    assert "END DEBUG DIAGNOSTICS" in stdout


def test_requires_query(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    """Test that CLI exits with error if no --query is provided."""
    stdout, stderr, code = run_cli("--debug")

    assert code == const.EXIT_INVALID_USAGE
    assert "--query is required" in (stdout + stderr).lower()


def test_handles_exception(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """Test that unexpected errors are caught and reported."""
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "crash", "--debug", "--env", "UAT"])

    with (
        patch(
            "myproject.cli.handlers.process_query_or_simulate",
            side_effect=RuntimeError("Boom"),
        ),
        pytest.raises(SystemExit) as excinfo,
    ):
        cli_main.main()

    assert excinfo.value.code == const.EXIT_ERROR

    captured = capsys.readouterr()
    combined_output = captured.out + captured.err
    assert "Boom" in combined_output or "runtimeerror" in combined_output.lower()


def test_main_module_executes_as_script() -> None:
    """Run the CLI via -m and ensure it executes."""
    result = subprocess.run(
        [sys.executable, "-m", "myproject", "--query", "x"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0
    assert "x" in result.stdout.lower()


def test_debug_prints_traceback(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Ensure traceback is printed in debug mode when an exception occurs."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["myproject", "--query", "boom", "--debug", "--env", "UAT"],
    )

    with (
        patch(
            "myproject.cli.handlers.process_query_or_simulate",
            side_effect=RuntimeError("Boom"),
        ),
        pytest.raises(SystemExit),
    ):
        cli_main.main()

    captured = capsys.readouterr()
    # Traceback and exception details are printed to stderr
    assert "traceback" in captured.err.lower()
    assert "runtimeerror: boom" in captured.err.lower()


def test_argcomplete_autocomplete_failure(
    monkeypatch: pytest.MonkeyPatch,
    log_stream: StringIO,
    debug_logger: logging.Logger,
) -> None:
    _ = debug_logger  # Ensure logging is initialized

    # Patch the fake argcomplete module with a valid __spec__
    mock_module = ArgcompleteStub()
    mock_module.__spec__ = importlib.util.spec_from_loader("argcomplete", loader=None)
    monkeypatch.setitem(sys.modules, "argcomplete", mock_module)

    # Force argcomplete flag on reload
    monkeypatch.setattr(cli_main, "ARGCOMPLETE_AVAILABLE", True)
    importlib.reload(cli_main)

    with contextlib.suppress(SystemExit):
        cli_main.main(["--query", "foo"])

    logs = log_stream.getvalue()
    assert "argcomplete setup failed: Simulated autocomplete failure" in logs
