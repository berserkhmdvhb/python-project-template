import json
import subprocess
import sys
from pathlib import Path
from typing import Callable

import pytest
from _pytest.monkeypatch import MonkeyPatch

import myproject.constants as const


def test_help(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--help", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS
    assert "usage" in out.lower()


def test_version(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--version", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS
    assert any(char.isdigit() for char in out)


@pytest.mark.parametrize("query", ["hello", " world ", "TEST"])
def test_valid_query_json_default(
    run_cli: Callable[..., tuple[str, str, int]], query: str
) -> None:
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
        "--query", "hello", "--format", "json", "--verbose", env={"MYPROJECT_ENV": "DEV"}
    )
    assert code == const.EXIT_SUCCESS
    assert "[INFO]" in out or "[DEBUG]" in out
    json_start = out.find("{")
    assert json_start != -1
    payload = json.loads(out[json_start:])
    assert payload["input"] == "hello"
    assert "output" in payload


def test_empty_query_string_whitespace(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli("--query", " ", env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_INVALID_USAGE
    assert "empty" in (out + err).lower()


def test_missing_query_argument(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli(env={"MYPROJECT_ENV": "DEV"})
    assert code == const.EXIT_SUCCESS
    assert "usage" in (out + err).lower()


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


def test_internal_error(monkeypatch: MonkeyPatch) -> None:
    import myproject.cli.cli_main

    def raise_unexpected(*_: object, **__: object) -> str:
        msg = "Simulated crash"
        raise RuntimeError(msg)

    monkeypatch.setattr("myproject.cli.handlers.process_query_or_simulate", raise_unexpected)
    monkeypatch.setattr(sys, "argv", ["myproject", "--query", "test"])

    with pytest.raises(SystemExit) as excinfo:
        myproject.cli.cli_main.main()

    assert excinfo.value.code == const.EXIT_INVALID_USAGE


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
    from myproject.cli import cli_main
    monkeypatch.setattr(sys, "argv", ["myproject"])

    with pytest.raises(SystemExit) as excinfo:
        cli_main.main()

    assert excinfo.value.code == const.EXIT_SUCCESS


def test_main_entry_point_via_module() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "myproject.cli.cli_main"],
        capture_output=True,
        text=True,
        env={"MYPROJECT_ENV": "DEV"}, check=False,
    )
    assert result.returncode == 0
    assert "usage" in (result.stdout + result.stderr).lower()
