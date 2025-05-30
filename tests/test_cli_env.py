from pathlib import Path
from typing import Callable

import pytest

import myproject.constants as const


@pytest.mark.parametrize(
    ("env_name", "expected_substr"),
    [
        ("UAT", "uat environment: pre-production validation"),
        ("PROD", "prod environment: logging limited"),
    ],
)
def test_cli_environment_messages(
    run_cli: Callable[..., tuple[str, str, int]],
    env_name: str,
    expected_substr: str,
) -> None:
    """CLI should emit correct message based on MYPROJECT_ENV value."""
    out, err, code = run_cli("--query", "hello", env={"MYPROJECT_ENV": env_name})
    combined = (out + err).lower()

    assert code == const.EXIT_SUCCESS, f"Expected 0 exit code for {env_name}, got {code}"
    assert expected_substr in combined, f"Missing expected output for {env_name}"


def test_cli_quiet_flag_suppresses_logs(
    run_cli: Callable[..., tuple[str, str, int]],
) -> None:
    """--quiet should suppress log messages but still return valid result."""
    out, err, code = run_cli("--query", "test", "--quiet", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()

    assert code == const.EXIT_SUCCESS, "Expected exit code 0"
    assert "[info]" not in combined, "Info log should be suppressed"
    assert "[debug]" not in combined, "Debug log should be suppressed"
    assert "processed (dev mock): test" in combined, "Expected output not found"


def test_cli_dotenv_path_argument(
    tmp_path: Path,
    run_cli: Callable[..., tuple[str, str, int]],
) -> None:
    """CLI should load MYPROJECT_ENV from --dotenv-path file."""
    custom_env = tmp_path / ".custom.env"
    custom_env.write_text("MYPROJECT_ENV=UAT\n")

    out, err, code = run_cli("--query", "loadenv", "--dotenv-path", str(custom_env))
    combined = (out + err).lower()

    assert code == const.EXIT_SUCCESS, "Expected exit code 0 with custom dotenv"
    assert "uat environment: pre-production validation" in combined, (
        "Expected UAT message not found"
    )


def test_cli_fallback_to_default_env(
    run_cli: Callable[..., tuple[str, str, int]],
) -> None:
    """CLI should default to DEV environment when nothing is configured."""
    out, err, code = run_cli("--query", "default")
    combined = (out + err).lower()

    assert code == const.EXIT_SUCCESS, "Expected exit code 0"
    assert "dev environment" in combined or "processed (dev mock)" in combined, (
        "Expected default DEV environment message"
    )
