import pytest
from myproject.constants import EXIT_SUCCESS


@pytest.mark.parametrize(
    "env_name,expected_substr",
    [
        ("UAT", "pre-production validation"),
        ("PROD", "logging limited"),
    ],
)
def test_cli_environment_messages(run_cli, env_name, expected_substr):
    """
    In UAT and PROD, the CLI should print the corresponding environment message.
    """
    out, err, code = run_cli("--query", "hello", env={"MYPROJECT_ENV": env_name})
    assert code == EXIT_SUCCESS
    combined = (out + err).lower()
    assert expected_substr in combined


def test_cli_quiet_flag_suppresses_logs(run_cli):
    """
    The --quiet flag should suppress all log lines, only leaving the result.
    """
    out, err, code = run_cli("--query", "test", "--quiet", env={"MYPROJECT_ENV": "DEV"})
    assert code == EXIT_SUCCESS

    combined = (out + err).lower()
    # No log-level tags
    assert "[info]" not in combined
    assert "[debug]" not in combined
    # But the processed result should still be printed (DEV mock)
    assert "processed (dev mock): test" in combined
