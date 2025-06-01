from __future__ import annotations

import logging
import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO


def invoke_cli(
    args: Sequence[str],
    tmp_path: Path,
    env: dict[str, str] | None = None,
) -> tuple[str, str, int]:
    cmd = [sys.executable, "-m", "myproject", *args]
    if not any(a.startswith("--color") for a in args):
        cmd.append("--color=never")

    full_env = {
        **os.environ,
        "MYPROJECT_LOG_MAX_BYTES": "10000",
        "MYPROJECT_LOG_BACKUP_COUNT": "2",
        "MYPROJECT_DEBUG_ENV_LOAD": "0",
        **(env or {}),
    }

    dummy_env = tmp_path / ".env"
    dummy_env.write_text("")
    full_env["DOTENV_PATH"] = str(dummy_env.resolve())

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=full_env,
        check=False,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


# ---------------------------------------------------------------------
# Safe dummy handler (for teardown tests)
# ---------------------------------------------------------------------


class SafeDummyHandler(logging.StreamHandler[TextIO]):
    def flush(self) -> None:
        pass  # Prevent actual flushing

    def close(self) -> None:
        pass  # Prevent actual closing
