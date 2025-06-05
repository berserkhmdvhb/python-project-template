"""Core logic for myproject.

This module provides the core processing functions that can be reused by both
the CLI interface and external consumers. It is intentionally kept free of any
CLI-specific or I/O code to maximize testability and portability.

Functions in this module:
- `sanitize_input`: Validates and cleans raw string input.
- `process_query`: Applies business logic to sanitized input.
- `example_hello`: A template demo function, useful for scaffolding.
- `simulate_failure`: Simulates a failure for testing error handling and logging.

This module adheres to clean-code principles and is part of the library
interface exposed via `__all__`.
"""

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

    Raises:
        ValueError: If the input is empty or invalid (via sanitize_input).
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

    Args:
        input_str: A user input string.

    Returns:
        Uppercased version of the input string if no failure is simulated.

    Raises:
        ValueError: If input contains the word 'fail' (case-insensitive).
    """
    if "fail" in input_str.lower():
        raise ValueError(_SIMULATED_FAILURE_MSG)
    return input_str.upper()
