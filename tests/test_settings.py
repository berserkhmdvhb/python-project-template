from pathlib import Path
import pytest

from myproject.settings import (
    get_log_max_bytes as get_default_log_max_bytes,
    get_log_backup_count as get_default_log_backup_count,
)


def test_default_environment_and_flags(load_fresh_settings) -> None:
    settings = load_fresh_settings()
    assert settings.get_environment() == "DEV"
    assert settings.is_dev()
    assert not settings.is_uat()
    assert not settings.is_prod()


@pytest.mark.parametrize("val", ["uat", "UAT", "UaT"])
def test_uat_variants(tmp_path: Path, load_fresh_settings, val: str) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text(f"MYPROJECT_ENV={val}\n")
    settings = load_fresh_settings(dotenv_path=env_file)
    assert settings.get_environment() == "UAT"
    assert settings.is_uat()


@pytest.mark.parametrize("val", ["prod", "PROD", "PrOd"])
def test_prod_variants(tmp_path: Path, load_fresh_settings, val: str) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text(f"MYPROJECT_ENV={val}\n")
    settings = load_fresh_settings(dotenv_path=env_file)
    assert settings.get_environment() == "PROD"
    assert settings.is_prod()


def test_unknown_environment(tmp_path: Path, load_fresh_settings) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text("MYPROJECT_ENV=STAGING\n")
    settings = load_fresh_settings(dotenv_path=env_file)
    assert settings.get_environment() == "STAGING"
    assert not settings.is_dev()
    assert not settings.is_uat()
    assert not settings.is_prod()


def test_numeric_overrides_via_env(
    monkeypatch: pytest.MonkeyPatch, load_fresh_settings
) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "4321")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "8")
    settings = load_fresh_settings()
    assert settings.get_log_max_bytes() == 4321
    assert settings.get_log_backup_count() == 8


def test_invalid_numeric_env_falls_back(
    monkeypatch: pytest.MonkeyPatch, load_fresh_settings
) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "notanint")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "alsonotanint")
    settings = load_fresh_settings()
    assert settings.get_log_max_bytes() == get_default_log_max_bytes()
    assert settings.get_log_backup_count() == get_default_log_backup_count()


def test_empty_numeric_env(
    monkeypatch: pytest.MonkeyPatch, load_fresh_settings
) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "")
    settings = load_fresh_settings()
    assert settings.get_log_max_bytes() == get_default_log_max_bytes()
    assert settings.get_log_backup_count() == get_default_log_backup_count()


def test_dotenv_file_loading(tmp_path: Path, load_fresh_settings) -> None:
    dotenv = tmp_path / ".env.test"
    dotenv.write_text(
        "MYPROJECT_ENV=PROD\nMYPROJECT_LOG_MAX_BYTES=1234\nMYPROJECT_LOG_BACKUP_COUNT=7\n"
    )
    settings = load_fresh_settings(dotenv_path=dotenv)
    assert settings.get_environment() == "PROD"
    assert settings.get_log_max_bytes() == 1234
    assert settings.get_log_backup_count() == 7


def test_dotenv_path_override(tmp_path: Path, load_fresh_settings) -> None:
    custom_env = tmp_path / ".custom.env"
    custom_env.write_text(
        "MYPROJECT_ENV=UAT\nMYPROJECT_LOG_MAX_BYTES=9001\nMYPROJECT_LOG_BACKUP_COUNT=3\n"
    )
    settings = load_fresh_settings(dotenv_path=custom_env)
    assert settings.get_environment() == "UAT"
    assert settings.get_log_max_bytes() == 9001
    assert settings.get_log_backup_count() == 3


def test_env_override_priority(tmp_path: Path, load_fresh_settings) -> None:
    (tmp_path / ".env").write_text("MYPROJECT_ENV=ENV\n")
    (tmp_path / ".env.override").write_text("MYPROJECT_ENV=OVERRIDE\n")
    (tmp_path / ".env.test").write_text("MYPROJECT_ENV=TEST\n")
    custom = tmp_path / ".custom.env"
    custom.write_text("MYPROJECT_ENV=EXPLICIT\n")
    settings = load_fresh_settings(dotenv_path=custom)
    assert settings.get_environment() == "EXPLICIT"


def test_pytest_without_env_test_falls_back(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, load_fresh_settings
) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("DOTENV_PATH", raising=False)
    (tmp_path / ".env").write_text("MYPROJECT_ENV=UAT\n")
    settings = load_fresh_settings(dotenv_path=tmp_path / ".env")
    assert settings.get_environment() == "UAT"
    assert settings.is_uat()


def test_default_log_level(load_fresh_settings) -> None:
    settings = load_fresh_settings()
    assert settings.get_default_log_level() == "INFO"
