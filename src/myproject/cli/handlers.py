"""Result processing and output handlers for MyProject CLI.

This module contains developer-facing logic for:
- Handling and displaying CLI command results.
- Simulating behavior depending on the environment (e.g., DEV mock logic).
- Dynamically formatting console or JSON output based on verbosity and user config.
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


def handle_result(
    processed: str,
    args: argparse.Namespace,
    sett: ModuleType,
    *,
    use_color: bool,
) -> None:
    """Render and output results based on format, verbosity, and color settings."""
    logger = logging.getLogger("myproject")
    verbose = args.verbose or args.debug

    # Shared formatter for environment message
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
            # This is a user-facing line — must remain [INFO]
            sys.stdout.write(
                format_info(f"Processed query: {payload['output']}", use_color=use_color) + "\n"
            )
            sys.stdout.write(format_env_message(env_message, use_color=use_color) + "\n")
        else:
            logger.info("Processed query: %s", payload["output"])
            logger.warning(env_message) if sett.is_prod() else logger.info(env_message)
        return

    # Default text output
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
    error_msg = "Simulated runtime failure for DEV debugging."
    raise ValueError(error_msg)


def process_query_or_simulate(args: argparse.Namespace, sett: ModuleType) -> str:
    """Run main logic or simulate it for DEV mode, including error simulation for logging."""
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
