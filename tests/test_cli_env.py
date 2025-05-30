import pytest
import myproject.constants as const


@pytest.mark.parametrize(
    "env_name, expected_substr",
    [
        ("UAT", "uat environment: pre-production validation"),
        ("PROD", "prod environment: logging limited"),
    ],
)
def test_cli_environment_messages(run_cli, env_name: str, expected_substr: str) -> None:
    """
    The CLI should print the correct message based on the MYPROJECT_ENV variable.
    """
    out, err, code = run_cli("--query", "hello", env={"MYPROJECT_ENV": env_name})
    combined = (out + err).lower()

    assert (
        code == const.EXIT_SUCCESS
    ), f"Expected 0 exit code for {env_name}, got {code}"
    assert expected_substr in combined, f"Missing environment message for {env_name}"


def test_cli_quiet_flag_suppresses_logs(run_cli) -> None:
    """
    The --quiet flag should suppress log messages, keeping only result output.
    """
    out, err, code = run_cli("--query", "test", "--quiet", env={"MYPROJECT_ENV": "DEV"})
    combined = (out + err).lower()

    assert code == const.EXIT_SUCCESS, "Expected exit code 0"
    assert "[info]" not in combined, "Info logs should be suppressed with --quiet"
    assert "[debug]" not in combined, "Debug logs should be suppressed with --quiet"
    assert "processed (dev mock): test" in combined, "Expected result not found"


def test_cli_dotenv_path_argument(tmp_path, run_cli) -> None:
    """
    CLI should load environment variables from a file passed via --dotenv-path.
    """
    custom_env = tmp_path / ".custom.env"
    custom_env.write_text("MYPROJECT_ENV=UAT\n")

    out, err, code = run_cli("--query", "loadenv", "--dotenv-path", str(custom_env))
    combined = (out + err).lower()

    assert (
        code == const.EXIT_SUCCESS
    ), "Expected exit code 0 from CLI with --dotenv-path"
    assert (
        "uat environment: pre-production validation" in combined
    ), "UAT message not found"


def test_cli_fallback_to_default_env(run_cli) -> None:
    """
    CLI should default to DEV environment when no env vars or dotenv are set.
    """
    out, err, code = run_cli("--query", "default")
    combined = (out + err).lower()

    assert code == const.EXIT_SUCCESS, "Expected exit code 0 in default (DEV) env"
    assert (
        "dev environment" in combined or "processed (dev mock)" in combined
    ), "Expected DEV environment output not found"
