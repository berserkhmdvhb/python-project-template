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


def test_should_use_color_never() -> None:
    assert not should_use_color("never")


def test_should_use_color_always() -> None:
    assert should_use_color("always")


def test_should_use_color_auto_tty(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert should_use_color("auto")


def test_should_use_color_auto_not_tty(monkeypatch: MonkeyPatch) -> None:
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
def test_colorize_line(line: str, expected_color: str | None) -> None:
    out = colorize_line(line)
    if expected_color:
        assert out.startswith(expected_color)
        assert out.endswith(RESET)
    else:
        assert out == line


def test_format_error_and_reset_off() -> None:
    s = format_error("oops", use_color=False)
    assert s == "[ERROR] oops"


def test_format_info_and_reset_off() -> None:
    s = format_info("info", use_color=False)
    assert s == "[INFO] info"


def test_format_success_and_reset_off() -> None:
    s = format_success("done", use_color=False)
    assert s == "[OK] done"


def test_format_warning_and_reset_off() -> None:
    s = format_warning("watch out", use_color=False)
    assert s == "[WARNING] watch out"


def test_format_debug_and_reset_off() -> None:
    s = format_debug("dbg", use_color=False)
    assert s == "[DEBUG] dbg"


def test_format_settings_and_reset_off() -> None:
    s = format_settings("loaded", use_color=False)
    assert s == "[SETTINGS] loaded"


def test_format_with_color() -> None:
    err = format_error("fail", use_color=True)
    assert "[ERROR]" in err
    assert RESET in err

    info = format_info("hi", use_color=True)
    assert "[INFO]" in info
    assert RESET in info

    settings = format_settings("env loaded", use_color=True)
    assert "[SETTINGS]" in settings
    assert COLOR_SETTINGS in settings
    assert RESET in settings


def test_print_lines_no_color(capsys: CaptureFixture[str]) -> None:
    lines = ["one", "two"]
    print_lines(lines, use_color=False)
    out, _ = capsys.readouterr()
    assert "one\n" in out
    assert "two\n" in out


def test_print_lines_empty(capsys: CaptureFixture[str]) -> None:
    print_lines([], use_color=True)
    out, _ = capsys.readouterr()
    assert out == ""


def test_print_lines_with_color(
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    lines = ["[RESULT] hello", "Input query hi", "other"]
    print_lines(lines, use_color=should_use_color("auto"))
    out, _ = capsys.readouterr()

    assert COLOR_HEADER in out
    assert COLOR_CODELINE in out
    assert "other" in out
"""
def test_cli_color_always(run_cli: Callable[..., tuple[str, str, int]]) -> None:
    out, err, code = run_cli(
        "--query",
        "hello",
        "--color",
        "always",
        "--verbose",
        env={"MYPROJECT_ENV": "DEV"},
    )
    assert code == const.EXIT_SUCCESS

    # ANSI escape codes begin with \x1b[
    has_ansi = any("\x1b[" in line for line in out.splitlines())
    assert has_ansi, "Expected ANSI color codes in output but none found"
"""
