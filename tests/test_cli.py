import sys
import pytest

from myproject.constants import (
    EXIT_SUCCESS,
    EXIT_INVALID_USAGE,
    EXIT_CANCELLED,
    EXIT_ARGPARSE_ERROR,
)


def test_cli_help(run_cli) -> None:
    out, err, code = run_cli("--help")
    assert code == EXIT_SUCCESS
    assert "usage" in out.lower()


def test_cli_version(run_cli) -> None:
    out, err, code = run_cli("--version")
    assert code == EXIT_SUCCESS
    assert any(char.isdigit() for char in out)


def test_cli_valid_query(run_cli) -> None:
    out, err, code = run_cli("--query", "hello")
    assert code == EXIT_SUCCESS
    assert "query" in out.lower()
    assert "hello" in out.lower()
    assert any(k in out.lower() for k in ["processed", "value", "mock"])


def test_cli_empty_query_string_whitespace(run_cli) -> None:
    out, err, code = run_cli("--query", " ")
    assert code == EXIT_INVALID_USAGE
    assert "empty" in err.lower() or "invalid" in err.lower()


def test_cli_missing_query_argument(run_cli) -> None:
    out, err, code = run_cli()
    assert code == EXIT_INVALID_USAGE
    assert "the following arguments are required" in err.lower()


def test_cli_invalid_flag(run_cli) -> None:
    out, err, code = run_cli("--not-a-real-option")
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
