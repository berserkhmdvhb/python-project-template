"""
Diagnostics utilities for user-facing CLI debug output.

This module provides human-readable runtime diagnostics when the `--debug` flag
is passed to the CLI. It is designed for *end users* and *developers* who want
to inspect how the CLI is interpreting arguments, resolving settings, and loading
`.env` files.

Behavior:
- Output is printed directly to stdout (not logging)
- ANSI coloring is applied based on `--color` flag or terminal support
- Output includes CLI arguments, selected environment, and loaded dotenv paths

Use Cases:
- CLI diagnostics with `--debug` during development or test runs
- Manual inspection of how the environment is configured
- Debugging config loading issues with `MYPROJECT_DEBUG_ENV_LOAD=1`

Note:
    This module handles only user-visible diagnostics.
    For internal tools or developer-specific utilities, use `debug.py`.

Functions:
    - print_dotenv_debug: Show the loaded .env file, if applicable
    - print_debug_diagnostics: Print args, env, and .env context
"""

import os
import sys
from argparse import Namespace

from myproject.cli.utils_color import format_debug, format_settings
from myproject.types import SettingsLike

__all__ = ["print_debug_diagnostics", "print_dotenv_debug"]


def print_dotenv_debug(
    sett: SettingsLike,
    *,
    debug: bool,
    use_color: bool,
) -> None:
    """
    Print information about loaded dotenv files if debug mode is enabled.

    Args:
        sett: A settings-like object that provides dotenv resolution.
        debug: True if --debug was passed to CLI.
        use_color: Whether to apply ANSI formatting.
    """
    if os.getenv("MYPROJECT_DEBUG_ENV_LOAD") == "1" and debug:
        dotenv_paths = sett.resolve_loaded_dotenv_paths()
        if dotenv_paths:
            msg = f"Loaded environment variables from: {dotenv_paths[0]}"
            sys.stdout.write(format_settings(msg, use_color=use_color) + "\n")


def print_debug_diagnostics(
    args: Namespace,
    sett: SettingsLike,
    *,
    use_color: bool,
) -> None:
    """
    Print structured diagnostics when `--debug` is active.

    Includes:
    - CLI arguments as parsed
    - Current environment setting
    - Loaded .env file paths

    Args:
        args: Parsed CLI arguments (argparse.Namespace)
        sett: The current settings object
        use_color: Whether to apply ANSI formatting
    """
    sys.stdout.write(format_debug("=== DEBUG DIAGNOSTICS ===", use_color=use_color) + "\n")
    sys.stdout.write(format_debug(f"Parsed args     : {vars(args)}", use_color=use_color) + "\n")
    sys.stdout.write(
        format_debug(
            f"Environment     : {sett.get_environment()}",
            use_color=use_color,
        )
        + "\n"
    )
    sys.stdout.write(
        format_debug(
            f"Loaded dotenvs  : {sett.resolve_loaded_dotenv_paths()}",
            use_color=use_color,
        )
        + "\n"
    )
    sys.stdout.write(format_debug("=== END DEBUG DIAGNOSTICS ===", use_color=use_color) + "\n")
