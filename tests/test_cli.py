import subprocess
import sys
import logging
from io import StringIO
import pytest

from myproject.constants import (
    EXIT_SUCCESS,
    EXIT_INVALID_USAGE,
    EXIT_CANCELLED,
    EXIT_ARGPARSE_ERROR,
)


def run_cli(args: list[str]) -> tuple[str, str, int]:
    """
    Run the CLI as a subprocess and return (stdout, stderr, returncode).
    Automatically adds --color=never to disable ANSI escape codes for tests.
    """
    if "--color=never" not in args:
        args.append("--color=never")
    result = subprocess.run(
        [sys.executable, "-m", "myproject"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def test_cli_help() -> None:
    out, err, code = run_cli(["--help"])
    assert code == EXIT_SUCCESS
    assert "usage" in out.lower()


def test_cli_version() -> None:
    out, err, code = run_cli(["--version"])
    assert code == EXIT_SUCCESS
    assert any(char.isdigit() for char in out)


def test_cli_valid_query() -> None:
    out, err, code = run_cli(["--query", "hello"])
    assert code == EXIT_SUCCESS
    assert "query" in out.lower()
    assert "hello" in out.lower()
    assert "processed value" in out.lower()


def test_cli_empty_query_string_whitespace() -> None:
    out, err, code = run_cli(["--query", " "])
    assert code == EXIT_ARGPARSE_ERROR
    assert "empty" in err.lower() or "invalid" in err.lower()


def test_cli_missing_query_argument() -> None:
    out, err, code = run_cli([])
    assert code == EXIT_ARGPARSE_ERROR
    assert "the following arguments are required" in err.lower()


def test_cli_invalid_flag() -> None:
    out, err, code = run_cli(["--not-a-real-option"])
    assert code in {EXIT_ARGPARSE_ERROR, EXIT_INVALID_USAGE}
    assert "usage" in err.lower() or "error" in err.lower()


def test_cli_keyboard_interrupt(monkeypatch):
    import myproject.cli

    def raise_keyboard_interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    monkeypatch.setattr(myproject.cli, "print_lines", raise_keyboard_interrupt)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "example"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.main()

    assert excinfo.value.code == EXIT_CANCELLED


def test_cli_internal_error(monkeypatch):
    import myproject.cli

    def raise_unexpected(*args, **kwargs):
        raise RuntimeError("Simulated crash")

    monkeypatch.setattr(myproject.cli, "print_lines", raise_unexpected)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "test"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.main()

    assert excinfo.value.code == EXIT_INVALID_USAGE


def test_log_output_for_valid_query(monkeypatch):
    import myproject.cli

    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    logger = logging.getLogger("myproject.cli")
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    monkeypatch.setattr(
        sys, "argv", ["myproject", "--query", "logtest", "--color=never"]
    )

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.main()

    logs = log_stream.getvalue()
    assert "processing query" in logs.lower()
    assert excinfo.value.code == EXIT_SUCCESS

    logger.removeHandler(handler)


def test_log_output_for_empty_query(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", " ", "--color=never"])
    result = subprocess.run(
        [sys.executable, "-m", "myproject", "--query", " ", "--color=never"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    assert "query string must not be empty" in result.stderr.lower()
    assert result.returncode == EXIT_ARGPARSE_ERROR
