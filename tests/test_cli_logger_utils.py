import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from myproject.cli_logger_utils import setup_logging, teardown_logger


def test_setup_logging_uses_monkeypatched_dir(patched_settings):
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


def test_environment_filter_injected_in_log_record(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)

    import myproject.settings as settings
    import myproject.cli_logger_utils as cli_logger_utils

    logger = logging.getLogger("test_env_filter")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    handler = logging.StreamHandler()
    handler.addFilter(cli_logger_utils.EnvironmentFilter())
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
        record.env == settings.get_environment()
    ), "Incorrect 'env' value in LogRecord"

    teardown_logger(logger)


def test_setup_logging_respects_log_level_and_dir(tmp_path, monkeypatch):
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

    teardown_logger(logger)


def test_reset_option_controls_duplication(patched_settings):
    log_dir = patched_settings
    logger = logging.getLogger("myproject")

    setup_logging(reset=False, log_dir=log_dir)
    count1 = len(logger.handlers)

    setup_logging(reset=False, log_dir=log_dir)
    count2 = len(logger.handlers)
    assert count1 == count2, "Handler count changed with reset=False"

    setup_logging(reset=True, log_dir=log_dir)
    count3 = len(logger.handlers)
    assert count3 == 2, "Expected two handlers after reset=True"

    logger.addHandler(logging.StreamHandler())
    assert len(logger.handlers) == 3, "Failed to manually add third handler"

    setup_logging(reset=True, log_dir=log_dir)
    assert len(logger.handlers) == 2, "Reset=True did not clean up handlers"

    teardown_logger(logger)


def test_teardown_logger_clears_all():
    logger = logging.getLogger("myproject")
    h1 = logging.StreamHandler()
    h2 = logging.StreamHandler()
    logger.addHandler(h1)
    logger.addHandler(h2)

    assert h1 in logger.handlers and h2 in logger.handlers, "Precondition failed"

    teardown_logger(logger)
    assert logger.handlers == [], "Handlers not cleared after teardown"


def test_file_rotation_parametrized(monkeypatch, tmp_path):
    import importlib
    import logging
    import time
    from myproject import settings as original_settings
    from myproject import cli_logger_utils as logger_utils

    monkeypatch.setenv("PYTEST_CURRENT_TEST", "dummy_test")
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "1024")  # 1 KB
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "1")
    monkeypatch.delenv("DOTENV_PATH", raising=False)
    monkeypatch.chdir(tmp_path)

    importlib.reload(original_settings)
    importlib.reload(logger_utils)

    logger_utils.setup_logging(reset=True, log_dir=tmp_path)
    logger = logging.getLogger("myproject")

    # Write initial log entries
    message = "x" * 300
    for _ in range(5):
        logger.debug(message)

    # Manually trigger rollover
    for handler in logger.handlers:
        if isinstance(handler, logging.handlers.RotatingFileHandler):
            handler.doRollover()

    # Write another log line to recreate the main log file
    logger.debug("Triggering creation of new log file after rollover")

    # Flush and wait
    for handler in logger.handlers:
        handler.flush()
    time.sleep(0.2)

    all_logs = list(tmp_path.glob("*"))
    main = [f for f in all_logs if f.name.endswith(".log")]
    backups = [f for f in all_logs if ".log." in f.name]

    assert main, f"Main log file missing in: {all_logs}"
    assert backups, f"Backup log file not created in: {all_logs}"

    logger_utils.teardown_logger(logger)
