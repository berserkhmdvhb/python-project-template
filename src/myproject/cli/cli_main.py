"""
Main CLI execution logic for MyProject.

This script coordinates the entire lifecycle of the CLI:

- Applies early environment overrides via `apply_early_env`
- Loads prioritized .env files with `load_settings()`
- Reloads settings to reflect updated environment state
- Creates the CLI argument parser (`argparse.ArgumentParser`)
- Sets up structured logging (per environment)
- Handles optional tab-completion (if `argcomplete` is available)
- Executes query processing or simulation logic from `handlers.py`
- Handles diagnostics output when `--debug` is enabled
- Routes formatted output to either stdout, stderr, or logs
- Catches and logs all errors gracefully with exit codes

Can be invoked directly or as part of `myproject` entry point:

    python -m myproject --query "foo"
    myproject --query "foo"

Exit codes follow Unix conventions and are defined in `constants.py`.
"""

from __future__ import annotations

import logging
import sys
import traceback
from importlib import reload
from importlib.util import find_spec

from myproject import constants as const
from myproject.cli import diagnostics, handlers
from myproject.cli import parser as cli_parser
from myproject.cli.args import apply_early_env
from myproject.cli.utils_color import (
    format_error,
    format_info,
    format_warning,
    should_use_color,
)
from myproject.cli.utils_logger import setup_logging, teardown_logger
from myproject.settings import load_settings

__all__ = ["main"]

# Detect argcomplete support (optional dependency)
ARGCOMPLETE_AVAILABLE = find_spec("argcomplete") is not None


def main(argv: list[str] | None = None) -> None:
    """
    Entry point for the CLI tool.

    Args:
        argv: Optional list of arguments (used for testing or internal calls).

    Raises:
        SystemExit: With appropriate exit code depending on error or result.
    """
    early_parser = apply_early_env(argv)
    load_settings()

    from myproject import settings as sett

    reload(sett)  # Ensure any .env changes are reflected

    parser = cli_parser.create_parser(early_parser)

    if ARGCOMPLETE_AVAILABLE:
        try:
            import argcomplete

            argcomplete.autocomplete(parser)
        # argcomplete may fail in unsupported shells
        except Exception as exc:  # noqa: BLE001
            logging.getLogger("myproject").debug("argcomplete setup failed: %s", exc)

    args = parser.parse_args(argv)
    verbose = args.verbose or args.debug
    use_color = should_use_color(args.color)

    logger = logging.getLogger("myproject")
    setup_logging(
        log_dir=sett.get_log_dir(),
        log_level=None if verbose else logging.CRITICAL,
        reset=True,
    )

    try:
        diagnostics.print_dotenv_debug(sett, debug=args.debug, use_color=use_color)

        if args.debug:
            diagnostics.print_debug_diagnostics(args, sett, use_color=use_color)

        if verbose:
            sys.stdout.write(format_info("Processing query...", use_color=use_color) + "\n")
        else:
            logger.info("Processing query...")

        if not args.query:
            sys.stderr.write(format_error("Error: --query is required.\n", use_color=use_color))
            sys.exit(const.EXIT_INVALID_USAGE)

        processed = handlers.process_query_or_simulate(args, sett)
        handlers.handle_result(processed, args, sett, use_color=use_color)
        sys.exit(const.EXIT_SUCCESS)

    except KeyboardInterrupt:
        msg = "Search cancelled by user."
        if verbose:
            sys.stderr.write(format_warning(msg, use_color=use_color) + "\n")
        else:
            logger.warning(msg)
        sys.exit(const.EXIT_CANCELLED)

    except Exception as exc:
        logger.exception("Unhandled error during CLI execution")
        sys.stderr.write(format_error(f"Error: {exc}", use_color=use_color) + "\n")

        if args.debug:
            traceback.print_exc()

        sys.exit(const.EXIT_ERROR)

    finally:
        teardown_logger(logger)


if __name__ == "__main__":  # pragma: no cover
    main()
