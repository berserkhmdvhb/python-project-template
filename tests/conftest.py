import sys
import os
import subprocess
import logging
import tempfile
import importlib
from io import StringIO
from pathlib import Path
from collections.abc import Generator
from typing import Callable

import pytest
from myproject.cli_logger_utils import teardown_logger


# --- Auto-clean logger before and after each test ---
@pytest.fixture(autouse=True)
def clean_myproject_logger() -> Generator[None, None, None]:
    """
    Fully tears down the 'myproject' logger before and after each test
    to avoid handler duplication or stale state.
    """
    logger = logging.getLogger("myproject")
    teardown_logger(logger)
    yield
    teardown_logger(logger)


# --- Clear relevant MYPROJECT_* environment variables ---
@pytest.fixture(autouse=True)
def clear_myproject_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Clears all MYPROJECT_* environment variables used in configuration.
    Automatically applied before each test but also usable explicitly.
    Skips DOTENV_PATH if _MYPROJECT_KEEP_DOTENV_PATH is set.
    """
    vars_to_clear = [
        "MYPROJECT_ENV",
        "MYPROJECT_LOG_MAX_BYTES",
        "MYPROJECT_LOG_BACKUP_COUNT",
        "MYPROJECT_LOG_LEVEL",
    ]

    if not os.environ.get("_MYPROJECT_KEEP_DOTENV_PATH"):
        vars_to_clear.append("DOTENV_PATH")

    for var in vars_to_clear:
        monkeypatch.delenv(var, raising=False)


# --- Helper to reload settings fresh from source, with optional dotenv path ---
@pytest.fixture
def load_fresh_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[Path | None], object]:
    """
    Returns a function to reload and return fresh myproject.settings.
    Optionally sets a custom DOTENV_PATH before loading.
    Useful in tests that dynamically create .env files.
    """

    def _load(dotenv_path: Path | None = None) -> object:
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")

        if dotenv_path:
            monkeypatch.setenv("DOTENV_PATH", str(dotenv_path))

        import myproject.settings as settings
        import importlib

        importlib.reload(settings)
        settings.load_settings()
        return settings

    return _load


# --- Temporary log directory fixture ---
@pytest.fixture
def temp_log_dir(monkeypatch) -> Generator[Path, None, None]:
    """
    Creates a temporary log directory and patches get_log_dir() to use it.
    Does NOT patch log-related config values like max bytes or backup count.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        monkeypatch.setenv("MYPROJECT_ENV", "TEST")

        import myproject.settings as sett
        import myproject.cli_logger_utils as clu

        importlib.reload(sett)
        importlib.reload(clu)

        monkeypatch.setattr("myproject.settings.get_log_dir", lambda: tmp_path)

        yield tmp_path

        teardown_logger(logging.getLogger("myproject"))


# --- Fully patched settings for logging ---
@pytest.fixture
def patched_settings(monkeypatch, tmp_path) -> Path:
    """
    Patch environment and settings related to logging.
    Reloads both settings and logger modules.
    """
    monkeypatch.setenv("MYPROJECT_ENV", "DEV")
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "50")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "1")

    import myproject.settings as sett
    import myproject.cli_logger_utils as clu

    importlib.reload(sett)
    importlib.reload(clu)

    monkeypatch.setattr("myproject.settings.get_log_dir", lambda: tmp_path)

    return tmp_path


# --- Patch just the environment name ---
@pytest.fixture
def patch_env(monkeypatch: pytest.MonkeyPatch) -> Callable[[str], None]:
    """
    Fixture returning a helper function to patch MYPROJECT_ENV.
    """

    def _patch(env_name: str) -> None:
        monkeypatch.setenv("MYPROJECT_ENV", env_name)

    return _patch


# --- Capture logs in a StringIO stream ---
@pytest.fixture
def log_stream() -> Generator[StringIO, None, None]:
    """
    Attach a temporary stream handler to capture log output.
    """
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger = logging.getLogger("myproject")
    logger.addHandler(handler)

    yield stream

    logger.removeHandler(handler)
    handler.close()


# --- CLI subprocess runner ---
@pytest.fixture
def run_cli(tmp_path: Path) -> Callable[..., tuple[str, str, int]]:
    """
    Returns a function to invoke the CLI via subprocess with controlled env vars.
    Automatically injects a dummy .env file if none is specified.
    """

    def _run(*args: str, env: dict[str, str] | None = None) -> tuple[str, str, int]:
        cmd = [sys.executable, "-m", "myproject", *args]
        if "--color=never" not in cmd:
            cmd.append("--color=never")

        full_env = {
            "PYTHONPATH": str(Path.cwd()),
            "MYPROJECT_LOG_MAX_BYTES": "10000",
            "MYPROJECT_LOG_BACKUP_COUNT": "2",
            **(env or {}),
        }

        # Apply DOTENV_PATH explicitly if provided in args
        if "--dotenv-path" in args:
            i = args.index("--dotenv-path")
            if i + 1 < len(args):
                full_env["DOTENV_PATH"] = str(args[i + 1])
        else:
            dummy_env = tmp_path / ".env"
            dummy_env.write_text("")
            full_env["DOTENV_PATH"] = str(dummy_env)

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=full_env,
            check=False,
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode

    return _run
