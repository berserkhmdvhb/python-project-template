"""Main CLI execution logic for MyProject.

This script coordinates all parts of the CLI:
- Parses early and main arguments
- Loads environment configuration
- Sets up logging
- Executes the query processing logic
- Provides diagnostics via --debug
"""

from __future__ import annotations

import logging
import sys
import traceback
from importlib import reload

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


def main(argv: list[str] | None = None) -> None:
    early_parser = apply_early_env(argv)
    load_settings()

    from myproject import settings as sett

    reload(sett)

    parser = cli_parser.create_parser(early_parser)
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
            parser.print_help()
            sys.exit(const.EXIT_SUCCESS)

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

    except Exception as e:
        if verbose:
            formatted_error = format_error(f"Unexpected error: {e}", use_color=use_color)
            sys.stderr.write(formatted_error + "\n")
        else:
            logger.exception("Unexpected error", exc_info=e)

        if args.debug:
            traceback.print_exc()

        sys.exit(const.EXIT_INVALID_USAGE)

    finally:
        teardown_logger(logger)


if __name__ == "__main__":
    main()
