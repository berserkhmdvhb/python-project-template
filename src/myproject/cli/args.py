"""Argument parsing and early environment setup for MyProject CLI."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import NoReturn

from myproject import constants as const
from myproject.cli.utils_color import format_error, should_use_color

_ERR_MSG_EMPTY_QUERY = "Query string must not be empty"
_WARNING_DOTENV_NOT_FOUND = "Warning: dotenv path not found: %s"


def nonempty_str(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise argparse.ArgumentTypeError(_ERR_MSG_EMPTY_QUERY)
    return stripped


class LoggingArgumentParser(argparse.ArgumentParser):
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
    early_parser = argparse.ArgumentParser(add_help=False)
    early_parser.add_argument("--dotenv-path", type=str)
    early_parser.add_argument("--env", type=str)

    early_args, _ = early_parser.parse_known_args(argv)

    dotenv_raw = early_args.dotenv_path
    if dotenv_raw:
        dotenv_path = Path(dotenv_raw).expanduser().resolve()
        if dotenv_path.exists():
            os.environ["DOTENV_PATH"] = str(dotenv_path)
        else:
            sys.stderr.write(_WARNING_DOTENV_NOT_FOUND % dotenv_path + "\n")

    env_raw = early_args.env
    if env_raw:
        os.environ["MYPROJECT_ENV"] = env_raw.upper()

    return early_parser
