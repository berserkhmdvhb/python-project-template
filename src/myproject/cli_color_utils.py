import sys
from typing import Final

from colorama import Fore, Style, init

from .constants import ColorMode

# Initialize colorama with auto-reset for cleaner output
init(autoreset=True)

# Apply UTF-8 encoding fix for Windows terminals (Python ≥3.7)
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Color definitions
COLOR_HEADER: Final = Fore.CYAN
COLOR_CODELINE: Final = Fore.YELLOW
COLOR_ERROR: Final = Fore.RED
COLOR_INFO: Final = Fore.BLUE
COLOR_SUCCESS: Final = Fore.GREEN
COLOR_WARNING: Final = Fore.MAGENTA
COLOR_DEBUG: Final = Fore.LIGHTBLACK_EX
RESET: Final = Style.RESET_ALL


def should_use_color(mode: ColorMode) -> bool:
    if mode == "never":
        return False
    if mode == "always":
        return True
    return sys.stdout.isatty()


def colorize_line(line: str) -> str:
    if line.startswith("[RESULT]"):
        return f"{COLOR_HEADER}{line}{RESET}"
    if line.strip().startswith("Input query"):
        return f"{COLOR_CODELINE}{line}{RESET}"
    if line.strip().startswith("Processed value"):
        return f"{COLOR_CODELINE}{line}{RESET}"
    return line


def print_lines(lines: list[str], use_color: bool) -> None:
    for line in lines:
        print(colorize_line(line) if use_color else line)


def format_error(message: str, use_color: bool = True) -> str:
    prefix = f"{COLOR_ERROR}[ERROR]{RESET}" if use_color else "[ERROR]"
    return f"{prefix} {message}"


def format_info(message: str, use_color: bool = True) -> str:
    prefix = f"{COLOR_INFO}[INFO]{RESET}" if use_color else "[INFO]"
    return f"{prefix} {message}"


def format_success(message: str, use_color: bool = True) -> str:
    prefix = f"{COLOR_SUCCESS}[OK]{RESET}" if use_color else "[OK]"
    return f"{prefix} {message}"


def format_warning(message: str, use_color: bool = True) -> str:
    prefix = f"{COLOR_WARNING}[WARNING]{RESET}" if use_color else "[WARNING]"
    return f"{prefix} {message}"


def format_debug(message: str, use_color: bool = True) -> str:
    prefix = f"{COLOR_DEBUG}[DEBUG]{RESET}" if use_color else "[DEBUG]"
    return f"{prefix} {message}"
