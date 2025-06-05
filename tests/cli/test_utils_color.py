"""
Unit tests for color formatting and output logic in CLI utilities.

This module verifies:
- Color detection logic (isatty, mode flags)
- Line formatting with or without ANSI codes
- Individual formatters for each log level
- print_lines() behavior under various conditions
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Protocol

import pytest

from myproject.cli.utils_color import (
    COLOR_CODELINE,
    COLOR_HEADER,
    COLOR_SETTINGS,
    RESET,
    colorize_line,
    format_debug,
    format_error,
    format_info,
    format_settings,
    format_success,
    format_warning,
    print_lines,
    should_use_color,
)

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch

__all__ = [
    "test_colorize_line",
    "test_formatters_with_color",
    "test_formatters_without_color",
    "test_print_lines_empty_stdout",
    "test_print_lines_no_color_stdout",
    "test_print_lines_with_color_stdout",
    "test_should_use_color_modes",
]


class Formatter(Protocol):
    def __call__(self, msg: str, *, use_color: bool) -> str: ...


# ---------------------------------------------------------------------
# Tests for color detection and mode handling
# ---------------------------------------------------------------------


def test_should_use_color_modes(monkeypatch: MonkeyPatch) -> None:
    """Verify should_use_color handles 'always', 'never', and 'auto' cases correctly."""
    assert not should_use_color("never")
    assert should_use_color("always")

    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert should_use_color("auto")

    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    assert not should_use_color("auto")


# ---------------------------------------------------------------------
# Tests for line colorization
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("line", "expected_color"),
    [
        ("[RESULT] All good", COLOR_HEADER),
        ("Input query: something", COLOR_CODELINE),
        ("Processed value: 123", COLOR_CODELINE),
        ("Random text", None),
    ],
)
def test_colorize_line(line: str, expected_color: str | None) -> None:
    """Check if specific patterns are colorized with appropriate codes."""
    result = colorize_line(line)
    if expected_color:
        assert result.startswith(expected_color)
        assert result.endswith(RESET)
    else:
        assert result == line


# ---------------------------------------------------------------------
# Tests for formatter utilities
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    ("formatter", "label", "message"),
    [
        (format_error, "[ERROR]", "fail"),
        (format_info, "[INFO]", "info"),
        (format_success, "[OK]", "done"),
        (format_warning, "[WARNING]", "warn"),
        (format_debug, "[DEBUG]", "debug"),
        (format_settings, "[SETTINGS]", "env"),
    ],
)
def test_formatters_without_color(
    formatter: Formatter,
    label: str,
    message: str,
) -> None:
    """Ensure formatters produce expected output without ANSI codes."""
    result = formatter(message, use_color=False)
    assert result == f"{label} {message}"


def test_formatters_with_color() -> None:
    """Ensure color codes appear when use_color=True."""
    colored = format_error("fail", use_color=True)
    assert "[ERROR]" in colored
    assert COLOR_SETTINGS in format_settings("env", use_color=True)
    assert RESET in colored


# ---------------------------------------------------------------------
# Tests for print_lines output logic
# ---------------------------------------------------------------------


def test_print_lines_no_color_stdout(capsys: CaptureFixture[str]) -> None:
    """Test print_lines() with no color output."""
    lines = ["one", "two"]
    print_lines(lines, use_color=False, force_stdout=True)
    out, _ = capsys.readouterr()
    for line in lines:
        assert f"{line}\n" in out


def test_print_lines_empty_stdout(capsys: CaptureFixture[str]) -> None:
    """Test print_lines() with an empty list produces no output."""
    print_lines([], use_color=True, force_stdout=True)
    out, _ = capsys.readouterr()
    assert out == ""


def test_print_lines_with_color_stdout(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    """Test that print_lines() applies color codes correctly when output is a tty."""
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    lines = ["[RESULT] hello", "Input query: hi", "plain text"]

    print_lines(lines, use_color=should_use_color("auto"), force_stdout=True)
    out, _ = capsys.readouterr()

    assert COLOR_HEADER in out
    assert COLOR_CODELINE in out
    for line in lines:
        assert line in out
