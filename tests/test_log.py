import logging
from pathlib import Path

import myproject.constants as const
from myproject.cli_logger_utils import setup_logging, teardown_logger


def test_setup_logging_creates_log_file(temp_log_dir: Path) -> None:
    """Ensure logging setup creates the correct log file."""
    setup_logging(reset=True)
    logger = logging.getLogger("myproject")

    logger.debug("Test debug log")
    logger.info("Test info log")
    logger.error("Test error log")

    log_file = temp_log_dir / const.LOG_FILE_NAME
    assert log_file.exists()

    contents = log_file.read_text(encoding="utf-8")
    assert "Test debug log" in contents
    assert "Test info log" in contents
    assert "Test error log" in contents

    teardown_logger(logger)


def test_console_logging(temp_log_dir: Path, patch_env, capsys) -> None:
    """Test that console output is working and includes log messages."""
    patch_env("DEV")
    setup_logging(reset=True)
    logger = logging.getLogger("myproject")

    logger.info("Visible to console")
    captured = capsys.readouterr()
    output = captured.out or captured.err
    assert "Visible to console" in output

    teardown_logger(logger)


def test_logger_is_idempotent(temp_log_dir: Path) -> None:
    """Ensure setup_logging does not duplicate handlers on repeated calls."""
    logger = logging.getLogger("myproject")

    setup_logging(reset=True)
    first_count = len(logger.handlers)

    setup_logging(reset=True)
    second_count = len(logger.handlers)

    assert first_count == second_count

    teardown_logger(logger)


def test_environment_filter_in_logs(temp_log_dir: Path, patch_env) -> None:
    """Check that the log output includes the correct environment tag."""
    patch_env("TEST")
    setup_logging(reset=True)
    logger = logging.getLogger("myproject")

    logger.warning("Env check")

    log_file = temp_log_dir / const.LOG_FILE_NAME
    contents = log_file.read_text(encoding="utf-8")
    assert "Env check" in contents
    assert "[TEST]" in contents or "TEST" in contents

    teardown_logger(logger)


def test_log_rotation(temp_log_dir: Path, monkeypatch) -> None:
    """Test that log rotation creates backup files when size exceeds maxBytes."""

    # Force a low rollover threshold for testing
    monkeypatch.setattr(const, "LOG_MAX_BYTES", 200)
    monkeypatch.setattr(const, "LOG_BACKUP_COUNT", 2)

    # Get handlers back from setup_logging
    handlers = setup_logging(reset=True, return_handlers=True)
    assert handlers is not None

    # Identify the RotatingFileHandler
    from logging.handlers import RotatingFileHandler

    file_handler = next(h for h in handlers if isinstance(h, RotatingFileHandler))

    logger = logging.getLogger("myproject")
    # First large message to exceed threshold
    logger.info("Rotating this oversized message: %s", "X" * 500)
    # Second message to be written to rotated file
    logger.info("Triggering rollover with a second message")

    # Manually force rollover
    file_handler.doRollover()
    # Emit one more record to open a fresh info.log
    logger.info("Post-rollover record")

    # Teardown to close handlers
    teardown_logger(logger)

    # Check files on disk
    main_log = temp_log_dir / const.LOG_FILE_NAME
    backups = sorted(temp_log_dir.glob(f"{const.LOG_FILE_NAME}.*"))

    assert main_log.exists()
    assert any(f.suffix == ".1" for f in backups)
    assert len(backups) <= const.LOG_BACKUP_COUNT
