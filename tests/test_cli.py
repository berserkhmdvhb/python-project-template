import sys
from pathlib import Path
from typing import Callable

import pytest
from _pytest.monkeypatch import MonkeyPatch

import myproject.constants as const


def test_cli_help(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--help", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS
    assert "usage" in out.lower()


def test_cli_version(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--version", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS
    assert any(char.isdigit() for char in out)


def test_cli_valid_query(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--query", "hello", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()
    assert code == const.EXIT_SUCCESS
    assert "query" in combined
    assert "hello" in combined
    assert any(k in combined for k in ["processed", "value", "mock"])


def test_cli_empty_query_string_whitespace(
    run_cli: Callable[..., tuple[str, str, int]],
) -> None:
    out, err, code = run_cli("--query", " ", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()
    assert code == const.EXIT_INVALID_USAGE
    assert "empty" in combined or "invalid" in combined


def test_cli_missing_query_argument(
    run_cli: Callable[..., tuple[str, str, int]],
) -> None:
    out, err, code = run_cli(env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()
    assert code == const.EXIT_INVALID_USAGE
    assert "the following arguments are required" in combined


def test_cli_invalid_flag(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--not-a-real-option", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()
    assert code in {const.EXIT_ARGPARSE_ERROR, const.EXIT_INVALID_USAGE}
    assert "usage" in combined or "error" in combined


def test_cli_keyboard_interrupt(monkeypatch: MonkeyPatch) -> None:
    import myproject.cli
    import myproject.cli_color_utils

    def raise_keyboard_interrupt() -> None:
        raise KeyboardInterrupt

    monkeypatch.setattr(myproject.cli_color_utils, "print_lines", raise_keyboard_interrupt)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "example"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.main()
    assert excinfo.value.code == const.EXIT_CANCELLED


def test_cli_internal_error(monkeypatch: MonkeyPatch) -> None:
    import myproject.cli
    import myproject.cli_color_utils

    def raise_unexpected() -> None:
        message = "Simulated crash"
        raise RuntimeError(message)

    monkeypatch.setattr(myproject.cli_color_utils, "print_lines", raise_unexpected)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "test"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.main()
    assert excinfo.value.code == const.EXIT_INVALID_USAGE


def test_cli_dotenv_path_not_found(
    run_cli: Callable[..., tuple[str, str, int]],
    tmp_path: Path,
) -> None:
    bad_path = tmp_path / "missing.env"
    out, err, code = run_cli(
        "--query",
        "hello",
        "--dotenv-path",
        str(bad_path),
        env={"MYPROJECT_ENV": "DEV"},
    )
    combined = (out + err).lower()
    assert "dotenv path not found" in combined
    assert code == const.EXIT_SUCCESS


def test_cli_debug_env_load_with_quiet(
    run_cli: Callable[..., tuple[str, str, int]],
    tmp_path: Path,
) -> None:
    dummy_env = tmp_path / ".env"
    dummy_env.write_text("MYPROJECT_ENV=DEV\n")

    out, err, code = run_cli(
        "--query",
        "hello",
        "--dotenv-path",
        str(dummy_env),
        "--quiet",
        env={"MYPROJECT_DEBUG_ENV_LOAD": "1"},
    )
    combined = (out + err).lower()
    assert "query" not in combined  # quiet suppresses output
    assert code == const.EXIT_SUCCESS
