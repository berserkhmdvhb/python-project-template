from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import cast

from dotenv import dotenv_values, load_dotenv

import myproject.constants as const

# ---------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------

logger = logging.getLogger("myproject")

# ---------------------------------------------------------------------
# Constants and Accessors
# ---------------------------------------------------------------------

ALLOWED_ENVIRONMENTS: set[str] = {"DEV", "UAT", "PROD"}

if "MYPROJECT_ROOT_DIR_FOR_TESTS" in os.environ:
    ROOT_DIR = Path(os.environ["MYPROJECT_ROOT_DIR_FOR_TESTS"])


def get_root_dir() -> Path:
    """Dynamically return the project root directory (patchable in tests)."""
    return cast("Path", globals().get("ROOT_DIR", Path(__file__).resolve().parents[2]))


# ---------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------


def is_test_mode() -> bool:
    """Return True if running under pytest."""
    return "PYTEST_CURRENT_TEST" in os.environ


# ---------------------------------------------------------------------
# Public Utilities
# ---------------------------------------------------------------------


def safe_int(env_var: str, default: int) -> int:
    """
    Safely retrieve an integer from an environment variable, falling back to a default.

    Args:
        env_var: Name of the environment variable.
        default: Default value to use if missing or invalid.

    Returns:
        Integer from the environment or default.
    """
    val: str | None = os.getenv(env_var)
    if val is not None:
        try:
            return int(val)
        except ValueError:
            logger.warning(
                "[settings] Invalid int for %r = %r; using default %d",
                env_var,
                val,
                default,
            )
    return default


# ---------------------------------------------------------------------
# .env Loading
# ---------------------------------------------------------------------


def _resolve_dotenv_paths() -> list[Path]:
    """Determine prioritized .env files to load based on context."""
    root_dir = get_root_dir()

    # Priority 1: DOTENV_PATH (explicit custom)
    if custom := os.getenv("DOTENV_PATH"):
        custom_path = Path(custom)
        if not custom_path.exists() and (os.getenv("MYPROJECT_DEBUG_ENV_LOAD") == "1"):
            logger.warning(
                "[settings] DOTENV_PATH is set to %s but the file does not exist.",
                custom_path,
            )
        return [custom_path]

    # Priority 5: .env.test (overrides others when in test mode)
    if is_test_mode():
        test_env = get_root_dir() / ".env.test"
        return [test_env] if test_env.exists() else []

    # Priorities 2-4: .env.override > .env > .env.local
    for name in [".env.override", ".env", ".env.local"]:
        path = root_dir / name
        if path.exists():
            return [path]

    # Priority 6: fallback sample
    sample = root_dir / ".env.sample"
    return [sample] if sample.exists() else []


def load_settings(*, verbose: bool = False) -> list[Path]:
    """
    Load environment variables from prioritized .env files.

    Args:
        verbose: Log loaded .env path if True or MYPROJECT_DEBUG_ENV_LOAD=1.

    Returns:
        List of loaded file paths.
    """
    override = is_test_mode()
    loaded: list[Path] = []

    for path in _resolve_dotenv_paths():
        if path.is_file():
            load_dotenv(dotenv_path=path, override=override)
            if verbose or os.getenv("MYPROJECT_DEBUG_ENV_LOAD") == "1":
                logger.info("[settings] Loaded environment variables from: %s", path)
            loaded.append(path)
            break

    if not loaded and (verbose or os.getenv("MYPROJECT_DEBUG_ENV_LOAD") == "1"):
        logger.info(
            "[settings] No .env file loaded — falling back to system env or defaults.",
        )

    return loaded


# ---------------------------------------------------------------------
# Environment Accessors
# ---------------------------------------------------------------------


def get_environment() -> str:
    """Return MYPROJECT_ENV uppercased (defaults to DEV)."""
    val: str | None = os.getenv(const.ENV_ENVIRONMENT)
    return val.strip().upper() if val else "DEV"


def is_dev() -> bool:
    return get_environment() == "DEV"


def is_uat() -> bool:
    return get_environment() == "UAT"


def is_prod() -> bool:
    return get_environment() == "PROD"


# ---------------------------------------------------------------------
# Logging Config
# ---------------------------------------------------------------------


def get_log_dir() -> Path:
    """Return per-environment log directory path."""
    return const.DEFAULT_LOG_ROOT / get_environment()


def get_log_max_bytes() -> int:
    return safe_int("MYPROJECT_LOG_MAX_BYTES", 1_000_000)


def get_log_backup_count() -> int:
    return safe_int("MYPROJECT_LOG_BACKUP_COUNT", 5)


def get_default_log_level() -> str:
    val: str | None = os.getenv(const.ENV_LOG_LEVEL)
    return val.strip().upper() if val else "INFO"


# ---------------------------------------------------------------------
# Public API for CLI/debug
# ---------------------------------------------------------------------


def resolve_loaded_dotenv_paths() -> list[Path]:
    """Expose resolved .env paths for CLI debug introspection."""
    return _resolve_dotenv_paths()


def print_dotenv_debug() -> None:
    """Log details of the resolved .env file and its contents."""
    paths = _resolve_dotenv_paths()

    if not paths:
        logger.info("[dotenv-debug] No .env file found or resolved.")
        logger.info("[dotenv-debug] Environment variables may only be coming from the OS.")
        return

    path = paths[0]
    logger.info("[dotenv-debug] Selected .env file: %s", path)

    try:
        values = dotenv_values(dotenv_path=path)

        if not values:
            logger.info(
                "[dotenv-debug] .env file exists but is empty or contains no key-value pairs."
            )
            return

        logger.info("[dotenv-debug] Loaded key-value pairs:")
        for key, value in values.items():
            logger.info("[dotenv-debug]   %s=%s", key, value)

    except Exception:
        logger.exception("[dotenv-debug] Failed to read .env file")
