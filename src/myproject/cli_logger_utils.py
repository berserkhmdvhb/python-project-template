import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

import myproject.constants as const

# Use a central constant for the logger name
LOGGER_NAME = "myproject"


class EnvironmentFilter(logging.Filter):
    """Injects the current environment (e.g., DEV, UAT, PROD) into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        import myproject.settings as sett

        record.env = sett.get_environment()
        return True


def setup_logging(
    log_dir: Path | None = None,
    log_level: int | None = None,
    reset: bool = False,
    return_handlers: bool = False,
) -> list[logging.Handler] | None:
    """
    Configure logging for both console and file output.
    Includes environment tagging, rotating file output, and safe reinitialization.

    Args:
        log_dir: Optional override for log directory (useful in tests).
        log_level: Console log level override (e.g., logging.DEBUG).
        reset: If True, removes existing handlers before setting up.
        return_handlers: If True, returns the list of created handlers.

    Returns:
        A list of handlers if `return_handlers` is True; otherwise None.
    """
    import myproject.settings as sett

    logger = logging.getLogger(LOGGER_NAME)

    if logger.hasHandlers() and not reset:
        return None  # Avoid duplicate handlers

    if reset:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # Ensure settings are loaded before logging setup
    sett.load_settings()

    resolved_dir = log_dir or sett.get_log_dir()
    resolved_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = resolved_dir / const.LOG_FILE_NAME

    formatter = logging.Formatter(const.LOG_FORMAT)
    env_filter = EnvironmentFilter()

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    if not any(isinstance(f, EnvironmentFilter) for f in stream_handler.filters):
        stream_handler.addFilter(env_filter)
    stream_handler.setLevel(
        log_level or (logging.DEBUG if sett.is_dev() else logging.INFO)
    )
    logger.addHandler(stream_handler)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        filename=log_file_path,
        mode="a",
        maxBytes=sett.get_log_max_bytes(),
        backupCount=sett.get_log_backup_count(),
        encoding="utf-8",
        delay=True,
    )
    file_handler.setFormatter(formatter)
    if not any(isinstance(f, EnvironmentFilter) for f in file_handler.filters):
        file_handler.addFilter(env_filter)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    if sett.is_dev():
        logger.debug(f"Logging initialized in {resolved_dir} with level DEBUG")

    return [stream_handler, file_handler] if return_handlers else None


def teardown_logger(logger: logging.Logger) -> None:
    """
    Cleanly remove all handlers from a logger to avoid duplication or file lock issues.

    Args:
        logger: The logger instance to clean up.
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


__all__: list[str] = ["setup_logging", "teardown_logger", "EnvironmentFilter"]
