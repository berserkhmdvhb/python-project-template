import os
from typing import Final, Literal

# ========================================================================
# General Constants
# ========================================================================

PACKAGE_NAME: Final = "myproject"
DEFAULT_ENCODING: Final = "utf-8"

# ========================================================================
# Exit Codes (conventional Unix-style)
# ========================================================================

EXIT_SUCCESS: Final = 0
EXIT_INVALID_USAGE: Final = 1
# EXIT_NO_RESULTS: Final = 2
EXIT_CANCELLED: Final = 130
EXIT_ARGPARSE_ERROR: Final = 2

# ========================================================================
# Logging Configuration
# ========================================================================

ENV_LOG_LEVEL: Final = "MYPROJECT_LOG_LEVEL"
DEFAULT_LOG_LEVEL: Final = os.getenv(ENV_LOG_LEVEL, "INFO")
LOG_FORMAT: Final = "%(asctime)s — %(levelname)s — %(message)s"

# ========================================================================
# Environment Variable Keys
# ========================================================================

ENV_CACHE_PATH: Final = "MYPROJECT_CACHE"

# ========================================================================
# I/O and Encoding
# ========================================================================

SUPPORTED_FILE_FORMATS: Final = (".json", ".csv", ".txt")
CLI_OUTPUT_ENCODING: Final = "utf-8"

# ========================================================================
# CLI Settings
# ========================================================================

ColorMode = Literal["auto", "always", "never"]
DEFAULT_THRESHOLD: Final[float] = 0.7
