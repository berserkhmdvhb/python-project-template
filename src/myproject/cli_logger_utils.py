import logging
import os
from myproject import settings
from myproject.constants import LOG_FILE_PATH, LOG_FORMAT


class EnvironmentFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.env = settings.ENVIRONMENT
        return True


def setup_logging() -> None:
    """
    Configure logging for both console and file output.
    Includes environment tagging and ensures log folder exists.
    Prevents duplicate handlers on repeated setup calls.
    """
    logger = logging.getLogger("myproject")

    if logger.handlers:
        return  # Prevent duplicate setup

    logger.setLevel(logging.DEBUG)  # Capture everything; filtering is handler-specific
    logger.propagate = False

    # Ensure log directory exists
    os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

    formatter = logging.Formatter(LOG_FORMAT)
    env_filter = EnvironmentFilter()

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(env_filter)
    stream_handler.setLevel(logging.DEBUG if settings.IS_DEV else logging.INFO)
    logger.addHandler(stream_handler)

    # File handler — always logs all levels
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.addFilter(env_filter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
