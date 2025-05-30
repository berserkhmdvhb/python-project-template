from typing import Final, Literal
from pathlib import Path

# -----------------------------------------------------------------------------
# Package Info
# -----------------------------------------------------------------------------
PACKAGE_NAME: Final = "myproject"
DEFAULT_ENCODING: Final = "utf-8"

# -----------------------------------------------------------------------------
# Exit Codes (Unix‐style)
# -----------------------------------------------------------------------------
EXIT_SUCCESS: Final = 0
EXIT_INVALID_USAGE: Final = 1
EXIT_ARGPARSE_ERROR: Final = 2
EXIT_CANCELLED: Final = 130

# -----------------------------------------------------------------------------
# Logging (static pieces)
# -----------------------------------------------------------------------------
# This is just the filename (not full path)
LOG_FILE_NAME: Final = "info.log"
# Format string for all handlers
LOG_FORMAT: Final = "[%(asctime)s] [%(levelname)s] [%(env)s] %(message)s"
# Default Root Directory
DEFAULT_LOG_ROOT: Final = Path("logs")

# -----------------------------------------------------------------------------
# CLI Settings
# -----------------------------------------------------------------------------
ColorMode = Literal["auto", "always", "never"]
DEFAULT_THRESHOLD: Final = 0.7

# -----------------------------------------------------------------------------
# I/O and Encoding
# -----------------------------------------------------------------------------
SUPPORTED_FILE_FORMATS: Final = (".json", ".csv", ".txt")
CLI_OUTPUT_ENCODING: Final = "utf-8"

# -----------------------------------------------------------------------------
# Environment variable names
# -----------------------------------------------------------------------------
ENV_ENVIRONMENT: Final = "MYPROJECT_ENV"
ENV_LOG_MAX_BYTES: Final = "LOG_MAX_BYTES"
ENV_LOG_BACKUP_COUNT: Final = "LOG_BACKUP_COUNT"
ENV_LOG_LEVEL: Final = "MYPROJECT_LOG_LEVEL"
