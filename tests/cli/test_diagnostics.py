from __future__ import annotations

from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from myproject.cli.diagnostics import print_debug_diagnostics, print_dotenv_debug
from myproject.types import SettingsLike

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


class DummySettings(SettingsLike):
    def get_environment(self) -> str:
        return "UAT"

    def is_dev(self) -> bool:
        return False

    def is_uat(self) -> bool:
        return True

    def is_prod(self) -> bool:
        return False

    def get_log_max_bytes(self) -> int:
        return 123456

    def get_log_backup_count(self) -> int:
        return 7

    def get_default_log_level(self) -> str:
        return "INFO"

    def resolve_loaded_dotenv_paths(self) -> list[Path]:
        return [Path("/fake/path/.env")]


@pytest.fixture
def dummy_args() -> Namespace:
    return Namespace(query="test", debug=True, verbose=True)


@pytest.fixture
def dummy_settings() -> DummySettings:
    return DummySettings()


def test_print_debug_diagnostics_output(
    dummy_args: Namespace,
    dummy_settings: DummySettings,
    capsys: CaptureFixture[str],
) -> None:
    print_debug_diagnostics(dummy_args, dummy_settings, use_color=False)
    out, _ = capsys.readouterr()
    assert "=== DEBUG DIAGNOSTICS ===" in out
    assert "Parsed args" in out
    assert "'query': 'test'" in out
    assert "Environment     : UAT" in out
    assert "Loaded dotenvs" in out
    assert "=== END DEBUG DIAGNOSTICS ===" in out


def test_print_dotenv_debug_enabled(
    dummy_settings: DummySettings,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setenv("MYPROJECT_DEBUG_ENV_LOAD", "1")
    print_dotenv_debug(dummy_settings, debug=True, use_color=False)
    out, _ = capsys.readouterr()
    assert "Loaded environment variables from:" in out
    assert str(Path("/fake/path/.env")) in out


@pytest.mark.parametrize("debug_flag", [False, True])
def test_print_dotenv_debug_disabled(
    dummy_settings: DummySettings,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
    *,
    debug_flag: bool,
) -> None:
    monkeypatch.delenv("MYPROJECT_DEBUG_ENV_LOAD", raising=False)
    print_dotenv_debug(dummy_settings, debug=debug_flag, use_color=False)
    out, _ = capsys.readouterr()
    assert out == ""
