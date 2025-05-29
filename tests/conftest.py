import os
import sys
import subprocess
import logging
import tempfile
from io import StringIO
from pathlib import Path
from collections.abc import Generator
from typing import Callable

import pytest

from myproject.cli_logger_utils import teardown_logger


@pytest.fixture(autouse=True)
def clean_myproject_logger() -> Generator[None, None, None]:
    """
    Ensure each test starts with a clean logger for 'myproject'.
    Uses teardown_logger to close/remove handlers after each test,
    and restores any original handlers.
    """
    logger = logging.getLogger("myproject")
    original_handlers = logger.handlers[:]
    logger.handlers.clear()
    yield
    teardown_logger(logger)
    for handler in original_handlers:
        logger.addHandler(handler)


@pytest.fixture
def temp_log_dir(monkeypatch) -> Generator[Path, None, None]:
    """
    Patch LOG_DIR with a temporary path and yield it as a Path.
    Ensures isolation and avoids writing logs to real user directories.
    """
    from myproject import settings

    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.setattr(settings, "LOG_DIR", tmpdir)
        yield Path(tmpdir)
        teardown_logger(logging.getLogger("myproject"))


@pytest.fixture
def patch_env(monkeypatch):
    """
    Patch the ENVIRONMENT value dynamically.
    Usage: patch_env("TEST") inside your test.
    """
    from myproject import settings

    def _patch(env_name: str):
        monkeypatch.setattr(settings, "ENVIRONMENT", env_name)

    return _patch


@pytest.fixture
def log_stream() -> Generator[StringIO, None, None]:
    """
    Capture logs from the 'myproject' logger into a StringIO buffer.
    Useful for asserting console output in tests.
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


@pytest.fixture
def run_cli() -> Callable[..., tuple[str, str, int]]:
    """
    Run the CLI (`python -m myproject`) and return (stdout, stderr, returncode).
    Automatically appends --color=never, defaults MYPROJECT_ENV to DEV,
    but an `env` dict override may be passed.
    Usage examples:
        out, err, code = run_cli("--query", "hello")
        out, err, code = run_cli("--query", "hello", env={"MYPROJECT_ENV":"UAT"})
    """

    def _run(*args: str, env: dict[str, str] | None = None) -> tuple[str, str, int]:
        cmd = [sys.executable, "-m", "myproject", *args]
        if "--color=never" not in cmd:
            cmd.append("--color=never")

        full_env = os.environ.copy()
        full_env.setdefault("MYPROJECT_ENV", "DEV")
        if env:
            full_env.update(env)

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
