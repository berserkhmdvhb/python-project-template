"""Diagnostics utilities for user-facing CLI debug output.

This module provides functions used to display runtime diagnostics
to the user when the `--debug` flag is enabled in the CLI. It is
intended for CLI users and developers alike who want visibility
into how the CLI parsed arguments, loaded environment settings,
and resolved `.env` files.

These diagnostics are printed to stdout in a human-readable format
using consistent color-coded output (if enabled).

This module should only handle *visible diagnostics* relevant to
end-user behavior or runtime context. For internal development
tools or test-time helpers, use `debug.py` instead.

Functions:
    - print_debug_diagnostics: Print detailed argument and env info.
    - print_dotenv_debug: Print the path of loaded dotenv files
      (if enabled via `MYPROJECT_DEBUG_ENV_LOAD=1`).
"""

import os
import sys
from argparse import Namespace
from types import ModuleType

from myproject.cli.utils_color import format_debug, format_settings


def print_dotenv_debug(
    sett: ModuleType,
    *,
    debug: bool,
    use_color: bool,
) -> None:
    """Print information about loaded dotenv files if debug mode is enabled."""
    if os.getenv("MYPROJECT_DEBUG_ENV_LOAD") == "1" and debug:
        dotenv_paths = sett.resolve_loaded_dotenv_paths()
        if dotenv_paths:
            msg = f"Loaded environment variables from: {dotenv_paths[0]}"
            sys.stdout.write(format_settings(msg, use_color=use_color) + "\n")


def print_debug_diagnostics(
    args: Namespace,
    sett: ModuleType,
    *,
    use_color: bool,
) -> None:
    """Print structured diagnostics when `--debug` is active."""
    sys.stdout.write(
        format_debug("=== DEBUG DIAGNOSTICS ===", use_color=use_color) + "\n",
    )
    sys.stdout.write(
        format_debug(f"Parsed args     : {vars(args)}", use_color=use_color) + "\n",
    )
    sys.stdout.write(
        format_debug(
            f"Environment     : {sett.get_environment()}",
            use_color=use_color,
        )
        + "\n",
    )
    sys.stdout.write(
        format_debug(
            f"Loaded dotenvs  : {sett.resolve_loaded_dotenv_paths()}",
            use_color=use_color,
        )
        + "\n",
    )
    sys.stdout.write(
        format_debug("=== END DEBUG DIAGNOSTICS ===", use_color=use_color) + "\n",
    )
