"""
Global pytest fixtures for MyProject test suite.

This file defines reusable fixtures to:
- Control and isolate environment variable state
- Setup temporary directories and test `.env` files
- Reload settings cleanly between tests
- Manage log capture and rotation configuration
- Provide CLI subprocess testing tools

All fixtures are designed for use in a multi-env configuration test setup.
"""

from __future__ import annotations

import importlib
import logging
import os
import sys
import tempfile
from collections.abc import Callable, Generator
from io import StringIO
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Final

import pytest

from myproject.cli.utils_logger import teardown_logger
from tests.utils import invoke_cli

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

    from myproject.types import LoadSettingsFunc, TestRootSetup

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

LOGGER_NAME: Final = "myproject"

# ---------------------------------------------------------------------
# Auto-clean logger before and after each test
# ---------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_myproject_logger() -> Generator[None, None, None]:
    """
    Clears all logging handlers for 'myproject' before and after each test
    to avoid log pollution between tests.
    """
    logger = logging.getLogger(LOGGER_NAME)
    teardown_logger(logger)
    yield
    teardown_logger(logger)


# ---------------------------------------------------------------------
# Clear relevant MYPROJECT_* environment variables and DOTENV_PATH
# ---------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_myproject_env(monkeypatch: MonkeyPatch) -> None:
    """
    Automatically clears all MYPROJECT-related env vars before each test
    to ensure test isolation.
    """
    vars_to_clear = [
        "MYPROJECT_ENV",
        "MYPROJECT_LOG_MAX_BYTES",
        "MYPROJECT_LOG_BACKUP_COUNT",
        "MYPROJECT_LOG_LEVEL",
        "MYPROJECT_DEBUG_ENV_LOAD",
        "DOTENV_PATH",
    ]
    for var in vars_to_clear:
        monkeypatch.delenv(var, raising=False)

    # Prevent verbose debug output unless test sets it
    monkeypatch.setenv("MYPROJECT_DEBUG_ENV_LOAD", "0")


# ---------------------------------------------------------------------
# Reload settings fresh from source
# ---------------------------------------------------------------------


@pytest.fixture
def load_fresh_settings(monkeypatch: MonkeyPatch) -> LoadSettingsFunc:
    """
    Reload settings in 'test mode', i.e. PYTEST_CURRENT_TEST is set.
    Simulates default test behavior with `.env.test`.
    """

    def _load(dotenv_path: Path | None = None, root_dir: Path | None = None) -> ModuleType:
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
        if dotenv_path:
            monkeypatch.setenv("DOTENV_PATH", str(dotenv_path.resolve()))
        else:
            monkeypatch.delenv("DOTENV_PATH", raising=False)
        if root_dir:
            monkeypatch.setenv("MYPROJECT_ROOT_DIR_FOR_TESTS", str(root_dir.resolve()))
        else:
            monkeypatch.delenv("MYPROJECT_ROOT_DIR_FOR_TESTS", raising=False)

        import myproject.settings as sett

        importlib.reload(sett)
        sett.load_settings()
        return sett

    return _load


@pytest.fixture
def load_fresh_settings_no_test_mode(monkeypatch: MonkeyPatch) -> LoadSettingsFunc:
    """
    Reload settings with PYTEST_CURRENT_TEST unset.
    Simulates runtime behavior to test fallback paths and non-test execution.
    """

    def _load(dotenv_path: Path | None = None, root_dir: Path | None = None) -> ModuleType:
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
        os.environ.pop("PYTEST_CURRENT_TEST", None)

        if dotenv_path:
            monkeypatch.setenv("DOTENV_PATH", str(dotenv_path.resolve()))
        else:
            monkeypatch.delenv("DOTENV_PATH", raising=False)
        if root_dir:
            monkeypatch.setenv("MYPROJECT_ROOT_DIR_FOR_TESTS", str(root_dir.resolve()))
        else:
            monkeypatch.delenv("MYPROJECT_ROOT_DIR_FOR_TESTS", raising=False)

        import myproject.settings as sett

        importlib.reload(sett)
        sett.load_settings()
        return sett

    return _load


# ---------------------------------------------------------------------
# Reusable test root setup for env and path-based tests
# ---------------------------------------------------------------------


@pytest.fixture
def setup_test_root(tmp_path: Path, monkeypatch: MonkeyPatch) -> TestRootSetup:
    """
    Sets up a temporary root with optional `.env*` files and env vars.

    - Overrides get_root_dir to use tmp_path
    - Creates .env files if requested
    - Sets up test environment and reloads settings
    """

    def _setup(
        *, env_files: list[str] | None = None, env_vars: dict[str, str] | None = None
    ) -> Path:
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")

        # Patch get_root_dir() to point to tmp_path
        monkeypatch.setattr("myproject.settings.get_root_dir", lambda: tmp_path)

        if env_vars:
            for k, v in env_vars.items():
                monkeypatch.setenv(k, v)

        if env_files:
            for fname in env_files:
                # Generate env content dynamically based on filename
                (tmp_path / fname).write_text(f"MYPROJECT_ENV={Path(fname).stem.upper()}")

        # Remove cached settings module to force clean reload
        sys.modules.pop("myproject.settings", None)

        import myproject.settings as sett

        importlib.reload(sett)
        sett.load_settings()

        return tmp_path

    return _setup


# ---------------------------------------------------------------------
# Temporary log directory fixture
# ---------------------------------------------------------------------


@pytest.fixture
def temp_log_dir(monkeypatch: MonkeyPatch) -> Generator[Path, None, None]:
    """
    Provides a temporary directory for log file output and injects it
    into logger config via monkeypatch.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir).resolve()
        monkeypatch.setenv("MYPROJECT_ENV", "TEST")

        import myproject.cli.utils_logger as clu
        import myproject.settings as sett

        importlib.reload(sett)
        importlib.reload(clu)

        # Patch log directory to use temporary location
        monkeypatch.setattr("myproject.settings.get_log_dir", lambda: tmp_path)
        yield tmp_path

        teardown_logger(logging.getLogger(LOGGER_NAME))


# ---------------------------------------------------------------------
# Patched logging config for DEV
# ---------------------------------------------------------------------


@pytest.fixture
def patched_settings(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
    """
    Sets DEV-mode environment with custom log settings and returns log path.
    Useful for testing rotating file handler setup.
    """
    monkeypatch.setenv("MYPROJECT_ENV", "DEV")
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "50")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "1")

    import myproject.cli.utils_logger as clu
    import myproject.settings as sett

    importlib.reload(sett)
    importlib.reload(clu)

    monkeypatch.setattr("myproject.settings.get_log_dir", lambda: tmp_path.resolve())
    return tmp_path.resolve()


# ---------------------------------------------------------------------
# Patch only the environment name
# ---------------------------------------------------------------------


@pytest.fixture
def patch_env(monkeypatch: MonkeyPatch) -> Callable[[str], None]:
    """
    Fixture that returns a callable to patch the current environment.
    Usage: patch_env("uat")
    """

    def _patch(env_name: str) -> None:
        monkeypatch.setenv("MYPROJECT_ENV", env_name)

    return _patch


# ---------------------------------------------------------------------
# Log stream capture
# ---------------------------------------------------------------------


@pytest.fixture
def log_stream() -> Generator[StringIO, None, None]:
    """
    Captures log output to a StringIO stream for log inspection in tests.
    """
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger(LOGGER_NAME)
    logger.addHandler(handler)
    yield stream

    logger.removeHandler(handler)
    handler.close()


# ---------------------------------------------------------------------
# Debug-level logger fixture (for dotenv debug / diagnostics)
# ---------------------------------------------------------------------


@pytest.fixture
def debug_logger(log_stream: StringIO) -> logging.Logger:
    """
    Configures a DEBUG logger and attaches it to the provided stream.
    Useful for diagnosing dotenv behavior.
    """
    teardown_logger()
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


# ---------------------------------------------------------------------
# CLI subprocess runner (wraps invoke_cli)
# ---------------------------------------------------------------------


@pytest.fixture
def run_cli(tmp_path: Path) -> Callable[..., tuple[str, str, int]]:
    """
    Returns a CLI runner for integration tests via subprocess.
    Wraps the invoke_cli helper with tmp_path isolation.
    """

    def _run(*args: str, env: dict[str, str] | None = None) -> tuple[str, str, int]:
        return invoke_cli(args, tmp_path=tmp_path, env=env)

    return _run
