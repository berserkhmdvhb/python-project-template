from __future__ import annotations

from pathlib import Path
from types import ModuleType
from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class SettingsLike(Protocol):
    def get_environment(self) -> str: ...
    def is_dev(self) -> bool: ...
    def is_uat(self) -> bool: ...
    def is_prod(self) -> bool: ...
    def get_log_max_bytes(self) -> int: ...
    def get_log_backup_count(self) -> int: ...
    def get_default_log_level(self) -> str: ...
    def resolve_loaded_dotenv_paths(self) -> list[Path]: ...


class FakeSettingsModule(ModuleType):
    def __init__(self, env: str) -> None:
        super().__init__("fake_settings")
        env = env.upper()
        self.get_environment: Callable[[], str] = lambda: env
        self.is_dev: Callable[[], bool] = lambda: env == "DEV"
        self.is_uat: Callable[[], bool] = lambda: env == "UAT"
        self.is_prod: Callable[[], bool] = lambda: env == "PROD"
