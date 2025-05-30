from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv

if TYPE_CHECKING:
    import myproject.constants as const
else:
    import myproject.constants as const

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

ROOT_DIR: Path = Path(__file__).resolve().parents[2]
ALLOWED_ENVIRONMENTS: set[str] = {"DEV", "UAT", "PROD"}
logger = logging.getLogger("myproject")

# ---------------------------------------------------------------------
# Internal Helpers
# ---------------------------------------------------------------------


def _is_test_mode() -> bool:
    """Return True if running under pytest."""
    return "PYTEST_CURRENT_TEST" in os.environ


def _safe_int(env_var: str, default: int) -> int:
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
    if custom := os.getenv("DOTENV_PATH"):
        return [Path(custom)]

    if _is_test_mode():
        test_env = Path.cwd() / ".env.test"
        return [test_env] if test_env.exists() else []

    env_files = [
        ROOT_DIR / name for name in [".env.override", ".env"] if (ROOT_DIR / name).exists()
    ]

    if env_files:
        return env_files

    sample = ROOT_DIR / ".env.sample"
    return [sample] if sample.exists() else []


def load_settings(*, verbose: bool = False) -> list[Path]:
    """
    Load environment variables from prioritized .env files.

    Args:
        verbose: Log loaded .env path if True or MYPROJECT_DEBUG_ENV_LOAD=1.

    Returns:
        List of loaded file paths.
    """
    override = _is_test_mode()
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
    return _safe_int("MYPROJECT_LOG_MAX_BYTES", 1_000_000)


def get_log_backup_count() -> int:
    return _safe_int("MYPROJECT_LOG_BACKUP_COUNT", 5)


def get_default_log_level() -> str:
    val: str | None = os.getenv(const.ENV_LOG_LEVEL)
    return val.strip().upper() if val else "INFO"


# ---------------------------------------------------------------------
# Public API for CLI/debug
# ---------------------------------------------------------------------


def resolve_loaded_dotenv_paths() -> list[Path]:
    """Expose resolved .env paths for CLI debug introspection."""
    return _resolve_dotenv_paths()
