from __future__ import annotations

import importlib
import logging
import os
import subprocess
import sys
import tempfile
from collections.abc import Generator
from io import StringIO
from pathlib import Path
from types import ModuleType
from typing import TYPE_CHECKING, Callable, Final

import pytest

from myproject.cli.utils_logger import teardown_logger

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

LOGGER_NAME: Final = "myproject"

# ---------------------------------------------------------------------
# Auto-clean logger before and after each test
# ---------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clean_myproject_logger() -> Generator[None, None, None]:
    logger = logging.getLogger(LOGGER_NAME)
    teardown_logger(logger)
    yield
    teardown_logger(logger)


# ---------------------------------------------------------------------
# Clear relevant MYPROJECT_* environment variables
# ---------------------------------------------------------------------


@pytest.fixture(autouse=True)
def clear_myproject_env(monkeypatch: MonkeyPatch) -> None:
    vars_to_clear = [
        "MYPROJECT_ENV",
        "MYPROJECT_LOG_MAX_BYTES",
        "MYPROJECT_LOG_BACKUP_COUNT",
        "MYPROJECT_LOG_LEVEL",
        "MYPROJECT_DEBUG_ENV_LOAD",
    ]
    if not os.environ.get("_MYPROJECT_KEEP_DOTENV_PATH"):
        vars_to_clear.append("DOTENV_PATH")

    for var in vars_to_clear:
        monkeypatch.delenv(var, raising=False)

    # Force default value to avoid shell override
    monkeypatch.setenv("MYPROJECT_DEBUG_ENV_LOAD", "0")


# ---------------------------------------------------------------------
# Reload settings fresh from source
# ---------------------------------------------------------------------


@pytest.fixture
def load_fresh_settings(
    monkeypatch: MonkeyPatch,
) -> Callable[[Path | None], ModuleType]:
    def _load(dotenv_path: Path | None = None) -> ModuleType:
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy")
        if dotenv_path:
            monkeypatch.setenv("DOTENV_PATH", str(dotenv_path.resolve()))

        from myproject import settings

        importlib.reload(settings)
        settings.load_settings()
        return settings

    return _load


# ---------------------------------------------------------------------
# Temporary log directory fixture
# ---------------------------------------------------------------------


@pytest.fixture
def temp_log_dir(monkeypatch: MonkeyPatch) -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir).resolve()
        monkeypatch.setenv("MYPROJECT_ENV", "TEST")

        import myproject.cli.utils_logger as clu
        import myproject.settings as sett

        importlib.reload(sett)
        importlib.reload(clu)

        monkeypatch.setattr("myproject.settings.get_log_dir", lambda: tmp_path)
        yield tmp_path
        teardown_logger(logging.getLogger(LOGGER_NAME))


# ---------------------------------------------------------------------
# Patched logging config for DEV
# ---------------------------------------------------------------------


@pytest.fixture
def patched_settings(monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
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
    def _patch(env_name: str) -> None:
        monkeypatch.setenv("MYPROJECT_ENV", env_name)

    return _patch


# ---------------------------------------------------------------------
# Log stream capture
# ---------------------------------------------------------------------


@pytest.fixture
def log_stream() -> Generator[StringIO, None, None]:
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
# CLI subprocess runner
# ---------------------------------------------------------------------


@pytest.fixture
def run_cli(tmp_path: Path) -> Callable[..., tuple[str, str, int]]:
    def _run(*args: str, env: dict[str, str] | None = None) -> tuple[str, str, int]:
        cmd = [sys.executable, "-m", "myproject", *args]

        # Enforce no color unless explicitly overridden
        if not any(arg.startswith("--color") or arg == "--color" for arg in args):
            cmd.append("--color=never")

        # Enforce non-verbose mode unless explicitly overridden
        if "--verbose" not in cmd:
            # CLI defaults to quiet mode, so we simulate non-verbose explicitly
            pass  # No flag needed since --verbose is opt-in

        full_env = {
            **os.environ,
            "MYPROJECT_LOG_MAX_BYTES": "10000",
            "MYPROJECT_LOG_BACKUP_COUNT": "2",
            "MYPROJECT_DEBUG_ENV_LOAD": "0",
            **(env or {}),
        }

        if "PYTHONPATH" not in full_env:
            full_env["PYTHONPATH"] = str(Path.cwd())

        if "--dotenv-path" in args:
            i = args.index("--dotenv-path")
            if i + 1 < len(args):
                full_env["DOTENV_PATH"] = str(Path(args[i + 1]).resolve())
        else:
            dummy_env = (tmp_path / ".env").resolve()
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