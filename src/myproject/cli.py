"""Command-line interface for myproject."""

import os
import argparse
import logging
import sys
import traceback
from importlib import reload
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path
from typing import NoReturn


def get_version() -> str:
    try:
        import myproject.constants as const

        return version(const.PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown (not installed)"


def nonempty_str(value: str) -> str:
    if not value or not value.strip():
        raise argparse.ArgumentTypeError("Query string must not be empty")
    return value.strip()


class LoggingArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        import logging
        import myproject.constants as const
        from myproject.cli_color_utils import format_error, should_use_color

        logger = logging.getLogger("myproject")
        logger.error(f"[ERROR] {message}")
        use_color = should_use_color("auto")
        print(format_error(f"argument error: {message}", use_color), file=sys.stderr)
        self.print_help(sys.stderr)
        self.exit(const.EXIT_INVALID_USAGE)


def setup_cli_logger(quiet: bool, sett) -> None:
    log_level = logging.CRITICAL if quiet else None
    from myproject.cli_logger_utils import setup_logging

    setup_logging(log_dir=sett.get_log_dir(), log_level=log_level, reset=True)


def main() -> None:
    # Early parse for --dotenv-path
    early_parser = argparse.ArgumentParser(add_help=False)
    early_parser.add_argument(
        "--dotenv-path",
        type=str,
        help="Path to a .env file to load environment variables from (e.g., .env.override)",
    )
    early_args, _ = early_parser.parse_known_args()

    # Set DOTENV_PATH so settings.py respects it
    if early_args.dotenv_path:
        dotenv_path = Path(early_args.dotenv_path).expanduser().resolve()
        if dotenv_path.exists():
            os.environ["DOTENV_PATH"] = str(dotenv_path)
        else:
            print(f"Warning: dotenv path not found: {dotenv_path}", file=sys.stderr)

    # Load settings and reload to reflect env
    from myproject.settings import load_settings

    load_settings()

    import myproject.settings as settings

    sett = reload(settings)

    import myproject.constants as const
    from myproject.cli_color_utils import (
        should_use_color,
        format_error,
        format_info,
        print_lines,
        format_debug,
        format_warning,
    )
    from myproject.cli_logger_utils import teardown_logger
    from myproject.core import process_query

    # Main parser
    parser = LoggingArgumentParser(
        description=(
            "MyProject CLI — a template command-line entry point.\n\n"
            "Environment variables may be loaded from:\n"
            "  1. --dotenv-path if provided\n"
            "  2. .env.test if PYTEST_CURRENT_TEST is set\n"
            "  3. .env.override > .env otherwise\n"
        ),
        parents=[early_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
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

    logger = logging.getLogger("myproject")
    setup_cli_logger(args.quiet, sett)

    try:
        logger.info("Processing query...")
        if not args.quiet:
            print(format_info("Processing query...", use_color))

        if sett.is_dev():
            logger.debug("Simulating logic in DEV mode...")
            if not args.quiet:
                print(format_debug("Simulating logic in DEV mode...", use_color))
            processed = f"Processed (DEV MOCK): {args.query.upper()}"
        else:
            processed = process_query(args.query)

        results = [
            "[RESULT]",
            f"Input query    : {args.query}",
            processed,
        ]

        if sett.is_dev():
            diag = "DEV environment: Full diagnostics enabled"
            logger.debug(diag)
            if not args.quiet:
                results.append(format_debug(diag, use_color))
        elif sett.is_uat():
            info = "UAT environment: Pre-production validation"
            logger.info(info)
            if not args.quiet:
                results.append(format_info(info, use_color))
        elif sett.is_prod():
            warn = "PROD environment: Logging limited, no debug output"
            logger.warning(warn)
            if not args.quiet:
                results.append(format_warning(warn, use_color))

        print_lines(results, use_color)
        teardown_logger(logger)
        sys.exit(const.EXIT_SUCCESS)

    except KeyboardInterrupt:
        msg = "Search cancelled by user."
        logger.error(msg)
        if not args.quiet:
            print(format_error(msg, use_color), file=sys.stderr)
        teardown_logger(logger)
        sys.exit(const.EXIT_CANCELLED)

    except Exception as e:
        err_msg = f"Unexpected error: {e}"
        logger.error(err_msg)
        if sett.is_dev():
            traceback.print_exc()
        if not args.quiet:
            print(format_error(err_msg, use_color), file=sys.stderr)
        teardown_logger(logger)
        sys.exit(const.EXIT_INVALID_USAGE)


if __name__ == "__main__":
    main()
