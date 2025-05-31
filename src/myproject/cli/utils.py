"""General-purpose CLI utilities for MyProject.

This module includes reusable helper functions such as version retrieval,
intended for CLI tooling logic that doesn't belong in more specific modules
like `args.py` or `parser.py`.

Primarily developer-facing.
"""

from importlib.metadata import PackageNotFoundError, version

from myproject.constants import PACKAGE_NAME


def get_version() -> str:
    """Retrieve the package version, or fallback to 'unknown' if not installed."""
    try:
        return version(PACKAGE_NAME)
    except PackageNotFoundError:
        return "unknown (not installed)"
