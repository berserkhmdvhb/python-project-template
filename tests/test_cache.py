"""
Unit tests for myproject.cache.

This module verifies:
- Correct caching behavior and return values
- Log output for cache hits/misses
- Cache-clearing and cache-stats functions

Tested Functions:
- `cached_query`: Caches cleaned query results
- `cached_simulated_failure`: Simulates cacheable failure-prone processing
- `clear_all_caches`: Resets all internal caches
- `print_cache_stats`: Logs summary of cache state
"""

from __future__ import annotations

import logging
from io import StringIO

import pytest

from myproject.cache import (
    cached_query,
    cached_simulated_failure,
    clear_all_caches,
    print_cache_stats,
)

__all__ = [
    "test_cached_query_behavior",
    "test_cached_simulated_failure_behavior",
    "test_clear_all_caches_resets_stats",
    "test_print_cache_stats_logs_output",
]

logger = logging.getLogger("myproject.cache")

# Minimum expected number of misses from fresh calls
CACHE_EXPECTED_MISSES = 2

# ---------------------------------------------------------------------
# Caching behavior and hit/miss stats
# ---------------------------------------------------------------------


def test_cached_query_behavior(log_stream: StringIO) -> None:
    """
    Test that cached_query returns consistent results and logs cache hits.
    """
    # First call should process and cache
    result1 = cached_query(" hello ")

    # Second call should hit the cache
    result2 = cached_query(" hello ")

    # Different input results in a miss
    result3 = cached_query("world")

    assert result1 == "hello"
    assert result2 == "hello"
    assert result3 == "world"

    # Check cache statistics for hits and misses
    stats = cached_query.cache_info()
    assert stats.hits >= 1
    assert stats.misses >= CACHE_EXPECTED_MISSES

    # Confirm log output indicates a cache hit
    output = log_stream.getvalue()
    assert "cached_query() hit for query:" in output


def test_cached_simulated_failure_behavior(log_stream: StringIO) -> None:
    """
    Test cached_simulated_failure returns/caches success, but raises for "fail case".
    """
    # Normal input should succeed and be cached
    result = cached_simulated_failure("TEST")
    assert result == "TEST"

    # Simulated failure input should raise
    with pytest.raises(ValueError, match="Simulated processing failure"):
        cached_simulated_failure("fail case")

    # Log should include cache hit for success case
    output = log_stream.getvalue()
    assert "cached_simulated_failure() hit for input:" in output


# ---------------------------------------------------------------------
# Cache clearing and logging
# ---------------------------------------------------------------------


def test_clear_all_caches_resets_stats() -> None:
    """
    Ensure clear_all_caches resets internal caches of all functions.
    """
    # Seed caches with any input
    cached_query("once")
    cached_simulated_failure("again")

    # Assert caches are populated
    assert cached_query.cache_info().currsize > 0
    assert cached_simulated_failure.cache_info().currsize > 0

    # Clear all caches
    clear_all_caches()

    # After clearing, caches should be empty
    assert cached_query.cache_info().currsize == 0
    assert cached_simulated_failure.cache_info().currsize == 0


def test_print_cache_stats_logs_output(log_stream: StringIO) -> None:
    """
    Ensure print_cache_stats emits cache usage logs.
    """
    # Prime the caches with a single entry each
    cached_query("x")
    cached_simulated_failure("y")

    # Clear again to test print output from a clean state
    clear_all_caches()

    # Call the stats printer and capture log output
    print_cache_stats()
    output = log_stream.getvalue()

    # Output should reference each cached function by name
    assert "cached_query:" in output
    assert "cached_simulated_failure:" in output
