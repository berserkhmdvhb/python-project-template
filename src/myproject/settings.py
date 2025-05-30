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
# .env Loading (Best Practice)
# ---------------------------------------------------------------------


def _resolve_dotenv_paths() -> list[Path]:
    """Determine prioritized .env files to load."""
    paths: list[Path] = []

    # 1. Explicit override via DOTENV_PATH (test or manual debug)
    custom_path = os.getenv("DOTENV_PATH")
    if custom_path:
        paths.append(Path(custom_path))
        return paths

    # 2. Test mode: load .env.test if it exists
    if is_test_mode():
        test_path = Path.cwd() / ".env.test"
        if test_path.is_file():
            paths.append(test_path)
            return paths

    # 3. Normal runtime
    candidates = [".env.override", ".env"]
    found_any = False
    for candidate in candidates:
        full_path = ROOT_DIR / candidate
        if full_path.exists():
            paths.append(full_path)
            found_any = True

    # 4. Fallback to .env.sample only if nothing else exists
    if not found_any:
        sample_path = ROOT_DIR / ".env.sample"
        if sample_path.exists():
            paths.append(sample_path)

    return paths


def load_settings() -> list[Path]:
    """
    Explicitly load environment variables from prioritized .env files.
    Logs which file was loaded for transparency.
    Returns:
        List of loaded .env file paths.
    """
    override = is_test_mode()
    loaded: list[Path] = []

    for path in _resolve_dotenv_paths():
        if path.is_file():
            load_dotenv(dotenv_path=path, override=override)
            print(f"[settings] Loaded environment variables from: {path}")
            loaded.append(path)
            break  # Load only the first matching file

    if not loaded:
        print("[settings] No .env file loaded — falling back to system env or defaults.")

    return loaded


# ---------------------------------------------------------------------
# Environment helpers
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