from __future__ import annotations

import importlib
import logging
import time
from collections.abc import Callable
from io import StringIO
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
    import pytest
    from _pytest.monkeypatch import MonkeyPatch

LOGGER_NAME = "myproject"


def get_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def test_setup_logging_creates_handlers(setup_test_root: Callable[[], Path]) -> None:
    log_path = setup_test_root()
    handlers = setup_logging(log_dir=log_path, reset=True, return_handlers=True)
    assert handlers
    assert any(isinstance(h, StreamHandler) for h in handlers)
    assert any(isinstance(h, RotatingFileHandler) for h in handlers)


def test_handlers_write_to_correct_log_dir(setup_test_root: Callable[[], Path]) -> None:
    log_path = setup_test_root()
    handlers = setup_logging(log_dir=log_path, reset=True, return_handlers=True)
    assert handlers
    file_handler = next(h for h in handlers if isinstance(h, RotatingFileHandler))
    log_dir = Path(file_handler.baseFilename).resolve().parent
    assert log_dir == log_path.resolve()


def test_setup_logging_skips_if_not_reset(setup_test_root: Path) -> None:
    logger = get_logger()
    teardown_logger(logger)
    logger.addHandler(StreamHandler())
    result = setup_logging(log_dir=setup_test_root, reset=False)
    assert result is None
    assert len(logger.handlers) == 1


def test_environment_filter_adds_env(
    monkeypatch: MonkeyPatch,
    setup_test_root: Callable[[], Path],
    capsys: pytest.CaptureFixture[str],
) -> None:
    tmp_path = setup_test_root()
    monkeypatch.chdir(tmp_path)

    import myproject.settings as sett

    logger = logging.getLogger("test_env_logger")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    stream = StringIO()
    handler = StreamHandler(stream)
    handler.addFilter(EnvironmentFilter())
    logger.addHandler(handler)

    logger.info("Env filtered log message")
    handler.flush()

    output = stream.getvalue()
    assert "Env filtered log message" in output

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

    out, err = capsys.readouterr()
    assert "testing" not in out + err


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


def test_rotating_log_rollover(
    monkeypatch: MonkeyPatch,
    setup_test_root: Callable[[], Path],
    capsys: pytest.CaptureFixture[str],
) -> None:
    max_log_backups = 2
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy_test")
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "512")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", str(max_log_backups))
    monkeypatch.delenv("DOTENV_PATH", raising=False)

    test_root = setup_test_root()
    monkeypatch.chdir(test_root)

    import myproject.cli.utils_logger as clu
    import myproject.settings as sett

    importlib.reload(sett)
    importlib.reload(clu)

    setup_logging(log_dir=test_root, reset=True)
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

    captured = capsys.readouterr()
    assert "trigger new file" in captured.out or captured.err

    all_logs = list(test_root.glob("*"))
    primary_logs = [f for f in all_logs if f.name == const.LOG_FILE_NAME]
    backups = [
        f
        for f in all_logs
        if f.name.startswith("info_") and f.suffix == ".log" and f.name != const.LOG_FILE_NAME
    ]

    assert primary_logs, f"Expected primary log file not found in {all_logs}"
    assert backups, f"No backup log file found in {all_logs}"
    assert any("1" in f.name or "2" in f.name for f in backups), (
        f"Expected versioned backups: {backups}"
    )
    assert len(backups) <= max_log_backups, (
        f"Expected at most {max_log_backups} backups, got {len(backups)}: {backups}"
    )

    unexpected_files = [
        f
        for f in all_logs
        if f.suffix == ".log" and f.name not in {const.LOG_FILE_NAME, *[b.name for b in backups]}
    ]
    assert not unexpected_files, f"Unexpected log files found: {unexpected_files}"


def test_teardown_logger_removes_handlers() -> None:
    logger = get_logger()
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
    logger = get_logger()

    handler = SafeDummyHandler()
    logger.addHandler(handler)

    monkeypatch.setattr(handler, "flush", lambda: None)
    monkeypatch.setattr(handler, "close", lambda: None)

    called = {"removed": False}

    def fake_remove_handler(h: logging.Handler) -> None:
        if h is handler:
            called["removed"] = True
        original_remove_handler(h)

    original_remove_handler = logger.removeHandler
    monkeypatch.setattr(logger, "removeHandler", fake_remove_handler)

    teardown_logger(logger)
    assert called["removed"]
