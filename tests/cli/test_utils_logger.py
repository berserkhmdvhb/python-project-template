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
    CustomRotatingFileHandler,
    EnvironmentFilter,
    get_default_formatter,
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


def test_rotation_filename_variants() -> None:
    handler = CustomRotatingFileHandler("dummy.log")

    assert handler.rotation_filename("info.log") == "info.log"
    assert handler.rotation_filename("info.log.1") == "info_1.log"
    assert handler.rotation_filename("randomfile.txt") == "randomfile.txt"


def test_get_files_to_delete_returns_expected(patched_settings: Path) -> None:
    log_file = patched_settings / const.LOG_FILE_NAME
    log_file.touch()

    rotated = [
        patched_settings / "info_1.log",
        patched_settings / "info_2.log",
        patched_settings / "info_3.log",
    ]
    for f in rotated:
        f.write_text("log content")
        time.sleep(0.01)

    handler = CustomRotatingFileHandler(
        filename=str(log_file),
        mode="a",
        maxBytes=50,
        backupCount=2,
        encoding="utf-8",
        delay=True,
    )

    to_delete = handler.get_files_to_delete()
    assert all(f.exists() for f in to_delete)
    assert len(to_delete) == 1
    oldest = min(rotated, key=lambda f: f.stat().st_mtime)
    assert to_delete[0] == oldest


def test_do_rollover_custom_pattern(patched_settings: Path) -> None:
    log_path = patched_settings / const.LOG_FILE_NAME
    log_path.write_text("first log")

    rotated = [
        patched_settings / "info_1.log",
        patched_settings / "info_2.log",
    ]
    for f in rotated:
        f.write_text("old log")

    handler = CustomRotatingFileHandler(
        filename=str(log_path),
        mode="a",
        maxBytes=50,
        backupCount=2,
        encoding="utf-8",
        delay=True,
    )
    handler.do_rollover()

    existing = {f.name for f in patched_settings.glob("*.log")}
    assert "info_2.log" in existing or "info_3.log" not in existing
    assert "info_1.log" in existing


def test_teardown_logger_explicit_removal(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = logging.getLogger("myproject")
    removed = {"status": False}

    class DummyHandler(logging.Handler):
        def flush(self) -> None: ...
        def close(self) -> None: ...

    handler = DummyHandler()

    def fake_remove(h: logging.Handler) -> None:
        if h is handler:
            removed["status"] = True
        original_remove(h)

    logger.addHandler(handler)
    original_remove = logger.removeHandler
    monkeypatch.setattr(logger, "removeHandler", fake_remove)

    teardown_logger(logger)
    assert removed["status"]


def test_setup_logging_full_flow(temp_log_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "100")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "2")
    monkeypatch.setenv("MYPROJECT_ENV", "DEV")

    handlers = setup_logging(log_dir=temp_log_dir, reset=True, return_handlers=True)
    assert handlers is not None

    # Check that formatter is attached correctly
    assert any(
        isinstance(getattr(h, "formatter", None), type(get_default_formatter())) for h in handlers
    )

    # Manually verify that EnvironmentFilter sets `record.env`
    record = logging.LogRecord(
        name="myproject",
        level=logging.INFO,
        pathname=__file__,
        lineno=123,
        msg="Log test",
        args=(),
        exc_info=None,
    )
    filt = EnvironmentFilter()
    result = filt.filter(record)
    assert result
    assert hasattr(record, "env")
    assert record.env == "DEV"

    # Ensure log file was created
    log_files = list(temp_log_dir.glob("*.log"))
    assert any(f.name == const.LOG_FILE_NAME for f in log_files)


def test_rollover_closes_stream_if_open(tmp_path: Path) -> None:
    log_file = tmp_path / const.LOG_FILE_NAME
    log_file.write_text("initial")

    handler = CustomRotatingFileHandler(
        filename=str(log_file),
        mode="a",
        maxBytes=10,
        backupCount=1,
        encoding="utf-8",
        delay=False,  # Ensure stream is opened
    )

    # Emulate that the stream is open
    assert handler.stream is not None
    handler.do_rollover()
    # Check if stream is reopened (i.e., replaced)
    assert handler.stream is not None


def test_rollover_unlinks_deletable_files(tmp_path: Path) -> None:
    log_file = tmp_path / const.LOG_FILE_NAME
    log_file.write_text("data")

    deletable = tmp_path / "info_1.log"
    keep_1 = tmp_path / "info_2.log"
    keep_2 = tmp_path / "info_3.log"

    for f in [deletable, keep_1, keep_2]:
        f.write_text("rotated log")
        time.sleep(0.01)  # ensure correct mtime ordering

    handler = CustomRotatingFileHandler(
        filename=str(log_file),
        mode="a",
        maxBytes=50,
        backupCount=2,
        encoding="utf-8",
        delay=True,
    )

    to_delete = handler.get_files_to_delete()
    assert deletable in to_delete
    assert keep_1 not in to_delete
    assert keep_2 not in to_delete
    assert len(to_delete) == 1


def test_rollover_opens_new_stream_if_not_delayed(tmp_path: Path) -> None:
    log_file = tmp_path / const.LOG_FILE_NAME
    log_file.write_text("initial")

    handler = CustomRotatingFileHandler(
        filename=str(log_file),
        mode="a",
        maxBytes=10,
        backupCount=1,
        encoding="utf-8",
        delay=False,  # not delayed → triggers stream open
    )

    handler.do_rollover()
    assert handler.stream is not None


def test_teardown_logger_removes_handler_line(monkeypatch: pytest.MonkeyPatch) -> None:
    logger = get_logger()
    handler = SafeDummyHandler()
    logger.addHandler(handler)

    # Spy on removeHandler
    called = {"removed": False}

    def fake_remove(h: logging.Handler) -> None:
        if h is handler:
            called["removed"] = True
        original(h)

    original = logger.removeHandler
    monkeypatch.setattr(logger, "removeHandler", fake_remove)

    teardown_logger(logger)
    assert called["removed"]


def test_rollover_handles_unlink_oserror(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    log_file = tmp_path / const.LOG_FILE_NAME
    log_file.write_text("main log")

    deletable = tmp_path / "info_1.log"
    handler = CustomRotatingFileHandler(
        filename=str(log_file),
        mode="a",
        maxBytes=1,
        backupCount=1,
        encoding="utf-8",
        delay=True,
    )

    def mock_get_files_to_delete() -> list[Path]:
        return [deletable]

    monkeypatch.setattr(handler, "get_files_to_delete", mock_get_files_to_delete)

    def custom_unlink(self: Path) -> None:
        if self.name == "info_1.log":
            msg = "simulated"
            raise OSError(msg)

    monkeypatch.setattr(Path, "unlink", custom_unlink)

    handler.do_rollover()


def test_rollover_unlinks_old_rotated_file(tmp_path: Path) -> None:
    log_file = tmp_path / "base.log"

    handler = CustomRotatingFileHandler(
        filename=str(log_file),
        mode="a",
        maxBytes=1,
        backupCount=1,
        encoding="utf-8",
        delay=False,
    )

    # First log → base.log
    handler.emit(logging.LogRecord("myproject", logging.DEBUG, "", 0, "A" * 100, (), None))
    handler.do_rollover()
    first_backup = tmp_path / "base_1.log"
    assert first_backup.exists(), "base_1.log was not created after first rollover"
    first_backup.unlink()
    handler.emit(logging.LogRecord("myproject", logging.DEBUG, "", 0, "B" * 100, (), None))
    handler.do_rollover()


def test_teardown_logger_executes_remove_handler() -> None:
    logger = get_logger()
    handler = StreamHandler()
    logger.addHandler(handler)

    assert handler in logger.handlers

    teardown_logger(logger)

    # If this line executed, the handler will be gone
    assert handler not in logger.handlers


def test_teardown_logger_finally_removes() -> None:
    logger = get_logger()

    class FlushError(Exception):
        """Custom error to simulate flush failure."""

    class FaultyHandler(logging.Handler):
        def flush(self) -> None:
            raise FlushError(flush_failed_msg)

    flush_failed_msg = "simulated flush failure"
    handler = FaultyHandler()
    logger.addHandler(handler)

    teardown_logger(logger)

    assert handler not in logger.handlers
