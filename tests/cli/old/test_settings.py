from pathlib import Path
from typing import Callable, Protocol

import pytest
from _pytest.monkeypatch import MonkeyPatch

from myproject.settings import (
    get_log_backup_count as get_default_log_backup_count,
)
from myproject.settings import (
    get_log_max_bytes as get_default_log_max_bytes,
)

# Constants for tests to replace magic numbers
OVERRIDE_LOG_MAX_BYTES = 4321
OVERRIDE_LOG_BACKUP_COUNT = 8

DOTENV_LOG_MAX_BYTES = 1234
DOTENV_LOG_BACKUP_COUNT = 7

CUSTOM_ENV_LOG_MAX_BYTES = 9001
CUSTOM_ENV_LOG_BACKUP_COUNT = 3


class SettingsLike(Protocol):
    def get_environment(self) -> str: ...
    def is_dev(self) -> bool: ...
    def is_uat(self) -> bool: ...
    def is_prod(self) -> bool: ...
    def get_log_max_bytes(self) -> int: ...
    def get_log_backup_count(self) -> int: ...
    def get_default_log_level(self) -> str: ...


def test_default_environment_and_flags(
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    settings = load_fresh_settings()
    assert settings.get_environment() == "DEV"
    assert settings.is_dev()
    assert not settings.is_uat()
    assert not settings.is_prod()


@pytest.mark.parametrize("val", ["uat", "UAT", "UaT"])
def test_uat_variants(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
    val: str,
) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text(f"MYPROJECT_ENV={val}\n")
    settings = load_fresh_settings(dotenv_path=env_file)
    assert settings.get_environment() == "UAT"
    assert settings.is_uat()


@pytest.mark.parametrize("val", ["prod", "PROD", "PrOd"])
def test_prod_variants(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
    val: str,
) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text(f"MYPROJECT_ENV={val}\n")
    settings = load_fresh_settings(dotenv_path=env_file)
    assert settings.get_environment() == "PROD"
    assert settings.is_prod()


def test_unknown_environment(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    env_file = tmp_path / ".env.test"
    env_file.write_text("MYPROJECT_ENV=STAGING\n")
    settings = load_fresh_settings(dotenv_path=env_file)
    assert settings.get_environment() == "STAGING"
    assert not settings.is_dev()
    assert not settings.is_uat()
    assert not settings.is_prod()


def test_numeric_overrides_via_env(
    monkeypatch: MonkeyPatch,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", str(OVERRIDE_LOG_MAX_BYTES))
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", str(OVERRIDE_LOG_BACKUP_COUNT))
    settings = load_fresh_settings()
    assert settings.get_log_max_bytes() == OVERRIDE_LOG_MAX_BYTES
    assert settings.get_log_backup_count() == OVERRIDE_LOG_BACKUP_COUNT


def test_invalid_numeric_env_falls_back(
    monkeypatch: MonkeyPatch,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "notanint")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "alsonotanint")
    settings = load_fresh_settings()
    assert settings.get_log_max_bytes() == get_default_log_max_bytes()
    assert settings.get_log_backup_count() == get_default_log_backup_count()


def test_empty_numeric_env(
    monkeypatch: MonkeyPatch,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "")
    settings = load_fresh_settings()
    assert settings.get_log_max_bytes() == get_default_log_max_bytes()
    assert settings.get_log_backup_count() == get_default_log_backup_count()


def test_dotenv_file_loading(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    dotenv = tmp_path / ".env.test"
    dotenv.write_text(
        f"MYPROJECT_ENV=PROD\nMYPROJECT_LOG_MAX_BYTES={DOTENV_LOG_MAX_BYTES}\n"
        f"MYPROJECT_LOG_BACKUP_COUNT={DOTENV_LOG_BACKUP_COUNT}\n",
    )
    settings = load_fresh_settings(dotenv_path=dotenv)
    assert settings.get_environment() == "PROD"
    assert settings.get_log_max_bytes() == DOTENV_LOG_MAX_BYTES
    assert settings.get_log_backup_count() == DOTENV_LOG_BACKUP_COUNT


def test_dotenv_path_override(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    custom_env = tmp_path / ".custom.env"
    custom_env.write_text(
        f"MYPROJECT_ENV=UAT\nMYPROJECT_LOG_MAX_BYTES={CUSTOM_ENV_LOG_MAX_BYTES}\n"
        f"MYPROJECT_LOG_BACKUP_COUNT={CUSTOM_ENV_LOG_BACKUP_COUNT}\n",
    )
    settings = load_fresh_settings(dotenv_path=custom_env)
    assert settings.get_environment() == "UAT"
    assert settings.get_log_max_bytes() == CUSTOM_ENV_LOG_MAX_BYTES
    assert settings.get_log_backup_count() == CUSTOM_ENV_LOG_BACKUP_COUNT


def test_env_override_priority(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    (tmp_path / ".env").write_text("MYPROJECT_ENV=ENV\n")
    (tmp_path / ".env.override").write_text("MYPROJECT_ENV=OVERRIDE\n")
    (tmp_path / ".env.test").write_text("MYPROJECT_ENV=TEST\n")
    custom = tmp_path / ".custom.env"
    custom.write_text("MYPROJECT_ENV=EXPLICIT\n")
    settings = load_fresh_settings(dotenv_path=custom)
    assert settings.get_environment() == "EXPLICIT"


def test_pytest_without_env_test_falls_back(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("DOTENV_PATH", raising=False)
    (tmp_path / ".env").write_text("MYPROJECT_ENV=UAT\n")
    settings = load_fresh_settings(dotenv_path=tmp_path / ".env")
    assert settings.get_environment() == "UAT"
    assert settings.is_uat()


def test_default_log_level(load_fresh_settings: Callable[..., SettingsLike]) -> None:
    settings = load_fresh_settings()
    assert settings.get_default_log_level() == "INFO"
