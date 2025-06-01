from __future__ import annotations

import argparse
import subprocess
import sys
from importlib.metadata import PackageNotFoundError

import pytest

from myproject.cli.parser import create_parser, get_version


def test_create_parser_has_expected_arguments() -> None:
    early = argparse.ArgumentParser(add_help=False)
    parser = create_parser(early)

    args = parser.parse_args(
        [
            "--query",
            "test",
            "--verbose",
            "--debug",
            "--color",
            "always",
            "--format",
            "text",
        ]
    )
    assert args.query == "test"
    assert args.verbose is True
    assert args.debug is True
    assert args.color == "always"
    assert args.format == "text"


def test_parser_defaults() -> None:
    early = argparse.ArgumentParser(add_help=False)
    parser = create_parser(early)

    args = parser.parse_args([])
    assert args.query is None
    assert args.verbose is False
    assert args.debug is False
    assert args.color == "auto"
    assert args.format == "json"


def test_parser_query_required_type_enforced() -> None:
    early = argparse.ArgumentParser(add_help=False)
    parser = create_parser(early)

    with pytest.raises(SystemExit):
        parser.parse_args(["--query", ""])  # should fail due to nonempty_str enforcement


def test_version_flag() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "myproject", "--version"],
        capture_output=True,
        text=True,
        shell=False,
        check=True,
    )
    assert result.stdout.strip()


def test_get_version_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "myproject.cli.parser.version",
        lambda _: (_ for _ in ()).throw(PackageNotFoundError()),
    )
    assert get_version() == "unknown (not installed)"
