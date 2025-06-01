from __future__ import annotations

from pathlib import Path
from typing import Protocol


class SettingsLike(Protocol):
    def get_environment(self) -> str:
        ...

    def resolve_loaded_dotenv_paths(self) -> list[Path]:
        ...
