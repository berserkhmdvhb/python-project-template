"""
Argument parsing and early environment setup for MyProject CLI.

This module supports two main responsibilities:

1. Early argument parsing:
   - Extracts and applies environment-related flags like `--dotenv-path` and `--env`
   - These are parsed early so settings can be loaded before building the full parser

2. Custom parsing behavior:
   - Provides `nonempty_str` as a stricter type for query input
   - Defines `LoggingArgumentParser`, which logs and colorizes CLI argument errors

This module is used by `cli_main.py` during initial CLI bootstrapping.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import NoReturn

from myproject import constants as const
from myproject.cli.utils_color import format_error, should_use_color

# Error message shown for blank or missing --query
_ERR_MSG_EMPTY_QUERY = "Query string must not be empty"

# Warning message for invalid --dotenv-path
_WARNING_DOTENV_NOT_FOUND = "Warning: dotenv path not found: %s"


def nonempty_str(value: str) -> str:
    """
    Argument type function for argparse to ensure non-empty strings.

    Args:
        value: The input string.

    Returns:
        The stripped string.

    Raises:
        ArgumentTypeError: If the string is empty or only whitespace.
    """
    stripped = value.strip()
    if not stripped:
        raise argparse.ArgumentTypeError(_ERR_MSG_EMPTY_QUERY)
    return stripped


class LoggingArgumentParser(argparse.ArgumentParser):
    """
    A subclass of ArgumentParser that logs and colorizes argument errors.

    Overrides the `error()` method to:
    - Log the error to the logger (if available)
    - Print a colored error to stderr
    - Show usage help
    - Exit with code `EXIT_INVALID_USAGE`
    """

    def error(self, message: str) -> NoReturn:
        from logging import getLogger

        logger = getLogger("myproject")
        if logger.hasHandlers():
            logger.error("Argument parsing error: %s", message)

        use_color = should_use_color("auto")
        sys.stderr.write(format_error(f"argument error: {message}", use_color=use_color) + "\n\n")
        self.print_help(sys.stderr)
        self.exit(const.EXIT_INVALID_USAGE)


def apply_early_env(argv: list[str] | None) -> argparse.ArgumentParser:
    """
    Apply early --env and --dotenv-path arguments to influence environment loading.

    This must be run before `load_settings()` and parser construction.

    Args:
        argv: Raw CLI arguments.

    Returns:
        An early-stage ArgumentParser instance (for re-use if needed).
    """
    early_parser = argparse.ArgumentParser(add_help=False)
    early_parser.add_argument("--dotenv-path", type=str)
    early_parser.add_argument("--env", type=str)

    early_args, _ = early_parser.parse_known_args(argv)

    # Apply --dotenv-path (if provided)
    dotenv_raw = early_args.dotenv_path
    if dotenv_raw:
        dotenv_path = Path(dotenv_raw).expanduser().resolve()
        if dotenv_path.exists():
            os.environ["DOTENV_PATH"] = str(dotenv_path)
        else:
            sys.stderr.write(_WARNING_DOTENV_NOT_FOUND % dotenv_path + "\n")

    # Apply --env (if provided)
    env_raw = early_args.env
    if env_raw:
        os.environ["MYPROJECT_ENV"] = env_raw.upper()

    return early_parser
