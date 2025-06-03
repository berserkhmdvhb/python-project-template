"""Unit tests for myproject.cache."""

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

logger = logging.getLogger("myproject.cache")

CACHE_EXPECTED_MISSES = 2


def test_cached_query_behavior(log_stream: StringIO) -> None:
    """Test that cached_query returns consistent results and logs hits."""
    result1 = cached_query(" hello ")
    result2 = cached_query(" hello ")
    result3 = cached_query("world")

    assert result1 == "hello"
    assert result2 == "hello"  # should hit cache
    assert result3 == "world"

    stats = cached_query.cache_info()
    assert stats.hits >= 1
    assert stats.misses >= CACHE_EXPECTED_MISSES

    output = log_stream.getvalue()
    assert "cached_query() hit for query:" in output


def test_cached_simulated_failure_behavior(log_stream: StringIO) -> None:
    """Test that cached_simulated_failure raises as expected and logs usage."""
    result = cached_simulated_failure("TEST")
    assert result == "TEST"

    with pytest.raises(ValueError, match="Simulated processing failure"):
        cached_simulated_failure("fail case")

    output = log_stream.getvalue()
    assert "cached_simulated_failure() hit for input:" in output


def test_clear_all_caches_resets_stats() -> None:
    """Ensure that clear_all_caches resets internal function caches."""
    cached_query("once")
    cached_simulated_failure("again")

    assert cached_query.cache_info().currsize > 0
    assert cached_simulated_failure.cache_info().currsize > 0

    clear_all_caches()

    assert cached_query.cache_info().currsize == 0
    assert cached_simulated_failure.cache_info().currsize == 0


def test_print_cache_stats_logs_output(log_stream: StringIO) -> None:
    """Ensure that print_cache_stats logs hit/miss info to logger."""
    cached_query("x")
    cached_simulated_failure("y")

    clear_all_caches()  # clear to show stat output from fresh state

    print_cache_stats()
    output = log_stream.getvalue()
    assert "cached_query:" in output
    assert "cached_simulated_failure:" in output
