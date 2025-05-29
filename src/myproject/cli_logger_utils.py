import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

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


def setup_logging() -> None:
    """
    Configure logging for both console and file output.
    Includes environment tagging, ensures log folder exists,
    and sets up rotating log files by size.
    Prevents duplicate handlers on repeated setup calls.
    """
    logger = logging.getLogger("myproject")

    if logger.handlers:
        return  # Prevent duplicate setup

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Compute log file path based on environment
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / LOG_FILE_NAME

    formatter = logging.Formatter(LOG_FORMAT)
    env_filter = EnvironmentFilter()

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(env_filter)
    stream_handler.setLevel(logging.DEBUG if settings.IS_DEV else logging.INFO)
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
