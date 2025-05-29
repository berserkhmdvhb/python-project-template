"""Command-line interface for myproject."""

import argparse
import logging
import sys
from importlib.metadata import version, PackageNotFoundError

from myproject.constants import (
    PACKAGE_NAME,
    EXIT_INVALID_USAGE,
    EXIT_SUCCESS,
    EXIT_CANCELLED,
    DEFAULT_LOG_LEVEL,
    LOG_FORMAT,
)
from myproject.cli_color_utils import (
    should_use_color,
    format_error,
    format_info,
    print_lines,
)

# Configuration of encoding settings
## Windows-specific UTF-8 setup
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")


def get_version() -> str:
    """Retrieve the installed package version using importlib.metadata."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown (not installed)"


def setup_logger(quiet: bool) -> logging.Logger:
    logger = logging.getLogger("myproject.cli")
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(handler)

    logger.setLevel(logging.CRITICAL if quiet else DEFAULT_LOG_LEVEL)
    logger.propagate = False
    return logger


def nonempty_str(value: str) -> str:
    """Argparse type validator: disallow empty or whitespace-only strings."""
    if not value or not value.strip():
        raise argparse.ArgumentTypeError("query string must not be empty")
    return value.strip()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="MyProject CLI — a template command-line entry point.",
    )
    parser.add_argument(
        "-q",
        "--query",
        type=nonempty_str,
        required=True,
        help="Search query or string to process (cannot be empty)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="Show the current version and exit",
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress log messages")
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Colorized terminal output",
    )

    args = parser.parse_args()
    use_color = should_use_color(args.color)
    logger = setup_logger(args.quiet)

    try:
        logger.info(format_info("Processing query...", use_color))
        results = [
            "[RESULT]",
            f"Input query    : {args.query}",
            "Processed value: dummy_value",
        ]
        print_lines(results, use_color)
        sys.exit(EXIT_SUCCESS)

    except KeyboardInterrupt:
        logger.error(format_error("Search cancelled by user.", use_color))
        sys.exit(EXIT_CANCELLED)

    except Exception as e:
        logger.error(format_error(f"Unexpected error: {e}", use_color))
        sys.exit(EXIT_INVALID_USAGE)


if __name__ == "__main__":
    main()
