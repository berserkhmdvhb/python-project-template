import logging
import sys
from typing import Final

from colorama import Fore, Style, init

from myproject.constants import ColorMode

__all__ = [
    "COLOR_CODELINE",
    "COLOR_HEADER",
    "COLOR_SETTINGS",
    "RESET",
    "colorize_line",
    "format_debug",
    "format_error",
    "format_info",
    "format_settings",
    "format_success",
    "format_warning",
    "print_lines",
    "should_use_color",
]

# Initialize colorama (auto-reset styles after each print)
init(autoreset=True)

# Windows: Ensure terminal handles UTF-8 output
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Color constants
COLOR_HEADER: Final = Fore.CYAN
COLOR_CODELINE: Final = Fore.YELLOW
COLOR_ERROR: Final = Fore.RED
COLOR_INFO: Final = Fore.BLUE
COLOR_SUCCESS: Final = Fore.GREEN
COLOR_WARNING: Final = Fore.MAGENTA
COLOR_DEBUG: Final = Fore.LIGHTBLACK_EX
COLOR_SETTINGS: Final = Fore.LIGHTBLACK_EX  # Matches DEBUG color
RESET: Final = Style.RESET_ALL

logger = logging.getLogger("myproject")


def should_use_color(mode: ColorMode) -> bool:
    """Determine whether to use colored output based on the selected mode."""
    if mode == "never":
        return False
    if mode == "always":
        return True
    return sys.stdout.isatty()


def colorize_line(line: str) -> str:
    """Apply appropriate color based on the content of the line."""
    content = line.strip()
    if content.startswith("[RESULT]"):
        return f"{COLOR_HEADER}{line}{RESET}"
    if content.startswith("Input query"):
        return f"{COLOR_CODELINE}{line}{RESET}"
    if content.startswith("Processed value"):
        return f"{COLOR_CODELINE}{line}{RESET}"
    return line


def print_lines(lines: list[str], *, use_color: bool, force_stdout: bool = False) -> None:
    """
    Print or log a list of lines with optional color formatting.

    - If `use_color` is True and `force_stdout` is True, print directly to stdout (with color).
    - Otherwise, log to logger.info (with or without color).
    """
    for line in lines:
        colored = colorize_line(line) if use_color else line
        if use_color and force_stdout:
            print(colored)
        else:
            logger.info(colored)


def format_error(message: str, *, use_color: bool = True) -> str:
    """Format error message with [ERROR] prefix."""
    prefix = f"{COLOR_ERROR}[ERROR]{RESET}" if use_color else "[ERROR]"
    return f"{prefix} {message}"


def format_info(message: str, *, use_color: bool = True) -> str:
    """Format info message with [INFO] prefix."""
    prefix = f"{COLOR_INFO}[INFO]{RESET}" if use_color else "[INFO]"
    return f"{prefix} {message}"


def format_success(message: str, *, use_color: bool = True) -> str:
    """Format success message with [OK] prefix."""
    prefix = f"{COLOR_SUCCESS}[OK]{RESET}" if use_color else "[OK]"
    return f"{prefix} {message}"


def format_warning(message: str, *, use_color: bool = True) -> str:
    """Format warning message with [WARNING] prefix."""
    prefix = f"{COLOR_WARNING}[WARNING]{RESET}" if use_color else "[WARNING]"
    return f"{prefix} {message}"


def format_debug(message: str, *, use_color: bool = True) -> str:
    """Format debug message with [DEBUG] prefix."""
    prefix = f"{COLOR_DEBUG}[DEBUG]{RESET}" if use_color else "[DEBUG]"
    return f"{prefix} {message}"


def format_settings(message: str, *, use_color: bool = True) -> str:
    """Format settings message with [SETTINGS] prefix."""
    prefix = f"{COLOR_SETTINGS}[SETTINGS]{RESET}" if use_color else "[SETTINGS]"
    return f"{prefix} {message}"
