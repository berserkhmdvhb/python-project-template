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


class Formatter(Protocol):
    def __call__(self, msg: str, *, use_color: bool) -> str: ...


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
        ("[RESULT] All good", COLOR_HEADER),
        ("Input query: something", COLOR_CODELINE),
        ("Processed value: 123", COLOR_CODELINE),
        ("Random text", None),
    ],
)
def test_colorize_line(line: str, expected_color: str | None) -> None:
    result = colorize_line(line)
    if expected_color:
        assert result.startswith(expected_color)
        assert result.endswith(RESET)
    else:
        assert result == line


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
    result = formatter(message, use_color=False)
    assert result == f"{label} {message}"


def test_formatters_with_color() -> None:
    colored = format_error("fail", use_color=True)
    assert "[ERROR]" in colored
    assert COLOR_SETTINGS in format_settings("env", use_color=True)
    assert RESET in colored


def test_print_lines_no_color_stdout(capsys: CaptureFixture[str]) -> None:
    lines = ["one", "two"]
    print_lines(lines, use_color=False, force_stdout=True)
    out, _ = capsys.readouterr()
    for line in lines:
        assert f"{line}\n" in out


def test_print_lines_empty_stdout(capsys: CaptureFixture[str]) -> None:
    print_lines([], use_color=True, force_stdout=True)
    out, _ = capsys.readouterr()
    assert out == ""


def test_print_lines_with_color_stdout(
    monkeypatch: MonkeyPatch, capsys: CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    lines = ["[RESULT] hello", "Input query: hi", "plain text"]

    print_lines(lines, use_color=should_use_color("auto"), force_stdout=True)
    out, _ = capsys.readouterr()

    assert COLOR_HEADER in out
    assert COLOR_CODELINE in out
    for line in lines:
        assert line in out
