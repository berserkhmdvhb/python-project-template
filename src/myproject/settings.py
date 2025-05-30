import os
from pathlib import Path
from dotenv import load_dotenv
import myproject.constants as const

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]
ALLOWED_ENVIRONMENTS = {"DEV", "UAT", "PROD"}

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------


def is_test_mode() -> bool:
    """Dynamically determine if running in a pytest context (.env.test loading)."""
    return os.environ.get("PYTEST_CURRENT_TEST") is not None


# ---------------------------------------------------------------------
# .env Loading
# ---------------------------------------------------------------------


def _resolve_dotenv_paths() -> list[Path]:
    """Determine which .env files to load based on context and env vars."""
    paths: list[Path] = []

    # 1. Explicit override via DOTENV_PATH
    if "DOTENV_PATH" in os.environ:
        dotenv_path = Path(os.environ["DOTENV_PATH"])
        if dotenv_path.is_file():
            paths.append(dotenv_path)
            return paths  # Explicit override takes precedence

    # 2. Test context — override all others if .env.test is present
    if is_test_mode():
        test_path = Path.cwd() / ".env.test"
        if test_path.is_file():
            paths.append(test_path)
            return paths
        # Fallback if no .env.test
        paths.extend([ROOT_DIR / ".env.override", ROOT_DIR / ".env"])

    # 3. Default runtime context
    else:
        paths.extend([ROOT_DIR / ".env.override", ROOT_DIR / ".env"])

    return paths


def load_settings() -> list[Path]:
    """
    Explicitly load environment variables from prioritized .env files.
    Returns:
        A list of loaded files (empty if none).
    """
    override = is_test_mode()
    loaded: list[Path] = []

    for path in _resolve_dotenv_paths():
        if path.is_file():
            load_dotenv(dotenv_path=path, override=override)
            loaded.append(path)

    if os.getenv("MYPROJECT_DEBUG_ENV_LOAD") == "1":
        print("[settings] Loaded environment variables from:")
        for f in loaded:
            print(f"  - {f}")
            try:
                print(f.read_text())
            except Exception as e:
                print(f"    [Could not read file: {e}]")
        if not loaded:
            print("  (no .env files were found)")

    return loaded


# ---------------------------------------------------------------------
# Environment helpers (Flexible Recognition, Strict Behavior)
# ---------------------------------------------------------------------


def get_environment() -> str:
    """Return MYPROJECT_ENV uppercased, defaulting to DEV if unset."""
    return os.getenv(const.ENV_ENVIRONMENT, "DEV").strip().upper()


def is_dev() -> bool:
    return get_environment() == "DEV"


def is_uat() -> bool:
    return get_environment() == "UAT"


def is_prod() -> bool:
    return get_environment() == "PROD"


# ---------------------------------------------------------------------
# Logging directory
# ---------------------------------------------------------------------


def get_log_dir() -> Path:
    """Determine log directory based on environment."""
    return const.DEFAULT_LOG_ROOT / get_environment()


# ---------------------------------------------------------------------
# Numeric config with fallback
# ---------------------------------------------------------------------


def _safe_int(env_var: str, default: int) -> int:
    val = os.getenv(env_var, "")
    try:
        return int(val)
    except (TypeError, ValueError):
        if val:
            print(
                f"[settings] Warning: Invalid int for {env_var!r} = {val!r}; using default {default}"
            )
        return default


def get_log_max_bytes() -> int:
    return _safe_int("MYPROJECT_LOG_MAX_BYTES", 1_000_000)


def get_log_backup_count() -> int:
    return _safe_int("MYPROJECT_LOG_BACKUP_COUNT", 5)


# ---------------------------------------------------------------------
# Log level
# ---------------------------------------------------------------------


def get_default_log_level() -> str:
    return os.getenv(const.ENV_LOG_LEVEL, "INFO").strip().upper()
