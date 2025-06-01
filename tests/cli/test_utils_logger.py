from __future__ import annotations

import importlib
import logging
import time
from logging import StreamHandler
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import TYPE_CHECKING

import myproject.constants as const
from myproject.cli.utils_logger import (
    EnvironmentFilter,
    setup_logging,
    teardown_logger,
)
from tests.utils import SafeDummyHandler

if TYPE_CHECKING:
    from _pytest.monkeypatch import MonkeyPatch

LOGGER_NAME = "myproject"


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def test_setup_logging_creates_handlers(tmp_path: Path) -> None:
    handlers = setup_logging(log_dir=tmp_path, reset=True, return_handlers=True)
    assert handlers is not None
    assert any(isinstance(h, StreamHandler) for h in handlers)
    assert any(isinstance(h, RotatingFileHandler) for h in handlers)


def test_handlers_write_to_correct_log_dir(tmp_path: Path) -> None:
    handlers = setup_logging(log_dir=tmp_path, reset=True, return_handlers=True)
    assert handlers is not None
    file_handler = next(h for h in handlers if isinstance(h, RotatingFileHandler))
    log_dir = Path(file_handler.baseFilename).resolve().parent
    assert log_dir == tmp_path.resolve()


def test_setup_logging_skips_if_not_reset(tmp_path: Path) -> None:
    logger = get_logger()
    teardown_logger(logger)
    logger.addHandler(StreamHandler())
    result = setup_logging(log_dir=tmp_path, reset=False)
    assert result is None


def test_environment_filter_adds_env(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    import myproject.settings as sett

    logger = logging.getLogger("test_env_logger")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = StreamHandler()
    handler.addFilter(EnvironmentFilter())
    logger.addHandler(handler)

    record = logger.makeRecord(
        name="test_env_logger",
        level=logging.INFO,
        fn="dummy.py",
        lno=1,
        msg="testing",
        args=(),
        exc_info=None,
    )

    assert EnvironmentFilter().filter(record)
    assert hasattr(record, "env")
    assert record.env == sett.get_environment()


def test_teardown_logger_removes_all_handlers() -> None:
    logger = get_logger()
    logger.addHandler(StreamHandler())
    assert logger.handlers
    teardown_logger(logger)
    assert not logger.handlers


def test_teardown_logger_default() -> None:
    logger = get_logger()
    logger.addHandler(StreamHandler())
    teardown_logger()
    assert not logger.handlers


def test_rotating_log_rollover(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy_test")
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "512")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "1")
    monkeypatch.delenv("DOTENV_PATH", raising=False)
    monkeypatch.chdir(tmp_path)

    import myproject.settings as sett

    importlib.reload(sett)
    importlib.reload(importlib.import_module("myproject.cli.utils_logger"))

    setup_logging(log_dir=tmp_path, reset=True)
    logger = get_logger()

    msg = "x" * 300
    for _ in range(5):
        logger.debug(msg)

    for handler in logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.doRollover()
            handler.flush()

    logger.debug("trigger new file")
    time.sleep(0.1)

    all_logs = list(tmp_path.glob("*"))
    primary_logs = [f for f in all_logs if f.name == const.LOG_FILE_NAME]
    backups = [f for f in all_logs if f.name.startswith(const.LOG_FILE_NAME + ".")]

    assert primary_logs, f"Expected primary log file not found in {all_logs}"
    assert backups, f"No backup log file found in {all_logs}"


def test_teardown_logger_removes_handlers() -> None:
    logger = logging.getLogger("myproject")
    dummy1 = SafeDummyHandler()
    dummy2 = SafeDummyHandler()
    logger.addHandler(dummy1)
    logger.addHandler(dummy2)

    assert dummy1 in logger.handlers
    assert dummy2 in logger.handlers

    teardown_logger(logger)

    assert dummy1 not in logger.handlers
    assert dummy2 not in logger.handlers
    assert not logger.handlers


def test_teardown_logger_covers_remove_handler(monkeypatch: MonkeyPatch) -> None:
    """Ensure teardown_logger calls removeHandler and it is covered."""
    logger = logging.getLogger(LOGGER_NAME)

    # Add a dummy handler
    handler = SafeDummyHandler()
    logger.addHandler(handler)

    # Patch flush and close to ensure they don't interfere
    monkeypatch.setattr(handler, "flush", lambda: None)
    monkeypatch.setattr(handler, "close", lambda: None)

    # Track if removeHandler is called
    called = {"removed": False}

    def fake_remove_handler(h: logging.Handler) -> None:
        if h is handler:
            called["removed"] = True
        original_remove_handler(h)

    original_remove_handler = logger.removeHandler
    monkeypatch.setattr(logger, "removeHandler", fake_remove_handler)

    teardown_logger(logger)

    assert called["removed"]
