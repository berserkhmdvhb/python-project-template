"""Core logic for myproject."""

from __future__ import annotations

__all__ = [
    "example_hello",
    "process_query",
    "sanitize_input",
    "simulate_failure",
]


_QUERY_EMPTY_ERROR = "Query string cannot be empty."
_SIMULATED_FAILURE_MSG = "Simulated processing failure triggered by input."


def sanitize_input(value: str | None) -> str:
    """
    Sanitize user input to ensure it's non-empty and not just whitespace.

    Args:
        value: Input string, possibly None or empty.

    Returns:
        A stripped, validated string.

    Raises:
        ValueError: If input is None or contains only whitespace.
    """
    if value is None or not value.strip():
        raise ValueError(_QUERY_EMPTY_ERROR)
    return value.strip()


def process_query(query: str | None) -> str:
    """
    Process the sanitized input query and return a result.

    Args:
        query: Raw user input.

    Returns:
        A clean or transformed version of the query.
    """
    # Placeholder logic — replace with real implementation
    return sanitize_input(query)


def example_hello() -> str:
    """
    Dummy function for template demonstration purposes.

    Returns:
        A static greeting string.
    """
    return "Hello from core!"


def simulate_failure(input_str: str) -> str:
    """
    Simulates a runtime failure to demonstrate error logging.

    Raises:
        ValueError: If input contains the word 'fail' (case-insensitive).
    """
    if "fail" in input_str.lower():
        raise ValueError(_SIMULATED_FAILURE_MSG)
    return input_str.upper()
