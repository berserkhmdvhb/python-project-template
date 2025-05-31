import importlib
import logging
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from myproject import settings as original_settings
from myproject.cli_logger_utils import (
    EnvironmentFilter,
    setup_logging,
    teardown_logger,
)

EXPECTED_HANDLER_COUNT = 2
EXTRA_HANDLER_COUNT = 3


def test_setup_logging_uses_monkeypatched_dir(patched_settings: Path) -> None:
    log_dir = patched_settings
    setup_logging(reset=True, log_dir=log_dir)
    logger = logging.getLogger("myproject")

    handlers = logger.handlers
    assert len(handlers) == EXPECTED_HANDLER_COUNT
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)
    assert any(isinstance(h, RotatingFileHandler) for h in handlers)

    file_handler = next(h for h in handlers if isinstance(h, RotatingFileHandler))
    assert Path(file_handler.baseFilename).parent.resolve() == log_dir.resolve()


def test_setup_logging_returns_handlers(tmp_path: Path) -> None:
    handlers = setup_logging(log_dir=tmp_path, reset=True, return_handlers=True)
    assert handlers is not None
    assert any(isinstance(h, logging.StreamHandler) for h in handlers)
    assert any(isinstance(h, RotatingFileHandler) for h in handlers)


def test_setup_logging_skips_if_handlers_exist_and_reset_false(tmp_path: Path) -> None:
    logger = logging.getLogger("myproject")
    teardown_logger(logger)
    logger.addHandler(logging.StreamHandler())
    result = setup_logging(log_dir=tmp_path, reset=False)
    assert result is None


def test_environment_filter_adds_env(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    logger = logging.getLogger("test_env_filter")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.addFilter(EnvironmentFilter())
    logger.addHandler(handler)

    record = logger.makeRecord(
        name="test_env_filter",
        level=logging.DEBUG,
        fn="test",
        lno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )

    logger.handle(record)

    assert hasattr(record, "env")
    assert record.env == original_settings.get_environment()


def test_setup_logging_respects_log_level_and_dir(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    monkeypatch.setenv("MYPROJECT_ENV", "UAT")

    setup_logging(log_dir=tmp_path, log_level=logging.WARNING, reset=True)
    logger = logging.getLogger("myproject")

    stream = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
    assert stream.level == logging.WARNING

    fileh = next(h for h in logger.handlers if isinstance(h, RotatingFileHandler))
    assert fileh.level == logging.DEBUG
    assert Path(fileh.baseFilename).parent.resolve() == tmp_path.resolve()


def test_setup_logging_respects_reset_flag(patched_settings: Path) -> None:
    log_dir = patched_settings
    logger = logging.getLogger("myproject")

    setup_logging(reset=False, log_dir=log_dir)
    count1 = len(logger.handlers)

    setup_logging(reset=False, log_dir=log_dir)
    count2 = len(logger.handlers)
    assert count1 == count2

    setup_logging(reset=True, log_dir=log_dir)
    assert len(logger.handlers) == EXPECTED_HANDLER_COUNT

    logger.addHandler(logging.StreamHandler())
    assert len(logger.handlers) == EXTRA_HANDLER_COUNT

    setup_logging(reset=True, log_dir=log_dir)
    assert len(logger.handlers) == EXPECTED_HANDLER_COUNT


def test_teardown_logger_removes_all_handlers() -> None:
    logger = logging.getLogger("myproject")
    h1 = logging.StreamHandler()
    h2 = logging.StreamHandler()
    logger.addHandler(h1)
    logger.addHandler(h2)

    assert h1 in logger.handlers
    assert h2 in logger.handlers

    teardown_logger(logger)
    assert logger.handlers == []


def test_teardown_logger_with_default_logger() -> None:
    logger = logging.getLogger("myproject")
    logger.addHandler(logging.StreamHandler())
    teardown_logger()
    assert not logger.handlers


def test_rotating_file_log_behavior(
    monkeypatch: MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy_test")
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "1024")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "1")
    monkeypatch.delenv("DOTENV_PATH", raising=False)
    monkeypatch.chdir(tmp_path)

    importlib.reload(original_settings)
    importlib.reload(importlib.import_module("myproject.cli_logger_utils"))

    setup_logging(reset=True, log_dir=tmp_path)
    logger = logging.getLogger("myproject")

    message = "x" * 300
    for _ in range(5):
        logger.debug(message)

    for handler in logger.handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.doRollover()

    logger.debug("Triggering creation of new log file after rollover")

    for handler in logger.handlers:
        handler.flush()

    time.sleep(0.2)

    all_logs = list(tmp_path.glob("*"))
    main = [f for f in all_logs if f.name.endswith(".log")]
    backups = [f for f in all_logs if ".log." in f.name]

    assert main, f"Main log file missing in: {all_logs}"
    assert backups, f"Backup log file not created in: {all_logs}"
