"""
Main argument parser creation for MyProject CLI.

This module defines the primary `argparse.ArgumentParser` used by the CLI.
It handles user-facing flags, usage help, and examples. It also integrates
the early-stage environment parser from `args.py` to ensure consistent
behavior and inherits those options.

Key features:
- Rich help text and usage examples
- Supports `--query`, `--format`, `--color`, `--verbose`, `--debug`, and `--version`
- Dynamically shows installed version using package metadata
- Default output format is JSON with quiet console unless verbose is enabled
"""

from __future__ import annotations

import argparse
from importlib.metadata import PackageNotFoundError, version

from myproject import constants as const
from myproject.cli.args import LoggingArgumentParser, nonempty_str

__all__ = ["create_parser"]


def get_version() -> str:
    """
    Return the installed package version from metadata.

    Returns:
        The version string if available, otherwise 'unknown'.
    """
    try:
        return version(const.PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown (not installed)"


def create_parser(early_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """
    Create the main CLI argument parser with full option set.

    Args:
        early_parser: The pre-parsed early-stage ArgumentParser (for --env, --dotenv-path).

    Returns:
        Fully configured ArgumentParser instance.
    """
    parser = LoggingArgumentParser(
        description=(
            "MyProject CLI — A modern command-line tool with environment-aware behavior.\n\n"
            "This tool processes queries using a reusable core library, while supporting rich\n"
            "output, diagnostics, and environment-based configuration loaded from .env files.\n\n"
            "Environment variable loading priority:\n"
            "  1. DOTENV_PATH   → Set via --dotenv-path or env var to force a specific file\n"
            "  2. .env.override → Enforced values (e.g., for CI/CD or production)\n"
            "  3. .env          → Default team-wide configuration\n"
            "  4. .env.local    → Developer-local overrides (ignored by Git)\n"
            "  5. .env.test     → Automatically used when running under pytest\n"
            "  6. .env.sample   → Fallback for docs or when no other .env file is present\n\n"
            "Examples:\n"
            "  myproject --query 'hello world'\n"
            "  myproject --query 'log test' --dotenv-path config/dev.env\n"
            "  myproject --query 'data' --env uat --format text --verbose\n\n"
            "Notes:\n"
            "  - Output defaults to JSON and suppresses console output.\n"
            "  - Use --verbose to enable stdout/stderr messages.\n"
            "  - Use --debug for full diagnostics including environment details.\n"
            "  - Use --color=never to disable ANSI formatting in terminal output."
        ),
        parents=[early_parser],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Main CLI arguments
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
