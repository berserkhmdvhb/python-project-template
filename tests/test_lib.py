import pytest

from myproject import __version__
import myproject.constants as const
from myproject.core import sanitize_input, example_hello, process_query


def test_version_is_string_and_nonempty() -> None:
    """Ensure that the package version is a non-empty string."""
    assert isinstance(__version__, str)
    assert __version__.strip() != ""
    assert __version__[0].isdigit()


def test_dummy_function_returns_expected_value() -> None:
    """Test the behavior of dummy_function in core.py."""
    expected = "Hello from core!"
    assert example_hello() == expected


def test_default_threshold_within_bounds() -> None:
    """Confirm the default threshold is within [0.0, 1.0] range."""
    assert isinstance(const.DEFAULT_THRESHOLD, float)
    assert 0.0 <= const.DEFAULT_THRESHOLD <= 1.0


@pytest.mark.parametrize(
    "value, should_raise",
    [
        (None, True),
        ("", True),
        ("   ", True),
        ("test", False),
        ("  hello  ", False),
    ],
)
def test_process_query_edge_cases(value: str | None, should_raise: bool) -> None:
    """Validate process_query handles optional and malformed input robustly."""
    if should_raise:
        with pytest.raises(ValueError):
            process_query(value)
    else:
        assert isinstance(value, str)  # Type guard for MyPy
        result = process_query(value)
        assert result == f"Processed query: {value.strip()}"


@pytest.mark.parametrize(
    "raw, expected",
    [
        (" hello ", "hello"),
        ("\tworld\n", "world"),
        ("valid", "valid"),
    ],
)
def test_sanitize_input_valid_cases(raw: str, expected: str) -> None:
    """Test that sanitize_input returns stripped strings for valid input."""
    assert sanitize_input(raw) == expected


@pytest.mark.parametrize("bad_input", [None, "", "   ", "\t\n "])
def test_sanitize_input_invalid_cases(bad_input: str | None) -> None:
    """Test that sanitize_input raises ValueError on bad input."""
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_input(bad_input)
