"""Main argument parser creation for MyProject CLI."""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version

from myproject import constants as const
from myproject.cli.args import LoggingArgumentParser, nonempty_str


def get_version() -> str:
    try:
        return version(const.PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown (not installed)"


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
            "  Use --color=never to disable ANSI output.\n"
            "  Use --debug for detailed diagnostics during development or tests."
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
    parser.add_argument(
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Enable rich diagnostics and detailed output. Implies --verbose.",
    )
    parser.add_argument("--color", choices=["auto", "always", "never"], default="auto")
    parser.add_argument("--format", choices=["text", "json"], default="json")
    return parser
