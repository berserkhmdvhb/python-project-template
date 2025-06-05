"""Environment and configuration management for myproject.

This module handles all aspects of environment detection, .env loading,
log configuration, and environment-dependent behavior.

Key Features:
- Detects execution context (DEV, UAT, PROD, TEST)
- Loads `.env` files in prioritized order, including overrides and test-specific files
- Provides accessors for current environment, root paths, and logging config
- Supports debug logging of dotenv resolution (`--debug` or `MYPROJECT_DEBUG_ENV_LOAD`)
- Designed to be test-aware (via `PYTEST_CURRENT_TEST`) and patchable (e.g. ROOT_DIR)

Used by CLI entry points, logging system, and core logic to provide a
centralized and testable configuration mechanism.
"""

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

# Set of allowed environment modes for runtime logic
ALLOWED_ENVIRONMENTS: set[str] = {"DEV", "UAT", "PROD"}

# Special override for tests: used in unit test patches
if "MYPROJECT_ROOT_DIR_FOR_TESTS" in os.environ:
    ROOT_DIR = Path(os.environ["MYPROJECT_ROOT_DIR_FOR_TESTS"])


def get_root_dir() -> Path:
    """
    Dynamically return the project root directory (patchable in tests).

    Returns:
        Absolute path to the project's root directory.
    """
    return cast("Path", globals().get("ROOT_DIR", Path(__file__).resolve().parents[2]))


# ---------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------


def is_test_mode() -> bool:
    """
    Return True if running under pytest.

    Uses the PYTEST_CURRENT_TEST env var injected by pytest.
    """
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
    """
    Determine prioritized .env files to load based on context.

    Order of priority:
      1. DOTENV_PATH (explicit override)
      2. .env.override
      3. .env
      4. .env.local
      5. .env.test (only if in test mode)
      6. .env.sample (fallback)
    """
    root_dir = get_root_dir()

    if custom := os.getenv("DOTENV_PATH"):
        custom_path = Path(custom)
        if not custom_path.exists() and (os.getenv("MYPROJECT_DEBUG_ENV_LOAD") == "1"):
            logger.warning(
                "[settings] DOTENV_PATH is set to %s but the file does not exist.",
                custom_path,
            )
        return [custom_path]

    if is_test_mode():
        test_env = get_root_dir() / ".env.test"
        return [test_env] if test_env.exists() else []

    for name in [".env.override", ".env", ".env.local"]:
        path = root_dir / name
        if path.exists():
            return [path]

    sample = root_dir / ".env.sample"
    return [sample] if sample.exists() else []


def load_settings(*, verbose: bool = False) -> list[Path]:
    """
    Load environment variables from prioritized .env files.

    Args:
        verbose: Log loaded .env path if True or if MYPROJECT_DEBUG_ENV_LOAD is set.

    Returns:
        List of loaded .env file paths.
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
    """
    Return MYPROJECT_ENV uppercased (default is DEV).

    Returns:
        One of DEV, UAT, PROD.
    """
    val: str | None = os.getenv(const.ENV_ENVIRONMENT)
    return val.strip().upper() if val else "DEV"


def is_dev() -> bool:
    """Check if environment is DEV."""
    return get_environment() == "DEV"


def is_uat() -> bool:
    """Check if environment is UAT."""
    return get_environment() == "UAT"


def is_prod() -> bool:
    """Check if environment is PROD."""
    return get_environment() == "PROD"


# ---------------------------------------------------------------------
# Logging Config
# ---------------------------------------------------------------------


def get_log_dir() -> Path:
    """
    Return per-environment log directory path.

    Example: logs/DEV/, logs/PROD/
    """
    return const.DEFAULT_LOG_ROOT / get_environment()


def get_log_max_bytes() -> int:
    """
    Return the log file size limit before rotation.

    Returns:
        Max size in bytes, default 1MB.
    """
    return safe_int("MYPROJECT_LOG_MAX_BYTES", 1_000_000)


def get_log_backup_count() -> int:
    """
    Return how many log backups to keep.

    Returns:
        Number of backup files, default 5.
    """
    return safe_int("MYPROJECT_LOG_BACKUP_COUNT", 5)


def get_default_log_level() -> str:
    """
    Return the default logging level from environment.

    Returns:
        Logging level as uppercase string (e.g. INFO, DEBUG).
    """
    val: str | None = os.getenv(const.ENV_LOG_LEVEL)
    return val.strip().upper() if val else "INFO"


# ---------------------------------------------------------------------
# Public API for CLI/debug
# ---------------------------------------------------------------------


def resolve_loaded_dotenv_paths() -> list[Path]:
    """
    Expose resolved .env paths for CLI debug introspection.

    Returns:
        List of paths that would be loaded by `load_settings()`.
    """
    return _resolve_dotenv_paths()


def print_dotenv_debug() -> None:
    """
    Log details of the resolved .env file and its contents.

    Intended for CLI `--debug` output to aid troubleshooting.
    """
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
