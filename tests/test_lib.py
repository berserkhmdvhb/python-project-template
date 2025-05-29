import pytest
from myproject import __version__
from myproject.constants import DEFAULT_THRESHOLD
from myproject.core import dummy_function, process_query


def test_version_is_string_and_nonempty() -> None:
    """Ensure that the package version is a non-empty string."""
    assert isinstance(__version__, str)
    assert len(__version__) >= 3
    assert __version__[0].isdigit()


def test_dummy_function_returns_expected_value() -> None:
    """Test the behavior of dummy_function in core.py."""
    assert dummy_function() == "Hello from core!"


def test_default_threshold_within_bounds() -> None:
    """Confirm the default threshold is within [0.0, 1.0] range."""
    assert isinstance(DEFAULT_THRESHOLD, float)
    assert 0.0 <= DEFAULT_THRESHOLD <= 1.0


@pytest.mark.parametrize("value", [None, "", "  ", "test", "  hello  "])
def test_process_query_edge_cases(value: str | None) -> None:
    """Validate process_query handles optional and malformed input robustly."""
    if value is None or not value.strip():
        with pytest.raises(ValueError):
            process_query(value)
    else:
        result = process_query(value)
        assert result == f"Processed query: {value.strip()}"
