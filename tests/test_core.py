from __future__ import annotations

import pytest

import myproject.constants as const
from myproject import __version__
from myproject.core import example_hello, process_query, sanitize_input

# --- Version & Constant Tests ---


def test___version__is_nonempty_string() -> None:
    """Ensure the package version is a non-empty string that starts with a digit."""
    assert isinstance(__version__, str)
    assert __version__.strip()
    assert __version__[0].isdigit()


def test_default_threshold_is_float_and_in_bounds() -> None:
    """Check that DEFAULT_THRESHOLD is a float in the [0.0, 1.0] range."""
    assert isinstance(const.DEFAULT_THRESHOLD, float)
    assert 0.0 <= const.DEFAULT_THRESHOLD <= 1.0


# --- Core Function Tests ---


def test_example_hello_returns_expected_string() -> None:
    """Verify the output of the dummy example_hello function."""
    assert example_hello() == "Hello from core!"


@pytest.mark.parametrize(
    ("input_value", "should_raise"),
    [
        (None, True),
        ("", True),
        ("   ", True),
        ("test", False),
        ("  hello  ", False),
    ],
)
def test_process_query_behavior(input_value: str | None, *, should_raise: bool) -> None:
    """Test process_query for valid and invalid input scenarios."""
    if should_raise:
        with pytest.raises(ValueError, match="cannot be empty"):
            process_query(input_value)
    else:
        assert isinstance(input_value, str)
        expected = f"{input_value.strip()}"
        assert process_query(input_value) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        (" hello ", "hello"),
        ("\tworld\n", "world"),
        ("valid", "valid"),
    ],
)
def test_sanitize_input_strips_and_validates(raw: str, expected: str) -> None:
    """Ensure sanitize_input strips and validates input correctly."""
    assert sanitize_input(raw) == expected


@pytest.mark.parametrize("bad_input", [None, "", "   ", "\t\n"])
def test_sanitize_input_rejects_invalid(bad_input: str | None) -> None:
    """Ensure sanitize_input raises ValueError on invalid input."""
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_input(bad_input)
