from __future__ import annotations

import types
from argparse import Namespace
from typing import TYPE_CHECKING, cast

import pytest

from myproject.cli.diagnostics import print_debug_diagnostics, print_dotenv_debug

if TYPE_CHECKING:
    from _pytest.capture import CaptureFixture
    from _pytest.monkeypatch import MonkeyPatch


@pytest.fixture
def dummy_args() -> Namespace:
    return Namespace(query="test", debug=True, verbose=True)


@pytest.fixture
def dummy_settings_module() -> types.ModuleType:
    module = types.ModuleType("dummy_settings")
    module.get_environment = lambda: "UAT"
    module.resolve_loaded_dotenv_paths = lambda: ["/fake/path/.env"]
    return cast("types.ModuleType", module)


def test_print_debug_diagnostics_output(
    dummy_args: Namespace,
    dummy_settings_module: types.ModuleType,
    capsys: CaptureFixture[str],
) -> None:
    print_debug_diagnostics(dummy_args, dummy_settings_module, use_color=False)
    out, _ = capsys.readouterr()
    assert "=== DEBUG DIAGNOSTICS ===" in out
    assert "Parsed args" in out
    assert "'query': 'test'" in out
    assert "Environment     : UAT" in out
    assert "Loaded dotenvs" in out
    assert "=== END DEBUG DIAGNOSTICS ===" in out


def test_print_dotenv_debug_enabled(
    dummy_settings_module: types.ModuleType,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
) -> None:
    monkeypatch.setenv("MYPROJECT_DEBUG_ENV_LOAD", "1")
    print_dotenv_debug(dummy_settings_module, debug=True, use_color=False)
    out, _ = capsys.readouterr()
    assert "Loaded environment variables from:" in out
    assert "/fake/path/.env" in out


@pytest.mark.parametrize("debug_flag", [False, True])
def test_print_dotenv_debug_disabled(
    dummy_settings_module: types.ModuleType,
    monkeypatch: MonkeyPatch,
    capsys: CaptureFixture[str],
    *,
    debug_flag: bool,
) -> None:
    monkeypatch.delenv("MYPROJECT_DEBUG_ENV_LOAD", raising=False)
    print_dotenv_debug(dummy_settings_module, debug=debug_flag, use_color=False)
    out, _ = capsys.readouterr()
    assert out == ""
