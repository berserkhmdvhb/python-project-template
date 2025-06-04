from __future__ import annotations

import importlib
import logging
import os
from io import StringIO
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

import myproject.settings as sett
from myproject.constants import DEFAULT_LOG_ROOT, ENV_ENVIRONMENT, ENV_LOG_LEVEL

if TYPE_CHECKING:
    from myproject.types import LoadSettingsFunc, TestRootSetup

MAX_BYTES_TEST = 2048
BACKUP_COUNT_TEST = 7
DOTENV_MAX_BYTES = 1111
DOTENV_BACKUP_COUNT = 3

# ---------------------------------------------------------------------
# Unit-level Tests
# ---------------------------------------------------------------------


def test_get_environment_defaults_to_dev(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_ENVIRONMENT, raising=False)
    assert sett.get_environment() == "DEV"


@pytest.mark.parametrize(
    ("val", "expected"),
    [("dev", "DEV"), ("uat", "UAT"), ("PROD", "PROD")],
)
def test_get_environment_case_insensitive(
    monkeypatch: pytest.MonkeyPatch, val: str, expected: str
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
    monkeypatch: pytest.MonkeyPatch, val: str | None, default: int, expected: int
) -> None:
    envvar = "MYPROJECT_LOG_MAX_BYTES"
    if val is None:
        monkeypatch.delenv(envvar, raising=False)
    else:
        monkeypatch.setenv(envvar, val)
    assert sett.safe_int(envvar, default) == expected


def test_log_config(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", str(MAX_BYTES_TEST))
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", str(BACKUP_COUNT_TEST))
    monkeypatch.setenv(ENV_LOG_LEVEL, "warning")
    assert sett.get_log_max_bytes() == MAX_BYTES_TEST
    assert sett.get_log_backup_count() == BACKUP_COUNT_TEST
    assert sett.get_default_log_level() == "WARNING"

    monkeypatch.delenv(ENV_LOG_LEVEL, raising=False)
    assert sett.get_default_log_level() == "INFO"


def test_resolve_loaded_dotenv_paths(
    setup_test_root: TestRootSetup,
    monkeypatch: pytest.MonkeyPatch,
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    _ = debug_logger
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy::test")
    tmp_path = setup_test_root(env_files=[".env.test"])
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("MYPROJECT_ROOT_DIR_FOR_TESTS", str(tmp_path))
    import myproject.settings as sett_module

    importlib.reload(sett_module)
    test_env = tmp_path / ".env.test"
    assert sett_module.resolve_loaded_dotenv_paths() == [test_env]
    sett_module.print_dotenv_debug()

    output = log_stream.getvalue()
    assert "Selected .env file" in output
    assert ".env.test" in output


def test_env_sample_fallback(
    tmp_path: Path,
    load_fresh_settings_no_test_mode: LoadSettingsFunc,
) -> None:
    expected_path = tmp_path / ".env.sample"
    expected_path.write_text("MYPROJECT_ENV=DEV\n")

    settings = load_fresh_settings_no_test_mode(
        dotenv_path=None,
        root_dir=tmp_path,
    )

    assert not settings.is_test_mode()
    assert settings.resolve_loaded_dotenv_paths() == [expected_path]


def test_no_dotenv_file(
    monkeypatch: pytest.MonkeyPatch,
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    _ = debug_logger
    monkeypatch.setattr(sett, "_resolve_dotenv_paths", list)
    result = sett.load_settings(verbose=True)
    assert result == []
    output = log_stream.getvalue()
    assert "No .env file loaded" in output
    assert "falling back to system env" in output


# ---------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------


@pytest.mark.parametrize("val", ["uat", "UAT", "UaT"])
def test_uat_variants(tmp_path: Path, load_fresh_settings: LoadSettingsFunc, val: str) -> None:
    dotenv = tmp_path / ".env.test"
    dotenv.write_text(f"MYPROJECT_ENV={val}")
    settings = load_fresh_settings(dotenv_path=dotenv)
    assert settings.get_environment() == "UAT"


@pytest.mark.parametrize("val", ["prod", "PROD", "PrOd"])
def test_prod_variants(tmp_path: Path, load_fresh_settings: LoadSettingsFunc, val: str) -> None:
    dotenv = tmp_path / ".env.test"
    dotenv.write_text(f"MYPROJECT_ENV={val}")
    settings = load_fresh_settings(dotenv_path=dotenv)
    assert settings.get_environment() == "PROD"


def test_dotenv_file_loading(tmp_path: Path, load_fresh_settings: LoadSettingsFunc) -> None:
    dotenv = tmp_path / ".env.test"
    dotenv.write_text(
        f"MYPROJECT_ENV=PROD\n"
        f"MYPROJECT_LOG_MAX_BYTES={DOTENV_MAX_BYTES}\n"
        f"MYPROJECT_LOG_BACKUP_COUNT={DOTENV_BACKUP_COUNT}\n"
    )
    settings = load_fresh_settings(dotenv_path=dotenv)
    assert settings.get_environment() == "PROD"
    assert settings.get_log_max_bytes() == DOTENV_MAX_BYTES
    assert settings.get_log_backup_count() == DOTENV_BACKUP_COUNT


def test_invalid_numeric_env_fallback(
    monkeypatch: pytest.MonkeyPatch, load_fresh_settings: LoadSettingsFunc
) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "notanint")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "nope")
    settings = load_fresh_settings()
    assert isinstance(settings.get_log_max_bytes(), int)
    assert isinstance(settings.get_log_backup_count(), int)


def test_env_override_priority(tmp_path: Path, load_fresh_settings: LoadSettingsFunc) -> None:
    (tmp_path / ".env.override").write_text("MYPROJECT_ENV=OVERRIDE")
    (tmp_path / ".env").write_text("MYPROJECT_ENV=BASE")
    (tmp_path / ".env.test").write_text("MYPROJECT_ENV=TEST")
    (tmp_path / ".custom.env").write_text("MYPROJECT_ENV=EXPLICIT")
    settings = load_fresh_settings(dotenv_path=tmp_path / ".custom.env")
    assert settings.get_environment() == "EXPLICIT"


@pytest.mark.parametrize(
    "combo",
    [
        ([".custom.env"], {}, "EXPLICIT"),
        ([".env.override"], {}, "OVERRIDE"),
        ([".env"], {}, "BASE"),
        ([".env.local"], {}, "LOCAL"),
        ([".env.test"], {"PYTEST_CURRENT_TEST": "yes"}, "TEST"),
        ([".env.sample"], {}, "SAMPLE"),
    ],
)
def test_dotenv_priority_matrix(
    combo: tuple[list[str], dict[str, str], str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    load_fresh_settings: LoadSettingsFunc,
    load_fresh_settings_no_test_mode: LoadSettingsFunc,
) -> None:
    files, env_vars, expected_env = combo

    for key, val in env_vars.items():
        monkeypatch.setenv(key, val)

    for file in files:
        (tmp_path / file).write_text(f"MYPROJECT_ENV={expected_env}")

    dotenv_path = tmp_path / ".custom.env" if ".custom.env" in files else None
    use_test_mode = "PYTEST_CURRENT_TEST" in env_vars

    if use_test_mode:
        os.environ["PYTEST_CURRENT_TEST"] = env_vars["PYTEST_CURRENT_TEST"]

    load = load_fresh_settings if use_test_mode else load_fresh_settings_no_test_mode
    settings = load(dotenv_path=dotenv_path, root_dir=tmp_path)
    assert settings.get_environment() == expected_env


# ---------------------------------------------------------------------
# Miscellaneous
# ---------------------------------------------------------------------


def test_default_environment_and_flags(load_fresh_settings: LoadSettingsFunc) -> None:
    settings = load_fresh_settings()
    assert settings.get_environment() == "DEV"


def test_default_log_level(load_fresh_settings: LoadSettingsFunc) -> None:
    settings = load_fresh_settings()
    assert settings.get_default_log_level() == "INFO"


def test_is_test_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "yes")
    assert sett.is_test_mode()


def test_is_not_test_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    assert not sett.is_test_mode()


def test_environment_empty_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_ENVIRONMENT, "")
    assert sett.get_environment() == "DEV"


# ---------------------------------------------------------------------
# Tests for dotenv debugging diagnostics
# ---------------------------------------------------------------------


def test_dotenv_path_missing_warns(
    monkeypatch: pytest.MonkeyPatch,
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    _ = debug_logger
    monkeypatch.setenv("DOTENV_PATH", "/nonexistent/.env")
    monkeypatch.setenv("MYPROJECT_DEBUG_ENV_LOAD", "1")
    sett.load_settings()

    output = log_stream.getvalue()
    assert "DOTENV_PATH is set to" in output
    assert ".env" in output


def test_dotenv_debug_no_files(
    monkeypatch: pytest.MonkeyPatch,
    log_stream: StringIO,
) -> None:
    monkeypatch.setattr(sett, "_resolve_dotenv_paths", list)
    sett.print_dotenv_debug()

    output = log_stream.getvalue()
    assert "No .env file found or resolved" in output
    assert "may only be coming from the OS" in output


def test_dotenv_debug_empty_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    log_stream: StringIO,
) -> None:
    empty_dotenv = tmp_path / ".env"
    empty_dotenv.write_text("")

    monkeypatch.setattr(sett, "_resolve_dotenv_paths", lambda: [empty_dotenv])
    sett.print_dotenv_debug()

    output = log_stream.getvalue()
    assert "file exists but is empty or contains no key-value pairs" in output


def test_dotenv_debug_raises(
    monkeypatch: pytest.MonkeyPatch,
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    _ = debug_logger
    fake_path = Path("/fake/path/.env")
    monkeypatch.setattr(sett, "_resolve_dotenv_paths", lambda: [fake_path])
    monkeypatch.setattr(
        sett,
        "dotenv_values",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(Exception("boom")),
    )

    sett.print_dotenv_debug()

    output = log_stream.getvalue()
    assert "Failed to read .env file" in output
    assert "Exception" in output or "boom" in output


def test_print_dotenv_debug_valid(
    setup_test_root: TestRootSetup,
    load_fresh_settings: LoadSettingsFunc,
    debug_logger: logging.Logger,
    log_stream: StringIO,
) -> None:
    _ = debug_logger
    tmp_path = setup_test_root(env_files=[".env"])
    dotenv = tmp_path / ".env"
    dotenv.write_text(dotenv.read_text() + "FOO=bar\n")

    settings = load_fresh_settings(dotenv_path=dotenv)
    settings.print_dotenv_debug()

    output = log_stream.getvalue()
    assert "Selected .env file" in output
    assert "FOO=bar" in output
