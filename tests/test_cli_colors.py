import sys
import pytest

from myproject.cli_color_utils import (
    should_use_color,
    colorize_line,
    print_lines,
    format_error,
    format_info,
    format_success,
    format_warning,
    format_debug,
    RESET,
    COLOR_HEADER,
    COLOR_CODELINE,
)


def test_should_use_color_never():
    assert not should_use_color("never")


def test_should_use_color_always():
    assert should_use_color("always")


def test_should_use_color_auto_tty(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    assert should_use_color("auto")


def test_should_use_color_auto_not_tty(monkeypatch):
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    assert not should_use_color("auto")


@pytest.mark.parametrize(
    "line,expected_color",
    [
        ("[RESULT] everything ok", COLOR_HEADER),
        ("Input query something", COLOR_CODELINE),
        ("Processed value 123", COLOR_CODELINE),
        ("Just some other text", None),
    ],
)
def test_colorize_line(line, expected_color):
    out = colorize_line(line)
    if expected_color:
        assert out.startswith(expected_color)
        assert out.endswith(RESET)
    else:
        assert out == line


def test_format_error_and_reset_off():
    s = format_error("oops", use_color=False)
    assert s == "[ERROR] oops"


def test_format_info_and_reset_off():
    s = format_info("info", use_color=False)
    assert s == "[INFO] info"


def test_format_success_and_reset_off():
    s = format_success("done", use_color=False)
    assert s == "[OK] done"


def test_format_warning_and_reset_off():
    s = format_warning("watch out", use_color=False)
    assert s == "[WARNING] watch out"


def test_format_debug_and_reset_off():
    s = format_debug("dbg", use_color=False)
    assert s == "[DEBUG] dbg"


def test_format_with_color():
    # ensure ANSI codes present
    err = format_error("fail", use_color=True)
    assert "[ERROR]" in err and RESET in err

    info = format_info("hi", use_color=True)
    assert "[INFO]" in info and RESET in info


def test_print_lines_no_color(capsys):
    lines = ["one", "two"]
    print_lines(lines, use_color=False)
    out, err = capsys.readouterr()
    assert "one\n" in out
    assert "two\n" in out


def test_print_lines_with_color(monkeypatch, capsys):
    # force use_color True
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    lines = ["[RESULT] hello", "Input query hi", "other"]
    print_lines(lines, use_color=should_use_color("auto"))
    out, err = capsys.readouterr()
    # header line should be colored (contains ANSI escape)
    assert COLOR_HEADER in out
    # code lines should also be colored
    assert COLOR_CODELINE in out
    # fallback line should appear unmodified
    assert "other" in out
