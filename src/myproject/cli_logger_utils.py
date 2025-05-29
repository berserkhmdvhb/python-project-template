import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional

from myproject import settings
from myproject.constants import (
    LOG_FORMAT,
    LOG_FILE_NAME,
    LOG_MAX_BYTES,
    LOG_BACKUP_COUNT,
)


class EnvironmentFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.env = settings.ENVIRONMENT
        return True


def setup_logging(
    log_dir: Optional[Path] = None,
    log_level: Optional[int] = None,
    reset: bool = False,
    return_handlers: bool = False,
) -> list[logging.Handler] | None:
    """
    Configure logging for both console and file output.
    Includes environment tagging, ensures log folder exists,
    and sets up rotating log files by size.
    Prevents duplicate handlers on repeated setup calls unless reset=True.

    Args:
        log_dir: Optional custom log directory (useful for testing).
        log_level: Optional base log level for console handler.
        reset: If True, forcibly removes existing handlers before setup.
        return_handlers: If True, returns list of handlers added.
    """
    logger = logging.getLogger("myproject")

    if logger.handlers and not reset:
        return None  # Prevent duplicate setup

    if reset:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    resolved_dir = Path(log_dir) if log_dir else Path(settings.LOG_DIR)
    resolved_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = resolved_dir / LOG_FILE_NAME

    formatter = logging.Formatter(LOG_FORMAT)
    env_filter = EnvironmentFilter()

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(env_filter)
    stream_handler.setLevel(
        log_level or (logging.DEBUG if settings.IS_DEV else logging.INFO)
    )
    logger.addHandler(stream_handler)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        filename=log_file_path,
        mode="a",
        maxBytes=LOG_MAX_BYTES,
        backupCount=LOG_BACKUP_COUNT,
        encoding="utf-8",
        delay=True,
    )
    file_handler.setFormatter(formatter)
    file_handler.addFilter(env_filter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    if settings.IS_DEV:
        logger.debug(f"Logging initialized in {resolved_dir} with level DEBUG")

    return [stream_handler, file_handler] if return_handlers else None


def teardown_logger(logger: logging.Logger) -> None:
    """
    Properly flush, close, and remove all handlers from a logger.
    Avoids file lock issues, especially on Windows.
    """
    for handler in logger.handlers[:]:
        try:
            handler.flush()
        except Exception:
            pass
        try:
            handler.close()
        except Exception:
            pass
        logger.removeHandler(handler)
