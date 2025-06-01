from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import pytest

from myproject.cli.args import (
    _ERR_MSG_EMPTY_QUERY,
    _WARNING_DOTENV_NOT_FOUND,
    LoggingArgumentParser,
    apply_early_env,
    nonempty_str,
)
from myproject.constants import EXIT_INVALID_USAGE


@pytest.mark.parametrize(
    ("input_val", "expected"),
    [("hello", "hello"), ("  trimmed  ", "trimmed")],
)
def test_nonempty_str_valid(input_val: str, expected: str) -> None:
    assert nonempty_str(input_val) == expected


@pytest.mark.parametrize("bad_val", ["", "   "])
def test_nonempty_str_invalid(bad_val: str) -> None:
    with pytest.raises(argparse.ArgumentTypeError, match=_ERR_MSG_EMPTY_QUERY):
        nonempty_str(bad_val)


def test_logging_argument_parser_error(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(sys, "exit", lambda code: (_ for _ in ()).throw(SystemExit(code)))

    parser = LoggingArgumentParser(prog="myprog")
    parser.add_argument("--name")

    with pytest.raises(SystemExit) as exc_info:
        parser.parse_args(["--unknown"])

    captured = capsys.readouterr()
    assert "argument error:" in captured.err
    assert "--name" in captured.err
    assert exc_info.value.code == EXIT_INVALID_USAGE


def test_apply_early_env_sets_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MYPROJECT_ENV", raising=False)
    parser = apply_early_env(["--env", "uat"])
    assert os.environ["MYPROJECT_ENV"] == "UAT"
    assert isinstance(parser, argparse.ArgumentParser)


def test_apply_early_env_sets_dotenv_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DOTENV_PATH", raising=False)
    dotenv_file = tmp_path / "custom.env"
    dotenv_file.write_text("SAMPLE_VAR=value")

    parser = apply_early_env(["--dotenv-path", str(dotenv_file)])
    assert os.environ["DOTENV_PATH"] == str(dotenv_file)
    assert isinstance(parser, argparse.ArgumentParser)


def test_apply_early_env_warns_if_missing_path(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fake_path = Path("nonexistent/path.env")
    assert not fake_path.exists()

    monkeypatch.delenv("DOTENV_PATH", raising=False)
    parser = apply_early_env(["--dotenv-path", str(fake_path)])

    captured = capsys.readouterr()
    assert _WARNING_DOTENV_NOT_FOUND.split("%s")[0] in captured.err
    assert isinstance(parser, argparse.ArgumentParser)
