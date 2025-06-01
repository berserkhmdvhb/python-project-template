import importlib
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Callable

import pytest

import myproject.constants as const
import myproject.settings as sett
from myproject.cli_logger_utils import setup_logging

EXPECTED_LOG_HANDLER_COUNT = 2


def test_setup_logging_creates_log_file(temp_log_dir: Path) -> None:
    """Ensure logging setup creates the correct log file."""
    setup_logging(log_dir=temp_log_dir, log_level=logging.DEBUG, reset=True)
    logger = logging.getLogger("myproject")

    logger.debug("Test debug log")
    logger.info("Test info log")
    logger.error("Test error log")

    log_file = temp_log_dir / const.LOG_FILE_NAME
    assert log_file.exists(), "Log file was not created"

    contents = log_file.read_text(encoding="utf-8")
    assert "Test debug log" in contents
    assert "Test info log" in contents
    assert "Test error log" in contents


def test_console_logging(
    temp_log_dir: Path,
    patch_env: Callable[[str], None],
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Test that console output is working and includes log messages."""
    patch_env("DEV")
    setup_logging(log_dir=temp_log_dir, log_level=logging.DEBUG, reset=True)
    logger = logging.getLogger("myproject")

    logger.info("Visible to console")
    captured = capsys.readouterr()
    output = captured.out or captured.err
    assert "Visible to console" in output


def test_logger_is_idempotent(temp_log_dir: Path) -> None:
    """Ensure setup_logging does not duplicate handlers on repeated calls."""
    logger = logging.getLogger("myproject")

    setup_logging(log_dir=temp_log_dir, log_level=logging.DEBUG, reset=True)
    first_count = len(logger.handlers)

    setup_logging(log_dir=temp_log_dir, log_level=logging.DEBUG, reset=True)
    second_count = len(logger.handlers)

    assert first_count == EXPECTED_LOG_HANDLER_COUNT
    assert second_count == EXPECTED_LOG_HANDLER_COUNT


def test_environment_filter_in_logs(
    temp_log_dir: Path,
    patch_env: Callable[[str], None],
) -> None:
    """Check that the log output includes the correct environment tag."""
    patch_env("TEST")
    setup_logging(log_dir=temp_log_dir, log_level=logging.DEBUG, reset=True)
    logger = logging.getLogger("myproject")

    logger.warning("Env check")

    log_file = temp_log_dir / const.LOG_FILE_NAME
    contents = log_file.read_text(encoding="utf-8")
    assert "Env check" in contents
    assert f"[{sett.get_environment()}]" in contents


def test_log_rotation(
    temp_log_dir: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that log rotation creates backup files when size exceeds maxBytes."""
    monkeypatch.setenv("MYPROJECT_LOG_MAX_BYTES", "50")
    monkeypatch.setenv("MYPROJECT_LOG_BACKUP_COUNT", "1")

    importlib.reload(sett)  # Reload settings to pick up patched environment

    setup_logging(log_dir=temp_log_dir, log_level=logging.DEBUG, reset=True)
    logger = logging.getLogger("myproject")

    file_handler = next(h for h in logger.handlers if isinstance(h, RotatingFileHandler))

    logger.info("Rotating this oversized message: %s", "X" * 500)
    logger.info("Triggering rollover with a second message")
    file_handler.doRollover()
    logger.info("Post-rollover record")

    main_log = temp_log_dir / const.LOG_FILE_NAME
    backups = sorted(temp_log_dir.glob(f"{const.LOG_FILE_NAME}.*"))

    assert main_log.exists(), "Main log file not found"
    assert any(f.suffix == ".1" for f in backups), "No backup file with .1 suffix found"
    assert len(backups) <= sett.get_log_backup_count()
