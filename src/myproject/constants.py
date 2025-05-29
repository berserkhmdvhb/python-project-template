import os
from typing import Final, Literal

# =============================================================================
# Package Info
# =============================================================================

PACKAGE_NAME: Final = "myproject"
DEFAULT_ENCODING: Final = "utf-8"

# =============================================================================
# Exit Codes (Unix-style)
# =============================================================================

EXIT_SUCCESS: Final = 0
EXIT_INVALID_USAGE: Final = 1
EXIT_ARGPARSE_ERROR: Final = 2
EXIT_CANCELLED: Final = 130

# =============================================================================
# Logging Configuration
# =============================================================================

ENV_LOG_LEVEL: Final = "MYPROJECT_LOG_LEVEL"
DEFAULT_LOG_LEVEL: Final = os.getenv(ENV_LOG_LEVEL, "INFO")
LOG_FORMAT: Final = "[%(asctime)s] [%(levelname)s] [%(env)s] %(message)s"

LOG_DIR: Final = "logs"
LOG_FILE_NAME: Final = "myproject.log"
LOG_FILE_PATH: Final = os.path.join(LOG_DIR, LOG_FILE_NAME)

# Rotating log settings (read from .env or use defaults)
LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 1_000_000))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

# =============================================================================
# Environment Variables
# =============================================================================

ENV_CACHE_PATH: Final = "MYPROJECT_CACHE"

# =============================================================================
# I/O and Encoding
# =============================================================================

SUPPORTED_FILE_FORMATS: Final = (".json", ".csv", ".txt")
CLI_OUTPUT_ENCODING: Final = "utf-8"

# =============================================================================
# CLI Settings
# =============================================================================

ColorMode = Literal["auto", "always", "never"]
DEFAULT_THRESHOLD: Final = 0.7
