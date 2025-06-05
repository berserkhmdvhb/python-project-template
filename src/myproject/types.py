"""
Shared type definitions and protocols for MyProject.

This module defines structural interfaces using `typing.Protocol` to allow
flexible and testable design across the CLI, settings, and test suite.

It enables:
- Type-safe dependency injection
- IDE/completion support for dynamic modules (like `settings`)
- Clean mocking/stubbing in tests

Contents:
- SettingsLike: Structural interface used by CLI/diagnostics to abstract settings module
- FakeSettingsModule: A runtime mock for testing CLI/settings behavior
- LoadSettingsFunc: Callable signature for settings loaders
- TestRootSetup: Callable signature for dynamic test environments

These are used heavily in `conftest.py`, `test_cli.py`, `diagnostics.py`, and
`utils_logger.py`.

Note:
    These are structural contracts (not class inheritance).
    They are compatible with real modules, mocks, or dynamically-loaded objects.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from types import ModuleType
from typing import Protocol, runtime_checkable

__all__ = [
    "FakeSettingsModule",
    "LoadSettingsFunc",
    "SettingsLike",
    "TestRootSetup",
]


@runtime_checkable
class SettingsLike(Protocol):
    """
    Protocol for settings modules or objects.

    Required methods:
        - get_environment: Returns current environment (DEV/UAT/PROD/etc.)
        - is_dev / is_uat / is_prod: Boolean accessors
        - get_log_max_bytes / get_log_backup_count: Log file limits
        - get_default_log_level: String log level (e.g., INFO)
        - resolve_loaded_dotenv_paths: List of .env files loaded in order
    """

    def get_environment(self) -> str: ...
    def is_dev(self) -> bool: ...
    def is_uat(self) -> bool: ...
    def is_prod(self) -> bool: ...
    def get_log_max_bytes(self) -> int: ...
    def get_log_backup_count(self) -> int: ...
    def get_default_log_level(self) -> str: ...
    def resolve_loaded_dotenv_paths(self) -> list[Path]: ...


class FakeSettingsModule(ModuleType):
    """
    Simple test double for simulating the settings module.

    Implements the SettingsLike interface using lambdas for logic
    based on a supplied environment name.

    Usage:
        fake = FakeSettingsModule("DEV")
        assert fake.is_dev() is True
    """

    def __init__(self, env: str) -> None:
        super().__init__("fake_settings")
        env = env.upper()
        self.get_environment: Callable[[], str] = lambda: env
        self.is_dev: Callable[[], bool] = lambda: env == "DEV"
        self.is_uat: Callable[[], bool] = lambda: env == "UAT"
        self.is_prod: Callable[[], bool] = lambda: env == "PROD"


class LoadSettingsFunc(Protocol):
    """
    Callable type for functions that load settings.

    Typically refers to the `load_settings()` function in `settings.py`.
    """

    def __call__(
        self, *, dotenv_path: Path | None = None, root_dir: Path | None = None
    ) -> ModuleType: ...


class TestRootSetup(Protocol):
    """
    Callable type for setting up temporary project roots for tests.

    Used in pytest fixtures to emulate `.env` loading and isolated settings.

    Args:
        env_files: List of .env-like files to create
        env_vars: Environment variables to inject temporarily

    Returns:
        A `Path` object pointing to the temporary root directory.
    """

    def __call__(
        self,
        *,
        env_files: list[str] | None = None,
        env_vars: dict[str, str] | None = None,
    ) -> Path: ...
