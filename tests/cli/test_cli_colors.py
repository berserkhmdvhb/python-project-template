"""
from __future__ import annotations

import sys
from typing import TYPE_CHECKING

import pytest

from myproject.cli_color_utils import (
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


def test_should_use_color_modes(monkeypatch: MonkeyPatch) -> None:
    assert not should_use_color("never")
    assert should_use_color("always")

    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert should_use_color("auto")

    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    assert not should_use_color("auto")


@pytest.mark.parametrize(
    ("line", "expected_color"),
    [
        ("[RESULT] everything ok", COLOR_HEADER),
        ("Input query something", COLOR_CODELINE),
        ("Processed value 123", COLOR_CODELINE),
        ("Just some other text", None),
    ],
)
def test_colorize_line_applies_expected_color(line: str, expected_color: str | None) -> None:
    out = colorize_line(line)
    if expected_color:
        assert out.startswith(expected_color)
        assert out.endswith(RESET)
    else:
        assert out == line


@pytest.mark.parametrize(
    ("func", "label", "msg"),
    [
        (format_error, "[ERROR]", "fail"),
        (format_info, "[INFO]", "info"),
        (format_success, "[OK]", "done"),
        (format_warning, "[WARNING]", "warn"),
        (format_debug, "[DEBUG]", "debug"),
        (format_settings, "[SETTINGS]", "loaded"),
    ],
)
def test_format_no_color(func, label, msg) -> None:
    result = func(msg, use_color=False)
    assert result == f"{label} {msg}"


def test_format_with_color_contains_prefix_and_reset() -> None:
    assert RESET in format_error("fail", use_color=True)
    assert COLOR_SETTINGS in format_settings("env", use_color=True)


def test_print_lines_no_color(capsys: CaptureFixture[str]) -> None:
    print_lines(["one", "two"], use_color=False)
    out, _ = capsys.readouterr()
    assert "one\n" in out
    assert "two\n" in out


def test_print_lines_empty_list(capsys: CaptureFixture[str]) -> None:
    print_lines([], use_color=True)
    out, _ = capsys.readouterr()
    assert out == ""


def test_print_lines_with_color(monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]) -> None:
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    lines = ["[RESULT] hello", "Input query hi", "other"]
    print_lines(lines, use_color=should_use_color("auto"))
    out, _ = capsys.readouterr()

    assert COLOR_HEADER in out
    assert COLOR_CODELINE in out
    assert "other" in out
"""
