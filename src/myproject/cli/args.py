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
    if not value or not value.strip():
        raise argparse.ArgumentTypeError(_ERR_MSG_EMPTY_QUERY)
    return value.strip()


class LoggingArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> NoReturn:
        use_color = should_use_color("auto")
        sys.stderr.write(format_error(f"argument error: {message}", use_color=use_color) + "\n\n")
        self.print_help(sys.stderr)
        self.exit(const.EXIT_INVALID_USAGE)


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
