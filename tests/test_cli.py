import sys
import pytest

import myproject.constants as const


def test_cli_help(run_cli) -> None:
    out, err, code = run_cli("--help", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS, "Help command should exit cleanly"
    assert "usage" in out.lower(), "Help output missing 'usage'"


def test_cli_version(run_cli) -> None:
    out, err, code = run_cli("--version", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS, "Version command should exit cleanly"
    assert any(char.isdigit() for char in out), "Version output missing digits"


def test_cli_valid_query(run_cli) -> None:
    out, err, code = run_cli("--query", "hello", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()

    assert code == const.EXIT_SUCCESS, "Valid query should exit successfully"
    assert "query" in combined, "Missing 'query' in output"
    assert "hello" in combined, "Original query string not echoed"
    assert any(
        k in combined for k in ["processed", "value", "mock"]
    ), "Expected keyword missing in output"


def test_cli_empty_query_string_whitespace(run_cli) -> None:
    out, err, code = run_cli("--query", " ", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()

    assert code == const.EXIT_INVALID_USAGE, "Whitespace-only query should fail"
    assert (
        "empty" in combined or "invalid" in combined
    ), "Expected error message missing for empty query"


def test_cli_missing_query_argument(run_cli) -> None:
    out, err, code = run_cli(env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()

    assert (
        code == const.EXIT_INVALID_USAGE
    ), "Missing argument should result in usage error"
    assert (
        "the following arguments are required" in combined
    ), "Missing required argument message not found"


def test_cli_invalid_flag(run_cli) -> None:
    out, err, code = run_cli("--not-a-real-option", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()

    assert code in {
        const.EXIT_ARGPARSE_ERROR,
        const.EXIT_INVALID_USAGE,
    }, "Invalid flag should return proper error code"
    assert (
        "usage" in combined or "error" in combined
    ), "Expected usage or error message missing"


def test_cli_keyboard_interrupt(monkeypatch) -> None:
    import myproject.cli
    import myproject.cli_color_utils
    import sys

    def raise_keyboard_interrupt(*args, **kwargs):
        raise KeyboardInterrupt

    # Patch where print_lines is defined, not where it's used
    monkeypatch.setattr(
        myproject.cli_color_utils, "print_lines", raise_keyboard_interrupt
    )
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "example"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.main()

    assert (
        excinfo.value.code == const.EXIT_CANCELLED
    ), "KeyboardInterrupt should return EXIT_CANCELLED"


def test_cli_internal_error(monkeypatch) -> None:
    import myproject.cli
    import myproject.cli_color_utils

    def raise_unexpected(*args, **kwargs):
        raise RuntimeError("Simulated crash")

    monkeypatch.setattr(myproject.cli_color_utils, "print_lines", raise_unexpected)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "test"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.main()

    assert (
        excinfo.value.code == const.EXIT_INVALID_USAGE
    ), "Unhandled exception should return EXIT_INVALID_USAGE"
