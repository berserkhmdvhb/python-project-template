"""Shared caching decorators and utilities."""

from __future__ import annotations

import logging
from functools import lru_cache

__all__ = [
    "MAX_CACHE_SIZE",
    "cached_query",
    "cached_simulated_failure",
    "clear_all_caches",
    "print_cache_stats",
]

MAX_CACHE_SIZE = 128
logger = logging.getLogger("myproject.cache")


@lru_cache(maxsize=MAX_CACHE_SIZE)
def cached_query(query: str | None) -> str:
    """
    Cached wrapper for sanitize_input to speed up repeated queries.
    """
    from .core import sanitize_input

    result = sanitize_input(query)
    logger.debug("cached_query() hit for query: %r", query)
    return result


@lru_cache(maxsize=MAX_CACHE_SIZE)
def cached_simulated_failure(input_str: str) -> str:
    """
    Cached simulation of failure handling logic to avoid redundant processing.
    """
    from .core import _SIMULATED_FAILURE_MSG

    if "fail" in input_str.lower():
        raise ValueError(_SIMULATED_FAILURE_MSG)
    logger.debug("cached_simulated_failure() hit for input: %r", input_str)
    return input_str.upper()


def clear_all_caches() -> None:
    """
    Clears all internal function caches. Useful for testing or debugging.
    """
    cached_query.cache_clear()
    cached_simulated_failure.cache_clear()
    logger.info("All caches cleared.")


def print_cache_stats() -> None:
    """
    Print the current cache statistics for all cached functions.
    Useful for debugging or performance monitoring.
    """
    logger.info("cached_query: %s", cached_query.cache_info())
    logger.info("cached_simulated_failure: %s", cached_simulated_failure.cache_info())
