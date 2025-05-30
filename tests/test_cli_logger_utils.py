import logging
import importlib
import time
from pathlib import Path
from logging.handlers import RotatingFileHandler

from myproject.cli_logger_utils import setup_logging, teardown_logger, EnvironmentFilter
from myproject import settings as original_settings


def test_setup_logging_uses_monkeypatched_dir(patched_settings, clean_myproject_logger):
    """setup_logging should attach handlers using patched log directory."""
    log_dir = patched_settings
    setup_logging(reset=True, log_dir=log_dir)
    logger = logging.getLogger("myproject")

    handlers = logger.handlers
    assert len(handlers) == 2, "Expected exactly two handlers (console + file)"
    assert any(
        isinstance(h, logging.StreamHandler) for h in handlers
    ), "Missing StreamHandler"
    assert any(
        isinstance(h, RotatingFileHandler) for h in handlers
    ), "Missing RotatingFileHandler"

    file_handler = next(h for h in handlers if isinstance(h, RotatingFileHandler))
    assert (
        Path(file_handler.baseFilename).parent.resolve() == log_dir.resolve()
    ), "Log file path mismatch"


def test_environment_filter_adds_env(monkeypatch, tmp_path, clean_myproject_logger):
    """EnvironmentFilter should inject 'env' attribute into log records."""
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

    for f in handler.filters:
        f.filter(record)

    assert hasattr(record, "env"), "LogRecord missing 'env' attribute"
    assert (
        record.env == original_settings.get_environment()
    ), "Incorrect 'env' value in LogRecord"


def test_setup_logging_respects_log_level_and_dir(
    tmp_path, monkeypatch, clean_myproject_logger
):
    """setup_logging should apply log level and output directory."""
    monkeypatch.setenv("MYPROJECT_ENV", "UAT")

    setup_logging(log_dir=tmp_path, log_level=logging.WARNING, reset=True)
    logger = logging.getLogger("myproject")

    stream = next(h for h in logger.handlers if isinstance(h, logging.StreamHandler))
    assert stream.level == logging.WARNING, "Console handler has incorrect level"

    fileh = next(h for h in logger.handlers if isinstance(h, RotatingFileHandler))
    assert fileh.level == logging.DEBUG, "File handler should default to DEBUG"
    assert (
        Path(fileh.baseFilename).parent.resolve() == tmp_path.resolve()
    ), "File handler path mismatch"


def test_setup_logging_respects_reset_flag(patched_settings, clean_myproject_logger):
    """setup_logging should clear handlers when reset=True and preserve when reset=False."""
    log_dir = patched_settings
    logger = logging.getLogger("myproject")

    setup_logging(reset=False, log_dir=log_dir)
    count1 = len(logger.handlers)

    setup_logging(reset=False, log_dir=log_dir)
    count2 = len(logger.handlers)
    assert count1 == count2, "Handler count changed with reset=False"

    setup_logging(reset=True, log_dir=log_dir)
    assert len(logger.handlers) == 2, "Expected two handlers after reset=True"

    logger.addHandler(logging.StreamHandler())
    assert len(logger.handlers) == 3, "Failed to manually add third handler"

    setup_logging(reset=True, log_dir=log_dir)
    assert len(logger.handlers) == 2, "Reset=True did not clean up handlers"


def test_teardown_logger_removes_all_handlers(clean_myproject_logger):
    """teardown_logger should remove all attached handlers."""
    logger = logging.getLogger("myproject")
    h1 = logging.StreamHandler()
    h2 = logging.StreamHandler()
    logger.addHandler(h1)
    logger.addHandler(h2)

    assert h1 in logger.handlers and h2 in logger.handlers, "Precondition failed"

    teardown_logger(logger)
    assert logger.handlers == [], "Handlers not cleared after teardown"


def test_rotating_file_log_behavior(monkeypatch, tmp_path, clean_myproject_logger):
    """Rotating file handler should create and rotate log files as expected."""
    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy_test")
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "1024")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "1")
    monkeypatch.delenv("DOTENV_PATH", raising=False)
    monkeypatch.chdir(tmp_path)

    importlib.reload(original_settings)
    importlib.reload(importlib.import_module("myproject.cli_logger_utils"))

    setup_logging(reset=True, log_dir=tmp_path)
    logger = logging.getLogger("myproject")

    # Write enough logs to trigger rollover
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
