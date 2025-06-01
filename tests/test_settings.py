from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Callable

import pytest
import myproject.settings as sett
from myproject.constants import (
    DEFAULT_LOG_ROOT,
    ENV_ENVIRONMENT,
    ENV_LOG_LEVEL,
)

if TYPE_CHECKING:
    from myproject.types import SettingsLike

# Magic constants for tests
MAX_BYTES_TEST = 2048
BACKUP_COUNT_TEST = 7
DOTENV_MAX_BYTES = 1111
DOTENV_BACKUP_COUNT = 3

# ---------------------------------------------------------------------
# Unit-level tests
# ---------------------------------------------------------------------


def test_get_environment_defaults_to_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_ENVIRONMENT, raising=False)
    assert sett.get_environment() == "DEV"


@pytest.mark.parametrize(
    ("val", "expected"),
    [("dev", "DEV"), ("uat", "UAT"), ("PROD", "PROD")],
)
def test_get_environment_case_insensitive(
    monkeypatch: pytest.MonkeyPatch,
    val: str,
    expected: str,
) -> None:
    monkeypatch.setenv(ENV_ENVIRONMENT, val)
    assert sett.get_environment() == expected


def test_unknown_environment_passthrough(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_ENVIRONMENT, "weird_env")
    assert sett.get_environment() == "WEIRD_ENV"


def test_env_accessors(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_ENVIRONMENT, "UAT")
    assert sett.is_uat()
    assert not sett.is_dev()
    assert not sett.is_prod()


def test_get_log_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_ENVIRONMENT, "prod")
    assert sett.get_log_dir() == DEFAULT_LOG_ROOT / "PROD"


@pytest.mark.parametrize(
    ("val", "default", "expected"),
    [("1234", 42, 1234), ("bad", 42, 42), (None, 99, 99)],
)
def test_safe_int(
    monkeypatch: pytest.MonkeyPatch,
    val: str | None,
    default: int,
    expected: int,
) -> None:
    envvar = "MYPROJECT_LOG_MAX_BYTES"
    if val is None:
        monkeypatch.delenv(envvar, raising=False)
    else:
        monkeypatch.setenv(envvar, val)
    result = sett.safe_int(envvar, default)
    assert result == expected


def test_log_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", str(MAX_BYTES_TEST))
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", str(BACKUP_COUNT_TEST))
    monkeypatch.setenv(ENV_LOG_LEVEL, "warning")

    assert sett.get_log_max_bytes() == MAX_BYTES_TEST
    assert sett.get_log_backup_count() == BACKUP_COUNT_TEST
    assert sett.get_default_log_level() == "WARNING"

    monkeypatch.delenv(ENV_LOG_LEVEL, raising=False)
    assert sett.get_default_log_level() == "INFO"


def test_resolve_loaded_dotenv_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy::test")
    test_env = tmp_path / ".env.test"
    test_env.write_text("MYPROJECT_ENV=uat\n")

    monkeypatch.chdir(tmp_path)
    result = sett.resolve_loaded_dotenv_paths()
    assert test_env.exists()
    assert result == [test_env]


# ---------------------------------------------------------------------
# Integration-style tests with load_fresh_settings
# ---------------------------------------------------------------------


@pytest.mark.parametrize("val", ["uat", "UAT", "UaT"])
def test_uat_variants(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
    val: str,
) -> None:
    path = tmp_path / ".env.test"
    path.write_text(f"MYPROJECT_ENV={val}")
    settings = load_fresh_settings(dotenv_path=path)
    assert settings.get_environment() == "UAT"
    assert settings.is_uat()


@pytest.mark.parametrize("val", ["prod", "PROD", "PrOd"])
def test_prod_variants(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
    val: str,
) -> None:
    path = tmp_path / ".env.test"
    path.write_text(f"MYPROJECT_ENV={val}")
    settings = load_fresh_settings(dotenv_path=path)
    assert settings.get_environment() == "PROD"
    assert settings.is_prod()


def test_dotenv_file_loading(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    dotenv = tmp_path / ".env.test"
    dotenv.write_text(
        f"MYPROJECT_ENV=PROD\n"
        f"MYPROJECT_LOG_MAX_BYTES={DOTENV_MAX_BYTES}\n"
        f"MYPROJECT_LOG_BACKUP_COUNT={DOTENV_BACKUP_COUNT}\n"
    )
    assert dotenv.exists()
    settings = load_fresh_settings(dotenv_path=dotenv)
    assert settings.get_environment() == "PROD"
    assert settings.get_log_max_bytes() == DOTENV_MAX_BYTES
    assert settings.get_log_backup_count() == DOTENV_BACKUP_COUNT


def test_invalid_numeric_env_fallback(
    monkeypatch: pytest.MonkeyPatch,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "notanint")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "alsoBad")
    settings = load_fresh_settings()
    assert isinstance(settings.get_log_max_bytes(), int)
    assert isinstance(settings.get_log_backup_count(), int)


def test_env_override_priority(
    tmp_path: Path,
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    (tmp_path / ".env.override").write_text("MYPROJECT_ENV=OVERRIDE")
    (tmp_path / ".env").write_text("MYPROJECT_ENV=BASE")
    (tmp_path / ".env.test").write_text("MYPROJECT_ENV=TEST")
    custom = tmp_path / ".custom.env"
    custom.write_text("MYPROJECT_ENV=EXPLICIT")

    settings = load_fresh_settings(dotenv_path=custom)
    assert settings.get_environment() == "EXPLICIT"


def test_default_environment_and_flags(
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    settings = load_fresh_settings()
    assert settings.get_environment() == "DEV"
    assert settings.is_dev()


def test_default_log_level(
    load_fresh_settings: Callable[..., SettingsLike],
) -> None:
    settings = load_fresh_settings()
    assert settings.get_default_log_level() == "INFO"
