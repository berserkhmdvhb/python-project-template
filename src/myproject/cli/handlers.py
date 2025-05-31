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

    # Add contextual summary message based on environment
    if sett.is_dev():
        msg = "DEV environment: Full diagnostics enabled"
    elif sett.is_uat():
        msg = "UAT environment: Pre-production validation"
    else:
        msg = "PROD environment: Logging limited, no debug output"

    if verbose:
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

    force_stdout = verbose and args.color == "always"
    print_lines(results, use_color=use_color, force_stdout=force_stdout)


def process_query_or_simulate(args: argparse.Namespace, sett: ModuleType) -> str:
    """Run main logic or simulate it for DEV mode."""
    logger = logging.getLogger("myproject")
    verbose = args.verbose or args.debug

    if sett.is_dev():
        msg = "Simulating logic in DEV mode..."
        if verbose:
            sys.stdout.write(format_debug(msg, use_color=should_use_color(args.color)) + "\n")
        else:
            logger.debug(msg)
        return f"Processed (DEV MOCK): {args.query.upper()}"

    return process_query(args.query)
