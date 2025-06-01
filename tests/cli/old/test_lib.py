from __future__ import annotations

import pytest

import myproject.constants as const
from myproject import __version__
from myproject.core import example_hello, process_query, sanitize_input


def test_version_is_string_and_nonempty() -> None:
    """Ensure that the package version is a non-empty string."""
    assert isinstance(__version__, str), "Version should be a string"
    assert __version__.strip() != "", "Version string should not be empty"
    assert __version__[0].isdigit(), "Version should start with a digit"


def test_dummy_function_returns_expected_value() -> None:
    """Test the behavior of dummy_function in core.py."""
    expected = "Hello from core!"
    assert example_hello() == expected, "Unexpected return from example_hello()"


def test_default_threshold_within_bounds() -> None:
    """Confirm the default threshold is within [0.0, 1.0] range."""
    assert isinstance(const.DEFAULT_THRESHOLD, float), "Threshold should be float"
    assert 0.0 <= const.DEFAULT_THRESHOLD <= 1.0, "Threshold out of [0.0, 1.0] bounds"


@pytest.mark.parametrize(
    ("value", "should_raise"),
    [
        (None, True),
        ("", True),
        ("   ", True),
        ("test", False),
        ("  hello  ", False),
    ],
)
def test_process_query_edge_cases(
    value: str | None,
    *,
    should_raise: bool,
) -> None:
    """Validate process_query handles optional and malformed input robustly."""
    if should_raise:
        with pytest.raises(ValueError, match="cannot be empty"):
            process_query(value)
    else:
        assert isinstance(value, str)
        result = process_query(value)
        expected = f"Processed query: {value.strip()}"
        assert result == expected, f"Expected '{expected}', got '{result}'"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" hello ", "hello"),
        ("\tworld\n", "world"),
        ("valid", "valid"),
    ],
)
def test_sanitize_input_valid_cases(raw: str, expected: str) -> None:
    """Test that sanitize_input returns stripped strings for valid input."""
    result = sanitize_input(raw)
    assert result == expected, f"Expected '{expected}' but got '{result}'"
    assert result == raw.strip(), "sanitize_input should strip whitespace"


@pytest.mark.parametrize("bad_input", [None, "", "   ", "\t\n "])
def test_sanitize_input_invalid_cases(bad_input: str | None) -> None:
    """Test that sanitize_input raises ValueError on bad input."""
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_input(bad_input)
