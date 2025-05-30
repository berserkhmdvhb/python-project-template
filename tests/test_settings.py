import sys
import importlib
import types
import pytest

from myproject.settings import (
    get_log_max_bytes as get_default_log_max_bytes,
    get_log_backup_count as get_default_log_backup_count,
)


def reload_settings() -> types.ModuleType:
    sys.modules.pop("myproject.settings", None)
    return importlib.import_module("myproject.settings")


def load_fresh_settings() -> types.ModuleType:
    settings = reload_settings()
    settings.load_settings()
    return settings


def test_default_environment_and_flags(monkeypatch, tmp_path):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    monkeypatch.chdir(tmp_path)

    settings = load_fresh_settings()
    assert settings.get_environment() == "DEV"
    assert settings.is_dev()
    assert not settings.is_uat()
    assert not settings.is_prod()


@pytest.mark.parametrize("val", ["uat", "UAT", "UaT"])
def test_uat_variants(monkeypatch, tmp_path, val):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env.test").write_text(f"MYPROJECT_ENV={val}\n")

    settings = load_fresh_settings()
    assert settings.get_environment() == "UAT"
    assert settings.is_uat()
    assert not settings.is_dev()
    assert not settings.is_prod()


@pytest.mark.parametrize("val", ["prod", "PROD", "PrOd"])
def test_prod_variants(monkeypatch, tmp_path, val):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env.test").write_text(f"MYPROJECT_ENV={val}\n")

    settings = load_fresh_settings()
    assert settings.get_environment() == "PROD"
    assert settings.is_prod()
    assert not settings.is_dev()
    assert not settings.is_uat()


def test_unknown_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env.test").write_text("MYPROJECT_ENV=STAGING\n")

    settings = load_fresh_settings()
    assert settings.get_environment() == "STAGING"
    assert not settings.is_dev()
    assert not settings.is_uat()
    assert not settings.is_prod()


def test_numeric_overrides_via_env(monkeypatch, tmp_path):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "4321")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "8")
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env.test").write_text("")

    settings = load_fresh_settings()
    assert settings.get_log_max_bytes() == 4321
    assert settings.get_log_backup_count() == 8


def test_invalid_numeric_env_falls_back(monkeypatch):
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "notanint")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "alsonotanint")

    settings = load_fresh_settings()
    assert settings.get_log_max_bytes() == get_default_log_max_bytes()
    assert settings.get_log_backup_count() == get_default_log_backup_count()


def test_empty_numeric_env(monkeypatch):
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "")

    settings = load_fresh_settings()
    assert settings.get_log_max_bytes() == get_default_log_max_bytes()
    assert settings.get_log_backup_count() == get_default_log_backup_count()


def test_dotenv_file_loading(tmp_path, monkeypatch):
    (tmp_path / ".env.test").write_text(
        "MYPROJECT_ENV=PROD\nMYPROJECT_LOG_MAX_BYTES=1234\nMYPROJECT_LOG_BACKUP_COUNT=7\n"
    )
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy_test")
    monkeypatch.chdir(tmp_path)

    settings = load_fresh_settings()
    assert settings.get_environment() == "PROD"
    assert settings.get_log_max_bytes() == 1234
    assert settings.get_log_backup_count() == 7


def test_dotenv_path_override(monkeypatch, tmp_path):
    env_override = tmp_path / ".custom.env"
    env_override.write_text(
        "MYPROJECT_ENV=UAT\nMYPROJECT_LOG_MAX_BYTES=9001\nMYPROJECT_LOG_BACKUP_COUNT=3\n"
    )
    monkeypatch.setenv("DOTENV_PATH", str(env_override))
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    monkeypatch.chdir(tmp_path)

    settings = load_fresh_settings()
    assert settings.get_environment() == "UAT"
    assert settings.get_log_max_bytes() == 9001
    assert settings.get_log_backup_count() == 3


def test_env_override_priority(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("MYPROJECT_ENV=ENV\n")
    (tmp_path / ".env.override").write_text("MYPROJECT_ENV=OVERRIDE\n")
    (tmp_path / ".env.test").write_text("MYPROJECT_ENV=TEST\n")
    (tmp_path / ".custom.env").write_text("MYPROJECT_ENV=EXPLICIT\n")

    monkeypatch.setenv("DOTENV_PATH", str(tmp_path / ".custom.env"))
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    monkeypatch.chdir(tmp_path)

    settings = load_fresh_settings()
    assert settings.get_environment() == "EXPLICIT"
    assert settings.get_environment() not in {"TEST", "OVERRIDE", "ENV"}


def test_pytest_without_env_test_falls_back(monkeypatch, tmp_path):
    """Fallback order applies if .env.test is missing."""
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.chdir(tmp_path)
    assert not (tmp_path / ".env.test").exists()

    (tmp_path / ".env").write_text("MYPROJECT_ENV=UAT\n")

    settings = load_fresh_settings()
    assert settings.get_environment() == "UAT"
    assert settings.is_uat()


def test_default_log_level(monkeypatch):
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
    settings = load_fresh_settings()
    assert settings.get_default_log_level() == "INFO"
