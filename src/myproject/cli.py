"""Command-line interface for myproject."""

import argparse
import logging
import sys
from importlib.metadata import version, PackageNotFoundError
from typing import NoReturn
from myproject.constants import (
    PACKAGE_NAME,
    EXIT_INVALID_USAGE,
    EXIT_SUCCESS,
    EXIT_CANCELLED,
)
from myproject.settings import IS_DEV, IS_UAT, IS_PROD
from myproject.cli_color_utils import (
    should_use_color,
    format_error,
    format_info,
    print_lines,
    format_debug,
    format_warning,
)
from myproject.cli_logger_utils import setup_logging
from myproject.core import process_query

# Set up logging to file + console with env context
setup_logging()


def get_version() -> str:
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown (not installed)"


def nonempty_str(value: str) -> str:
    if not value or not value.strip():
        raise argparse.ArgumentTypeError("Query string must not be empty")
    return value.strip()


def setup_cli_logger(quiet: bool) -> logging.Logger:
    logger = logging.getLogger("myproject")
    if quiet:
        logger.setLevel(logging.CRITICAL)
    return logger


class LoggingArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        logger = logging.getLogger("myproject")
        logger.error(f"[ERROR] {message}")

        use_color = should_use_color("auto")
        print(format_error(f"argument error: {message}", use_color), file=sys.stderr)

        self.print_help(sys.stderr)
        self.exit(EXIT_INVALID_USAGE)


def main() -> None:
    parser = LoggingArgumentParser(
        description="MyProject CLI — a template command-line entry point.",
    )
    parser.add_argument(
        "-q",
        "--query",
        type=nonempty_str,
        required=True,
        help="Search query or string to process (must not be empty)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {get_version()}",
        help="Show version and exit",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress log messages",
    )
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default="auto",
        help="Colorized output: auto, always, or never",
    )

    args = parser.parse_args()
    use_color = should_use_color(args.color)
    logger = setup_cli_logger(args.quiet)

    try:
        msg = "Processing query..."
        logger.info(msg)
        if not args.quiet:
            print(format_info(msg, use_color))

        if IS_DEV:
            dev_msg = "Simulating logic in DEV mode..."
            logger.debug(dev_msg)
            if not args.quiet:
                print(format_debug(dev_msg, use_color))
            processed = f"Processed (DEV MOCK): {args.query.upper()}"
        else:
            processed = process_query(args.query)

        results = [
            "[RESULT]",
            f"Input query    : {args.query}",
            f"{processed}",
        ]

        if IS_DEV:
            diag = "DEV environment: Full diagnostics enabled"
            logger.debug(diag)
            if not args.quiet:
                results.append(format_debug(diag, use_color))
        elif IS_UAT:
            info = "UAT environment: Pre-production validation"
            logger.info(info)
            if not args.quiet:
                results.append(format_info(info, use_color))
        elif IS_PROD:
            warn = "PROD environment: Logging limited, no debug output"
            logger.warning(warn)
            if not args.quiet:
                results.append(format_warning(warn, use_color))

        print_lines(results, use_color)
        sys.exit(EXIT_SUCCESS)

    except KeyboardInterrupt:
        msg = "Search cancelled by user."
        logger.error(msg)
        if not args.quiet:
            print(format_error(msg, use_color))
        sys.exit(EXIT_CANCELLED)

    except Exception as e:
        err_msg = f"Unexpected error: {e}"
        if IS_DEV:
            import traceback

            traceback.print_exc()
        logger.error(err_msg)
        if not args.quiet:
            print(format_error(err_msg, use_color))
        sys.exit(EXIT_INVALID_USAGE)


if __name__ == "__main__":
    main()
