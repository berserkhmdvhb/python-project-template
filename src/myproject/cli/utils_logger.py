from __future__ import annotations

import contextlib
import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path

import myproject.constants as const

# Centralized logger name for the project
LOGGER_NAME = "myproject"

__all__ = [
    "LOGGER_NAME",
    "CustomRotatingFileHandler",
    "EnvironmentFilter",
    "get_default_formatter",
    "setup_logging",
    "teardown_logger",
]


class CustomRotatingFileHandler(RotatingFileHandler):
    """Custom handler with renamed rotated logs: info.log, info_1.log, info_2.log."""

    def rotation_filename(self, default_name: str) -> str:
        """Rename rotated files: info.log.1 → info_1.log"""
        if default_name.endswith(".log"):
            return default_name
        if ".log." in default_name:
            base, suffix = default_name.rsplit(".log.", maxsplit=1)
            return f"{base}_{suffix}.log"
        return default_name

    def do_rollover(self) -> None:
        """Override base class to support custom filename logic."""
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore[assignment]

        if self.backupCount > 0:
            for path in self.get_files_to_delete():
                with contextlib.suppress(OSError):
                    path.unlink()

            for i in range(self.backupCount - 1, 0, -1):
                src = Path(self.rotation_filename(f"{self.baseFilename}.{i}"))
                dst = Path(self.rotation_filename(f"{self.baseFilename}.{i + 1}"))
                if src.exists():
                    src.rename(dst)

            rollover_path = Path(self.rotation_filename(f"{self.baseFilename}.1"))
            current_log = Path(self.baseFilename)
            if current_log.exists():
                current_log.rename(rollover_path)

        if not self.delay:
            self.stream = self._open()

    def get_files_to_delete(self) -> list[Path]:
        """Return rotated log files to delete to enforce backup count."""
        base_path = Path(self.baseFilename)
        prefix = base_path.stem
        ext = base_path.suffix
        pattern = re.compile(rf"^{re.escape(prefix)}_(\d+){re.escape(ext)}$")

        return sorted(
            [p for p in base_path.parent.iterdir() if pattern.match(p.name)],
            key=lambda p: p.stat().st_mtime,
        )[: -self.backupCount]


class EnvironmentFilter(logging.Filter):
    """Injects the current environment (e.g., DEV, UAT, PROD) into log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        import myproject.settings as sett

        record.env = sett.get_environment()
        return True


def ensure_filter(handler: logging.Handler, filt: logging.Filter) -> None:
    """Ensure the filter is applied only once to a handler."""
    if not any(isinstance(existing, type(filt)) for existing in handler.filters):
        handler.addFilter(filt)


def get_default_formatter() -> logging.Formatter:
    """Returns the default CLI-style formatter for log messages."""
    return logging.Formatter(const.LOG_FORMAT)


def setup_logging(
    log_dir: Path | None = None,
    log_level: int | None = None,
    *,
    reset: bool = False,
    return_handlers: bool = False,
) -> list[logging.Handler] | None:
    """
    Set up logging to both console and file.

    Args:
        log_dir: Optional directory to store the log file.
        log_level: Optional log level for console output.
        reset: If True, clears existing handlers before reconfiguring.
        return_handlers: If True, returns the list of attached handlers.

    Returns:
        List of handlers if `return_handlers` is True; otherwise None.
    """
    import myproject.settings as sett

    logger = logging.getLogger(LOGGER_NAME)

    if logger.hasHandlers() and not reset:
        return None

    if reset:
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    sett.load_settings()
    resolved_dir = log_dir or sett.get_log_dir()
    resolved_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = resolved_dir / const.LOG_FILE_NAME

    formatter = get_default_formatter()
    env_filter = EnvironmentFilter()

    # Console handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    ensure_filter(stream_handler, env_filter)
    stream_handler.setLevel(
        log_level if log_level is not None else (logging.DEBUG if sett.is_dev() else logging.INFO)
    )
    logger.addHandler(stream_handler)

    # Custom rotating file handler
    custom_file_handler = CustomRotatingFileHandler(
        filename=str(log_file_path),
        mode="a",
        maxBytes=sett.get_log_max_bytes(),
        backupCount=sett.get_log_backup_count(),
        encoding="utf-8",
        delay=True,
    )
    custom_file_handler.setFormatter(formatter)
    ensure_filter(custom_file_handler, env_filter)
    custom_file_handler.setLevel(logging.DEBUG)
    logger.addHandler(custom_file_handler)

    if sett.is_dev():
        logger.debug("Logging initialized in %s with level DEBUG", resolved_dir)

    return [stream_handler, custom_file_handler] if return_handlers else None


def teardown_logger(logger: logging.Logger | None = None) -> None:
    """
    Cleanly detach all handlers from the logger.

    Args:
        logger: Target logger to tear down. Defaults to project logger.
    """
    logger = logger or logging.getLogger(LOGGER_NAME)
    for handler in logger.handlers[:]:
        with contextlib.suppress(Exception):
            handler.flush()
        with contextlib.suppress(Exception):
            handler.close()
        logger.removeHandler(handler)
