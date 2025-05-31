import json
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


def test_cli_valid_query_json_default(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--query", "hello", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS
    payload = json.loads(out)
    assert payload["input"] == "hello"
    assert "output" in payload
    assert "environment" in payload


def test_cli_format_json_with_verbose_logging(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli(
        "--query",
        "hello",
        "--format",
        "json",
        "--verbose",
        env={"MYPROJECT_ENV": "DEV"},
    )
    assert code == const.EXIT_SUCCESS

    # Confirm presence of logging
    assert "[INFO]" in out or "[DEBUG]" in out
    assert "Processing query" in out

    # Extract the JSON part (assuming it's printed in stdout after logs)
    json_start = out.find("{")
    assert json_start != -1, "No JSON output found in stdout"

    json_text = out[json_start:].strip()
    payload = json.loads(json_text)

    assert payload["input"] == "hello"
    assert "output" in payload
    assert "environment" in payload


def test_cli_valid_query_verbose_text(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli(
        "--query",
        "hello",
        "--verbose",
        "--format",
        "text",
        env={"MYPROJECT_ENV": "DEV"},
    )
    combined = (out + err).lower()
    assert code == const.EXIT_SUCCESS
    assert "query" in combined
    assert "hello" in combined
    assert any(k in combined for k in ("processed", "mock"))


def test_cli_empty_query_string_whitespace(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--query", " ", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()
    assert code == const.EXIT_INVALID_USAGE
    assert "empty" in combined or "invalid" in combined


def test_cli_missing_query_argument(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli(env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()
    assert code == const.EXIT_SUCCESS
    assert "usage" in combined


def test_cli_invalid_flag(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--not-a-real-option", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()
    assert code in {const.EXIT_ARGPARSE_ERROR, const.EXIT_INVALID_USAGE}
    assert "usage" in combined or "error" in combined


def test_cli_keyboard_interrupt(monkeypatch: MonkeyPatch) -> None:
    import myproject.cli.cli_main

    def raise_interrupt(*_: object, **__: object) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(myproject.cli, "process_query_or_simulate", raise_interrupt)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "example"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.cli_main.main()

    assert excinfo.value.code == const.EXIT_CANCELLED


def test_cli_internal_error(monkeypatch: MonkeyPatch) -> None:
    import myproject.cli.cli_main

    def raise_unexpected(*_: object, **__: object) -> str:
        error_msg = "Simulated crash"
        raise RuntimeError(error_msg)

    monkeypatch.setattr(myproject.cli, "process_query_or_simulate", raise_unexpected)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "test"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.cli_main.main()

    assert excinfo.value.code == const.EXIT_INVALID_USAGE


def test_cli_dotenv_path_not_found(
    run_cli: Callable[..., tuple[str, str, int]],
    tmp_path: Path,
) -> None:
    missing_env = tmp_path / "missing.env"
    out, err, code = run_cli(
        "--query",
        "hello",
        "--dotenv-path",
        str(missing_env),
        env={"MYPROJECT_ENV": "DEV"},
    )
    combined = (out + err).lower()
    assert "dotenv path not found" in combined
    assert code == const.EXIT_SUCCESS


def test_cli_debug_env_load_hidden_by_default(
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
        env={"MYPROJECT_DEBUG_ENV_LOAD": "1"},
    )
    combined = (out + err).lower()
    assert "loaded environment variables" not in combined
    assert code == const.EXIT_SUCCESS


def test_cli_debug_env_load_with_verbose(
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
        "--verbose",
        env={"MYPROJECT_DEBUG_ENV_LOAD": "1"},
    )
    combined = (out + err).lower()
    assert "loaded environment variables" in combined
    assert code == const.EXIT_SUCCESS


def test_cli_color_output_with_always_flag(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    """
    Integration test: ensure CLI output contains ANSI color codes
    when --color=always is passed explicitly.
    """
    out, err, code = run_cli(
        "--query",
        "hello",
        "--color",
        "always",
        "--verbose",
        env={"MYPROJECT_ENV": "DEV"},
    )
    """
    print("\n[DEBUG] STDOUT:")
    print(repr(out))
    print("\n[DEBUG] STDERR:")
    print(repr(err))
    """

    assert code == const.EXIT_SUCCESS

    # ANSI escape sequences start with \x1b[
    has_ansi = any("\x1b[" in line for line in out.splitlines())
    assert has_ansi, "Expected ANSI color codes in output but none found"
