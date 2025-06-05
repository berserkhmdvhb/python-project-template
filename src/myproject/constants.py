"""
Global constants for myproject.

This module centralizes all fixed values used throughout the codebase to
ensure consistency, traceability, and easy configuration.

Sections include:
- Package metadata and defaults
- Exit codes for CLI
- Logging configuration
- CLI-specific settings and literals
- I/O support
- Environment variable names

All constants are `Final` and should not be modified at runtime.
"""

from pathlib import Path
from typing import Final, Literal

# -----------------------------------------------------------------------------
# Package Info
# -----------------------------------------------------------------------------

PACKAGE_NAME: Final = "myproject"
DEFAULT_ENCODING: Final = "utf-8"

# -----------------------------------------------------------------------------
# Exit Codes (Unix style)
# -----------------------------------------------------------------------------

EXIT_SUCCESS: Final = 0
EXIT_INVALID_USAGE: Final = 1
EXIT_ARGPARSE_ERROR: Final = 2
EXIT_CANCELLED: Final = 130
EXIT_ERROR: Final = 3

# -----------------------------------------------------------------------------
# Logging (static pieces)
# -----------------------------------------------------------------------------

# Filename for logging (without full path)
LOG_FILE_NAME: Final = "info.log"

# Format string for logs (used by all handlers)
LOG_FORMAT: Final = "[%(asctime)s] [%(levelname)s] [%(env)s] %(message)s"

# Default root directory for log files
DEFAULT_LOG_ROOT: Final = Path("logs")

# -----------------------------------------------------------------------------
# CLI Settings
# -----------------------------------------------------------------------------

# CLI output color mode
ColorMode = Literal["auto", "always", "never"]

# Default fuzzy match threshold
DEFAULT_THRESHOLD: Final = 0.7

# -----------------------------------------------------------------------------
# I/O and Encoding
# -----------------------------------------------------------------------------

# Supported file extensions for input/output
SUPPORTED_FILE_FORMATS: Final = (".json", ".csv", ".txt")

# Encoding used for CLI stdout/stderr
CLI_OUTPUT_ENCODING: Final = "utf-8"

# -----------------------------------------------------------------------------
# Environment variable names
# -----------------------------------------------------------------------------

# Primary environment selector (DEV/UAT/PROD)
ENV_ENVIRONMENT: Final = "MYPROJECT_ENV"

# Max log file size in bytes
ENV_LOG_MAX_BYTES: Final = "LOG_MAX_BYTES"

# Number of log backups to keep
ENV_LOG_BACKUP_COUNT: Final = "LOG_BACKUP_COUNT"

# Default logging level
ENV_LOG_LEVEL: Final = "MYPROJECT_LOG_LEVEL"
