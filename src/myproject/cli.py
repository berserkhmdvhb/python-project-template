"""Command-line interface for myproject."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import traceback
from importlib import reload
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import TYPE_CHECKING, NoReturn

import myproject.constants as const
from myproject.cli_color_utils import (
    format_debug,
    format_error,
    format_info,
    format_settings,
    format_warning,
    print_lines,
    should_use_color,
)
from myproject.cli_logger_utils import setup_logging, teardown_logger
from myproject.core import process_query
from myproject.settings import load_settings

if TYPE_CHECKING:
    from types import ModuleType

# ---------------------------------------------------------------------
# Messages
# ---------------------------------------------------------------------

_ERR_MSG_EMPTY_QUERY = "Query string must not be empty"
_WARNING_DOTENV_NOT_FOUND = "Warning: dotenv path not found: %s"
_ENV_LOAD_PREFIX = "Loaded environment variables from: %s"
_UNEXPECTED_ERROR_PREFIX = "Unexpected error: %s"
_SEARCH_CANCELLED_MSG = "Search cancelled by user."

# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------


def get_version() -> str:
    try:
        return version(const.PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown (not installed)"


def nonempty_str(value: str) -> str:
    if not value or not value.strip():
        raise argparse.ArgumentTypeError(_ERR_MSG_EMPTY_QUERY)
    return value.strip()


class LoggingArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        use_color = should_use_color("auto")
        sys.stderr.write(format_error(f"argument error: {message}", use_color=use_color) + "\n\n")
        self.print_help(sys.stderr)
        self.exit(const.EXIT_INVALID_USAGE)


def setup_cli_logger(*, verbose: bool, sett: ModuleType) -> None:
    log_level = None if verbose else logging.CRITICAL
    setup_logging(log_dir=sett.get_log_dir(), log_level=log_level, reset=True)


def apply_early_env(argv: list[str] | None) -> argparse.ArgumentParser:
    early_parser = argparse.ArgumentParser(add_help=False)
    early_parser.add_argument("--dotenv-path", type=str)
    early_parser.add_argument("--env", type=str)
    early_args, _ = early_parser.parse_known_args(argv)

    if early_args.dotenv_path:
        dotenv_path = Path(early_args.dotenv_path).expanduser().resolve()
        if dotenv_path.exists():
            os.environ["DOTENV_PATH"] = str(dotenv_path)
        else:
            sys.stderr.write(_WARNING_DOTENV_NOT_FOUND % dotenv_path + "\n")

    if early_args.env:
        os.environ["MYPROJECT_ENV"] = early_args.env.upper()

    return early_parser


# ---------------------------------------------------------------------
# Argument Parser
# ---------------------------------------------------------------------


def create_parser(early_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser = LoggingArgumentParser(
        description=(
            "MyProject CLI — A template command-line interface with environment awareness.\n\n"
            "This tool loads configuration from .env files or command-line flags and processes a "
            "search query.\n\n"
            "Environment variable loading priority:\n"
            "  1. --dotenv-path if provided\n"
            "  2. .env.test if PYTEST_CURRENT_TEST is set\n"
            "  3. .env.override > .env > .env.sample (fallback chain)\n\n"
            "Examples:\n"
            "  myproject --query 'hello world'\n"
            "  myproject --query 'hello' --format text --verbose\n"
            "  myproject --query 'data' --env uat\n"
            "  myproject --query 'log test' --dotenv-path config/dev.env\n\n"
            "Note:\n"
            "  By default, console output is suppressed and JSON output is returned.\n"
            "  Use --verbose to show logs and messages on the console.\n"
            "  Use --color=never to disable ANSI output, e.g., for clean logs or JSON parsers."
        ),
        parents=[early_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-q", "--query", type=nonempty_str, help="Search query to process")
    parser.add_argument("--version", action="version", version=f"%(prog)s {get_version()}")
    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        default=False,
        help="Enable console output (stdout/stderr). Default is off.",
    )
    parser.add_argument("--color", choices=["auto", "always", "never"], default="auto")
    parser.add_argument("--format", choices=["text", "json"], default="json")
    return parser


def print_dotenv_debug(sett: ModuleType, *, verbose: bool, use_color: bool) -> None:
    if os.getenv("MYPROJECT_DEBUG_ENV_LOAD") == "1" and verbose:
        dotenv_paths = sett.resolve_loaded_dotenv_paths()
        if dotenv_paths:
            msg = _ENV_LOAD_PREFIX % dotenv_paths[0]
            sys.stdout.write(format_settings(msg, use_color=use_color) + "\n")


def handle_result(
    processed: str,
    args: argparse.Namespace,
    sett: ModuleType,
    *,
    use_color: bool,
) -> None:
    logger = logging.getLogger("myproject")

    if args.format == "json":
        payload = {
            "environment": sett.get_environment(),
            "input": args.query,
            "output": processed,
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return

    results = [
        "[RESULT]",
        f"Input query    : {args.query}",
        processed,
    ]

    if sett.is_dev():
        msg = "DEV environment: Full diagnostics enabled"
    elif sett.is_uat():
        msg = "UAT environment: Pre-production validation"
    else:
        msg = "PROD environment: Logging limited, no debug output"

    if args.verbose:
        formatter = {
            "DEV": format_debug,
            "UAT": format_info,
            "PROD": format_warning,
        }.get(sett.get_environment(), format_info)
        results.append(formatter(msg, use_color=use_color))
    else:
        {
            "DEV": logger.debug,
            "UAT": logger.info,
            "PROD": logger.warning,
        }.get(sett.get_environment(), logger.info)(msg)

    print_lines(results, use_color=use_color)


def process_query_or_simulate(args: argparse.Namespace, sett: ModuleType) -> str:
    logger = logging.getLogger("myproject")
    if sett.is_dev():
        msg = "Simulating logic in DEV mode..."
        if args.verbose:
            sys.stdout.write(format_debug(msg, use_color=should_use_color(args.color)) + "\n")
        else:
            logger.debug(msg)
        return f"Processed (DEV MOCK): {args.query.upper()}"

    return process_query(args.query)


def main(argv: list[str] | None = None) -> None:
    early_parser = apply_early_env(argv)
    load_settings()

    from myproject import settings as sett

    reload(sett)

    parser = create_parser(early_parser)
    args = parser.parse_args(argv)
    use_color = should_use_color(args.color)
    logger = logging.getLogger("myproject")
    setup_cli_logger(verbose=args.verbose, sett=sett)

    try:
        print_dotenv_debug(sett, verbose=args.verbose, use_color=use_color)

        if args.verbose:
            sys.stdout.write(format_info("Processing query...", use_color=use_color) + "\n")
        else:
            logger.info("Processing query...")

        if not args.query:
            parser.print_help()
            sys.exit(const.EXIT_SUCCESS)

        processed = process_query_or_simulate(args, sett)
        handle_result(processed, args, sett, use_color=use_color)
        sys.exit(const.EXIT_SUCCESS)

    except KeyboardInterrupt:
        msg = _SEARCH_CANCELLED_MSG
        if args.verbose:
            sys.stderr.write(format_warning(msg, use_color=use_color) + "\n")
        else:
            logger.warning(msg)
        sys.exit(const.EXIT_CANCELLED)

    except Exception as e:
        if args.verbose:
            formatted_error = format_error(
                _UNEXPECTED_ERROR_PREFIX % str(e),
                use_color=use_color,
            )
            sys.stderr.write(formatted_error + "\n")
        else:
            logger.exception("Unexpected error", exc_info=e)
        if sett.get_environment() == "DEV":
            traceback.print_exc()
        sys.exit(const.EXIT_INVALID_USAGE)

    finally:
        teardown_logger(logger)


if __name__ == "__main__":
    main()
