"""
Result processing and output handlers for MyProject CLI.

This module provides the core CLI-side behavior for:
- Executing query logic (real or simulated)
- Formatting output based on CLI options (text vs JSON)
- Emitting colored messages, structured logs, and user-facing results
- DEV-mode simulation and failure injection for logging/testing purposes

This is the final step of the CLI pipeline after arguments and settings are parsed.
It routes to the core logic (`process_query`) or simulates it, and decides how
to display or log the results based on the environment and verbosity flags.

Functions:
- handle_result: Format and emit the result (stdout or log)
- process_query_or_simulate: Execute real or simulated processing logic
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from types import ModuleType

from myproject.cli.utils_color import (
    format_debug,
    format_info,
    format_warning,
    print_lines,
    should_use_color,
)
from myproject.core import process_query

__all__ = ["handle_result", "process_query_or_simulate"]


def handle_result(
    processed: str,
    args: argparse.Namespace,
    sett: ModuleType,
    *,
    use_color: bool,
) -> None:
    """
    Render and output the final result (text or JSON) based on CLI arguments.

    Args:
        processed: The processed result string from core or simulated logic.
        args: Parsed CLI arguments.
        sett: Environment-aware settings module.
        use_color: Whether to apply ANSI color formatting.
    """
    logger = logging.getLogger("myproject")
    verbose = args.verbose or args.debug

    format_env_message = {
        "DEV": format_debug,
        "UAT": format_info,
        "PROD": format_warning,
    }.get(sett.get_environment(), format_info)

    env_message = {
        "DEV": "DEV environment: Full diagnostics enabled",
        "UAT": "UAT environment: Pre-production validation",
        "PROD": "PROD environment: Logs and diagnostics are limited",
    }.get(sett.get_environment(), "Unknown environment")

    if args.format == "json":
        payload = {
            "environment": sett.get_environment(),
            "input": args.query,
            "output": processed,
        }
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")

        if verbose:
            sys.stdout.write(
                format_info(f"Processed query: {payload['output']}", use_color=use_color) + "\n"
            )
            sys.stdout.write(format_env_message(env_message, use_color=use_color) + "\n")
        else:
            logger.info("Processed query: %s", payload["output"])
            logger.warning(env_message) if sett.is_prod() else logger.info(env_message)
        return

    # Text output fallback (default)
    results = [
        "[RESULT]",
        f"Input query    : {args.query}",
        processed,
    ]
    logger.info("Processed query: %s", processed)

    if verbose:
        results.append(format_env_message(env_message, use_color=use_color))
    else:
        log_fn = {
            "DEV": logger.debug,
            "UAT": logger.info,
            "PROD": logger.warning,
        }.get(sett.get_environment(), logger.info)
        log_fn(env_message)

    force_stdout = verbose and args.color == "always"
    print_lines(results, use_color=use_color, force_stdout=force_stdout)


def _simulate_error() -> None:
    """
    Internal helper that raises a ValueError to simulate a failure.

    Used in DEV mode to test logging and error handling.
    """
    error_msg = "Simulated runtime failure for DEV debugging."
    raise ValueError(error_msg)


def process_query_or_simulate(args: argparse.Namespace, sett: ModuleType) -> str:
    """
    Run main query logic or simulate it in DEV mode.

    Simulated behavior:
    - If `--query fail` is passed in DEV mode, triggers `_simulate_error`
    - Otherwise returns a mock processed result

    Args:
        args: Parsed CLI arguments.
        sett: The loaded settings module.

    Returns:
        Processed string result (real or simulated).

    Raises:
        Any exception from `process_query` or `_simulate_error`.
    """
    logger = logging.getLogger("myproject")
    verbose = args.verbose or args.debug

    try:
        if sett.is_dev():
            msg = "Simulating logic in DEV mode..."
            if verbose:
                sys.stdout.write(format_debug(msg, use_color=should_use_color(args.color)) + "\n")
            else:
                logger.debug(msg)

            if args.query.strip().lower() == "fail":
                _simulate_error()

            return f"Processed (DEV MOCK): {args.query.upper()}"

        return process_query(args.query)

    except Exception:
        logger.exception("Unhandled error during query processing")
        raise
